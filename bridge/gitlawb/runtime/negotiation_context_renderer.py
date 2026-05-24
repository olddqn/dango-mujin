"""
negotiation_context_renderer.py — Render negotiation context as Markdown

Produces human-readable Markdown sections for:
  - contestability
  - authority: none
  - prerequisite lifecycle state
  - negotiation reopenability
  - federation convergence note

No API. No network. stdlib only.

Human-readable negotiation is part of the protocol.

Usage:
    from negotiation_context_renderer import render_negotiation_context
    md = render_negotiation_context(negotiation_context_dict)
"""

from __future__ import annotations

from typing import Any

# ── Lifecycle state descriptions ──────────────────────────────────────────────

PREREQUISITE_STATE_DESCRIPTIONS: dict[str, str] = {
    "promoted": (
        "This prerequisite was promoted from an emerging pattern "
        "when 2 or more independent claims discovered the same condition. "
        "It is now a federation signal — advisory, not mandatory."
    ),
    "reaffirmed": (
        "This prerequisite has been reaffirmed by additional independent claims. "
        "Its relevance is strengthening, but it remains advisory and contestable."
    ),
    "weakened": (
        "This prerequisite has been weakened — a recognised bypass path exists. "
        "Claims with precertification or equivalent safety evidence may bypass it. "
        "It still applies to claims in scope that do not qualify for bypass."
    ),
    "deprecated": (
        "This prerequisite is deprecated. "
        "Its lifecycle has ended. No new issue drafts should be generated from it."
    ),
}

SCOPE_DESCRIPTIONS: dict[str, str] = {
    "non_precertified_spaces": (
        "This prerequisite applies to spaces that are not precertified "
        "and have not been independently audited for structural or fire safety."
    ),
    "modified_existing_structures": (
        "This prerequisite applies to existing structures that have been "
        "locally modified and carry no external audit trail."
    ),
    "applicable": (
        "This prerequisite is applicable in the context of this claim."
    ),
}


# ── Core renderer ─────────────────────────────────────────────────────────────

def render_negotiation_context(
    nc: dict[str, Any],
    claim_id: str = "",
    condition: str = "",
    convergence_count: int | None = None,
) -> str:
    """
    Render a negotiation_context dict as a Markdown section.

    Returns a string of Markdown lines (no trailing newline).
    """
    contestable  = nc.get("contestable", True)
    authority    = nc.get("authority", "none")
    hard_enforce = nc.get("hard_enforcement", False)
    reopen       = nc.get("negotiation_reopen_allowed", True)
    prereq_state = nc.get("prerequisite_state", nc.get("source", ""))
    scope        = nc.get("scope", "")

    lines: list[str] = []

    lines.append("## Negotiation Context")
    lines.append("")

    # Authority
    lines.append(f"| Field | Value |")
    lines.append(f"|-------|-------|")
    lines.append(f"| authority | `{authority}` |")
    lines.append(f"| contestable | `{str(contestable).lower()}` |")
    lines.append(f"| hard_enforcement | `{str(hard_enforce).lower()}` |")
    lines.append(f"| negotiation_reopen_allowed | `{str(reopen).lower()}` |")
    lines.append(f"| execution_allowed | `false` |")
    lines.append(f"| moves_money | `false` |")
    if scope:
        lines.append(f"| scope | `{scope}` |")
    lines.append("")

    # Authority explanation
    lines.append("**authority: none** — No coordinator issued this issue.")
    lines.append("It arose from independent claim convergence in the federation.")
    lines.append("No agent or institution has the power to enforce it.")
    lines.append("")

    # Contestability
    if contestable:
        lines.append("**Contestable:** Yes.")
        lines.append("")
        if condition:
            lines.append(
                f"If you believe `{condition}` does not apply in this context, "
                "you can contest by:"
            )
        else:
            lines.append("To contest this prerequisite:")
        lines.append("")
        lines.append("1. Produce a plan tree that addresses the underlying concern")
        lines.append("   via an alternative evidence path.")
        lines.append("2. Submit the plan tree as a PR referencing this issue.")
        lines.append("3. If accepted, the prerequisite will be weakened or scoped out.")
        lines.append("4. No coordinator is needed. Better evidence wins.")
        lines.append("")
    else:
        lines.append("**Contestable:** No — this prerequisite is not currently contestable.")
        lines.append("")

    # Prerequisite lifecycle
    state_key = ""
    if "weakened" in prereq_state:
        state_key = "weakened"
    elif "reaffirmed" in prereq_state:
        state_key = "reaffirmed"
    elif "promoted" in prereq_state:
        state_key = "promoted"
    elif "deprecated" in prereq_state:
        state_key = "deprecated"

    if state_key and state_key in PREREQUISITE_STATE_DESCRIPTIONS:
        lines.append(f"**Prerequisite lifecycle state: `{state_key}`**")
        lines.append("")
        lines.append(PREREQUISITE_STATE_DESCRIPTIONS[state_key])
        lines.append("")

    # Scope
    if scope and scope in SCOPE_DESCRIPTIONS:
        lines.append(f"**Scope: `{scope}`**")
        lines.append("")
        lines.append(SCOPE_DESCRIPTIONS[scope])
        lines.append("")

    # Reopenability
    if reopen:
        lines.append("**Negotiation is always reopenable.**")
        lines.append("")
        lines.append(
            "A PR merge is advisory — it records that evidence was accepted at a point in time. "
            "It does not permanently close negotiation. "
            "Any participant can reopen by submitting a better plan tree or contesting the scope."
        )
        lines.append("")

    # Federation convergence
    if convergence_count is not None and convergence_count >= 2:
        lines.append(
            f"**Federation convergence:** {convergence_count} independent claim(s) "
            "identified this condition as a necessary prerequisite."
        )
        lines.append(
            "Convergence strengthens the signal but does not make it mandatory."
        )
        lines.append("")

    return "\n".join(lines)


def render_dignity_guard(issue: dict[str, Any]) -> str:
    """
    Render a dignity guard section from an issue draft.
    """
    lines: list[str] = []
    lines.append("## Dignity Guard")
    lines.append("")
    lines.append("| Rule | Status |")
    lines.append("|------|--------|")
    lines.append("| no identity exposure | required |")
    lines.append("| revocable consent | required |")
    lines.append("| participant consent | required |")
    lines.append("| execution_allowed | `false` |")
    lines.append("| moves_money | `false` |")
    lines.append("| authority | `none` |")
    lines.append("")
    lines.append(
        "> No personal data about plan participants may be attached to evidence. "
        "Evidence must be about conditions, not people."
    )
    lines.append("")
    return "\n".join(lines)


def render_advisory_footer() -> str:
    """
    Render the standard advisory footer for every Dan-Go issue.
    """
    return "\n".join([
        "---",
        "",
        "> **Advisory only.** This issue was generated by Dan-Go / dango-gitsea-bridge.",
        "> No authority. No coordinator. Evidence only.",
        ">",
        "> A scoped issue is not a command. It is a negotiation invitation.",
        ">",
        "> `authority: none · advisory · execution_allowed: false · moves_money: false`",
        "",
    ])
