#!/usr/bin/env python3
"""
dignity_guard.py — dango-gitsea-bridge

Run the dignity guard on a Claim JSON.
Checks consent, exposure risks, emergency need, and revenue sharing.

Decisions: pass | block | escalate
If unsure: block.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone


def load_claim(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def run_guard(claim: dict) -> list[dict]:
    """Run all dignity checks. Return list of check results."""
    results = []
    observed   = claim.get("observed_state", [])
    missing    = claim.get("missing_conditions", [])
    constraints = claim.get("dignity_constraints", [])
    contributions = claim.get("possible_contributions", [])
    statement  = claim.get("statement", "").lower()
    risks      = claim.get("risks", [])

    def check(rule, decision, detail):
        results.append({"rule": rule, "result": decision, "detail": detail})

    # Rule 1: consent_unknown
    if "consent_unknown" in observed or "explicit_consent" in missing:
        check("consent_unknown",
              "BLOCK",
              "consent_unknown in observed_state or explicit_consent in missing_conditions. "
              "Cannot proceed without established consent.")
    else:
        check("consent_unknown", "PASS", "Consent not flagged as unknown.")

    # Rule 2: identity exposure
    identity_risk = any("identity" in s for s in observed + risks)
    if "no_identity_exposure" not in constraints and identity_risk:
        check("identity_exposure",
              "BLOCK",
              "Identity exposure risk detected but no_identity_exposure not in dignity_constraints.")
    elif "no_identity_exposure" in constraints:
        check("identity_exposure", "PASS", "no_identity_exposure guaranteed in dignity_constraints.")
    else:
        check("identity_exposure", "PASS", "No identity exposure risk detected.")

    # Rule 3: location exposure
    location_risk = any("location" in s for s in observed + risks)
    if "no_location_exposure" not in constraints and location_risk:
        check("location_exposure",
              "BLOCK",
              "Location exposure risk detected but no_location_exposure not in dignity_constraints.")
    elif "no_location_exposure" in constraints:
        check("location_exposure", "PASS", "no_location_exposure guaranteed in dignity_constraints.")
    else:
        check("location_exposure", "PASS", "No location exposure risk detected.")

    # Rule 4: exploitation risk
    exploitation_keywords = ["exploit", "trafficking", "coerce", "force", "manipulation"]
    exploitation_risk = any(k in statement for k in exploitation_keywords) or \
                        any(k in r for r in risks for k in exploitation_keywords)
    if exploitation_risk:
        check("exploitation_risk",
              "ESCALATE",
              "Exploitation language detected. Human review required before proceeding.")
    else:
        check("exploitation_risk", "PASS", "No exploitation risk language detected.")

    # Rule 5: emergency need
    emergency_keywords = ["emergency", "crisis", "urgent", "immediate_need"]
    emergency = any(k in s for s in observed for k in emergency_keywords)
    if emergency:
        check("emergency_need",
              "ESCALATE",
              "Emergency need detected. Route to direct support, not monetization stream.")
    else:
        check("emergency_need", "PASS", "No emergency need flagged.")

    # Rule 6: revocable consent
    if constraints:  # dignity_constraints exists
        if "revocable_consent" not in constraints:
            check("revocable_consent",
                  "BLOCK",
                  "dignity_constraints present but revocable_consent not guaranteed.")
        else:
            check("revocable_consent", "PASS", "revocable_consent guaranteed in dignity_constraints.")
    else:
        check("revocable_consent", "PASS", "No dignity_constraints — revocable consent not required.")

    # Rule 7: revenue sharing if funding involved
    if "funding" in contributions or "fair_revenue_share" in constraints:
        if "fair_revenue_share" not in constraints:
            check("revenue_sharing",
                  "BLOCK",
                  "funding in possible_contributions but fair_revenue_share not in dignity_constraints.")
        else:
            check("revenue_sharing", "PASS", "fair_revenue_share guaranteed in dignity_constraints.")
    else:
        check("revenue_sharing", "PASS", "No funding contribution — revenue sharing check not required.")

    return results


def final_decision(checks: list[dict]) -> tuple[str, str]:
    decisions = [c["result"] for c in checks]
    if "BLOCK" in decisions:
        blocking = [c for c in checks if c["result"] == "BLOCK"]
        return "block", blocking[0]["detail"]
    if "ESCALATE" in decisions:
        escalating = [c for c in checks if c["result"] == "ESCALATE"]
        return "escalate", escalating[0]["detail"]
    return "pass", "All dignity checks passed."


def main():
    if len(sys.argv) < 2:
        print("Usage: python dignity_guard.py <claim.json>")
        sys.exit(1)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"Error: file not found: {path}")
        sys.exit(1)

    claim = load_claim(path)
    checks = run_guard(claim)
    decision, reason = final_decision(checks)

    DECISION_ICON = {"pass": "✓", "block": "✗", "escalate": "⚠"}

    print("=" * 60)
    print("DIGNITY GUARD")
    print(f"Claim: {claim.get('claim_id', '?')}")
    print("=" * 60)

    for c in checks:
        icon = {"PASS": "✓", "BLOCK": "✗", "ESCALATE": "⚠", "NOT_FLAGGED": "—"}.get(c["result"], "?")
        print(f"  {icon} [{c['result']}] {c['rule']}")
        print(f"       {c['detail']}")

    print()
    print("-" * 60)
    icon = DECISION_ICON.get(decision, "?")
    print(f"FINAL DECISION: {icon} {decision.upper()}")
    print(f"Reason: {reason}")

    if decision == "block":
        print("\nThis Claim is BLOCKED.")
        print("No stream, no asset transformation, no contribution accounting.")
        print("Resolve the blocking condition and rerun the dignity guard.")
    elif decision == "escalate":
        print("\nThis Claim requires HUMAN REVIEW.")
        print("Pause all automated processing.")
        print("A human reviewer must assess and document their decision before proceeding.")
    else:
        print("\nThis Claim has PASSED the dignity guard.")
        print("It may proceed to asset transformation and contribution stream negotiation.")

    print("=" * 60)

    # Exit code: 0=pass, 1=block, 2=escalate
    sys.exit({"pass": 0, "block": 1, "escalate": 2}.get(decision, 1))


if __name__ == "__main__":
    main()
