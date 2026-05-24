"""
negotiation_reopen.py — Generate a negotiation_reopened event

A merged PR does not end negotiation.
This module generates a negotiation_reopened event from any PR feedback
record, recording that the negotiation has been formally reopened.

Input:
    PR feedback JSON (issue-001.pr-feedback.json or scoped-pr-feedback.output.json)

Output:
    negotiation_reopened event JSON:
    {
      event_type: "negotiation_reopened",
      reason: "counter_evidence_submitted",
      reopens_issue: 1,
      reopens_condition: "space_safety_assessed",
      authority: "none",
      contestable: true,
      reopenable: true,
      ...
    }

Reopen reasons:
    counter_evidence           — new evidence contradicts accepted evidence
    bypass_equivalence         — claim demonstrates bypass path was incorrect
    dignity_violation          — dignity guard breach identified
    prerequisite_deprecation   — prerequisite has been deprecated after merge
    scope_contest              — scope applicability is contested

No real issue or PR is modified. Append-only event generation only.
stdlib only.

A merged PR is evidence. Not authority.

Usage:
    python gitlawb/runtime/negotiation_reopen.py \\
      gitlawb/examples/issue-001.pr-feedback.json
    python gitlawb/runtime/negotiation_reopen.py \\
      gitlawb/examples/issue-001.pr-feedback.json --json
    python gitlawb/runtime/negotiation_reopen.py \\
      gitlawb/examples/issue-001.pr-feedback.json \\
      --reason bypass_equivalence
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_FILE_DIR = Path(__file__).parent

# ── Reopen reasons ────────────────────────────────────────────────────────────

REOPEN_REASONS: dict[str, str] = {
    "counter_evidence": (
        "New evidence has been submitted that contradicts or qualifies "
        "the previously accepted evidence. The condition requires re-evaluation."
    ),
    "bypass_equivalence": (
        "The claim has demonstrated an equivalent bypass path that was not "
        "recognised during initial review. Scope applicability should be re-evaluated."
    ),
    "dignity_violation": (
        "A dignity guard violation has been identified in the accepted evidence. "
        "The evidence must be re-reviewed without the violating content."
    ),
    "prerequisite_deprecation": (
        "The federation prerequisite has been deprecated after this PR was merged. "
        "The plan tree no longer requires this condition."
    ),
    "scope_contest": (
        "The scope applicability of this prerequisite is being contested. "
        "A better plan tree has been submitted demonstrating the condition "
        "does not apply in this context."
    ),
}

DEFAULT_REASON = "counter_evidence"


# ── Extract source fields ─────────────────────────────────────────────────────

def _extract_source_fields(data: Any) -> dict[str, Any]:
    """
    Extract claim_id, condition, scope_status etc. from various input formats:
      - list of PR feedback events
      - single PR feedback event
      - scoped issue dict
    """
    if isinstance(data, list) and data:
        # List of PR feedback events — look for pr_merged for context
        for fb in data:
            if isinstance(fb, dict):
                rf = fb.get("reality_feedback", fb)
                if rf.get("source") == "pr_merged" or rf.get("pr_event") == "pr_merged":
                    return _fields_from_feedback(rf)
        # Fall back to first event
        return _fields_from_feedback(data[0].get("reality_feedback", data[0]))

    if isinstance(data, dict):
        # Could be a single event or a reality_feedback wrapper
        if "reality_feedback" in data:
            return _fields_from_feedback(data["reality_feedback"])
        if data.get("event_type") == "reality_feedback":
            return _fields_from_feedback(data)
        # Plain PR feedback JSON
        return {
            "claim_id":      data.get("claim_id", "unknown"),
            "condition":     data.get("condition_resolved", data.get("condition", "unknown")),
            "scope_status":  data.get("scope_status", "applicable"),
            "scope":         data.get("scope", ""),
            "prereq_state":  data.get("prerequisite_state", "unknown"),
            "pr_id":         data.get("pr_id", "unknown"),
            "issue_number":  data.get("issue_number", None),
        }

    return {
        "claim_id": "unknown", "condition": "unknown",
        "scope_status": "unknown", "scope": "",
        "prereq_state": "unknown", "pr_id": "unknown",
        "issue_number": None,
    }


def _fields_from_feedback(rf: dict[str, Any]) -> dict[str, Any]:
    return {
        "claim_id":     rf.get("claim_id", "unknown"),
        "condition":    rf.get("condition", rf.get("condition_resolved", "unknown")),
        "scope_status": rf.get("scope_status", "applicable"),
        "scope":        rf.get("scope", ""),
        "prereq_state": rf.get("prerequisite_state", "unknown"),
        "pr_id":        rf.get("pr_id", "unknown"),
        "issue_number": rf.get("issue_number", None),
    }


# ── Core ──────────────────────────────────────────────────────────────────────

def generate_reopen_event(
    source_data: Any,
    reason: str = DEFAULT_REASON,
    reopen_note: str = "",
) -> dict[str, Any]:
    """
    Generate a negotiation_reopened event from PR feedback data.

    The event is append-only — it does not modify the original PR or issue.
    It records that negotiation has been formally reopened.
    """
    fields = _extract_source_fields(source_data)

    claim_id     = fields["claim_id"]
    condition    = fields["condition"]
    scope_status = fields["scope_status"]
    scope        = fields["scope"]
    prereq_state = fields["prereq_state"]
    pr_id        = fields["pr_id"]
    issue_number = fields["issue_number"]

    # Derive issue number from claim_id if not explicit
    if issue_number is None and claim_id == "housing-007":
        issue_number = 1

    reason_desc = REOPEN_REASONS.get(reason, f"Negotiation reopened: {reason}")

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "event_type":          "negotiation_reopened",
        "timestamp":           timestamp,
        "claim_id":            claim_id,
        "condition":           condition,
        "scope_status":        scope_status,
        "scope":               scope,
        "prerequisite_state":  prereq_state,
        "pr_id":               pr_id,
        "reopens_issue":       issue_number,
        "reopens_condition":   condition,
        "reason":              reason,
        "reason_description":  reason_desc,
        "note":                reopen_note or reason_desc,
        "authority":           "none",
        "contestable":         True,
        "hard_enforcement":    False,
        "negotiation_reopen_allowed": True,
        "reopenable":          True,
        "execution_allowed":   False,
        "moves_money":         False,
        "advisory":            True,
        "reopen_reason_examples": list(REOPEN_REASONS.keys()),
        "append_only":         True,
        "note_merge":          (
            "A merged PR is evidence. Not authority. "
            "This reopen event does not invalidate the PR — "
            "it records that the negotiation has entered a new phase."
        ),
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

def _print_event(ev: dict[str, Any]) -> None:
    print(f"\n{'='*60}")
    print(f"  Negotiation Reopen Event")
    print(f"{'='*60}")
    print(f"  event_type:    {ev['event_type']}")
    print(f"  claim_id:      {ev['claim_id']}")
    print(f"  condition:     {ev['condition']}")
    print(f"  reopens_issue: #{ev.get('reopens_issue','?')}")
    print(f"  reason:        {ev['reason']}")
    print(f"  authority:     {ev['authority']}")
    print(f"  contestable:   {ev['contestable']}")
    print(f"  append_only:   {ev['append_only']}")
    print(f"  note_merge:    {ev['note_merge'][:70]}...")
    print()


def main() -> None:
    p = argparse.ArgumentParser(
        description="Generate a negotiation_reopened event from PR feedback.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gitlawb/runtime/negotiation_reopen.py \\
    gitlawb/examples/issue-001.pr-feedback.json

  python gitlawb/runtime/negotiation_reopen.py \\
    gitlawb/examples/issue-001.pr-feedback.json --reason bypass_equivalence

  python gitlawb/runtime/negotiation_reopen.py \\
    gitlawb/examples/issue-001.pr-feedback.json --json \\
    > gitlawb/examples/issue-001.reopen-event.json
        """,
    )
    p.add_argument("feedback_file", metavar="FEEDBACK_FILE")
    p.add_argument("--json",   action="store_true", dest="json_output")
    p.add_argument("--reason", default=DEFAULT_REASON,
                   choices=list(REOPEN_REASONS.keys()),
                   help=f"Reopen reason (default: {DEFAULT_REASON})")
    p.add_argument("--note",   default="",
                   help="Optional human-readable note for this reopen event")
    args = p.parse_args()

    if not os.path.exists(args.feedback_file):
        print(f"ERROR: file not found: {args.feedback_file}", file=sys.stderr)
        sys.exit(1)

    with open(args.feedback_file) as f:
        data = json.load(f)

    ev = generate_reopen_event(data, reason=args.reason, reopen_note=args.note)

    if args.json_output:
        print(json.dumps(ev, indent=2))
    else:
        print("\nNegotiation Reopen Generator")
        print(f"Input: {args.feedback_file}")
        print(f"(No issue or PR modified — append-only event only)")
        _print_event(ev)


if __name__ == "__main__":
    main()
