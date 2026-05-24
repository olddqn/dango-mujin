"""
issue_markdown_renderer.py — Issue JSON → GitHub-compatible Markdown

Reads a scoped issue draft (output of scoped_plan_to_issue.py) and produces
a human-readable Markdown document suitable for GitHub issues, Gitlawb issues,
or any Markdown renderer.

Key design:
  - applicable prerequisites → full issue body with federation context
  - bypassed prerequisites   → suppression explanation document
  - all output is advisory, contestable, execution-disabled
  - sections separated by horizontal rules (---)
  - no HTML dependency — pure Markdown only
  - deterministic output for the same input
  - peer comparison in federation context (scans gitlawb/examples/)
  - human-readable auditability is part of the protocol

No API. No network. No external libraries. stdlib only.

Human-readable negotiation is part of the protocol.

Usage:
    from issue_markdown_renderer import render_markdown
    md = render_markdown(issue_dict)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_FILE_DIR   = Path(__file__).parent
_BRIDGE_DIR = _FILE_DIR.parent.parent
_EX_DIR     = _FILE_DIR.parent / "examples"

sys.path.insert(0, str(_FILE_DIR))

# ── Repository config ─────────────────────────────────────────────────────────

REPO_CONFIG: dict[str, str] = {
    "github":  "https://github.com/olddqn/dango-mujin",
    "gitlawb": (
        "https://gitlawb.com"
        "/z6MkpWP3c2xE5Veu5xSJxviWUrM69SDX4offMifsVXAs31Ts"
        "/dango-mujin"
    ),
}

# ── Capability map ────────────────────────────────────────────────────────────

CONDITION_CAPABILITIES: dict[str, list[str]] = {
    "space_safety_assessed": [
        "evidence_checking",
        "structural_review",
        "local_space_assessment",
    ],
    "food_safety_reviewed": [
        "evidence_checking",
        "safety_review",
        "food_handling_assessment",
    ],
    "structural_assessment": [
        "evidence_checking",
        "structural_review",
    ],
    "local_structural_assessment": [
        "evidence_checking",
        "structural_review",
        "local_space_assessment",
    ],
    "risk_assessment": [
        "evidence_checking",
        "risk_review",
    ],
    "legal_ownership_confirmed": [
        "evidence_checking",
        "legal_review",
    ],
    "participant_consent": [
        "consent_facilitation",
        "dignity_review",
    ],
}

_DEFAULT_CAPABILITIES = ["evidence_checking"]

# ── Scope signal extraction ───────────────────────────────────────────────────

_SCOPE_SIGNAL_MAP: dict[str, str] = {
    "local_safety_review":                "local_safety_review",
    "structural_modification_documented": "modified_existing_structure",
    "modified_existing_structure":        "modified_existing_structure",
    "no_precertification":                "non_precertified_space_conditions",
}


def _extract_scope_signals(body: str, scope: str) -> list[str]:
    """
    Extract human-readable scope signal keywords from the issue body text.
    Returns a list of bullet labels (no leading dash).
    """
    signals: list[str] = []
    seen: set[str] = set()

    for line in body.splitlines():
        if "scope_indicator_present:" not in line:
            continue
        # "scope_indicator_present: local_safety_review → non_precertified_spaces"
        after_colon = line.split("scope_indicator_present:", 1)[-1].strip()
        indicator   = after_colon.split("→")[0].strip()
        label       = _SCOPE_SIGNAL_MAP.get(indicator, indicator)
        if label not in seen:
            signals.append(label)
            seen.add(label)

    # Always include the scope value as a signal if not already present
    if scope:
        scope_label = scope.replace("_", " ")
        scope_key   = scope + "_conditions"
        if scope_key not in seen and scope not in seen:
            # Use short form e.g. "non_precertified_space_conditions"
            short = scope.rstrip("s") + "_conditions"
            if short not in seen:
                signals.append(short)
                seen.add(short)

    return signals


def _extract_convergence_count(body: str) -> int | None:
    for line in body.splitlines():
        if "independently by" in line and "claim(s)" in line:
            for tok in line.split():
                if tok.isdigit():
                    return int(tok)
    return None


# ── Peer comparison (other claims, same condition) ────────────────────────────

def _find_peer_bypassed(
    condition: str,
    this_claim_id: str,
) -> dict[str, Any] | None:
    """
    Scan gitlawb/examples/ for a bypassed peer with the same condition.
    Returns the first found dict, or None.
    """
    for path in sorted(_EX_DIR.glob("scoped-issue-*.output.json")):
        try:
            with open(path) as f:
                data = json.load(f)
            peers = data if isinstance(data, list) else [data]
            for peer in peers:
                if (
                    peer.get("condition") == condition
                    and peer.get("claim_id") != this_claim_id
                    and peer.get("scope_status") == "bypassed"
                    and peer.get("bypass_conditions")
                ):
                    return peer
        except Exception:
            continue
    return None


# ── Section helpers ───────────────────────────────────────────────────────────

def _sec(heading: str, body_lines: list[str]) -> list[str]:
    """Build a titled section with a trailing --- separator."""
    out = [f"## {heading}", ""]
    out.extend(body_lines)
    if not out[-1]:
        pass
    else:
        out.append("")
    out.append("---")
    out.append("")
    return out


# ── Applicable issue renderer ─────────────────────────────────────────────────

def render_issue_markdown(issue: dict[str, Any]) -> str:  # noqa: C901
    """
    Render an applicable scoped issue draft as GitHub-compatible Markdown.

    Format:
      # Title
      ## Claim ---
      ## Condition ---
      ## Scope Status ---
      ## Why this issue exists ---
      ## Federation Context ---
      ## Negotiation Context ---
      ## Suggested Agent Task ---
      ## Dignity Guard ---
      ## Important ---
      ## Structural Note ---
      ## Repository
    """
    claim_id     = issue.get("claim_id", "unknown")
    condition    = issue.get("condition", "unknown")
    scope_status = issue.get("scope_status", "applicable")
    scope        = issue.get("scope", "")
    prereq_state = issue.get("prerequisite_state", "unknown")
    nc           = issue.get("negotiation_context", {})
    hint         = issue.get("agent_task_hint", {})
    body_text    = issue.get("body", "")

    task_type    = hint.get("task_type", "evidence_review") if hint else "evidence_review"
    capabilities = CONDITION_CAPABILITIES.get(condition, _DEFAULT_CAPABILITIES)
    conv_count   = _extract_convergence_count(body_text)
    scope_signals = _extract_scope_signals(body_text, scope)
    peer_bypassed = _find_peer_bypassed(condition, claim_id)

    title = issue.get("title", f"[Scoped Prerequisite] {condition} required — {claim_id}")

    lines: list[str] = []

    # ── Title ──
    lines.append(f"# {title}")
    lines.append("")

    # ── Claim ──
    lines += _sec("Claim", [claim_id, ""])

    # ── Condition ──
    lines += _sec("Condition", [condition, ""])

    # ── Scope Status ──
    lines += _sec("Scope Status", [scope_status, ""])

    # ── Why this issue exists ──
    why_lines: list[str] = [
        "This prerequisite was identified through federation prerequisite convergence.",
        "",
        "It is not universally enforced.",
        "",
        "It applies in this context because the current plan includes:",
        "",
    ]
    for sig in scope_signals:
        why_lines.append(f"- {sig}")
    if not scope_signals:
        why_lines.append(f"- {scope or 'scoped context signals'}")
    why_lines.append("")
    why_lines.append(
        "The scoped prerequisite layer determined that this claim "
        "does not satisfy the bypass path conditions."
    )
    why_lines.append("")
    lines += _sec("Why this issue exists", why_lines)

    # ── Federation Context ──
    fed_lines: list[str] = [
        "This condition emerged independently across multiple negotiation histories.",
        "",
        "No coordinator declared it.",
        "",
        "The prerequisite surfaced because multiple contested plan trees "
        "converged on the same structural requirement.",
        "",
        "Current lifecycle state:",
        "",
        f"- status: {prereq_state}",
        "- authority: none",
        "- contestable: true",
        "- negotiation_reopen_allowed: true",
        "",
    ]

    if prereq_state == "weakened":
        fed_lines += [
            "The weakened status means:",
            "",
            "This prerequisite may not apply universally.",
            "Equivalent safety paths may bypass it in some contexts.",
            "",
        ]

    if peer_bypassed:
        peer_id  = peer_bypassed.get("claim_id", "another claim")
        peer_byp = peer_bypassed.get("bypass_conditions", [])
        fed_lines.append(f"Example:")
        fed_lines.append("")
        fed_lines.append(
            f"{peer_id} bypasses this prerequisite because it includes:"
        )
        fed_lines.append("")
        for bc in peer_byp:
            fed_lines.append(f"- {bc}")
        fed_lines.append("")
        fed_lines.append(
            f"{claim_id} does not include those bypass conditions."
        )
        fed_lines.append("")
        fed_lines.append("Therefore the prerequisite remains applicable here.")
        fed_lines.append("")

    elif conv_count is not None and conv_count >= 2:
        fed_lines += [
            f"{conv_count} independent claims discovered this condition as a necessary prerequisite.",
            "Convergence strengthens the signal — it does not make it mandatory.",
            "",
        ]

    lines += _sec("Federation Context", fed_lines)

    # ── Negotiation Context ──
    contestable  = nc.get("contestable", True)
    hard_enforce = nc.get("hard_enforcement", False)
    reopen       = nc.get("negotiation_reopen_allowed", True)

    nc_lines: list[str] = [
        "| Field | Value |",
        "|---|---|",
        "| authority | none |",
        f"| contestable | {str(contestable).lower()} |",
        f"| hard_enforcement | {str(hard_enforce).lower()} |",
        "| advisory | true |",
        "| execution_allowed | false |",
        "| moves_money | false |",
        f"| negotiation_reopen_allowed | {str(reopen).lower()} |",
        "",
    ]
    lines += _sec("Negotiation Context", nc_lines)

    # ── Suggested Agent Task ──
    task_lines: list[str] = [
        "Suggested task type:",
        "",
        f"`{task_type}`",
        "",
        "Suggested capabilities:",
        "",
    ]
    for cap in capabilities:
        task_lines.append(f"- {cap}")
    task_lines += [
        "",
        "This task is advisory only.",
        "",
        "No automatic execution is permitted.",
        "",
    ]
    lines += _sec("Suggested Agent Task", task_lines)

    # ── Dignity Guard ──
    dig_lines: list[str] = [
        "Required:",
        "",
        "- revocable_consent",
        "- participant_consent",
        "- no_identity_exposure",
        "",
        "Current status:",
        "",
        "- no_identity_exposure: pass",
        "- execution_allowed: false",
        "",
    ]
    lines += _sec("Dignity Guard", dig_lines)

    # ── Important ──
    imp_lines: list[str] = [
        "This issue is not a command.",
        "",
        "It is a negotiation invitation.",
        "",
        "PR merge does not establish truth.",
        "",
        "Negotiation may reopen if:",
        "",
        "- new evidence appears",
        "- a counterplan emerges",
        "- equivalent safety paths are demonstrated",
        "- federation prerequisites are contested or deprecated",
        "",
    ]
    lines += _sec("Important", imp_lines)

    # ── Structural Note ──
    struct_lines: list[str] = [
        "Human-readable negotiation is part of the protocol.",
        "",
        "This issue was generated from:",
        "",
        "Claim",
        "→ Scoped Plan Tree",
        "→ Federation Prerequisite Resolution",
        "→ Scoped Issue Draft",
        "→ Markdown Rendering",
        "",
        "No hidden scoring.",
        "No central authority.",
        "No hard enforcement.",
        "",
    ]
    lines += _sec("Structural Note", struct_lines)

    # ── Repository ──
    repo_lines: list[str] = [
        "GitHub:",
        REPO_CONFIG["github"],
        "",
        "gitlawb:",
        REPO_CONFIG["gitlawb"],
        "",
    ]
    # Last section — no trailing separator
    lines.append("## Repository")
    lines.append("")
    lines.extend(repo_lines)

    return "\n".join(lines)


# ── Suppression renderer ──────────────────────────────────────────────────────

def render_suppressed_markdown(issue: dict[str, Any]) -> str:
    """
    Render a suppressed (bypassed) scoped issue as a bypass explanation document.

    Even when no issue is created, the bypass is rendered transparently:
    auditors can verify it, participants can contest it.
    Bypass transparency is part of the protocol.
    """
    claim_id         = issue.get("claim_id", "unknown")
    condition        = issue.get("condition", "unknown")
    scope_status     = issue.get("scope_status", "bypassed")
    reason           = issue.get("reason", "suppressed")
    bypass_conditions = issue.get("bypass_conditions", [])
    filter_reason    = issue.get("filter_reason", "")

    lines: list[str] = []

    # ── Title ──
    lines.append(f"# [Scoped Prerequisite] {condition} bypassed — {claim_id}")
    lines.append("")

    # ── Status ──
    status_body: list[str] = [
        "Issue suppressed.",
        "",
        f"- scope_status: `{scope_status}`",
        "- issue_candidate: `false`",
        f"- reason: {reason}",
    ]
    if filter_reason:
        status_body.append(f"- filter_reason: {filter_reason}")
    status_body.append("")
    lines += _sec("Status", status_body)

    # ── Reason ──
    reason_body: list[str] = [
        "Equivalent safety path detected:",
        "",
    ]
    for bc in bypass_conditions:
        reason_body.append(f"- {bc}")
    reason_body += ["", "No issue draft generated.", ""]
    lines += _sec("Reason", reason_body)

    # ── What this means ──
    what_lines: list[str] = [
        f"`{condition}` was recognised as a federation prerequisite, "
        "but it does not apply to this claim.",
        "",
        "An equivalent safety path exists in the plan tree. "
        "The prerequisite is bypassed — not deleted. "
        "It remains recorded as an audit assertion in the OGI plan tree.",
        "",
        "> **A bypassed prerequisite is still memory. "
        "It is just not an active requirement in this context.**",
        "",
    ]
    lines += _sec("What This Means", what_lines)

    # ── Contestability ──
    contest_lines: list[str] = [
        "This suppression is contestable.",
        "",
        "If you believe the bypass should not apply:",
        "",
        f"1. Submit a plan tree that removes the bypass conditions "
        f"and demonstrates that `{condition}` is still required.",
        "2. Reference this suppression record in the PR description.",
        "3. If the PR is accepted, a new issue draft will be generated "
        "for the corrected plan tree.",
        "",
        "No coordinator is needed. Better evidence wins.",
        "",
    ]
    lines += _sec("Contestability", contest_lines)

    # ── Structural Note ──
    struct_lines: list[str] = [
        "Human-readable negotiation is part of the protocol.",
        "",
        "This suppression record was generated from:",
        "",
        "Claim",
        "→ Scoped Plan Tree",
        "→ Federation Prerequisite Resolution",
        "→ Bypass Detection",
        "→ Suppression Record",
        "→ Markdown Rendering",
        "",
        "No hidden scoring.",
        "No central authority.",
        "No hard enforcement.",
        "",
    ]
    lines += _sec("Structural Note", struct_lines)

    # ── Repository ──
    lines.append("## Repository")
    lines.append("")
    lines.append("GitHub:")
    lines.append(REPO_CONFIG["github"])
    lines.append("")
    lines.append("gitlawb:")
    lines.append(REPO_CONFIG["gitlawb"])
    lines.append("")

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
