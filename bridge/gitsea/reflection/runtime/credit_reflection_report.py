"""
credit_reflection_report.py — Credit Reflection Report (Human-Readable, Advisory)

Generates the Phase 13 summary report explaining:
  - What contribution candidates exist
  - What external credit was or wasn't observed
  - What the gap means (and doesn't mean)
  - Why Dan-Go records this as reflection, not judgment
  - Why contribution memory matters even without credit

This is the authoritative advisory summary for Phase 13.
It does not resolve gaps; it explains why they need not be resolved.

This file does NOT:
  - Issue credit
  - Escalate to external systems
  - Create disputes or appeals
  - Modify any external state
  - Move funds

Core principles:
  "Unrecognized contribution is still observable."
  "Reflection is not judgment."

No secrets. No private keys. No wallet operations. No network. stdlib only.

Usage:
    python bridge/gitsea/reflection/runtime/credit_reflection_report.py
    python bridge/gitsea/reflection/runtime/credit_reflection_report.py --save
    python bridge/gitsea/reflection/runtime/credit_reflection_report.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_FILE_DIR        = Path(__file__).parent
_REFLECTION      = _FILE_DIR.parent
_EXAMPLES        = _REFLECTION / "examples"
_REPO_ROOT       = _REFLECTION.parent.parent.parent
_CREDIT_EXAMPLES = _REPO_ROOT / "bridge" / "gitsea" / "credit" / "examples"


# ── Report sections ───────────────────────────────────────────────────────────

REFLECTION_SECTIONS = [
    {
        "section": "Contribution Happened",
        "summary": (
            "Contributions were recorded in Dan-Go regardless of external credit. "
            "They are observable here."
        ),
        "detail": (
            "The Dan-Go protocol recorded contribution events during negotiation "
            "of claim housing-007, Issue #1. Evidence was reviewed, accepted, "
            "and contested. These events are stored in the append-only contribution "
            "history (Phase 11). They are not erased by the absence of external credit. "
            "A contribution that occurred is always observable in Dan-Go memory."
        ),
        "contribution_permanent": True,
        "credit_issued":          False,
    },
    {
        "section": "External Credit Was Not Observed",
        "summary": (
            "GITSEA was observed after Phase 11 and 12. "
            "No corresponding credit record was detected."
        ),
        "detail": (
            "Phase 12 observed GITSEA and found no credit record corresponding "
            "to the Dan-Go contribution candidates. This observation was recorded "
            "in the external credit adapter and snapshot. The absence of credit "
            "is an observation — not a judgment on the quality of contributions "
            "or a failure of any party."
        ),
        "external_credit":        False,
        "credit_issued":          False,
    },
    {
        "section": "The Gap Is Not a Failure",
        "summary": (
            "Missing GITSEA credit is not a Dan-Go failure, a contributor failure, "
            "or a protocol failure."
        ),
        "detail": (
            "External credit systems such as GITSEA are sovereign over their own "
            "credit decisions. They may issue credit at any time, on their own "
            "schedule, according to their own eligibility logic — or not at all. "
            "Dan-Go does not control this process. A gap between Dan-Go candidates "
            "and GITSEA credit is expected and architecturally by design. "
            "Phase 12 established gap_is_error: false as a permanent invariant."
        ),
        "gap_is_failure":         False,
        "credit_issued":          False,
    },
    {
        "section": "Gaps Are Not Accusations",
        "summary": (
            "Unrecognized contribution records do not accuse external systems, "
            "contributors, or maintainers."
        ),
        "detail": (
            "Phase 13 records unrecognized contributions as observation facts. "
            "The is_accusation: false invariant makes this explicit in every record. "
            "Recording that a contribution exists without external credit is not a "
            "complaint, dispute, or appeal. It is a factual record of what was "
            "observed. Dan-Go does not evaluate why credit was or wasn't issued. "
            "Dan-Go records what happened."
        ),
        "is_accusation":          False,
        "credit_issued":          False,
    },
    {
        "section": "External Systems Remain Sovereign",
        "summary": (
            "GITSEA may credit these contributions at any time. "
            "Dan-Go will not prevent, delay, or trigger that decision."
        ),
        "detail": (
            "The reflection memory stored in Phase 13 does not limit or extend "
            "the window for external credit issuance. GITSEA may observe Dan-Go "
            "reflection records and may use them in future eligibility decisions. "
            "Dan-Go does not push, request, or activate this process. "
            "External system sovereignty is preserved. Dan-Go observes and remembers."
        ),
        "external_system_sovereign": True,
        "credit_issued":           False,
    },
    {
        "section": "Contribution Memory Matters",
        "summary": (
            "Remembering contribution — even without credit — is the purpose "
            "of the Dan-Go reflection layer."
        ),
        "detail": (
            "Contribution becomes legible before it becomes valuable. "
            "Reflection memory makes contribution permanently observable, even "
            "when economic recognition does not follow. This matters because: "
            "(1) Contribution history is a public record of negotiation participation. "
            "(2) Future credit systems may observe historical contribution records. "
            "(3) The Dan-Go protocol's value is in legibility, not in economic outcome. "
            "Unrecognized contribution is still observable. That is sufficient."
        ),
        "memory_sufficient":      True,
        "credit_issued":          False,
    },
]


# ── Report builder ────────────────────────────────────────────────────────────

def build_credit_reflection_report(
    claim_id: str = "housing-007",
    issue_id: int = 1,
    candidate_count: int = 3,
    credit_eligible: int = 2,
    externally_credited: int = 0,
    contributors: list[str] | None = None,
    external_system: str = "gitsea",
) -> dict[str, Any]:
    """
    Build the Phase 13 credit reflection report.

    Parameters
    ----------
    claim_id : str
        Dan-Go claim identifier.
    issue_id : int
        GitHub issue number.
    candidate_count : int
        Total contribution candidates from Phase 11.
    credit_eligible : int
        Number of credit-eligible candidates.
    externally_credited : int
        Number credited by external system.
    contributors : list[str] | None
        Pseudonymous contributor list.
    external_system : str
        External system identifier.
    """
    gap_count = max(0, credit_eligible - externally_credited)
    contributors = contributors or ["external-001", "external-002", "external-003"]

    return {
        "report_type":       "credit_reflection_report",
        "generated_at":      datetime.now(timezone.utc).isoformat(),
        "report_id":         f"reflect-report-{claim_id}-issue-{issue_id}",

        # Claim context
        "claim_id":          claim_id,
        "issue_id":          issue_id,
        "external_system":   external_system,

        # State summary
        "candidate_count":   candidate_count,
        "credit_eligible":   credit_eligible,
        "externally_credited": externally_credited,
        "gap_count":         gap_count,
        "contributors":      sorted(contributors),

        # Report content
        "section_count":     len(REFLECTION_SECTIONS),
        "sections":          REFLECTION_SECTIONS,

        # Summary table
        "summary_table": {
            "contribution_happened":      True,
            "external_credit_observed":   externally_credited > 0,
            "gap_is_failure":             False,
            "gap_is_accusation":          False,
            "external_system_sovereign":  True,
            "memory_sufficient":          True,
            "dango_judges_contributors":  False,
            "dango_escalates_gaps":       False,
        },

        # Permanent invariants
        "credit_issued":     False,
        "moves_money":       False,
        "execution_allowed": False,
        "hard_enforcement":  False,
        "advisory":          True,
        "reflection_only":   True,
        "authority":         "none",
        "append_only":       True,
        "contestable":       True,
        "reopenable":        True,

        "principle_1": "Unrecognized contribution is still observable.",
        "principle_2": "Reflection is not judgment.",
        "principle_3": "Contribution becomes legible before it becomes valuable.",
    }


# ── Load helpers ──────────────────────────────────────────────────────────────

def load_phase11(path: Path) -> dict:
    if not path.exists():
        return {"claim_id": "housing-007", "issue_id": 1,
                "candidate_count": 3, "credit_eligible": 2,
                "contributors": ["external-001", "external-002", "external-003"]}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ── Save ──────────────────────────────────────────────────────────────────────

def save_report(doc: dict, out_path: Path | None = None) -> Path:
    if out_path is None:
        out_path = _EXAMPLES / "credit-reflection-report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Generate credit reflection report (advisory, no credit issued).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Unrecognized contribution is still observable.
Reflection is not judgment.
Dan-Go remembers; it does not punish, rank, or decide.

Examples:
  python bridge/gitsea/reflection/runtime/credit_reflection_report.py
  python bridge/gitsea/reflection/runtime/credit_reflection_report.py --save
  python bridge/gitsea/reflection/runtime/credit_reflection_report.py --json
        """,
    )
    p.add_argument("--input", metavar="PATH",
                   help="Path to credit-candidate-snapshot.json from Phase 11")
    p.add_argument("--claim", default=None)
    p.add_argument("--issue", type=int, default=None)
    p.add_argument("--externally-credited", type=int, default=0)
    p.add_argument("--system", default="gitsea")
    p.add_argument("--save", action="store_true",
                   help="Save to reflection/examples/credit-reflection-report.json")
    p.add_argument("--json", action="store_true", dest="json_output")
    args = p.parse_args()

    p11_path = Path(args.input) if args.input else _CREDIT_EXAMPLES / "credit-candidate-snapshot.json"
    phase11 = load_phase11(p11_path)

    doc = build_credit_reflection_report(
        claim_id=args.claim or phase11.get("claim_id", "housing-007"),
        issue_id=args.issue or phase11.get("issue_id", 1),
        candidate_count=phase11.get("candidate_count", 0),
        credit_eligible=phase11.get("credit_eligible", 0),
        externally_credited=args.externally_credited,
        contributors=phase11.get("contributors"),
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
    print(f"  Credit Reflection Report: {doc['report_id']}")
    print(f"{'='*60}")
    print(f"  Claim:             {doc['claim_id']}  (issue #{doc['issue_id']})")
    print(f"  External system:   {doc['external_system']}")
    print(f"  Candidates:        {doc['candidate_count']}  "
          f"({doc['credit_eligible']} eligible)")
    print(f"  Externally credited: {doc['externally_credited']}")
    print(f"  Gap count:         {doc['gap_count']}")
    print()
    for sec in doc["sections"]:
        print(f"  ▶  {sec['section']}")
        print(f"     {sec['summary'][:72]}")
        print()
    st = doc["summary_table"]
    print(f"  Summary table:")
    print(f"    Contribution happened:       {st['contribution_happened']}")
    print(f"    External credit observed:    {st['external_credit_observed']}")
    print(f"    Gap is failure:              {st['gap_is_failure']}")
    print(f"    Gap is accusation:           {st['gap_is_accusation']}")
    print(f"    External system sovereign:   {st['external_system_sovereign']}")
    print(f"    Memory sufficient:           {st['memory_sufficient']}")
    print(f"    Dan-Go judges contributors:  {st['dango_judges_contributors']}")
    print(f"    Dan-Go escalates gaps:       {st['dango_escalates_gaps']}")
    print(f"\n  credit_issued:      {doc['credit_issued']}")
    print(f"  reflection_only:    {doc['reflection_only']}")
    print(f"  moves_money:        {doc['moves_money']}")
    print(f"  execution_allowed:  {doc['execution_allowed']}")
    print(f"  advisory:           {doc['advisory']}")
    print(f"  authority:          {doc['authority']}")
    print(f"\n  \"{doc['principle_1']}\"")
    print(f"  \"{doc['principle_2']}\"")
    print()


if __name__ == "__main__":
    main()
