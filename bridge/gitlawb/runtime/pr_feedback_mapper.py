"""
pr_feedback_mapper.py — PR events → Dan-Go Reality Feedback translation

Reads a PR events file and maps each PR event to a Dan-Go reality_feedback
event shape. No real PR is accessed. No su-table is written.
This is a read-only translation layer.

PR event lifecycle supported:
  pr_opened → condition_evidence_submitted
  pr_reviewed → condition_evidence_reviewed
  pr_merged → condition_evidence_accepted
  pr_rejected → condition_evidence_rejected
  pr_superseded → condition_evidence_superseded

Scoped prerequisite fields (schema_version 1.1):
  scope_status              — "applicable" | "bypassed" | "unknown"
  contestable               — True always (prerequisites are advisory hints)
  negotiation_reopen_allowed — True always (PR merge is not final truth)

No hard enforcement. No funds. No external network. stdlib only.

Usage:
    python pr_feedback_mapper.py <pr-events.json>
    python pr_feedback_mapper.py <pr-events.json> --json
    python pr_feedback_mapper.py <pr-events.json> --event pr_merged
"""

import json
import sys
import os


# ---------------------------------------------------------------------------
# Event type mapping
# ---------------------------------------------------------------------------

PR_EVENT_TO_FEEDBACK_TYPE = {
    "pr_opened":     "condition_evidence_submitted",
    "pr_reviewed":   "condition_evidence_reviewed",
    "pr_merged":     "condition_evidence_accepted",
    "pr_rejected":   "condition_evidence_rejected",
    "pr_superseded": "condition_evidence_superseded",
}

PR_EVENT_NOTES = {
    "pr_opened": (
        "Evidence submitted via PR. Not yet reviewed. "
        "Condition is not satisfied until reviewed and merged."
    ),
    "pr_reviewed": (
        "PR reviewed by an agent or human. Outcome noted. "
        "Condition is not satisfied until merged."
    ),
    "pr_merged": (
        "PR merged. Evidence accepted. "
        "Advisory: plan author should append a plan_correction event "
        "to formally update the plan tree. Merge alone does not auto-satisfy "
        "the condition in the Dan-Go negotiation protocol."
    ),
    "pr_rejected": (
        "PR rejected. Evidence not accepted. "
        "Condition remains open. A new PR or alternative evidence path is needed."
    ),
    "pr_superseded": (
        "PR superseded by a newer PR or bypass path. "
        "Original evidence is recorded but no longer the active resolution path."
    ),
}

STREAM_SIGNAL_BY_PR_EVENT = {
    "pr_opened":     "evidence_submitted",
    "pr_reviewed":   "reviewed_contribution",
    "pr_merged":     "accepted_contribution",
    "pr_rejected":   "rejected_submission",
    "pr_superseded": "superseded_submission",
}

GITSEA_ELIGIBLE_EVENTS = {"pr_merged"}


# ---------------------------------------------------------------------------
# Core: map one PR event to reality_feedback + stream_candidate
# ---------------------------------------------------------------------------

def map_pr_event(pr_event: dict) -> dict:
    """
    Map a single PR event dict to a combined feedback + stream_candidate record.

    Scoped prerequisite fields are carried through every event:
      scope_status              — from pr_event or defaults to "unknown"
      contestable               — True always
      negotiation_reopen_allowed — True always (PR merge is not final truth)
      hard_enforcement          — False always
    """
    event_type   = pr_event.get("pr_event", "unknown")
    pr_id        = pr_event.get("pr_id", "unknown")
    claim_id     = pr_event.get("claim_id", "unknown")
    condition    = pr_event.get("condition_resolved", "unknown")
    author       = pr_event.get("author", "unknown")
    reviewer     = pr_event.get("reviewer", None)
    outcome      = pr_event.get("review_outcome", None)
    comment      = pr_event.get("comment", None)

    # Scoped prerequisite fields (schema_version 1.1)
    scope_status = pr_event.get("scope_status", "unknown")
    scope        = pr_event.get("scope", "")
    prereq_state = pr_event.get("prerequisite_state", "unknown")

    feedback_type = PR_EVENT_TO_FEEDBACK_TYPE.get(event_type, f"unknown_pr_event:{event_type}")
    note          = PR_EVENT_NOTES.get(event_type, "")
    credit_signal = STREAM_SIGNAL_BY_PR_EVENT.get(event_type, "unknown")
    gitsea_elig   = event_type in GITSEA_ELIGIBLE_EVENTS

    reality_feedback: dict = {
        "event_type":                "reality_feedback",
        "feedback_type":             feedback_type,
        "claim_id":                  claim_id,
        "condition":                 condition,
        "pr_id":                     pr_id,
        "source":                    event_type,
        "authority":                 "none",
        "advisory":                  True,
        "dignity_guard":             "pass",
        "moves_money":               False,
        "hard_enforcement":          False,
        "contestable":               True,
        "negotiation_reopen_allowed": True,
        "scope_status":              scope_status,
        "scope":                     scope,
        "prerequisite_state":        prereq_state,
        "note":                      note,
    }
    if reviewer:
        reality_feedback["reviewer"] = reviewer
    if outcome:
        reality_feedback["review_outcome"] = outcome
    if comment:
        reality_feedback["review_comment"] = comment
    if event_type == "pr_merged":
        reality_feedback["plan_impact"] = (
            f"{claim_id} active plan condition `{condition}` "
            "may now be considered satisfied — pending plan_correction event by plan author. "
            "Negotiation can reopen — PR merge is not final truth."
        )

    stream_candidate: dict = {
        "stream_candidate": True,
        "moves_money":      False,
        "contribution_type": "safety_review" if "safety" in condition else "evidence_review",
        "credit_signal":    credit_signal,
        "contributor":      author,
        "claim_id":         claim_id,
        "condition":        condition,
        "pr_event":         event_type,
        "dignity_guard":    "pass",
        "gitsea_eligible":  gitsea_elig,
        "advisory":         True,
    }
    if reviewer:
        stream_candidate["reviewer"] = reviewer
    if gitsea_elig:
        stream_candidate["gitsea_note"] = (
            f"Merged contribution for a Dan-Go condition ({condition}). "
            "Eligible for GITSEA stream credit if economic layer activates. "
            "No funds move now."
        )
    else:
        stream_candidate["gitsea_note"] = (
            f"Not yet GITSEA-eligible — requires pr_merged to qualify."
        )

    return {
        "pr_event":        event_type,
        "pr_id":           pr_id,
        "reality_feedback": reality_feedback,
        "stream_candidate": stream_candidate,
    }


def map_all_pr_events(data: dict, filter_event: str | None = None) -> list[dict]:
    pr_events = data.get("pr_events", [])
    if filter_event:
        pr_events = [e for e in pr_events if e.get("pr_event") == filter_event]
    return [map_pr_event(e) for e in pr_events]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_mapped(mapped: dict) -> None:
    rf  = mapped["reality_feedback"]
    sc  = mapped["stream_candidate"]
    print(f"\n  PR event: {mapped['pr_event']}  ({mapped['pr_id']})")
    print(f"  ├─ Reality feedback type: {rf['feedback_type']}")
    print(f"  │    claim: {rf['claim_id']}  condition: {rf['condition']}")
    print(f"  │    advisory: {rf['advisory']}  moves_money: {rf['moves_money']}")
    print(f"  │    scope_status: {rf.get('scope_status','?')}  contestable: {rf.get('contestable','?')}")
    print(f"  │    hard_enforcement: {rf.get('hard_enforcement','?')}  negotiation_reopen: {rf.get('negotiation_reopen_allowed','?')}")
    if rf.get("note"):
        print(f"  │    note: {rf['note'][:90]}...")
    print(f"  └─ Stream candidate:")
    print(f"       credit_signal: {sc['credit_signal']}")
    print(f"       gitsea_eligible: {sc['gitsea_eligible']}")
    print(f"       contributor: {sc['contributor']}")
    if sc.get("reviewer"):
        print(f"       reviewer: {sc['reviewer']}")
    print(f"       gitsea_note: {sc['gitsea_note'][:80]}...")


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    input_path   = args[0]
    as_json      = "--json" in args
    filter_event = None
    if "--event" in args:
        idx = args.index("--event")
        if idx + 1 < len(args):
            filter_event = args[idx + 1]

    if not os.path.exists(input_path):
        print(f"ERROR: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    with open(input_path) as f:
        data = json.load(f)

    mapped = map_all_pr_events(data, filter_event)

    if as_json:
        print(json.dumps(mapped, indent=2))
        return

    print(f"\nDan-Go PR → Reality Feedback Mapper")
    print(f"Input: {input_path}")
    print(f"PR events mapped: {len(mapped)}")
    print(f"(No su-table written — translation only)")
    for m in mapped:
        _print_mapped(m)
    print()


if __name__ == "__main__":
    main()
