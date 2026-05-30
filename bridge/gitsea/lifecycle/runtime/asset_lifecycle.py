"""
asset_lifecycle.py — Dan-Go × GITSEA Asset Lifecycle Representation

Represents the full lifecycle from Claim to Asset Signal:

  Claim
    → Issue
    → Negotiation
    → Contribution
    → Cooperation Signal
    → Asset Signal

This module does NOT:
  - Assign economic value
  - Enforce reputation
  - Move funds
  - Activate GITSEA streams
  - Perform on-chain operations
  - Call external APIs

All output is advisory. All snapshots are immutable once generated.
Append-only: new snapshots add to the record; prior snapshots are never
modified.

Core principle:
  "Contribution becomes legible before it becomes valuable."

No secrets. No private keys. No wallet operations. No network. stdlib only.

Usage:
    python bridge/gitsea/lifecycle/runtime/asset_lifecycle.py
    python bridge/gitsea/lifecycle/runtime/asset_lifecycle.py --claim housing-007
    python bridge/gitsea/lifecycle/runtime/asset_lifecycle.py --claim housing-007 --save
    python bridge/gitsea/lifecycle/runtime/asset_lifecycle.py --claim housing-007 --json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_FILE_DIR  = Path(__file__).parent
_LIFECYCLE = _FILE_DIR.parent
_EXAMPLES  = _LIFECYCLE / "examples"
_REPO_ROOT = _LIFECYCLE.parent.parent.parent


# ── Lifecycle stage definitions ───────────────────────────────────────────────

LIFECYCLE_STAGES = [
    "claim_created",
    "issue_drafted",
    "negotiation_opened",
    "pr_submitted",
    "pr_merged",
    "contribution_recorded",
    "cooperation_signal_generated",
    "asset_signal_generated",
]

STAGE_LABELS = {
    "claim_created":               "Claim Created",
    "issue_drafted":               "Issue Drafted",
    "negotiation_opened":          "Negotiation Opened",
    "pr_submitted":                "PR Submitted",
    "pr_merged":                   "PR Merged (evidence accepted)",
    "contribution_recorded":       "Contribution Recorded",
    "cooperation_signal_generated":"Cooperation Signal Generated",
    "asset_signal_generated":      "Asset Signal Generated",
}

# Stage → what it means for Dan-Go and GITSEA
STAGE_NOTES = {
    "claim_created": (
        "A claim enters the Dan-Go protocol. "
        "Authority: none. No commitment is made."
    ),
    "issue_drafted": (
        "A scoped issue is generated from an applicable prerequisite. "
        "It is a negotiation invitation, not a command."
    ),
    "negotiation_opened": (
        "Participants contribute evidence, contest, or reaffirm. "
        "All steps are append-only. No adjudicator."
    ),
    "pr_submitted": (
        "A PR is submitted as an evidence contribution. "
        "Merge does not establish truth."
    ),
    "pr_merged": (
        "PR merge is recorded. gitsea_eligible: true is possible. "
        "Negotiation remains reopenable. A merged PR is evidence. Not authority."
    ),
    "contribution_recorded": (
        "Contribution is recorded in the append-only event log. "
        "No reward is assigned. No reputation is changed."
    ),
    "cooperation_signal_generated": (
        "An advisory cooperation signal is generated from participation patterns. "
        "It is not a score. It is not enforced. It is advisory."
    ),
    "asset_signal_generated": (
        "GITSEA may observe this signal to assess stream eligibility. "
        "Dan-Go does not activate the stream. Economic value is optional."
    ),
}


# ── Lifecycle snapshot builder ────────────────────────────────────────────────

def build_lifecycle_snapshot(
    claim_id: str,
    issue_id: int | None = None,
    current_stage: str = "contribution_recorded",
    participants: list[str] | None = None,
    cooperation_signal: float = 0.75,
    notes: str | None = None,
) -> dict[str, Any]:
    """
    Build an advisory lifecycle snapshot for a claim.

    Parameters
    ----------
    claim_id : str
        The Dan-Go claim identifier (e.g. "housing-007").
    issue_id : int | None
        Associated GitHub issue number.
    current_stage : str
        Current stage in LIFECYCLE_STAGES.
    participants : list[str] | None
        Participant identifiers (pseudonymous). No personal data.
    cooperation_signal : float
        Advisory cooperation signal (0.0–1.0). Not a score. Not enforced.
    notes : str | None
        Optional human-readable note.
    """
    if current_stage not in LIFECYCLE_STAGES:
        raise ValueError(
            f"Unknown stage: {current_stage!r}. "
            f"Valid stages: {LIFECYCLE_STAGES}"
        )

    stage_index = LIFECYCLE_STAGES.index(current_stage)
    completed   = LIFECYCLE_STAGES[:stage_index + 1]
    pending     = LIFECYCLE_STAGES[stage_index + 1:]

    return {
        "snapshot_type":     "asset_lifecycle_snapshot",
        "generated_at":      datetime.now(timezone.utc).isoformat(),
        "claim_id":          claim_id,
        "issue_id":          issue_id,

        # Lifecycle position
        "current_stage":     current_stage,
        "stage_label":       STAGE_LABELS[current_stage],
        "stage_note":        STAGE_NOTES[current_stage],
        "completed_stages":  completed,
        "pending_stages":    pending,

        # Signals
        "cooperation_signal": cooperation_signal,
        "asset_signal":       stage_index >= LIFECYCLE_STAGES.index("asset_signal_generated"),
        "economic_value":     False,   # never set by Dan-Go

        # Participants — pseudonymous, advisory only
        "participants":       participants or [],
        "participant_count":  len(participants or []),

        # Optional note
        "notes": notes or (
            "This snapshot records the current lifecycle position of a Dan-Go "
            "claim as it relates to GITSEA asset signalling. "
            "Contribution becomes legible before it becomes valuable."
        ),

        # Invariants — must remain true at every stage
        "authority":          "none",
        "execution_allowed":  False,
        "moves_money":        False,
        "hard_enforcement":   False,
        "advisory":           True,
        "append_only":        True,
        "contestable":        True,
        "reopenable":         True,
        "economic_value_note": (
            "Dan-Go does not create economic value. "
            "Dan-Go records cooperation before value emerges. "
            "GITSEA may observe this snapshot when assessing stream eligibility."
        ),
    }


# ── Save ──────────────────────────────────────────────────────────────────────

def save_snapshot(snapshot: dict, out_path: Path | None = None) -> Path:
    claim_id = snapshot.get("claim_id", "unknown").replace("/", "-")
    if out_path is None:
        out_path = _EXAMPLES / f"asset-lifecycle-{claim_id}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Build a Dan-Go × GITSEA asset lifecycle snapshot.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Lifecycle stages (in order):
  1. claim_created
  2. issue_drafted
  3. negotiation_opened
  4. pr_submitted
  5. pr_merged
  6. contribution_recorded        ← default
  7. cooperation_signal_generated
  8. asset_signal_generated

Core principle:
  "Contribution becomes legible before it becomes valuable."

Examples:
  python bridge/gitsea/lifecycle/runtime/asset_lifecycle.py --claim housing-007
  python bridge/gitsea/lifecycle/runtime/asset_lifecycle.py --claim housing-007 --json
  python bridge/gitsea/lifecycle/runtime/asset_lifecycle.py --claim housing-007 --save
  python bridge/gitsea/lifecycle/runtime/asset_lifecycle.py \\
      --claim housing-007 --stage cooperation_signal_generated --save
        """,
    )
    p.add_argument("--claim", metavar="CLAIM_ID", default="housing-007",
                   help="Claim identifier (default: housing-007)")
    p.add_argument("--issue", metavar="ISSUE_NUM", type=int, default=1,
                   help="Issue number (default: 1)")
    p.add_argument("--stage", metavar="STAGE", default="contribution_recorded",
                   choices=LIFECYCLE_STAGES,
                   help="Current lifecycle stage")
    p.add_argument("--participants", metavar="P", nargs="*",
                   default=["alice", "bob", "carol"],
                   help="Participant identifiers (pseudonymous)")
    p.add_argument("--cooperation", metavar="FLOAT", type=float, default=0.75,
                   help="Advisory cooperation signal 0.0–1.0 (default: 0.75)")
    p.add_argument("--save", action="store_true",
                   help="Save snapshot to lifecycle/examples/")
    p.add_argument("--json", action="store_true", dest="json_output",
                   help="Print full JSON")
    args = p.parse_args()

    try:
        snapshot = build_lifecycle_snapshot(
            claim_id=args.claim,
            issue_id=args.issue,
            current_stage=args.stage,
            participants=args.participants,
            cooperation_signal=args.cooperation,
        )
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    if args.save:
        out = save_snapshot(snapshot)
        print(f"Saved: {out}")

    if args.json_output:
        print(json.dumps(snapshot, indent=2, ensure_ascii=False))
        return

    # Default: human-readable
    print(f"\n{'='*58}")
    print(f"  Asset Lifecycle Snapshot: {snapshot['claim_id']}")
    print(f"{'='*58}")
    print(f"  Issue:          #{snapshot['issue_id']}")
    print(f"  Stage:          {snapshot['stage_label']}")
    print(f"  Note:           {snapshot['stage_note']}")
    print(f"\n  Completed stages ({len(snapshot['completed_stages'])}):")
    for s in snapshot["completed_stages"]:
        print(f"    ✓  {STAGE_LABELS[s]}")
    if snapshot["pending_stages"]:
        print(f"\n  Pending stages ({len(snapshot['pending_stages'])}):")
        for s in snapshot["pending_stages"]:
            print(f"    ○  {STAGE_LABELS[s]}")
    print(f"\n  Participants:       {', '.join(snapshot['participants']) or 'none'}")
    print(f"  Cooperation signal: {snapshot['cooperation_signal']}  (advisory, not a score)")
    print(f"  Asset signal:       {snapshot['asset_signal']}")
    print(f"  Economic value:     {snapshot['economic_value']}  (Dan-Go never sets this)")
    print(f"\n  execution_allowed:  {snapshot['execution_allowed']}")
    print(f"  moves_money:        {snapshot['moves_money']}")
    print(f"  advisory:           {snapshot['advisory']}")
    print(f"  authority:          {snapshot['authority']}")
    print()


if __name__ == "__main__":
    main()
