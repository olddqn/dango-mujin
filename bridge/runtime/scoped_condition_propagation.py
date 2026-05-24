"""
scoped_condition_propagation.py

Scope-aware federation prerequisite propagation.

When the federation propagates prerequisite hints to a claim, it must
respect the scope of weakened prerequisites. A bypassed prerequisite
should not be propagated as a hint to a claim that already uses an
equivalent safety path — that would be redundant and misleading.

This module wraps the existing prerequisite_memory_integration logic
with scope-aware filtering.

Rules:
  - Weakened prerequisite + claim has bypass conditions → DO NOT propagate hint
  - Weakened prerequisite + claim lacks bypass conditions → propagate with scope note
  - Unscoped (promoted) prerequisite → propagate unconditionally (advisory)
  - Deprecated prerequisite → never propagate

No hard enforcement. All hints are advisory.
No hidden logic. stdlib only. Read-only.
"""

import json
import os
import sys

_BRIDGE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _BRIDGE)


def _sutable_path(table: str) -> str:
    base = os.path.dirname(_BRIDGE)
    p = os.path.join(base, "sutable", f"{table}.jsonl")
    if os.path.exists(p):
        return p
    p2 = os.path.normpath(os.path.join(_BRIDGE, "..", "sutable", f"{table}.jsonl"))
    return p2 if os.path.exists(p2) else p


def _read_jsonl(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    events = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return events


def _load_fmap(fmap=None) -> dict:
    if fmap is not None:
        return fmap
    return {
        "plans":      _read_jsonl(_sutable_path("plans")),
        "memory":     _read_jsonl(_sutable_path("memory")),
        "federation": _read_jsonl(_sutable_path("federation")),
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_scoped_propagation_hints(claim_id: str, fmap=None) -> list[dict]:
    """
    Return scope-filtered prerequisite hints for a claim.

    Each hint:
    {
      "condition":            str,
      "hint_type":            "federation_prerequisite",
      "authority":            "none",
      "advisory":             True,
      "applicable":           bool,   # False if bypassed (hint suppressed)
      "scoped":               bool,   # True if this prerequisite is weakened
      "scope":                str,    # new_scope from weakened event (if scoped)
      "bypass_reason":        list[str] | None,
      "note":                 str,
    }

    Bypassed prerequisites are included with applicable=False so callers
    can see why the prerequisite is not being propagated.
    """
    from prerequisite_scope_resolver import load_scope_rules, resolve_scope
    from prerequisite_contest_resolver import all_prerequisite_statuses

    fm = _load_fmap(fmap)
    rules = load_scope_rules(fmap=fm)
    statuses = all_prerequisite_statuses(fm["federation"])

    hints = []
    for status in statuses:
        cond = status["condition"]
        st   = status.get("status", "")

        if st == "deprecated":
            continue  # never propagate deprecated prerequisites

        if cond in rules:
            # Scoped (weakened) prerequisite
            rule = rules[cond]
            res  = resolve_scope(cond, claim_id, fmap=fm)

            if res["bypassed"]:
                # Suppressed — claim uses equivalent safety path
                hints.append({
                    "condition":        cond,
                    "hint_type":        "federation_prerequisite",
                    "authority":        "none",
                    "advisory":         True,
                    "applicable":       False,
                    "scoped":           True,
                    "scope":            rule["new_scope"],
                    "bypass_reason":    res["bypass_conditions_found"],
                    "note": (
                        f"Prerequisite bypassed for this claim: "
                        f"{', '.join(res['bypass_conditions_found'])} "
                        f"provides equivalent safety path."
                    ),
                })
            else:
                # Applicable — propagate with scope note
                hints.append({
                    "condition":        cond,
                    "hint_type":        "federation_prerequisite",
                    "authority":        "none",
                    "advisory":         True,
                    "applicable":       True,
                    "scoped":           True,
                    "scope":            rule["new_scope"],
                    "bypass_reason":    None,
                    "note": (
                        f"Independently discovered by {status.get('evidence_claims_count', '?')} "
                        f"claim(s) via structural plan tree diff. "
                        f"Applies to: {rule['applies_to_label']}. "
                        f"Can be bypassed via: {rule['bypassed_by_labels']}."
                    ),
                })
        else:
            # Unscoped (universally applicable) promoted prerequisite
            hints.append({
                "condition":        cond,
                "hint_type":        "federation_prerequisite",
                "authority":        "none",
                "advisory":         True,
                "applicable":       True,
                "scoped":           False,
                "scope":            "all_spaces",
                "bypass_reason":    None,
                "note": (
                    f"Independently discovered by {status.get('evidence_claims_count', '?')} "
                    f"claim(s) via structural plan tree diff. Universally applicable."
                ),
            })

    return hints


def propagate_to_all_claims(fmap=None) -> dict[str, list[dict]]:
    """
    Run get_scoped_propagation_hints for all claims with active plans.
    Returns: {claim_id: [hints]}
    """
    from prerequisite_scope_resolver import _active_plan_conditions

    fm = _load_fmap(fmap)
    all_plans = _active_plan_conditions(fm["plans"])
    return {
        cid: get_scoped_propagation_hints(cid, fmap=fm)
        for cid in sorted(all_plans.keys())
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli():
    import argparse
    ap = argparse.ArgumentParser(description="Scope-aware prerequisite propagation hints")
    ap.add_argument("--claim-id", help="specific claim to compute hints for")
    ap.add_argument("--all",      action="store_true", help="all claims")
    ap.add_argument("--json",     action="store_true")
    args = ap.parse_args()

    if args.claim_id:
        hints = get_scoped_propagation_hints(args.claim_id)
        if args.json:
            print(json.dumps(hints, indent=2))
        else:
            _print_hints(args.claim_id, hints)
    else:
        all_hints = propagate_to_all_claims()
        if args.json:
            print(json.dumps(all_hints, indent=2))
        else:
            for cid, hints in all_hints.items():
                _print_hints(cid, hints)
                print()


def _print_hints(cid: str, hints: list[dict]):
    print(f"  {cid}:")
    if not hints:
        print("    (no active prerequisites)")
        return
    for h in hints:
        cond = h["condition"]
        if h["applicable"]:
            scope_tag = f"  [scope: {h['scope']}]" if h["scoped"] else "  [universal]"
            print(f"    → propagate: {cond}{scope_tag}")
            print(f"      {h['note']}")
        else:
            print(f"    ⊛ suppress:  {cond}  [bypassed via: {h['bypass_reason']}]")


if __name__ == "__main__":
    _cli()
