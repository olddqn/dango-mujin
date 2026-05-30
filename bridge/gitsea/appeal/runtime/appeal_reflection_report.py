"""
appeal_reflection_report.py — Appeal Reflection Report (Human-Readable, Advisory)

Generates the Phase 14 summary report explaining:
  - Why appeal exists in the Dan-Go protocol
  - Why appeal does not compel GITSEA or any external system
  - Why Dan-Go cannot issue credit
  - Why reopenability matters for contribution records
  - Why contributors can request reconsideration without creating authority

This is the authoritative advisory summary for Phase 14.
It does not submit appeals; it explains the appeal layer.

This file does NOT:
  - Submit appeals to external systems
  - Issue credit
  - Create enforceable claims
  - Move funds
  - Perform wallet operations

Core principles:
  "Appeal is not enforcement."
  "Recognition remains external."

No secrets. No private keys. No wallet operations. No network. stdlib only.

Usage:
    python bridge/gitsea/appeal/runtime/appeal_reflection_report.py
    python bridge/gitsea/appeal/runtime/appeal_reflection_report.py --save
    python bridge/gitsea/appeal/runtime/appeal_reflection_report.py --json
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


# ── Report sections ───────────────────────────────────────────────────────────

APPEAL_REPORT_SECTIONS = [
    {
        "section": "Why Appeal Exists",
        "summary": (
            "Appeal provides a protocol path for contributors to request "
            "reconsideration of unrecognized contributions without creating authority."
        ),
        "detail": (
            "Phase 13 recorded that contribution candidates exist without external credit. "
            "Phase 14 provides a structured way to record that a contributor or observer "
            "requests reconsideration. This is the difference between passive observation "
            "(Phase 13) and an active — but still advisory — request (Phase 14). "
            "Appeal is a voice, not a lever. It is recorded; it is not enforced."
        ),
        "appeal_is_enforcement": False,
    },
    {
        "section": "Why Appeal Does Not Compel GITSEA",
        "summary": (
            "Dan-Go has no authority over GITSEA. "
            "An advisory appeal cannot compel a sovereign external system."
        ),
        "detail": (
            "GITSEA is sovereign over its own credit decisions. Dan-Go's authority "
            "is explicitly none. An appeal recorded in Dan-Go is visible to any "
            "observer who reads Dan-Go records — including GITSEA. But GITSEA is "
            "not bound to respond, acknowledge, or act on any Dan-Go appeal. "
            "The appeal_compels_response: false invariant makes this permanent. "
            "Recognition remains external — always."
        ),
        "compels_response":     False,
        "authority":            "none",
    },
    {
        "section": "Why Dan-Go Cannot Issue Credit",
        "summary": (
            "Dan-Go is a negotiation protocol. It records contribution candidates. "
            "It is not a credit system. credit_issued is a permanent false invariant."
        ),
        "detail": (
            "The Dan-Go protocol was designed from Phase 11 forward with credit_issued: false "
            "as a permanent invariant. This means: even if Dan-Go records an appeal, "
            "even if an external system acknowledges it, even if credit is subsequently "
            "issued — Dan-Go's own record will still show credit_issued: false, because "
            "Dan-Go did not issue it. Dan-Go records contributions. External systems "
            "issue credit. These roles are permanently separated."
        ),
        "credit_issued":        False,
        "permanent_invariant":  True,
    },
    {
        "section": "Why Reopenability Matters",
        "summary": (
            "Contribution records being reopenable means appeals can always be recorded. "
            "No contribution is permanently closed to reconsideration."
        ),
        "detail": (
            "The reopenable: true invariant on all Dan-Go records means that a contribution "
            "which was once observed without credit is never permanently foreclosed. "
            "A new appeal can be recorded at any time. A new external credit observation "
            "can be appended. The contribution history is append-only but never closed. "
            "Reopenability is the protocol's way of acknowledging that credit recognition "
            "is a process that may continue beyond a single observation window."
        ),
        "reopenable":           True,
        "append_only":          True,
    },
    {
        "section": "Why Request Without Authority",
        "summary": (
            "Contributors can request reconsideration precisely because the request "
            "carries no authority. Authority would change the protocol's nature."
        ),
        "detail": (
            "If an appeal could compel credit, then Dan-Go would have authority over "
            "external systems. That would make Dan-Go an enforcement system, not a "
            "negotiation protocol. The authority: none invariant is not a limitation — "
            "it is the design. By having no authority, Dan-Go can record appeals freely "
            "without the records becoming weapons, levers, or claims. "
            "A request without authority is an expression of interest, not a demand. "
            "External systems can respond to interest without being compelled to."
        ),
        "authority":            "none",
        "appeal_is_demand":     False,
    },
]


# ── Report builder ────────────────────────────────────────────────────────────

def build_appeal_reflection_report(
    claim_id: str = "housing-007",
    issue_id: int = 1,
    total_appeals: int = 2,
    appeals_pending: int = 2,
    external_system: str = "gitsea",
) -> dict[str, Any]:
    """Build the Phase 14 appeal reflection report."""
    return {
        "report_type":       "appeal_reflection_report",
        "generated_at":      datetime.now(timezone.utc).isoformat(),
        "report_id":         f"appeal-report-{claim_id}-issue-{issue_id}",

        # Claim context
        "claim_id":          claim_id,
        "issue_id":          issue_id,
        "external_system":   external_system,

        # Appeal state summary
        "total_appeals":     total_appeals,
        "appeals_pending":   appeals_pending,

        # Report content
        "section_count":     len(APPEAL_REPORT_SECTIONS),
        "sections":          APPEAL_REPORT_SECTIONS,

        # Summary table
        "summary_table": {
            "appeal_exists":              True,
            "appeal_is_enforcement":      False,
            "appeal_compels_gitsea":      False,
            "dango_can_issue_credit":     False,
            "records_reopenable":         True,
            "authority_exists":           False,
            "appeal_is_demand":           False,
            "recognition_remains_external": True,
        },

        # Permanent invariants
        "credit_issued":     False,
        "moves_money":       False,
        "execution_allowed": False,
        "hard_enforcement":  False,
        "advisory":          True,
        "appeal_only":       True,
        "authority":         "none",
        "append_only":       True,
        "contestable":       True,
        "reopenable":        True,

        "principle_1": "Appeal is not enforcement.",
        "principle_2": "Recognition remains external.",
        "principle_3": "Contribution becomes legible before it becomes valuable.",
    }


# ── Save ──────────────────────────────────────────────────────────────────────

def save_report(doc: dict, out_path: Path | None = None) -> Path:
    if out_path is None:
        out_path = _EXAMPLES / "appeal-reflection-report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Generate appeal reflection report (advisory, no credit issued).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Appeal is not enforcement.
Recognition remains external.
Dan-Go records appeals; it does not enforce them.

Examples:
  python bridge/gitsea/appeal/runtime/appeal_reflection_report.py
  python bridge/gitsea/appeal/runtime/appeal_reflection_report.py --save
  python bridge/gitsea/appeal/runtime/appeal_reflection_report.py --json
        """,
    )
    p.add_argument("--claim", default="housing-007")
    p.add_argument("--issue", type=int, default=1)
    p.add_argument("--total-appeals", type=int, default=2)
    p.add_argument("--system", default="gitsea")
    p.add_argument("--save", action="store_true",
                   help="Save to appeal/examples/appeal-reflection-report.json")
    p.add_argument("--json", action="store_true", dest="json_output")
    args = p.parse_args()

    doc = build_appeal_reflection_report(
        claim_id=args.claim,
        issue_id=args.issue,
        total_appeals=args.total_appeals,
        appeals_pending=args.total_appeals,
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
    print(f"  Appeal Reflection Report: {doc['report_id']}")
    print(f"{'='*60}")
    print(f"  Claim:             {doc['claim_id']}  (issue #{doc['issue_id']})")
    print(f"  External system:   {doc['external_system']}")
    print(f"  Total appeals:     {doc['total_appeals']}  "
          f"(pending: {doc['appeals_pending']})")
    print()
    for sec in doc["sections"]:
        print(f"  ▶  {sec['section']}")
        print(f"     {sec['summary'][:72]}")
        print()
    st = doc["summary_table"]
    print(f"  Summary table:")
    print(f"    Appeal exists:                {st['appeal_exists']}")
    print(f"    Appeal is enforcement:        {st['appeal_is_enforcement']}")
    print(f"    Appeal compels GITSEA:        {st['appeal_compels_gitsea']}")
    print(f"    Dan-Go can issue credit:      {st['dango_can_issue_credit']}")
    print(f"    Records reopenable:           {st['records_reopenable']}")
    print(f"    Authority exists:             {st['authority_exists']}")
    print(f"    Appeal is demand:             {st['appeal_is_demand']}")
    print(f"    Recognition remains external: {st['recognition_remains_external']}")
    print(f"\n  credit_issued:     {doc['credit_issued']}")
    print(f"  appeal_only:       {doc['appeal_only']}")
    print(f"  hard_enforcement:  {doc['hard_enforcement']}")
    print(f"  moves_money:       {doc['moves_money']}")
    print(f"  advisory:          {doc['advisory']}")
    print(f"  authority:         {doc['authority']}")
    print(f"\n  \"{doc['principle_1']}\"")
    print(f"  \"{doc['principle_2']}\"")
    print()


if __name__ == "__main__":
    main()
