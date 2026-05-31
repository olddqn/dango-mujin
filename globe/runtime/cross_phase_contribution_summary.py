#!/usr/bin/env python3
"""
cross_phase_contribution_summary.py — Cross-Phase Contribution Summary (Phase 30)
Dan-Go × GITSEA — Globe Execution Layer

Reads Phase 20/21 aid pattern / need forecast data and Phase 25–29 Execution Log /
Resolution Signal / Reality Feedback data to produce an advisory cross-phase summary.

Cross-phase summary is advisory only.
Cross-phase summary is not proof of impact.
Cross-phase summary does not rank participants.
Cross-phase summary does not allocate resources.
Human review is required before any real-world action.

authority: none · advisory · append-only source · non-coercive · stdlib only

Usage:
    python3 globe/runtime/cross_phase_contribution_summary.py summary
    python3 globe/runtime/cross_phase_contribution_summary.py save
    python3 globe/runtime/cross_phase_contribution_summary.py show-globe <globe_id>
    python3 globe/runtime/cross_phase_contribution_summary.py show-section aid
    python3 globe/runtime/cross_phase_contribution_summary.py show-section forecast
    python3 globe/runtime/cross_phase_contribution_summary.py show-section logs
    python3 globe/runtime/cross_phase_contribution_summary.py show-section bridge
    python3 globe/runtime/cross_phase_contribution_summary.py show-section links
    python3 globe/runtime/cross_phase_contribution_summary.py show-section resolution
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT       = Path(__file__).resolve().parents[2]
_GLOBE_DIR       = Path(__file__).resolve().parents[1]
_LOGS_DIR        = _GLOBE_DIR / "logs"
_REPORTS_DIR     = _GLOBE_DIR / "reports"
_DIRECTIVES_DIR  = _GLOBE_DIR / "directives"
_DATA_DIR        = _GLOBE_DIR / "data"

# Phase 20/21 data paths (relative to repo root)
_AID_PATTERN_REGISTRY  = _REPO_ROOT / "bridge/gitsea/aid_patterns/examples/aid-pattern-registry.json"
_AID_PATTERN_MEMORY    = _REPO_ROOT / "bridge/gitsea/aid_patterns/examples/pattern-memory.json"
_RECURRENCE_SNAPSHOT   = _REPO_ROOT / "bridge/gitsea/aid_patterns/examples/recurrence-snapshot.json"
_NEED_FORECAST_REG     = _REPO_ROOT / "bridge/gitsea/need_forecast/examples/need-forecast-registry.json"
_FORECAST_MEMORY       = _REPO_ROOT / "bridge/gitsea/need_forecast/examples/forecast-memory.json"
_PREPAREDNESS_SNAPSHOT = _REPO_ROOT / "bridge/gitsea/need_forecast/examples/preparedness-hint-snapshot.json"

# Phase 26/27/27b/29 report paths
_EXEC_LOG_SUMMARY  = _REPORTS_DIR / "execution_log_summary.json"
_BRIDGE_REPORT     = _REPORTS_DIR / "reality_feedback_bridge.json"
_LINK_REPORT       = _REPORTS_DIR / "bridge_target_links.json"

# ─── Phase 30 invariants ────────────────────────────────────────────────────────

SUMMARY_INVARIANTS = {
    "cross_phase_summary_is_advisory_only":          True,
    "cross_phase_summary_is_not_proof_of_impact":    True,
    "cross_phase_summary_does_not_rank_participants": True,
    "cross_phase_summary_does_not_allocate_resources": True,
    "human_review_is_required_before_any_real_world_action": True,
    "authority": "none",
}

PHASE_PHRASES = [
    "Cross-phase summary is advisory only.",
    "Cross-phase summary is not proof of impact.",
    "Cross-phase summary does not rank participants.",
    "Cross-phase summary does not allocate resources.",
    "Human review is required before any real-world action.",
]

VALID_SECTIONS = {"aid", "forecast", "logs", "bridge", "links", "resolution"}

# ─── IO helpers ─────────────────────────────────────────────────────────────────

def _load_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _load_jsonl(path: Path) -> list:
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


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_globes() -> list:
    d = _load_json(_DATA_DIR / "globes.json")
    return d if isinstance(d, list) else []


def _globe_name(globe_id: str, globes: list) -> str:
    for g in globes:
        if g.get("globe_id") == globe_id:
            return g.get("name", globe_id)
    return globe_id


# ─── Phase 20: Aid Pattern data ─────────────────────────────────────────────────

def _load_aid_section() -> dict:
    """Load Phase 20 aid pattern data. Returns structured section dict."""
    registry  = _load_json(_AID_PATTERN_REGISTRY) or {}
    memory    = _load_json(_AID_PATTERN_MEMORY) or {}
    recurrence = _load_json(_RECURRENCE_SNAPSHOT) or {}

    patterns  = registry.get("patterns", [])
    memories  = memory.get("pattern_memories", memory.get("memories", []))
    recurrences = recurrence.get("recurrences", [])

    # Commons distribution
    commons_counts: dict[str, int] = {}
    for p in patterns:
        cid = p.get("commons_id", "unknown")
        commons_counts[cid] = commons_counts.get(cid, 0) + 1

    pattern_types = [p.get("pattern_type", "") for p in patterns]

    return {
        "phase": 20,
        "phase_label": "Aid Pattern Learning",
        "aid_pattern_count": len(patterns),
        "pattern_memory_count": len(memories),
        "recurrence_count": len(recurrences),
        "commons_represented": sorted(set(commons_counts.keys())),
        "commons_pattern_counts": commons_counts,
        "pattern_types": pattern_types,
        "source_files_found": {
            "aid_pattern_registry":  _AID_PATTERN_REGISTRY.exists(),
            "pattern_memory":        _AID_PATTERN_MEMORY.exists(),
            "recurrence_snapshot":   _RECURRENCE_SNAPSHOT.exists(),
        },
        # Phase 20 invariants
        "pattern_is_prediction": False,
        "learning_is_prescription": False,
        "recurrence_is_ranking": False,
    }


# ─── Phase 21: Need Forecast data ───────────────────────────────────────────────

def _load_forecast_section() -> dict:
    """Load Phase 21 need forecast data. Returns structured section dict."""
    registry    = _load_json(_NEED_FORECAST_REG) or {}
    f_memory    = _load_json(_FORECAST_MEMORY) or {}
    prep_snap   = _load_json(_PREPAREDNESS_SNAPSHOT) or {}

    forecasts   = registry.get("forecasts", [])
    f_memories  = f_memory.get("forecast_memories", f_memory.get("memories", []))
    hints       = prep_snap.get("preparedness_hints", prep_snap.get("hints", []))

    # Commons distribution
    commons_counts: dict[str, int] = {}
    for f in forecasts:
        cid = f.get("commons_id", "unknown")
        commons_counts[cid] = commons_counts.get(cid, 0) + 1

    forecast_types = [f.get("forecast_type", "") for f in forecasts]

    return {
        "phase": 21,
        "phase_label": "Commons Need Forecast Memory",
        "need_forecast_count": len(forecasts),
        "forecast_memory_count": len(f_memories),
        "preparedness_hint_count": len(hints),
        "commons_represented": sorted(set(commons_counts.keys())),
        "commons_forecast_counts": commons_counts,
        "forecast_types": forecast_types,
        "source_files_found": {
            "need_forecast_registry":   _NEED_FORECAST_REG.exists(),
            "forecast_memory":          _FORECAST_MEMORY.exists(),
            "preparedness_hint_snapshot": _PREPAREDNESS_SNAPSHOT.exists(),
        },
        # Phase 21 invariants
        "forecast_is_certainty": False,
        "preparedness_is_command": False,
        "hint_is_allocation": False,
    }


# ─── Phase 25–29: Execution Log data ────────────────────────────────────────────

def _load_logs_section() -> dict:
    """Load raw JSONL execution logs across all directives."""
    all_entries: list = []
    by_directive: dict[str, list] = {}

    for p in sorted(_LOGS_DIR.glob("*.jsonl")):
        did = p.stem
        entries = _load_jsonl(p)
        all_entries.extend(entries)
        by_directive[did] = entries

    # Count by entry_type
    type_counts: dict[str, int] = {}
    for e in all_entries:
        et = e.get("entry_type", "unknown")
        type_counts[et] = type_counts.get(et, 0) + 1

    # Resolution status breakdown (Phase 29)
    rs_counts: dict[str, int] = {}
    for e in all_entries:
        if e.get("entry_type") == "voluntary_resolution_signal":
            rs = e.get("resolution_status", "unknown")
            rs_counts[rs] = rs_counts.get(rs, 0) + 1

    # Globe distribution (via directive JSON)
    globe_log_counts: dict[str, int] = {}
    globe_directive_counts: dict[str, int] = {}
    for did, entries in by_directive.items():
        p = _DIRECTIVES_DIR / f"{did}.json"
        d = _load_json(p) or {}
        gid = d.get("globe_id", "unknown")
        globe_log_counts[gid] = globe_log_counts.get(gid, 0) + len(entries)
        globe_directive_counts[gid] = globe_directive_counts.get(gid, 0) + 1

    return {
        "phases": [25, 26, 27, 29],
        "phase_label": "Execution Log / Resolution Signal",
        "total_log_entries": len(all_entries),
        "directive_count": len(by_directive),
        "entry_type_counts": type_counts,
        "human_approval_count":              type_counts.get("human_approval", 0),
        "execution_attempt_count":           type_counts.get("execution_attempt", 0),
        "observation_count":                 type_counts.get("observation", 0),
        "feedback_count":                    type_counts.get("feedback", 0),
        "objection_count":                   type_counts.get("objection", 0),
        "rollback_request_count":            type_counts.get("rollback_request", 0),
        "voluntary_resolution_signal_count": type_counts.get("voluntary_resolution_signal", 0),
        # Phase 29 breakdown
        "resolution_status_counts": rs_counts,
        "resolved_count":           rs_counts.get("resolved", 0),
        "partially_resolved_count": rs_counts.get("partially_resolved", 0),
        "paused_count":             rs_counts.get("paused", 0),
        "unresolved_signal_count":  rs_counts.get("unresolved", 0),
        "contested_signal_count":   rs_counts.get("contested", 0),
        # Distribution
        "globe_log_counts":        globe_log_counts,
        "globe_directive_counts":  globe_directive_counts,
    }


# ─── Phase 27: Reality Feedback Bridge data ─────────────────────────────────────

def _load_bridge_section() -> dict:
    """Load Phase 27 reality feedback bridge report."""
    report = _load_json(_BRIDGE_REPORT) or {}
    records = report.get("records", [])
    target_counts = report.get("bridge_target_counts", {})

    # Scanned vs bridged
    scanned    = report.get("total_source_entries_scanned", 0)
    bridged    = len(records)
    none_count = target_counts.get("none", 0)
    matched    = bridged - none_count

    # Entry type breakdown in bridge records
    entry_type_in_records: dict[str, int] = {}
    for r in records:
        et = r.get("entry_type", "unknown")
        entry_type_in_records[et] = entry_type_in_records.get(et, 0) + 1

    # Resolution-status breakdown in bridge records (Phase 29)
    rs_in_records: dict[str, int] = {}
    for r in records:
        rs = r.get("resolution_status", "")
        if rs:
            rs_in_records[rs] = rs_in_records.get(rs, 0) + 1

    return {
        "phase": 27,
        "phase_label": "Reality Feedback Bridge",
        "total_source_entries_scanned": scanned,
        "bridge_record_count": bridged,
        "bridge_matched_count": matched,
        "bridge_none_count": none_count,
        "target_counts": target_counts,
        "relief_case_memory_count": target_counts.get("relief_case_memory", 0),
        "care_loop_reopen_count":   target_counts.get("care_loop_reopen", 0),
        "both_count":               target_counts.get("both", 0),
        "entry_type_in_records": entry_type_in_records,
        "resolution_status_in_records": rs_in_records,
        "source_file_found": _BRIDGE_REPORT.exists(),
        # Phase 27 invariants
        "feedback_bridge_is_not_proof_of_resolution": True,
        "feedback_bridge_creates_no_legal_authority": True,
    }


# ─── Phase 27b: Bridge Target Links data ────────────────────────────────────────

def _load_links_section() -> dict:
    """Load Phase 27b bridge target link candidates."""
    report = _load_json(_LINK_REPORT) or {}
    candidates = report.get("candidates", [])

    # Confidence distribution
    conf_counts: dict[str, int] = {}
    for c in candidates:
        conf = c.get("confidence", "low")
        conf_counts[conf] = conf_counts.get(conf, 0) + 1

    # Target type distribution
    target_counts: dict[str, int] = {}
    for c in candidates:
        tt = c.get("candidate_target_type", "none")
        target_counts[tt] = target_counts.get(tt, 0) + 1

    # Items linked (excluding "none")
    items_with_links = [c for c in candidates if c.get("candidate_target_type") != "none"]
    item_ids = [c.get("candidate_item_id", "") for c in items_with_links if c.get("candidate_item_id")]

    return {
        "phase": "27b",
        "phase_label": "Bridge Target Detail Link",
        "total_link_candidates": len(candidates),
        "high_confidence_count":   conf_counts.get("high", 0),
        "medium_confidence_count": conf_counts.get("medium", 0),
        "low_confidence_count":    conf_counts.get("low", 0),
        "confidence_counts": conf_counts,
        "target_type_counts": target_counts,
        "linked_item_ids": item_ids,
        "source_file_found": _LINK_REPORT.exists(),
        # Phase 27b invariants
        "link_candidate_is_not_proof_of_case_relation": True,
        "link_candidate_creates_no_legal_authority": True,
    }


# ─── Globe-level aggregation ────────────────────────────────────────────────────

def _build_globe_summaries(
    globes: list,
    logs_section: dict,
    bridge_section: dict,
    links_section: dict,
) -> list:
    """Build per-globe cross-phase sub-summaries."""
    bridge_report  = _load_json(_BRIDGE_REPORT) or {}
    link_report    = _load_json(_LINK_REPORT) or {}

    # Precompute per-globe bridge counts
    globe_bridge: dict[str, int] = {}
    for r in bridge_report.get("records", []):
        gid = r.get("globe_id", "unknown")
        globe_bridge[gid] = globe_bridge.get(gid, 0) + 1

    # Precompute per-globe link counts
    globe_links: dict[str, int] = {}
    for c in link_report.get("candidates", []):
        gid = c.get("globe_id", "unknown")
        globe_links[gid] = globe_links.get(gid, 0) + 1

    # Per-globe resolution signal details from raw logs
    globe_rs_counts: dict[str, dict] = {}
    for p in sorted(_LOGS_DIR.glob("*.jsonl")):
        did = p.stem
        d_json = _load_json(_DIRECTIVES_DIR / f"{did}.json") or {}
        gid = d_json.get("globe_id", "unknown")
        for e in _load_jsonl(p):
            if e.get("entry_type") == "voluntary_resolution_signal":
                rs = e.get("resolution_status", "")
                if gid not in globe_rs_counts:
                    globe_rs_counts[gid] = {}
                globe_rs_counts[gid][rs] = globe_rs_counts[gid].get(rs, 0) + 1

    # Per-globe log entry type counts from raw logs
    globe_entry_counts: dict[str, dict] = {}
    for p in sorted(_LOGS_DIR.glob("*.jsonl")):
        did = p.stem
        d_json = _load_json(_DIRECTIVES_DIR / f"{did}.json") or {}
        gid = d_json.get("globe_id", "unknown")
        for e in _load_jsonl(p):
            et = e.get("entry_type", "")
            if gid not in globe_entry_counts:
                globe_entry_counts[gid] = {}
            globe_entry_counts[gid][et] = globe_entry_counts[gid].get(et, 0) + 1

    # Collect all globe_ids that appear in any data
    all_globe_ids = set()
    all_globe_ids.update(logs_section.get("globe_log_counts", {}).keys())
    all_globe_ids.update(globe_bridge.keys())
    all_globe_ids.update(globe_links.keys())

    result = []
    for gid in sorted(all_globe_ids):
        ec = globe_entry_counts.get(gid, {})
        rs = globe_rs_counts.get(gid, {})
        result.append({
            "globe_id":               gid,
            "globe_name":             _globe_name(gid, globes),
            "directive_count":        logs_section.get("globe_directive_counts", {}).get(gid, 0),
            "log_entry_count":        logs_section.get("globe_log_counts", {}).get(gid, 0),
            "human_approval_count":   ec.get("human_approval", 0),
            "objection_count":        ec.get("objection", 0),
            "rollback_request_count": ec.get("rollback_request", 0),
            "observation_count":      ec.get("observation", 0),
            "feedback_count":         ec.get("feedback", 0),
            # Phase 29
            "resolution_signal_count": ec.get("voluntary_resolution_signal", 0),
            "unresolved_signal_count": rs.get("unresolved", 0),
            "contested_signal_count":  rs.get("contested", 0),
            "paused_signal_count":     rs.get("paused", 0),
            "resolved_count":          rs.get("resolved", 0),
            "partially_resolved_count": rs.get("partially_resolved", 0),
            # Phase 27/27b
            "bridge_record_count":    globe_bridge.get(gid, 0),
            "link_candidate_count":   globe_links.get(gid, 0),
        })

    return result


# ─── Advisory interpretation ────────────────────────────────────────────────────

def _build_interpretation(
    logs_sec: dict,
    bridge_sec: dict,
    links_sec: dict,
    globe_summaries: list,
) -> dict:
    """
    Generate advisory interpretation observations.

    These are not rankings, scores, or commands — they are human-readable
    summaries of where observable signals cluster. Human review required.
    """
    observations: list[str] = []
    attention: list[str] = []
    unresolved: list[str] = []
    with_objections: list[str] = []
    requires_review: list[str] = []

    for g in globe_summaries:
        gid = g["globe_id"]
        name = g["globe_name"]
        label = f"{gid} ({name})"

        # Where attention is increasing (by log entry count)
        if g["log_entry_count"] > 0:
            attention.append(
                f"{label}: {g['log_entry_count']} log entries across "
                f"{g['directive_count']} directive(s)"
            )

        # Where unresolved signals remain
        if g["unresolved_signal_count"] > 0 or g["contested_signal_count"] > 0:
            unresolved.append(
                f"{label}: {g['unresolved_signal_count']} unresolved signal(s), "
                f"{g['contested_signal_count']} contested signal(s) "
                f"[self-reported · not proof]"
            )

        # Where objections exist
        if g["objection_count"] > 0:
            with_objections.append(
                f"{label}: {g['objection_count']} objection(s) recorded"
            )

        # Where bridge candidates require human review
        if g["bridge_record_count"] > 0 or g["link_candidate_count"] > 0:
            requires_review.append(
                f"{label}: {g['bridge_record_count']} bridge record(s), "
                f"{g['link_candidate_count']} link candidate(s) — human review required"
            )

    # Overall observations
    total_sig = logs_sec.get("voluntary_resolution_signal_count", 0)
    total_unresolved = logs_sec.get("unresolved_signal_count", 0)
    total_contested  = logs_sec.get("contested_signal_count", 0)
    total_bridge     = bridge_sec.get("bridge_record_count", 0)
    high_conf        = links_sec.get("high_confidence_count", 0)

    if total_sig > 0:
        observations.append(
            f"{total_sig} voluntary resolution signal(s) recorded — "
            f"self-reported only, not proof of resolution"
        )
    if total_unresolved > 0:
        observations.append(
            f"{total_unresolved} unresolved signal(s) — "
            f"advisory candidate for Phase 19 Care Loop Reopen"
        )
    if total_contested > 0:
        observations.append(
            f"{total_contested} contested signal(s) — "
            f"always recordable; indicates disagreement with current path"
        )
    if total_bridge > 0:
        observations.append(
            f"{total_bridge} bridge record(s) generated — "
            f"advisory connection to Phase 18/19 relief and care data"
        )
    if high_conf > 0:
        observations.append(
            f"{high_conf} high-confidence link candidate(s) — "
            f"require human review before any action"
        )

    return {
        "disclaimer": (
            "Advisory interpretation only. This section describes observable patterns "
            "in recorded data. It is not a ranking, score, or command. "
            "No allocation or execution follows from these observations. "
            "Human review is required before any real-world action."
        ),
        "where_attention_is_increasing":         attention,
        "where_unresolved_signals_remain":        unresolved,
        "where_objections_exist":                 with_objections,
        "where_bridge_candidates_require_review": requires_review,
        "cross_phase_observations":               observations,
    }


# ─── Report builder ─────────────────────────────────────────────────────────────

def build_summary() -> dict:
    """Build the full cross-phase contribution summary."""
    globes = _load_globes()

    aid_sec      = _load_aid_section()
    forecast_sec = _load_forecast_section()
    logs_sec     = _load_logs_section()
    bridge_sec   = _load_bridge_section()
    links_sec    = _load_links_section()

    globe_summaries = _build_globe_summaries(globes, logs_sec, bridge_sec, links_sec)
    interpretation  = _build_interpretation(logs_sec, bridge_sec, links_sec, globe_summaries)

    return {
        "summary_id": "cross-phase-contribution-summary-001",
        **SUMMARY_INVARIANTS,
        "phase": 30,
        "generated_at": _now(),
        # Global tallies (top-level, for quick read)
        "aid_pattern_count":                     aid_sec["aid_pattern_count"],
        "need_forecast_record_count":            forecast_sec["need_forecast_count"],
        "execution_log_entry_count":             logs_sec["total_log_entries"],
        "human_approval_count":                  logs_sec["human_approval_count"],
        "observation_count":                     logs_sec["observation_count"],
        "feedback_count":                        logs_sec["feedback_count"],
        "objection_count":                       logs_sec["objection_count"],
        "rollback_request_count":                logs_sec["rollback_request_count"],
        "voluntary_resolution_signal_count":     logs_sec["voluntary_resolution_signal_count"],
        "unresolved_signal_count":               logs_sec["unresolved_signal_count"],
        "contested_signal_count":                logs_sec["contested_signal_count"],
        "bridge_record_count":                   bridge_sec["bridge_record_count"],
        "bridge_target_link_count":              links_sec["total_link_candidates"],
        "high_confidence_link_count":            links_sec["high_confidence_count"],
        # Sections
        "section_aid":        aid_sec,
        "section_forecast":   forecast_sec,
        "section_logs":       logs_sec,
        "section_bridge":     bridge_sec,
        "section_links":      links_sec,
        # Per-globe
        "globe_summaries":    globe_summaries,
        # Advisory interpretation
        "interpretation":     interpretation,
        "phase_phrases":      PHASE_PHRASES,
    }


# ─── CLI display ────────────────────────────────────────────────────────────────

def _hr(n: int = 60) -> None:
    print("─" * n)


def _fmt_date(ts: str) -> str:
    return ts[:19].replace("T", " ") if ts else "—"


def print_summary(report: dict) -> None:
    print("Cross-Phase Contribution Summary (Phase 30)")
    print("=" * 60)
    print(f"  generated_at:                    {_fmt_date(report.get('generated_at', ''))}")
    print()
    print("  ── Phase 20 Aid Patterns ──────────────────────────────")
    print(f"  aid_pattern_count:               {report.get('aid_pattern_count', 0)}")
    print()
    print("  ── Phase 21 Need Forecasts ────────────────────────────")
    print(f"  need_forecast_record_count:      {report.get('need_forecast_record_count', 0)}")
    print()
    print("  ── Phase 25–29 Execution Log ──────────────────────────")
    print(f"  execution_log_entry_count:       {report.get('execution_log_entry_count', 0)}")
    print(f"  human_approval_count:            {report.get('human_approval_count', 0)}")
    print(f"  observation_count:               {report.get('observation_count', 0)}")
    print(f"  feedback_count:                  {report.get('feedback_count', 0)}")
    print(f"  objection_count:                 {report.get('objection_count', 0)}")
    print(f"  rollback_request_count:          {report.get('rollback_request_count', 0)}")
    print(f"  voluntary_resolution_signal:     {report.get('voluntary_resolution_signal_count', 0)}")
    print(f"    🔴 unresolved:   {report.get('unresolved_signal_count', 0)}")
    print(f"    ⚔️  contested:    {report.get('contested_signal_count', 0)}")
    print(f"  [Phase 29 signals: self-reported · not proof]")
    print()
    print("  ── Phase 27/27b Bridge & Links ────────────────────────")
    print(f"  bridge_record_count:             {report.get('bridge_record_count', 0)}")
    print(f"  bridge_target_link_count:        {report.get('bridge_target_link_count', 0)}")
    print(f"  high_confidence_link_count:      {report.get('high_confidence_link_count', 0)}")
    print()
    print("  Invariants:")
    for k, v in SUMMARY_INVARIANTS.items():
        if k != "authority":
            print(f"    {k}: {str(v).lower()}")
    print(f"    authority: {report.get('authority', 'none')}")
    print()

    interp = report.get("interpretation", {})
    _print_interpretation(interp)

    print()
    print("By Globe:")
    _hr()
    for g in report.get("globe_summaries", []):
        _print_globe_row(g)
    print()
    print("Phase 30 phrases:")
    for phrase in report.get("phase_phrases", []):
        print(f'  "{phrase}"')


def _print_globe_row(g: dict) -> None:
    gid  = g["globe_id"]
    name = g["globe_name"]
    print(f"  {gid}  {name}")
    print(f"    directives:      {g['directive_count']}   log_entries: {g['log_entry_count']}")
    print(f"    ✅ approvals:    {g['human_approval_count']}")
    print(f"    ⚠️  objections:   {g['objection_count']}")
    print(f"    🔗 bridge:       {g['bridge_record_count']}   links: {g['link_candidate_count']}")
    sig = g.get("resolution_signal_count", 0)
    if sig:
        print(
            f"    🏳️  signals:     {sig}   "
            f"unresolved: {g.get('unresolved_signal_count',0)}   "
            f"contested: {g.get('contested_signal_count',0)}   "
            f"[self-reported · not proof]"
        )
    print()


def _print_interpretation(interp: dict) -> None:
    print("  Advisory Interpretation (not ranking · not command):")
    _hr(58)
    print(f"  ⓘ  {interp.get('disclaimer','')[:120]}…")
    print()

    obs = interp.get("cross_phase_observations", [])
    if obs:
        print("  Cross-phase observations:")
        for o in obs:
            print(f"    • {o}")
        print()

    attn = interp.get("where_attention_is_increasing", [])
    if attn:
        print("  Where attention is increasing:")
        for a in attn:
            print(f"    → {a}")
        print()

    unres = interp.get("where_unresolved_signals_remain", [])
    if unres:
        print("  Where unresolved signals remain:")
        for u in unres:
            print(f"    🔴 {u}")
        print()

    obj = interp.get("where_objections_exist", [])
    if obj:
        print("  Where objections exist:")
        for o in obj:
            print(f"    ⚠️  {o}")
        print()

    rev = interp.get("where_bridge_candidates_require_review", [])
    if rev:
        print("  Where bridge candidates require human review:")
        for r in rev:
            print(f"    🔗 {r}")


def print_globe(report: dict, globe_id: str) -> None:
    globe_summaries = report.get("globe_summaries", [])
    g = next((x for x in globe_summaries if x["globe_id"] == globe_id), None)
    if not g:
        print(f"Globe '{globe_id}' not found in cross-phase summary.")
        return

    print(f"Cross-Phase Summary — {globe_id}  ({g['globe_name']})")
    print("=" * 60)
    print(f"  directive_count:          {g['directive_count']}")
    print(f"  log_entry_count:          {g['log_entry_count']}")
    print(f"  human_approval_count:     {g['human_approval_count']}")
    print(f"  observation_count:        {g['observation_count']}")
    print(f"  feedback_count:           {g['feedback_count']}")
    print(f"  objection_count:          {g['objection_count']}")
    print(f"  rollback_request_count:   {g['rollback_request_count']}")
    print()
    print("  Phase 29 Resolution Signals (self-reported · not proof):")
    print(f"    resolution_signal_count:    {g.get('resolution_signal_count', 0)}")
    print(f"    ✅ resolved:                {g.get('resolved_count', 0)}")
    print(f"    🟡 partially_resolved:      {g.get('partially_resolved_count', 0)}")
    print(f"    ⏸️  paused:                  {g.get('paused_signal_count', 0)}")
    print(f"    🔴 unresolved:              {g.get('unresolved_signal_count', 0)}")
    print(f"    ⚔️  contested:               {g.get('contested_signal_count', 0)}")
    print()
    print("  Phase 27/27b Bridge & Links:")
    print(f"    bridge_record_count:        {g['bridge_record_count']}")
    print(f"    link_candidate_count:       {g['link_candidate_count']}")
    print()
    print("  advisory: none of these counts certify execution, impact, or authority.")


def print_section(report: dict, section: str) -> None:
    if section not in VALID_SECTIONS:
        print(f"Unknown section '{section}'. Valid: {', '.join(sorted(VALID_SECTIONS))}")
        return

    sec_map = {
        "aid":        ("section_aid",      "Phase 20 — Aid Pattern Learning"),
        "forecast":   ("section_forecast", "Phase 21 — Commons Need Forecast Memory"),
        "logs":       ("section_logs",     "Phase 25–29 — Execution Log"),
        "bridge":     ("section_bridge",   "Phase 27 — Reality Feedback Bridge"),
        "links":      ("section_links",    "Phase 27b — Bridge Target Detail Links"),
        "resolution": ("section_logs",     "Phase 29 — Voluntary Resolution Signals"),
    }
    key, label = sec_map[section]
    data = report.get(key, {})

    print(f"{label}")
    print("=" * 60)

    if section == "aid":
        print(f"  aid_pattern_count:       {data.get('aid_pattern_count', 0)}")
        print(f"  pattern_memory_count:    {data.get('pattern_memory_count', 0)}")
        print(f"  recurrence_count:        {data.get('recurrence_count', 0)}")
        print(f"  commons_represented:     {', '.join(data.get('commons_represented', []))}")
        print(f"  pattern_types:")
        for pt in data.get("pattern_types", []):
            print(f"    • {pt}")
        print()
        print("  Invariants:")
        print(f"    pattern_is_prediction:      {data.get('pattern_is_prediction', False)}")
        print(f"    learning_is_prescription:   {data.get('learning_is_prescription', False)}")
        print(f"    recurrence_is_ranking:      {data.get('recurrence_is_ranking', False)}")

    elif section == "forecast":
        print(f"  need_forecast_count:         {data.get('need_forecast_count', 0)}")
        print(f"  forecast_memory_count:       {data.get('forecast_memory_count', 0)}")
        print(f"  preparedness_hint_count:     {data.get('preparedness_hint_count', 0)}")
        print(f"  commons_represented:         {', '.join(data.get('commons_represented', []))}")
        print(f"  forecast_types:")
        for ft in data.get("forecast_types", []):
            print(f"    • {ft}")
        print()
        print("  Invariants:")
        print(f"    forecast_is_certainty:      {data.get('forecast_is_certainty', False)}")
        print(f"    preparedness_is_command:    {data.get('preparedness_is_command', False)}")
        print(f"    hint_is_allocation:         {data.get('hint_is_allocation', False)}")

    elif section == "logs":
        print(f"  total_log_entries:           {data.get('total_log_entries', 0)}")
        print(f"  directive_count:             {data.get('directive_count', 0)}")
        print()
        print("  Entry type breakdown:")
        for et, n in sorted(data.get("entry_type_counts", {}).items()):
            print(f"    {et:<32} {n}")
        print()
        print("  Per-globe log distribution:")
        for gid, n in sorted(data.get("globe_log_counts", {}).items()):
            print(f"    {gid}: {n} entries")

    elif section == "bridge":
        print(f"  total_source_entries_scanned: {data.get('total_source_entries_scanned', 0)}")
        print(f"  bridge_record_count:          {data.get('bridge_record_count', 0)}")
        print(f"  bridge_matched_count:         {data.get('bridge_matched_count', 0)}")
        print(f"  bridge_none_count:            {data.get('bridge_none_count', 0)}")
        print()
        print("  Bridge targets:")
        for t, n in sorted(data.get("target_counts", {}).items()):
            print(f"    {t:<25} {n}")
        print()
        print("  Entry types in bridge records:")
        for et, n in sorted(data.get("entry_type_in_records", {}).items()):
            print(f"    {et:<25} {n}")
        if data.get("resolution_status_in_records"):
            print()
            print("  Resolution statuses in bridge records (Phase 29):")
            for rs, n in sorted(data.get("resolution_status_in_records", {}).items()):
                print(f"    {rs:<25} {n}")

    elif section == "links":
        print(f"  total_link_candidates:        {data.get('total_link_candidates', 0)}")
        print()
        print("  Confidence distribution:")
        for conf, n in sorted(data.get("confidence_counts", {}).items()):
            icon = {"high": "🔴", "medium": "🟡", "low": "⚪"}.get(conf, "•")
            print(f"    {icon} {conf:<12} {n}")
        print()
        print("  Target type distribution:")
        for tt, n in sorted(data.get("target_type_counts", {}).items()):
            print(f"    {tt:<25} {n}")
        item_ids = data.get("linked_item_ids", [])
        if item_ids:
            print()
            print("  Linked item IDs:")
            for iid in item_ids:
                print(f"    • {iid}")

    elif section == "resolution":
        print(f"  voluntary_resolution_signal_count:  {data.get('voluntary_resolution_signal_count', 0)}")
        print()
        print("  Resolution status breakdown (self-reported · not proof):")
        icons = {"resolved":"✅","partially_resolved":"🟡","paused":"⏸️",
                 "unresolved":"🔴","contested":"⚔️"}
        for rs, n in sorted(data.get("resolution_status_counts", {}).items()):
            icon = icons.get(rs, "•")
            print(f"    {icon} {rs:<22} {n}")
        print()
        print("  Per-globe resolution distribution:")
        for gid, n in sorted(data.get("globe_log_counts", {}).items()):
            print(f"    {gid}")
        print()
        print("  Invariants:")
        print("    resolution_signal_is_self_reported:       true")
        print("    resolution_signal_is_not_proof:           true")
        print("    resolution_signal_does_not_close_support: true")
        print("    contested_always_recordable:              true")

    print()
    print("  advisory only · not proof of impact · no ranking · no allocation")


# ─── Markdown renderer ──────────────────────────────────────────────────────────

def _build_markdown(report: dict) -> str:
    lines: list[str] = []
    gen = _fmt_date(report.get("generated_at", ""))

    lines += [
        "# Cross-Phase Contribution Summary (Phase 30)",
        "",
        "> **Cross-phase summary is advisory only.**",
        "> Cross-phase summary is not proof of impact.",
        "> Cross-phase summary does not rank participants.",
        "> Cross-phase summary does not allocate resources.",
        "> Human review is required before any real-world action.",
        "",
        f"**Generated:** {gen}  ",
        "**authority:** none  ",
        "**phase:** 30",
        "",
        "## Global Tallies",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Aid patterns (Phase 20) | {report.get('aid_pattern_count', 0)} |",
        f"| Need forecasts (Phase 21) | {report.get('need_forecast_record_count', 0)} |",
        f"| Execution log entries (Phase 25–29) | {report.get('execution_log_entry_count', 0)} |",
        f"| Human approvals | {report.get('human_approval_count', 0)} |",
        f"| Observations | {report.get('observation_count', 0)} |",
        f"| Objections | {report.get('objection_count', 0)} |",
        f"| Rollback requests | {report.get('rollback_request_count', 0)} |",
        f"| 🏳️ Resolution signals (self-reported) | {report.get('voluntary_resolution_signal_count', 0)} |",
        f"| &nbsp;&nbsp;🔴 unresolved | {report.get('unresolved_signal_count', 0)} |",
        f"| &nbsp;&nbsp;⚔️ contested | {report.get('contested_signal_count', 0)} |",
        f"| Bridge records (Phase 27) | {report.get('bridge_record_count', 0)} |",
        f"| Link candidates (Phase 27b) | {report.get('bridge_target_link_count', 0)} |",
        f"| &nbsp;&nbsp;🔴 high-confidence | {report.get('high_confidence_link_count', 0)} |",
        "",
    ]

    # Globe summary table
    lines += [
        "## By Globe",
        "",
        "| Globe | Directives | Entries | Approvals | Objections | 🏳️ Unresolved | 🔗 Bridge | Links |",
        "|-------|-----------|---------|-----------|------------|----------------|-----------|-------|",
    ]
    for g in report.get("globe_summaries", []):
        lines.append(
            f"| {g['globe_id']} ({g['globe_name']}) "
            f"| {g['directive_count']} "
            f"| {g['log_entry_count']} "
            f"| {g['human_approval_count']} "
            f"| {g['objection_count']} "
            f"| {g.get('unresolved_signal_count', 0)} "
            f"| {g['bridge_record_count']} "
            f"| {g['link_candidate_count']} |"
        )
    lines += [""]

    # Advisory interpretation
    interp = report.get("interpretation", {})
    lines += [
        "## Advisory Interpretation",
        "",
        f"> ⓘ {interp.get('disclaimer', '')}",
        "",
    ]
    obs = interp.get("cross_phase_observations", [])
    if obs:
        lines.append("### Cross-Phase Observations")
        lines.append("")
        for o in obs:
            lines.append(f"- {o}")
        lines.append("")

    for heading, key in [
        ("Where Attention Is Increasing",         "where_attention_is_increasing"),
        ("Where Unresolved Signals Remain",        "where_unresolved_signals_remain"),
        ("Where Objections Exist",                 "where_objections_exist"),
        ("Where Bridge Candidates Require Review", "where_bridge_candidates_require_review"),
    ]:
        items = interp.get(key, [])
        if items:
            lines.append(f"### {heading}")
            lines.append("")
            for item in items:
                lines.append(f"- {item}")
            lines.append("")

    # Invariants
    lines += [
        "## Invariants",
        "",
        "| Field | Value |",
        "|-------|-------|",
    ]
    for k, v in SUMMARY_INVARIANTS.items():
        val = str(v).lower() if isinstance(v, bool) else v
        lines.append(f"| `{k}` | `{val}` |")
    lines += [
        "",
        "## Phase 30 Protocol Phrases",
        "",
    ]
    for phrase in report.get("phase_phrases", []):
        lines.append(f"- *{phrase}*")
    lines += [
        "",
        "---",
        "",
        "*Dan-Go Cross-Phase Contribution Summary · authority: none · advisory · not proof of impact*",
    ]
    return "\n".join(lines)


# ─── Save ───────────────────────────────────────────────────────────────────────

def save_report(report: dict) -> None:
    _REPORTS_DIR.mkdir(exist_ok=True)

    json_path = _REPORTS_DIR / "cross_phase_contribution_summary.json"
    json_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Saved: {json_path}")

    md_path = _REPORTS_DIR / "cross_phase_contribution_summary.md"
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
            print("Usage: cross_phase_contribution_summary.py show-globe <globe_id>")
            sys.exit(1)
        report = build_summary()
        print_globe(report, argv[1])

    elif cmd == "show-section":
        if len(argv) < 2:
            print(f"Usage: cross_phase_contribution_summary.py show-section <section>")
            print(f"Sections: {', '.join(sorted(VALID_SECTIONS))}")
            sys.exit(1)
        report = build_summary()
        print_section(report, argv[1])

    else:
        print(f"Unknown command: {cmd}")
        _usage()


if __name__ == "__main__":
    main(sys.argv[1:])
