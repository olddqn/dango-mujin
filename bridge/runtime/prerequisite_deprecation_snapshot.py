"""
prerequisite_deprecation_snapshot.py

Full lifecycle query for federation prerequisites:
  - current lifecycle state (promoted / weakened / reaffirmed / contested / deprecated)
  - survivability score + status band
  - bypass evidence (which claims, which equivalent conditions)
  - reevaluation recommendation

This is the top-level query module for the deprecation lifecycle.
It delegates computation to:
  prerequisite_reevaluation.py      — lifecycle synthesis
  prerequisite_survivability.py     — score
  prerequisite_deprecation_detector.py — bypass patterns
  prerequisite_alternative_plan.py  — alternative plan details

stdlib only. Read-only.
"""

import json
import os
import sys

_BRIDGE = os.path.dirname(os.path.abspath(__file__))


def _sutable_path(table: str) -> str:
    base = os.path.dirname(_BRIDGE)
    p = os.path.join(base, "sutable", f"{table}.jsonl")
    if os.path.exists(p):
        return p
    p2 = os.path.normpath(os.path.join(_BRIDGE, "..", "sutable", f"{table}.jsonl"))
    if os.path.exists(p2):
        return p2
    return p


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

def deprecation_snapshot(condition: str = None, fmap=None) -> dict | list[dict]:
    """
    Return full deprecation lifecycle snapshot.

    If condition is given, returns a single dict.
    Otherwise returns a list of all promoted prerequisites.

    Each record contains:
    {
      "condition":             str,
      "lifecycle_state":       str,
      "survivability":         float | None,
      "survivability_status":  str,
      "requiring_count":       int,
      "bypassing_count":       int,
      "weakening_candidate":   bool,
      "deprecation_candidate": bool,
      "recommended_action":    str,
      "bypass_details":        list[dict],
      "lifecycle_events":      list[dict],
      "new_scope":             str | None,   # set if weakened
    }
    """
    sys.path.insert(0, _BRIDGE)
    from prerequisite_reevaluation        import reevaluate, reevaluate_all
    from prerequisite_deprecation_detector import detect_bypass_patterns

    fm = _load_fmap(fmap)
    fed_events = fm["federation"]

    def _build(cond: str) -> dict:
        rev  = reevaluate(cond, fmap=fm)
        bp   = detect_bypass_patterns(cond, fmap=fm)

        # Find new_scope from the weakened event, if any
        new_scope = None
        for ev in fed_events:
            if (ev.get("event_type") == "federation_prerequisite_weakened"
                    and ev.get("condition") == cond):
                new_scope = ev.get("new_scope")
                break

        return {
            "condition":             cond,
            "lifecycle_state":       rev["lifecycle_state"],
            "survivability":         rev["survivability"],
            "survivability_status":  rev["survivability_status"],
            "requiring_count":       rev["requiring_count"],
            "bypassing_count":       rev["bypass_count"],
            "weakening_candidate":   rev["weakening_candidate"],
            "deprecation_candidate": rev["deprecation_candidate"],
            "recommended_action":    rev["recommended_action"],
            "bypass_details":        bp.get("bypass_details", []),
            "lifecycle_events":      rev["lifecycle_events"],
            "new_scope":             new_scope,
        }

    if condition:
        return _build(condition)

    results = reevaluate_all(fmap=fm)
    return [_build(r["condition"]) for r in results]


def weakened_prerequisites(fmap=None) -> list[str]:
    """Return conditions currently in 'weakened' lifecycle state."""
    results = deprecation_snapshot(fmap=fmap)
    if isinstance(results, dict):
        results = [results]
    return [r["condition"] for r in results if r["lifecycle_state"] == "weakened"]


def deprecated_prerequisites(fmap=None) -> list[str]:
    """Return conditions currently in 'deprecated' lifecycle state."""
    results = deprecation_snapshot(fmap=fmap)
    if isinstance(results, dict):
        results = [results]
    return [r["condition"] for r in results if r["lifecycle_state"] == "deprecated"]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli():
    import argparse
    ap = argparse.ArgumentParser(description="Full deprecation lifecycle snapshot for prerequisites")
    ap.add_argument("--condition",  help="specific prerequisite to inspect")
    ap.add_argument("--weakened",   action="store_true", help="list weakened prerequisites only")
    ap.add_argument("--deprecated", action="store_true", help="list deprecated prerequisites only")
    ap.add_argument("--json",       action="store_true", help="output JSON")
    args = ap.parse_args()

    if args.weakened:
        result = weakened_prerequisites()
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("Weakened prerequisites:", result or "(none)")
        return

    if args.deprecated:
        result = deprecated_prerequisites()
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("Deprecated prerequisites:", result or "(none)")
        return

    result = deprecation_snapshot(args.condition)
    if args.json:
        print(json.dumps(result, indent=2))
        return

    records = [result] if isinstance(result, dict) else result
    if not records:
        print("No promoted prerequisites.")
    for r in records:
        _print_snapshot(r)
        print()


def _print_snapshot(r: dict):
    cond   = r["condition"]
    state  = r["lifecycle_state"]
    score  = r["survivability"]
    status = r["survivability_status"]

    state_icons = {
        "promoted":   "◆ ",
        "reaffirmed": "◆◆",
        "weakened":   "◈ ",
        "contested":  "◇ ",
        "deprecated": "✗ ",
    }
    icon      = state_icons.get(state, "? ")
    score_str = f"{score:.4f}" if score is not None else "N/A"
    scope_str = f"  new_scope: {r['new_scope']}" if r.get("new_scope") else ""

    print(f"{icon} {cond}")
    print(f"   lifecycle:     {state}{scope_str}")
    print(f"   survivability: {score_str}  [{status}]")
    print(f"   requiring:     {r['requiring_count']}  bypassing: {r['bypassing_count']}")
    if r.get("deprecation_candidate"):
        print(f"   ⚠  DEPRECATION CANDIDATE")
    elif r.get("weakening_candidate"):
        print(f"   ~  weakening candidate")
    print(f"   → {r['recommended_action']}")

    if r["bypass_details"]:
        print(f"   bypass evidence:")
        for d in r["bypass_details"]:
            equiv = ", ".join(d.get("equivalent_conditions", []))
            print(f"     ✓ {d['claim_id']}  plan={d['plan_id']}  equiv=[{equiv}]")

    if r["lifecycle_events"]:
        print(f"   events ({len(r['lifecycle_events'])}):")
        for ev in r["lifecycle_events"]:
            ts = ev.get("timestamp", "")[:10]
            print(f"     {ev['event_type']}  {ts}  {ev.get('hash', '')}")


if __name__ == "__main__":
    _cli()
