#!/usr/bin/env python3
"""
governance_summary.py — Globe Governance Summary (Phase 44)
Dan-Go × GITSEA — Globe Foundation Layer

Aggregates governance-related counts per Globe across proposals, claims,
directives, execution logs, attention items, signals, members, and dependencies.

INVARIANTS:
- Governance summary is advisory display only.
- Governance summary is not governance score.
- Governance summary does not rank globes.
- Governance summary creates no authority.
- Governance summary does not allocate resources.
- Human review is required before any real-world action.
- authority: none

Data sources (read-only):
  globe/data/globes.json
  globe/data/proposals.json
  globe/claims/*.json
  globe/directives/*.json
  globe/logs/*.jsonl
  globe/reports/attention_dashboard.json
  globe/reports/cross_directive_signal_aggregation.json
  globe/reports/member_profiles.json
  globe/reports/member_directive_map.json
  globe/reports/directive_dependency_map.json

CLI:
  python3 globe/runtime/governance_summary.py summary
  python3 globe/runtime/governance_summary.py save
  python3 globe/runtime/governance_summary.py show-globe <globe_id>
  python3 globe/runtime/governance_summary.py show-section proposals|directives|logs|attention|signals|members|dependencies
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ─── Paths ──────────────────────────────────────────────────────────────────

_HERE = Path(__file__).parent
_GLOBE_DIR = _HERE.parent
_DATA_DIR = _GLOBE_DIR / "data"
_CLAIMS_DIR = _GLOBE_DIR / "claims"
_DIRECTIVES_DIR = _GLOBE_DIR / "directives"
_LOGS_DIR = _GLOBE_DIR / "logs"
_REPORTS_DIR = _GLOBE_DIR / "reports"

# ─── Invariants ─────────────────────────────────────────────────────────────

GOV_INVARIANTS: dict[str, object] = {
    "governance_summary_is_advisory_display_only": True,
    "governance_summary_is_not_governance_score": True,
    "governance_summary_does_not_rank_globes": True,
    "governance_summary_creates_no_authority": True,
    "governance_summary_does_not_allocate_resources": True,
    "human_review_is_required_before_any_real_world_action": True,
    "authority": "none",
}

GOV_PHRASES: list[str] = [
    "Governance summary is advisory display only.",
    "Governance summary is not governance score.",
    "Governance summary does not rank globes.",
    "Governance summary creates no authority.",
    "Governance summary does not allocate resources.",
    "Human review is required before any real-world action.",
]

SECTIONS: list[str] = [
    "proposals", "directives", "logs", "attention", "signals", "members", "dependencies",
]

# ─── Per-globe accumulator ───────────────────────────────────────────────────

class _GlobeAcc:
    def __init__(self, globe_id: str, globe_name: str) -> None:
        self.globe_id = globe_id
        self.globe_name = globe_name
        self.proposal_count = 0
        self.accepted_proposal_count = 0
        self.claim_count = 0
        self.directive_count = 0
        self.execution_log_count = 0
        self.human_approval_count = 0
        self.observation_count = 0
        self.objection_count = 0
        self.rollback_request_count = 0
        self.voluntary_resolution_signal_count = 0
        self.unresolved_signal_count = 0
        self.contested_signal_count = 0
        self.attention_item_count = 0
        self.member_count = 0
        self.dependency_edge_count = 0
        self.latest_activity_at: str = ""
        # Internal tracking
        self._directive_ids: set[str] = set()

    def _update_ts(self, ts: str) -> None:
        if ts and ts > self.latest_activity_at:
            self.latest_activity_at = ts

    def finalize(self) -> dict:
        """Derive governance_observation_notes from accumulated counts."""
        notes: list[str] = []

        if self.proposal_count == 0:
            notes.append("提案なし (No proposals recorded)")
        else:
            ratio = self.accepted_proposal_count / self.proposal_count
            if ratio == 1.0:
                notes.append(f"全提案採択 ({self.accepted_proposal_count}/{self.proposal_count} accepted)")
            elif ratio > 0:
                notes.append(f"一部採択 ({self.accepted_proposal_count}/{self.proposal_count} proposals accepted)")
            else:
                notes.append(f"採択提案なし (0/{self.proposal_count} proposals accepted)")

        if self.directive_count > 0 and self.execution_log_count == 0:
            notes.append("Directive あり・実行ログなし (Directive exists but no execution logs)")
        elif self.execution_log_count > 0:
            notes.append(f"実行ログ {self.execution_log_count} 件 (execution logs recorded)")

        if self.objection_count > 0:
            notes.append(f"異議 {self.objection_count} 件記録 (objections recorded — advisory only)")
        if self.unresolved_signal_count > 0:
            notes.append(f"未解決シグナル {self.unresolved_signal_count} 件 (unresolved signals — not priority)")
        if self.contested_signal_count > 0:
            notes.append(f"contested シグナル {self.contested_signal_count} 件 (VRS + objection coexist)")
        if self.rollback_request_count > 0:
            notes.append(f"ロールバック要求 {self.rollback_request_count} 件 (rollback requests)")
        if self.attention_item_count > 0:
            notes.append(f"注意事項 {self.attention_item_count} 件 (attention items — advisory only)")
        if self.dependency_edge_count > 0:
            notes.append(f"依存関係 {self.dependency_edge_count} 件 (dependency edges observed)")

        if not notes:
            notes.append("観察対象のシグナルなし (No signals observed)")

        return {
            "globe_id": self.globe_id,
            "globe_name": self.globe_name,
            "proposal_count": self.proposal_count,
            "accepted_proposal_count": self.accepted_proposal_count,
            "claim_count": self.claim_count,
            "directive_count": self.directive_count,
            "execution_log_count": self.execution_log_count,
            "human_approval_count": self.human_approval_count,
            "observation_count": self.observation_count,
            "objection_count": self.objection_count,
            "rollback_request_count": self.rollback_request_count,
            "voluntary_resolution_signal_count": self.voluntary_resolution_signal_count,
            "unresolved_signal_count": self.unresolved_signal_count,
            "contested_signal_count": self.contested_signal_count,
            "attention_item_count": self.attention_item_count,
            "member_count": self.member_count,
            "dependency_edge_count": self.dependency_edge_count,
            "latest_activity_at": self.latest_activity_at,
            "governance_observation_notes": notes,
            "advisory_only": True,
            "not_governance_score": True,
            "does_not_rank_globes": True,
            "creates_no_authority": True,
            "does_not_allocate_resources": True,
        }


# ─── Builder ────────────────────────────────────────────────────────────────

def build_summary() -> dict:
    """
    Build governance summary per Globe from all data sources.
    """
    # ── Load globes ──────────────────────────────────────────────────────
    globes_path = _DATA_DIR / "globes.json"
    globes_raw = json.loads(globes_path.read_text(encoding="utf-8")) if globes_path.exists() else []
    accs: dict[str, _GlobeAcc] = {}
    for g in globes_raw:
        gid = g.get("globe_id", "")
        name = g.get("name", gid)
        if gid:
            accs[gid] = _GlobeAcc(gid, name)
            ts = g.get("updated_at") or g.get("created_at") or ""
            accs[gid]._update_ts(ts)

    def _acc(gid: str) -> _GlobeAcc | None:
        return accs.get(gid)

    # ── Proposals ────────────────────────────────────────────────────────
    proposals_path = _DATA_DIR / "proposals.json"
    if proposals_path.exists():
        proposals = json.loads(proposals_path.read_text(encoding="utf-8"))
        for p in proposals:
            gid = p.get("globe_id", "")
            a = _acc(gid)
            if not a:
                continue
            a.proposal_count += 1
            if p.get("status") == "accepted":
                a.accepted_proposal_count += 1
            a._update_ts(p.get("updated_at") or p.get("created_at") or "")

    # ── Claims ───────────────────────────────────────────────────────────
    for claim_path in sorted(_CLAIMS_DIR.glob("*.json")):
        try:
            claim = json.loads(claim_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        gid = claim.get("globe_id", "")
        a = _acc(gid)
        if not a:
            continue
        a.claim_count += 1
        a._update_ts(claim.get("updated_at") or claim.get("created_at") or "")

    # ── Directives ───────────────────────────────────────────────────────
    for dir_path in sorted(_DIRECTIVES_DIR.glob("*.json")):
        try:
            directive = json.loads(dir_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        gid = directive.get("globe_id", "")
        did = directive.get("directive_id", "")
        a = _acc(gid)
        if not a:
            continue
        a.directive_count += 1
        a._directive_ids.add(did)
        a._update_ts(directive.get("updated_at") or directive.get("created_at") or "")

    # ── Execution Logs ───────────────────────────────────────────────────
    _LOG_ET_MAP = {
        "human_approval":              "human_approval_count",
        "observation":                 "observation_count",
        "objection":                   "objection_count",
        "rollback_request":            "rollback_request_count",
        "voluntary_resolution_signal": "voluntary_resolution_signal_count",
    }
    for log_path in sorted(_LOGS_DIR.glob("*.jsonl")):
        for line in log_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            gid = entry.get("globe_id", "")
            a = _acc(gid)
            if not a:
                continue
            a.execution_log_count += 1
            et = entry.get("entry_type", "")
            field = _LOG_ET_MAP.get(et)
            if field:
                setattr(a, field, getattr(a, field) + 1)
            # Unresolved signal
            if et == "voluntary_resolution_signal":
                rs = entry.get("resolution_status", "")
                if rs == "unresolved":
                    a.unresolved_signal_count += 1
            a._update_ts(entry.get("created_at") or "")

    # ── Attention Dashboard ──────────────────────────────────────────────
    ad_path = _REPORTS_DIR / "attention_dashboard.json"
    if ad_path.exists():
        try:
            ad = json.loads(ad_path.read_text(encoding="utf-8"))
        except Exception:
            ad = {}
        for item in ad.get("items", []):
            gid = item.get("globe_id", "")
            a = _acc(gid)
            if not a:
                continue
            a.attention_item_count += 1
            a._update_ts(item.get("created_at") or "")

    # ── Signal Aggregation — contested_signal_count per globe ────────────
    sig_path = _REPORTS_DIR / "cross_directive_signal_aggregation.json"
    if sig_path.exists():
        try:
            sig = json.loads(sig_path.read_text(encoding="utf-8"))
        except Exception:
            sig = {}
        for rec in sig.get("by_globe", []):
            gid = rec.get("dimension_value", "")
            a = _acc(gid)
            if not a:
                continue
            a.contested_signal_count = rec.get("contested_count", 0)
            # also update unresolved from signal aggregation for confirmation
            if rec.get("unresolved_count", 0) > a.unresolved_signal_count:
                a.unresolved_signal_count = rec["unresolved_count"]

    # ── Member Profiles ──────────────────────────────────────────────────
    mp_path = _REPORTS_DIR / "member_profiles.json"
    if mp_path.exists():
        try:
            mp = json.loads(mp_path.read_text(encoding="utf-8"))
        except Exception:
            mp = {}
        for member in mp.get("members", []):
            for gid in member.get("globe_ids", []):
                a = _acc(gid)
                if a:
                    a.member_count += 1

    # ── Dependency Edges ─────────────────────────────────────────────────
    ddm_path = _REPORTS_DIR / "directive_dependency_map.json"
    if ddm_path.exists():
        try:
            ddm = json.loads(ddm_path.read_text(encoding="utf-8"))
        except Exception:
            ddm = {}
        # Build directive → globe map from accs
        dir_to_globe: dict[str, str] = {}
        for gid, acc in accs.items():
            for did in acc._directive_ids:
                dir_to_globe[did] = gid
        for edge in ddm.get("edges", []):
            src = edge.get("source_directive_id", "")
            tgt = edge.get("target_directive_id", "")
            # Count edge for each globe that has a directive involved
            involved: set[str] = set()
            if src in dir_to_globe:
                involved.add(dir_to_globe[src])
            if tgt in dir_to_globe:
                involved.add(dir_to_globe[tgt])
            for gid in involved:
                a = _acc(gid)
                if a:
                    a.dependency_edge_count += 1

    # ── Build output ──────────────────────────────────────────────────────
    globe_summaries = [a.finalize() for a in accs.values()]
    # Sort by globe_id for stable output
    globe_summaries.sort(key=lambda x: x["globe_id"])

    # Overall totals
    total_proposals    = sum(g["proposal_count"] for g in globe_summaries)
    total_directives   = sum(g["directive_count"] for g in globe_summaries)
    total_log_entries  = sum(g["execution_log_count"] for g in globe_summaries)
    total_attention    = sum(g["attention_item_count"] for g in globe_summaries)
    total_members      = sum(g["member_count"] for g in globe_summaries)
    total_dep_edges    = sum(g["dependency_edge_count"] for g in globe_summaries)

    return {
        "summary_id": "governance-summary-001",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": "Phase 44",
        "total_globes": len(globe_summaries),
        "total_proposals": total_proposals,
        "total_directives": total_directives,
        "total_execution_log_entries": total_log_entries,
        "total_attention_items": total_attention,
        "total_members_observed": total_members,
        "total_dependency_edges": total_dep_edges,
        **GOV_INVARIANTS,
        "advisory_phrases": GOV_PHRASES,
        "globes": globe_summaries,
    }


# ─── Output helpers ──────────────────────────────────────────────────────────

def _globe_md(g: dict) -> str:
    lines = [
        f"### {g['globe_id']} — {g['globe_name']}",
        "",
        f"| 項目 | 値 |",
        f"|---|---|",
        f"| proposals | {g['proposal_count']} (accepted: {g['accepted_proposal_count']}) |",
        f"| claims | {g['claim_count']} |",
        f"| directives | {g['directive_count']} |",
        f"| execution_log_entries | {g['execution_log_count']} |",
        f"| human_approvals | {g['human_approval_count']} |",
        f"| observations | {g['observation_count']} |",
        f"| objections | {g['objection_count']} |",
        f"| rollback_requests | {g['rollback_request_count']} |",
        f"| voluntary_resolution_signals | {g['voluntary_resolution_signal_count']} |",
        f"| unresolved_signals | {g['unresolved_signal_count']} |",
        f"| contested_signals | {g['contested_signal_count']} |",
        f"| attention_items | {g['attention_item_count']} |",
        f"| members | {g['member_count']} |",
        f"| dependency_edges | {g['dependency_edge_count']} |",
        f"| latest_activity_at | {(g['latest_activity_at'] or '—')[:19]} |",
        "",
        "**Governance Observation Notes** (advisory only):",
        "",
    ]
    for note in g.get("governance_observation_notes", []):
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)


def _to_markdown(data: dict) -> str:
    lines = [
        "# Globe Governance Summary (Phase 44)",
        "",
        f"generated_at: {data.get('generated_at', '')}",
        f"total_globes: {data.get('total_globes', 0)}",
        f"total_proposals: {data.get('total_proposals', 0)}",
        f"total_directives: {data.get('total_directives', 0)}",
        f"total_execution_log_entries: {data.get('total_execution_log_entries', 0)}",
        f"total_attention_items: {data.get('total_attention_items', 0)}",
        f"total_members_observed: {data.get('total_members_observed', 0)}",
        f"total_dependency_edges: {data.get('total_dependency_edges', 0)}",
        "",
        "## Invariants",
        "",
    ]
    for phrase in data.get("advisory_phrases", []):
        lines.append(f'- "{phrase}"')
    lines.append("")
    lines.append("## Globe Summaries")
    lines.append("")
    for g in data.get("globes", []):
        lines.append(_globe_md(g))
    return "\n".join(lines)


def save_summary(data: dict | None = None) -> None:
    if data is None:
        data = build_summary()
    json_path = _REPORTS_DIR / "governance_summary.json"
    md_path = _REPORTS_DIR / "governance_summary.md"
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(_to_markdown(data), encoding="utf-8")
    print(f"  Saved: {json_path.relative_to(_GLOBE_DIR.parent)}")
    print(f"  Saved: {md_path.relative_to(_GLOBE_DIR.parent)}")


def load_summary() -> dict:
    json_path = _REPORTS_DIR / "governance_summary.json"
    if json_path.exists():
        try:
            return json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return build_summary()


# ─── CLI ────────────────────────────────────────────────────────────────────

_SECTION_FIELDS: dict[str, list[str]] = {
    "proposals":     ["proposal_count", "accepted_proposal_count", "claim_count"],
    "directives":    ["directive_count"],
    "logs":          ["execution_log_count", "human_approval_count", "observation_count",
                      "objection_count", "rollback_request_count", "voluntary_resolution_signal_count"],
    "attention":     ["attention_item_count", "unresolved_signal_count",
                      "contested_signal_count", "objection_count"],
    "signals":       ["voluntary_resolution_signal_count", "unresolved_signal_count",
                      "contested_signal_count", "rollback_request_count"],
    "members":       ["member_count"],
    "dependencies":  ["dependency_edge_count"],
}


def cmd_summary(data: dict) -> None:
    print("Globe Governance Summary (Phase 44)")
    print("=" * 60)
    print(f"  generated_at:              {data.get('generated_at', '')[:19]}")
    print(f"  total_globes:              {data.get('total_globes', 0)}")
    print(f"  total_proposals:           {data.get('total_proposals', 0)}")
    print(f"  total_directives:          {data.get('total_directives', 0)}")
    print(f"  total_execution_logs:      {data.get('total_execution_log_entries', 0)}")
    print(f"  total_attention_items:     {data.get('total_attention_items', 0)}")
    print(f"  total_members_observed:    {data.get('total_members_observed', 0)}")
    print(f"  total_dependency_edges:    {data.get('total_dependency_edges', 0)}")
    print()
    header = f"  {'globe_id':<30} {'prop':>4} {'dir':>3} {'log':>3} {'attn':>4} {'mem':>4} {'dep':>3} {'lrs':<20}"
    print(header)
    print("  " + "-" * 76)
    for g in data.get("globes", []):
        gid = g["globe_id"]
        lrs = g.get("latest_activity_at", "")[:10] if g.get("latest_activity_at") else "—"
        row = (f"  {gid:<30} {g['proposal_count']:>4} {g['directive_count']:>3}"
               f" {g['execution_log_count']:>3} {g['attention_item_count']:>4}"
               f" {g['member_count']:>4} {g['dependency_edge_count']:>3} {lrs:<20}")
        print(row)
    print()
    for phrase in GOV_PHRASES:
        print(f'  "{phrase}"')


def _print_globe(g: dict) -> None:
    print(f"  Globe: {g['globe_id']} — {g['globe_name']}")
    print(f"    proposals:           {g['proposal_count']} (accepted: {g['accepted_proposal_count']})")
    print(f"    claims:              {g['claim_count']}")
    print(f"    directives:          {g['directive_count']}")
    print(f"    execution_logs:      {g['execution_log_count']}")
    print(f"      human_approval:    {g['human_approval_count']}")
    print(f"      observation:       {g['observation_count']}")
    print(f"      objection:         {g['objection_count']}")
    print(f"      rollback_request:  {g['rollback_request_count']}")
    print(f"      vrs:               {g['voluntary_resolution_signal_count']}")
    print(f"    unresolved_signals:  {g['unresolved_signal_count']}")
    print(f"    contested_signals:   {g['contested_signal_count']}")
    print(f"    attention_items:     {g['attention_item_count']}")
    print(f"    members:             {g['member_count']}")
    print(f"    dep_edges:           {g['dependency_edge_count']}")
    lat = g.get("latest_activity_at", "")
    print(f"    latest_activity_at:  {lat[:19] if lat else '—'}")
    print(f"    governance_observation_notes:")
    for note in g.get("governance_observation_notes", []):
        print(f"      - {note}")
    print()


def main(argv: list[str] | None = None) -> None:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("Usage: governance_summary.py <summary|save|show-globe|show-section> [arg]")
        sys.exit(1)

    cmd = args[0]
    data = build_summary()

    if cmd == "summary":
        cmd_summary(data)

    elif cmd == "save":
        print("Saving Globe Governance Summary (Phase 44)...")
        save_summary(data)
        print(f"  total_globes: {data['total_globes']}")
        print()
        for phrase in GOV_PHRASES:
            print(f'  "{phrase}"')

    elif cmd == "show-globe":
        gid = args[1] if len(args) > 1 else ""
        globes = [g for g in data.get("globes", []) if g["globe_id"] == gid]
        print(f"Governance Summary — globe={gid}")
        print("=" * 60)
        if not globes:
            print(f"  Globe not found: {gid}")
        else:
            _print_globe(globes[0])
        for phrase in GOV_PHRASES:
            print(f'  "{phrase}"')

    elif cmd == "show-section":
        section = args[1] if len(args) > 1 else ""
        fields = _SECTION_FIELDS.get(section)
        if not fields:
            print(f"Unknown section: {section}. Valid: {', '.join(SECTIONS)}")
            sys.exit(1)
        print(f"Governance Summary — section={section}")
        print("=" * 60)
        for g in data.get("globes", []):
            vals = {f: g.get(f, 0) for f in fields}
            total = sum(vals.values())
            row_parts = " | ".join(f"{f.split('_')[0][:6]}:{v}" for f, v in vals.items())
            print(f"  {g['globe_id']:<35} {row_parts}  total={total}")
        print()
        for phrase in GOV_PHRASES:
            print(f'  "{phrase}"')

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
