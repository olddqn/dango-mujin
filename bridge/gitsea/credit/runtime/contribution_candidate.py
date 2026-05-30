"""
contribution_candidate.py — Contribution Credit Candidates (Advisory)

Records individual contribution events that are candidates for credit
consideration by external systems (e.g. GITSEA).

A contribution candidate records:
  - Which issue and PR the contribution belongs to
  - Which contributor made it
  - Whether it passed negotiation review (evidence accepted)
  - Whether credit has been issued (always: false — Dan-Go never issues credit)

Contribution history is not credit.
Dan-Go records contribution candidates; external systems may issue credit.

This file does NOT:
  - Issue credit
  - Allocate rewards
  - Trigger GITSEA streams
  - Move funds
  - Call external APIs

All candidates are advisory. `credit_issued: false` is a permanent invariant.

No secrets. No private keys. No wallet operations. No network. stdlib only.

Usage:
    python bridge/gitsea/credit/runtime/contribution_candidate.py
    python bridge/gitsea/credit/runtime/contribution_candidate.py --save
    python bridge/gitsea/credit/runtime/contribution_candidate.py --json
    python bridge/gitsea/credit/runtime/contribution_candidate.py \\
        --issue 1 --pr 1 --contributor external-001 --role reviewer
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
_GL_EXAMPLES = _REPO_ROOT / "bridge" / "gitlawb" / "examples"


# ── Candidate types ───────────────────────────────────────────────────────────

CONTRIBUTION_TYPES = {
    "evidence_submitted":  "Evidence submitted via PR",
    "evidence_reviewed":   "Evidence reviewed and approved",
    "evidence_accepted":   "Evidence accepted via PR merge",
    "contest_raised":      "Legitimate contest raised",
    "reaffirm_submitted":  "Reaffirmation submitted with new context",
    "plan_correction":     "Plan correction proposed",
}


# ── Candidate builder ─────────────────────────────────────────────────────────

def build_contribution_candidate(
    issue_id: int,
    pr_id: int | str,
    contributor_id: str,
    contribution_type: str,
    claim_id: str = "housing-007",
    condition: str = "space_safety_assessed",
    evidence_accepted: bool = True,
) -> dict[str, Any]:
    """
    Build an advisory contribution candidate record.

    credit_issued is always False — Dan-Go never issues credit.
    candidate_credit indicates this contribution is a candidate
    for external credit consideration.
    """
    if contribution_type not in CONTRIBUTION_TYPES:
        raise ValueError(
            f"Unknown contribution_type {contribution_type!r}. "
            f"Valid: {list(CONTRIBUTION_TYPES)}"
        )

    # A candidate is credit-eligible if evidence was accepted
    # and the contribution type represents completed work
    completed_types = {
        "evidence_accepted", "evidence_reviewed",
        "reaffirm_submitted", "plan_correction",
    }
    candidate_credit = evidence_accepted and contribution_type in completed_types

    return {
        "candidate_type":      "contribution_candidate",
        "generated_at":        datetime.now(timezone.utc).isoformat(),

        # Source
        "claim_id":            claim_id,
        "condition":           condition,
        "issue_id":            issue_id,
        "pr_id":               pr_id,

        # Contributor
        "contributor_id":      contributor_id,
        "contribution_type":   contribution_type,
        "contribution_label":  CONTRIBUTION_TYPES[contribution_type],

        # Candidate status
        "evidence_accepted":   evidence_accepted,
        "candidate_credit":    candidate_credit,
        "credit_issued":       False,   # permanent invariant — never changed by Dan-Go
        "external_system":     "gitsea",
        "external_credit_note": (
            "GITSEA may observe this candidate when assessing stream credit. "
            "Dan-Go does not activate or confirm credit. "
            "Dan-Go records contribution candidates; external systems may issue credit."
        ),

        # Invariants
        "moves_money":         False,
        "execution_allowed":   False,
        "hard_enforcement":    False,
        "advisory":            True,
        "authority":           "none",
        "append_only":         True,
        "contestable":         True,
        "reopenable":          True,

        "contribution_note":   "Contribution history is not credit.",
    }


# ── Default examples ──────────────────────────────────────────────────────────

DEFAULT_CANDIDATES: list[dict[str, Any]] = [
    {
        "issue_id":         1,
        "pr_id":            1,
        "contributor_id":   "external-001",
        "contribution_type": "evidence_reviewed",
        "evidence_accepted": True,
    },
    {
        "issue_id":         1,
        "pr_id":            1,
        "contributor_id":   "external-002",
        "contribution_type": "evidence_accepted",
        "evidence_accepted": True,
    },
    {
        "issue_id":         1,
        "pr_id":            1,
        "contributor_id":   "external-003",
        "contribution_type": "contest_raised",
        "evidence_accepted": True,
    },
]


def build_candidates_list(
    raw_candidates: list[dict] | None = None,
) -> dict[str, Any]:
    """Build an aggregated list of contribution candidates."""
    raws = raw_candidates if raw_candidates is not None else DEFAULT_CANDIDATES
    candidates = [
        build_contribution_candidate(
            issue_id=r["issue_id"],
            pr_id=r["pr_id"],
            contributor_id=r["contributor_id"],
            contribution_type=r["contribution_type"],
            evidence_accepted=r.get("evidence_accepted", True),
        )
        for r in raws
    ]
    credit_eligible = [c for c in candidates if c["candidate_credit"]]
    return {
        "list_type":           "contribution_candidate_list",
        "generated_at":        datetime.now(timezone.utc).isoformat(),
        "total_candidates":    len(candidates),
        "credit_eligible":     len(credit_eligible),
        "candidates":          candidates,

        # Invariants
        "credit_issued":       False,
        "moves_money":         False,
        "execution_allowed":   False,
        "hard_enforcement":    False,
        "advisory":            True,
        "authority":           "none",
        "append_only":         True,

        "contribution_note":   "Contribution history is not credit.",
        "credit_note": (
            "Dan-Go records contribution candidates; "
            "external systems may issue credit."
        ),
    }


# ── Save ──────────────────────────────────────────────────────────────────────

def save_candidates(doc: dict, out_path: Path | None = None) -> Path:
    if out_path is None:
        out_path = _EXAMPLES / "contribution-candidate.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Record contribution credit candidates (advisory, no credit issued).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contribution history is not credit.
Dan-Go records contribution candidates; external systems may issue credit.

Contribution types:
  evidence_submitted  evidence_reviewed  evidence_accepted
  contest_raised      reaffirm_submitted plan_correction

Examples:
  python bridge/gitsea/credit/runtime/contribution_candidate.py
  python bridge/gitsea/credit/runtime/contribution_candidate.py --save
  python bridge/gitsea/credit/runtime/contribution_candidate.py --json
  python bridge/gitsea/credit/runtime/contribution_candidate.py \\
      --issue 1 --pr 1 --contributor external-001 --role evidence_reviewed
        """,
    )
    p.add_argument("--issue", type=int, default=None)
    p.add_argument("--pr", default=None)
    p.add_argument("--contributor", default=None)
    p.add_argument("--role", default=None, dest="ctype",
                   choices=list(CONTRIBUTION_TYPES))
    p.add_argument("--save", action="store_true",
                   help="Save to credit/examples/contribution-candidate.json")
    p.add_argument("--json", action="store_true", dest="json_output")
    args = p.parse_args()

    if args.issue and args.pr and args.contributor and args.ctype:
        # Single candidate mode
        try:
            doc = build_contribution_candidate(
                issue_id=args.issue,
                pr_id=args.pr,
                contributor_id=args.contributor,
                contribution_type=args.ctype,
            )
        except ValueError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Default: full candidates list
        doc = build_candidates_list()

    if args.save:
        out = save_candidates(doc)
        print(f"Saved: {out}")

    if args.json_output:
        print(json.dumps(doc, indent=2, ensure_ascii=False))
        return

    # Default: human-readable
    print(f"\n{'='*58}")
    print(f"  Contribution Candidates")
    print(f"{'='*58}")

    if "candidates" in doc:
        print(f"  Total:          {doc['total_candidates']}")
        print(f"  Credit eligible:{doc['credit_eligible']}  (candidate status only)")
        print(f"  Credit issued:  {doc['credit_issued']}  (permanent: never by Dan-Go)")
        print()
        for c in doc["candidates"]:
            mark = "✓" if c["candidate_credit"] else "○"
            print(f"  {mark}  [{c['contributor_id']}]  {c['contribution_label']}")
            print(f"       issue #{c['issue_id']}  pr {c['pr_id']}  "
                  f"accepted={c['evidence_accepted']}")
    else:
        print(f"  Contributor:    {doc.get('contributor_id')}")
        print(f"  Type:           {doc.get('contribution_label')}")
        print(f"  Candidate:      {doc.get('candidate_credit')}")
        print(f"  Credit issued:  {doc.get('credit_issued')}")

    print(f"\n  moves_money:        {doc.get('moves_money', False)}")
    print(f"  execution_allowed:  {doc.get('execution_allowed', False)}")
    print(f"  advisory:           {doc.get('advisory', True)}")
    print(f"\n  \"{doc.get('contribution_note', '')}\"")
    print()


if __name__ == "__main__":
    main()
