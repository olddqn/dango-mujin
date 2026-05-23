#!/usr/bin/env python3
"""
contribution_weight.py — dango-gitsea-bridge / trust layer

Compute the trust weight for a single contribution event JSON file.

Usage:
  python runtime/contribution_weight.py <event.json>
  python runtime/contribution_weight.py <event.json> --reference-date 2026-05-24
  python runtime/contribution_weight.py <event.json> --half-life 180
  python runtime/contribution_weight.py <event.json> --count 3

Output:
  JSON pretty-print of the trust weight computation.

Exit codes:
  0 — success
  1 — invalid input or file not found
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from temporal_trust_decay import (
    compute_trust_weight,
    trust_level,
    HALF_LIFE_DAYS,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Compute trust weight for a single contribution event.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compute with current time as reference
  python runtime/contribution_weight.py examples/trust-decay-input.json

  # Fixed reference date (for deterministic output)
  python runtime/contribution_weight.py examples/trust-decay-input.json \\
    --reference-date 2026-05-24

  # Custom half-life and contributor history count
  python runtime/contribution_weight.py examples/trust-decay-input.json \\
    --half-life 180 --count 3
        """,
    )
    p.add_argument("event_file", metavar="EVENT_FILE",
                   help="Path to a JSON event file")
    p.add_argument("--reference-date", metavar="DATE",
                   help="ISO date for decay calculation (default: now UTC). Format: YYYY-MM-DD")
    p.add_argument("--half-life", type=float, default=HALF_LIFE_DAYS,
                   metavar="DAYS",
                   help=f"Half-life for decay in days (default: {HALF_LIFE_DAYS})")
    p.add_argument("--count", type=int, default=1,
                   metavar="N",
                   help="Total contribution count for this contributor (for continuity multiplier, default: 1)")
    return p.parse_args()


def _parse_reference_date(s: str) -> datetime:
    """Parse YYYY-MM-DD or ISO 8601 string to UTC datetime."""
    if "T" not in s and "Z" not in s:
        s = s + "T00:00:00Z"
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)


def main() -> None:
    args = parse_args()

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

    # Reference date
    reference_date: datetime | None = None
    if args.reference_date:
        try:
            reference_date = _parse_reference_date(args.reference_date)
        except ValueError as e:
            print(f"Error: invalid --reference-date: {e}", file=sys.stderr)
            sys.exit(1)

    # Also check for embedded reference date in the event (for example files)
    if reference_date is None and "_reference_date_for_example" in event:
        try:
            reference_date = _parse_reference_date(event["_reference_date_for_example"])
        except ValueError:
            pass

    # Compute
    result = compute_trust_weight(
        event,
        reference_date=reference_date,
        half_life_days=args.half_life,
        contribution_count=args.count,
    )

    level = trust_level(result["trust_weight"])
    ref_str = reference_date.date().isoformat() if reference_date else "now"

    # Add contextual fields to output
    out = {
        "event_type":        event.get("event_type", ""),
        "contributor":       event.get("contributor", ""),
        "contribution_type": event.get("contribution_type", ""),
        "timestamp":         event.get("timestamp", ""),
        "reference_date":    ref_str,
        "trust_level":       level,
        **result,
    }

    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
