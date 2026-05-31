"""contribution_timeline.py — Phase 32: Contribution Timeline View

Builds a chronological timeline of all Execution Log, Resolution Signal,
Reality Feedback, and Bridge Target Link events across Globe directives.

INVARIANTS (permanent, not negotiable):
  Timeline is advisory display only.
  Timeline is not proof of impact.
  Timeline does not rank participants.
  Timeline does not allocate resources.
  Human review is required before any real-world action.
  authority: none

Source types:
  execution_log       — globe/logs/*.jsonl  (non-resolution-signal entries)
  resolution_signal   — globe/logs/*.jsonl  (voluntary_resolution_signal entries)
  reality_feedback    — globe/reports/reality_feedback_bridge.json
  bridge_target_link  — globe/reports/bridge_target_links.json

CLI:
  python3 globe/runtime/contribution_timeline.py summary
  python3 globe/runtime/contribution_timeline.py save
  python3 globe/runtime/contribution_timeline.py show-globe <globe_id>
  python3 globe/runtime/contribution_timeline.py show-directive <directive_id>
  python3 globe/runtime/contribution_timeline.py show-type execution_log|resolution_signal|reality_feedback|bridge_target_link
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────

_GLOBE_DIR      = Path(__file__).resolve().parents[1]
_REPORTS_DIR    = _GLOBE_DIR / "reports"
_LOGS_DIR       = _GLOBE_DIR / "logs"

_BRIDGE_REPORT  = _REPORTS_DIR / "reality_feedback_bridge.json"
_LINKS_REPORT   = _REPORTS_DIR / "bridge_target_links.json"
_TIMELINE_JSON  = _REPORTS_DIR / "contribution_timeline.json"
_TIMELINE_MD    = _REPORTS_DIR / "contribution_timeline.md"

# ─── Invariants ───────────────────────────────────────────────────────────────

TIMELINE_INVARIANTS = {
    "timeline_is_advisory_display_only": True,
    "timeline_is_not_proof_of_impact": True,
    "timeline_does_not_rank_participants": True,
    "timeline_does_not_allocate_resources": True,
    "human_review_is_required_before_any_real_world_action": True,
    "authority": "none",
}

TIMELINE_PHRASES = [
    "Timeline is advisory display only.",
    "Timeline is not proof of impact.",
    "Timeline does not rank participants.",
    "Timeline does not allocate resources.",
    "Human review is required before any real-world action.",
]

VALID_SOURCE_TYPES = frozenset({
    "execution_log", "resolution_signal", "reality_feedback", "bridge_target_link",
})

# ─── Event-type display metadata ──────────────────────────────────────────────

_EVENT_ICON = {
    "human_approval":              "✅",
    "execution_attempt":           "▶️",
    "observation":                 "👁️",
    "feedback":                    "💬",
    "objection":                   "⚠️",
    "rollback_request":            "↩️",
    "voluntary_resolution_signal": "🏳️",
    "resolution_signal":           "🏳️",
    "reality_feedback":            "🔗",
    "bridge_target_link":          "🔗",
    "link_candidate":              "🔗",
}

_RS_ICON = {
    "resolved":          "✅",
    "partially_resolved":"🟡",
    "paused":            "⏸️",
    "unresolved":        "🔴",
    "contested":         "⚔️",
}

_ATTENTION_TYPES = frozenset({
    "objection", "rollback_request",
})
_ATTENTION_RS = frozenset({
    "unresolved", "contested",
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
    items = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                items.append(json.loads(line))
            except Exception:
                pass
    return items


def _excerpt(text: str, max_len: int = 180) -> str:
    text = " ".join(str(text).split())
    return text[:max_len] + ("…" if len(text) > max_len else "")


def _sort_key(item: dict) -> tuple:
    """Stable sort key: created_at (ISO string sorts correctly) then source_type + source_id."""
    return (item["created_at"], item["source_type"], item["source_id"])


def _make_item(
    timeline_id: str,
    globe_id: str,
    directive_id: str,
    source_type: str,
    source_id: str,
    event_type: str,
    actor_type: str,
    actor_name: str,
    title: str,
    content: str,
    created_at: str,
    resolution_status: str = "",
    bridge_target: str = "",
    confidence: str = "",
    needs_attention: bool = False,
) -> dict:
    return {
        "timeline_id": timeline_id,
        "globe_id": globe_id,
        "directive_id": directive_id,
        "source_type": source_type,
        "source_id": source_id,
        "event_type": event_type,
        "actor_type": actor_type,
        "actor_name": actor_name,
        "title": title,
        "content": _excerpt(content),
        "created_at": created_at,
        "resolution_status": resolution_status,
        "bridge_target": bridge_target,
        "confidence": confidence,
        "needs_attention": needs_attention,
        "advisory_only": True,
        "not_proof_of_impact": True,
    }


# ─── Source builders ──────────────────────────────────────────────────────────

def _build_from_logs() -> list[dict]:
    """Build timeline items from execution log JSONL files.

    voluntary_resolution_signal → source_type: resolution_signal
    all other entry types        → source_type: execution_log
    """
    items: list[dict] = []
    for p in sorted(_LOGS_DIR.glob("*.jsonl")):
        for entry in _load_jsonl(p):
            et = entry.get("entry_type", "")
            lid = entry.get("log_id", "")
            did = entry.get("directive_id", "")
            gid = entry.get("globe_id", "")
            actor_t = entry.get("actor_type", "")
            actor_n = entry.get("actor_name", actor_t)
            content = entry.get("content", "")
            ts = entry.get("created_at", "")
            rs = entry.get("resolution_status", "")

            if et == "voluntary_resolution_signal":
                src_type = "resolution_signal"
                rs_icon = _RS_ICON.get(rs, "")
                title = (f"Resolution Signal: {rs_icon} {rs}"
                         if rs else "Resolution Signal")
                needs_attn = rs in _ATTENTION_RS
            else:
                src_type = "execution_log"
                icon = _EVENT_ICON.get(et, "•")
                title = f"{icon} {et.replace('_', ' ')}"
                needs_attn = et in _ATTENTION_TYPES

            tid = f"tl-{src_type[:4]}-{lid}"
            items.append(_make_item(
                timeline_id=tid,
                globe_id=gid,
                directive_id=did,
                source_type=src_type,
                source_id=lid,
                event_type=et,
                actor_type=actor_t,
                actor_name=actor_n,
                title=title,
                content=content,
                created_at=ts,
                resolution_status=rs,
                needs_attention=needs_attn,
            ))
    return items


def _build_from_bridge() -> list[dict]:
    """Build timeline items from reality_feedback_bridge.json records."""
    items: list[dict] = []
    data = _load_json(_BRIDGE_REPORT)
    if not isinstance(data, dict):
        return items
    for r in data.get("records", []):
        fid = r.get("feedback_id", "")
        did = r.get("source_directive_id", "")
        gid = r.get("globe_id", "")
        et = r.get("entry_type", "")
        actor_t = r.get("actor_type", "")
        actor_n = r.get("actor_name", actor_t)
        content = r.get("content", "")
        reason = r.get("suggested_reason", "")
        ts = r.get("source_entry_created_at", r.get("record_generated_at", ""))
        target = r.get("suggested_bridge_target", "")

        title = f"🔗 Feedback Bridge: {et.replace('_', ' ')} → {target}"
        items.append(_make_item(
            timeline_id=f"tl-rfb-{fid}",
            globe_id=gid,
            directive_id=did,
            source_type="reality_feedback",
            source_id=fid,
            event_type=et,
            actor_type=actor_t,
            actor_name=actor_n,
            title=title,
            content=f"{content} [{reason}]" if reason else content,
            created_at=ts,
            bridge_target=target,
            needs_attention=(target in {"both", "care_loop_reopen"}),
        ))
    return items


def _build_from_links() -> list[dict]:
    """Build timeline items from bridge_target_links.json candidates."""
    items: list[dict] = []
    data = _load_json(_LINKS_REPORT)
    if not isinstance(data, dict):
        return items
    for c in data.get("candidates", []):
        lid = c.get("link_id", "")
        did = c.get("source_directive_id", "")
        gid = c.get("globe_id", "")
        conf = c.get("confidence", "")
        ctype = c.get("candidate_target_type", "")
        desc = c.get("candidate_description", "")
        reason = c.get("match_reason", "")
        ts = c.get("created_at", "")
        target = c.get("suggested_bridge_target", "")

        title = f"🔗 Link Candidate: {ctype} ({conf})"
        items.append(_make_item(
            timeline_id=f"tl-lnk-{lid}",
            globe_id=gid,
            directive_id=did,
            source_type="bridge_target_link",
            source_id=lid,
            event_type="link_candidate",
            actor_type="system",
            actor_name="bridge_target_linker",
            title=title,
            content=f"{desc} [{reason}]" if reason else desc,
            created_at=ts,
            bridge_target=target,
            confidence=conf,
            needs_attention=(conf == "high"),
        ))
    return items


# ─── Timeline assembly ────────────────────────────────────────────────────────

def build_timeline() -> dict:
    """Build and return the full contribution timeline.

    Advisory only. Not proof of impact. No ranking. No allocation.
    Sorted by created_at ascending, then source_type + source_id (stable).
    """
    items: list[dict] = []
    items.extend(_build_from_logs())
    items.extend(_build_from_bridge())
    items.extend(_build_from_links())

    # Stable chronological sort — no relevance score
    items.sort(key=_sort_key)

    # Counts
    by_source: dict[str, int] = {}
    by_globe: dict[str, int] = {}
    by_directive: dict[str, int] = {}
    attention_count = 0
    for it in items:
        st = it["source_type"]
        gid = it["globe_id"]
        did = it["directive_id"]
        by_source[st] = by_source.get(st, 0) + 1
        if gid:
            by_globe[gid] = by_globe.get(gid, 0) + 1
        if did:
            by_directive[did] = by_directive.get(did, 0) + 1
        if it["needs_attention"]:
            attention_count += 1

    return {
        "timeline_id": "globe-contribution-timeline",
        "generated_at": _now(),
        "total_items": len(items),
        "attention_items": attention_count,
        "source_type_counts": by_source,
        "by_globe": by_globe,
        "by_directive": by_directive,
        **TIMELINE_INVARIANTS,
        "phase": "32",
        "phase_phrases": TIMELINE_PHRASES,
        "items": items,
    }


# ─── Persistence ──────────────────────────────────────────────────────────────

def _build_markdown(tl: dict) -> str:
    lines: list[str] = []
    lines.append("# Contribution Timeline (Phase 32)")
    lines.append("")
    lines.append(f"generated_at: {tl['generated_at']}")
    lines.append(f"total_items: {tl['total_items']}")
    lines.append(f"attention_items: {tl['attention_items']}")
    lines.append("")
    lines.append("## Invariants")
    lines.append("")
    lines.append("| Key | Value |")
    lines.append("|-----|-------|")
    for k, v in TIMELINE_INVARIANTS.items():
        lines.append(f"| `{k}` | `{v}` |")
    lines.append("")
    lines.append("## Source Type Counts")
    lines.append("")
    lines.append("| source_type | count |")
    lines.append("|-------------|-------|")
    for st, cnt in sorted(tl["source_type_counts"].items()):
        lines.append(f"| `{st}` | {cnt} |")
    lines.append("")
    lines.append("## Timeline")
    lines.append("")
    lines.append("| # | created_at | source_type | event_type | globe_id | actor | title |")
    lines.append("|---|-----------|-------------|-----------|---------|-------|-------|")
    for i, item in enumerate(tl["items"], 1):
        ts = item["created_at"][:16].replace("T", " ") if item["created_at"] else ""
        lines.append(
            f"| {i} | {ts} | `{item['source_type']}` | `{item['event_type']}` "
            f"| {item['globe_id']} | {item['actor_name']} | {item['title']} |"
        )
    lines.append("")
    for phrase in TIMELINE_PHRASES:
        lines.append(f"> \"{phrase}\"")
    return "\n".join(lines)


def save_timeline() -> tuple[Path, Path]:
    """Save timeline as JSON + Markdown. Advisory only."""
    tl = build_timeline()
    _REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    _TIMELINE_JSON.write_text(
        json.dumps(tl, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _TIMELINE_MD.write_text(_build_markdown(tl), encoding="utf-8")
    return _TIMELINE_JSON, _TIMELINE_MD


def load_timeline() -> dict:
    """Load timeline from saved JSON, or build on-the-fly."""
    if _TIMELINE_JSON.exists():
        try:
            raw = json.loads(_TIMELINE_JSON.read_text(encoding="utf-8"))
            if isinstance(raw, dict) and "items" in raw:
                return raw
        except Exception:
            pass
    return build_timeline()


# ─── CLI print helpers ────────────────────────────────────────────────────────

def _fmt_ts(ts: str) -> str:
    if not ts:
        return "—"
    return ts[:16].replace("T", " ")


def _print_item(it: dict, idx: int) -> None:
    attn = " ⚠️" if it.get("needs_attention") else ""
    rs_note = ""
    if it.get("resolution_status"):
        icon = _RS_ICON.get(it["resolution_status"], "")
        rs_note = f" [{icon} {it['resolution_status']}]"
    conf_note = f" (conf: {it['confidence']})" if it.get("confidence") else ""
    bt_note = f" → {it['bridge_target']}" if it.get("bridge_target") else ""

    print(f"  [{idx:02d}] {_fmt_ts(it['created_at'])}  "
          f"{it['source_type']:20s}  {it['event_type']:30s}{attn}")
    print(f"        globe: {it['globe_id']}  directive: {it['directive_id']}")
    print(f"        title: {it['title']}{rs_note}{conf_note}{bt_note}")
    print(f"        actor: {it['actor_name']} ({it['actor_type']})")
    if it["content"]:
        print(f"        content: {it['content'][:100]}")
    print()


def print_timeline_summary(tl: dict, items: list[dict] | None = None, label: str = "") -> None:
    title = f"Contribution Timeline (Phase 32)"
    if label:
        title += f" — {label}"
    print(f"\n{title}")
    print("=" * 60)
    print(f"  generated_at:   {tl.get('generated_at', '')}")
    print(f"  total_items:    {tl.get('total_items', 0)}")
    print(f"  attention_items:{tl.get('attention_items', 0)}"
          "  [items with objection/unresolved/contested/high-conf link]")
    print()
    print("  Source types:")
    for st, cnt in sorted(tl.get("source_type_counts", {}).items()):
        print(f"    {st:25s}: {cnt}")
    print()
    print("  By Globe:")
    for gid, cnt in sorted(tl.get("by_globe", {}).items()):
        print(f"    {gid:15s}: {cnt} items")
    print()
    print("  By Directive:")
    for did, cnt in sorted(tl.get("by_directive", {}).items()):
        print(f"    {did:40s}: {cnt} items")
    print()
    for phrase in TIMELINE_PHRASES:
        print(f'  "{phrase}"')

    if items is not None:
        print()
        print(f"  {len(items)} item(s):")
        print()
        for i, it in enumerate(items, 1):
            _print_item(it, i)


# ─── CLI entry point ──────────────────────────────────────────────────────────

def main(argv: list[str]) -> None:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return

    cmd = argv[0]

    if cmd == "summary":
        tl = build_timeline()
        print_timeline_summary(tl)
        return

    if cmd == "save":
        tl = build_timeline()
        json_path, md_path = save_timeline()
        print_timeline_summary(tl)
        print(f"Saved: {json_path}")
        print(f"Saved: {md_path}")
        return

    if cmd == "show-globe":
        if len(argv) < 2:
            print("Usage: contribution_timeline.py show-globe <globe_id>",
                  file=sys.stderr)
            sys.exit(1)
        globe_id = argv[1]
        tl = load_timeline()
        filtered = [it for it in tl["items"] if it["globe_id"] == globe_id]
        print_timeline_summary(tl, filtered, f"globe={globe_id}")
        return

    if cmd == "show-directive":
        if len(argv) < 2:
            print("Usage: contribution_timeline.py show-directive <directive_id>",
                  file=sys.stderr)
            sys.exit(1)
        directive_id = argv[1]
        tl = load_timeline()
        filtered = [it for it in tl["items"] if it["directive_id"] == directive_id]
        print_timeline_summary(tl, filtered, f"directive={directive_id}")
        return

    if cmd == "show-type":
        if len(argv) < 2:
            print("Usage: contribution_timeline.py show-type "
                  "<execution_log|resolution_signal|reality_feedback|bridge_target_link>",
                  file=sys.stderr)
            sys.exit(1)
        src_type = argv[1]
        if src_type not in VALID_SOURCE_TYPES:
            print(f"Unknown source_type: {src_type}. Valid: {sorted(VALID_SOURCE_TYPES)}",
                  file=sys.stderr)
            sys.exit(1)
        tl = load_timeline()
        filtered = [it for it in tl["items"] if it["source_type"] == src_type]
        print_timeline_summary(tl, filtered, f"source_type={src_type}")
        return

    print(f"Unknown command: {cmd}", file=sys.stderr)
    print("Commands: summary | save | show-globe <id> | "
          "show-directive <id> | show-type <type>", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
