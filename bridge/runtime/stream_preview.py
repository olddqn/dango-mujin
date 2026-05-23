#!/usr/bin/env python3
"""
stream_preview.py — dango-gitsea-bridge

Read a Claim and a contribution stream JSON.
Display:
  - Missing conditions
  - Executable contributions
  - Whether the stream is eligible (dignity guard decision)
"""

import json
import sys
from pathlib import Path

# Import guard logic inline to avoid import complexity
def dignity_quick_check(claim: dict) -> tuple[str, str]:
    observed    = claim.get("observed_state", [])
    missing     = claim.get("missing_conditions", [])
    constraints = claim.get("dignity_constraints", [])
    contributions = claim.get("possible_contributions", [])

    if "consent_unknown" in observed or "explicit_consent" in missing:
        return "block", "consent_unknown — consent not established"
    if "no_location_exposure" not in constraints and any("location" in s for s in observed):
        return "block", "location exposure risk without protection"
    if claim.get("decision") == "reject":
        return "block", "Claim is rejected"
    if "funding" in contributions and "fair_revenue_share" not in constraints:
        return "block", "funding listed but fair_revenue_share not guaranteed"
    return "pass", "Dignity check passed"


def load_json(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def summarize_contributions(entries: list[dict]) -> tuple[list, list]:
    executable  = [e for e in entries if e.get("dignity_cleared") and e.get("status") in ("flowing", "completed")]
    blocked     = [e for e in entries if not e.get("dignity_cleared")]
    return executable, blocked


def main():
    if len(sys.argv) < 3:
        print("Usage: python stream_preview.py <claim.json> <contribution-stream.json>")
        sys.exit(1)

    claim_path  = sys.argv[1]
    stream_path = sys.argv[2]

    for p in [claim_path, stream_path]:
        if not Path(p).exists():
            print(f"Error: file not found: {p}")
            sys.exit(1)

    claim  = load_json(claim_path)
    stream = load_json(stream_path)
    entries = stream.get("entries", [])

    dignity_decision, dignity_reason = dignity_quick_check(claim)

    print("=" * 60)
    print("STREAM PREVIEW — dango-gitsea-bridge")
    print("=" * 60)
    print(f"Claim:   {claim.get('claim_id')} — {claim.get('title')}")
    print(f"Stream:  {stream.get('stream_id', '(none)')}")
    print()

    # 1. Missing conditions
    missing = claim.get("missing_conditions", [])
    print(f"── MISSING CONDITIONS ({len(missing)}) ──")
    if not missing:
        print("  (none — all conditions met)")
    for m in missing:
        print(f"  ✗ {m}")
    print()

    # 2. Executable contributions
    executable, blocked = summarize_contributions(entries)
    print(f"── EXECUTABLE CONTRIBUTIONS ({len(executable)}) ──")
    if not executable:
        print("  (none)")
    for e in executable:
        print(f"  ✓ [{e.get('contribution_type')}] {e.get('contributor_id')}")
        print(f"    → addresses: {e.get('addresses_condition')}")
        print(f"    → volume:    {e.get('volume')}")
    print()

    if blocked:
        print(f"── DIGNITY-BLOCKED CONTRIBUTIONS ({len(blocked)}) ──")
        for e in blocked:
            print(f"  ✗ [{e.get('contribution_type')}] {e.get('contributor_id')}")
            print(f"    blocked: {e.get('dignity_block_reason', 'unknown reason')}")
        print()

    # 3. Stream eligibility
    stream_ok = dignity_decision == "pass"
    ICON = {True: "✓", False: "✗"}
    print(f"── STREAM ELIGIBILITY ──")
    print(f"  Dignity guard:   {dignity_decision.upper()}")
    print(f"  Reason:          {dignity_reason}")
    print(f"  Stream eligible: {ICON[stream_ok]} {'YES' if stream_ok else 'NO'}")

    if not stream_ok:
        print()
        print("  BLOCKED. Resolve the following before any stream can proceed:")
        print(f"  → {dignity_reason}")
        if "consent_unknown" in claim.get("observed_state", []):
            print("  → Establish explicit, informed, revocable consent")
            print("  → Document consent. Rerun dignity guard.")

    print()
    print("── POSSIBLE CONTRIBUTIONS (from Claim) ──")
    for c in claim.get("possible_contributions", []):
        print(f"  → {c}")

    print()
    print("=" * 60)
    if stream_ok:
        print("STATUS: Stream can proceed. Negotiate contributions.")
    else:
        print("STATUS: Stream is BLOCKED. See dignity guard decision above.")
    print("=" * 60)


if __name__ == "__main__":
    main()
