#!/usr/bin/env python3
"""
federation_graph.py — dango-gitsea-bridge / claim federation

Build and export a cross-claim federation graph.

The federation graph shows relationships BETWEEN claims.
(The negotiation graph shows events WITHIN a single claim.)

Node = claim_id
Edge = federation relationship (depends_on, enables, blocks, counterclaim, …)

Export formats:
  text    — human-readable terminal output
  mermaid — Mermaid flowchart TD (paste into mermaid.live)
  dict    — Python dict for HTML integration

CLI:
  python runtime/federation_graph.py
  python runtime/federation_graph.py examples/claim-federation.json
  python runtime/federation_graph.py --format mermaid
  python runtime/federation_graph.py --format text
  python runtime/federation_graph.py --output examples/federation.graph.mmd
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from claim_federation import (
    build_federation_map,
    load_federation_events,
    get_claim_summary,
    list_claim_ids,
    _extract_relationships,
)

# ── Mermaid styling ────────────────────────────────────────────

MERMAID_CLASSDEFS = """\
  classDef claim          fill:#1e3a5f,stroke:#2563eb,color:#dbeafe
  classDef counterclaim   fill:#450a0a,stroke:#dc2626,color:#fee2e2
  classDef amendment      fill:#2e1065,stroke:#7c3aed,color:#ede9fe
  classDef derived        fill:#064e3b,stroke:#059669,color:#d1fae5
  classDef blocked        fill:#1c1917,stroke:#78716c,color:#d6d3d1\
"""

# Shape for each claim role (inferred from its relationships)
def _claim_shape(claim_id: str, fmap: dict) -> str:
    """Return mermaid shape based on the claim's dominant role."""
    info = fmap.get(claim_id, {})
    if info.get("counterclaims") or info.get("counterclaimed_by"):
        return ("{\"{label}\"}", "counterclaim")  # hex for conflict
    if info.get("amendment_of"):
        return ("(\"{label}\")", "amendment")     # round for amendment
    if info.get("derived_from"):
        return ("[\"{label}\"]", "derived")       # rect
    return ("[\"{label}\"]", "claim")             # default rect


# Edge styles
EDGE_ARROW: dict[str, str] = {
    "depends_on":       "-->",
    "enables":          "==>",       # thick arrow
    "blocks":           "-.-X",      # dashed with X
    "counterclaim":     "-.->",      # dashed
    "amendment_of":     "-->",
    "derived_from":     "-.->",
    "federation_link":  "---",       # undirected
    "dignity_override": "-->",
    "correction_of":    "-.->",
}

EDGE_LABEL: dict[str, str] = {
    "depends_on":       "depends on",
    "enables":          "enables",
    "blocks":           "blocks",
    "counterclaim":     "counterclaim",
    "amendment_of":     "amends",
    "derived_from":     "derived from",
    "federation_link":  "linked",
    "dignity_override": "dignity override",
    "correction_of":    "corrects",
}

EDGE_STYLE_CLASS: dict[str, str] = {
    "depends_on":       "",               # default
    "enables":          "stroke:#16a34a", # green
    "blocks":           "stroke:#dc2626", # red
    "counterclaim":     "stroke:#dc2626,stroke-dasharray:5 5",
    "amendment_of":     "stroke:#7c3aed", # violet
    "derived_from":     "stroke:#64748b", # gray
    "federation_link":  "stroke:#22d3ee", # cyan
    "dignity_override": "stroke:#ea580c", # orange
    "correction_of":    "stroke:#6b7280", # gray
}


# ── Graph builder ──────────────────────────────────────────────

def build_graph(events: list[dict]) -> dict[str, Any]:
    """
    Build a federation graph dict from a list of events.

    Returns:
      {
        "nodes": [{id, label, role}, ...],
        "edges": [{from, to, rel, label}, ...],
        "meta":  {total_claims, total_edges, has_counterclaims, ...}
      }
    """
    fmap = build_federation_map(events)

    nodes: list[dict] = []
    edges: list[dict] = []

    claim_ids = list_claim_ids(fmap)

    # Collect all edges (avoid duplicates for symmetric federation_link)
    seen_edges: set[tuple[str, str, str]] = set()

    for src, rel, dst, reason in (
        (s, r, d, rsn)
        for e in events
        for s, r, d, rsn in _extract_relationships(e)
    ):
        # _extract_relationships() uses claim_id=src (DOWNSTREAM), depends_on_claim_id=dst (UPSTREAM).
        # "enables" and "blocks" mean UPSTREAM acts on DOWNSTREAM → flip so arrows read correctly.
        if rel in ("enables", "blocks"):
            src, dst = dst, src

        edge_key = (src, rel, dst)
        # Skip duplicate direction of symmetric links
        sym_key  = (dst, rel, src)
        if edge_key in seen_edges or (rel == "federation_link" and sym_key in seen_edges):
            continue
        seen_edges.add(edge_key)
        edges.append({"from": src, "rel": rel, "to": dst, "reason": reason,
                      "label": EDGE_LABEL.get(rel, rel)})

    # Build nodes for all claims encountered
    for cid in claim_ids:
        info = fmap.get(cid, {})
        role = "claim"
        if info.get("counterclaims") or info.get("counterclaimed_by"):
            role = "counterclaim"
        elif info.get("amendment_of"):
            role = "amendment"
        elif info.get("derived_from"):
            role = "derived"
        nodes.append({"id": cid, "label": cid, "role": role, "info": get_claim_summary(cid, fmap)})

    has_counterclaims = any(e["rel"] == "counterclaim" for e in edges)
    has_blocks        = any(e["rel"] == "blocks" for e in edges)

    meta = {
        "total_claims":      len(nodes),
        "total_edges":       len(edges),
        "has_counterclaims": has_counterclaims,
        "has_blocks":        has_blocks,
        "claim_ids":         claim_ids,
    }

    return {"nodes": nodes, "edges": edges, "meta": meta, "fmap": fmap}


# ── Mermaid export ─────────────────────────────────────────────

def export_mermaid(graph: dict) -> str:
    nodes = graph["nodes"]
    edges = graph["edges"]
    meta  = graph["meta"]
    fmap  = graph.get("fmap", {})

    if not nodes:
        return "%% No federation events found\nflowchart TD\n  empty[\"(no federation)\"]"

    lines: list[str] = []
    lines.append(f"%% Claim Federation Graph")
    lines.append(f"%% Generated by dango-gitsea-bridge / federation_graph.py")
    lines.append(f"%% Claims: {meta['total_claims']}  Edges: {meta['total_edges']}")
    if meta.get("has_counterclaims"):
        lines.append(f"%% ⚠ Counterclaims present — disagreement recorded in graph")
    lines.append("")
    lines.append("flowchart TD")
    lines.append(MERMAID_CLASSDEFS)
    lines.append("")
    lines.append("  %% ── Claim nodes ─────────────────────────────")

    for node in nodes:
        cid  = node["id"]
        role = node["role"]
        info = fmap.get(cid, {})

        # Choose shape
        if role == "counterclaim" or info.get("counterclaimed_by"):
            shape_open, shape_close = "{\"", "\"}"
        elif role == "amendment":
            shape_open, shape_close = "(\"", "\")"
        else:
            shape_open, shape_close = "[\"", "\"]"

        lines.append(f'  {cid}{shape_open}{cid}{shape_close}:::{role}')

    lines.append("")
    lines.append("  %% ── Federation edges ────────────────────────")

    # Track edge style indices for linkStyle
    edge_styles: list[str] = []
    for edge in edges:
        src   = edge["from"]
        dst   = edge["to"]
        rel   = edge["rel"]
        arrow = EDGE_ARROW.get(rel, "-->")
        elbl  = edge["label"]
        lines.append(f'  {src} {arrow} |{elbl}| {dst}')
        edge_styles.append(EDGE_STYLE_CLASS.get(rel, ""))

    # Add linkStyle for colored edges
    lines.append("")
    for i, style in enumerate(edge_styles):
        if style:
            lines.append(f"  linkStyle {i} {style}")

    return "\n".join(lines)


# ── Text export ────────────────────────────────────────────────

_REL_ICON: dict[str, str] = {
    "depends_on":       "→  [depends on]",
    "enables":          "⇒  [enables]",
    "blocks":           "✗  [blocks]",
    "counterclaim":     "⚡ [counterclaim]",
    "amendment_of":     "✏ [amends]",
    "derived_from":     "⬡  [derived from]",
    "federation_link":  "⟷  [linked]",
    "dignity_override": "⚠  [dignity override]",
    "correction_of":    "↩  [corrects]",
}


def export_text(graph: dict) -> str:
    nodes = graph["nodes"]
    edges = graph["edges"]
    meta  = graph["meta"]

    if not nodes:
        return "CLAIM FEDERATION\n  (no federation events found)"

    lines: list[str] = []
    lines.append("=" * 60)
    lines.append("CLAIM FEDERATION GRAPH")
    lines.append("=" * 60)
    lines.append(f"Claims:       {meta['total_claims']}")
    lines.append(f"Relationships:{meta['total_edges']}")
    if meta.get("has_counterclaims"):
        lines.append("⚠ Counterclaims: disagreement recorded")
    if meta.get("has_blocks"):
        lines.append("✗ Blocks: execution constraints present")
    lines.append("")

    # Group edges by source
    by_src: dict[str, list[dict]] = {}
    for e in edges:
        by_src.setdefault(e["from"], []).append(e)

    lines.append("── CLAIM RELATIONSHIPS ──")
    lines.append("")
    for node in nodes:
        cid = node["id"]
        lines.append(f"  {cid}")
        for edge in by_src.get(cid, []):
            icon = _REL_ICON.get(edge["rel"], "?")
            reason = edge.get("reason", "")
            reason_str = f'  "{reason}"' if reason else ""
            lines.append(f"    {icon} {edge['to']}{reason_str}")
        if not by_src.get(cid):
            lines.append("    (no outgoing relationships)")
        lines.append("")

    lines.append("=" * 60)
    return "\n".join(lines)


# ── CLI ───────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Build and export a claim federation graph.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # From su-table, text output
  python runtime/federation_graph.py --format text

  # From file, mermaid output
  python runtime/federation_graph.py examples/claim-federation.json --format mermaid

  # Save mermaid to file
  python runtime/federation_graph.py examples/claim-federation.json \\
    --format mermaid --output examples/federation.graph.mmd
        """,
    )
    p.add_argument("events_file", metavar="EVENTS_FILE", nargs="?",
                   help="JSON file with list of federation events (default: read su-table)")
    p.add_argument("--format", choices=["text", "mermaid"], default="text",
                   help="Output format (default: text)")
    p.add_argument("--output", metavar="FILE",
                   help="Write output to FILE (default: stdout)")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    if args.events_file:
        path = Path(args.events_file)
        if not path.exists():
            print(f"Error: file not found: {path}", file=sys.stderr)
            sys.exit(1)
        with open(path, encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error: invalid JSON: {e}", file=sys.stderr)
                sys.exit(1)
        events = data if isinstance(data, list) else [data]
    else:
        events = load_federation_events()

    if not events:
        print("No federation events found.", file=sys.stderr)
        sys.exit(1)

    graph = build_graph(events)

    content = export_mermaid(graph) if args.format == "mermaid" else export_text(graph)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content + "\n", encoding="utf-8")
        print(f"✓ Written to {out}", file=sys.stderr)
    else:
        print(content)


if __name__ == "__main__":
    main()
