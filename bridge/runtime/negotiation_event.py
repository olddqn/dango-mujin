#!/usr/bin/env python3
"""
negotiation_event.py — dango-gitsea-bridge / su-table

Structured event constructors for Dan-Go negotiation events.

Event types in su-table/negotiations.jsonl:
  objection    — a speaker challenges a claim or proposed condition
  amendment    — a proposed modification to an existing claim or condition
  support      — a speaker affirms a claim or proposed condition
  escalation   — issue cannot be resolved at current negotiation level
  correction   — corrects a previous event (never deletes — appends correction)
  withdrawal   — a party withdraws from the negotiation

Correction principle:
  Dan-Go does not allow deletion of past events.
  If an event was made in error, a correction event is appended.
  The original event remains in the log.
  The correction event references the original by event_hash.

Usage:
  python runtime/negotiation_event.py objection \\
    --claim-id housing-001 \\
    --speaker did:key:critic-001 \\
    --reason "Legal ownership has not been established for this property."

  python runtime/negotiation_event.py correction \\
    --claim-id housing-001 \\
    --speaker did:key:critic-001 \\
    --corrects <event_hash> \\
    --reason "Previous objection contained incorrect legal reference. Corrected."

  python runtime/negotiation_event.py amendment \\
    --claim-id housing-001 \\
    --speaker did:key:proposer-001 \\
    --amendment "Require proof of ownership or written consent from property owner before proceeding."
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sutable_log import append_event, SutableError

EVENT_TYPES = {
    "objection",
    "amendment",
    "support",
    "escalation",
    "correction",
    "withdrawal",
}

EVENT_DOCS = {
    "objection":   "A speaker challenges a claim or proposed condition.",
    "amendment":   "A proposed modification to an existing claim or condition.",
    "support":     "A speaker affirms a claim or proposed condition.",
    "escalation":  "Issue cannot be resolved at current negotiation level; routes to human review.",
    "correction":  "Corrects a previous event. References original by event_hash. Does not delete.",
    "withdrawal":  "A party withdraws from the negotiation.",
}


def build_event(event_type: str, args: argparse.Namespace) -> dict:
    event: dict = {"event_type": event_type}

    if args.claim_id:
        event["claim_id"] = args.claim_id
    if args.speaker:
        event["speaker"] = args.speaker

    match event_type:
        case "objection":
            if not args.reason:
                print("Error: --reason required for objection", file=sys.stderr)
                sys.exit(1)
            event["reason"] = args.reason
            if args.condition:
                event["disputed_condition"] = args.condition

        case "amendment":
            if not args.amendment:
                print("Error: --amendment required for amendment", file=sys.stderr)
                sys.exit(1)
            event["proposed_amendment"] = args.amendment
            if args.condition:
                event["amends_condition"] = args.condition

        case "support":
            # --reason maps to "note" for support events (support affirms, not disputes)
            if args.reason:
                event["note"] = args.reason
            if args.condition:
                event["supports_condition"] = args.condition

        case "escalation":
            if not args.reason:
                print("Error: --reason required for escalation", file=sys.stderr)
                sys.exit(1)
            event["reason"] = args.reason
            event["requires_human_review"] = True

        case "correction":
            if not args.corrects:
                print("Error: --corrects <event_hash> required for correction", file=sys.stderr)
                sys.exit(1)
            if not args.reason:
                print("Error: --reason required for correction", file=sys.stderr)
                sys.exit(1)
            event["corrects_event_hash"] = args.corrects
            event["correction_reason"] = args.reason
            event["original_still_in_log"] = True  # explicit reminder

        case "withdrawal":
            event["reason"] = args.reason or ""

    return event


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Append a structured negotiation event to su-table/negotiations.jsonl",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\n".join(f"  {k:12s} — {v}" for k, v in EVENT_DOCS.items()),
    )
    p.add_argument("event_type", choices=sorted(EVENT_TYPES),
                   help="Type of negotiation event")
    p.add_argument("--claim-id", metavar="ID", help="Claim ID this event relates to")
    p.add_argument("--speaker", metavar="DID", help="DID or pseudonym of the speaker")
    p.add_argument("--reason", metavar="TEXT", help="Reason / explanation text")
    p.add_argument("--amendment", metavar="TEXT", help="Proposed amendment text (for amendment events)")
    p.add_argument("--condition", metavar="NAME", help="Condition being disputed, supported, or amended")
    p.add_argument("--corrects", metavar="HASH", help="event_hash of the event being corrected")
    p.add_argument("--dry-run", action="store_true",
                   help="Print event without writing")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    event = build_event(args.event_type, args)

    if args.dry_run:
        print("[dry-run] Would append to sutable/negotiations.jsonl:")
        print(json.dumps(event, indent=2, ensure_ascii=False))
        return

    try:
        written = append_event("negotiations", event)
    except SutableError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    icon = {
        "objection":  "⚡",
        "amendment":  "✏",
        "support":    "✓",
        "escalation": "⚠",
        "correction": "↩",
        "withdrawal": "↰",
    }.get(args.event_type, "•")

    print(f"{icon} Negotiation event appended: [{args.event_type.upper()}]")
    print(f"  claim_id:   {event.get('claim_id', '(none)')}")
    print(f"  speaker:    {event.get('speaker', '(none)')}")
    print(f"  event_hash: {written['event_hash'][:16]}…")
    if args.event_type == "correction":
        print(f"  corrects:   {args.corrects[:16]}…")
        print(f"  Note: original event remains in log. Correction is appended.")


if __name__ == "__main__":
    main()
