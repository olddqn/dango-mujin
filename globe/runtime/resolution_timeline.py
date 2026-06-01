#!/usr/bin/env python3
"""
resolution_timeline.py — Globe Directive Resolution Timeline (Phase 42)
Dan-Go × GITSEA — Globe Foundation Layer

Collects voluntary_resolution_signal, objection, rollback_request, and
attention-flagged items per directive and renders them as an ordered timeline.

INVARIANTS:
- Resolution timeline is advisory display only.
- Resolution timeline is not proof of resolution.
- Resolution timeline does not close support.
- Resolution timeline creates no authority.
- Human review is required before any real-world action.
- authority: none

Data sources (read-only):
  globe/logs/*.jsonl
  globe/reports/attention_dashboard.json
  globe/reports/contribution_timeline.json
  globe/reports/member_directive_map.json

CLI:
  python3 globe/runtime/resolution_timeline.py summary
  python3 globe/runtime/resolution_timeline.py save
  python3 globe/runtime/resolution_timeline.py show-directive <directive_id>
  python3 globe/runtime/resolution_timeline.py show-globe <globe_id>
  python3 globe/runtime/resolution_timeline.py show-status unresolved|contested|partially_resolved|resolved|paused
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ─── Paths ──────────────────────────────────────────────────────────────────

_HERE = Path(__file__).parent
_GLOBE_DIR = _HERE.parent
_LOGS_DIR = _GLOBE_DIR / "logs"
_REPORTS_DIR = _GLOBE_DIR / "reports"

# ─── Invariants ─────────────────────────────────────────────────────────────

TIMELINE_INVARIANTS: dict[str, object] = {
    "resolution_timeline_is_advisory_display_only": True,
    "resolution_timeline_is_not_proof_of_resolution": True,
    "resolution_timeline_does_not_close_support": True,
    "resolution_timeline_creates_no_authority": True,
    "human_review_is_required_before_any_real_world_action": True,
    "authority": "none",
}

TIMELINE_PHRASES: list[str] = [
    "Resolution timeline is advisory display only.",
    "Resolution timeline is not proof of resolution.",
    "Resolution timeline does not close support.",
    "Resolution timeline creates no authority.",
    "Human review is required before any real-world action.",
]

# Event types that appear in the resolution timeline
RESOLUTION_EVENT_TYPES: list[str] = [
    "voluntary_resolution_signal",
    "objection",
    "rollback_request",
    "contested_signal",
    "unresolved_signal",
    "partially_resolved_signal",
]

# Log entry_types that map directly to resolution timeline event_types
_LOG_ET_RESOLUTION: set[str] = {
    "voluntary_resolution_signal",
    "objection",
    "rollback_request",
}

# Attention types that add derived timeline entries (not directly in logs)
_ATTN_DERIVED: set[str] = {
    "contested_signal",
}

# Attention types whose source event is already captured from logs
_ATTN_LOG_COVERED: set[str] = {
    "unresolved_signal",
    "partially_resolved_signal",
    "objection",
    "rollback_request",
}


def normalize_member_id(name: str) -> str:
    """Spaces AND underscores → hyphens."""
    if not name or name.lower() in ("unknown", "", "n/a"):
        return "member-unknown"
    s = name.lower().replace(" ", "-").replace("_", "-")
    s = re.sub(r"[^a-z0-9\-]", "", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return f"member-{s}" if s else "member-unknown"


# ─── Directive aggregator ────────────────────────────────────────────────────

class _DirectiveAcc:
    """Per-directive resolution timeline aggregator."""

    def __init__(self, directive_id: str, globe_id: str) -> None:
        self.directive_id = directive_id
        self.globe_id = globe_id
        self.resolution_signal_count = 0
        self.unresolved_count = 0
        self.contested_count = 0
        self.partially_resolved_count = 0
        self.objection_count = 0
        self.rollback_request_count = 0
        self.latest_resolution_status: str = ""
        self.latest_event_at: str = ""
        # track latest VRS timestamp to set latest_resolution_status
        self._latest_vrs_at: str = ""
        self._latest_vrs_status: str = ""

    def _update_latest(self, ts: str) -> None:
        if ts and ts > self.latest_event_at:
            self.latest_event_at = ts

    def count(self, event_type: str, resolution_status: str, created_at: str) -> None:
        self._update_latest(created_at)
        if event_type == "voluntary_resolution_signal":
            self.resolution_signal_count += 1
            rs = resolution_status or ""
            if rs == "unresolved":
                self.unresolved_count += 1
            elif rs in ("partially_resolved", "paused"):
                self.partially_resolved_count += 1
            # Track latest VRS for status
            if created_at and created_at > self._latest_vrs_at:
                self._latest_vrs_at = created_at
                self._latest_vrs_status = rs
        elif event_type == "objection":
            self.objection_count += 1
        elif event_type == "rollback_request":
            self.rollback_request_count += 1
        elif event_type == "contested_signal":
            self.contested_count += 1

    def finalize(self) -> None:
        if self._latest_vrs_status:
            self.latest_resolution_status = self._latest_vrs_status
        elif self.contested_count:
            self.latest_resolution_status = "contested"
        elif self.objection_count:
            self.latest_resolution_status = "objection_pending"
        else:
            self.latest_resolution_status = ""


# ─── Builder ────────────────────────────────────────────────────────────────

def _make(
    timeline_id: str,
    directive_id: str,
    globe_id: str,
    member_id: str,
    actor_name: str,
    source_type: str,
    source_id: str,
    event_type: str,
    resolution_status: str,
    content_excerpt: str,
    created_at: str,
) -> dict:
    return {
        "timeline_id": timeline_id,
        "directive_id": directive_id,
        "globe_id": globe_id,
        "member_id": member_id,
        "actor_name": actor_name,
        "source_type": source_type,
        "source_id": source_id,
        "event_type": event_type,
        "resolution_status": resolution_status,
        "content_excerpt": content_excerpt[:200] if content_excerpt else "",
        "created_at": created_at,
        "advisory_only": True,
        "not_proof_of_resolution": True,
        "does_not_close_support": True,
        "creates_no_authority": True,
    }


def build_timeline() -> dict:
    """
    Build resolution timeline from all data sources.
    Primary: logs/*.jsonl → VRS, objection, rollback_request
    Supplement: attention_dashboard.json → contested_signal (derived)
    Cross-check: contribution_timeline.json (dedup by created_at)
    Reference: member_directive_map.json (for has_contested_signal cross-check)
    """
    items: list[dict] = []
    # Dedup key: (directive_id, event_type, created_at[:19]) — avoids counting
    # reality_feedback bridge copies of the same underlying log event
    _seen: set[str] = set()
    dir_accs: dict[str, _DirectiveAcc] = {}

    def _acc(did: str, gid: str) -> _DirectiveAcc:
        if did not in dir_accs:
            dir_accs[did] = _DirectiveAcc(did, gid)
        return dir_accs[did]

    # ── Source 1: logs/*.jsonl ─────────────────────────────────────────────
    for log_path in sorted(_LOGS_DIR.glob("*.jsonl")):
        for line in log_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            et = entry.get("entry_type", "")
            if et not in _LOG_ET_RESOLUTION:
                continue
            did = entry.get("directive_id", "")
            gid = entry.get("globe_id", "")
            log_id = entry.get("log_id", "")
            actor_name = entry.get("actor_name", "") or ""
            mid = normalize_member_id(actor_name)
            rs = entry.get("resolution_status", "") or ""
            content = entry.get("content", "") or ""
            ts = entry.get("created_at", "") or ""
            ts_short = ts[:19]

            dedup_key = f"{did}|{et}|{ts_short}"
            if dedup_key in _seen:
                continue
            _seen.add(dedup_key)

            tid = f"tl-rt-{log_id}-{did.replace('directive-claim-proposal-', '')}"
            items.append(_make(
                timeline_id=tid,
                directive_id=did,
                globe_id=gid,
                member_id=mid,
                actor_name=actor_name,
                source_type="execution_log",
                source_id=log_id,
                event_type=et,
                resolution_status=rs,
                content_excerpt=content,
                created_at=ts,
            ))
            _acc(did, gid).count(et, rs, ts)

    # ── Source 2: attention_dashboard.json — contested_signal (derived) ───
    attn_path = _REPORTS_DIR / "attention_dashboard.json"
    if attn_path.exists():
        try:
            attn_data = json.loads(attn_path.read_text(encoding="utf-8"))
        except Exception:
            attn_data = {}
        for attn in attn_data.get("items", []):
            at = attn.get("attention_type", "")
            if at not in _ATTN_DERIVED:
                continue
            did = attn.get("directive_id", "") or ""
            gid = attn.get("globe_id", "") or ""
            mid = attn.get("member_id", "") or ""
            actor_name = mid.removeprefix("member-") if mid else ""
            attn_id = attn.get("attention_id", "")
            excerpt = attn.get("content_excerpt", "") or ""
            ts = attn.get("created_at", "") or ""
            ts_short = ts[:19]

            dedup_key = f"{did}|{at}|{ts_short}"
            if dedup_key in _seen:
                continue
            _seen.add(dedup_key)

            tid = f"tl-rt-{attn_id}"
            items.append(_make(
                timeline_id=tid,
                directive_id=did,
                globe_id=gid,
                member_id=mid,
                actor_name=actor_name,
                source_type="attention_dashboard",
                source_id=attn_id,
                event_type=at,
                resolution_status="contested",
                content_excerpt=excerpt,
                created_at=ts,
            ))
            _acc(did, gid).count(at, "contested", ts)

    # ── Source 3: contribution_timeline.json — supplementary only ─────────
    # Only add items not already captured from logs (different source_type,
    # different created_at timestamp, or event_type not in _LOG_ET_RESOLUTION).
    ct_path = _REPORTS_DIR / "contribution_timeline.json"
    if ct_path.exists():
        try:
            ct_data = json.loads(ct_path.read_text(encoding="utf-8"))
        except Exception:
            ct_data = {}
        for ct in ct_data.get("items", []):
            et = ct.get("event_type", "")
            if et not in _LOG_ET_RESOLUTION:
                continue
            st = ct.get("source_type", "")
            # Skip execution_log and resolution_signal — already covered by logs/*.jsonl
            if st in ("execution_log", "resolution_signal"):
                continue
            did = ct.get("directive_id", "") or ""
            gid = ct.get("globe_id", "") or ""
            actor_name = ct.get("actor_name", "") or ""
            mid = normalize_member_id(actor_name)
            rs = ct.get("resolution_status", "") or ""
            content = ct.get("content", "") or ""
            ts = ct.get("created_at", "") or ""
            ts_short = ts[:19]

            dedup_key = f"{did}|{et}|{ts_short}"
            if dedup_key in _seen:
                continue
            _seen.add(dedup_key)

            src_id = ct.get("source_id", "")
            tid = f"tl-rt-{src_id}-{did.replace('directive-claim-proposal-', '')}"
            items.append(_make(
                timeline_id=tid,
                directive_id=did,
                globe_id=gid,
                member_id=mid,
                actor_name=actor_name,
                source_type=st,
                source_id=src_id,
                event_type=et,
                resolution_status=rs,
                content_excerpt=content,
                created_at=ts,
            ))
            _acc(did, gid).count(et, rs, ts)

    # ── Source 4: member_directive_map.json — has_contested_signal cross-check
    # Only adds contested entries if not already captured from attention_dashboard
    mdm_path = _REPORTS_DIR / "member_directive_map.json"
    if mdm_path.exists():
        try:
            mdm_data = json.loads(mdm_path.read_text(encoding="utf-8"))
        except Exception:
            mdm_data = {}
        for entry in mdm_data.get("entries", []):
            if not entry.get("has_contested_signal"):
                continue
            did = entry.get("directive_id", "") or ""
            gid = entry.get("globe_id", "") or ""
            mid = entry.get("member_id", "") or ""
            actor_name = entry.get("display_name", "") or mid.removeprefix("member-")
            ts = entry.get("latest_activity_at", "") or ""
            ts_short = ts[:19]

            dedup_key = f"{did}|contested_signal|{ts_short}"
            if dedup_key in _seen:
                continue
            _seen.add(dedup_key)

            map_id = entry.get("map_id", "")
            tid = f"tl-rt-mdm-{map_id}"
            items.append(_make(
                timeline_id=tid,
                directive_id=did,
                globe_id=gid,
                member_id=mid,
                actor_name=actor_name,
                source_type="member_directive_map",
                source_id=map_id,
                event_type="contested_signal",
                resolution_status="contested",
                content_excerpt=f"Contested signal for {actor_name} in {did} (from member_directive_map)",
                created_at=ts,
            ))
            _acc(did, gid).count("contested_signal", "contested", ts)

    # ── Finalize directive aggregations ───────────────────────────────────
    for acc in dir_accs.values():
        acc.finalize()

    # ── Sort items: by directive, then chronological ───────────────────────
    items.sort(key=lambda x: (x["directive_id"], x["created_at"]))

    # ── Build directive summaries ─────────────────────────────────────────
    directives: list[dict] = []
    for acc in sorted(dir_accs.values(), key=lambda a: a.directive_id):
        directives.append({
            "directive_id": acc.directive_id,
            "globe_id": acc.globe_id,
            "latest_resolution_status": acc.latest_resolution_status,
            "resolution_signal_count": acc.resolution_signal_count,
            "unresolved_count": acc.unresolved_count,
            "contested_count": acc.contested_count,
            "partially_resolved_count": acc.partially_resolved_count,
            "objection_count": acc.objection_count,
            "rollback_request_count": acc.rollback_request_count,
            "latest_event_at": acc.latest_event_at,
        })

    return {
        "timeline_id": "resolution-timeline-001",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": "Phase 42",
        "total_items": len(items),
        "total_directives": len(directives),
        **TIMELINE_INVARIANTS,
        "advisory_phrases": TIMELINE_PHRASES,
        "items": items,
        "by_directive": directives,
    }


# ─── Output helpers ──────────────────────────────────────────────────────────

def _to_markdown(data: dict) -> str:
    lines: list[str] = [
        "# Globe Resolution Timeline (Phase 42)",
        "",
        f"generated_at: {data.get('generated_at', '')}",
        f"total_items: {data.get('total_items', 0)}",
        f"total_directives: {data.get('total_directives', 0)}",
        "",
        "## Invariants",
        "",
    ]
    for phrase in data.get("advisory_phrases", []):
        lines.append(f'- "{phrase}"')
    lines.append("")
    lines.append("## By Directive")
    lines.append("")
    for d in data.get("by_directive", []):
        lines.append(f"### {d['directive_id']}")
        lines.append(f"- globe: {d['globe_id']}")
        lines.append(f"- latest_resolution_status: {d['latest_resolution_status']}")
        lines.append(f"- resolution_signal_count: {d['resolution_signal_count']}")
        lines.append(f"- unresolved_count: {d['unresolved_count']}")
        lines.append(f"- contested_count: {d['contested_count']}")
        lines.append(f"- partially_resolved_count: {d['partially_resolved_count']}")
        lines.append(f"- objection_count: {d['objection_count']}")
        lines.append(f"- rollback_request_count: {d['rollback_request_count']}")
        lines.append(f"- latest_event_at: {d['latest_event_at']}")
        lines.append("")
    lines.append("## Timeline Items")
    lines.append("")
    for item in data.get("items", []):
        lines.append(f"### {item['timeline_id']}")
        lines.append(f"- directive: {item['directive_id']} (globe: {item['globe_id']})")
        lines.append(f"- member: {item['member_id']} ({item['actor_name']})")
        lines.append(f"- event_type: {item['event_type']}")
        lines.append(f"- resolution_status: {item['resolution_status']}")
        lines.append(f"- source: {item['source_type']} / {item['source_id']}")
        lines.append(f"- created_at: {item['created_at']}")
        if item.get("content_excerpt"):
            lines.append(f"- excerpt: {item['content_excerpt'][:100]}")
        lines.append("")
    return "\n".join(lines)


def save_timeline(data: dict | None = None) -> None:
    if data is None:
        data = build_timeline()
    json_path = _REPORTS_DIR / "resolution_timeline.json"
    md_path = _REPORTS_DIR / "resolution_timeline.md"
    json_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    md_path.write_text(_to_markdown(data), encoding="utf-8")
    print(f"  Saved: {json_path.relative_to(_GLOBE_DIR.parent)}")
    print(f"  Saved: {md_path.relative_to(_GLOBE_DIR.parent)}")


def load_timeline() -> dict:
    """Load from JSON if available, otherwise build on-the-fly."""
    json_path = _REPORTS_DIR / "resolution_timeline.json"
    if json_path.exists():
        try:
            return json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return build_timeline()


def filter_items(
    data: dict,
    directive_filter: str | None = None,
    globe_filter: str | None = None,
    status_filter: str | None = None,
) -> list[dict]:
    items = data.get("items", [])
    if directive_filter:
        items = [i for i in items if i.get("directive_id") == directive_filter]
    if globe_filter:
        items = [i for i in items if i.get("globe_id") == globe_filter]
    if status_filter:
        items = [
            i for i in items
            if (i.get("resolution_status") == status_filter
                or i.get("event_type") == status_filter
                or (status_filter == "contested" and i.get("event_type") == "contested_signal"))
        ]
    return items


# ─── CLI ────────────────────────────────────────────────────────────────────

def cmd_summary(data: dict) -> None:
    print("Globe Resolution Timeline (Phase 42)")
    print("=" * 60)
    print(f"  generated_at:      {data.get('generated_at', '')[:19]}")
    print(f"  total_items:       {data.get('total_items', 0)}")
    print(f"  total_directives:  {data.get('total_directives', 0)}")
    print()
    by_et: dict[str, int] = {}
    by_rs: dict[str, int] = {}
    for item in data.get("items", []):
        et = item.get("event_type", "?")
        by_et[et] = by_et.get(et, 0) + 1
        rs = item.get("resolution_status", "") or "—"
        by_rs[rs] = by_rs.get(rs, 0) + 1
    print("  By event_type:")
    for et, n in sorted(by_et.items(), key=lambda x: -x[1]):
        print(f"    {et:<35}: {n}")
    print()
    print("  By resolution_status:")
    for rs, n in sorted(by_rs.items(), key=lambda x: -x[1]):
        print(f"    {rs:<35}: {n}")
    print()
    print("  By directive:")
    for d in data.get("by_directive", []):
        s = d.get("latest_resolution_status", "—") or "—"
        print(f"    {d['directive_id']} → {s} "
              f"(vrs:{d['resolution_signal_count']} obj:{d['objection_count']} "
              f"contested:{d['contested_count']})")
    print()
    for phrase in TIMELINE_PHRASES:
        print(f'  "{phrase}"')


def _print_items(items: list[dict], label: str) -> None:
    print(f"Resolution Timeline — {label}")
    print("=" * 60)
    print(f"  {len(items)} item(s)")
    print()
    for item in items:
        et = item.get("event_type", "")
        rs = item.get("resolution_status", "") or ""
        tid = item.get("timeline_id", "")
        did = item.get("directive_id", "")
        gid = item.get("globe_id", "")
        mid = item.get("member_id", "")
        ts = item.get("created_at", "")[:19]
        excerpt = (item.get("content_excerpt") or "")[:80]
        print(f"  [{et}] {tid}")
        print(f"     directive: {did}  globe: {gid}")
        print(f"     member: {mid}")
        print(f"     resolution_status: {rs or '—'}")
        print(f"     created: {ts}")
        if excerpt:
            print(f"     excerpt: {excerpt}")
        print()
    for phrase in TIMELINE_PHRASES:
        print(f'  "{phrase}"')


def main(argv: list[str] | None = None) -> None:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("Usage: resolution_timeline.py <summary|save|show-directive|show-globe|show-status> [arg]")
        sys.exit(1)

    cmd = args[0]
    data = build_timeline()

    if cmd == "summary":
        cmd_summary(data)

    elif cmd == "save":
        print("Saving Globe Resolution Timeline (Phase 42)...")
        save_timeline(data)
        print(f"  total_items: {data['total_items']}")
        print()
        for phrase in TIMELINE_PHRASES:
            print(f'  "{phrase}"')

    elif cmd == "show-directive":
        did = args[1] if len(args) > 1 else ""
        _print_items(filter_items(data, directive_filter=did), f"directive={did}")

    elif cmd == "show-globe":
        gid = args[1] if len(args) > 1 else ""
        _print_items(filter_items(data, globe_filter=gid), f"globe={gid}")

    elif cmd == "show-status":
        st = args[1] if len(args) > 1 else ""
        _print_items(filter_items(data, status_filter=st), f"status={st}")

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
