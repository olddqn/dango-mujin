"""
recognition_appeal.py — Recognition Appeal Record (Advisory, Append-Only)

Records that a contributor, agent, or observer has requested reconsideration
of a contribution that was not externally credited. The appeal is advisory.
It does not compel any external system to act.

An appeal record:
  - Names the contributor requesting reconsideration
  - References the unrecognized contribution from Phase 13
  - States the grounds for the appeal (optional, free-form)
  - Records the appeal as append-only advisory memory

This file does NOT:
  - Force GITSEA to issue credit
  - Create an enforceable claim against any party
  - Modify external credit state
  - Contact any external system
  - Move funds
  - Perform wallet operations

Core principles:
  "Appeal is not enforcement."
  "Recognition remains external."

All appeal records are advisory. All appeal records are append-only.
credit_issued is always False. hard_enforcement is always False.

No secrets. No private keys. No wallet operations. No network. stdlib only.

Usage:
    python bridge/gitsea/appeal/runtime/recognition_appeal.py
    python bridge/gitsea/appeal/runtime/recognition_appeal.py --save
    python bridge/gitsea/appeal/runtime/recognition_appeal.py --json
    python bridge/gitsea/appeal/runtime/recognition_appeal.py \\
        --contributor external-001 --claim housing-007 --issue 1 \\
        --type evidence_reviewed
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_FILE_DIR = Path(__file__).parent
_APPEAL   = _FILE_DIR.parent
_EXAMPLES = _APPEAL / "examples"

# ── Appeal grounds ────────────────────────────────────────────────────────────

APPEAL_GROUNDS = {
    "evidence_complete":
        "Evidence submitted was complete and accepted in Dan-Go negotiation.",
    "review_completed":
        "Review was performed and recorded as credit-eligible in Phase 11.",
    "contested_in_good_faith":
        "Contest was raised in good faith and recorded in negotiation history.",
    "reaffirmation_provided":
        "Reaffirmation with new context was submitted and accepted.",
    "correction_proposed":
        "Plan correction was proposed within the negotiation protocol.",
    "general_reconsideration":
        "Requesting general reconsideration of unrecognized contribution.",
}


# ── Appeal builder ────────────────────────────────────────────────────────────

def build_recognition_appeal(
    contributor_id: str,
    claim_id: str,
    issue_id: int,
    contribution_type: str,
    contribution_label: str = "",
    appeal_grounds_key: str = "general_reconsideration",
    appeal_note: str | None = None,
    external_system: str = "gitsea",
    pr_id: int | str | None = None,
) -> dict[str, Any]:
    """
    Build an advisory recognition appeal record.

    Records that a contributor requests reconsideration of an unrecognized
    contribution. The appeal does not compel any action.

    Parameters
    ----------
    contributor_id : str
        Pseudonymous contributor identifier.
    claim_id : str
        Dan-Go claim identifier.
    issue_id : int
        GitHub issue number.
    contribution_type : str
        Type of contribution (from Phase 11 CONTRIBUTION_TYPES).
    contribution_label : str
        Human-readable label for the contribution type.
    appeal_grounds_key : str
        Key into APPEAL_GROUNDS for the stated appeal grounds.
    appeal_note : str | None
        Optional free-form note from the appellant.
    external_system : str
        External system being appealed to (advisory reference only).
    pr_id : int | str | None
        GitHub PR number, if applicable.
    """
    if appeal_grounds_key not in APPEAL_GROUNDS:
        raise ValueError(
            f"Unknown appeal_grounds_key {appeal_grounds_key!r}. "
            f"Valid: {list(APPEAL_GROUNDS)}"
        )
    grounds_text = APPEAL_GROUNDS[appeal_grounds_key]

    return {
        "appeal_type":        "recognition_appeal",
        "generated_at":       datetime.now(timezone.utc).isoformat(),
        "appeal_id":          (
            f"appeal-{claim_id}-issue-{issue_id}-{contributor_id}"
        ),

        # Appellant
        "contributor_id":     contributor_id,
        "appeal_by":          contributor_id,

        # Contribution reference (from Phase 11/13)
        "claim_id":           claim_id,
        "issue_id":           issue_id,
        "pr_id":              pr_id,
        "contribution_type":  contribution_type,
        "contribution_label": contribution_label or contribution_type,

        # Appeal content
        "appeal_grounds_key": appeal_grounds_key,
        "appeal_grounds":     grounds_text,
        "appeal_note":        appeal_note or "",
        "appeal_to":          external_system,

        # What the appeal is and isn't
        "appeal_is_enforceable":   False,   # invariant
        "appeal_compels_credit":   False,   # invariant
        "appeal_modifies_external": False,  # invariant
        "appeal_creates_authority": False,  # invariant
        "appeal_explanation": (
            f"This appeal requests that {external_system} reconsider the "
            f"contribution by {contributor_id} for claim {claim_id} issue #{issue_id}. "
            "The appeal is advisory. It does not compel any external system to act. "
            "Recognition remains external. Dan-Go records the appeal; "
            f"{external_system} decides independently."
        ),

        # Permanent invariants
        "credit_issued":      False,
        "moves_money":        False,
        "execution_allowed":  False,
        "hard_enforcement":   False,
        "advisory":           True,
        "appeal_only":        True,
        "authority":          "none",
        "append_only":        True,
        "contestable":        True,
        "reopenable":         True,

        "principle_1": "Appeal is not enforcement.",
        "principle_2": "Recognition remains external.",
    }


# ── Default appeals ───────────────────────────────────────────────────────────

DEFAULT_APPEALS = [
    {
        "contributor_id":    "external-001",
        "claim_id":          "housing-007",
        "issue_id":          1,
        "pr_id":             1,
        "contribution_type": "evidence_reviewed",
        "contribution_label": "Evidence reviewed and approved",
        "appeal_grounds_key": "review_completed",
    },
    {
        "contributor_id":    "external-002",
        "claim_id":          "housing-007",
        "issue_id":          1,
        "pr_id":             1,
        "contribution_type": "evidence_accepted",
        "contribution_label": "Evidence accepted via PR merge",
        "appeal_grounds_key": "evidence_complete",
    },
]


def build_appeals_list(
    raw_appeals: list[dict] | None = None,
) -> dict[str, Any]:
    """Build an aggregated list of recognition appeal records."""
    raws = raw_appeals if raw_appeals is not None else DEFAULT_APPEALS
    appeals = [
        build_recognition_appeal(
            contributor_id=r["contributor_id"],
            claim_id=r["claim_id"],
            issue_id=r["issue_id"],
            contribution_type=r["contribution_type"],
            contribution_label=r.get("contribution_label", ""),
            appeal_grounds_key=r.get("appeal_grounds_key", "general_reconsideration"),
            pr_id=r.get("pr_id"),
        )
        for r in raws
    ]
    return {
        "list_type":          "recognition_appeal_list",
        "generated_at":       datetime.now(timezone.utc).isoformat(),
        "total_appeals":      len(appeals),
        "appeals":            appeals,

        "list_note": (
            f"{len(appeals)} advisory recognition appeal(s) recorded. "
            "No appeal compels credit issuance. Recognition remains external."
        ),

        # Invariants
        "credit_issued":      False,
        "moves_money":        False,
        "execution_allowed":  False,
        "hard_enforcement":   False,
        "advisory":           True,
        "appeal_only":        True,
        "authority":          "none",
        "append_only":        True,

        "principle_1": "Appeal is not enforcement.",
        "principle_2": "Recognition remains external.",
    }


# ── Save ──────────────────────────────────────────────────────────────────────

def save_appeal(doc: dict, out_path: Path | None = None) -> Path:
    if out_path is None:
        out_path = _EXAMPLES / "recognition-appeal.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Record advisory recognition appeal (no credit issued).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Appeal is not enforcement.
Recognition remains external.
Dan-Go records appeals; external systems decide independently.

Appeal grounds:
  evidence_complete      review_completed       contested_in_good_faith
  reaffirmation_provided correction_proposed    general_reconsideration

Examples:
  python bridge/gitsea/appeal/runtime/recognition_appeal.py
  python bridge/gitsea/appeal/runtime/recognition_appeal.py --save
  python bridge/gitsea/appeal/runtime/recognition_appeal.py --json
  python bridge/gitsea/appeal/runtime/recognition_appeal.py \\
      --contributor external-001 --claim housing-007 --issue 1 \\
      --type evidence_reviewed --grounds review_completed
        """,
    )
    p.add_argument("--contributor", default=None)
    p.add_argument("--claim", default=None)
    p.add_argument("--issue", type=int, default=None)
    p.add_argument("--type", default=None, dest="ctype")
    p.add_argument("--grounds", default="general_reconsideration",
                   choices=list(APPEAL_GROUNDS))
    p.add_argument("--note", default=None, help="Optional appeal note")
    p.add_argument("--pr", default=None)
    p.add_argument("--save", action="store_true",
                   help="Save to appeal/examples/recognition-appeal.json")
    p.add_argument("--json", action="store_true", dest="json_output")
    args = p.parse_args()

    if args.contributor and args.claim and args.issue and args.ctype:
        try:
            doc = build_recognition_appeal(
                contributor_id=args.contributor,
                claim_id=args.claim,
                issue_id=args.issue,
                contribution_type=args.ctype,
                appeal_grounds_key=args.grounds,
                appeal_note=args.note,
                pr_id=args.pr,
            )
        except ValueError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        doc = build_appeals_list()

    if args.save:
        out = save_appeal(doc)
        print(f"Saved: {out}")

    if args.json_output:
        print(json.dumps(doc, indent=2, ensure_ascii=False))
        return

    # Default: human-readable
    print(f"\n{'='*60}")
    print(f"  Recognition Appeals")
    print(f"{'='*60}")

    if "appeals" in doc:
        print(f"  Total appeals: {doc['total_appeals']}")
        print()
        for a in doc["appeals"]:
            print(f"  ↑  [{a['contributor_id']}]  {a['contribution_label']}")
            print(f"       claim: {a['claim_id']}  issue: #{a['issue_id']}")
            print(f"       grounds: {a['appeal_grounds_key']}")
            print(f"       enforceable={a['appeal_is_enforceable']}  "
                  f"compels_credit={a['appeal_compels_credit']}")
    else:
        print(f"  Appeal ID:       {doc['appeal_id']}")
        print(f"  Appellant:       {doc['contributor_id']}")
        print(f"  Contribution:    {doc['contribution_label']}")
        print(f"  Grounds:         {doc['appeal_grounds'][:60]}...")
        print(f"  Enforceable:     {doc['appeal_is_enforceable']}")
        print(f"  Compels credit:  {doc['appeal_compels_credit']}")

    print(f"\n  credit_issued:       {doc.get('credit_issued', False)}")
    print(f"  appeal_only:         {doc.get('appeal_only', True)}")
    print(f"  hard_enforcement:    {doc.get('hard_enforcement', False)}")
    print(f"  moves_money:         {doc.get('moves_money', False)}")
    print(f"  advisory:            {doc.get('advisory', True)}")
    print(f"  authority:           {doc.get('authority', 'none')}")
    print(f"\n  \"{doc.get('principle_1', '')}\"")
    print(f"  \"{doc.get('principle_2', '')}\"")
    print()


if __name__ == "__main__":
    main()
