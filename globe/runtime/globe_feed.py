"""globe_feed.py — Phase 36: Globe Feed / Changelog

Aggregates all Globe-layer activities into an append-only-style advisory feed,
sorted by created_at descending (most recent first). The feed is a browsing
aid — it is not proof of execution, proof of impact, or a ranking of
participants.

INVARIANTS (permanent, not negotiable):
  Feed is advisory display only.
  Feed is not proof of execution.
  Feed is not proof of impact.
  Feed does not rank participants.
  Feed does not allocate resources.
  Human review is required before any real-world action.
  authority: none

Data sources (read-only):
  globe/data/proposals.json
  globe/claims/*.json
  globe/directives/*.json
  globe/logs/*.jsonl                      → source_type: execution_log
  globe/reports/reality_feedback_bridge.json → source_type: reality_feedback
  globe/reports/bridge_target_links.json     → source_type: bridge_target_link
  globe/reports/contribution_timeline.json   → source_type: timeline (report item)
  globe/reports/activity_heatmap.json        → source_type: activity_heatmap (report item)
  globe/reports/directive_checklists.json    → source_type: directive_checklist (per directive)

CLI:
  python3 globe/runtime/globe_feed.py summary
  python3 globe/runtime/globe_feed.py save
  python3 globe/runtime/globe_feed.py show-globe <globe_id>
  python3 globe/runtime/globe_feed.py show-type <source_type>
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────

_GLOBE_DIR      = Path(__file__).resolve().parents[1]
_DATA_DIR       = _GLOBE_DIR / "data"
_CLAIMS_DIR     = _GLOBE_DIR / "claims"
_DIRECTIVES_DIR = _GLOBE_DIR / "directives"
_LOGS_DIR       = _GLOBE_DIR / "logs"
_REPORTS_DIR    = _GLOBE_DIR / "reports"

_FEED_JSON = _REPORTS_DIR / "globe_feed.json"
_FEED_MD   = _REPORTS_DIR / "globe_feed.md"

# ─── Invariants ───────────────────────────────────────────────────────────────

FEED_INVARIANTS = {
    "feed_is_advisory_display_only": True,
    "feed_is_not_proof_of_execution": True,
    "feed_is_not_proof_of_impact": True,
    "feed_does_not_rank_participants": True,
    "feed_does_not_allocate_resources": True,
    "human_review_is_required_before_any_real_world_action": True,
    "authority": "none",
}

FEED_PHRASES = [
    "Feed is advisory display only.",
    "Feed is not proof of execution.",
    "Feed is not proof of impact.",
    "Feed does not rank participants.",
    "Feed does not allocate resources.",
    "Human review is required before any real-world action.",
]

VALID_SOURCE_TYPES = frozenset({
    "proposal", "claim", "directive", "execution_log",
    "reality_feedback", "bridge_target_link",
    "timeline", "activity_heatmap", "directive_checklist",
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


def _ts(s: str) -> str:
    """Normalise any ISO timestamp to a sortable 19-char string."""
    return str(s)[:19].replace("T", " ") if s else ""


def _excerpt(text: str, max_len: int = 120) -> str:
    if not text:
        return ""
    text = text.replace("\n", " ").strip()
    return text[:max_len] + ("…" if len(text) > max_len else "")


def _make_item(
    *,
    feed_id: str,
    globe_id: str,
    source_type: str,
    source_id: str,
    title: str,
    content_excerpt: str,
    created_at: str,
    source_path: str,
    url_path: str = "",
    tags: list[str] | None = None,
    extra: dict | None = None,
) -> dict:
    return {
        "feed_id":        feed_id,
        "globe_id":       globe_id,
        "source_type":    source_type,
        "source_id":      source_id,
        "title":          title,
        "content_excerpt": content_excerpt,
        "created_at":     created_at,
        "source_path":    source_path,
        "url_path":       url_path,
        "tags":           tags or [],
        **(extra or {}),
        "advisory_only":          True,
        "not_proof_of_execution": True,
    }


# ─── Indexers per source_type ─────────────────────────────────────────────────

def _index_proposals() -> list[dict]:
    raw = _load_json(_DATA_DIR / "proposals.json")
    if not isinstance(raw, list):
        return []
    items = []
    for p in raw:
        pid   = p.get("proposal_id", "")
        gid   = p.get("globe_id", "")
        ts    = _ts(p.get("created_at", ""))
        items.append(_make_item(
            feed_id       = f"feed-proposal-{pid}",
            globe_id      = gid,
            source_type   = "proposal",
            source_id     = pid,
            title         = f"Proposal: {p.get('title', pid)}",
            content_excerpt = _excerpt(p.get("body", "")),
            created_at    = ts,
            source_path   = "globe/data/proposals.json",
            url_path      = f"/globe/{gid}/proposals/{pid}" if gid else "",
            tags          = [p.get("status", ""), gid],
            extra         = {"status": p.get("status", ""), "proposer": p.get("proposer", "")},
        ))
    return items


def _index_claims() -> list[dict]:
    items = []
    for p in sorted(_CLAIMS_DIR.glob("*.json")):
        c = _load_json(p)
        if not isinstance(c, dict):
            continue
        cid  = c.get("claim_id", p.stem)
        gid  = c.get("globe_id", "")
        pid  = c.get("source_proposal_id", "")
        ts   = _ts(c.get("created_at", ""))
        title_str = c.get("title", c.get("claim_title", cid))
        items.append(_make_item(
            feed_id       = f"feed-claim-{cid}",
            globe_id      = gid,
            source_type   = "claim",
            source_id     = cid,
            title         = f"Claim: {title_str}",
            content_excerpt = _excerpt(c.get("body", c.get("executive_summary", ""))),
            created_at    = ts,
            source_path   = f"globe/claims/{p.name}",
            url_path      = f"/globe/{gid}/proposals/{pid}" if gid and pid else "",
            tags          = [gid, pid],
            extra         = {"source_proposal_id": pid},
        ))
    return items


def _index_directives() -> list[dict]:
    items = []
    for p in sorted(_DIRECTIVES_DIR.glob("*.json")):
        d = _load_json(p)
        if not isinstance(d, dict):
            continue
        did  = d.get("directive_id", p.stem)
        gid  = d.get("globe_id", "")
        ts   = _ts(d.get("created_at", ""))
        steps = len(d.get("execution_steps", []))
        items.append(_make_item(
            feed_id       = f"feed-directive-{did}",
            globe_id      = gid,
            source_type   = "directive",
            source_id     = did,
            title         = f"Directive: {d.get('title', did)}",
            content_excerpt = _excerpt(d.get("objective", "")),
            created_at    = ts,
            source_path   = f"globe/directives/{p.name}",
            url_path      = f"/globe/{gid}/directives/{did}" if gid else "",
            tags          = [gid, f"{steps} steps"],
            extra         = {"step_count": steps,
                             "source_claim_id": d.get("source_claim_id", "")},
        ))
    return items


def _index_execution_logs() -> list[dict]:
    items = []
    for p in sorted(_LOGS_DIR.glob("*.jsonl")):
        directive_id = p.stem
        entries = _load_jsonl(p)
        # Infer globe_id from directive file
        d = _load_json(_DIRECTIVES_DIR / f"{directive_id}.json")
        gid = d.get("globe_id", "") if isinstance(d, dict) else ""
        for e in entries:
            log_id = e.get("log_id", "")
            et     = e.get("entry_type", "unknown")
            actor  = e.get("actor_name", "?")
            ts     = _ts(e.get("created_at", ""))
            items.append(_make_item(
                feed_id       = f"feed-exec-{log_id or directive_id + '-' + et}",
                globe_id      = gid,
                source_type   = "execution_log",
                source_id     = log_id or f"{directive_id}/{et}",
                title         = f"Log: {et.replace('_',' ')} — {actor}",
                content_excerpt = _excerpt(e.get("content", "")),
                created_at    = ts,
                source_path   = f"globe/logs/{p.name}",
                url_path      = f"/globe/{gid}/logs/{directive_id}" if gid else "",
                tags          = [et, gid, directive_id],
                extra         = {"entry_type": et, "actor_name": actor,
                                 "actor_type": e.get("actor_type", ""),
                                 "directive_id": directive_id,
                                 "resolution_status": e.get("resolution_status", "")},
            ))
    return items


def _index_reality_feedback() -> list[dict]:
    rpt = _load_json(_REPORTS_DIR / "reality_feedback_bridge.json")
    if not isinstance(rpt, dict):
        return []
    items = []
    for r in rpt.get("records", []):
        fid  = r.get("feedback_id", "")
        gid  = r.get("globe_id", "")
        did  = r.get("source_directive_id", "")
        et   = r.get("entry_type", "")
        actor= r.get("actor_name", "?")
        # Use source_entry_created_at if available; else report generated_at
        ts   = _ts(r.get("source_entry_created_at", rpt.get("generated_at", "")))
        target = r.get("suggested_bridge_target", "none")
        items.append(_make_item(
            feed_id       = f"feed-rfb-{fid}",
            globe_id      = gid,
            source_type   = "reality_feedback",
            source_id     = fid,
            title         = f"Reality Feedback: {et.replace('_',' ')} → bridge:{target}",
            content_excerpt = _excerpt(r.get("content", r.get("suggested_reason", ""))),
            created_at    = ts,
            source_path   = "globe/reports/reality_feedback_bridge.json",
            url_path      = f"/globe/{gid}/logs/{did}" if gid and did else "",
            tags          = [et, gid, target],
            extra         = {"entry_type": et, "actor_name": actor,
                             "suggested_bridge_target": target,
                             "source_directive_id": did},
        ))
    return items


def _index_bridge_target_links() -> list[dict]:
    rpt = _load_json(_REPORTS_DIR / "bridge_target_links.json")
    if not isinstance(rpt, dict):
        return []
    items = []
    for c in rpt.get("candidates", []):
        lid  = c.get("link_id", "")
        gid  = c.get("globe_id", "")
        did  = c.get("source_directive_id", "")
        conf = c.get("confidence", "low")
        ttype = c.get("candidate_target_type", "none")
        ts   = _ts(c.get("created_at", rpt.get("generated_at", "")))
        items.append(_make_item(
            feed_id       = f"feed-lnk-{lid}",
            globe_id      = gid,
            source_type   = "bridge_target_link",
            source_id     = lid,
            title         = f"Bridge Link: {ttype} (confidence: {conf})",
            content_excerpt = _excerpt(c.get("candidate_description", c.get("match_reason", ""))),
            created_at    = ts,
            source_path   = "globe/reports/bridge_target_links.json",
            url_path      = f"/globe/{gid}/directives/{did}" if gid and did else "",
            tags          = [conf, ttype, gid],
            extra         = {"confidence": conf, "candidate_target_type": ttype,
                             "source_directive_id": did,
                             "source_feedback_id": c.get("source_feedback_id", "")},
        ))
    return items


def _index_timeline() -> list[dict]:
    """One feed item representing the timeline report itself."""
    rpt = _load_json(_REPORTS_DIR / "contribution_timeline.json")
    if not isinstance(rpt, dict):
        return []
    n  = rpt.get("total_items", len(rpt.get("items", [])))
    ts = _ts(rpt.get("generated_at", ""))
    return [_make_item(
        feed_id       = "feed-timeline-report",
        globe_id      = "",
        source_type   = "timeline",
        source_id     = "contribution_timeline",
        title         = f"Contribution Timeline generated — {n} items",
        content_excerpt = (f"date_range: {rpt.get('earliest_date','')} — {rpt.get('latest_date','')}  "
                           f"source_types: {', '.join(rpt.get('source_type_counts',{}).keys())}"),
        created_at    = ts,
        source_path   = "globe/reports/contribution_timeline.json",
        url_path      = "/globe/timeline",
        tags          = ["timeline", str(n) + " items"],
        extra         = {"total_items": n,
                         "source_type_counts": rpt.get("source_type_counts", {})},
    )]


def _index_activity_heatmap() -> list[dict]:
    """One feed item representing the heatmap report itself."""
    rpt = _load_json(_REPORTS_DIR / "activity_heatmap.json")
    if not isinstance(rpt, dict):
        return []
    n  = rpt.get("total_events", 0)
    ts = _ts(rpt.get("generated_at", ""))
    return [_make_item(
        feed_id       = "feed-heatmap-report",
        globe_id      = "",
        source_type   = "activity_heatmap",
        source_id     = "activity_heatmap",
        title         = f"Activity Heatmap generated — {n} events · {rpt.get('date_count',0)} dates",
        content_excerpt = (f"date_range: {rpt.get('earliest_date','')} — {rpt.get('latest_date','')}  "
                           f"attention_events: {rpt.get('attention_events',0)}"),
        created_at    = ts,
        source_path   = "globe/reports/activity_heatmap.json",
        url_path      = "/globe/activity",
        tags          = ["heatmap", str(n) + " events"],
        extra         = {"total_events": n, "date_count": rpt.get("date_count", 0),
                         "attention_events": rpt.get("attention_events", 0)},
    )]


def _index_directive_checklists() -> list[dict]:
    """One feed item per directive checklist."""
    rpt = _load_json(_REPORTS_DIR / "directive_checklists.json")
    if not isinstance(rpt, dict):
        return []
    ts_report = _ts(rpt.get("generated_at", ""))
    items = []
    for d in rpt.get("directives", []):
        did  = d.get("directive_id", "")
        gid  = d.get("globe_id", "")
        n    = d.get("step_count", 0)
        attn = sum(1 for it in d.get("items", []) if it.get("needs_attention"))
        items.append(_make_item(
            feed_id       = f"feed-cl-{did}",
            globe_id      = gid,
            source_type   = "directive_checklist",
            source_id     = f"checklist-{did}",
            title         = f"Checklist: {d.get('title', did)} — {n} steps",
            content_excerpt = (f"log_entries: {d.get('log_entry_count',0)}  "
                               + (f"⚠️ {attn} attention" if attn else "no attention flags")),
            created_at    = ts_report,
            source_path   = "globe/reports/directive_checklists.json",
            url_path      = f"/globe/{gid}/directives/{did}/checklist" if gid else "",
            tags          = [gid, did, f"{n} steps"],
            extra         = {"step_count": n, "needs_attention_count": attn,
                             "directive_id": did},
        ))
    return items


# ─── Main build function ──────────────────────────────────────────────────────

def build_feed() -> dict:
    """Build and return the full Globe feed.

    Advisory only. Not proof of impact or execution.
    Items sorted by created_at descending (most recent first).
    Secondary sort: source_path ascending (stable).
    """
    items: list[dict] = []
    items.extend(_index_proposals())
    items.extend(_index_claims())
    items.extend(_index_directives())
    items.extend(_index_execution_logs())
    items.extend(_index_reality_feedback())
    items.extend(_index_bridge_target_links())
    items.extend(_index_timeline())
    items.extend(_index_activity_heatmap())
    items.extend(_index_directive_checklists())

    # Sort: created_at descending, source_path ascending (stable tiebreaker)
    items.sort(key=lambda x: (x["created_at"], x["source_path"]), reverse=True)
    # Secondary: stable within same timestamp — source_path ascending
    # Python's sort is stable, so we do two passes
    items.sort(key=lambda x: x["source_path"])          # secondary: path asc
    items.sort(key=lambda x: x["created_at"], reverse=True)  # primary: time desc

    # Count by source_type
    type_counts: dict[str, int] = {}
    globe_counts: dict[str, int] = {}
    for it in items:
        st = it["source_type"]
        gid = it["globe_id"]
        type_counts[st] = type_counts.get(st, 0) + 1
        if gid:
            globe_counts[gid] = globe_counts.get(gid, 0) + 1

    return {
        "feed_id":      "globe-feed",
        "generated_at": _now(),
        "total_items":  len(items),
        "source_type_counts": type_counts,
        "globe_counts": globe_counts,
        "phase":        "36",
        "phase_phrases": FEED_PHRASES,
        **FEED_INVARIANTS,
        "items": items,
    }


# ─── Filtered views ───────────────────────────────────────────────────────────

def filter_by_globe(feed: dict, globe_id: str) -> list[dict]:
    return [it for it in feed.get("items", []) if it["globe_id"] == globe_id]


def filter_by_type(feed: dict, source_type: str) -> list[dict]:
    return [it for it in feed.get("items", []) if it["source_type"] == source_type]


# ─── Persistence ─────────────────────────────────────────────────────────────

def _build_markdown(feed: dict) -> str:
    lines: list[str] = []
    lines.append("# Globe Feed / Changelog (Phase 36)")
    lines.append("")
    lines.append(f"generated_at: {feed['generated_at']}")
    lines.append(f"total_items: {feed['total_items']}")
    lines.append("")
    lines.append("## Source Type Counts")
    lines.append("")
    lines.append("| source_type | count |")
    lines.append("|-------------|-------|")
    for st, n in sorted(feed.get("source_type_counts", {}).items()):
        lines.append(f"| `{st}` | {n} |")
    lines.append("")
    lines.append("## Invariants")
    lines.append("")
    lines.append("| Key | Value |")
    lines.append("|-----|-------|")
    for k, v in FEED_INVARIANTS.items():
        lines.append(f"| `{k}` | `{v}` |")
    lines.append("")
    lines.append(
        "> Feed is advisory display only. It is not proof of execution, "
        "impact, or ranking. Human review is required before any real-world action."
    )
    lines.append("")
    lines.append("## Feed Items (created_at desc)")
    lines.append("")
    for it in feed.get("items", []):
        lines.append(f"### {it['feed_id']}")
        lines.append(f"**type:** `{it['source_type']}` &nbsp; "
                     f"**globe:** `{it['globe_id'] or '—'}` &nbsp; "
                     f"**created_at:** `{it['created_at']}`")
        lines.append(f"**title:** {it['title']}")
        if it.get("content_excerpt"):
            lines.append(f"> {it['content_excerpt']}")
        lines.append(f"source: `{it['source_path']}`")
        lines.append("")
    for phrase in FEED_PHRASES:
        lines.append(f'> "{phrase}"')
    return "\n".join(lines)


def save_feed() -> tuple[Path, Path]:
    feed = build_feed()
    _REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    _FEED_JSON.write_text(
        json.dumps(feed, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _FEED_MD.write_text(_build_markdown(feed), encoding="utf-8")
    return _FEED_JSON, _FEED_MD


def load_feed() -> dict:
    if _FEED_JSON.exists():
        try:
            raw = json.loads(_FEED_JSON.read_text(encoding="utf-8"))
            if isinstance(raw, dict) and "items" in raw:
                return raw
        except Exception:
            pass
    return build_feed()


# ─── CLI print helpers ────────────────────────────────────────────────────────

_TYPE_ICON = {
    "proposal":          "📋",
    "claim":             "📌",
    "directive":         "🗂️",
    "execution_log":     "📝",
    "reality_feedback":  "🔗",
    "bridge_target_link":"🔗",
    "timeline":          "⏱",
    "activity_heatmap":  "🗓",
    "directive_checklist":"📋",
}


def _print_item(it: dict, indent: str = "  ") -> None:
    icon = _TYPE_ICON.get(it["source_type"], "•")
    gid  = f"[{it['globe_id']}]" if it.get("globe_id") else ""
    print(f"{indent}{icon} {it['source_type']:20s} {gid:12s} {it['created_at']}")
    print(f"{indent}  {it['title']}")
    if it.get("content_excerpt"):
        print(f"{indent}  {it['content_excerpt'][:90]}")
    print()


def print_feed_summary(feed: dict) -> None:
    print(f"\nGlobe Feed / Changelog (Phase 36)")
    print("=" * 60)
    print(f"  generated_at:  {feed.get('generated_at','')}")
    print(f"  total_items:   {feed.get('total_items',0)}")
    print()
    print("  Source type counts:")
    for st, n in sorted(feed.get("source_type_counts", {}).items()):
        icon = _TYPE_ICON.get(st, "•")
        print(f"    {icon} {st:22s}: {n}")
    print()
    print("  Globe counts:")
    for gid, n in sorted(feed.get("globe_counts", {}).items()):
        print(f"    {gid:20s}: {n}")
    print()
    print("  Recent items (top 10):")
    for it in feed.get("items", [])[:10]:
        _print_item(it)
    for phrase in FEED_PHRASES:
        print(f'  "{phrase}"')


def print_items(items: list[dict], label: str) -> None:
    print(f"\nGlobe Feed — {label}")
    print("=" * 60)
    print(f"  {len(items)} items")
    print()
    for it in items:
        _print_item(it)
    for phrase in FEED_PHRASES:
        print(f'  "{phrase}"')


# ─── CLI entry point ──────────────────────────────────────────────────────────

def main(argv: list[str]) -> None:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return

    cmd = argv[0]

    if cmd == "summary":
        feed = build_feed()
        print_feed_summary(feed)
        return

    if cmd == "save":
        feed = build_feed()
        print_feed_summary(feed)
        jp, mp = save_feed()
        print(f"Saved: {jp}")
        print(f"Saved: {mp}")
        return

    if cmd == "show-globe":
        if len(argv) < 2:
            print("Usage: globe_feed.py show-globe <globe_id>", file=sys.stderr)
            sys.exit(1)
        globe_id = argv[1]
        feed = load_feed()
        items = filter_by_globe(feed, globe_id)
        if not items:
            print(f"No feed items for globe: {globe_id}", file=sys.stderr)
            sys.exit(1)
        print_items(items, f"globe={globe_id}")
        return

    if cmd == "show-type":
        if len(argv) < 2:
            print("Usage: globe_feed.py show-type <source_type>", file=sys.stderr)
            sys.exit(1)
        stype = argv[1]
        if stype not in VALID_SOURCE_TYPES:
            print(f"Unknown source_type: {stype}", file=sys.stderr)
            print(f"Valid types: {', '.join(sorted(VALID_SOURCE_TYPES))}", file=sys.stderr)
            sys.exit(1)
        feed = load_feed()
        items = filter_by_type(feed, stype)
        if not items:
            print(f"No feed items of type: {stype}", file=sys.stderr)
            sys.exit(1)
        print_items(items, f"type={stype}")
        return

    print(f"Unknown command: {cmd}", file=sys.stderr)
    print("Commands: summary | save | show-globe <id> | show-type <type>",
          file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
