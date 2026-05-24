#!/usr/bin/env python3
"""
federation_branching.py — dango-gitsea-bridge / federation-aware plan branching

Compute the branch activation status of a claim based on the
negotiation state of the claims it depends on.

No claim exists alone. A plan may branch on:
  - another claim's active plan (dependency met)
  - another claim's dignity state (dignity_violation → blocked)
  - another claim's negotiation status (contested/open → paused)
  - federation_condition_met events (explicit propagated conditions)

This module is READ-ONLY. It computes — it does not write events.
To record propagated conditions, use federation_condition_propagation.py.
To record activation, use federation_activation.py.

Propagation is ADVISORY. No execution is triggered.

Branch status values:
  active  — all dependencies satisfied; claim can proceed
  paused  — upstream claims still negotiating; wait
  blocked — upstream has dignity_violation or formal rejection
  unknown — insufficient information to determine

CLI:
  python runtime/federation_branching.py --claim-id housing-002
  python runtime/federation_branching.py --claim-id housing-002 --json
  python runtime/federation_branching.py --all-claims
  python runtime/federation_branching.py --all-claims --verbose
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from sutable_log import read_all
from claim_federation import load_federation_events, build_federation_map

# ── Constants ─────────────────────────────────────────────────────────────────

_DIGNITY_OBJECTION_TYPE = "dignity_violation"
_BLOCKED_PLAN_STATUSES  = frozenset({"rejected", "superseded", "corrected"})
_PLAN_TREE_TYPES        = frozenset({"plan_tree_created", "plan_tree_amended", "plan_tree_corrected"})


# ── Helper: derive claim negotiation state from plans.jsonl ───────────────────

def _load_plan_events(claim_id: str) -> list[dict[str, Any]]:
    return [e for e in read_all("plans") if e.get("claim_id") == claim_id]


def _has_active_plan(claim_id: str, plan_events: list[dict[str, Any]] | None = None) -> bool:
    """Return True if the claim has a computed or formally selected active plan."""
    events = plan_events if plan_events is not None else _load_plan_events(claim_id)
    if not events:
        return False
    # Check for formal active_plan_selected event
    for ev in reversed(events):
        if ev.get("event_type") == "active_plan_selected":
            return bool(ev.get("selected_plan_id"))
    # Fallback: use active_plan_selector
    try:
        from active_plan_selector import select_active_plan
        result = select_active_plan(claim_id)
        return result.get("result") == "active"
    except ImportError:
        return False


def _has_dignity_violation(claim_id: str, plan_events: list[dict[str, Any]] | None = None) -> bool:
    """Return True if any plan for this claim has an unresolved dignity_violation objection."""
    events = plan_events if plan_events is not None else _load_plan_events(claim_id)
    for ev in events:
        if (ev.get("event_type") == "plan_objected"
                and ev.get("objection_type") == _DIGNITY_OBJECTION_TYPE):
            return True
    return False


def _is_formally_rejected(claim_id: str, plan_events: list[dict[str, Any]] | None = None) -> bool:
    """Return True if all known plans are rejected/superseded."""
    events = plan_events if plan_events is not None else _load_plan_events(claim_id)
    plan_ids = {e.get("plan_id") for e in events if e.get("event_type") in _PLAN_TREE_TYPES}
    if not plan_ids:
        return False
    # A claim is "formally rejected" only if every plan it has is in a blocked status
    for ev in events:
        if ev.get("event_type") == "plan_rejected" and ev.get("plan_id") in plan_ids:
            plan_ids.discard(ev.get("plan_id"))
    return len(plan_ids) == 0


def _negotiation_status_of(claim_id: str) -> str:
    """
    Return the negotiation status string for a claim:
    empty / open / signalled / contested / active.
    """
    try:
        from reflective_memory import compute_memory
        mem = compute_memory(claim_id)
        if "error" not in mem:
            return mem.get("negotiation_status", "unknown")
    except ImportError:
        pass
    return "unknown"


def _active_conditions(claim_id: str) -> set[str]:
    """
    Return the set of conditions present in the active plan tree for this claim,
    plus any learned_conditions from reflective memory.
    """
    conditions: set[str] = set()
    try:
        from reflective_memory import extract_prior_knowledge, extract_conditions
        pk = extract_prior_knowledge(claim_id)
        if pk:
            conditions.update(pk.get("learned_conditions", []))
            # Also extract from the active plan tree itself
            active_plan_id = pk.get("active_plan_id", "")
            if active_plan_id:
                from sutable_log import read_all as _read
                plan_events = [e for e in _read("plans") if e.get("claim_id") == claim_id]
                for ev in plan_events:
                    if ev.get("plan_id") == active_plan_id and ev.get("event_type") in _PLAN_TREE_TYPES:
                        tree = ev.get("plan_tree", {})
                        conditions.update(extract_conditions(tree))
    except ImportError:
        pass
    return conditions


def _fed_conditions_met(
    upstream_claim_id: str,
    fed_events: list[dict[str, Any]],
) -> set[str]:
    """Return the set of conditions formally marked as met for an upstream claim."""
    return {
        ev.get("condition", "")
        for ev in fed_events
        if ev.get("event_type") == "federation_condition_met"
        and ev.get("depends_on_claim_id") == upstream_claim_id
        and ev.get("condition")
    }


def _fed_conditions_blocked(
    upstream_claim_id: str,
    fed_events: list[dict[str, Any]],
) -> bool:
    """Return True if any federation_condition_blocked event targets this upstream claim."""
    return any(
        ev.get("event_type") == "federation_condition_blocked"
        and ev.get("depends_on_claim_id") == upstream_claim_id
        for ev in fed_events
    )


# ── Core: compute branch status for one claim ─────────────────────────────────

def compute_branch_status(
    claim_id: str,
    fmap: dict[str, Any],
    fed_events: list[dict[str, Any]],
    *,
    _plan_cache: dict[str, list] | None = None,
) -> dict[str, Any]:
    """
    Compute the branch activation status of a claim given its federation context.

    Returns:
      {
        "claim_id":          str,
        "branch_status":     "active" | "paused" | "blocked" | "unknown",
        "blocking_claims":   [claim_id, ...],
        "pausing_claims":    [claim_id, ...],
        "activation_dependencies": [
          {
            "claim_id":      str,
            "relationship":  str,
            "status":        "met" | "paused" | "blocked" | "unknown",
            "conditions_met": [str, ...],
          }, ...
        ],
        "negotiation_status": str,
      }

    Advisory — does not write any events.
    """
    if _plan_cache is None:
        _plan_cache = {}

    info = fmap.get(claim_id, {})
    upstream_claims = info.get("depends_on", []) + info.get("blocked_by", [])

    # For enables: the upstream that enables this claim
    enabled_by = info.get("enabled_by", [])

    all_upstream = list(dict.fromkeys(upstream_claims + enabled_by))  # deduplicate, preserve order

    activation_deps: list[dict[str, Any]] = []
    blocking: list[str]  = []
    pausing:  list[str]  = []

    for up_id in all_upstream:
        # Determine relationship type
        if up_id in info.get("depends_on", []):
            rel = "depends_on"
        elif up_id in info.get("blocked_by", []):
            rel = "blocked_by"
        elif up_id in info.get("enabled_by", []):
            rel = "enabled_by"
        else:
            rel = "unknown"

        # Load plan events (cached)
        if up_id not in _plan_cache:
            _plan_cache[up_id] = _load_plan_events(up_id)
        up_events = _plan_cache[up_id]

        # 1. Check for explicit federation_condition_blocked (strongest signal)
        if _fed_conditions_blocked(up_id, fed_events):
            dep_status = "blocked"
            blocking.append(up_id)
            activation_deps.append({
                "claim_id":       up_id,
                "relationship":   rel,
                "status":         "blocked",
                "conditions_met": [],
                "reason":         "federation_condition_blocked event",
            })
            continue

        # 2. Dignity violation on upstream → this claim is blocked
        if _has_dignity_violation(up_id, up_events):
            blocking.append(up_id)
            activation_deps.append({
                "claim_id":       up_id,
                "relationship":   rel,
                "status":         "blocked",
                "conditions_met": [],
                "reason":         "dignity_violation objection on upstream plan",
            })
            continue

        # 3. Formally rejected upstream → blocked
        if _is_formally_rejected(up_id, up_events):
            blocking.append(up_id)
            activation_deps.append({
                "claim_id":       up_id,
                "relationship":   rel,
                "status":         "blocked",
                "conditions_met": [],
                "reason":         "all upstream plans formally rejected",
            })
            continue

        # 4. Active plan found → dependency met
        if _has_active_plan(up_id, up_events):
            conds_met = sorted(
                _fed_conditions_met(up_id, fed_events) | _active_conditions(up_id)
            )
            dep_status = "met"
            activation_deps.append({
                "claim_id":       up_id,
                "relationship":   rel,
                "status":         "met",
                "conditions_met": conds_met,
                "reason":         "upstream has active plan",
            })
            continue

        # 5. No active plan yet → paused
        neg_status = _negotiation_status_of(up_id)
        pausing.append(up_id)
        activation_deps.append({
            "claim_id":          up_id,
            "relationship":      rel,
            "status":            "paused",
            "conditions_met":    [],
            "reason":            f"upstream negotiation_status={neg_status!r}",
        })

    # Determine overall branch status
    if blocking:
        branch_status = "blocked"
    elif pausing:
        branch_status = "paused"
    elif all_upstream:
        branch_status = "active"
    else:
        # No upstream dependencies — this claim is self-standing
        branch_status = "active"

    return {
        "claim_id":               claim_id,
        "branch_status":          branch_status,
        "blocking_claims":        blocking,
        "pausing_claims":         pausing,
        "activation_dependencies": activation_deps,
        "negotiation_status":     _negotiation_status_of(claim_id),
    }


# ── Batch: all claims in federation ──────────────────────────────────────────

def compute_all_branch_statuses(
    fmap: dict[str, Any],
    fed_events: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Return branch status for every claim in the federation map."""
    _plan_cache: dict[str, list] = {}
    return {
        cid: compute_branch_status(cid, fmap, fed_events, _plan_cache=_plan_cache)
        for cid in sorted(fmap)
    }


# ── Display ───────────────────────────────────────────────────────────────────

def _print_status(result: dict[str, Any], verbose: bool) -> None:
    status = result["branch_status"]
    icon   = {"active": "✓", "paused": "⏸", "blocked": "✗", "unknown": "?"}.get(status, "?")
    print(f"\n{icon} {result['claim_id']}  [{status}]")

    deps = result.get("activation_dependencies", [])
    if deps:
        print("  dependencies:")
        for d in deps:
            s = d["status"]
            di = {"met": "✓", "paused": "⏸", "blocked": "✗", "unknown": "?"}.get(s, "?")
            rel_str = f"({d['relationship']})"
            print(f"    {di} {d['claim_id']:20s} {rel_str:15s} {s}")
            if verbose:
                if d.get("conditions_met"):
                    for c in d["conditions_met"]:
                        print(f"         condition: {c} ✓")
                if d.get("reason"):
                    print(f"         reason:    {d['reason']}")
    else:
        print("  (no upstream dependencies — self-standing)")

    if result.get("negotiation_status"):
        print(f"  negotiation_status: {result['negotiation_status']}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="federation_branching",
        description=(
            "Compute branch activation status of claims based on federation dependencies. "
            "Read-only — does not write events."
        ),
    )
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--claim-id", metavar="CLAIM_ID",
                   help="Compute branch status for one claim")
    g.add_argument("--all-claims", action="store_true",
                   help="Compute branch status for all claims in federation")
    p.add_argument("--json",          action="store_true", dest="json_output")
    p.add_argument("--verbose", "-v", action="store_true")
    return p.parse_args()


def main() -> None:
    args = _parse_args()

    fed_events = load_federation_events()
    if not fed_events:
        print("No federation events found in sutable/federation.jsonl.", file=sys.stderr)
        if args.json_output:
            print(json.dumps({}, indent=2))
        sys.exit(0)

    fmap = build_federation_map(fed_events)

    if args.all_claims:
        statuses = compute_all_branch_statuses(fmap, fed_events)
        if args.json_output:
            print(json.dumps(statuses, indent=2, ensure_ascii=False))
        else:
            for cid in sorted(statuses):
                _print_status(statuses[cid], verbose=args.verbose)
        return

    cid = args.claim_id
    result = compute_branch_status(cid, fmap, fed_events)

    if args.json_output:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        _print_status(result, verbose=args.verbose)


if __name__ == "__main__":
    main()
