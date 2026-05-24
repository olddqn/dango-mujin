#!/usr/bin/env python3
"""
reflective_memory.py — dango-gitsea-bridge / reflective memory layer

Pure computation library: derive a memory record from plans.jsonl events.

A memory record summarises what a claim's negotiation history has produced:
  - which plan is active
  - what objections were raised (and what types)
  - what new conditions were learned from competing plans
  - how deep the correction chain is
  - how many contests occurred

This record feeds into the next world model cycle as "prior knowledge",
closing the loop:

  World Model → Plan Tree → Negotiation → Memory
                ↑                              |
                └──────────────────────────────┘
                        (prior_knowledge)

No events are written here. No files are created. This module only reads.
All state changes go through memory_append.py (append-only).

Absolute prohibitions:
  - No execution, no network, no external libraries
  - No mutation of existing records
  - No centralized authority — memory is derived, not decreed

CLI (read-only introspection):
  python runtime/reflective_memory.py --claim-id housing-001
  python runtime/reflective_memory.py --claim-id housing-001 --json
  python runtime/reflective_memory.py --claim-id housing-001 --verbose
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from sutable_log import read_all

# ── Plan event type constants ────────────────────────────────────────────────

_PLAN_TREE_TYPES = frozenset({
    "plan_tree_created",
    "plan_tree_amended",
    "plan_tree_corrected",
})

_NEGOTIATION_TYPES = frozenset({
    "plan_supported",
    "plan_objected",
    "plan_contested",
    "plan_rejected",
    "plan_superseded",
    "active_plan_selected",
})


# ── Condition extraction from plan trees ─────────────────────────────────────

def extract_conditions(plan_tree: dict[str, Any]) -> set[str]:
    """
    Walk a plan tree and collect all condition names from branch nodes.

    A 'condition' is the value of the 'condition' field on any branch node.
    These are the gating conditions the plan checks before proceeding.

    Returns a set of condition name strings.
    """
    found: set[str] = set()

    def _walk(node: Any) -> None:
        if not isinstance(node, dict):
            return
        if node.get("node_type") == "branch":
            cond = node.get("condition")
            if cond and isinstance(cond, str):
                found.add(cond)
        for child in node.get("children", []):
            _walk(child)
        _walk(node.get("true"))
        _walk(node.get("false"))

    _walk(plan_tree)
    return found


def _get_plan_tree(events: list[dict[str, Any]], plan_id: str) -> dict[str, Any]:
    """Return the plan_tree dict for a given plan_id, or {} if not found."""
    for ev in events:
        if ev.get("plan_id") == plan_id and ev.get("event_type") in _PLAN_TREE_TYPES:
            tree = ev.get("plan_tree")
            if isinstance(tree, dict):
                return tree
    return {}


# ── Memory computation ────────────────────────────────────────────────────────

def compute_memory(claim_id: str) -> dict[str, Any]:
    """
    Derive a memory record from plans.jsonl events for a claim.

    The memory record captures:
      active_plan_id         — current active plan (or computed if no formal selection)
      negotiation_status     — open / signalled / contested / active
      prior_objections       — objection signals per plan (typed, counted)
      prior_supports         — support signals per plan (counted)
      learned_conditions     — conditions in counterplans but not in contested plans
      correction_chain_depth — how deep the correction chain is
      contest_count          — number of competing plan proposals
      known_contested_plans  — plan_ids that were contested
      summary                — human-readable one-line summary

    Returns:
        dict suitable for use as memory record body (without event metadata).
        Returns {"error": "..."} if no plan events exist.
    """
    events = [ev for ev in read_all("plans") if ev.get("claim_id") == claim_id]

    if not events:
        return {"error": f"no plan events for claim_id: {claim_id!r}"}

    # ── Collect plan_ids ──────────────────────────────────────────────────────
    plan_ids: list[str] = []
    seen: set[str] = set()
    for ev in events:
        pid = ev.get("plan_id", "")
        if pid and ev.get("event_type") in _PLAN_TREE_TYPES and pid not in seen:
            plan_ids.append(pid)
            seen.add(pid)

    # ── Correction chain ──────────────────────────────────────────────────────
    corrected_by: dict[str, str] = {}   # old_pid → new_pid
    for ev in events:
        if ev.get("event_type") == "plan_tree_corrected":
            old = ev.get("corrects_plan_id", "")
            new = ev.get("plan_id", "")
            if old and new:
                corrected_by[old] = new

    def _correction_depth(pid: str, visited: set[str] | None = None) -> int:
        if visited is None:
            visited = set()
        if pid in visited:
            return 0  # cycle guard
        visited.add(pid)
        # Find if pid itself is a correction of something
        for ev in events:
            if ev.get("plan_id") == pid and ev.get("event_type") == "plan_tree_corrected":
                src = ev.get("corrects_plan_id", "")
                if src:
                    return _correction_depth(src, visited) + 1
        return 0

    correction_chain_depth = max((_correction_depth(pid) for pid in plan_ids), default=0)

    # ── Contest chains ────────────────────────────────────────────────────────
    contests: list[dict[str, str]] = []
    known_contested: list[str] = []
    for ev in events:
        if ev.get("event_type") == "plan_contested":
            contested   = ev.get("contested_plan_id", "")
            counterplan = ev.get("counterplan_id", "")
            reason      = ev.get("contest_reason", "")
            if contested and counterplan:
                contests.append({
                    "contested":   contested,
                    "counterplan": counterplan,
                    "reason":      reason,
                })
                if contested not in known_contested:
                    known_contested.append(contested)

    # ── Learned conditions (structural diff between contested and counterplan) ─
    learned_conditions: list[str] = []
    seen_conditions: set[str] = set()
    for c in contests:
        contested_tree   = _get_plan_tree(events, c["contested"])
        counterplan_tree = _get_plan_tree(events, c["counterplan"])
        if not contested_tree or not counterplan_tree:
            continue
        orig_conds  = extract_conditions(contested_tree)
        new_conds   = extract_conditions(counterplan_tree)
        added_conds = new_conds - orig_conds
        for cond in sorted(added_conds):
            if cond not in seen_conditions:
                learned_conditions.append(cond)
                seen_conditions.add(cond)

    # ── Support / objection signals ───────────────────────────────────────────
    prior_supports: list[dict[str, Any]] = []
    prior_objections: list[dict[str, Any]] = []

    # Aggregate per plan
    sup_map: dict[str, dict[str, Any]] = {}
    obj_map: dict[str, dict[str, Any]] = {}

    for ev in events:
        et  = ev.get("event_type", "")
        pid = ev.get("plan_id", "")

        if et == "plan_supported" and pid:
            e = sup_map.setdefault(pid, {"plan_id": pid, "count": 0, "reasons": []})
            e["count"] += 1
            r = ev.get("support_reason", "")
            if r:
                e["reasons"].append(r)

        elif et == "plan_objected" and pid:
            e = obj_map.setdefault(pid, {
                "plan_id": pid,
                "count": 0,
                "by_type": {},
                "reasons": [],
            })
            e["count"] += 1
            otype = ev.get("objection_type", "other")
            e["by_type"][otype] = e["by_type"].get(otype, 0) + 1
            r = ev.get("objection_reason", "")
            if r:
                e["reasons"].append(r)

    prior_supports   = list(sup_map.values())
    prior_objections = list(obj_map.values())

    # ── Active plan ───────────────────────────────────────────────────────────
    # First: check for explicit active_plan_selected event
    formal_active = ""
    for ev in reversed(events):
        if ev.get("event_type") == "active_plan_selected":
            formal_active = ev.get("selected_plan_id", "")
            break

    # Fallback: compute from selection rules (import lazily)
    computed_active = ""
    if not formal_active:
        try:
            from active_plan_selector import select_active_plan
            sel = select_active_plan(claim_id)
            if sel.get("result") == "active":
                computed_active = sel.get("selected_plan_id", "")
        except ImportError:
            pass

    active_plan_id = formal_active or computed_active

    # ── Negotiation status ────────────────────────────────────────────────────
    has_plans    = bool(plan_ids)
    has_contests = bool(contests)
    has_signals  = bool(prior_supports or prior_objections)

    if not has_plans:
        negotiation_status = "empty"
    elif formal_active:
        negotiation_status = "active"
    elif has_contests:
        negotiation_status = "contested"
    elif has_signals:
        negotiation_status = "signalled"
    else:
        negotiation_status = "open"

    # ── Snapshot basis ────────────────────────────────────────────────────────
    latest_hash = ""
    for ev in reversed(events):
        if ev.get("event_hash"):
            latest_hash = ev["event_hash"]
            break

    snapshot_basis = {
        "plans_event_count": len(events),
        "plan_count":        len(plan_ids),
        "latest_event_hash": latest_hash,
    }

    # ── Human-readable summary ────────────────────────────────────────────────
    total_objections = sum(o["count"] for o in prior_objections)
    total_supports   = sum(s["count"] for s in prior_supports)
    parts: list[str] = []
    if correction_chain_depth:
        parts.append(f"{correction_chain_depth} correction(s)")
    if contests:
        parts.append(f"{len(contests)} contest(s)")
    if total_objections:
        obj_types = sorted({
            t for o in prior_objections for t in o.get("by_type", {})
        })
        parts.append(f"{total_objections} objection(s) ({', '.join(obj_types)})")
    if total_supports:
        parts.append(f"{total_supports} support(s)")
    if learned_conditions:
        parts.append(f"learned: {', '.join(sorted(learned_conditions))}")
    if active_plan_id:
        parts.append(f"active: {active_plan_id}")

    summary = "; ".join(parts) if parts else "no negotiation activity"

    return {
        "active_plan_id":        active_plan_id,
        "negotiation_status":    negotiation_status,
        "prior_objections":      prior_objections,
        "prior_supports":        prior_supports,
        "learned_conditions":    learned_conditions,
        "correction_chain_depth": correction_chain_depth,
        "contest_count":         len(contests),
        "known_contested_plans": known_contested,
        "snapshot_basis":        snapshot_basis,
        "summary":               summary,
    }


# ── Memory ID generation ──────────────────────────────────────────────────────

def next_memory_id(claim_id: str) -> str:
    """
    Return the next sequential memory_id for a claim.

    Format: mem-{claim_id}-{n:03d}
    Reads existing memory.jsonl to determine n.
    """
    existing = read_all("memory")
    n = sum(
        1 for ev in existing
        if ev.get("claim_id") == claim_id
        and ev.get("event_type") == "memory_snapshot_created"
    )
    return f"mem-{claim_id}-{n + 1:03d}"


# ── Prior knowledge extraction (for world model integration) ──────────────────

def extract_prior_knowledge(claim_id: str) -> dict[str, Any]:
    """
    Extract the most recent prior knowledge summary for a claim.

    This reads memory.jsonl (not plans.jsonl) and returns the latest
    memory snapshot as a 'prior_knowledge' dict suitable for injection
    into a world model.

    Returns {} if no memory snapshots exist for the claim.
    """
    snapshots = [
        ev for ev in read_all("memory")
        if ev.get("claim_id") == claim_id
        and ev.get("event_type") == "memory_snapshot_created"
    ]
    if not snapshots:
        return {}

    latest = snapshots[-1]
    return {
        "memory_id":             latest.get("memory_id", ""),
        "active_plan_id":        latest.get("active_plan_id", ""),
        "negotiation_status":    latest.get("negotiation_status", ""),
        "learned_conditions":    latest.get("learned_conditions", []),
        "known_objection_types": sorted({
            t
            for o in latest.get("prior_objections", [])
            for t in o.get("by_type", {})
        }),
        "correction_depth":      latest.get("correction_chain_depth", 0),
        "contest_count":         latest.get("contest_count", 0),
        "summary":               latest.get("summary", ""),
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

def _print_memory(mem: dict[str, Any], verbose: bool) -> None:
    if "error" in mem:
        print(f"✗ {mem['error']}", file=sys.stderr)
        return

    print(f"Reflective Memory — {mem.get('_claim_id', '')}")
    print(f"  negotiation_status:    {mem['negotiation_status']}")
    print(f"  active_plan_id:        {mem['active_plan_id'] or '(none)'}")
    print(f"  correction_depth:      {mem['correction_chain_depth']}")
    print(f"  contest_count:         {mem['contest_count']}")
    print(f"  learned_conditions:    {mem['learned_conditions'] or '(none)'}")
    print(f"  summary:               {mem['summary']}")

    if verbose:
        basis = mem.get("snapshot_basis", {})
        print(f"\n  Snapshot basis:")
        print(f"    plans_event_count: {basis.get('plans_event_count', 0)}")
        print(f"    plan_count:        {basis.get('plan_count', 0)}")

        if mem.get("prior_supports"):
            print(f"\n  Support signals:")
            for s in mem["prior_supports"]:
                print(f"    {s['plan_id']:40s}  +{s['count']}")
                for r in s.get("reasons", []):
                    print(f"      + {r[:70]}")

        if mem.get("prior_objections"):
            print(f"\n  Objection signals:")
            for o in mem["prior_objections"]:
                types = ", ".join(o.get("by_type", {}).keys())
                print(f"    {o['plan_id']:40s}  -{o['count']} [{types}]")
                for r in o.get("reasons", []):
                    print(f"      ✗ {r[:70]}")

        if mem.get("known_contested_plans"):
            print(f"\n  Contested plans: {mem['known_contested_plans']}")


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="reflective_memory",
        description=(
            "Compute a reflective memory record from negotiation history. "
            "Read-only: does not write to any file."
        ),
    )
    p.add_argument("--claim-id", required=True, metavar="CLAIM_ID")
    p.add_argument("--json", action="store_true", dest="json_output")
    p.add_argument("--verbose", "-v", action="store_true")
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    mem  = compute_memory(args.claim_id)
    mem["_claim_id"] = args.claim_id  # carry claim_id for display

    if args.json_output:
        out = {k: v for k, v in mem.items() if k != "_claim_id"}
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        _print_memory(mem, verbose=args.verbose)


if __name__ == "__main__":
    main()
