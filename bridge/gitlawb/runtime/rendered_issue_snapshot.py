"""
rendered_issue_snapshot.py — Render all scoped issues as Markdown snapshot

Scans all scoped plan trees in ogi/examples/,
generates issue drafts, and produces a Markdown rendering summary:

  housing-006 / space_safety_assessed → suppressed (bypass explanation rendered)
  housing-007 / space_safety_assessed → open_draft (full issue markdown rendered)

Can also write rendered Markdown files to gitlawb/examples/.

No API. No network. stdlib only.

Human-readable negotiation is part of the protocol.

Usage:
  python gitlawb/runtime/rendered_issue_snapshot.py
  python gitlawb/runtime/rendered_issue_snapshot.py --json
  python gitlawb/runtime/rendered_issue_snapshot.py --write-files
  python gitlawb/runtime/rendered_issue_snapshot.py --claim-id housing-007
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_FILE_DIR    = Path(__file__).parent
_BRIDGE_DIR  = _FILE_DIR.parent.parent
_RUNTIME_DIR = _BRIDGE_DIR / "runtime"
_OGI_EX      = _BRIDGE_DIR / "ogi" / "examples"
_GITLAWB_EX  = _BRIDGE_DIR / "gitlawb" / "examples"

sys.path.insert(0, str(_RUNTIME_DIR))
sys.path.insert(0, str(_FILE_DIR))


# ── Load helpers ──────────────────────────────────────────────────────────────

def _load_plan_trees() -> list[dict[str, Any]]:
    trees = []
    for path in sorted(_OGI_EX.glob("scoped-plan-*.output.json")):
        try:
            with open(path) as f:
                trees.append(json.load(f))
        except Exception as e:
            print(f"  WARNING: {path.name}: {e}", file=sys.stderr)
    return trees


def _load_scoped_issues() -> list[dict[str, Any]]:
    """Load all pre-generated scoped issue JSONs from gitlawb/examples/."""
    issues = []
    for path in sorted(_GITLAWB_EX.glob("scoped-issue-*.output.json")):
        try:
            with open(path) as f:
                data = json.load(f)
                if isinstance(data, list):
                    issues.extend(data)
                else:
                    issues.append(data)
        except Exception as e:
            print(f"  WARNING: {path.name}: {e}", file=sys.stderr)
    return issues


# ── Core snapshot builder ─────────────────────────────────────────────────────

def build_rendered_snapshot(
    claim_id_filter: str | None = None,
    write_files: bool = False,
) -> list[dict[str, Any]]:
    """
    Build a rendering snapshot: for each scoped issue, generate Markdown
    and return a summary record.

    If write_files=True, write rendered Markdown to gitlawb/examples/.
    """
    from issue_markdown_renderer import render_markdown

    issues = _load_scoped_issues()
    if not issues:
        # Fall back: generate from plan trees
        try:
            from scoped_plan_to_issue import issues_from_scoped_tree
            from scoped_issue_filter  import _apply_filters
            trees = _load_plan_trees()
            raw: list[dict[str, Any]] = []
            for tree in trees:
                raw.extend(issues_from_scoped_tree(tree))
            issues = _apply_filters(raw)
        except ImportError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return []

    records: list[dict[str, Any]] = []

    for issue in issues:
        cid       = issue.get("claim_id", "?")
        condition = issue.get("condition", "?")

        if claim_id_filter and cid != claim_id_filter:
            continue

        is_candidate = issue.get("issue_candidate", False)
        status       = "open_draft" if is_candidate else "suppressed"

        # Render Markdown
        md = render_markdown(issue)

        # Optionally write to file
        output_path: str | None = None
        if write_files:
            fname = f"github-issue-{cid}.md"
            out   = _GITLAWB_EX / fname
            out.write_text(md, encoding="utf-8")
            output_path = str(out.relative_to(_BRIDGE_DIR))

        record: dict[str, Any] = {
            "claim_id":       cid,
            "condition":      condition,
            "issue_status":   status,
            "issue_candidate": is_candidate,
            "scope_status":   issue.get("scope_status", "?"),
            "markdown_renderable": True,
            "markdown_length": len(md),
            "execution_allowed": False,
            "moves_money":    False,
            "advisory":       True,
        }
        if output_path:
            record["written_to"] = output_path
        if not is_candidate:
            record["suppression_reason"] = issue.get("reason", issue.get("filter_reason", "?"))
            record["bypass_conditions"]  = issue.get("bypass_conditions", [])

        records.append(record)

    return records


# ── CLI display ───────────────────────────────────────────────────────────────

def _print_snapshot(records: list[dict[str, Any]]) -> None:
    open_drafts = [r for r in records if r["issue_status"] == "open_draft"]
    suppressed  = [r for r in records if r["issue_status"] == "suppressed"]

    print(f"\n{'='*60}")
    print(f"  Rendered Issue Snapshot")
    print(f"  Total: {len(records)}  "
          f"Rendered: {len(open_drafts)}  "
          f"Suppressed: {len(suppressed)}")
    print(f"{'='*60}\n")

    if open_drafts:
        print("  Open Issue Drafts (rendered as Markdown):")
        for r in open_drafts:
            print(f"\n  ✓  [{r['claim_id']}] {r['condition']}")
            print(f"       issue_status:       open_draft")
            print(f"       scope_status:       {r.get('scope_status')}")
            print(f"       markdown_renderable: {r.get('markdown_renderable')}")
            print(f"       markdown_length:    {r.get('markdown_length')} chars")
            print(f"       execution_allowed:  {r.get('execution_allowed')}")
            print(f"       moves_money:        {r.get('moves_money')}")
            if r.get("written_to"):
                print(f"       written_to:         {r['written_to']}")

    if suppressed:
        print("\n  Suppressed (bypass explanation rendered):")
        for r in suppressed:
            byp = r.get("bypass_conditions", [])
            print(f"\n  ⊗  [{r['claim_id']}] {r['condition']}")
            print(f"       issue_status:       suppressed")
            print(f"       suppression_reason: {r.get('suppression_reason')}")
            print(f"       bypass_conditions:  {byp}")
            print(f"       markdown_renderable: {r.get('markdown_renderable')}")
            print(f"       markdown_length:    {r.get('markdown_length')} chars")
            if r.get("written_to"):
                print(f"       written_to:         {r['written_to']}")

    print(f"\n  Invariants:")
    print(f"    execution_allowed:   False (all)")
    print(f"    moves_money:         False (all)")
    print(f"    advisory:            True  (all)")
    print(f"    markdown_renderable: True  (all)")
    print()


def main() -> None:
    p = argparse.ArgumentParser(
        description="Render all scoped issues as Markdown — snapshot view.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gitlawb/runtime/rendered_issue_snapshot.py
  python gitlawb/runtime/rendered_issue_snapshot.py --json
  python gitlawb/runtime/rendered_issue_snapshot.py --write-files
  python gitlawb/runtime/rendered_issue_snapshot.py --claim-id housing-007
        """,
    )
    p.add_argument("--json",        action="store_true", dest="json_output")
    p.add_argument("--write-files", action="store_true",
                   help="Write rendered Markdown to gitlawb/examples/")
    p.add_argument("--claim-id",    metavar="CLAIM_ID")
    args = p.parse_args()

    records = build_rendered_snapshot(
        claim_id_filter=args.claim_id,
        write_files=args.write_files,
    )

    if not records:
        print("No scoped issues found.", file=sys.stderr)
        sys.exit(0)

    if args.json_output:
        print(json.dumps(records, indent=2))
        return

    _print_snapshot(records)


if __name__ == "__main__":
    main()
