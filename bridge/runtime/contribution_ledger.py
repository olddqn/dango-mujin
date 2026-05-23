#!/usr/bin/env python3
"""
contribution_ledger.py — dango-gitsea-bridge

Read a contribution stream JSON and produce a ledger organized by contribution type.
Identifies stream candidates (dignity-cleared, status=flowing/completed).
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

STATUS_ICON = {
    "flowing":   "▶",
    "completed": "✓",
    "paused":    "⏸",
    "disputed":  "⚠",
}


def load_stream(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def organize_by_type(entries: list[dict]) -> dict[str, list[dict]]:
    by_type = defaultdict(list)
    for e in entries:
        by_type[e.get("contribution_type", "unknown")].append(e)
    return dict(by_type)


def stream_candidates(entries: list[dict]) -> list[dict]:
    return [
        e for e in entries
        if e.get("dignity_cleared") and e.get("status") in ("flowing", "completed")
    ]


def main():
    if len(sys.argv) < 2:
        print("Usage: python contribution_ledger.py <contribution-stream.json>")
        sys.exit(1)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"Error: file not found: {path}")
        sys.exit(1)

    stream = load_stream(path)
    entries = stream.get("entries", [])

    print("=" * 60)
    print("CONTRIBUTION LEDGER")
    print(f"Stream:  {stream.get('stream_id', '?')}")
    print(f"Claim:   {stream.get('claim_id', '?')}")
    print(f"Status:  {stream.get('stream_status', '?').upper()}")
    if stream.get("stream_block_reason"):
        print(f"Blocked: {stream['stream_block_reason']}")
    print("=" * 60)

    if not entries:
        print("\nNo contribution entries found.")
        return

    by_type = organize_by_type(entries)
    print(f"\nTotal entries: {len(entries)} across {len(by_type)} type(s)\n")

    for ctype, items in sorted(by_type.items()):
        print(f"[{ctype.upper()}] ({len(items)} entries)")
        for e in items:
            icon = STATUS_ICON.get(e.get("status", ""), "?")
            cleared = "✓ dignity" if e.get("dignity_cleared") else "✗ dignity BLOCKED"
            print(f"  {icon} {e.get('contributor_id', '?')}")
            print(f"    Volume:    {e.get('volume', '?')}")
            print(f"    Condition: {e.get('addresses_condition', '?')}")
            print(f"    Dignity:   {cleared}")
            if not e.get("dignity_cleared") and e.get("dignity_block_reason"):
                print(f"    Block:     {e['dignity_block_reason']}")
            print()

    candidates = stream_candidates(entries)
    print("-" * 60)
    print(f"Stream candidates (dignity-cleared + active/completed): {len(candidates)}")
    if candidates:
        for c in candidates:
            print(f"  ✓ {c.get('contributor_id')} — {c.get('contribution_type')} — {c.get('volume')}")
    else:
        print("  None. Dignity guard is blocking all stream activity.")

    print("\nDignity guard decision:", stream.get("dignity_guard_decision", "unknown").upper())
    print("=" * 60)


if __name__ == "__main__":
    main()
