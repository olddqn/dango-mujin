"""
contribution_history.py — Contribution History (Append-Only, Advisory)

Records an append-only log of negotiation contribution events for a
given claim and issue. This is the audit trail of who did what in the
Dan-Go negotiation — NOT a credit ledger.

A contribution history entry records:
  - The history identifier and claim context
  - Issue and PR numbers
  - Whether the PR was merged (evidence accepted)
  - Whether the issue was reopened (negotiation continued)
  - Which contributor performed which contribution type

This file does NOT:
  - Issue credit
  - Allocate rewards
  - Remove or modify past entries (append-only invariant)
  - Score contributors
  - Connect to external systems

Contribution history is not credit.
Dan-Go records contribution candidates; external systems may issue credit.

All history entries are advisory. All entries are append-only.
credit_issued is always False.

No secrets. No private keys. No wallet operations. No network. stdlib only.

Usage:
    python bridge/gitsea/credit/runtime/contribution_history.py
    python bridge/gitsea/credit/runtime/contribution_history.py --save
    python bridge/gitsea/credit/runtime/contribution_history.py --json
    python bridge/gitsea/credit/runtime/contribution_history.py \\
        --history-id history-001 --issue 3 --pr 2 --merged --contributor external-001 \\
        --type evidence_accepted
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_FILE_DIR    = Path(__file__).parent
_CREDIT      = _FILE_DIR.parent
_EXAMPLES    = _CREDIT / "examples"

# ── Event types ───────────────────────────────────────────────────────────────

HISTORY_EVENT_TYPES = {
    "evidence_submitted":  "Evidence submitted via PR",
    "evidence_reviewed":   "Evidence reviewed and approved",
    "evidence_accepted":   "Evidence accepted via PR merge",
    "contest_raised":      "Legitimate contest raised",
    "reaffirm_submitted":  "Reaffirmation submitted with new context",
    "plan_correction":     "Plan correction proposed",
    "issue_opened":        "Issue opened to start negotiation",
    "issue_reopened":      "Issue reopened after contest",
    "pr_submitted":        "PR submitted for evidence",
    "pr_merged":           "PR merged — evidence accepted",
    "pr_closed":           "PR closed without merge",
}


# ── History entry builder ─────────────────────────────────────────────────────

def build_history_entry(
    contributor_id: str,
    event_type: str,
    issue_id: int,
    pr_id: int | str | None = None,
    claim_id: str = "housing-007",
    note: str | None = None,
) -> dict[str, Any]:
    """Build a single append-only history entry."""
    if event_type not in HISTORY_EVENT_TYPES:
        raise ValueError(
            f"Unknown event_type {event_type!r}. "
            f"Valid: {list(HISTORY_EVENT_TYPES)}"
        )
    return {
        "event_type":    event_type,
        "event_label":   HISTORY_EVENT_TYPES[event_type],
        "contributor_id": contributor_id,
        "claim_id":      claim_id,
        "issue_id":      issue_id,
        "pr_id":         pr_id,
        "recorded_at":   datetime.now(timezone.utc).isoformat(),
        "note":          note or "",
        "credit_issued": False,   # permanent invariant
        "advisory":      True,
        "append_only":   True,
    }


# ── History document builder ──────────────────────────────────────────────────

def build_contribution_history(
    history_id: str,
    issue_id: int,
    pr_id: int | str,
    merged: bool,
    reopened: bool,
    entries: list[dict[str, Any]],
    claim_id: str = "housing-007",
) -> dict[str, Any]:
    """
    Build an append-only contribution history document.

    Parameters
    ----------
    history_id : str
        Unique identifier for this history record (e.g. "history-001").
    issue_id : int
        GitHub issue number.
    pr_id : int | str
        GitHub PR number associated with the primary evidence.
    merged : bool
        Whether the evidence PR was merged.
    reopened : bool
        Whether the issue was reopened after initial resolution.
    entries : list[dict]
        Ordered list of history entries (append-only; never removed).
    claim_id : str
        Dan-Go claim identifier.
    """
    contributor_ids = list({e.get("contributor_id", "") for e in entries})
    event_types = [e.get("event_type", "") for e in entries]
    return {
        "history_type":      "contribution_history",
        "generated_at":      datetime.now(timezone.utc).isoformat(),
        "history_id":        history_id,

        # Claim context
        "claim_id":          claim_id,
        "issue_id":          issue_id,
        "pr_id":             pr_id,

        # Negotiation outcome
        "merged":            merged,
        "reopened":          reopened,

        # History entries (append-only)
        "entry_count":       len(entries),
        "entries":           entries,

        # Participants
        "contributor_count": len(contributor_ids),
        "contributors":      sorted(contributor_ids),
        "event_types_seen":  sorted(set(event_types)),

        # Credit status (permanent)
        "credit_issued":     False,   # permanent invariant — never changed by Dan-Go
        "external_system":   "gitsea",
        "credit_note": (
            "Dan-Go records contribution candidates; "
            "external systems may issue credit."
        ),

        # Invariants
        "moves_money":        False,
        "execution_allowed":  False,
        "hard_enforcement":   False,
        "advisory":           True,
        "authority":          "none",
        "append_only":        True,
        "contestable":        True,
        "reopenable":         True,

        "contribution_note": "Contribution history is not credit.",
    }


# ── Default history (housing-007, Issue #3, PR #2) ────────────────────────────

def build_default_history() -> dict[str, Any]:
    """Build the default example contribution history for housing-007."""
    entries = [
        build_history_entry(
            contributor_id="external-002",
            event_type="issue_opened",
            issue_id=3,
            claim_id="housing-007",
            note="Issue opened to negotiate housing safety assessment evidence",
        ),
        build_history_entry(
            contributor_id="external-002",
            event_type="pr_submitted",
            issue_id=3,
            pr_id=2,
            claim_id="housing-007",
            note="PR #2 submitted with space safety assessment report",
        ),
        build_history_entry(
            contributor_id="external-001",
            event_type="evidence_reviewed",
            issue_id=3,
            pr_id=2,
            claim_id="housing-007",
            note="Reviewer external-001 reviewed and approved evidence",
        ),
        build_history_entry(
            contributor_id="external-003",
            event_type="contest_raised",
            issue_id=3,
            pr_id=2,
            claim_id="housing-007",
            note="Contester external-003 raised legitimate contest regarding scope",
        ),
        build_history_entry(
            contributor_id="external-002",
            event_type="reaffirm_submitted",
            issue_id=3,
            pr_id=2,
            claim_id="housing-007",
            note="Author reaffirmed evidence with additional context addressing contest",
        ),
        build_history_entry(
            contributor_id="external-001",
            event_type="pr_merged",
            issue_id=3,
            pr_id=2,
            claim_id="housing-007",
            note="PR #2 merged after reaffirmation — evidence accepted",
        ),
        build_history_entry(
            contributor_id="external-002",
            event_type="evidence_accepted",
            issue_id=3,
            pr_id=2,
            claim_id="housing-007",
            note="Evidence accepted; contribution candidate recorded",
        ),
    ]
    return build_contribution_history(
        history_id="history-001",
        issue_id=3,
        pr_id=2,
        merged=True,
        reopened=False,
        entries=entries,
        claim_id="housing-007",
    )


# ── Save ──────────────────────────────────────────────────────────────────────

def save_history(doc: dict, out_path: Path | None = None) -> Path:
    if out_path is None:
        out_path = _EXAMPLES / "contribution-history.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Record append-only contribution history (no credit issued).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contribution history is not credit.
Dan-Go records contribution candidates; external systems may issue credit.

Event types:
  evidence_submitted  evidence_reviewed  evidence_accepted
  contest_raised      reaffirm_submitted plan_correction
  issue_opened        issue_reopened
  pr_submitted        pr_merged          pr_closed

Examples:
  python bridge/gitsea/credit/runtime/contribution_history.py
  python bridge/gitsea/credit/runtime/contribution_history.py --save
  python bridge/gitsea/credit/runtime/contribution_history.py --json
  python bridge/gitsea/credit/runtime/contribution_history.py \\
      --history-id history-001 --issue 3 --pr 2 --merged \\
      --contributor external-001 --type evidence_accepted
        """,
    )
    p.add_argument("--history-id", default="history-001",
                   help="History record identifier (default: history-001)")
    p.add_argument("--issue", type=int, default=None,
                   help="GitHub issue number")
    p.add_argument("--pr", default=None,
                   help="GitHub PR number")
    p.add_argument("--merged", action="store_true",
                   help="Mark the PR as merged")
    p.add_argument("--reopened", action="store_true",
                   help="Mark the issue as reopened")
    p.add_argument("--contributor", default=None,
                   help="Contributor ID for single-entry mode")
    p.add_argument("--type", default=None, dest="etype",
                   choices=list(HISTORY_EVENT_TYPES),
                   help="Event type for single-entry mode")
    p.add_argument("--claim", default="housing-007")
    p.add_argument("--save", action="store_true",
                   help="Save to credit/examples/contribution-history.json")
    p.add_argument("--json", action="store_true", dest="json_output")
    args = p.parse_args()

    if args.issue and args.pr and args.contributor and args.etype:
        # Single-entry mode: build a one-entry history
        try:
            entry = build_history_entry(
                contributor_id=args.contributor,
                event_type=args.etype,
                issue_id=args.issue,
                pr_id=args.pr,
                claim_id=args.claim,
            )
        except ValueError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)
        doc = build_contribution_history(
            history_id=args.history_id,
            issue_id=args.issue,
            pr_id=args.pr,
            merged=args.merged,
            reopened=args.reopened,
            entries=[entry],
            claim_id=args.claim,
        )
    else:
        # Default: full example history for housing-007
        doc = build_default_history()

    if args.save:
        out = save_history(doc)
        print(f"Saved: {out}")

    if args.json_output:
        print(json.dumps(doc, indent=2, ensure_ascii=False))
        return

    # Default: human-readable
    print(f"\n{'='*60}")
    print(f"  Contribution History: {doc['history_id']}")
    print(f"{'='*60}")
    print(f"  Claim:           {doc['claim_id']}")
    print(f"  Issue:           #{doc['issue_id']}  PR: {doc['pr_id']}")
    print(f"  Merged:          {doc['merged']}")
    print(f"  Reopened:        {doc['reopened']}")
    print(f"  Entries:         {doc['entry_count']}")
    print(f"  Contributors:    {', '.join(doc['contributors'])}")
    print()
    for e in doc["entries"]:
        mark = "→"
        print(f"  {mark}  [{e['contributor_id']}]  {e['event_label']}")
        if e.get("pr_id"):
            print(f"       issue #{e['issue_id']}  pr {e['pr_id']}")
        else:
            print(f"       issue #{e['issue_id']}")
        if e.get("note"):
            print(f"       note: {e['note'][:60]}")
    print(f"\n  credit_issued:       {doc['credit_issued']}  (permanent: never by Dan-Go)")
    print(f"  moves_money:         {doc['moves_money']}")
    print(f"  execution_allowed:   {doc['execution_allowed']}")
    print(f"  advisory:            {doc['advisory']}")
    print(f"  authority:           {doc['authority']}")
    print(f"  append_only:         {doc['append_only']}")
    print(f"\n  \"{doc['contribution_note']}\"")
    print()


if __name__ == "__main__":
    main()
