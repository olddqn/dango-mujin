#!/usr/bin/env python3
"""
contribution_router.py — Dan-Go Mujin Protocol

Given a claim, suggest what types of contributors are needed
and what they could specifically do.
"""

import json
import sys
from pathlib import Path

CONTRIBUTION_DESCRIPTIONS = {
    "code": "Write software, scripts, or automation to help coordinate or execute",
    "compute": "Provide CPU/GPU time, server hosting, or storage",
    "legal": "Review legal questions, draft agreements, or clarify rights",
    "translation": "Translate language, mediate cultural differences, or adapt content",
    "housing": "Provide physical space, shelter, or venue",
    "funding": "Contribute financial resources toward specific missing conditions",
    "social_reach": "Share through your network, make introductions, or amplify",
    "reputation": "Vouch for participants or lend institutional credibility",
    "care": "Provide emotional support, facilitate conversations, or mediate conflict",
    "knowledge": "Contribute research, documentation, or domain expertise",
    "coordination": "Organize logistics, schedule meetings, or connect people",
}


def load_claim(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def route_contributions(claim: dict) -> None:
    missing = claim.get("missing_conditions", [])
    possible = claim.get("possible_contributions", [])

    print("=" * 60)
    print(f"CONTRIBUTION ROUTING: {claim.get('claim_id', '?')}")
    print("=" * 60)

    if not missing:
        print("\nNo missing conditions. No contributions needed at this time.")
        return

    if not possible:
        print("\nNo contribution types specified in this claim.")
        print("Add a 'possible_contributions' list to enable routing.")
        return

    print(f"\nThis claim needs help with {len(missing)} condition(s).")
    print(f"The following contribution types are relevant:\n")

    for contrib_type in possible:
        desc = CONTRIBUTION_DESCRIPTIONS.get(contrib_type, "Contribution type not yet described")
        print(f"  [{contrib_type.upper()}]")
        print(f"  {desc}")
        print()

    print("-" * 60)
    print("If you can contribute, record your offer in the sutable:")
    print()
    print("  {")
    print(f'    "claim_id": "{claim.get("claim_id", "?")}",')
    print('    "contributor_id": "your-did-or-pseudonym",')
    print('    "contribution_type": "one of the types above",')
    print('    "description": "what specifically you are offering",')
    print('    "addresses_condition": "which missing condition this closes",')
    print('    "verifiable": true,')
    print('    "verification_method": "how this can be independently verified"')
    print("  }")
    print()
    print("Submit as a pull request or open an issue on this repository.")
    print("=" * 60)


def main():
    if len(sys.argv) < 2:
        print("Usage: python contribution_router.py <claim.json>")
        sys.exit(1)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"Error: file not found: {path}")
        sys.exit(1)

    claim = load_claim(path)
    route_contributions(claim)


if __name__ == "__main__":
    main()
