#!/usr/bin/env python3
"""
reality_feedback_append.py — dango-gitsea-bridge / su-table

Append a reality feedback event to su-table/reality_feedback.jsonl.

Reality feedback closes the loop between intent and outcome.
It is not an evaluation of the contributor.
It is an honest record of what actually happened in the world.

Result types:
  success              — conditions fully met, claim realized
  partial_success      — some conditions met, claim partially realized
  failed               — conditions not met, claim did not realize
  unexpected_outcome   — outcome differs from claim in unanticipated ways
  dignity_violation_detected — dignity was violated during execution; escalate immediately

Usage:
  python runtime/reality_feedback_append.py \\
    --claim-id housing-001 \\
    --result partial_success \\
    --notes "Internet connection established. Shared space not yet legal."

  python runtime/reality_feedback_append.py \\
    --claim-id housing-001 \\
    --result dignity_violation_detected \\
    --notes "Identity of participant was exposed without consent." \\
    --requires-review
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sutable_log import append_event, SutableError

VALID_RESULTS = {
    "success",
    "partial_success",
    "failed",
    "unexpected_outcome",
    "dignity_violation_detected",
}

RESULT_DOCS = {
    "success":                   "All conditions met. Claim fully realized.",
    "partial_success":           "Some conditions met. Claim partially realized.",
    "failed":                    "Conditions not met. Claim did not realize.",
    "unexpected_outcome":        "Outcome differs from claim in unanticipated ways.",
    "dignity_violation_detected":"Dignity violated during execution. Escalate immediately.",
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Append a reality feedback event to su-table/reality_feedback.jsonl",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\n".join(f"  {k:30s} — {v}" for k, v in RESULT_DOCS.items()),
    )
    p.add_argument("--claim-id", required=True, metavar="ID",
                   help="Claim ID this feedback relates to")
    p.add_argument("--result", required=True, choices=sorted(VALID_RESULTS),
                   help="Feedback result type")
    p.add_argument("--notes", metavar="TEXT", default="",
                   help="Free-form notes about what actually happened")
    p.add_argument("--speaker", metavar="DID",
                   help="DID or pseudonym of the person submitting feedback")
    p.add_argument("--conditions-met", metavar="COND", nargs="*",
                   help="Conditions that were successfully met")
    p.add_argument("--conditions-unmet", metavar="COND", nargs="*",
                   help="Conditions that were not met")
    p.add_argument("--requires-review", action="store_true",
                   help="Flag this feedback for human review")
    p.add_argument("--dry-run", action="store_true",
                   help="Print event without writing")
    return p.parse_args()


def build_event(args: argparse.Namespace) -> dict:
    event: dict = {
        "event_type": "reality_feedback",
        "claim_id": args.claim_id,
        "result": args.result,
    }

    if args.notes:
        event["notes"] = args.notes
    if args.speaker:
        event["speaker"] = args.speaker
    if args.conditions_met:
        event["conditions_met"] = args.conditions_met
    if args.conditions_unmet:
        event["conditions_unmet"] = args.conditions_unmet

    if args.result == "dignity_violation_detected":
        event["requires_human_review"] = True
        event["dignity_violation"] = True
        event["automated_processing_halted"] = True
    elif args.requires_review:
        event["requires_human_review"] = True

    return event


RESULT_ICON = {
    "success":                   "✓",
    "partial_success":           "◑",
    "failed":                    "✗",
    "unexpected_outcome":        "⚡",
    "dignity_violation_detected":"🛑",
}


def main() -> None:
    args = parse_args()
    event = build_event(args)

    if args.dry_run:
        print("[dry-run] Would append to sutable/reality_feedback.jsonl:")
        print(json.dumps(event, indent=2, ensure_ascii=False))
        return

    try:
        written = append_event("reality_feedback", event)
    except SutableError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    icon = RESULT_ICON.get(args.result, "•")
    print(f"{icon} Reality feedback appended [{args.result.upper()}]")
    print(f"  claim_id:   {written['claim_id']}")
    print(f"  result:     {written['result']}")
    print(f"  event_hash: {written['event_hash'][:16]}…")
    if args.notes:
        print(f"  notes:      {args.notes[:80]}{'…' if len(args.notes) > 80 else ''}")

    if args.result == "dignity_violation_detected":
        print()
        print("  ══════════════════════════════════════════")
        print("  DIGNITY VIOLATION DETECTED")
        print("  Automated processing halted.")
        print("  Requires immediate human review.")
        print("  ══════════════════════════════════════════")


if __name__ == "__main__":
    main()
