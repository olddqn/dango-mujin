#!/usr/bin/env python3
"""
negotiation_graph.py — dango-gitsea-bridge / su-table

Build a directed graph of negotiation events for a given claim_id.

Reads all five su-table JSONL files and produces a graph dict:
  {
    "claim_id": str,
    "nodes": [ NodeDict, ... ],
    "edges": [ EdgeDict, ... ],
    "meta": { ... summary info ... },
  }

NodeDict:
  id         — stable node ID ("n0", "n1", ...)
  event_type — raw event_type string
  table      — which JSONL table the event came from
  timestamp  — ISO 8601 string
  event_hash — sha256 hex
  label      — human-readable single-line label
  shape      — mermaid node shape hint
  style      — semantic style class name
  meta       — additional event-specific fields (speaker, reason, result, ...)

EdgeDict:
  from       — source node ID
  to         — target node ID
  kind       — "temporal" | "correction" | "hash_chain"

Design notes:
  - Correction events produce a "correction" (dashed) edge from the original
    event they reference (by corrects_event_hash) IN ADDITION to the
    normal temporal flow. The original event is NOT removed.
  - dignity_violation_detected events are styled as danger nodes and
    all edges INTO them are also marked danger.
  - Events are ordered by timestamp; within the same millisecond, table
    insertion order (claims < negotiations < contributions < executions
    < reality_feedback) is used as tiebreaker.
"""

from __future__ import annotations
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from sutable_log import read_all, VALID_TABLES
from temporal_trust_decay import (
    compute_trust_weight,
    compute_days_since,
    trust_level,
    CONTRIBUTION_EVENT_TYPES,
)

# Event types that count toward continuity multiplier
_TRUST_ACCEPTED_TYPES = frozenset({"contribution_accepted", "contribution_completed"})

# ── Table ordering (tiebreaker when timestamps are equal) ─────
TABLE_ORDER = {t: i for i, t in enumerate(
    ["claims", "negotiations", "contributions", "executions", "reality_feedback", "plans"]
)}

# ── Shape hints (used by graph_export.py) ────────────────────
# Values map to mermaid node shape syntax
SHAPE = {
    "claim_created":             "rect",       # ["..."]
    "claim_updated":             "rect",
    "objection":                 "hex",         # {"..."}
    "amendment":                 "round",       # ("...")
    "support":                   "rect",
    "escalation":                "hex",
    "correction":                "asymmetric",  # >..."<
    "withdrawal":                "rect",
    "contribution_offer":        "para",        # [/"..."/]
    "contribution_accepted":     "para",
    "contribution_rejected":     "para",
    "contribution_completed":    "para",
    "execution_started":         "stadium",     # (["..."])
    "execution_paused":          "stadium",
    "execution_completed":       "stadium",
    "execution_blocked":         "stadium",
    "reality_feedback":          "stadium",
    # Plan events (from plans.jsonl)
    "plan_tree_created":         "rect",
    "plan_tree_amended":         "round",
    "plan_tree_corrected":       "asymmetric",
    "task_bundle_created":       "para",
    "task_bundle_blocked":       "para",
    "task_bundle_ready":         "para",
    "task_bundle_abandoned":     "para",
    # Plan negotiation events
    "plan_supported":            "rect",
    "plan_objected":             "hex",
    "plan_contested":            "hex",
    "plan_rejected":             "asymmetric",
    "plan_superseded":           "rect",
    "active_plan_selected":      "stadium",
}

# ── Style class names ─────────────────────────────────────────
def _style_for(event: dict) -> str:
    et     = event.get("event_type", "")
    result = event.get("result", "")

    if et == "reality_feedback":
        match result:
            case "success":                   return "feedbackOk"
            case "partial_success":           return "feedbackPartial"
            case "failed":                    return "feedbackFail"
            case "unexpected_outcome":        return "feedbackUnexpected"
            case "dignity_violation_detected":return "danger"
        return "feedbackPartial"

    return {
        "claim_created":         "claim",
        "claim_updated":         "claim",
        "objection":             "objection",
        "amendment":             "amendment",
        "support":               "support",
        "escalation":            "escalation",
        "correction":            "correction",
        "withdrawal":            "withdrawal",
        "contribution_offer":    "contrib",
        "contribution_accepted": "contrib",
        "contribution_rejected": "contribBlocked",
        "contribution_completed":"contrib",
        "execution_started":     "execution",
        "execution_paused":      "execution",
        "execution_completed":   "execution",
        "execution_blocked":     "danger",
        # Plan events
        "plan_tree_created":     "plan",
        "plan_tree_amended":     "planAmended",
        "plan_tree_corrected":   "planCorrected",
        "task_bundle_created":   "bundle",
        "task_bundle_blocked":   "bundleBlocked",
        "task_bundle_ready":     "bundleReady",
        "task_bundle_abandoned": "bundleAbandoned",
        # Plan negotiation events
        "plan_supported":        "planSupported",
        "plan_objected":         "planObjected",
        "plan_contested":        "planContested",
        "plan_rejected":         "planRejected",
        "plan_superseded":       "planSuperseded",
        "active_plan_selected":  "planActive",
    }.get(et, "default")


# ── Label builder ─────────────────────────────────────────────
_MAX_LABEL = 52  # characters before truncation

def _trunc(s: str, n: int = _MAX_LABEL) -> str:
    s = s.replace("\n", " ").replace('"', "'")
    return s[:n] + "…" if len(s) > n else s


def _label_for(event: dict, claim_id: str) -> str:
    et     = event.get("event_type", "unknown")
    result = event.get("result", "")

    match et:
        case "claim_created":
            stmt = event.get("statement", claim_id)
            return f"Claim: {_trunc(stmt, 44)}"

        case "claim_updated":
            return f"Claim Updated: {claim_id}"

        case "objection":
            reason = event.get("reason", "")
            return f"Objection: {_trunc(reason, 42)}"

        case "amendment":
            amend = event.get("proposed_amendment", "")
            cond  = event.get("amends_condition", "")
            body  = f"[{cond}] {amend}" if cond else amend
            return f"Amendment: {_trunc(body, 42)}"

        case "support":
            note = event.get("note", event.get("reason", ""))
            return f"Support: {_trunc(note, 44)}" if note else "Support ✓"

        case "escalation":
            reason = event.get("reason", "")
            return f"⚠ Escalation: {_trunc(reason, 38)}"

        case "correction":
            reason = event.get("correction_reason", "")
            return f"↩ Correction: {_trunc(reason, 38)}"

        case "withdrawal":
            reason = event.get("reason", "")
            return f"↰ Withdrawal: {_trunc(reason, 38)}" if reason else "↰ Withdrawal"

        case "contribution_offer":
            ctype = event.get("contribution_type", "")
            return f"Offer: {ctype}"

        case "contribution_accepted":
            ctype = event.get("contribution_type", "")
            note  = event.get("note", "")
            return f"Accepted: {ctype}" + (f" — {_trunc(note, 28)}" if note else "")

        case "contribution_rejected":
            ctype = event.get("contribution_type", "")
            return f"Rejected: {ctype}"

        case "contribution_completed":
            ctype = event.get("contribution_type", "")
            return f"Completed: {ctype}"

        case "execution_started":
            note = event.get("note", "")
            return f"Execution Started" + (f": {_trunc(note, 34)}" if note else "")

        case "execution_paused":
            return "Execution Paused ⏸"

        case "execution_completed":
            return "Execution Completed ✓"

        case "execution_blocked":
            return "🛑 Execution Blocked"

        case "reality_feedback":
            notes = event.get("notes", "")
            tag   = result.replace("_", " ").title() if result else "Feedback"
            label = f"Feedback: {tag}"
            if result == "dignity_violation_detected":
                label = f"🛑 DIGNITY VIOLATION"
            return label + (f"\n{_trunc(notes, 40)}" if notes else "")

        case "plan_tree_created":
            pid = event.get("plan_id", "")
            return f"Plan: {_trunc(pid, 44)}"

        case "plan_tree_amended":
            pid    = event.get("plan_id", "")
            reason = event.get("amendment_reason", "")
            return f"✏ Amended: {_trunc(pid, 38)}" + (f"\n{_trunc(reason, 38)}" if reason else "")

        case "plan_tree_corrected":
            pid    = event.get("plan_id", "")
            reason = event.get("correction_reason", "")
            return f"↩ Corrected: {_trunc(pid, 36)}" + (f"\n{_trunc(reason, 36)}" if reason else "")

        case "task_bundle_created":
            bid = event.get("bundle_id", "")
            tc  = event.get("task_count", "?")
            bc  = event.get("blocked_count", 0)
            return f"Bundle: {_trunc(bid, 36)} ({tc} tasks, {bc} blocked)"

        case "task_bundle_blocked":
            bid = event.get("bundle_id", "")
            return f"🛑 Bundle Blocked: {_trunc(bid, 34)}"

        case "task_bundle_ready":
            bid = event.get("bundle_id", "")
            return f"✓ Bundle Ready: {_trunc(bid, 36)}"

        case "task_bundle_abandoned":
            bid    = event.get("bundle_id", "")
            reason = event.get("abandoned_reason", "")
            return f"✗ Abandoned: {_trunc(bid, 38)}" + (f"\n{_trunc(reason, 38)}" if reason else "")

        case "plan_supported":
            pid    = event.get("plan_id", "")
            reason = event.get("support_reason", "")
            return f"✓ Support → {_trunc(pid, 36)}" + (f"\n{_trunc(reason, 40)}" if reason else "")

        case "plan_objected":
            pid    = event.get("plan_id", "")
            otype  = event.get("objection_type", "")
            reason = event.get("objection_reason", "")
            tag    = f"[{otype}] " if otype else ""
            return f"✗ Objection → {_trunc(pid, 34)}\n{tag}{_trunc(reason, 40)}"

        case "plan_contested":
            contested   = event.get("contested_plan_id", "")
            counterplan = event.get("counterplan_id", "")
            reason      = event.get("contest_reason", "")
            s = f"⚔ Contest: {_trunc(contested, 26)} ← {_trunc(counterplan, 26)}"
            return s + (f"\n{_trunc(reason, 44)}" if reason else "")

        case "plan_rejected":
            pid    = event.get("plan_id", "")
            reason = event.get("rejection_reason", "")
            return f"✗ Rejected: {_trunc(pid, 38)}" + (f"\n{_trunc(reason, 40)}" if reason else "")

        case "plan_superseded":
            pid   = event.get("plan_id", "")
            by_id = event.get("superseded_by", "")
            return f"Superseded: {_trunc(pid, 36)}" + (f" by {_trunc(by_id, 28)}" if by_id else "")

        case "active_plan_selected":
            sel   = event.get("selected_plan_id", "")
            basis = event.get("selection_basis", {})
            sup   = basis.get("support_count", "?") if isinstance(basis, dict) else "?"
            obj   = basis.get("objection_count", "?") if isinstance(basis, dict) else "?"
            return f"★ Active: {_trunc(sel, 40)}\nsup={sup}  obj={obj}"

        case _:
            return _trunc(et.replace("_", " ").title())


# ── Meta extraction ───────────────────────────────────────────
_META_KEYS = {
    "speaker", "contributor", "contributor_id",
    "contribution_type", "addresses_condition",
    "reason", "proposed_amendment", "amends_condition",
    "note", "notes", "result",
    "corrects_event_hash", "correction_reason",
    "dignity_violation", "requires_human_review",
    "conditions_met", "conditions_unmet",
    "dignity_cleared", "dignity_block_reason",
    "stream_id",
    # DID signature fields
    "signature_status",
    "signature",
    # Temporal trust fields (computed post-load, not in JSONL)
    "trust_weight",
    "trust_level",
    "decay_factor",
    "trust_detail",
    # Plan fields
    "plan_id", "corrects_plan_id", "amends_plan_id",
    "bundle_id", "derived_from_plan_id",
    "plan_tree_hash", "task_bundle_hash",
    "task_count", "blocked_count", "bundle_status",
    "abandoned_reason", "amendment_reason",
    # Plan negotiation fields
    "contested_plan_id", "counterplan_id",
    "contest_reason", "support_reason",
    "objection_type", "objection_reason",
    "rejection_reason", "superseded_by",
    "selected_plan_id", "selection_basis",
}

def _meta_for(event: dict) -> dict:
    meta = {k: v for k, v in event.items() if k in _META_KEYS}
    # Flatten signer DID for quick access in exporters
    sig = event.get("signature")
    if isinstance(sig, dict):
        meta["signer_did"] = sig.get("did", "")
        meta["signature_key_id"] = sig.get("key_id", "")
    return meta


# ── Core graph builder ────────────────────────────────────────

def build_graph(claim_id: str) -> dict[str, Any]:
    """
    Build a directed negotiation graph for the given claim_id.
    Returns a graph dict with nodes and edges.
    """
    # Collect all events across all tables
    raw: list[tuple[str, dict]] = []  # (table, event)
    for table in TABLE_ORDER:
        for event in read_all(table):
            if event.get("claim_id") == claim_id:
                raw.append((table, event))

    if not raw:
        return {
            "claim_id": claim_id,
            "nodes": [],
            "edges": [],
            "meta": {"error": f"No events found for claim_id: {claim_id}"},
        }

    # Sort by timestamp, then table order as tiebreaker
    raw.sort(key=lambda x: (x[1].get("timestamp", ""), TABLE_ORDER[x[0]]))

    # Build node list
    nodes: list[dict] = []
    hash_to_id: dict[str, str] = {}  # event_hash → node ID

    for idx, (table, event) in enumerate(raw):
        node_id = f"n{idx}"
        eh = event.get("event_hash", "")
        if eh:
            hash_to_id[eh] = node_id

        et = event.get("event_type", "unknown")
        nodes.append({
            "id":         node_id,
            "event_type": et,
            "table":      table,
            "timestamp":  event.get("timestamp", ""),
            "event_hash": eh,
            "label":      _label_for(event, claim_id),
            "shape":      SHAPE.get(et, "rect"),
            "style":      _style_for(event),
            "meta":       _meta_for(event),
        })

    # ── Trust weight computation ──────────────────────────────
    # For each contribution node, compute temporal trust weight.
    # Continuity multiplier uses the contributor's total accepted count
    # up to and including this event (in chronological order).
    from datetime import datetime, timezone
    ref_now = datetime.now(timezone.utc)

    # Count accepted contributions per contributor (in order)
    contrib_seen: dict[str, int] = {}
    for _, event in raw:
        et  = event.get("event_type", "")
        did = event.get("contributor") or event.get("contributor_id", "")
        if et in _TRUST_ACCEPTED_TYPES and did:
            contrib_seen[did] = contrib_seen.get(did, 0) + 1

    # Now attach trust_weight to contribution node meta
    contrib_running: dict[str, int] = {}
    for node in nodes:
        et  = node["event_type"]
        did = node["meta"].get("contributor") or node["meta"].get("contributor_id", "")
        if et not in CONTRIBUTION_EVENT_TYPES:
            continue
        # Find the raw event for this node to get full fields
        # (nodes are indexed the same as raw)
        idx = int(node["id"][1:])  # "n3" → 3
        _, event = raw[idx]
        if et in _TRUST_ACCEPTED_TYPES and did:
            contrib_running[did] = contrib_running.get(did, 0) + 1
        count = contrib_running.get(did, 1)
        tw = compute_trust_weight(
            event,
            reference_date=ref_now,
            contribution_count=count,
        )
        node["meta"]["trust_weight"]  = tw["trust_weight"]
        node["meta"]["trust_level"]   = trust_level(tw["trust_weight"])
        node["meta"]["decay_factor"]  = tw["decay_factor"]
        node["meta"]["trust_detail"]  = tw

    # Build edges
    edges: list[dict] = []

    # 1. Temporal chain: connect each node to the next
    for i in range(len(nodes) - 1):
        src = nodes[i]
        dst = nodes[i + 1]
        kind = "temporal"
        # Elevate edge to "danger" if destination is a danger node
        if dst["style"] == "danger":
            kind = "danger"
        edges.append({"from": src["id"], "to": dst["id"], "kind": kind})

    # 2. Correction edges: dashed from the event being corrected
    for node in nodes:
        if node["event_type"] == "correction":
            original_hash = node["meta"].get("corrects_event_hash", "")
            if original_hash and original_hash in hash_to_id:
                edges.append({
                    "from": hash_to_id[original_hash],
                    "to":   node["id"],
                    "kind": "correction",
                })

    # 2b. Plan correction edges: plan_tree_corrected → plan_tree_created/corrected
    # Build plan_id → node_id map first
    plan_id_to_node: dict[str, str] = {}
    for node in nodes:
        pid = node["meta"].get("plan_id", "")
        if pid and node["event_type"] in (
            "plan_tree_created", "plan_tree_amended", "plan_tree_corrected"
        ):
            plan_id_to_node[pid] = node["id"]

    for node in nodes:
        et = node["event_type"]
        if et == "plan_tree_corrected":
            old_pid = node["meta"].get("corrects_plan_id", "")
            if old_pid and old_pid in plan_id_to_node:
                edges.append({
                    "from": plan_id_to_node[old_pid],
                    "to":   node["id"],
                    "kind": "plan_correction",
                    "label": "corrected_by",
                })
        elif et == "plan_tree_amended":
            src_pid = node["meta"].get("amends_plan_id", "")
            if src_pid and src_pid in plan_id_to_node:
                edges.append({
                    "from": plan_id_to_node[src_pid],
                    "to":   node["id"],
                    "kind": "plan_amendment",
                    "label": "amended_by",
                })
        elif et == "task_bundle_created":
            dpid = node["meta"].get("derived_from_plan_id", "")
            if dpid and dpid in plan_id_to_node:
                edges.append({
                    "from": plan_id_to_node[dpid],
                    "to":   node["id"],
                    "kind": "bundle_derivation",
                    "label": "produces",
                })

        # 2c. Plan negotiation edges
        elif et == "plan_contested":
            contested   = node["meta"].get("contested_plan_id", "")
            counterplan = node["meta"].get("counterplan_id", "")
            if contested and contested in plan_id_to_node:
                edges.append({
                    "from":  plan_id_to_node[contested],
                    "to":    node["id"],
                    "kind":  "plan_contest",
                    "label": "contested_by",
                })
            if counterplan and counterplan in plan_id_to_node:
                edges.append({
                    "from":  node["id"],
                    "to":    plan_id_to_node[counterplan],
                    "kind":  "plan_contest",
                    "label": "counterplan",
                })

        elif et == "plan_supported":
            pid = node["meta"].get("plan_id", "")
            if pid and pid in plan_id_to_node:
                edges.append({
                    "from":  node["id"],
                    "to":    plan_id_to_node[pid],
                    "kind":  "plan_support",
                    "label": "supports",
                })

        elif et == "plan_objected":
            pid = node["meta"].get("plan_id", "")
            if pid and pid in plan_id_to_node:
                edges.append({
                    "from":  node["id"],
                    "to":    plan_id_to_node[pid],
                    "kind":  "plan_objection",
                    "label": "objects_to",
                })

        elif et == "active_plan_selected":
            sel = node["meta"].get("selected_plan_id", "")
            if sel and sel in plan_id_to_node:
                edges.append({
                    "from":  plan_id_to_node[sel],
                    "to":    node["id"],
                    "kind":  "active_selection",
                    "label": "selected_as_active",
                })

    # 3. Hash-chain edges within tables (for visual chain verification)
    #    Only add if not already covered by temporal edge
    existing = {(e["from"], e["to"]) for e in edges}
    for idx, (table, event) in enumerate(raw):
        prev_hash = event.get("previous_event_hash", "")
        if prev_hash and prev_hash in hash_to_id:
            src_id = hash_to_id[prev_hash]
            dst_id = f"n{idx}"
            if (src_id, dst_id) not in existing:
                edges.append({"from": src_id, "to": dst_id, "kind": "hash_chain"})
                existing.add((src_id, dst_id))

    # Meta summary
    event_types = [n["event_type"] for n in nodes]
    has_dignity_violation = any(
        n["style"] == "danger" and n["event_type"] == "reality_feedback"
        for n in nodes
    )
    feedback_nodes = [n for n in nodes if n["event_type"] == "reality_feedback"]
    final_result = feedback_nodes[-1]["meta"].get("result", "") if feedback_nodes else ""

    # Trust summary across contribution nodes
    contrib_nodes = [n for n in nodes if n.get("meta", {}).get("trust_weight") is not None]
    trust_counts = {"high": 0, "medium": 0, "low": 0, "blocked": 0}
    for cn in contrib_nodes:
        lvl = cn["meta"].get("trust_level", "low")
        trust_counts[lvl] = trust_counts.get(lvl, 0) + 1

    meta = {
        "total_events":          len(nodes),
        "tables_involved":       sorted({t for t, _ in raw}),
        "event_types":           event_types,
        "has_dignity_violation": has_dignity_violation,
        "final_result":          final_result,
        "first_timestamp":       nodes[0]["timestamp"] if nodes else "",
        "last_timestamp":        nodes[-1]["timestamp"] if nodes else "",
        "trust_summary":         trust_counts,
    }

    # ── Federation prerequisite edges (advisory) ─────────────────
    # Adds edges: claim → prerequisite_condition (kind: prerequisite_evidence)
    # These are structural edges showing which claim contributed evidence
    # to which promoted prerequisite. Advisory only — not enforcement.
    try:
        from prerequisite_snapshot import snapshot as prereq_snapshot
        prereq_statuses = prereq_snapshot()
        node_ids = {n["id"] for n in nodes}
        for s in prereq_statuses:
            status = s.get("status", "")
            if status not in ("promoted", "reaffirmed", "weakened"):
                continue
            cond = s["condition"]
            # Build a virtual prerequisite node
            prereq_node_id = f"prereq_{cond}"
            if prereq_node_id not in node_ids:
                label_suffix = " [weakened]" if status == "weakened" else " [federation prerequisite]"
                nodes.append({
                    "id":         prereq_node_id,
                    "label":      f"⊛ {cond}{label_suffix}",
                    "event_type": "federation_prerequisite_promoted",
                    "table":      "federation",
                    "style":      "correction",   # neutral style
                    "timestamp":  "",
                    "speaker":    "authority:none",
                    "meta":       {
                        "condition":   cond,
                        "authority":   "none",
                        "status":      status,
                        "new_scope":   s.get("new_scope"),
                        "contestable": True,
                    },
                })
                node_ids.add(prereq_node_id)

            # Draw evidence edges from each evidence claim's plan events to the prerequisite
            for evidence_cid in s.get("evidence_claims", []):
                if evidence_cid == claim_id:
                    plan_sources = [
                        n["id"] for n in nodes
                        if n.get("event_type") in (
                            "plan_tree_created", "plan_tree_corrected",
                            "plan_contested", "plan_objected",
                        )
                    ]
                    if plan_sources:
                        edge_key = (plan_sources[-1], prereq_node_id)
                        if edge_key not in existing:
                            edges.append({
                                "from":  plan_sources[-1],
                                "to":    prereq_node_id,
                                "kind":  "prerequisite_evidence",
                                "label": f"evidence: {cond}",
                            })
                            existing.add(edge_key)

            # Draw bypass edges for the current claim_id (if it bypasses this prerequisite)
            try:
                from prerequisite_deprecation_detector import detect_bypass_patterns
                bp = detect_bypass_patterns(cond)
                if claim_id in bp.get("bypassing_claims", []):
                    plan_sources = [
                        n["id"] for n in nodes
                        if n.get("event_type") in (
                            "plan_tree_created", "plan_tree_corrected",
                            "plan_supported",
                        )
                    ]
                    if plan_sources:
                        edge_key = (plan_sources[-1], prereq_node_id)
                        if edge_key not in existing:
                            edges.append({
                                "from":  plan_sources[-1],
                                "to":    prereq_node_id,
                                "kind":  "prerequisite_bypass",
                                "label": f"bypass: {cond}",
                            })
                            existing.add(edge_key)
            except ImportError:
                pass

    except ImportError:
        pass

    return {
        "claim_id": claim_id,
        "nodes":    nodes,
        "edges":    edges,
        "meta":     meta,
    }


def list_claim_ids() -> list[str]:
    """Return all unique claim_ids present in any su-table."""
    ids: set[str] = set()
    for table in TABLE_ORDER:
        for event in read_all(table):
            cid = event.get("claim_id")
            if cid:
                ids.add(cid)
    return sorted(ids)
