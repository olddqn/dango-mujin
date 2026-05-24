"""
prerequisite_weakening.py

Appends federation_prerequisite_weakened events when a promoted prerequisite
has been successfully bypassed by at least one claim using equivalent safety
conditions.

Weakening does NOT deprecate the prerequisite — it narrows its scope.
The prerequisite remains active for claims that lack the equivalent safety path.

Event appended: federation_prerequisite_weakened
  condition:        the prerequisite being narrowed
  new_scope:        "non_precertified_spaces"  (or equivalent narrowing label)
  reason:           "equivalent_safe_alternative_detected"
  bypassing_claims: [list of claims that bypassed]
  equivalent_safety_conditions: [conditions that constitute the safe alternative]
  authority:        "none"   (always — never overrideable)
  contestable:      True     (always — never overrideable)

Design:
  Weakening is idempotent: if a weakened event already exists for the condition,
  this module does nothing (append-only dedup).

  A second bypass claim does not create a second weakened event.
  The weakened status is superseded by deprecated when deprecation_candidate
  is True and the requisite evidence exists.

stdlib only. Writes to sutable/federation.jsonl.
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
# Scope labels: how a prerequisite is narrowed when an equivalent path exists
# ---------------------------------------------------------------------------

SCOPE_LABELS: dict[str, str] = {
    "space_safety_assessed": "non_precertified_spaces",
    "food_safety_reviewed":  "non_certified_food_operations",
}

DEFAULT_SCOPE = "non_precertified_cases"


# ---------------------------------------------------------------------------
# Build and append
# ---------------------------------------------------------------------------

def build_weakening_event(
    condition: str,
    bypassing_claims: list[str],
    equivalent_safety_conditions: list[str],
    *,
    reason: str = "equivalent_safe_alternative_detected",
    speaker: str = "did:key:zSystemDetector",
) -> dict:
    """
    Construct (but do not write) a federation_prerequisite_weakened event.
    authority is always "none". contestable is always True.
    """
    new_scope = SCOPE_LABELS.get(condition, DEFAULT_SCOPE)
    return {
        "event_type":                  "federation_prerequisite_weakened",
        "condition":                   condition,
        "new_scope":                   new_scope,
        "reason":                      reason,
        "bypassing_claims":            sorted(bypassing_claims),
        "equivalent_safety_conditions": sorted(equivalent_safety_conditions),
        "promotion_basis":             "independent_plan_tree_diff_convergence",
        "authority":                   "none",
        "contestable":                 True,
        "speaker":                     speaker,
    }


def compute_weakening_candidates(fmap=None) -> list[dict]:
    """
    Return list of {condition, bypassing_claims, equivalent_safety_conditions}
    for prerequisites that are weakening_candidates AND not already weakened.
    """
    sys.path.insert(0, _BRIDGE)
    from prerequisite_deprecation_detector import weakening_candidates as _wk_cands

    fm = _load_fmap(fmap)
    candidates = _wk_cands(fmap=fm)

    result = []
    for c in candidates:
        cond = c["condition"]
        bypassing = c["bypassing_claims"]
        equiv = []
        for detail in c.get("bypass_details", []):
            equiv.extend(detail.get("equivalent_conditions", []))
        equiv = sorted(set(equiv))
        result.append({
            "condition":                   cond,
            "bypassing_claims":            bypassing,
            "equivalent_safety_conditions": equiv,
        })
    return result


def append_weakening_events(
    candidates=None,
    *,
    dry_run: bool = True,
    verbose: bool = False,
    speaker: str = "did:key:zSystemDetector",
    fmap=None,
) -> list[dict]:
    """
    Build and append weakening events for all candidates.

    Parameters:
      candidates: output of compute_weakening_candidates() — if None, computed fresh.
      dry_run: if True, print preview but do not write.
      verbose: print event details.
      speaker: DID for the weakening event.

    Returns list of events that were (or would be) appended.
    """
    sys.path.insert(0, _BRIDGE)
    from sutable_log import append_event

    fm = _load_fmap(fmap)
    if candidates is None:
        candidates = compute_weakening_candidates(fmap=fm)

    appended = []
    for c in candidates:
        event = build_weakening_event(
            c["condition"],
            c["bypassing_claims"],
            c["equivalent_safety_conditions"],
            speaker=speaker,
        )
        if dry_run:
            if verbose:
                print(f"[dry-run] would append: {json.dumps(event, indent=2)}")
            else:
                print(f"[dry-run] federation_prerequisite_weakened  {c['condition']}"
                      f"  new_scope={event['new_scope']}"
                      f"  bypassing={c['bypassing_claims']}")
        else:
            written = append_event("federation", event)
            appended.append(written)
            if verbose:
                print(f"Appended: federation_prerequisite_weakened  {c['condition']}"
                      f"  new_scope={event['new_scope']}"
                      f"  hash={written.get('event_hash','')[:12]}")
            else:
                print(f"Weakened: {c['condition']}  new_scope={event['new_scope']}")

    if not candidates:
        if verbose:
            print("No weakening candidates.")

    return appended


def weaken_prerequisites(
    *,
    dry_run: bool = True,
    verbose: bool = False,
    json_output: bool = False,
    speaker: str = "did:key:zSystemDetector",
) -> dict:
    """
    Top-level entry point. Detect + (optionally) append weakening events.

    Returns summary dict.
    """
    candidates = compute_weakening_candidates()
    if json_output and dry_run:
        events = [build_weakening_event(
            c["condition"], c["bypassing_claims"], c["equivalent_safety_conditions"],
            speaker=speaker,
        ) for c in candidates]
        print(json.dumps(events, indent=2))
        return {"dry_run": True, "candidates": candidates, "events": events}

    appended = append_weakening_events(candidates, dry_run=dry_run, verbose=verbose, speaker=speaker)
    return {
        "dry_run":    dry_run,
        "candidates": candidates,
        "appended":   appended,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli():
    import argparse
    ap = argparse.ArgumentParser(description="Append weakening events for bypassed prerequisites")
    ap.add_argument("--append",  action="store_true", help="write to federation.jsonl (default: dry-run)")
    ap.add_argument("--dry-run", action="store_true", help="preview only (default)")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--json",    action="store_true", help="output candidate events as JSON (implies dry-run)")
    ap.add_argument("--speaker", default="did:key:zSystemDetector",
                    help="DID for the weakening event speaker")
    args = ap.parse_args()

    dry_run = not args.append
    weaken_prerequisites(
        dry_run=dry_run,
        verbose=args.verbose,
        json_output=args.json,
        speaker=args.speaker,
    )


if __name__ == "__main__":
    _cli()
