"""
recognition_ledger.py — Recognition Ledger (Advisory, Append-Only)

Creates a combined recognition history across Phases 11–14, linking
all contribution, observation, reflection, and appeal records into
one coherent advisory ledger per claim.

The recognition ledger is the authoritative append-only record of
what occurred in the full contribution → recognition lifecycle for
a given claim and contributor set. It does not judge. It does not
issue credit. It does not create authority.

This file does NOT:
  - Issue credit
  - Judge contributors or contributions
  - Create authority over external systems
  - Score or rank participants
  - Move funds
  - Perform wallet operations
  - Call any API

Core principles:
  "Recognition history is not authority."
  "Ledger is not judgment."

No secrets. No private keys. No wallet operations. No network. stdlib only.

Usage:
    python bridge/gitsea/ledger/runtime/recognition_ledger.py
    python bridge/gitsea/ledger/runtime/recognition_ledger.py --save
    python bridge/gitsea/ledger/runtime/recognition_ledger.py --json
    python bridge/gitsea/ledger/runtime/recognition_ledger.py \\
        --ledger-id recognition-ledger-001 --claim housing-007 --issue 3
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_FILE_DIR        = Path(__file__).parent
_LEDGER          = _FILE_DIR.parent
_EXAMPLES        = _LEDGER / "examples"
_REPO_ROOT       = _LEDGER.parent.parent.parent
_CREDIT_EXAMPLES = _REPO_ROOT / "bridge" / "gitsea" / "credit" / "examples"
_EXT_EXAMPLES    = _REPO_ROOT / "bridge" / "gitsea" / "external_credit" / "examples"
_REF_EXAMPLES    = _REPO_ROOT / "bridge" / "gitsea" / "reflection" / "examples"
_APP_EXAMPLES    = _REPO_ROOT / "bridge" / "gitsea" / "appeal" / "examples"


# ── Ledger builder ────────────────────────────────────────────────────────────

def build_recognition_ledger(
    ledger_id: str,
    claim_id: str,
    issue_id: int,
    contributors: list[dict[str, Any]],
    external_system: str = "gitsea",
) -> dict[str, Any]:
    """
    Build a recognition ledger for a claim.

    Links Phase 11–14 records into one combined recognition history.
    Each contributor gets one ledger entry covering all four phases.

    Parameters
    ----------
    ledger_id : str
        Unique ledger identifier.
    claim_id : str
        Dan-Go claim identifier.
    issue_id : int
        GitHub issue number.
    contributors : list[dict]
        List of contributor records with Phase 11–14 state.
    external_system : str
        External system identifier.
    """
    entries = []
    for c in contributors:
        cid   = c["contributor_id"]
        entry = {
            "contributor":           cid,
            "contribution_type":     c.get("contribution_type", ""),
            "contribution_label":    c.get("contribution_label", ""),
            "candidate_credit":      c.get("candidate_credit", False),   # Phase 11
            "external_credit":       c.get("external_credit", False),    # Phase 12
            "reflection_recorded":   c.get("reflection_recorded", True), # Phase 13
            "appeal_recorded":       c.get("appeal_recorded", True),     # Phase 14
            "recognition_history_complete": True,
            "authority":             "none",
            "judgment":              False,
        }
        entries.append(entry)

    credited = [e for e in entries if e["external_credit"]]
    with_gaps = [e for e in entries if e["candidate_credit"] and not e["external_credit"]]

    return {
        "ledger_type":               "recognition_ledger",
        "generated_at":              datetime.now(timezone.utc).isoformat(),
        "ledger_id":                 ledger_id,

        # Claim identity
        "claim_id":                  claim_id,
        "issue":                     issue_id,
        "external_system":           external_system,

        # Ledger entries
        "entry_count":               len(entries),
        "entries":                   entries,

        # Summary counts
        "candidate_count":           sum(1 for e in entries if e["candidate_credit"]),
        "external_credit_count":     len(credited),
        "reflection_count":          sum(1 for e in entries if e["reflection_recorded"]),
        "appeal_count":              sum(1 for e in entries if e["appeal_recorded"]),
        "gap_count":                 len(with_gaps),

        # Ledger completeness
        "recognition_history_complete": all(
            e["recognition_history_complete"] for e in entries
        ),

        # What the ledger does NOT do
        "ledger_issues_credit":      False,   # invariant
        "ledger_judges":             False,   # invariant
        "ledger_ranks":              False,   # invariant
        "ledger_creates_authority":  False,   # invariant

        # Permanent invariants
        "credit_issued":             False,
        "moves_money":               False,
        "execution_allowed":         False,
        "hard_enforcement":          False,
        "advisory":                  True,
        "ledger_only":               True,
        "authority":                 "none",
        "judgment":                  False,
        "append_only":               True,
        "contestable":               True,
        "reopenable":                True,

        "principle_1": "Recognition history is not authority.",
        "principle_2": "Ledger is not judgment.",
        "ledger_note": (
            "This ledger links Phase 11–14 records into one recognition history. "
            "It is append-only, advisory, and carries no authority. "
            "History being complete does not mean recognition is complete — "
            "recognition remains external."
        ),
    }


# ── Default ledger ────────────────────────────────────────────────────────────

DEFAULT_CONTRIBUTORS = [
    {
        "contributor_id":    "external-001",
        "contribution_type": "evidence_reviewed",
        "contribution_label": "Evidence reviewed and approved",
        "candidate_credit":  True,
        "external_credit":   False,
        "reflection_recorded": True,
        "appeal_recorded":   True,
    },
    {
        "contributor_id":    "external-002",
        "contribution_type": "evidence_accepted",
        "contribution_label": "Evidence accepted via PR merge",
        "candidate_credit":  True,
        "external_credit":   False,
        "reflection_recorded": True,
        "appeal_recorded":   True,
    },
    {
        "contributor_id":    "external-003",
        "contribution_type": "contest_raised",
        "contribution_label": "Legitimate contest raised",
        "candidate_credit":  False,
        "external_credit":   False,
        "reflection_recorded": True,
        "appeal_recorded":   False,
    },
]


# ── Load helpers ──────────────────────────────────────────────────────────────

def load_phase11_contributors(path: Path) -> list[dict]:
    """Load contributor list from Phase 11 credit-candidate-snapshot."""
    if not path.exists():
        return DEFAULT_CONTRIBUTORS
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    # Extract contributor IDs; fill defaults for other phases
    raw_ids = doc.get("contributors", [])
    if not raw_ids:
        return DEFAULT_CONTRIBUTORS
    return [
        {
            "contributor_id":    cid,
            "contribution_type": "unknown",
            "candidate_credit":  True,
            "external_credit":   False,
            "reflection_recorded": True,
            "appeal_recorded":   True,
        }
        for cid in raw_ids
    ]


# ── Save ──────────────────────────────────────────────────────────────────────

def save_ledger(doc: dict, out_path: Path | None = None) -> Path:
    if out_path is None:
        out_path = _EXAMPLES / "recognition-ledger.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Build recognition ledger linking Phases 11–14 (no credit issued).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Recognition history is not authority.
Ledger is not judgment.

Examples:
  python bridge/gitsea/ledger/runtime/recognition_ledger.py
  python bridge/gitsea/ledger/runtime/recognition_ledger.py --save
  python bridge/gitsea/ledger/runtime/recognition_ledger.py --json
  python bridge/gitsea/ledger/runtime/recognition_ledger.py \\
      --ledger-id recognition-ledger-001 --claim housing-007 --issue 3
        """,
    )
    p.add_argument("--ledger-id", default="recognition-ledger-001")
    p.add_argument("--claim", default="housing-007")
    p.add_argument("--issue", type=int, default=3)
    p.add_argument("--input", metavar="PATH",
                   help="Path to credit-candidate-snapshot.json from Phase 11")
    p.add_argument("--save", action="store_true",
                   help="Save to ledger/examples/recognition-ledger.json")
    p.add_argument("--json", action="store_true", dest="json_output")
    args = p.parse_args()

    if args.input:
        contributors = load_phase11_contributors(Path(args.input))
    else:
        p11_path = _CREDIT_EXAMPLES / "credit-candidate-snapshot.json"
        contributors = load_phase11_contributors(p11_path)
        if not contributors or contributors == DEFAULT_CONTRIBUTORS:
            contributors = DEFAULT_CONTRIBUTORS

    doc = build_recognition_ledger(
        ledger_id=args.ledger_id,
        claim_id=args.claim,
        issue_id=args.issue,
        contributors=contributors,
    )

    if args.save:
        out = save_ledger(doc)
        print(f"Saved: {out}")

    if args.json_output:
        print(json.dumps(doc, indent=2, ensure_ascii=False))
        return

    # Default: human-readable
    print(f"\n{'='*60}")
    print(f"  Recognition Ledger: {doc['ledger_id']}")
    print(f"{'='*60}")
    print(f"  Claim:                  {doc['claim_id']}  (issue #{doc['issue']})")
    print(f"  External system:        {doc['external_system']}")
    print()
    print(f"  Entries:                {doc['entry_count']}")
    print(f"  Candidates:             {doc['candidate_count']}")
    print(f"  Externally credited:    {doc['external_credit_count']}")
    print(f"  Reflections recorded:   {doc['reflection_count']}")
    print(f"  Appeals recorded:       {doc['appeal_count']}")
    print(f"  Gaps present:           {doc['gap_count']}")
    print(f"  History complete:       {doc['recognition_history_complete']}")
    print()
    for e in doc["entries"]:
        mark = "✓" if e["external_credit"] else ("△" if e["candidate_credit"] else "○")
        print(f"  {mark}  [{e['contributor']}]  {e['contribution_label']}")
        print(f"       candidate={e['candidate_credit']}  "
              f"external={e['external_credit']}  "
              f"reflected={e['reflection_recorded']}  "
              f"appealed={e['appeal_recorded']}")
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
