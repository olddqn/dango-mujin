"""
issue_to_agent_task.py — Gitlawb issue draft → agent task specification

Reads an issue draft (output of claim_to_issue.py) and produces a structured
agent task specification. No task is created, submitted, or executed.
This is a translation layer only.

No hard enforcement. No funds. No external network. stdlib only.

Usage:
    python issue_to_agent_task.py <issue-draft.json>
    python issue_to_agent_task.py <issue-draft.json> --json
"""

import json
import sys
import os


# ---------------------------------------------------------------------------
# Capability maps
# ---------------------------------------------------------------------------

SEVERITY_CAPABILITIES = {
    "safety_critical": ["safety_review", "evidence_checking", "structural_assessment"],
    "risk":            ["risk_review",   "evidence_checking"],
    "coordination":    ["coordination_review"],
    "dignity":         ["dignity_review", "consent_verification"],
}

TASK_TYPE_BY_SEVERITY = {
    "safety_critical": "risk_review",
    "risk":            "risk_review",
    "coordination":    "coordination_task",
    "dignity":         "dignity_review",
}

PRIORITY_BY_SEVERITY = {
    "safety_critical": "high",
    "risk":            "medium",
    "coordination":    "low",
    "dignity":         "high",
}


# ---------------------------------------------------------------------------
# Core translation
# ---------------------------------------------------------------------------

def issue_to_agent_task(issue_draft: dict) -> dict:
    """
    Translate an issue draft into an agent task specification.

    The task is never executed automatically. execution_allowed is always False
    unless an explicit human/agent negotiation has occurred (outside this module).

    Returns:
        {
          task_type, claim_id, condition, required_capabilities,
          priority, execution_allowed, reason,
          prerequisite_context, bypass_context,
          checklist, authority, advisory
        }
    """
    claim_id     = issue_draft.get("source_claim_id", "unknown")
    condition    = issue_draft.get("missing_condition", "unknown")
    severity     = issue_draft.get("severity", "unknown")
    is_fed_prereq = issue_draft.get("federation_prerequisite", False)
    prereq_state = issue_draft.get("prerequisite_state", "")
    prereq_scope = issue_draft.get("prerequisite_scope", "")
    bypass_avail = issue_draft.get("bypass_available", False)

    task_type    = TASK_TYPE_BY_SEVERITY.get(severity, "evidence_review")
    capabilities = SEVERITY_CAPABILITIES.get(severity, ["evidence_checking"])
    priority     = PRIORITY_BY_SEVERITY.get(severity, "medium")

    # --- prerequisite context ---
    prereq_ctx = {}
    if is_fed_prereq:
        prereq_ctx = {
            "is_federation_prerequisite": True,
            "state":        prereq_state,
            "scope":        prereq_scope,
            "note": (
                f"This condition is a federation prerequisite in state '{prereq_state}'."
                f" It applies to claims in scope '{prereq_scope}'."
            ),
        }

    # --- bypass context ---
    bypass_ctx = {
        "bypass_available_for_this_claim": bypass_avail,
        "bypass_note": (
            "No bypass path recognised for this claim — condition must be satisfied directly."
            if not bypass_avail
            else "A bypass path exists. Agent should verify whether the claim qualifies."
        ),
    }

    # --- checklist ---
    checklist = [
        f"Verify that `{condition}` is not already present in the active plan.",
        f"Collect evidence that `{condition}` is satisfied (e.g., inspection certificate, audit report).",
        "Confirm dignity guard: no identity exposure, revocable consent, participant consent.",
        "Attach evidence to a PR referencing the issue.",
        "Do not execute any physical or financial action — evidence submission only.",
        "Agent must not auto-approve. Human or peer agent review required before merge.",
    ]
    if bypass_avail:
        checklist.insert(2, "Check whether the claim has a recognised bypass path (precertification + external audit).")
    if is_fed_prereq:
        checklist.append(
            f"Note: This condition has federation precedent (convergence_count ≥ 2). "
            f"Resolution here contributes to federation evidence."
        )

    return {
        "task_type":             task_type,
        "claim_id":              claim_id,
        "condition":             condition,
        "required_capabilities": capabilities,
        "priority":              priority,
        "execution_allowed":     False,
        "reason":                "requires human/agent negotiation before execution",
        "prerequisite_context":  prereq_ctx,
        "bypass_context":        bypass_ctx,
        "checklist":             checklist,
        "authority":             "none",
        "advisory":              True,
        "moves_money":           False,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_task(task: dict) -> None:
    print(f"\n{'='*60}")
    print(f"  Agent Task Specification")
    print(f"{'='*60}")
    print(f"  Claim:          {task['claim_id']}")
    print(f"  Condition:      {task['condition']}")
    print(f"  Task type:      {task['task_type']}")
    print(f"  Priority:       {task['priority']}")
    print(f"  Capabilities:   {task['required_capabilities']}")
    print(f"  Execution:      {'ALLOWED' if task['execution_allowed'] else 'NOT ALLOWED'}")
    print(f"  Reason:         {task['reason']}")
    print()
    if task.get("prerequisite_context"):
        ctx = task["prerequisite_context"]
        print(f"  Federation prerequisite: {ctx.get('is_federation_prerequisite')}")
        print(f"  Prereq state: {ctx.get('state')} / scope: {ctx.get('scope')}")
    bctx = task.get("bypass_context", {})
    print(f"  Bypass for this claim: {bctx.get('bypass_available_for_this_claim')}")
    print()
    print(f"  Checklist:")
    for i, item in enumerate(task["checklist"], 1):
        print(f"    {i}. {item}")
    print()
    print(f"  authority: {task['authority']} · advisory: {task['advisory']} · moves_money: {task['moves_money']}")
    print()


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    input_path = args[0]
    as_json    = "--json" in args

    if not os.path.exists(input_path):
        print(f"ERROR: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    with open(input_path) as f:
        data = json.load(f)

    # Accept either a single issue draft or the full output of claim_to_issue
    if "issue_draft" in data:
        issue_draft = data
    elif isinstance(data, list):
        issue_draft = data[0]
    else:
        print("ERROR: input must be an issue draft (output of claim_to_issue.py)", file=sys.stderr)
        sys.exit(1)

    task = issue_to_agent_task(issue_draft)

    if as_json:
        print(json.dumps(task, indent=2))
    else:
        print(f"\nDan-Go → Agent Task Specification")
        print(f"Input: {input_path}")
        print(f"(No task created — specification only)")
        _print_task(task)


if __name__ == "__main__":
    main()
