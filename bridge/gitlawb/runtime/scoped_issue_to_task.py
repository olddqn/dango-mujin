"""
scoped_issue_to_task.py — Scoped issue draft → agent task specification

Reads a scoped issue draft (output of scoped_plan_to_issue.py) and produces
an agent task specification with scope_status support.

Extends issue_to_agent_task.py with:
  - scope_status field
  - prerequisite_state context
  - negotiation_reopen_allowed
  - scoped checklist items

No task is created, submitted, or executed. execution_allowed: false always.
No hard enforcement. No funds. No external network. stdlib only.

Usage:
  python gitlawb/runtime/scoped_issue_to_task.py <scoped-issue.json>
  python gitlawb/runtime/scoped_issue_to_task.py <scoped-issue.json> --json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

# ── Capability maps ───────────────────────────────────────────────────────────

CONDITION_TASK_TYPE: dict[str, str] = {
    "space_safety_assessed":     "safety_review",
    "food_safety_reviewed":      "safety_review",
    "structural_assessment":     "structural_review",
    "local_structural_assessment": "structural_review",
    "risk_assessment":           "risk_review",
    "legal_ownership_confirmed": "legal_review",
    "participant_consent":       "consent_facilitation",
}

SCOPE_STATUS_PRIORITY: dict[str, str] = {
    "applicable": "high",
    "bypassed":   "none",      # should never reach here
}

CONDITION_CHECKLIST: dict[str, list[str]] = {
    "space_safety_assessed": [
        "Obtain structural/electrical clearance certificate for the space.",
        "Confirm no open-flame hazard without suppression system present.",
        "Attach inspection report to PR referencing this issue.",
        "Reviewer must confirm: no precertification bypass path exists for this claim.",
    ],
    "food_safety_reviewed": [
        "Obtain food handling certification for the distribution context.",
        "Confirm volunteer training records are available.",
        "Attach certification to PR referencing this issue.",
    ],
}

DEFAULT_CHECKLIST = [
    "Verify the condition is not already present in the active plan.",
    "Collect evidence that the condition is satisfied.",
    "Confirm dignity guard: no identity exposure, revocable consent, participant consent.",
    "Attach evidence to a PR referencing this issue.",
    "Do not execute any physical or financial action — evidence submission only.",
    "Agent must not auto-approve. Human or peer agent review required before merge.",
]

SCOPE_CHECKLIST_ADDONS: list[str] = [
    "Confirm this claim has no bypass path (no precertification, no external audit).",
    "Check scope: prerequisite applies to non_precertified_spaces only.",
    "After PR merge, append a plan_correction event — merge alone does not satisfy the condition.",
]


# ── Core translation ──────────────────────────────────────────────────────────

def scoped_issue_to_task(issue: dict[str, Any]) -> dict[str, Any]:
    """
    Translate a scoped issue draft to an agent task specification.

    Returns a task dict with scope_status, negotiation_reopen_allowed,
    and a checklist derived from both the condition and scope context.
    """
    if not issue.get("issue_candidate", False):
        return {
            "task_generated":  False,
            "reason":          issue.get("reason", "issue suppressed"),
            "scope_status":    issue.get("scope_status", "bypassed"),
            "claim_id":        issue.get("claim_id", "?"),
            "condition":       issue.get("condition", "?"),
            "execution_allowed": False,
            "moves_money":     False,
            "advisory":        True,
        }

    claim_id       = issue.get("claim_id", "unknown")
    condition      = issue.get("condition", "unknown")
    scope_status   = issue.get("scope_status", "applicable")
    scope          = issue.get("scope", "")
    prereq_state   = issue.get("prerequisite_state", "unknown")
    nc             = issue.get("negotiation_context", {})
    contestable    = nc.get("contestable", True)
    hard_enforce   = nc.get("hard_enforcement", False)
    reopen         = nc.get("negotiation_reopen_allowed", True)

    hint           = issue.get("agent_task_hint", {})
    capabilities   = hint.get("required_capabilities",
                               issue.get("required_capabilities", ["evidence_checking"]))
    task_type      = CONDITION_TASK_TYPE.get(condition, hint.get("task_type", "evidence_review"))
    priority       = SCOPE_STATUS_PRIORITY.get(scope_status, "medium")

    # Checklist: condition-specific + scope addons + defaults
    checklist: list[str] = []
    checklist += CONDITION_CHECKLIST.get(condition, DEFAULT_CHECKLIST)
    if scope_status == "applicable" and scope:
        for addon in SCOPE_CHECKLIST_ADDONS:
            # Substitute actual scope value
            checklist.append(addon.replace("non_precertified_spaces", scope))
    if prereq_state == "weakened":
        checklist.append(
            "Note: prerequisite is weakened. A bypass path (equivalent safety evidence) "
            "is accepted by the federation — but this claim does not qualify. "
            "Resolve directly or produce a bypass-eligible plan."
        )
    if contestable:
        checklist.append(
            "Note: this prerequisite is contestable. If you believe it should not apply "
            "here, contest via a better plan tree. No coordinator needed."
        )

    return {
        "task_generated":            True,
        "task_type":                 task_type,
        "claim_id":                  claim_id,
        "condition":                 condition,
        "scope_status":              scope_status,
        "scope":                     scope,
        "prerequisite_state":        prereq_state,
        "required_capabilities":     capabilities,
        "priority":                  priority,
        "execution_allowed":         False,
        "reason":                    "requires human/agent negotiation before execution",
        "hard_enforcement":          hard_enforce,
        "contestable":               contestable,
        "negotiation_reopen_allowed": reopen,
        "checklist":                 checklist,
        "source_issue_title":        issue.get("title", ""),
        "authority":                 "none",
        "advisory":                  True,
        "moves_money":               False,
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

def _print_task(task: dict[str, Any]) -> None:
    if not task.get("task_generated"):
        print(f"\n  Task NOT generated — {task.get('reason','?')}")
        print(f"  scope_status: {task.get('scope_status')}  claim: {task.get('claim_id')}")
        return

    print(f"\n  {'='*55}")
    print(f"  Scoped Agent Task Specification")
    print(f"  {'='*55}")
    print(f"  Claim:               {task['claim_id']}")
    print(f"  Condition:           {task['condition']}")
    print(f"  Scope status:        {task['scope_status']}")
    print(f"  Scope:               {task.get('scope', '(none)')}")
    print(f"  Prerequisite state:  {task.get('prerequisite_state')}")
    print(f"  Task type:           {task['task_type']}")
    print(f"  Priority:            {task['priority']}")
    print(f"  Capabilities:        {task['required_capabilities']}")
    print(f"  Execution allowed:   {task['execution_allowed']}")
    print(f"  Hard enforcement:    {task['hard_enforcement']}")
    print(f"  Contestable:         {task['contestable']}")
    print(f"  Negotiation reopen:  {task['negotiation_reopen_allowed']}")
    print(f"  moves_money:         {task['moves_money']}")
    print(f"\n  Checklist:")
    for i, item in enumerate(task["checklist"], 1):
        print(f"    {i}. {item}")
    print()


def main() -> None:
    p = argparse.ArgumentParser(
        description="Convert a scoped issue draft to an agent task specification.",
    )
    p.add_argument("issue_file", metavar="ISSUE_FILE")
    p.add_argument("--json", action="store_true", dest="json_output")
    args = p.parse_args()

    if not os.path.exists(args.issue_file):
        print(f"ERROR: file not found: {args.issue_file}", file=sys.stderr)
        sys.exit(1)

    with open(args.issue_file) as f:
        data = json.load(f)

    if isinstance(data, list):
        issues = data
    else:
        issues = [data]

    tasks = [scoped_issue_to_task(iss) for iss in issues]

    if args.json_output:
        out = tasks[0] if len(tasks) == 1 else tasks
        print(json.dumps(out, indent=2))
        return

    print(f"\nScoped Issue → Agent Task")
    print(f"Input: {args.issue_file}")
    print(f"(No task created — specification only)")
    for t in tasks:
        _print_task(t)


if __name__ == "__main__":
    main()
