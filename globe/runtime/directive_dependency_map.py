"""directive_dependency_map.py — Phase 37: Cross-Directive Dependency Map

Observes cross-directive relations across all Globe-layer Directives.
The dependency map is advisory display only — it is NOT execution order,
NOT a ranking of directives, and does NOT allocate responsibility.

INVARIANTS (permanent, not negotiable):
  Dependency map is advisory display only.
  Dependency is not execution order.
  Dependency does not rank directives.
  Dependency does not allocate responsibility.
  Human review is required before any real-world action.
  authority: none

Detected relation types (7):
  same_globe            — both directives belong to the same Globe
  shared_keyword        — meaningful non-template scope / title terms overlap
  shared_claim_source   — both converted from the same Claim
  shared_proposal_source — both trace back to the same Proposal
  shared_bridge_target  — both reference the same reality-feedback bridge target
  shared_resolution_status — both logs carry the same resolution_status value
  shared_attention_marker — both logs contain an attention-flagged entry_type

Data sources (read-only):
  globe/directives/*.json
  globe/claims/*.json
  globe/data/proposals.json
  globe/logs/*.jsonl
  globe/reports/bridge_target_links.json
  globe/reports/reality_feedback_bridge.json

CLI:
  python3 globe/runtime/directive_dependency_map.py summary
  python3 globe/runtime/directive_dependency_map.py save
  python3 globe/runtime/directive_dependency_map.py show-directive <id>
  python3 globe/runtime/directive_dependency_map.py show-globe <globe_id>
  python3 globe/runtime/directive_dependency_map.py show-relation <relation_type>
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────

_GLOBE_DIR      = Path(__file__).resolve().parents[1]
_DATA_DIR       = _GLOBE_DIR / "data"
_CLAIMS_DIR     = _GLOBE_DIR / "claims"
_DIRECTIVES_DIR = _GLOBE_DIR / "directives"
_LOGS_DIR       = _GLOBE_DIR / "logs"
_REPORTS_DIR    = _GLOBE_DIR / "reports"

_DEP_JSON = _REPORTS_DIR / "directive_dependency_map.json"
_DEP_MD   = _REPORTS_DIR / "directive_dependency_map.md"

# ─── Invariants ───────────────────────────────────────────────────────────────

DEPENDENCY_INVARIANTS = {
    "dependency_map_is_advisory_display_only":        True,
    "dependency_is_not_execution_order":              True,
    "dependency_does_not_rank_directives":            True,
    "dependency_does_not_allocate_responsibility":    True,
    "human_review_is_required_before_any_real_world_action": True,
    "authority": "none",
}

DEPENDENCY_PHRASES = [
    "Dependency map is advisory display only.",
    "Dependency is not execution order.",
    "Dependency does not rank directives.",
    "Dependency does not allocate responsibility.",
    "Human review is required before any real-world action.",
]

VALID_RELATION_TYPES = frozenset({
    "same_globe",
    "shared_keyword",
    "shared_claim_source",
    "shared_proposal_source",
    "shared_bridge_target",
    "shared_resolution_status",
    "shared_attention_marker",
})

# Attention-flagging entry_types (ordered by severity)
_ATTENTION_TYPES = ("objection", "rollback_request", "voluntary_resolution_signal")

# Protocol-level scope items — generic across all directives (template-derived)
_PROTOCOL_KW = frozenset({
    "情報共有", "任意参加意思", "熟議ログ", "未解決論点",
    "実行フィードバック", "Reality Feedback", "Dan-Go", "ログへの追記",
    "論点の整理", "整理と記録",
})


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _load_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except Exception:
                pass
    return entries


def _is_template_scope_item(item: str) -> bool:
    """Return True if a scope.in_scope item is a protocol-template phrase (not directive-specific)."""
    return sum(1 for kw in _PROTOCOL_KW if kw in item) >= 2


def _cjk_terms(text: str, min_len: int = 4) -> set[str]:
    """Extract CJK character runs of ≥ min_len and their 4-char n-grams."""
    terms: set[str] = set()
    # CJK Unified Ideographs + Hiragana + Katakana + Extension A
    for run in re.findall(
        r'[぀-ヿ㐀-䶿一-鿿]+', text
    ):
        if len(run) >= min_len:
            terms.add(run)
            for i in range(len(run) - 3):
                terms.add(run[i : i + 4])
    return terms


# ─── Data loaders ─────────────────────────────────────────────────────────────

def _load_directives() -> list[dict]:
    directives = []
    for p in sorted(_DIRECTIVES_DIR.glob("*.json")):
        d = _load_json(p)
        if isinstance(d, dict):
            directives.append(d)
    return directives


def _load_logs_by_directive() -> dict[str, list[dict]]:
    result: dict[str, list[dict]] = {}
    for p in sorted(_LOGS_DIR.glob("*.jsonl")):
        entries = _load_jsonl(p)
        result[p.stem] = entries
    return result


def _load_bridge_targets_by_directive() -> dict[str, list[str]]:
    """
    Returns directive_id → list of non-'none' candidate_target_type strings,
    sourced from bridge_target_links.json.
    """
    rpt = _load_json(_REPORTS_DIR / "bridge_target_links.json")
    result: dict[str, list[str]] = {}
    if not isinstance(rpt, dict):
        return result
    for c in rpt.get("candidates", []):
        did    = c.get("source_directive_id", "")
        target = c.get("candidate_target_type", "none")
        if target and target != "none":
            result.setdefault(did, []).append(target)
    return result


def _load_rfb_targets_by_directive() -> dict[str, list[str]]:
    """
    Returns directive_id → list of non-'none' suggested_bridge_target strings,
    sourced from reality_feedback_bridge.json.
    """
    rpt = _load_json(_REPORTS_DIR / "reality_feedback_bridge.json")
    result: dict[str, list[str]] = {}
    if not isinstance(rpt, dict):
        return result
    for r in rpt.get("records", []):
        did    = r.get("source_directive_id", "")
        target = r.get("suggested_bridge_target", "none")
        if target and target != "none":
            result.setdefault(did, []).append(target)
    return result


# ─── Node builder ─────────────────────────────────────────────────────────────

def _build_node(
    d: dict,
    logs: list[dict],
    bridge_targets: list[str],
    rfb_targets: list[str],
) -> dict:
    did = d.get("directive_id", "")
    resolution_statuses = sorted(set(
        e["resolution_status"] for e in logs
        if e.get("resolution_status")
    ))
    attention_types = sorted(set(
        e["entry_type"] for e in logs
        if e.get("entry_type") in _ATTENTION_TYPES
    ))
    all_targets = sorted(set(bridge_targets + rfb_targets))
    return {
        "directive_id":         did,
        "globe_id":             d.get("globe_id", ""),
        "title":                d.get("title", did),
        "source_claim_id":      d.get("source_claim_id", ""),
        "source_proposal_id":   d.get("source_proposal_id", ""),
        "step_count":           len(d.get("execution_steps", [])),
        "log_count":            len(logs),
        "resolution_statuses":  resolution_statuses,
        "attention_types":      attention_types,
        "bridge_targets":       all_targets,
        "has_objection":        "objection" in attention_types,
        "has_rollback":         "rollback_request" in attention_types,
        "has_vrs":              "voluntary_resolution_signal" in attention_types,
    }


# ─── Edge factory ─────────────────────────────────────────────────────────────

_edge_counter: dict[str, int] = {}


def _make_edge(
    src: str,
    tgt: str,
    relation_type: str,
    *,
    reason: str,
    shared_terms: list[str],
    confidence: str,
) -> dict:
    key = f"{relation_type}-{src}-{tgt}"
    n   = _edge_counter.get(key, 0)
    _edge_counter[key] = n + 1
    suffix = f"-{n}" if n else ""
    return {
        "edge_id":              f"edge-{relation_type}-{src.split('-')[-1]}-{tgt.split('-')[-1]}{suffix}",
        "source_directive_id":  src,
        "target_directive_id":  tgt,
        "relation_type":        relation_type,
        "relation_reason":      reason,
        "shared_terms":         shared_terms,
        "confidence":           confidence,
        "advisory_only":                    True,
        "not_execution_order":              True,
        "does_not_allocate_responsibility": True,
    }


# ─── Relation detectors ───────────────────────────────────────────────────────

def _detect_same_globe(n1: dict, n2: dict) -> list[dict]:
    """Both directives in the same Globe."""
    if not n1["globe_id"] or n1["globe_id"] != n2["globe_id"]:
        return []
    return [_make_edge(
        n1["directive_id"], n2["directive_id"],
        "same_globe",
        reason=f"Both directives belong to Globe {n1['globe_id']}",
        shared_terms=[n1["globe_id"]],
        confidence="high",
    )]


def _detect_shared_claim_source(n1: dict, n2: dict) -> list[dict]:
    """Both converted from the same Claim."""
    c1 = n1["source_claim_id"]
    c2 = n2["source_claim_id"]
    if not c1 or c1 != c2:
        return []
    return [_make_edge(
        n1["directive_id"], n2["directive_id"],
        "shared_claim_source",
        reason=f"Both directives originated from claim {c1}",
        shared_terms=[c1],
        confidence="high",
    )]


def _detect_shared_proposal_source(n1: dict, n2: dict) -> list[dict]:
    """Both trace back to the same Proposal."""
    p1 = n1["source_proposal_id"]
    p2 = n2["source_proposal_id"]
    if not p1 or p1 != p2:
        return []
    return [_make_edge(
        n1["directive_id"], n2["directive_id"],
        "shared_proposal_source",
        reason=f"Both directives originated from proposal {p1}",
        shared_terms=[p1],
        confidence="high",
    )]


def _detect_shared_keywords(d1: dict, d2: dict) -> list[dict]:
    """
    Shared scope items (non-template) or meaningful CJK keyword overlap.
    Template scope items are those containing ≥2 protocol meta-keywords.
    """
    edges: list[dict] = []

    scope1: set[str] = set(d1.get("scope", {}).get("in_scope", []))
    scope2: set[str] = set(d2.get("scope", {}).get("in_scope", []))
    shared = scope1 & scope2

    meaningful = [it for it in sorted(shared) if not _is_template_scope_item(it)]
    template   = [it for it in sorted(shared) if     _is_template_scope_item(it)]

    # High-confidence: directive-specific (non-template) shared scope items
    if meaningful:
        terms: list[str] = []
        for item in meaningful:
            for run in re.findall(r'[぀-ヿ㐀-䶿一-鿿]+', item):
                if len(run) >= 4:
                    terms.append(run)
        edges.append(_make_edge(
            d1["directive_id"], d2["directive_id"],
            "shared_keyword",
            reason=(
                f"Shared non-template scope item(s): "
                + "; ".join(f'"{it}"' for it in meaningful[:2])
            ),
            shared_terms=sorted(set(terms))[:8],
            confidence="high",
        ))

    # Low-confidence: template-level shared scope items
    if template:
        terms_t: list[str] = []
        for item in template[:3]:
            for run in re.findall(r'[぀-ヿ㐀-䶿一-鿿]+', item):
                if len(run) >= 4:
                    terms_t.append(run)
        edges.append(_make_edge(
            d1["directive_id"], d2["directive_id"],
            "shared_keyword",
            reason=(
                f"Shared protocol-template scope items ({len(template)} items) — "
                "these derive from the Dan-Go Directive template"
            ),
            shared_terms=sorted(set(terms_t))[:5],
            confidence="low",
        ))

    return edges


def _detect_shared_bridge_target(n1: dict, n2: dict) -> list[dict]:
    """
    Both directives reference the same bridge target.
    'both' is treated as a wildcard — if one side has 'both', it can match any non-none target.
    """
    t1: set[str] = set(n1["bridge_targets"])
    t2: set[str] = set(n2["bridge_targets"])
    if not t1 and not t2:
        return []

    # Expand 'both' to act as wildcard
    t1_real = t1 - {"both"}
    t2_real = t2 - {"both"}

    direct_match = t1_real & t2_real
    via_both = set()
    if "both" in t1 and t2_real:
        via_both.update(t2_real)
    if "both" in t2 and t1_real:
        via_both.update(t1_real)

    if direct_match:
        targets = sorted(direct_match)
        return [_make_edge(
            n1["directive_id"], n2["directive_id"],
            "shared_bridge_target",
            reason=f"Both reference bridge target(s): {', '.join(targets)}",
            shared_terms=targets,
            confidence="high",
        )]
    if via_both:
        targets = sorted(via_both)
        return [_make_edge(
            n1["directive_id"], n2["directive_id"],
            "shared_bridge_target",
            reason=(
                f"One directive has 'both' bridge target; other references {', '.join(targets)} "
                "— possible shared bridge connection"
            ),
            shared_terms=targets,
            confidence="low",
        )]
    return []


def _detect_shared_resolution_status(n1: dict, n2: dict) -> list[dict]:
    """Both logs carry the same resolution_status."""
    s1: set[str] = set(n1["resolution_statuses"])
    s2: set[str] = set(n2["resolution_statuses"])
    shared = s1 & s2
    if not shared:
        return []
    statuses = sorted(shared)
    return [_make_edge(
        n1["directive_id"], n2["directive_id"],
        "shared_resolution_status",
        reason=f"Both logs contain resolution_status: {', '.join(statuses)}",
        shared_terms=statuses,
        confidence="medium",
    )]


def _detect_shared_attention_marker(n1: dict, n2: dict) -> list[dict]:
    """Both logs contain the same attention-flagging entry_type."""
    a1: set[str] = set(n1["attention_types"])
    a2: set[str] = set(n2["attention_types"])
    shared = a1 & a2
    if not shared:
        return []
    # Determine highest-severity shared marker
    for marker in _ATTENTION_TYPES:
        if marker in shared:
            conf = ("high"   if marker in ("objection", "rollback_request")
                    else "medium")
            return [_make_edge(
                n1["directive_id"], n2["directive_id"],
                "shared_attention_marker",
                reason=(
                    f"Both directives' logs contain entry_type '{marker}' "
                    "— shared attention signal"
                ),
                shared_terms=sorted(shared),
                confidence=conf,
            )]
    return []


# ─── Main build function ──────────────────────────────────────────────────────

def build_dependency_map() -> dict:
    """Build and return the full dependency map.

    Advisory only. Not execution order. Not a ranking.
    """
    global _edge_counter
    _edge_counter = {}

    directives   = _load_directives()
    logs_by_did  = _load_logs_by_directive()
    btl_by_did   = _load_bridge_targets_by_directive()
    rfb_by_did   = _load_rfb_targets_by_directive()

    # Build node list
    nodes = []
    node_by_id: dict[str, dict] = {}
    for d in directives:
        did  = d.get("directive_id", "")
        logs = logs_by_did.get(did, [])
        node = _build_node(
            d, logs,
            btl_by_did.get(did, []),
            rfb_by_did.get(did, []),
        )
        nodes.append(node)
        node_by_id[did] = node

    # Detect edges for every unordered pair
    edges: list[dict] = []
    did_list = [n["directive_id"] for n in nodes]
    d_by_id  = {d.get("directive_id", ""): d for d in directives}

    for did1, did2 in combinations(did_list, 2):
        n1 = node_by_id[did1]
        n2 = node_by_id[did2]
        d1 = d_by_id[did1]
        d2 = d_by_id[did2]

        edges.extend(_detect_same_globe(n1, n2))
        edges.extend(_detect_shared_claim_source(n1, n2))
        edges.extend(_detect_shared_proposal_source(n1, n2))
        edges.extend(_detect_shared_keywords(d1, d2))
        edges.extend(_detect_shared_bridge_target(n1, n2))
        edges.extend(_detect_shared_resolution_status(n1, n2))
        edges.extend(_detect_shared_attention_marker(n1, n2))

    # Count by relation_type
    relation_counts: dict[str, int] = {}
    for e in edges:
        rt = e["relation_type"]
        relation_counts[rt] = relation_counts.get(rt, 0) + 1

    # Count by confidence
    confidence_counts: dict[str, int] = {}
    for e in edges:
        c = e["confidence"]
        confidence_counts[c] = confidence_counts.get(c, 0) + 1

    return {
        "map_id":           "globe-dependency-map",
        "generated_at":     _now(),
        "phase":            "37",
        "directive_count":  len(nodes),
        "edge_count":       len(edges),
        "relation_type_counts": relation_counts,
        "confidence_counts":    confidence_counts,
        "phase_phrases":    DEPENDENCY_PHRASES,
        **DEPENDENCY_INVARIANTS,
        "nodes":  nodes,
        "edges":  edges,
    }


# ─── Filtered views ───────────────────────────────────────────────────────────

def filter_by_directive(dep_map: dict, directive_id: str) -> dict:
    """Return nodes and edges touching the given directive."""
    edges = [
        e for e in dep_map.get("edges", [])
        if e["source_directive_id"] == directive_id
        or e["target_directive_id"] == directive_id
    ]
    touched = {e["source_directive_id"] for e in edges} | \
              {e["target_directive_id"] for e in edges}
    nodes = [n for n in dep_map.get("nodes", []) if n["directive_id"] in touched]
    return {"nodes": nodes, "edges": edges}


def filter_by_globe(dep_map: dict, globe_id: str) -> dict:
    """Return nodes and edges where at least one end is in the given Globe."""
    globe_dids = {
        n["directive_id"] for n in dep_map.get("nodes", [])
        if n["globe_id"] == globe_id
    }
    nodes = [n for n in dep_map.get("nodes", []) if n["directive_id"] in globe_dids]
    edges = [
        e for e in dep_map.get("edges", [])
        if e["source_directive_id"] in globe_dids
        or e["target_directive_id"] in globe_dids
    ]
    return {"nodes": nodes, "edges": edges}


def filter_by_relation(dep_map: dict, relation_type: str) -> dict:
    """Return all edges of the given relation_type."""
    edges = [e for e in dep_map.get("edges", []) if e["relation_type"] == relation_type]
    touched = {e["source_directive_id"] for e in edges} | \
              {e["target_directive_id"] for e in edges}
    nodes = [n for n in dep_map.get("nodes", []) if n["directive_id"] in touched]
    return {"nodes": nodes, "edges": edges}


# ─── Persistence ─────────────────────────────────────────────────────────────

def _build_markdown(dep_map: dict) -> str:
    lines: list[str] = []
    lines.append("# Directive Dependency Map (Phase 37)")
    lines.append("")
    lines.append(f"generated_at: {dep_map['generated_at']}")
    lines.append(f"directive_count: {dep_map['directive_count']}")
    lines.append(f"edge_count: {dep_map['edge_count']}")
    lines.append("")
    lines.append("## Invariants")
    lines.append("")
    lines.append("| Key | Value |")
    lines.append("|-----|-------|")
    for k, v in DEPENDENCY_INVARIANTS.items():
        lines.append(f"| `{k}` | `{v}` |")
    lines.append("")
    lines.append(
        "> Dependency map is advisory display only. It is not execution order, "
        "not a ranking of directives, and does not allocate responsibility. "
        "Human review is required before any real-world action."
    )
    lines.append("")
    lines.append("## Relation Type Counts")
    lines.append("")
    lines.append("| relation_type | count |")
    lines.append("|---------------|-------|")
    for rt, n in sorted(dep_map.get("relation_type_counts", {}).items()):
        lines.append(f"| `{rt}` | {n} |")
    lines.append("")
    lines.append("## Nodes (Directives)")
    lines.append("")
    for node in dep_map.get("nodes", []):
        lines.append(f"### {node['directive_id']}")
        lines.append(f"**globe_id:** `{node['globe_id']}` &nbsp; "
                     f"**steps:** {node['step_count']} &nbsp; "
                     f"**logs:** {node['log_count']}")
        lines.append(f"**title:** {node['title']}")
        if node["resolution_statuses"]:
            lines.append(f"**resolution_status:** {', '.join(node['resolution_statuses'])}")
        if node["bridge_targets"]:
            lines.append(f"**bridge_targets:** {', '.join(node['bridge_targets'])}")
        lines.append("")
    lines.append("## Edges (Relations)")
    lines.append("")
    for e in dep_map.get("edges", []):
        lines.append(f"### {e['edge_id']}")
        lines.append(f"**{e['source_directive_id']}** ↔ **{e['target_directive_id']}**")
        lines.append(f"relation_type: `{e['relation_type']}` &nbsp; "
                     f"confidence: `{e['confidence']}`")
        lines.append(f"reason: {e['relation_reason']}")
        if e["shared_terms"]:
            lines.append(f"shared_terms: {', '.join(e['shared_terms'][:6])}")
        lines.append("")
    for phrase in DEPENDENCY_PHRASES:
        lines.append(f'> "{phrase}"')
    return "\n".join(lines)


def save_dependency_map() -> tuple[Path, Path]:
    dep_map = build_dependency_map()
    _REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    _DEP_JSON.write_text(
        json.dumps(dep_map, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _DEP_MD.write_text(_build_markdown(dep_map), encoding="utf-8")
    return _DEP_JSON, _DEP_MD


def load_dependency_map() -> dict:
    if _DEP_JSON.exists():
        try:
            raw = json.loads(_DEP_JSON.read_text(encoding="utf-8"))
            if isinstance(raw, dict) and "edges" in raw:
                return raw
        except Exception:
            pass
    return build_dependency_map()


# ─── CLI print helpers ────────────────────────────────────────────────────────

_CONF_COLOUR = {"high": "●", "medium": "◑", "low": "○"}
_REL_ICON = {
    "same_globe":              "🌐",
    "shared_keyword":          "🔤",
    "shared_claim_source":     "📌",
    "shared_proposal_source":  "📋",
    "shared_bridge_target":    "🔗",
    "shared_resolution_status":"🏁",
    "shared_attention_marker": "⚠️",
}


def _print_node(node: dict, indent: str = "  ") -> None:
    print(f"{indent}🗂️  {node['directive_id']}  [globe:{node['globe_id']}]")
    print(f"{indent}    {node['title'][:60]}")
    if node["resolution_statuses"]:
        print(f"{indent}    resolution: {', '.join(node['resolution_statuses'])}")
    if node["attention_types"]:
        print(f"{indent}    attention:  {', '.join(node['attention_types'])}")
    print()


def _print_edge(e: dict, indent: str = "  ") -> None:
    icon = _REL_ICON.get(e["relation_type"], "•")
    conf = _CONF_COLOUR.get(e["confidence"], "?")
    print(f"{indent}{icon} {e['relation_type']:28s} {conf} {e['confidence']}")
    print(f"{indent}    {e['source_directive_id']} ↔ {e['target_directive_id']}")
    print(f"{indent}    reason: {e['relation_reason'][:90]}")
    if e["shared_terms"]:
        print(f"{indent}    terms:  {', '.join(e['shared_terms'][:5])}")
    print()


def print_dependency_summary(dep_map: dict) -> None:
    print(f"\nDirective Dependency Map (Phase 37)")
    print("=" * 60)
    print(f"  generated_at:    {dep_map.get('generated_at','')}")
    print(f"  directive_count: {dep_map.get('directive_count', 0)}")
    print(f"  edge_count:      {dep_map.get('edge_count', 0)}")
    print()
    print("  Relation type counts:")
    for rt, n in sorted(dep_map.get("relation_type_counts", {}).items()):
        icon = _REL_ICON.get(rt, "•")
        print(f"    {icon} {rt:28s}: {n}")
    print()
    print("  Confidence counts:")
    for conf, n in sorted(dep_map.get("confidence_counts", {}).items()):
        c = _CONF_COLOUR.get(conf, "?")
        print(f"    {c} {conf:10s}: {n}")
    print()
    print("  Nodes:")
    for node in dep_map.get("nodes", []):
        _print_node(node)
    print("  All edges:")
    for e in dep_map.get("edges", []):
        _print_edge(e)
    for phrase in DEPENDENCY_PHRASES:
        print(f'  "{phrase}"')


def print_filtered(view: dict, label: str) -> None:
    print(f"\nDirective Dependency Map — {label}")
    print("=" * 60)
    print(f"  {len(view['nodes'])} nodes  ·  {len(view['edges'])} edges")
    print()
    print("  Nodes:")
    for node in view["nodes"]:
        _print_node(node)
    print("  Edges:")
    for e in view["edges"]:
        _print_edge(e)
    for phrase in DEPENDENCY_PHRASES:
        print(f'  "{phrase}"')


# ─── CLI entry point ──────────────────────────────────────────────────────────

def main(argv: list[str]) -> None:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return

    cmd = argv[0]

    if cmd == "summary":
        dep_map = build_dependency_map()
        print_dependency_summary(dep_map)
        return

    if cmd == "save":
        dep_map = build_dependency_map()
        print_dependency_summary(dep_map)
        jp, mp = save_dependency_map()
        print(f"Saved: {jp}")
        print(f"Saved: {mp}")
        return

    if cmd == "show-directive":
        if len(argv) < 2:
            print("Usage: directive_dependency_map.py show-directive <directive_id>",
                  file=sys.stderr)
            sys.exit(1)
        dep_map = load_dependency_map()
        view    = filter_by_directive(dep_map, argv[1])
        if not view["edges"] and not view["nodes"]:
            print(f"No dependency edges for directive: {argv[1]}", file=sys.stderr)
            sys.exit(1)
        print_filtered(view, f"directive={argv[1]}")
        return

    if cmd == "show-globe":
        if len(argv) < 2:
            print("Usage: directive_dependency_map.py show-globe <globe_id>",
                  file=sys.stderr)
            sys.exit(1)
        dep_map = load_dependency_map()
        view    = filter_by_globe(dep_map, argv[1])
        if not view["nodes"]:
            print(f"No directives found for globe: {argv[1]}", file=sys.stderr)
            sys.exit(1)
        print_filtered(view, f"globe={argv[1]}")
        return

    if cmd == "show-relation":
        if len(argv) < 2:
            print("Usage: directive_dependency_map.py show-relation <relation_type>",
                  file=sys.stderr)
            sys.exit(1)
        rtype = argv[1]
        if rtype not in VALID_RELATION_TYPES:
            print(f"Unknown relation_type: {rtype}", file=sys.stderr)
            print(f"Valid types: {', '.join(sorted(VALID_RELATION_TYPES))}",
                  file=sys.stderr)
            sys.exit(1)
        dep_map = load_dependency_map()
        view    = filter_by_relation(dep_map, rtype)
        if not view["edges"]:
            print(f"No edges of relation_type: {rtype}", file=sys.stderr)
            sys.exit(1)
        print_filtered(view, f"relation={rtype}")
        return

    print(f"Unknown command: {cmd}", file=sys.stderr)
    print(
        "Commands: summary | save | show-directive <id> | "
        "show-globe <id> | show-relation <type>",
        file=sys.stderr,
    )
    sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
