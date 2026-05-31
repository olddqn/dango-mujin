#!/usr/bin/env python3
"""
reality_feedback_bridge.py — Reality Feedback Bridge (Phase 27)
Dan-Go × GITSEA — Globe Execution Layer

Reads Directive Execution Log entries (observation / feedback / objection /
rollback_request) and generates advisory bridge records connecting them with
Phase 18 Relief Case Memory and Phase 19 Care Loop Reopen.

Reality feedback is advisory only.
Feedback bridge is not proof of resolution.
Feedback bridge creates no legal authority.
Feedback bridge does not reopen a case automatically.
Human review is required before any real-world action.

authority: none · advisory · append-only source · non-coercive · stdlib only

Usage:
    python3 globe/runtime/reality_feedback_bridge.py summary
    python3 globe/runtime/reality_feedback_bridge.py save
    python3 globe/runtime/reality_feedback_bridge.py show-directive <directive_id>
    python3 globe/runtime/reality_feedback_bridge.py show-globe <globe_id>
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_GLOBE_DIR      = Path(__file__).resolve().parents[1]
_LOGS_DIR       = _GLOBE_DIR / "logs"
_DIRECTIVES_DIR = _GLOBE_DIR / "directives"
_DATA_DIR       = _GLOBE_DIR / "data"
_REPORTS_DIR    = _GLOBE_DIR / "reports"

# ─── Phase 27 invariants ────────────────────────────────────────────────────────

BRIDGE_INVARIANTS = {
    "reality_feedback_is_advisory_only":               True,
    "feedback_bridge_is_not_proof_of_resolution":      True,
    "feedback_bridge_creates_no_legal_authority":      True,
    "feedback_bridge_does_not_reopen_case_automatically": True,
    "human_review_is_required_before_any_real_world_action": True,
    "authority": "none",
}

BRIDGE_PHRASES = [
    "Reality feedback is advisory only.",
    "Feedback bridge is not proof of resolution.",
    "Feedback bridge creates no legal authority.",
    "Feedback bridge does not reopen a case automatically.",
    "Human review is required before any real-world action.",
]

# Entry types that generate bridge records
BRIDGE_ENTRY_TYPES = {"observation", "feedback", "objection", "rollback_request",
                      "voluntary_resolution_signal"}   # Phase 29

# Phase 29 — resolution statuses that route to bridge (unresolved/contested/paused)
# resolved / partially_resolved are excluded from bridging but kept in summary
BRIDGE_RESOLUTION_STATUSES = {"unresolved", "contested", "paused"}

# Keywords triggering Phase 18 Relief Case Memory suggestion
RELIEF_KEYWORDS = [
    "住居", "housing", "tenant", "テナント", "テナンシー", "tenancy",
    "避難", "難民", "refugee", "relief", "shelter", "シェルター",
    "居住", "displacement", "立ち退き", "追い出し", "d.r.a", "dra",
]

# Keywords triggering Phase 19 Care Loop Reopen suggestion
CARE_KEYWORDS = [
    "再開", "reopen", "care", "ケア", "follow-up", "フォローアップ",
    "継続", "continue", "再確認", "follow up", "followup",
    "loop", "ループ", "援助", "支援継続", "care loop",
]

# Bridge target display metadata
_TARGET_ICON = {
    "relief_case_memory": "🏠",
    "care_loop_reopen":   "🔄",
    "both":               "🏠🔄",
    "none":               "—",
}

_TARGET_LABEL = {
    "relief_case_memory": "Phase 18 Relief Case Memory",
    "care_loop_reopen":   "Phase 19 Care Loop Reopen",
    "both":               "Phase 18 + Phase 19",
    "none":               "no bridge match",
}

_ENTRY_ICON = {
    "observation":                 "👁",
    "feedback":                    "💬",
    "objection":                   "⚠",
    "rollback_request":            "↩",
    "voluntary_resolution_signal": "🏳️",   # Phase 29
}


# ─── Data loading ───────────────────────────────────────────────────────────────

def _load_all_entries() -> dict:
    """Read all *.jsonl from globe/logs/. Returns {directive_id: [entries]}."""
    result: dict[str, list] = {}
    for p in sorted(_LOGS_DIR.glob("*.jsonl")):
        directive_id = p.stem
        entries: list = []
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
    """Load directive JSON for title / globe_id etc."""
    p = _DIRECTIVES_DIR / f"{directive_id}.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _load_globe_name(globe_id: str) -> str:
    """Resolve globe_id → globe name from data/globes.json."""
    p = _DATA_DIR / "globes.json"
    if not p.exists():
        return globe_id
    try:
        globes = json.loads(p.read_text(encoding="utf-8"))
        g = next((x for x in globes if x.get("globe_id") == globe_id), None)
        return g["name"] if g else globe_id
    except Exception:
        return globe_id


# ─── Bridge determination ───────────────────────────────────────────────────────

def _determine_bridge_target(entry: dict) -> tuple:
    """
    Returns (suggested_bridge_target, suggested_reason).

    Targets:
      "relief_case_memory"  Phase 18
      "care_loop_reopen"    Phase 19
      "both"                Phase 18 + 19
      "none"                no confident match

    Rules (in priority order):
      1. Phase 29: voluntary_resolution_signal with unresolved/contested/paused
         → care_loop_reopen (and keyword escalation applies on top)
      2. Keyword scan of entry content (applies to all entry types)
      3. objection / rollback_request default to care_loop_reopen if no keyword match
      4. Otherwise: none
    """
    content_lower = entry.get("content", "").lower()
    et = entry.get("entry_type", "")
    rs = entry.get("resolution_status", "")

    has_relief = any(k.lower() in content_lower for k in RELIEF_KEYWORDS)
    has_care   = any(k.lower() in content_lower for k in CARE_KEYWORDS)

    # Phase 29 — voluntary_resolution_signal routing
    if et == "voluntary_resolution_signal":
        if rs not in BRIDGE_RESOLUTION_STATUSES:
            # resolved / partially_resolved → not bridged (kept in summary only)
            return (
                "none",
                f"voluntary_resolution_signal with resolution_status='{rs}' — "
                "resolved/partially_resolved signals are not routed to bridge "
                "(self-reported positive outcomes are advisory only and not escalated)",
            )
        # unresolved / contested / paused → care_loop_reopen, with keyword escalation
        if has_relief and has_care:
            return (
                "both",
                f"voluntary_resolution_signal status='{rs}' with both relief and care keywords — "
                "advisory candidate for Phase 18 Relief Case Memory AND Phase 19 Care Loop Reopen",
            )
        if has_relief:
            return (
                "both",
                f"voluntary_resolution_signal status='{rs}' with relief/housing keywords — "
                "advisory candidate for Phase 18 Relief Case Memory AND Phase 19 Care Loop Reopen "
                "(unresolved/contested/paused signals escalate to both by default)",
            )
        return (
            "care_loop_reopen",
            f"voluntary_resolution_signal status='{rs}' — "
            "unresolved/contested/paused signals are advisory candidates for "
            "Phase 19 Care Loop Reopen; human review required",
        )

    if has_relief and has_care:
        return (
            "both",
            "content contains both relief/housing keywords and care/reopen keywords — "
            "advisory candidate for Phase 18 Relief Case Memory AND Phase 19 Care Loop Reopen",
        )
    if has_relief:
        return (
            "relief_case_memory",
            "content contains relief / housing / tenancy / displacement keywords — "
            "advisory candidate for Phase 18 Relief Case Memory review",
        )
    if has_care:
        return (
            "care_loop_reopen",
            "content contains care / reopen / continuity keywords — "
            "advisory candidate for Phase 19 Care Loop Reopen review",
        )
    if et in ("objection", "rollback_request"):
        return (
            "care_loop_reopen",
            f"entry_type '{et}' indicates the current execution path requires re-examination — "
            "advisory candidate for Phase 19 Care Loop Reopen (default for objection/rollback)",
        )
    return (
        "none",
        "no keyword match and entry type does not imply a default bridge target — "
        "human review may identify a relevant Phase 18 or Phase 19 connection",
    )


# ─── Record construction ────────────────────────────────────────────────────────

def _make_feedback_record(entry: dict, seq: int, meta: dict) -> dict:
    """Build a single advisory feedback record from a log entry."""
    bridge_target, reason = _determine_bridge_target(entry)
    now = datetime.now(timezone.utc).isoformat()
    rec = {
        "feedback_id":             f"rfb-{seq:03d}",
        "source_directive_id":     entry.get("directive_id", meta.get("directive_id", "")),
        "globe_id":                entry.get("globe_id", meta.get("globe_id", "")),
        "source_log_id":           entry.get("log_id", ""),
        "entry_type":              entry.get("entry_type", ""),
        "actor_type":              entry.get("actor_type", ""),
        "actor_name":              entry.get("actor_name", ""),
        "content":                 entry.get("content", ""),
        "suggested_bridge_target": bridge_target,
        "suggested_reason":        reason,
        "requires_human_review":   True,
        "creates_no_legal_authority": True,
        "not_proof_of_resolution":    True,
        "advisory_only":              True,
        "source_entry_created_at": entry.get("created_at", ""),
        "record_generated_at":     now,
    }
    # Phase 29 — carry resolution_status metadata when present
    rs = entry.get("resolution_status")
    if rs:
        rec["resolution_status"] = rs
        rec["resolution_signal_is_self_reported"] = True
        rec["resolution_signal_is_not_proof"]     = True
    return rec


# ─── Report builder ─────────────────────────────────────────────────────────────

def build_bridge() -> dict:
    """Build the full Reality Feedback Bridge report."""
    all_entries = _load_all_entries()
    records: list = []
    seq = 1

    for directive_id, entries in sorted(all_entries.items()):
        meta = _load_directive_meta(directive_id)
        for entry in entries:
            et = entry.get("entry_type", "")
            if et not in BRIDGE_ENTRY_TYPES:
                continue
            # Phase 29 — skip resolved/partially_resolved signals (keep summary only)
            if et == "voluntary_resolution_signal":
                rs = entry.get("resolution_status", "")
                if rs not in BRIDGE_RESOLUTION_STATUSES:
                    continue  # resolved / partially_resolved → not bridged
            records.append(_make_feedback_record(entry, seq, meta))
            seq += 1

    # Count by bridge target
    target_counts: dict[str, int] = {
        "relief_case_memory": 0,
        "care_loop_reopen":   0,
        "both":               0,
        "none":               0,
    }
    for r in records:
        t = r.get("suggested_bridge_target", "none")
        target_counts[t] = target_counts.get(t, 0) + 1

    # Aggregate by directive
    by_directive: dict[str, dict] = {}
    for r in records:
        did = r["source_directive_id"]
        if did not in by_directive:
            meta = _load_directive_meta(did)
            globe_id = r["globe_id"]
            by_directive[did] = {
                "directive_id":  did,
                "globe_id":      globe_id,
                "globe_name":    _load_globe_name(globe_id),
                "title":         meta.get("title", did),
                "record_count":  0,
                "bridge_targets": {},
            }
        rec = by_directive[did]
        rec["record_count"] += 1
        t = r["suggested_bridge_target"]
        rec["bridge_targets"][t] = rec["bridge_targets"].get(t, 0) + 1

    # Aggregate by globe
    by_globe: dict[str, dict] = {}
    for d in by_directive.values():
        gid = d["globe_id"]
        if gid not in by_globe:
            by_globe[gid] = {
                "globe_id":        gid,
                "globe_name":      d["globe_name"],
                "directive_count": 0,
                "record_count":    0,
                "bridge_targets":  {},
            }
        bg = by_globe[gid]
        bg["directive_count"] += 1
        bg["record_count"]    += d["record_count"]
        for t, n in d["bridge_targets"].items():
            bg["bridge_targets"][t] = bg["bridge_targets"].get(t, 0) + n

    now = datetime.now(timezone.utc).isoformat()
    return {
        "bridge_id": "reality-feedback-bridge-001",
        **BRIDGE_INVARIANTS,
        "phase": 27,
        "generated_at": now,
        "total_source_entries_scanned": sum(len(v) for v in all_entries.values()),
        "total_bridge_records": len(records),
        "bridge_target_counts": target_counts,
        "records": records,
        "by_directive": list(by_directive.values()),
        "by_globe":     list(by_globe.values()),
        "phase_phrases": BRIDGE_PHRASES,
    }


# ─── CLI display ────────────────────────────────────────────────────────────────

def _print_invariants() -> None:
    print("  Invariants:")
    for k, v in BRIDGE_INVARIANTS.items():
        print(f"    {k}: {str(v).lower()}")


def print_summary(report: dict) -> None:
    print("Reality Feedback Bridge (Phase 27)")
    print("=" * 60)
    gen = str(report.get("generated_at", ""))[:19].replace("T", " ")
    print(f"  generated_at:                    {gen}")
    print(f"  total_source_entries_scanned:    {report.get('total_source_entries_scanned', 0)}")
    print(f"  total_bridge_records:            {report.get('total_bridge_records', 0)}")
    tc = report.get("bridge_target_counts", {})
    print(f"  🏠  relief_case_memory:            {tc.get('relief_case_memory', 0)}")
    print(f"  🔄  care_loop_reopen:              {tc.get('care_loop_reopen', 0)}")
    print(f"  🏠🔄 both:                          {tc.get('both', 0)}")
    print(f"  —   none (no match):               {tc.get('none', 0)}")
    print()
    _print_invariants()

    print()
    print("By Directive:")
    print("-" * 60)
    for d in report.get("by_directive", []):
        print(f"  {d['directive_id']}")
        print(f"    globe: {d['globe_id']}  records: {d['record_count']}")
        for t, n in d.get("bridge_targets", {}).items():
            icon = _TARGET_ICON.get(t, "?")
            label = _TARGET_LABEL.get(t, t)
            print(f"    {icon} {label}: {n}")

    print()
    print("By Globe:")
    print("-" * 60)
    for g in report.get("by_globe", []):
        print(f"  {g['globe_id']}  {g['globe_name']}")
        print(f"    directives: {g['directive_count']}  records: {g['record_count']}")
        for t, n in g.get("bridge_targets", {}).items():
            icon = _TARGET_ICON.get(t, "?")
            label = _TARGET_LABEL.get(t, t)
            print(f"    {icon} {label}: {n}")

    print()
    print("Phase 27 phrases:")
    for phrase in report.get("phase_phrases", []):
        print(f"  \"{phrase}\"")


def print_directive(report: dict, directive_id: str) -> None:
    records = [r for r in report.get("records", []) if r["source_directive_id"] == directive_id]
    if not records:
        print(f"No bridge records found for directive: {directive_id}")
        return
    d_info = next(
        (d for d in report.get("by_directive", []) if d["directive_id"] == directive_id), {}
    )
    print(f"Reality Feedback Bridge — {directive_id}")
    print("=" * 60)
    print(f"  globe:   {d_info.get('globe_id', '')}  {d_info.get('globe_name', '')}")
    print(f"  title:   {d_info.get('title', '')}")
    print(f"  records: {len(records)}")
    print()
    for r in records:
        ei    = _ENTRY_ICON.get(r["entry_type"], "•")
        ti    = _TARGET_ICON.get(r["suggested_bridge_target"], "—")
        label = _TARGET_LABEL.get(r["suggested_bridge_target"], r["suggested_bridge_target"])
        print(f"  {ei} [{r['feedback_id']}] {r['entry_type']}  →  {ti} {label}")
        print(f"       log_id:  {r.get('source_log_id', '?')}")
        print(f"       actor:   {r['actor_type']}: {r['actor_name']}")
        content = r["content"]
        print(f"       content: {content[:80]}{'...' if len(content) > 80 else ''}")
        reason = r["suggested_reason"]
        print(f"       reason:  {reason[:90]}{'...' if len(reason) > 90 else ''}")
        print(f"       requires_human_review: true  |  creates_no_legal_authority: true")
        print(f"       not_proof_of_resolution: true  |  advisory_only: true")
        print()


def print_globe(report: dict, globe_id: str) -> None:
    records = [r for r in report.get("records", []) if r["globe_id"] == globe_id]
    g_info  = next(
        (g for g in report.get("by_globe", []) if g["globe_id"] == globe_id), {}
    )
    if not records:
        print(f"No bridge records found for globe: {globe_id}")
        return
    print(f"Reality Feedback Bridge — {globe_id}  {g_info.get('globe_name', '')}")
    print("=" * 60)
    print(f"  directives: {g_info.get('directive_count', 0)}  records: {len(records)}")
    print()
    for r in records:
        ei    = _ENTRY_ICON.get(r["entry_type"], "•")
        ti    = _TARGET_ICON.get(r["suggested_bridge_target"], "—")
        label = _TARGET_LABEL.get(r["suggested_bridge_target"], r["suggested_bridge_target"])
        print(f"  {ei} [{r['feedback_id']}] {r['source_directive_id']}")
        print(f"       {r['entry_type']}  →  {ti} {label}")
        print(f"       actor: {r['actor_name']}")
        content = r["content"]
        print(f"       content: {content[:80]}{'...' if len(content) > 80 else ''}")
        print()
    print("  advisory: requires_human_review: true on all records")
    print("  advisory: feedback_bridge_does_not_reopen_case_automatically: true")


# ─── Markdown export ────────────────────────────────────────────────────────────

def _build_markdown(report: dict) -> str:
    gen = str(report.get("generated_at", ""))[:19].replace("T", " ")
    tc  = report.get("bridge_target_counts", {})
    lines = [
        "# Reality Feedback Bridge Report (Phase 27)",
        "",
        "> **Reality feedback is advisory only.**",
        "> **Feedback bridge is not proof of resolution.**",
        "> **Feedback bridge creates no legal authority.**",
        "> **Feedback bridge does not reopen a case automatically.**",
        "> **Human review is required before any real-world action.**",
        "",
        f"Generated: {gen}",
        "",
        "## Summary",
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| total_source_entries_scanned | {report.get('total_source_entries_scanned', 0)} |",
        f"| total_bridge_records | {report.get('total_bridge_records', 0)} |",
        f"| 🏠 relief_case_memory | {tc.get('relief_case_memory', 0)} |",
        f"| 🔄 care_loop_reopen | {tc.get('care_loop_reopen', 0)} |",
        f"| 🏠🔄 both | {tc.get('both', 0)} |",
        f"| — none (no match) | {tc.get('none', 0)} |",
        f"| authority | none |",
        "",
    ]

    lines += ["## By Directive", ""]
    for d in report.get("by_directive", []):
        lines.append(f"### {d['directive_id']}  ({d['globe_id']})")
        lines.append(f"- title: {d['title']}")
        lines.append(f"- records: {d['record_count']}")
        for t, n in d.get("bridge_targets", {}).items():
            icon  = _TARGET_ICON.get(t, "?")
            label = _TARGET_LABEL.get(t, t)
            lines.append(f"- {icon} {label}: {n}")
        lines.append("")

    lines += ["## All Bridge Records", ""]
    for r in report.get("records", []):
        ei    = _ENTRY_ICON.get(r["entry_type"], "•")
        ti    = _TARGET_ICON.get(r["suggested_bridge_target"], "—")
        label = _TARGET_LABEL.get(r["suggested_bridge_target"], r["suggested_bridge_target"])
        lines += [
            f"### {r['feedback_id']}",
            f"- directive: `{r['source_directive_id']}`",
            f"- log_id: `{r.get('source_log_id', '?')}`",
            f"- entry_type: {ei} `{r['entry_type']}`",
            f"- actor: {r['actor_type']} / {r['actor_name']}",
            f"- content: {r['content']}",
            f"- **suggested_bridge_target:** {ti} `{r['suggested_bridge_target']}` ({label})",
            f"- suggested_reason: {r['suggested_reason']}",
            f"- requires_human_review: true",
            f"- creates_no_legal_authority: true",
            f"- not_proof_of_resolution: true",
            f"- advisory_only: true",
            "",
        ]

    lines += [
        "---",
        "",
        "*Reality feedback is advisory only.*",
        "*Feedback bridge is not proof of resolution.*",
        "*Feedback bridge creates no legal authority.*",
        "*Feedback bridge does not reopen a case automatically.*",
        "*Human review is required before any real-world action.*",
    ]
    return "\n".join(lines)


def save_report(report: dict) -> None:
    _REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = _REPORTS_DIR / "reality_feedback_bridge.json"
    md_path   = _REPORTS_DIR / "reality_feedback_bridge.md"
    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    md_path.write_text(_build_markdown(report), encoding="utf-8")
    print_summary(report)
    print()
    print(f"Saved: {json_path}")
    print(f"Saved: {md_path}")


# ─── CLI dispatcher ─────────────────────────────────────────────────────────────

def main(argv: list) -> None:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return

    cmd = argv[0]

    if cmd == "summary":
        print_summary(build_bridge())

    elif cmd == "save":
        save_report(build_bridge())

    elif cmd == "show-directive":
        if len(argv) < 2:
            print("Usage: reality_feedback_bridge.py show-directive <directive_id>")
            sys.exit(1)
        print_directive(build_bridge(), argv[1])

    elif cmd == "show-globe":
        if len(argv) < 2:
            print("Usage: reality_feedback_bridge.py show-globe <globe_id>")
            sys.exit(1)
        print_globe(build_bridge(), argv[1])

    else:
        print(f"Unknown command: {cmd}")
        print("Commands: summary  save  show-directive <id>  show-globe <id>")
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
