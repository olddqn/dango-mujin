"""
external_credit_snapshot.py — External Credit Observation Snapshot (Advisory)

Produces a point-in-time snapshot of the observed external credit state
for a given claim. Aggregates all known external systems and summarises
whether any credit has been detected.

A snapshot records:
  - Which external systems were observed
  - The total candidate count from Phase 11
  - Whether external credit was detected in any system
  - The observation timestamp

This file does NOT:
  - Issue credit
  - Trigger external credit
  - Activate GITSEA streams
  - Move funds
  - Call any API

Dan-Go produces observation snapshots. It does not produce credit events.

Core principles:
  "Observation is not issuance."
  "Candidate credit is not external credit."

No secrets. No private keys. No wallet operations. No network. stdlib only.

Usage:
    python bridge/gitsea/external_credit/runtime/external_credit_snapshot.py
    python bridge/gitsea/external_credit/runtime/external_credit_snapshot.py --save
    python bridge/gitsea/external_credit/runtime/external_credit_snapshot.py --json
    python bridge/gitsea/external_credit/runtime/external_credit_snapshot.py \\
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
_EXTERNAL_CREDIT = _FILE_DIR.parent
_EXAMPLES        = _EXTERNAL_CREDIT / "examples"
_REPO_ROOT       = _EXTERNAL_CREDIT.parent.parent.parent
_CREDIT_EXAMPLES = _REPO_ROOT / "bridge" / "gitsea" / "credit" / "examples"


# ── Snapshot builder ──────────────────────────────────────────────────────────

def build_external_credit_snapshot(
    claim_id: str,
    issue_id: int,
    candidate_count: int,
    credit_eligible: int,
    systems_observed: list[str],
    external_credit_detected: bool = False,
    credit_visible_in: list[str] | None = None,
) -> dict[str, Any]:
    """
    Build an advisory external credit observation snapshot.

    Parameters
    ----------
    claim_id : str
        Dan-Go claim identifier.
    issue_id : int
        GitHub issue number.
    candidate_count : int
        Total contribution candidates from Phase 11.
    credit_eligible : int
        Number of candidates with candidate_credit=true from Phase 11.
    systems_observed : list[str]
        List of external system identifiers that were observed.
    external_credit_detected : bool
        Whether any external system has confirmed credit. Default False.
    credit_visible_in : list[str] | None
        Which systems (if any) show credit. Default empty.
    """
    visible_in = credit_visible_in or []
    return {
        "snapshot_type":            "external_credit_snapshot",
        "generated_at":             datetime.now(timezone.utc).isoformat(),
        "snapshot_id":              f"ext-snapshot-{claim_id}-issue-{issue_id}",

        # Claim context
        "claim_id":                 claim_id,
        "issue_id":                 issue_id,

        # Phase 11 candidate counts
        "candidate_count":          candidate_count,
        "credit_eligible":          credit_eligible,

        # External observation
        "systems_observed":         sorted(systems_observed),
        "system_count":             len(systems_observed),
        "external_credit_detected": external_credit_detected,
        "credit_visible_in":        sorted(visible_in),
        "observation_only":         True,

        # Status summary
        "observation_status": (
            f"credit_detected_in: {sorted(visible_in)}"
            if external_credit_detected
            else "no_external_credit_detected"
        ),
        "gap_note": (
            None if not (credit_eligible > 0 and not external_credit_detected)
            else (
                f"{credit_eligible} candidate(s) exist but no external credit detected. "
                "This is not an error. External credit is sovereign and optional. "
                "Candidate credit is not external credit."
            )
        ),

        # Permanent invariants
        "credit_issued":            False,
        "moves_money":              False,
        "execution_allowed":        False,
        "hard_enforcement":         False,
        "advisory":                 True,
        "authority":                "none",
        "append_only":              True,
        "contestable":              True,
        "reopenable":               True,

        "principle_1": "Observation is not issuance.",
        "principle_2": "Candidate credit is not external credit.",
    }


# ── Load Phase 11 candidate snapshot ─────────────────────────────────────────

def load_credit_candidate_snapshot(path: Path) -> dict[str, Any]:
    """Load a credit-candidate-snapshot.json produced by Phase 11."""
    if not path.exists():
        # Reasonable defaults matching Phase 11 examples
        return {
            "claim_id":       "housing-007",
            "issue_id":       1,
            "candidate_count": 3,
            "credit_eligible": 2,
        }
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ── Save ──────────────────────────────────────────────────────────────────────

def save_snapshot(doc: dict, out_path: Path | None = None) -> Path:
    if out_path is None:
        out_path = _EXAMPLES / "external-credit-snapshot.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Snapshot external credit observation state (no credit issued).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Observation is not issuance.
Candidate credit is not external credit.

Reads Phase 11 credit-candidate-snapshot.json to get candidate counts.

Examples:
  python bridge/gitsea/external_credit/runtime/external_credit_snapshot.py
  python bridge/gitsea/external_credit/runtime/external_credit_snapshot.py --save
  python bridge/gitsea/external_credit/runtime/external_credit_snapshot.py --json
  python bridge/gitsea/external_credit/runtime/external_credit_snapshot.py \\
      --input bridge/gitsea/credit/examples/credit-candidate-snapshot.json
        """,
    )
    p.add_argument("--input", metavar="PATH",
                   help="Path to credit-candidate-snapshot.json from Phase 11")
    p.add_argument("--claim", default=None)
    p.add_argument("--issue", type=int, default=None)
    p.add_argument("--credit-detected", action="store_true",
                   help="Mark external credit as detected (default: false)")
    p.add_argument("--save", action="store_true",
                   help="Save to external_credit/examples/external-credit-snapshot.json")
    p.add_argument("--json", action="store_true", dest="json_output")
    args = p.parse_args()

    # Load Phase 11 data
    input_path = (
        Path(args.input) if args.input
        else _CREDIT_EXAMPLES / "credit-candidate-snapshot.json"
    )
    phase11 = load_credit_candidate_snapshot(input_path)

    claim_id = args.claim or phase11.get("claim_id", "housing-007")
    issue_id = args.issue or phase11.get("issue_id", 1)

    doc = build_external_credit_snapshot(
        claim_id=claim_id,
        issue_id=issue_id,
        candidate_count=phase11.get("candidate_count", 0),
        credit_eligible=phase11.get("credit_eligible", 0),
        systems_observed=["gitsea"],
        external_credit_detected=args.credit_detected,
    )

    if args.save:
        out = save_snapshot(doc)
        print(f"Saved: {out}")

    if args.json_output:
        print(json.dumps(doc, indent=2, ensure_ascii=False))
        return

    # Default: human-readable
    print(f"\n{'='*60}")
    print(f"  External Credit Snapshot: {doc['snapshot_id']}")
    print(f"{'='*60}")
    print(f"  Claim:                    {doc['claim_id']}  (issue #{doc['issue_id']})")
    print(f"  Systems observed:         {', '.join(doc['systems_observed'])}")
    print()
    print(f"  Phase 11 candidates:      {doc['candidate_count']}")
    print(f"  Credit eligible:          {doc['credit_eligible']}  (candidate status only)")
    print()
    print(f"  External credit detected: {doc['external_credit_detected']}")
    print(f"  Visible in:               {doc['credit_visible_in'] or '(none)'}")
    print(f"  Status:                   {doc['observation_status']}")

    if doc.get("gap_note"):
        print(f"\n  Gap note: {doc['gap_note']}")

    print(f"\n  credit_issued:            {doc['credit_issued']}  (permanent: never by Dan-Go)")
    print(f"  observation_only:         {doc['observation_only']}")
    print(f"  moves_money:              {doc['moves_money']}")
    print(f"  execution_allowed:        {doc['execution_allowed']}")
    print(f"  advisory:                 {doc['advisory']}")
    print(f"  authority:                {doc['authority']}")
    print(f"\n  \"{doc['principle_1']}\"")
    print(f"  \"{doc['principle_2']}\"")
    print()


if __name__ == "__main__":
    main()
