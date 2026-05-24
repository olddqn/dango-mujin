#!/usr/bin/env python3
"""
memory_snapshot.py — dango-gitsea-bridge / reflective memory layer

View the current reflective memory state for a claim.

Shows:
  - All memory snapshots (from sutable/memory.jsonl)
  - Latest memory record (authoritative)
  - Prior knowledge summary (for world model integration)
  - Diff from computed current state (if plans.jsonl has changed since snapshot)

This is a read-only query tool. It does not append events.
To create a new snapshot: use memory_append.py.

CLI:
  python runtime/memory_snapshot.py --claim-id housing-001
  python runtime/memory_snapshot.py --claim-id housing-001 --json
  python runtime/memory_snapshot.py --claim-id housing-001 --prior-knowledge
  python runtime/memory_snapshot.py --claim-id housing-001 --diff
  python runtime/memory_snapshot.py --all-claims
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from sutable_log import read_all
from reflective_memory import compute_memory, extract_prior_knowledge


# ── Snapshot reader ───────────────────────────────────────────────────────────

def get_snapshots(claim_id: str) -> list[dict[str, Any]]:
    """Return all memory_snapshot_created events for a claim, in order."""
    return [
        ev for ev in read_all("memory")
        if ev.get("claim_id") == claim_id
        and ev.get("event_type") == "memory_snapshot_created"
    ]


def get_latest_snapshot(claim_id: str) -> dict[str, Any] | None:
    """Return the most recent memory snapshot for a claim, or None."""
    snaps = get_snapshots(claim_id)
    return snaps[-1] if snaps else None


def all_claim_ids_with_memory() -> list[str]:
    """Return claim_ids that have at least one memory snapshot."""
    ids: set[str] = set()
    for ev in read_all("memory"):
        cid = ev.get("claim_id")
        if cid and ev.get("event_type") == "memory_snapshot_created":
            ids.add(cid)
    return sorted(ids)


# ── Diff computation ──────────────────────────────────────────────────────────

def compute_diff(
    snapshot: dict[str, Any],
    current: dict[str, Any],
) -> dict[str, Any]:
    """
    Compare a stored snapshot against the current computed memory.

    Returns a diff dict highlighting what has changed since the snapshot.
    """
    changes: list[str] = []

    # Active plan changed?
    snap_active = snapshot.get("active_plan_id", "")
    curr_active = current.get("active_plan_id", "")
    if snap_active != curr_active:
        changes.append(f"active_plan_id: {snap_active!r} → {curr_active!r}")

    # Negotiation status changed?
    snap_status = snapshot.get("negotiation_status", "")
    curr_status = current.get("negotiation_status", "")
    if snap_status != curr_status:
        changes.append(f"negotiation_status: {snap_status!r} → {curr_status!r}")

    # New learned conditions?
    snap_lc = set(snapshot.get("learned_conditions", []))
    curr_lc = set(current.get("learned_conditions", []))
    added_lc   = curr_lc - snap_lc
    removed_lc = snap_lc - curr_lc
    if added_lc:
        changes.append(f"learned_conditions added: {sorted(added_lc)}")
    if removed_lc:
        changes.append(f"learned_conditions removed: {sorted(removed_lc)}")

    # Contest count changed?
    snap_cc = snapshot.get("contest_count", 0)
    curr_cc = current.get("contest_count", 0)
    if snap_cc != curr_cc:
        changes.append(f"contest_count: {snap_cc} → {curr_cc}")

    # Plans event count (new events since snapshot)?
    snap_basis  = snapshot.get("snapshot_basis", {})
    curr_basis  = current.get("snapshot_basis", {})
    snap_events = snap_basis.get("plans_event_count", 0)
    curr_events = curr_basis.get("plans_event_count", 0)
    new_events  = curr_events - snap_events
    if new_events > 0:
        changes.append(f"{new_events} new plan event(s) since snapshot")

    return {
        "snapshot_memory_id": snapshot.get("memory_id", ""),
        "changes":            changes,
        "is_stale":           bool(changes),
        "new_events_since":   max(0, new_events),
    }


# ── Display ───────────────────────────────────────────────────────────────────

def _print_snapshot(
    claim_id: str,
    latest: dict[str, Any] | None,
    all_snaps: list[dict[str, Any]],
    diff: dict[str, Any] | None,
    verbose: bool,
) -> None:
    print(f"Memory Snapshot — {claim_id}")

    if not latest:
        print("  (no memory snapshots — run memory_append.py to create one)")
        return

    print(f"  latest_memory_id:     {latest.get('memory_id', '?')}")
    print(f"  snapshot_count:       {len(all_snaps)}")
    print(f"  negotiation_status:   {latest.get('negotiation_status', '?')}")
    print(f"  active_plan_id:       {latest.get('active_plan_id') or '(none)'}")
    print(f"  correction_depth:     {latest.get('correction_chain_depth', 0)}")
    print(f"  contest_count:        {latest.get('contest_count', 0)}")
    lc = latest.get("learned_conditions", [])
    print(f"  learned_conditions:   {lc or '(none)'}")
    print(f"  summary:              {latest.get('summary', '')}")

    if diff:
        if diff.get("is_stale"):
            print(f"\n  ⚠ STALE — {diff['new_events_since']} new plan event(s) since snapshot")
            for change in diff["changes"]:
                print(f"    • {change}")
            print(f"  Run memory_append.py --claim-id {claim_id} to update.")
        else:
            print(f"\n  ✓ Up to date (no changes since snapshot)")

    if verbose:
        ts = latest.get("timestamp", "")[:19].replace("T", " ")
        print(f"\n  Timestamp: {ts}")
        basis = latest.get("snapshot_basis", {})
        print(f"  Based on {basis.get('plans_event_count', 0)} plan event(s)")

        sups = latest.get("prior_supports", [])
        if sups:
            print(f"\n  Support signals:")
            for s in sups:
                print(f"    {s['plan_id']:40s}  +{s['count']}")

        objs = latest.get("prior_objections", [])
        if objs:
            print(f"\n  Objection signals:")
            for o in objs:
                types = ", ".join(o.get("by_type", {}).keys())
                print(f"    {o['plan_id']:40s}  -{o['count']} [{types}]")

        if len(all_snaps) > 1:
            print(f"\n  Snapshot history ({len(all_snaps)}):")
            for s in all_snaps:
                ts_s = s.get("timestamp", "")[:19].replace("T", " ")
                print(f"    {s.get('memory_id'):25s}  {ts_s}  {s.get('negotiation_status')}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="memory_snapshot",
        description="View reflective memory state for a claim.",
    )
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--claim-id", metavar="CLAIM_ID")
    g.add_argument("--all-claims", action="store_true")
    p.add_argument("--json",           action="store_true", dest="json_output")
    p.add_argument("--verbose", "-v",  action="store_true")
    p.add_argument("--prior-knowledge", action="store_true",
                   help="Output the prior_knowledge block (for world model integration).")
    p.add_argument("--diff", action="store_true",
                   help="Compare stored snapshot against current plans.jsonl state.")
    return p.parse_args()


def main() -> None:
    args = _parse_args()

    if args.all_claims:
        cids = all_claim_ids_with_memory()
        if not cids:
            print("No memory snapshots found.", file=sys.stderr)
            return
        for i, cid in enumerate(cids):
            if i > 0:
                print()
            snaps = get_snapshots(cid)
            latest = snaps[-1] if snaps else None
            if args.json_output:
                print(json.dumps(latest, indent=2, ensure_ascii=False))
            else:
                _print_snapshot(cid, latest, snaps, None, verbose=args.verbose)
        return

    cid    = args.claim_id
    snaps  = get_snapshots(cid)
    latest = snaps[-1] if snaps else None

    if args.prior_knowledge:
        pk = extract_prior_knowledge(cid)
        if args.json_output or not pk:
            print(json.dumps(pk, indent=2, ensure_ascii=False))
        else:
            print(f"Prior Knowledge — {cid}")
            if not pk:
                print("  (no memory snapshots)")
                return
            print(f"  memory_id:           {pk.get('memory_id')}")
            print(f"  active_plan_id:      {pk.get('active_plan_id') or '(none)'}")
            print(f"  negotiation_status:  {pk.get('negotiation_status')}")
            print(f"  learned_conditions:  {pk.get('learned_conditions') or '(none)'}")
            print(f"  known_objection_types: {pk.get('known_objection_types') or '(none)'}")
            print(f"  correction_depth:    {pk.get('correction_depth', 0)}")
            print(f"  summary:             {pk.get('summary')}")
        return

    diff = None
    if args.diff and latest:
        current = compute_memory(cid)
        diff    = compute_diff(latest, current)

    if args.json_output:
        out: dict[str, Any] = {
            "claim_id":       cid,
            "snapshot_count": len(snaps),
            "latest":         latest,
        }
        if diff:
            out["diff"] = diff
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        _print_snapshot(cid, latest, snaps, diff, verbose=args.verbose)


if __name__ == "__main__":
    main()
