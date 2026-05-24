"""
prerequisite_markdown_renderer.py — Render prerequisite state as human-readable Markdown

Produces Markdown sections for each prerequisite lifecycle state:
  applicable  — condition must be satisfied; explain why and how
  bypassed    — condition suppressed; explain what bypass was found
  weakened    — condition applies in scope; note bypass path exists elsewhere
  reaffirmed  — condition strengthened by additional convergence
  deprecated  — condition lifecycle ended; note it is no longer active

No API. No network. stdlib only.

Human-readable negotiation is part of the protocol.

Usage:
    from prerequisite_markdown_renderer import (
        render_applicable_section,
        render_bypassed_section,
        render_prerequisite_state_section,
    )
"""

from __future__ import annotations

from typing import Any

# ── Bypass condition descriptions ─────────────────────────────────────────────

BYPASS_DESCRIPTIONS: dict[str, str] = {
    "precertified_structure": (
        "The space is a precertified structure — "
        "it meets safety requirements through an established certification pathway."
    ),
    "external_safety_audit_attached": (
        "An external safety audit has been attached — "
        "independent professional review has already confirmed safety compliance."
    ),
    "embedded_fire_controls": (
        "Embedded fire controls are present — "
        "the space includes fire suppression systems that satisfy safety requirements."
    ),
    "external_audit_trail": (
        "An external audit trail exists — "
        "safety compliance has been documented by an external authority."
    ),
    "local_structural_assessment": (
        "A local structural assessment is available — "
        "a qualified assessor has reviewed the structural integrity on-site."
    ),
}

# ── Applicable scope indicators ───────────────────────────────────────────────

SCOPE_INDICATOR_DESCRIPTIONS: dict[str, str] = {
    "local_safety_review":                "The plan requires a local safety review, "
                                          "indicating the space is not precertified.",
    "structural_modification_documented": "Structural modification has been documented, "
                                          "indicating a locally-modified existing structure.",
    "modified_existing_structure":        "The space is a modified existing structure "
                                          "without external safety audit.",
    "no_precertification":                "No precertification is present for this space.",
}


# ── Applicable section ────────────────────────────────────────────────────────

def render_applicable_section(
    condition: str,
    scope: str,
    scope_reasoning: list[str],
    prerequisite_state: str,
    claim_id: str = "",
) -> str:
    """
    Render the 'why this prerequisite applies' section for an applicable condition.
    """
    lines: list[str] = []

    lines.append("## Why This Prerequisite Applies")
    lines.append("")
    lines.append(
        f"`{condition}` is a federation prerequisite in state `{prerequisite_state}`."
    )
    lines.append(
        "It applies in this context because the plan tree signals indicate "
        f"a `{scope}` context."
    )
    lines.append("")

    if scope_reasoning:
        lines.append("### Scope Signals Detected")
        lines.append("")
        for reason in scope_reasoning:
            # Try to parse "key: indicator → scope" format
            if "→" in reason:
                parts = reason.split("→", 1)
                indicator_part = parts[0].strip()
                scope_part     = parts[1].strip()
                # Strip "scope_indicator_present: " prefix if present
                indicator = indicator_part.replace("scope_indicator_present:", "").strip()
                desc = SCOPE_INDICATOR_DESCRIPTIONS.get(
                    indicator,
                    f"Scope indicator `{indicator}` detected — maps to `{scope_part}`."
                )
                lines.append(f"- **`{indicator}`** → `{scope_part}`")
                lines.append(f"  {desc}")
            else:
                lines.append(f"- {reason}")
        lines.append("")

    lines.append("### What This Means")
    lines.append("")
    lines.append(
        f"The plan for `{claim_id}` must actively satisfy `{condition}`. "
        "No precertification or equivalent bypass path was detected for this claim."
    )
    lines.append("")
    lines.append("This is not a prohibition — it is a prerequisite signal.")
    lines.append("Satisfying it strengthens the plan's safety evidence trail.")
    lines.append("")

    return "\n".join(lines)


# ── Bypassed section ──────────────────────────────────────────────────────────

def render_bypassed_section(
    condition: str,
    bypass_conditions: list[str],
    claim_id: str = "",
) -> str:
    """
    Render the bypass explanation section for a suppressed (bypassed) condition.
    """
    lines: list[str] = []

    lines.append("## Bypass Explanation")
    lines.append("")
    lines.append(
        f"`{condition}` was detected as a federation prerequisite, "
        "but it does not apply to this claim."
    )
    lines.append("")
    lines.append(
        "An equivalent safety path was found in the plan tree. "
        "The prerequisite is bypassed — not deleted. "
        "It remains as an audit assertion in the OGI plan tree."
    )
    lines.append("")

    if bypass_conditions:
        lines.append("### Bypass Conditions Found")
        lines.append("")
        for bc in bypass_conditions:
            desc = BYPASS_DESCRIPTIONS.get(
                bc,
                f"`{bc}` — bypass condition present in plan."
            )
            lines.append(f"- **`{bc}`**")
            lines.append(f"  {desc}")
        lines.append("")

    lines.append("### Why No Issue Was Generated")
    lines.append("")
    lines.append(
        f"`{claim_id}` does not need to satisfy `{condition}` directly. "
        "The bypass path provides equivalent safety assurance."
    )
    lines.append("")
    lines.append(
        "> **A bypassed prerequisite is still memory. "
        "It is just not an active requirement in this context.**"
    )
    lines.append("")
    lines.append(
        "The bypass is recorded in the OGI plan tree as an audit assertion. "
        "It can be reviewed and contested. It does not disappear."
    )
    lines.append("")

    return "\n".join(lines)


# ── Lifecycle state section ───────────────────────────────────────────────────

def render_prerequisite_state_section(state: str, condition: str = "") -> str:
    """
    Render a short human-readable note about the prerequisite lifecycle state.
    """
    lines: list[str] = []

    if state == "promoted":
        lines.append("## Prerequisite Lifecycle: Promoted")
        lines.append("")
        lines.append(
            f"`{condition}` was promoted when 2 or more independent claims "
            "identified it as a necessary condition. "
            "It became a federation signal — advisory, not mandatory."
        )

    elif state == "reaffirmed":
        lines.append("## Prerequisite Lifecycle: Reaffirmed")
        lines.append("")
        lines.append(
            f"`{condition}` has been reaffirmed by additional claims. "
            "Its relevance is strengthening. "
            "It remains advisory and contestable."
        )

    elif state == "weakened":
        lines.append("## Prerequisite Lifecycle: Weakened")
        lines.append("")
        lines.append(
            f"`{condition}` has been weakened — a recognised bypass path exists "
            "for claims with precertification or equivalent safety evidence."
        )
        lines.append("")
        lines.append(
            "This claim does not qualify for the bypass. "
            "The condition is still applicable here."
        )
        lines.append("")
        lines.append(
            "Weakening is not deprecation. "
            "The prerequisite still applies in non-bypass contexts."
        )

    elif state == "deprecated":
        lines.append("## Prerequisite Lifecycle: Deprecated")
        lines.append("")
        lines.append(
            f"`{condition}` has been deprecated. "
            "Its lifecycle has ended. No new issue drafts are generated from it."
        )
        lines.append("")
        lines.append(
            "Existing plan trees that carried this prerequisite are unaffected — "
            "they retain the historical record."
        )

    else:
        lines.append(f"## Prerequisite Lifecycle: `{state}`")
        lines.append("")
        lines.append(f"Lifecycle state: `{state}`.")

    lines.append("")
    return "\n".join(lines)


# ── Resolution guide ──────────────────────────────────────────────────────────

def render_resolution_guide(condition: str, claim_id: str = "") -> str:
    """
    Render a how-to-resolve section for an applicable prerequisite.
    """
    lines: list[str] = []

    lines.append("## How to Resolve")
    lines.append("")
    lines.append(f"1. Collect evidence that `{condition}` is satisfied.")
    lines.append("   Examples: inspection certificate, structural assessment report,")
    lines.append("   fire safety certificate, authority sign-off.")
    lines.append("")
    lines.append("2. Open a PR in this repository attaching the evidence.")
    lines.append("   Reference this issue in the PR description.")
    lines.append("")
    lines.append("3. A peer agent or human reviewer will evaluate the evidence.")
    lines.append("   The review is advisory — the reviewer does not have authority")
    lines.append("   to enforce the condition, only to accept or request more evidence.")
    lines.append("")
    lines.append("4. On merge, append a `plan_correction` event to update the plan tree.")
    lines.append("")
    lines.append("   > **A merged PR is advisory — it does not auto-satisfy the condition.**")
    lines.append("   > The plan tree is updated by a `plan_correction` event, not by merge.")
    lines.append("")
    lines.append("5. If you believe this prerequisite should not apply here,")
    lines.append("   contest it by producing a better plan tree (see Negotiation Context).")
    lines.append("")

    return "\n".join(lines)
