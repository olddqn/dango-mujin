"""
scoped_issue_markdown.py — CLI: scoped issue JSON → GitHub Markdown

Reads a scoped issue draft (output of scoped_plan_to_issue.py or
scoped_issue_filter.py) and prints GitHub-compatible Markdown to stdout.

Usage:
    python gitlawb/runtime/scoped_issue_markdown.py <issue.json>
    python gitlawb/runtime/scoped_issue_markdown.py <issue.json> --pr-feedback <pr.json>
    python gitlawb/runtime/scoped_issue_markdown.py <issue.json> --json

Redirect output to a file:
    python gitlawb/runtime/scoped_issue_markdown.py \
      gitlawb/examples/scoped-issue-housing-007.output.json \
      > gitlawb/examples/github-issue-housing-007.md

No API. No network. stdlib only.
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

from issue_markdown_renderer import render_markdown


# ── PR feedback markdown ──────────────────────────────────────────────────────

_PR_EVENT_SUMMARY: dict[str, str] = {
    "pr_opened":   "Evidence submitted. Awaiting review.",
    "pr_reviewed": "Evidence reviewed. Awaiting merge.",
    "pr_merged":   (
        "PR merged. Condition evidence accepted. "
        "Negotiation remains reopenable. "
        "Append a `plan_correction` event to formally update the plan tree."
    ),
    "pr_rejected": (
        "PR rejected. Evidence not accepted. "
        "Condition remains open. A new PR or alternative path is needed."
    ),
}


def render_pr_feedback_markdown(pr_feedback: list[dict[str, Any]]) -> str:
    """
    Render a list of scoped PR feedback events as a Markdown summary section.
    """
    lines: list[str] = []
    lines.append("## PR Feedback History")
    lines.append("")
    lines.append("| Event | Feedback Type | Scope | GITSEA Eligible |")
    lines.append("|-------|---------------|-------|-----------------|")

    for fb in pr_feedback:
        event   = fb.get("pr_event", "?")
        pr_id   = fb.get("pr_id", "?")
        rf      = fb.get("reality_feedback", {})
        sc      = fb.get("stream_candidate", {})
        ftype   = rf.get("feedback_type", "?")
        scope   = rf.get("scope_status", "?")
        gitsea  = sc.get("gitsea_eligible", False)
        lines.append(
            f"| `{event}` | `{ftype}` | `{scope}` | "
            f"{'✓' if gitsea else '—'} |"
        )

    lines.append("")

    for fb in pr_feedback:
        event = fb.get("pr_event", "?")
        rf    = fb.get("reality_feedback", {})
        sc    = fb.get("stream_candidate", {})
        summary = _PR_EVENT_SUMMARY.get(event, rf.get("note", ""))
        lines.append(f"### `{event}`")
        lines.append("")
        lines.append(f"> {summary}")
        lines.append("")
        lines.append(f"- negotiation_reopen_allowed: `{rf.get('negotiation_reopen_allowed', True)}`")
        lines.append(f"- hard_enforcement: `{rf.get('hard_enforcement', False)}`")
        lines.append(f"- contestable: `{rf.get('contestable', True)}`")
        lines.append(f"- moves_money: `{rf.get('moves_money', False)}`")
        if sc.get("gitsea_eligible"):
            lines.append("")
            lines.append(f"**GITSEA-eligible.** No stream activates now.")
            lines.append(f"Credit signal: `{sc.get('credit_signal','?')}`.")
        lines.append("")

    lines.append(
        "> **PR merge is not truth.** "
        "A `plan_correction` event by the plan author is needed to "
        "formally update the plan tree."
    )
    lines.append("")

    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Render a scoped issue draft as GitHub-compatible Markdown.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gitlawb/runtime/scoped_issue_markdown.py \\
    gitlawb/examples/scoped-issue-housing-007.output.json

  python gitlawb/runtime/scoped_issue_markdown.py \\
    gitlawb/examples/scoped-issue-housing-007.output.json \\
    --pr-feedback gitlawb/examples/scoped-pr-feedback.output.json

  python gitlawb/runtime/scoped_issue_markdown.py \\
    gitlawb/examples/scoped-issue-housing-007.output.json \\
    > gitlawb/examples/github-issue-housing-007.md
        """,
    )
    p.add_argument("issue_file", metavar="ISSUE_FILE",
                   help="Scoped issue JSON (output of scoped_plan_to_issue.py)")
    p.add_argument("--pr-feedback", metavar="PR_FILE",
                   help="Optional: scoped PR feedback JSON to append")
    p.add_argument("--json", action="store_true", dest="json_output",
                   help="Output JSON envelope {markdown, metadata} instead of raw Markdown")
    args = p.parse_args()

    if not os.path.exists(args.issue_file):
        print(f"ERROR: file not found: {args.issue_file}", file=sys.stderr)
        sys.exit(1)

    with open(args.issue_file) as f:
        data = json.load(f)

    issues = data if isinstance(data, list) else [data]

    pr_feedback: list[dict[str, Any]] = []
    if args.pr_feedback:
        if not os.path.exists(args.pr_feedback):
            print(f"ERROR: file not found: {args.pr_feedback}", file=sys.stderr)
            sys.exit(1)
        with open(args.pr_feedback) as f:
            pr_feedback = json.load(f)
        if isinstance(pr_feedback, dict):
            pr_feedback = [pr_feedback]

    rendered_parts: list[str] = []
    for issue in issues:
        md = render_markdown(issue)
        if pr_feedback and issue.get("issue_candidate", False):
            md = md + "\n" + render_pr_feedback_markdown(pr_feedback)
        rendered_parts.append(md)

    final_md = "\n\n---\n\n".join(rendered_parts)

    if args.json_output:
        issue = issues[0]
        envelope = {
            "markdown": final_md,
            "markdown_renderable": True,
            "claim_id":    issue.get("claim_id", "?"),
            "condition":   issue.get("condition", "?"),
            "scope_status": issue.get("scope_status", "?"),
            "issue_candidate": issue.get("issue_candidate", False),
            "execution_allowed": False,
            "moves_money": False,
            "advisory": True,
        }
        print(json.dumps(envelope, indent=2))
    else:
        print(final_md)


if __name__ == "__main__":
    main()
