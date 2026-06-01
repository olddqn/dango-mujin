#!/usr/bin/env python3
"""
cross_directive_signal_aggregation.py — Cross-Directive Signal Aggregation (Phase 43)
Dan-Go × GITSEA — Globe Foundation Layer

Aggregates resolution_status / objection / rollback / attention signals across
Globe, Directive, and Member dimensions.

INVARIANTS:
- Signal aggregation is advisory display only.
- Signal aggregation is not proof of resolution.
- Signal aggregation does not assign responsibility.
- Signal aggregation creates no authority.
- Human review is required before any real-world action.
- authority: none

Data sources (read-only):
  globe/reports/resolution_timeline.json   (primary signal source)
  globe/reports/attention_dashboard.json   (supplement: high_confidence_link, needs_attention)
  globe/reports/member_directive_map.json  (flag cross-check)
  globe/logs/*.jsonl                       (ground truth for raw counts)

CLI:
  python3 globe/runtime/cross_directive_signal_aggregation.py summary
  python3 globe/runtime/cross_directive_signal_aggregation.py save
  python3 globe/runtime/cross_directive_signal_aggregation.py show-globe <globe_id>
  python3 globe/runtime/cross_directive_signal_aggregation.py show-member <member_id>
  python3 globe/runtime/cross_directive_signal_aggregation.py show-directive <directive_id>
  python3 globe/runtime/cross_directive_signal_aggregation.py show-status <status>
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

AGG_INVARIANTS: dict[str, object] = {
    "signal_aggregation_is_advisory_display_only": True,
    "signal_aggregation_is_not_proof_of_resolution": True,
    "signal_aggregation_does_not_assign_responsibility": True,
    "signal_aggregation_creates_no_authority": True,
    "human_review_is_required_before_any_real_world_action": True,
    "authority": "none",
}

AGG_PHRASES: list[str] = [
    "Signal aggregation is advisory display only.",
    "Signal aggregation is not proof of resolution.",
    "Signal aggregation does not assign responsibility.",
    "Signal aggregation creates no authority.",
    "Human review is required before any real-world action.",
]

# Event types included in signal aggregation
SIGNAL_EVENT_TYPES: set[str] = {
    "voluntary_resolution_signal",
    "objection",
    "rollback_request",
    "contested_signal",
}

# resolution_status → canonical aggregation status key
_RS_TO_STATUS: dict[str, str] = {
    "unresolved":         "unresolved",
    "partially_resolved": "partially_resolved",
    "paused":             "paused",
    "resolved":           "resolved",
    "contested":          "contested",
}


def normalize_member_id(name: str) -> str:
    if not name or name.lower() in ("unknown", "", "n/a"):
        return "member-unknown"
    s = name.lower().replace(" ", "-").replace("_", "-")
    s = re.sub(r"[^a-z0-9\-]", "", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return f"member-{s}" if s else "member-unknown"


# ─── Per-dimension accumulator ───────────────────────────────────────────────

class _Acc:
    """Signal accumulator for one aggregation dimension value."""

    def __init__(self, agg_id: str, dimension: str, value: str) -> None:
        self.agg_id = agg_id
        self.dimension = dimension      # "globe" | "directive" | "member" | "status"
        self.value = value
        self.total_signal_count = 0
        self.voluntary_resolution_signal_count = 0
        self.unresolved_count = 0
        self.contested_count = 0
        self.partially_resolved_count = 0
        self.resolved_count = 0
        self.paused_count = 0
        self.objection_count = 0
        self.rollback_request_count = 0
        self.latest_signal_at: str = ""
        self.latest_resolution_status: str = ""
        self._latest_rs_at: str = ""
        self.affected_globe_ids: set[str] = set()
        self.affected_directive_ids: set[str] = set()
        self.affected_member_ids: set[str] = set()
        self._seen: set[str] = set()    # (event_type, member_id, directive_id, created_at[:19])

    def _update_ts(self, ts: str) -> None:
        if ts and ts > self.latest_signal_at:
            self.latest_signal_at = ts

    def add(
        self,
        event_type: str,
        resolution_status: str,
        member_id: str,
        directive_id: str,
        globe_id: str,
        created_at: str,
    ) -> bool:
        """Add a signal event. Returns True if new (not deduped)."""
        key = f"{event_type}|{member_id}|{directive_id}|{created_at[:19]}"
        if key in self._seen:
            return False
        self._seen.add(key)

        self.total_signal_count += 1
        self._update_ts(created_at)

        if globe_id:
            self.affected_globe_ids.add(globe_id)
        if directive_id:
            self.affected_directive_ids.add(directive_id)
        if member_id:
            self.affected_member_ids.add(member_id)

        rs = resolution_status or ""
        if event_type == "voluntary_resolution_signal":
            self.voluntary_resolution_signal_count += 1
            canon = _RS_TO_STATUS.get(rs, "")
            if canon == "unresolved":
                self.unresolved_count += 1
            elif canon == "partially_resolved":
                self.partially_resolved_count += 1
            elif canon == "paused":
                self.paused_count += 1
            elif canon == "resolved":
                self.resolved_count += 1
            # Track latest VRS resolution status
            if created_at and created_at > self._latest_rs_at and rs:
                self._latest_rs_at = created_at
                self.latest_resolution_status = rs
        elif event_type == "objection":
            self.objection_count += 1
        elif event_type == "rollback_request":
            self.rollback_request_count += 1
        elif event_type == "contested_signal":
            self.contested_count += 1
            if created_at and created_at > self._latest_rs_at:
                self._latest_rs_at = created_at
                self.latest_resolution_status = "contested"
        return True

    def to_dict(self, extra: dict | None = None) -> dict:
        d: dict = {
            "agg_id": self.agg_id,
            "dimension": self.dimension,
            "dimension_value": self.value,
            "total_signal_count": self.total_signal_count,
            "voluntary_resolution_signal_count": self.voluntary_resolution_signal_count,
            "unresolved_count": self.unresolved_count,
            "contested_count": self.contested_count,
            "partially_resolved_count": self.partially_resolved_count,
            "resolved_count": self.resolved_count,
            "paused_count": self.paused_count,
            "objection_count": self.objection_count,
            "rollback_request_count": self.rollback_request_count,
            "latest_signal_at": self.latest_signal_at,
            "latest_resolution_status": self.latest_resolution_status,
            "affected_globe_ids": sorted(self.affected_globe_ids),
            "affected_directive_ids": sorted(self.affected_directive_ids),
            "affected_member_ids": sorted(self.affected_member_ids),
            "advisory_only": True,
            "not_proof_of_resolution": True,
            "does_not_assign_responsibility": True,
            "creates_no_authority": True,
        }
        if extra:
            d.update(extra)
        return d


# ─── Builder ────────────────────────────────────────────────────────────────

def _status_key(event_type: str, resolution_status: str) -> str:
    """Derive a status key for by_status aggregation."""
    rs = resolution_status or ""
    if rs and rs in _RS_TO_STATUS:
        return _RS_TO_STATUS[rs]
    # Use event_type as fallback key when rs is absent
    if event_type == "objection":
        return "objection"
    if event_type == "rollback_request":
        return "rollback_request"
    if event_type == "contested_signal":
        return "contested"
    return "unknown"


def build_aggregation() -> dict:
    """
    Build cross-directive signal aggregation from all data sources.

    Primary source: resolution_timeline.json (already deduped across logs)
    Supplement: attention_dashboard.json for needs_attention / high_confidence_link
    Cross-check: member_directive_map.json (flag-based)
    Ground truth: logs/*.jsonl (for dedup verification)
    """
    # Per-dimension accumulators
    globe_accs: dict[str, _Acc] = {}
    dir_accs: dict[str, _Acc] = {}
    member_accs: dict[str, _Acc] = {}
    status_accs: dict[str, _Acc] = {}

    # Global dedup: (event_type, member_id, directive_id, created_at[:19])
    _global_seen: set[str] = set()

    def _gacc(gid: str) -> _Acc:
        if gid not in globe_accs:
            globe_accs[gid] = _Acc(f"agg-globe-{gid}", "globe", gid)
        return globe_accs[gid]

    def _dacc(did: str) -> _Acc:
        if did not in dir_accs:
            dir_accs[did] = _Acc(f"agg-directive-{did}", "directive", did)
        return dir_accs[did]

    def _macc(mid: str) -> _Acc:
        if mid not in member_accs:
            member_accs[mid] = _Acc(f"agg-member-{mid}", "member", mid)
        return member_accs[mid]

    def _sacc(sk: str) -> _Acc:
        if sk not in status_accs:
            status_accs[sk] = _Acc(f"agg-status-{sk}", "status", sk)
        return status_accs[sk]

    def _ingest(
        event_type: str,
        resolution_status: str,
        member_id: str,
        directive_id: str,
        globe_id: str,
        created_at: str,
    ) -> None:
        gkey = f"{event_type}|{member_id}|{directive_id}|{created_at[:19]}"
        if gkey in _global_seen:
            return
        _global_seen.add(gkey)

        if globe_id:
            _gacc(globe_id).add(event_type, resolution_status, member_id, directive_id, globe_id, created_at)
        if directive_id:
            _dacc(directive_id).add(event_type, resolution_status, member_id, directive_id, globe_id, created_at)
        if member_id:
            _macc(member_id).add(event_type, resolution_status, member_id, directive_id, globe_id, created_at)
        sk = _status_key(event_type, resolution_status)
        _sacc(sk).add(event_type, resolution_status, member_id, directive_id, globe_id, created_at)

    # ── Source 1: resolution_timeline.json (primary) ──────────────────────
    rt_path = _REPORTS_DIR / "resolution_timeline.json"
    if rt_path.exists():
        try:
            rt_data = json.loads(rt_path.read_text(encoding="utf-8"))
        except Exception:
            rt_data = {}
        for item in rt_data.get("items", []):
            et = item.get("event_type", "")
            if et not in SIGNAL_EVENT_TYPES:
                continue
            _ingest(
                event_type=et,
                resolution_status=item.get("resolution_status", "") or "",
                member_id=item.get("member_id", "") or "",
                directive_id=item.get("directive_id", "") or "",
                globe_id=item.get("globe_id", "") or "",
                created_at=item.get("created_at", "") or "",
            )

    # ── Source 2: logs/*.jsonl (ground truth cross-check) ─────────────────
    # Only adds signals not already captured via resolution_timeline
    _LOG_SIG_ETS = {"voluntary_resolution_signal", "objection", "rollback_request"}
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
            if et not in _LOG_SIG_ETS:
                continue
            did = entry.get("directive_id", "") or ""
            gid = entry.get("globe_id", "") or ""
            actor_name = entry.get("actor_name", "") or ""
            mid = normalize_member_id(actor_name)
            rs = entry.get("resolution_status", "") or ""
            ts = entry.get("created_at", "") or ""
            _ingest(et, rs, mid, did, gid, ts)

    # ── Source 3: attention_dashboard.json (supplement) ───────────────────
    # Adds attention-type signals not in resolution_timeline
    _ATTN_SIGNAL_TYPES = {"contested_signal", "unresolved_signal", "partially_resolved_signal"}
    ad_path = _REPORTS_DIR / "attention_dashboard.json"
    if ad_path.exists():
        try:
            ad_data = json.loads(ad_path.read_text(encoding="utf-8"))
        except Exception:
            ad_data = {}
        for attn in ad_data.get("items", []):
            at = attn.get("attention_type", "")
            if at not in _ATTN_SIGNAL_TYPES:
                continue
            # Map attention_type to event_type
            et_map = {
                "contested_signal": "contested_signal",
                "unresolved_signal": "voluntary_resolution_signal",
                "partially_resolved_signal": "voluntary_resolution_signal",
            }
            rs_map = {
                "unresolved_signal": "unresolved",
                "partially_resolved_signal": "partially_resolved",
                "contested_signal": "contested",
            }
            et = et_map.get(at, at)
            rs = rs_map.get(at, "")
            mid = attn.get("member_id", "") or ""
            did = attn.get("directive_id", "") or ""
            gid = attn.get("globe_id", "") or ""
            ts = attn.get("created_at", "") or ""
            _ingest(et, rs, mid, did, gid, ts)

    # ── Source 4: member_directive_map.json (flag cross-check) ────────────
    # Adds any contested signals not captured from resolution_timeline or attention_dashboard
    mdm_path = _REPORTS_DIR / "member_directive_map.json"
    if mdm_path.exists():
        try:
            mdm_data = json.loads(mdm_path.read_text(encoding="utf-8"))
        except Exception:
            mdm_data = {}
        for entry in mdm_data.get("entries", []):
            did = entry.get("directive_id", "") or ""
            gid = entry.get("globe_id", "") or ""
            mid = entry.get("member_id", "") or ""
            ts = entry.get("latest_activity_at", "") or ""
            if entry.get("has_contested_signal"):
                _ingest("contested_signal", "contested", mid, did, gid, ts)

    # ── Build output ──────────────────────────────────────────────────────
    def _sort_accs(accs: dict[str, _Acc]) -> list[dict]:
        return sorted(
            [a.to_dict() for a in accs.values() if a.total_signal_count > 0],
            key=lambda x: (-x["total_signal_count"], x["dimension_value"]),
        )

    by_globe = _sort_accs(globe_accs)
    by_directive = _sort_accs(dir_accs)
    by_member = _sort_accs(member_accs)
    by_status = _sort_accs(status_accs)

    total = len(_global_seen)

    return {
        "aggregation_id": "cross-directive-signal-aggregation-001",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": "Phase 43",
        "total_signals": total,
        "total_globes": len(globe_accs),
        "total_directives": len(dir_accs),
        "total_members_with_signals": len(member_accs),
        "total_status_keys": len(status_accs),
        **AGG_INVARIANTS,
        "advisory_phrases": AGG_PHRASES,
        "by_globe": by_globe,
        "by_directive": by_directive,
        "by_member": by_member,
        "by_status": by_status,
    }


# ─── Output helpers ──────────────────────────────────────────────────────────

def _agg_record_md(rec: dict) -> str:
    lines = [
        f"### {rec['agg_id']}",
        f"- dimension: {rec['dimension']} = {rec['dimension_value']}",
        f"- total_signal_count: {rec['total_signal_count']}",
        f"- vrs: {rec['voluntary_resolution_signal_count']}  "
        f"unresolved: {rec['unresolved_count']}  "
        f"partially_resolved: {rec['partially_resolved_count']}  "
        f"contested: {rec['contested_count']}  "
        f"objection: {rec['objection_count']}  "
        f"rollback: {rec['rollback_request_count']}",
        f"- latest_resolution_status: {rec['latest_resolution_status'] or '—'}",
        f"- latest_signal_at: {rec['latest_signal_at'][:19] if rec['latest_signal_at'] else '—'}",
        f"- affected_directives: {', '.join(rec['affected_directive_ids']) or '—'}",
        f"- affected_members: {', '.join(rec['affected_member_ids']) or '—'}",
        f"- affected_globes: {', '.join(rec['affected_globe_ids']) or '—'}",
        "",
    ]
    return "\n".join(lines)


def _to_markdown(data: dict) -> str:
    lines = [
        "# Cross-Directive Signal Aggregation (Phase 43)",
        "",
        f"generated_at: {data.get('generated_at', '')}",
        f"total_signals: {data.get('total_signals', 0)}",
        f"total_globes: {data.get('total_globes', 0)}",
        f"total_directives: {data.get('total_directives', 0)}",
        f"total_members_with_signals: {data.get('total_members_with_signals', 0)}",
        "",
        "## Invariants",
        "",
    ]
    for phrase in data.get("advisory_phrases", []):
        lines.append(f'- "{phrase}"')
    lines.append("")

    for section_key, section_label in [
        ("by_globe", "By Globe"),
        ("by_directive", "By Directive"),
        ("by_member", "By Member"),
        ("by_status", "By Status"),
    ]:
        lines.append(f"## {section_label}")
        lines.append("")
        for rec in data.get(section_key, []):
            lines.append(_agg_record_md(rec))

    return "\n".join(lines)


def save_aggregation(data: dict | None = None) -> None:
    if data is None:
        data = build_aggregation()
    json_path = _REPORTS_DIR / "cross_directive_signal_aggregation.json"
    md_path = _REPORTS_DIR / "cross_directive_signal_aggregation.md"
    json_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    md_path.write_text(_to_markdown(data), encoding="utf-8")
    print(f"  Saved: {json_path.relative_to(_GLOBE_DIR.parent)}")
    print(f"  Saved: {md_path.relative_to(_GLOBE_DIR.parent)}")


def load_aggregation() -> dict:
    json_path = _REPORTS_DIR / "cross_directive_signal_aggregation.json"
    if json_path.exists():
        try:
            return json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return build_aggregation()


def filter_records(
    data: dict,
    globe_filter: str | None = None,
    directive_filter: str | None = None,
    member_filter: str | None = None,
    status_filter: str | None = None,
) -> dict[str, list[dict]]:
    """Return filtered views across all dimensions."""
    def _match(rec: dict) -> bool:
        if globe_filter and globe_filter not in rec.get("affected_globe_ids", []):
            return False
        if directive_filter and directive_filter not in rec.get("affected_directive_ids", []):
            return False
        if member_filter and member_filter not in rec.get("affected_member_ids", []):
            return False
        if status_filter:
            sk = _status_key("voluntary_resolution_signal", status_filter)
            if status_filter not in (
                rec.get("latest_resolution_status", ""),
                rec.get("dimension_value", ""),
                sk,
            ):
                if not (status_filter == rec.get("dimension_value", "")):
                    return False
        return True

    # When filtering by a specific dimension value, show all OTHER dimensions
    out: dict[str, list[dict]] = {}
    for key in ("by_globe", "by_directive", "by_member", "by_status"):
        records = data.get(key, [])
        # For the matching dimension, filter by value directly
        if globe_filter and key == "by_globe":
            out[key] = [r for r in records if r["dimension_value"] == globe_filter]
        elif directive_filter and key == "by_directive":
            out[key] = [r for r in records if r["dimension_value"] == directive_filter]
        elif member_filter and key == "by_member":
            out[key] = [r for r in records if r["dimension_value"] == member_filter]
        elif status_filter and key == "by_status":
            out[key] = [r for r in records if r["dimension_value"] == status_filter]
        else:
            # Cross-filter: keep records that touch the filtered dimension
            out[key] = [r for r in records if _match(r)]
    return out


# ─── CLI ────────────────────────────────────────────────────────────────────

def cmd_summary(data: dict) -> None:
    print("Cross-Directive Signal Aggregation (Phase 43)")
    print("=" * 60)
    print(f"  generated_at:              {data.get('generated_at', '')[:19]}")
    print(f"  total_signals:             {data.get('total_signals', 0)}")
    print(f"  total_globes:              {data.get('total_globes', 0)}")
    print(f"  total_directives:          {data.get('total_directives', 0)}")
    print(f"  total_members_with_signals:{data.get('total_members_with_signals', 0)}")
    print()
    print("  By globe:")
    for r in data.get("by_globe", []):
        s = r.get("latest_resolution_status") or "—"
        print(f"    {r['dimension_value']:<40} total={r['total_signal_count']} lrs={s}")
    print()
    print("  By directive:")
    for r in data.get("by_directive", []):
        s = r.get("latest_resolution_status") or "—"
        print(f"    {r['dimension_value']:<40} total={r['total_signal_count']} lrs={s}")
    print()
    print("  By member:")
    for r in data.get("by_member", []):
        s = r.get("latest_resolution_status") or "—"
        dids = ",".join(r.get("affected_directive_ids", []))
        print(f"    {r['dimension_value']:<40} total={r['total_signal_count']} lrs={s} dirs=[{dids}]")
    print()
    print("  By status:")
    for r in data.get("by_status", []):
        print(f"    {r['dimension_value']:<20} total={r['total_signal_count']}")
    print()
    for phrase in AGG_PHRASES:
        print(f'  "{phrase}"')


def _print_section(section_label: str, records: list[dict]) -> None:
    print(f"  {section_label} ({len(records)} record(s)):")
    if not records:
        print("    (none)")
        return
    for r in records:
        s = r.get("latest_resolution_status") or "—"
        dids = ",".join(r.get("affected_directive_ids", []))
        mids = ",".join(r.get("affected_member_ids", []))
        gids = ",".join(r.get("affected_globe_ids", []))
        print(f"    [{r['dimension']}] {r['dimension_value']}")
        print(f"      total={r['total_signal_count']} lrs={s} vrs={r['voluntary_resolution_signal_count']}"
              f" obj={r['objection_count']} cont={r['contested_count']}"
              f" unres={r['unresolved_count']} partial={r['partially_resolved_count']}")
        if dids:
            print(f"      directives: {dids}")
        if mids:
            print(f"      members: {mids}")
        if gids:
            print(f"      globes: {gids}")
        lat = r.get("latest_signal_at", "")
        if lat:
            print(f"      latest_signal_at: {lat[:19]}")
    print()


def _print_filtered(data: dict, label: str,
                    globe_filter=None, directive_filter=None,
                    member_filter=None, status_filter=None) -> None:
    views = filter_records(data, globe_filter, directive_filter, member_filter, status_filter)
    print(f"Signal Aggregation — {label}")
    print("=" * 60)
    _print_section("by_globe", views.get("by_globe", []))
    _print_section("by_directive", views.get("by_directive", []))
    _print_section("by_member", views.get("by_member", []))
    _print_section("by_status", views.get("by_status", []))
    for phrase in AGG_PHRASES:
        print(f'  "{phrase}"')


def main(argv: list[str] | None = None) -> None:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("Usage: cross_directive_signal_aggregation.py "
              "<summary|save|show-globe|show-member|show-directive|show-status> [arg]")
        sys.exit(1)

    cmd = args[0]
    data = build_aggregation()

    if cmd == "summary":
        cmd_summary(data)

    elif cmd == "save":
        print("Saving Cross-Directive Signal Aggregation (Phase 43)...")
        save_aggregation(data)
        print(f"  total_signals: {data['total_signals']}")
        print()
        for phrase in AGG_PHRASES:
            print(f'  "{phrase}"')

    elif cmd == "show-globe":
        gid = args[1] if len(args) > 1 else ""
        _print_filtered(data, f"globe={gid}", globe_filter=gid)

    elif cmd == "show-member":
        mid = args[1] if len(args) > 1 else ""
        _print_filtered(data, f"member={mid}", member_filter=mid)

    elif cmd == "show-directive":
        did = args[1] if len(args) > 1 else ""
        _print_filtered(data, f"directive={did}", directive_filter=did)

    elif cmd == "show-status":
        st = args[1] if len(args) > 1 else ""
        _print_filtered(data, f"status={st}", status_filter=st)

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
