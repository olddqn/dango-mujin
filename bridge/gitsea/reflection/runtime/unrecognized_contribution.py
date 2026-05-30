"""
unrecognized_contribution.py — Unrecognized Contribution Record (Advisory)

Records contributions that completed the Dan-Go candidate threshold but were
not recognized by external credit systems. These records exist because the
contribution happened — whether or not it was credited.

An unrecognized contribution record is:
  - An observable fact about what occurred
  - A permanent part of the contribution history
  - Not an accusation against any external system
  - Not evidence of failure
  - Not grounds for appeal or escalation

This file does NOT:
  - Issue credit
  - Flag external systems
  - Create disputes
  - Score contributors
  - Move funds
  - Perform wallet operations

Dan-Go records what happened. Whether credit follows is external.
Unrecognized does not mean unlost — the contribution is still observable here.

Core principles:
  "Unrecognized contribution is still observable."
  "Reflection is not judgment."

No secrets. No private keys. No wallet operations. No network. stdlib only.

Usage:
    python bridge/gitsea/reflection/runtime/unrecognized_contribution.py
    python bridge/gitsea/reflection/runtime/unrecognized_contribution.py --save
    python bridge/gitsea/reflection/runtime/unrecognized_contribution.py --json
    python bridge/gitsea/reflection/runtime/unrecognized_contribution.py \\
        --contributor external-001 --type evidence_reviewed --claim housing-007
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_FILE_DIR   = Path(__file__).parent
_REFLECTION = _FILE_DIR.parent
_EXAMPLES   = _REFLECTION / "examples"


# ── Record builder ────────────────────────────────────────────────────────────

def build_unrecognized_contribution(
    contributor_id: str,
    contribution_type: str,
    claim_id: str,
    issue_id: int,
    pr_id: int | str | None = None,
    contribution_label: str = "",
    external_system: str = "gitsea",
    observation_note: str | None = None,
) -> dict[str, Any]:
    """
    Build a record for a contribution that was not recognized by external credit.

    Parameters
    ----------
    contributor_id : str
        Pseudonymous contributor identifier.
    contribution_type : str
        Type of contribution (from Phase 11 CONTRIBUTION_TYPES).
    claim_id : str
        Dan-Go claim identifier.
    issue_id : int
        GitHub issue number.
    pr_id : int | str | None
        GitHub PR number, if applicable.
    contribution_label : str
        Human-readable label for the contribution type.
    external_system : str
        External system that was observed and found no credit.
    observation_note : str | None
        Optional observation note.
    """
    return {
        "record_type":       "unrecognized_contribution",
        "generated_at":      datetime.now(timezone.utc).isoformat(),
        "record_id":         (
            f"unrecog-{claim_id}-issue-{issue_id}-{contributor_id}"
        ),

        # Contribution identity
        "contributor_id":    contributor_id,
        "contribution_type": contribution_type,
        "contribution_label": contribution_label or contribution_type,
        "claim_id":          claim_id,
        "issue_id":          issue_id,
        "pr_id":             pr_id,

        # Candidate status (Phase 11)
        "candidate_credit":  True,   # This record only exists for credit-eligible candidates
        "candidate_threshold_met": True,

        # External observation (Phase 12)
        "external_system":   external_system,
        "external_credit":   False,
        "recognized":        False,

        # What "unrecognized" means
        "unrecognized_means": (
            "The contribution candidate met the Dan-Go threshold and was "
            "recorded in Phase 11, but no corresponding credit record was "
            f"detected in {external_system} during Phase 12 observation. "
            "This is an observation, not an accusation. "
            "External credit systems are sovereign over their decisions."
        ),
        "contribution_lost": False,   # invariant — contribution is always here
        "is_failure":        False,   # invariant — unrecognized is not failure
        "is_accusation":     False,   # invariant — records do not accuse

        # Observation note
        "observation_note": (
            observation_note or
            f"Contribution observed in Dan-Go; not detected in {external_system}. "
            "Unrecognized contribution is still observable."
        ),

        # Permanent invariants
        "credit_issued":      False,
        "moves_money":        False,
        "execution_allowed":  False,
        "hard_enforcement":   False,
        "advisory":           True,
        "reflection_only":    True,
        "authority":          "none",
        "append_only":        True,
        "contestable":        True,
        "reopenable":         True,

        "principle_1": "Unrecognized contribution is still observable.",
        "principle_2": "Reflection is not judgment.",
    }


# ── Default examples ──────────────────────────────────────────────────────────

DEFAULT_UNRECOGNIZED = [
    {
        "contributor_id":    "external-001",
        "contribution_type": "evidence_reviewed",
        "contribution_label": "Evidence reviewed and approved",
        "claim_id":          "housing-007",
        "issue_id":          1,
        "pr_id":             1,
    },
    {
        "contributor_id":    "external-002",
        "contribution_type": "evidence_accepted",
        "contribution_label": "Evidence accepted via PR merge",
        "claim_id":          "housing-007",
        "issue_id":          1,
        "pr_id":             1,
    },
]


def build_unrecognized_list(
    raw: list[dict] | None = None,
) -> dict[str, Any]:
    """Build an aggregated list of unrecognized contribution records."""
    entries = raw if raw is not None else DEFAULT_UNRECOGNIZED
    records = [
        build_unrecognized_contribution(
            contributor_id=r["contributor_id"],
            contribution_type=r["contribution_type"],
            claim_id=r["claim_id"],
            issue_id=r["issue_id"],
            pr_id=r.get("pr_id"),
            contribution_label=r.get("contribution_label", ""),
        )
        for r in entries
    ]
    return {
        "list_type":          "unrecognized_contribution_list",
        "generated_at":       datetime.now(timezone.utc).isoformat(),
        "total_unrecognized": len(records),
        "records":            records,

        "list_note": (
            f"{len(records)} contribution(s) met the Dan-Go candidate threshold "
            "but were not detected in observed external credit systems. "
            "These contributions are still observable here. "
            "This list is not a complaint or appeal."
        ),

        # Invariants
        "credit_issued":      False,
        "moves_money":        False,
        "execution_allowed":  False,
        "hard_enforcement":   False,
        "advisory":           True,
        "reflection_only":    True,
        "authority":          "none",
        "append_only":        True,

        "principle_1": "Unrecognized contribution is still observable.",
        "principle_2": "Reflection is not judgment.",
    }


# ── Save ──────────────────────────────────────────────────────────────────────

def save_unrecognized(doc: dict, out_path: Path | None = None) -> Path:
    if out_path is None:
        out_path = _EXAMPLES / "unrecognized-contribution.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Record unrecognized contributions (observation only, no credit issued).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Unrecognized contribution is still observable.
Reflection is not judgment.
This is an observation record, not a complaint or appeal.

Examples:
  python bridge/gitsea/reflection/runtime/unrecognized_contribution.py
  python bridge/gitsea/reflection/runtime/unrecognized_contribution.py --save
  python bridge/gitsea/reflection/runtime/unrecognized_contribution.py --json
  python bridge/gitsea/reflection/runtime/unrecognized_contribution.py \\
      --contributor external-001 --type evidence_reviewed \\
      --claim housing-007 --issue 1
        """,
    )
    p.add_argument("--contributor", default=None)
    p.add_argument("--type", default=None, dest="ctype")
    p.add_argument("--claim", default=None)
    p.add_argument("--issue", type=int, default=None)
    p.add_argument("--pr", default=None)
    p.add_argument("--save", action="store_true",
                   help="Save to reflection/examples/unrecognized-contribution.json")
    p.add_argument("--json", action="store_true", dest="json_output")
    args = p.parse_args()

    if args.contributor and args.ctype and args.claim and args.issue:
        doc = build_unrecognized_contribution(
            contributor_id=args.contributor,
            contribution_type=args.ctype,
            claim_id=args.claim,
            issue_id=args.issue,
            pr_id=args.pr,
        )
    else:
        doc = build_unrecognized_list()

    if args.save:
        out = save_unrecognized(doc)
        print(f"Saved: {out}")

    if args.json_output:
        print(json.dumps(doc, indent=2, ensure_ascii=False))
        return

    # Default: human-readable
    print(f"\n{'='*60}")
    print(f"  Unrecognized Contribution Records")
    print(f"{'='*60}")

    if "records" in doc:
        print(f"  Total unrecognized: {doc['total_unrecognized']}")
        print(f"  Note: {doc['list_note'][:70]}...")
        print()
        for r in doc["records"]:
            print(f"  △  [{r['contributor_id']}]  {r['contribution_label']}")
            print(f"       claim: {r['claim_id']}  issue: #{r['issue_id']}"
                  + (f"  pr: {r['pr_id']}" if r.get("pr_id") else ""))
            print(f"       recognized={r['recognized']}  "
                  f"is_failure={r['is_failure']}  "
                  f"contribution_lost={r['contribution_lost']}")
    else:
        print(f"  Record ID:     {doc['record_id']}")
        print(f"  Contributor:   {doc['contributor_id']}")
        print(f"  Type:          {doc['contribution_label']}")
        print(f"  Recognized:    {doc['recognized']}")
        print(f"  Is failure:    {doc['is_failure']}")
        print(f"  Is accusation: {doc['is_accusation']}")

    print(f"\n  credit_issued:     {doc.get('credit_issued', False)}")
    print(f"  reflection_only:   {doc.get('reflection_only', True)}")
    print(f"  moves_money:       {doc.get('moves_money', False)}")
    print(f"  advisory:          {doc.get('advisory', True)}")
    print(f"  authority:         {doc.get('authority', 'none')}")
    print(f"\n  \"{doc.get('principle_1', '')}\"")
    print(f"  \"{doc.get('principle_2', '')}\"")
    print()


if __name__ == "__main__":
    main()
