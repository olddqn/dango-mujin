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
    ["claims", "negotiations", "contributions", "executions", "reality_feedback"]
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
