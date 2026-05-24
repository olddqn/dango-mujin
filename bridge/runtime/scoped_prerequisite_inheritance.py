"""
scoped_prerequisite_inheritance.py

Computes which federation prerequisites are applicable to a specific claim,
given that some prerequisites are scoped (weakened) rather than universal.

Core design:
  "A weakened prerequisite does not disappear.
   Its applicability becomes conditional."

For each scoped prerequisite, this module determines:
  - applicable: the prerequisite still applies in this claim's context
  - bypassed: the claim's plan uses an equivalent safety path

A prerequisite is bypassed if and only if the claim's active plan includes
at least one recognised equivalent safety condition for that prerequisite.
This is structural, deterministic, and transparent.

No hidden scoring. No centralized authority. stdlib only. Read-only.
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

def compute_inheritance(claim_id: str, fmap=None) -> dict:
    """
    Compute which prerequisites are applicable and which are bypassed
    for a specific claim_id, considering scope rules from weakened events.

    Also handles non-scoped (universally applicable) promoted prerequisites.

    Returns:
    {
      "claim_id":                 str,
      "applicable_prerequisites": list[str],   # applies in this claim's context
      "bypassed_prerequisites":   list[str],   # bypassed via equivalent safety
      "unscoped_prerequisites":   list[str],   # promoted but not yet weakened
      "scope_reasoning":          dict[str, list[str]],  # per-condition reasoning
      "applicability_details":    list[dict],  # full resolution per condition
    }
    """
    from prerequisite_scope_resolver import resolve_scope, load_scope_rules
    from prerequisite_snapshot import snapshot as prereq_snapshot

    fm = _load_fmap(fmap)

    # All currently active (promoted/reaffirmed/weakened) prerequisites
    all_statuses = prereq_snapshot(fmap=fm) if False else []
    try:
        from claim_federation import load_federation_events
        from prerequisite_contest_resolver import all_prerequisite_statuses
        fed_events = fm["federation"]
        all_statuses = all_prerequisite_statuses(fed_events)
    except Exception:
        all_statuses = []

    scoped_rules = load_scope_rules(fmap=fm)

    applicable:  list[str] = []
    bypassed:    list[str] = []
    unscoped:    list[str] = []
    reasoning:   dict[str, list[str]] = {}
    details:     list[dict] = []

    for status in all_statuses:
        cond   = status["condition"]
        st     = status.get("status", "")
        if st == "deprecated":
            continue  # deprecated prerequisites are not inherited

        if cond in scoped_rules:
            # Scoped (weakened) prerequisite — resolve per claim context
            res = resolve_scope(cond, claim_id, fmap=fm)
            reasoning[cond] = res["scope_reasoning"]
            details.append(res)
            if res["bypassed"]:
                bypassed.append(cond)
            else:
                applicable.append(cond)
        else:
            # Unscoped (universally applicable) promoted prerequisite
            unscoped.append(cond)
            reasoning[cond] = ["no_scope_rule: universally applicable"]
            details.append({
                "condition":               cond,
                "claim_id":               claim_id,
                "applicable":             True,
                "bypassed":               False,
                "bypass_conditions_found": [],
                "scope_indicators_found":  [],
                "bypassed_by_labels":      [],
                "applies_to_label":        "all_spaces",
                "scope_reasoning":         ["universally_applicable"],
                "has_scope_rule":          False,
            })

    return {
        "claim_id":                 claim_id,
        "applicable_prerequisites": sorted(applicable),
        "bypassed_prerequisites":   sorted(bypassed),
        "unscoped_prerequisites":   sorted(unscoped),
        "scope_reasoning":          reasoning,
        "applicability_details":    details,
    }


def compute_all_inheritances(fmap=None) -> list[dict]:
    """
    Compute inheritance for every claim that has an active plan.
    Returns list ordered by claim_id.
    """
    from prerequisite_scope_resolver import _active_plan_conditions, _load_fmap as _ld

    fm = _load_fmap(fmap)
    plans = _active_plan_conditions(fm["plans"])
    return [compute_inheritance(cid, fmap=fm) for cid in sorted(plans.keys())]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli():
    import argparse
    ap = argparse.ArgumentParser(
        description="Compute scoped prerequisite inheritance for claims"
    )
    ap.add_argument("--claim-id", help="specific claim to compute for")
    ap.add_argument("--all",      action="store_true", help="all claims (default)")
    ap.add_argument("--json",     action="store_true")
    args = ap.parse_args()

    if args.claim_id:
        result = compute_inheritance(args.claim_id)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            _print_inheritance(result)
    else:
        results = compute_all_inheritances()
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            if not results:
                print("No claims with active plans.")
            for r in results:
                _print_inheritance(r)
                print()


def _print_inheritance(r: dict):
    cid = r["claim_id"]
    app = r["applicable_prerequisites"]
    byp = r["bypassed_prerequisites"]
    uns = r["unscoped_prerequisites"]

    print(f"  {cid}:")
    if app:
        for cond in app:
            rsn = r["scope_reasoning"].get(cond, [])
            print(f"    ✓ applicable:  {cond}")
            for line in rsn:
                print(f"        {line}")
    if byp:
        for cond in byp:
            rsn = r["scope_reasoning"].get(cond, [])
            print(f"    ⊛ bypassed:    {cond}")
            for line in rsn:
                print(f"        {line}")
    if uns:
        for cond in uns:
            print(f"    ◆ unscoped:    {cond}  [universally applicable]")
    if not app and not byp and not uns:
        print("    (no active prerequisites)")


if __name__ == "__main__":
    _cli()
