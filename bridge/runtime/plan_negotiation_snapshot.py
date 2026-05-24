#!/usr/bin/env python3
"""
plan_negotiation_snapshot.py — dango-gitsea-bridge / plan negotiation layer

Compute and display the negotiation state for a claim.

The snapshot shows:
  - All plans and their negotiation status
  - Support and objection summaries per plan
  - Contest chains (which plan contests which)
  - Computed active plan (from selection rules, without writing an event)
  - Formal active plan (if active_plan_selected event exists)
  - Overall negotiation_status for the claim

negotiation_status values:
  open      — plans proposed, no negotiation signals yet
  active    — formal active_plan_selected event exists
  contested — at least one plan_contested event exists
  signalled — support or objection signals exist but no contest/selection
  empty     — no plan_tree events found for this claim

CLI:
  python runtime/plan_negotiation_snapshot.py --claim-id housing-001
  python runtime/plan_negotiation_snapshot.py --claim-id housing-001 --json
  python runtime/plan_negotiation_snapshot.py --all-claims --verbose
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from sutable_log import read_all
from plan_contest_resolver import (
    aggregate_signals,
    build_contest_chain,
    build_full_contest_graph,
    compute_correction_depth,
    generate_summary,
    get_plan_statuses,
    _load_plan_events,
    _get_plan_ids,
    _PLAN_TREE_TYPES,
)
from active_plan_selector import select_active_plan


# ── Snapshot builder ──────────────────────────────────────────────────────────

def build_snapshot(claim_id: str) -> dict[str, Any]:
    """
    Build the full negotiation snapshot for a claim.

    Returns:
    {
      "claim_id":             str,
      "negotiation_status":   str,
      "active_plan":          str | None,  # from active_plan_selected event
      "computed_active_plan": str | None,  # from deterministic selection rules
      "plans":                [...],
      "contested_plans":      [...],
      "rejected_plans":       [...],
      "superseded_plans":     [...],
      "support_summary":      {...},
      "objection_summary":    {...},
      "contest_chains":       [...],
    }
    """
    events   = _load_plan_events(claim_id)
    plan_ids = _get_plan_ids(events)

    if not plan_ids:
        return {
            "claim_id":             claim_id,
            "negotiation_status":   "empty",
            "active_plan":          None,
            "computed_active_plan": None,
            "plans":                [],
            "contested_plans":      [],
            "rejected_plans":       [],
            "superseded_plans":     [],
            "support_summary":      {},
            "objection_summary":    {},
            "contest_chains":       [],
        }

    signals  = aggregate_signals(events)
    depths   = compute_correction_depth(events)
    statuses = get_plan_statuses(events)
    contests = build_full_contest_graph(events)

    # Build per-plan records
    plans: list[dict[str, Any]] = []
    for pid in plan_ids:
        ts = ""
        for ev in events:
            if ev.get("plan_id") == pid and ev.get("event_type") in _PLAN_TREE_TYPES:
                ts = ev.get("timestamp", "")
                break
        sigs   = signals.get(pid, {})
        status = statuses.get(pid, "open")
        plans.append({
            "plan_id":           pid,
            "status":            status,
            "correction_depth":  depths.get(pid, 0),
            "timestamp":         ts,
            "support_count":     sigs.get("support_count", 0),
            "objection_count":   sigs.get("objection_count", 0),
            "support_speakers":  sigs.get("support_speakers", []),
            "support_reasons":   sigs.get("support_reasons", []),
            "objections_by_type":sigs.get("objections_by_type", {}),
            "objection_speakers":sigs.get("objection_speakers", []),
            "objection_reasons": sigs.get("objection_reasons", []),
        })

    # Categorised plan lists
    contested_plans  = [p["plan_id"] for p in plans if p["status"] == "contested"]
    rejected_plans   = [p["plan_id"] for p in plans if p["status"] == "rejected"]
    superseded_plans = [p["plan_id"] for p in plans if p["status"] in ("superseded", "corrected")]

    # Support / objection summaries (keyed by plan_id)
    support_summary: dict[str, Any] = {}
    objection_summary: dict[str, Any] = {}
    for p in plans:
        pid = p["plan_id"]
        if p["support_count"] > 0:
            support_summary[pid] = {
                "count":   p["support_count"],
                "speakers":p["support_speakers"],
                "reasons": p["support_reasons"],
            }
        if p["objection_count"] > 0:
            objection_summary[pid] = {
                "count":    p["objection_count"],
                "by_type":  p["objections_by_type"],
                "speakers": p["objection_speakers"],
                "reasons":  p["objection_reasons"],
            }

    # Formal active plan (from active_plan_selected event)
    formal_active: str | None = None
    for ev in reversed(events):
        if ev.get("event_type") == "active_plan_selected":
            formal_active = ev.get("selected_plan_id")
            break

    # Computed active plan (from selection rules, not written to log)
    selection_result = select_active_plan(claim_id)
    computed_active = selection_result.get("selected_plan_id")

    # Negotiation status
    negotiation_status = _compute_negotiation_status(events, formal_active, contests)

    return {
        "claim_id":             claim_id,
        "negotiation_status":   negotiation_status,
        "active_plan":          formal_active,
        "computed_active_plan": computed_active,
        "plans":                plans,
        "contested_plans":      contested_plans,
        "rejected_plans":       rejected_plans,
        "superseded_plans":     superseded_plans,
        "support_summary":      support_summary,
        "objection_summary":    objection_summary,
        "contest_chains":       contests,
    }


def _compute_negotiation_status(
    events: list[dict[str, Any]],
    formal_active: str | None,
    contests: list[dict[str, Any]],
) -> str:
    """
    Compute the overall negotiation status of a claim's plan negotiation.

    Priority order:
      active    — formal active_plan_selected event exists
      contested — at least one plan_contested event
      signalled — support or objection signals exist
      open      — plan(s) exist, no signals
      empty     — no plan events
    """
    has_plans     = any(ev.get("event_type") in _PLAN_TREE_TYPES for ev in events)
    has_contested = bool(contests)
    has_signals   = any(
        ev.get("event_type") in ("plan_supported", "plan_objected")
        for ev in events
    )

    if not has_plans:
        return "empty"
    if formal_active:
        return "active"
    if has_contested:
        return "contested"
    if has_signals:
        return "signalled"
    return "open"


# ── Display ───────────────────────────────────────────────────────────────────

def _print_snapshot(snap: dict[str, Any], verbose: bool) -> None:
    cid    = snap["claim_id"]
    status = snap["negotiation_status"]
    active = snap.get("active_plan") or snap.get("computed_active_plan") or "(none)"
    formal = snap.get("active_plan")
    comp   = snap.get("computed_active_plan")

    print(f"Negotiation Snapshot — {cid}")
    print(f"  negotiation_status:   {status}")
    if formal:
        print(f"  active_plan:          {formal}  [formal selection]")
    elif comp:
        print(f"  computed_active_plan: {comp}  [computed — not yet recorded]")
    else:
        print(f"  active_plan:          (none)")

    plans = snap.get("plans", [])
    print(f"\n  Plans ({len(plans)}):")
    for p in plans:
        pid    = p["plan_id"]
        pstat  = p["status"]
        sup    = p["support_count"]
        obj    = p["objection_count"]
        depth  = p["correction_depth"]
        active_marker = " ← active" if (pid == formal or (not formal and pid == comp)) else ""
        print(f"    {pid:35s}  [{pstat:12s}]  "
              f"sup={sup}  obj={obj}  depth={depth}{active_marker}")
        if verbose:
            if p.get("support_reasons"):
                for r in p["support_reasons"]:
                    print(f"      + {r}")
            if p.get("objection_reasons"):
                for r in p["objection_reasons"]:
                    otype = list(p["objections_by_type"].keys())
                    print(f"      ✗ [{otype[0] if otype else '?'}] {r}")

    contests = snap.get("contest_chains", [])
    if contests:
        print(f"\n  Contests ({len(contests)}):")
        for c in contests:
            print(f"    {c['contested']:30s} -.->|contested_by| {c['counterplan']}")
            if verbose and c.get("reason"):
                print(f"      reason: {c['reason']}")

    sup_sum = snap.get("support_summary", {})
    obj_sum = snap.get("objection_summary", {})

    if sup_sum or obj_sum:
        print(f"\n  Signal summary:")
        for pid in {*sup_sum.keys(), *obj_sum.keys()}:
            s = sup_sum.get(pid, {}).get("count", 0)
            o = obj_sum.get(pid, {}).get("count", 0)
            print(f"    {pid}: +{s} support / -{o} objection")


# ── All-claims listing ────────────────────────────────────────────────────────

def _all_claim_ids() -> list[str]:
    """Return all claim_ids that have plan events."""
    ids: set[str] = set()
    for ev in read_all("plans"):
        cid = ev.get("claim_id")
        if cid:
            ids.add(cid)
    return sorted(ids)


# ── CLI ───────────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="plan_negotiation_snapshot",
        description="Compute negotiation state for competing plans of a claim.",
    )
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--claim-id", metavar="CLAIM_ID",
                   help="Show snapshot for a single claim.")
    g.add_argument("--all-claims", action="store_true",
                   help="Show snapshots for all claims with plan events.")
    p.add_argument(
        "--json",
        action="store_true",
        default=False,
        dest="json_output",
        help="Output as JSON.",
    )
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        default=False,
        help="Show support/objection reasons.",
    )
    return p.parse_args()


def main() -> None:
    args = _parse_args()

    if args.all_claims:
        claim_ids = _all_claim_ids()
        if not claim_ids:
            print("No claims with plan events found.", file=sys.stderr)
            sys.exit(0)
        all_snaps = [build_snapshot(cid) for cid in claim_ids]
        if args.json_output:
            print(json.dumps(all_snaps, indent=2, ensure_ascii=False))
        else:
            for i, snap in enumerate(all_snaps):
                if i > 0:
                    print()
                _print_snapshot(snap, verbose=args.verbose)
        return

    snap = build_snapshot(args.claim_id)
    if args.json_output:
        print(json.dumps(snap, indent=2, ensure_ascii=False))
    else:
        _print_snapshot(snap, verbose=args.verbose)


if __name__ == "__main__":
    main()
