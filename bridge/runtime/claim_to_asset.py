#!/usr/bin/env python3
"""
claim_to_asset.py — dango-gitsea-bridge

Read a Dan-Go Claim JSON and output a GITSEA-style repo asset JSON.
Runs dignity guard first. Blocks if dignity guard fails.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

DECISION_TO_STATUS = {
    "negotiate": "pending",
    "execute":   "active",
    "escalate":  "pending",
    "reject":    "invalid",
}


def load_claim(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def dignity_quick_check(claim: dict) -> tuple[str, str]:
    """Fast dignity pre-check before full transformation. Returns (decision, reason)."""
    observed = claim.get("observed_state", [])
    constraints = claim.get("dignity_constraints", [])
    contributions = claim.get("possible_contributions", [])

    if "consent_unknown" in observed:
        return "block", "consent_unknown in observed_state — cannot transform until consent is established"

    if "no_location_exposure" not in constraints and any(
        "location" in s for s in observed
    ):
        return "block", "location data in observed_state but no_location_exposure not guaranteed"

    if claim.get("decision") == "reject":
        return "block", "Claim decision is reject — cannot become a repo asset"

    if "funding" in contributions and "fair_revenue_share" not in constraints:
        return "block", "funding listed but fair_revenue_share not in dignity_constraints"

    return "pass", "Dignity pre-check passed"


def derive_trust_mode(claim: dict, dignity_status: str) -> str:
    """Determine trust mode from dignity constraints and consent state."""
    observed = claim.get("observed_state", [])
    constraints = claim.get("dignity_constraints", [])
    if dignity_status == "block":
        return "blocked"
    if "explicit_consent_established" in observed and "revocable_consent" in constraints:
        if "anonymization_complete" in observed or "fair_revenue_share" in constraints:
            return "dignity-first"
    if constraints:
        return "guarded"
    return "open"


def transform(claim: dict, dignity_status: str, dignity_reason: str) -> dict:
    decision = claim.get("decision", "negotiate")
    asset_status = DECISION_TO_STATUS.get(decision, "pending")
    if dignity_status == "block":
        asset_status = "under_review"

    stream_eligible = dignity_status == "pass" and asset_status in ("pending", "active")
    trust_mode = derive_trust_mode(claim, dignity_status)

    return {
        "asset_id": claim.get("claim_id", "unknown"),
        "name": claim.get("title", ""),
        "description": claim.get("statement", ""),
        "origin_contributor": claim.get("speaker", "unknown"),
        "asset_status": asset_status,
        "required_conditions": claim.get("required_state", []),
        "open_conditions": claim.get("missing_conditions", []),
        "eligible_stream_types": claim.get("possible_contributions", []),
        "dignity_guard_flags": claim.get("dignity_constraints", []),
        "dignity_review": dignity_status,
        "dignity_guard_reason": dignity_reason,
        "trust_mode": trust_mode,
        "stream_eligible": stream_eligible,
        "created_at": claim.get("created_at", datetime.now(timezone.utc).isoformat()),
        "source_claim_id": claim.get("claim_id", "unknown"),
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python claim_to_asset.py <claim.json> [--json]")
        sys.exit(1)

    path = sys.argv[1]
    as_json = "--json" in sys.argv

    if not Path(path).exists():
        print(f"Error: file not found: {path}")
        sys.exit(1)

    claim = load_claim(path)
    dignity_status, dignity_reason = dignity_quick_check(claim)
    asset = transform(claim, dignity_status, dignity_reason)

    if as_json:
        print(json.dumps(asset, indent=2, ensure_ascii=False))
        return

    print("=" * 60)
    print("CLAIM → REPO ASSET TRANSFORMATION")
    print("=" * 60)
    print(f"\nSource claim:  {claim.get('claim_id')}")
    print(f"Asset ID:      {asset['asset_id']}")
    print(f"Name:          {asset['name']}")
    print(f"Asset status:  {asset['asset_status']}")
    print(f"\nDignity guard: {dignity_status.upper()}")
    print(f"Reason:        {dignity_reason}")
    print(f"Stream eligible: {'YES' if asset['stream_eligible'] else 'NO'}")

    print(f"\nOpen conditions ({len(asset['open_conditions'])}):")
    for c in asset["open_conditions"]:
        print(f"  ✗ {c}")

    print(f"\nEligible stream types ({len(asset['eligible_stream_types'])}):")
    for s in asset["eligible_stream_types"]:
        print(f"  → {s}")

    if dignity_status == "block":
        print("\n" + "=" * 60)
        print("BLOCKED: This Claim cannot become a stream asset.")
        print(f"Reason: {dignity_reason}")
        print("Resolve the blocking condition and rerun.")
    else:
        print("\n" + "=" * 60)
        print("PASSED: Transformation complete.")
        print("This asset can proceed to contribution stream negotiation.")
    print("=" * 60)


if __name__ == "__main__":
    main()
