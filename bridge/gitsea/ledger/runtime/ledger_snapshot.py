"""
ledger_snapshot.py — Ledger Snapshot (Advisory)

Summarises all ledger entries for a claim into a single advisory snapshot.
Reports aggregate counts across all four phases without judging the entries.

A ledger snapshot answers:
  - How many ledger entries exist?
  - How many entries have candidate credit? (Phase 11)
  - How many entries have external credit? (Phase 12)
  - How many entries have reflection records? (Phase 13)
  - How many entries have appeal records? (Phase 14)
  - Is the recognition history complete for each entry?

The snapshot does not evaluate whether outcomes were fair.
The snapshot does not issue credit. The snapshot does not create authority.

This file does NOT:
  - Issue credit
  - Judge the ledger state
  - Create authority
  - Move funds
  - Call any API

Core principles:
  "Recognition history is not authority."
  "Ledger is not judgment."

No secrets. No private keys. No wallet operations. No network. stdlib only.

Usage:
    python bridge/gitsea/ledger/runtime/ledger_snapshot.py
    python bridge/gitsea/ledger/runtime/ledger_snapshot.py --save
    python bridge/gitsea/ledger/runtime/ledger_snapshot.py --json
    python bridge/gitsea/ledger/runtime/ledger_snapshot.py \\
        --input bridge/gitsea/ledger/examples/recognition-ledger.json
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


# ── Snapshot builder ──────────────────────────────────────────────────────────

def build_ledger_snapshot(
    claim_id: str,
    issue_id: int,
    ledger_entry_count: int,
    candidate_count: int,
    external_credit_count: int,
    reflection_count: int,
    appeal_count: int,
    gap_count: int,
    recognition_history_complete: bool,
    external_system: str = "gitsea",
    source_ledger_id: str | None = None,
) -> dict[str, Any]:
    """
    Build a ledger snapshot summarising all entries.

    Parameters
    ----------
    claim_id : str
        Dan-Go claim identifier.
    issue_id : int
        GitHub issue number.
    ledger_entry_count : int
        Total ledger entries.
    candidate_count : int
        Entries with candidate_credit=true (Phase 11).
    external_credit_count : int
        Entries with external credit detected (Phase 12).
    reflection_count : int
        Entries with reflection recorded (Phase 13).
    appeal_count : int
        Entries with appeal recorded (Phase 14).
    gap_count : int
        Entries with candidate but no external credit.
    recognition_history_complete : bool
        Whether all entries have complete Phase 11–14 history.
    external_system : str
        External system identifier.
    source_ledger_id : str | None
        Ledger this snapshot summarises.
    """
    return {
        "snapshot_type":              "ledger_snapshot",
        "generated_at":               datetime.now(timezone.utc).isoformat(),
        "snapshot_id":                f"ledger-snap-{claim_id}-issue-{issue_id}",

        # Source
        "claim_id":                   claim_id,
        "issue_id":                   issue_id,
        "external_system":            external_system,
        "source_ledger_id":           source_ledger_id,

        # Phase-by-phase counts
        "ledger_entry_count":         ledger_entry_count,
        "candidate_count":            candidate_count,      # Phase 11
        "external_credit_count":      external_credit_count,# Phase 12
        "reflection_count":           reflection_count,     # Phase 13
        "appeal_count":               appeal_count,         # Phase 14

        # Derived
        "gap_count":                  gap_count,
        "coverage_rate": {
            "candidate":   round(candidate_count / ledger_entry_count, 3)
                           if ledger_entry_count else 0.0,
            "external_credit": round(external_credit_count / ledger_entry_count, 3)
                               if ledger_entry_count else 0.0,
            "reflection":  round(reflection_count / ledger_entry_count, 3)
                           if ledger_entry_count else 0.0,
            "appeal":      round(appeal_count / ledger_entry_count, 3)
                           if ledger_entry_count else 0.0,
        },

        # Ledger completeness
        "recognition_history_complete": recognition_history_complete,

        # Snapshot interpretation
        "snapshot_judges":            False,   # invariant
        "snapshot_ranks":             False,   # invariant
        "snapshot_note": (
            f"{ledger_entry_count} ledger entry/entries for claim {claim_id} issue #{issue_id}. "
            f"{candidate_count} candidate(s), {external_credit_count} externally credited, "
            f"{gap_count} gap(s). Recognition history complete: {recognition_history_complete}. "
            "Ledger is not judgment."
        ),

        # Permanent invariants
        "credit_issued":              False,
        "moves_money":                False,
        "execution_allowed":          False,
        "hard_enforcement":           False,
        "advisory":                   True,
        "ledger_only":                True,
        "authority":                  "none",
        "judgment":                   False,
        "append_only":                True,
        "contestable":                True,
        "reopenable":                 True,

        "principle_1": "Recognition history is not authority.",
        "principle_2": "Ledger is not judgment.",
    }


# ── Load from ledger ──────────────────────────────────────────────────────────

def load_recognition_ledger(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ── Save ──────────────────────────────────────────────────────────────────────

def save_snapshot(doc: dict, out_path: Path | None = None) -> Path:
    if out_path is None:
        out_path = _EXAMPLES / "ledger-snapshot.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Snapshot ledger summary counts (no credit issued).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Recognition history is not authority.
Ledger is not judgment.

Examples:
  python bridge/gitsea/ledger/runtime/ledger_snapshot.py
  python bridge/gitsea/ledger/runtime/ledger_snapshot.py --save
  python bridge/gitsea/ledger/runtime/ledger_snapshot.py --json
  python bridge/gitsea/ledger/runtime/ledger_snapshot.py \\
      --input bridge/gitsea/ledger/examples/recognition-ledger.json
        """,
    )
    p.add_argument("--input", metavar="PATH",
                   help="Path to recognition-ledger.json")
    p.add_argument("--claim", default="housing-007")
    p.add_argument("--issue", type=int, default=3)
    p.add_argument("--save", action="store_true",
                   help="Save to ledger/examples/ledger-snapshot.json")
    p.add_argument("--json", action="store_true", dest="json_output")
    args = p.parse_args()

    # Load from ledger if available
    ledger_path = (
        Path(args.input) if args.input
        else _EXAMPLES / "recognition-ledger.json"
    )
    ledger = load_recognition_ledger(ledger_path)

    if ledger:
        claim_id    = ledger.get("claim_id", args.claim)
        issue_id    = ledger.get("issue", args.issue)
        source_id   = ledger.get("ledger_id")
        ext_sys     = ledger.get("external_system", "gitsea")
        entries     = ledger.get("entries", [])
        n           = len(entries)
        doc = build_ledger_snapshot(
            claim_id=claim_id,
            issue_id=issue_id,
            ledger_entry_count=ledger.get("entry_count", n),
            candidate_count=ledger.get("candidate_count", 0),
            external_credit_count=ledger.get("external_credit_count", 0),
            reflection_count=ledger.get("reflection_count", 0),
            appeal_count=ledger.get("appeal_count", 0),
            gap_count=ledger.get("gap_count", 0),
            recognition_history_complete=ledger.get("recognition_history_complete", False),
            external_system=ext_sys,
            source_ledger_id=source_id,
        )
    else:
        # Default stub
        doc = build_ledger_snapshot(
            claim_id=args.claim,
            issue_id=args.issue,
            ledger_entry_count=2,
            candidate_count=2,
            external_credit_count=0,
            reflection_count=2,
            appeal_count=2,
            gap_count=2,
            recognition_history_complete=True,
        )

    if args.save:
        out = save_snapshot(doc)
        print(f"Saved: {out}")

    if args.json_output:
        print(json.dumps(doc, indent=2, ensure_ascii=False))
        return

    # Default: human-readable
    print(f"\n{'='*60}")
    print(f"  Ledger Snapshot: {doc['snapshot_id']}")
    print(f"{'='*60}")
    print(f"  Claim:                   {doc['claim_id']}  (issue #{doc['issue_id']})")
    print(f"  Source ledger:           {doc['source_ledger_id'] or '(default)'}")
    print()
    print(f"  Ledger entries:          {doc['ledger_entry_count']}")
    print(f"  Candidate count:         {doc['candidate_count']}   "
          f"(coverage: {doc['coverage_rate']['candidate']:.0%})")
    print(f"  External credit count:   {doc['external_credit_count']}   "
          f"(coverage: {doc['coverage_rate']['external_credit']:.0%})")
    print(f"  Reflection count:        {doc['reflection_count']}   "
          f"(coverage: {doc['coverage_rate']['reflection']:.0%})")
    print(f"  Appeal count:            {doc['appeal_count']}   "
          f"(coverage: {doc['coverage_rate']['appeal']:.0%})")
    print(f"  Gap count:               {doc['gap_count']}")
    print(f"  History complete:        {doc['recognition_history_complete']}")
    print(f"\n  authority:    {doc['authority']}")
    print(f"  judgment:     {doc['judgment']}")
    print(f"  ledger_only:  {doc['ledger_only']}")
    print(f"  credit_issued:{doc['credit_issued']}")
    print(f"  advisory:     {doc['advisory']}")
    print(f"\n  \"{doc['principle_1']}\"")
    print(f"  \"{doc['principle_2']}\"")
    print()


if __name__ == "__main__":
    main()
