#!/usr/bin/env python3
"""
claim_matcher.py — Dan-Go Mujin Protocol

Read a claim JSON file and report:
- What conditions are still missing
- What contribution types could close each gap
- Whether the claim passes the constitution check
"""

import json
import sys
from pathlib import Path

CONTRIBUTION_TO_CONDITION = {
    "legal": ["legal_agreement", "legal_uncertainty", "legal_review", "owner_permission",
              "participant_agreement_signed", "food_safety_compliance_confirmed",
              "copyright_ownership_ambiguity"],
    "funding": ["monthly_support", "funding", "transport_cost_may_exceed_value_of_surplus"],
    "coordination": ["local_coordination", "coordination_channel_established_between_orgs",
                     "coordination_system_established", "transport_schedule_agreed"],
    "code": ["session_handoff_protocol_written", "feedback_loop_for_surplus_prediction",
             "coordination_system_established"],
    "translation": ["language_barrier_delays_intake", "language_support"],
    "housing": ["temporary_housing", "housing_availability_changes"],
    "care": ["participant_conflict", "volunteer_coordinator_burnout"],
    "knowledge": ["script_draft_agreed", "visual_style_agreed", "post_production_workflow_agreed"],
    "social_reach": ["distribution_channel_identified", "promotion"],
    "compute": [],
    "reputation": [],
}


def load_claim(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def check_constitution(claim: dict) -> tuple[bool, list[str]]:
    check = claim.get("constitution_check", {})
    violations = []
    if check.get("violates_dignity"):
        violations.append("VIOLATION: This claim violates the dignity of another person.")
    if check.get("uses_coercion"):
        violations.append("VIOLATION: This claim uses coercion as a means of realization.")
    return len(violations) == 0, violations


def match_contributions_to_conditions(missing: list[str], possible: list[str]) -> dict:
    """For each missing condition, find which contribution types could address it."""
    result = {}
    for condition in missing:
        matched = []
        for contrib_type in possible:
            keywords = CONTRIBUTION_TO_CONDITION.get(contrib_type, [])
            if condition in keywords or any(k in condition for k in keywords):
                matched.append(contrib_type)
        result[condition] = matched if matched else ["(no automatic match — human negotiation needed)"]
    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python claim_matcher.py <claim.json>")
        sys.exit(1)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"Error: file not found: {path}")
        sys.exit(1)

    claim = load_claim(path)

    print("=" * 60)
    print(f"CLAIM: {claim.get('claim_id', '?')}")
    print(f"Title: {claim.get('title', '?')}")
    print(f"Type:  {claim.get('claim_type', '?')}")
    print("=" * 60)

    print(f"\nStatement:\n  {claim.get('statement', '?')}\n")

    # Constitution check
    ok, violations = check_constitution(claim)
    if ok:
        print("✓ Constitution check passed")
    else:
        print("✗ Constitution check FAILED:")
        for v in violations:
            print(f"  {v}")
        print("\nThis claim cannot proceed.")
        sys.exit(1)

    # Current state
    print(f"\nDecision: {claim.get('decision', '?').upper()}")

    # Observed vs required
    observed = set(claim.get("observed_state", []))
    required = set(claim.get("required_state", []))
    missing = claim.get("missing_conditions", [])

    print(f"\nObserved conditions ({len(observed)}):")
    for s in sorted(observed):
        print(f"  ✓ {s}")

    print(f"\nMissing conditions ({len(missing)}):")
    if not missing:
        print("  (none — all conditions met)")
    for m in missing:
        print(f"  ✗ {m}")

    # Contribution matching
    possible = claim.get("possible_contributions", [])
    if missing:
        print(f"\nContribution matching:")
        matches = match_contributions_to_conditions(missing, possible)
        for condition, contribs in matches.items():
            print(f"  {condition}")
            for c in contribs:
                print(f"    → {c}")

    # Risks
    risks = claim.get("risks", [])
    if risks:
        print(f"\nKnown risks ({len(risks)}):")
        for r in risks:
            print(f"  ⚠  {r}")

    print("\n" + "=" * 60)
    if missing:
        print(f"STATUS: {len(missing)} condition(s) missing. Negotiation needed.")
    else:
        print("STATUS: All conditions met. Ready for execution.")
    print("=" * 60)


if __name__ == "__main__":
    main()
