#!/usr/bin/env python3
"""
plan_contest_resolver.py — dango-gitsea-bridge / plan negotiation layer

Build contest chains, aggregate support/objection signals, and generate
negotiation summaries for competing plans.

This module is pure computation — it reads plans.jsonl and returns structured
data. It does not append events. It does not execute anything.

All logic is deterministic. No hidden scoring. No probabilistic ranking.
Every signal (support, objection, contest) is accounted for transparently.

Usage (library):
    from plan_contest_resolver import (
        build_contest_chain,
        aggregate_signals,
        compute_correction_depth,
        get_plan_statuses,
        generate_summary,
    )
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from sutable_log import read_all

# ── Event type constants ──────────────────────────────────────────────────────

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


# ── Data loading ──────────────────────────────────────────────────────────────

def _load_plan_events(claim_id: str) -> list[dict[str, Any]]:
    """Load all events from plans.jsonl for the given claim_id, in order."""
    return [
        ev for ev in read_all("plans")
        if ev.get("claim_id") == claim_id
    ]


def _get_plan_ids(events: list[dict[str, Any]]) -> list[str]:
    """Return all plan_ids (plan_tree_* events) in chronological order."""
    seen: list[str] = []
    seen_set: set[str] = set()
    for ev in events:
        pid = ev.get("plan_id", "")
        if pid and ev.get("event_type") in _PLAN_TREE_TYPES and pid not in seen_set:
            seen.append(pid)
            seen_set.add(pid)
    return seen


# ── Contest chain ─────────────────────────────────────────────────────────────

def build_contest_chain(events: list[dict[str, Any]]) -> dict[str, str]:
    """
    Build the contest relationship map.

    Returns:
        dict mapping contested_plan_id → counterplan_id.
        A plan may be contested by at most one counterplan (first-wins).
        Multiple contests of the same plan are recorded as additional entries
        with disambiguated keys, but primary entry uses the original plan_id.
    """
    chain: dict[str, str] = {}
    for ev in events:
        if ev.get("event_type") == "plan_contested":
            contested = ev.get("contested_plan_id", "")
            counterplan = ev.get("counterplan_id", "")
            if contested and counterplan:
                # First contest wins as primary
                if contested not in chain:
                    chain[contested] = counterplan
    return chain


def build_full_contest_graph(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Build all contest relationships as a list of records.

    Returns:
        [{"contested": plan_id, "counterplan": plan_id, "reason": str, "speaker": str, "timestamp": str}]
    """
    records = []
    for ev in events:
        if ev.get("event_type") == "plan_contested":
            records.append({
                "contested":    ev.get("contested_plan_id", ""),
                "counterplan":  ev.get("counterplan_id", ""),
                "reason":       ev.get("contest_reason", ""),
                "speaker":      ev.get("speaker", ""),
                "timestamp":    ev.get("timestamp", ""),
            })
    return records


# ── Signal aggregation ────────────────────────────────────────────────────────

def aggregate_signals(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """
    Aggregate support and objection signals per plan.

    Returns:
        {
          plan_id: {
            "support_count": int,
            "objection_count": int,
            "support_speakers": [did, ...],
            "support_reasons": [str, ...],
            "objections_by_type": {type: count},
            "objection_speakers": [did, ...],
            "objection_reasons": [str, ...],
          }
        }
    """
    result: dict[str, dict[str, Any]] = {}

    def _entry(pid: str) -> dict[str, Any]:
        if pid not in result:
            result[pid] = {
                "support_count":     0,
                "objection_count":   0,
                "support_speakers":  [],
                "support_reasons":   [],
                "objections_by_type": {},
                "objection_speakers": [],
                "objection_reasons":  [],
            }
        return result[pid]

    for ev in events:
        et = ev.get("event_type", "")
        pid = ev.get("plan_id", "")

        if et == "plan_supported" and pid:
            e = _entry(pid)
            e["support_count"] += 1
            speaker = ev.get("speaker", "")
            reason  = ev.get("support_reason", "")
            if speaker and speaker not in e["support_speakers"]:
                e["support_speakers"].append(speaker)
            if reason:
                e["support_reasons"].append(reason)

        elif et == "plan_objected" and pid:
            e = _entry(pid)
            e["objection_count"] += 1
            otype   = ev.get("objection_type", "other")
            speaker = ev.get("speaker", "")
            reason  = ev.get("objection_reason", "")
            e["objections_by_type"][otype] = e["objections_by_type"].get(otype, 0) + 1
            if speaker and speaker not in e["objection_speakers"]:
                e["objection_speakers"].append(speaker)
            if reason:
                e["objection_reasons"].append(reason)

    return result


# ── Correction depth ──────────────────────────────────────────────────────────

def compute_correction_depth(events: list[dict[str, Any]]) -> dict[str, int]:
    """
    Compute correction chain depth for each plan.

    A plan created as plan_tree_created has depth 0.
    A plan created as plan_tree_corrected (corrects plan X) has depth = depth(X) + 1.

    Returns:
        {plan_id: depth}
    """
    # Gather correction relationships: new_plan_id → corrects_plan_id
    corrects: dict[str, str] = {}
    for ev in events:
        if ev.get("event_type") == "plan_tree_corrected":
            pid = ev.get("plan_id", "")
            src = ev.get("corrects_plan_id", "")
            if pid and src:
                corrects[pid] = src

    all_plan_ids = _get_plan_ids(events)
    depths: dict[str, int] = {}

    def _depth(pid: str, visited: set[str]) -> int:
        if pid in depths:
            return depths[pid]
        if pid in visited:
            # Cycle guard — should not happen in well-formed data
            return 0
        visited.add(pid)
        src = corrects.get(pid)
        if src is None:
            depths[pid] = 0
        else:
            depths[pid] = _depth(src, visited) + 1
        return depths[pid]

    for pid in all_plan_ids:
        _depth(pid, set())

    return depths


# ── Plan status computation ───────────────────────────────────────────────────

def get_plan_statuses(events: list[dict[str, Any]]) -> dict[str, str]:
    """
    Compute the negotiation status of each plan_id.

    Status values (in decreasing precedence):
      rejected      — plan_rejected event exists for this plan
      superseded    — plan_superseded event exists, or corrected by another plan
      active        — active_plan_selected event names this plan as selected
      contested     — plan_contested event names this plan as contested_plan_id
      corrected     — plan_tree_corrected references this plan in corrects_plan_id
      active        — default for uncorrected plans with no negative signals

    Note: a plan can be both corrected (by plan_tree_corrected) and active
    if it's the most recent uncorrected plan in the chain. We use negotiation
    signals to determine status in this layer.
    """
    plan_ids = set(_get_plan_ids(events))
    statuses: dict[str, str] = {pid: "open" for pid in plan_ids}

    # Track correction chain: which plans are structurally corrected
    corrected_by: dict[str, str] = {}  # old_pid → new_pid
    for ev in events:
        if ev.get("event_type") == "plan_tree_corrected":
            old = ev.get("corrects_plan_id", "")
            new = ev.get("plan_id", "")
            if old and new:
                corrected_by[old] = new

    for pid in plan_ids:
        if pid in corrected_by:
            statuses[pid] = "corrected"

    # Apply negotiation signals (higher precedence than structural state)
    for ev in events:
        et  = ev.get("event_type", "")
        pid = ev.get("plan_id", "")

        if et == "plan_rejected" and pid in statuses:
            statuses[pid] = "rejected"

        elif et == "plan_superseded" and pid in statuses:
            statuses[pid] = "superseded"

    # Contest signals
    for ev in events:
        if ev.get("event_type") == "plan_contested":
            contested = ev.get("contested_plan_id", "")
            if contested in statuses and statuses[contested] not in ("rejected", "superseded"):
                statuses[contested] = "contested"

    # Active plan selection (highest precedence)
    for ev in events:
        if ev.get("event_type") == "active_plan_selected":
            sel = ev.get("selected_plan_id", "")
            if sel in statuses:
                statuses[sel] = "active"

    # Plans not corrected, not contested, not rejected/superseded → "open"
    # (open = proposed but not yet acted upon in negotiation)
    return statuses


# ── Full summary ──────────────────────────────────────────────────────────────

def generate_summary(claim_id: str) -> dict[str, Any]:
    """
    Generate a full negotiation summary for a claim.

    Returns a structured dict with:
      - all plan records + their signals
      - contest graph
      - correction depths
      - plan statuses
      - active plan (if selected)
    """
    events   = _load_plan_events(claim_id)
    plan_ids = _get_plan_ids(events)

    signals   = aggregate_signals(events)
    depths    = compute_correction_depth(events)
    statuses  = get_plan_statuses(events)
    contests  = build_full_contest_graph(events)

    plans: list[dict[str, Any]] = []
    for pid in plan_ids:
        entry: dict[str, Any] = {
            "plan_id":          pid,
            "status":           statuses.get(pid, "open"),
            "correction_depth": depths.get(pid, 0),
        }
        sigs = signals.get(pid, {})
        entry["support_count"]     = sigs.get("support_count", 0)
        entry["objection_count"]   = sigs.get("objection_count", 0)
        entry["support_speakers"]  = sigs.get("support_speakers", [])
        entry["objection_speakers"]= sigs.get("objection_speakers", [])
        entry["objections_by_type"]= sigs.get("objections_by_type", {})
        plans.append(entry)

    # Determine active plan from explicit selection events
    active_plan: str = ""
    for ev in reversed(events):
        if ev.get("event_type") == "active_plan_selected":
            active_plan = ev.get("selected_plan_id", "")
            break

    return {
        "claim_id":      claim_id,
        "active_plan":   active_plan,
        "plans":         plans,
        "contest_graph": contests,
        "plan_count":    len(plan_ids),
        "total_events":  len(events),
    }
