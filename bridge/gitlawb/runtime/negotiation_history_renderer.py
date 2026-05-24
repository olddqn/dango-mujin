"""
negotiation_history_renderer.py — Render full negotiation history as Markdown

Reads the Issue #1 negotiation artifacts (pr-feedback, reopen-event,
plan-correction) and renders a human-readable Markdown history showing
the full append-only negotiation lifecycle:

  Issue Created
  → PR Draft Submitted
  → PR Feedback (merged)
  → Negotiation Reopened
  → Plan Correction Proposed

No real issue or PR is accessed. stdlib only.

Human-readable negotiation is part of the protocol.
A merged PR is evidence. Not authority.

Usage:
    python gitlawb/runtime/negotiation_history_renderer.py
    python gitlawb/runtime/negotiation_history_renderer.py --json
    python gitlawb/runtime/negotiation_history_renderer.py \\
      > gitlawb/examples/issue-001.negotiation-history.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_FILE_DIR   = Path(__file__).parent
_BRIDGE_DIR = _FILE_DIR.parent.parent
_EX_DIR     = _FILE_DIR.parent / "examples"

# ── Artifact loader ───────────────────────────────────────────────────────────

def _load(filename: str) -> dict[str, Any] | list[dict[str, Any]] | None:
    path = _EX_DIR / filename
    if not path.exists():
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


def _first(data: Any) -> dict[str, Any]:
    if isinstance(data, list) and data:
        return data[0]
    return data or {}


def _merged_event(feedback_data: Any) -> dict[str, Any] | None:
    if isinstance(feedback_data, list):
        for fb in feedback_data:
            if isinstance(fb, dict):
                rf = fb.get("reality_feedback", fb)
                if rf.get("source") == "pr_merged" or rf.get("pr_event") == "pr_merged":
                    return fb
    return None


# ── Core renderer ─────────────────────────────────────────────────────────────

def render_negotiation_history() -> str:  # noqa: C901
    """
    Render the full negotiation history for Issue #1 as Markdown.
    """
    # Load artifacts
    issue_data    = _load("scoped-issue-housing-007.output.json")
    feedback_data = _load("issue-001.pr-feedback.json") or _load("scoped-pr-feedback.output.json")
    reopen_data   = _load("issue-001.reopen-event.json")
    correction    = _load("issue-001.plan-correction.json")

    issue     = _first(issue_data)    if issue_data    else {}
    reopen    = reopen_data           if isinstance(reopen_data, dict) else {}
    corr      = correction            if isinstance(correction, dict)  else {}
    merged_fb = _merged_event(feedback_data) if feedback_data else None

    claim_id  = issue.get("claim_id", "housing-007")
    condition = issue.get("condition", "space_safety_assessed")
    nc        = issue.get("negotiation_context", {})

    lines: list[str] = []

    # ── Title ──
    lines.append("# Negotiation History — Issue #1")
    lines.append("")
    lines.append(f"**Claim:** `{claim_id}`")
    lines.append(f"**Condition:** `{condition}`")
    lines.append(f"**GitHub:** https://github.com/olddqn/dango-mujin/issues/1")
    lines.append("")
    lines.append("> This is an append-only record. No step is deleted or overwritten.")
    lines.append("> A merged PR is evidence. Not authority.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Step 1: Issue Created ──
    lines.append("## 1. Issue Created")
    lines.append("")
    lines.append("Scoped prerequisite identified:")
    lines.append(f"`{condition}`")
    lines.append("")
    lines.append(f"- scope_status: `{issue.get('scope_status','applicable')}`")
    lines.append(f"- scope: `{issue.get('scope','non_precertified_spaces')}`")
    lines.append(f"- prerequisite_state: `{issue.get('prerequisite_state','weakened')}`")
    lines.append(f"- authority: `none`")
    lines.append(f"- contestable: `true`")
    lines.append(f"- negotiation_reopen_allowed: `true`")
    lines.append("")
    if nc:
        lines.append(
            "The prerequisite was identified through federation convergence. "
            "No coordinator declared it."
        )
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Step 2: PR Draft Submitted ──
    lines.append("## 2. PR Draft Submitted")
    lines.append("")
    lines.append("Evidence added:")
    lines.append("")
    lines.append("- local structural review")
    lines.append("- safety inspection notes")
    lines.append("- community access risk assessment")
    lines.append("")
    lines.append(
        "The PR was submitted as advisory evidence. "
        "It did not claim to establish truth."
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Step 3: PR Feedback ──
    lines.append("## 3. PR Feedback")
    lines.append("")

    if feedback_data and isinstance(feedback_data, list):
        for fb in feedback_data:
            if not isinstance(fb, dict):
                continue
            ev    = fb.get("pr_event", "?")
            rf    = fb.get("reality_feedback", {})
            ftype = rf.get("feedback_type", "?")
            note  = rf.get("note", "")
            ms    = fb.get("markdown_summary", note[:80] if note else "")
            lines.append(f"**`{ev}`** → `{ftype}`")
            if ms:
                lines.append(f"> {ms}")
            lines.append("")
    else:
        lines.append("`pr_opened` → `condition_evidence_submitted`")
        lines.append("")
        lines.append("`pr_reviewed` → `condition_evidence_reviewed`")
        lines.append("")
        lines.append("`pr_merged` → `condition_evidence_accepted`")
        lines.append("")

    if merged_fb:
        rf = merged_fb.get("reality_feedback", {})
        lines.append(
            "> **Advisory note on merge:**"
        )
        lines.append(
            "> A merged PR is evidence. Not authority. "
            "Negotiation remained reopenable."
        )
        lines.append("")

    lines.append("---")
    lines.append("")

    # ── Step 4: Negotiation Reopened ──
    lines.append("## 4. Negotiation Reopened")
    lines.append("")

    if reopen:
        reason = reopen.get("reason", "counter_evidence")
        reason_desc = reopen.get("reason_description", "")
        lines.append(f"**Reason:** `{reason}`")
        lines.append("")
        if reason_desc:
            lines.append(reason_desc)
            lines.append("")
        lines.append(
            "The negotiation_reopened event is append-only. "
            "The merged PR is not invalidated — it remains as evidence."
        )
        lines.append("")
        lines.append(f"- authority: `none`")
        lines.append(f"- contestable: `true`")
        lines.append(f"- append_only: `true`")
        lines.append("")
    else:
        lines.append("**Reason:** `counter_evidence_submitted`")
        lines.append("")
        lines.append(
            "New evidence was submitted that qualifies the previously accepted evidence."
        )
        lines.append("")

    lines.append(
        "> **A merged PR is evidence. Not authority.** "
        "The reopen event records a new negotiation phase — "
        "it does not undo the merge."
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Step 5: Plan Correction Proposed ──
    lines.append("## 5. Plan Correction Proposed")
    lines.append("")

    if corr:
        orig  = corr.get("corrects_plan", "plan-housing-007-v1")
        prop  = corr.get("proposed_plan", "plan-housing-007-v2")
        changes = corr.get("proposed_plan_changes", [])
        lines.append(f"**Original plan:** `{orig}`")
        lines.append(f"**Proposed plan:** `{prop}`")
        lines.append("")
        if changes:
            lines.append("Proposed changes:")
            lines.append("")
            for ch in changes:
                lines.append(f"- {ch}")
            lines.append("")
        lines.append(
            f"The original plan `{orig}` is preserved in the append-only event log."
        )
        lines.append("")
    else:
        lines.append("**Original plan:** `plan-housing-007-v1`")
        lines.append("")
        lines.append("**Proposed plan:** `plan-housing-007-v2`")
        lines.append("")
        lines.append(
            "The plan correction is proposed — not executed. "
            "Human or peer agent review is required before acceptance."
        )
        lines.append("")

    lines.append(
        "> The original plan is NOT deleted. "
        "Both versions remain in the append-only event log."
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Summary ──
    lines.append("## Summary")
    lines.append("")
    lines.append("| Step | Event | Authority | Append-Only |")
    lines.append("|------|-------|-----------|-------------|")
    lines.append("| 1 | issue_created | none | ✓ |")
    lines.append("| 2 | pr_draft_submitted | none | ✓ |")
    lines.append("| 3 | pr_feedback (merged) | none | ✓ |")
    lines.append("| 4 | negotiation_reopened | none | ✓ |")
    lines.append("| 5 | plan_correction_proposed | none | ✓ |")
    lines.append("")
    lines.append("**Invariants across all steps:**")
    lines.append("")
    lines.append("- `execution_allowed: false`")
    lines.append("- `moves_money: false`")
    lines.append("- `hard_enforcement: false`")
    lines.append("- `authority: none`")
    lines.append("- `append_only: true`")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(
        "_Human-readable negotiation is part of the protocol._"
    )
    lines.append(
        "_A merged PR is evidence. Not authority._"
    )
    lines.append("")

    return "\n".join(lines)


def _build_json_summary() -> list[dict[str, Any]]:
    """Return a JSON-serialisable summary of the negotiation history."""
    issue_data    = _load("scoped-issue-housing-007.output.json")
    feedback_data = _load("issue-001.pr-feedback.json") or _load("scoped-pr-feedback.output.json")
    reopen_data   = _load("issue-001.reopen-event.json")
    correction    = _load("issue-001.plan-correction.json")

    issue  = _first(issue_data) if issue_data else {}
    reopen = reopen_data if isinstance(reopen_data, dict) else {}
    corr   = correction  if isinstance(correction, dict) else {}

    steps: list[dict[str, Any]] = [
        {
            "step": 1, "event": "issue_created",
            "claim_id": issue.get("claim_id","housing-007"),
            "condition": issue.get("condition","space_safety_assessed"),
            "authority": "none", "append_only": True,
        },
        {
            "step": 2, "event": "pr_draft_submitted",
            "claim_id": issue.get("claim_id","housing-007"),
            "condition": issue.get("condition","space_safety_assessed"),
            "authority": "none", "append_only": True,
        },
    ]

    if feedback_data and isinstance(feedback_data, list):
        for fb in feedback_data:
            ev = fb.get("pr_event", "?")
            steps.append({
                "step": len(steps) + 1,
                "event": f"pr_feedback:{ev}",
                "claim_id": issue.get("claim_id","housing-007"),
                "condition": issue.get("condition","space_safety_assessed"),
                "authority": "none", "append_only": True,
                "reopenable": True,
            })
    else:
        steps.append({"step": 3, "event": "pr_feedback", "authority": "none", "append_only": True})

    steps.append({
        "step": len(steps) + 1,
        "event": "negotiation_reopened",
        "reason": reopen.get("reason","counter_evidence"),
        "authority": "none", "append_only": True,
    })
    steps.append({
        "step": len(steps) + 1,
        "event": "plan_correction_proposed",
        "corrects_plan": corr.get("corrects_plan","plan-housing-007-v1"),
        "proposed_plan": corr.get("proposed_plan","plan-housing-007-v2"),
        "authority": "none", "append_only": True,
    })

    return steps


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Render the full negotiation history for Issue #1.",
    )
    p.add_argument("--json", action="store_true", dest="json_output")
    args = p.parse_args()

    if args.json_output:
        print(json.dumps(_build_json_summary(), indent=2))
    else:
        print(render_negotiation_history())


if __name__ == "__main__":
    main()
