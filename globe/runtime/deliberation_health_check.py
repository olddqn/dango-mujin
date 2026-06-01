"""
deliberation_health_check.py — Deliberation Health Check (Phase 49)

Reads proposals + deliberations + consensus_discovery + deliberation_round_tracker
and produces, per proposal, an advisory health-check note that surfaces:
  - gaps (no concerns recorded, no common ground, etc.)
  - flags (has_unresolved, has_candidate, etc.)
  - suggested next questions for human reviewers

This is NOT a score, NOT a ranking, NOT a final judgment.
It is a human-readable advisory memo to help reviewers spot blind spots
before continuing deliberation.

INVARIANTS (permanent, all sessions):
    Deliberation health check is advisory display only.
    Health check is not a score.
    Health check is not ranking.
    Health check is not final judgment.
    Health check does not approve execution.
    Human review is required before any real-world action.
    authority: none
    execution_allowed: false
    moves_money: false
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────

_RUNTIME_DIR    = Path(__file__).parent
_GLOBE_DIR      = _RUNTIME_DIR.parent
_DATA_DIR       = _GLOBE_DIR / "data"
_REPORTS_DIR    = _GLOBE_DIR / "reports"

_PROPOSALS_JSON    = _DATA_DIR    / "proposals.json"
_DELIBERATIONS_JSON = _DATA_DIR   / "deliberations.json"
_CD_JSON           = _REPORTS_DIR / "consensus_discovery.json"
_DRT_JSON          = _REPORTS_DIR / "deliberation_round_tracker.json"

# ─── Invariants ───────────────────────────────────────────────────────────────

HEALTH_INVARIANTS: dict[str, object] = {
    "deliberation_health_check_is_advisory_display_only": True,
    "health_check_is_not_a_score":       True,
    "health_check_is_not_ranking":       True,
    "health_check_is_not_final_judgment": True,
    "health_check_does_not_approve_execution": True,
    "human_review_is_required_before_any_real_world_action": True,
    "authority":         "none",
    "execution_allowed": False,
    "moves_money":       False,
    "hard_enforcement":  False,
    "credit_issued":     False,
}

HEALTH_PHRASES: list[str] = [
    "Deliberation health check is advisory display only.",
    "Health check is not a score.",
    "Health check is not ranking.",
    "Health check is not final judgment.",
    "Health check does not approve execution.",
    "Human review is required before any real-world action.",
]

FLAGS: list[str] = [
    "concerns", "objections", "common_ground", "candidate", "unresolved",
]

# ─── Load helpers ─────────────────────────────────────────────────────────────

def _load_json(path: Path) -> list | dict:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []


# ─── Note generation ──────────────────────────────────────────────────────────

def _make_health_notes(
    delib_count:       int,
    issue_count:       int,
    stance_count:      int,
    cg_count:          int,
    conflict_count:    int,
    cand_count:        int,
    misund_count:      int,
    round_count:       int,
    latest_round_type: str,
    has_concerns:      bool,
    has_objections:    bool,
    has_cg:            bool,
    has_candidate:     bool,
    has_unresolved:    bool,
    stance_dist:       dict[str, int],
    status:            str,
) -> list[str]:
    notes: list[str] = []

    # No deliberation data
    if delib_count == 0:
        notes.append(
            "No deliberation data detected for this proposal. "
            "Talk may not have started yet, or data may not be loaded."
        )
        return notes

    # Concerns / objections coverage
    if not has_concerns:
        notes.append(
            "No concerns or objections detected in deliberations. "
            "This may indicate genuine consensus, or that dissenting voices have not yet been recorded."
        )
    else:
        notes.append("Concerns are recorded — possible tension or condition noted.")

    if has_objections:
        notes.append(
            "Objection signals detected. "
            "These are preserved as minority opinions per Dan-Go protocol."
        )

    # Issue coverage
    if issue_count == 0:
        notes.append(
            "No issue keywords detected. "
            "Core questions or discussion topics may not yet be explicitly stated."
        )
    else:
        notes.append(
            f"{issue_count} possible issue(s) detected — may indicate open discussion points."
        )

    # Common ground
    if has_cg:
        notes.append(
            "Common ground candidate(s) present — "
            "possible shared understanding detected, pending human verification."
        )
    else:
        notes.append(
            "No common ground detected yet. "
            "Shared points of agreement may benefit from explicit articulation."
        )

    # Conflict
    if conflict_count > 0:
        notes.append(
            f"{conflict_count} conflict point(s) detected — "
            "possible unresolved disagreements remain."
        )

    # Consensus candidate
    if has_candidate:
        notes.append(
            "Consensus candidate(s) detected. "
            "These are advisory proposals only — not final agreements."
        )

    # Unresolved conditions
    if has_unresolved:
        notes.append(
            "Unresolved conditions noted. "
            "Further deliberation rounds may be needed before advancing."
        )

    # Round progression
    if round_count <= 2:
        notes.append(
            "Deliberation appears to be at an early stage (few rounds). "
            "More voices and perspectives may help broaden the discussion."
        )
    elif latest_round_type == "synthesis_round":
        notes.append(
            "Latest round is a synthesis — discussion is being organised. "
            "Human review of the synthesis is recommended."
        )
    elif latest_round_type == "consensus_candidate_round":
        notes.append(
            "Latest round surfaces a consensus candidate. "
            "Verify that all concerns have been addressed before proceeding."
        )
    elif latest_round_type == "unresolved_condition_round":
        notes.append(
            "Latest round recorded an unresolved condition. "
            "Resolution of this condition should be discussed before advancing."
        )

    # Proposal status context
    if status == "accepted":
        notes.append(
            "Proposal status is 'accepted'. "
            "Advisory: even accepted proposals may have outstanding deliberation items."
        )
    elif status == "draft":
        notes.append(
            "Proposal is in draft status. "
            "Opening this proposal for broader deliberation may surface important perspectives."
        )

    return notes


def _make_suggested_questions(
    delib_count:   int,
    has_concerns:  bool,
    has_objections: bool,
    has_cg:        bool,
    has_candidate: bool,
    has_unresolved: bool,
    issue_count:   int,
    conflict_count: int,
    misund_count:  int,
    status:        str,
) -> list[str]:
    qs: list[str] = []

    if delib_count == 0:
        qs.append("この提案に対してまだ話し合いが始まっていませんか？")
        qs.append("提案の内容は十分に共有されていますか？")
        return qs

    if not has_concerns:
        qs.append("この提案に対する懸念は十分に記録されていますか？")
    if not has_objections:
        qs.append("反対意見や少数意見は保存されていますか？")
    if not has_cg:
        qs.append("参加者間の一致点はまだ整理されていませんか？")
    if has_candidate:
        qs.append("合意候補はまだ仮説として扱われていますか？")
    if has_unresolved:
        qs.append("未解決条件は明示されていますか？どのような条件が残っていますか？")
    if conflict_count > 0:
        qs.append("対立点に対して、すべての立場から応答がありましたか？")
    if misund_count > 0:
        qs.append("誤解の可能性は当事者に確認されましたか？")
    if issue_count == 0:
        qs.append("この提案の核心的な論点は明示されていますか？")

    # Always include a reminder
    qs.append("人間によるレビューが必要です。このメモは advisory のみです。")

    return qs[:6]   # cap at 6


# ─── Build ────────────────────────────────────────────────────────────────────

def build_health_check() -> dict:
    """Build health check items for all proposals."""
    proposals     = _load_json(_PROPOSALS_JSON)
    deliberations = _load_json(_DELIBERATIONS_JSON)
    cd_data       = _load_json(_CD_JSON) if isinstance(_load_json(_CD_JSON), dict) else {}
    drt_data      = _load_json(_DRT_JSON) if isinstance(_load_json(_DRT_JSON), dict) else {}

    # Re-load as dicts (handle list/dict)
    if not isinstance(cd_data, dict):
        cd_data = {}
    if not isinstance(drt_data, dict):
        drt_data = {}

    if isinstance(proposals, dict):
        proposals = list(proposals.values())
    if isinstance(deliberations, dict):
        deliberations = list(deliberations.values())

    # Index counts
    delib_count_by_prop: dict[str, int] = {}
    for d in deliberations:
        pid = d.get("proposal_id", "")
        delib_count_by_prop[pid] = delib_count_by_prop.get(pid, 0) + 1

    # Index consensus_discovery summaries
    cd_by_prop: dict[str, dict] = {
        ps.get("proposal_id", ""): ps
        for ps in cd_data.get("proposal_summaries", [])
    }

    # Index deliberation_round_tracker summaries
    drt_by_prop: dict[str, dict] = {
        ps.get("proposal_id", ""): ps
        for ps in drt_data.get("proposal_summaries", [])
    }

    items: list[dict] = []

    for prop in proposals:
        pid    = prop.get("proposal_id", "")
        gid    = prop.get("globe_id", "")
        title  = prop.get("title", "")
        status = prop.get("status", "")

        cd_ps  = cd_by_prop.get(pid, {})
        drt_ps = drt_by_prop.get(pid, {})
        dc     = delib_count_by_prop.get(pid, 0)

        issue_count   = cd_ps.get("issue_count", 0)
        stance_count  = cd_ps.get("stance_count", 0)
        cg_count      = cd_ps.get("common_ground_count", 0)
        conflict_count = cd_ps.get("conflict_count", 0)
        misund_count  = cd_ps.get("misunderstanding_count", 0)
        cand_count    = cd_ps.get("candidate_count", 0)
        stance_dist   = cd_ps.get("stance_distribution", {})

        round_count       = drt_ps.get("round_count", 1 if dc == 0 else 0)
        latest_round_type = drt_ps.get("latest_round_type", "proposal_opened")
        has_candidate     = bool(drt_ps.get("has_consensus_candidate", cand_count > 0))
        has_conflict      = bool(drt_ps.get("has_conflict", conflict_count > 0))
        has_unresolved    = bool(drt_ps.get("has_unresolved_condition", False))
        has_cg            = bool(drt_ps.get("has_common_ground", cg_count > 0))

        # has_concerns: concern or objection in stance_dist, or concern_round exists
        has_concerns   = bool(
            stance_dist.get("concern", 0) + stance_dist.get("objection", 0) > 0
        )
        has_objections = bool(stance_dist.get("objection", 0) > 0)

        # Also mark has_concerns if concern_round present in rounds
        if not has_concerns:
            for r in drt_data.get("rounds", []):
                if r.get("proposal_id") == pid and r.get("round_type") == "concern_round":
                    has_concerns = True
                    break

        notes = _make_health_notes(
            dc, issue_count, stance_count, cg_count,
            conflict_count, cand_count, misund_count,
            round_count, latest_round_type,
            has_concerns, has_objections, has_cg,
            has_candidate, has_unresolved,
            stance_dist, status,
        )

        questions = _make_suggested_questions(
            dc, has_concerns, has_objections, has_cg,
            has_candidate, has_unresolved,
            issue_count, conflict_count, misund_count, status,
        )

        items.append({
            "health_id":                 f"health-{pid}",
            "proposal_id":               pid,
            "globe_id":                  gid,
            "proposal_title":            title,
            "status":                    status,
            "deliberation_count":        dc,
            "issue_count":               issue_count,
            "stance_count":              stance_count,
            "common_ground_count":       cg_count,
            "conflict_count":            conflict_count,
            "misunderstanding_count":    misund_count,
            "consensus_candidate_count": cand_count,
            "round_count":               round_count,
            "latest_round_type":         latest_round_type,
            "stance_distribution":       stance_dist,
            "has_concerns":              has_concerns,
            "has_objections":            has_objections,
            "has_common_ground":         has_cg,
            "has_consensus_candidate":   has_candidate,
            "has_unresolved_condition":  has_unresolved,
            "health_notes":              notes,
            "suggested_next_questions":  questions,
            "advisory_only":             True,
            "not_score":                 True,
            "not_ranking":               True,
            "not_final_judgment":        True,
            "does_not_approve_execution": True,
        })

    # Global flag counts
    flag_counts: dict[str, int] = {
        "has_concerns":             sum(1 for i in items if i["has_concerns"]),
        "has_objections":           sum(1 for i in items if i["has_objections"]),
        "has_common_ground":        sum(1 for i in items if i["has_common_ground"]),
        "has_consensus_candidate":  sum(1 for i in items if i["has_consensus_candidate"]),
        "has_unresolved_condition": sum(1 for i in items if i["has_unresolved_condition"]),
    }

    return {
        "health_check_id":  "deliberation-health-check-phase-49",
        "generated_at":     datetime.now(timezone.utc).isoformat(),
        "phase":            "49",
        "total_proposals":  len(items),
        "flag_counts":      flag_counts,
        **HEALTH_INVARIANTS,
        "advisory_phrases": HEALTH_PHRASES,
        "items":            items,
    }


# ─── Filter ───────────────────────────────────────────────────────────────────

_FLAG_FIELD: dict[str, str] = {
    "concerns":      "has_concerns",
    "objections":    "has_objections",
    "common_ground": "has_common_ground",
    "candidate":     "has_consensus_candidate",
    "unresolved":    "has_unresolved_condition",
}


def filter_items(
    data:        dict,
    proposal_id: str | None = None,
    globe_id:    str | None = None,
    flag:        str | None = None,
) -> list[dict]:
    items = data.get("items", [])
    if proposal_id:
        items = [i for i in items if i.get("proposal_id") == proposal_id]
    if globe_id:
        items = [i for i in items if i.get("globe_id") == globe_id]
    if flag:
        field = _FLAG_FIELD.get(flag)
        if field:
            items = [i for i in items if i.get(field)]
    return items


# ─── Markdown ─────────────────────────────────────────────────────────────────

def _to_markdown(data: dict) -> str:
    lines: list[str] = []
    lines.append("# Deliberation Health Check (Phase 49)\n")
    lines.append(f"Generated: {data.get('generated_at', '')}\n")
    lines.append(f"Total proposals: {data.get('total_proposals', 0)}\n")
    lines.append("## Flag Counts\n")
    for k, v in data.get("flag_counts", {}).items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")

    for item in data.get("items", []):
        pid   = item["proposal_id"]
        title = item["proposal_title"][:60]
        lines.append(f"\n## {pid} — {title}")
        lines.append(
            f"globe={item['globe_id']} | status={item['status']} | "
            f"deliberations={item['deliberation_count']} | rounds={item['round_count']}"
        )
        counts_str = (
            f"issues={item['issue_count']} stances={item['stance_count']} "
            f"cg={item['common_ground_count']} conflicts={item['conflict_count']} "
            f"candidates={item['consensus_candidate_count']}"
        )
        lines.append(counts_str)
        flags = []
        for f, field in _FLAG_FIELD.items():
            if item.get(field):
                flags.append(f)
        if flags:
            lines.append(f"flags: {', '.join(flags)}")
        lines.append("")
        lines.append("### Health Notes")
        for note in item.get("health_notes", []):
            lines.append(f"- {note}")
        lines.append("")
        lines.append("### Suggested Next Questions")
        for q in item.get("suggested_next_questions", []):
            lines.append(f"- {q}")
        lines.append("")

    lines.append("---\n")
    for p in HEALTH_PHRASES:
        lines.append(f"*{p}*")
    lines.append("")
    return "\n".join(lines)


# ─── Save / Load ──────────────────────────────────────────────────────────────

_HEALTH_JSON = _REPORTS_DIR / "deliberation_health_check.json"
_HEALTH_MD   = _REPORTS_DIR / "deliberation_health_check.md"


def save_health_check() -> dict:
    data = build_health_check()
    _REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    _HEALTH_JSON.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _HEALTH_MD.write_text(_to_markdown(data), encoding="utf-8")
    return data


def load_health_check() -> dict:
    if _HEALTH_JSON.exists():
        return json.loads(_HEALTH_JSON.read_text(encoding="utf-8"))
    return build_health_check()


# ─── CLI helpers ──────────────────────────────────────────────────────────────

_FLAG_ICON: dict[str, str] = {
    "has_concerns":             "⚠️ ",
    "has_objections":           "▼ ",
    "has_common_ground":        "🤝",
    "has_consensus_candidate":  "🌱",
    "has_unresolved_condition": "⚡",
}


def _print_items(items: list[dict], label: str) -> None:
    width = 64
    print(f"\nDeliberation Health Check — {label}")
    print("=" * width)
    print(f"  {len(items)} proposal(s)\n")
    for item in items:
        pid   = item["proposal_id"]
        title = item["proposal_title"][:50]
        sta   = item["status"]
        dc    = item["deliberation_count"]
        rc    = item["round_count"]
        print(f"  ── {pid} [{sta}] {title}")
        print(f"     delib={dc} rounds={rc} issues={item['issue_count']} "
              f"cg={item['common_ground_count']} conflicts={item['conflict_count']} "
              f"cands={item['consensus_candidate_count']}")
        flags = [k for k, field in _FLAG_FIELD.items() if item.get(field)]
        if flags:
            icon_str = " ".join(f"{_FLAG_ICON.get('has_'+k,'·')} {k}" for k in flags)
            print(f"     flags: {icon_str}")
        print("     health_notes:")
        for note in item.get("health_notes", []):
            print(f"       · {note[:90]}")
        print("     suggested_next_questions:")
        for q in item.get("suggested_next_questions", []):
            print(f"       ? {q[:90]}")
        print()
    for p in HEALTH_PHRASES:
        print(f"  \"{p}\"")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main() -> None:   # noqa: C901
    args = sys.argv[1:]
    if not args:
        args = ["summary"]
    cmd = args[0]

    if cmd == "summary":
        data  = build_health_check()
        total = data.get("total_proposals", 0)
        width = 64
        print(f"Deliberation Health Check (Phase 49)")
        print("=" * width)
        print(f"  generated_at:    {data.get('generated_at','')}")
        print(f"  total_proposals: {total}")
        print()
        print("  Flag summary:")
        for k, v in data.get("flag_counts", {}).items():
            bar  = "█" * int(20 * v / max(total, 1))
            icon = _FLAG_ICON.get(k, "·")
            print(f"    {icon} {k:<32} {v:>3}  {bar}")
        print()
        print("  Per proposal:")
        for item in data.get("items", []):
            pid  = item["proposal_id"]
            sta  = item["status"]
            dc   = item["deliberation_count"]
            flags = [f for f, field in _FLAG_FIELD.items() if item.get(field)]
            flag_s = " ".join(f"[{f}]" for f in flags) if flags else "—"
            print(f"    {pid} [{sta}]  delib={dc}  {flag_s}")
        print()
        for p in HEALTH_PHRASES:
            print(f"  \"{p}\"")

    elif cmd == "save":
        print("Saving Deliberation Health Check (Phase 49)...")
        data = save_health_check()
        print(f"  Saved: {_HEALTH_JSON.relative_to(Path.cwd())}")
        print(f"  Saved: {_HEALTH_MD.relative_to(Path.cwd())}")
        print(f"  total_proposals: {data.get('total_proposals', 0)}")
        for k, v in data.get("flag_counts", {}).items():
            print(f"    {k}: {v}")
        print()
        for p in HEALTH_PHRASES:
            print(f"  \"{p}\"")

    elif cmd == "show-proposal":
        if len(args) < 2:
            print("Usage: deliberation_health_check.py show-proposal <proposal_id>")
            sys.exit(1)
        data  = load_health_check()
        items = filter_items(data, proposal_id=args[1])
        _print_items(items, f"proposal={args[1]}")

    elif cmd == "show-globe":
        if len(args) < 2:
            print("Usage: deliberation_health_check.py show-globe <globe_id>")
            sys.exit(1)
        data  = load_health_check()
        items = filter_items(data, globe_id=args[1])
        _print_items(items, f"globe={args[1]}")

    elif cmd == "show-flag":
        valid = list(_FLAG_FIELD.keys())
        if len(args) < 2 or args[1] not in valid:
            print(f"Usage: deliberation_health_check.py show-flag <{'|'.join(valid)}>")
            sys.exit(1)
        data  = load_health_check()
        items = filter_items(data, flag=args[1])
        _print_items(items, f"flag={args[1]}")

    else:
        print("Usage: deliberation_health_check.py "
              "<summary|save|show-proposal|show-globe|show-flag> [arg]")
        sys.exit(1)


if __name__ == "__main__":
    main()
