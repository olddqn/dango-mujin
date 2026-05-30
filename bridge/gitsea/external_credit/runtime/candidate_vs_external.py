"""
candidate_vs_external.py — Candidate vs External Credit Comparison (Advisory)

Compares Dan-Go contribution candidates against observed external credit
outcomes. Makes the gap between candidate credit and external credit explicit.

A comparison record answers:
  - Does a Dan-Go candidate exist?
  - Is external credit visible?
  - Are they equivalent? (almost never — by design)
  - What is the observed relationship?

This file does NOT:
  - Issue credit
  - Resolve the gap between candidates and external credit
  - Push candidates to external systems
  - Request credit issuance
  - Modify any external state

The gap between candidate credit and external credit is not an error.
External systems are sovereign. Dan-Go observes; it does not decide.

Core principles:
  "Observation is not issuance."
  "Candidate credit is not external credit."

No secrets. No private keys. No wallet operations. No network. stdlib only.

Usage:
    python bridge/gitsea/external_credit/runtime/candidate_vs_external.py
    python bridge/gitsea/external_credit/runtime/candidate_vs_external.py --save
    python bridge/gitsea/external_credit/runtime/candidate_vs_external.py --json
    python bridge/gitsea/external_credit/runtime/candidate_vs_external.py \\
        --claim housing-007 --issue 1 --candidates 3 --eligible 2
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_FILE_DIR        = Path(__file__).parent
_EXTERNAL_CREDIT = _FILE_DIR.parent
_EXAMPLES        = _EXTERNAL_CREDIT / "examples"
_REPO_ROOT       = _EXTERNAL_CREDIT.parent.parent.parent
_CREDIT_EXAMPLES = _REPO_ROOT / "bridge" / "gitsea" / "credit" / "examples"


# ── Observation labels ────────────────────────────────────────────────────────

OBSERVATION_LABELS = {
    "candidate_not_yet_recognized":
        "Candidate exists; no external credit observed yet. "
        "External credit is sovereign and may emerge independently.",

    "candidate_recognized_externally":
        "Candidate exists and external credit has been observed. "
        "Candidate credit and external credit are distinct records.",

    "no_candidate_no_credit":
        "No candidate credit and no external credit. "
        "No contribution has completed the candidate threshold.",

    "external_credit_without_candidate":
        "External credit observed without a matching Dan-Go candidate. "
        "External systems may issue credit independently of Dan-Go.",
}


# ── Comparison builder ────────────────────────────────────────────────────────

def build_candidate_vs_external(
    claim_id: str,
    issue_id: int,
    candidate_credit: bool,
    candidate_count: int,
    credit_eligible: int,
    external_credit: bool,
    external_system: str = "gitsea",
) -> dict[str, Any]:
    """
    Compare Dan-Go candidate credit against observed external credit.

    Parameters
    ----------
    claim_id : str
        Dan-Go claim identifier.
    issue_id : int
        GitHub issue number.
    candidate_credit : bool
        Whether any Dan-Go credit candidates exist with candidate_credit=true.
    candidate_count : int
        Total number of contribution candidates.
    credit_eligible : int
        Number of candidates with candidate_credit=true.
    external_credit : bool
        Whether external credit has been observed in the external system.
    external_system : str
        External system identifier.
    """
    # Derive observation label
    if candidate_credit and not external_credit:
        obs_key = "candidate_not_yet_recognized"
    elif candidate_credit and external_credit:
        obs_key = "candidate_recognized_externally"
    elif not candidate_credit and not external_credit:
        obs_key = "no_candidate_no_credit"
    else:
        obs_key = "external_credit_without_candidate"

    equivalent = candidate_credit == external_credit

    return {
        "comparison_type":    "candidate_vs_external_credit",
        "generated_at":       datetime.now(timezone.utc).isoformat(),
        "comparison_id":      f"cmp-{claim_id}-issue-{issue_id}",

        # Claim context
        "claim_id":           claim_id,
        "issue_id":           issue_id,
        "external_system":    external_system,

        # Phase 11 candidate state
        "candidate_credit":   candidate_credit,
        "candidate_count":    candidate_count,
        "credit_eligible":    credit_eligible,

        # External observation
        "external_credit":    external_credit,
        "equivalent":         equivalent,
        "observation":        obs_key,
        "observation_label":  OBSERVATION_LABELS[obs_key],

        # Gap analysis
        "gap_exists":         candidate_credit and not external_credit,
        "gap_is_error":       False,   # never — external credit is sovereign
        "gap_explanation": (
            None if not (candidate_credit and not external_credit)
            else (
                "A contribution candidate exists in Dan-Go records but no "
                "external credit has been detected in the observed system. "
                "This is expected: external credit systems are sovereign. "
                "Dan-Go does not issue or request credit on behalf of contributors. "
                "The gap may close when the external system independently "
                "processes the contribution context."
            )
        ),

        # Permanent invariants
        "credit_issued":      False,
        "moves_money":        False,
        "execution_allowed":  False,
        "hard_enforcement":   False,
        "advisory":           True,
        "authority":          "none",
        "append_only":        True,
        "contestable":        True,
        "reopenable":         True,

        "principle_1": "Observation is not issuance.",
        "principle_2": "Candidate credit is not external credit.",
    }


# ── Default comparison ────────────────────────────────────────────────────────

def build_default_comparison() -> dict[str, Any]:
    """
    Build the default comparison for housing-007 / Issue #1.

    Phase 11 generated 3 candidates, 2 credit_eligible.
    No external credit detected as of 2026-05-30.
    """
    return build_candidate_vs_external(
        claim_id="housing-007",
        issue_id=1,
        candidate_credit=True,    # Phase 11: 2 credit-eligible candidates
        candidate_count=3,
        credit_eligible=2,
        external_credit=False,    # No GITSEA credit detected
        external_system="gitsea",
    )


# ── Load from Phase 11 ────────────────────────────────────────────────────────

def load_phase11_snapshot(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"claim_id": "housing-007", "issue_id": 1,
                "candidate_count": 3, "credit_eligible": 2}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ── Save ──────────────────────────────────────────────────────────────────────

def save_comparison(doc: dict, out_path: Path | None = None) -> Path:
    if out_path is None:
        out_path = _EXAMPLES / "candidate-vs-external.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Compare candidate credit against external credit (observation only).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Observation is not issuance.
Candidate credit is not external credit.
The gap between candidates and external credit is not an error.

Examples:
  python bridge/gitsea/external_credit/runtime/candidate_vs_external.py
  python bridge/gitsea/external_credit/runtime/candidate_vs_external.py --save
  python bridge/gitsea/external_credit/runtime/candidate_vs_external.py --json
  python bridge/gitsea/external_credit/runtime/candidate_vs_external.py \\
      --claim housing-007 --issue 1 --candidates 3 --eligible 2
        """,
    )
    p.add_argument("--input", metavar="PATH",
                   help="Path to credit-candidate-snapshot.json from Phase 11")
    p.add_argument("--claim", default=None)
    p.add_argument("--issue", type=int, default=None)
    p.add_argument("--candidates", type=int, default=None,
                   help="Override candidate_count")
    p.add_argument("--eligible", type=int, default=None,
                   help="Override credit_eligible count")
    p.add_argument("--external-credit", action="store_true",
                   help="Mark external credit as observed (default: false)")
    p.add_argument("--system", default="gitsea",
                   help="External system identifier (default: gitsea)")
    p.add_argument("--save", action="store_true",
                   help="Save to external_credit/examples/candidate-vs-external.json")
    p.add_argument("--json", action="store_true", dest="json_output")
    args = p.parse_args()

    # Load Phase 11 data if available
    input_path = (
        Path(args.input) if args.input
        else _CREDIT_EXAMPLES / "credit-candidate-snapshot.json"
    )
    phase11 = load_phase11_snapshot(input_path)

    claim_id       = args.claim      or phase11.get("claim_id", "housing-007")
    issue_id       = args.issue      or phase11.get("issue_id", 1)
    candidate_count = args.candidates if args.candidates is not None else phase11.get("candidate_count", 0)
    credit_eligible = args.eligible   if args.eligible   is not None else phase11.get("credit_eligible", 0)

    doc = build_candidate_vs_external(
        claim_id=claim_id,
        issue_id=issue_id,
        candidate_credit=(credit_eligible > 0),
        candidate_count=candidate_count,
        credit_eligible=credit_eligible,
        external_credit=args.external_credit,
        external_system=args.system,
    )

    if args.save:
        out = save_comparison(doc)
        print(f"Saved: {out}")

    if args.json_output:
        print(json.dumps(doc, indent=2, ensure_ascii=False))
        return

    # Default: human-readable
    print(f"\n{'='*60}")
    print(f"  Candidate vs External Credit: {doc['comparison_id']}")
    print(f"{'='*60}")
    print(f"  Claim:              {doc['claim_id']}  (issue #{doc['issue_id']})")
    print(f"  External system:    {doc['external_system']}")
    print()
    print(f"  Candidates:         {doc['candidate_count']}  "
          f"({doc['credit_eligible']} credit-eligible)")
    print(f"  candidate_credit:   {doc['candidate_credit']}")
    print(f"  external_credit:    {doc['external_credit']}")
    print(f"  equivalent:         {doc['equivalent']}")
    print()
    print(f"  Observation:        {doc['observation']}")
    print(f"  Label:              {doc['observation_label'][:60]}...")

    if doc.get("gap_exists"):
        print(f"\n  Gap exists:         {doc['gap_exists']}")
        print(f"  Gap is error:       {doc['gap_is_error']}  (never — external credit is sovereign)")

    print(f"\n  credit_issued:      {doc['credit_issued']}  (permanent: never by Dan-Go)")
    print(f"  moves_money:        {doc['moves_money']}")
    print(f"  execution_allowed:  {doc['execution_allowed']}")
    print(f"  advisory:           {doc['advisory']}")
    print(f"  authority:          {doc['authority']}")
    print(f"\n  \"{doc['principle_1']}\"")
    print(f"  \"{doc['principle_2']}\"")
    print()


if __name__ == "__main__":
    main()
