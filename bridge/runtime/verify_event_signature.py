#!/usr/bin/env python3
"""
verify_event_signature.py — dango-gitsea-bridge / DID signature layer

Verify the mock DID signature on a su-table event JSON file.

Usage:
  python runtime/verify_event_signature.py <event.json>
  python runtime/verify_event_signature.py <event.json> --json
  python runtime/verify_event_signature.py <event.json> --quiet

Exit codes:
  0  — mock_valid
  1  — mock_invalid, unsupported_signature_type, or unsigned
  2  — file/parse error

⚠ This verifies mock-ed25519-test-vector — NOT real cryptography.
  See did_signature.py for the formula.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from did_signature import (
    check_signature_status,
    signature_summary,
    STATUS_MOCK_VALID,
    STATUS_UNSIGNED,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Verify the mock DID signature on an event JSON file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Human-readable output
  python runtime/verify_event_signature.py examples/signed-claim-event.json

  # JSON output (for pipeline use)
  python runtime/verify_event_signature.py examples/signed-claim-event.json --json

  # Quiet: just exit code (0 = valid, 1 = invalid/unsigned, 2 = error)
  python runtime/verify_event_signature.py examples/signed-claim-event.json --quiet
        """,
    )
    p.add_argument("event_file", metavar="EVENT_FILE",
                   help="Path to a signed event JSON file")
    p.add_argument("--json", action="store_true", dest="json_out",
                   help="Output result as JSON")
    p.add_argument("--quiet", action="store_true",
                   help="No output — rely on exit code only")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    path = Path(args.event_file)
    if not path.exists():
        if not args.quiet:
            print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(2)

    try:
        with open(path, encoding="utf-8") as f:
            event = json.load(f)
    except json.JSONDecodeError as e:
        if not args.quiet:
            print(f"Error: invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(2)

    if not isinstance(event, dict):
        if not args.quiet:
            print("Error: event must be a JSON object.", file=sys.stderr)
        sys.exit(2)

    summary = signature_summary(event)
    status  = summary["status"]

    if args.quiet:
        sys.exit(0 if status == STATUS_MOCK_VALID else 1)

    if args.json_out:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        sys.exit(0 if status == STATUS_MOCK_VALID else 1)

    # Human-readable output
    icon = {
        "mock_valid":                "✓",
        "mock_invalid":              "✗",
        "unsigned":                  "○",
        "unsupported_signature_type":"?",
    }.get(status, "?")

    print(f"{icon} Signature status: {status}")

    if status == "unsigned":
        print("  No signature field present. Event is unsigned.")
        sys.exit(1)

    print(f"  DID:               {summary['did'] or '(none)'}")
    print(f"  key_id:            {summary['key_id'] or '(none)'}")
    print(f"  type:              {summary['type'] or '(none)'}")

    seh = summary["signed_event_hash"]
    aeh = summary["actual_event_hash"]
    print(f"  signed_event_hash: {seh[:16]}…" if seh else "  signed_event_hash: (missing)")
    print(f"  actual_event_hash: {aeh[:16]}…" if aeh else "  actual_event_hash: (missing)")

    if seh and aeh:
        hash_match = seh == aeh
        print(f"  hash_match:        {'✓ yes' if hash_match else '✗ no (event content has changed)'}")

    if status == "mock_invalid":
        print("\n  ✗ Signature is INVALID — event may have been tampered with.")
        sys.exit(1)
    elif status == "unsupported_signature_type":
        print(f"\n  ? Unsupported signature type: {summary['type']}")
        sys.exit(1)
    else:
        print("\n  ✓ Signature verified (mock test vector).")
        sys.exit(0)


if __name__ == "__main__":
    main()
