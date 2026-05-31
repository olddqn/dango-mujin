#!/usr/bin/env python3
"""
bridge_target_linker.py — Bridge Target Detail Link (Phase 27b)
Dan-Go × GITSEA — Globe Execution Layer

Reads Phase 27 Reality Feedback Bridge records and generates advisory link
candidates connecting each bridge record to specific Phase 18 Relief Case Memory
or Phase 19 Care Loop Reopen items in the repository.

Bridge target link is advisory only.
Link candidate is not proof of case relation.
Link candidate creates no legal authority.
Link candidate does not reopen a case automatically.
Human review is required before any real-world action.

authority: none · advisory · non-coercive · stdlib only

Usage:
    python3 globe/runtime/bridge_target_linker.py summary
    python3 globe/runtime/bridge_target_linker.py save
    python3 globe/runtime/bridge_target_linker.py show-feedback <feedback_id>
    python3 globe/runtime/bridge_target_linker.py show-globe <globe_id>
    python3 globe/runtime/bridge_target_linker.py show-target <relief_case_memory|care_loop_reopen>
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_GLOBE_DIR   = Path(__file__).resolve().parents[1]
_REPO_ROOT   = _GLOBE_DIR.parents[0]
_REPORTS_DIR = _GLOBE_DIR / "reports"

# ─── Phase 27b invariants ────────────────────────────────────────────────────────

LINK_INVARIANTS = {
    "bridge_target_link_is_advisory_only":            True,
    "link_candidate_is_not_proof_of_case_relation":   True,
    "link_candidate_creates_no_legal_authority":       True,
    "link_candidate_does_not_reopen_case_automatically": True,
    "human_review_is_required_before_any_real_world_action": True,
    "authority": "none",
}

LINK_PHRASES = [
    "Bridge target link is advisory only.",
    "Link candidate is not proof of case relation.",
    "Link candidate creates no legal authority.",
    "Link candidate does not reopen a case automatically.",
    "Human review is required before any real-world action.",
]

# ─── Phase 18 / Phase 19 canonical data paths (relative to repo root) ──────────

RELIEF_PATHS = {
    "relief_case_registry": "bridge/gitsea/relief/examples/relief-case-registry.json",
    "care_memory":          "bridge/gitsea/relief/examples/care-memory.json",
    "relief_outcome":       "bridge/gitsea/relief/examples/relief-outcome-snapshot.json",
    "relief_memory_report": "bridge/gitsea/relief/examples/relief-memory-report.json",
}

CARE_PATHS = {
    "care_reopen_registry": "bridge/gitsea/care_loop/examples/care-reopen-registry.json",
    "care_loop":            "bridge/gitsea/care_loop/examples/care-loop.json",
    "followup_snapshot":    "bridge/gitsea/care_loop/examples/followup-need-snapshot.json",
    "care_loop_report":     "bridge/gitsea/care_loop/examples/care-loop-report.json",
}

# ─── Commons keyword map ─────────────────────────────────────────────────────────

COMMONS_KEYWORDS: dict = {
    "dra-001":           ["d.r.a", "dra", "難民支援行動", "refugee relief action"],
    "jammy-house-001":   ["jammy", "jammy house", "jammy-house"],
    "yacypherpunks-001": ["yacypherpunks", "yacy"],
}

# Keywords for scoring
REFUGEE_KEYWORDS = ["refugee", "難民", "displacement", "避難", "shelter", "シェルター",
                    "displaced", "asylum"]
HOUSING_KEYWORDS = ["housing", "住居", "tenancy", "tenant", "テナンシー", "テナント",
                    "eviction", "立ち退き"]
CARE_KEYWORDS    = ["care", "reopen", "再開", "継続", "follow", "フォロー", "loop",
                    "ループ", "followup", "follow-up"]

_CONFIDENCE_RANK = {"high": 3, "medium": 2, "low": 1}

_CONFIDENCE_ICON = {"high": "🔴", "medium": "🟡", "low": "⚪"}


# ─── Data loading ────────────────────────────────────────────────────────────────

def _load_bridge_report() -> dict | None:
    """Load the Phase 27 Reality Feedback Bridge report."""
    p = _REPORTS_DIR / "reality_feedback_bridge.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    # Fall back: build on the fly
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "reality_feedback_bridge",
            Path(__file__).parent / "reality_feedback_bridge.py",
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.build_bridge()
    except Exception:
        return None


def _load_json_safe(rel_path: str) -> dict:
    """Load JSON relative to repo root. Returns {} on any error."""
    p = _REPO_ROOT / rel_path
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


# ─── Commons detection ───────────────────────────────────────────────────────────

def _detect_commons(content_lower: str) -> list:
    """Return list of commons_ids whose keywords appear in content."""
    found = []
    for commons_id, keywords in COMMONS_KEYWORDS.items():
        if any(k.lower() in content_lower for k in keywords):
            found.append(commons_id)
    return found


# ─── Scoring ────────────────────────────────────────────────────────────────────

def _score_relief_case(case: dict, content_lower: str, detected_commons: list) -> tuple:
    """
    Score a relief_case dict against feedback content.
    Returns (confidence, reason).
    """
    case_commons = case.get("commons_id", "")
    case_type    = case.get("case_type", "").lower()
    desc         = case.get("description", "").lower()
    case_text    = case_type + " " + desc

    commons_match    = case_commons in detected_commons
    relief_kws       = REFUGEE_KEYWORDS + HOUSING_KEYWORDS
    content_has_kw   = any(k.lower() in content_lower for k in relief_kws)
    case_has_kw      = any(k.lower() in case_text     for k in relief_kws)

    if commons_match and case_has_kw:
        return (
            "high",
            f"commons_id match ({case_commons} detected in feedback content) + "
            f"case_type '{case.get('case_type','')}' contains matching relief/housing keywords",
        )
    if commons_match:
        return (
            "medium",
            f"commons_id match ({case_commons} detected in feedback content) — "
            f"case is in the same commons referenced by the feedback",
        )
    if case_has_kw and content_has_kw:
        return (
            "medium",
            f"keyword overlap: feedback content and case '{case.get('relief_case_id','')}' "
            f"share relief/housing-related terms",
        )
    return (
        "low",
        f"indirect relevance — case type '{case.get('case_type','')}' is a Phase 18 relief case",
    )


def _score_care_reopen(reopen: dict, content_lower: str, detected_commons: list) -> tuple:
    """
    Score a care_reopen dict against feedback content.
    Returns (confidence, reason).
    """
    reopen_commons = reopen.get("commons_id", "")
    reopen_reason  = reopen.get("reopen_reason", "").lower()
    desc           = reopen.get("description", "").lower()
    reopen_text    = reopen_reason + " " + desc

    commons_match  = reopen_commons in detected_commons
    all_kws        = CARE_KEYWORDS + REFUGEE_KEYWORDS + HOUSING_KEYWORDS
    content_has_kw = any(k.lower() in content_lower for k in all_kws)
    reopen_has_kw  = any(k.lower() in reopen_text   for k in all_kws)

    if commons_match and reopen_has_kw:
        return (
            "high",
            f"commons_id match ({reopen_commons} detected in feedback content) + "
            f"reopen_reason '{reopen.get('reopen_reason','')}' is related to the feedback",
        )
    if commons_match:
        return (
            "medium",
            f"commons_id match ({reopen_commons} detected in feedback content) — "
            f"reopen is in the same commons referenced by the feedback",
        )
    if reopen_has_kw and content_has_kw:
        return (
            "medium",
            f"keyword overlap: feedback content and reopen '{reopen.get('reopen_id','')}' "
            f"share care/reopen-related terms",
        )
    return (
        "low",
        f"indirect relevance — reopen_reason '{reopen.get('reopen_reason','')}' is a Phase 19 care loop reopen",
    )


# ─── Candidate factory ───────────────────────────────────────────────────────────

def _make_candidate(
    record: dict,
    seq: int,
    target_type: str,
    path: str | None,
    item_id: str | None,
    item_type: str | None,
    candidate_description: str,
    confidence: str,
    match_reason: str,
) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "link_id":                  f"lnk-{seq:03d}",
        "source_feedback_id":       record.get("feedback_id", ""),
        "source_directive_id":      record.get("source_directive_id", ""),
        "globe_id":                 record.get("globe_id", ""),
        "suggested_bridge_target":  record.get("suggested_bridge_target", "none"),
        "candidate_target_type":    target_type,
        "candidate_path":           path,
        "candidate_item_id":        item_id,
        "candidate_item_type":      item_type,
        "candidate_description":    candidate_description,
        "match_reason":             match_reason,
        "confidence":               confidence,
        "requires_human_review":    True,
        "creates_no_legal_authority": True,
        "does_not_reopen_case_automatically": True,
        "advisory_only":            True,
        "created_at":               now,
    }


# ─── Candidate generators ────────────────────────────────────────────────────────

def _relief_candidates(record: dict, seq_start: int) -> list:
    """Generate relief_case_memory link candidates for a bridge record."""
    content_lower    = record.get("content", "").lower()
    detected_commons = _detect_commons(content_lower)
    candidates: list = []
    seq = seq_start

    registry = _load_json_safe(RELIEF_PATHS["relief_case_registry"])
    for case in registry.get("cases", []):
        confidence, reason = _score_relief_case(case, content_lower, detected_commons)
        if confidence in ("high", "medium"):
            desc = case.get("description", "")
            extra = (
                f"case_type: {case.get('case_type','')}  "
                f"commons: {case.get('commons_id','')}  "
                f"status: {case.get('case_status','')}"
            )
            candidates.append(_make_candidate(
                record=record, seq=seq,
                target_type="relief_case_memory",
                path=RELIEF_PATHS["relief_case_registry"],
                item_id=case.get("relief_case_id", ""),
                item_type="relief_case",
                candidate_description=desc,
                confidence=confidence,
                match_reason=f"{reason}  [{extra}]",
            ))
            seq += 1

    if not candidates:
        # File-level fallback
        candidates.append(_make_candidate(
            record=record, seq=seq,
            target_type="relief_case_memory",
            path=RELIEF_PATHS["relief_case_registry"],
            item_id=None,
            item_type="relief_case_registry",
            candidate_description="Phase 18 Relief Case Registry — no specific case matched by keyword/commons",
            confidence="low",
            match_reason=(
                "suggested_bridge_target is relief_case_memory; no specific case matched "
                "by commons_id or relief/housing keywords in feedback content — "
                "file-level candidate only; human review required"
            ),
        ))

    return candidates


def _care_candidates(record: dict, seq_start: int) -> list:
    """Generate care_loop_reopen link candidates for a bridge record."""
    content_lower    = record.get("content", "").lower()
    detected_commons = _detect_commons(content_lower)
    candidates: list = []
    seq = seq_start

    registry = _load_json_safe(CARE_PATHS["care_reopen_registry"])
    for reopen in registry.get("reopens", []):
        confidence, reason = _score_care_reopen(reopen, content_lower, detected_commons)
        if confidence in ("high", "medium"):
            desc = reopen.get("description", "")
            extra = (
                f"reopen_reason: {reopen.get('reopen_reason','')}  "
                f"commons: {reopen.get('commons_id','')}  "
                f"status: {reopen.get('reopen_status','')}"
            )
            candidates.append(_make_candidate(
                record=record, seq=seq,
                target_type="care_loop_reopen",
                path=CARE_PATHS["care_reopen_registry"],
                item_id=reopen.get("reopen_id", ""),
                item_type="care_reopen",
                candidate_description=desc,
                confidence=confidence,
                match_reason=f"{reason}  [{extra}]",
            ))
            seq += 1

    if not candidates:
        candidates.append(_make_candidate(
            record=record, seq=seq,
            target_type="care_loop_reopen",
            path=CARE_PATHS["care_reopen_registry"],
            item_id=None,
            item_type="care_reopen_registry",
            candidate_description="Phase 19 Care Loop Reopen Registry — no specific reopen matched by keyword/commons",
            confidence="low",
            match_reason=(
                "suggested_bridge_target is care_loop_reopen; no specific reopen matched "
                "by commons_id or care/reopen keywords in feedback content — "
                "file-level candidate only; human review required"
            ),
        ))

    return candidates


def _no_candidate(record: dict, seq: int) -> dict:
    """Produce a no-candidate record for bridge records with target 'none'."""
    return _make_candidate(
        record=record, seq=seq,
        target_type="none",
        path=None,
        item_id=None,
        item_type=None,
        candidate_description="No bridge target suggested — no link candidate generated",
        confidence="low",
        match_reason=(
            "suggested_bridge_target is 'none' — no automated link candidate generated; "
            "human review may identify a Phase 18 or Phase 19 connection"
        ),
    )


# ─── Report builder ──────────────────────────────────────────────────────────────

def build_links() -> dict:
    """Build the full Bridge Target Links report."""
    bridge_report = _load_bridge_report()
    if not bridge_report:
        return {
            "link_report_id": "bridge-target-links-001",
            **LINK_INVARIANTS,
            "phase": "27b",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_feedback_records": 0,
            "total_link_candidates": 0,
            "confidence_counts": {"high": 0, "medium": 0, "low": 0},
            "candidates": [],
            "by_feedback": [],
            "phase_phrases": LINK_PHRASES,
            "error": (
                "reality_feedback_bridge.json not found — "
                "run: python3 globe/runtime/reality_feedback_bridge.py save"
            ),
        }

    records = bridge_report.get("records", [])
    candidates: list = []
    seq = 1

    for record in records:
        target = record.get("suggested_bridge_target", "none")

        if target == "none":
            candidates.append(_no_candidate(record, seq))
            seq += 1

        if target in ("relief_case_memory", "both"):
            new = _relief_candidates(record, seq)
            candidates.extend(new)
            seq += len(new)

        if target in ("care_loop_reopen", "both"):
            new = _care_candidates(record, seq)
            candidates.extend(new)
            seq += len(new)

    # Aggregate by feedback_id
    by_feedback_map: dict = {}
    for c in candidates:
        fid = c["source_feedback_id"]
        if fid not in by_feedback_map:
            by_feedback_map[fid] = {
                "feedback_id":           fid,
                "source_directive_id":   c["source_directive_id"],
                "globe_id":              c["globe_id"],
                "suggested_bridge_target": c["suggested_bridge_target"],
                "candidate_count":       0,
                "high_count":   0,
                "medium_count": 0,
                "low_count":    0,
            }
        bf = by_feedback_map[fid]
        bf["candidate_count"] += 1
        bf[f"{c['confidence']}_count"] += 1

    confidence_counts: dict = {"high": 0, "medium": 0, "low": 0}
    for c in candidates:
        conf = c["confidence"]
        confidence_counts[conf] = confidence_counts.get(conf, 0) + 1

    now = datetime.now(timezone.utc).isoformat()
    return {
        "link_report_id": "bridge-target-links-001",
        **LINK_INVARIANTS,
        "phase": "27b",
        "generated_at": now,
        "total_feedback_records": len(records),
        "total_link_candidates":  len(candidates),
        "confidence_counts":      confidence_counts,
        "candidates":             candidates,
        "by_feedback":            list(by_feedback_map.values()),
        "phase_phrases":          LINK_PHRASES,
    }


# ─── CLI display ─────────────────────────────────────────────────────────────────

def _print_invariants() -> None:
    print("  Invariants:")
    for k, v in LINK_INVARIANTS.items():
        print(f"    {k}: {str(v).lower()}")


def _print_candidate(c: dict, indent: str = "  ") -> None:
    icon = _CONFIDENCE_ICON.get(c["confidence"], "?")
    print(f"{indent}{icon} [{c['link_id']}] {c['confidence'].upper()}  {c['candidate_target_type']}")
    if c.get("candidate_item_id"):
        print(f"{indent}   item_id:  {c['candidate_item_id']}  ({c.get('candidate_item_type','')})")
    if c.get("candidate_path"):
        print(f"{indent}   path:     {c['candidate_path']}")
    desc = c.get("candidate_description", "")
    if desc:
        print(f"{indent}   desc:     {desc[:80]}{'...' if len(desc) > 80 else ''}")
    reason = c.get("match_reason", "")
    if reason:
        print(f"{indent}   reason:   {reason[:90]}{'...' if len(reason) > 90 else ''}")
    print(f"{indent}   requires_human_review: true  |  creates_no_legal_authority: true")
    print(f"{indent}   does_not_reopen_case_automatically: true  |  advisory_only: true")


def print_summary(report: dict) -> None:
    print("Bridge Target Links Report (Phase 27b)")
    print("=" * 60)
    gen = str(report.get("generated_at", ""))[:19].replace("T", " ")
    print(f"  generated_at:            {gen}")
    print(f"  total_feedback_records:  {report.get('total_feedback_records', 0)}")
    print(f"  total_link_candidates:   {report.get('total_link_candidates', 0)}")
    cc = report.get("confidence_counts", {})
    print(f"  🔴 high:     {cc.get('high', 0)}")
    print(f"  🟡 medium:   {cc.get('medium', 0)}")
    print(f"  ⚪ low:      {cc.get('low', 0)}")

    if report.get("error"):
        print(f"\n  ⚠ {report['error']}")

    print()
    _print_invariants()

    print()
    print("By Feedback Record:")
    print("-" * 60)
    for bf in report.get("by_feedback", []):
        icon = {"high": "🔴", "medium": "🟡", "low": "⚪"}.get(
            "high" if bf["high_count"] else "medium" if bf["medium_count"] else "low", "⚪"
        )
        print(
            f"  {icon} {bf['feedback_id']}  →  {bf['suggested_bridge_target']}"
            f"   candidates: {bf['candidate_count']}"
            f"  (high: {bf['high_count']}  medium: {bf['medium_count']}  low: {bf['low_count']})"
        )

    print()
    print("Phase 27b phrases:")
    for phrase in report.get("phase_phrases", []):
        print(f"  \"{phrase}\"")


def print_feedback(report: dict, feedback_id: str) -> None:
    candidates = [c for c in report.get("candidates", []) if c["source_feedback_id"] == feedback_id]
    if not candidates:
        print(f"No link candidates found for feedback_id: {feedback_id}")
        return
    bf = next((b for b in report.get("by_feedback", []) if b["feedback_id"] == feedback_id), {})
    print(f"Bridge Target Links — {feedback_id}")
    print("=" * 60)
    print(f"  source_directive: {bf.get('source_directive_id', '')}")
    print(f"  suggested_target: {bf.get('suggested_bridge_target', '')}")
    print(f"  candidates:       {len(candidates)}")
    print()
    for c in candidates:
        _print_candidate(c)
        print()


def print_globe(report: dict, globe_id: str) -> None:
    candidates = [c for c in report.get("candidates", []) if c["globe_id"] == globe_id]
    if not candidates:
        print(f"No link candidates found for globe: {globe_id}")
        return
    print(f"Bridge Target Links — {globe_id}")
    print("=" * 60)
    print(f"  candidates: {len(candidates)}")
    print()
    for c in candidates:
        _print_candidate(c)
        print()


def print_target(report: dict, target_type: str) -> None:
    candidates = [
        c for c in report.get("candidates", [])
        if c["candidate_target_type"] == target_type
    ]
    if not candidates:
        print(f"No link candidates with candidate_target_type: {target_type}")
        return
    print(f"Bridge Target Links — {target_type}")
    print("=" * 60)
    print(f"  candidates: {len(candidates)}")
    print()
    for c in candidates:
        fid = c.get("source_feedback_id", "?")
        print(f"  ← {fid}  (source: {c.get('source_directive_id','')})")
        _print_candidate(c, indent="    ")
        print()


# ─── Markdown export ─────────────────────────────────────────────────────────────

def _build_markdown(report: dict) -> str:
    gen = str(report.get("generated_at", ""))[:19].replace("T", " ")
    cc  = report.get("confidence_counts", {})
    lines = [
        "# Bridge Target Links Report (Phase 27b)",
        "",
        "> **Bridge target link is advisory only.**",
        "> **Link candidate is not proof of case relation.**",
        "> **Link candidate creates no legal authority.**",
        "> **Link candidate does not reopen a case automatically.**",
        "> **Human review is required before any real-world action.**",
        "",
        f"Generated: {gen}",
        "",
        "## Summary",
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| total_feedback_records | {report.get('total_feedback_records', 0)} |",
        f"| total_link_candidates | {report.get('total_link_candidates', 0)} |",
        f"| 🔴 high | {cc.get('high', 0)} |",
        f"| 🟡 medium | {cc.get('medium', 0)} |",
        f"| ⚪ low | {cc.get('low', 0)} |",
        f"| authority | none |",
        "",
    ]

    lines += ["## By Feedback Record", ""]
    for bf in report.get("by_feedback", []):
        lines.append(
            f"- **{bf['feedback_id']}** → `{bf['suggested_bridge_target']}`  "
            f"candidates: {bf['candidate_count']}  "
            f"(high: {bf['high_count']}  medium: {bf['medium_count']}  low: {bf['low_count']})"
        )
    lines.append("")

    lines += ["## All Link Candidates", ""]
    for c in report.get("candidates", []):
        icon = _CONFIDENCE_ICON.get(c["confidence"], "?")
        lines += [
            f"### {c['link_id']}  {icon} {c['confidence'].upper()}",
            f"- source_feedback_id: `{c['source_feedback_id']}`",
            f"- source_directive_id: `{c['source_directive_id']}`",
            f"- suggested_bridge_target: `{c['suggested_bridge_target']}`",
            f"- **candidate_target_type:** `{c['candidate_target_type']}`",
            f"- candidate_path: `{c.get('candidate_path') or 'null'}`",
            f"- candidate_item_id: `{c.get('candidate_item_id') or 'null'}`",
            f"- candidate_item_type: `{c.get('candidate_item_type') or 'null'}`",
            f"- candidate_description: {c.get('candidate_description', '')}",
            f"- match_reason: {c.get('match_reason', '')}",
            f"- confidence: **{c['confidence']}**",
            f"- requires_human_review: true",
            f"- creates_no_legal_authority: true",
            f"- does_not_reopen_case_automatically: true",
            f"- advisory_only: true",
            "",
        ]

    lines += [
        "---",
        "",
        "*Bridge target link is advisory only.*",
        "*Link candidate is not proof of case relation.*",
        "*Link candidate creates no legal authority.*",
        "*Link candidate does not reopen a case automatically.*",
        "*Human review is required before any real-world action.*",
    ]
    return "\n".join(lines)


def save_report(report: dict) -> None:
    _REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = _REPORTS_DIR / "bridge_target_links.json"
    md_path   = _REPORTS_DIR / "bridge_target_links.md"
    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    md_path.write_text(_build_markdown(report), encoding="utf-8")
    print_summary(report)
    print()
    print(f"Saved: {json_path}")
    print(f"Saved: {md_path}")


# ─── CLI dispatcher ──────────────────────────────────────────────────────────────

def main(argv: list) -> None:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return

    cmd = argv[0]

    if cmd == "summary":
        print_summary(build_links())

    elif cmd == "save":
        save_report(build_links())

    elif cmd == "show-feedback":
        if len(argv) < 2:
            print("Usage: bridge_target_linker.py show-feedback <feedback_id>")
            sys.exit(1)
        print_feedback(build_links(), argv[1])

    elif cmd == "show-globe":
        if len(argv) < 2:
            print("Usage: bridge_target_linker.py show-globe <globe_id>")
            sys.exit(1)
        print_globe(build_links(), argv[1])

    elif cmd == "show-target":
        if len(argv) < 2:
            print("Usage: bridge_target_linker.py show-target <relief_case_memory|care_loop_reopen>")
            sys.exit(1)
        print_target(build_links(), argv[1])

    else:
        print(f"Unknown command: {cmd}")
        print("Commands: summary  save  show-feedback <id>  show-globe <id>  show-target <type>")
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
