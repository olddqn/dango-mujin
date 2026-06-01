#!/usr/bin/env python3
"""
attention_dashboard.py — Globe Attention-Required Dashboard (Phase 41)
Dan-Go × GITSEA — Globe Foundation Layer

Collects attention-required records across the protocol (objections,
unresolved signals, contested signals, high-confidence bridge links)
into an advisory dashboard. Advisory display only — not priority score,
creates no obligation, does not assign responsibility.

Sources:
    globe/logs/*.jsonl                       — objections, rollbacks, VRS
    globe/reports/bridge_target_links.json   — high confidence link candidates
    globe/reports/member_directive_map.json  — contested signals
    globe/reports/contribution_timeline.json — supplementary (needs_attention)
    globe/reports/activity_heatmap.json      — metadata context
    globe/reports/member_activity_heatmap.json — member-level context

CLI:
    python3 globe/runtime/attention_dashboard.py summary
    python3 globe/runtime/attention_dashboard.py save
    python3 globe/runtime/attention_dashboard.py show-globe globe-001
    python3 globe/runtime/attention_dashboard.py show-directive directive-claim-proposal-002
    python3 globe/runtime/attention_dashboard.py show-member member-masuo-komori
    python3 globe/runtime/attention_dashboard.py show-type objection
"""

import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# ─── Paths ──────────────────────────────────────────────────────────────────────

_GLOBE_DIR   = Path(__file__).resolve().parents[1]
_LOGS_DIR    = _GLOBE_DIR / "logs"
_REPORTS_DIR = _GLOBE_DIR / "reports"

_BTL_JSON     = _REPORTS_DIR / "bridge_target_links.json"
_MDM_JSON     = _REPORTS_DIR / "member_directive_map.json"
_TIMELINE_JSON = _REPORTS_DIR / "contribution_timeline.json"
_AH_JSON      = _REPORTS_DIR / "activity_heatmap.json"
_MAH_JSON     = _REPORTS_DIR / "member_activity_heatmap.json"
_OUTPUT_JSON  = _REPORTS_DIR / "attention_dashboard.json"
_OUTPUT_MD    = _REPORTS_DIR / "attention_dashboard.md"

# ─── Invariants ─────────────────────────────────────────────────────────────────

DASHBOARD_INVARIANTS: dict = {
    "attention_dashboard_is_advisory_display_only": True,
    "attention_item_is_not_priority_score": True,
    "attention_item_creates_no_obligation": True,
    "attention_item_does_not_assign_responsibility": True,
    "human_review_is_required_before_any_real_world_action": True,
    "authority": "none",
}

DASHBOARD_PHRASES: list[str] = [
    "Attention dashboard is advisory display only.",
    "Attention item is not priority score.",
    "Attention item creates no obligation.",
    "Attention item does not assign responsibility.",
    "Human review is required before any real-world action.",
]

# Canonical attention types (ordered for display)
ATTENTION_TYPES: list[str] = [
    "objection",
    "rollback_request",
    "unresolved_signal",
    "partially_resolved_signal",
    "contested_signal",
    "high_confidence_link",
    "needs_attention",
]

# Log entry_type → attention_type map (None means skip)
_LOG_ET_TO_ATTN: dict[str, str | None] = {
    "objection":                   "objection",
    "rollback_request":            "rollback_request",
    "voluntary_resolution_signal": None,   # handled separately by resolution_status
}

# ─── Helpers ────────────────────────────────────────────────────────────────────

def _parse_date(ts: str) -> str:
    if not ts:
        return ""
    m = re.match(r"(\d{4}-\d{2}-\d{2})", ts.strip())
    return m.group(1) if m else ""

def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

def normalize_member_id(name: str) -> str:
    """Normalize actor display name to member_id slug."""
    if not name or name.lower() in ("unknown", "", "n/a"):
        return "member-unknown"
    s = name.lower().replace(" ", "-").replace("_", "-")
    s = re.sub(r"[^a-z0-9\-]", "", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return f"member-{s}" if s else "member-unknown"

def _load_json(path: Path) -> dict | list:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}

# ─── Build ───────────────────────────────────────────────────────────────────────

def build_dashboard() -> dict:
    """Collect attention items from all sources."""

    items: list[dict] = []
    seen_ids: set[str] = set()

    def _add(item: dict) -> None:
        aid = item["attention_id"]
        if aid in seen_ids:
            return
        seen_ids.add(aid)
        items.append(item)

    def _make(
        attention_id:   str,
        source_type:    str,
        source_id:      str,
        globe_id:       str,
        directive_id:   str,
        member_id:      str,
        attention_type: str,
        title:          str,
        content_excerpt: str,
        reason:         str,
        created_at:     str,
        source_path:    str,
    ) -> dict:
        return {
            "attention_id":    attention_id,
            "source_type":     source_type,
            "source_id":       source_id,
            "globe_id":        globe_id,
            "directive_id":    directive_id,
            "member_id":       member_id,
            "attention_type":  attention_type,
            "title":           title,
            "content_excerpt": content_excerpt,
            "reason":          reason,
            "created_at":      created_at,
            "source_path":     source_path,
            "advisory_only":               True,
            "not_priority_score":          True,
            "creates_no_obligation":       True,
            "does_not_assign_responsibility": True,
        }

    # ── Source 1: logs/*.jsonl ───────────────────────────────────────────────
    # Track objections per directive for contested_signal computation
    directive_objectors: dict[str, set[str]] = defaultdict(set)
    vrs_entries: list[dict] = []   # collect VRS entries for later

    for logfile in sorted(_LOGS_DIR.glob("*.jsonl")):
        did       = logfile.stem
        rel_path  = str(logfile.relative_to(_GLOBE_DIR.parent))
        for raw_line in logfile.read_text(encoding="utf-8").splitlines():
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            try:
                entry = json.loads(raw_line)
            except json.JSONDecodeError:
                continue
            et       = entry.get("entry_type", "")
            log_id   = entry.get("log_id", "")
            actor    = entry.get("actor_name", "")
            gid      = entry.get("globe_id", "")
            ts       = entry.get("created_at", "")
            content  = entry.get("content", "")
            rs       = entry.get("resolution_status", "")
            mid      = normalize_member_id(actor)

            if et == "objection":
                directive_objectors[did].add(mid)
                _add(_make(
                    attention_id    = f"attn-objection-{did.split('-')[-1]}-{log_id}",
                    source_type     = "execution_log",
                    source_id       = log_id,
                    globe_id        = gid,
                    directive_id    = did,
                    member_id       = mid,
                    attention_type  = "objection",
                    title           = f"⚠️ Objection recorded — {actor}",
                    content_excerpt = content[:120],
                    reason          = "Objection by member — human review may be required before proceeding",
                    created_at      = ts,
                    source_path     = rel_path,
                ))

            elif et == "rollback_request":
                _add(_make(
                    attention_id    = f"attn-rollback-{did.split('-')[-1]}-{log_id}",
                    source_type     = "execution_log",
                    source_id       = log_id,
                    globe_id        = gid,
                    directive_id    = did,
                    member_id       = mid,
                    attention_type  = "rollback_request",
                    title           = f"↩️ Rollback request — {actor}",
                    content_excerpt = content[:120],
                    reason          = "Rollback requested — human review required before any state change",
                    created_at      = ts,
                    source_path     = rel_path,
                ))

            elif et == "voluntary_resolution_signal":
                # Determine attention_type based on resolution_status
                if rs == "unresolved":
                    attn_type = "unresolved_signal"
                    title     = f"🔴 Unresolved signal — {actor}"
                    reason    = ("Voluntary resolution signal marked unresolved — "
                                 "does not confirm resolution; human review may be needed")
                elif rs in ("partially_resolved", "paused"):
                    attn_type = "partially_resolved_signal"
                    title     = f"🟡 Partially-resolved signal — {actor} (status: {rs})"
                    reason    = ("Voluntary resolution signal not fully resolved — "
                                 "does not confirm resolution; human review may be needed")
                elif rs == "contested":
                    attn_type = "contested_signal"
                    title     = f"⚠️ Contested resolution signal — {actor}"
                    reason    = ("Resolution signal marked contested — "
                                 "disagreement exists; human review required")
                else:
                    # resolved or empty — skip as attention item
                    vrs_entries.append({
                        "did": did, "log_id": log_id, "mid": mid, "ts": ts,
                        "gid": gid, "content": content, "rs": rs, "rel_path": rel_path,
                    })
                    continue

                _add(_make(
                    attention_id    = f"attn-vrs-{did.split('-')[-1]}-{log_id}",
                    source_type     = "execution_log",
                    source_id       = log_id,
                    globe_id        = gid,
                    directive_id    = did,
                    member_id       = mid,
                    attention_type  = attn_type,
                    title           = title,
                    content_excerpt = content[:120],
                    reason          = reason,
                    created_at      = ts,
                    source_path     = rel_path,
                ))
                vrs_entries.append({
                    "did": did, "log_id": log_id, "mid": mid, "ts": ts,
                    "gid": gid, "content": content, "rs": rs, "rel_path": rel_path,
                })

    # ── Source 2: bridge_target_links.json — high confidence candidates ───────
    btl_raw = _load_json(_BTL_JSON)
    if isinstance(btl_raw, dict):
        btl_path = str(_BTL_JSON.relative_to(_GLOBE_DIR.parent))
        for c in btl_raw.get("candidates", []):
            if c.get("confidence") != "high":
                continue
            link_id = c.get("link_id", "")
            gid     = c.get("globe_id", "")
            did     = c.get("source_directive_id", "")
            ts      = c.get("created_at", "")
            desc    = c.get("candidate_description", "")
            target  = c.get("suggested_bridge_target", "")
            reason  = c.get("match_reason", "")
            _add(_make(
                attention_id    = f"attn-link-{link_id}",
                source_type     = "bridge_target_link",
                source_id       = link_id,
                globe_id        = gid,
                directive_id    = did,
                member_id       = "member-bridge-target-linker",
                attention_type  = "high_confidence_link",
                title           = f"🔗 High-confidence link candidate → {target}",
                content_excerpt = desc[:120],
                reason          = reason[:180] if reason else "High-confidence bridge link — human review required to confirm",
                created_at      = ts,
                source_path     = btl_path,
            ))

    # ── Source 3: member_directive_map.json — contested signals ──────────────
    mdm_raw = _load_json(_MDM_JSON)
    if isinstance(mdm_raw, dict):
        mdm_path = str(_MDM_JSON.relative_to(_GLOBE_DIR.parent))
        for e in mdm_raw.get("entries", []):
            if not e.get("has_contested_signal"):
                continue
            mid = e.get("member_id", "")
            did = e.get("directive_id", "")
            gid = e.get("globe_id", "")
            ts  = e.get("latest_activity_at", "")
            # Find the objectors in same directive (from our collected data)
            objectors = directive_objectors.get(did, set())
            other_obj = objectors - {mid}
            obj_str   = ", ".join(sorted(other_obj)) if other_obj else "another member"
            _add(_make(
                attention_id    = f"attn-contested-{mid.removeprefix('member-')[:12]}-{did.split('-')[-1]}",
                source_type     = "member_directive_map",
                source_id       = e.get("map_id", ""),
                globe_id        = gid,
                directive_id    = did,
                member_id       = mid,
                attention_type  = "contested_signal",
                title           = f"⚔️ Contested resolution signal — {mid}",
                content_excerpt = (f"VRS from {mid} is contested because "
                                   f"{obj_str} objected in the same directive"),
                reason          = ("A voluntary resolution signal and an objection coexist "
                                   "in the same directive — human review required to determine "
                                   "whether the signal reflects shared understanding"),
                created_at      = ts,
                source_path     = mdm_path,
            ))

    # ── Source 4: contribution_timeline.json — supplementary needs_attention ──
    # Ingest timeline items marked needs_attention=True that aren't already
    # captured from direct log/btl sources (deduplication by source_id).
    tl_raw = _load_json(_TIMELINE_JSON)
    if isinstance(tl_raw, dict):
        tl_path = str(_TIMELINE_JSON.relative_to(_GLOBE_DIR.parent))
        captured_source_ids = {i["source_id"] for i in items}
        for item in tl_raw.get("items", []):
            if not item.get("needs_attention"):
                continue
            src_id = item.get("source_id", "")
            if src_id in captured_source_ids:
                continue  # already captured from primary source
            # Only add if not already seen via attention_id
            tl_id   = item.get("timeline_id", "")
            et      = item.get("event_type", "")
            actor   = item.get("actor_name", "")
            gid     = item.get("globe_id", "")
            did     = item.get("directive_id", "")
            ts      = item.get("created_at", "")
            content = item.get("content", "")
            title   = item.get("title", et)
            mid     = normalize_member_id(actor) if actor else ""
            _add(_make(
                attention_id    = f"attn-tl-{tl_id}",
                source_type     = "contribution_timeline",
                source_id       = tl_id,
                globe_id        = gid,
                directive_id    = did,
                member_id       = mid,
                attention_type  = "needs_attention",
                title           = f"⚠️ {title}",
                content_excerpt = content[:120],
                reason          = "Flagged needs_attention=True in contribution timeline",
                created_at      = ts,
                source_path     = tl_path,
            ))

    # ── Source 5/6: activity_heatmap / member_activity_heatmap — metadata ─────
    # Used for summary metadata only; attention items already captured above.
    ah_raw  = _load_json(_AH_JSON)
    mah_raw = _load_json(_MAH_JSON)
    ah_attention_events  = ah_raw.get("attention_events", 0) if isinstance(ah_raw, dict) else 0
    mah_members_with_attn = sum(
        1 for m in (mah_raw.get("members", []) if isinstance(mah_raw, dict) else [])
        if m.get("objection_count") or m.get("unresolved_signal_count") or m.get("contested_signal_count")
    ) if isinstance(mah_raw, dict) else 0

    # ── Sort by created_at descending, then attention_type ───────────────────
    items.sort(key=lambda i: (i.get("created_at", ""), i["attention_type"]), reverse=True)

    # ── Index maps ───────────────────────────────────────────────────────────
    by_globe:     dict[str, list[str]] = defaultdict(list)
    by_directive: dict[str, list[str]] = defaultdict(list)
    by_member:    dict[str, list[str]] = defaultdict(list)
    by_type:      dict[str, list[str]] = defaultdict(list)

    for i in items:
        by_globe[i["globe_id"]].append(i["attention_id"])
        by_directive[i["directive_id"]].append(i["attention_id"])
        if i["member_id"]:
            by_member[i["member_id"]].append(i["attention_id"])
        by_type[i["attention_type"]].append(i["attention_id"])

    # Attention type count summary
    type_counts: dict[str, int] = {at: len(by_type.get(at, [])) for at in ATTENTION_TYPES}

    return {
        "dashboard_id":  "globe-attention-dashboard",
        "generated_at":  _now_iso(),
        "phase":         "41",
        "total_items":   len(items),
        "type_counts":   type_counts,
        "ah_attention_events":    ah_attention_events,
        "mah_members_with_attn":  mah_members_with_attn,
        "phase_phrases":  DASHBOARD_PHRASES,
        **DASHBOARD_INVARIANTS,
        "items":         items,
        "by_globe":      dict(by_globe),
        "by_directive":  dict(by_directive),
        "by_member":     dict(by_member),
        "by_type":       dict(by_type),
    }

# ─── Save helpers ────────────────────────────────────────────────────────────────

def save_dashboard(data: dict) -> None:
    _OUTPUT_JSON.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    _OUTPUT_MD.write_text(_to_markdown(data), encoding="utf-8")
    print(f"  Saved: {_OUTPUT_JSON.relative_to(_GLOBE_DIR.parent)}")
    print(f"  Saved: {_OUTPUT_MD.relative_to(_GLOBE_DIR.parent)}")


def _to_markdown(data: dict) -> str:
    lines: list[str] = [
        "# Globe Attention-Required Dashboard (Phase 41)",
        "",
        f"**Generated:** {data['generated_at']}",
        f"**Total attention items:** {data['total_items']}",
        "",
        "> Attention dashboard is advisory display only.",
        "> Attention item is not priority score.",
        "> Attention item creates no obligation.",
        "> Attention item does not assign responsibility.",
        "> Human review is required before any real-world action.",
        "",
        "---",
        "",
        "## Attention Type Counts",
        "",
    ]
    for at, cnt in data.get("type_counts", {}).items():
        if cnt:
            lines.append(f"- {at}: {cnt}")
    lines += ["", "---", "", "## Items", ""]

    for item in data.get("items", []):
        lines.append(f"### {item['attention_id']}")
        lines.append(f"**Type:** {item['attention_type']}")
        lines.append(f"**Title:** {item['title']}")
        lines.append(f"**Globe:** {item['globe_id']} · **Directive:** {item['directive_id']}")
        lines.append(f"**Member:** {item['member_id']}")
        lines.append(f"**Reason:** {item['reason']}")
        if item.get("content_excerpt"):
            lines.append(f"**Excerpt:** _{item['content_excerpt']}_")
        lines.append(f"**Created:** {item.get('created_at', '')[:19]}")
        lines.append("")
    return "\n".join(lines)

# ─── Load (server helper) ────────────────────────────────────────────────────────

def load_dashboard() -> dict:
    if _OUTPUT_JSON.exists():
        return json.loads(_OUTPUT_JSON.read_text(encoding="utf-8"))
    return build_dashboard()


def filter_items(data: dict, *, globe: str | None = None,
                 directive: str | None = None, member: str | None = None,
                 attn_type: str | None = None) -> list[dict]:
    items = data.get("items", [])
    if globe:
        items = [i for i in items if i["globe_id"] == globe]
    if directive:
        items = [i for i in items if i["directive_id"] == directive]
    if member:
        items = [i for i in items if i["member_id"] == member]
    if attn_type:
        items = [i for i in items if i["attention_type"] == attn_type]
    return items

# ─── CLI ────────────────────────────────────────────────────────────────────────

_ATTN_ICON: dict[str, str] = {
    "objection":                 "⚠️",
    "rollback_request":          "↩️",
    "unresolved_signal":         "🔴",
    "partially_resolved_signal": "🟡",
    "contested_signal":          "⚔️",
    "high_confidence_link":      "🔗",
    "needs_attention":           "🚨",
}


def _print_item(i: dict) -> None:
    icon = _ATTN_ICON.get(i["attention_type"], "•")
    print(f"  {icon} [{i['attention_type']}] {i['attention_id']}")
    print(f"     title:    {i['title']}")
    print(f"     globe:    {i['globe_id']}  directive: {i['directive_id']}")
    print(f"     member:   {i['member_id']}")
    print(f"     reason:   {i['reason'][:80]}")
    if i.get("content_excerpt"):
        print(f"     excerpt:  {i['content_excerpt'][:70]}")
    print(f"     created:  {(i.get('created_at') or '')[:19] or 'N/A'}")
    print()


def _print_phrases() -> None:
    print()
    for phrase in DASHBOARD_PHRASES:
        print(f'  "{phrase}"')


def cmd_summary() -> None:
    data = build_dashboard()
    print("Globe Attention-Required Dashboard (Phase 41)")
    print("=" * 60)
    print(f"  generated_at:   {data['generated_at']}")
    print(f"  total_items:    {data['total_items']}")
    print(f"  ah_attention_events:   {data['ah_attention_events']} (from activity_heatmap)")
    print(f"  mah_members_with_attn: {data['mah_members_with_attn']} members")
    print()
    print("  By attention type:")
    for at, cnt in data["type_counts"].items():
        if cnt:
            icon = _ATTN_ICON.get(at, "•")
            print(f"    {icon} {at:<30}: {cnt}")
    print()
    print("  By globe:")
    for gid, aids in data.get("by_globe", {}).items():
        print(f"    {gid}: {len(aids)} items")
    _print_phrases()


def cmd_save() -> None:
    data = build_dashboard()
    print("Saving Globe Attention Dashboard (Phase 41)...")
    save_dashboard(data)
    print(f"  total_items: {data['total_items']}")
    _print_phrases()


def _cmd_filter(label: str, items: list[dict]) -> None:
    print(f"Attention Dashboard — {label}")
    print("=" * 60)
    print(f"  {len(items)} item(s)")
    print()
    for i in items:
        _print_item(i)
    if not items:
        print(f"  No attention items for {label}")
    _print_phrases()


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] == "summary":
        cmd_summary()
    elif args[0] == "save":
        cmd_save()
    elif args[0] == "show-globe":
        if len(args) < 2:
            print("Usage: show-globe <globe_id>", file=sys.stderr); sys.exit(1)
        data = build_dashboard()
        _cmd_filter(f"globe={args[1]}", filter_items(data, globe=args[1]))
    elif args[0] == "show-directive":
        if len(args) < 2:
            print("Usage: show-directive <directive_id>", file=sys.stderr); sys.exit(1)
        data = build_dashboard()
        _cmd_filter(f"directive={args[1]}", filter_items(data, directive=args[1]))
    elif args[0] == "show-member":
        if len(args) < 2:
            print("Usage: show-member <member_id>", file=sys.stderr); sys.exit(1)
        data = build_dashboard()
        _cmd_filter(f"member={args[1]}", filter_items(data, member=args[1]))
    elif args[0] == "show-type":
        if len(args) < 2:
            print("Usage: show-type <attention_type>", file=sys.stderr); sys.exit(1)
        data = build_dashboard()
        _cmd_filter(f"type={args[1]}", filter_items(data, attn_type=args[1]))
    else:
        print(f"Unknown command: {args[0]!r}", file=sys.stderr)
        print("Commands: summary | save | show-globe | show-directive | show-member | show-type",
              file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
