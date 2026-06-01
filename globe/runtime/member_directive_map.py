#!/usr/bin/env python3
"""
member_directive_map.py — Globe Member × Directive Participation Map (Phase 40)
Dan-Go × GITSEA — Globe Foundation Layer

Builds a member × directive participation map from 6 data sources.
Advisory display only — not identity verification, not reputation score,
does not rank members, does not allocate responsibility.

Sources:
    globe/directives/*.json              — directive roster
    globe/data/proposals.json            — proposal→proposer→directive chain
    globe/data/deliberations.json        — deliberation participation
    globe/logs/*.jsonl                   — execution log events
    globe/reports/contribution_timeline.json — supplementary (bridge_target_link)
    globe/reports/reality_feedback_bridge.json — feedback bridge records

CLI:
    python3 globe/runtime/member_directive_map.py summary
    python3 globe/runtime/member_directive_map.py save
    python3 globe/runtime/member_directive_map.py show-member member-masuo-komori
    python3 globe/runtime/member_directive_map.py show-directive directive-claim-proposal-002
    python3 globe/runtime/member_directive_map.py show-globe globe-001
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
_DIRS_DIR    = _GLOBE_DIR / "directives"

_PROPOSALS_JSON     = _DATA_DIR / "proposals.json"
_DELIBERATIONS_JSON = _DATA_DIR / "deliberations.json"
_TIMELINE_JSON      = _REPORTS_DIR / "contribution_timeline.json"
_RFB_JSON           = _REPORTS_DIR / "reality_feedback_bridge.json"
_OUTPUT_JSON        = _REPORTS_DIR / "member_directive_map.json"
_OUTPUT_MD          = _REPORTS_DIR / "member_directive_map.md"

# ─── Invariants ─────────────────────────────────────────────────────────────────

MAP_INVARIANTS: dict = {
    "member_directive_map_is_advisory_display_only": True,
    "member_directive_map_is_not_identity_verification": True,
    "member_directive_map_is_not_reputation_score": True,
    "member_directive_map_does_not_rank_members": True,
    "member_directive_map_does_not_allocate_responsibility": True,
    "human_review_is_required_before_any_real_world_action": True,
    "authority": "none",
}

MAP_PHRASES: list[str] = [
    "Member-directive map is advisory display only.",
    "Member-directive map is not identity verification.",
    "Member-directive map is not reputation score.",
    "Member-directive map does not rank members.",
    "Member-directive map does not allocate responsibility.",
    "Human review is required before any real-world action.",
]

# Canonical relation types (ordered for display)
RELATION_TYPES: list[str] = [
    "proposer_related",
    "deliberation_related",
    "human_approval",
    "observation",
    "objection",
    "feedback",
    "rollback_request",
    "voluntary_resolution_signal",
    "execution_attempt",   # supplementary — not in original spec list but present in data
    "timeline_related",
    "feedback_bridge_related",
]

# Log entry_type → relation_type (direct map; anything else → "log_related")
_LOG_ET_TO_REL: dict[str, str] = {
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

# ─── Accumulator ────────────────────────────────────────────────────────────────

class _EntryAcc:
    """Accumulates events for one (member_id, directive_id) pair."""

    def __init__(self, member_id: str, directive_id: str, globe_id: str, directive_title: str):
        self.member_id      = member_id
        self.directive_id   = directive_id
        self.globe_id       = globe_id
        self.directive_title = directive_title
        self.display_name   = member_id.removeprefix("member-")
        self.actor_types: set[str] = set()
        self.relation_types: set[str] = set()
        self.event_count    = 0
        self.latest_ts      = ""
        self.has_human_approval  = False
        self.has_objection       = False
        self.has_unresolved_signal = False
        self.has_contested_signal  = False
        self._seen: set[str] = set()

    # ------------------------------------------------------------------
    def add(
        self,
        relation_type: str,
        *,
        key: str = "",
        ts: str = "",
        actor_type: str = "",
        resolution_status: str = "",
    ) -> bool:
        if key:
            if key in self._seen:
                return False
            self._seen.add(key)
        self.relation_types.add(relation_type)
        self.event_count += 1
        if actor_type:
            self.actor_types.add(actor_type)
        if ts and (not self.latest_ts or ts > self.latest_ts):
            self.latest_ts = ts
        if relation_type == "human_approval":
            self.has_human_approval = True
        if relation_type == "objection":
            self.has_objection = True
        if relation_type == "voluntary_resolution_signal":
            if resolution_status in ("unresolved", "partially_resolved", ""):
                self.has_unresolved_signal = True
        return True

    # ------------------------------------------------------------------
    def to_dict(self) -> dict:
        mid_slug  = self.member_id.removeprefix("member-")[:12]
        did_slug  = self.directive_id.split("-")[-1][:6]
        map_id    = f"map-{mid_slug}-{did_slug}"
        ordered_rels = [r for r in RELATION_TYPES if r in self.relation_types]
        return {
            "map_id":              map_id,
            "member_id":           self.member_id,
            "display_name":        self.display_name,
            "actor_types":         sorted(self.actor_types),
            "directive_id":        self.directive_id,
            "directive_title":     self.directive_title,
            "globe_id":            self.globe_id,
            "relation_types":      ordered_rels,
            "event_count":         self.event_count,
            "latest_activity_at":  self.latest_ts,
            "has_human_approval":  self.has_human_approval,
            "has_objection":       self.has_objection,
            "has_unresolved_signal": self.has_unresolved_signal,
            "has_contested_signal":  self.has_contested_signal,
            "advisory_only":                    True,
            "not_identity_verification":        True,
            "not_reputation_score":             True,
            "does_not_rank_members":            True,
            "does_not_allocate_responsibility": True,
        }

# ─── Build ───────────────────────────────────────────────────────────────────────

def build_map() -> dict:
    """Collect participation events and build the member × directive map."""

    # ── Load directive roster ────────────────────────────────────────────────
    directives: dict[str, dict] = {}  # directive_id → {globe_id, title, source_proposal_id}
    for f in sorted(_DIRS_DIR.glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        did = d.get("directive_id", "")
        if did:
            directives[did] = {
                "globe_id":           d.get("globe_id", ""),
                "title":              d.get("title", ""),
                "source_proposal_id": d.get("source_proposal_id", ""),
            }

    # ── Load proposals: proposal_id → proposer & globe ───────────────────────
    proposals_raw = _load_json(_PROPOSALS_JSON)
    if not isinstance(proposals_raw, list):
        proposals_raw = []
    proposal_to_proposer: dict[str, str]      = {}
    proposal_to_globe:    dict[str, str]      = {}
    proposal_to_actor_type: dict[str, str]   = {}
    for p in proposals_raw:
        pid = p.get("proposal_id", "")
        if pid:
            proposal_to_proposer[pid]    = p.get("proposer", "")
            proposal_to_globe[pid]       = p.get("globe_id", "")
            proposal_to_actor_type[pid]  = "human"

    # Build proposal_id → directive_id
    proposal_to_directive: dict[str, str] = {}
    for did, dmeta in directives.items():
        spid = dmeta.get("source_proposal_id", "")
        if spid:
            proposal_to_directive[spid] = did

    # ── Accumulator registry ─────────────────────────────────────────────────
    accs: dict[tuple[str, str], _EntryAcc] = {}

    def _acc(member_id: str, directive_id: str) -> _EntryAcc:
        key = (member_id, directive_id)
        if key not in accs:
            dmeta = directives.get(directive_id, {})
            accs[key] = _EntryAcc(
                member_id, directive_id,
                globe_id=dmeta.get("globe_id", ""),
                directive_title=dmeta.get("title", ""),
            )
        return accs[key]

    # ── Source 1: proposer_related via proposals → directives ────────────────
    for pid, proposer in proposal_to_proposer.items():
        if not proposer:
            continue
        did = proposal_to_directive.get(pid)
        if not did:
            continue
        mid  = normalize_member_id(proposer)
        gid  = proposal_to_globe.get(pid, "")
        atype = proposal_to_actor_type.get(pid, "human")
        _acc(mid, did).add(
            "proposer_related",
            key=f"proposer:{pid}",
            actor_type=atype,
        )

    # ── Source 2: deliberation_related via deliberations → proposals → directives
    delibs_raw = _load_json(_DELIBERATIONS_JSON)
    if not isinstance(delibs_raw, list):
        delibs_raw = []
    for d in delibs_raw:
        pid = d.get("proposal_id", "")
        did = proposal_to_directive.get(pid)
        if not did:
            continue  # deliberation on a proposal without a directive
        speaker  = d.get("speaker_name", "")
        sptype   = d.get("speaker_type", "human")
        delib_id = d.get("deliberation_id", "")
        ts       = d.get("created_at", "")
        if not speaker:
            continue
        mid = normalize_member_id(speaker)
        _acc(mid, did).add(
            "deliberation_related",
            key=f"deliberation:{delib_id}",
            ts=ts,
            actor_type=sptype,
        )

    # ── Source 3: logs/*.jsonl — direct entry_type → relation_type ──────────
    # Track objections and VRS per directive for contested_signal computation
    directive_objectors:  dict[str, set[str]] = defaultdict(set)
    directive_vrs_makers: dict[str, set[str]] = defaultdict(set)

    for logfile in sorted(_LOGS_DIR.glob("*.jsonl")):
        did = logfile.stem
        if did not in directives:
            continue
        for raw_line in logfile.read_text(encoding="utf-8").splitlines():
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            try:
                entry = json.loads(raw_line)
            except json.JSONDecodeError:
                continue
            actor      = entry.get("actor_name", "")
            atype      = entry.get("actor_type", "human")
            entry_type = entry.get("entry_type", "")
            log_id     = entry.get("log_id", "")
            ts         = entry.get("created_at", "")
            rs         = entry.get("resolution_status", "")
            if not actor:
                continue
            mid      = normalize_member_id(actor)
            rel_type = _LOG_ET_TO_REL.get(entry_type, "log_related")
            _acc(mid, did).add(
                rel_type,
                key=f"log:{did}:{log_id}",
                ts=ts,
                actor_type=atype,
                resolution_status=rs,
            )
            if rel_type == "objection":
                directive_objectors[did].add(mid)
            if rel_type == "voluntary_resolution_signal":
                directive_vrs_makers[did].add(mid)

    # Compute contested_signal flags
    for did, vrs_members in directive_vrs_makers.items():
        objectors = directive_objectors.get(did, set())
        for mid in vrs_members:
            if (mid, did) in accs and (objectors - {mid}):
                accs[(mid, did)].has_contested_signal = True

    # ── Source 4: reality_feedback_bridge — feedback_bridge_related ──────────
    rfb_raw = _load_json(_RFB_JSON)
    if isinstance(rfb_raw, dict):
        for rec in rfb_raw.get("records", []):
            actor = rec.get("actor_name", "")
            if not actor:
                continue
            did   = rec.get("source_directive_id", "")
            if not did or did not in directives:
                continue
            mid   = normalize_member_id(actor)
            atype = rec.get("actor_type", "human")
            fid   = rec.get("feedback_id", "")
            _acc(mid, did).add(
                "feedback_bridge_related",
                key=f"rfb:{fid}",
                actor_type=atype,
            )

    # ── Source 5: contribution_timeline — timeline_related (bridge_target_link)
    tl_raw = _load_json(_TIMELINE_JSON)
    _TL_KEEP = frozenset({"bridge_target_link"})
    if isinstance(tl_raw, dict):
        for item in tl_raw.get("items", []):
            src_type = item.get("source_type", "")
            if src_type not in _TL_KEEP:
                continue
            actor  = item.get("actor_name", "")
            if not actor:
                continue
            # Try to resolve directive_id from item
            did   = item.get("directive_id", "")
            if not did or did not in directives:
                continue
            mid    = normalize_member_id(actor)
            atype  = item.get("actor_type", "system")
            tl_id  = item.get("timeline_id", "")
            src_id = item.get("source_id", "")
            ts     = item.get("created_at", "")
            _acc(mid, did).add(
                "timeline_related",
                key=f"tl:{tl_id}:{src_id}",
                ts=ts,
                actor_type=atype,
            )

    # ── Assemble output ──────────────────────────────────────────────────────
    entries = sorted(
        (a.to_dict() for a in accs.values()),
        key=lambda e: (e["directive_id"], -e["event_count"], e["member_id"]),
    )

    # Index maps
    by_member: dict[str, list[str]]    = defaultdict(list)
    by_directive: dict[str, list[str]] = defaultdict(list)
    by_globe: dict[str, list[str]]     = defaultdict(list)
    for e in entries:
        by_member[e["member_id"]].append(e["map_id"])
        by_directive[e["directive_id"]].append(e["map_id"])
        by_globe[e["globe_id"]].append(e["map_id"])

    # Attention summary
    attention_entries = [
        e["map_id"] for e in entries
        if e["has_objection"] or e["has_unresolved_signal"] or e["has_contested_signal"]
    ]

    return {
        "map_id":          "globe-member-directive-map",
        "generated_at":    _now_iso(),
        "phase":           "40",
        "total_entries":   len(entries),
        "total_members":   len(by_member),
        "total_directives": len(by_directive),
        "total_globes":    len(by_globe),
        "attention_entries": attention_entries,
        "relation_types":  RELATION_TYPES,
        "phase_phrases":   MAP_PHRASES,
        **MAP_INVARIANTS,
        "entries":         entries,
        "by_member":       dict(by_member),
        "by_directive":    dict(by_directive),
        "by_globe":        dict(by_globe),
    }

# ─── Save helpers ────────────────────────────────────────────────────────────────

def save_map(data: dict) -> None:
    _OUTPUT_JSON.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    _OUTPUT_MD.write_text(_to_markdown(data), encoding="utf-8")
    print(f"  Saved: {_OUTPUT_JSON.relative_to(_GLOBE_DIR.parent)}")
    print(f"  Saved: {_OUTPUT_MD.relative_to(_GLOBE_DIR.parent)}")


def _to_markdown(data: dict) -> str:
    lines: list[str] = [
        "# Globe Member × Directive Participation Map (Phase 40)",
        "",
        f"**Generated:** {data['generated_at']}",
        f"**Total entries:** {data['total_entries']}",
        f"**Total members:** {data['total_members']}",
        f"**Total directives:** {data['total_directives']}",
        "",
        "> Member-directive map is advisory display only.",
        "> Member-directive map is not identity verification.",
        "> Member-directive map is not reputation score.",
        "> Member-directive map does not rank members.",
        "> Member-directive map does not allocate responsibility.",
        "",
        "---",
        "",
        "## Entries",
        "",
    ]
    # Group by directive
    by_did: dict[str, list[dict]] = defaultdict(list)
    for e in data.get("entries", []):
        by_did[e["directive_id"]].append(e)
    for did, ents in sorted(by_did.items()):
        title = ents[0].get("directive_title", did) if ents else did
        lines.append(f"### {did}")
        lines.append(f"*{title}*")
        lines.append("")
        lines.append("| Member | Relations | Events | Latest |")
        lines.append("|---|---|---|---|")
        for e in ents:
            rels  = ", ".join(e.get("relation_types", []))
            attn  = ""
            if e.get("has_objection"):        attn += "⚠️obj "
            if e.get("has_unresolved_signal"): attn += "⚠️vrs "
            if e.get("has_contested_signal"):  attn += "⚠️con "
            lines.append(
                f"| {e['member_id']} {attn}| {rels} "
                f"| {e['event_count']} | {e.get('latest_activity_at','')[:19]} |"
            )
        lines.append("")
    return "\n".join(lines)

# ─── Load (server helper) ────────────────────────────────────────────────────────

def load_map() -> dict:
    """Load from JSON file, or build on-the-fly if not saved yet."""
    if _OUTPUT_JSON.exists():
        return json.loads(_OUTPUT_JSON.read_text(encoding="utf-8"))
    return build_map()


def filter_by_member(data: dict, member_id: str) -> dict:
    entries = [e for e in data.get("entries", []) if e["member_id"] == member_id]
    return {**data, "entries": entries}


def filter_by_directive(data: dict, directive_id: str) -> dict:
    entries = [e for e in data.get("entries", []) if e["directive_id"] == directive_id]
    return {**data, "entries": entries}


def filter_by_globe(data: dict, globe_id: str) -> dict:
    entries = [e for e in data.get("entries", []) if e["globe_id"] == globe_id]
    return {**data, "entries": entries}

# ─── CLI ────────────────────────────────────────────────────────────────────────

def _print_entry(e: dict) -> None:
    rels  = ", ".join(e.get("relation_types", []))
    attn  = []
    if e.get("has_objection"):         attn.append("⚠️ objection")
    if e.get("has_unresolved_signal"): attn.append("⚠️ unresolved_signal")
    if e.get("has_contested_signal"):  attn.append("⚠️ contested_signal")
    print(f"  [{e['directive_id']}]")
    print(f"    member:    {e['member_id']}")
    print(f"    globe:     {e['globe_id']}")
    print(f"    relations: {rels}")
    print(f"    events:    {e['event_count']}")
    print(f"    latest:    {(e.get('latest_activity_at') or '')[:19] or 'N/A'}")
    if attn:
        print(f"    attention: {' · '.join(attn)} — advisory only")
    print()


def _print_phrases() -> None:
    print()
    for phrase in MAP_PHRASES:
        print(f'  "{phrase}"')


def cmd_summary() -> None:
    data = build_map()
    print("Globe Member × Directive Participation Map (Phase 40)")
    print("=" * 60)
    print(f"  generated_at:     {data['generated_at']}")
    print(f"  total_entries:    {data['total_entries']}")
    print(f"  total_members:    {data['total_members']}")
    print(f"  total_directives: {data['total_directives']}")
    print(f"  total_globes:     {data['total_globes']}")
    print(f"  attention_entries:{len(data.get('attention_entries', []))}")
    print()
    print("  Relation type distribution:")
    rel_counts: dict[str, int] = defaultdict(int)
    for e in data["entries"]:
        for rt in e.get("relation_types", []):
            rel_counts[rt] += 1
    for rt in RELATION_TYPES:
        cnt = rel_counts.get(rt, 0)
        if cnt:
            print(f"    {rt:<32}: {cnt}")
    _print_phrases()


def cmd_save() -> None:
    data = build_map()
    print("Saving Globe Member × Directive Participation Map (Phase 40)...")
    save_map(data)
    print(f"  total_entries: {data['total_entries']}")
    print(f"  total_members: {data['total_members']}")
    _print_phrases()


def cmd_show_member(member_id: str) -> None:
    data     = build_map()
    filtered = filter_by_member(data, member_id)
    print(f"Member × Directive Map — member={member_id}")
    print("=" * 60)
    print(f"  {len(filtered['entries'])} entry(ies)")
    print()
    for e in filtered["entries"]:
        _print_entry(e)
    if not filtered["entries"]:
        print(f"  No entries for member={member_id!r}")
    _print_phrases()


def cmd_show_directive(directive_id: str) -> None:
    data     = build_map()
    filtered = filter_by_directive(data, directive_id)
    entries  = filtered["entries"]
    title    = entries[0].get("directive_title", directive_id) if entries else directive_id
    print(f"Member × Directive Map — directive={directive_id}")
    print(f"  {title}")
    print("=" * 60)
    print(f"  {len(entries)} member(s)")
    print()
    for e in entries:
        _print_entry(e)
    if not entries:
        print(f"  No entries for directive={directive_id!r}")
    _print_phrases()


def cmd_show_globe(globe_id: str) -> None:
    data     = build_map()
    filtered = filter_by_globe(data, globe_id)
    print(f"Member × Directive Map — globe={globe_id}")
    print("=" * 60)
    print(f"  {len(filtered['entries'])} entry(ies)")
    print()
    for e in filtered["entries"]:
        _print_entry(e)
    if not filtered["entries"]:
        print(f"  No entries in globe={globe_id!r}")
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
    elif args[0] == "show-directive":
        if len(args) < 2:
            print("Usage: show-directive <directive_id>", file=sys.stderr)
            sys.exit(1)
        cmd_show_directive(args[1])
    elif args[0] == "show-globe":
        if len(args) < 2:
            print("Usage: show-globe <globe_id>", file=sys.stderr)
            sys.exit(1)
        cmd_show_globe(args[1])
    else:
        print(f"Unknown command: {args[0]!r}", file=sys.stderr)
        print("Commands: summary | save | show-member | show-directive | show-globe",
              file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
