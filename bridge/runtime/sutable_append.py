#!/usr/bin/env python3
"""
sutable_append.py — dango-gitsea-bridge / su-table

Append a single event to a su-table JSONL file.

Usage:
  python runtime/sutable_append.py --table <table> --event <event.json>
  python runtime/sutable_append.py --table <table> --json '{"event_type":"...",...}'

Flags:
  --table      claims | negotiations | contributions | executions | reality_feedback
  --event      path to a JSON file containing the event object
  --json       inline JSON string (alternative to --event)
  --no-chain   do not link previous_event_hash (default: chain enabled)
  --dry-run    validate and print the event without writing

Principles:
  - event_type is required
  - timestamp is auto-generated if absent
  - Never overwrites existing lines
  - Always appends
"""

import argparse
import json
import sys
from pathlib import Path

# Allow running from any directory
sys.path.insert(0, str(Path(__file__).parent))
from sutable_log import append_event, SutableError, VALID_TABLES


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Append an event to a su-table JSONL file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python runtime/sutable_append.py --table claims --event examples/sutable_events/claim_event.json
  python runtime/sutable_append.py --table negotiations --json '{"event_type":"objection","claim_id":"housing-001","reason":"legal ownership unresolved"}'
  python runtime/sutable_append.py --table claims --event my_event.json --dry-run
        """,
    )
    p.add_argument("--table", required=True,
                   help=f"Target table: {', '.join(sorted(VALID_TABLES))}")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--event", metavar="FILE",
                     help="Path to a JSON file containing the event object")
    src.add_argument("--json", metavar="JSON",
                     help="Inline JSON event string")
    p.add_argument("--no-chain", action="store_true",
                   help="Disable previous_event_hash chaining")
    p.add_argument("--dry-run", action="store_true",
                   help="Validate and print without writing")
    return p.parse_args()


def load_event(args: argparse.Namespace) -> dict:
    if args.event:
        path = Path(args.event)
        if not path.exists():
            print(f"Error: file not found: {path}", file=sys.stderr)
            sys.exit(1)
        with open(path, encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error: invalid JSON in {path}: {e}", file=sys.stderr)
                sys.exit(1)
    else:
        try:
            return json.loads(args.json)
        except json.JSONDecodeError as e:
            print(f"Error: invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)


def main() -> None:
    args = parse_args()
    event = load_event(args)

    if "event_type" not in event:
        print("Error: event_type is required.", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print("[dry-run] Event validated. Would append to:", args.table)
        print(json.dumps(event, indent=2, ensure_ascii=False))
        return

    try:
        written = append_event(args.table, event, chain=not args.no_chain)
    except SutableError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"✓ Appended to sutable/{args.table}.jsonl")
    print(f"  event_type: {written['event_type']}")
    print(f"  timestamp:  {written['timestamp']}")
    print(f"  event_hash: {written['event_hash'][:16]}…")
    if "previous_event_hash" in written:
        print(f"  prev_hash:  {written['previous_event_hash'][:16]}…")
    if "claim_id" in written:
        print(f"  claim_id:   {written['claim_id']}")


if __name__ == "__main__":
    main()
