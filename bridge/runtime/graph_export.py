#!/usr/bin/env python3
"""
graph_export.py — dango-gitsea-bridge / su-table

Export a negotiation graph to Mermaid, plain-text, or HTML format.
No external libraries required. No CDN. No network calls.

Usage:
  python runtime/graph_export.py --claim-id housing-001 --format text
  python runtime/graph_export.py --claim-id housing-001 --format mermaid
  python runtime/graph_export.py --claim-id housing-001 --format html --output examples/housing-001.graph.html
  python runtime/graph_export.py --claim-id housing-001 --format mermaid > examples/housing-001.graph.mmd
  python runtime/graph_export.py --list

HTML preview is local-only. It does not load any external scripts or stylesheets.
Mermaid code is displayed as a copyable source block with instructions to paste
into https://mermaid.live for rendering.
"""

import argparse
import html as html_escape_mod
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from negotiation_graph import build_graph, list_claim_ids
from claim_federation import (
    load_federation_events,
    build_federation_map,
    get_claim_summary as get_fed_summary,
)


# ══════════════════════════════════════════════════════════════
# MERMAID EXPORT
# ══════════════════════════════════════════════════════════════

MERMAID_SHAPE = {
    "rect":       ("[", "]"),
    "round":      ("(", ")"),
    "hex":        ("{", "}"),
    "para":       ("[/", "/]"),
    "stadium":    ("([", "])"),
    "asymmetric": (">", "]"),
}

MERMAID_CLASSDEFS = """\
  classDef claim          fill:#dbeafe,stroke:#2563eb,color:#1e3a5f
  classDef objection      fill:#ffedd5,stroke:#ea580c,color:#431407
  classDef amendment      fill:#ede9fe,stroke:#7c3aed,color:#2e1065
  classDef support        fill:#dcfce7,stroke:#16a34a,color:#14532d
  classDef escalation     fill:#fef3c7,stroke:#d97706,color:#451a03
  classDef correction     fill:#f3f4f6,stroke:#6b7280,color:#111827
  classDef withdrawal     fill:#f1f5f9,stroke:#64748b,color:#0f172a
  classDef contrib        fill:#f5f3ff,stroke:#8b5cf6,color:#2e1065
  classDef contribBlocked fill:#fee2e2,stroke:#dc2626,color:#450a0a
  classDef execution      fill:#ede7f6,stroke:#7c3aed,color:#2e1065
  classDef feedbackOk     fill:#dcfce7,stroke:#15803d,color:#14532d
  classDef feedbackPartial fill:#fef9c3,stroke:#ca8a04,color:#422006
  classDef feedbackFail   fill:#fee2e2,stroke:#dc2626,color:#450a0a
  classDef feedbackUnexpected fill:#fff7ed,stroke:#c2410c,color:#431407
  classDef danger         fill:#7f1d1d,stroke:#450a0a,color:#fef2f2
  classDef plan           fill:#e0f2fe,stroke:#0284c7,color:#0c4a6e
  classDef planAmended    fill:#fef9c3,stroke:#a16207,color:#3b1a00
  classDef planCorrected  fill:#fce7f3,stroke:#9d174d,color:#4a0020
  classDef bundle         fill:#d1fae5,stroke:#059669,color:#064e3b
  classDef bundleBlocked  fill:#fee2e2,stroke:#dc2626,color:#450a0a
  classDef bundleReady    fill:#bbf7d0,stroke:#15803d,color:#14532d
  classDef bundleAbandoned fill:#f3f4f6,stroke:#9ca3af,color:#6b7280
  classDef planSupported  fill:#d1fae5,stroke:#059669,color:#064e3b
  classDef planObjected   fill:#ffedd5,stroke:#ea580c,color:#431407
  classDef planContested  fill:#fce7f3,stroke:#be185d,color:#500724
  classDef planRejected   fill:#f3f4f6,stroke:#6b7280,color:#374151
  classDef planSuperseded fill:#f3f4f6,stroke:#9ca3af,color:#6b7280
  classDef planActive     fill:#bbf7d0,stroke:#15803d,color:#14532d\
"""

EDGE_ARROW = {
    "temporal":          "-->",
    "danger":            "-->",
    "correction":        "-.->",
    "hash_chain":        "-.->",
    "plan_correction":   "-.->",
    "plan_amendment":    "-.->",
    "bundle_derivation": "-->",
    "plan_contest":      "-.->",
    "plan_support":      "-.->",
    "plan_objection":    "-.->",
    "active_selection":  "-->",
}

EDGE_LABEL = {
    "correction":        "|corrects|",
    "hash_chain":        "|chain|",
    "plan_correction":   "|corrected_by|",
    "plan_amendment":    "|amended_by|",
    "bundle_derivation": "|produces|",
    "plan_contest":      "|contested_by|",
    "plan_support":      "|supports|",
    "plan_objection":    "|objects_to|",
    "active_selection":  "|selected_as_active|",
}


def _sanitize_label(label: str) -> str:
    return label.replace('"', "'").replace("\n", "<br/>")


def _sig_suffix(node: dict) -> str:
    """Return ' ✓sig' if the node has a valid mock signature, else ''."""
    sig_status = node.get("meta", {}).get("signature_status", "")
    if sig_status == "mock_valid":
        return " ✓sig"
    return ""


def _trust_suffix(node: dict) -> str:
    """Return trust info string for contribution nodes, else ''."""
    m  = node.get("meta", {})
    tw = m.get("trust_weight")
    if tw is None:
        return ""
    lvl = m.get("trust_level", "low")
    icon = {"high": "↑", "medium": "→", "low": "↓", "blocked": "🛑"}.get(lvl, "")
    return f" {icon}trust={tw}"


def _mermaid_node_line(node: dict) -> str:
    shape = node.get("shape", "rect")
    op, cl = MERMAID_SHAPE.get(shape, ("[", "]"))
    label  = _sanitize_label(node["label"]) + _sig_suffix(node) + _trust_suffix(node)
    nid    = node["id"]
    cls    = node.get("style", "default")
    ts     = node["timestamp"][:16].replace("T", " ")
    full   = f'{label}<br/><small>{ts}</small>'
    return f'  {nid}{op}"{full}"{cl}:::{cls}'


def _mermaid_edge_line(edge: dict) -> str:
    kind   = edge["kind"]
    arrow  = EDGE_ARROW.get(kind, "-->")
    elabel = EDGE_LABEL.get(kind, "")
    if elabel:
        return f'  {edge["from"]} {arrow} {elabel} {edge["to"]}'
    return f'  {edge["from"]} {arrow} {edge["to"]}'


def export_mermaid(graph: dict) -> str:
    claim_id = graph["claim_id"]
    nodes    = graph["nodes"]
    edges    = graph["edges"]
    meta     = graph.get("meta", {})

    if not nodes:
        return f"%% No events found for claim_id: {claim_id}\nflowchart TD\n  empty[\"(no events)\"]"

    lines: list[str] = []
    lines.append(f"%% Negotiation Graph: {claim_id}")
    lines.append(f"%% Generated by dango-gitsea-bridge / graph_export.py")
    lines.append(f"%% Events: {meta.get('total_events', '?')}  |  "
                 f"Final: {meta.get('final_result', 'in progress')}")
    # Federation context header
    fed_events_mmd = load_federation_events()
    if fed_events_mmd:
        fmap_mmd = build_federation_map(fed_events_mmd)
        if claim_id in fmap_mmd:
            fi_mmd = get_fed_summary(claim_id, fmap_mmd)
            lines.append(f"%% Federation depth: {fi_mmd['federation_depth']}")
            for _fk in ("depends_on","enables","blocks","blocked_by",
                        "counterclaims","counterclaimed_by","federation_link"):
                _fv = fi_mmd.get(_fk, [])
                if _fv:
                    lines.append(f"%%   {_fk}: {', '.join(_fv)}")
    if meta.get("has_dignity_violation"):
        lines.append("%% ⚠ DIGNITY VIOLATION DETECTED — see red node")
    lines.append("")
    lines.append("flowchart TD")
    lines.append(MERMAID_CLASSDEFS)
    lines.append("")
    lines.append("  %% ── Nodes ─────────────────────────────")
    for node in nodes:
        lines.append(_mermaid_node_line(node))
    lines.append("")
    lines.append("  %% ── Edges ─────────────────────────────")
    for edge in edges:
        lines.append(_mermaid_edge_line(edge))

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════
# TEXT EXPORT
# ══════════════════════════════════════════════════════════════

ICON = {
    "claim":             "📋",
    "objection":         "⚡",
    "amendment":         "✏",
    "support":           "✓",
    "escalation":        "⚠",
    "correction":        "↩",
    "withdrawal":        "↰",
    "contrib":           "→",
    "contribBlocked":    "✗",
    "execution":         "▶",
    "feedbackOk":        "✓",
    "feedbackPartial":   "◑",
    "feedbackFail":      "✗",
    "feedbackUnexpected":"⚡",
    "danger":            "🛑",
    "default":           "•",
}

EDGE_TEXT = {
    "temporal":   "│",
    "danger":     "│",
    "correction": "╌╌ corrects ╌╌",
    "hash_chain": "╌╌ chain ╌╌",
}


def export_text(graph: dict) -> str:
    claim_id = graph["claim_id"]
    nodes    = graph["nodes"]
    edges    = graph["edges"]
    meta     = graph.get("meta", {})

    if not nodes:
        return f"CLAIM {claim_id}\n  (no events found)"

    lines: list[str] = []
    lines.append("=" * 60)
    lines.append(f"NEGOTIATION GRAPH — {claim_id}")
    lines.append("=" * 60)
    lines.append(f"Total events:  {meta.get('total_events', '?')}")
    lines.append(f"Tables:        {', '.join(meta.get('tables_involved', []))}")
    lines.append(f"Final result:  {meta.get('final_result', 'in progress') or 'in progress'}")
    if meta.get("has_dignity_violation"):
        lines.append("⚠ DIGNITY VIOLATION DETECTED")
    ts_meta = meta.get("trust_summary", {})
    if any(ts_meta.values()):
        parts = []
        for lvl in ("high", "medium", "low", "blocked"):
            n = ts_meta.get(lvl, 0)
            if n:
                icon = {"high":"↑","medium":"→","low":"↓","blocked":"🛑"}.get(lvl,"")
                parts.append(f"{icon}{lvl}:{n}")
        lines.append(f"Trust:         {' '.join(parts)}")
    lines.append("")

    correction_edges: dict[str, list] = {}
    for edge in edges:
        if edge["kind"] in ("correction", "hash_chain"):
            correction_edges.setdefault(edge["from"], []).append(
                (edge["to"], edge["kind"])
            )

    lines.append("── EVENT TIMELINE ──")
    lines.append("")
    id_to_node = {n["id"]: n for n in nodes}

    for i, node in enumerate(nodes):
        nid   = node["id"]
        icon  = ICON.get(node["style"], "•")
        ts    = node["timestamp"][:19].replace("T", " ")
        label = node["label"].replace("\n", " / ")
        table = node["table"]

        lines.append(f"  {i+1:2d}. {icon} [{table}] {label}")
        lines.append(f"       {ts}")

        meta_n = node.get("meta", {})
        actor = meta_n.get("speaker") or meta_n.get("contributor") or meta_n.get("contributor_id")
        if actor:
            lines.append(f"       speaker: {actor}")

        # Signature status line
        sig_status = meta_n.get("signature_status", "")
        if sig_status:
            sig_icons = {
                "mock_valid":                "✓ [signature: mock_valid]",
                "unsigned":                  "○ [signature: unsigned]",
                "mock_invalid":              "✗ [signature: mock_invalid]",
                "unsupported_signature_type":"? [signature: unsupported]",
            }
            signer = meta_n.get("signer_did", "")
            sig_line = sig_icons.get(sig_status, f"? [signature: {sig_status}]")
            if signer and sig_status == "mock_valid":
                sig_line += f"  signer: {signer}"
            lines.append(f"       {sig_line}")

        # Trust weight line (contribution events only)
        tw = meta_n.get("trust_weight")
        if tw is not None:
            lvl = meta_n.get("trust_level", "low")
            decay = meta_n.get("decay_factor", "")
            td = meta_n.get("trust_detail", {})
            verif = td.get("verification_status", "")
            trust_icon = {"high":"↑","medium":"→","low":"↓","blocked":"🛑"}.get(lvl, "?")
            trust_line = f"       {trust_icon} trust={tw}  decay={decay}  level={lvl}"
            if verif:
                trust_line += f"  [{verif}]"
            lines.append(trust_line)

        if meta_n.get("dignity_violation"):
            lines.append("       ⚠ DIGNITY VIOLATION — automated processing halted")
        if meta_n.get("requires_human_review"):
            lines.append("       ⚠ requires human review")

        if nid in correction_edges:
            for (dst_id, kind) in correction_edges[nid]:
                dst_node = id_to_node.get(dst_id)
                if dst_node:
                    lines.append(f"       {EDGE_TEXT.get(kind, '?')} → {dst_node['label'][:50]}")

        if i < len(nodes) - 1:
            lines.append("       │")

    lines.append("")

    corr_edges = [e for e in edges if e["kind"] == "correction"]
    if corr_edges:
        lines.append("── CORRECTION EDGES ──")
        for e in corr_edges:
            src = id_to_node.get(e["from"], {})
            dst = id_to_node.get(e["to"],   {})
            lines.append(f"  {src.get('id','?')} ({src.get('label','?')[:32]})")
            lines.append(f"    ╌╌ corrects ╌╌→ {dst.get('id','?')} ({dst.get('label','?')[:32]})")
        lines.append("")

    # ── Plan history ─────────────────────────────────────────
    plan_nodes = [n for n in nodes if n["event_type"] in (
        "plan_tree_created", "plan_tree_amended", "plan_tree_corrected",
        "task_bundle_created", "task_bundle_blocked",
        "task_bundle_ready", "task_bundle_abandoned",
    )]
    if plan_nodes:
        lines.append("")
        lines.append("── PLAN HISTORY ──────────────────────────────────────────")
        # Group plan tree events and bundle events separately
        tree_nodes   = [n for n in plan_nodes if "plan_tree" in n["event_type"]]
        bundle_nodes = [n for n in plan_nodes if "task_bundle" in n["event_type"]]

        # Correction chain: determine corrected_by relationships
        corr_by: dict[str, str] = {}   # old_plan_id → new_plan_id
        for n in tree_nodes:
            if n["event_type"] == "plan_tree_corrected":
                old = n["meta"].get("corrects_plan_id", "")
                new = n["meta"].get("plan_id", "")
                if old and new:
                    corr_by[old] = new

        # Contest signals from negotiation events
        contested_pids: set[str] = set()
        try:
            from plan_contest_resolver import build_full_contest_graph, _load_plan_events
            _neg_evs = _load_plan_events(claim_id)
            for c in build_full_contest_graph(_neg_evs):
                contested_pids.add(c.get("contested", ""))
        except ImportError:
            pass

        for n in tree_nodes:
            pid   = n["meta"].get("plan_id", n["id"])
            ts    = n["timestamp"][:19].replace("T", " ")
            et    = n["event_type"]
            if pid in corr_by:
                badge = "[corrected]"
            elif et == "plan_tree_amended":
                badge = "[amended]"
            elif pid in contested_pids:
                badge = "[contested]"
            else:
                badge = "[active]"

            if et == "plan_tree_created":
                icon = "📋"
            elif et == "plan_tree_corrected":
                icon = "↩"
            else:
                icon = "✏"

            lines.append(f"  {icon} {pid}  {badge}")
            if et == "plan_tree_corrected":
                reason = n["meta"].get("correction_reason", "")
                old    = n["meta"].get("corrects_plan_id", "")
                if old:
                    lines.append(f"       corrects: {old}")
                if reason:
                    lines.append(f"       reason: {reason}")
            if pid in corr_by:
                lines.append(f"       ↳ corrected by: {corr_by[pid]}")
            lines.append(f"       {ts}")

        if bundle_nodes:
            lines.append("")
            for n in bundle_nodes:
                bid  = n["meta"].get("bundle_id", n["id"])
                et   = n["event_type"]
                dpid = n["meta"].get("derived_from_plan_id", "")
                tc   = n["meta"].get("task_count", "?")
                bc   = n["meta"].get("blocked_count", 0)
                ts   = n["timestamp"][:19].replace("T", " ")

                _bundle_icons = {
                    "task_bundle_created":   "→",
                    "task_bundle_blocked":   "🛑",
                    "task_bundle_ready":     "✓",
                    "task_bundle_abandoned": "✗",
                }
                icon = _bundle_icons.get(et, "•")
                lines.append(f"  {icon} {bid}  [{et.replace('task_bundle_','')}]")
                if dpid:
                    lines.append(f"       derived from: {dpid}")
                if tc != "?":
                    lines.append(f"       tasks: {tc} total, {bc} blocked")
                lines.append(f"       {ts}")
        lines.append("")

    # ── Plan negotiation ──────────────────────────────────────
    neg_nodes = [n for n in nodes if n["event_type"] in (
        "plan_supported", "plan_objected", "plan_contested",
        "plan_rejected", "plan_superseded", "active_plan_selected",
    )]
    if neg_nodes:
        # Import negotiation resolution lazily (avoids circular imports in test)
        try:
            from plan_contest_resolver import (
                aggregate_signals, build_full_contest_graph,
                get_plan_statuses, _load_plan_events, _get_plan_ids,
            )
            neg_events = _load_plan_events(claim_id)
            neg_plan_ids = _get_plan_ids(neg_events)
            neg_signals  = aggregate_signals(neg_events)
            neg_statuses = get_plan_statuses(neg_events)
            neg_contests = build_full_contest_graph(neg_events)
        except ImportError:
            neg_plan_ids = []
            neg_signals  = {}
            neg_statuses = {}
            neg_contests = []

        lines.append("")
        lines.append("── PLAN NEGOTIATION ──────────────────────────────────────")

        # Formal active from active_plan_selected events
        formal_active = ""
        for n in neg_nodes:
            if n["event_type"] == "active_plan_selected":
                formal_active = n["meta"].get("selected_plan_id", "")

        # Computed active from selector
        computed_active = ""
        try:
            from active_plan_selector import select_active_plan
            sel = select_active_plan(claim_id)
            computed_active = sel.get("selected_plan_id") or ""
        except ImportError:
            pass

        if formal_active:
            lines.append(f"  Active plan (formal):   {formal_active}")
        elif computed_active:
            lines.append(f"  Active plan (computed): {computed_active}  [not yet recorded]")

        if neg_plan_ids:
            lines.append("")
            for pid in neg_plan_ids:
                status  = neg_statuses.get(pid, "open")
                sigs    = neg_signals.get(pid, {})
                sup_n   = sigs.get("support_count", 0)
                obj_n   = sigs.get("objection_count", 0)
                active_m = " ← active" if pid == (formal_active or computed_active) else ""
                lines.append(
                    f"  {'★' if active_m else ' '} {pid}  [{status}]"
                    f"  +{sup_n} support / -{obj_n} objection{active_m}"
                )
                for reason in sigs.get("support_reasons", []):
                    lines.append(f"      + {reason[:60]}")
                obj_reasons = sigs.get("objection_reasons", [])
                obj_types   = sigs.get("objections_by_type", {})
                for i_obj, reason in enumerate(obj_reasons):
                    otype = list(obj_types.keys())[i_obj] if i_obj < len(obj_types) else "?"
                    lines.append(f"      ✗ [{otype}] {reason[:60]}")

        if neg_contests:
            lines.append("")
            for c in neg_contests:
                lines.append(
                    f"  {c['contested']:30s} -.->|contested_by| {c['counterplan']}"
                )
                if c.get("reason"):
                    lines.append(f"      reason: {c['reason'][:60]}")

        lines.append("")

    # ── Federation context ───────────────────────────────────
    fed_events = load_federation_events()
    if fed_events:
        fmap_text = build_federation_map(fed_events)
        if claim_id in fmap_text:
            fi = get_fed_summary(claim_id, fmap_text)
            lines.append("")
            lines.append("── CLAIM FEDERATION ──")
            lines.append(f"  Federation depth:  {fi['federation_depth']}")
            _FED_LABELS = [
                ("depends_on",        "Depends on:       "),
                ("enables",           "Enables:          "),
                ("blocks",            "Blocks:           "),
                ("blocked_by",        "Blocked by:       "),
                ("counterclaims",     "Counterclaims:    "),
                ("counterclaimed_by", "Countercl. by:    "),
                ("enabled_by",        "Enabled by:       "),
                ("depended_on_by",    "Depended on by:   "),
                ("federation_link",   "Fed. links:       "),
                ("amendment_of",      "Amends:           "),
                ("derived_from",      "Derived from:     "),
                ("dignity_override",  "Dignity override: "),
            ]
            for key, label in _FED_LABELS:
                vals = fi.get(key, [])
                if vals:
                    lines.append(f"  {label}{', '.join(vals)}")
            lines.append("")

    lines.append("=" * 60)
    final = meta.get("final_result", "")
    if final == "success":
        lines.append("OUTCOME: ✓ SUCCESS — Claim fully realized.")
    elif final == "partial_success":
        lines.append("OUTCOME: ◑ PARTIAL SUCCESS — Claim partially realized.")
    elif final == "failed":
        lines.append("OUTCOME: ✗ FAILED — Claim not realized.")
    elif final == "dignity_violation_detected":
        lines.append("OUTCOME: 🛑 DIGNITY VIOLATION — requires immediate human review.")
    elif final == "unexpected_outcome":
        lines.append("OUTCOME: ⚡ UNEXPECTED — outcome differed from claim.")
    else:
        lines.append("OUTCOME: ⏳ IN PROGRESS — no reality feedback yet.")
    lines.append("=" * 60)

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════
# HTML EXPORT
# ══════════════════════════════════════════════════════════════

# Style class → CSS class name used in HTML
_HTML_STYLE_CLASS = {
    "claim":             "ev-claim",
    "objection":         "ev-objection",
    "amendment":         "ev-amendment",
    "support":           "ev-support",
    "escalation":        "ev-escalation",
    "correction":        "ev-correction",
    "withdrawal":        "ev-withdrawal",
    "contrib":           "ev-contrib",
    "contribBlocked":    "ev-contrib-blocked",
    "execution":         "ev-execution",
    "feedbackOk":        "ev-feedback-ok",
    "feedbackPartial":   "ev-feedback-partial",
    "feedbackFail":      "ev-feedback-fail",
    "feedbackUnexpected":"ev-feedback-unexpected",
    "danger":            "ev-danger",
    "plan":              "ev-plan",
    "planAmended":       "ev-plan-amended",
    "planCorrected":     "ev-plan-corrected",
    "bundle":            "ev-bundle",
    "bundleBlocked":     "ev-bundle-blocked",
    "bundleReady":       "ev-bundle-ready",
    "bundleAbandoned":   "ev-bundle-abandoned",
    # Plan negotiation events
    "planSupported":     "ev-plan-supported",
    "planObjected":      "ev-plan-objected",
    "planContested":     "ev-plan-contested",
    "planRejected":      "ev-plan-rejected",
    "planSuperseded":    "ev-plan-superseded",
    "planActive":        "ev-plan-active",
    "default":           "ev-default",
}

# Accent colours for the timeline pill badges
_BADGE_STYLE = {
    "claim":             "background:#1d4ed8;color:#eff6ff",
    "objection":         "background:#c2410c;color:#fff7ed",
    "amendment":         "background:#6d28d9;color:#ede9fe",
    "support":           "background:#15803d;color:#dcfce7",
    "escalation":        "background:#b45309;color:#fef3c7",
    "correction":        "background:#4b5563;color:#f3f4f6",
    "withdrawal":        "background:#475569;color:#f1f5f9",
    "contrib":           "background:#7c3aed;color:#f5f3ff",
    "contribBlocked":    "background:#991b1b;color:#fee2e2",
    "execution":         "background:#065f46;color:#d1fae5",
    "feedbackOk":        "background:#166534;color:#dcfce7",
    "feedbackPartial":   "background:#92400e;color:#fef3c7",
    "feedbackFail":      "background:#7f1d1d;color:#fee2e2",
    "feedbackUnexpected":"background:#9a3412;color:#fff7ed",
    "danger":            "background:#450a0a;color:#fca5a5",
    "plan":              "background:#0369a1;color:#e0f2fe",
    "planAmended":       "background:#92400e;color:#fef3c7",
    "planCorrected":     "background:#9d174d;color:#fce7f3",
    "bundle":            "background:#065f46;color:#d1fae5",
    "bundleBlocked":     "background:#7f1d1d;color:#fee2e2",
    "bundleReady":       "background:#14532d;color:#bbf7d0",
    "bundleAbandoned":   "background:#4b5563;color:#f3f4f6",
    # Plan negotiation events
    "planSupported":     "background:#059669;color:#d1fae5",
    "planObjected":      "background:#c2410c;color:#ffedd5",
    "planContested":     "background:#be185d;color:#fce7f3",
    "planRejected":      "background:#6b7280;color:#f3f4f6",
    "planSuperseded":    "background:#9ca3af;color:#f3f4f6",
    "planActive":        "background:#15803d;color:#bbf7d0",
    "default":           "background:#374151;color:#d1d5db",
}

_INLINE_CSS = """
:root {
  --bg:        #0d0d0d;
  --surface:   #141414;
  --surface2:  #1c1c1c;
  --border:    #2a2a2a;
  --text:      #e2e8f0;
  --muted:     #64748b;
  --accent:    #7c3aed;
  --cyan:      #22d3ee;
  --green:     #4ade80;
  --amber:     #fbbf24;
  --red:       #f87171;
  --violet:    #c084fc;
  --mono:      'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
  --sans:      system-ui, -apple-system, sans-serif;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--sans);
  font-size: 14px;
  line-height: 1.6;
  padding: 0 0 4rem 0;
}

.page-header {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 1.5rem 2rem;
  display: flex;
  align-items: baseline;
  gap: 1rem;
  flex-wrap: wrap;
}
.page-header h1 {
  font-size: 1.25rem;
  font-weight: 700;
  font-family: var(--mono);
  color: var(--cyan);
  letter-spacing: -0.02em;
}
.page-header .subtitle {
  color: var(--muted);
  font-size: 0.85rem;
}
.warn-banner {
  background: #450a0a;
  border-bottom: 2px solid #f87171;
  color: #fca5a5;
  padding: 0.6rem 2rem;
  font-size: 0.9rem;
  font-weight: 600;
}

.container { max-width: 1100px; margin: 0 auto; padding: 2rem; }

section { margin-bottom: 2.5rem; }

h2 {
  font-family: var(--mono);
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--muted);
  margin-bottom: 1rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid var(--border);
}

/* ── Summary cards ──────────────────────────────── */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem;
}
.stat-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 1rem;
}
.stat-card .val {
  font-size: 2rem;
  font-weight: 700;
  font-family: var(--mono);
  color: var(--cyan);
  line-height: 1;
}
.stat-card .lbl {
  color: var(--muted);
  font-size: 0.75rem;
  margin-top: 0.25rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.stat-card.danger .val { color: var(--red); }
.stat-card.good   .val { color: var(--green); }
.stat-card.amber  .val { color: var(--amber); }

/* ── Timeline ───────────────────────────────────── */
.timeline { list-style: none; }
.tl-item {
  display: flex;
  gap: 1rem;
  padding: 0.8rem 0;
  border-bottom: 1px solid var(--border);
  position: relative;
}
.tl-item:last-child { border-bottom: none; }
.tl-index {
  font-family: var(--mono);
  color: var(--muted);
  font-size: 0.75rem;
  width: 2rem;
  flex-shrink: 0;
  padding-top: 0.15rem;
  text-align: right;
}
.tl-body { flex: 1; }
.tl-badge {
  display: inline-block;
  border-radius: 4px;
  padding: 0.15rem 0.55rem;
  font-size: 0.7rem;
  font-family: var(--mono);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-right: 0.4rem;
}
.tl-label {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text);
}
.tl-meta {
  margin-top: 0.3rem;
  color: var(--muted);
  font-size: 0.78rem;
  font-family: var(--mono);
}
.tl-meta span { margin-right: 1.2rem; }
.tl-edge {
  margin-top: 0.3rem;
  font-size: 0.75rem;
  color: var(--violet);
  font-family: var(--mono);
}
.tl-danger-flag {
  margin-top: 0.4rem;
  color: var(--red);
  font-size: 0.8rem;
  font-weight: 600;
}

.ev-danger    .tl-label { color: var(--red); }
.ev-correction .tl-label { color: var(--violet); }
.ev-contrib   .tl-label { color: var(--cyan); }
.ev-execution .tl-label { color: var(--green); }
.ev-feedback-partial .tl-label { color: var(--amber); }

/* ── Mermaid block ──────────────────────────────── */
.mermaid-wrap {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
}
.mermaid-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.6rem 1rem;
  border-bottom: 1px solid var(--border);
  background: var(--surface2);
}
.mermaid-toolbar .toolbar-left {
  font-size: 0.75rem;
  color: var(--muted);
  font-family: var(--mono);
}
.copy-btn {
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 0.3rem 0.8rem;
  font-size: 0.75rem;
  font-family: var(--mono);
  cursor: pointer;
  transition: background 0.15s;
}
.copy-btn:hover  { background: #6d28d9; }
.copy-btn.copied { background: #15803d; }
.mermaid-hint {
  padding: 0.5rem 1rem;
  font-size: 0.75rem;
  color: var(--muted);
  background: var(--surface2);
  border-bottom: 1px solid var(--border);
}
.mermaid-hint a {
  color: var(--cyan);
  text-decoration: none;
}
.mermaid-hint a:hover { text-decoration: underline; }
pre.mermaid-src {
  padding: 1rem;
  font-family: var(--mono);
  font-size: 0.78rem;
  line-height: 1.5;
  color: #94a3b8;
  overflow-x: auto;
  white-space: pre;
  background: transparent;
}

/* ── Event table ────────────────────────────────── */
.event-table-wrap { overflow-x: auto; }
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.78rem;
  font-family: var(--mono);
}
th {
  background: var(--surface2);
  color: var(--muted);
  text-align: left;
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid var(--border);
  font-weight: 600;
  white-space: nowrap;
  text-transform: uppercase;
  font-size: 0.68rem;
  letter-spacing: 0.06em;
}
td {
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid var(--border);
  vertical-align: top;
  color: var(--text);
  word-break: break-all;
}
tr:hover td { background: var(--surface); }
.td-hash { color: var(--muted); font-size: 0.7rem; }
.td-type { font-weight: 600; }
.row-danger td { color: var(--red); }
.row-correction td { color: var(--violet); }

/* ── Integrity notes ────────────────────────────── */
.integrity-block {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 1rem 1.25rem;
  font-family: var(--mono);
  font-size: 0.8rem;
}
.integrity-block .ok   { color: var(--green); }
.integrity-block .warn { color: var(--amber); }
.integrity-block .err  { color: var(--red); }
.integrity-item { margin-bottom: 0.4rem; }

/* ── Trust badges ───────────────────────────────── */
.trust-badge {
  display: inline-block;
  border-radius: 3px;
  padding: 0.1rem 0.45rem;
  font-size: 0.67rem;
  font-family: var(--mono);
  font-weight: 700;
  letter-spacing: 0.04em;
  vertical-align: middle;
  cursor: help;
}
.trust-high    { background:#164e4e; color:var(--cyan); }
.trust-medium  { background:#451a03; color:var(--amber); }
.trust-low     { background:#1c1c1c; color:#6b7280; border:1px solid #2a2a2a; }
.trust-blocked { background:#450a0a; color:var(--red); }

/* ── Signature badges ───────────────────────────── */
.sig-badge {
  display: inline-block;
  border-radius: 3px;
  padding: 0.1rem 0.45rem;
  font-size: 0.67rem;
  font-family: var(--mono);
  font-weight: 700;
  letter-spacing: 0.04em;
  vertical-align: middle;
  margin-left: 0.4rem;
}
.sig-valid    { background:#14532d; color:#86efac; }
.sig-unsigned { background:#1c1c1c; color:#64748b; border:1px solid #2a2a2a; }
.sig-invalid  { background:#450a0a; color:#fca5a5; }
.sig-unsup    { background:#1c1f2b; color:#818cf8; }

/* ── Federation panel ───────────────────────────── */
.fed-panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 0.75rem 1.25rem;
}
.fed-row {
  display: flex;
  gap: 0.75rem;
  padding: 0.3rem 0;
  border-bottom: 1px solid var(--border);
  font-size: 0.82rem;
  align-items: baseline;
}
.fed-row:last-child { border-bottom: none; }
.fed-key {
  color: var(--muted);
  font-family: var(--mono);
  font-size: 0.72rem;
  width: 140px;
  flex-shrink: 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.fed-val { flex: 1; }
.fed-claim-tag {
  display: inline-block;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 3px;
  padding: 0.1rem 0.5rem;
  font-family: var(--mono);
  font-size: 0.75rem;
  margin: 0.1rem 0.2rem 0.1rem 0;
  color: var(--cyan);
}
.fed-claim-tag.fed-counterclaim { border-color: #dc2626; color: var(--red); }
.fed-claim-tag.fed-blocks       { border-color: #dc2626; color: var(--red); }
.fed-claim-tag.fed-enables      { border-color: #16a34a; color: var(--green); }
.fed-claim-tag.fed-blocked      { border-color: #b45309; color: var(--amber); }
.fed-none { color: var(--muted); font-style: italic; }

/* ── Plan history panel ──────────────────────────── */
.plan-panel {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.plan-row {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  padding: 0.6rem 0.8rem;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 4px;
}
.bundle-row { border-color: #065f46; }
.plan-id {
  font-family: var(--mono);
  font-size: 0.85rem;
  color: var(--cyan);
}
.plan-ts {
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--muted);
}
.plan-sub {
  font-size: 0.78rem;
  color: var(--muted);
}
.plan-sub code { color: var(--text); font-family: var(--mono); font-size: 0.78rem; }
.plan-sub.reason { color: var(--amber); font-style: italic; }
.plan-badge {
  display: inline-block;
  border-radius: 3px;
  padding: 0.1rem 0.45rem;
  font-size: 0.7rem;
  font-family: var(--mono);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  vertical-align: middle;
}
.plan-active    { background:#0369a1;color:#e0f2fe; }
.plan-corrected { background:#9d174d;color:#fce7f3; }
.plan-amended   { background:#92400e;color:#fef3c7; }
.plan-contested { background:#be185d;color:#fce7f3; }
.plan-rejected  { background:#6b7280;color:#f3f4f6; }
.plan-supported { background:#059669;color:#d1fae5; }
.plan-objected  { background:#c2410c;color:#ffedd5; }
.bundle-created  { background:#065f46;color:#d1fae5; }
.bundle-blocked  { background:#7f1d1d;color:#fee2e2; }
.bundle-ready    { background:#14532d;color:#bbf7d0; }
.bundle-abandoned{ background:#4b5563;color:#f3f4f6; }
.plan-divider { border: none; border-top: 1px solid var(--border); margin: 0.3rem 0; }
.plan-none { color: var(--muted); font-style: italic; }

/* ── Footer ─────────────────────────────────────── */
.page-footer {
  margin-top: 3rem;
  padding: 1rem 2rem;
  border-top: 1px solid var(--border);
  color: var(--muted);
  font-size: 0.72rem;
  font-family: var(--mono);
}
"""

_COPY_SCRIPT = """
function copyMermaid() {
  var src = document.getElementById('mermaid-source').textContent;
  var btn = document.getElementById('copy-btn');
  if (navigator && navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(src).then(function() {
      btn.textContent = '✓ Copied';
      btn.classList.add('copied');
      setTimeout(function(){ btn.textContent = 'Copy'; btn.classList.remove('copied'); }, 2000);
    }).catch(function() { fallbackCopy(src, btn); });
  } else {
    fallbackCopy(src, btn);
  }
}
function fallbackCopy(text, btn) {
  var ta = document.createElement('textarea');
  ta.value = text;
  ta.style.position = 'fixed';
  ta.style.opacity = '0';
  document.body.appendChild(ta);
  ta.focus(); ta.select();
  try {
    document.execCommand('copy');
    btn.textContent = '✓ Copied';
    btn.classList.add('copied');
    setTimeout(function(){ btn.textContent = 'Copy'; btn.classList.remove('copied'); }, 2000);
  } catch(e) {
    btn.textContent = 'Select & copy manually';
  }
  document.body.removeChild(ta);
}
"""


def _h(s: str) -> str:
    """HTML-escape a string."""
    return html_escape_mod.escape(str(s))


def _short_hash(h: str) -> str:
    return h[:12] + "…" if len(h) >= 12 else h


def _actor(node: dict) -> str:
    m = node.get("meta", {})
    a = m.get("speaker") or m.get("contributor") or m.get("contributor_id") or ""
    if len(a) > 28:
        a = a[:12] + "…" + a[-8:]
    return a


def _summary_line(node: dict) -> str:
    """One-line human summary of the node for the event table."""
    et = node.get("event_type", "")
    m  = node.get("meta", {})
    for key in ("reason", "proposed_amendment", "notes", "note", "correction_reason"):
        val = m.get(key)
        if val:
            s = str(val)
            return s[:80] + "…" if len(s) > 80 else s
    result = m.get("result", "")
    if result:
        return f"result: {result}"
    return node.get("label", "").replace("\n", " ")[:80]


def _corrects_id(node: dict, hash_to_id: dict[str, str]) -> str:
    h = node.get("meta", {}).get("corrects_event_hash", "")
    if h and h in hash_to_id:
        return hash_to_id[h]
    return ""


def export_html(graph: dict) -> str:
    claim_id = graph["claim_id"]
    nodes    = graph["nodes"]
    edges    = graph["edges"]
    meta     = graph.get("meta", {})

    # ── Pre-compute helpers ──────────────────────────────────
    hash_to_id   = {n["event_hash"]: n["id"] for n in nodes if n.get("event_hash")}
    id_to_node   = {n["id"]: n for n in nodes}
    mermaid_src  = export_mermaid(graph)

    total        = meta.get("total_events", len(nodes))
    final_result = meta.get("final_result", "") or "in progress"
    corr_count   = sum(1 for n in nodes if n["event_type"] == "correction")
    contrib_count= sum(1 for n in nodes if "contrib" in n.get("style", ""))
    danger_count  = sum(1 for n in nodes if n.get("style") == "danger")
    corr_edges    = [e for e in edges if e["kind"] == "correction"]
    chain_edges   = [e for e in edges if e["kind"] == "hash_chain"]
    signed_preview= sum(1 for n in nodes if n.get("meta",{}).get("signature_status") == "mock_valid")
    trust_summary = meta.get("trust_summary", {})
    high_trust    = trust_summary.get("high", 0)
    blocked_trust = trust_summary.get("blocked", 0)

    # Federation context for this claim
    fed_events_html = load_federation_events()
    fmap_html: dict = {}
    fed_info_html: dict = {}
    if fed_events_html:
        fmap_html = build_federation_map(fed_events_html)
        if claim_id in fmap_html:
            fed_info_html = get_fed_summary(claim_id, fmap_html)

    # outgoing correction/chain edges per node
    out_special: dict[str, list] = {}
    for e in edges:
        if e["kind"] in ("correction", "hash_chain"):
            out_special.setdefault(e["from"], []).append(e)

    gen_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # ── Helper: timeline items ───────────────────────────────
    def tl_item(i: int, node: dict) -> str:
        style  = node.get("style", "default")
        css    = _HTML_STYLE_CLASS.get(style, "ev-default")
        badge  = _BADGE_STYLE.get(style, "background:#374151;color:#d1d5db")
        et     = node["event_type"].replace("_", " ")
        ts     = node["timestamp"][:19].replace("T", " ")
        label  = _h(node["label"].replace("\n", " / "))
        actor  = _h(_actor(node))
        table  = _h(node["table"])
        m      = node.get("meta", {})
        nid    = node["id"]

        sig_status = m.get("signature_status", "")
        signer_did = m.get("signer_did", "")
        sig_badge_html = ""
        if sig_status == "mock_valid":
            sig_badge_html = '<span class="sig-badge sig-valid" title="mock_valid — signed">✓ sig</span>'
        elif sig_status == "unsigned":
            sig_badge_html = '<span class="sig-badge sig-unsigned" title="unsigned">unsigned</span>'
        elif sig_status == "mock_invalid":
            sig_badge_html = '<span class="sig-badge sig-invalid" title="mock_invalid — tampered?">✗ sig</span>'
        elif sig_status == "unsupported_signature_type":
            sig_badge_html = '<span class="sig-badge sig-unsup" title="unsupported signature type">? sig</span>'

        # Trust badge (contribution events only)
        tw  = m.get("trust_weight")
        lvl = m.get("trust_level", "")
        td  = m.get("trust_detail", {})
        trust_badge_html = ""
        if tw is not None:
            decay   = td.get("decay_factor", "")
            verif   = td.get("verification_status", "")
            days    = td.get("days_since_event", "")
            tooltip = (f"trust={tw} decay={decay} "
                       f"days={days} verif={verif}")
            css_lvl = {"high":"trust-high","medium":"trust-medium",
                       "low":"trust-low","blocked":"trust-blocked"}.get(lvl,"trust-low")
            icon    = {"high":"↑","medium":"→","low":"↓","blocked":"🛑"}.get(lvl,"")
            trust_badge_html = (
                f'<span class="trust-badge {css_lvl}" title="{_h(tooltip)}">'
                f'{icon} {tw}'
                f'</span>'
            )

        parts = [
            f'<li class="tl-item {_h(css)}">',
            f'  <span class="tl-index">{i}</span>',
            f'  <div class="tl-body">',
            f'    <span class="tl-badge" style="{_h(badge)}">{_h(et)}</span>',
            f'    <span class="tl-label">{label}</span>',
        ]
        if sig_badge_html:
            parts.append(f'    {sig_badge_html}')
        if trust_badge_html:
            parts.append(f'    {trust_badge_html}')
        parts += [
            f'    <div class="tl-meta">',
            f'      <span>🗄 {table}</span>',
        ]
        if actor:
            parts.append(f'      <span>👤 {actor}</span>')
        if sig_status == "mock_valid" and signer_did:
            did_short = signer_did[:24] + "…" if len(signer_did) > 24 else signer_did
            parts.append(f'      <span title="{_h(signer_did)}">🔑 {_h(did_short)}</span>')
        parts.append(f'      <span>🕐 {_h(ts)}</span>')
        parts.append(f'    </div>')

        # Out-edges (correction / chain)
        if nid in out_special:
            for e in out_special[nid]:
                dst = id_to_node.get(e["to"])
                if dst:
                    kind_lbl = "corrects →" if e["kind"] == "correction" else "chain →"
                    dst_lbl  = _h(dst["label"].replace("\n", " ")[:48])
                    parts.append(f'    <div class="tl-edge">╌╌ {_h(kind_lbl)} {dst_lbl}</div>')

        # Dignity flags
        if m.get("dignity_violation"):
            parts.append('    <div class="tl-danger-flag">🛑 DIGNITY VIOLATION — automated processing halted</div>')
        if m.get("requires_human_review") and not m.get("dignity_violation"):
            parts.append('    <div class="tl-danger-flag" style="color:var(--amber)">⚠ requires human review</div>')

        parts += ["  </div>", "</li>"]
        return "\n".join(parts)

    # Signature badge HTML for table cells
    _SIG_CELL = {
        "mock_valid":                '<span class="sig-badge sig-valid">✓ mock_valid</span>',
        "unsigned":                  '<span class="sig-badge sig-unsigned">unsigned</span>',
        "mock_invalid":              '<span class="sig-badge sig-invalid">✗ invalid</span>',
        "unsupported_signature_type":'<span class="sig-badge sig-unsup">? unsupported</span>',
    }

    # Trust cell helper
    def _trust_cell(node: dict) -> str:
        m   = node.get("meta", {})
        tw  = m.get("trust_weight")
        lvl = m.get("trust_level", "")
        td  = m.get("trust_detail", {})
        if tw is None:
            return ""
        css_lvl = {"high":"trust-high","medium":"trust-medium",
                   "low":"trust-low","blocked":"trust-blocked"}.get(lvl,"trust-low")
        icon    = {"high":"↑","medium":"→","low":"↓","blocked":"🛑"}.get(lvl,"")
        decay   = td.get("decay_factor","")
        days    = td.get("days_since_event","")
        verif   = td.get("verification_status","")
        tooltip = f"trust={tw} decay={decay} days={days} verif={verif}"
        return (
            f'<span class="trust-badge {css_lvl}" title="{_h(tooltip)}">'
            f'{icon} {tw}'
            f'</span>'
        )

    # ── Helper: event table rows ─────────────────────────────
    def table_row(i: int, node: dict) -> str:
        style   = node.get("style", "default")
        row_cls = ""
        if style == "danger":
            row_cls = "row-danger"
        elif style == "correction":
            row_cls = "row-correction"
        eh  = node.get("event_hash", "")
        prev_nid  = f"n{i-2}" if i > 1 else ""  # n0-based, i is 1-based display
        prev_node = id_to_node.get(prev_nid, {})
        prev_hash = prev_node.get("event_hash", "") if prev_node else ""
        corrects_nid = _corrects_id(node, hash_to_id)
        summary = _h(_summary_line(node))
        m = node.get("meta", {})
        sig_status = m.get("signature_status", "")
        signer_did = m.get("signer_did", "")
        sig_cell   = _SIG_CELL.get(sig_status, "")
        did_short  = (signer_did[:20] + "…") if len(signer_did) > 20 else signer_did
        tc         = _trust_cell(node)

        return (
            f'<tr class="{row_cls}">'
            f'<td class="td-hash">{_h(node["id"])}</td>'
            f'<td>{_h(node["table"])}</td>'
            f'<td class="td-type">{_h(node["event_type"])}</td>'
            f'<td>{_h(_actor(node))}</td>'
            f'<td class="td-hash">{_h(node["timestamp"][:19].replace("T"," "))}</td>'
            f'<td>{summary}</td>'
            f'<td>{tc}</td>'
            f'<td>{sig_cell}</td>'
            f'<td class="td-hash" title="{_h(signer_did)}">{_h(did_short)}</td>'
            f'<td class="td-hash">{_h(_short_hash(eh))}</td>'
            f'<td class="td-hash">{_h(_short_hash(prev_hash))}</td>'
            f'<td class="td-hash">{_h(corrects_nid)}</td>'
            f'</tr>'
        )

    # ── Integrity notes ──────────────────────────────────────
    signed_count   = sum(1 for n in nodes if n.get("meta",{}).get("signature_status") == "mock_valid")
    unsigned_count = sum(1 for n in nodes if n.get("meta",{}).get("signature_status") == "unsigned")
    invalid_count  = sum(1 for n in nodes if n.get("meta",{}).get("signature_status") == "mock_invalid")
    tw_nodes = [n for n in nodes if n.get("meta",{}).get("trust_weight") is not None]
    high_tw_count  = sum(1 for n in tw_nodes if n["meta"]["trust_level"] == "high")
    blk_tw_count   = sum(1 for n in tw_nodes if n["meta"]["trust_level"] == "blocked")

    def integrity_html() -> str:
        items = []
        items.append(f'<div class="integrity-item ok">✓ {total} events across {len(set(n["table"] for n in nodes))} table(s)</div>')
        if corr_count:
            items.append(f'<div class="integrity-item warn">↩ {corr_count} correction event(s) — originals preserved in log</div>')
        if len(chain_edges):
            items.append(f'<div class="integrity-item ok">✓ {len(chain_edges)} hash-chain link(s) detected</div>')
        if len(corr_edges):
            items.append(f'<div class="integrity-item warn">╌ {len(corr_edges)} correction edge(s) in graph</div>')
        if danger_count:
            items.append(f'<div class="integrity-item err">🛑 {danger_count} danger node(s) — dignity or execution breach</div>')
        else:
            items.append(f'<div class="integrity-item ok">✓ No dignity violations detected</div>')
        # Signature summary
        if signed_count:
            items.append(f'<div class="integrity-item ok">✓ {signed_count} event(s) with valid mock signature</div>')
        if unsigned_count:
            items.append(f'<div class="integrity-item warn">○ {unsigned_count} event(s) unsigned (allowed)</div>')
        if invalid_count:
            items.append(f'<div class="integrity-item err">✗ {invalid_count} event(s) with INVALID signature — possible tampering</div>')
        # Trust integrity
        if tw_nodes:
            items.append(f'<div class="integrity-item ok">↻ {len(tw_nodes)} contribution event(s) with temporal trust weight</div>')
        if high_tw_count:
            items.append(f'<div class="integrity-item ok">↑ {high_tw_count} high-trust contribution(s) (≥ 0.7)</div>')
        if blk_tw_count:
            items.append(f'<div class="integrity-item err">🛑 {blk_tw_count} dignity-blocked contribution(s) — trust=0.0</div>')
        if fed_info_html:
            fed_depth = fed_info_html.get("federation_depth", 0)
            fed_cc = len(fed_info_html.get("counterclaimed_by", []))
            items.append(f'<div class="integrity-item ok">⇌ Federation depth {fed_depth} — linked to {len(fmap_html) - 1} other claim(s)</div>')
            if fed_cc:
                items.append(f'<div class="integrity-item warn">⚡ {fed_cc} counterclaim(s) recorded — disagreement preserved in log</div>')
        items.append(f'<div class="integrity-item ok">✓ No external scripts or stylesheets loaded</div>')
        items.append(f'<div class="integrity-item ok">✓ No network communication performed</div>')
        return "\n".join(items)

    # ── Federation panel HTML ────────────────────────────────
    def federation_html() -> str:
        if not fed_info_html:
            return '<div class="fed-panel"><span class="fed-none">(no federation events for this claim)</span></div>'

        depth = fed_info_html.get("federation_depth", 0)
        _FED_ROWS = [
            ("depends_on",        "Depends on",       ""),
            ("enables",           "Enables",           "fed-enables"),
            ("blocks",            "Blocks",            "fed-blocks"),
            ("blocked_by",        "Blocked by",        "fed-blocked"),
            ("counterclaims",     "Counterclaims",     "fed-counterclaim"),
            ("counterclaimed_by", "Counterclaimed by", "fed-counterclaim"),
            ("enabled_by",        "Enabled by",        "fed-enables"),
            ("depended_on_by",    "Depended on by",    ""),
            ("federation_link",   "Fed. links",        ""),
            ("amendment_of",      "Amends",            ""),
            ("derived_from",      "Derived from",      ""),
            ("dignity_override",  "Dignity override",  "fed-blocks"),
        ]
        rows = [
            f'<div class="fed-row">'
            f'<span class="fed-key">depth</span>'
            f'<span class="fed-val" style="font-family:var(--mono);font-size:1.4rem;font-weight:700;color:var(--cyan)">{depth}</span>'
            f'</div>'
        ]
        for key, label, tag_cls in _FED_ROWS:
            vals = fed_info_html.get(key, [])
            if vals:
                tags = " ".join(
                    f'<span class="fed-claim-tag {tag_cls}">{_h(v)}</span>'
                    for v in vals
                )
                rows.append(
                    f'<div class="fed-row">'
                    f'<span class="fed-key">{_h(label)}</span>'
                    f'<span class="fed-val">{tags}</span>'
                    f'</div>'
                )
        return f'<div class="fed-panel">\n' + "\n".join(rows) + "\n</div>"

    # ── Final result badge ───────────────────────────────────
    RESULT_COLOR = {
        "success":                   "var(--green)",
        "partial_success":           "var(--amber)",
        "failed":                    "var(--red)",
        "unexpected_outcome":        "var(--red)",
        "dignity_violation_detected":"var(--red)",
        "in progress":               "var(--muted)",
    }
    result_color = RESULT_COLOR.get(final_result, "var(--muted)")

    # ── Plan history context ─────────────────────────────────
    from sutable_log import read_all as _read_all
    _plan_events = [e for e in _read_all("plans") if e.get("claim_id") == claim_id]
    plan_tree_events  = [e for e in _plan_events
                         if e.get("event_type") in ("plan_tree_created", "plan_tree_amended", "plan_tree_corrected")]
    bundle_events_raw = [e for e in _plan_events
                         if e.get("event_type") in ("task_bundle_created", "task_bundle_blocked",
                                                     "task_bundle_ready", "task_bundle_abandoned")]

    # Correction chain
    _corr_by: dict[str, str] = {}
    for _pe in plan_tree_events:
        if _pe.get("event_type") == "plan_tree_corrected":
            _old = _pe.get("corrects_plan_id", "")
            _new = _pe.get("plan_id", "")
            if _old and _new:
                _corr_by[_old] = _new

    def plan_history_html() -> str:
        if not plan_tree_events and not bundle_events_raw:
            return '<div class="plan-panel"><span class="plan-none">(no plan events for this claim)</span></div>'

        rows: list[str] = []

        # Plan tree rows
        for pe in plan_tree_events:
            pid   = pe.get("plan_id", "?")
            et    = pe.get("event_type", "")
            ts    = pe.get("timestamp", "")[:19].replace("T", " ")
            reason = pe.get("correction_reason", "") or pe.get("amendment_reason", "")

            if pid in _corr_by:
                status_badge = '<span class="plan-badge plan-corrected">corrected</span>'
            elif et == "plan_tree_amended":
                status_badge = '<span class="plan-badge plan-amended">amended</span>'
            else:
                status_badge = '<span class="plan-badge plan-active">active</span>'

            corrects_row = ""
            if et == "plan_tree_corrected":
                old = pe.get("corrects_plan_id", "")
                corrects_row = f'<div class="plan-sub">corrects: <code>{_h(old)}</code></div>'
            if pid in _corr_by:
                corrects_row += f'<div class="plan-sub">↳ corrected by: <code>{_h(_corr_by[pid])}</code></div>'
            reason_row = f'<div class="plan-sub reason">{_h(reason)}</div>' if reason else ""

            rows.append(
                f'<div class="plan-row">'
                f'<code class="plan-id">{_h(pid)}</code> {status_badge}'
                f'<div class="plan-ts">{_h(ts)}</div>'
                f'{corrects_row}{reason_row}'
                f'</div>'
            )

        # Bundle rows
        if bundle_events_raw:
            rows.append('<hr class="plan-divider">')
            for be in bundle_events_raw:
                bid   = be.get("bundle_id", "?")
                et    = be.get("event_type", "")
                ts    = be.get("timestamp", "")[:19].replace("T", " ")
                dpid  = be.get("derived_from_plan_id", "")
                tc    = be.get("task_count", "?")
                bc    = be.get("blocked_count", 0)

                _bundle_badge_css = {
                    "task_bundle_created":   "bundle-created",
                    "task_bundle_blocked":   "bundle-blocked",
                    "task_bundle_ready":     "bundle-ready",
                    "task_bundle_abandoned": "bundle-abandoned",
                }
                badge_css = _bundle_badge_css.get(et, "bundle-created")
                status_lbl = et.replace("task_bundle_", "")
                status_badge = f'<span class="plan-badge {badge_css}">{status_lbl}</span>'
                from_row = f'<div class="plan-sub">from: <code>{_h(dpid)}</code></div>' if dpid else ""
                count_row = (f'<div class="plan-sub">{tc} tasks, {bc} blocked</div>'
                             if tc != "?" else "")

                rows.append(
                    f'<div class="plan-row bundle-row">'
                    f'<code class="plan-id">{_h(bid)}</code> {status_badge}'
                    f'<div class="plan-ts">{_h(ts)}</div>'
                    f'{from_row}{count_row}'
                    f'</div>'
                )

        return '<div class="plan-panel">\n' + "\n".join(rows) + "\n</div>"

    def plan_negotiation_html() -> str:
        """Generate HTML panel for plan negotiation signals."""
        try:
            from plan_contest_resolver import (
                aggregate_signals, build_full_contest_graph,
                get_plan_statuses, _load_plan_events, _get_plan_ids,
            )
            neg_events  = _load_plan_events(claim_id)
            neg_pids    = _get_plan_ids(neg_events)
            neg_signals = aggregate_signals(neg_events)
            neg_statuses= get_plan_statuses(neg_events)
            neg_contests= build_full_contest_graph(neg_events)
        except ImportError:
            return '<div class="plan-panel"><span class="plan-none">(plan_contest_resolver not available)</span></div>'

        neg_events_list = [
            ev for ev in neg_events
            if ev.get("event_type") in (
                "plan_supported", "plan_objected", "plan_contested",
                "plan_rejected", "plan_superseded", "active_plan_selected",
            )
        ]
        if not neg_events_list and not neg_contests:
            return '<div class="plan-panel"><span class="plan-none">(no negotiation signals for this claim)</span></div>'

        # Formal active plan
        formal_active = ""
        for ev in reversed(neg_events):
            if ev.get("event_type") == "active_plan_selected":
                formal_active = ev.get("selected_plan_id", "")
                break

        # Computed active plan
        computed_active = ""
        try:
            from active_plan_selector import select_active_plan
            sel_res = select_active_plan(claim_id)
            computed_active = sel_res.get("selected_plan_id") or ""
        except ImportError:
            pass

        rows: list[str] = []

        # Active plan badge
        effective_active = formal_active or computed_active
        if effective_active:
            formal_lbl = "(formal selection)" if formal_active else "(computed — not yet recorded)"
            rows.append(
                f'<div class="plan-row">'
                f'<span class="plan-badge plan-active">★ active</span> '
                f'<code class="plan-id">{_h(effective_active)}</code> '
                f'<span class="plan-ts">{_h(formal_lbl)}</span>'
                f'</div>'
            )
            rows.append('<hr class="plan-divider">')

        # Per-plan signal rows
        for pid in neg_pids:
            status = neg_statuses.get(pid, "open")
            sigs   = neg_signals.get(pid, {})
            sup_n  = sigs.get("support_count", 0)
            obj_n  = sigs.get("objection_count", 0)

            _status_css = {
                "active":     "plan-active",
                "contested":  "plan-contested",
                "corrected":  "plan-corrected",
                "superseded": "plan-amended",
                "rejected":   "bundle-abandoned",
                "open":       "bundle-created",
            }
            badge_css  = _status_css.get(status, "bundle-created")
            active_mark = "★ " if pid == effective_active else ""
            status_badge = f'<span class="plan-badge {badge_css}">{_h(active_mark + status)}</span>'

            signal_html = ""
            if sup_n or obj_n:
                signal_html = (
                    f'<div class="plan-sub">'
                    f'<span style="color:#22c55e">+{sup_n} support</span> '
                    f'<span style="color:#f97316">−{obj_n} objection</span>'
                    f'</div>'
                )

            obj_reasons = sigs.get("objection_reasons", [])
            obj_types   = list(sigs.get("objections_by_type", {}).keys())
            obj_rows = ""
            for i_o, reason in enumerate(obj_reasons):
                otype = obj_types[i_o] if i_o < len(obj_types) else "?"
                obj_rows += f'<div class="plan-sub reason">✗ [{_h(otype)}] {_h(reason[:80])}</div>'

            sup_rows = ""
            for reason in sigs.get("support_reasons", []):
                sup_rows += f'<div class="plan-sub">+ {_h(reason[:80])}</div>'

            rows.append(
                f'<div class="plan-row">'
                f'<code class="plan-id">{_h(pid)}</code> {status_badge}'
                f'{signal_html}{sup_rows}{obj_rows}'
                f'</div>'
            )

        # Contest chains
        if neg_contests:
            rows.append('<hr class="plan-divider">')
            rows.append('<div class="plan-sub" style="font-weight:600;margin-bottom:4px">Contest chains:</div>')
            for c in neg_contests:
                reason = c.get("reason", "")
                rows.append(
                    f'<div class="plan-row">'
                    f'<code class="plan-id">{_h(c["contested"])}</code>'
                    f'<span class="plan-badge plan-contested">contested_by</span>'
                    f'<code class="plan-id">{_h(c["counterplan"])}</code>'
                    + (f'<div class="plan-sub reason">{_h(reason)}</div>' if reason else "")
                    + f'</div>'
                )

        return '<div class="plan-panel">\n' + "\n".join(rows) + "\n</div>"

    # ── Assemble HTML ────────────────────────────────────────
    tl_items_html  = "\n".join(tl_item(i+1, n) for i, n in enumerate(nodes))
    table_rows_html= "\n".join(table_row(i+1, n) for i, n in enumerate(nodes))

    danger_banner = ""
    if danger_count:
        danger_banner = (
            '<div class="warn-banner">'
            '🛑 DIGNITY VIOLATION DETECTED — automated processing halted — '
            f'{danger_count} danger node(s) in this graph'
            '</div>'
        )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dan-Go Negotiation Graph — {_h(claim_id)}</title>
<style>
{_INLINE_CSS}
</style>
</head>
<body>

<header class="page-header">
  <h1>Dan-Go Negotiation Graph — {_h(claim_id)}</h1>
  <span class="subtitle">dango-gitsea-bridge / su-table · generated {_h(gen_ts)}</span>
</header>

{danger_banner}

<div class="container">

<!-- ── SUMMARY ─────────────────────────────────── -->
<section>
  <h2>Summary</h2>
  <div class="summary-grid">
    <div class="stat-card">
      <div class="val">{total}</div>
      <div class="lbl">Total Events</div>
    </div>
    <div class="stat-card {'danger' if danger_count else 'good'}">
      <div class="val" style="color:{_h(result_color)}">{_h(final_result.replace('_',' ').title())}</div>
      <div class="lbl">Final Result</div>
    </div>
    <div class="stat-card {'amber' if corr_count else ''}">
      <div class="val">{corr_count}</div>
      <div class="lbl">Corrections</div>
    </div>
    <div class="stat-card">
      <div class="val">{contrib_count}</div>
      <div class="lbl">Contributions</div>
    </div>
    <div class="stat-card {'danger' if danger_count else ''}">
      <div class="val">{danger_count}</div>
      <div class="lbl">Dignity Violations</div>
    </div>
    <div class="stat-card {'good' if signed_preview else ''}">
      <div class="val">{signed_preview}</div>
      <div class="lbl">Signed Events</div>
    </div>
    <div class="stat-card {'good' if high_trust else ''}">
      <div class="val">{high_trust}</div>
      <div class="lbl">High Trust</div>
    </div>
    <div class="stat-card {'danger' if blocked_trust else ''}">
      <div class="val">{blocked_trust}</div>
      <div class="lbl">Trust Blocked</div>
    </div>
    <div class="stat-card {'good' if fed_info_html else ''}">
      <div class="val">{fed_info_html.get('federation_depth', '—')}</div>
      <div class="lbl">Fed. Depth</div>
    </div>
  </div>
</section>

<!-- ── TIMELINE ─────────────────────────────────── -->
<section>
  <h2>Event Timeline</h2>
  <ul class="timeline">
{tl_items_html}
  </ul>
</section>

<!-- ── PLAN HISTORY ──────────────────────────────── -->
<section>
  <h2>Plan History</h2>
  {plan_history_html()}
</section>

<!-- ── PLAN NEGOTIATION ──────────────────────────── -->
<section>
  <h2>Plan Negotiation</h2>
  {plan_negotiation_html()}
</section>

<!-- ── CLAIM FEDERATION ─────────────────────────── -->
<section>
  <h2>Claim Federation</h2>
  {federation_html()}
</section>

<!-- ── MERMAID SOURCE ────────────────────────────── -->
<section>
  <h2>Mermaid Source</h2>
  <div class="mermaid-wrap">
    <div class="mermaid-toolbar">
      <span class="toolbar-left">flowchart TD · {total} nodes · {len(edges)} edges</span>
      <button class="copy-btn" id="copy-btn" onclick="copyMermaid()">Copy</button>
    </div>
    <div class="mermaid-hint">
      Paste into <strong>mermaid.live</strong> to render the graph visually.
      This file loads no external scripts — rendering is your choice, not ours.
    </div>
    <pre class="mermaid-src"><code id="mermaid-source">{_h(mermaid_src)}</code></pre>
  </div>
</section>

<!-- ── EVENT TABLE ───────────────────────────────── -->
<section>
  <h2>Event Table</h2>
  <div class="event-table-wrap">
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>table</th>
          <th>event_type</th>
          <th>speaker / contributor</th>
          <th>timestamp</th>
          <th>summary</th>
          <th>trust</th>
          <th>signature</th>
          <th>signer did</th>
          <th>event_hash</th>
          <th>prev_hash</th>
          <th>corrects</th>
        </tr>
      </thead>
      <tbody>
{table_rows_html}
      </tbody>
    </table>
  </div>
</section>

<!-- ── INTEGRITY NOTES ───────────────────────────── -->
<section>
  <h2>Integrity Notes</h2>
  <div class="integrity-block">
{integrity_html()}
  </div>
</section>

</div><!-- /container -->

<footer class="page-footer">
  dango-gitsea-bridge · su-table append-only log ·
  claim_id: {_h(claim_id)} ·
  {_h(gen_ts)} ·
  No external dependencies. No network communication.
</footer>

<script>
{_COPY_SCRIPT}
</script>

</body>
</html>"""

    return html


# ══════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Export a su-table negotiation graph to mermaid, text, or HTML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python runtime/graph_export.py --claim-id housing-001 --format text
  python runtime/graph_export.py --claim-id housing-001 --format mermaid
  python runtime/graph_export.py --claim-id housing-001 --format mermaid > examples/housing-001.graph.mmd
  python runtime/graph_export.py --claim-id housing-001 --format html --output examples/housing-001.graph.html
  python runtime/graph_export.py --list
        """,
    )
    p.add_argument("--claim-id", metavar="ID",
                   help="Claim ID to visualize")
    p.add_argument("--format",   choices=["mermaid", "text", "html"], default="text",
                   help="Output format (default: text)")
    p.add_argument("--output",   metavar="FILE",
                   help="Write output to FILE instead of stdout (required for --format html if piping)")
    p.add_argument("--list",     action="store_true",
                   help="List all available claim_ids in the su-table")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    if args.list:
        ids = list_claim_ids()
        if not ids:
            print("No claim_ids found in su-table.")
        else:
            print("Available claim_ids in su-table:")
            for cid in ids:
                print(f"  {cid}")
        return

    if not args.claim_id:
        print("Error: --claim-id is required (or use --list)", file=sys.stderr)
        sys.exit(1)

    graph = build_graph(args.claim_id)

    if not graph["nodes"]:
        print(f"No events found for claim_id: {args.claim_id}", file=sys.stderr)
        sys.exit(1)

    match args.format:
        case "mermaid":
            content = export_mermaid(graph)
        case "text":
            content = export_text(graph)
        case "html":
            content = export_html(graph)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
        print(f"✓ Written to {out_path}", file=sys.stderr)
        if args.format == "html":
            print(f"  Open in browser: file://{out_path.resolve()}", file=sys.stderr)
    else:
        print(content)


if __name__ == "__main__":
    main()
