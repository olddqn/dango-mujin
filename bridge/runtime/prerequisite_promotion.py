#!/usr/bin/env python3
"""
prerequisite_promotion.py — dango-gitsea-bridge / prerequisite promotion

Promote federation prerequisite candidates to the event log.

A prerequisite candidate is promoted when:
  - independent_convergence_count >= INDEPENDENT_CLAIM_THRESHOLD (2)
  - all evidence claims are dignity-safe (no dignity_violation objections)
  - the condition is not already promoted (dedup)

Promotion appends a federation_prerequisite_promoted event to federation.jsonl.

Key invariants:
  authority: always "none"    — no central authority promotes this
  contestable: always true    — any participant can contest any prerequisite
  append-only                 — no existing event is modified

CLI:
  python runtime/prerequisite_promotion.py
  python runtime/prerequisite_promotion.py --dry-run
  python runtime/prerequisite_promotion.py --append
  python runtime/prerequisite_promotion.py --json
  python runtime/prerequisite_promotion.py --verbose
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from sutable_log import read_all, append_event
from claim_federation import load_federation_events, build_federation_map
from federation_prerequisite_detector import (
    detect_prerequisite_candidates,
    INDEPENDENT_CLAIM_THRESHOLD,
)
from prerequisite_evidence_bundle import build_evidence_bundle

# ── Already-promoted check ────────────────────────────────────────────────────

def _already_promoted_conditions(fed_events: list[dict[str, Any]]) -> set[str]:
    """Return conditions already in federation.jsonl as promoted (not deprecated)."""
    promoted: set[str] = set()
    for ev in fed_events:
        et = ev.get("event_type", "")
        cond = ev.get("condition", "")
        if not cond:
            continue
        if et == "federation_prerequisite_promoted":
            promoted.add(cond)
        elif et == "federation_prerequisite_deprecated":
            promoted.discard(cond)
    return promoted


# ── Event builder ─────────────────────────────────────────────────────────────

def build_promotion_event(
    condition: str,
    evidence_claims: list[str],
    evidence_bundle: dict[str, Any],
) -> dict[str, Any]:
    """
    Build a federation_prerequisite_promoted event dict.

    authority is always "none".
    contestable is always True.
    """
    eb = evidence_bundle.get("evidence_bundle", {})
    return {
        "event_type": "federation_prerequisite_promoted",
        "condition": condition,
        "evidence_claims": evidence_claims,
        "promotion_basis": "independent_plan_tree_diff_convergence",
        "authority": "none",
        "contestable": True,
        "convergence_count": len(evidence_claims),
        "independent_convergence": eb.get("independent_convergence", False),
        "shared_authorship": eb.get("shared_authorship", False),
        "shared_objector": eb.get("shared_objector", False),
        "dignity_safe": eb.get("dignity_safe", True),
        "evidence_score": eb.get("evidence_score", 0),
    }


# ── Promotion pipeline ────────────────────────────────────────────────────────

def compute_promotion_candidates(
    fmap: dict[str, Any] | None = None,
    fed_events: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """
    Return candidate dicts ready for promotion — filtered to:
      - independent_convergence_count >= INDEPENDENT_CLAIM_THRESHOLD
      - dignity_safe
      - not already promoted (or previously deprecated and re-eligible)

    Each dict contains: {condition, evidence_claims, evidence_bundle, event}
    where event is the built federation_prerequisite_promoted dict (not yet written).
    """
    if fmap is None:
        fmap = build_federation_map(load_federation_events())
    if fed_events is None:
        fed_events = load_federation_events()

    already_promoted = _already_promoted_conditions(fed_events)

    candidates = detect_prerequisite_candidates(fmap=fmap)
    results: list[dict[str, Any]] = []

    for cand in candidates:
        condition = cand["condition"]

        # Skip if already promoted (and not deprecated)
        if condition in already_promoted:
            continue

        # Must be dignity-safe
        if not cand["dignity_safe"]:
            continue

        # Must meet threshold (already filtered by detector, but be explicit)
        if cand["convergence_count"] < INDEPENDENT_CLAIM_THRESHOLD:
            continue

        bundle = build_evidence_bundle(condition, fmap=fmap)
        event  = build_promotion_event(condition, cand["triggered_by"], bundle)

        results.append({
            "condition": condition,
            "evidence_claims": cand["triggered_by"],
            "evidence_bundle": bundle,
            "event": event,
        })

    return results


def append_promotion_events(
    candidates: list[dict[str, Any]],
    *,
    dry_run: bool = False,
    verbose: bool = False,
) -> list[dict[str, Any]]:
    """
    Append federation_prerequisite_promoted events to federation.jsonl.

    Returns list of written events.
    """
    written: list[dict[str, Any]] = []
    for cand in candidates:
        ev = cand["event"]
        if dry_run:
            if verbose:
                print(f"[dry-run] would promote: {cand['condition']}")
            written.append(ev)
        else:
            result = append_event("federation", ev)
            if verbose:
                print(f"✓ promoted: {cand['condition']}  evidence_score={ev['evidence_score']}  {result['event_hash'][:12]}…")
            written.append(result)
    return written


def promote_prerequisites(
    *,
    dry_run: bool = False,
    verbose: bool = False,
    json_output: bool = False,
) -> dict[str, Any]:
    """
    Full promotion pipeline: detect → filter → build events → append.

    Returns a summary dict.
    """
    fmap = build_federation_map(load_federation_events())
    fed_events = load_federation_events()
    candidates = compute_promotion_candidates(fmap=fmap, fed_events=fed_events)

    if not candidates:
        summary = {
            "promoted": [],
            "skipped": [],
            "dry_run": dry_run,
            "message": "No new prerequisites to promote.",
        }
    else:
        written = append_promotion_events(candidates, dry_run=dry_run, verbose=verbose)
        summary = {
            "promoted": [
                {
                    "condition": c["condition"],
                    "evidence_claims": c["evidence_claims"],
                    "evidence_score": c["event"].get("evidence_score", 0),
                    "independent_convergence": c["event"].get("independent_convergence"),
                    "authority": "none",
                }
                for c in candidates
            ],
            "skipped": [],
            "dry_run": dry_run,
            "message": f"{len(written)} prerequisite(s) promoted.",
        }

    if json_output:
        print(json.dumps(summary, indent=2))

    return summary


# ── CLI ───────────────────────────────────────────────────────────────────────

def _main() -> None:
    parser = argparse.ArgumentParser(
        description="Promote federation prerequisite candidates to federation.jsonl."
    )
    parser.add_argument(
        "--append", action="store_true",
        help="Write promotion events to federation.jsonl (default: read-only preview)"
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    fmap = build_federation_map(load_federation_events())
    fed_events = load_federation_events()
    candidates = compute_promotion_candidates(fmap=fmap, fed_events=fed_events)

    if not candidates:
        if args.json:
            print(json.dumps({"message": "No new prerequisites to promote.", "promoted": []}, indent=2))
        else:
            print("No new prerequisites to promote.")
        return

    if args.json:
        # Show what would be / was promoted
        events = [c["event"] for c in candidates]
        if args.append and not args.dry_run:
            written = append_promotion_events(candidates, dry_run=False, verbose=False)
            print(json.dumps(written, indent=2))
        else:
            print(json.dumps(events, indent=2))
        return

    # Human-readable preview
    print(f"Federation Prerequisite Promotion")
    print(f"  candidates: {len(candidates)}")
    print()
    for c in candidates:
        ev = c["event"]
        ind = "✓ independent" if ev.get("independent_convergence") else "~ shared authors"
        print(f"  {c['condition']}")
        print(f"    authority:   none")
        print(f"    convergence: {ev['convergence_count']} claim(s)  {ind}")
        print(f"    evidence:    {', '.join(c['evidence_claims'])}")
        print(f"    score:       {ev['evidence_score']}")
        print(f"    contestable: True")
        print()

    if args.append and not args.dry_run:
        written = append_promotion_events(candidates, dry_run=False, verbose=True)
        print(f"\n{len(written)} event(s) written to federation.jsonl")
    elif args.dry_run:
        print("[dry-run] No events written.")
    else:
        print("Run with --append to write events to federation.jsonl")


if __name__ == "__main__":
    _main()
