#!/usr/bin/env python3
"""
plan_negotiation_graph.py — dango-gitsea-bridge / plan negotiation layer

Build a focused graph of plan negotiation events for a claim.

This graph shows:
  - Plan nodes (plan_tree_created/corrected/amended) with status
  - Support signal nodes (plan_supported)
  - Objection signal nodes (plan_objected)
  - Contest nodes (plan_contested)
  - Active plan selection nodes (active_plan_selected)

Edges:
  - plan_contest:   contested_plan -.->|contested_by| counterplan
  - plan_support:   plan_supported -> plan (support signals flow to plan)
  - plan_objection: plan_objected -> plan (objection signals flow to plan)
  - plan_correction: corrected_plan -.->|corrected_by| new_plan
  - active_selection: plan -.->|selected_as_active| active_plan_selected

Output format matches negotiation_graph.py graph dict:
  {
    "claim_id": str,
    "nodes":    [NodeDict, ...],
    "edges":    [EdgeDict, ...],
    "meta":     {...},
  }

CLI:
  python runtime/plan_negotiation_graph.py --claim-id housing-001
  python runtime/plan_negotiation_graph.py --claim-id housing-001 --json
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
    get_plan_statuses,
    _load_plan_events,
    _get_plan_ids,
    _PLAN_TREE_TYPES,
    _NEGOTIATION_TYPES,
)


# ── Node shape / style maps ───────────────────────────────────────────────────

_SHAPE: dict[str, str] = {
    "plan_tree_created":    "rect",
    "plan_tree_corrected":  "asymmetric",
    "plan_tree_amended":    "round",
    "plan_supported":       "rect",
    "plan_objected":        "hex",
    "plan_contested":       "hex",
    "plan_rejected":        "rect",
    "plan_superseded":      "rect",
    "active_plan_selected": "stadium",
}

# Status → style class
_STATUS_STYLE: dict[str, str] = {
    "active":     "planActive",
    "contested":  "planContested",
    "corrected":  "planCorrected",
    "superseded": "planSuperseded",
    "rejected":   "planRejected",
    "open":       "plan",
}

_EVENT_STYLE: dict[str, str] = {
    "plan_tree_created":    "plan",
    "plan_tree_corrected":  "planCorrected",
    "plan_tree_amended":    "planAmended",
    "plan_supported":       "planSupported",
    "plan_objected":        "planObjected",
    "plan_contested":       "planContested",
    "plan_rejected":        "planRejected",
    "plan_superseded":      "planSuperseded",
    "active_plan_selected": "planActive",
}

_ALL_PLAN_EVENT_TYPES: frozenset[str] = _PLAN_TREE_TYPES | _NEGOTIATION_TYPES


# ── Label builder ─────────────────────────────────────────────────────────────

def _trunc(s: str, n: int = 48) -> str:
    s = s.replace("\n", " ").replace('"', "'")
    return s[:n] + "…" if len(s) > n else s


def _label_for(ev: dict[str, Any], status_map: dict[str, str]) -> str:
    et  = ev.get("event_type", "")
    pid = ev.get("plan_id", "")

    match et:
        case "plan_tree_created":
            status = status_map.get(pid, "open")
            return f"Plan: {_trunc(pid, 40)}  [{status}]"
        case "plan_tree_corrected":
            status = status_map.get(pid, "corrected")
            reason = ev.get("correction_reason", "")
            s = f"↩ Correction: {_trunc(pid, 36)}"
            return s + (f"\n{_trunc(reason, 40)}" if reason else "")
        case "plan_tree_amended":
            reason = ev.get("amendment_reason", "")
            return f"✏ Amendment: {_trunc(pid, 36)}" + (f"\n{_trunc(reason, 36)}" if reason else "")
        case "plan_supported":
            reason = ev.get("support_reason", "")
            return f"✓ Support: {_trunc(reason, 44)}" if reason else "✓ Support"
        case "plan_objected":
            otype  = ev.get("objection_type", "")
            reason = ev.get("objection_reason", "")
            tag    = f"[{otype}] " if otype else ""
            return f"✗ Objection: {tag}{_trunc(reason, 38)}"
        case "plan_contested":
            contested   = ev.get("contested_plan_id", "")
            counterplan = ev.get("counterplan_id", "")
            reason      = ev.get("contest_reason", "")
            s = f"⚔ Contest: {_trunc(contested, 28)} ← {_trunc(counterplan, 28)}"
            return s + (f"\n{_trunc(reason, 44)}" if reason else "")
        case "plan_rejected":
            reason = ev.get("rejection_reason", "")
            return f"✗ Rejected: {_trunc(pid, 38)}" + (f"\n{_trunc(reason, 40)}" if reason else "")
        case "plan_superseded":
            by_id = ev.get("superseded_by", "")
            return f"Superseded: {_trunc(pid, 36)}" + (f" by {_trunc(by_id, 28)}" if by_id else "")
        case "active_plan_selected":
            sel = ev.get("selected_plan_id", "")
            return f"★ Active: {_trunc(sel, 44)}"
        case _:
            return _trunc(et.replace("_", " ").title())


# ── Graph builder ─────────────────────────────────────────────────────────────

def build_negotiation_graph(claim_id: str) -> dict[str, Any]:
    """
    Build a plan negotiation graph for a claim.

    Returns graph dict with nodes and edges.
    """
    events   = _load_plan_events(claim_id)
    plan_ids = _get_plan_ids(events)

    if not events:
        return {
            "claim_id": claim_id,
            "nodes":    [],
            "edges":    [],
            "meta":     {"error": f"No plan events for claim_id: {claim_id}"},
        }

    signals    = aggregate_signals(events)
    status_map = get_plan_statuses(events)

    # ── Build nodes ───────────────────────────────────────────────────────────
    nodes: list[dict[str, Any]] = []
    event_hash_to_id: dict[str, str] = {}
    plan_id_to_node:  dict[str, str] = {}  # plan_id → node_id (plan_tree_* events)

    for idx, ev in enumerate(events):
        node_id = f"pn{idx}"
        et      = ev.get("event_type", "")
        eh      = ev.get("event_hash", "")
        pid     = ev.get("plan_id", "")

        if eh:
            event_hash_to_id[eh] = node_id

        # Determine style: plan_tree_* nodes use status-based style
        if et in _PLAN_TREE_TYPES and pid:
            style = _STATUS_STYLE.get(status_map.get(pid, "open"), "plan")
            plan_id_to_node[pid] = node_id
        else:
            style = _EVENT_STYLE.get(et, "default")

        nodes.append({
            "id":           node_id,
            "event_type":   et,
            "timestamp":    ev.get("timestamp", ""),
            "event_hash":   eh,
            "label":        _label_for(ev, status_map),
            "shape":        _SHAPE.get(et, "rect"),
            "style":        style,
            "meta": {
                "plan_id":           ev.get("plan_id", ""),
                "contested_plan_id": ev.get("contested_plan_id", ""),
                "counterplan_id":    ev.get("counterplan_id", ""),
                "corrects_plan_id":  ev.get("corrects_plan_id", ""),
                "selected_plan_id":  ev.get("selected_plan_id", ""),
                "speaker":           ev.get("speaker", ""),
                "objection_type":    ev.get("objection_type", ""),
                "contest_reason":    ev.get("contest_reason", ""),
                "support_reason":    ev.get("support_reason", ""),
                "objection_reason":  ev.get("objection_reason", ""),
            },
        })

    # ── Build edges ───────────────────────────────────────────────────────────
    edges: list[dict[str, Any]] = []
    existing_pairs: set[tuple[str, str]] = set()

    def _add_edge(frm: str, to: str, kind: str, label: str = "") -> None:
        pair = (frm, to)
        if pair not in existing_pairs:
            e: dict[str, Any] = {"from": frm, "to": to, "kind": kind}
            if label:
                e["label"] = label
            edges.append(e)
            existing_pairs.add(pair)

    for idx, ev in enumerate(events):
        et  = ev.get("event_type", "")
        nid = f"pn{idx}"

        if et == "plan_tree_corrected":
            # corrected plan -.->|corrected_by| new plan
            old_pid = ev.get("corrects_plan_id", "")
            new_pid = ev.get("plan_id", "")
            if old_pid in plan_id_to_node and new_pid in plan_id_to_node:
                _add_edge(plan_id_to_node[old_pid], plan_id_to_node[new_pid],
                          "plan_correction", "corrected_by")

        elif et == "plan_contested":
            contested   = ev.get("contested_plan_id", "")
            counterplan = ev.get("counterplan_id", "")
            # contested plan -.->|contested_by| contest event
            if contested in plan_id_to_node:
                _add_edge(plan_id_to_node[contested], nid, "plan_contest", "contested_by")
            # contest event -->|counterplan| counterplan node
            if counterplan in plan_id_to_node:
                _add_edge(nid, plan_id_to_node[counterplan], "plan_contest", "counterplan")

        elif et == "plan_supported":
            pid = ev.get("plan_id", "")
            # support event -.->|supports| plan
            if pid in plan_id_to_node:
                _add_edge(nid, plan_id_to_node[pid], "plan_support", "supports")

        elif et == "plan_objected":
            pid = ev.get("plan_id", "")
            # objection event -.->|objects_to| plan
            if pid in plan_id_to_node:
                _add_edge(nid, plan_id_to_node[pid], "plan_objection", "objects_to")

        elif et == "active_plan_selected":
            sel = ev.get("selected_plan_id", "")
            # selected plan -->|selected_as_active| selection event
            if sel in plan_id_to_node:
                _add_edge(plan_id_to_node[sel], nid, "active_selection", "selected_as_active")

        elif et == "plan_rejected":
            pid = ev.get("plan_id", "")
            if pid in plan_id_to_node:
                _add_edge(plan_id_to_node[pid], nid, "plan_rejection", "rejected")

        elif et == "plan_superseded":
            pid = ev.get("plan_id", "")
            if pid in plan_id_to_node:
                _add_edge(plan_id_to_node[pid], nid, "plan_supersession", "superseded")

    # ── Meta ──────────────────────────────────────────────────────────────────
    status_counts: dict[str, int] = {}
    for pid, status in status_map.items():
        status_counts[status] = status_counts.get(status, 0) + 1

    total_support   = sum(s.get("support_count", 0) for s in signals.values())
    total_objection = sum(s.get("objection_count", 0) for s in signals.values())

    return {
        "claim_id": claim_id,
        "nodes":    nodes,
        "edges":    edges,
        "meta": {
            "plan_count":        len(plan_ids),
            "total_events":      len(events),
            "status_counts":     status_counts,
            "total_support":     total_support,
            "total_objection":   total_objection,
        },
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="plan_negotiation_graph",
        description="Build plan negotiation graph for a claim.",
    )
    p.add_argument("--claim-id", required=True, metavar="CLAIM_ID")
    p.add_argument("--json", action="store_true", dest="json_output")
    return p.parse_args()


def main() -> None:
    args  = _parse_args()
    graph = build_negotiation_graph(args.claim_id)
    if args.json_output:
        print(json.dumps(graph, indent=2, ensure_ascii=False))
    else:
        nodes = graph["nodes"]
        edges = graph["edges"]
        meta  = graph["meta"]
        print(f"Plan Negotiation Graph — {args.claim_id}")
        print(f"  plans: {meta.get('plan_count', 0)}  events: {meta.get('total_events', 0)}")
        print(f"  +{meta.get('total_support', 0)} support / -{meta.get('total_objection', 0)} objection")
        print(f"\n  Nodes ({len(nodes)}):")
        for n in nodes:
            print(f"    [{n['id']}] {n['style']:18s} {n['label'][:60]}")
        print(f"\n  Edges ({len(edges)}):")
        for e in edges:
            lbl = f"|{e['label']}|" if e.get("label") else ""
            print(f"    {e['from']} --{lbl}--> {e['to']}  ({e['kind']})")


if __name__ == "__main__":
    main()
