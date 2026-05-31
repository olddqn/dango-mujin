#!/usr/bin/env python3
"""
execution_log_summary.py — Cross-Globe Execution Log Summary (Phase 26)
Dan-Go × GITSEA — Globe Execution Layer

Reads all Directive Execution Log files (globe/logs/*.jsonl) and generates
an advisory cross-globe / cross-directive summary dashboard.

Summary is advisory only.
Summary is not proof of execution.
Summary creates no legal authority.
Summary does not rank or punish participants.
Summary preserves objections and rollback requests.

authority: none · advisory · append-only source · non-coercive

Usage:
    python3 globe/runtime/execution_log_summary.py summary
    python3 globe/runtime/execution_log_summary.py save
    python3 globe/runtime/execution_log_summary.py show-globe <globe_id>
    python3 globe/runtime/execution_log_summary.py show-directive <directive_id>
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_GLOBE_DIR = Path(__file__).resolve().parents[1]
_DATA_DIR = _GLOBE_DIR / "data"
_LOGS_DIR = _GLOBE_DIR / "logs"
_DIRECTIVES_DIR = _GLOBE_DIR / "directives"
_REPORTS_DIR = _GLOBE_DIR / "reports"

# ─── Phase 26 invariants ────────────────────────────────────────────────────────

SUMMARY_INVARIANTS = {
    "summary_is_advisory_only": True,
    "summary_is_not_proof_of_execution": True,
    "summary_creates_no_legal_authority": True,
    "summary_does_not_rank_participants": True,
    "summary_preserves_objections": True,
    "authority": "none",
}

PHASE_PHRASES = [
    "Summary is advisory only.",
    "Summary is not proof of execution.",
    "Summary creates no legal authority.",
    "Summary does not rank or punish participants.",
    "Summary must preserve objections and rollback requests.",
]

# Entry types tracked
ENTRY_TYPES = [
    "human_approval",
    "execution_attempt",
    "observation",
    "feedback",
    "objection",
    "rollback_request",
    "voluntary_resolution_signal",   # Phase 29
]

ENTRY_ICON = {
    "human_approval":              "✅",
    "execution_attempt":           "▶️",
    "observation":                 "👁️",
    "feedback":                    "💬",
    "objection":                   "⚠️",
    "rollback_request":            "↩️",
    "voluntary_resolution_signal": "🏳️",   # Phase 29
}

# Phase 29 — resolution statuses
RESOLUTION_STATUSES = [
    "resolved",
    "partially_resolved",
    "paused",
    "unresolved",
    "contested",
]

RESOLUTION_STATUS_ICON = {
    "resolved":           "✅",
    "partially_resolved": "🟡",
    "paused":             "⏸️",
    "unresolved":         "🔴",
    "contested":          "⚔️",
}


# ─── IO helpers ─────────────────────────────────────────────────────────────────

def _load_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _load_globes() -> list:
    d = _load_json(_DATA_DIR / "globes.json")
    return d if isinstance(d, list) else []


def _globe_name(globe_id: str, globes: list) -> str:
    for g in globes:
        if g.get("globe_id") == globe_id:
            return g.get("name", globe_id)
    return globe_id


def _load_all_entries() -> dict[str, list]:
    """Return {directive_id: [entry, ...]} for every JSONL file in logs/."""
    result: dict[str, list] = {}
    if not _LOGS_DIR.exists():
        return result
    for p in sorted(_LOGS_DIR.glob("*.jsonl")):
        directive_id = p.stem
        entries = []
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except Exception:
                    pass
        if entries:
            result[directive_id] = entries
    return result


def _load_directive_meta(directive_id: str) -> dict:
    """Load title and globe_id from the directive JSON."""
    p = _DIRECTIVES_DIR / f"{directive_id}.json"
    d = _load_json(p)
    if not d:
        return {"title": directive_id, "globe_id": "unknown"}
    return {"title": d.get("title", directive_id), "globe_id": d.get("globe_id", "unknown")}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─── Core aggregation ───────────────────────────────────────────────────────────

def _summarize_directive(directive_id: str, entries: list, meta: dict, globe_name: str) -> dict:
    """Build a per-directive summary record."""
    counts = {et: 0 for et in ENTRY_TYPES}
    for e in entries:
        et = e.get("entry_type", "")
        if et in counts:
            counts[et] += 1

    has_approval = counts["human_approval"] > 0
    last = entries[-1] if entries else {}

    # Phase 29 — aggregate resolution signal counts
    rs_counts = {rs: 0 for rs in RESOLUTION_STATUSES}
    latest_resolution_status = ""
    for e in entries:
        if e.get("entry_type") == "voluntary_resolution_signal":
            rs = e.get("resolution_status", "")
            if rs in rs_counts:
                rs_counts[rs] += 1
                latest_resolution_status = rs

    return {
        "directive_id": directive_id,
        "globe_id": meta["globe_id"],
        "globe_name": globe_name,
        "title": meta["title"],
        "total_entries": len(entries),
        "human_approval_count": counts["human_approval"],
        "execution_attempt_count": counts["execution_attempt"],
        "observation_count": counts["observation"],
        "feedback_count": counts["feedback"],
        "objection_count": counts["objection"],
        "rollback_request_count": counts["rollback_request"],
        # Phase 29
        "resolution_signal_count": counts["voluntary_resolution_signal"],
        "resolved_count":           rs_counts["resolved"],
        "partially_resolved_count": rs_counts["partially_resolved"],
        "paused_count":             rs_counts["paused"],
        "unresolved_count":         rs_counts["unresolved"],
        "contested_count":          rs_counts["contested"],
        "latest_resolution_status": latest_resolution_status,
        "has_human_approval": has_approval,
        "last_entry_type": last.get("entry_type", ""),
        "last_entry_at": last.get("created_at", ""),
        # Invariants sourced from entries (all must be false)
        "all_entries_legal_authority_created_false": all(
            e.get("legal_authority_created") is False for e in entries
        ),
        "all_entries_log_is_proof_of_execution_false": all(
            e.get("log_is_proof_of_execution") is False for e in entries
        ),
    }


def _aggregate_by_globe(directives: list, globes: list) -> list:
    """Aggregate directive summaries into per-globe totals."""
    by_globe: dict[str, dict] = {}
    for d in directives:
        gid = d["globe_id"]
        if gid not in by_globe:
            by_globe[gid] = {
                "globe_id": gid,
                "globe_name": _globe_name(gid, globes),
                "directive_count": 0,
                "total_entries": 0,
                "human_approval_count": 0,
                "execution_attempt_count": 0,
                "observation_count": 0,
                "feedback_count": 0,
                "objection_count": 0,
                "rollback_request_count": 0,
                # Phase 29
                "resolution_signal_count": 0,
                "resolved_count": 0,
                "partially_resolved_count": 0,
                "paused_count": 0,
                "unresolved_count": 0,
                "contested_count": 0,
                "has_any_approval": False,
                "directive_ids": [],
            }
        rec = by_globe[gid]
        rec["directive_count"] += 1
        rec["total_entries"] += d["total_entries"]
        rec["human_approval_count"] += d["human_approval_count"]
        rec["execution_attempt_count"] += d["execution_attempt_count"]
        rec["observation_count"] += d["observation_count"]
        rec["feedback_count"] += d["feedback_count"]
        rec["objection_count"] += d["objection_count"]
        rec["rollback_request_count"] += d["rollback_request_count"]
        # Phase 29
        rec["resolution_signal_count"] += d["resolution_signal_count"]
        rec["resolved_count"]           += d["resolved_count"]
        rec["partially_resolved_count"] += d["partially_resolved_count"]
        rec["paused_count"]             += d["paused_count"]
        rec["unresolved_count"]         += d["unresolved_count"]
        rec["contested_count"]          += d["contested_count"]
        rec["has_any_approval"] = rec["has_any_approval"] or d["has_human_approval"]
        rec["directive_ids"].append(d["directive_id"])
    # Return in globe_id order
    return list(by_globe.values())


def build_summary() -> dict:
    """Build the full cross-globe execution log summary."""
    globes = _load_globes()
    all_entries = _load_all_entries()

    directives = []
    for directive_id, entries in all_entries.items():
        meta = _load_directive_meta(directive_id)
        gname = _globe_name(meta["globe_id"], globes)
        directives.append(_summarize_directive(directive_id, entries, meta, gname))

    # Sort by globe_id then directive_id for stable output
    directives.sort(key=lambda d: (d["globe_id"], d["directive_id"]))

    by_globe = _aggregate_by_globe(directives, globes)

    total_entries = sum(d["total_entries"] for d in directives)

    return {
        "summary_id": "execution-log-summary-001",
        **SUMMARY_INVARIANTS,
        "phase": "26+29",
        "generated_at": _now(),
        "total_directives_with_logs": len(directives),
        "total_log_entries": total_entries,
        "total_objections": sum(d["objection_count"] for d in directives),
        "total_rollback_requests": sum(d["rollback_request_count"] for d in directives),
        # Phase 29
        "total_resolution_signals":        sum(d["resolution_signal_count"] for d in directives),
        "total_resolved":                  sum(d["resolved_count"] for d in directives),
        "total_partially_resolved":        sum(d["partially_resolved_count"] for d in directives),
        "total_paused":                    sum(d["paused_count"] for d in directives),
        "total_unresolved":                sum(d["unresolved_count"] for d in directives),
        "total_contested":                 sum(d["contested_count"] for d in directives),
        "directives": directives,
        "by_globe": by_globe,
        "phase_phrases": PHASE_PHRASES,
    }


# ─── Formatting ─────────────────────────────────────────────────────────────────

def _fmt_bool(v: bool) -> str:
    return "true" if v else "false"


def _fmt_date(ts: str) -> str:
    return ts[:19].replace("T", " ") if ts else "—"


def print_summary(report: dict) -> None:
    """Print the summary to stdout."""
    print("Cross-Globe Execution Log Summary (Phase 26)")
    print("=" * 60)
    print(f"  generated_at:               {_fmt_date(report.get('generated_at', ''))}")
    print(f"  total_directives_with_logs: {report.get('total_directives_with_logs', 0)}")
    print(f"  total_log_entries:          {report.get('total_log_entries', 0)}")
    print(f"  total_objections:           {report.get('total_objections', 0)}")
    print(f"  total_rollback_requests:    {report.get('total_rollback_requests', 0)}")
    # Phase 29
    if report.get("total_resolution_signals", 0):
        print(f"  🏳️  resolution_signals:       {report.get('total_resolution_signals', 0)}")
        print(f"    ✅ resolved:          {report.get('total_resolved', 0)}")
        print(f"    🟡 partially_resolved:{report.get('total_partially_resolved', 0)}")
        print(f"    ⏸️  paused:            {report.get('total_paused', 0)}")
        print(f"    🔴 unresolved:        {report.get('total_unresolved', 0)}")
        print(f"    ⚔️  contested:         {report.get('total_contested', 0)}")
        print("  [self-reported only · not proof of resolution · does not close support]")
    print()
    print("  Invariants:")
    for k, v in SUMMARY_INVARIANTS.items():
        if k != "authority":
            print(f"    {k}: {_fmt_bool(v) if isinstance(v, bool) else v}")
    print(f"    authority: {report.get('authority', 'none')}")
    print()

    print("By Globe:")
    print("-" * 60)
    by_globe = report.get("by_globe", [])
    if not by_globe:
        print("  (no logs recorded yet)")
    for g in by_globe:
        print(f"  {g['globe_id']}  {g['globe_name']}")
        print(f"    directives: {g['directive_count']}  entries: {g['total_entries']}")
        print(f"    ✅ approvals:   {g['human_approval_count']}")
        print(f"    ⚠️  objections:  {g['objection_count']}")
        print(f"    ↩️  rollbacks:   {g['rollback_request_count']}")
        print(f"    ▶️  attempts:    {g['execution_attempt_count']}")
        print(f"    👁️  observations: {g['observation_count']}")
        print(f"    has_any_approval: {_fmt_bool(g['has_any_approval'])}")
        print()

    print("By Directive:")
    print("-" * 60)
    directives = report.get("directives", [])
    if not directives:
        print("  (no logs recorded yet)")
    for d in directives:
        icon = "✅" if d["has_human_approval"] else "⬜"
        print(f"  {icon} {d['directive_id']}")
        print(f"     globe: {d['globe_id']}  entries: {d['total_entries']}")
        print(f"     approvals={d['human_approval_count']}  "
              f"objections={d['objection_count']}  "
              f"rollbacks={d['rollback_request_count']}  "
              f"attempts={d['execution_attempt_count']}  "
              f"observations={d['observation_count']}")
        # Phase 29
        if d.get("resolution_signal_count", 0):
            lrs = d.get("latest_resolution_status", "")
            rs_icons = {"resolved":"✅","partially_resolved":"🟡","paused":"⏸️",
                        "unresolved":"🔴","contested":"⚔️"}
            print(f"     🏳️  signals={d['resolution_signal_count']}  "
                  f"latest: {rs_icons.get(lrs,'•')} {lrs}  (self-reported · not proof)")
        print(f"     last: {ENTRY_ICON.get(d['last_entry_type'], '•')} {d['last_entry_type']}  "
              f"({_fmt_date(d['last_entry_at'])})")
        print()


def print_globe(report: dict, globe_id: str) -> None:
    """Print summary for a single globe."""
    by_globe = report.get("by_globe", [])
    rec = next((g for g in by_globe if g["globe_id"] == globe_id), None)
    if not rec:
        print(f"Globe '{globe_id}' has no execution log entries.")
        return

    print(f"Globe Execution Summary: {globe_id}  ({rec['globe_name']})")
    print("=" * 60)
    print(f"  directives_with_logs:  {rec['directive_count']}")
    print(f"  total_entries:         {rec['total_entries']}")
    print(f"  human_approvals:       {rec['human_approval_count']}")
    print(f"  execution_attempts:    {rec['execution_attempt_count']}")
    print(f"  observations:          {rec['observation_count']}")
    print(f"  feedback:              {rec['feedback_count']}")
    print(f"  objections:            {rec['objection_count']}")
    print(f"  rollback_requests:     {rec['rollback_request_count']}")
    print(f"  has_any_approval:      {_fmt_bool(rec['has_any_approval'])}")
    # Phase 29
    if rec.get("resolution_signal_count", 0):
        print(f"  🏳️  resolution_signals: {rec['resolution_signal_count']}")
        print(f"    ✅ resolved={rec.get('resolved_count',0)}  "
              f"🟡 partial={rec.get('partially_resolved_count',0)}  "
              f"⏸️  paused={rec.get('paused_count',0)}  "
              f"🔴 unresolved={rec.get('unresolved_count',0)}  "
              f"⚔️  contested={rec.get('contested_count',0)}")
        print("    [self-reported only · not proof of resolution]")
    print()
    print("  Directives in this Globe:")
    for did in rec.get("directive_ids", []):
        d = next((x for x in report.get("directives", [])
                  if x["directive_id"] == did), None)
        if d:
            icon = "✅" if d["has_human_approval"] else "⬜"
            print(f"    {icon} {did}  (entries: {d['total_entries']})")
    print()
    print("  advisory: none of these counts certify execution or create authority.")


def print_directive(report: dict, directive_id: str) -> None:
    """Print summary for a single directive."""
    directives = report.get("directives", [])
    d = next((x for x in directives if x["directive_id"] == directive_id), None)
    if not d:
        print(f"Directive '{directive_id}' has no execution log entries.")
        return

    print(f"Directive Execution Summary: {directive_id}")
    print("=" * 60)
    print(f"  globe:                 {d['globe_id']}  ({d['globe_name']})")
    print(f"  title:                 {d['title']}")
    print(f"  total_entries:         {d['total_entries']}")
    print(f"  has_human_approval:    {_fmt_bool(d['has_human_approval'])}")
    print(f"  human_approvals:       {d['human_approval_count']}")
    print(f"  execution_attempts:    {d['execution_attempt_count']}")
    print(f"  observations:          {d['observation_count']}")
    print(f"  feedback:              {d['feedback_count']}")
    print(f"  objections:            {d['objection_count']}")
    print(f"  rollback_requests:     {d['rollback_request_count']}")
    # Phase 29
    if d.get("resolution_signal_count", 0):
        print(f"  🏳️  resolution_signals: {d['resolution_signal_count']}")
        print(f"    ✅ resolved={d.get('resolved_count',0)}  "
              f"🟡 partial={d.get('partially_resolved_count',0)}  "
              f"⏸️  paused={d.get('paused_count',0)}  "
              f"🔴 unresolved={d.get('unresolved_count',0)}  "
              f"⚔️  contested={d.get('contested_count',0)}")
        lrs = d.get("latest_resolution_status", "")
        if lrs:
            rs_icons = {"resolved":"✅","partially_resolved":"🟡","paused":"⏸️",
                        "unresolved":"🔴","contested":"⚔️"}
            print(f"    latest: {rs_icons.get(lrs,'•')} {lrs}  (self-reported · not proof)")
        print("    [Resolution signal does not close support automatically]")
    print(f"  last_entry_type:       {d['last_entry_type']}")
    print(f"  last_entry_at:         {_fmt_date(d['last_entry_at'])}")
    print()
    print(f"  Invariants (sourced from JSONL):")
    print(f"    all legal_authority_created = false: "
          f"{_fmt_bool(d['all_entries_legal_authority_created_false'])}")
    print(f"    all log_is_proof_of_execution = false: "
          f"{_fmt_bool(d['all_entries_log_is_proof_of_execution_false'])}")
    print()
    print("  advisory: this count is not proof of execution and creates no authority.")


# ─── Markdown renderer ──────────────────────────────────────────────────────────

def _build_markdown(report: dict) -> str:
    lines = []
    gen = _fmt_date(report.get("generated_at", ""))
    nd = report.get("total_directives_with_logs", 0)
    ne = report.get("total_log_entries", 0)
    nobj = report.get("total_objections", 0)
    nrb = report.get("total_rollback_requests", 0)

    lines.append("# Execution Log Cross-Globe Summary (Phase 26)")
    lines.append("")
    lines.append("> **Summary is advisory only.**")
    lines.append("> Summary is not proof of execution.")
    lines.append("> Summary creates no legal authority.")
    lines.append("> Summary does not rank or punish participants.")
    lines.append("> Summary preserves objections and rollback requests.")
    lines.append("")
    lines.append(f"**Generated:** {gen}  ")
    lines.append(f"**authority:** none  ")
    lines.append(f"**phase:** 26")
    lines.append("")
    lines.append("## Totals")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| Directives with logs | {nd} |")
    lines.append(f"| Total log entries | {ne} |")
    lines.append(f"| Total objections | {nobj} |")
    lines.append(f"| Total rollback requests | {nrb} |")
    # Phase 29
    n_sig = report.get("total_resolution_signals", 0)
    if n_sig:
        lines.append(f"| 🏳️ Resolution signals (self-reported · not proof) | {n_sig} |")
        lines.append(f"| &nbsp;&nbsp;✅ resolved | {report.get('total_resolved', 0)} |")
        lines.append(f"| &nbsp;&nbsp;🟡 partially_resolved | {report.get('total_partially_resolved', 0)} |")
        lines.append(f"| &nbsp;&nbsp;⏸️ paused | {report.get('total_paused', 0)} |")
        lines.append(f"| &nbsp;&nbsp;🔴 unresolved | {report.get('total_unresolved', 0)} |")
        lines.append(f"| &nbsp;&nbsp;⚔️ contested | {report.get('total_contested', 0)} |")
    lines.append("")

    lines.append("## By Globe")
    lines.append("")
    by_globe = report.get("by_globe", [])
    if not by_globe:
        lines.append("*No execution logs recorded yet.*")
    else:
        lines.append("| Globe | Directives | Entries | ✅ Approvals | ⚠️ Objections | ↩️ Rollbacks | ▶️ Attempts |")
        lines.append("|-------|------------|---------|-------------|--------------|-------------|------------|")
        for g in by_globe:
            appr = "✅" if g["has_any_approval"] else "⬜"
            lines.append(
                f"| {g['globe_id']} ({g['globe_name']}) "
                f"| {g['directive_count']} "
                f"| {g['total_entries']} "
                f"| {appr} {g['human_approval_count']} "
                f"| {g['objection_count']} "
                f"| {g['rollback_request_count']} "
                f"| {g['execution_attempt_count']} |"
            )
    lines.append("")

    lines.append("## By Directive")
    lines.append("")
    directives = report.get("directives", [])
    if not directives:
        lines.append("*No execution logs recorded yet.*")
    else:
        lines.append("| Directive | Globe | Entries | Approval | Objections | Rollbacks | 🏳️ Signal (self-reported) | Last Entry |")
        lines.append("|-----------|-------|---------|----------|------------|-----------|--------------------------|------------|")
        rs_icons = {"resolved":"✅","partially_resolved":"🟡","paused":"⏸️",
                    "unresolved":"🔴","contested":"⚔️"}
        for d in directives:
            icon = "✅" if d["has_human_approval"] else "⬜"
            last = f"{ENTRY_ICON.get(d['last_entry_type'],'•')} {d['last_entry_type']}"
            lrs = d.get("latest_resolution_status", "")
            sig_cell = (
                f"{rs_icons.get(lrs,'•')} {lrs} ({d.get('resolution_signal_count',0)})"
                if d.get("resolution_signal_count", 0) else "—"
            )
            lines.append(
                f"| {d['directive_id']} "
                f"| {d['globe_id']} "
                f"| {d['total_entries']} "
                f"| {icon} {d['human_approval_count']} "
                f"| {d['objection_count']} "
                f"| {d['rollback_request_count']} "
                f"| {sig_cell} "
                f"| {last} |"
            )
    lines.append("")

    lines.append("## Invariants")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|-------|-------|")
    for k, v in SUMMARY_INVARIANTS.items():
        val = str(v).lower() if isinstance(v, bool) else v
        lines.append(f"| `{k}` | `{val}` |")
    lines.append("")

    lines.append("## Phase 26 Protocol Phrases")
    lines.append("")
    for phrase in PHASE_PHRASES:
        lines.append(f"- *{phrase}*")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Dan-Go Execution Log Summary · authority: none · advisory · not proof of execution*")

    return "\n".join(lines)


# ─── Save ───────────────────────────────────────────────────────────────────────

def save_report(report: dict) -> None:
    """Save JSON and Markdown reports to globe/reports/."""
    _REPORTS_DIR.mkdir(exist_ok=True)

    json_path = _REPORTS_DIR / "execution_log_summary.json"
    json_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Saved: {json_path}")

    md_path = _REPORTS_DIR / "execution_log_summary.md"
    md_path.write_text(_build_markdown(report), encoding="utf-8")
    print(f"Saved: {md_path}")


# ─── CLI ────────────────────────────────────────────────────────────────────────

def _usage() -> None:
    print(__doc__)
    sys.exit(1)


def main(argv: list[str]) -> None:
    if not argv:
        _usage()

    cmd = argv[0]

    if cmd == "summary":
        report = build_summary()
        print_summary(report)

    elif cmd == "save":
        report = build_summary()
        print_summary(report)
        save_report(report)

    elif cmd == "show-globe":
        if len(argv) < 2:
            print("Usage: execution_log_summary.py show-globe <globe_id>")
            sys.exit(1)
        report = build_summary()
        print_globe(report, argv[1])

    elif cmd == "show-directive":
        if len(argv) < 2:
            print("Usage: execution_log_summary.py show-directive <directive_id>")
            sys.exit(1)
        report = build_summary()
        print_directive(report, argv[1])

    else:
        print(f"Unknown command: {cmd}")
        _usage()


if __name__ == "__main__":
    main(sys.argv[1:])
