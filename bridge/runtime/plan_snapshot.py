#!/usr/bin/env python3
"""
plan_snapshot.py — dango-gitsea-bridge / plan append-only layer

Build a compact snapshot of the plan correction chain for a given claim.

The snapshot shows:
  - active plan (the latest uncorrected plan)
  - correction chain (v1 → v2 → v3, ...)
  - abandoned plans (plan trees with abandoned task bundles)
  - associated task bundles per plan
  - correction chain depth

Nothing is deleted. The snapshot is a read-only view of the su-table.

Terminology:
  active    — the plan_tree event that has not been superseded by a correction
  corrected — a plan that has been superseded by a newer plan_tree_corrected event
  amended   — a plan that was the source of a plan_tree_amended event (still active)
  abandoned — a plan whose task bundle was abandoned

CLI:
  python runtime/plan_snapshot.py --claim-id housing-001
  python runtime/plan_snapshot.py --claim-id housing-001 --json
  python runtime/plan_snapshot.py --all-claims
  python runtime/plan_snapshot.py --all-claims --verbose
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from sutable_log import read_all

# ── Plan event type sets ──────────────────────────────────────────────────────

_PLAN_TREE_TYPES = frozenset({
    "plan_tree_created",
    "plan_tree_amended",
    "plan_tree_corrected",
})

_BUNDLE_TYPES = frozenset({
    "task_bundle_created",
    "task_bundle_blocked",
    "task_bundle_ready",
    "task_bundle_abandoned",
})


# ── Snapshot builder ──────────────────────────────────────────────────────────

def build_snapshot(claim_id: str) -> dict[str, Any]:
    """
    Build a plan snapshot for the given claim_id.

    Reads all events from plans.jsonl and computes:
      - The active plan (latest uncorrected plan tree)
      - The correction chain
      - All associated task bundles per plan
      - Summary statistics

    Returns:
        Snapshot dict.
    """
    all_events = read_all("plans")
    claim_events = [e for e in all_events if e.get("claim_id") == claim_id]

    if not claim_events:
        return {
            "claim_id":              claim_id,
            "active_plan":           None,
            "correction_chain_depth": 0,
            "plans":                 [],
            "bundles":               [],
            "error":                 f"No plan events found for claim_id: {claim_id!r}",
        }

    # Collect plan tree events (plan_id → event)
    plan_events: dict[str, dict[str, Any]] = {}
    for ev in claim_events:
        et  = ev.get("event_type", "")
        pid = ev.get("plan_id")
        if et in _PLAN_TREE_TYPES and pid:
            plan_events[pid] = ev

    # Collect task bundle events (bundle_id → latest status event)
    bundle_events: dict[str, list[dict[str, Any]]] = {}
    for ev in claim_events:
        et  = ev.get("event_type", "")
        bid = ev.get("bundle_id")
        if et in _BUNDLE_TYPES and bid:
            bundle_events.setdefault(bid, []).append(ev)

    # Determine which plans are superseded (corrected)
    corrected_by: dict[str, str] = {}  # old_plan_id → new_plan_id
    for pid, ev in plan_events.items():
        et = ev.get("event_type", "")
        if et == "plan_tree_corrected":
            old = ev.get("corrects_plan_id", "")
            if old:
                corrected_by[old] = pid
        elif et == "plan_tree_amended":
            # Amended plans remain active — record the amendment relationship
            src = ev.get("amends_plan_id", "")
            if src and src not in corrected_by:
                corrected_by[src] = f"{pid} (amendment)"  # soft reference

    # Find plans with abandoned bundles
    abandoned_plan_ids: set[str] = set()
    for bid, bevents in bundle_events.items():
        latest = bevents[-1]
        if latest.get("event_type") == "task_bundle_abandoned":
            dpid = _derive_plan_for_bundle(bid, claim_events)
            if dpid:
                abandoned_plan_ids.add(dpid)

    # Build plan record list (chronological order)
    plan_records: list[dict[str, Any]] = []
    for pid, ev in sorted(plan_events.items(), key=lambda x: x[1].get("timestamp", "")):
        et = ev.get("event_type", "")

        # Determine status
        if pid in corrected_by:
            ref = corrected_by[pid]
            if "(amendment)" in ref:
                status = "amended"
            else:
                status = "corrected"
        elif pid in abandoned_plan_ids:
            status = "abandoned"
        else:
            status = "active"

        # Bundles derived from this plan
        plan_bundles = [
            bid for bid, bevents in bundle_events.items()
            if any(e.get("derived_from_plan_id") == pid for e in bevents)
        ]

        record: dict[str, Any] = {
            "plan_id":    pid,
            "event_type": et,
            "status":     status,
            "timestamp":  ev.get("timestamp", ""),
        }

        if et == "plan_tree_corrected":
            record["corrects_plan_id"]  = ev.get("corrects_plan_id", "")
            record["correction_reason"] = ev.get("correction_reason", "")
        elif et == "plan_tree_amended":
            record["amends_plan_id"]   = ev.get("amends_plan_id", "")
            record["amendment_reason"] = ev.get("amendment_reason", "")

        if pid in corrected_by:
            ref = corrected_by[pid]
            if "(amendment)" not in ref:
                record["corrected_by"] = ref

        if plan_bundles:
            record["bundles"] = plan_bundles

        if ev.get("plan_tree_hash"):
            record["plan_tree_hash"] = ev["plan_tree_hash"][:16] + "…"

        plan_records.append(record)

    # Find active plan (last uncorrected plan tree)
    active_plan: str | None = None
    for rec in reversed(plan_records):
        if rec["status"] == "active":
            active_plan = rec["plan_id"]
            break

    # Compute correction chain depth
    # Start from the earliest plan, follow corrected_by links
    chain_depth = _compute_chain_depth(corrected_by)

    # Build bundle records
    bundle_records: list[dict[str, Any]] = []
    for bid, bevents in bundle_events.items():
        created = next(
            (e for e in bevents if e.get("event_type") == "task_bundle_created"), None
        )
        latest  = bevents[-1]
        latest_status = latest.get("event_type", "").replace("task_bundle_", "")
        brecord: dict[str, Any] = {
            "bundle_id":            bid,
            "status":               latest_status,
            "derived_from_plan_id": (created or {}).get("derived_from_plan_id", ""),
            "task_count":           (created or {}).get("task_count", 0),
            "blocked_count":        (created or {}).get("blocked_count", 0),
        }
        if (created or {}).get("bundle_status"):
            brecord["bundle_status"] = (created or {})["bundle_status"]
        bundle_records.append(brecord)

    return {
        "claim_id":              claim_id,
        "active_plan":           active_plan,
        "correction_chain_depth": chain_depth,
        "plan_count":            len(plan_records),
        "bundle_count":          len(bundle_records),
        "plans":                 plan_records,
        "bundles":               bundle_records,
    }


def _derive_plan_for_bundle(bundle_id: str, claim_events: list[dict]) -> str | None:
    """Find the derived_from_plan_id for a given bundle_id."""
    for ev in claim_events:
        if ev.get("bundle_id") == bundle_id and ev.get("event_type") == "task_bundle_created":
            return ev.get("derived_from_plan_id")
    return None


def _compute_chain_depth(corrected_by: dict[str, str]) -> int:
    """
    Compute the longest correction chain depth.
    depth = max number of correction hops from root to leaf.
    """
    if not corrected_by:
        return 0
    # corrected_by: old → new
    # Count nodes that are "old" (have been corrected at least once)
    # The depth is the length of the longest chain
    all_olds = set(corrected_by.keys())
    all_news = set(corrected_by.values())
    roots = all_olds - all_news  # plans that were corrected but not themselves corrections
    if not roots:
        roots = all_olds  # fallback

    max_depth = 0
    for root in roots:
        depth = 0
        current = root
        seen: set[str] = set()
        while current in corrected_by and current not in seen:
            seen.add(current)
            current = corrected_by[current]
            depth += 1
        max_depth = max(max_depth, depth)
    return max_depth


# ── CLI ───────────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="plan_snapshot",
        description="Build a plan correction chain snapshot from sutable/plans.jsonl.",
    )
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--claim-id",
        metavar="CLAIM_ID",
        help="Show snapshot for a specific claim.",
    )
    group.add_argument(
        "--all-claims",
        action="store_true",
        default=False,
        help="Show snapshot for all claims in plans.jsonl.",
    )
    p.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output JSON (default when stdout is not a terminal).",
    )
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        default=False,
        help="Include plan tree hashes and full correction reasons.",
    )
    return p.parse_args()


def _all_claim_ids() -> list[str]:
    events = read_all("plans")
    ids: set[str] = {e["claim_id"] for e in events if "claim_id" in e}
    return sorted(ids)


_STATUS_ICONS = {
    "active":    "✓",
    "corrected": "↩",
    "amended":   "✏",
    "abandoned": "✗",
}


def _print_snapshot(snap: dict[str, Any], verbose: bool = False) -> None:
    cid   = snap["claim_id"]
    apid  = snap.get("active_plan") or "(none)"
    depth = snap.get("correction_chain_depth", 0)
    error = snap.get("error")

    print(f"Claim:          {cid}")
    if error:
        print(f"  ✗ {error}")
        return

    print(f"Active plan:    {apid}")
    print(f"Chain depth:    {depth}")
    print(f"Plans:          {snap.get('plan_count', 0)}")
    print(f"Bundles:        {snap.get('bundle_count', 0)}")
    print()

    plans = snap.get("plans", [])
    if plans:
        print("── PLAN HISTORY ──────────────────────────────────────────────")
        for p in plans:
            pid    = p["plan_id"]
            status = p["status"]
            icon   = _STATUS_ICONS.get(status, "?")
            ts     = p.get("timestamp", "")[:19].replace("T", " ")
            print(f"  {icon} {pid}  [{status}]")
            if verbose and p.get("plan_tree_hash"):
                print(f"      hash: {p['plan_tree_hash']}")
            if p.get("corrects_plan_id"):
                reason = p.get("correction_reason", "")
                corr   = p["corrects_plan_id"]
                print(f"      corrects: {corr}")
                if reason:
                    print(f"      reason: {reason}")
            if p.get("corrected_by"):
                print(f"      ↳ corrected by: {p['corrected_by']}")
            if p.get("amends_plan_id"):
                reason = p.get("amendment_reason", "")
                print(f"      amends: {p['amends_plan_id']}")
                if reason:
                    print(f"      reason: {reason}")
            if p.get("bundles"):
                print(f"      bundles: {', '.join(p['bundles'])}")
            if ts:
                print(f"      {ts}")
        print()

    bundles = snap.get("bundles", [])
    if bundles:
        print("── TASK BUNDLES ──────────────────────────────────────────────")
        for b in bundles:
            bid    = b["bundle_id"]
            status = b["status"]
            dfpid  = b.get("derived_from_plan_id", "")
            tc     = b.get("task_count", 0)
            bc     = b.get("blocked_count", 0)
            bstatus = b.get("bundle_status", "")
            icon   = _STATUS_ICONS.get(status, "?")
            print(f"  {icon} {bid}  [{status}]")
            if dfpid:
                print(f"      derived from: {dfpid}")
            if tc:
                print(f"      tasks: {tc} total, {bc} blocked")
            if bstatus:
                print(f"      bundle_status: {bstatus}")
        print()


def main() -> None:
    args = _parse_args()

    if args.all_claims:
        claim_ids = _all_claim_ids()
        if not claim_ids:
            print("No plan events found in plans.jsonl.", file=sys.stderr)
            sys.exit(0)
        snapshots = [build_snapshot(cid) for cid in claim_ids]
        if args.json or not sys.stdout.isatty():
            print(json.dumps(snapshots, indent=2, ensure_ascii=False))
        else:
            for snap in snapshots:
                _print_snapshot(snap, verbose=args.verbose)
                print()
    else:
        snap = build_snapshot(args.claim_id)
        if args.json or not sys.stdout.isatty():
            print(json.dumps(snap, indent=2, ensure_ascii=False))
        else:
            _print_snapshot(snap, verbose=args.verbose)


if __name__ == "__main__":
    main()
