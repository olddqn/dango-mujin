"""
credit_observation_report.py — Credit Observation Report (Human-Readable, Advisory)

Generates a human-readable JSON report explaining the full state of:
  - Dan-Go contribution candidates (Phase 11)
  - External credit observation (Phase 12)
  - The gap between candidates and external credit
  - Why the gap is not an error
  - Why observation is sufficient

This report is the authoritative advisory record for a claim's credit
observation state. It does not resolve the gap; it explains it.

This file does NOT:
  - Issue credit
  - Request credit issuance from external systems
  - Modify any external state
  - Move funds
  - Call any API

Core principles:
  "Observation is not issuance."
  "Candidate credit is not external credit."

No secrets. No private keys. No wallet operations. No network. stdlib only.

Usage:
    python bridge/gitsea/external_credit/runtime/credit_observation_report.py
    python bridge/gitsea/external_credit/runtime/credit_observation_report.py --save
    python bridge/gitsea/external_credit/runtime/credit_observation_report.py --json
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


# ── Report sections ───────────────────────────────────────────────────────────

def _build_report_sections(
    candidate_credit: bool,
    credit_eligible: int,
    candidate_count: int,
    external_credit: bool,
    external_system: str,
) -> list[dict[str, Any]]:
    return [
        {
            "section":   "Candidate Exists",
            "summary":   (
                f"{credit_eligible} of {candidate_count} contribution candidate(s) "
                f"met the credit-eligibility threshold in Phase 11."
                if candidate_credit
                else "No contribution candidates met the credit-eligibility threshold."
            ),
            "detail": (
                "Dan-Go Phase 11 recorded contribution events as candidates. "
                f"{credit_eligible} candidate(s) have candidate_credit=true, meaning "
                "they completed accepted work (evidence_reviewed, evidence_accepted, "
                "reaffirm_submitted, or plan_correction). This is an advisory "
                "classification — it does not trigger any action."
            ),
            "candidate_credit": candidate_credit,
            "credit_issued":    False,
        },
        {
            "section":   "External Credit Absent",
            "summary":   (
                f"No external credit observed in {external_system}."
                if not external_credit
                else f"External credit detected in {external_system}."
            ),
            "detail": (
                f"Dan-Go observed {external_system} and found no credit record "
                "corresponding to the contribution candidates above. "
                "This is not an error. External credit systems are sovereign — "
                f"{external_system} decides independently whether and when to "
                "issue credit. Dan-Go does not request, push, or activate credit."
            )
            if not external_credit
            else (
                f"Dan-Go observed {external_system} and found credit corresponding "
                "to this claim. Note: external credit and candidate credit are "
                "distinct records. Dan-Go did not issue the external credit."
            ),
            "external_credit":  external_credit,
            "credit_issued":    False,
        },
        {
            "section":   "No Contradiction Exists",
            "summary":   (
                "The gap between candidate credit and external credit "
                "is not a protocol contradiction."
            ),
            "detail": (
                "Dan-Go candidate credit and external credit are different things. "
                "A candidate existing in Dan-Go does not mean external credit was "
                "issued or is owed. A gap between the two states is expected and "
                "by design. External credit systems such as GITSEA are sovereign: "
                "they may issue credit at any time, on their own schedule, or not "
                "at all. Dan-Go does not guarantee credit. Dan-Go records candidates."
            ),
            "gap_is_error":     False,
            "credit_issued":    False,
        },
        {
            "section":   "Observation Is Sufficient",
            "summary":   (
                "Dan-Go's role ends at observation. "
                "Making contribution legible is the goal — not issuing credit."
            ),
            "detail": (
                "The Dan-Go protocol is designed to make contribution legible "
                "before it becomes economically valuable. Recording candidates, "
                "building contribution history, and surfacing them for external "
                "system observation is the complete role of Dan-Go in the credit "
                "process. Whether value follows is determined by external systems. "
                "Observation is not issuance. Dan-Go has fulfilled its role "
                "by recording candidates accurately and making them observable."
            ),
            "observation_sufficient": True,
            "credit_issued":         False,
        },
    ]


# ── Report builder ────────────────────────────────────────────────────────────

def build_credit_observation_report(
    claim_id: str = "housing-007",
    issue_id: int = 1,
    candidate_count: int = 3,
    credit_eligible: int = 2,
    candidate_credit: bool = True,
    external_credit: bool = False,
    external_system: str = "gitsea",
) -> dict[str, Any]:
    """
    Build a human-readable credit observation report.

    Parameters
    ----------
    claim_id : str
        Dan-Go claim identifier.
    issue_id : int
        GitHub issue number.
    candidate_count : int
        Total contribution candidates from Phase 11.
    credit_eligible : int
        Number of candidates with candidate_credit=true.
    candidate_credit : bool
        Whether any candidate_credit=true records exist.
    external_credit : bool
        Whether external credit has been observed.
    external_system : str
        External system identifier.
    """
    sections = _build_report_sections(
        candidate_credit=candidate_credit,
        credit_eligible=credit_eligible,
        candidate_count=candidate_count,
        external_credit=external_credit,
        external_system=external_system,
    )

    return {
        "report_type":       "credit_observation_report",
        "generated_at":      datetime.now(timezone.utc).isoformat(),
        "report_id":         f"obs-report-{claim_id}-issue-{issue_id}",

        # Claim context
        "claim_id":          claim_id,
        "issue_id":          issue_id,
        "external_system":   external_system,

        # Summary (matches spec example structure)
        "summary": (
            f"Contribution candidate exists but no external credit observed."
            if candidate_credit and not external_credit
            else (
                "Contribution candidate exists and external credit observed."
                if candidate_credit and external_credit
                else "No contribution candidates and no external credit."
                if not candidate_credit and not external_credit
                else "External credit observed without matching contribution candidate."
            )
        ),
        "candidate_credit":  candidate_credit,
        "external_credit":   external_credit,
        "credit_issued":     False,   # permanent invariant
        "advisory":          True,

        # Detailed breakdown
        "candidate_count":   candidate_count,
        "credit_eligible":   credit_eligible,
        "section_count":     len(sections),
        "sections":          sections,

        # Summary table
        "summary_table": {
            "candidate_exists":            candidate_credit,
            "external_credit_absent":      not external_credit,
            "gap_is_error":                False,
            "observation_sufficient":      True,
            "dango_issues_credit":         False,
            "dango_requests_credit":       False,
            "external_system_sovereign":   True,
        },

        # Invariants
        "moves_money":        False,
        "execution_allowed":  False,
        "hard_enforcement":   False,
        "authority":          "none",
        "append_only":        True,
        "contestable":        True,
        "reopenable":         True,

        "principle_1": "Observation is not issuance.",
        "principle_2": "Candidate credit is not external credit.",
        "principle_3": "Contribution becomes legible before it becomes valuable.",
    }


# ── Load helpers ──────────────────────────────────────────────────────────────

def load_phase11(path: Path) -> dict:
    if not path.exists():
        return {"claim_id": "housing-007", "issue_id": 1,
                "candidate_count": 3, "credit_eligible": 2}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ── Save ──────────────────────────────────────────────────────────────────────

def save_report(doc: dict, out_path: Path | None = None) -> Path:
    if out_path is None:
        out_path = _EXAMPLES / "credit-observation-report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Generate credit observation report (advisory, no credit issued).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Observation is not issuance.
Candidate credit is not external credit.
Dan-Go observes; it does not decide credit.

Examples:
  python bridge/gitsea/external_credit/runtime/credit_observation_report.py
  python bridge/gitsea/external_credit/runtime/credit_observation_report.py --save
  python bridge/gitsea/external_credit/runtime/credit_observation_report.py --json
        """,
    )
    p.add_argument("--input", metavar="PATH",
                   help="Path to credit-candidate-snapshot.json from Phase 11")
    p.add_argument("--claim", default=None)
    p.add_argument("--issue", type=int, default=None)
    p.add_argument("--external-credit", action="store_true",
                   help="Mark external credit as observed (default: false)")
    p.add_argument("--system", default="gitsea")
    p.add_argument("--save", action="store_true",
                   help="Save to external_credit/examples/credit-observation-report.json")
    p.add_argument("--json", action="store_true", dest="json_output")
    args = p.parse_args()

    input_path = (
        Path(args.input) if args.input
        else _CREDIT_EXAMPLES / "credit-candidate-snapshot.json"
    )
    phase11 = load_phase11(input_path)

    claim_id        = args.claim or phase11.get("claim_id", "housing-007")
    issue_id        = args.issue or phase11.get("issue_id", 1)
    candidate_count = phase11.get("candidate_count", 0)
    credit_eligible = phase11.get("credit_eligible", 0)

    doc = build_credit_observation_report(
        claim_id=claim_id,
        issue_id=issue_id,
        candidate_count=candidate_count,
        credit_eligible=credit_eligible,
        candidate_credit=(credit_eligible > 0),
        external_credit=args.external_credit,
        external_system=args.system,
    )

    if args.save:
        out = save_report(doc)
        print(f"Saved: {out}")

    if args.json_output:
        print(json.dumps(doc, indent=2, ensure_ascii=False))
        return

    # Default: human-readable
    print(f"\n{'='*60}")
    print(f"  Credit Observation Report: {doc['report_id']}")
    print(f"{'='*60}")
    print(f"  Summary: {doc['summary']}")
    print()
    print(f"  Candidates:          {doc['candidate_count']}  "
          f"({doc['credit_eligible']} credit-eligible)")
    print(f"  candidate_credit:    {doc['candidate_credit']}")
    print(f"  external_credit:     {doc['external_credit']}")
    print(f"  credit_issued:       {doc['credit_issued']}  (permanent: never by Dan-Go)")
    print()
    for sec in doc["sections"]:
        print(f"  ▶  {sec['section']}")
        print(f"     {sec['summary']}")
        print()
    st = doc["summary_table"]
    print(f"  Summary table:")
    print(f"    Candidate exists:          {st['candidate_exists']}")
    print(f"    External credit absent:    {st['external_credit_absent']}")
    print(f"    Gap is error:              {st['gap_is_error']}")
    print(f"    Observation sufficient:    {st['observation_sufficient']}")
    print(f"    Dan-Go issues credit:      {st['dango_issues_credit']}")
    print(f"    External system sovereign: {st['external_system_sovereign']}")
    print(f"\n  moves_money:         {doc['moves_money']}")
    print(f"  execution_allowed:   {doc['execution_allowed']}")
    print(f"  advisory:            {doc['advisory']}")
    print(f"  authority:           {doc['authority']}")
    print(f"\n  \"{doc['principle_1']}\"")
    print(f"  \"{doc['principle_2']}\"")
    print()


if __name__ == "__main__":
    main()
