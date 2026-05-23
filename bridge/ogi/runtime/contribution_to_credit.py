#!/usr/bin/env python3
"""
contribution_to_credit.py — dango-ogi-bridge

Map Dan-Go contribution events to OGI-style credit signals.

Only dignity-cleared contributions receive credit signals.
Dignity-blocked contributions are noted but no credit is issued.

Usage:
  python runtime/contribution_to_credit.py examples/contribution-credit.json
  python runtime/contribution_to_credit.py examples/contribution-credit.json --json
"""

import json
import sys
import hashlib
from pathlib import Path
from datetime import datetime, timezone

# ── Contribution type → Credit dimension ──────────────────────
CREDIT_DIMENSION = {
    "compute":        "compute_credit",
    "code":           "code_credit",
    "translation":    "translation_credit",
    "care":           "care_credit",
    "distribution":   "distribution_credit",
    "verification":   "verification_credit",
    "legal_review":   "review_credit",
    "safety_review":  "review_credit",
    "risk_review":    "review_credit",
    "local_knowledge":"knowledge_credit",
    "story_editing":  "content_credit",
    "coordination":   "coordination_credit",
    "funding":        "monetary_credit",
    "support":        "care_credit",
}

# ── Secondary credit dimensions (multi-dimensional value) ─────
SECONDARY_CREDIT = {
    "local_knowledge": ["knowledge_credit", "review_credit"],  # knowledge + review value
    "legal_review":    ["review_credit", "coordination_credit"], # review + coordination
    "coordination":    ["coordination_credit"],
}

# ── Credit weight rules ───────────────────────────────────────
def _credit_weight(entry: dict) -> str:
    """Determine credit weight from verification and condition status."""
    if not entry.get("dignity_cleared", False):
        return None  # no credit for dignity-blocked
    verified = entry.get("verified", False)
    addresses = entry.get("addresses_condition")
    if verified and addresses:
        return "high"
    if verified:
        return "verified"
    return "standard"


def _event_hash(entry: dict) -> str:
    """Generate a stable reference hash for the contribution entry."""
    key = json.dumps({
        "contributor": entry.get("contributor", entry.get("contributor_id", "")),
        "contribution_type": entry.get("contribution_type", ""),
        "timestamp": entry.get("timestamp", ""),
    }, sort_keys=True)
    return hashlib.sha256(key.encode()).hexdigest()


def process_contributions(data: dict) -> dict:
    claim_id = data.get("claim_id", "unknown")
    entries  = data.get("entries", [])

    credits:  list[dict] = []
    blocked:  list[dict] = []
    skipped:  list[dict] = []

    now = datetime.now(timezone.utc).isoformat()

    for idx, entry in enumerate(entries):
        ctype      = entry.get("contribution_type", "unknown")
        contributor = entry.get("contributor", entry.get("contributor_id", "unknown"))
        weight     = _credit_weight(entry)

        if not entry.get("dignity_cleared", False):
            blocked.append({
                "contributor":          contributor,
                "contribution_type":    ctype,
                "credit_issued":        False,
                "reason":               entry.get("dignity_block_reason", "dignity_cleared: false"),
                "timestamp":            entry.get("timestamp", now),
            })
            continue

        if entry.get("status") not in (None, "completed", "flowing", "accepted"):
            skipped.append({
                "contributor":       contributor,
                "contribution_type": ctype,
                "status":            entry.get("status"),
                "reason":            f"status '{entry.get('status')}' not credit-eligible",
            })
            continue

        primary_dim = CREDIT_DIMENSION.get(ctype, f"{ctype}_credit")
        origin_hash = _event_hash(entry)

        credit = {
            "credit_id":                f"credit-{idx:03d}-{origin_hash[:8]}",
            "origin_claim_id":          claim_id,
            "contributor":              contributor,
            "contribution_type":        ctype,
            "credit_dimension":         primary_dim,
            "volume":                   entry.get("volume", ""),
            "addresses_condition":      entry.get("addresses_condition"),
            "dignity_cleared":          True,
            "verified":                 entry.get("verified", False),
            "verification_method":      entry.get("verification_method", ""),
            "credit_weight":            weight,
            "timestamp":                entry.get("timestamp", now),
            "origin_contribution_hash": f"sha256:{origin_hash}",
        }

        # Multi-dimensional credit (secondary dimensions)
        secondary = SECONDARY_CREDIT.get(ctype, [])
        if len(secondary) > 1:
            credit["secondary_credit_dimensions"] = [d for d in secondary if d != primary_dim]

        credits.append(credit)

    return {
        "claim_id":           claim_id,
        "processed_at":       now,
        "credit_signals":     credits,
        "dignity_blocked":    blocked,
        "skipped":            skipped,
        "summary": {
            "total_contributions": len(entries),
            "credits_issued":      len(credits),
            "dignity_blocked":     len(blocked),
            "skipped":             len(skipped),
            "credit_dimensions":   sorted({c["credit_dimension"] for c in credits}),
            "verified_count":      sum(1 for c in credits if c["verified"]),
            "high_weight_count":   sum(1 for c in credits if c["credit_weight"] == "high"),
        },
    }


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python contribution_to_credit.py <contribution.json> [--json]")
        sys.exit(1)

    path    = sys.argv[1]
    as_json = "--json" in sys.argv

    if not Path(path).exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    result = process_contributions(data)

    if as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    s = result["summary"]
    print("=" * 60)
    print("CONTRIBUTION → CREDIT SIGNALS — dango-ogi-bridge")
    print(f"Claim: {result['claim_id']}")
    print("=" * 60)
    print(f"\nTotal contributions: {s['total_contributions']}")
    print(f"Credits issued:      {s['credits_issued']}")
    print(f"Dignity blocked:     {s['dignity_blocked']}")
    print(f"Skipped:             {s['skipped']}")
    print(f"Verified:            {s['verified_count']}")
    print(f"High-weight:         {s['high_weight_count']}")

    if result["credit_signals"]:
        print(f"\n── CREDIT SIGNALS ({len(result['credit_signals'])}) ──")
        for c in result["credit_signals"]:
            weight_tag = {"high": " ★", "verified": " ✓", "standard": ""}.get(c["credit_weight"], "")
            print(f"\n  [{c['credit_dimension'].upper()}{weight_tag}]")
            print(f"   contributor: {c['contributor']}")
            print(f"   type:        {c['contribution_type']}")
            print(f"   volume:      {c['volume']}")
            if c.get("addresses_condition"):
                print(f"   addresses:   {c['addresses_condition']}")
            if c.get("secondary_credit_dimensions"):
                print(f"   secondary:   {', '.join(c['secondary_credit_dimensions'])}")
            print(f"   weight:      {c['credit_weight']}")
            print(f"   credit_id:   {c['credit_id']}")

    if result["dignity_blocked"]:
        print(f"\n── DIGNITY-BLOCKED (no credit issued) ({len(result['dignity_blocked'])}) ──")
        for b in result["dignity_blocked"]:
            print(f"  ✗ [{b['contribution_type']}] {b['contributor']}")
            print(f"    reason: {b['reason']}")

    if result["skipped"]:
        print(f"\n── SKIPPED ({len(result['skipped'])}) ──")
        for sk in result["skipped"]:
            print(f"  ○ [{sk['contribution_type']}] {sk.get('contributor', '?')} — {sk['reason']}")

    print(f"\nCredit dimensions active: {', '.join(s['credit_dimensions'])}")
    print("=" * 60)


if __name__ == "__main__":
    main()
