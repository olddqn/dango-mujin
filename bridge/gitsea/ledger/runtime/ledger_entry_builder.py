"""
ledger_entry_builder.py — Ledger Entry Builder (Advisory, Append-Only)

Builds a single append-only ledger entry by combining records from:
  - Phase 11: contribution candidate
  - Phase 12: external credit observation
  - Phase 13: reflection memory
  - Phase 14: recognition appeal

A ledger entry is the atomic unit of the recognition ledger. It records
the complete Phase 11–14 history for one contributor on one claim.

The entry does not judge the contributor. It does not issue credit.
It does not create authority. It preserves the full observable record.

This file does NOT:
  - Issue credit
  - Judge contribution quality
  - Create authority over external systems
  - Rank contributors
  - Move funds
  - Perform wallet operations
  - Call any API

Core principles:
  "Recognition history is not authority."
  "Ledger is not judgment."

No secrets. No private keys. No wallet operations. No network. stdlib only.

Usage:
    python bridge/gitsea/ledger/runtime/ledger_entry_builder.py
    python bridge/gitsea/ledger/runtime/ledger_entry_builder.py --save
    python bridge/gitsea/ledger/runtime/ledger_entry_builder.py --json
    python bridge/gitsea/ledger/runtime/ledger_entry_builder.py \\
        --entry-id ledger-entry-001 --claim housing-007 --issue 3 \\
        --pr 2 --contributor external-001
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_FILE_DIR = Path(__file__).parent
_LEDGER   = _FILE_DIR.parent
_EXAMPLES = _LEDGER / "examples"

# ── Canonical event sequence ───────────────────────────────────────────────────

LEDGER_EVENTS = {
    "candidate_created":           "Contribution candidate recorded (Phase 11)",
    "external_credit_not_observed": "No external credit detected (Phase 12)",
    "external_credit_observed":    "External credit detected (Phase 12)",
    "reflection_recorded":         "Reflection memory stored (Phase 13)",
    "appeal_recorded":             "Recognition appeal filed (Phase 14)",
    "appeal_acknowledged":         "Appeal acknowledged by external system",
    "appeal_credited":             "External credit issued following appeal",
    "appeal_not_credited":         "Appeal considered; no credit issued",
}


# ── Entry builder ─────────────────────────────────────────────────────────────

def build_ledger_entry(
    entry_id: str,
    claim_id: str,
    issue_id: int,
    pr_id: int | str | None,
    contributor_id: str,
    contribution_type: str,
    contribution_label: str = "",
    candidate_credit: bool = True,
    external_credit: bool = False,
    reflection_recorded: bool = True,
    appeal_recorded: bool = True,
    appeal_status: str = "pending",
    external_system: str = "gitsea",
) -> dict[str, Any]:
    """
    Build a single append-only ledger entry.

    Combines Phase 11–14 records for a single contributor on a single claim
    into one canonical entry in the recognition ledger.

    Parameters
    ----------
    entry_id : str
        Unique ledger entry identifier.
    claim_id : str
        Dan-Go claim identifier.
    issue_id : int
        GitHub issue number.
    pr_id : int | str | None
        GitHub PR number.
    contributor_id : str
        Pseudonymous contributor identifier.
    contribution_type : str
        Type of contribution (from Phase 11).
    contribution_label : str
        Human-readable contribution label.
    candidate_credit : bool
        Phase 11: whether candidate_credit was true.
    external_credit : bool
        Phase 12: whether external credit was detected.
    reflection_recorded : bool
        Phase 13: whether reflection memory was stored.
    appeal_recorded : bool
        Phase 14: whether a recognition appeal was filed.
    appeal_status : str
        Phase 14: current appeal lifecycle state.
    external_system : str
        External system identifier.
    """
    # Build the event sequence from what occurred
    events: list[str] = ["candidate_created"]
    if external_credit:
        events.append("external_credit_observed")
    else:
        events.append("external_credit_not_observed")
    if reflection_recorded:
        events.append("reflection_recorded")
    if appeal_recorded:
        events.append("appeal_recorded")
    if appeal_status == "acknowledged":
        events.append("appeal_acknowledged")
    elif appeal_status == "credited":
        events.append("appeal_credited")
    elif appeal_status == "not_credited":
        events.append("appeal_not_credited")

    recognition_history_complete = (
        candidate_credit is not None
        and reflection_recorded
        and appeal_recorded
    )

    return {
        "entry_type":          "ledger_entry",
        "generated_at":        datetime.now(timezone.utc).isoformat(),
        "entry_id":            entry_id,

        # Claim identity
        "claim_id":            claim_id,
        "issue":               issue_id,
        "pr":                  pr_id,

        # Contributor
        "contributor":         contributor_id,
        "contribution_type":   contribution_type,
        "contribution_label":  contribution_label or contribution_type,

        # Phase-by-phase record
        "candidate_credit":    candidate_credit,    # Phase 11
        "external_credit":     external_credit,     # Phase 12
        "reflection_recorded": reflection_recorded, # Phase 13
        "appeal_recorded":     appeal_recorded,     # Phase 14
        "appeal_status":       appeal_status,       # Phase 14 lifecycle

        # External system
        "external_system":     external_system,

        # Event sequence (append-only)
        "events":              events,
        "event_count":         len(events),

        # Ledger status
        "recognition_history_complete": recognition_history_complete,
        "gap_present":         candidate_credit and not external_credit,

        # What the entry does NOT do
        "entry_issues_credit":   False,   # invariant
        "entry_judges":          False,   # invariant
        "entry_ranks":           False,   # invariant
        "entry_creates_authority": False, # invariant

        # Permanent invariants
        "credit_issued":        False,
        "moves_money":          False,
        "execution_allowed":    False,
        "hard_enforcement":     False,
        "advisory":             True,
        "ledger_only":          True,
        "authority":            "none",
        "judgment":             False,
        "append_only":          True,
        "contestable":          True,
        "reopenable":           True,

        "principle_1": "Recognition history is not authority.",
        "principle_2": "Ledger is not judgment.",
    }


# ── Default entries ───────────────────────────────────────────────────────────

DEFAULT_ENTRIES = [
    {
        "entry_id":          "ledger-entry-001",
        "claim_id":          "housing-007",
        "issue_id":          3,
        "pr_id":             2,
        "contributor_id":    "external-001",
        "contribution_type": "evidence_reviewed",
        "contribution_label": "Evidence reviewed and approved",
        "candidate_credit":  True,
        "external_credit":   False,
        "reflection_recorded": True,
        "appeal_recorded":   True,
    },
    {
        "entry_id":          "ledger-entry-002",
        "claim_id":          "housing-007",
        "issue_id":          3,
        "pr_id":             2,
        "contributor_id":    "external-002",
        "contribution_type": "evidence_accepted",
        "contribution_label": "Evidence accepted via PR merge",
        "candidate_credit":  True,
        "external_credit":   False,
        "reflection_recorded": True,
        "appeal_recorded":   True,
    },
]


def build_entries_list(
    raw_entries: list[dict] | None = None,
) -> dict[str, Any]:
    """Build a list of ledger entries."""
    raws = raw_entries if raw_entries is not None else DEFAULT_ENTRIES
    entries = [
        build_ledger_entry(
            entry_id=r["entry_id"],
            claim_id=r["claim_id"],
            issue_id=r["issue_id"],
            pr_id=r.get("pr_id"),
            contributor_id=r["contributor_id"],
            contribution_type=r["contribution_type"],
            contribution_label=r.get("contribution_label", ""),
            candidate_credit=r.get("candidate_credit", True),
            external_credit=r.get("external_credit", False),
            reflection_recorded=r.get("reflection_recorded", True),
            appeal_recorded=r.get("appeal_recorded", True),
        )
        for r in raws
    ]
    return {
        "list_type":    "ledger_entry_list",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_entries": len(entries),
        "entries":      entries,

        # Invariants
        "credit_issued":     False,
        "moves_money":       False,
        "execution_allowed": False,
        "hard_enforcement":  False,
        "advisory":          True,
        "ledger_only":       True,
        "authority":         "none",
        "judgment":          False,
        "append_only":       True,

        "principle_1": "Recognition history is not authority.",
        "principle_2": "Ledger is not judgment.",
    }


# ── Save ──────────────────────────────────────────────────────────────────────

def save_entry(doc: dict, out_path: Path | None = None) -> Path:
    if out_path is None:
        out_path = _EXAMPLES / "ledger-entry.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Build append-only ledger entries (no credit issued).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Recognition history is not authority.
Ledger is not judgment.

Examples:
  python bridge/gitsea/ledger/runtime/ledger_entry_builder.py
  python bridge/gitsea/ledger/runtime/ledger_entry_builder.py --save
  python bridge/gitsea/ledger/runtime/ledger_entry_builder.py --json
  python bridge/gitsea/ledger/runtime/ledger_entry_builder.py \\
      --entry-id ledger-entry-001 --claim housing-007 --issue 3 \\
      --pr 2 --contributor external-001 --type evidence_reviewed
        """,
    )
    p.add_argument("--entry-id", default=None)
    p.add_argument("--claim", default=None)
    p.add_argument("--issue", type=int, default=None)
    p.add_argument("--pr", default=None)
    p.add_argument("--contributor", default=None)
    p.add_argument("--type", default=None, dest="ctype")
    p.add_argument("--external-credit", action="store_true")
    p.add_argument("--save", action="store_true",
                   help="Save to ledger/examples/ledger-entry.json")
    p.add_argument("--json", action="store_true", dest="json_output")
    args = p.parse_args()

    if args.entry_id and args.claim and args.issue and args.contributor and args.ctype:
        doc = build_ledger_entry(
            entry_id=args.entry_id,
            claim_id=args.claim,
            issue_id=args.issue,
            pr_id=args.pr,
            contributor_id=args.contributor,
            contribution_type=args.ctype,
            external_credit=args.external_credit,
        )
    else:
        doc = build_entries_list()

    if args.save:
        out = save_entry(doc)
        print(f"Saved: {out}")

    if args.json_output:
        print(json.dumps(doc, indent=2, ensure_ascii=False))
        return

    # Default: human-readable
    print(f"\n{'='*60}")
    print(f"  Ledger Entries")
    print(f"{'='*60}")

    if "entries" in doc:
        print(f"  Total entries: {doc['total_entries']}")
        print()
        for e in doc["entries"]:
            print(f"  ◆  [{e['contributor']}]  {e['contribution_label']}")
            print(f"       entry: {e['entry_id']}  issue: #{e['issue']}  pr: {e['pr']}")
            print(f"       events: {' → '.join(e['events'])}")
            print(f"       complete={e['recognition_history_complete']}  "
                  f"gap={e['gap_present']}  judgment={e['judgment']}")
    else:
        print(f"  Entry ID:     {doc['entry_id']}")
        print(f"  Contributor:  {doc['contributor']}")
        print(f"  Events:       {' → '.join(doc['events'])}")
        print(f"  Complete:     {doc['recognition_history_complete']}")
        print(f"  Judgment:     {doc['judgment']}")

    print(f"\n  authority:    {doc.get('authority', 'none')}")
    print(f"  judgment:     {doc.get('judgment', False)}")
    print(f"  ledger_only:  {doc.get('ledger_only', True)}")
    print(f"  credit_issued:{doc.get('credit_issued', False)}")
    print(f"  advisory:     {doc.get('advisory', True)}")
    print(f"\n  \"{doc.get('principle_1', '')}\"")
    print(f"  \"{doc.get('principle_2', '')}\"")
    print()


if __name__ == "__main__":
    main()
