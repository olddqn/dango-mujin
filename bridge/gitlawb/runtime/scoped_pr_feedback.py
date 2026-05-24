"""
scoped_pr_feedback.py — PR feedback with scoped prerequisite metadata

Extends pr_feedback_mapper.py with scope_status, contestable,
and negotiation_reopen_allowed fields on every feedback event.

Key design:
  - PR merge is NEVER truth about the plan tree
  - negotiation_reopen_allowed: true always (even after merge)
  - hard_enforcement: false always
  - scope_status is carried through the full PR lifecycle

Input:
  - A scoped agent task (from scoped_issue_to_task.py)
  - OR a scoped issue draft (from scoped_plan_to_issue.py)
  - OR a plain PR events file (extends pr_feedback_mapper.py output)

Output:
  List of scoped PR feedback records.

No real PR is accessed. No su-table is written. stdlib only.

Usage:
  python gitlawb/runtime/scoped_pr_feedback.py <task-or-issue.json>
  python gitlawb/runtime/scoped_pr_feedback.py <task-or-issue.json> --json
  python gitlawb/runtime/scoped_pr_feedback.py <task-or-issue.json> --simulate-lifecycle
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

# ── PR lifecycle ──────────────────────────────────────────────────────────────

PR_LIFECYCLE: list[str] = ["pr_opened", "pr_reviewed", "pr_merged"]

FEEDBACK_TYPE_MAP: dict[str, str] = {
    "pr_opened":   "condition_evidence_submitted",
    "pr_reviewed": "condition_evidence_reviewed",
    "pr_merged":   "condition_evidence_accepted",
    "pr_rejected": "condition_evidence_rejected",
}

CREDIT_SIGNAL_MAP: dict[str, str] = {
    "pr_opened":   "evidence_submitted",
    "pr_reviewed": "reviewed_contribution",
    "pr_merged":   "accepted_contribution",
    "pr_rejected": "rejected_submission",
}

GITSEA_ELIGIBLE: set[str] = {"pr_merged"}

# ── Notes ─────────────────────────────────────────────────────────────────────

def _pr_note(event: str, condition: str, scope_status: str) -> str:
    notes = {
        "pr_opened": (
            f"Evidence submitted for '{condition}' (scope_status: {scope_status}). "
            "Not yet reviewed. Condition is not satisfied until merged."
        ),
        "pr_reviewed": (
            f"PR reviewed. Condition '{condition}' evidence evaluated. "
            "Scope context preserved. Not yet merged."
        ),
        "pr_merged": (
            f"PR merged. Evidence for '{condition}' accepted. "
            "ADVISORY: plan author must append a plan_correction event to formally "
            "update the plan tree. PR merge does not auto-satisfy the condition. "
            "Negotiation can reopen — PR merge is not truth."
        ),
        "pr_rejected": (
            f"PR rejected. Evidence for '{condition}' not accepted. "
            "Condition remains open. A new PR or alternative evidence path is needed."
        ),
    }
    return notes.get(event, f"PR event '{event}' recorded.")


# ── Markdown summary ──────────────────────────────────────────────────────────

_MARKDOWN_SUMMARIES: dict[str, str] = {
    "pr_opened": (
        "Evidence submitted. Awaiting peer review. "
        "Condition is not satisfied until merged."
    ),
    "pr_reviewed": (
        "Evidence reviewed. Scope context preserved. "
        "Condition is not satisfied until merged."
    ),
    "pr_merged": (
        "PR merged. Condition evidence accepted. "
        "Negotiation remains reopenable. "
        "Append a `plan_correction` event to formally update the plan tree."
    ),
    "pr_rejected": (
        "PR rejected. Evidence not accepted. "
        "Condition remains open. A new PR or alternative evidence path is needed."
    ),
}


def _markdown_summary(event: str, condition: str) -> str:
    """Return a one-line human-readable markdown summary for a PR event."""
    base = _MARKDOWN_SUMMARIES.get(
        event, f"PR event `{event}` recorded for `{condition}`."
    )
    return base


# ── Core ──────────────────────────────────────────────────────────────────────

def _extract_task_fields(source: dict[str, Any]) -> dict[str, Any]:
    """
    Extract common fields from either a scoped task or a scoped issue draft.
    """
    if source.get("task_generated") is not None:
        # Scoped task
        return {
            "claim_id":      source.get("claim_id", "unknown"),
            "condition":     source.get("condition", "unknown"),
            "scope_status":  source.get("scope_status", "applicable"),
            "scope":         source.get("scope", ""),
            "prereq_state":  source.get("prerequisite_state", "unknown"),
            "contestable":   source.get("contestable", True),
            "hard_enforce":  source.get("hard_enforcement", False),
        }
    elif source.get("issue_candidate") is not None:
        # Scoped issue draft
        nc = source.get("negotiation_context", {})
        return {
            "claim_id":      source.get("claim_id", "unknown"),
            "condition":     source.get("condition", "unknown"),
            "scope_status":  source.get("scope_status", "applicable"),
            "scope":         source.get("scope", ""),
            "prereq_state":  source.get("prerequisite_state", "unknown"),
            "contestable":   nc.get("contestable", True),
            "hard_enforce":  nc.get("hard_enforcement", False),
        }
    else:
        # Unknown — fill defaults
        return {
            "claim_id":      source.get("claim_id", "unknown"),
            "condition":     source.get("condition", "unknown"),
            "scope_status":  "unknown",
            "scope":         "",
            "prereq_state":  "unknown",
            "contestable":   True,
            "hard_enforce":  False,
        }


def generate_scoped_pr_feedback(
    source: dict[str, Any],
    pr_events: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Generate scoped PR feedback records for a given source (task or issue draft).

    pr_events: list of PR event names to simulate.
               Default: full lifecycle [pr_opened, pr_reviewed, pr_merged]
    """
    if pr_events is None:
        pr_events = PR_LIFECYCLE

    fields = _extract_task_fields(source)
    claim_id     = fields["claim_id"]
    condition    = fields["condition"]
    scope_status = fields["scope_status"]
    scope        = fields["scope"]
    prereq_state = fields["prereq_state"]
    contestable  = fields["contestable"]
    hard_enforce = fields["hard_enforce"]

    results = []
    pr_id = f"pr-{claim_id}-{condition.replace('_','-')}-001"

    for event in pr_events:
        feedback_type = FEEDBACK_TYPE_MAP.get(event, f"unknown:{event}")
        credit_signal = CREDIT_SIGNAL_MAP.get(event, "unknown")
        gitsea_elig   = event in GITSEA_ELIGIBLE
        note          = _pr_note(event, condition, scope_status)

        reality_feedback: dict[str, Any] = {
            "event_type":                "reality_feedback",
            "feedback_type":             feedback_type,
            "claim_id":                  claim_id,
            "condition":                 condition,
            "scope_status":              scope_status,
            "scope":                     scope,
            "prerequisite_state":        prereq_state,
            "pr_id":                     pr_id,
            "source":                    event,
            "authority":                 "none",
            "advisory":                  True,
            "dignity_guard":             "pass",
            "moves_money":               False,
            "hard_enforcement":          hard_enforce,
            "contestable":               contestable,
            "negotiation_reopen_allowed": True,
            "note":                      note,
        }

        if event == "pr_merged":
            reality_feedback["plan_impact"] = (
                f"{claim_id} active plan condition '{condition}' may now be considered "
                "satisfied — pending explicit plan_correction event by plan author. "
                "Negotiation can reopen at any time — PR merge is not final truth."
            )

        stream_candidate: dict[str, Any] = {
            "stream_candidate":  True,
            "moves_money":       False,
            "contribution_type": "safety_review" if "safety" in condition else "evidence_review",
            "credit_signal":     credit_signal,
            "claim_id":          claim_id,
            "condition":         condition,
            "scope_status":      scope_status,
            "pr_event":          event,
            "dignity_guard":     "pass",
            "gitsea_eligible":   gitsea_elig,
            "advisory":          True,
            "gitsea_note": (
                f"Merged contribution for scoped condition '{condition}' "
                f"(scope: {scope or 'unknown'}). GITSEA-eligible if stream activates. "
                "No funds move now."
            ) if gitsea_elig else (
                "Not GITSEA-eligible at this stage — requires pr_merged."
            ),
        }

        # Human-readable markdown summary for this event
        markdown_summary = _markdown_summary(event, condition)

        results.append({
            "pr_event":         event,
            "pr_id":            pr_id,
            "reality_feedback": reality_feedback,
            "stream_candidate": stream_candidate,
            "markdown_summary": markdown_summary,
        })

    return results


# ── CLI ───────────────────────────────────────────────────────────────────────

def _print_feedback(fb_list: list[dict]) -> None:
    for fb in fb_list:
        rf = fb["reality_feedback"]
        sc = fb["stream_candidate"]
        event = fb["pr_event"]
        gitsea_tag = " [GITSEA-eligible]" if sc["gitsea_eligible"] else ""
        print(f"\n  PR event: {event}{gitsea_tag}  ({fb['pr_id']})")
        print(f"  ├─ feedback_type:             {rf['feedback_type']}")
        print(f"  │    condition:               {rf['condition']}")
        print(f"  │    scope_status:            {rf['scope_status']}")
        print(f"  │    scope:                   {rf.get('scope','(none)')}")
        print(f"  │    hard_enforcement:        {rf['hard_enforcement']}")
        print(f"  │    contestable:             {rf['contestable']}")
        print(f"  │    negotiation_reopen:      {rf['negotiation_reopen_allowed']}")
        print(f"  │    moves_money:             {rf['moves_money']}")
        if rf.get("plan_impact"):
            print(f"  │    plan_impact: {rf['plan_impact'][:70]}...")
        print(f"  └─ stream: credit_signal={sc['credit_signal']}  "
              f"gitsea_eligible={sc['gitsea_eligible']}")
    print()


def main() -> None:
    p = argparse.ArgumentParser(
        description="Generate scoped PR feedback from a scoped issue or agent task.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gitlawb/runtime/scoped_pr_feedback.py gitlawb/examples/scoped-agent-task.output.json
  python gitlawb/runtime/scoped_pr_feedback.py gitlawb/examples/scoped-issue-housing-007.output.json
  python gitlawb/runtime/scoped_pr_feedback.py gitlawb/examples/scoped-agent-task.output.json --json
  python gitlawb/runtime/scoped_pr_feedback.py gitlawb/examples/scoped-agent-task.output.json \\
    --simulate-lifecycle
        """,
    )
    p.add_argument("source_file", metavar="SOURCE_FILE")
    p.add_argument("--json",              action="store_true", dest="json_output")
    p.add_argument("--simulate-lifecycle", action="store_true",
                   help="Simulate full PR lifecycle (open → review → merge)")
    p.add_argument("--event", metavar="EVENT",
                   choices=["pr_opened", "pr_reviewed", "pr_merged", "pr_rejected"],
                   help="Simulate a single PR event")
    args = p.parse_args()

    if not os.path.exists(args.source_file):
        print(f"ERROR: file not found: {args.source_file}", file=sys.stderr)
        sys.exit(1)

    with open(args.source_file) as f:
        data = json.load(f)

    if isinstance(data, list):
        source = data[0]
    else:
        source = data

    if args.event:
        events = [args.event]
    elif args.simulate_lifecycle:
        events = PR_LIFECYCLE
    else:
        events = PR_LIFECYCLE

    results = generate_scoped_pr_feedback(source, events)

    if args.json_output:
        print(json.dumps(results, indent=2))
        return

    print(f"\nScoped PR Feedback Generator")
    print(f"Input:   {args.source_file}")
    print(f"Events:  {events}")
    print(f"(No PR created — translation only · moves_money: False)")
    _print_feedback(results)


if __name__ == "__main__":
    main()
