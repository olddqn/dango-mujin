"""
scope_conflict_detector.py

Detects contradictory scope declarations in claim plans.

A scope conflict arises when a claim's active plan simultaneously asserts:
  - A bypass condition   (signals: "this space is precertified/exempt")
  - A local modification condition (signals: "this space is NOT precertified")

These are logically incompatible claims about the space's certification status.

Examples:
  precertified_structure  +  structural_modification_documented
  → Cannot simultaneously be "pre-certified as-built" and "locally modified"

  external_safety_audit_attached  +  local_structural_assessment
  → An external audit would cover the same assessment — both asserting is contradictory

This module does NOT block any plan. It reports conflicts as advisory warnings.
The plan can still be submitted, negotiated, and selected.

No authority. No hidden logic. No enforcement. stdlib only. Read-only.
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
        "plans":  _read_jsonl(_sutable_path("plans")),
        "memory": _read_jsonl(_sutable_path("memory")),
        "federation": _read_jsonl(_sutable_path("federation")),
    }


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def detect_conflicts(claim_id: str, fmap=None) -> list[dict]:
    """
    Detect scope conflicts for a single claim.

    Returns list of conflict records:
    {
      "condition":      str,   # the prerequisite whose scope is conflicted
      "claim_id":       str,
      "conflict":       True,
      "bypass_condition_found":       str,  # the bypass-signalling condition
      "local_indicator_found":        str,  # the local-modification condition
      "reason":                       str,  # human-readable explanation
      "advisory":                     True, # conflicts are advisory, not blocking
    }
    """
    from prerequisite_scope_resolver import (
        SCOPE_CONFLICT_PAIRS,
        load_scope_rules,
        _active_plan_conditions,
    )

    fm = _load_fmap(fmap)
    rules = load_scope_rules(fmap=fm)
    all_plans = _active_plan_conditions(fm["plans"])
    plan_conds = all_plans.get(claim_id, set())

    conflicts = []
    for cond in rules:
        for bypass_cond, local_cond in SCOPE_CONFLICT_PAIRS:
            if bypass_cond in plan_conds and local_cond in plan_conds:
                conflicts.append({
                    "condition":              cond,
                    "claim_id":              claim_id,
                    "conflict":              True,
                    "bypass_condition_found": bypass_cond,
                    "local_indicator_found":  local_cond,
                    "reason": (
                        f"plan declares both '{bypass_cond}' (bypass indicator) "
                        f"and '{local_cond}' (local modification indicator) — "
                        f"logically incompatible space type assertions"
                    ),
                    "advisory": True,
                })

    return conflicts


def detect_all_conflicts(fmap=None) -> dict[str, list[dict]]:
    """
    Detect scope conflicts across all claims with active plans.
    Returns: {claim_id: [conflict_records]}
    """
    from prerequisite_scope_resolver import _active_plan_conditions

    fm = _load_fmap(fmap)
    all_plans = _active_plan_conditions(fm["plans"])
    return {
        cid: detect_conflicts(cid, fmap=fm)
        for cid in sorted(all_plans.keys())
    }


def any_conflicts(fmap=None) -> bool:
    """Return True if any claim has a scope conflict."""
    all_c = detect_all_conflicts(fmap)
    return any(bool(v) for v in all_c.values())


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli():
    import argparse
    ap = argparse.ArgumentParser(description="Detect scope conflicts in claim plans")
    ap.add_argument("--claim-id", help="specific claim to check")
    ap.add_argument("--json",     action="store_true")
    args = ap.parse_args()

    if args.claim_id:
        conflicts = detect_conflicts(args.claim_id)
        if args.json:
            print(json.dumps(conflicts, indent=2))
        else:
            _print_conflicts(args.claim_id, conflicts)
    else:
        all_c = detect_all_conflicts()
        if args.json:
            print(json.dumps(all_c, indent=2))
        else:
            found = False
            for cid, conflicts in all_c.items():
                if conflicts:
                    found = True
                    _print_conflicts(cid, conflicts)
            if not found:
                print("No scope conflicts detected.")


def _print_conflicts(cid: str, conflicts: list[dict]):
    if not conflicts:
        print(f"  {cid}: no scope conflicts")
        return
    for c in conflicts:
        print(f"  ⚠ {cid}  conflict on: {c['condition']}")
        print(f"      bypass indicator:   {c['bypass_condition_found']}")
        print(f"      local indicator:    {c['local_indicator_found']}")
        print(f"      reason:             {c['reason']}")
        print(f"      advisory: True — plan is not blocked")


if __name__ == "__main__":
    _cli()
