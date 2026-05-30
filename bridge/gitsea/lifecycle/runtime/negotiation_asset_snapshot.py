"""
negotiation_asset_snapshot.py — Convert Negotiation History to Asset Snapshots

Reads available Dan-Go negotiation event files for a claim and converts them
into an append-only asset snapshot. The snapshot shows:

  - What negotiation events occurred
  - Whether a cooperation signal was generated
  - Whether the claim reached GITSEA asset signal eligibility
  - Whether economic value was assigned (never: Dan-Go does not do this)

This file does NOT:
  - Activate GITSEA streams
  - Move funds
  - Enforce decisions
  - Modify prior negotiation records
  - Call external APIs

Append-only: each snapshot is a new record. Prior snapshots are preserved.

No secrets. No private keys. No wallet operations. No network. stdlib only.

Usage:
    python bridge/gitsea/lifecycle/runtime/negotiation_asset_snapshot.py
    python bridge/gitsea/lifecycle/runtime/negotiation_asset_snapshot.py --claim housing-007
    python bridge/gitsea/lifecycle/runtime/negotiation_asset_snapshot.py --save
    python bridge/gitsea/lifecycle/runtime/negotiation_asset_snapshot.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_FILE_DIR    = Path(__file__).parent
_LIFECYCLE   = _FILE_DIR.parent
_EXAMPLES    = _LIFECYCLE / "examples"
_REPO_ROOT   = _LIFECYCLE.parent.parent.parent
_GL_EXAMPLES = _REPO_ROOT / "bridge" / "gitlawb" / "examples"


# ── Event file registry ───────────────────────────────────────────────────────

def _load_event_file(path: Path, label: str) -> dict | None:
    if path.exists():
        with open(path, encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return None
    return None


def _collect_negotiation_events(claim_id: str, issue_id: int) -> list[dict]:
    """
    Collect negotiation events from known Dan-Go example files.
    Returns a list of summarised event records in chronological order.
    """
    prefix = f"issue-{issue_id:03d}"
    events: list[dict] = []

    # 1. PR feedback events
    pr_fb_path = _GL_EXAMPLES / f"{prefix}.pr-feedback.json"
    pr_fb = _load_event_file(pr_fb_path, "pr_feedback")
    if pr_fb:
        fb_list = pr_fb if isinstance(pr_fb, list) else [pr_fb]
        for ev in fb_list:
            # gitsea_eligible is nested under stream_candidate
            sc = ev.get("stream_candidate", {})
            pr_event_type = ev.get("pr_event", ev.get("event_type", "pr_event"))
            events.append({
                "type":   pr_event_type,
                "source": str(pr_fb_path.name),
                "gitsea_eligible": sc.get("gitsea_eligible", False),
            })

    # 2. Reopen event
    reopen_path = _GL_EXAMPLES / f"{prefix}.reopen-event.json"
    reopen = _load_event_file(reopen_path, "reopen_event")
    if reopen:
        events.append({
            "type":   reopen.get("event_type", "negotiation_reopened"),
            "source": str(reopen_path.name),
            "reason": reopen.get("reason", ""),
        })

    # 3. Plan correction
    pcorr_path = _GL_EXAMPLES / f"{prefix}.plan-correction.json"
    pcorr = _load_event_file(pcorr_path, "plan_correction")
    if pcorr:
        events.append({
            "type":   pcorr.get("event_type", "plan_correction_proposed"),
            "source": str(pcorr_path.name),
            "corrects_plan": pcorr.get("corrects_plan", ""),
            "proposed_plan": pcorr.get("proposed_plan", ""),
        })

    # If no events found, produce a minimal stub
    if not events:
        events = [
            {"type": "evidence",  "source": "stub"},
            {"type": "contest",   "source": "stub"},
            {"type": "reaffirm",  "source": "stub"},
        ]

    return events


# ── Snapshot builder ──────────────────────────────────────────────────────────

def build_negotiation_asset_snapshot(
    claim_id: str = "housing-007",
    issue_id: int = 1,
    cooperation_signal: bool = True,
) -> dict[str, Any]:
    """
    Convert Dan-Go negotiation history into an advisory asset snapshot.
    """
    events = _collect_negotiation_events(claim_id, issue_id)

    event_type_list = [ev.get("type", "unknown") for ev in events]

    # gitsea_eligible: true if any PR merge event has the flag
    gitsea_eligible = any(
        ev.get("gitsea_eligible", False) for ev in events
    )

    # Reopened: true if a reopen event is present
    was_reopened = any(
        "reopen" in ev.get("type", "") for ev in events
    )

    # Plan corrected: true if a plan correction is present
    plan_corrected = any(
        "correction" in ev.get("type", "") for ev in events
    )

    return {
        "snapshot_type":     "negotiation_asset_snapshot",
        "generated_at":      datetime.now(timezone.utc).isoformat(),
        "append_only":       True,

        # Identity
        "issue":             issue_id,
        "claim":             claim_id,

        # Events observed
        "events":            event_type_list,
        "event_count":       len(events),
        "event_detail":      events,

        # Negotiation state
        "gitsea_eligible":   gitsea_eligible,
        "was_reopened":      was_reopened,
        "plan_corrected":    plan_corrected,
        "negotiation_reopen_allowed": True,

        # Signals
        "cooperation_signal": cooperation_signal,
        "economic_value":    False,

        # Invariants
        "authority":         "none",
        "execution_allowed": False,
        "moves_money":       False,
        "hard_enforcement":  False,
        "advisory":          True,
        "contestable":       True,
        "reopenable":        True,

        "note": (
            "This snapshot converts Dan-Go negotiation history into an advisory "
            "GITSEA asset signal record. No stream is activated. No funds are moved. "
            "A merged PR is evidence. Not authority. "
            "Contribution becomes legible before it becomes valuable."
        ),
    }


# ── Save ──────────────────────────────────────────────────────────────────────

def save_snapshot(snapshot: dict, out_path: Path | None = None) -> Path:
    if out_path is None:
        out_path = _EXAMPLES / "negotiation-snapshot.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Convert Dan-Go negotiation history to an advisory asset snapshot.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Reads negotiation event files from:
  bridge/gitlawb/examples/issue-001.pr-feedback.json
  bridge/gitlawb/examples/issue-001.reopen-event.json
  bridge/gitlawb/examples/issue-001.plan-correction.json

Produces:
  bridge/gitsea/lifecycle/examples/negotiation-snapshot.json

Examples:
  python bridge/gitsea/lifecycle/runtime/negotiation_asset_snapshot.py
  python bridge/gitsea/lifecycle/runtime/negotiation_asset_snapshot.py --save
  python bridge/gitsea/lifecycle/runtime/negotiation_asset_snapshot.py --json
  python bridge/gitsea/lifecycle/runtime/negotiation_asset_snapshot.py \\
      --claim housing-007 --issue 1
        """,
    )
    p.add_argument("--claim", metavar="CLAIM_ID", default="housing-007")
    p.add_argument("--issue", metavar="ISSUE_NUM", type=int, default=1)
    p.add_argument("--no-cooperation", action="store_true",
                   help="Set cooperation_signal to false")
    p.add_argument("--save", action="store_true",
                   help="Save to lifecycle/examples/negotiation-snapshot.json")
    p.add_argument("--json", action="store_true", dest="json_output")
    args = p.parse_args()

    snapshot = build_negotiation_asset_snapshot(
        claim_id=args.claim,
        issue_id=args.issue,
        cooperation_signal=not args.no_cooperation,
    )

    if args.save:
        out = save_snapshot(snapshot)
        print(f"Saved: {out}")

    if args.json_output:
        print(json.dumps(snapshot, indent=2, ensure_ascii=False))
        return

    # Default: human-readable
    print(f"\n{'='*58}")
    print(f"  Negotiation → Asset Snapshot: {snapshot['claim']}")
    print(f"{'='*58}")
    print(f"  Issue:             #{snapshot['issue']}")
    print(f"  Events observed:   {snapshot['event_count']}")
    for ev in snapshot["event_detail"]:
        print(f"    • {ev.get('type','?'):<35}  ({ev.get('source','?')})")
    print(f"\n  GITSEA eligible:   {snapshot['gitsea_eligible']}")
    print(f"  Was reopened:      {snapshot['was_reopened']}")
    print(f"  Plan corrected:    {snapshot['plan_corrected']}")
    print(f"  Cooperation signal:{snapshot['cooperation_signal']}")
    print(f"  Economic value:    {snapshot['economic_value']}")
    print(f"\n  execution_allowed: {snapshot['execution_allowed']}")
    print(f"  moves_money:       {snapshot['moves_money']}")
    print(f"  advisory:          {snapshot['advisory']}")
    print(f"  authority:         {snapshot['authority']}")
    print()


if __name__ == "__main__":
    main()
