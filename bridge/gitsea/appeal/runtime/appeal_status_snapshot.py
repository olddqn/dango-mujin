"""
appeal_status_snapshot.py — Appeal Status Snapshot (Advisory)

Produces a point-in-time snapshot of the appeal state for a claim:
  - How many appeals have been recorded
  - Whether any appeals have been acknowledged by external systems
  - The current appeal lifecycle status
  - What remains observable regardless of external response

Dan-Go records appeal state. It does not observe external acknowledgement
in real-time — it records the state as last observed locally.

This file does NOT:
  - Contact external systems to check appeal status
  - Update appeal state based on external responses
  - Issue credit if an appeal is acknowledged
  - Force any external system to respond
  - Move funds

Core principles:
  "Appeal is not enforcement."
  "Recognition remains external."

No secrets. No private keys. No wallet operations. No network. stdlib only.

Usage:
    python bridge/gitsea/appeal/runtime/appeal_status_snapshot.py
    python bridge/gitsea/appeal/runtime/appeal_status_snapshot.py --save
    python bridge/gitsea/appeal/runtime/appeal_status_snapshot.py --json
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

# ── Appeal lifecycle states ────────────────────────────────────────────────────

APPEAL_STATES = {
    "pending":       "Appeal recorded; awaiting external system observation.",
    "acknowledged":  "External system has acknowledged the appeal (observed externally).",
    "reconsidered":  "External system has reconsidered the contribution.",
    "credited":      "External credit has been issued following appeal.",
    "not_credited":  "Appeal was considered; external credit was not issued.",
    "withdrawn":     "Appeal was withdrawn by the appellant.",
}


# ── Snapshot builder ──────────────────────────────────────────────────────────

def build_appeal_status_snapshot(
    claim_id: str,
    issue_id: int,
    total_appeals: int,
    appeals_acknowledged: int = 0,
    appeals_credited: int = 0,
    appeals_withdrawn: int = 0,
    appeal_states: dict[str, str] | None = None,
    external_system: str = "gitsea",
) -> dict[str, Any]:
    """
    Build an advisory appeal status snapshot.

    Parameters
    ----------
    claim_id : str
        Dan-Go claim identifier.
    issue_id : int
        GitHub issue number.
    total_appeals : int
        Total appeals recorded.
    appeals_acknowledged : int
        Appeals acknowledged by external system (default 0).
    appeals_credited : int
        Appeals that resulted in external credit (default 0).
    appeals_withdrawn : int
        Appeals withdrawn by appellants (default 0).
    appeal_states : dict | None
        Per-appeal state mapping {appeal_id: state_key}.
    external_system : str
        External system identifier.
    """
    appeals_pending = total_appeals - appeals_acknowledged - appeals_withdrawn
    appeals_pending = max(0, appeals_pending)

    return {
        "snapshot_type":         "appeal_status_snapshot",
        "generated_at":          datetime.now(timezone.utc).isoformat(),
        "snapshot_id":           f"appeal-snap-{claim_id}-issue-{issue_id}",

        # Claim context
        "claim_id":              claim_id,
        "issue_id":              issue_id,
        "external_system":       external_system,

        # Appeal counts
        "total_appeals":         total_appeals,
        "appeals_pending":       appeals_pending,
        "appeals_acknowledged":  appeals_acknowledged,
        "appeals_credited":      appeals_credited,
        "appeals_withdrawn":     appeals_withdrawn,
        "appeals_not_credited":  (
            max(0, appeals_acknowledged - appeals_credited - appeals_withdrawn)
        ),

        # Per-appeal states
        "appeal_states":         appeal_states or {
            f"appeal-{claim_id}-issue-{issue_id}-external-001": "pending",
            f"appeal-{claim_id}-issue-{issue_id}-external-002": "pending",
        },

        # Overall status
        "overall_status": (
            "pending"
            if appeals_pending > 0 and appeals_acknowledged == 0
            else "partially_acknowledged"
            if appeals_acknowledged > 0 and appeals_pending > 0
            else "all_acknowledged"
            if appeals_acknowledged == total_appeals
            else "pending"
        ),
        "credit_issued_via_appeal": appeals_credited > 0,

        # What the snapshot does NOT do
        "contacts_external_system":   False,   # invariant
        "issues_credit_on_response":  False,   # invariant
        "compels_response":           False,   # invariant

        # Permanent invariants
        "credit_issued":              False,   # always — even if appeal is credited externally,
                                               # Dan-Go did not issue it
        "moves_money":                False,
        "execution_allowed":          False,
        "hard_enforcement":           False,
        "advisory":                   True,
        "appeal_only":                True,
        "authority":                  "none",
        "append_only":                True,
        "contestable":                True,
        "reopenable":                 True,

        "principle_1": "Appeal is not enforcement.",
        "principle_2": "Recognition remains external.",
    }


# ── Save ──────────────────────────────────────────────────────────────────────

def save_snapshot(doc: dict, out_path: Path | None = None) -> Path:
    if out_path is None:
        out_path = _EXAMPLES / "appeal-status-snapshot.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Snapshot advisory appeal status (no credit issued).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Appeal is not enforcement.
Recognition remains external.

Appeal states: pending, acknowledged, reconsidered, credited, not_credited, withdrawn

Examples:
  python bridge/gitsea/appeal/runtime/appeal_status_snapshot.py
  python bridge/gitsea/appeal/runtime/appeal_status_snapshot.py --save
  python bridge/gitsea/appeal/runtime/appeal_status_snapshot.py --json
  python bridge/gitsea/appeal/runtime/appeal_status_snapshot.py \\
      --claim housing-007 --issue 1 --total 2 --acknowledged 0
        """,
    )
    p.add_argument("--claim", default="housing-007")
    p.add_argument("--issue", type=int, default=1)
    p.add_argument("--total", type=int, default=2,
                   help="Total appeals recorded (default: 2)")
    p.add_argument("--acknowledged", type=int, default=0)
    p.add_argument("--credited", type=int, default=0)
    p.add_argument("--withdrawn", type=int, default=0)
    p.add_argument("--system", default="gitsea")
    p.add_argument("--save", action="store_true",
                   help="Save to appeal/examples/appeal-status-snapshot.json")
    p.add_argument("--json", action="store_true", dest="json_output")
    args = p.parse_args()

    doc = build_appeal_status_snapshot(
        claim_id=args.claim,
        issue_id=args.issue,
        total_appeals=args.total,
        appeals_acknowledged=args.acknowledged,
        appeals_credited=args.credited,
        appeals_withdrawn=args.withdrawn,
        external_system=args.system,
    )

    if args.save:
        out = save_snapshot(doc)
        print(f"Saved: {out}")

    if args.json_output:
        print(json.dumps(doc, indent=2, ensure_ascii=False))
        return

    # Default: human-readable
    print(f"\n{'='*60}")
    print(f"  Appeal Status Snapshot: {doc['snapshot_id']}")
    print(f"{'='*60}")
    print(f"  Claim:                {doc['claim_id']}  (issue #{doc['issue_id']})")
    print(f"  External system:      {doc['external_system']}")
    print()
    print(f"  Total appeals:        {doc['total_appeals']}")
    print(f"  Pending:              {doc['appeals_pending']}")
    print(f"  Acknowledged:         {doc['appeals_acknowledged']}")
    print(f"  Credited (external):  {doc['appeals_credited']}")
    print(f"  Withdrawn:            {doc['appeals_withdrawn']}")
    print(f"  Overall status:       {doc['overall_status']}")
    print()
    for aid, state in doc.get("appeal_states", {}).items():
        label = APPEAL_STATES.get(state, state)
        print(f"  [{aid[-20:]}...]  {state}  — {label[:40]}...")
    print(f"\n  credit_issued:           {doc['credit_issued']}")
    print(f"  credit_issued_via_appeal:{doc['credit_issued_via_appeal']}")
    print(f"  compels_response:         {doc['compels_response']}")
    print(f"  hard_enforcement:         {doc['hard_enforcement']}")
    print(f"  appeal_only:              {doc['appeal_only']}")
    print(f"  advisory:                 {doc['advisory']}")
    print(f"  authority:                {doc['authority']}")
    print(f"\n  \"{doc['principle_1']}\"")
    print(f"  \"{doc['principle_2']}\"")
    print()


if __name__ == "__main__":
    main()
