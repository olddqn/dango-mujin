#!/usr/bin/env python3
"""
federation_snapshot.py — dango-gitsea-bridge / claim federation

Read the su-table federation events and produce a per-claim
federation snapshot: dependencies, enables, counterclaims, depth.

CLI:
  python runtime/federation_snapshot.py --claim-id housing-001
  python runtime/federation_snapshot.py --all-claims
  python runtime/federation_snapshot.py --claim-id housing-001 --verbose
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from claim_federation import (
    load_federation_events,
    build_federation_map,
    get_claim_summary,
    list_claim_ids,
)


def _compact_summary(full: dict) -> dict:
    """Compact version for quick display."""
    return {
        "claim_id":        full["claim_id"],
        "federation": {
            "depends_on_count":    len(full["depends_on"]),
            "enabled_claims":      len(full["enables"]) + len(full["enabled_by"]),
            "counterclaims":       len(full["counterclaims"]) + len(full["counterclaimed_by"]),
            "blocked_by_count":    len(full["blocked_by"]),
            "blocks_count":        len(full["blocks"]),
            "derived_from_count":  len(full["derived_from"]),
            "federation_depth":    full["federation_depth"],
        },
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Snapshot federation relationships for a claim.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python runtime/federation_snapshot.py --claim-id housing-001
  python runtime/federation_snapshot.py --all-claims
  python runtime/federation_snapshot.py --claim-id housing-001 --verbose
        """,
    )
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--claim-id", metavar="ID",
                       help="Claim ID to snapshot")
    group.add_argument("--all-claims", action="store_true",
                       help="Snapshot all claim IDs in federation table")
    p.add_argument("--verbose", action="store_true",
                   help="Show full federation details instead of compact summary")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    events = load_federation_events()
    if not events:
        print("No federation events found in sutable/federation.jsonl.", file=sys.stderr)
        if args.all_claims:
            print(json.dumps([], indent=2))
            return
        sys.exit(1)

    fmap = build_federation_map(events)

    if args.all_claims:
        all_ids = list_claim_ids(fmap)
        results = []
        for cid in all_ids:
            full = get_claim_summary(cid, fmap)
            results.append(full if args.verbose else _compact_summary(full))
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    # Single claim
    cid = args.claim_id
    if cid not in fmap:
        print(f"claim_id '{cid}' not found in federation events.", file=sys.stderr)
        known = list_claim_ids(fmap)
        if known:
            print(f"Known claim IDs: {known}", file=sys.stderr)
        sys.exit(1)

    full = get_claim_summary(cid, fmap)
    result = full if args.verbose else _compact_summary(full)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
