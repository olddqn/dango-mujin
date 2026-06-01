"""
consensus_discovery.py — Consensus Discovery Layer (Phase 47)

Reads proposals.json + deliberations.json and extracts, in a rule-based
advisory manner:
  A. issues          — 論点 detected from deliberation content
  B. stances         — support / concern / objection / clarification / neutral
  C. common_ground   — 一致点 / 合意点 candidates
  D. conflict_points — 対立点 / 未解決点 candidates
  E. misunderstandings — 誤解の可能性 candidates
  F. consensus_candidates — 合意候補

All output is ADVISORY DISPLAY ONLY.
Nothing here constitutes voting, adoption, approval, or enforcement.

INVARIANTS (permanent, all sessions):
    Consensus discovery is advisory display only.
    Consensus discovery is not voting.
    Consensus candidate is not final agreement.
    Consensus discovery does not approve execution.
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

_RUNTIME_DIR   = Path(__file__).parent
_GLOBE_DIR     = _RUNTIME_DIR.parent
_DATA_DIR      = _GLOBE_DIR / "data"
_CLAIMS_DIR    = _GLOBE_DIR / "claims"
_DIRECTIVES_DIR = _GLOBE_DIR / "directives"
_REPORTS_DIR   = _GLOBE_DIR / "reports"

_PROPOSALS_JSON    = _DATA_DIR / "proposals.json"
_DELIBERATIONS_JSON = _DATA_DIR / "deliberations.json"

# ─── Invariants ───────────────────────────────────────────────────────────────

CONSENSUS_INVARIANTS: dict[str, object] = {
    "consensus_discovery_is_advisory_display_only":     True,
    "consensus_discovery_is_not_voting":                True,
    "consensus_candidate_is_not_final_agreement":       True,
    "consensus_discovery_does_not_approve_execution":   True,
    "human_review_is_required_before_any_real_world_action": True,
    "authority":         "none",
    "execution_allowed": False,
    "moves_money":       False,
    "hard_enforcement":  False,
    "credit_issued":     False,
}

CONSENSUS_PHRASES: list[str] = [
    "Consensus discovery is advisory display only.",
    "Consensus discovery is not voting.",
    "Consensus candidate is not final agreement.",
    "Consensus discovery does not approve execution.",
    "Human review is required before any real-world action.",
]

# ─── Keyword sets ─────────────────────────────────────────────────────────────

_KW_SUPPORT = {
    "賛成", "支持", "必要", "良い", "良さそう", "agree", "support",
    "採用", "賛同", "同意", "いいと思", "重要", "有益", "期待",
    "提案します", "推進", "進める", "重要です",
}
_KW_CONCERN = {
    "懸念", "不安", "注意が必要", "risk", "concern", "リスク", "問題がある",
    "条件として", "心配", "難しい", "検討が必要", "ただし",
    "しかし", "でも", "だが", "注意が必要",
}
_KW_OBJECTION = {
    "反対", "異議", "objection", "oppose", "排除", "除外",
    "認めない", "問題だ", "危険", "不当", "すべきでない",
}
_KW_CLARIFICATION = {
    "確認", "定義", "意味", "clarify", "question", "整理", "論点",
    "とは", "確かめ", "質問", "不明", "どういう", "どのよう",
    "明確", "前提", "範囲", "基準",
}
_KW_COMMON_GROUND = {
    "合意点", "合意できる", "共通", "一致", "全員", "both", "shared",
    "全員が認識", "共有", "共通認識", "全員一致", "共感",
    "同じ目標", "同じ方向", "皆が",
}
_KW_CONFLICT = {
    "未解決", "対立", "disagree", "意見の相違", "課題として残",
    "分かれ", "divide", "争点", "未定", "解決していない",
    "優先順位", "リソース配分", "どう行うか", "どう確保",
}
_KW_MISUNDERSTANDING = {
    "誤解", "定義が違う", "前提が違う", "misunderstanding",
    "clarify", "明確化が必要", "意味が違", "別の意味",
    "異なる理解", "前提が異なる", "用語の定義",
}
_KW_CANDIDATE = {
    "条件として", "修正案", "提案として", "であれば合意", "合意候補",
    "candidate", "修正を加えれば", "条件付きで", "一定の条件",
    "であれば賛成", "以下を条件に", "前提として合意",
}
_KW_ISSUE = {
    "論点", "課題", "問題", "issue", "question", "議題",
    "検討すべき", "明確にする必要", "判断が必要", "決める必要",
    "どう定義", "【", "■", "◆",
}

# ─── Utilities ────────────────────────────────────────────────────────────────

def _contains(text: str, kw_set: set[str]) -> bool:
    tl = text.lower()
    return any(kw.lower() in tl for kw in kw_set)


def _count_kw(text: str, kw_set: set[str]) -> int:
    tl = text.lower()
    return sum(1 for kw in kw_set if kw.lower() in tl)


def _extract_keywords(text: str, kw_set: set[str]) -> list[str]:
    tl = text.lower()
    return [kw for kw in sorted(kw_set) if kw.lower() in tl]


def _sentences(text: str) -> list[str]:
    """Split into rough sentences/lines."""
    parts = re.split(r"[。\n・\-]", text)
    return [p.strip() for p in parts if len(p.strip()) >= 10]


def _excerpt(text: str, max_len: int = 120) -> str:
    t = text.strip()
    return t[:max_len] + ("…" if len(t) > max_len else "")


def _load_json(path: Path) -> list | dict:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []


# ─── Core extraction ──────────────────────────────────────────────────────────

def _detect_stance(content: str) -> str:
    """Rule-based stance detection using keyword scoring — returns primary stance type."""
    # Score each stance category
    scores: dict[str, int] = {
        "support":       _count_kw(content, _KW_SUPPORT) * 2,   # weight support higher
        "concern":       _count_kw(content, _KW_CONCERN),
        "objection":     _count_kw(content, _KW_OBJECTION),
        "clarification": _count_kw(content, _KW_CLARIFICATION),
    }
    # Discount objection if "反対意見" appears in a "recording" context
    tl = content.lower()
    if "反対意見を保存" in tl or "反対意見も" in tl or "少数意見を記録" in tl:
        scores["objection"] = max(0, scores["objection"] - 2)
    best = max(scores, key=lambda k: scores[k])
    if scores[best] == 0:
        return "neutral"
    return best


def _extract_issues(
    proposal_id: str,
    globe_id: str,
    deliberations: list[dict],
) -> list[dict]:
    """Extract issue nodes from deliberations for a proposal."""
    issues: list[dict] = []
    seq = 1
    seen_texts: set[str] = set()

    for delib in deliberations:
        content = delib.get("content", "")
        did = delib.get("deliberation_id", "")

        # Extract lines/sentences that look like issue statements
        for sent in _sentences(content):
            if not _contains(sent, _KW_ISSUE):
                continue
            norm = re.sub(r"\s+", " ", sent.lower().strip())
            if norm in seen_texts or len(norm) < 12:
                continue
            seen_texts.add(norm)
            kws = _extract_keywords(sent, _KW_ISSUE | _KW_CONCERN | _KW_CLARIFICATION)
            issues.append({
                "issue_id":               f"issue-{proposal_id}-{seq:03d}",
                "proposal_id":            proposal_id,
                "globe_id":               globe_id,
                "title":                  f"Possible issue detected (may indicate: {', '.join(kws[:3])})",
                "issue_text":             _excerpt(sent, 200),
                "detected_keywords":      kws[:8],
                "source_deliberation_ids": [did],
                "advisory_only":          True,
            })
            seq += 1
            if seq > 10:
                break

    return issues


def _extract_stances(
    proposal_id: str,
    globe_id: str,
    deliberations: list[dict],
) -> list[dict]:
    """One stance node per deliberation (primary stance type)."""
    stances: list[dict] = []
    seq = 1
    for delib in deliberations:
        content    = delib.get("content", "")
        did        = delib.get("deliberation_id", "")
        speaker    = delib.get("speaker_name", "unknown")
        spk_type   = delib.get("speaker_type", "unknown")
        stance_type = _detect_stance(content)
        kws = _extract_keywords(
            content,
            _KW_SUPPORT | _KW_CONCERN | _KW_OBJECTION | _KW_CLARIFICATION,
        )
        stances.append({
            "stance_id":              f"stance-{did}",
            "proposal_id":            proposal_id,
            "globe_id":               globe_id,
            "speaker_name":           speaker,
            "speaker_type":           spk_type,
            "stance_type":            stance_type,
            "stance_text":            _excerpt(content, 200),
            "detected_keywords":      kws[:8],
            "source_deliberation_id": did,
            "advisory_only":          True,
        })
        seq += 1
    return stances


def _extract_common_ground(
    proposal_id: str,
    globe_id: str,
    deliberations: list[dict],
) -> list[dict]:
    """Extract common-ground candidates."""
    results: list[dict] = []
    seq = 1
    seen: set[str] = set()
    for delib in deliberations:
        content = delib.get("content", "")
        did     = delib.get("deliberation_id", "")
        for sent in _sentences(content):
            if not _contains(sent, _KW_COMMON_GROUND):
                continue
            norm = re.sub(r"\s+", " ", sent.lower().strip())
            if norm in seen or len(norm) < 10:
                continue
            seen.add(norm)
            # Try to name supporters from the same block
            speakers = [delib.get("speaker_name", "")]
            results.append({
                "common_ground_id":       f"cg-{proposal_id}-{seq:03d}",
                "proposal_id":            proposal_id,
                "globe_id":               globe_id,
                "common_text":            _excerpt(sent, 200),
                "supporting_speakers":    speakers,
                "source_deliberation_ids": [did],
                "advisory_only":          True,
            })
            seq += 1
            if seq > 8:
                break
    return results


def _extract_conflicts(
    proposal_id: str,
    globe_id: str,
    deliberations: list[dict],
) -> list[dict]:
    """Extract conflict / unresolved-point candidates."""
    results: list[dict] = []
    seq = 1
    seen: set[str] = set()
    for delib in deliberations:
        content = delib.get("content", "")
        did     = delib.get("deliberation_id", "")
        for sent in _sentences(content):
            if not _contains(sent, _KW_CONFLICT):
                continue
            norm = re.sub(r"\s+", " ", sent.lower().strip())
            if norm in seen or len(norm) < 10:
                continue
            seen.add(norm)
            kws = _extract_keywords(sent, _KW_CONFLICT)
            results.append({
                "conflict_id":            f"conflict-{proposal_id}-{seq:03d}",
                "proposal_id":            proposal_id,
                "globe_id":               globe_id,
                "conflict_text":          _excerpt(sent, 200),
                "speaker_groups":         [delib.get("speaker_name", "")],
                "detected_keywords":      kws[:6],
                "source_deliberation_ids": [did],
                "advisory_only":          True,
            })
            seq += 1
            if seq > 8:
                break
    return results


def _extract_misunderstandings(
    proposal_id: str,
    globe_id: str,
    deliberations: list[dict],
) -> list[dict]:
    """Extract possible-misunderstanding candidates."""
    results: list[dict] = []
    seq = 1
    seen: set[str] = set()
    for delib in deliberations:
        content = delib.get("content", "")
        did     = delib.get("deliberation_id", "")
        for sent in _sentences(content):
            if not _contains(sent, _KW_MISUNDERSTANDING):
                continue
            norm = re.sub(r"\s+", " ", sent.lower().strip())
            if norm in seen or len(norm) < 10:
                continue
            seen.add(norm)
            kws = _extract_keywords(sent, _KW_MISUNDERSTANDING)
            results.append({
                "misunderstanding_id":    f"misund-{proposal_id}-{seq:03d}",
                "proposal_id":            proposal_id,
                "globe_id":               globe_id,
                "misunderstanding_text":  _excerpt(sent, 200),
                "reason":                 f"Possible misunderstanding candidate — may indicate: {', '.join(kws[:3])}",
                "source_deliberation_ids": [did],
                "advisory_only":          True,
            })
            seq += 1
            if seq > 6:
                break
    return results


def _extract_candidates(
    proposal_id: str,
    globe_id: str,
    deliberations: list[dict],
    proposal_body: str = "",
) -> list[dict]:
    """Extract consensus-candidate signals."""
    results: list[dict] = []
    seq = 1
    seen: set[str] = set()

    # Check proposal body too for embedded candidate hints
    all_texts: list[tuple[str, str]] = [
        (d.get("deliberation_id", ""), d.get("content", ""))
        for d in deliberations
    ]
    if proposal_body:
        all_texts.append(("proposal-body", proposal_body))

    for src_id, content in all_texts:
        for sent in _sentences(content):
            if not _contains(sent, _KW_CANDIDATE | _KW_COMMON_GROUND):
                continue
            norm = re.sub(r"\s+", " ", sent.lower().strip())
            if norm in seen or len(norm) < 15:
                continue
            seen.add(norm)
            kws = _extract_keywords(sent, _KW_CANDIDATE | _KW_COMMON_GROUND)
            # Derive unresolved conditions from conflict keywords
            unresolv = []
            if _contains(sent, _KW_CONFLICT):
                unresolv = ["Unresolved conditions may exist — human review required"]
            results.append({
                "candidate_id":           f"cand-{proposal_id}-{seq:03d}",
                "proposal_id":            proposal_id,
                "globe_id":               globe_id,
                "candidate_text":         _excerpt(sent, 250),
                "basis":                  f"Keyword signal: {', '.join(kws[:4])}",
                "unresolved_conditions":  unresolv,
                "source_deliberation_ids": [src_id],
                "advisory_only":          True,
                "not_final_agreement":    True,
            })
            seq += 1
            if seq > 6:
                break
    return results


# ─── Build ────────────────────────────────────────────────────────────────────

def build_discovery() -> dict:
    """Build full consensus discovery from proposals + deliberations."""
    proposals    = _load_json(_PROPOSALS_JSON)
    deliberations = _load_json(_DELIBERATIONS_JSON)

    if isinstance(proposals, dict):
        proposals = list(proposals.values())
    if isinstance(deliberations, dict):
        deliberations = list(deliberations.values())

    # Group deliberations by proposal_id
    delib_by_proposal: dict[str, list[dict]] = {}
    for d in deliberations:
        pid = d.get("proposal_id", "")
        delib_by_proposal.setdefault(pid, []).append(d)

    all_issues:         list[dict] = []
    all_stances:        list[dict] = []
    all_common_ground:  list[dict] = []
    all_conflicts:      list[dict] = []
    all_misunderstandings: list[dict] = []
    all_candidates:     list[dict] = []
    proposal_summaries: list[dict] = []

    for prop in proposals:
        pid      = prop.get("proposal_id", "")
        gid      = prop.get("globe_id", "")
        title    = prop.get("title", "")
        body     = prop.get("body", "")
        status   = prop.get("status", "")
        delibss  = delib_by_proposal.get(pid, [])

        issues        = _extract_issues(pid, gid, delibss)
        stances       = _extract_stances(pid, gid, delibss)
        common_ground = _extract_common_ground(pid, gid, delibss)
        conflicts     = _extract_conflicts(pid, gid, delibss)
        misunders     = _extract_misunderstandings(pid, gid, delibss)
        candidates    = _extract_candidates(pid, gid, delibss, body)

        all_issues.extend(issues)
        all_stances.extend(stances)
        all_common_ground.extend(common_ground)
        all_conflicts.extend(conflicts)
        all_misunderstandings.extend(misunders)
        all_candidates.extend(candidates)

        # Aggregate stance distribution
        stance_dist: dict[str, int] = {}
        for s in stances:
            st = s.get("stance_type", "neutral")
            stance_dist[st] = stance_dist.get(st, 0) + 1

        proposal_summaries.append({
            "proposal_id":         pid,
            "globe_id":            gid,
            "title":               title,
            "status":              status,
            "deliberation_count":  len(delibss),
            "issue_count":         len(issues),
            "stance_count":        len(stances),
            "stance_distribution": stance_dist,
            "common_ground_count": len(common_ground),
            "conflict_count":      len(conflicts),
            "misunderstanding_count": len(misunders),
            "candidate_count":     len(candidates),
            "advisory_only":       True,
        })

    total_items = (
        len(all_issues) + len(all_stances) + len(all_common_ground)
        + len(all_conflicts) + len(all_misunderstandings) + len(all_candidates)
    )

    return {
        "discovery_id":       "consensus-discovery-phase-47",
        "generated_at":       datetime.now(timezone.utc).isoformat(),
        "phase":              "47",
        "total_proposals":    len(proposals),
        "total_deliberations": len(deliberations),
        "total_items":        total_items,
        "counts": {
            "issues":             len(all_issues),
            "stances":            len(all_stances),
            "common_ground":      len(all_common_ground),
            "conflict_points":    len(all_conflicts),
            "misunderstandings":  len(all_misunderstandings),
            "consensus_candidates": len(all_candidates),
        },
        **CONSENSUS_INVARIANTS,
        "advisory_phrases":   CONSENSUS_PHRASES,
        "proposal_summaries": proposal_summaries,
        "issues":             all_issues,
        "stances":            all_stances,
        "common_ground":      all_common_ground,
        "conflict_points":    all_conflicts,
        "misunderstandings":  all_misunderstandings,
        "consensus_candidates": all_candidates,
    }


# ─── Filter ───────────────────────────────────────────────────────────────────

_ITEM_TYPE_MAP: dict[str, str] = {
    "issue":           "issues",
    "stance":          "stances",
    "common_ground":   "common_ground",
    "conflict":        "conflict_points",
    "misunderstanding": "misunderstandings",
    "candidate":       "consensus_candidates",
}


def filter_items(
    data:        dict,
    proposal_id: str | None = None,
    globe_id:    str | None = None,
    item_type:   str | None = None,
) -> dict[str, list[dict]]:
    """Return filtered item dict keyed by type."""
    keys = list(_ITEM_TYPE_MAP.values()) if not item_type \
        else [_ITEM_TYPE_MAP.get(item_type, item_type)]

    result: dict[str, list[dict]] = {}
    for key in keys:
        items = data.get(key, [])
        if proposal_id:
            items = [i for i in items if i.get("proposal_id") == proposal_id]
        if globe_id:
            items = [i for i in items if i.get("globe_id") == globe_id]
        result[key] = items
    return result


# ─── Markdown ─────────────────────────────────────────────────────────────────

def _to_markdown(data: dict) -> str:
    lines: list[str] = []
    lines.append("# Consensus Discovery (Phase 47)\n")
    lines.append(f"Generated: {data.get('generated_at', '')}\n")
    counts = data.get("counts", {})
    lines.append(f"Proposals: {data.get('total_proposals',0)} | "
                 f"Deliberations: {data.get('total_deliberations',0)} | "
                 f"Total items: {data.get('total_items',0)}\n")
    lines.append("## Item Counts\n")
    for k, v in counts.items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")

    for ps in data.get("proposal_summaries", []):
        lines.append(f"\n## {ps['proposal_id']} — {ps['title']}")
        lines.append(f"globe: {ps['globe_id']} | status: {ps['status']} | "
                     f"deliberations: {ps['deliberation_count']}")
        lines.append(f"issues: {ps['issue_count']} | stances: {ps['stance_count']} | "
                     f"common_ground: {ps['common_ground_count']} | "
                     f"conflicts: {ps['conflict_count']} | "
                     f"candidates: {ps['candidate_count']}")
        lines.append("")

    for section_key, label in [
        ("issues",             "Issues"),
        ("stances",            "Stances"),
        ("common_ground",      "Common Ground"),
        ("conflict_points",    "Conflict Points"),
        ("misunderstandings",  "Possible Misunderstandings"),
        ("consensus_candidates", "Consensus Candidates"),
    ]:
        items = data.get(section_key, [])
        if not items:
            continue
        lines.append(f"\n## {label} ({len(items)})\n")
        for item in items:
            id_key = next((k for k in item if k.endswith("_id") and k != "proposal_id"), "")
            text_key = next((k for k in item if "text" in k), "")
            lines.append(f"### {item.get(id_key, '')} (proposal={item.get('proposal_id','')})")
            lines.append(f"{item.get(text_key, '')}")
            lines.append("")

    lines.append("---\n")
    for p in CONSENSUS_PHRASES:
        lines.append(f"*{p}*")
    lines.append("")
    return "\n".join(lines)


# ─── Save / Load ──────────────────────────────────────────────────────────────

_DISCOVERY_JSON = _REPORTS_DIR / "consensus_discovery.json"
_DISCOVERY_MD   = _REPORTS_DIR / "consensus_discovery.md"


def save_discovery() -> dict:
    data = build_discovery()
    _REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    _DISCOVERY_JSON.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _DISCOVERY_MD.write_text(_to_markdown(data), encoding="utf-8")
    return data


def load_discovery() -> dict:
    if _DISCOVERY_JSON.exists():
        return json.loads(_DISCOVERY_JSON.read_text(encoding="utf-8"))
    return build_discovery()


# ─── CLI helpers ──────────────────────────────────────────────────────────────

_SECTION_ICON: dict[str, str] = {
    "issues":              "🔎",
    "stances":             "💬",
    "common_ground":       "🤝",
    "conflict_points":     "⚡",
    "misunderstandings":   "❓",
    "consensus_candidates": "🌱",
}


def _print_section(key: str, items: list[dict]) -> None:
    icon  = _SECTION_ICON.get(key, "·")
    label = key.replace("_", " ")
    print(f"\n  {icon} {label.upper()} ({len(items)} items)")
    id_key   = {"issues": "issue_id", "stances": "stance_id",
                 "common_ground": "common_ground_id",
                 "conflict_points": "conflict_id",
                 "misunderstandings": "misunderstanding_id",
                 "consensus_candidates": "candidate_id"}.get(key, "")
    text_key = {"issues": "issue_text", "stances": "stance_text",
                 "common_ground": "common_text",
                 "conflict_points": "conflict_text",
                 "misunderstandings": "misunderstanding_text",
                 "consensus_candidates": "candidate_text"}.get(key, "")
    extra_keys = {
        "stances": ("stance_type", "speaker_name"),
        "issues":  ("detected_keywords",),
        "consensus_candidates": ("not_final_agreement", "unresolved_conditions"),
    }.get(key, ())
    for item in items[:15]:
        item_id = item.get(id_key, "")
        text    = item.get(text_key, "")[:120]
        print(f"    [{item_id}]")
        print(f"      {text}")
        for ek in extra_keys:
            v = item.get(ek)
            if v is not None:
                print(f"      {ek}: {v}")
    if len(items) > 15:
        print(f"    … +{len(items)-15} more")


def _print_discovery(data: dict, label: str) -> None:
    width = 60
    print(f"\nConsensus Discovery — {label}")
    print("=" * width)
    counts = data.get("counts", {})
    for k, v in counts.items():
        print(f"  {k:<28} {v:>4}")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main() -> None:  # noqa: C901
    args = sys.argv[1:]
    if not args:
        args = ["summary"]
    cmd = args[0]

    if cmd == "summary":
        data = build_discovery()
        _print_discovery(data, "全体")
        print()
        for ps in data.get("proposal_summaries", []):
            pid    = ps["proposal_id"]
            gid    = ps["globe_id"]
            title  = ps["title"][:45]
            sta    = ps["status"]
            nd     = ps["deliberation_count"]
            dist   = ps.get("stance_distribution", {})
            dist_s = " ".join(f"{k}={v}" for k, v in dist.items())
            print(f"  {pid} [{gid}] {sta:12s}  delib={nd}  {dist_s}")
            print(f"    issue={ps['issue_count']} cg={ps['common_ground_count']} "
                  f"conflict={ps['conflict_count']} cand={ps['candidate_count']}")
        print()
        for p in CONSENSUS_PHRASES:
            print(f"  \"{p}\"")

    elif cmd == "save":
        print("Saving Consensus Discovery (Phase 47)...")
        data = save_discovery()
        counts = data.get("counts", {})
        print(f"  Saved: {_DISCOVERY_JSON.relative_to(Path.cwd())}")
        print(f"  Saved: {_DISCOVERY_MD.relative_to(Path.cwd())}")
        print(f"  total_items: {data.get('total_items', 0)}")
        for k, v in counts.items():
            print(f"    {k}: {v}")
        print()
        for p in CONSENSUS_PHRASES:
            print(f"  \"{p}\"")

    elif cmd == "show-proposal":
        if len(args) < 2:
            print("Usage: consensus_discovery.py show-proposal <proposal_id>")
            sys.exit(1)
        data = load_discovery()
        pid  = args[1]
        filtered = filter_items(data, proposal_id=pid)
        total = sum(len(v) for v in filtered.values())
        print(f"\nConsensus Discovery — proposal={pid}")
        print("=" * 60)
        print(f"  {total} items\n")
        for key, items in filtered.items():
            if items:
                _print_section(key, items)
        print()
        for p in CONSENSUS_PHRASES:
            print(f"  \"{p}\"")

    elif cmd == "show-globe":
        if len(args) < 2:
            print("Usage: consensus_discovery.py show-globe <globe_id>")
            sys.exit(1)
        data = load_discovery()
        gid  = args[1]
        filtered = filter_items(data, globe_id=gid)
        total = sum(len(v) for v in filtered.values())
        print(f"\nConsensus Discovery — globe={gid}")
        print("=" * 60)
        print(f"  {total} items\n")
        for key, items in filtered.items():
            if items:
                _print_section(key, items)
        print()
        for p in CONSENSUS_PHRASES:
            print(f"  \"{p}\"")

    elif cmd == "show-type":
        valid = list(_ITEM_TYPE_MAP.keys())
        if len(args) < 2 or args[1] not in valid:
            print(f"Usage: consensus_discovery.py show-type <{'|'.join(valid)}>")
            sys.exit(1)
        data = load_discovery()
        itype = args[1]
        filtered = filter_items(data, item_type=itype)
        key   = _ITEM_TYPE_MAP[itype]
        items = filtered.get(key, [])
        print(f"\nConsensus Discovery — type={itype}")
        print("=" * 60)
        _print_section(key, items)
        print()
        for p in CONSENSUS_PHRASES:
            print(f"  \"{p}\"")

    else:
        print("Usage: consensus_discovery.py <summary|save|show-proposal|show-globe|show-type> [arg]")
        sys.exit(1)


if __name__ == "__main__":
    main()
