"""
scoped_prerequisite_snapshot.py

Full scoped prerequisite snapshot: for each weakened prerequisite,
shows the scope rules, which claims it applies to, which bypass it,
and any detected scope conflicts.

This is the top-level query module for the scoped prerequisite layer.
It delegates to:
  prerequisite_scope_resolver.py    — scope rule loading + resolution
  scoped_prerequisite_inheritance.py — per-claim applicability
  scope_conflict_detector.py        — conflict detection
  prerequisite_survivability.py     — survivability score

stdlib only. Read-only.
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

def scoped_snapshot(condition: str = None, fmap=None) -> dict | list[dict]:
    """
    Return a full scoped snapshot.

    If condition is given, returns a single record.
    Otherwise returns a list of all scoped prerequisites.

    Each record:
    {
      "condition":          str,
      "new_scope":          str,
      "applies_to_label":   str,
      "bypassed_by_labels": list[str],
      "bypass_conditions":  list[str],
      "applicable_claims":  list[str],
      "bypassed_claims":    list[str],
      "claim_details":      dict[str, dict],  # per-claim resolution
      "conflicts":          list[dict],        # scope conflicts across all claims
      "survivability":      float | None,
      "survivability_status": str,
    }
    """
    from prerequisite_scope_resolver import (
        load_scope_rules, scope_summary, resolve_scope, _active_plan_conditions
    )
    from scope_conflict_detector import detect_all_conflicts
    from prerequisite_survivability import compute_survivability

    fm = _load_fmap(fmap)
    rules = load_scope_rules(fmap=fm)
    all_conflicts = detect_all_conflicts(fmap=fm)
    all_plans = _active_plan_conditions(fm["plans"])
    all_claims = sorted(all_plans.keys())

    def _build(cond: str) -> dict:
        rule = rules[cond]
        claim_details: dict[str, dict] = {}
        applicable_claims = []
        bypassed_claims   = []

        for cid in all_claims:
            res = resolve_scope(cond, cid, fmap=fm)
            claim_details[cid] = res
            if res["bypassed"]:
                bypassed_claims.append(cid)
            else:
                applicable_claims.append(cid)

        # Collect scope conflicts touching this condition
        cond_conflicts = [
            c for conflicts in all_conflicts.values()
            for c in conflicts
            if c["condition"] == cond
        ]

        surv = compute_survivability(cond, fmap=fm)

        return {
            "condition":            cond,
            "new_scope":            rule["new_scope"],
            "applies_to_label":     rule["applies_to_label"],
            "bypassed_by_labels":   rule["bypassed_by_labels"],
            "bypass_conditions":    rule["bypass_conditions"],
            "applicable_claims":    applicable_claims,
            "bypassed_claims":      bypassed_claims,
            "claim_details":        claim_details,
            "conflicts":            cond_conflicts,
            "survivability":        surv.get("survivability"),
            "survivability_status": surv.get("status", "no_data"),
        }

    if condition:
        if condition not in rules:
            return {}
        return _build(condition)

    return [_build(cond) for cond in sorted(rules.keys())]


def applicable_for_claim(claim_id: str, fmap=None) -> list[str]:
    """Return conditions applicable to a specific claim."""
    from scoped_prerequisite_inheritance import compute_inheritance
    inh = compute_inheritance(claim_id, fmap=fmap)
    return inh["applicable_prerequisites"]


def bypassed_for_claim(claim_id: str, fmap=None) -> list[str]:
    """Return scoped conditions bypassed by a specific claim."""
    from scoped_prerequisite_inheritance import compute_inheritance
    inh = compute_inheritance(claim_id, fmap=fmap)
    return inh["bypassed_prerequisites"]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli():
    import argparse
    ap = argparse.ArgumentParser(description="Full scoped prerequisite snapshot")
    ap.add_argument("--condition", help="specific prerequisite")
    ap.add_argument("--claim-id",  help="show applicability for a specific claim")
    ap.add_argument("--json",      action="store_true")
    args = ap.parse_args()

    if args.claim_id:
        from scoped_prerequisite_inheritance import compute_inheritance
        result = compute_inheritance(args.claim_id)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            _print_inheritance(result)
        return

    result = scoped_snapshot(args.condition)
    if args.json:
        print(json.dumps(result, indent=2))
        return

    records = [result] if isinstance(result, dict) else result
    if not records:
        print("No scoped prerequisites.")
    for r in records:
        _print_scoped(r)
        print()


def _print_scoped(r: dict):
    cond   = r["condition"]
    scope  = r["new_scope"]
    surv   = r["survivability"]
    status = r["survivability_status"]
    s_str  = f"{surv:.4f}" if surv is not None else "N/A"

    print(f"◈ {cond}  [scoped: {scope}]  survivability={s_str} ({status})")
    print(f"  applies_to:   {r['applies_to_label']}")
    print(f"  bypassed_by:  {r['bypassed_by_labels']}")
    print()
    print(f"  applicable ({len(r['applicable_claims'])}): {r['applicable_claims']}")
    for cid in r["applicable_claims"]:
        det = r["claim_details"][cid]
        rsn = "; ".join(det.get("scope_reasoning", []))
        print(f"    ✓ {cid}:  {rsn}")

    if r["bypassed_claims"]:
        print()
        print(f"  bypassed   ({len(r['bypassed_claims'])}): {r['bypassed_claims']}")
        for cid in r["bypassed_claims"]:
            det  = r["claim_details"][cid]
            bypc = ", ".join(det.get("bypass_conditions_found", []))
            print(f"    ⊛ {cid}:  bypass via [{bypc}]")

    if r["conflicts"]:
        print()
        print(f"  ⚠ scope conflicts ({len(r['conflicts'])}):")
        for c in r["conflicts"]:
            print(f"    {c['claim_id']}: {c['reason']}")


def _print_inheritance(r: dict):
    cid = r["claim_id"]
    print(f"{cid}:")
    for cond in r["applicable_prerequisites"]:
        rsn = "; ".join(r["scope_reasoning"].get(cond, []))
        print(f"  ✓ applicable:  {cond}  ({rsn})")
    for cond in r["bypassed_prerequisites"]:
        rsn = "; ".join(r["scope_reasoning"].get(cond, []))
        print(f"  ⊛ bypassed:    {cond}  ({rsn})")
    for cond in r["unscoped_prerequisites"]:
        print(f"  ◆ unscoped:    {cond}  [universally applicable]")


if __name__ == "__main__":
    _cli()
