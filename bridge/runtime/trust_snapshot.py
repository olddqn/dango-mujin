#!/usr/bin/env python3
"""
trust_snapshot.py — dango-gitsea-bridge / trust layer

Read su-table contribution events for a claim and produce a
contributor trust snapshot: current trust weight per contributor,
with continuity bonus applied.

Trust is computed against the contributor's LATEST accepted contribution,
using the continuity multiplier based on their full contribution count.

Usage:
  python runtime/trust_snapshot.py --claim-id housing-001
  python runtime/trust_snapshot.py --claim-id housing-001 --reference-date 2026-05-24
  python runtime/trust_snapshot.py --claim-id housing-001 --half-life 180
  python runtime/trust_snapshot.py --claim-id housing-001 --all-claims

Output:
  JSON — contributor trust snapshot

Exit codes:
  0 — success
  1 — no events found / error
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
from sutable_log import read_all
from temporal_trust_decay import (
    compute_trust_weight,
    compute_days_since,
    trust_level,
    HALF_LIFE_DAYS,
    CONTRIBUTION_EVENT_TYPES,
)

# Which event types count as "accepted" contributions for trust calculation
_ACCEPTED_TYPES = frozenset({"contribution_accepted", "contribution_completed"})
# Offer events are included in history but do not count for continuity
_ALL_CONTRIBUTION_TYPES = CONTRIBUTION_EVENT_TYPES


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Build a contributor trust snapshot from the su-table.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python runtime/trust_snapshot.py --claim-id housing-001
  python runtime/trust_snapshot.py --claim-id housing-001 \\
    --reference-date 2026-05-24 --half-life 180
  python runtime/trust_snapshot.py --all-claims
        """,
    )
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--claim-id", metavar="ID",
                       help="Claim ID to snapshot")
    group.add_argument("--all-claims", action="store_true",
                       help="Snapshot all claim IDs in the su-table")
    p.add_argument("--reference-date", metavar="DATE",
                   help="ISO date for decay reference (default: now UTC). Format: YYYY-MM-DD")
    p.add_argument("--half-life", type=float, default=HALF_LIFE_DAYS, metavar="DAYS",
                   help=f"Half-life for decay in days (default: {HALF_LIFE_DAYS})")
    p.add_argument("--include-offers", action="store_true",
                   help="Include contribution_offer events in history (not counted for continuity)")
    return p.parse_args()


def _parse_reference_date(s: str) -> datetime:
    if "T" not in s and "Z" not in s:
        s = s + "T00:00:00Z"
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)


def _load_contributions(claim_id: Optional[str] = None) -> list[dict]:
    """Load contribution events, optionally filtered by claim_id."""
    events = []
    for event in read_all("contributions"):
        if event.get("event_type") in _ALL_CONTRIBUTION_TYPES:
            if claim_id is None or event.get("claim_id") == claim_id:
                events.append(event)
    # Sort by timestamp ascending
    events.sort(key=lambda e: e.get("timestamp", ""))
    return events


def _build_contributor_snapshot(
    events: list[dict],
    reference_date: Optional[datetime],
    half_life_days: float,
) -> list[dict]:
    """
    Group events by contributor and compute trust snapshot per contributor.

    Only 'accepted' event types count toward the continuity multiplier.
    Trust weight is computed against the latest accepted contribution.
    """
    # Group by contributor DID
    by_contributor: dict[str, list[dict]] = {}
    for event in events:
        did = event.get("contributor") or event.get("contributor_id", "unknown")
        by_contributor.setdefault(did, []).append(event)

    ref = reference_date or datetime.now(timezone.utc)

    contributors: list[dict] = []

    for did, evs in sorted(by_contributor.items()):
        # Count only accepted types for continuity
        accepted_evs = [e for e in evs if e.get("event_type") in _ACCEPTED_TYPES]
        all_evs_sorted = sorted(evs, key=lambda e: e.get("timestamp", ""))
        accepted_sorted = sorted(accepted_evs, key=lambda e: e.get("timestamp", ""))

        contribution_count = len(accepted_evs)
        total_event_count  = len(evs)

        # Trust is computed on the latest accepted event (if any)
        # Fall back to latest event of any type if no accepted events
        latest_accepted = accepted_sorted[-1] if accepted_sorted else all_evs_sorted[-1]
        latest_ts = latest_accepted.get("timestamp", "")

        days_ago = compute_days_since(latest_ts, ref) if latest_ts else 0.0

        trust_result = compute_trust_weight(
            latest_accepted,
            reference_date=ref,
            half_life_days=half_life_days,
            contribution_count=max(1, contribution_count),
        )

        level = trust_level(trust_result["trust_weight"])

        # Gather contribution types
        ctypes = sorted({e.get("contribution_type", "") for e in evs if e.get("contribution_type")})

        contributors.append({
            "did":                         did,
            "current_trust_weight":        trust_result["trust_weight"],
            "trust_level":                 level,
            "contribution_count":          contribution_count,
            "total_event_count":           total_event_count,
            "latest_contribution_days_ago":round(days_ago, 1),
            "contribution_types":          ctypes,
            "decay_factor":                trust_result["decay_factor"],
            "continuity_multiplier":       trust_result["continuity_multiplier"],
            "verification_multiplier":     trust_result["verification_multiplier"],
            "dignity_multiplier":          trust_result["dignity_multiplier"],
            "dignity_review":              trust_result["dignity_review"],
        })

    # Sort by trust weight descending
    contributors.sort(key=lambda c: c["current_trust_weight"], reverse=True)
    return contributors


def snapshot_claim(
    claim_id: str,
    reference_date: Optional[datetime],
    half_life_days: float,
) -> dict:
    """Build full trust snapshot for one claim_id."""
    events = _load_contributions(claim_id)
    ref_str = reference_date.date().isoformat() if reference_date else "now (UTC)"
    contributors = _build_contributor_snapshot(events, reference_date, half_life_days)

    blocked = [c for c in contributors if c["trust_level"] == "blocked"]
    high    = [c for c in contributors if c["trust_level"] == "high"]
    medium  = [c for c in contributors if c["trust_level"] == "medium"]
    low     = [c for c in contributors if c["trust_level"] == "low"]

    return {
        "claim_id":       claim_id,
        "reference_date": ref_str,
        "half_life_days": half_life_days,
        "summary": {
            "total_contributors": len(contributors),
            "high_trust":         len(high),
            "medium_trust":       len(medium),
            "low_trust":          len(low),
            "dignity_blocked":    len(blocked),
        },
        "contributors":   contributors,
    }


def main() -> None:
    args = parse_args()

    reference_date: Optional[datetime] = None
    if args.reference_date:
        try:
            reference_date = _parse_reference_date(args.reference_date)
        except ValueError as e:
            print(f"Error: invalid --reference-date: {e}", file=sys.stderr)
            sys.exit(1)

    if args.all_claims:
        # Collect all claim_ids from contributions table
        all_ids: set[str] = set()
        for event in read_all("contributions"):
            cid = event.get("claim_id")
            if cid:
                all_ids.add(cid)
        if not all_ids:
            print("No contribution events found in su-table.", file=sys.stderr)
            sys.exit(1)
        results = [
            snapshot_claim(cid, reference_date, args.half_life)
            for cid in sorted(all_ids)
        ]
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    # Single claim
    snap = snapshot_claim(args.claim_id, reference_date, args.half_life)

    if not snap["contributors"]:
        print(f"No contribution events found for claim_id: {args.claim_id}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(snap, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
