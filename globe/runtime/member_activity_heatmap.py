#!/usr/bin/env python3
"""
member_activity_heatmap.py — Globe Member Activity Heatmap (Phase 39)
Dan-Go × GITSEA — Globe Foundation Layer

Builds a per-member, per-date, per-activity-type activity heatmap from
6 data sources. Advisory display only — not identity verification,
not reputation score, does not rank members, creates no authority.

Sources:
    globe/reports/member_profiles.json   — member roster
    globe/logs/*.jsonl                   — execution log events
    globe/data/deliberations.json        — deliberation events
    globe/data/proposals.json            — proposal events
    globe/reports/contribution_timeline.json — supplementary events
    globe/reports/globe_feed.json        — supplementary (no actor data)

CLI:
    python3 globe/runtime/member_activity_heatmap.py summary
    python3 globe/runtime/member_activity_heatmap.py save
    python3 globe/runtime/member_activity_heatmap.py show-member member-masuo-komori
    python3 globe/runtime/member_activity_heatmap.py show-globe globe-001
    python3 globe/runtime/member_activity_heatmap.py show-date 2026-05-31
"""

import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# ─── Paths ──────────────────────────────────────────────────────────────────────

_GLOBE_DIR   = Path(__file__).resolve().parents[1]
_DATA_DIR    = _GLOBE_DIR / "data"
_LOGS_DIR    = _GLOBE_DIR / "logs"
_REPORTS_DIR = _GLOBE_DIR / "reports"

_PROFILES_JSON      = _REPORTS_DIR / "member_profiles.json"
_TIMELINE_JSON      = _REPORTS_DIR / "contribution_timeline.json"
_FEED_JSON          = _REPORTS_DIR / "globe_feed.json"
_PROPOSALS_JSON     = _DATA_DIR / "proposals.json"
_DELIBERATIONS_JSON = _DATA_DIR / "deliberations.json"
_OUTPUT_JSON        = _REPORTS_DIR / "member_activity_heatmap.json"
_OUTPUT_MD          = _REPORTS_DIR / "member_activity_heatmap.md"

# ─── Invariants ─────────────────────────────────────────────────────────────────

HEATMAP_INVARIANTS: dict = {
    "member_activity_heatmap_is_advisory_display_only": True,
    "member_activity_heatmap_is_not_identity_verification": True,
    "member_activity_heatmap_is_not_reputation_score": True,
    "member_activity_heatmap_does_not_rank_members": True,
    "member_activity_heatmap_creates_no_authority": True,
    "human_review_is_required_before_any_real_world_action": True,
    "authority": "none",
}

HEATMAP_PHRASES: list[str] = [
    "Member activity heatmap is advisory display only.",
    "Member activity heatmap is not identity verification.",
    "Member activity heatmap is not reputation score.",
    "Member activity heatmap does not rank members.",
    "Member activity heatmap creates no authority.",
    "Human review is required before any real-world action.",
]

# Canonical ordered activity types — each log entry maps to exactly one
ACTIVITY_TYPES: list[str] = [
    "proposal",
    "deliberation",
    "human_approval",
    "observation",
    "objection",
    "feedback",
    "rollback_request",
    "voluntary_resolution_signal",
    "execution_attempt",
    "execution_log",    # catch-all for unrecognised log entry_types
    "timeline_event",   # bridge_target_link and other timeline-only events
    "feed_item",
]

# entry_type from logs → activity_type (direct map; anything else → execution_log)
_LOG_ET_MAP: dict[str, str] = {
    "human_approval":              "human_approval",
    "observation":                 "observation",
    "objection":                   "objection",
    "feedback":                    "feedback",
    "rollback_request":            "rollback_request",
    "voluntary_resolution_signal": "voluntary_resolution_signal",
    "execution_attempt":           "execution_attempt",
}

# ─── Helpers ────────────────────────────────────────────────────────────────────

def _parse_date(ts: str) -> str:
    """Extract YYYY-MM-DD from any ISO timestamp string."""
    if not ts:
        return ""
    m = re.match(r"(\d{4}-\d{2}-\d{2})", ts.strip())
    return m.group(1) if m else ""

def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

def normalize_member_id(name: str) -> str:
    """Normalize actor display name to member_id slug.

    Spaces and underscores → hyphens; then strip non-alphanumeric-hyphen chars.
    Matches the same slug logic used in member_profile.py.
    """
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

# ─── Accumulator ────────────────────────────────────────────────────────────────

class _MemberAcc:
    """Accumulates per-member, per-date, per-activity-type event counts.

    Each event is counted exactly once (deduplicated by key).
    """

    def __init__(self, member_id: str):
        self.member_id = member_id
        self.display_name = member_id.removeprefix("member-")
        self.actor_types: set[str] = set()
        self.globe_ids: set[str] = set()
        # by_date[date_str][activity_type] = count
        self.by_date: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        # by_globe[globe_id] = count
        self.by_globe: dict[str, int] = defaultdict(int)
        # by_activity_type[activity_type] = count
        self.by_at: dict[str, int] = defaultdict(int)
        self.total_events: int = 0
        self.latest_ts: str = ""
        self.objection_count: int = 0
        self.unresolved_signal_count: int = 0
        self.contested_signal_count: int = 0
        # Deduplication keys (source-event-id level)
        self._seen: set[str] = set()

    # ------------------------------------------------------------------
    def add(
        self,
        activity_type: str,
        date: str,
        globe_id: str = "",
        *,
        key: str = "",
        ts: str = "",
        actor_type: str = "",
        resolution_status: str = "",
    ) -> bool:
        """Record one event.  Returns False if deduplicated (already seen)."""
        if key:
            if key in self._seen:
                return False
            self._seen.add(key)
        if actor_type:
            self.actor_types.add(actor_type)
        self.by_at[activity_type] += 1
        if date:
            self.by_date[date][activity_type] += 1
        if globe_id:
            self.by_globe[globe_id] += 1
            self.globe_ids.add(globe_id)
        self.total_events += 1
        if ts and (not self.latest_ts or ts > self.latest_ts):
            self.latest_ts = ts
        if activity_type == "objection":
            self.objection_count += 1
        if activity_type == "voluntary_resolution_signal":
            if resolution_status in ("unresolved", "partially_resolved", ""):
                self.unresolved_signal_count += 1
        return True

    # ------------------------------------------------------------------
    def to_dict(self) -> dict:
        by_date_out: dict[str, dict[str, int]] = {}
        for d in sorted(self.by_date):
            row = {at: self.by_date[d].get(at, 0) for at in ACTIVITY_TYPES}
            # Only include non-zero types
            by_date_out[d] = {k: v for k, v in row.items() if v > 0}
        by_at_out = {at: self.by_at.get(at, 0) for at in ACTIVITY_TYPES}
        return {
            "member_id":               self.member_id,
            "display_name":            self.display_name,
            "actor_types":             sorted(self.actor_types),
            "globe_ids":               sorted(self.globe_ids),
            "total_events":            self.total_events,
            "by_activity_type":        by_at_out,
            "by_globe":                dict(self.by_globe),
            "by_date":                 by_date_out,
            "latest_activity_at":      self.latest_ts,
            "objection_count":         self.objection_count,
            "unresolved_signal_count": self.unresolved_signal_count,
            "contested_signal_count":  self.contested_signal_count,
            "advisory_only":                    True,
            "not_identity_verification":        True,
            "not_reputation_score":             True,
            "does_not_rank_members":            True,
            "creates_no_authority":             True,
        }

# ─── Build ───────────────────────────────────────────────────────────────────────

def build_heatmap() -> dict:
    """Collect events from all 6 sources and build the member activity heatmap."""

    accs: dict[str, _MemberAcc] = {}

    def _acc(member_id: str) -> _MemberAcc:
        if member_id not in accs:
            accs[member_id] = _MemberAcc(member_id)
        return accs[member_id]

    # ── Source 1: member_profiles.json — seed member roster + display names ──
    profiles_raw = _load_json(_PROFILES_JSON)
    if isinstance(profiles_raw, dict):
        for mp in profiles_raw.get("members", []):
            mid = mp.get("member_id", "")
            if not mid:
                continue
            a = _acc(mid)
            a.display_name = mp.get("display_name", mid.removeprefix("member-"))
            for at in mp.get("actor_types", []):
                a.actor_types.add(at)

    # ── Source 2: proposals.json ─────────────────────────────────────────────
    proposals_raw = _load_json(_PROPOSALS_JSON)
    if not isinstance(proposals_raw, list):
        proposals_raw = []
    pid_to_globe: dict[str, str] = {}
    for p in proposals_raw:
        gid = p.get("globe_id", "")
        pid = p.get("proposal_id", "")
        if pid:
            pid_to_globe[pid] = gid
        proposer = p.get("proposer", "")
        if not proposer:
            continue
        mid = normalize_member_id(proposer)
        ts  = p.get("created_at", "")
        date = _parse_date(ts)
        _acc(mid).add(
            "proposal", date, gid,
            key=f"proposal:{pid}",
            ts=ts,
            actor_type="human",
        )

    # ── Source 3: deliberations.json ─────────────────────────────────────────
    delibs_raw = _load_json(_DELIBERATIONS_JSON)
    if not isinstance(delibs_raw, list):
        delibs_raw = []
    for d in delibs_raw:
        did    = d.get("deliberation_id", "")
        speaker = d.get("speaker_name", "")
        sptype  = d.get("speaker_type", "human")
        pid     = d.get("proposal_id", "")
        ts      = d.get("created_at", "")
        date    = _parse_date(ts)
        gid     = pid_to_globe.get(pid, "")
        if not speaker:
            continue
        mid = normalize_member_id(speaker)
        _acc(mid).add(
            "deliberation", date, gid,
            key=f"deliberation:{did}",
            ts=ts,
            actor_type=sptype,
        )

    # ── Source 4: logs/*.jsonl ───────────────────────────────────────────────
    # Track which directives have objections and VRS (for contested_signal_count)
    directive_objectors:  dict[str, set[str]] = defaultdict(set)  # dir_id → set of member_ids
    directive_vrs_makers: dict[str, set[str]] = defaultdict(set)  # dir_id → set of member_ids

    for logfile in sorted(_LOGS_DIR.glob("*.jsonl")):
        directive_id = logfile.stem   # e.g. directive-claim-proposal-002
        for raw_line in logfile.read_text(encoding="utf-8").splitlines():
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            try:
                entry = json.loads(raw_line)
            except json.JSONDecodeError:
                continue
            log_id    = entry.get("log_id", "")
            actor     = entry.get("actor_name", "")
            atype     = entry.get("actor_type", "human")
            entry_type = entry.get("entry_type", "")
            gid       = entry.get("globe_id", "")
            ts        = entry.get("created_at", "")
            date      = _parse_date(ts)
            rs        = entry.get("resolution_status", "")
            if not actor:
                continue
            mid      = normalize_member_id(actor)
            act_type = _LOG_ET_MAP.get(entry_type, "execution_log")
            key      = f"log:{directive_id}:{log_id}"
            _acc(mid).add(
                act_type, date, gid,
                key=key, ts=ts, actor_type=atype, resolution_status=rs,
            )
            # Track for contested_signal_count computation
            if act_type == "objection":
                directive_objectors[directive_id].add(mid)
            if act_type == "voluntary_resolution_signal":
                directive_vrs_makers[directive_id].add(mid)

    # Compute contested_signal_count:
    # A member's VRS is "contested" if another member has objected in the same directive
    for dir_id, vrs_members in directive_vrs_makers.items():
        objectors = directive_objectors.get(dir_id, set())
        for mid in vrs_members:
            other_objectors = objectors - {mid}
            if other_objectors and mid in accs:
                accs[mid].contested_signal_count += 1

    # ── Source 5: contribution_timeline.json — supplementary only ────────────
    # Only ingest timeline_event items from non-log / non-rfb sources
    # (bridge_target_link entries — actor=bridge_target_linker).
    # Skip items whose source_type is execution_log, reality_feedback,
    # or resolution_signal (already counted from log files).
    tl_raw = _load_json(_TIMELINE_JSON)
    _TL_SKIP_SOURCES = frozenset(
        {"execution_log", "reality_feedback", "resolution_signal"}
    )
    if isinstance(tl_raw, dict):
        for item in tl_raw.get("items", []):
            src_type = item.get("source_type", "")
            if src_type in _TL_SKIP_SOURCES:
                continue
            actor    = item.get("actor_name", "")
            if not actor:
                continue
            tl_id    = item.get("timeline_id", "")
            src_id   = item.get("source_id", "")
            atype    = item.get("actor_type", "system")
            gid      = item.get("globe_id", "")
            ts       = item.get("created_at", "")
            date     = _parse_date(ts)
            mid      = normalize_member_id(actor)
            key      = f"tl:{tl_id}:{src_id}"
            _acc(mid).add(
                "timeline_event", date, gid,
                key=key, ts=ts, actor_type=atype,
            )

    # ── Source 6: globe_feed.json — skip (no actor_name in feed items) ───────
    # Feed items are aggregated summaries; no per-actor attribution available.

    # ── Global by_date summary ───────────────────────────────────────────────
    all_dates: set[str] = set()
    for a in accs.values():
        all_dates.update(a.by_date.keys())

    by_date_summary: dict[str, dict] = {}
    for date in sorted(all_dates):
        active: list[str] = []
        date_at: dict[str, int] = defaultdict(int)
        total_ev = 0
        for mid, a in accs.items():
            if date in a.by_date:
                active.append(mid)
                total_ev += sum(a.by_date[date].values())
                for at, cnt in a.by_date[date].items():
                    date_at[at] += cnt
        by_date_summary[date] = {
            "total_events":     total_ev,
            "active_members":   sorted(active),
            "by_activity_type": dict(date_at),
        }

    # ── Assemble output ──────────────────────────────────────────────────────
    members_list = sorted(
        (a.to_dict() for a in accs.values()),
        key=lambda d: (-d["total_events"], d["member_id"]),
    )

    total_events = sum(a.total_events for a in accs.values())

    return {
        "heatmap_id":    "globe-member-activity-heatmap",
        "generated_at":  _now_iso(),
        "phase":         "39",
        "total_members": len(accs),
        "total_events":  total_events,
        "all_dates":     sorted(all_dates),
        "activity_types": ACTIVITY_TYPES,
        "phase_phrases":  HEATMAP_PHRASES,
        **HEATMAP_INVARIANTS,
        "members":         members_list,
        "by_date_summary": by_date_summary,
    }

# ─── Save helpers ────────────────────────────────────────────────────────────────

def save_heatmap(data: dict) -> None:
    """Write heatmap JSON and Markdown reports."""
    _OUTPUT_JSON.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    _OUTPUT_MD.write_text(_to_markdown(data), encoding="utf-8")
    print(f"  Saved: {_OUTPUT_JSON.relative_to(_GLOBE_DIR.parent)}")
    print(f"  Saved: {_OUTPUT_MD.relative_to(_GLOBE_DIR.parent)}")


def _to_markdown(data: dict) -> str:
    lines: list[str] = [
        "# Globe Member Activity Heatmap (Phase 39)",
        "",
        f"**Generated:** {data['generated_at']}",
        f"**Total members:** {data['total_members']}",
        f"**Total events:** {data['total_events']}",
        f"**Date range:** {data['all_dates'][0] if data['all_dates'] else 'N/A'}"
        f" – {data['all_dates'][-1] if data['all_dates'] else 'N/A'}",
        "",
        "> Member activity heatmap is advisory display only.",
        "> Member activity heatmap is not identity verification.",
        "> Member activity heatmap is not reputation score.",
        "> Member activity heatmap does not rank members.",
        "> Member activity heatmap creates no authority.",
        "",
        "---",
        "",
        "## Members",
        "",
    ]
    for m in data["members"]:
        lines.append(f"### {m['member_id']}")
        lines.append(f"- display_name: {m['display_name']}")
        lines.append(f"- actor_types: {', '.join(m['actor_types'])}")
        lines.append(f"- globe_ids: {', '.join(m['globe_ids'])}")
        lines.append(f"- total_events: {m['total_events']}")
        lines.append(f"- latest_activity_at: {m['latest_activity_at']}")
        at = m["by_activity_type"]
        at_parts = [f"{k}:{v}" for k, v in at.items() if v > 0]
        if at_parts:
            lines.append(f"- activity: {', '.join(at_parts)}")
        if m["objection_count"]:
            lines.append(f"- ⚠️ objections: {m['objection_count']} (advisory only — requires human review)")
        if m["unresolved_signal_count"]:
            lines.append(
                f"- ⚠️ unresolved_signals: {m['unresolved_signal_count']}"
                " (voluntary_resolution_signal does not confirm resolution)"
            )
        if m["contested_signal_count"]:
            lines.append(
                f"- ⚠️ contested_signals: {m['contested_signal_count']}"
                " (objection by another member exists — human review required)"
            )
        lines.append("")
        if m["by_date"]:
            lines.append("  | Date | Activity |")
            lines.append("  |---|---|")
            for date, acts in sorted(m["by_date"].items()):
                act_str = ", ".join(f"{k}:{v}" for k, v in acts.items() if v > 0)
                lines.append(f"  | {date} | {act_str} |")
        lines.append("")

    lines += [
        "---",
        "",
        "## By Date",
        "",
    ]
    for date, summary in sorted(data["by_date_summary"].items()):
        lines.append(f"### {date}")
        lines.append(f"- total_events: {summary['total_events']}")
        lines.append(f"- active_members: {', '.join(summary['active_members'])}")
        at_str = ", ".join(
            f"{k}:{v}" for k, v in summary["by_activity_type"].items() if v > 0
        )
        if at_str:
            lines.append(f"- by_activity_type: {at_str}")
        lines.append("")

    return "\n".join(lines)

# ─── Load (server helper) ────────────────────────────────────────────────────────

def load_heatmap() -> dict:
    """Load from JSON file, or build on-the-fly if not saved yet."""
    if _OUTPUT_JSON.exists():
        return json.loads(_OUTPUT_JSON.read_text(encoding="utf-8"))
    return build_heatmap()

# ─── Filter helpers (for HTTP server) ───────────────────────────────────────────

def filter_by_member(data: dict, member_id: str) -> dict:
    """Return a copy of data filtered to one member."""
    members = [m for m in data.get("members", []) if m["member_id"] == member_id]
    return {**data, "members": members, "total_members": len(members)}


def filter_by_globe(data: dict, globe_id: str) -> dict:
    """Return a copy of data filtered to members in globe_id."""
    members = [
        m for m in data.get("members", [])
        if globe_id in m.get("globe_ids", [])
    ]
    return {**data, "members": members, "total_members": len(members)}


def filter_by_date(data: dict, date: str) -> dict:
    """Return a copy of data filtered to members active on date."""
    members = [
        m for m in data.get("members", [])
        if date in m.get("by_date", {})
    ]
    return {**data, "members": members, "total_members": len(members)}

# ─── CLI ────────────────────────────────────────────────────────────────────────

def _print_member(m: dict) -> None:
    icon = {"human": "👤", "ai": "🤖", "system": "⚙️"}.get(
        (m["actor_types"] or ["human"])[0], "👤"
    )
    print(f"  {icon} {m['member_id']}")
    print(f"     display_name: {m['display_name']}")
    print(f"     globe_ids:    {', '.join(m['globe_ids'])}")
    print(f"     total_events: {m['total_events']}")
    print(f"     latest:       {m['latest_activity_at'][:19] if m['latest_activity_at'] else 'N/A'}")
    at = m["by_activity_type"]
    at_parts = [f"{k}:{v}" for k, v in at.items() if v > 0]
    if at_parts:
        print(f"     activity:     {',  '.join(at_parts)}")
    if m["objection_count"]:
        print(f"     ⚠️  objections: {m['objection_count']} — advisory only")
    if m["unresolved_signal_count"]:
        print(f"     ⚠️  unresolved_signals: {m['unresolved_signal_count']}")
    if m["contested_signal_count"]:
        print(f"     ⚠️  contested_signals: {m['contested_signal_count']} — human review required")
    if m["by_date"]:
        print(f"     by_date:")
        for date, acts in sorted(m["by_date"].items()):
            act_str = ",  ".join(f"{k}:{v}" for k, v in acts.items() if v > 0)
            print(f"       {date}: {act_str}")
    print()


def _print_phrases() -> None:
    print()
    for phrase in HEATMAP_PHRASES:
        print(f'  "{phrase}"')


def cmd_summary() -> None:
    data = build_heatmap()
    print("Globe Member Activity Heatmap (Phase 39)")
    print("=" * 60)
    print(f"  generated_at:  {data['generated_at']}")
    print(f"  total_members: {data['total_members']}")
    print(f"  total_events:  {data['total_events']}")
    print(f"  date_range:    {data['all_dates'][0] if data['all_dates'] else 'N/A'}"
          f" — {data['all_dates'][-1] if data['all_dates'] else 'N/A'}")
    print()
    print("  Activity type totals:")
    at_totals: dict[str, int] = defaultdict(int)
    for m in data["members"]:
        for at, cnt in m["by_activity_type"].items():
            at_totals[at] += cnt
    for at in ACTIVITY_TYPES:
        cnt = at_totals.get(at, 0)
        if cnt:
            print(f"    {at:<30}: {cnt}")
    print()
    print("  Active dates:")
    for date, summ in sorted(data["by_date_summary"].items()):
        print(f"    {date}: {summ['total_events']} events, "
              f"{len(summ['active_members'])} members")
    _print_phrases()


def cmd_save() -> None:
    data = build_heatmap()
    print("Saving Globe Member Activity Heatmap (Phase 39)...")
    save_heatmap(data)
    print(f"  total_members: {data['total_members']}")
    print(f"  total_events:  {data['total_events']}")
    _print_phrases()


def cmd_show_member(member_id: str) -> None:
    data = build_heatmap()
    filtered = filter_by_member(data, member_id)
    print(f"Globe Member Activity — member={member_id}")
    print("=" * 60)
    print(f"  {filtered['total_members']} member(s)")
    print()
    for m in filtered["members"]:
        _print_member(m)
    if not filtered["members"]:
        print(f"  No member found with id={member_id!r}")
    _print_phrases()


def cmd_show_globe(globe_id: str) -> None:
    data = build_heatmap()
    filtered = filter_by_globe(data, globe_id)
    print(f"Globe Member Activity — globe={globe_id}")
    print("=" * 60)
    print(f"  {filtered['total_members']} member(s)")
    print()
    for m in filtered["members"]:
        _print_member(m)
    if not filtered["members"]:
        print(f"  No members found in globe_id={globe_id!r}")
    _print_phrases()


def cmd_show_date(date: str) -> None:
    data = build_heatmap()
    filtered = filter_by_date(data, date)
    print(f"Globe Member Activity — date={date}")
    print("=" * 60)
    print(f"  {filtered['total_members']} member(s) active on {date}")
    print()
    summary = data.get("by_date_summary", {}).get(date)
    if summary:
        print(f"  Total events on {date}: {summary['total_events']}")
        at_str = ",  ".join(
            f"{k}:{v}" for k, v in summary["by_activity_type"].items() if v > 0
        )
        print(f"  By type: {at_str}")
        print()
    for m in filtered["members"]:
        _print_member(m)
    if not filtered["members"]:
        print(f"  No activity found on date={date!r}")
    _print_phrases()


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] == "summary":
        cmd_summary()
    elif args[0] == "save":
        cmd_save()
    elif args[0] == "show-member":
        if len(args) < 2:
            print("Usage: show-member <member_id>", file=sys.stderr)
            sys.exit(1)
        cmd_show_member(args[1])
    elif args[0] == "show-globe":
        if len(args) < 2:
            print("Usage: show-globe <globe_id>", file=sys.stderr)
            sys.exit(1)
        cmd_show_globe(args[1])
    elif args[0] == "show-date":
        if len(args) < 2:
            print("Usage: show-date <YYYY-MM-DD>", file=sys.stderr)
            sys.exit(1)
        cmd_show_date(args[1])
    else:
        print(f"Unknown command: {args[0]!r}", file=sys.stderr)
        print("Commands: summary | save | show-member | show-globe | show-date", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
