"""
ledger_report.py — Ledger Report (Human-Readable, Advisory)

Generates the Phase 15 summary report explaining:
  - Why recognition history exists and what it contains
  - Why the ledger does not judge
  - Why the ledger does not issue credit
  - Why the ledger does not force recognition
  - Why append-only history preserves reopenability

This is the authoritative advisory summary for Phase 15.

This file does NOT:
  - Issue credit
  - Judge contributions
  - Force recognition
  - Create authority
  - Move funds

Core principles:
  "Recognition history is not authority."
  "Ledger is not judgment."

No secrets. No private keys. No wallet operations. No network. stdlib only.

Usage:
    python bridge/gitsea/ledger/runtime/ledger_report.py
    python bridge/gitsea/ledger/runtime/ledger_report.py --save
    python bridge/gitsea/ledger/runtime/ledger_report.py --json
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


# ── Report sections ───────────────────────────────────────────────────────────

LEDGER_REPORT_SECTIONS = [
    {
        "section": "Why Recognition History Exists",
        "summary": (
            "A complete history of what occurred — candidate, observation, "
            "reflection, appeal — is more legible than any single phase alone."
        ),
        "detail": (
            "Phases 11–14 each produced separate advisory records: contribution "
            "candidates, external credit observations, reflection memory, and "
            "recognition appeals. Phase 15 links these into one recognition "
            "ledger so that the full lifecycle of a contributor's participation "
            "is visible in one place. History makes contribution legible. "
            "Legibility is the goal of the Dan-Go protocol."
        ),
        "history_useful": True,
        "credit_issued":  False,
    },
    {
        "section": "Why the Ledger Does Not Judge",
        "summary": (
            "A ledger records events. It does not evaluate whether outcomes were "
            "fair, appropriate, or deserved."
        ),
        "detail": (
            "The judgment: false invariant appears on every ledger record. "
            "This means the ledger does not classify contributions as good or bad, "
            "successful or failed, worthy or unworthy. It records what occurred: "
            "a candidate was created, credit was or wasn't observed, reflection "
            "was stored, an appeal was filed. These are observable facts. "
            "Whether the outcomes were just is not a question the ledger answers."
        ),
        "judgment":      False,
        "credit_issued": False,
    },
    {
        "section": "Why the Ledger Does Not Issue Credit",
        "summary": (
            "credit_issued: false is a permanent invariant inherited from "
            "all prior phases. The ledger is a read-only view of what happened."
        ),
        "detail": (
            "From Phase 11 onward, credit_issued: false is a permanent protocol "
            "invariant. The ledger does not change this. Even if every ledger entry "
            "shows candidate_credit: true and appeal_recorded: true, the ledger "
            "itself does not issue credit. Credit is issued by external systems, "
            "on their own schedule, according to their own eligibility criteria. "
            "The ledger preserves this boundary by being read-only with respect "
            "to external credit state."
        ),
        "credit_issued":   False,
        "permanent":       True,
    },
    {
        "section": "Why the Ledger Does Not Force Recognition",
        "summary": (
            "The ledger has authority: none. It is an observer of recognition "
            "history, not a participant in recognition decisions."
        ),
        "detail": (
            "The authority: none invariant means the ledger cannot compel any "
            "external system to recognize a contribution. A ledger entry showing "
            "appeal_recorded: true and external_credit: false does not create an "
            "obligation for GITSEA or any other system to issue credit. "
            "The ledger makes history observable. Forcing recognition would require "
            "authority the Dan-Go protocol explicitly disclaims. "
            "Recognition remains external."
        ),
        "authority":       "none",
        "credit_issued":   False,
    },
    {
        "section": "Why Append-Only History Preserves Reopenability",
        "summary": (
            "Because the ledger never deletes or modifies entries, it can always "
            "receive new entries — including future credit observations."
        ),
        "detail": (
            "The append_only: true and reopenable: true invariants work together. "
            "Append-only means no existing ledger entry is ever changed. "
            "Reopenable means a new entry can always be appended — for example, "
            "if external credit is later issued, or if a new appeal is filed. "
            "The recognition history is never permanently closed. "
            "A contributor whose contribution was not credited today can still "
            "have a new ledger entry added tomorrow. History grows; it does not close."
        ),
        "append_only":   True,
        "reopenable":    True,
    },
]


# ── Report builder ────────────────────────────────────────────────────────────

def build_ledger_report(
    claim_id: str = "housing-007",
    issue_id: int = 3,
    ledger_entry_count: int = 2,
    candidate_count: int = 2,
    external_credit_count: int = 0,
    reflection_count: int = 2,
    appeal_count: int = 2,
    gap_count: int = 2,
    external_system: str = "gitsea",
) -> dict[str, Any]:
    """Build the Phase 15 ledger report."""
    return {
        "report_type":         "ledger_report",
        "generated_at":        datetime.now(timezone.utc).isoformat(),
        "report_id":           f"ledger-report-{claim_id}-issue-{issue_id}",

        # Claim context
        "claim_id":            claim_id,
        "issue_id":            issue_id,
        "external_system":     external_system,

        # Ledger state
        "ledger_entry_count":  ledger_entry_count,
        "candidate_count":     candidate_count,
        "external_credit_count": external_credit_count,
        "reflection_count":    reflection_count,
        "appeal_count":        appeal_count,
        "gap_count":           gap_count,

        # Report content
        "section_count":       len(LEDGER_REPORT_SECTIONS),
        "sections":            LEDGER_REPORT_SECTIONS,

        # Summary table
        "summary_table": {
            "history_exists":             True,
            "ledger_judges":              False,
            "ledger_issues_credit":       False,
            "ledger_forces_recognition":  False,
            "reopenable":                 True,
            "append_only":                True,
            "history_complete":           True,
            "recognition_remains_external": True,
        },

        # Permanent invariants
        "credit_issued":       False,
        "moves_money":         False,
        "execution_allowed":   False,
        "hard_enforcement":    False,
        "advisory":            True,
        "ledger_only":         True,
        "authority":           "none",
        "judgment":            False,
        "append_only":         True,
        "contestable":         True,
        "reopenable":          True,

        "principle_1": "Recognition history is not authority.",
        "principle_2": "Ledger is not judgment.",
        "principle_3": "Contribution becomes legible before it becomes valuable.",
    }


# ── Load helper ───────────────────────────────────────────────────────────────

def load_ledger(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ── Save ──────────────────────────────────────────────────────────────────────

def save_report(doc: dict, out_path: Path | None = None) -> Path:
    if out_path is None:
        out_path = _EXAMPLES / "ledger-report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Generate ledger report (advisory, no credit issued).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Recognition history is not authority.
Ledger is not judgment.

Examples:
  python bridge/gitsea/ledger/runtime/ledger_report.py
  python bridge/gitsea/ledger/runtime/ledger_report.py --save
  python bridge/gitsea/ledger/runtime/ledger_report.py --json
  python bridge/gitsea/ledger/runtime/ledger_report.py \\
      --input bridge/gitsea/ledger/examples/recognition-ledger.json
        """,
    )
    p.add_argument("--input", metavar="PATH",
                   help="Path to recognition-ledger.json")
    p.add_argument("--claim", default="housing-007")
    p.add_argument("--issue", type=int, default=3)
    p.add_argument("--system", default="gitsea")
    p.add_argument("--save", action="store_true",
                   help="Save to ledger/examples/ledger-report.json")
    p.add_argument("--json", action="store_true", dest="json_output")
    args = p.parse_args()

    ledger_path = (
        Path(args.input) if args.input
        else _EXAMPLES / "recognition-ledger.json"
    )
    ledger = load_ledger(ledger_path)

    doc = build_ledger_report(
        claim_id=ledger.get("claim_id", args.claim),
        issue_id=ledger.get("issue", args.issue),
        ledger_entry_count=ledger.get("entry_count", 2),
        candidate_count=ledger.get("candidate_count", 2),
        external_credit_count=ledger.get("external_credit_count", 0),
        reflection_count=ledger.get("reflection_count", 2),
        appeal_count=ledger.get("appeal_count", 2),
        gap_count=ledger.get("gap_count", 2),
        external_system=ledger.get("external_system", args.system),
    )

    if args.save:
        out = save_report(doc)
        print(f"Saved: {out}")

    if args.json_output:
        print(json.dumps(doc, indent=2, ensure_ascii=False))
        return

    # Default: human-readable
    print(f"\n{'='*60}")
    print(f"  Ledger Report: {doc['report_id']}")
    print(f"{'='*60}")
    print(f"  Claim:              {doc['claim_id']}  (issue #{doc['issue_id']})")
    print(f"  Entries:            {doc['ledger_entry_count']}  "
          f"(candidates: {doc['candidate_count']}, "
          f"credited: {doc['external_credit_count']}, "
          f"gaps: {doc['gap_count']})")
    print()
    for sec in doc["sections"]:
        print(f"  ▶  {sec['section']}")
        print(f"     {sec['summary'][:72]}")
        print()
    st = doc["summary_table"]
    print(f"  Summary table:")
    print(f"    History exists:              {st['history_exists']}")
    print(f"    Ledger judges:               {st['ledger_judges']}")
    print(f"    Ledger issues credit:        {st['ledger_issues_credit']}")
    print(f"    Ledger forces recognition:   {st['ledger_forces_recognition']}")
    print(f"    Reopenable:                  {st['reopenable']}")
    print(f"    Append-only:                 {st['append_only']}")
    print(f"    History complete:            {st['history_complete']}")
    print(f"    Recognition remains external:{st['recognition_remains_external']}")
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
