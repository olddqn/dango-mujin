"""
prerequisite_survivability.py

Computes a survivability score for each promoted federation prerequisite.

Survivability measures how strongly the prerequisite is still warranted
given the current distribution of requiring vs. bypassing claims.

Formula (transparent — no hidden ranking):
  base      = requiring_count / (requiring_count + bypassing_count)
  penalty   = 0.15  if shared_objector (objector concentration)
  score     = base - penalty    (floor: 0.0)

Status bands:
  score >= 0.80  →  "strong"
  score >= 0.50  →  "weakened"
  score >= 0.20  →  "at_risk"
  score  < 0.20  →  "deprecated_candidate"

Design principles:
  - Score is a derived metric, not a decision maker.
  - Callers (weakening.py, reevaluation.py) decide what events to write.
  - No auto-removal. No governance vote. stdlib only. Read-only.

When requiring_count + bypassing_count == 0 (no claims with active plans),
survivability is treated as undefined ("no_data").
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
# Score bands
# ---------------------------------------------------------------------------

STRONG             = 0.80
WEAKENED_THRESHOLD = 0.50
AT_RISK_THRESHOLD  = 0.20

OBJECTOR_PENALTY   = 0.15


def _status_label(score: float) -> str:
    if score >= STRONG:
        return "strong"
    if score >= WEAKENED_THRESHOLD:
        return "weakened"
    if score >= AT_RISK_THRESHOLD:
        return "at_risk"
    return "deprecated_candidate"


def _shared_objector(condition: str, fed_events: list[dict]) -> bool:
    """
    Return True if the promoted event for this condition has shared_objector=True.
    """
    for ev in fed_events:
        if (ev.get("event_type") == "federation_prerequisite_promoted"
                and ev.get("condition") == condition):
            return bool(ev.get("shared_objector", False))
    return False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compute_survivability(condition: str, fmap=None) -> dict:
    """
    Compute survivability for a single promoted prerequisite.

    Returns:
    {
      "condition":          str,
      "requiring_count":    int,
      "bypassing_count":    int,
      "base_score":         float,
      "objector_penalty":   float,
      "survivability":      float,
      "status":             str,   # strong / weakened / at_risk / deprecated_candidate / no_data
      "shared_objector":    bool,
      "requiring_claims":   list[str],
      "bypassing_claims":   list[str],
    }
    """
    sys.path.insert(0, _BRIDGE)
    from prerequisite_deprecation_detector import detect_bypass_patterns

    fm = _load_fmap(fmap)
    bp = detect_bypass_patterns(condition, fmap=fm)

    if "error" in bp:
        return {
            "condition":        condition,
            "error":            bp["error"],
            "survivability":    None,
            "status":           "no_data",
            "requiring_count":  0,
            "bypassing_count":  0,
            "base_score":       None,
            "objector_penalty": 0.0,
            "shared_objector":  False,
            "requiring_claims": [],
            "bypassing_claims": [],
        }

    req_count = len(bp["requiring_claims"])
    byp_count = len(bp["bypassing_claims"])
    total     = req_count + byp_count

    if total == 0:
        return {
            "condition":        condition,
            "survivability":    None,
            "status":           "no_data",
            "requiring_count":  0,
            "bypassing_count":  0,
            "base_score":       None,
            "objector_penalty": 0.0,
            "shared_objector":  False,
            "requiring_claims": [],
            "bypassing_claims": [],
        }

    shared_obj  = _shared_objector(condition, fm["federation"])
    base_score  = req_count / total
    penalty     = OBJECTOR_PENALTY if shared_obj else 0.0
    survivability = max(0.0, base_score - penalty)

    return {
        "condition":        condition,
        "requiring_count":  req_count,
        "bypassing_count":  byp_count,
        "base_score":       round(base_score, 4),
        "objector_penalty": penalty,
        "survivability":    round(survivability, 4),
        "status":           _status_label(survivability),
        "shared_objector":  shared_obj,
        "requiring_claims": bp["requiring_claims"],
        "bypassing_claims": bp["bypassing_claims"],
    }


def compute_all_survivability(fmap=None) -> list[dict]:
    """
    Compute survivability for all promoted prerequisites.
    Returns list ordered by survivability ascending (most at-risk first).
    """
    fm = _load_fmap(fmap)
    from prerequisite_deprecation_detector import detect_all_bypass_patterns
    sys.path.insert(0, _BRIDGE)
    patterns = detect_all_bypass_patterns(fmap=fm)
    results  = [compute_survivability(r["condition"], fmap=fm) for r in patterns]
    # Sort by survivability ascending (None goes last)
    return sorted(results, key=lambda r: (r["survivability"] is None, r.get("survivability") or 1.0))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli():
    import argparse
    ap = argparse.ArgumentParser(description="Compute survivability scores for promoted prerequisites")
    ap.add_argument("--condition", help="specific prerequisite to inspect")
    ap.add_argument("--json",      action="store_true", help="output JSON")
    args = ap.parse_args()

    if args.condition:
        result = compute_survivability(args.condition)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            _print_survivability(result)
    else:
        results = compute_all_survivability()
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            if not results:
                print("No promoted prerequisites.")
            for r in results:
                _print_survivability(r)
                print()


def _print_survivability(r: dict):
    cond = r["condition"]
    if "error" in r:
        print(f"{cond}: {r['error']}")
        return
    score  = r["survivability"]
    status = r["status"]
    band_map = {
        "strong":               "●●●● strong",
        "weakened":             "●●●○ weakened",
        "at_risk":              "●●○○ at_risk",
        "deprecated_candidate": "●○○○ deprecated_candidate",
        "no_data":              "○○○○ no_data",
    }
    band = band_map.get(status, status)
    score_str = f"{score:.4f}" if score is not None else "N/A"
    print(f"{cond}:  survivability={score_str}  [{band}]")
    print(f"  base={r.get('base_score', 'N/A')}  penalty={r['objector_penalty']}  shared_objector={r['shared_objector']}")
    print(f"  requiring ({r['requiring_count']}): {r['requiring_claims']}")
    print(f"  bypassing ({r['bypassing_count']}): {r['bypassing_claims']}")


if __name__ == "__main__":
    _cli()
