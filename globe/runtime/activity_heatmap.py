"""activity_heatmap.py — Phase 34: Globe Activity Heatmap

Aggregates all Globe-layer events by date (YYYY-MM-DD) to produce a
calendar-style activity view. Heatmap reflects observed event counts only —
it is not a measurement of impact, performance, or priority.

INVARIANTS (permanent, not negotiable):
  Heatmap is advisory display only.
  Heatmap is not proof of impact.
  Heatmap does not rank participants.
  Heatmap does not allocate resources.
  Human review is required before any real-world action.
  authority: none

Data sources:
  primary  — globe/reports/contribution_timeline.json  (all 16 items)
  fallback — globe/logs/*.jsonl  (if timeline not available)

CLI:
  python3 globe/runtime/activity_heatmap.py summary
  python3 globe/runtime/activity_heatmap.py save
  python3 globe/runtime/activity_heatmap.py show-date <YYYY-MM-DD>
  python3 globe/runtime/activity_heatmap.py show-globe <globe_id>
  python3 globe/runtime/activity_heatmap.py show-directive <directive_id>
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────

_GLOBE_DIR   = Path(__file__).resolve().parents[1]
_REPORTS_DIR = _GLOBE_DIR / "reports"
_LOGS_DIR    = _GLOBE_DIR / "logs"

_TIMELINE_PATH = _REPORTS_DIR / "contribution_timeline.json"
_HEATMAP_JSON  = _REPORTS_DIR / "activity_heatmap.json"
_HEATMAP_MD    = _REPORTS_DIR / "activity_heatmap.md"

# ─── Invariants ───────────────────────────────────────────────────────────────

HEATMAP_INVARIANTS = {
    "heatmap_is_advisory_display_only": True,
    "heatmap_is_not_proof_of_impact": True,
    "heatmap_does_not_rank_participants": True,
    "heatmap_does_not_allocate_resources": True,
    "human_review_is_required_before_any_real_world_action": True,
    "authority": "none",
}

HEATMAP_PHRASES = [
    "Heatmap is advisory display only.",
    "Heatmap is not proof of impact.",
    "Heatmap does not rank participants.",
    "Heatmap does not allocate resources.",
    "Human review is required before any real-world action.",
]

# Event types that warrant observation (not priority — just flagged)
_ATTENTION_EVENT_TYPES = frozenset({
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
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except Exception:
                pass
    return entries


def _date(ts: str) -> str:
    """Extract YYYY-MM-DD from any ISO timestamp string."""
    return ts[:10] if ts else ""


# ─── Event loading ────────────────────────────────────────────────────────────

def _load_events() -> list[dict]:
    """Load all events for the heatmap.

    Primary source: contribution_timeline.json (already de-duplicated).
    Fallback: scan logs/*.jsonl directly.
    """
    tl = _load_json(_TIMELINE_PATH)
    if isinstance(tl, dict) and tl.get("items"):
        return tl["items"]

    # Fallback: build from logs only
    events: list[dict] = []
    for p in sorted(_LOGS_DIR.glob("*.jsonl")):
        for e in _load_jsonl(p):
            et = e.get("entry_type", "")
            rs = e.get("resolution_status", "")
            src = ("resolution_signal"
                   if et == "voluntary_resolution_signal"
                   else "execution_log")
            needs_attn = et in _ATTENTION_EVENT_TYPES or rs in _ATTENTION_RS
            events.append({
                "timeline_id":    f"fb-{e.get('log_id','')}",
                "globe_id":       e.get("globe_id", ""),
                "directive_id":   e.get("directive_id", ""),
                "source_type":    src,
                "event_type":     et,
                "resolution_status": rs,
                "needs_attention": needs_attn,
                "created_at":     e.get("created_at", ""),
            })
    return events


# ─── Aggregation ─────────────────────────────────────────────────────────────

def _empty_day() -> dict:
    return {
        "total_events":          0,
        "execution_log_count":   0,
        "resolution_signal_count": 0,
        "reality_feedback_count": 0,
        "bridge_target_link_count": 0,
        "objection_count":       0,
        "rollback_request_count": 0,
        "unresolved_count":      0,
        "contested_count":       0,
        "needs_attention_count": 0,
        "by_globe":     {},   # globe_id → count
        "by_directive": {},   # directive_id → count
        "event_type_counts": {},  # event_type → count
        "source_type_counts": {}, # source_type → count
        "items": [],          # raw item refs (timeline_id list)
    }


def _inc(d: dict, key: str, amount: int = 1) -> None:
    d[key] = d.get(key, 0) + amount


def build_heatmap() -> dict:
    """Build and return the full activity heatmap.

    Advisory only. Not proof of impact. No ranking. No allocation.
    Events are aggregated by date; counts reflect what was recorded.
    """
    events = _load_events()

    by_date: dict[str, dict] = {}

    for ev in events:
        date = _date(ev.get("created_at", ""))
        if not date:
            continue
        if date not in by_date:
            by_date[date] = _empty_day()
        day = by_date[date]

        st  = ev.get("source_type", "")
        et  = ev.get("event_type", "")
        rs  = ev.get("resolution_status", "")
        gid = ev.get("globe_id", "")
        did = ev.get("directive_id", "")
        attn = ev.get("needs_attention", False)
        tid  = ev.get("timeline_id", "")

        day["total_events"] += 1

        # Source type counts
        if st == "execution_log":
            day["execution_log_count"] += 1
        elif st == "resolution_signal":
            day["resolution_signal_count"] += 1
        elif st == "reality_feedback":
            day["reality_feedback_count"] += 1
        elif st == "bridge_target_link":
            day["bridge_target_link_count"] += 1
        _inc(day["source_type_counts"], st)

        # Event type counts
        _inc(day["event_type_counts"], et)

        # Attention counts
        if et == "objection":
            day["objection_count"] += 1
        if et == "rollback_request":
            day["rollback_request_count"] += 1
        if rs == "unresolved":
            day["unresolved_count"] += 1
        if rs == "contested":
            day["contested_count"] += 1
        if attn:
            day["needs_attention_count"] += 1

        # By globe / directive
        if gid:
            _inc(day["by_globe"], gid)
        if did:
            _inc(day["by_directive"], did)

        if tid:
            day["items"].append(tid)

    # Global totals
    total_events = sum(d["total_events"] for d in by_date.values())
    total_attention = sum(d["needs_attention_count"] for d in by_date.values())
    all_dates = sorted(by_date.keys())

    # Per-globe totals across all dates
    globe_totals: dict[str, int] = {}
    for day in by_date.values():
        for gid, cnt in day["by_globe"].items():
            _inc(globe_totals, gid, cnt)

    # Per-directive totals
    directive_totals: dict[str, int] = {}
    for day in by_date.values():
        for did, cnt in day["by_directive"].items():
            _inc(directive_totals, did, cnt)

    # Source type totals
    source_totals: dict[str, int] = {}
    for day in by_date.values():
        for st, cnt in day["source_type_counts"].items():
            _inc(source_totals, st, cnt)

    return {
        "heatmap_id":    "globe-activity-heatmap",
        "generated_at":  _now(),
        "total_events":  total_events,
        "date_count":    len(all_dates),
        "earliest_date": all_dates[0] if all_dates else "",
        "latest_date":   all_dates[-1] if all_dates else "",
        "attention_events": total_attention,
        "source_type_totals": source_totals,
        "globe_totals":  globe_totals,
        "directive_totals": directive_totals,
        **HEATMAP_INVARIANTS,
        "phase":         "34",
        "phase_phrases": HEATMAP_PHRASES,
        "by_date":       by_date,
    }


# ─── Filtered views ───────────────────────────────────────────────────────────

def filter_by_date(hm: dict, date: str) -> dict | None:
    return hm["by_date"].get(date)


def filter_by_globe(hm: dict, globe_id: str) -> dict[str, dict]:
    """Return per-date sub-dicts filtered to a specific globe_id."""
    result = {}
    for date, day in sorted(hm["by_date"].items()):
        if globe_id in day["by_globe"]:
            result[date] = day
    return result


def filter_by_directive(hm: dict, directive_id: str) -> dict[str, dict]:
    result = {}
    for date, day in sorted(hm["by_date"].items()):
        if directive_id in day["by_directive"]:
            result[date] = day
    return result


# ─── Persistence ─────────────────────────────────────────────────────────────

def _build_markdown(hm: dict) -> str:
    lines: list[str] = []
    lines.append("# Globe Activity Heatmap (Phase 34)")
    lines.append("")
    lines.append(f"generated_at: {hm['generated_at']}")
    lines.append(f"date_range: {hm['earliest_date']} — {hm['latest_date']}")
    lines.append(f"total_events: {hm['total_events']}  "
                 f"attention_events: {hm['attention_events']}")
    lines.append("")
    lines.append("## Invariants")
    lines.append("")
    lines.append("| Key | Value |")
    lines.append("|-----|-------|")
    for k, v in HEATMAP_INVARIANTS.items():
        lines.append(f"| `{k}` | `{v}` |")
    lines.append("")
    lines.append("> Event counts reflect what was recorded. "
                 "They are not measures of quality, priority, or impact.")
    lines.append("")
    lines.append("## By Date")
    lines.append("")
    lines.append("| Date | Total | exec_log | resol_sig | rfb | links | ⚠️ attn |")
    lines.append("|------|-------|----------|-----------|-----|-------|---------|")
    for date in sorted(hm["by_date"]):
        d = hm["by_date"][date]
        lines.append(
            f"| {date} | {d['total_events']} "
            f"| {d['execution_log_count']} "
            f"| {d['resolution_signal_count']} "
            f"| {d['reality_feedback_count']} "
            f"| {d['bridge_target_link_count']} "
            f"| {d['needs_attention_count']} |"
        )
    lines.append("")
    lines.append("## By Globe (all dates)")
    lines.append("")
    lines.append("| Globe | Total events |")
    lines.append("|-------|-------------|")
    for gid, cnt in sorted(hm["globe_totals"].items()):
        lines.append(f"| {gid} | {cnt} |")
    lines.append("")
    for phrase in HEATMAP_PHRASES:
        lines.append(f"> \"{phrase}\"")
    return "\n".join(lines)


def save_heatmap() -> tuple[Path, Path]:
    hm = build_heatmap()
    _REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    _HEATMAP_JSON.write_text(
        json.dumps(hm, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _HEATMAP_MD.write_text(_build_markdown(hm), encoding="utf-8")
    return _HEATMAP_JSON, _HEATMAP_MD


def load_heatmap() -> dict:
    if _HEATMAP_JSON.exists():
        try:
            raw = json.loads(_HEATMAP_JSON.read_text(encoding="utf-8"))
            if isinstance(raw, dict) and "by_date" in raw:
                return raw
        except Exception:
            pass
    return build_heatmap()


# ─── CLI print helpers ────────────────────────────────────────────────────────

_BAR_CHARS = " ▁▂▃▄▅▆▇█"


def _bar(count: int, max_count: int, width: int = 12) -> str:
    """ASCII density bar — advisory visual only, not a score."""
    if max_count == 0:
        return " " * width
    ratio = count / max_count
    filled = round(ratio * width)
    char_idx = min(8, round(ratio * 8))
    c = _BAR_CHARS[char_idx]
    return (c * filled).ljust(width)


def _print_day(date: str, day: dict, max_events: int) -> None:
    bar = _bar(day["total_events"], max_events)
    attn = f"  ⚠️  {day['needs_attention_count']}" if day["needs_attention_count"] else ""
    print(f"  {date}  [{bar}] {day['total_events']:2d}{attn}")
    if day["by_globe"]:
        gstr = "  ".join(f"{gid}:{cnt}" for gid, cnt in sorted(day["by_globe"].items()))
        print(f"           globes: {gstr}")
    et = day.get("event_type_counts", {})
    if et:
        etstr = "  ".join(f"{k}:{v}" for k, v in sorted(et.items()))
        print(f"           events: {etstr}")
    print()


def print_heatmap_summary(hm: dict) -> None:
    print(f"\nGlobe Activity Heatmap (Phase 34)")
    print("=" * 60)
    print(f"  generated_at:  {hm.get('generated_at','')}")
    print(f"  date_range:    {hm.get('earliest_date','')} — {hm.get('latest_date','')}")
    print(f"  date_count:    {hm.get('date_count',0)}")
    print(f"  total_events:  {hm.get('total_events',0)}")
    print(f"  attention:     {hm.get('attention_events',0)}"
          "  [objection/rollback/unresolved/contested — not priority]")
    print()
    print("  Source type totals:")
    for st, cnt in sorted(hm.get("source_type_totals", {}).items()):
        print(f"    {st:25s}: {cnt}")
    print()
    print("  Globe totals:")
    for gid, cnt in sorted(hm.get("globe_totals", {}).items()):
        print(f"    {gid:20s}: {cnt}")
    print()
    by_date = hm.get("by_date", {})
    max_ev = max((d["total_events"] for d in by_date.values()), default=1)
    print("  Activity by date  [advisory counts · not measures of quality]")
    print()
    for date in sorted(by_date):
        _print_day(date, by_date[date], max_ev)
    for phrase in HEATMAP_PHRASES:
        print(f'  "{phrase}"')


def print_filtered(hm: dict, label: str, days: dict[str, dict]) -> None:
    total = sum(d["total_events"] for d in days.values())
    attn  = sum(d["needs_attention_count"] for d in days.values())
    print(f"\nGlobe Activity Heatmap (Phase 34) — {label}")
    print("=" * 60)
    print(f"  total_events (filtered): {total}  attention: {attn}")
    print()
    max_ev = max((d["total_events"] for d in days.values()), default=1)
    for date in sorted(days):
        _print_day(date, days[date], max_ev)
    for phrase in HEATMAP_PHRASES:
        print(f'  "{phrase}"')


# ─── CLI entry point ──────────────────────────────────────────────────────────

def main(argv: list[str]) -> None:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return

    cmd = argv[0]

    if cmd == "summary":
        hm = build_heatmap()
        print_heatmap_summary(hm)
        return

    if cmd == "save":
        hm = build_heatmap()
        print_heatmap_summary(hm)
        jp, mp = save_heatmap()
        print(f"Saved: {jp}")
        print(f"Saved: {mp}")
        return

    if cmd == "show-date":
        if len(argv) < 2:
            print("Usage: activity_heatmap.py show-date <YYYY-MM-DD>", file=sys.stderr)
            sys.exit(1)
        date = argv[1]
        hm = load_heatmap()
        day = filter_by_date(hm, date)
        if not day:
            print(f"No activity on {date}", file=sys.stderr)
            sys.exit(1)
        print_filtered(hm, f"date={date}", {date: day})
        return

    if cmd == "show-globe":
        if len(argv) < 2:
            print("Usage: activity_heatmap.py show-globe <globe_id>", file=sys.stderr)
            sys.exit(1)
        globe_id = argv[1]
        hm = load_heatmap()
        days = filter_by_globe(hm, globe_id)
        if not days:
            print(f"No activity for globe {globe_id}", file=sys.stderr)
            sys.exit(1)
        print_filtered(hm, f"globe={globe_id}", days)
        return

    if cmd == "show-directive":
        if len(argv) < 2:
            print("Usage: activity_heatmap.py show-directive <directive_id>",
                  file=sys.stderr)
            sys.exit(1)
        did = argv[1]
        hm = load_heatmap()
        days = filter_by_directive(hm, did)
        if not days:
            print(f"No activity for directive {did}", file=sys.stderr)
            sys.exit(1)
        print_filtered(hm, f"directive={did}", days)
        return

    print(f"Unknown command: {cmd}", file=sys.stderr)
    print("Commands: summary | save | show-date <date> | "
          "show-globe <id> | show-directive <id>", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
