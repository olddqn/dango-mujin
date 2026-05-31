"""proposal_compare.py — Phase 33: Proposal Comparison View

Builds a side-by-side advisory comparison of two Proposals across all
Globe-layer artifacts (deliberations, claim, directive, execution log,
bridge feedback, link candidates, timeline).

INVARIANTS (permanent, not negotiable):
  Comparison is advisory display only.
  Comparison is not ranking.
  Comparison does not score proposals.
  Comparison does not allocate resources.
  Human review is required before any real-world action.
  authority: none

Difference display:
  Fields that differ are listed as observations — not as judgements,
  not as "better / worse", not as scores.

CLI:
  python3 globe/runtime/proposal_compare.py list
  python3 globe/runtime/proposal_compare.py compare <proposal_id_a> <proposal_id_b>
  python3 globe/runtime/proposal_compare.py save <proposal_id_a> <proposal_id_b>
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

# ─── Invariants ───────────────────────────────────────────────────────────────

COMPARE_INVARIANTS = {
    "comparison_is_advisory_display_only": True,
    "comparison_is_not_ranking": True,
    "comparison_does_not_score_proposals": True,
    "comparison_does_not_allocate_resources": True,
    "human_review_is_required_before_any_real_world_action": True,
    "authority": "none",
}

COMPARE_PHRASES = [
    "Comparison is advisory display only.",
    "Comparison is not ranking.",
    "Comparison does not score proposals.",
    "Comparison does not allocate resources.",
    "Human review is required before any real-world action.",
]

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
    items = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                items.append(json.loads(line))
            except Exception:
                pass
    return items


def _excerpt(text: str | None, max_len: int = 200) -> str:
    if not text:
        return ""
    text = " ".join(str(text).split())
    return text[:max_len] + ("…" if len(text) > max_len else "")


# ─── Data loaders ─────────────────────────────────────────────────────────────

def _all_proposals() -> list[dict]:
    data = _load_json(_DATA_DIR / "proposals.json")
    return data if isinstance(data, list) else []


def _get_proposal(proposal_id: str) -> dict | None:
    for p in _all_proposals():
        if p.get("proposal_id") == proposal_id:
            return p
    return None


def _deliberations_for(proposal_id: str) -> list[dict]:
    data = _load_json(_DATA_DIR / "deliberations.json")
    if not isinstance(data, list):
        return []
    return [d for d in data if d.get("proposal_id") == proposal_id]


def _claim_for(proposal_id: str) -> dict | None:
    return _load_json(_CLAIMS_DIR / f"claim-{proposal_id}.json")


def _directive_for(proposal_id: str) -> dict | None:
    return _load_json(_DIRECTIVES_DIR / f"directive-claim-{proposal_id}.json")


def _log_entries_for_directive(directive_id: str) -> list[dict]:
    return _load_jsonl(_LOGS_DIR / f"{directive_id}.jsonl")


def _bridge_records_for_directive(directive_id: str) -> list[dict]:
    data = _load_json(_REPORTS_DIR / "reality_feedback_bridge.json")
    if not isinstance(data, dict):
        return []
    return [r for r in data.get("records", [])
            if r.get("source_directive_id") == directive_id]


def _link_candidates_for_directive(directive_id: str) -> list[dict]:
    data = _load_json(_REPORTS_DIR / "bridge_target_links.json")
    if not isinstance(data, dict):
        return []
    return [c for c in data.get("candidates", [])
            if c.get("source_directive_id") == directive_id]


def _timeline_items_for_directive(directive_id: str) -> list[dict]:
    data = _load_json(_REPORTS_DIR / "contribution_timeline.json")
    if not isinstance(data, dict):
        return []
    return [it for it in data.get("items", [])
            if it.get("directive_id") == directive_id]


# ─── Proposal snapshot ────────────────────────────────────────────────────────

def _build_snapshot(proposal_id: str) -> dict:
    """Build a single-proposal data snapshot for comparison.

    Returns a flat dict of comparable fields.
    Advisory only — not a score, not a judgement.
    """
    p = _get_proposal(proposal_id)
    if not p:
        return {"error": f"proposal not found: {proposal_id}"}

    delibs = _deliberations_for(proposal_id)
    claim  = _claim_for(proposal_id)
    directive = _directive_for(proposal_id)

    directive_id = directive["directive_id"] if directive else f"directive-claim-{proposal_id}"
    log_entries   = _log_entries_for_directive(directive_id) if directive else []
    bridge_recs   = _bridge_records_for_directive(directive_id)
    link_cands    = _link_candidates_for_directive(directive_id)
    tl_items      = _timeline_items_for_directive(directive_id)

    # Log entry type counts
    log_counts: dict[str, int] = {}
    latest_rs = ""
    for e in log_entries:
        et = e.get("entry_type", "")
        log_counts[et] = log_counts.get(et, 0) + 1
        if et == "voluntary_resolution_signal" and e.get("resolution_status"):
            latest_rs = e["resolution_status"]

    # Link confidence counts
    high_links = sum(1 for c in link_cands if c.get("confidence") == "high")

    snap: dict = {
        # Proposal core
        "proposal_id":    proposal_id,
        "title":          p.get("title", ""),
        "body_excerpt":   _excerpt(p.get("body", "")),
        "status":         p.get("status", ""),
        "proposer":       p.get("proposer", ""),
        "globe_id":       p.get("globe_id", ""),
        "created_at":     p.get("created_at", "")[:10],
        # Deliberation
        "deliberation_count": len(delibs),
        # Claim
        "claim_exists":  claim is not None,
        "claim_id":      claim.get("claim_id", "") if claim else "",
        "claim_status":  claim.get("status", "") if claim else "",
        # Directive
        "directive_exists":  directive is not None,
        "directive_id":      directive.get("directive_id", "") if directive else "",
        "directive_status":  directive.get("status", "") if directive else "",
        # Execution Log
        "log_entry_count":                 len(log_entries),
        "human_approval_count":            log_counts.get("human_approval", 0),
        "observation_count":               log_counts.get("observation", 0),
        "feedback_count":                  log_counts.get("feedback", 0),
        "objection_count":                 log_counts.get("objection", 0),
        "rollback_request_count":          log_counts.get("rollback_request", 0),
        "voluntary_resolution_signal_count": log_counts.get("voluntary_resolution_signal", 0),
        "latest_resolution_status":        latest_rs,
        # Bridge / Links
        "bridge_record_count":     len(bridge_recs),
        "link_candidate_count":    len(link_cands),
        "high_confidence_links":   high_links,
        # Timeline
        "timeline_item_count":     len(tl_items),
    }
    return snap


# ─── Comparison builder ───────────────────────────────────────────────────────

# Fields where we surface differences (no scoring — just observations)
_DIFF_FIELDS = [
    ("status",                          "Proposal status"),
    ("globe_id",                        "Globe"),
    ("deliberation_count",              "Deliberation entries"),
    ("claim_exists",                    "Claim converted"),
    ("claim_status",                    "Claim status"),
    ("directive_exists",                "Directive converted"),
    ("directive_status",                "Directive status"),
    ("log_entry_count",                 "Execution log entries"),
    ("human_approval_count",            "Human approvals"),
    ("objection_count",                 "Objections"),
    ("rollback_request_count",          "Rollback requests"),
    ("voluntary_resolution_signal_count","Resolution signals"),
    ("latest_resolution_status",        "Latest resolution status"),
    ("bridge_record_count",             "Bridge feedback records"),
    ("link_candidate_count",            "Link candidates"),
    ("high_confidence_links",           "High-confidence links"),
    ("timeline_item_count",             "Timeline items"),
]


def build_comparison(proposal_id_a: str, proposal_id_b: str) -> dict:
    """Build an advisory comparison between two proposals.

    Advisory only. Not ranking. No score. No allocation.
    """
    snap_a = _build_snapshot(proposal_id_a)
    snap_b = _build_snapshot(proposal_id_b)

    # Surface observable differences — not judgements
    differences: list[dict] = []
    for field, label in _DIFF_FIELDS:
        val_a = snap_a.get(field)
        val_b = snap_b.get(field)
        if val_a != val_b:
            differences.append({
                "field":  field,
                "label":  label,
                "value_a": val_a,
                "value_b": val_b,
                "observation": f"{label} differs: {val_a!r} vs {val_b!r}",
            })

    # Common attributes
    same: list[str] = []
    for field, label in _DIFF_FIELDS:
        if snap_a.get(field) == snap_b.get(field):
            same.append(field)

    return {
        "comparison_id": f"compare-{proposal_id_a}-vs-{proposal_id_b}",
        "generated_at":  _now(),
        "proposal_a":    proposal_id_a,
        "proposal_b":    proposal_id_b,
        **COMPARE_INVARIANTS,
        "phase":         "33",
        "phase_phrases": COMPARE_PHRASES,
        "snapshot_a":    snap_a,
        "snapshot_b":    snap_b,
        "difference_count": len(differences),
        "differences":   differences,
        "same_fields":   same,
        "comparison_note": (
            "Differences are observable distinctions only. "
            "They are not scores, rankings, or judgements of quality. "
            "Human review is required before any real-world action."
        ),
    }


# ─── Persistence ──────────────────────────────────────────────────────────────

def _report_paths(id_a: str, id_b: str) -> tuple[Path, Path]:
    base = f"proposal_comparison_{id_a}_vs_{id_b}"
    return _REPORTS_DIR / f"{base}.json", _REPORTS_DIR / f"{base}.md"


def _build_markdown(cmp: dict) -> str:
    id_a = cmp["proposal_a"]
    id_b = cmp["proposal_b"]
    sa   = cmp["snapshot_a"]
    sb   = cmp["snapshot_b"]
    lines: list[str] = []
    lines.append(f"# Proposal Comparison — {id_a} vs {id_b} (Phase 33)")
    lines.append("")
    lines.append(f"generated_at: {cmp['generated_at']}")
    lines.append("")
    lines.append("## Invariants")
    lines.append("")
    lines.append("| Key | Value |")
    lines.append("|-----|-------|")
    for k, v in COMPARE_INVARIANTS.items():
        lines.append(f"| `{k}` | `{v}` |")
    lines.append("")
    lines.append(f"> {cmp['comparison_note']}")
    lines.append("")
    lines.append("## Side-by-Side")
    lines.append("")
    lines.append(f"| Field | {id_a} | {id_b} |")
    lines.append("|-------|-------|-------|")
    for field, label in _DIFF_FIELDS:
        va = sa.get(field, "")
        vb = sb.get(field, "")
        diff_mark = " ◀" if va != vb else ""
        lines.append(f"| {label} | `{va}` | `{vb}`{diff_mark} |")
    lines.append("")
    lines.append(f"## Differences ({cmp['difference_count']})")
    lines.append("")
    lines.append("> Differences are observable distinctions, not scores or rankings.")
    lines.append("")
    if cmp["differences"]:
        for d in cmp["differences"]:
            lines.append(f"- **{d['label']}**: `{d['value_a']}` vs `{d['value_b']}`")
    else:
        lines.append("_No differences observed._")
    lines.append("")
    for phrase in COMPARE_PHRASES:
        lines.append(f"> \"{phrase}\"")
    return "\n".join(lines)


def save_comparison(id_a: str, id_b: str) -> tuple[Path, Path]:
    cmp = build_comparison(id_a, id_b)
    _REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path, md_path = _report_paths(id_a, id_b)
    json_path.write_text(json.dumps(cmp, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(_build_markdown(cmp), encoding="utf-8")
    return json_path, md_path


# ─── CLI print helpers ────────────────────────────────────────────────────────

_RS_ICON = {
    "resolved": "✅", "partially_resolved": "🟡", "paused": "⏸️",
    "unresolved": "🔴", "contested": "⚔️",
}

_STATUS_ICON = {
    "accepted": "✅", "discussion": "💬", "draft": "📝",
    "voting": "🗳️", "rejected": "❌", "archived": "📦",
}


def _fmt_val(field: str, val: object) -> str:
    if field == "latest_resolution_status" and isinstance(val, str) and val:
        return f"{_RS_ICON.get(val, '')} {val}"
    if field == "status" and isinstance(val, str):
        return f"{_STATUS_ICON.get(val, '')} {val}"
    if isinstance(val, bool):
        return "✅ yes" if val else "— no"
    if val == "" or val is None:
        return "—"
    return str(val)


def print_comparison(cmp: dict) -> None:
    id_a = cmp["proposal_a"]
    id_b = cmp["proposal_b"]
    sa   = cmp["snapshot_a"]
    sb   = cmp["snapshot_b"]

    print(f"\nProposal Comparison (Phase 33) — {id_a}  vs  {id_b}")
    print("=" * 70)
    print(f"  generated_at: {cmp['generated_at']}")
    print(f"  ⚠️  {cmp['comparison_note']}")
    print()

    # Titles
    print(f"  [A] {id_a}")
    print(f"      {sa.get('title', '')}")
    print(f"      globe: {sa.get('globe_id','')}  status: {sa.get('status','')}  proposer: {sa.get('proposer','')}")
    print(f"      {sa.get('body_excerpt','')[:80]}")
    print()
    print(f"  [B] {id_b}")
    print(f"      {sb.get('title', '')}")
    print(f"      globe: {sb.get('globe_id','')}  status: {sb.get('status','')}  proposer: {sb.get('proposer','')}")
    print(f"      {sb.get('body_excerpt','')[:80]}")
    print()

    # Side-by-side table
    col_w = 30
    print(f"  {'Field':<28} {'[A]':^22} {'[B]':^22}")
    print(f"  {'-'*28} {'-'*22} {'-'*22}")
    for field, label in _DIFF_FIELDS:
        va = _fmt_val(field, sa.get(field))
        vb = _fmt_val(field, sb.get(field))
        diff = " ◀" if sa.get(field) != sb.get(field) else ""
        print(f"  {label:<28} {va:<22} {vb:<22}{diff}")
    print()

    # Differences
    diffs = cmp.get("differences", [])
    print(f"  Observable differences ({len(diffs)}) — not scores, not rankings:")
    if diffs:
        for d in diffs:
            print(f"    • {d['label']}: {_fmt_val(d['field'], d['value_a'])} vs {_fmt_val(d['field'], d['value_b'])}")
    else:
        print("    No differences observed.")
    print()

    for phrase in COMPARE_PHRASES:
        print(f'  "{phrase}"')


def print_proposal_list() -> None:
    proposals = _all_proposals()
    print(f"\nProposals available for comparison ({len(proposals)}):")
    print("=" * 60)
    for p in proposals:
        pid    = p.get("proposal_id", "")
        title  = p.get("title", "")[:45]
        status = p.get("status", "")
        globe  = p.get("globe_id", "")
        icon   = _STATUS_ICON.get(status, "•")
        has_claim = (_CLAIMS_DIR / f"claim-{pid}.json").exists()
        has_dir   = (_DIRECTIVES_DIR / f"directive-claim-{pid}.json").exists()
        chain = "proposal"
        if has_claim:
            chain += " → claim"
        if has_dir:
            chain += " → directive"
        print(f"  {pid:<15} {icon} {status:<12} globe={globe:<12} {title}")
        print(f"  {'':15} chain: {chain}")
        print()
    print("Usage:")
    print("  python3 globe/runtime/proposal_compare.py compare <id_a> <id_b>")
    print("  python3 globe/runtime/proposal_compare.py save    <id_a> <id_b>")


# ─── CLI entry point ──────────────────────────────────────────────────────────

def main(argv: list[str]) -> None:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return

    cmd = argv[0]

    if cmd == "list":
        print_proposal_list()
        return

    if cmd in ("compare", "save"):
        if len(argv) < 3:
            print(f"Usage: proposal_compare.py {cmd} <proposal_id_a> <proposal_id_b>",
                  file=sys.stderr)
            sys.exit(1)
        id_a, id_b = argv[1], argv[2]
        cmp = build_comparison(id_a, id_b)
        if cmp["snapshot_a"].get("error"):
            print(f"Error: {cmp['snapshot_a']['error']}", file=sys.stderr)
            sys.exit(1)
        if cmp["snapshot_b"].get("error"):
            print(f"Error: {cmp['snapshot_b']['error']}", file=sys.stderr)
            sys.exit(1)
        print_comparison(cmp)
        if cmd == "save":
            json_path, md_path = save_comparison(id_a, id_b)
            print(f"Saved: {json_path}")
            print(f"Saved: {md_path}")
        return

    print(f"Unknown command: {cmd}", file=sys.stderr)
    print("Commands: list | compare <id_a> <id_b> | save <id_a> <id_b>",
          file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
