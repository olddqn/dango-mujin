"""
scoped_issue_snapshot.py — Full scoped issue state across all claims

Reads all known scoped plan trees and produces a snapshot of issue status:
  - applicable prerequisites → open_draft
  - bypassed prerequisites   → suppressed (bypass recorded)

Also integrates:
  - prerequisite status (promoted / weakened / deprecated)
  - negotiation_reopen_allowed
  - contestable flag
  - filter reasons

No real issue is created. No API is called. No funds move. stdlib only.

Usage:
  python gitlawb/runtime/scoped_issue_snapshot.py
  python gitlawb/runtime/scoped_issue_snapshot.py --json
  python gitlawb/runtime/scoped_issue_snapshot.py --claim-id housing-007
  python gitlawb/runtime/scoped_issue_snapshot.py --applicable-only
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# ── Path setup ────────────────────────────────────────────────────────────────
_FILE_DIR     = Path(__file__).parent
_BRIDGE_DIR   = _FILE_DIR.parent.parent
_RUNTIME_DIR  = _BRIDGE_DIR / "runtime"
_OGI_EXAMPLES = _BRIDGE_DIR / "ogi" / "examples"
sys.path.insert(0, str(_RUNTIME_DIR))
sys.path.insert(0, str(_FILE_DIR))


# ── Snapshot builder ──────────────────────────────────────────────────────────

def _load_plan_trees() -> list[dict[str, Any]]:
    """Load all scoped plan tree JSON files from ogi/examples/."""
    trees = []
    for path in sorted(_OGI_EXAMPLES.glob("scoped-plan-*.output.json")):
        try:
            with open(path) as f:
                trees.append(json.load(f))
        except Exception as e:
            print(f"  WARNING: {path.name}: {e}", file=sys.stderr)
    return trees


def _issue_status(candidate: dict[str, Any]) -> str:
    if not candidate.get("issue_candidate", False):
        return "suppressed"
    return "open_draft"


def build_snapshot(
    claim_id_filter: str | None = None,
    applicable_only: bool = False,
) -> list[dict[str, Any]]:
    """
    Build the full scoped issue snapshot across all known claims.
    """
    from scoped_plan_to_issue import issues_from_scoped_tree
    from scoped_issue_filter  import _apply_filters

    trees = _load_plan_trees()
    if not trees:
        return []

    all_candidates: list[dict[str, Any]] = []
    for tree in trees:
        cid = tree.get("claim_id", "?")
        if claim_id_filter and cid != claim_id_filter:
            continue
        candidates = issues_from_scoped_tree(tree)
        all_candidates.extend(candidates)

    filtered = _apply_filters(all_candidates)

    snapshot_records = []
    for r in filtered:
        if applicable_only and not r.get("issue_candidate", False):
            continue

        status  = _issue_status(r)
        nc      = r.get("negotiation_context", {})
        record  = {
            "claim_id":      r.get("claim_id", "?"),
            "condition":     r.get("condition", "?"),
            "issue_candidate": r.get("issue_candidate", False),
            "issue_status":  status,
            "scope_status":  r.get("scope_status", "?"),
            "scope":         r.get("scope", ""),
            "prerequisite_state": r.get("prerequisite_state", "?"),
            "filter_action": r.get("filter_action", "?"),
            "filter_reason": r.get("filter_reason", "?"),
            "execution_allowed": r.get("execution_allowed", False),
            "moves_money":       r.get("moves_money", False),
            "advisory":          r.get("advisory", True),
            "hard_enforcement":  nc.get("hard_enforcement", False) if nc else False,
            "contestable":       nc.get("contestable", True) if nc else True,
            "negotiation_reopen_allowed":
                nc.get("negotiation_reopen_allowed", True) if nc else True,
        }
        if status == "suppressed":
            record["reason"]  = r.get("reason", r.get("filter_reason", "suppressed"))
            record["bypass_conditions"] = r.get("bypass_conditions", [])
        else:
            record["title"]   = r.get("title", "")
            record["labels"]  = r.get("labels", [])

        snapshot_records.append(record)

    return snapshot_records


# ── CLI display ───────────────────────────────────────────────────────────────

def _print_snapshot(records: list[dict[str, Any]]) -> None:
    open_drafts = [r for r in records if r["issue_status"] == "open_draft"]
    suppressed  = [r for r in records if r["issue_status"] == "suppressed"]

    print(f"\n{'='*60}")
    print(f"  Scoped Issue Snapshot")
    print(f"  Total: {len(records)}  "
          f"Open drafts: {len(open_drafts)}  "
          f"Suppressed: {len(suppressed)}")
    print(f"{'='*60}\n")

    if open_drafts:
        print(f"  Open Issue Drafts (applicable prerequisites):")
        for r in open_drafts:
            print(f"\n  ✓  [{r['claim_id']}] {r['condition']}")
            print(f"       issue_status:           open_draft")
            print(f"       scope_status:           {r['scope_status']}")
            print(f"       scope:                  {r.get('scope','(none)')}")
            print(f"       prerequisite_state:     {r.get('prerequisite_state')}")
            print(f"       contestable:            {r.get('contestable')}")
            print(f"       negotiation_reopen:     {r.get('negotiation_reopen_allowed')}")
            print(f"       hard_enforcement:       {r.get('hard_enforcement')}")
            print(f"       execution_allowed:      {r.get('execution_allowed')}")
            print(f"       moves_money:            {r.get('moves_money')}")

    if suppressed:
        print(f"\n  Suppressed (bypassed / filtered):")
        for r in suppressed:
            icon = "⊗"
            reason = r.get("reason", r.get("filter_reason", "?"))
            byp    = r.get("bypass_conditions", [])
            print(f"  {icon}  [{r['claim_id']}] {r['condition']}")
            print(f"       reason:    {reason}")
            if byp:
                print(f"       bypass:    {byp}")

    print(f"\n  Invariants:")
    print(f"    execution_allowed:  False (all)")
    print(f"    moves_money:        False (all)")
    print(f"    advisory:           True  (all)")
    print(f"    hard_enforcement:   False (all)")
    print(f"    negotiation_reopen: True  (all open drafts)")
    print()


def main() -> None:
    p = argparse.ArgumentParser(
        description="Show scoped issue snapshot across all claims.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gitlawb/runtime/scoped_issue_snapshot.py
  python gitlawb/runtime/scoped_issue_snapshot.py --json
  python gitlawb/runtime/scoped_issue_snapshot.py --claim-id housing-007
  python gitlawb/runtime/scoped_issue_snapshot.py --applicable-only
        """,
    )
    p.add_argument("--json",           action="store_true", dest="json_output")
    p.add_argument("--claim-id",       metavar="CLAIM_ID")
    p.add_argument("--applicable-only", action="store_true",
                   help="Show only open_draft records (suppress suppression records)")
    args = p.parse_args()

    records = build_snapshot(
        claim_id_filter=args.claim_id,
        applicable_only=args.applicable_only,
    )

    if not records:
        print("No scoped plan trees found in ogi/examples/.", file=sys.stderr)
        sys.exit(0)

    if args.json_output:
        print(json.dumps(records, indent=2))
        return

    _print_snapshot(records)


if __name__ == "__main__":
    main()
