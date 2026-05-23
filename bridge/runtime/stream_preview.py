#!/usr/bin/env python3
"""
stream_preview.py — dango-gitsea-bridge

Read a Claim and a contribution stream JSON.
Display:
  - Stream eligibility (dignity guard decision)
  - Open conditions (what still needs to be met)
  - Active contributions (dignity-cleared, flowing/completed)
  - Dignity-blocked contributions
  - Possible contributions (from Claim)
"""

import json
import sys
from pathlib import Path


def dignity_quick_check(claim: dict) -> tuple[str, str]:
    """Inline dignity guard — mirrors dignity_guard.py core logic."""
    observed      = claim.get("observed_state", [])
    missing       = claim.get("missing_conditions", [])
    constraints   = claim.get("dignity_constraints", [])
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


def derive_trust_mode(claim: dict, dignity_status: str) -> str:
    """Determine trust mode from consent state and dignity constraints."""
    observed    = claim.get("observed_state", [])
    constraints = claim.get("dignity_constraints", [])
    if dignity_status == "block":
        return "blocked"
    if "explicit_consent_established" in observed and "revocable_consent" in constraints:
        if "anonymization_complete" in observed or "fair_revenue_share" in constraints:
            return "dignity-first"
    if constraints:
        return "guarded"
    return "open"


def load_json(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def categorize_entries(entries: list[dict]) -> tuple[list, list, list]:
    """Split entries into: active, paused-dignity-ok, blocked."""
    active  = [e for e in entries if e.get("dignity_cleared") and e.get("status") in ("flowing", "completed")]
    blocked = [e for e in entries if not e.get("dignity_cleared")]
    paused  = [e for e in entries if e.get("dignity_cleared") and e.get("status") not in ("flowing", "completed")]
    return active, paused, blocked


def condition_coverage(entries: list[dict]) -> dict[str, list[str]]:
    """Map condition → list of contributor_ids addressing it (active only)."""
    coverage: dict[str, list[str]] = {}
    for e in entries:
        if e.get("dignity_cleared") and e.get("status") in ("flowing", "completed"):
            cond = e.get("addresses_condition")
            if cond:
                coverage.setdefault(cond, []).append(e.get("contributor_id", "?"))
    return coverage


STATUS_ICON = {
    "flowing":   "▶",
    "completed": "✓",
    "paused":    "⏸",
    "disputed":  "⚠",
}

TRUST_LABEL = {
    "dignity-first": "DIGNITY-FIRST  ★",
    "guarded":       "GUARDED",
    "open":          "OPEN",
    "blocked":       "BLOCKED  ✗",
}


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

    claim   = load_json(claim_path)
    stream  = load_json(stream_path)
    entries = stream.get("entries", [])

    dignity_decision, dignity_reason = dignity_quick_check(claim)
    trust_mode = derive_trust_mode(claim, dignity_decision)
    stream_ok  = dignity_decision == "pass"

    ICON = {True: "✓", False: "✗"}

    print("=" * 60)
    print("STREAM PREVIEW — dango-gitsea-bridge")
    print("=" * 60)
    print(f"Claim:      {claim.get('claim_id')} — {claim.get('title', '')}")
    print(f"Stream:     {stream.get('stream_id', '(none)')}")
    print(f"Trust mode: {TRUST_LABEL.get(trust_mode, trust_mode)}")
    print()

    # ── 1. STREAM ELIGIBILITY ──────────────────────────────────
    print("── STREAM ELIGIBILITY ──")
    print(f"  Dignity guard:   {dignity_decision.upper()}")
    print(f"  Reason:          {dignity_reason}")
    print(f"  Stream eligible: {ICON[stream_ok]} {'YES' if stream_ok else 'NO'}")
    if stream_ok:
        print(f"  Stream status:   {stream.get('stream_status', '?').upper()}")
    else:
        print()
        print("  BLOCKED. Resolve before any stream can proceed:")
        print(f"  → {dignity_reason}")
        if "consent_unknown" in claim.get("observed_state", []):
            print("  → Establish explicit, informed, revocable consent")
            print("  → Document consent. Rerun dignity guard.")
    print()

    # ── 2. OPEN CONDITIONS ────────────────────────────────────
    missing  = claim.get("missing_conditions", [])
    coverage = condition_coverage(entries)
    print(f"── OPEN CONDITIONS ({len(missing)}) ──")
    if not missing:
        print("  (none — all conditions met)")
    for m in missing:
        covering = coverage.get(m, [])
        if covering:
            print(f"  ⏳ {m}  ← in progress: {', '.join(covering)}")
        else:
            print(f"  ✗ {m}  ← no contributor yet")
    print()

    # ── 3. ACTIVE CONTRIBUTIONS ──────────────────────────────
    active, paused_ok, blocked = categorize_entries(entries)
    print(f"── ACTIVE CONTRIBUTIONS ({len(active)}) ──")
    if not active:
        print("  (none)")
    for e in active:
        icon = STATUS_ICON.get(e.get("status", ""), "?")
        print(f"  {icon} [{e.get('contribution_type')}] {e.get('contributor_id')}")
        cond = e.get("addresses_condition")
        if cond:
            print(f"    → addresses: {cond}")
        print(f"    → volume:    {e.get('volume')}")
        print(f"    → status:    {e.get('status')}")
    print()

    # ── 4. PAUSED (dignity-cleared but inactive) ──────────────
    if paused_ok:
        print(f"── PAUSED CONTRIBUTIONS ({len(paused_ok)}) ──")
        for e in paused_ok:
            print(f"  ⏸ [{e.get('contribution_type')}] {e.get('contributor_id')}")
            print(f"    → status: {e.get('status')}")
        print()

    # ── 5. DIGNITY-BLOCKED CONTRIBUTIONS ─────────────────────
    if blocked:
        print(f"── DIGNITY-BLOCKED CONTRIBUTIONS ({len(blocked)}) ──")
        for e in blocked:
            print(f"  ✗ [{e.get('contribution_type')}] {e.get('contributor_id')}")
            print(f"    blocked: {e.get('dignity_block_reason', 'unknown reason')}")
        print()

    # ── 6. POSSIBLE CONTRIBUTIONS (from Claim) ────────────────
    possible = claim.get("possible_contributions", [])
    print(f"── POSSIBLE CONTRIBUTIONS (from Claim) ──")
    for c in possible:
        active_ids = [e.get("contributor_id") for e in active if e.get("contribution_type") == c]
        if active_ids:
            print(f"  ▶ {c}  ← active")
        else:
            print(f"  ○ {c}")
    print()

    # ── SUMMARY ───────────────────────────────────────────────
    print("=" * 60)
    if stream_ok:
        print("STATUS: Stream can proceed. Negotiate contributions.")
        if missing:
            print(f"        {len(missing)} open condition(s) still require contributors.")
    else:
        print("STATUS: Stream is BLOCKED. See dignity guard decision above.")
    print("=" * 60)


if __name__ == "__main__":
    main()
