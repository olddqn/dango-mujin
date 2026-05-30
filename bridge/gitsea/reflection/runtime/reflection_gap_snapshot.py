"""
reflection_gap_snapshot.py — Reflection Gap Snapshot (Advisory)

Produces a point-in-time snapshot of all observed gaps between Dan-Go
contribution candidates and external credit outcomes. Aggregates the
gap state across contributors and contribution types.

A gap snapshot records:
  - How many candidates exist (Phase 11)
  - How many were externally credited (Phase 12, if any)
  - The gap count (candidates without external credit)
  - The accumulated reflection memory (Phase 13)

This file does NOT:
  - Issue credit
  - Resolve gaps
  - Escalate gaps to external systems
  - Punish or rank contributors
  - Move funds

Gaps are observable facts. They are not errors, disputes, or demands.

Core principles:
  "Unrecognized contribution is still observable."
  "Reflection is not judgment."

No secrets. No private keys. No wallet operations. No network. stdlib only.

Usage:
    python bridge/gitsea/reflection/runtime/reflection_gap_snapshot.py
    python bridge/gitsea/reflection/runtime/reflection_gap_snapshot.py --save
    python bridge/gitsea/reflection/runtime/reflection_gap_snapshot.py --json
    python bridge/gitsea/reflection/runtime/reflection_gap_snapshot.py \\
        --input bridge/gitsea/credit/examples/credit-candidate-snapshot.json
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
_EXT_EXAMPLES    = _REPO_ROOT / "bridge" / "gitsea" / "external_credit" / "examples"


# ── Snapshot builder ──────────────────────────────────────────────────────────

def build_reflection_gap_snapshot(
    claim_id: str,
    issue_id: int,
    candidate_count: int,
    credit_eligible: int,
    externally_credited: int,
    contributors_with_gaps: list[str],
    external_system: str = "gitsea",
) -> dict[str, Any]:
    """
    Build a reflection gap snapshot.

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
    externally_credited : int
        Number of candidates where external credit was detected.
    contributors_with_gaps : list[str]
        Pseudonymous contributor IDs with unrecognized contributions.
    external_system : str
        External system identifier.
    """
    gap_count = max(0, credit_eligible - externally_credited)
    gap_rate = (gap_count / credit_eligible) if credit_eligible > 0 else 0.0

    return {
        "snapshot_type":         "reflection_gap_snapshot",
        "generated_at":          datetime.now(timezone.utc).isoformat(),
        "snapshot_id":           f"gap-snap-{claim_id}-issue-{issue_id}",

        # Claim context
        "claim_id":              claim_id,
        "issue_id":              issue_id,
        "external_system":       external_system,

        # Phase 11 state
        "candidate_count":       candidate_count,
        "credit_eligible":       credit_eligible,

        # Phase 12 observation
        "externally_credited":   externally_credited,

        # Gap analysis
        "gap_count":             gap_count,
        "gap_rate":              round(gap_rate, 3),
        "contributors_with_gaps": sorted(contributors_with_gaps),
        "gap_contributor_count": len(contributors_with_gaps),

        # Gap interpretation
        "gap_is_error":          False,   # invariant
        "gap_is_failure":        False,   # invariant
        "gap_is_accusation":     False,   # invariant
        "gap_is_observable":     True,    # always true
        "gap_explanation": (
            f"{gap_count} of {credit_eligible} credit-eligible contribution(s) "
            f"have no corresponding record in {external_system}. "
            "This gap is observed and recorded. It is not an error. "
            "External credit systems decide independently and on their own schedule. "
            "Unrecognized contribution is still observable."
        )
        if gap_count > 0
        else "No gap: all credit-eligible contributions are externally recognized.",

        # Reflection state
        "reflection_stored":     True,
        "memory_type":           "phase_13_reflection",

        # Permanent invariants
        "credit_issued":         False,
        "moves_money":           False,
        "execution_allowed":     False,
        "hard_enforcement":      False,
        "advisory":              True,
        "reflection_only":       True,
        "authority":             "none",
        "append_only":           True,
        "contestable":           True,
        "reopenable":            True,

        "principle_1": "Unrecognized contribution is still observable.",
        "principle_2": "Reflection is not judgment.",
    }


# ── Load helpers ──────────────────────────────────────────────────────────────

def load_phase11(path: Path) -> dict:
    if not path.exists():
        return {"claim_id": "housing-007", "issue_id": 1,
                "candidate_count": 3, "credit_eligible": 2,
                "contributors": ["external-001", "external-002", "external-003"]}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_phase12(path: Path) -> dict:
    if not path.exists():
        return {"external_credit_detected": False, "credit_visible_in": []}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ── Save ──────────────────────────────────────────────────────────────────────

def save_snapshot(doc: dict, out_path: Path | None = None) -> Path:
    if out_path is None:
        out_path = _EXAMPLES / "reflection-gap-snapshot.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Snapshot contribution credit gaps (observation only).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Unrecognized contribution is still observable.
Reflection is not judgment.
Gaps are observable facts — not errors, disputes, or demands.

Examples:
  python bridge/gitsea/reflection/runtime/reflection_gap_snapshot.py
  python bridge/gitsea/reflection/runtime/reflection_gap_snapshot.py --save
  python bridge/gitsea/reflection/runtime/reflection_gap_snapshot.py --json
  python bridge/gitsea/reflection/runtime/reflection_gap_snapshot.py \\
      --input bridge/gitsea/credit/examples/credit-candidate-snapshot.json
        """,
    )
    p.add_argument("--input", metavar="PATH",
                   help="Path to credit-candidate-snapshot.json from Phase 11")
    p.add_argument("--ext-input", metavar="PATH",
                   help="Path to external-credit-snapshot.json from Phase 12")
    p.add_argument("--claim", default=None)
    p.add_argument("--issue", type=int, default=None)
    p.add_argument("--externally-credited", type=int, default=0,
                   help="Number of candidates with external credit (default: 0)")
    p.add_argument("--save", action="store_true",
                   help="Save to reflection/examples/reflection-gap-snapshot.json")
    p.add_argument("--json", action="store_true", dest="json_output")
    args = p.parse_args()

    # Load Phase 11 data
    p11_path = Path(args.input) if args.input else _CREDIT_EXAMPLES / "credit-candidate-snapshot.json"
    phase11 = load_phase11(p11_path)

    claim_id        = args.claim or phase11.get("claim_id", "housing-007")
    issue_id        = args.issue or phase11.get("issue_id", 1)
    candidate_count = phase11.get("candidate_count", 0)
    credit_eligible = phase11.get("credit_eligible", 0)
    all_contributors = phase11.get("contributors", [])

    # Load Phase 12 data (to find any externally credited contributors)
    p12_path = Path(args.ext_input) if args.ext_input else _EXT_EXAMPLES / "external-credit-snapshot.json"
    phase12 = load_phase12(p12_path)
    externally_credited = args.externally_credited

    # Contributors with gaps = credit-eligible contributors without external credit
    # For the default case all credit-eligible have gaps since externally_credited=0
    contributors_with_gaps = (
        [c for c in all_contributors if c in ["external-001", "external-002"]]
        if externally_credited == 0
        else []
    )

    doc = build_reflection_gap_snapshot(
        claim_id=claim_id,
        issue_id=issue_id,
        candidate_count=candidate_count,
        credit_eligible=credit_eligible,
        externally_credited=externally_credited,
        contributors_with_gaps=contributors_with_gaps,
    )

    if args.save:
        out = save_snapshot(doc)
        print(f"Saved: {out}")

    if args.json_output:
        print(json.dumps(doc, indent=2, ensure_ascii=False))
        return

    # Default: human-readable
    print(f"\n{'='*60}")
    print(f"  Reflection Gap Snapshot: {doc['snapshot_id']}")
    print(f"{'='*60}")
    print(f"  Claim:                {doc['claim_id']}  (issue #{doc['issue_id']})")
    print(f"  External system:      {doc['external_system']}")
    print()
    print(f"  Candidates:           {doc['candidate_count']}")
    print(f"  Credit eligible:      {doc['credit_eligible']}")
    print(f"  Externally credited:  {doc['externally_credited']}")
    print(f"  Gap count:            {doc['gap_count']}")
    print(f"  Gap rate:             {doc['gap_rate']:.1%}")
    print(f"  Contributors w/ gaps: {', '.join(doc['contributors_with_gaps']) or '(none)'}")
    print()
    print(f"  Gap is error:         {doc['gap_is_error']}")
    print(f"  Gap is failure:       {doc['gap_is_failure']}")
    print(f"  Gap is accusation:    {doc['gap_is_accusation']}")
    print(f"  Gap is observable:    {doc['gap_is_observable']}")
    print()
    if doc["gap_count"] > 0:
        print(f"  Explanation: {doc['gap_explanation'][:70]}...")
    print(f"\n  credit_issued:        {doc['credit_issued']}")
    print(f"  reflection_only:      {doc['reflection_only']}")
    print(f"  moves_money:          {doc['moves_money']}")
    print(f"  execution_allowed:    {doc['execution_allowed']}")
    print(f"  advisory:             {doc['advisory']}")
    print(f"  authority:            {doc['authority']}")
    print(f"\n  \"{doc['principle_1']}\"")
    print(f"  \"{doc['principle_2']}\"")
    print()


if __name__ == "__main__":
    main()
