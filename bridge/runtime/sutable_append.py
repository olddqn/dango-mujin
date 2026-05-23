#!/usr/bin/env python3
"""
sutable_append.py — dango-gitsea-bridge / su-table

Append a single event to a su-table JSONL file.

Usage:
  python runtime/sutable_append.py --table <table> --event <event.json>
  python runtime/sutable_append.py --table <table> --json '{"event_type":"...",...}'

Flags:
  --table         claims | negotiations | contributions | executions | reality_feedback
  --event         path to a JSON file containing the event object
  --json          inline JSON string (alternative to --event)
  --no-chain      do not link previous_event_hash (default: chain enabled)
  --no-signature  skip signature validation (allows unsigned events without warning)
  --dry-run       validate and print the event without writing

Principles:
  - event_type is required
  - timestamp is auto-generated if absent
  - Never overwrites existing lines
  - Always appends

Signature policy:
  - unsigned       → append with signature_status="unsigned" (allowed)
  - mock_valid     → append with signature_status="mock_valid" (allowed)
  - mock_invalid   → REJECT (signature present but invalid)
  - unsupported_signature_type → REJECT (unknown signature type)
"""

import argparse
import json
import sys
from pathlib import Path

# Allow running from any directory
sys.path.insert(0, str(Path(__file__).parent))
from sutable_log import append_event, SutableError, VALID_TABLES
from did_signature import check_signature_status, STATUS_MOCK_VALID, STATUS_UNSIGNED


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
    p.add_argument("--no-signature", action="store_true",
                   help="Skip signature validation (unsigned events append without warning)")
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


def _check_signature(event: dict, skip: bool) -> str:
    """
    Validate event signature and return the signature_status string.

    Policy:
      unsigned     → allowed, returns "unsigned"
      mock_valid   → allowed, returns "mock_valid"
      mock_invalid → REJECT (exits with code 1)
      unsupported  → REJECT (exits with code 1)

    If skip=True, always returns "unsigned" without checking.
    """
    if skip:
        return STATUS_UNSIGNED

    status = check_signature_status(event)

    if status == STATUS_UNSIGNED:
        return STATUS_UNSIGNED

    if status == STATUS_MOCK_VALID:
        return STATUS_MOCK_VALID

    # mock_invalid or unsupported_signature_type → reject
    if status == "mock_invalid":
        print(
            "Error: signature validation FAILED (mock_invalid).\n"
            "  The signature field is present but does not verify.\n"
            "  Possible causes: event content changed after signing, wrong key_id.\n"
            "  Event not appended.",
            file=sys.stderr,
        )
    else:
        print(
            f"Error: unsupported signature type ({status}).\n"
            "  Only 'mock-ed25519-test-vector' is accepted.\n"
            "  Event not appended.",
            file=sys.stderr,
        )
    sys.exit(1)


def main() -> None:
    args = parse_args()
    event = load_event(args)

    if "event_type" not in event:
        print("Error: event_type is required.", file=sys.stderr)
        sys.exit(1)

    # Signature check (before dry-run print so dry-run also validates)
    sig_status = _check_signature(event, skip=args.no_signature)

    if args.dry_run:
        print("[dry-run] Event validated. Would append to:", args.table)
        print(f"  signature_status: {sig_status}")
        print(json.dumps(event, indent=2, ensure_ascii=False))
        return

    # Attach signature_status to event before appending
    event["signature_status"] = sig_status

    try:
        written = append_event(args.table, event, chain=not args.no_chain)
    except SutableError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    sig_icon = "✓" if sig_status == STATUS_MOCK_VALID else "○"
    print(f"✓ Appended to sutable/{args.table}.jsonl")
    print(f"  event_type:       {written['event_type']}")
    print(f"  timestamp:        {written['timestamp']}")
    print(f"  event_hash:       {written['event_hash'][:16]}…")
    if "previous_event_hash" in written:
        print(f"  prev_hash:        {written['previous_event_hash'][:16]}…")
    if "claim_id" in written:
        print(f"  claim_id:         {written['claim_id']}")
    print(f"  signature_status: {sig_icon} {sig_status}")


if __name__ == "__main__":
    main()
