"""
prerequisite_reevaluation.py

Synthesises all available signals for each promoted federation prerequisite
and produces a reevaluation record: current lifecycle state, survivability,
bypass evidence, and recommended next step.

This is a read-only synthesis module. It writes nothing.
Decisions (contest, weaken, deprecate) belong to callers.

Reevaluation outcomes (one per prerequisite):
  "reaffirmed"   — strong survivability, reaffirm event present
  "weakened"     — weakening event present; still active for non-bypassed cases
  "deprecated"   — federation_prerequisite_deprecated event present
  "at_risk"      — bypass evidence exists but below deprecation threshold
  "contested"    — contested event present, awaiting resolution
  "unresolved"   — promoted, no bypass evidence, no reaffirm event yet

stdlib only. No external libraries. Read-only.
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
# Lifecycle event type constants
# ---------------------------------------------------------------------------

EV_PROMOTED   = "federation_prerequisite_promoted"
EV_CONTESTED  = "federation_prerequisite_contested"
EV_REAFFIRMED = "federation_prerequisite_reaffirmed"
EV_DEPRECATED = "federation_prerequisite_deprecated"
EV_WEAKENED   = "federation_prerequisite_weakened"

_ALL_LIFECYCLE = {EV_PROMOTED, EV_CONTESTED, EV_REAFFIRMED, EV_DEPRECATED, EV_WEAKENED}


def _collect_condition_events(condition: str, fed_events: list[dict]) -> list[dict]:
    """Return all lifecycle events for a condition in chronological order."""
    return [
        ev for ev in fed_events
        if ev.get("condition") == condition and ev.get("event_type") in _ALL_LIFECYCLE
    ]


def _promoted_conditions(fed_events: list[dict]) -> list[str]:
    """Return conditions that have been promoted and not deprecated."""
    promoted: set[str] = set()
    deprecated: set[str] = set()
    for ev in fed_events:
        et   = ev.get("event_type", "")
        cond = ev.get("condition", "")
        if not cond:
            continue
        if et == EV_PROMOTED:
            promoted.add(cond)
        elif et == EV_DEPRECATED:
            deprecated.add(cond)
    return sorted(promoted - deprecated)


# ---------------------------------------------------------------------------
# Lifecycle state resolution
# ---------------------------------------------------------------------------

def _resolve_lifecycle_state(events_for_condition: list[dict]) -> str:
    """
    Determine the current lifecycle state from the ordered event list.
    Later events take precedence, with the priority order:
      deprecated > weakened > reaffirmed > contested > promoted
    """
    state = "promoted"  # must have at least one promoted event to be here
    for ev in events_for_condition:
        et = ev.get("event_type", "")
        if et == EV_DEPRECATED:
            state = "deprecated"
        elif et == EV_WEAKENED and state != "deprecated":
            state = "weakened"
        elif et == EV_REAFFIRMED and state not in ("deprecated", "weakened"):
            state = "reaffirmed"
        elif et == EV_CONTESTED and state not in ("deprecated", "weakened", "reaffirmed"):
            state = "contested"
    return state


def _recommended_action(
    lifecycle_state: str,
    survivability_status: str,
    deprecation_candidate: bool,
    weakening_candidate: bool,
) -> str:
    """Derive a human-readable recommended next step. No auto-action."""
    if lifecycle_state == "deprecated":
        return "none — already deprecated"
    if lifecycle_state == "weakened":
        if deprecation_candidate:
            return "consider deprecation — bypass_count >= threshold with equivalent safety"
        return "monitor — weakened scope; watch for additional bypass evidence"
    if lifecycle_state == "contested":
        return "resolve contest — submit alternative plan tree or reaffirm with new evidence"
    if lifecycle_state == "reaffirmed":
        if weakening_candidate:
            return "consider weakening — bypass evidence detected despite reaffirmation"
        return "monitor — prerequisite remains strong"
    # promoted / default
    if deprecation_candidate:
        return "consider deprecation — bypass_count >= threshold with equivalent safety"
    if weakening_candidate:
        return "run prerequisite_weakening.py --append to narrow scope"
    if survivability_status in ("at_risk",):
        return "monitor — at_risk, approaching weakening threshold"
    return "monitor — prerequisite appears stable"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def reevaluate(condition: str, fmap=None) -> dict:
    """
    Synthesise all signals for a single prerequisite and return a reevaluation record.

    Returns:
    {
      "condition":             str,
      "lifecycle_state":       str,   # promoted/weakened/reaffirmed/contested/deprecated
      "survivability":         float | None,
      "survivability_status":  str,
      "bypass_count":          int,
      "requiring_count":       int,
      "weakening_candidate":   bool,
      "deprecation_candidate": bool,
      "recommended_action":    str,
      "lifecycle_events":      list[dict],   # summary of events
    }
    """
    sys.path.insert(0, _BRIDGE)
    from prerequisite_survivability        import compute_survivability
    from prerequisite_deprecation_detector import detect_bypass_patterns

    fm = _load_fmap(fmap)
    fed_events = fm["federation"]

    cond_events = _collect_condition_events(condition, fed_events)
    lifecycle_state = _resolve_lifecycle_state(cond_events)

    surv = compute_survivability(condition, fmap=fm)
    bp   = detect_bypass_patterns(condition, fmap=fm)

    surv_score  = surv.get("survivability")
    surv_status = surv.get("status", "no_data")
    wk_cand     = bp.get("weakening_candidate",   False)
    dep_cand    = bp.get("deprecation_candidate", False)

    recommended = _recommended_action(lifecycle_state, surv_status, dep_cand, wk_cand)

    # Compact event summary
    event_summary = [
        {
            "event_type": ev.get("event_type"),
            "timestamp":  ev.get("timestamp", ""),
            "hash":       ev.get("event_hash", "")[:12],
        }
        for ev in cond_events
    ]

    return {
        "condition":             condition,
        "lifecycle_state":       lifecycle_state,
        "survivability":         surv_score,
        "survivability_status":  surv_status,
        "bypass_count":          bp.get("bypass_count", 0),
        "requiring_count":       len(bp.get("requiring_claims", [])),
        "weakening_candidate":   wk_cand,
        "deprecation_candidate": dep_cand,
        "recommended_action":    recommended,
        "lifecycle_events":      event_summary,
    }


def reevaluate_all(fmap=None) -> list[dict]:
    """
    Reevaluate all promoted prerequisites.
    Returns list ordered by survivability ascending (most at-risk first).
    """
    fm = _load_fmap(fmap)
    conditions = _promoted_conditions(fm["federation"])
    results = [reevaluate(cond, fmap=fm) for cond in conditions]
    return sorted(
        results,
        key=lambda r: (r["survivability"] is None, r.get("survivability") or 1.0),
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli():
    import argparse
    ap = argparse.ArgumentParser(description="Reevaluate federation prerequisite lifecycle signals")
    ap.add_argument("--condition", help="specific prerequisite to reevaluate")
    ap.add_argument("--json",      action="store_true", help="output JSON")
    args = ap.parse_args()

    if args.condition:
        result = reevaluate(args.condition)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            _print_reevaluation(result)
    else:
        results = reevaluate_all()
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            if not results:
                print("No promoted prerequisites to reevaluate.")
            for r in results:
                _print_reevaluation(r)
                print()


def _print_reevaluation(r: dict):
    cond   = r["condition"]
    state  = r["lifecycle_state"]
    score  = r["survivability"]
    status = r["survivability_status"]
    action = r["recommended_action"]
    score_str = f"{score:.4f}" if score is not None else "N/A"

    state_icons = {
        "promoted":   "◆",
        "reaffirmed": "◆◆",
        "weakened":   "◈",
        "contested":  "◇",
        "deprecated": "✗",
    }
    icon = state_icons.get(state, "?")

    print(f"{icon} {cond}  [{state}]  survivability={score_str}  ({status})")
    print(f"  requiring={r['requiring_count']}  bypassing={r['bypass_count']}")
    print(f"  weakening_candidate={r['weakening_candidate']}  deprecation_candidate={r['deprecation_candidate']}")
    print(f"  → {action}")
    if r["lifecycle_events"]:
        print(f"  events ({len(r['lifecycle_events'])}):")
        for ev in r["lifecycle_events"]:
            ts = ev["timestamp"][:10] if ev.get("timestamp") else ""
            print(f"    {ev['event_type']}  {ts}  {ev['hash']}")


if __name__ == "__main__":
    _cli()
