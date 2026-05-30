"""
credit_candidate_snapshot.py — Credit Candidate Snapshot (Advisory)

Aggregates contribution candidates into a single advisory snapshot record
for GITSEA credit observability.

A credit candidate snapshot records:
  - Total number of contribution candidates observed
  - How many are credit-eligible (candidate_credit: true)
  - Whether any credit has been issued (always: false — Dan-Go never issues credit)
  - The external system that may observe credit eligibility (gitsea)

This file does NOT:
  - Issue credit
  - Allocate rewards
  - Trigger GITSEA streams
  - Move funds
  - Call external APIs
  - Score contributors for payouts

All snapshots are advisory. `credit_issued: false` is a permanent invariant.

Contribution history is not credit.
Dan-Go records contribution candidates; external systems may issue credit.

No secrets. No private keys. No wallet operations. No network. stdlib only.

Usage:
    python bridge/gitsea/credit/runtime/credit_candidate_snapshot.py
    python bridge/gitsea/credit/runtime/credit_candidate_snapshot.py --save
    python bridge/gitsea/credit/runtime/credit_candidate_snapshot.py --json
    python bridge/gitsea/credit/runtime/credit_candidate_snapshot.py \\
        --input bridge/gitsea/credit/examples/contribution-candidate.json
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
_REPO_ROOT   = _CREDIT.parent.parent.parent


# ── Snapshot builder ──────────────────────────────────────────────────────────

def build_credit_candidate_snapshot(
    candidates: list[dict[str, Any]],
    claim_id: str = "housing-007",
    issue_id: int = 1,
    source: str = "contribution_candidate.py",
) -> dict[str, Any]:
    """
    Build an advisory credit candidate snapshot.

    Aggregates a list of contribution candidate records into a single
    summary snapshot. credit_issued is always False.

    Parameters
    ----------
    candidates : list[dict]
        List of contribution candidate records (from build_contribution_candidate).
    claim_id : str
        Dan-Go claim identifier.
    issue_id : int
        GitHub issue number.
    source : str
        Source module that generated the candidates.
    """
    credit_eligible = [c for c in candidates if c.get("candidate_credit", False)]
    contributor_ids = list({c.get("contributor_id", "") for c in candidates})
    contribution_types = list({c.get("contribution_type", "") for c in candidates})

    return {
        "snapshot_type":     "credit_candidate_snapshot",
        "generated_at":      datetime.now(timezone.utc).isoformat(),
        "snapshot_id":       f"snapshot-{claim_id}-issue-{issue_id}",

        # Source
        "claim_id":          claim_id,
        "issue_id":          issue_id,
        "source":            source,

        # Aggregate counts
        "candidate_count":   len(candidates),
        "credit_eligible":   len(credit_eligible),
        "contributor_count": len(contributor_ids),
        "contributors":      sorted(contributor_ids),
        "contribution_types": sorted(contribution_types),

        # Credit status (permanent)
        "credit_issued":     False,   # permanent invariant — never changed by Dan-Go
        "external_system":   "gitsea",
        "credit_note": (
            "GITSEA may observe this snapshot when assessing stream credit. "
            "Dan-Go does not activate or confirm credit. "
            "Dan-Go records contribution candidates; external systems may issue credit."
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


# ── Load from prior phase output ──────────────────────────────────────────────

def load_candidates_from_file(path: Path) -> list[dict[str, Any]]:
    """Load contribution candidates from a previously saved JSON file."""
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    # Handles both single candidate and list format
    if "candidates" in doc:
        return doc["candidates"]
    if doc.get("candidate_type") == "contribution_candidate":
        return [doc]
    return []


def default_candidates() -> list[dict[str, Any]]:
    """Return a minimal default candidate list for demo/stub purposes."""
    from contribution_candidate import build_candidates_list  # type: ignore[import]
    doc = build_candidates_list()
    return doc["candidates"]


# ── Save ──────────────────────────────────────────────────────────────────────

def save_snapshot(doc: dict, out_path: Path | None = None) -> Path:
    if out_path is None:
        out_path = _EXAMPLES / "credit-candidate-snapshot.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Generate an advisory credit candidate snapshot (no credit issued).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contribution history is not credit.
Dan-Go records contribution candidates; external systems may issue credit.

Examples:
  python bridge/gitsea/credit/runtime/credit_candidate_snapshot.py
  python bridge/gitsea/credit/runtime/credit_candidate_snapshot.py --save
  python bridge/gitsea/credit/runtime/credit_candidate_snapshot.py --json
  python bridge/gitsea/credit/runtime/credit_candidate_snapshot.py \\
      --input bridge/gitsea/credit/examples/contribution-candidate.json
        """,
    )
    p.add_argument("--input", metavar="PATH",
                   help="Path to contribution-candidate.json (from contribution_candidate.py)")
    p.add_argument("--claim", default="housing-007")
    p.add_argument("--issue", type=int, default=1)
    p.add_argument("--save", action="store_true",
                   help="Save to credit/examples/credit-candidate-snapshot.json")
    p.add_argument("--json", action="store_true", dest="json_output")
    args = p.parse_args()

    # Load candidates
    if args.input:
        candidates = load_candidates_from_file(Path(args.input))
        if not candidates:
            print(f"WARNING: No candidates found in {args.input}", file=sys.stderr)
    else:
        # Try the default examples path
        default_path = _EXAMPLES / "contribution-candidate.json"
        candidates = load_candidates_from_file(default_path)
        if not candidates:
            # Fall back to inline defaults
            candidates = [
                {
                    "candidate_type":    "contribution_candidate",
                    "claim_id":          args.claim,
                    "issue_id":          args.issue,
                    "pr_id":             1,
                    "contributor_id":    "external-001",
                    "contribution_type": "evidence_reviewed",
                    "contribution_label": "Evidence reviewed and approved",
                    "evidence_accepted": True,
                    "candidate_credit":  True,
                    "credit_issued":     False,
                    "external_system":   "gitsea",
                    "moves_money":       False,
                    "execution_allowed": False,
                    "advisory":          True,
                    "authority":         "none",
                    "contribution_note": "Contribution history is not credit.",
                },
            ]

    doc = build_credit_candidate_snapshot(
        candidates=candidates,
        claim_id=args.claim,
        issue_id=args.issue,
    )

    if args.save:
        out = save_snapshot(doc)
        print(f"Saved: {out}")

    if args.json_output:
        print(json.dumps(doc, indent=2, ensure_ascii=False))
        return

    # Default: human-readable
    print(f"\n{'='*58}")
    print(f"  Credit Candidate Snapshot")
    print(f"{'='*58}")
    print(f"  Snapshot ID:     {doc['snapshot_id']}")
    print(f"  Claim:           {doc['claim_id']}  (issue #{doc['issue_id']})")
    print(f"  Candidates:      {doc['candidate_count']}")
    print(f"  Credit eligible: {doc['credit_eligible']}  (candidate status only)")
    print(f"  Contributors:    {', '.join(doc['contributors'])}")
    print(f"  Types:           {', '.join(doc['contribution_types'])}")
    print()
    print(f"  credit_issued:       {doc['credit_issued']}  (permanent: never by Dan-Go)")
    print(f"  external_system:     {doc['external_system']}")
    print(f"  moves_money:         {doc['moves_money']}")
    print(f"  execution_allowed:   {doc['execution_allowed']}")
    print(f"  advisory:            {doc['advisory']}")
    print(f"  authority:           {doc['authority']}")
    print(f"\n  \"{doc['contribution_note']}\"")
    print()


if __name__ == "__main__":
    main()
