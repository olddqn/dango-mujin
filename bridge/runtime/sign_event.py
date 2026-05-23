#!/usr/bin/env python3
"""
sign_event.py — dango-gitsea-bridge / DID signature layer

Attach a mock DID signature to a su-table event JSON file.

Usage:
  python runtime/sign_event.py <event.json> \
    [--did <did>] [--key-id <key_id>] [--output <out.json>]

Options:
  --did      DID string  (default: did:key:mock-dango-agent)
  --key-id   key ID      (default: mock-key-001)
  --output   write result to file (default: stdout)
  --verify   after signing, immediately verify and print status

⚠ This uses mock-ed25519-test-vector — NOT real cryptography.
  See did_signature.py for the formula.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from did_signature import attach_signature, check_signature_status, signature_summary

_DEFAULT_DID    = "did:key:mock-dango-agent"
_DEFAULT_KEY_ID = "mock-key-001"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Attach a mock DID signature to an event JSON file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sign and print to stdout
  python runtime/sign_event.py examples/sutable_events/claim_event.json

  # Sign with custom DID/key and write to file
  python runtime/sign_event.py examples/sutable_events/claim_event.json \\
    --did did:key:z6MkLegalReviewer \\
    --key-id legal-key-001 \\
    --output examples/signed-claim-event.json

  # Sign and verify in one step
  python runtime/sign_event.py examples/sutable_events/claim_event.json --verify
        """,
    )
    p.add_argument("event_file", metavar="EVENT_FILE",
                   help="Path to a JSON event file to sign")
    p.add_argument("--did", default=_DEFAULT_DID,
                   help=f"DID to sign with (default: {_DEFAULT_DID})")
    p.add_argument("--key-id", default=_DEFAULT_KEY_ID, dest="key_id",
                   help=f"Key ID (default: {_DEFAULT_KEY_ID})")
    p.add_argument("--output", metavar="FILE",
                   help="Write signed event to this file (default: stdout)")
    p.add_argument("--verify", action="store_true",
                   help="Also verify the signature after signing and print status")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    # Load event
    path = Path(args.event_file)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(path, encoding="utf-8") as f:
            event = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(event, dict):
        print("Error: event must be a JSON object.", file=sys.stderr)
        sys.exit(1)

    # Sign
    signed = attach_signature(event, args.did, args.key_id)

    # Output
    signed_json = json.dumps(signed, indent=2, ensure_ascii=False)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(signed_json + "\n", encoding="utf-8")
        print(f"✓ Signed event written to {out}", file=sys.stderr)
    else:
        print(signed_json)

    # Optional immediate verification
    if args.verify:
        summary = signature_summary(signed)
        status  = summary["status"]
        icon    = "✓" if status == "mock_valid" else "✗"
        print(f"\n{icon} Signature verification: {status}", file=sys.stderr)
        print(f"  DID:               {summary['did']}", file=sys.stderr)
        print(f"  key_id:            {summary['key_id']}", file=sys.stderr)
        print(f"  signed_event_hash: {summary['signed_event_hash'][:16]}…", file=sys.stderr)
        print(f"  actual_event_hash: {summary['actual_event_hash'][:16]}…", file=sys.stderr)
        print(f"  type:              {summary['type']}", file=sys.stderr)


if __name__ == "__main__":
    main()
