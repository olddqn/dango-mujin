#!/usr/bin/env python3
"""
reality_feedback_mapper.py — dango-ogi-bridge

Map a Dan-Go reality_feedback event to an OGI-compatible outcome record.

Dan-Go reality feedback closes the loop between a Claim's intent and
what actually happened in the world.

This mapper translates that record into an OGI outcome format, which:
  - Names the outcome type in OGI terms
  - Extracts coordination-relevant signals (conditions met/unmet)
  - Flags dignity violations for immediate escalation
  - Proposes next steps based on the outcome type

OGI Outcome Types:
  coordination_success    — claim fully realized
  coordination_partial    — claim partially realized
  coordination_failure    — claim not realized
  coordination_unexpected — outcome differs from claim in unanticipated ways
  dignity_breach          — dignity violated; automated processing halts

Usage:
  python runtime/reality_feedback_mapper.py examples/reality-feedback.json
  python runtime/reality_feedback_mapper.py examples/reality-feedback.json --json
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# ── Dan-Go result → OGI outcome type ──────────────────────────
OUTCOME_TYPE = {
    "success":                   "coordination_success",
    "partial_success":           "coordination_partial",
    "failed":                    "coordination_failure",
    "unexpected_outcome":        "coordination_unexpected",
    "dignity_violation_detected":"dignity_breach",
}

OUTCOME_ICON = {
    "coordination_success":    "✓",
    "coordination_partial":    "◑",
    "coordination_failure":    "✗",
    "coordination_unexpected": "⚡",
    "dignity_breach":          "🛑",
}

# ── Next step suggestions by outcome ──────────────────────────
NEXT_STEPS = {
    "coordination_success": [
        "Archive claim to su-table with final status.",
        "Issue credit signals for all dignity-cleared contributions.",
        "Document success pattern for future coordination reference.",
    ],
    "coordination_partial": [
        "Identify unmet conditions and renegotiate.",
        "Append new negotiation events to su-table for unmet conditions.",
        "Issue credit signals for completed contributions.",
        "Do not penalize parties who withdrew — document withdrawal as negotiation event.",
    ],
    "coordination_failure": [
        "Append failure event to su-table reality_feedback.",
        "Run new objection events to surface blockers.",
        "If dignity was maintained, claim may be renegotiated with amended conditions.",
        "If dignity was violated, route to dignity_breach handling.",
    ],
    "coordination_unexpected": [
        "Document unexpected outcome in detail in su-table notes.",
        "Human review recommended before next coordination attempt.",
        "Append amendment events to claim with updated required_state.",
        "Unexpected outcomes inform future claim design — preserve full record.",
    ],
    "dignity_breach": [
        "HALT: All automated processing must stop immediately.",
        "Route to human reviewer — do not delegate to agents.",
        "Document breach in su-table as dignity_violation_detected event.",
        "No credit signals are issued for the breaching contribution.",
        "All parties must be notified that a dignity breach occurred.",
        "Full account of what happened must be appended to su-table.",
        "Remediation plan required before any further coordination.",
    ],
}


def map_feedback(feedback: dict) -> dict:
    result       = feedback.get("result", "")
    outcome_type = OUTCOME_TYPE.get(result, "coordination_unexpected")
    claim_id     = feedback.get("claim_id", "unknown")
    now          = datetime.now(timezone.utc).isoformat()

    dignity_breach  = outcome_type == "dignity_breach"
    requires_review = feedback.get("requires_human_review", False) or dignity_breach

    # Coordination effectiveness score (simple heuristic)
    met   = feedback.get("conditions_met",   [])
    unmet = feedback.get("conditions_unmet", [])
    total = len(met) + len(unmet)
    effectiveness = round(len(met) / total, 2) if total > 0 else (1.0 if result == "success" else 0.0)

    # Next steps (claim-supplied override or default)
    next_steps = feedback.get("next_steps") or NEXT_STEPS.get(outcome_type, [])

    record = {
        "outcome_id":               f"outcome-{claim_id}-{now[:10]}",
        "origin_claim_id":          claim_id,
        "ogi_outcome_type":         outcome_type,
        "dango_result":             result,
        "notes":                    feedback.get("notes", ""),
        "speaker":                  feedback.get("speaker", ""),
        "conditions_met":           met,
        "conditions_unmet":         unmet,
        "coordination_effectiveness": effectiveness,
        "dignity_breach":           dignity_breach,
        "requires_human_review":    requires_review,
        "automated_processing_halted": dignity_breach,
        "next_steps":               next_steps,
        "mapped_at":                now,
        "origin_timestamp":         feedback.get("timestamp", ""),
    }

    return record


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python reality_feedback_mapper.py <feedback.json> [--json]")
        sys.exit(1)

    path    = sys.argv[1]
    as_json = "--json" in sys.argv

    if not Path(path).exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        feedback = json.load(f)

    record = map_feedback(feedback)

    if as_json:
        print(json.dumps(record, indent=2, ensure_ascii=False))
        return

    icon = OUTCOME_ICON.get(record["ogi_outcome_type"], "•")
    print("=" * 60)
    print("REALITY FEEDBACK → OGI OUTCOME — dango-ogi-bridge")
    print(f"Claim: {record['origin_claim_id']}")
    print("=" * 60)
    print(f"\n{icon} OGI outcome type:  {record['ogi_outcome_type']}")
    print(f"   Dan-Go result:     {record['dango_result']}")
    print(f"   Effectiveness:     {record['coordination_effectiveness']:.0%}")

    if record["notes"]:
        print(f"\nNotes: {record['notes'][:120]}{'…' if len(record['notes']) > 120 else ''}")

    if record["conditions_met"]:
        print(f"\nConditions met ({len(record['conditions_met'])}):")
        for c in record["conditions_met"]:
            print(f"  ✓ {c}")

    if record["conditions_unmet"]:
        print(f"\nConditions unmet ({len(record['conditions_unmet'])}):")
        for c in record["conditions_unmet"]:
            print(f"  ✗ {c}")

    if record["dignity_breach"]:
        print()
        print("  ══════════════════════════════════════════════")
        print("  🛑 DIGNITY BREACH")
        print("  Automated processing HALTED.")
        print("  Requires IMMEDIATE human review.")
        print("  ══════════════════════════════════════════════")

    print(f"\n── NEXT STEPS ──")
    for i, step in enumerate(record["next_steps"], 1):
        print(f"  {i}. {step}")

    print(f"\nOutcome ID:   {record['outcome_id']}")
    print(f"Human review: {'REQUIRED' if record['requires_human_review'] else 'not required'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
