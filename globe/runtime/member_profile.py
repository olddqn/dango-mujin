"""member_profile.py — Phase 38: Globe Member Profile View

Aggregates activity records for each actor observed across Globe-layer data
sources into an advisory member profile. The profile is a browsing aid only.

INVARIANTS (permanent, not negotiable):
  Member profile is advisory display only.
  Member profile is not identity verification.
  Member profile is not reputation score.
  Member profile creates no authority.
  Member profile does not rank participants.
  Human review is required before any real-world action.
  authority: none

Data sources (read-only):
  globe/data/proposals.json         → proposer field
  globe/data/deliberations.json     → speaker_name field
  globe/logs/*.jsonl                → actor_name field
  globe/reports/reality_feedback_bridge.json → actor_name field
  globe/reports/contribution_timeline.json   → actor_name field
  globe/reports/globe_feed.json              → supplementary cross-check

CLI:
  python3 globe/runtime/member_profile.py summary
  python3 globe/runtime/member_profile.py save
  python3 globe/runtime/member_profile.py show-member <member_id>
  python3 globe/runtime/member_profile.py show-globe <globe_id>
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────

_GLOBE_DIR      = Path(__file__).resolve().parents[1]
_DATA_DIR       = _GLOBE_DIR / "data"
_DIRECTIVES_DIR = _GLOBE_DIR / "directives"
_LOGS_DIR       = _GLOBE_DIR / "logs"
_REPORTS_DIR    = _GLOBE_DIR / "reports"

_PROFILES_JSON = _REPORTS_DIR / "member_profiles.json"
_PROFILES_MD   = _REPORTS_DIR / "member_profiles.md"

# ─── Invariants ───────────────────────────────────────────────────────────────

PROFILE_INVARIANTS = {
    "member_profile_is_advisory_display_only":    True,
    "member_profile_is_not_identity_verification": True,
    "member_profile_is_not_reputation_score":     True,
    "member_profile_creates_no_authority":         True,
    "member_profile_does_not_rank_participants":   True,
    "human_review_is_required_before_any_real_world_action": True,
    "authority": "none",
}

PROFILE_PHRASES = [
    "Member profile is advisory display only.",
    "Member profile is not identity verification.",
    "Member profile is not reputation score.",
    "Member profile creates no authority.",
    "Member profile does not rank participants.",
    "Human review is required before any real-world action.",
]

# ─── Member ID normalisation ──────────────────────────────────────────────────

def normalize_member_id(name: str) -> str:
    """Convert any actor_name / speaker_name / proposer to a stable member_id.

    Rules:
      - Lowercase
      - Spaces → hyphens
      - Non-alphanumeric (except hyphens) → removed
      - Collapse consecutive hyphens
      - Strip leading/trailing hyphens
      - Prefix "member-"
      - Empty / unknown → "member-unknown"
    """
    if not name or not name.strip():
        return "member-unknown"
    slug = name.lower()
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    slug = re.sub(r'-+', '-', slug).strip('-')
    if not slug:
        return "member-unknown"
    return f"member-{slug}"


# ─── Member accumulator ───────────────────────────────────────────────────────

class _MemberAcc:
    """Collects activity counts for one member across all data sources."""

    def __init__(self, display_name: str) -> None:
        self.display_name         = display_name
        self.actor_types: set[str] = set()
        self.globe_ids: set[str]   = set()
        self.proposal_count        = 0
        self.deliberation_count    = 0
        self.execution_log_count   = 0
        self.human_approval_count  = 0
        self.observation_count     = 0
        self.feedback_count        = 0   # reality_feedback_bridge records
        self.objection_count       = 0
        self.rollback_request_count = 0
        self.voluntary_resolution_signal_count = 0
        self.execution_attempt_count = 0
        self.latest_activity_at    = ""
        self.source_paths: set[str] = set()

    def touch_ts(self, ts: str) -> None:
        normalized = str(ts)[:19].replace("T", " ") if ts else ""
        if normalized and normalized > self.latest_activity_at:
            self.latest_activity_at = normalized

    def to_dict(self, member_id: str) -> dict:
        total = (
            self.proposal_count + self.deliberation_count
            + self.execution_log_count + self.feedback_count
        )
        return {
            "member_id":            member_id,
            "display_name":         self.display_name,
            "actor_types":          sorted(self.actor_types),
            "globe_ids":            sorted(self.globe_ids),
            "total_activity_count": total,
            "proposal_count":       self.proposal_count,
            "deliberation_count":   self.deliberation_count,
            "execution_log_count":  self.execution_log_count,
            "human_approval_count": self.human_approval_count,
            "observation_count":    self.observation_count,
            "feedback_count":       self.feedback_count,
            "objection_count":      self.objection_count,
            "rollback_request_count": self.rollback_request_count,
            "voluntary_resolution_signal_count": self.voluntary_resolution_signal_count,
            "execution_attempt_count": self.execution_attempt_count,
            "latest_activity_at":   self.latest_activity_at,
            "source_paths":         sorted(self.source_paths),
            "advisory_only":              True,
            "not_identity_verification":  True,
            "not_reputation_score":       True,
            "creates_no_authority":       True,
        }


# ─── Data loaders ─────────────────────────────────────────────────────────────

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


def _directive_globe_map() -> dict[str, str]:
    """Return directive_id → globe_id mapping from directives/*.json."""
    result: dict[str, str] = {}
    directives_dir = _GLOBE_DIR / "directives"
    for p in sorted(directives_dir.glob("*.json")):
        d = _load_json(p)
        if isinstance(d, dict):
            result[d.get("directive_id", p.stem)] = d.get("globe_id", "")
    return result


def _proposal_globe_map() -> dict[str, str]:
    """Return proposal_id → globe_id mapping from proposals.json."""
    raw = _load_json(_DATA_DIR / "proposals.json")
    if not isinstance(raw, list):
        return {}
    return {p["proposal_id"]: p.get("globe_id", "") for p in raw if "proposal_id" in p}


# ─── Core aggregation ─────────────────────────────────────────────────────────

def build_profiles() -> dict:
    """Build and return the full member profiles report.

    Advisory only. Not identity verification. Not reputation score.
    """
    accumulators: dict[str, _MemberAcc] = {}   # member_id → acc

    def _acc(name: str, actor_type: str = "") -> _MemberAcc:
        mid = normalize_member_id(name)
        if mid not in accumulators:
            accumulators[mid] = _MemberAcc(name)
        acc = accumulators[mid]
        if actor_type:
            acc.actor_types.add(actor_type)
        return acc

    pg_map = _proposal_globe_map()
    dg_map = _directive_globe_map()

    # ── 1. proposals.json ─────────────────────────────────────────────────────
    raw_proposals = _load_json(_DATA_DIR / "proposals.json")
    if isinstance(raw_proposals, list):
        for p in raw_proposals:
            name = p.get("proposer", "")
            gid  = p.get("globe_id", "")
            ts   = p.get("created_at", "")
            if not name:
                continue
            acc = _acc(name, "human")
            acc.proposal_count += 1
            if gid:
                acc.globe_ids.add(gid)
            acc.touch_ts(ts)
            acc.source_paths.add("globe/data/proposals.json")

    # ── 2. deliberations.json ─────────────────────────────────────────────────
    raw_delibs = _load_json(_DATA_DIR / "deliberations.json")
    if isinstance(raw_delibs, list):
        for d in raw_delibs:
            name  = d.get("speaker_name", "")
            stype = d.get("speaker_type", "human")
            pid   = d.get("proposal_id", "")
            gid   = pg_map.get(pid, "")
            ts    = d.get("created_at", "")
            if not name:
                continue
            acc = _acc(name, stype)
            acc.deliberation_count += 1
            if gid:
                acc.globe_ids.add(gid)
            acc.touch_ts(ts)
            acc.source_paths.add("globe/data/deliberations.json")

    # ── 3. logs/*.jsonl ───────────────────────────────────────────────────────
    for p in sorted(_LOGS_DIR.glob("*.jsonl")):
        directive_id = p.stem
        gid_from_dir = dg_map.get(directive_id, "")
        entries = _load_jsonl(p)
        for e in entries:
            name  = e.get("actor_name", "")
            atype = e.get("actor_type", "human")
            etype = e.get("entry_type", "")
            ts    = e.get("created_at", "")
            gid   = e.get("globe_id", gid_from_dir)
            if not name:
                continue
            acc = _acc(name, atype)
            acc.execution_log_count += 1
            if gid:
                acc.globe_ids.add(gid)
            acc.touch_ts(ts)
            acc.source_paths.add(f"globe/logs/{p.name}")
            # Specific type counts
            if etype == "human_approval":
                acc.human_approval_count += 1
            elif etype == "observation":
                acc.observation_count += 1
            elif etype == "objection":
                acc.objection_count += 1
            elif etype == "rollback_request":
                acc.rollback_request_count += 1
            elif etype == "voluntary_resolution_signal":
                acc.voluntary_resolution_signal_count += 1
            elif etype == "execution_attempt":
                acc.execution_attempt_count += 1

    # ── 4. reality_feedback_bridge.json ───────────────────────────────────────
    rpt_rfb = _load_json(_REPORTS_DIR / "reality_feedback_bridge.json")
    if isinstance(rpt_rfb, dict):
        for r in rpt_rfb.get("records", []):
            name  = r.get("actor_name", "")
            atype = r.get("actor_type", "human")
            gid   = r.get("globe_id", "")
            ts    = r.get("source_entry_created_at", rpt_rfb.get("generated_at", ""))
            if not name:
                continue
            acc = _acc(name, atype)
            acc.feedback_count += 1
            if gid:
                acc.globe_ids.add(gid)
            acc.touch_ts(ts)
            acc.source_paths.add("globe/reports/reality_feedback_bridge.json")

    # ── 5. contribution_timeline.json (supplementary) ─────────────────────────
    rpt_tl = _load_json(_REPORTS_DIR / "contribution_timeline.json")
    if isinstance(rpt_tl, dict):
        for it in rpt_tl.get("items", []):
            name  = it.get("actor_name", "")
            atype = it.get("actor_type", "")
            gid   = it.get("globe_id", "")
            ts    = it.get("created_at", "")
            if not name:
                continue
            # Only update globe_ids / actor_types / timestamps; avoid double-counting
            acc = _acc(name, atype)
            if gid:
                acc.globe_ids.add(gid)
            acc.touch_ts(ts)
            acc.source_paths.add("globe/reports/contribution_timeline.json")

    # ── 6. globe_feed.json (supplementary — catch any remaining actors) ────────
    rpt_feed = _load_json(_REPORTS_DIR / "globe_feed.json")
    if isinstance(rpt_feed, dict):
        for it in rpt_feed.get("items", []):
            name = it.get("actor_name", "")
            gid  = it.get("globe_id", "")
            ts   = it.get("created_at", "")
            if not name:
                continue
            acc = _acc(name, "")
            if gid:
                acc.globe_ids.add(gid)
            acc.touch_ts(ts)

    # ── Finalise ──────────────────────────────────────────────────────────────
    # Sort: by total_activity_count desc, then member_id asc
    member_list = [
        acc.to_dict(mid)
        for mid, acc in sorted(accumulators.items())
    ]
    member_list.sort(key=lambda m: (-m["total_activity_count"], m["member_id"]))

    # Globe distribution
    globe_counts: dict[str, int] = {}
    type_counts:  dict[str, int] = {}
    for m in member_list:
        for gid in m["globe_ids"]:
            globe_counts[gid] = globe_counts.get(gid, 0) + 1
        for at in m["actor_types"]:
            type_counts[at] = type_counts.get(at, 0) + 1

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    return {
        "report_id":    "member-profiles",
        "generated_at": now,
        "phase":        "38",
        "member_count": len(member_list),
        "globe_counts": globe_counts,
        "actor_type_counts": type_counts,
        "phase_phrases": PROFILE_PHRASES,
        **PROFILE_INVARIANTS,
        "members": member_list,
    }


# ─── Filtered views ───────────────────────────────────────────────────────────

def filter_by_globe(report: dict, globe_id: str) -> list[dict]:
    return [m for m in report.get("members", []) if globe_id in m.get("globe_ids", [])]


def filter_by_member(report: dict, member_id: str) -> dict | None:
    for m in report.get("members", []):
        if m["member_id"] == member_id:
            return m
    return None


# ─── Persistence ─────────────────────────────────────────────────────────────

def _build_markdown(report: dict) -> str:
    lines: list[str] = []
    lines.append("# Globe Member Profiles (Phase 38)")
    lines.append("")
    lines.append(f"generated_at: {report['generated_at']}")
    lines.append(f"member_count: {report['member_count']}")
    lines.append("")
    lines.append("## Invariants")
    lines.append("")
    lines.append("| Key | Value |")
    lines.append("|-----|-------|")
    for k, v in PROFILE_INVARIANTS.items():
        lines.append(f"| `{k}` | `{v}` |")
    lines.append("")
    lines.append(
        "> Member profile is advisory display only. "
        "It is not identity verification, not a reputation score, "
        "and creates no authority. Does not rank participants. "
        "Human review is required before any real-world action."
    )
    lines.append("")
    lines.append("## Actor Type Counts")
    lines.append("")
    lines.append("| actor_type | count |")
    lines.append("|------------|-------|")
    for at, n in sorted(report.get("actor_type_counts", {}).items()):
        lines.append(f"| `{at}` | {n} |")
    lines.append("")
    lines.append("## Members")
    lines.append("")
    for m in report.get("members", []):
        lines.append(f"### {m['member_id']}")
        lines.append(f"**display_name:** {m['display_name']}  ")
        lines.append(f"**actor_types:** {', '.join(m['actor_types'])}  ")
        lines.append(f"**globe_ids:** {', '.join(m['globe_ids']) or '—'}  ")
        lines.append(f"**latest_activity_at:** {m['latest_activity_at']}")
        lines.append("")
        lines.append("| metric | count |")
        lines.append("|--------|-------|")
        for field in (
            "total_activity_count", "proposal_count", "deliberation_count",
            "execution_log_count", "human_approval_count", "observation_count",
            "feedback_count", "objection_count", "rollback_request_count",
            "voluntary_resolution_signal_count", "execution_attempt_count",
        ):
            if m.get(field, 0):
                lines.append(f"| `{field}` | {m[field]} |")
        lines.append(f"source_paths: {', '.join(m['source_paths'][:3])}")
        lines.append("")
    for phrase in PROFILE_PHRASES:
        lines.append(f'> "{phrase}"')
    return "\n".join(lines)


def save_profiles() -> tuple[Path, Path]:
    report = build_profiles()
    _REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    _PROFILES_JSON.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _PROFILES_MD.write_text(_build_markdown(report), encoding="utf-8")
    return _PROFILES_JSON, _PROFILES_MD


def load_profiles() -> dict:
    if _PROFILES_JSON.exists():
        try:
            raw = json.loads(_PROFILES_JSON.read_text(encoding="utf-8"))
            if isinstance(raw, dict) and "members" in raw:
                return raw
        except Exception:
            pass
    return build_profiles()


# ─── CLI print helpers ────────────────────────────────────────────────────────

_TYPE_ICON = {"human": "👤", "ai": "🤖", "system": "⚙️"}

_COUNT_FIELDS = [
    ("proposal",    "proposal_count"),
    ("deliberation","deliberation_count"),
    ("exec_log",    "execution_log_count"),
    ("approval",    "human_approval_count"),
    ("observation", "observation_count"),
    ("feedback",    "feedback_count"),
    ("objection",   "objection_count"),
    ("rollback",    "rollback_request_count"),
    ("vrs",         "voluntary_resolution_signal_count"),
    ("exec_attempt","execution_attempt_count"),
]


def _print_member(m: dict, indent: str = "  ") -> None:
    icons = " ".join(_TYPE_ICON.get(at, "?") for at in m.get("actor_types", []))
    gids  = ", ".join(m.get("globe_ids", [])) or "—"
    print(f"{indent}{icons} {m['member_id']}")
    print(f"{indent}   display_name: {m['display_name']}")
    print(f"{indent}   globe_ids:    {gids}")
    print(f"{indent}   latest:       {m.get('latest_activity_at','')}")
    counts = [(lbl, m.get(fld, 0)) for lbl, fld in _COUNT_FIELDS if m.get(fld, 0)]
    if counts:
        print(f"{indent}   counts: " +
              "  ".join(f"{lbl}:{n}" for lbl, n in counts))
    print()


def print_profiles_summary(report: dict) -> None:
    print(f"\nGlobe Member Profiles (Phase 38)")
    print("=" * 60)
    print(f"  generated_at:  {report.get('generated_at','')}")
    print(f"  member_count:  {report.get('member_count', 0)}")
    print()
    print("  Actor type counts:")
    for at, n in sorted(report.get("actor_type_counts", {}).items()):
        icon = _TYPE_ICON.get(at, "?")
        print(f"    {icon} {at:10s}: {n}")
    print()
    print("  Globe distribution:")
    for gid, n in sorted(report.get("globe_counts", {}).items()):
        print(f"    {gid:20s}: {n} members")
    print()
    print("  Members (sorted by total activity):")
    for m in report.get("members", []):
        _print_member(m)
    for phrase in PROFILE_PHRASES:
        print(f'  "{phrase}"')


def print_member_list(members: list[dict], label: str) -> None:
    print(f"\nGlobe Member Profiles — {label}")
    print("=" * 60)
    print(f"  {len(members)} member(s)")
    print()
    for m in members:
        _print_member(m)
    for phrase in PROFILE_PHRASES:
        print(f'  "{phrase}"')


# ─── CLI entry point ──────────────────────────────────────────────────────────

def main(argv: list[str]) -> None:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return

    cmd = argv[0]

    if cmd == "summary":
        report = build_profiles()
        print_profiles_summary(report)
        return

    if cmd == "save":
        report = build_profiles()
        print_profiles_summary(report)
        jp, mp = save_profiles()
        print(f"Saved: {jp}")
        print(f"Saved: {mp}")
        return

    if cmd == "show-member":
        if len(argv) < 2:
            print("Usage: member_profile.py show-member <member_id>", file=sys.stderr)
            sys.exit(1)
        report = load_profiles()
        m = filter_by_member(report, argv[1])
        if not m:
            print(f"No profile found: {argv[1]}", file=sys.stderr)
            print("Known members:", ", ".join(
                x["member_id"] for x in report.get("members", [])
            ), file=sys.stderr)
            sys.exit(1)
        print_member_list([m], f"member={argv[1]}")
        return

    if cmd == "show-globe":
        if len(argv) < 2:
            print("Usage: member_profile.py show-globe <globe_id>", file=sys.stderr)
            sys.exit(1)
        report = load_profiles()
        members = filter_by_globe(report, argv[1])
        if not members:
            print(f"No members found for globe: {argv[1]}", file=sys.stderr)
            sys.exit(1)
        print_member_list(members, f"globe={argv[1]}")
        return

    print(f"Unknown command: {cmd}", file=sys.stderr)
    print("Commands: summary | save | show-member <id> | show-globe <id>",
          file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
