#!/usr/bin/env python3
"""
reality_feedback.py — Dan-Go Mujin Protocol

Record and display execution feedback for claims.
Feedback statuses: executed, partial, failed, pending
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime, timezone

FEEDBACK_DIR = Path(__file__).parent.parent / "sutable" / "feedback"

VALID_STATUSES = ("executed", "partial", "failed", "pending")

SAMPLE_FEEDBACK = [
    {
        "feedback_id": "feedback-housing-001-a",
        "claim_id": "claim-housing-001",
        "author_id": "did:key:z6Mkexample1",
        "status": "partial",
        "description": "Owner was contacted and expressed interest but has not yet given formal permission. Cleaning team is ready. Internet connection arranged. Monthly support still missing.",
        "conditions_realized": ["cleaning_team", "internet_connection"],
        "conditions_still_missing": ["owner_permission", "monthly_support"],
        "timestamp": "2026-05-23T00:00:00Z"
    }
]


def load_feedback(claim_id: str = None) -> list[dict]:
    """Load feedback from sutable/feedback/ directory, optionally filtered by claim_id."""
    feedback_list = []
    if FEEDBACK_DIR.exists():
        for f in FEEDBACK_DIR.glob("*.json"):
            try:
                with open(f) as fh:
                    entry = json.load(fh)
                if claim_id is None or entry.get("claim_id") == claim_id:
                    feedback_list.append(entry)
            except Exception:
                pass
    return feedback_list


def save_feedback(entry: dict) -> Path:
    FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)
    fid = entry["feedback_id"]
    path = FEEDBACK_DIR / f"{fid}.json"
    with open(path, "w") as f:
        json.dump(entry, f, indent=2)
    return path


def display_feedback(feedback_list: list[dict]) -> None:
    if not feedback_list:
        print("No feedback recorded yet.")
        return

    STATUS_ICON = {
        "executed": "✓",
        "partial":  "◑",
        "failed":   "✗",
        "pending":  "…",
    }

    for entry in sorted(feedback_list, key=lambda e: e.get("timestamp", "")):
        icon = STATUS_ICON.get(entry.get("status", ""), "?")
        print(f"\n{icon} [{entry.get('status', '?').upper()}] {entry.get('claim_id', '?')}")
        print(f"  By: {entry.get('author_id', '?')}")
        print(f"  At: {entry.get('timestamp', '?')[:10]}")
        print(f"  {entry.get('description', '')}")

        realized = entry.get("conditions_realized", [])
        if realized:
            print(f"  Realized: {', '.join(realized)}")

        still_missing = entry.get("conditions_still_missing", [])
        if still_missing:
            print(f"  Still missing: {', '.join(still_missing)}")


def record_feedback_interactive() -> None:
    print("Record new execution feedback")
    print("-" * 40)
    claim_id = input("Claim ID: ").strip()
    author_id = input("Your ID (DID or pseudonym): ").strip()
    status = ""
    while status not in VALID_STATUSES:
        status = input(f"Status ({'/'.join(VALID_STATUSES)}): ").strip()
    description = input("Description: ").strip()

    feedback_id = f"feedback-{claim_id}-{int(datetime.now(timezone.utc).timestamp())}"
    entry = {
        "feedback_id": feedback_id,
        "claim_id": claim_id,
        "author_id": author_id,
        "status": status,
        "description": description,
        "conditions_realized": [],
        "conditions_still_missing": [],
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    path = save_feedback(entry)
    print(f"\nFeedback saved to: {path}")
    print("Submit this file as a pull request to make it part of the public record.")


def main():
    args = sys.argv[1:]

    if "--record" in args:
        record_feedback_interactive()
        return

    claim_id = args[0] if args else None

    print("=" * 60)
    print("REALITY FEEDBACK — Dan-Go Mujin Protocol")
    if claim_id:
        print(f"Claim: {claim_id}")
    print("=" * 60)

    feedback = load_feedback(claim_id)

    if not feedback:
        print("\nNo feedback found in sutable/feedback/")
        print("Showing sample feedback:\n")
        display_feedback(SAMPLE_FEEDBACK)
    else:
        display_feedback(feedback)

    print("\n" + "=" * 60)
    print("To record new feedback: python reality_feedback.py --record")
    print("=" * 60)


if __name__ == "__main__":
    main()
