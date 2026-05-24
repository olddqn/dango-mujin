#!/usr/bin/env python3
"""
federation_prerequisite_detector.py — dango-gitsea-bridge / prerequisite promotion

Detect federation-level prerequisite candidates from cross-claim memory snapshots.

A federation prerequisite emerges when:
  - A condition appears in learned_conditions for ≥ INDEPENDENT_CLAIM_THRESHOLD
    distinct claims
  - The condition was discovered independently — via structural plan tree diff —
    not declared by any authority

This module reads. It does not write.

Design invariants:
  - No text similarity. Structure only.
  - No authority. Convergence count is evidence, not governance.
  - No hidden scoring. Every field is traceable to a plan event.
  - independence is determined by plan authorship, not by coordination.

CLI:
  python runtime/federation_prerequisite_detector.py
  python runtime/federation_prerequisite_detector.py --json
  python runtime/federation_prerequisite_detector.py --verbose
  python runtime/federation_prerequisite_detector.py --condition space_safety_assessed
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from sutable_log import read_all
from claim_federation import load_federation_events, build_federation_map

# ── Threshold ─────────────────────────────────────────────────────────────────

INDEPENDENT_CLAIM_THRESHOLD = 2   # min distinct claims for candidate status


# ── Memory loading ────────────────────────────────────────────────────────────

def _latest_memory_per_claim() -> dict[str, dict[str, Any]]:
    """Return { claim_id → latest memory_snapshot_created event }."""
    latest: dict[str, dict[str, Any]] = {}
    for ev in read_all("memory"):
        if ev.get("event_type") != "memory_snapshot_created":
            continue
        cid = ev.get("claim_id", "")
        if cid:
            latest[cid] = ev   # last one wins
    return latest


# ── Plan authorship ───────────────────────────────────────────────────────────

def _plan_authors(claim_id: str, events: list[dict[str, Any]]) -> set[str]:
    """
    Return the set of speakers who proposed plan trees for a claim.
    Covers plan_tree_created, plan_tree_corrected, plan_tree_amended.
    """
    tree_types = {"plan_tree_created", "plan_tree_corrected", "plan_tree_amended"}
    return {
        ev.get("speaker", "")
        for ev in events
        if ev.get("claim_id") == claim_id
        and ev.get("event_type") in tree_types
        and ev.get("speaker")
    }


def _objectors(claim_id: str, events: list[dict[str, Any]]) -> set[str]:
    """Return the set of speakers who raised plan_objected events for a claim."""
    return {
        ev.get("speaker", "")
        for ev in events
        if ev.get("claim_id") == claim_id
        and ev.get("event_type") == "plan_objected"
        and ev.get("speaker")
    }


# ── Core detection ────────────────────────────────────────────────────────────

def detect_prerequisite_candidates(
    fmap: dict[str, Any] | None = None,
    fed_events: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """
    Find conditions that appear in learned_conditions for ≥ INDEPENDENT_CLAIM_THRESHOLD
    distinct claims.

    Returns a list of candidate dicts, each describing:
      condition              — the condition name
      convergence_count      — number of claims that learned it
      triggered_by           — list of claim_ids
      plan_author_overlap    — bool: do the plan proposers overlap across claims?
      objector_overlap       — bool: does the same objector appear in multiple claims?
      independent_convergence— bool: True when different plan authors, different claims
      dignity_safe           — bool: no dignity_violation objections on any evidence plan
      evidence_score         — int: composite metric (convergence * 2 + bonuses)
    """
    if fmap is None:
        fmap = build_federation_map(load_federation_events())

    snapshots = _latest_memory_per_claim()
    plan_events = read_all("plans")

    # ── Collect condition → [claim_ids] ──────────────────────────────────────
    condition_to_claims: dict[str, list[str]] = {}
    for cid, snap in snapshots.items():
        for cond in snap.get("learned_conditions", []):
            if not cond:
                continue
            condition_to_claims.setdefault(cond, [])
            if cid not in condition_to_claims[cond]:
                condition_to_claims[cond].append(cid)

    # ── Filter to threshold ───────────────────────────────────────────────────
    candidates: list[dict[str, Any]] = []

    for cond, claim_ids in sorted(condition_to_claims.items()):
        if len(claim_ids) < INDEPENDENT_CLAIM_THRESHOLD:
            continue

        # ── Authorship + objector overlap ────────────────────────────────────
        all_authors: list[set[str]] = [
            _plan_authors(cid, plan_events) for cid in claim_ids
        ]
        all_objectors: list[set[str]] = [
            _objectors(cid, plan_events) for cid in claim_ids
        ]

        # Author overlap: any author appears in ≥2 claim author sets
        author_pool: dict[str, int] = {}
        for author_set in all_authors:
            for a in author_set:
                author_pool[a] = author_pool.get(a, 0) + 1
        plan_author_overlap = any(v >= 2 for v in author_pool.values())

        # Objector overlap: same objector in ≥2 claims
        objector_pool: dict[str, int] = {}
        for obj_set in all_objectors:
            for o in obj_set:
                objector_pool[o] = objector_pool.get(o, 0) + 1
        objector_overlap = any(v >= 2 for v in objector_pool.values())

        # Independent convergence: different plan authors even if same objector
        independent_convergence = not plan_author_overlap

        # ── Dignity safety ────────────────────────────────────────────────────
        dignity_violations = {
            ev.get("claim_id")
            for ev in plan_events
            if ev.get("event_type") == "plan_objected"
            and ev.get("objection_type") == "dignity_violation"
        }
        dignity_safe = not bool(dignity_violations & set(claim_ids))

        # ── Evidence score ────────────────────────────────────────────────────
        # Base: 2 per claim. Bonus: +2 for independent authors. +1 if dignity safe.
        # Penalty: -1 if objector_overlap (single objector may have driven both).
        score = len(claim_ids) * 2
        if independent_convergence:
            score += 2
        if dignity_safe:
            score += 1
        if objector_overlap:
            score -= 1

        candidates.append({
            "condition": cond,
            "convergence_count": len(claim_ids),
            "triggered_by": sorted(claim_ids),
            "plan_author_overlap": plan_author_overlap,
            "objector_overlap": objector_overlap,
            "independent_convergence": independent_convergence,
            "dignity_safe": dignity_safe,
            "evidence_score": max(score, 0),
        })

    # Sort: dignity-safe + independent first, then by evidence_score desc
    candidates.sort(
        key=lambda c: (
            not c["dignity_safe"],
            not c["independent_convergence"],
            -c["evidence_score"],
        )
    )

    return candidates


def detect_single(
    condition: str,
    fmap: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Return candidate dict for a single condition, or None if below threshold."""
    candidates = detect_prerequisite_candidates(fmap=fmap)
    for c in candidates:
        if c["condition"] == condition:
            return c
    return None


# ── CLI ───────────────────────────────────────────────────────────────────────

def _main() -> None:
    parser = argparse.ArgumentParser(
        description="Detect federation prerequisite candidates from cross-claim memory snapshots."
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--verbose", action="store_true", help="Verbose detail")
    parser.add_argument("--condition", metavar="COND", help="Inspect single condition")
    args = parser.parse_args()

    if args.condition:
        result = detect_single(args.condition)
        if result is None:
            print(
                f"'{args.condition}' does not meet threshold "
                f"(need ≥{INDEPENDENT_CLAIM_THRESHOLD} claims).",
                file=sys.stderr,
            )
            sys.exit(1)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            _print_candidate(result, verbose=True)
        return

    candidates = detect_prerequisite_candidates()

    if args.json:
        print(json.dumps(candidates, indent=2))
        return

    if not candidates:
        print(f"No prerequisite candidates found (threshold: ≥{INDEPENDENT_CLAIM_THRESHOLD} claims).")
        return

    print(f"Federation Prerequisite Candidates  (threshold: ≥{INDEPENDENT_CLAIM_THRESHOLD} claims)")
    print()
    for c in candidates:
        _print_candidate(c, verbose=args.verbose)


def _print_candidate(c: dict[str, Any], *, verbose: bool = False) -> None:
    status = "✓ INDEPENDENT" if c["independent_convergence"] else "~ SHARED AUTHORS"
    dignity = "dignity-safe" if c["dignity_safe"] else "⚠ DIGNITY RISK"
    print(f"  {c['condition']}")
    print(f"    convergence: {c['convergence_count']} claim(s)  {status}  [{dignity}]")
    print(f"    triggered by: {', '.join(c['triggered_by'])}")
    print(f"    evidence score: {c['evidence_score']}")
    if verbose:
        print(f"    plan_author_overlap: {c['plan_author_overlap']}")
        print(f"    objector_overlap:    {c['objector_overlap']}")
    print()


if __name__ == "__main__":
    _main()
