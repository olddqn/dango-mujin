#!/usr/bin/env python3
"""
memory_append.py — dango-gitsea-bridge / reflective memory layer

Append a memory_snapshot_created event to sutable/memory.jsonl.

Memory snapshots are derived from plans.jsonl negotiation history.
They are append-only: each snapshot is a point-in-time record of what
the system knew at the moment it was created.

Multiple snapshots may exist for the same claim. The latest is authoritative.
Older snapshots are preserved — append-only, never deleted.

The memory record captures:
  - active_plan_id           — which plan is currently active
  - negotiation_status       — open / signalled / contested / active
  - learned_conditions       — new conditions surfaced by negotiation
  - prior_objections         — typed objection signals per plan
  - prior_supports           — support signals per plan
  - correction_chain_depth   — how many correction hops exist
  - contest_count            — how many competing plans were proposed
  - summary                  — human-readable one-line summary

Absolute prohibitions:
  - No execution of plans or bundles
  - No network, no API keys, no external libraries
  - No deletion or modification of existing events

CLI:
  python runtime/memory_append.py --claim-id housing-001
  python runtime/memory_append.py --claim-id housing-001 --dry-run
  python runtime/memory_append.py --claim-id housing-001 --verbose
  python runtime/memory_append.py --claim-id housing-001 --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from sutable_log import append_event, SutableError
from reflective_memory import compute_memory, next_memory_id

# ── Event type ────────────────────────────────────────────────────────────────

MEMORY_EVENT_TYPE = "memory_snapshot_created"


# ── Build event ───────────────────────────────────────────────────────────────

def build_memory_event(claim_id: str) -> dict[str, Any]:
    """
    Compute and build a memory_snapshot_created event for a claim.

    Returns the event dict (not yet written).
    Raises SystemExit(1) if no plan events exist for the claim.
    """
    mem = compute_memory(claim_id)

    if "error" in mem:
        print(f"✗ memory_append: {mem['error']}", file=sys.stderr)
        sys.exit(1)

    memory_id = next_memory_id(claim_id)

    return {
        "event_type":              MEMORY_EVENT_TYPE,
        "claim_id":                claim_id,
        "memory_id":               memory_id,
        "active_plan_id":          mem["active_plan_id"],
        "negotiation_status":      mem["negotiation_status"],
        "learned_conditions":      mem["learned_conditions"],
        "prior_supports":          mem["prior_supports"],
        "prior_objections":        mem["prior_objections"],
        "correction_chain_depth":  mem["correction_chain_depth"],
        "contest_count":           mem["contest_count"],
        "known_contested_plans":   mem["known_contested_plans"],
        "snapshot_basis":          mem["snapshot_basis"],
        "summary":                 mem["summary"],
    }


# ── Append ────────────────────────────────────────────────────────────────────

def append_memory_snapshot(
    claim_id: str,
    *,
    dry_run: bool = False,
    verbose: bool = False,
    json_output: bool = False,
) -> dict[str, Any]:
    """
    Build and append a memory_snapshot_created event to sutable/memory.jsonl.

    Args:
        claim_id:    The claim to snapshot.
        dry_run:     Compute and print but do not write.
        verbose:     Print progress to stderr.
        json_output: Print final event as JSON to stdout.

    Returns:
        The written (or dry-run) event dict.
    """
    event = build_memory_event(claim_id)

    if dry_run:
        print("── DRY RUN — memory event not written ──")
        print(json.dumps(event, indent=2, ensure_ascii=False))
        return event

    written = append_event("memory", event)

    if verbose:
        print(f"✓ appended to memory.jsonl", file=sys.stderr)
        print(f"  memory_id:          {written.get('memory_id')}", file=sys.stderr)
        print(f"  claim_id:           {written.get('claim_id')}", file=sys.stderr)
        print(f"  active_plan_id:     {written.get('active_plan_id', '(none)')}", file=sys.stderr)
        print(f"  negotiation_status: {written.get('negotiation_status')}", file=sys.stderr)
        lc = written.get("learned_conditions", [])
        if lc:
            print(f"  learned_conditions: {lc}", file=sys.stderr)
        print(f"  event_hash:         {written.get('event_hash', '')[:16]}…", file=sys.stderr)

    return written


# ── CLI ───────────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="memory_append",
        description=(
            "Create a reflective memory snapshot for a claim "
            "and append it to sutable/memory.jsonl."
        ),
    )
    p.add_argument("--claim-id", required=True, metavar="CLAIM_ID")
    p.add_argument("--dry-run", action="store_true", default=False,
                   help="Compute and print without writing.")
    p.add_argument("--verbose", "-v", action="store_true", default=False)
    p.add_argument("--json", action="store_true", dest="json_output", default=False,
                   help="Print the written event as JSON to stdout.")
    return p.parse_args()


def main() -> None:
    args    = _parse_args()
    written = append_memory_snapshot(
        args.claim_id,
        dry_run=args.dry_run,
        verbose=args.verbose,
        json_output=args.json_output,
    )
    if not args.dry_run and args.json_output:
        print(json.dumps(written, indent=2, ensure_ascii=False))
    elif not args.dry_run and not args.verbose:
        # Minimal confirmation output
        print(
            f"✓ {written.get('memory_id')}  "
            f"[{written.get('negotiation_status')}]  "
            f"active={written.get('active_plan_id', '(none)')}"
        )


if __name__ == "__main__":
    main()
