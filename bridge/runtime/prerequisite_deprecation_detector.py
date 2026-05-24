"""
prerequisite_deprecation_detector.py

Monitors promoted federation prerequisites for bypass patterns.
Produces weakening and deprecation candidates based on how many claims
successfully bypass a prerequisite with equivalent safety conditions.

No auto-removal. No centralized override. No hidden scoring.
Read-only — writes nothing. stdlib only.

Thresholds:
  bypass_claims >= 1 AND equivalent_safety = True  → weakening_candidate
  bypass_claims >= 2 AND equivalent_safety = True  → deprecation_candidate

Design note:
  A "bypass" only counts when the alternative plan includes a recognised
  equivalent safety condition. A plan that simply omits the prerequisite
  without any equivalent safety is not a bypass — it's a gap.

  This distinction prevents low-effort plans from triggering deprecation.
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


# Thresholds
WEAKENING_BYPASS_THRESHOLD    = 1   # bypass_claims >= 1 AND equivalent_safety
DEPRECATION_BYPASS_THRESHOLD  = 2   # bypass_claims >= 2 AND equivalent_safety


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _promoted_conditions(fed_events: list[dict]) -> dict[str, dict]:
    """
    Return {condition: promoted_event} for prerequisites currently in
    promoted/reaffirmed/weakened state (not deprecated).
    """
    promoted: dict[str, dict] = {}
    deprecated: set[str] = set()
    for ev in fed_events:
        et   = ev.get("event_type", "")
        cond = ev.get("condition", "")
        if not cond:
            continue
        if et == "federation_prerequisite_promoted":
            promoted[cond] = ev
        elif et == "federation_prerequisite_deprecated":
            deprecated.add(cond)
    for cond in deprecated:
        promoted.pop(cond, None)
    return promoted


def _already_weakened(condition: str, fed_events: list[dict]) -> bool:
    """Return True if a federation_prerequisite_weakened event exists for condition."""
    for ev in fed_events:
        if (ev.get("event_type") == "federation_prerequisite_weakened"
                and ev.get("condition") == condition):
            return True
    return False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def detect_bypass_patterns(condition: str, fmap=None) -> dict:
    """
    For a single promoted prerequisite, analyse how many claims bypass it
    with equivalent safety conditions vs. how many require it.

    Returns:
    {
      "condition":              str,
      "requiring_claims":       list[str],  # active plans include condition
      "bypassing_claims":       list[str],  # bypass with equivalent safety
      "gap_claims":             list[str],  # omit condition WITHOUT equiv safety
      "bypass_count":           int,
      "equivalent_safety":      bool,       # True if any bypass has equiv safety
      "weakening_candidate":    bool,
      "deprecation_candidate":  bool,
      "already_weakened":       bool,
      "bypass_details":         list[dict], # from prerequisite_alternative_plan
    }
    """
    fm = _load_fmap(fmap)

    # Import here to avoid circular dependency
    sys.path.insert(0, _BRIDGE)
    from prerequisite_alternative_plan import (
        detect_alternative_plans,
        _claim_plan_conditions,
        _promoted_conditions as _alt_promoted,
    )

    promoted = _promoted_conditions(fm["federation"])
    if condition not in promoted:
        return {
            "condition":             condition,
            "error":                 "not_a_promoted_condition",
            "requiring_claims":      [],
            "bypassing_claims":      [],
            "gap_claims":            [],
            "bypass_count":          0,
            "equivalent_safety":     False,
            "weakening_candidate":   False,
            "deprecation_candidate": False,
            "already_weakened":      False,
            "bypass_details":        [],
        }

    # Get bypass records (equivalent safety confirmed)
    bypass_records = detect_alternative_plans(condition, fmap=fm)
    bypass_claim_ids = {r["claim_id"] for r in bypass_records}

    # Get all claims with active plans
    claim_plans = _claim_plan_conditions(fm["plans"])

    requiring_claims = []
    gap_claims       = []

    for cid, info in claim_plans.items():
        if cid in bypass_claim_ids:
            continue  # already counted as bypass
        if condition in info["conditions"]:
            requiring_claims.append(cid)
        # else: omits condition but not in bypass_records — only a gap if
        # the claim has a plan at all (which it does, since it's in claim_plans)
        else:
            # Check if they have any equiv safety (counted in bypass_records)
            # If not in bypass_records and condition not in conditions → gap
            gap_claims.append(cid)

    bypass_count      = len(bypass_claim_ids)
    equivalent_safety = any(r["equivalent_safety_found"] for r in bypass_records)
    already_wkn       = _already_weakened(condition, fm["federation"])

    weakening_candidate   = (bypass_count >= WEAKENING_BYPASS_THRESHOLD
                             and equivalent_safety
                             and not already_wkn)
    deprecation_candidate = (bypass_count >= DEPRECATION_BYPASS_THRESHOLD
                             and equivalent_safety)

    return {
        "condition":             condition,
        "requiring_claims":      sorted(requiring_claims),
        "bypassing_claims":      sorted(bypass_claim_ids),
        "gap_claims":            sorted(gap_claims),
        "bypass_count":          bypass_count,
        "equivalent_safety":     equivalent_safety,
        "weakening_candidate":   weakening_candidate,
        "deprecation_candidate": deprecation_candidate,
        "already_weakened":      already_wkn,
        "bypass_details":        bypass_records,
    }


def detect_all_bypass_patterns(fmap=None) -> list[dict]:
    """
    Run detect_bypass_patterns for all promoted prerequisites.
    Returns list of bypass pattern records, ordered by bypass_count desc.
    """
    fm = _load_fmap(fmap)
    promoted = _promoted_conditions(fm["federation"])
    results = [detect_bypass_patterns(cond, fmap=fm) for cond in promoted]
    return sorted(results, key=lambda r: r.get("bypass_count", 0), reverse=True)


def weakening_candidates(fmap=None) -> list[dict]:
    """Return only the records where weakening_candidate is True."""
    return [r for r in detect_all_bypass_patterns(fmap) if r.get("weakening_candidate")]


def deprecation_candidates(fmap=None) -> list[dict]:
    """Return only the records where deprecation_candidate is True."""
    return [r for r in detect_all_bypass_patterns(fmap) if r.get("deprecation_candidate")]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli():
    import argparse
    ap = argparse.ArgumentParser(
        description="Detect bypass patterns for promoted federation prerequisites"
    )
    ap.add_argument("--condition", help="specific prerequisite to inspect")
    ap.add_argument("--weakening-candidates",   action="store_true",
                    help="show only weakening candidates")
    ap.add_argument("--deprecation-candidates", action="store_true",
                    help="show only deprecation candidates")
    ap.add_argument("--json", action="store_true", help="output JSON")
    args = ap.parse_args()

    if args.condition:
        result = detect_bypass_patterns(args.condition)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            _print_bypass(result)
    elif args.weakening_candidates:
        results = weakening_candidates()
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            if not results:
                print("No weakening candidates.")
            for r in results:
                _print_bypass(r)
    elif args.deprecation_candidates:
        results = deprecation_candidates()
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            if not results:
                print("No deprecation candidates.")
            for r in results:
                _print_bypass(r)
    else:
        results = detect_all_bypass_patterns()
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            if not results:
                print("No promoted prerequisites.")
            for r in results:
                _print_bypass(r)
                print()


def _print_bypass(r: dict):
    cond = r["condition"]
    if "error" in r:
        print(f"{cond}: {r['error']}")
        return
    bcount = r["bypass_count"]
    wk     = "  ← WEAKENING CANDIDATE"   if r["weakening_candidate"]   else ""
    dep    = "  ← DEPRECATION CANDIDATE" if r["deprecation_candidate"] else ""
    wknd   = "  [already weakened]"       if r["already_weakened"]      else ""
    print(f"{cond}:")
    print(f"  requiring: {r['requiring_claims']}")
    print(f"  bypassing: {r['bypassing_claims']}  ({bcount} bypass(es), equiv_safety={r['equivalent_safety']}){wk}{dep}{wknd}")
    if r["gap_claims"]:
        print(f"  gap (no equiv): {r['gap_claims']}")
    for d in r["bypass_details"]:
        equiv = ", ".join(d["equivalent_conditions"]) if d["equivalent_conditions"] else "(none)"
        print(f"    ✓ {d['claim_id']}  plan={d['plan_id']}  equiv=[{equiv}]")


if __name__ == "__main__":
    _cli()
