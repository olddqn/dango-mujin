"""
deliberation_round_tracker.py — Deliberation Round Tracker (Phase 48)

Reads proposals.json + deliberations.json + consensus_discovery.json and
organises each proposal's deliberation history into a sequence of advisory
"rounds".  Each round is typed as one of:

    proposal_opened          — the proposal itself
    initial_response         — first human response
    concern_round            — concern or objection raised
    clarification_round      — question / definition check
    synthesis_round          — AI/system summary of state
    consensus_candidate_round — consensus candidate surfaces
    unresolved_condition_round — unresolved condition noted

INVARIANTS (permanent, all sessions):
    Deliberation rounds are advisory display only.
    Deliberation round is not voting.
    Deliberation round is not final agreement.
    Deliberation round does not approve execution.
    Human review is required before any real-world action.
    authority: none
    execution_allowed: false
    moves_money: false
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────

_RUNTIME_DIR    = Path(__file__).parent
_GLOBE_DIR      = _RUNTIME_DIR.parent
_DATA_DIR       = _GLOBE_DIR / "data"
_REPORTS_DIR    = _GLOBE_DIR / "reports"

_PROPOSALS_JSON     = _DATA_DIR     / "proposals.json"
_DELIBERATIONS_JSON = _DATA_DIR     / "deliberations.json"
_CD_JSON            = _REPORTS_DIR  / "consensus_discovery.json"

# ─── Invariants ───────────────────────────────────────────────────────────────

ROUND_INVARIANTS: dict[str, object] = {
    "deliberation_rounds_are_advisory_display_only":    True,
    "deliberation_round_is_not_voting":                 True,
    "deliberation_round_is_not_final_agreement":        True,
    "deliberation_round_does_not_approve_execution":    True,
    "human_review_is_required_before_any_real_world_action": True,
    "authority":         "none",
    "execution_allowed": False,
    "moves_money":       False,
    "hard_enforcement":  False,
    "credit_issued":     False,
}

ROUND_PHRASES: list[str] = [
    "Deliberation rounds are advisory display only.",
    "Deliberation round is not voting.",
    "Deliberation round is not final agreement.",
    "Deliberation round does not approve execution.",
    "Human review is required before any real-world action.",
]

ROUND_TYPES: list[str] = [
    "proposal_opened",
    "initial_response",
    "concern_round",
    "clarification_round",
    "synthesis_round",
    "consensus_candidate_round",
    "unresolved_condition_round",
]

# ─── Round-type detection keywords ───────────────────────────────────────────

_KW_SYNTHESIS = {
    "合意点", "論点を整理", "支持意見の核心", "懸念点の核心",
    "summary", "summarize", "整理します",
}
_KW_CANDIDATE = {
    "条件として", "修正案", "候補", "candidate",
    "であれば合意", "以下を条件", "提案として",
}
_KW_UNRESOLVED = {
    "未解決", "未定", "条件は未解決", "継続的な熟議",
    "次の熟議ラウンド", "解決していない", "引き続き",
    "unresolved",
}
_KW_CONCERN = {
    "懸念", "リスク", "危険", "不安", "排除のリスク",
    "concern", "risk",
}
_KW_OBJECTION = {
    "反対", "異議", "oppose",
}
_KW_CLARIFICATION = {
    "確認", "定義", "論点", "意味", "clarify",
    "参照します", "データを", "参照データ",
}


def _contains(text: str, kw_set: set[str]) -> bool:
    tl = text.lower()
    return any(kw.lower() in tl for kw in kw_set)


def _excerpt(text: str, max_len: int = 160) -> str:
    t = text.strip()
    return t[:max_len] + ("…" if len(t) > max_len else "")


# ─── Round-type classifier ────────────────────────────────────────────────────

def _classify_round(
    delib: dict,
    is_first_human: bool,
    has_cd_candidates: bool,
    has_cd_conflicts: bool,
) -> str:
    """Assign a round_type to a single deliberation entry."""
    content      = delib.get("content", "")
    speaker_type = delib.get("speaker_type", "human")

    if speaker_type in ("ai", "system"):
        # priority: candidate > unresolved > synthesis > clarification
        if has_cd_candidates and _contains(content, _KW_CANDIDATE):
            return "consensus_candidate_round"
        if _contains(content, _KW_UNRESOLVED):
            return "unresolved_condition_round"
        if _contains(content, _KW_SYNTHESIS):
            return "synthesis_round"
        return "clarification_round"

    # human speaker
    if is_first_human:
        return "initial_response"
    # concern / objection takes priority over clarification
    if _contains(content, _KW_OBJECTION) or _contains(content, _KW_CONCERN):
        return "concern_round"
    if _contains(content, _KW_CLARIFICATION):
        return "clarification_round"
    if has_cd_candidates and _contains(content, _KW_CANDIDATE):
        return "consensus_candidate_round"
    return "initial_response"


# ─── Build a summary text for a round ────────────────────────────────────────

def _make_summary(
    round_type: str,
    content: str,
    speaker: str,
) -> str:
    prefix_map = {
        "proposal_opened":          "Proposal opened by",
        "initial_response":         "Initial response from",
        "concern_round":            "Concern raised by",
        "clarification_round":      "Clarification / question from",
        "synthesis_round":          "Synthesis by",
        "consensus_candidate_round": "Consensus candidate surfaced by",
        "unresolved_condition_round": "Unresolved condition noted by",
    }
    prefix = prefix_map.get(round_type, "Response by")
    short  = _excerpt(content, 120)
    return f"[{prefix} {speaker}] {short}"


# ─── Load helpers ─────────────────────────────────────────────────────────────

def _load_json(path: Path) -> list | dict:
    if not path.exists():
        return [] if "proposals" in path.name or "deliberations" in path.name else {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []


# ─── Build ────────────────────────────────────────────────────────────────────

def build_tracker() -> dict:
    """Build deliberation rounds for all proposals."""
    proposals    = _load_json(_PROPOSALS_JSON)
    deliberations = _load_json(_DELIBERATIONS_JSON)
    cd_data      = _load_json(_CD_JSON) if _CD_JSON.exists() else {}

    if isinstance(proposals, dict):
        proposals = list(proposals.values())
    if isinstance(deliberations, dict):
        deliberations = list(deliberations.values())

    # Group deliberations by proposal_id (sorted by created_at)
    delib_by_prop: dict[str, list[dict]] = {}
    for d in deliberations:
        pid = d.get("proposal_id", "")
        delib_by_prop.setdefault(pid, []).append(d)
    for pid in delib_by_prop:
        delib_by_prop[pid].sort(key=lambda d: d.get("created_at", ""))

    # Index consensus_discovery items by source_deliberation_id
    cd_issues:      dict[str, list[dict]] = {}
    cd_stances:     dict[str, list[dict]] = {}
    cd_cg:          dict[str, list[dict]] = {}
    cd_conflicts:   dict[str, list[dict]] = {}
    cd_candidates:  dict[str, list[dict]] = {}

    for item in cd_data.get("issues", []):
        for sid in item.get("source_deliberation_ids", []):
            cd_issues.setdefault(sid, []).append(item)
    for item in cd_data.get("stances", []):
        sid = item.get("source_deliberation_id", "")
        if sid:
            cd_stances.setdefault(sid, []).append(item)
    for item in cd_data.get("common_ground", []):
        for sid in item.get("source_deliberation_ids", []):
            cd_cg.setdefault(sid, []).append(item)
    for item in cd_data.get("conflict_points", []):
        for sid in item.get("source_deliberation_ids", []):
            cd_conflicts.setdefault(sid, []).append(item)
    for item in cd_data.get("consensus_candidates", []):
        for sid in item.get("source_deliberation_ids", []):
            cd_candidates.setdefault(sid, []).append(item)

    # Per-proposal: has any candidate / conflict
    prop_has_candidate: dict[str, bool] = {}
    prop_has_conflict:  dict[str, bool] = {}
    for item in cd_data.get("consensus_candidates", []):
        prop_has_candidate[item.get("proposal_id", "")] = True
    for item in cd_data.get("conflict_points", []):
        prop_has_conflict[item.get("proposal_id", "")] = True

    all_rounds: list[dict] = []
    proposal_summaries: list[dict] = []

    for prop in proposals:
        pid    = prop.get("proposal_id", "")
        gid    = prop.get("globe_id", "")
        title  = prop.get("title", "")
        status = prop.get("status", "")
        body   = prop.get("body", "")
        p_at   = prop.get("created_at", "")
        proposer = prop.get("proposer", "unknown")

        delibss       = delib_by_prop.get(pid, [])
        has_candidate = prop_has_candidate.get(pid, False)
        has_conflict  = prop_has_conflict.get(pid, False)

        rounds: list[dict] = []
        round_idx = 0

        # ── Round 0: proposal_opened ──────────────────────────────────────────
        opened_round: dict = {
            "round_id":              f"round-{pid}-{round_idx:03d}",
            "proposal_id":           pid,
            "globe_id":              gid,
            "round_index":           round_idx,
            "round_type":            "proposal_opened",
            "source_ids":            [pid],
            "speakers":              [proposer],
            "summary_text":          _make_summary("proposal_opened", body, proposer),
            "detected_issues":       [],
            "detected_stances":      [],
            "detected_common_ground": [],
            "detected_conflicts":    [],
            "detected_candidates":   [],
            "created_at":            p_at,
            "advisory_only":         True,
            "not_voting":            True,
            "not_final_agreement":   True,
            "does_not_approve_execution": True,
        }
        rounds.append(opened_round)
        round_idx += 1

        # ── Rounds from deliberations ─────────────────────────────────────────
        first_human_seen = False
        for delib in delibss:
            did          = delib.get("deliberation_id", "")
            speaker      = delib.get("speaker_name", "unknown")
            spk_type     = delib.get("speaker_type", "human")
            content      = delib.get("content", "")
            d_at         = delib.get("created_at", "")

            is_first_human = (spk_type == "human" and not first_human_seen)
            if spk_type == "human":
                first_human_seen = True

            rtype = _classify_round(
                delib, is_first_human, has_candidate, has_conflict
            )

            # Link consensus_discovery items
            d_issues     = [i.get("issue_id", "") for i in cd_issues.get(did, [])]
            d_stances    = [i.get("stance_id", "") for i in cd_stances.get(did, [])]
            d_cg         = [i.get("common_ground_id", "") for i in cd_cg.get(did, [])]
            d_conflicts  = [i.get("conflict_id", "") for i in cd_conflicts.get(did, [])]
            d_candidates = [i.get("candidate_id", "") for i in cd_candidates.get(did, [])]

            round_item: dict = {
                "round_id":               f"round-{pid}-{round_idx:03d}",
                "proposal_id":            pid,
                "globe_id":               gid,
                "round_index":            round_idx,
                "round_type":             rtype,
                "source_ids":             [did],
                "speakers":               [speaker],
                "summary_text":           _make_summary(rtype, content, speaker),
                "detected_issues":        d_issues,
                "detected_stances":       d_stances,
                "detected_common_ground": d_cg,
                "detected_conflicts":     d_conflicts,
                "detected_candidates":    d_candidates,
                "created_at":             d_at,
                "advisory_only":          True,
                "not_voting":             True,
                "not_final_agreement":    True,
                "does_not_approve_execution": True,
            }
            rounds.append(round_item)
            round_idx += 1

        all_rounds.extend(rounds)

        latest_round = rounds[-1] if rounds else {}
        has_unresolved = any(
            r.get("round_type") == "unresolved_condition_round" for r in rounds
        )
        has_cg = any(r.get("detected_common_ground") for r in rounds)

        proposal_summaries.append({
            "proposal_id":          pid,
            "globe_id":             gid,
            "title":                title,
            "status":               status,
            "round_count":          len(rounds),
            "latest_round_type":    latest_round.get("round_type", ""),
            "latest_round_at":      latest_round.get("created_at", p_at),
            "has_consensus_candidate": has_candidate,
            "has_conflict":         has_conflict,
            "has_unresolved_condition": has_unresolved,
            "has_common_ground":    has_cg,
            "advisory_only":        True,
        })

    # Global counts
    type_counts: dict[str, int] = {rt: 0 for rt in ROUND_TYPES}
    for r in all_rounds:
        rt = r.get("round_type", "")
        type_counts[rt] = type_counts.get(rt, 0) + 1

    return {
        "tracker_id":          "deliberation-round-tracker-phase-48",
        "generated_at":        datetime.now(timezone.utc).isoformat(),
        "phase":               "48",
        "total_proposals":     len(proposals),
        "total_deliberations": len(deliberations),
        "total_rounds":        len(all_rounds),
        "rounds_by_type":      type_counts,
        **ROUND_INVARIANTS,
        "advisory_phrases":    ROUND_PHRASES,
        "proposal_summaries":  proposal_summaries,
        "rounds":              all_rounds,
    }


# ─── Filter ───────────────────────────────────────────────────────────────────

def filter_rounds(
    data:        dict,
    proposal_id: str | None = None,
    globe_id:    str | None = None,
    round_type:  str | None = None,
) -> list[dict]:
    rounds = data.get("rounds", [])
    if proposal_id:
        rounds = [r for r in rounds if r.get("proposal_id") == proposal_id]
    if globe_id:
        rounds = [r for r in rounds if r.get("globe_id") == globe_id]
    if round_type:
        rounds = [r for r in rounds if r.get("round_type") == round_type]
    return rounds


# ─── Markdown ─────────────────────────────────────────────────────────────────

def _to_markdown(data: dict) -> str:
    lines: list[str] = []
    lines.append("# Deliberation Round Tracker (Phase 48)\n")
    lines.append(f"Generated: {data.get('generated_at', '')}\n")
    lines.append(f"Total proposals: {data.get('total_proposals',0)} | "
                 f"Deliberations: {data.get('total_deliberations',0)} | "
                 f"Rounds: {data.get('total_rounds',0)}\n")
    lines.append("## Rounds by Type\n")
    for rt, cnt in data.get("rounds_by_type", {}).items():
        if cnt:
            lines.append(f"- `{rt}`: {cnt}")
    lines.append("")

    for ps in data.get("proposal_summaries", []):
        pid   = ps["proposal_id"]
        title = ps["title"][:60]
        lines.append(f"\n## {pid} — {title}")
        lines.append(
            f"globe={ps['globe_id']} | status={ps['status']} | "
            f"rounds={ps['round_count']} | "
            f"latest={ps['latest_round_type']}"
        )
        flags = []
        if ps.get("has_consensus_candidate"): flags.append("has_candidate")
        if ps.get("has_conflict"):            flags.append("has_conflict")
        if ps.get("has_unresolved_condition"): flags.append("has_unresolved")
        if ps.get("has_common_ground"):        flags.append("has_common_ground")
        if flags:
            lines.append("flags: " + ", ".join(flags))
        lines.append("")
        for r in data.get("rounds", []):
            if r.get("proposal_id") != pid:
                continue
            rt  = r["round_type"]
            idx = r["round_index"]
            spk = ", ".join(r.get("speakers", []))
            lines.append(f"  [{idx}] {rt} — {spk}")
            lines.append(f"    {r.get('summary_text','')[:100]}")
            for key, label in [
                ("detected_issues",        "issues"),
                ("detected_common_ground", "common_ground"),
                ("detected_conflicts",     "conflicts"),
                ("detected_candidates",    "candidates"),
            ]:
                v = r.get(key, [])
                if v:
                    lines.append(f"    {label}: {', '.join(v)}")
            lines.append("")

    lines.append("---\n")
    for p in ROUND_PHRASES:
        lines.append(f"*{p}*")
    lines.append("")
    return "\n".join(lines)


# ─── Save / Load ──────────────────────────────────────────────────────────────

_TRACKER_JSON = _REPORTS_DIR / "deliberation_round_tracker.json"
_TRACKER_MD   = _REPORTS_DIR / "deliberation_round_tracker.md"


def save_tracker() -> dict:
    data = build_tracker()
    _REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    _TRACKER_JSON.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _TRACKER_MD.write_text(_to_markdown(data), encoding="utf-8")
    return data


def load_tracker() -> dict:
    if _TRACKER_JSON.exists():
        return json.loads(_TRACKER_JSON.read_text(encoding="utf-8"))
    return build_tracker()


# ─── CLI helpers ──────────────────────────────────────────────────────────────

_RT_ICON: dict[str, str] = {
    "proposal_opened":          "📄",
    "initial_response":         "💬",
    "concern_round":            "⚠️ ",
    "clarification_round":      "🔍",
    "synthesis_round":          "🧩",
    "consensus_candidate_round": "🌱",
    "unresolved_condition_round": "⚡",
}
_RT_SHORT: dict[str, str] = {
    "proposal_opened":          "opened",
    "initial_response":         "response",
    "concern_round":            "concern",
    "clarification_round":      "clarify",
    "synthesis_round":          "synthesis",
    "consensus_candidate_round": "candidate",
    "unresolved_condition_round": "unresolved",
}


def _print_rounds(rounds: list[dict], label: str) -> None:
    width = 64
    print(f"\nDeliberation Round Tracker — {label}")
    print("=" * width)
    print(f"  {len(rounds)} round(s)\n")
    for r in rounds:
        pid  = r.get("proposal_id", "")
        idx  = r.get("round_index", 0)
        rt   = r.get("round_type", "")
        spk  = ", ".join(r.get("speakers", []))
        smry = r.get("summary_text", "")[:100]
        icon = _RT_ICON.get(rt, "·")
        print(f"  {icon} [{pid}·{idx}] {rt}")
        print(f"    speakers: {spk}")
        print(f"    {smry}")
        for key, label2 in [
            ("detected_issues",        "issues"),
            ("detected_common_ground", "common_ground"),
            ("detected_conflicts",     "conflicts"),
            ("detected_candidates",    "candidates"),
        ]:
            v = r.get(key, [])
            if v:
                print(f"    {label2}: {', '.join(v)}")
        print()
    for p in ROUND_PHRASES:
        print(f"  \"{p}\"")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main() -> None:   # noqa: C901
    args = sys.argv[1:]
    if not args:
        args = ["summary"]
    cmd = args[0]

    if cmd == "summary":
        data  = build_tracker()
        total = data.get("total_rounds", 0)
        width = 64
        print(f"Deliberation Round Tracker (Phase 48)")
        print("=" * width)
        print(f"  generated_at:        {data.get('generated_at','')}")
        print(f"  total_proposals:     {data.get('total_proposals',0)}")
        print(f"  total_deliberations: {data.get('total_deliberations',0)}")
        print(f"  total_rounds:        {total}")
        print()
        print("  By round_type:")
        for rt, cnt in data.get("rounds_by_type", {}).items():
            bar = "█" * int(30 * cnt / max(total, 1))
            icon = _RT_ICON.get(rt, "·")
            print(f"    {icon} {rt:<32} {cnt:>3}  {bar}")
        print()
        print("  By proposal:")
        for ps in data.get("proposal_summaries", []):
            flags = []
            if ps.get("has_consensus_candidate"): flags.append("cand")
            if ps.get("has_conflict"):            flags.append("conflict")
            if ps.get("has_unresolved_condition"): flags.append("unresolved")
            flag_str = " ".join(f"[{f}]" for f in flags) if flags else ""
            print(f"    {ps['proposal_id']} [{ps['globe_id']}]  "
                  f"rounds={ps['round_count']}  "
                  f"latest={_RT_SHORT.get(ps['latest_round_type'], ps['latest_round_type'])}"
                  f"  {flag_str}")
        print()
        for p in ROUND_PHRASES:
            print(f"  \"{p}\"")

    elif cmd == "save":
        print("Saving Deliberation Round Tracker (Phase 48)...")
        data = save_tracker()
        print(f"  Saved: {_TRACKER_JSON.relative_to(Path.cwd())}")
        print(f"  Saved: {_TRACKER_MD.relative_to(Path.cwd())}")
        print(f"  total_rounds: {data.get('total_rounds', 0)}")
        for rt, cnt in data.get("rounds_by_type", {}).items():
            if cnt:
                print(f"    {rt}: {cnt}")
        print()
        for p in ROUND_PHRASES:
            print(f"  \"{p}\"")

    elif cmd == "show-proposal":
        if len(args) < 2:
            print("Usage: deliberation_round_tracker.py show-proposal <proposal_id>")
            sys.exit(1)
        data   = load_tracker()
        rounds = filter_rounds(data, proposal_id=args[1])
        _print_rounds(rounds, f"proposal={args[1]}")

    elif cmd == "show-globe":
        if len(args) < 2:
            print("Usage: deliberation_round_tracker.py show-globe <globe_id>")
            sys.exit(1)
        data   = load_tracker()
        rounds = filter_rounds(data, globe_id=args[1])
        _print_rounds(rounds, f"globe={args[1]}")

    elif cmd == "show-round-type":
        if len(args) < 2:
            print(f"Usage: deliberation_round_tracker.py show-round-type <{'|'.join(ROUND_TYPES)}>")
            sys.exit(1)
        data   = load_tracker()
        rounds = filter_rounds(data, round_type=args[1])
        _print_rounds(rounds, f"round_type={args[1]}")

    else:
        print("Usage: deliberation_round_tracker.py <summary|save|show-proposal|show-globe|show-round-type> [arg]")
        sys.exit(1)


if __name__ == "__main__":
    main()
