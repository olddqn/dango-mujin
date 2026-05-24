"""
pr_draft_renderer.py — Scoped issue → PR Draft Markdown

Reads a scoped issue draft (output of scoped_plan_to_issue.py) and produces
a GitHub-compatible PR Draft Markdown body.

The PR draft:
  - describes the condition being addressed
  - suggests evidence types to attach
  - carries the full negotiation context
  - is explicit that PR merge does not establish truth
  - is reopenable after merge

No real PR is created. No API is called. Markdown generation only.
stdlib only.

A merged PR is evidence. Not authority.

Usage:
    python gitlawb/runtime/pr_draft_renderer.py <scoped-issue.json>
    python gitlawb/runtime/pr_draft_renderer.py <scoped-issue.json> --json
    python gitlawb/runtime/pr_draft_renderer.py <scoped-issue.json> \\
      > gitlawb/examples/issue-001.pr-draft.md
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

_FILE_DIR = Path(__file__).parent
sys.path.insert(0, str(_FILE_DIR))

# ── Evidence suggestion map ───────────────────────────────────────────────────

CONDITION_EVIDENCE: dict[str, list[str]] = {
    "space_safety_assessed": [
        "local structural review",
        "safety inspection notes",
        "community access risk assessment",
    ],
    "food_safety_reviewed": [
        "food handling certification",
        "volunteer training records",
        "distribution site safety assessment",
    ],
    "structural_assessment": [
        "structural engineer assessment",
        "building permit records",
        "load-bearing capacity documentation",
    ],
    "local_structural_assessment": [
        "on-site structural inspection report",
        "local authority sign-off",
        "modification documentation",
    ],
    "risk_assessment": [
        "risk register",
        "mitigation plan",
        "community consultation notes",
    ],
    "participant_consent": [
        "signed consent forms",
        "revocable consent records",
        "anonymised participant acknowledgements",
    ],
    "legal_ownership_confirmed": [
        "title documents",
        "lease agreement",
        "authority authorisation letter",
    ],
}

_DEFAULT_EVIDENCE = [
    "inspection certificate or equivalent",
    "authority sign-off documentation",
    "community review notes",
]


def _get_evidence(condition: str) -> list[str]:
    return CONDITION_EVIDENCE.get(condition, _DEFAULT_EVIDENCE)


# ── Core renderer ─────────────────────────────────────────────────────────────

def render_pr_draft_markdown(issue: dict[str, Any]) -> str:
    """
    Render a PR draft Markdown body from a scoped issue draft.
    """
    claim_id     = issue.get("claim_id", "unknown")
    condition    = issue.get("condition", "unknown")
    scope_status = issue.get("scope_status", "applicable")
    scope        = issue.get("scope", "")
    prereq_state = issue.get("prerequisite_state", "unknown")
    nc           = issue.get("negotiation_context", {})
    contestable  = nc.get("contestable", True)
    hard_enforce = nc.get("hard_enforcement", False)
    reopen       = nc.get("negotiation_reopen_allowed", True)

    evidence     = _get_evidence(condition)

    # Derive issue reference from claim_id
    issue_ref = "#1" if claim_id == "housing-007" else f"#{claim_id}"

    lines: list[str] = []

    lines.append(
        f"# PR Draft — Add safety review requirement for {claim_id}"
    )
    lines.append("")

    # ── Resolves ──
    lines.append(f"Resolves: {issue_ref}")
    lines.append(f"Claim: `{claim_id}`")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Condition Addressed ──
    lines.append("## Condition Addressed")
    lines.append("")
    lines.append(f"`{condition}`")
    lines.append("")
    if scope:
        lines.append(f"Scope: `{scope}`")
        lines.append("")
    lines.append("---")
    lines.append("")

    # ── Evidence Added ──
    lines.append("## Evidence Added")
    lines.append("")
    for ev in evidence:
        lines.append(f"- {ev}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Negotiation Context ──
    lines.append("## Negotiation Context")
    lines.append("")
    lines.append("This PR does not establish truth.")
    lines.append("")
    lines.append(
        "It contributes evidence toward resolving the scoped prerequisite."
    )
    lines.append("")
    lines.append("Negotiation may reopen.")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|---|---|")
    lines.append("| authority | none |")
    lines.append(f"| contestable | {str(contestable).lower()} |")
    lines.append(f"| hard_enforcement | {str(hard_enforce).lower()} |")
    lines.append("| execution_allowed | false |")
    lines.append("| moves_money | false |")
    lines.append(f"| negotiation_reopen_allowed | {str(reopen).lower()} |")
    lines.append(f"| reopenable | true |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Reopenability ──
    lines.append("## Reopenability")
    lines.append("")
    lines.append("A merged PR is evidence. Not authority.")
    lines.append("")
    lines.append(
        "After this PR is merged, negotiation may reopen if:"
    )
    lines.append("")
    lines.append("- counter evidence is submitted")
    lines.append("- bypass equivalence is demonstrated")
    lines.append("- a dignity violation is identified")
    lines.append(f"- the `{condition}` prerequisite is contested or deprecated")
    lines.append("")
    lines.append(
        "A `plan_correction` event by the plan author is required "
        "to formally update the plan tree."
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Dignity Guard ──
    lines.append("## Dignity Guard")
    lines.append("")
    lines.append("- participant_consent required")
    lines.append("- revocable_consent required")
    lines.append("- no_identity_exposure: required")
    lines.append("- execution_allowed: false")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Important ──
    lines.append("## Important")
    lines.append("")
    lines.append("This PR is advisory only.")
    lines.append("")
    lines.append("- No action is executed automatically.")
    lines.append("- No funds are moved.")
    lines.append("- No authority is granted.")
    lines.append("- Merge does not close negotiation.")
    lines.append("")
    lines.append(
        "> **A merged PR is evidence. Not authority.**"
    )
    lines.append("")

    return "\n".join(lines)


# ── JSON envelope ─────────────────────────────────────────────────────────────

def render_pr_draft_json(issue: dict[str, Any]) -> dict[str, Any]:
    """
    Return a JSON envelope for the PR draft.
    """
    claim_id  = issue.get("claim_id", "unknown")
    condition = issue.get("condition", "unknown")
    nc        = issue.get("negotiation_context", {})

    return {
        "event_type":      "pr_draft_rendered",
        "claim_id":        claim_id,
        "condition":       condition,
        "scope_status":    issue.get("scope_status", "applicable"),
        "pr_title":        f"Add safety evidence for {condition} — {claim_id}",
        "pr_body_source":  f"gitlawb/examples/github-issue-housing-007.md",
        "resolves_issue":  1 if claim_id == "housing-007" else None,
        "evidence_types":  _get_evidence(condition),
        "negotiation_context": nc,
        "execution_allowed":  False,
        "moves_money":        False,
        "advisory":           True,
        "reopenable":         True,
        "reopen_reason_examples": [
            "counter_evidence",
            "bypass_equivalence",
            "dignity_violation",
            "prerequisite_deprecation",
        ],
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Render a PR draft Markdown from a scoped issue draft.",
    )
    p.add_argument("issue_file", metavar="ISSUE_FILE")
    p.add_argument("--json", action="store_true", dest="json_output")
    args = p.parse_args()

    if not os.path.exists(args.issue_file):
        print(f"ERROR: file not found: {args.issue_file}", file=sys.stderr)
        sys.exit(1)

    with open(args.issue_file) as f:
        data = json.load(f)

    issue = data[0] if isinstance(data, list) else data

    if not issue.get("issue_candidate", False):
        print(
            f"ERROR: issue is suppressed — no PR draft generated for bypassed issues.",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.json_output:
        print(json.dumps(render_pr_draft_json(issue), indent=2))
    else:
        print(render_pr_draft_markdown(issue))


if __name__ == "__main__":
    main()
