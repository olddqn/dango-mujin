"""
issue_markdown_renderer.py — Issue JSON → GitHub-compatible Markdown

Reads a scoped issue draft (output of scoped_plan_to_issue.py or
scoped_issue_filter.py) and produces a human-readable Markdown document
suitable for GitHub issues, Gitlawb issues, or any Markdown renderer.

Key design principles:
  - applicable prerequisites → full issue body with negotiation context
  - bypassed prerequisites   → suppression explanation (no issue body)
  - all output is advisory, contestable, execution-disabled
  - no HTML dependency — pure Markdown only
  - deterministic output for the same input
  - human-readable auditability is part of the protocol

No API. No network. No external libraries. stdlib only.

Human-readable negotiation is part of the protocol.

Usage:
    from issue_markdown_renderer import render_issue_markdown, render_suppressed_markdown
    md = render_issue_markdown(issue_dict)
    md = render_suppressed_markdown(issue_dict)
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_FILE_DIR = Path(__file__).parent
sys.path.insert(0, str(_FILE_DIR))

from negotiation_context_renderer import (
    render_negotiation_context,
    render_dignity_guard,
    render_advisory_footer,
)
from prerequisite_markdown_renderer import (
    render_applicable_section,
    render_bypassed_section,
    render_prerequisite_state_section,
    render_resolution_guide,
)


# ── Applicable issue renderer ─────────────────────────────────────────────────

def render_issue_markdown(issue: dict[str, Any]) -> str:
    """
    Render an applicable scoped issue draft as GitHub-compatible Markdown.

    Returns a single string containing the full issue body.
    """
    claim_id     = issue.get("claim_id", "unknown")
    condition    = issue.get("condition", "unknown")
    scope_status = issue.get("scope_status", "applicable")
    scope        = issue.get("scope", "")
    prereq_state = issue.get("prerequisite_state", "unknown")
    labels       = issue.get("labels", [])
    nc           = issue.get("negotiation_context", {})
    hint         = issue.get("agent_task_hint", {})

    # Try to get scope reasoning from the body or negotiation context
    scope_reasoning: list[str] = []
    body_text = issue.get("body", "")
    if "Scope Reasoning" in body_text:
        # Extract reasoning lines from body
        in_reasoning = False
        for line in body_text.splitlines():
            if "### Scope Reasoning" in line:
                in_reasoning = True
                continue
            if in_reasoning:
                if line.startswith("###") or line.startswith("##"):
                    break
                stripped = line.strip()
                if stripped.startswith("- "):
                    scope_reasoning.append(stripped[2:])
                elif stripped and not stripped.startswith("#"):
                    scope_reasoning.append(stripped)

    # Extract convergence count from body if present
    convergence_count: int | None = None
    for line in body_text.splitlines():
        if "independently by" in line and "claim(s)" in line:
            for tok in line.split():
                if tok.isdigit():
                    convergence_count = int(tok)
                    break

    # ── Title ──
    title = issue.get("title", f"[Scoped Prerequisite] {condition} required — {claim_id}")
    lines: list[str] = []
    lines.append(f"# {title}")
    lines.append("")

    # ── Label strip ──
    if labels:
        label_str = " ".join(f"`{lbl}`" for lbl in labels)
        lines.append(f"**Labels:** {label_str}")
        lines.append("")

    # ── Claim / condition summary ──
    lines.append("## Claim")
    lines.append("")
    lines.append(f"`{claim_id}`")
    lines.append("")
    lines.append("## Condition")
    lines.append("")
    lines.append(f"`{condition}`")
    lines.append("")
    lines.append("## Scope Status")
    lines.append("")
    lines.append(f"`{scope_status}`" + (f" — scope: `{scope}`" if scope else ""))
    lines.append("")

    # ── Applicable section ──
    lines.append(render_applicable_section(
        condition    = condition,
        scope        = scope,
        scope_reasoning = scope_reasoning,
        prerequisite_state = prereq_state,
        claim_id     = claim_id,
    ))

    # ── Prerequisite lifecycle ──
    lines.append(render_prerequisite_state_section(prereq_state, condition))

    # ── Resolution guide ──
    lines.append(render_resolution_guide(condition, claim_id))

    # ── Negotiation context ──
    lines.append(render_negotiation_context(
        nc               = nc,
        claim_id         = claim_id,
        condition        = condition,
        convergence_count = convergence_count,
    ))

    # ── Agent task hint ──
    if hint:
        task_type    = hint.get("task_type", "evidence_review")
        capabilities = hint.get("required_capabilities", [])
        lines.append("## Agent Task Hint")
        lines.append("")
        lines.append(f"- task_type: `{task_type}`")
        lines.append(f"- required_capabilities: {', '.join(f'`{c}`' for c in capabilities)}")
        lines.append(f"- execution_allowed: `false`")
        lines.append("")

    # ── Dignity guard ──
    lines.append(render_dignity_guard(issue))

    # ── Important notice ──
    lines.append("## Important")
    lines.append("")
    lines.append("This issue is advisory only.")
    lines.append("PR merge does not establish truth.")
    lines.append("Negotiation may reopen at any time.")
    lines.append("")
    lines.append(
        "A `plan_correction` event by the plan author is needed to formally "
        "update the plan tree after a PR merge."
    )
    lines.append("")

    # ── Footer ──
    lines.append(render_advisory_footer())

    return "\n".join(lines)


# ── Suppression renderer ──────────────────────────────────────────────────────

def render_suppressed_markdown(issue: dict[str, Any]) -> str:
    """
    Render a suppressed (bypassed) scoped issue as an explanation document.

    Even though no issue is created, the bypass is rendered transparently
    so auditors and participants can understand why the issue was suppressed.
    Bypass transparency is part of the protocol.
    """
    claim_id         = issue.get("claim_id", "unknown")
    condition        = issue.get("condition", "unknown")
    scope_status     = issue.get("scope_status", "bypassed")
    reason           = issue.get("reason", "suppressed")
    bypass_conditions = issue.get("bypass_conditions", [])
    filter_reason    = issue.get("filter_reason", "")

    lines: list[str] = []

    lines.append(
        f"# [Scoped Prerequisite] {condition} bypassed — {claim_id}"
    )
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append("Issue suppressed.")
    lines.append("")
    lines.append(f"- scope_status: `{scope_status}`")
    lines.append(f"- issue_candidate: `false`")
    lines.append(f"- reason: {reason}")
    if filter_reason:
        lines.append(f"- filter_reason: {filter_reason}")
    lines.append("")

    # ── Bypass explanation ──
    lines.append(render_bypassed_section(
        condition        = condition,
        bypass_conditions = bypass_conditions,
        claim_id         = claim_id,
    ))

    # ── Transparency note ──
    lines.append("## Transparency")
    lines.append("")
    lines.append(
        "Even though no issue was generated, this suppression record exists "
        "so that the decision can be audited and contested."
    )
    lines.append("")
    lines.append("If you believe the bypass should not apply:")
    lines.append("")
    lines.append(
        "1. Submit a plan tree that removes the bypass conditions "
        f"and demonstrates that `{condition}` is still required."
    )
    lines.append(
        "2. Reference this suppression record in the PR description."
    )
    lines.append(
        "3. If the PR is accepted, a new issue draft will be generated "
        "for the corrected plan tree."
    )
    lines.append("")

    # ── Footer ──
    lines.append(render_advisory_footer())

    return "\n".join(lines)


# ── Dispatcher ────────────────────────────────────────────────────────────────

def render_markdown(issue: dict[str, Any]) -> str:
    """
    Dispatch to applicable or suppressed renderer based on issue_candidate field.
    """
    if issue.get("issue_candidate", False):
        return render_issue_markdown(issue)
    else:
        return render_suppressed_markdown(issue)
