#!/usr/bin/env python3
"""
federation_memory_feedback.py — dango-gitsea-bridge / federation branching

Compute federation-wide reflective memory feedback.

A single claim's memory records what its negotiation has learned.
Federation memory feedback extends this across related claims:

  - What objection types recur across multiple claims? (systemic pattern)
  - What conditions appear as learned across multiple claims? (federation gap)
  - What planning hints apply federation-wide?
  - Which claims share the same structural problems?

This module reads memory.jsonl snapshots for all claims in the federation
and synthesizes cross-claim insights.

Federation memory feedback is ADVISORY. It does not modify memory events.
Results can be appended to federation.jsonl as federation_memory_feedback events.

Planning hint example:
  {
    "hint": "risk_review should become a federation-level prerequisite",
    "hint_type": "federation_prerequisite",
    "triggered_by": ["housing-001", "housing-002"],
    "recurrence_count": 2,
  }

CLI:
  python runtime/federation_memory_feedback.py
  python runtime/federation_memory_feedback.py --json
  python runtime/federation_memory_feedback.py --append
  python runtime/federation_memory_feedback.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from sutable_log import read_all, append_event
from claim_federation import load_federation_events, build_federation_map

# ── Threshold ─────────────────────────────────────────────────────────────────

_RECURRENCE_THRESHOLD = 2   # must appear in ≥ this many claims to become a federation hint


# ── Memory loading ────────────────────────────────────────────────────────────

def _load_memory_snapshots() -> dict[str, dict[str, Any]]:
    """
    Return the latest memory snapshot per claim_id.
    { claim_id → latest memory_snapshot_created event }
    """
    latest: dict[str, dict[str, Any]] = {}
    for ev in read_all("memory"):
        if ev.get("event_type") != "memory_snapshot_created":
            continue
        cid = ev.get("claim_id", "")
        if cid:
            latest[cid] = ev   # last one wins (events are in append order)
    return latest


# ── Cross-claim analysis ──────────────────────────────────────────────────────

def _recurring_objection_types(
    snapshots: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Find objection types that recur across ≥ threshold claims."""
    type_to_claims: dict[str, list[str]] = {}

    for cid, snap in snapshots.items():
        for obj in snap.get("prior_objections", []):
            for otype in obj.get("by_type", {}):
                type_to_claims.setdefault(otype, [])
                if cid not in type_to_claims[otype]:
                    type_to_claims[otype].append(cid)

    return [
        {
            "objection_type":   otype,
            "recurrence_count": len(claims),
            "triggered_by":     sorted(claims),
        }
        for otype, claims in sorted(type_to_claims.items())
        if len(claims) >= _RECURRENCE_THRESHOLD
    ]


def _recurring_learned_conditions(
    snapshots: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Find conditions that were learned across ≥ threshold claims."""
    cond_to_claims: dict[str, list[str]] = {}

    for cid, snap in snapshots.items():
        for cond in snap.get("learned_conditions", []):
            cond_to_claims.setdefault(cond, [])
            if cid not in cond_to_claims[cond]:
                cond_to_claims[cond].append(cid)

    return [
        {
            "condition":        cond,
            "recurrence_count": len(claims),
            "triggered_by":     sorted(claims),
        }
        for cond, claims in sorted(cond_to_claims.items())
        if len(claims) >= _RECURRENCE_THRESHOLD
    ]


def _generate_planning_hints(
    recurring_objections: list[dict[str, Any]],
    recurring_conditions: list[dict[str, Any]],
    snapshots: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Synthesize planning hints from recurring patterns.

    Hint types:
      federation_prerequisite — condition should be required federation-wide
      shared_risk_pattern     — same objection type appears repeatedly
      correction_pattern      — high correction depth across multiple claims
    """
    hints: list[dict[str, Any]] = []

    # Recurring learned conditions → federation prerequisite
    for rc in recurring_conditions:
        hints.append({
            "hint":             (
                f"{rc['condition']!r} should become a federation-level prerequisite "
                f"(learned independently by {rc['recurrence_count']} claims)"
            ),
            "hint_type":        "federation_prerequisite",
            "condition":        rc["condition"],
            "triggered_by":     rc["triggered_by"],
            "recurrence_count": rc["recurrence_count"],
        })

    # Recurring objection types → shared risk pattern
    for ro in recurring_objections:
        hints.append({
            "hint":             (
                f"{ro['objection_type']!r} objections recur across "
                f"{ro['recurrence_count']} claims — consider a federation-wide "
                f"review for this objection type"
            ),
            "hint_type":        "shared_risk_pattern",
            "objection_type":   ro["objection_type"],
            "triggered_by":     ro["triggered_by"],
            "recurrence_count": ro["recurrence_count"],
        })

    # High correction depth across multiple claims
    high_correction_claims = [
        cid for cid, snap in snapshots.items()
        if snap.get("correction_chain_depth", 0) >= 2
    ]
    if len(high_correction_claims) >= _RECURRENCE_THRESHOLD:
        hints.append({
            "hint":             (
                f"Multiple claims ({len(high_correction_claims)}) have deep correction "
                f"chains — consider federation-wide plan quality review before proposing"
            ),
            "hint_type":        "correction_pattern",
            "triggered_by":     sorted(high_correction_claims),
            "recurrence_count": len(high_correction_claims),
        })

    return hints


# ── Core computation ──────────────────────────────────────────────────────────

def compute_federation_memory_feedback(
    fmap: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Compute federation-wide memory feedback from all memory snapshots.

    Returns:
      {
        "claims_with_memory":         [str, ...],
        "claims_without_memory":      [str, ...],
        "recurring_objection_types":  [{objection_type, recurrence_count, triggered_by}, ...],
        "recurring_learned_conditions": [{condition, recurrence_count, triggered_by}, ...],
        "planning_hints":             [{hint, hint_type, triggered_by, ...}, ...],
        "federation_summary":         str,
      }
    """
    snapshots   = _load_memory_snapshots()
    fed_events  = load_federation_events()
    if fmap is None:
        fmap = build_federation_map(fed_events)

    all_fed_claims = sorted(fmap.keys())
    with_memory    = sorted(k for k in snapshots if k in fmap)
    without_memory = sorted(c for c in all_fed_claims if c not in snapshots)

    # Also include claims not in federation but with memory (standalone claims)
    standalone_with_memory = sorted(k for k in snapshots if k not in fmap)

    all_snapshot_claims = dict(snapshots)

    recurring_obj  = _recurring_objection_types(all_snapshot_claims)
    recurring_cond = _recurring_learned_conditions(all_snapshot_claims)
    hints          = _generate_planning_hints(recurring_obj, recurring_cond, all_snapshot_claims)

    # Summary
    parts: list[str] = []
    if recurring_cond:
        parts.append(f"{len(recurring_cond)} shared learned condition(s)")
    if recurring_obj:
        parts.append(f"{len(recurring_obj)} recurring objection type(s)")
    if hints:
        parts.append(f"{len(hints)} planning hint(s)")
    federation_summary = "; ".join(parts) if parts else "no cross-claim patterns detected"

    return {
        "claims_with_memory":           with_memory,
        "claims_without_memory":        without_memory,
        "standalone_claims_with_memory": standalone_with_memory,
        "recurring_objection_types":    recurring_obj,
        "recurring_learned_conditions": recurring_cond,
        "planning_hints":               hints,
        "federation_summary":           federation_summary,
    }


# ── Build events ──────────────────────────────────────────────────────────────

def build_feedback_events(feedback: dict[str, Any]) -> list[dict[str, Any]]:
    """Build federation_memory_feedback events from planning hints."""
    return [
        {
            "event_type":       "federation_memory_feedback",
            "hint":             h["hint"],
            "hint_type":        h["hint_type"],
            "triggered_by":     h["triggered_by"],
            "recurrence_count": h["recurrence_count"],
        }
        for h in feedback.get("planning_hints", [])
    ]


def append_feedback_events(
    events: list[dict[str, Any]],
    *,
    dry_run: bool = False,
    verbose: bool = False,
) -> list[dict[str, Any]]:
    if not events:
        if verbose:
            print("No federation memory feedback events to append.", file=sys.stderr)
        return []
    written = []
    for ev in events:
        if dry_run:
            print(f"[DRY RUN] {ev['event_type']}  hint_type={ev['hint_type']}")
            written.append(ev)
        else:
            result = append_event("federation", ev)
            written.append(result)
            if verbose:
                print(f"✓ {result['event_type']}  {result['hint_type']}", file=sys.stderr)
    return written


# ── Display ───────────────────────────────────────────────────────────────────

def _print_feedback(fb: dict[str, Any]) -> None:
    print("Federation Memory Feedback")
    print(f"  claims with memory:    {fb['claims_with_memory'] or '(none)'}")
    print(f"  claims without memory: {fb['claims_without_memory'] or '(none)'}")
    print(f"  summary:               {fb['federation_summary']}")

    rec_cond = fb.get("recurring_learned_conditions", [])
    if rec_cond:
        print(f"\n  Recurring learned conditions ({len(rec_cond)}):")
        for rc in rec_cond:
            print(f"    • {rc['condition']}  (×{rc['recurrence_count']} claims: {rc['triggered_by']})")

    rec_obj = fb.get("recurring_objection_types", [])
    if rec_obj:
        print(f"\n  Recurring objection types ({len(rec_obj)}):")
        for ro in rec_obj:
            print(f"    • {ro['objection_type']}  (×{ro['recurrence_count']} claims: {ro['triggered_by']})")

    hints = fb.get("planning_hints", [])
    if hints:
        print(f"\n  Planning hints ({len(hints)}):")
        for h in hints:
            print(f"    [{h['hint_type']}]")
            print(f"      {h['hint']}")
            print(f"      triggered by: {h['triggered_by']}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="federation_memory_feedback",
        description=(
            "Compute federation-wide reflective memory feedback. "
            "Synthesizes cross-claim patterns and planning hints."
        ),
    )
    p.add_argument("--append",   action="store_true",
                   help="Append federation_memory_feedback events to federation.jsonl")
    p.add_argument("--dry-run",  action="store_true")
    p.add_argument("--json",     action="store_true", dest="json_output")
    p.add_argument("--verbose", "-v", action="store_true")
    return p.parse_args()


def main() -> None:
    args = _parse_args()

    feedback = compute_federation_memory_feedback()

    if args.append or args.dry_run:
        events  = build_feedback_events(feedback)
        written = append_feedback_events(
            events, dry_run=args.dry_run, verbose=args.verbose
        )
        if args.json_output:
            print(json.dumps({"feedback": feedback, "events": written},
                             indent=2, ensure_ascii=False))
        else:
            _print_feedback(feedback)
        return

    if args.json_output:
        print(json.dumps(feedback, indent=2, ensure_ascii=False))
    else:
        _print_feedback(feedback)


if __name__ == "__main__":
    main()
