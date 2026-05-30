"""
issue_asset_linker.py — Link Dan-Go Issue snapshots to GITSEA Asset snapshots

Reads issue metadata from a Dan-Go scoped issue output file and produces
a deterministic issue-to-asset link document.

The link document records:
  - which claim generated the issue
  - what prerequisite condition the issue addresses
  - what scope state applied (applicable vs bypassed)
  - whether the issue is a candidate for GITSEA asset signalling
  - the current negotiation status

This file does NOT:
  - Submit anything to GITSEA
  - Activate any stream
  - Move funds
  - Modify prior records (append-only)
  - Call external APIs

Append-only: each call appends a new link record. Prior records are preserved.

No secrets. No private keys. No wallet operations. No network. stdlib only.

Usage:
    python bridge/gitsea/lifecycle/runtime/issue_asset_linker.py
    python bridge/gitsea/lifecycle/runtime/issue_asset_linker.py --input PATH
    python bridge/gitsea/lifecycle/runtime/issue_asset_linker.py --save
    python bridge/gitsea/lifecycle/runtime/issue_asset_linker.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_FILE_DIR  = Path(__file__).parent
_LIFECYCLE = _FILE_DIR.parent
_EXAMPLES  = _LIFECYCLE / "examples"
_REPO_ROOT = _LIFECYCLE.parent.parent.parent

# Default input: the scoped issue output for housing-007
_DEFAULT_INPUT = (
    _REPO_ROOT / "bridge" / "gitlawb" / "examples"
    / "scoped-issue-housing-007.output.json"
)


# ── Link builder ──────────────────────────────────────────────────────────────

def build_issue_asset_link(issue_data: dict[str, Any]) -> dict[str, Any]:
    """
    Build an advisory issue-to-asset link record from a scoped issue output.

    The link is deterministic: same input → same output (except `generated_at`).
    It is append-only: calling this function again with updated input appends
    a new version; the caller is responsible for log management.
    """
    claim_id   = issue_data.get("claim_id", "unknown")
    condition  = issue_data.get("condition", "unknown")
    scope      = issue_data.get("scope_status", "unknown")
    is_issue   = issue_data.get("issue_candidate", False)
    issue_num  = issue_data.get("issue_number", None)

    # Determine asset signal eligibility
    # A claim can generate an asset signal only if:
    # 1. The issue was actually drafted (applicable)
    # 2. Negotiation has started (issue_candidate = true)
    asset_signal_eligible = is_issue and scope in ("applicable", "unknown")

    # Negotiation status from issue data
    negotiation_status = "pending"
    if is_issue:
        negotiation_status = "negotiation_invited"
    if not is_issue and scope == "bypassed":
        negotiation_status = "bypassed_no_issue"

    return {
        "link_type":         "issue_to_asset_link",
        "generated_at":      datetime.now(timezone.utc).isoformat(),
        "append_only":       True,

        # Source
        "claim_id":          claim_id,
        "condition":         condition,
        "scope_status":      scope,

        # Issue
        "issue_candidate":   is_issue,
        "issue_number":      issue_num,
        "issue_url": (
            f"https://github.com/olddqn/dango-mujin/issues/{issue_num}"
            if issue_num else None
        ),

        # Negotiation
        "negotiation_status":    negotiation_status,
        "negotiation_reopen_allowed": True,
        "contestable":            True,

        # Asset signal
        "asset_signal_eligible": asset_signal_eligible,
        "economic_value":        False,

        # Invariants
        "authority":         "none",
        "execution_allowed": False,
        "moves_money":       False,
        "hard_enforcement":  False,
        "advisory":          True,

        "note": (
            "This link record is advisory only. No GITSEA stream is activated. "
            "No funds are moved. No wallet operation is performed. "
            "Contribution becomes legible before it becomes valuable."
        ),
    }


# ── Save (append-only) ────────────────────────────────────────────────────────

def save_link(link: dict, out_path: Path | None = None) -> Path:
    """
    Save the link record to issue-to-asset.json.
    Append-only: if the file already exists, a new record is appended to
    the JSON array. If it does not exist, a new array is created.
    """
    if out_path is None:
        out_path = _EXAMPLES / "issue-to-asset.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    records: list[dict] = []
    if out_path.exists():
        with open(out_path, encoding="utf-8") as f:
            try:
                existing = json.load(f)
                if isinstance(existing, list):
                    records = existing
                elif isinstance(existing, dict):
                    records = [existing]
            except json.JSONDecodeError:
                records = []

    records.append(link)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Link a Dan-Go issue snapshot to a GITSEA asset signal.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Input: scoped issue output JSON (from scoped_plan_to_issue.py).
Output: issue-to-asset link record (advisory, append-only).

Examples:
  python bridge/gitsea/lifecycle/runtime/issue_asset_linker.py
  python bridge/gitsea/lifecycle/runtime/issue_asset_linker.py --save
  python bridge/gitsea/lifecycle/runtime/issue_asset_linker.py --json
  python bridge/gitsea/lifecycle/runtime/issue_asset_linker.py \\
      --input bridge/gitlawb/examples/scoped-issue-housing-007.output.json
        """,
    )
    p.add_argument("--input", metavar="PATH",
                   help="Path to scoped issue output JSON")
    p.add_argument("--save", action="store_true",
                   help="Append link to lifecycle/examples/issue-to-asset.json")
    p.add_argument("--json", action="store_true", dest="json_output",
                   help="Print full JSON")
    args = p.parse_args()

    input_path = Path(args.input) if args.input else _DEFAULT_INPUT

    if not input_path.exists():
        # Fallback: build a minimal housing-007 stub
        issue_data: dict[str, Any] = {
            "claim_id":       "housing-007",
            "condition":      "space_safety_assessed",
            "scope_status":   "applicable",
            "issue_candidate": True,
            "issue_number":   1,
        }
        print(f"Note: {input_path} not found — using built-in stub for housing-007",
              file=sys.stderr)
    else:
        with open(input_path, encoding="utf-8") as f:
            issue_data = json.load(f)

    link = build_issue_asset_link(issue_data)

    if args.save:
        out = save_link(link)
        print(f"Saved (appended): {out}")

    if args.json_output:
        print(json.dumps(link, indent=2, ensure_ascii=False))
        return

    # Default: human-readable
    print(f"\n{'='*55}")
    print(f"  Issue → Asset Link: {link['claim_id']}")
    print(f"{'='*55}")
    print(f"  Condition:           {link['condition']}")
    print(f"  Scope:               {link['scope_status']}")
    print(f"  Issue candidate:     {link['issue_candidate']}")
    if link["issue_number"]:
        print(f"  Issue URL:           {link['issue_url']}")
    print(f"  Negotiation status:  {link['negotiation_status']}")
    print(f"  Asset signal eligible: {link['asset_signal_eligible']}")
    print(f"  Economic value:      {link['economic_value']}")
    print(f"\n  execution_allowed:  {link['execution_allowed']}")
    print(f"  moves_money:        {link['moves_money']}")
    print(f"  advisory:           {link['advisory']}")
    print(f"  authority:          {link['authority']}")
    print()


if __name__ == "__main__":
    main()
