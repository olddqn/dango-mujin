#!/usr/bin/env python3
"""
globe_server.py — Globe UI Server (Phase 22–28)
Dan-Go × GITSEA — Globe Foundation Layer

Local HTTP server that serves the Globe pages.
Stdlib only — no external dependencies.

Routes:
    /              → redirect to /globe
    /globe         → Globe list page
    /globe/<id>    → Globe detail page (proposals + GITSEA link)
    /globe/<id>/proposals               → Proposals list for a Globe
    /globe/<id>/proposals/<proposal_id> → Proposal detail + deliberation log
    /globe/<id>/directives              → Directives list for a Globe  [Phase 28]
    /globe/<id>/directives/<dir_id>     → Directive detail page        [Phase 28]
    /globe/<id>/logs/<dir_id>           → Execution Log detail page    [Phase 28]
    /globe/search                       → Search / Filter page         [Phase 31]
    /globe/search?q=<query>             → Text search across all items [Phase 31]
    /globe/search?globe=<globe_id>      → Filter by globe              [Phase 31]
    /globe/search?entry_type=<type>     → Filter by entry_type         [Phase 31]
    /globe/search?resolution_status=<s> → Filter by resolution_status  [Phase 31]
    /globe/search?bridge_target=<t>     → Filter by bridge_target      [Phase 31]

UI display is advisory only — not proof of execution — creates no legal authority.
UI display does not approve execution. Objections and rollback requests are preserved.

Usage:
    python3 globe/runtime/globe_server.py [port]
    # Default port: 7422
    # Then open http://localhost:7422/globe
"""

import html
import json
import re
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

_GLOBE_DIR = Path(__file__).resolve().parents[1]
_DATA_DIR = _GLOBE_DIR / "data"
_CLAIMS_DIR = _GLOBE_DIR / "claims"
_DIRECTIVES_DIR = _GLOBE_DIR / "directives"
_LOGS_DIR = _GLOBE_DIR / "logs"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 7422

# ─── Data helpers ──────────────────────────────────────────────────────────────

def _load(filename: str) -> list:
    p = _DATA_DIR / filename
    return json.loads(p.read_text()) if p.exists() else []


def _globes():       return _load("globes.json")
def _proposals():    return _load("proposals.json")
def _deliberations(): return _load("deliberations.json")


def _load_exec_summary() -> dict | None:
    """Load the pre-built execution log summary report, or build it on the fly."""
    # Try pre-built report first (fast)
    report_path = _GLOBE_DIR / "reports" / "execution_log_summary.json"
    if report_path.exists():
        try:
            return json.loads(report_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    # Fall back: build from JSONL files
    try:
        import importlib.util, sys as _sys
        _spec = importlib.util.spec_from_file_location(
            "execution_log_summary",
            Path(__file__).parent / "execution_log_summary.py",
        )
        _mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
        return _mod.build_summary()
    except Exception:
        return None


def _load_bridge_report() -> dict | None:
    """Load the pre-built Reality Feedback Bridge report, or build it on the fly."""
    report_path = _GLOBE_DIR / "reports" / "reality_feedback_bridge.json"
    if report_path.exists():
        try:
            return json.loads(report_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    try:
        import importlib.util
        _spec = importlib.util.spec_from_file_location(
            "reality_feedback_bridge",
            Path(__file__).parent / "reality_feedback_bridge.py",
        )
        _mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
        return _mod.build_bridge()
    except Exception:
        return None


def _render_resolution_signal_stat(entries: list) -> str:
    """Phase 29 — render a compact resolution signal summary row.

    Self-reported only. Not proof of resolution. Does not close support automatically.
    Contested status must always remain recordable.
    """
    signals = [e for e in entries if e.get("entry_type") == "voluntary_resolution_signal"]
    if not signals:
        return ""
    latest = signals[-1]
    rs = latest.get("resolution_status", "")
    rs_icon = _RS_ICON.get(rs, "•")
    actor = _e(latest.get("actor_name", "?"))
    rs_counts: dict[str, int] = {}
    for s in signals:
        k = s.get("resolution_status", "")
        rs_counts[k] = rs_counts.get(k, 0) + 1

    count_parts = " &nbsp;".join(
        f'{_RS_ICON.get(k,"•")} {_e(k)}: {n}'
        for k, n in sorted(rs_counts.items()) if n
    )
    return f"""
<div style="margin:12px 0 4px;padding:10px 14px;background:#0a0e18;border:1px solid #1a2238;
            border-radius:6px;font-size:0.82rem">
  <span style="color:#4a6070">🏳️ Resolution Signal (Phase 29)</span>
  &nbsp;—&nbsp;
  <span class="rs-badge {_e(rs)}">{rs_icon} {_e(rs)}</span>
  <span style="color:#3a4a68;margin-left:8px">latest by {actor}</span>
  &nbsp;·&nbsp;
  <span style="color:#2a3850">{count_parts}</span>
  <div style="font-size:0.70rem;color:#1e2838;margin-top:4px">
    self-reported only · not proof of resolution · does not close support automatically ·
    creates no legal authority · contested status always recordable
  </div>
</div>"""


def _render_bridge_panel(directive_id: str) -> str:
    """Render Reality Feedback Bridge suggestions for a given directive.

    Phase 27 — advisory only. No approval buttons. No execution links.
    Reality feedback is advisory only.
    Feedback bridge does not reopen a case automatically.
    Human review is required before any real-world action.
    """
    report = _load_bridge_report()
    if not report:
        return ""
    records = [r for r in report.get("records", []) if r["source_directive_id"] == directive_id]
    if not records:
        return ""

    _TARGET_ICON_MAP = {
        "relief_case_memory": "🏠",
        "care_loop_reopen":   "🔄",
        "both":               "🏠🔄",
        "none":               "—",
    }
    _TARGET_LABEL_MAP = {
        "relief_case_memory": "Phase 18 Relief Case Memory",
        "care_loop_reopen":   "Phase 19 Care Loop Reopen",
        "both":               "Phase 18 + Phase 19",
        "none":               "no bridge match",
    }
    _ENTRY_ICON_MAP = {
        "observation":      "👁",
        "feedback":         "💬",
        "objection":        "⚠",
        "rollback_request": "↩",
    }

    items = ""
    for r in records:
        target = r.get("suggested_bridge_target", "none")
        css_cls = {
            "relief_case_memory": "relief",
            "care_loop_reopen":   "care",
            "both":               "both",
            "none":               "none",
        }.get(target, "none")
        ei    = _ENTRY_ICON_MAP.get(r["entry_type"], "•")
        ti    = _TARGET_ICON_MAP.get(target, "—")
        label = _TARGET_LABEL_MAP.get(target, target)
        items += f"""
<div class="bridge-record {css_cls}">
  <div class="br-header">
    {ei} {_e(r["entry_type"])} &nbsp;[{_e(r["feedback_id"])}]
    <span class="bridge-target-badge">{ti} {_e(label)}</span>
  </div>
  <div class="br-content">{_e(r["content"])}</div>
  <div class="br-reason">reason: {_e(r["suggested_reason"])}</div>
  <div class="br-flags">
    requires_human_review: true &nbsp;·&nbsp;
    creates_no_legal_authority: true &nbsp;·&nbsp;
    not_proof_of_resolution: true &nbsp;·&nbsp;
    advisory_only: true
  </div>
</div>"""

    gen = str(report.get("generated_at", ""))[:19].replace("T", " ")
    return f"""
<div class="bridge-panel">
  <h3>🔗 Reality Feedback Bridge (Phase 27) — {len(records)} suggestion(s)</h3>
  {items}
  <div class="bridge-advisory">
    Reality feedback is advisory only · Feedback bridge is not proof of resolution ·
    Feedback bridge creates no legal authority ·
    Feedback bridge does not reopen a case automatically ·
    Human review is required before any real-world action ·
    generated: {_e(gen)}
  </div>
</div>"""


def _load_link_report() -> dict | None:
    """Load the pre-built Bridge Target Links report, or build it on the fly.

    Phase 27b — advisory only. No approval buttons. No execution links.
    Bridge target link is advisory only.
    Link candidate does not reopen a case automatically.
    Human review is required before any real-world action.
    """
    report_path = _GLOBE_DIR / "reports" / "bridge_target_links.json"
    if report_path.exists():
        try:
            return json.loads(report_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    try:
        import importlib.util
        _spec = importlib.util.spec_from_file_location(
            "bridge_target_linker",
            Path(__file__).parent / "bridge_target_linker.py",
        )
        _mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
        return _mod.build_links()
    except Exception:
        return None


def _render_link_candidates_panel(directive_id: str) -> str:
    """Render Bridge Target Detail Link candidates for a given directive.

    Phase 27b — advisory only. No approval buttons. No reopen buttons. No execution links.
    Bridge target link is advisory only.
    Link candidate is not proof of case relation.
    Link candidate creates no legal authority.
    Link candidate does not reopen a case automatically.
    Human review is required before any real-world action.
    """
    report = _load_link_report()
    if not report:
        return ""
    all_cands = report.get("candidates", [])
    candidates = [c for c in all_cands if c.get("source_directive_id") == directive_id]
    if not candidates:
        return ""

    _CONF_ICON = {"high": "🔴", "medium": "🟡", "low": "⚪"}
    _TARGET_LABEL = {
        "relief_case_memory": "Phase 18 Relief Case Memory",
        "care_loop_reopen":   "Phase 19 Care Loop Reopen",
        "none":               "no link",
    }

    items = ""
    for c in candidates:
        conf   = c.get("confidence", "low")
        icon   = _CONF_ICON.get(conf, "⚪")
        css    = f"lnk-{conf}"
        lnk_id = c.get("link_id", "")
        target_type = c.get("candidate_target_type", "none")
        target_label = _TARGET_LABEL.get(target_type, target_type)
        item_id = c.get("candidate_item_id", "")
        item_type = c.get("candidate_item_type", "")
        desc   = c.get("candidate_description", "")
        reason = c.get("match_reason", "")
        path   = c.get("candidate_path", "")
        src_fb = c.get("source_feedback_id", "")

        item_badge = f'<span class="lnk-conf-badge {conf}">{_e(conf.upper())}</span>' if conf != "low" or target_type != "none" else ""

        items += f"""
<div class="link-cand-card {css}">
  <div class="lnk-header">
    {icon} [{_e(lnk_id)}] &nbsp;← {_e(src_fb)}
    {item_badge}
    <span style="color:#2a3858;font-size:0.78rem;margin-left:8px">{_e(target_label)}</span>
    {f'&nbsp; item: <code style="font-size:0.78rem;color:#2a4a38">{_e(item_id)}</code> ({_e(item_type)})' if item_id else ''}
  </div>
  <div class="lnk-desc">{_e(desc)}</div>
  <div class="lnk-reason">reason: {_e(reason)}</div>
  {f'<div class="lnk-path">path: {_e(path)}</div>' if path else ''}
  <div class="lnk-flags">
    requires_human_review: true &nbsp;·&nbsp;
    creates_no_legal_authority: true &nbsp;·&nbsp;
    does_not_reopen_case_automatically: true &nbsp;·&nbsp;
    advisory_only: true
  </div>
</div>"""

    high_count   = sum(1 for c in candidates if c.get("confidence") == "high")
    medium_count = sum(1 for c in candidates if c.get("confidence") == "medium")
    low_count    = sum(1 for c in candidates if c.get("confidence") == "low")
    gen = str(report.get("generated_at", ""))[:19].replace("T", " ")

    return f"""
<div class="link-cand-panel">
  <h3>🔗 Bridge Target Detail Links (Phase 27b) — {len(candidates)} candidate(s)
    &nbsp;<span style="font-size:0.75rem;color:#253040">🔴 high: {high_count} &nbsp;🟡 medium: {medium_count} &nbsp;⚪ low: {low_count}</span>
  </h3>
  {items}
  <div class="link-cand-advisory">
    Bridge target link is advisory only · Link candidate is not proof of case relation ·
    Link candidate creates no legal authority ·
    Link candidate does not reopen a case automatically ·
    Human review is required before any real-world action ·
    generated: {_e(gen)}
  </div>
</div>"""


def _load_cross_phase_summary() -> dict | None:
    """Phase 30 — load cross_phase_contribution_summary.json or build on-the-fly.

    Cross-phase summary is advisory only. Not proof of impact.
    Does not rank participants. Does not allocate resources.
    Human review is required before any real-world action.
    """
    _rpt_path = _REPORTS_DIR / "cross_phase_contribution_summary.json"
    if _rpt_path.exists():
        try:
            return json.loads(_rpt_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    try:
        import importlib.util as _ilu
        _mod_path = Path(__file__).parent / "cross_phase_contribution_summary.py"
        spec = _ilu.spec_from_file_location("cross_phase_contribution_summary", _mod_path)
        mod = _ilu.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        return mod.build_summary()
    except Exception:
        return None


def _render_cross_phase_panel(globe_id: str | None = None) -> str:
    """Phase 30 — Cross-Phase Contribution Summary advisory panel.

    Cross-phase summary is advisory only. Not proof of impact.
    Does not rank participants. Does not allocate resources.
    No execution buttons. No allocation buttons.
    """
    rpt = _load_cross_phase_summary()
    if not rpt:
        return ""

    gen = _e(rpt.get("generated_at", ""))

    def _row(label: str, val: object) -> str:
        return (f'<div class="xphase-metric">'
                f'<span class="xp-label">{label}</span>'
                f'<span class="xp-value">{val}</span></div>\n')

    # ── Per-globe view ────────────────────────────────────────────────────
    if globe_id:
        gs_list = rpt.get("globe_summaries", [])
        gs = next((x for x in gs_list if x.get("globe_id") == globe_id), None)
        if not gs:
            return ""
        rows = ""
        for key, label in [
            ("directive_count",       "Directive 数"),
            ("log_entry_count",       "Log entries"),
            ("human_approval_count",  "✅ Approvals"),
            ("objection_count",       "⚠️ Objections"),
            ("rollback_request_count","↩️ Rollback requests"),
            ("bridge_record_count",   "🔗 Bridge records"),
            ("link_candidate_count",  "🔗 Link candidates"),
        ]:
            rows += _row(label, gs.get(key, 0))
        sig = gs.get("resolution_signal_count", 0)
        if sig:
            un = gs.get("unresolved_signal_count", 0)
            ct = gs.get("contested_signal_count", 0)
            note = '<span style="color:#182030;font-size:0.75em">self-reported · not proof</span>'
            rows += _row("🏳️ Resolution signals",
                         f'{sig} &nbsp;(🔴 unresolved: {un} · ⚔️ contested: {ct}) {note}')
        return f"""
<div class="xphase-panel">
  <h3>📊 Cross-Phase Contribution Summary (Phase 30) — {_e(gs.get("globe_name", globe_id))}</h3>
  {rows}
  <div class="xphase-advisory">
    Cross-phase summary is advisory only · Not proof of impact ·
    Does not rank participants · Does not allocate resources ·
    Human review is required before any real-world action ·
    generated: {gen}
  </div>
</div>"""

    # ── Global view ───────────────────────────────────────────────────────
    totals = rpt.get("global_totals", {})
    metrics = ""
    metrics += _row("Phase 20 Aid patterns", totals.get("aid_pattern_count", 0))
    metrics += _row("Phase 21 Need forecasts", totals.get("need_forecast_record_count", 0))
    metrics += _row("Execution log entries (Phases 25–29)",
                    totals.get("execution_log_entry_count", 0))
    metrics += _row("✅ Human approvals", totals.get("human_approval_count", 0))
    metrics += _row("⚠️ Objections", totals.get("objection_count", 0))
    sig = totals.get("voluntary_resolution_signal_count", 0)
    if sig:
        un = totals.get("unresolved_signal_count", 0)
        ct = totals.get("contested_signal_count", 0)
        note = '<span style="color:#182030;font-size:0.75em">self-reported · not proof</span>'
        metrics += _row("🏳️ Resolution signals",
                        f'{sig} &nbsp;(🔴 unresolved: {un} · ⚔️ contested: {ct}) {note}')
    metrics += _row("🔗 Bridge records", totals.get("bridge_record_count", 0))
    hc = totals.get("high_confidence_link_count", 0)
    metrics += _row("🔗 Link candidates (high-conf)",
                    f'{totals.get("bridge_target_link_count", 0)} &nbsp;(🟢 high: {hc})')

    # Advisory interpretation
    interp = rpt.get("interpretation", {})
    interp_inner = ""
    attn = interp.get("where_attention_is_increasing", [])
    if attn:
        items = "".join(f'<div class="xi-item">→ {_e(x)}</div>' for x in attn)
        interp_inner += f'<div class="xi-title">⚠️ Where attention is increasing</div>{items}'
    unres_l = interp.get("where_unresolved_signals_remain", [])
    if unres_l:
        items = "".join(f'<div class="xi-item">🔴 {_e(x)}</div>' for x in unres_l)
        interp_inner += ('<div class="xi-title" style="margin-top:6px">'
                         'Where unresolved signals remain</div>' + items)
    obj_l = interp.get("where_objections_exist", [])
    if obj_l:
        items = "".join(f'<div class="xi-item">⚠️ {_e(x)}</div>' for x in obj_l)
        interp_inner += ('<div class="xi-title" style="margin-top:6px">'
                         'Where objections exist</div>' + items)
    obs_l = interp.get("cross_phase_observations", [])
    if obs_l:
        items = "".join(f'<div class="xi-item">• {_e(x)}</div>' for x in obs_l)
        interp_inner += ('<div class="xi-title" style="margin-top:6px">'
                         'Cross-phase observations</div>' + items)

    interp_html = ""
    if interp_inner:
        disc = _e(interp.get("disclaimer", "Advisory interpretation only."))[:90]
        interp_html = (f'<div class="xphase-interp">'
                       f'<div class="xi-title" style="color:#182838">{disc}…</div>'
                       f'{interp_inner}</div>')

    n_globes = len(rpt.get("globe_summaries", []))
    return f"""
<div class="xphase-panel">
  <h3>📊 Cross-Phase Contribution Summary (Phase 30) — {n_globes} globe(s)</h3>
  {metrics}
  {interp_html}
  <div class="xphase-advisory">
    Cross-phase summary is advisory only · Not proof of impact ·
    Does not rank participants · Does not allocate resources ·
    Human review is required before any real-world action ·
    generated: {gen}
  </div>
</div>"""


def _load_claim(proposal_id: str) -> dict | None:
    """Load a generated claim for the given proposal_id, or None if not yet converted."""
    claim_path = _CLAIMS_DIR / f"claim-{proposal_id}.json"
    if not claim_path.exists():
        return None
    try:
        return json.loads(claim_path.read_text())
    except Exception:
        return None


def _load_directive(proposal_id: str) -> dict | None:
    """Load a generated directive for the given proposal_id chain, or None."""
    claim_id = f"claim-{proposal_id}"
    directive_path = _DIRECTIVES_DIR / f"directive-{claim_id}.json"
    if not directive_path.exists():
        return None
    try:
        return json.loads(directive_path.read_text())
    except Exception:
        return None


def _load_exec_log(proposal_id: str) -> list:
    """Load execution log entries (JSONL) for the directive derived from proposal_id."""
    directive_id = f"directive-claim-{proposal_id}"
    log_path = _LOGS_DIR / f"{directive_id}.jsonl"
    if not log_path.exists():
        return []
    entries = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except Exception:
                pass
    return entries


def _load_all_directives() -> list:
    """Load all directive JSON files from globe/directives/ (sorted by filename)."""
    result = []
    for p in sorted(_DIRECTIVES_DIR.glob("*.json")):
        try:
            result.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            pass
    return result


def _load_directives_for_globe(globe_id: str) -> list:
    """Return all directives whose globe_id matches."""
    return [d for d in _load_all_directives() if d.get("globe_id") == globe_id]


def _load_directive_by_id(directive_id: str) -> dict | None:
    """Load a single directive JSON by its directive_id."""
    p = _DIRECTIVES_DIR / f"{directive_id}.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _load_exec_log_by_id(directive_id: str) -> list:
    """Load execution log entries (JSONL) by directive_id directly."""
    log_path = _LOGS_DIR / f"{directive_id}.jsonl"
    if not log_path.exists():
        return []
    entries = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except Exception:
                pass
    return entries


STATUS_BADGE = {
    "draft":      ('<span class="badge draft">draft</span>',      "badge-draft"),
    "discussion": ('<span class="badge disc">discussion</span>',   "badge-disc"),
    "voting":     ('<span class="badge vote">voting</span>',       "badge-vote"),
    "accepted":   ('<span class="badge acc">accepted</span>',      "badge-acc"),
    "rejected":   ('<span class="badge rej">rejected</span>',      "badge-rej"),
    "archived":   ('<span class="badge arch">archived</span>',     "badge-arch"),
}

SPEAKER_ICON = {"human": "👤", "ai": "🤖", "system": "⚙️"}

# ─── CSS / Layout ──────────────────────────────────────────────────────────────

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Hiragino Kaku Gothic ProN', 'Noto Sans JP', sans-serif;
       background: #0d0f14; color: #d4d8e0; min-height: 100vh; }
a { color: #6ab0f5; text-decoration: none; }
a:hover { text-decoration: underline; }
header { background: #161a24; border-bottom: 1px solid #2a2f3f;
         padding: 14px 28px; display: flex; align-items: center; gap: 16px; }
header h1 { font-size: 1.15rem; color: #a0b8e0; font-weight: 600; }
header .subtitle { font-size: 0.78rem; color: #5a6480; }
.breadcrumb { font-size: 0.82rem; padding: 10px 28px; color: #5a6480;
              border-bottom: 1px solid #1e2230; }
.breadcrumb a { color: #5a8fc0; }
main { max-width: 900px; margin: 32px auto; padding: 0 24px 64px; }
h2 { font-size: 1.25rem; color: #c0cce0; margin-bottom: 18px; font-weight: 600; }
h3 { font-size: 1rem; color: #8898b0; margin: 28px 0 12px; font-weight: 600;
     text-transform: uppercase; letter-spacing: 0.04em; }
.card { background: #161a24; border: 1px solid #252b3a; border-radius: 8px;
        padding: 18px 22px; margin-bottom: 14px; }
.card h4 { font-size: 1rem; color: #c8d8f0; margin-bottom: 6px; }
.card .meta { font-size: 0.78rem; color: #4e5a78; margin-top: 8px; }
.card .desc { font-size: 0.88rem; color: #8898b0; margin-top: 8px; line-height: 1.55; }
.badge { font-size: 0.72rem; padding: 2px 8px; border-radius: 4px;
         font-weight: 600; letter-spacing: 0.02em; vertical-align: middle; }
.badge.draft   { background: #2a3040; color: #8090a8; }
.badge.disc    { background: #1e2e4a; color: #6ab0f5; }
.badge.vote    { background: #2a2040; color: #a07af0; }
.badge.acc     { background: #102a18; color: #50c878; }
.badge.rej     { background: #2a1010; color: #f07878; }
.badge.arch    { background: #1e1e1e; color: #606070; }
.tag { font-size: 0.75rem; color: #4e5a78; background: #1e2230;
       border: 1px solid #2a3040; border-radius: 4px; padding: 2px 8px;
       display: inline-block; margin-right: 6px; }
.field-row { display: grid; grid-template-columns: 180px 1fr;
             gap: 8px 16px; font-size: 0.86rem; margin-bottom: 8px; }
.field-row .label { color: #4e5a78; font-weight: 600; }
.field-row .value { color: #a0b0c8; }
.founding { background: #0e1420; border-left: 3px solid #2a4a6a;
            padding: 14px 18px; border-radius: 0 6px 6px 0; margin: 12px 0;
            font-size: 0.88rem; color: #8898b0; line-height: 1.65;
            white-space: pre-wrap; word-break: break-word; }
.deliberation { border: 1px solid #1e2430; border-radius: 6px; padding: 14px 18px;
                margin-bottom: 10px; font-size: 0.86rem; }
.deliberation.human  { background: #12181e; border-left: 3px solid #2a4a6a; }
.deliberation.ai     { background: #0e1418; border-left: 3px solid #2a3a5a; }
.deliberation.system { background: #101012; border-left: 3px solid #2a2a3a; }
.deliberation .speaker { font-weight: 600; color: #8898b0; margin-bottom: 6px; }
.deliberation .content { color: #9aa8c0; line-height: 1.65; white-space: pre-wrap;
                          word-break: break-word; }
.gitsea-box { background: #0e1018; border: 1px solid #1e2430; border-radius: 6px;
              padding: 14px 18px; font-size: 0.82rem; color: #5a6878; }
.gitsea-box a { color: #4a7aa8; }
.empty { color: #3a4258; font-style: italic; font-size: 0.88rem; }
.body-block { background: #0e1018; border: 1px solid #1e2430; border-radius: 6px;
              padding: 16px 20px; font-size: 0.88rem; color: #8898b0;
              line-height: 1.7; white-space: pre-wrap; word-break: break-word; }
.next-actions { background: #0e1820; border: 1px solid #1e3040; border-radius: 6px;
                padding: 14px 18px; font-size: 0.85rem; color: #6a8aaa; }
.next-actions ul { margin: 8px 0 0 18px; line-height: 2; }
.claim-box { border-radius: 6px; padding: 14px 20px; font-size: 0.85rem;
             margin-bottom: 4px; }
.claim-box.converted { background: #0c1e14; border: 1px solid #1e4028; color: #50a870; }
.claim-box.not-converted { background: #12141e; border: 1px solid #1e2030; color: #4e5878; }
.claim-box .claim-id { font-family: monospace; font-size: 0.82rem; color: #5ab880; }
.claim-box .claim-hint { font-size: 0.78rem; color: #3a4a5a; margin-top: 6px; }
.directive-box { border-radius: 6px; padding: 14px 20px; font-size: 0.85rem;
                 margin-bottom: 4px; }
.directive-box.converted { background: #12100e; border: 1px solid #3a2e14; color: #c0a050; }
.directive-box.not-converted { background: #12141e; border: 1px solid #1e2030; color: #4e5878; }
.directive-box .dir-id { font-family: monospace; font-size: 0.82rem; color: #c09040; }
.directive-box .dir-hint { font-size: 0.78rem; color: #3a3828; margin-top: 6px; }
.log-box { border-radius: 6px; padding: 14px 20px; font-size: 0.85rem;
           margin-bottom: 4px; }
.log-box.has-entries { background: #0d1520; border: 1px solid #1e2e50; color: #7090c0; }
.log-box.approved    { border-color: #1e3858; color: #80b0e0; }
.log-box.no-entries  { background: #12141e; border: 1px solid #1e2030; color: #4e5878; }
.log-box .log-hint   { font-size: 0.78rem; color: #2a3858; margin-top: 6px; }
.log-entry-badge { font-size: 0.72rem; padding: 2px 7px; border-radius: 4px;
                   background: #1a2a40; color: #5070a0; margin-right: 4px;
                   display: inline-block; }
.exec-summary-panel { background: #0c1020; border: 1px solid #1a2438;
                      border-radius: 8px; padding: 16px 22px; margin: 18px 0; }
.exec-summary-panel h3 { font-size: 0.88rem; color: #607090; margin-bottom: 12px;
                          text-transform: uppercase; letter-spacing: 0.04em; }
.exec-summary-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
.exec-summary-table th { color: #3a5070; font-weight: 600; text-align: left;
                          padding: 4px 10px; border-bottom: 1px solid #1e2a3a; }
.exec-summary-table td { color: #6080a0; padding: 5px 10px;
                          border-bottom: 1px solid #141c28; }
.exec-summary-table td:first-child { color: #8090a8; }
.exec-advisory { font-size: 0.72rem; color: #2a3850; margin-top: 10px; }
/* Phase 28 — Directive / Execution Log pages */
.advisory-banner { background: #0a0e18; border: 1px solid #1a2030;
                   border-left: 3px solid #2a3a5a; border-radius: 0 6px 6px 0;
                   padding: 10px 16px; font-size: 0.78rem; color: #3a4a6a;
                   margin-bottom: 18px; line-height: 1.6; }
.directive-step { background: #0e121e; border: 1px solid #1e2438;
                  border-radius: 6px; padding: 12px 16px; margin-bottom: 8px; }
.directive-step .step-id { font-family: monospace; font-size: 0.78rem;
                            color: #3a4a6a; margin-bottom: 4px; }
.directive-step .step-desc { font-size: 0.86rem; color: #8090a8; line-height: 1.6; }
.directive-step .step-meta { font-size: 0.75rem; color: #2a3a58; margin-top: 6px; }
.step-badge { font-size: 0.7rem; padding: 2px 6px; border-radius: 4px;
              background: #1a2030; color: #4a5870; margin-right: 4px; }
.step-badge.pending { background: #1a2038; color: #5070a0; }
.step-badge.done    { background: #102018; color: #40a060; }
.invariant-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; margin-bottom: 8px; }
.invariant-table td { padding: 4px 10px; border-bottom: 1px solid #141c28; }
.invariant-table td:first-child { color: #3a4a6a; width: 240px; font-family: monospace; }
.invariant-table td:last-child { color: #5a7090; }
.invariant-table .invar-false { color: #3a5060; }
.invariant-table .invar-none  { color: #3a4a5a; }
.log-entry-card { border: 1px solid #1a2438; border-radius: 6px;
                  padding: 12px 16px; margin-bottom: 8px; font-size: 0.85rem; }
.log-entry-card.human_approval    { background: #0a1820; border-left: 3px solid #1e4a28; }
.log-entry-card.execution_attempt { background: #0e1420; border-left: 3px solid #2a2060; }
.log-entry-card.observation       { background: #0e1620; border-left: 3px solid #1e3050; }
.log-entry-card.feedback          { background: #0c1018; border-left: 3px solid #2a2a40; }
.log-entry-card.objection         { background: #1a1010; border-left: 3px solid #5a2020; }
.log-entry-card.rollback_request  { background: #181010; border-left: 3px solid #4a2818; }
.log-entry-card.voluntary_resolution_signal { background: #0c1218; border-left: 3px solid #2a3a60; }
.rs-badge { display: inline-block; font-size: 0.72rem; padding: 2px 8px; border-radius: 4px;
            margin-left: 6px; }
.rs-badge.resolved           { background: #0e2018; color: #3a7848; }
.rs-badge.partially_resolved { background: #1a1a10; color: #7a7030; }
.rs-badge.paused             { background: #14141e; color: #4a5888; }
.rs-badge.unresolved         { background: #1a0e0e; color: #8a3838; }
.rs-badge.contested          { background: #180e18; color: #6a3870; }
.rs-self-reported            { font-size: 0.70rem; color: #2a3050; margin-top: 4px; }
.log-entry-card .entry-header { font-weight: 600; color: #7090b0; margin-bottom: 6px; }
.log-entry-card .entry-content { color: #8898b0; line-height: 1.65;
                                  white-space: pre-wrap; word-break: break-word; }
.log-entry-card .entry-meta { font-size: 0.75rem; color: #2a3858; margin-top: 8px; }
.scope-list     { font-size: 0.85rem; color: #7090a8; margin: 6px 0 0 18px; line-height: 1.8; }
.scope-list.out { color: #5a4a6a; }
.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr);
             gap: 8px; text-align: center; font-size: 0.85rem; }
.stat-grid .stat-num { font-size: 1.4rem; color: #8098b8; }
.stat-grid .stat-lbl { color: #3a4a68; font-size: 0.75rem; }
/* Phase 27 — Reality Feedback Bridge panel */
.bridge-panel { background: #0c1018; border: 1px solid #1e2838;
                border-radius: 8px; padding: 16px 22px; margin: 18px 0; }
.bridge-panel h3 { font-size: 0.88rem; color: #507080; margin-bottom: 12px;
                   text-transform: uppercase; letter-spacing: 0.04em; }
.bridge-record { border: 1px solid #1a2438; border-radius: 6px;
                 padding: 10px 14px; margin-bottom: 8px; font-size: 0.84rem; }
.bridge-record.relief { background: #0a1618; border-left: 3px solid #1e4838; }
.bridge-record.care   { background: #0a0e18; border-left: 3px solid #1e2850; }
.bridge-record.both   { background: #0c1020; border-left: 3px solid #3a1a50; }
.bridge-record.none   { background: #0b0d12; border-left: 3px solid #1a1e28; }
.bridge-record .br-header  { color: #5a7090; font-size: 0.82rem;
                              font-weight: 600; margin-bottom: 4px; }
.bridge-record .br-content { color: #7088a0; font-size: 0.82rem;
                              line-height: 1.55; white-space: pre-wrap; word-break: break-word; }
.bridge-record .br-reason  { color: #2a3a52; font-size: 0.74rem; margin-top: 5px; }
.bridge-record .br-flags   { color: #1e2a3a; font-size: 0.72rem; margin-top: 4px; }
.bridge-target-badge { font-size: 0.72rem; padding: 2px 7px; border-radius: 4px;
                       background: #14202e; color: #3a5870; margin-left: 6px; }
.bridge-advisory { font-size: 0.72rem; color: #1e2a3a; margin-top: 10px;
                   border-top: 1px solid #111820; padding-top: 8px; }
/* Phase 27b — Bridge Target Detail Link candidates panel */
.link-cand-panel { background: #090c14; border: 1px solid #1a2232;
                   border-radius: 8px; padding: 16px 22px; margin: 18px 0; }
.link-cand-panel h3 { font-size: 0.88rem; color: #4a6070; margin-bottom: 12px;
                      text-transform: uppercase; letter-spacing: 0.04em; }
.link-cand-card  { border: 1px solid #161e2e; border-radius: 6px;
                   padding: 10px 14px; margin-bottom: 8px; font-size: 0.84rem; }
.link-cand-card.lnk-high   { background: #08130e; border-left: 3px solid #1a3e22; }
.link-cand-card.lnk-medium { background: #0d1220; border-left: 3px solid #1a2a50; }
.link-cand-card.lnk-low    { background: #0a0c12; border-left: 3px solid #1a1e28; }
.link-cand-card .lnk-header  { color: #4a6878; font-size: 0.82rem;
                                font-weight: 600; margin-bottom: 4px; }
.link-cand-card .lnk-desc    { color: #607888; font-size: 0.82rem;
                                line-height: 1.55; white-space: pre-wrap; word-break: break-word; }
.link-cand-card .lnk-reason  { color: #253040; font-size: 0.74rem; margin-top: 5px; }
.link-cand-card .lnk-path    { color: #1e2838; font-size: 0.72rem; margin-top: 3px; font-family: monospace; }
.link-cand-card .lnk-flags   { color: #182030; font-size: 0.72rem; margin-top: 4px; }
.lnk-conf-badge { font-size: 0.70rem; padding: 2px 7px; border-radius: 4px; margin-left: 6px; }
.lnk-conf-badge.high   { background: #0e2018; color: #3a7848; }
.lnk-conf-badge.medium { background: #0e1828; color: #3a5878; }
.lnk-conf-badge.low    { background: #10121a; color: #2a3450; }
.link-cand-advisory { font-size: 0.72rem; color: #182030; margin-top: 10px;
                      border-top: 1px solid #0e1420; padding-top: 8px; }
/* Phase 31 — Search / Filter UI */
.search-bar { display: flex; gap: 8px; margin-bottom: 18px; }
.search-bar input { flex: 1; background: #0e1220; border: 1px solid #1e2a3a;
                    border-radius: 6px; padding: 8px 14px; color: #a0b8e0;
                    font-size: 0.92rem; font-family: inherit; }
.search-bar input:focus { outline: none; border-color: #2a4a6a; }
.search-bar button { background: #14202e; border: 1px solid #2a4a6a;
                     border-radius: 6px; padding: 8px 18px; color: #6ab0f5;
                     font-size: 0.88rem; cursor: pointer; font-family: inherit; }
.search-bar button:hover { background: #1a2a3e; }
.search-filters { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 18px; }
.filter-chip { font-size: 0.75rem; padding: 3px 10px; border-radius: 4px;
               background: #0e1220; border: 1px solid #1a2a3a; color: #4a6880; }
.filter-chip a { color: #4a6880; }
.filter-chip.active { background: #0e1828; border-color: #2a4a6a; color: #6ab0f5; }
.search-result { border: 1px solid #1a2232; border-radius: 6px; padding: 12px 16px;
                 margin-bottom: 8px; background: #0e1018; }
.search-result .sr-header { display: flex; align-items: baseline; gap: 8px;
                             margin-bottom: 6px; }
.sr-type-badge { font-size: 0.70rem; padding: 2px 7px; border-radius: 4px;
                 font-weight: 600; letter-spacing: 0.03em; }
.sr-type-badge.globe       { background: #0e1828; color: #4a88c8; }
.sr-type-badge.proposal    { background: #0e1820; color: #4aa878; }
.sr-type-badge.deliberation{ background: #14141e; color: #7878c8; }
.sr-type-badge.claim       { background: #1a1408; color: #c8a040; }
.sr-type-badge.directive   { background: #141820; color: #6888a8; }
.sr-type-badge.log         { background: #0c1410; color: #3a7848; }
.sr-type-badge.feedback    { background: #100c18; color: #7848a8; }
.sr-type-badge.link        { background: #101820; color: #3858a8; }
.sr-title a { color: #8898b0; font-size: 0.90rem; font-weight: 600; }
.sr-title span { color: #8898b0; font-size: 0.90rem; font-weight: 600; }
.sr-meta { font-size: 0.76rem; color: #3a4a62; margin-top: 4px; }
.sr-excerpt { font-size: 0.82rem; color: #5a6a7a; margin-top: 5px;
              line-height: 1.5; white-space: pre-wrap; word-break: break-word; }
.sr-reason { font-size: 0.72rem; color: #253040; margin-top: 4px; }
.search-advisory { font-size: 0.76rem; color: #182030; margin: 14px 0;
                   padding: 8px 12px; border: 1px solid #101820; border-radius: 5px;
                   background: #08090f; }
.search-empty { color: #3a4a5a; font-size: 0.88rem; padding: 18px 0; }
/* Phase 30 — Cross-Phase Contribution Summary panel */
.xphase-panel { background: #08090f; border: 1px solid #161e30;
                border-radius: 8px; padding: 16px 22px; margin: 18px 0; }
.xphase-panel h3 { font-size: 0.88rem; color: #3a5070; margin-bottom: 12px;
                   text-transform: uppercase; letter-spacing: 0.04em; }
.xphase-metric { display: grid; grid-template-columns: 240px 1fr;
                 gap: 4px 12px; font-size: 0.83rem; margin-bottom: 4px; }
.xphase-metric .xp-label { color: #2a3a52; }
.xphase-metric .xp-value { color: #4a6880; }
.xphase-interp { background: #090c12; border: 1px solid #111820;
                 border-radius: 6px; padding: 10px 14px; margin-top: 10px;
                 font-size: 0.82rem; }
.xphase-interp .xi-title { color: #2a3a52; font-size: 0.76rem;
                            text-transform: uppercase; letter-spacing: 0.04em;
                            margin-bottom: 6px; }
.xphase-interp .xi-item  { color: #3a5068; margin-bottom: 3px; }
.xphase-advisory { font-size: 0.72rem; color: #182030; margin-top: 10px;
                   border-top: 1px solid #0e1420; padding-top: 8px; }
footer { text-align: center; font-size: 0.72rem; color: #2a3040;
         padding: 32px 0 16px; }
"""

def _page(title: str, breadcrumb: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} — Dan-Go Globe</title>
<style>{CSS}</style>
</head>
<body>
<header>
  <div>
    <h1>🌐 Dan-Go Globe</h1>
    <div class="subtitle">自由参加型共同体 · Deliberative Consensus · Phase 22</div>
  </div>
</header>
<div class="breadcrumb">{breadcrumb}</div>
<main>
{body}
</main>
<footer>Dan-Go Mujin Protocol · authority: none · append-only · stdlib only<br>
AI is not a governor. AI is a mediator, missionary, and recorder.</footer>
</body>
</html>"""

def _e(s) -> str:
    return html.escape(str(s)) if s else ""

def _badge(status: str) -> str:
    return STATUS_BADGE.get(status, (f'<span class="badge">{_e(status)}</span>', ""))[0]

def _gitsea_html(link: dict | None) -> str:
    if not link:
        return '<p class="empty">GITSEA link not yet configured.</p>'
    rows = []
    for field in ["gitsea_repo_url", "gitsea_issue_url", "gitsea_pr_url", "commit_hash", "linked_rule_path"]:
        val = link.get(field)
        if val:
            label = field.replace("_", " ")
            if field.endswith("_url"):
                val_html = f'<a href="{_e(val)}" target="_blank">{_e(val)}</a>'
            else:
                val_html = f'<code>{_e(val)}</code>'
            rows.append(f'<div class="field-row"><span class="label">{_e(label)}</span>'
                        f'<span class="value">{val_html}</span></div>')
    if not rows:
        return '<p class="empty">GITSEA link fields not yet populated.</p>'
    return '<div class="gitsea-box">' + "".join(rows) + "</div>"

# ─── Phase 31: Search / Filter ──────────────────────────────────────────────

_SEARCH_INDEX_PATH = _REPORTS_DIR / "globe_search_index.json"

_SR_TYPE_ICONS = {
    "globe":        "🌐",
    "proposal":     "📋",
    "deliberation": "💬",
    "claim":        "📌",
    "directive":    "🗂️",
    "log":          "📝",
    "feedback":     "🔗",
    "link":         "🔗",
}


def _load_search_index() -> list[dict]:
    """Phase 31 — load globe_search_index.json or build on-the-fly.

    Search is advisory display only. Not proof of relevance. No ranking.
    """
    if _SEARCH_INDEX_PATH.exists():
        try:
            raw = json.loads(_SEARCH_INDEX_PATH.read_text(encoding="utf-8"))
            if isinstance(raw, dict) and "items" in raw:
                return raw["items"]
        except Exception:
            pass
    try:
        import importlib.util as _ilu
        _mod = Path(__file__).parent / "globe_search.py"
        spec = _ilu.spec_from_file_location("globe_search", _mod)
        mod = _ilu.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        return mod.build_index()["items"]
    except Exception:
        return []


def _render_search_result(r: dict) -> str:
    """Render a single search result card. Advisory display only."""
    itype = r.get("item_type", "")
    icon = _SR_TYPE_ICONS.get(itype, "•")
    url = r.get("url_path", "")
    title = _e(r.get("title", r.get("item_id", "")))
    title_html = (f'<a href="{_e(url)}">{title}</a>' if url else f'<span>{title}</span>')

    meta_parts = []
    if r.get("globe_id"):
        meta_parts.append(f'globe: {_e(r["globe_id"])}')
    if r.get("entry_type"):
        meta_parts.append(f'entry_type: {_e(r["entry_type"])}')
    if r.get("resolution_status"):
        meta_parts.append(f'resolution_status: {_e(r["resolution_status"])}')
    if r.get("bridge_target"):
        meta_parts.append(f'bridge_target: {_e(r["bridge_target"])}')
    if r.get("confidence"):
        meta_parts.append(f'confidence: {_e(r["confidence"])}')
    if r.get("created_at"):
        meta_parts.append(f'{_e(r["created_at"][:10])}')
    meta_html = " &nbsp;·&nbsp; ".join(meta_parts)

    excerpt = _e(r.get("content_excerpt", ""))
    reason  = _e(r.get("match_reason", ""))
    src     = _e(r.get("source_path", ""))

    return f"""
<div class="search-result">
  <div class="sr-header">
    <span class="sr-type-badge {_e(itype)}">{icon} {_e(itype)}</span>
    <span class="sr-title">{title_html}</span>
  </div>
  <div class="sr-meta">{meta_html}</div>
  {f'<div class="sr-excerpt">{excerpt}</div>' if excerpt else ''}
  <div class="sr-reason">match: {reason} &nbsp;·&nbsp; <code style="font-size:0.70rem;color:#1e2838">{src}</code></div>
</div>"""


def render_search_page(
    query: str | None = None,
    globe_filter: str | None = None,
    entry_type_filter: str | None = None,
    resolution_status_filter: str | None = None,
    bridge_target_filter: str | None = None,
) -> str:
    """Phase 31 — Search / Filter page.

    Search is advisory display only. Not proof of relevance. No ranking.
    No execution buttons. No allocation buttons.
    """
    # Load index and run search / filter
    index_items = _load_search_index()

    # Import search function dynamically
    try:
        import importlib.util as _ilu
        _mod = Path(__file__).parent / "globe_search.py"
        spec = _ilu.spec_from_file_location("globe_search", _mod)
        mod = _ilu.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        results = mod.search(
            index_items,
            query=query or None,
            globe_id=globe_filter or None,
            entry_type=entry_type_filter or None,
            resolution_status=resolution_status_filter or None,
            bridge_target=bridge_target_filter or None,
        )
    except Exception:
        results = []

    # ── Search bar ────────────────────────────────────────────────────────
    q_val = _e(query or "")
    search_bar = f"""
<form method="GET" action="/globe/search">
  <div class="search-bar">
    <input type="text" name="q" value="{q_val}"
           placeholder="キーワード検索 — 住居 / D.R.A. / unresolved / directive …">
    <button type="submit">🔍 Search</button>
  </div>"""

    # Preserve active filters as hidden inputs
    if globe_filter:
        search_bar += f'<input type="hidden" name="globe" value="{_e(globe_filter)}">'
    if entry_type_filter:
        search_bar += f'<input type="hidden" name="entry_type" value="{_e(entry_type_filter)}">'
    if resolution_status_filter:
        search_bar += f'<input type="hidden" name="resolution_status" value="{_e(resolution_status_filter)}">'
    if bridge_target_filter:
        search_bar += f'<input type="hidden" name="bridge_target" value="{_e(bridge_target_filter)}">'
    search_bar += "</form>"

    # ── Filter chips ──────────────────────────────────────────────────────
    def _chip(label: str, href: str, active: bool) -> str:
        cls = "filter-chip active" if active else "filter-chip"
        return f'<span class="{cls}"><a href="{href}">{label}</a></span>'

    q_param = f"?q={_e(query)}" if query else "?"

    chips = ""
    # Globe chips
    globes = _globes()
    for g in globes:
        gid = g["globe_id"]
        active = globe_filter == gid
        chips += _chip(
            f'🌐 {_e(g["name"][:12])}',
            f'/globe/search{q_param}{"&" if query else ""}globe={_e(gid)}',
            active
        )
    # Entry type chips
    for et in ["human_approval", "observation", "objection", "rollback_request",
               "voluntary_resolution_signal"]:
        active = entry_type_filter == et
        chips += _chip(
            f'📝 {et.replace("_"," ")}',
            f'/globe/search{q_param}{"&" if query else ""}entry_type={_e(et)}',
            active
        )
    # Resolution status chips
    for rs in ["resolved", "partially_resolved", "paused", "unresolved", "contested"]:
        active = resolution_status_filter == rs
        chips += _chip(
            f'🏳️ {rs}',
            f'/globe/search{q_param}{"&" if query else ""}resolution_status={_e(rs)}',
            active
        )
    # Bridge target chips
    for bt in ["relief_case_memory", "care_loop_reopen", "both", "none"]:
        active = bridge_target_filter == bt
        chips += _chip(
            f'🔗 {bt}',
            f'/globe/search{q_param}{"&" if query else ""}bridge_target={_e(bt)}',
            active
        )
    # Clear filter link
    clear_href = f'/globe/search?q={_e(query)}' if query else '/globe/search'
    chips += _chip('✕ clear filters', clear_href, False)
    filter_row = f'<div class="search-filters">{chips}</div>'

    # ── Result list ───────────────────────────────────────────────────────
    active_filters = [
        x for x in [globe_filter, entry_type_filter,
                     resolution_status_filter, bridge_target_filter] if x
    ]
    has_query   = bool(query)
    has_filters = bool(active_filters)

    if not has_query and not has_filters:
        result_html = '<p class="search-empty">キーワードを入力するか、フィルタを選択してください。<br>Search is advisory display only · no ranking · no allocation</p>'
        count_html  = ""
    else:
        count_html = (
            f'<p style="font-size:0.82rem;color:#3a4a5a;margin-bottom:12px">'
            f'{len(results)} 件 — advisory display only · not proof of relevance · no ranking</p>'
        )
        if results:
            result_html = "".join(_render_search_result(r) for r in results)
        else:
            result_html = '<p class="search-empty">一致する項目が見つかりませんでした。</p>'

    advisory = """
<div class="search-advisory">
  <strong>Search is advisory display only.</strong> ·
  Search result is not proof of relevance. ·
  Search result does not rank participants. ·
  Search result does not allocate resources. ·
  Human review is required before any real-world action. ·
  authority: none
</div>"""

    body = f"""
<h2>🔍 Globe 横断検索 / Search &amp; Filter <small style="font-size:0.7em;color:#3a4258">(Phase 31)</small></h2>
{search_bar}
{filter_row}
{advisory}
{count_html}
{result_html}"""

    return _page(
        "Globe 検索",
        '<a href="/globe">Globe</a> › Search',
        body
    )


# ─── Page renderers ────────────────────────────────────────────────────────────

def render_globe_list() -> str:
    globes = _globes()
    if not globes:
        items = '<p class="empty">グローブがまだ登録されていません。<br>globe/runtime/globe_registry.py create で追加できます。</p>'
    else:
        items = ""
        for g in globes:
            proposals_for = [p for p in _proposals() if p.get("globe_id") == g["globe_id"]]
            items += f"""
<div class="card">
  <h4><a href="/globe/{_e(g['globe_id'])}">{_e(g['name'])}</a></h4>
  <div class="desc">{_e(g.get('description',''))}</div>
  <div class="meta">
    <span class="tag">{_e(g.get('governance_model',''))}</span>
    <span class="tag">membership: {_e(g.get('membership_policy',''))}</span>
    <span class="tag">{len(proposals_for)} proposals</span>
    <span style="margin-left:8px;color:#3a4258">Created {_e(g.get('created_at','')[:10])}</span>
    &nbsp;·&nbsp; <a href="/globe/{_e(g['globe_id'])}">詳細 →</a>
  </div>
</div>"""
    exec_summary_html = _render_exec_summary_panel()
    cross_phase_html = _render_cross_phase_panel()   # Phase 30
    return _page(
        "Globe 一覧",
        '<a href="/globe">Globe</a>',
        f'<h2>🌐 Globe 一覧 <small style="font-size:0.7em;color:#3a4258">({len(globes)})</small>'
        f'&nbsp;<a href="/globe/search" style="font-size:0.65em;color:#4a6880">🔍 検索 →</a></h2>'
        + items
        + exec_summary_html
        + cross_phase_html
        + '<p style="margin-top:24px;font-size:0.8rem;color:#3a4258">'
        + 'Globe = 自由参加型共同体の単位。国家・自治体・DAO・コミュニティ・プロジェクトを包含できる。</p>'
    )


def render_globe_detail(globe_id: str) -> str | None:
    globes = _globes()
    g = next((x for x in globes if x["globe_id"] == globe_id), None)
    if not g:
        return None

    # Directive / Log counts for this globe
    globe_directives = _load_directives_for_globe(globe_id)
    dir_log_total = 0
    dir_approval_total = 0
    for gd in globe_directives:
        elog = _load_exec_log_by_id(gd["directive_id"])
        dir_log_total += len(elog)
        dir_approval_total += sum(1 for e in elog if e.get("entry_type") == "human_approval")
    dir_count = len(globe_directives)

    proposals_for = [p for p in _proposals() if p.get("globe_id") == globe_id]
    proposal_html = ""
    for p in proposals_for:
        delibs = [d for d in _deliberations() if d.get("proposal_id") == p["proposal_id"]]
        proposal_html += f"""
<div class="card">
  <h4><a href="/globe/{_e(globe_id)}/proposals/{_e(p['proposal_id'])}">{_e(p['title'])}</a>
    &nbsp;{_badge(p.get('status','draft'))}</h4>
  <div class="meta">
    提案者: {_e(p.get('proposer','?'))} &nbsp;·&nbsp;
    熟議: {len(delibs)} entries &nbsp;·&nbsp;
    {_e(p.get('created_at','')[:10])}
    &nbsp;·&nbsp; <a href="/globe/{_e(globe_id)}/proposals/{_e(p['proposal_id'])}">詳細 →</a>
  </div>
</div>"""
    if not proposal_html:
        proposal_html = '<p class="empty">まだ提案がありません。</p>'

    body = f"""
<h2>🌐 {_e(g['name'])}</h2>
<div class="desc" style="margin-bottom:16px">{_e(g.get('description',''))}</div>

<h3>基本情報</h3>
<div class="card">
  <div class="field-row"><span class="label">governance_model</span>
    <span class="value">{_e(g.get('governance_model',''))}</span></div>
  <div class="field-row"><span class="label">membership_policy</span>
    <span class="value">{_e(g.get('membership_policy',''))}</span></div>
  <div class="field-row"><span class="label">created_at</span>
    <span class="value">{_e(g.get('created_at','')[:10])}</span></div>
</div>

<h3>founding_statement</h3>
<div class="founding">{_e(g.get('founding_statement',''))}</div>

<h3>GITSEA 連携情報</h3>
{_gitsea_html(g.get('gitsea_link'))}

<h3>🗂️ Directives &nbsp;<a href="/globe/{_e(globe_id)}/directives" style="font-size:0.8rem">すべて見る →</a></h3>
<div class="card">
  <div class="field-row">
    <span class="label">Directive 数</span>
    <span class="value">{dir_count} 件</span>
  </div>
  <div class="field-row">
    <span class="label">Execution Log entries</span>
    <span class="value">{dir_log_total} エントリ &nbsp;·&nbsp; ✅ approvals: {dir_approval_total}</span>
  </div>
  <div class="field-row" style="margin-top:6px">
    <span class="label"></span>
    <span class="value">
      <a href="/globe/{_e(globe_id)}/directives">Directive 一覧 →</a>
    </span>
  </div>
</div>

<h3>Proposal 一覧 &nbsp;<a href="/globe/{_e(globe_id)}/proposals" style="font-size:0.8rem">すべて見る →</a></h3>
{proposal_html}
{_render_exec_summary_panel(globe_id)}
{_render_cross_phase_panel(globe_id)}
"""
    return _page(
        g["name"],
        f'<a href="/globe">Globe</a> › {_e(g["name"])}',
        body
    )


def render_proposals_list(globe_id: str) -> str | None:
    globes = _globes()
    g = next((x for x in globes if x["globe_id"] == globe_id), None)
    if not g:
        return None
    proposals_for = [p for p in _proposals() if p.get("globe_id") == globe_id]
    items = ""
    for p in proposals_for:
        delibs = [d for d in _deliberations() if d.get("proposal_id") == p["proposal_id"]]
        items += f"""
<div class="card">
  <h4><a href="/globe/{_e(globe_id)}/proposals/{_e(p['proposal_id'])}">{_e(p['title'])}</a>
    &nbsp;{_badge(p.get('status','draft'))}</h4>
  <div class="meta">
    提案者: {_e(p.get('proposer','?'))} &nbsp;·&nbsp;
    熟議ログ: {len(delibs)} &nbsp;·&nbsp; {_e(p.get('created_at','')[:10])}
  </div>
</div>"""
    if not items:
        items = '<p class="empty">まだ提案がありません。</p>'
    return _page(
        f"Proposals — {g['name']}",
        f'<a href="/globe">Globe</a> › <a href="/globe/{_e(globe_id)}">{_e(g["name"])}</a> › Proposals',
        f'<h2>📋 Proposals — {_e(g["name"])}</h2>' + items
    )


def _render_claim_status(proposal_id: str, status: str) -> str:
    """Render the Claim conversion status box for a proposal detail page."""
    if status != "accepted":
        return ""
    claim = _load_claim(proposal_id)
    if claim:
        claim_id = _e(claim.get("claim_id", ""))
        delib_count = claim.get("deliberation_count", 0)
        created = _e(str(claim.get("created_at", ""))[:10])
        return f"""
<h3>🔖 Dan-Go Claim 変換状況</h3>
<div class="claim-box converted">
  ✅ Claim 変換済み &nbsp;
  <span class="claim-id">{claim_id}</span><br>
  <span style="font-size:0.8rem;color:#3a6a50">
    熟議エントリ: {delib_count} &nbsp;·&nbsp; 変換日: {created}
    &nbsp;·&nbsp; status: claim_draft
  </span>
  <div class="claim-hint">
    globe/claims/{claim_id}.json &nbsp;/&nbsp; globe/claims/{claim_id}.md<br>
    authority: none · claim_creates_obligation: false
  </div>
</div>"""
    else:
        return f"""
<h3>🔖 Dan-Go Claim 変換状況</h3>
<div class="claim-box not-converted">
  ⬜ 未変換 — この Proposal はまだ Claim に変換されていません。<br>
  <code style="font-size:0.8rem;color:#3a4a5a">
    python3 globe/runtime/proposal_to_claim.py convert {_e(proposal_id)}
  </code>
  <div class="claim-hint">
    accepted 状態の Proposal のみ Claim に変換できます。<br>
    Proposal is not execution. Claim is not command. Conversion is not allocation.
  </div>
</div>"""


def _render_directive_status(proposal_id: str, status: str) -> str:
    """Render the Directive conversion status box — only shown when a claim exists."""
    if status != "accepted":
        return ""
    # Directive only meaningful once a claim exists
    claim = _load_claim(proposal_id)
    if not claim:
        return ""
    claim_id = f"claim-{proposal_id}"
    directive = _load_directive(proposal_id)
    if directive:
        did = _e(directive.get("directive_id", ""))
        steps = directive.get("execution_steps", [])
        created = _e(str(directive.get("created_at", ""))[:10])
        return f"""
<h3>🗂️ Dan-Go Directive 変換状況</h3>
<div class="directive-box converted">
  ✅ Directive 変換済み &nbsp;
  <span class="dir-id">{did}</span><br>
  <span style="font-size:0.8rem;color:#806030">
    実行ステップ: {len(steps)} &nbsp;·&nbsp; 変換日: {created}
    &nbsp;·&nbsp; status: directive_draft
  </span>
  <div class="dir-hint">
    globe/directives/{did}.json &nbsp;/&nbsp; globe/directives/{did}.md<br>
    authority: none · directive_creates_legal_authority: false · human_approval_required: true
  </div>
</div>"""
    else:
        return f"""
<h3>🗂️ Dan-Go Directive 変換状況</h3>
<div class="directive-box not-converted">
  ⬜ 未変換 — Claim はありますが、まだ Directive に変換されていません。<br>
  <code style="font-size:0.8rem;color:#3a3828">
    python3 globe/runtime/claim_to_directive.py convert {_e(claim_id)}
  </code>
  <div class="dir-hint">
    claim_draft 状態の Claim のみ Directive に変換できます。<br>
    Claim is not execution. Directive is not coercion. Directive creates no legal authority.
  </div>
</div>"""


_EXEC_ENTRY_ICON = {
    "human_approval":              "✅",
    "execution_attempt":           "▶",
    "observation":                 "👁",
    "feedback":                    "💬",
    "objection":                   "⚠",
    "rollback_request":            "↩",
    "voluntary_resolution_signal": "🏳️",   # Phase 29
}

_RS_ICON = {
    "resolved":           "✅",
    "partially_resolved": "🟡",
    "paused":             "⏸️",
    "unresolved":         "🔴",
    "contested":          "⚔️",
}


def _render_execution_log_status(proposal_id: str, status: str) -> str:
    """Render Execution Log status — only shown when a directive exists."""
    if status != "accepted":
        return ""
    directive = _load_directive(proposal_id)
    if not directive:
        return ""

    directive_id = f"directive-claim-{proposal_id}"
    entries = _load_exec_log(proposal_id)
    has_approval = any(e.get("entry_type") == "human_approval" for e in entries)

    if not entries:
        return f"""
<h3>📋 Execution Log</h3>
<div class="log-box no-entries">
  ⬜ ログなし — まだエントリが記録されていません。<br>
  <code style="font-size:0.8rem;color:#2a3858">
    python3 globe/runtime/directive_execution_log.py append {_e(directive_id)} human_approval human &lt;name&gt; &lt;content&gt;
  </code>
  <div class="log-hint">
    legal_authority_created: false · log_is_proof_of_execution: false · append_only: true
  </div>
</div>"""

    # Count by type
    counts: dict[str, int] = {}
    for e in entries:
        et = e.get("entry_type", "unknown")
        counts[et] = counts.get(et, 0) + 1

    last = entries[-1]
    last_icon = _EXEC_ENTRY_ICON.get(last.get("entry_type", ""), "•")
    last_actor = _e(last.get("actor_name", "?"))
    last_type = _e(last.get("entry_type", "?"))

    box_class = "log-box approved" if has_approval else "log-box has-entries"
    approval_html = (
        '✅ human_approval 記録済み'
        if has_approval else
        '⚠ human_approval 未記録 — 実世界アクション前に必要'
    )

    badges = "".join(
        f'<span class="log-entry-badge">{_EXEC_ENTRY_ICON.get(et,"•")} {_e(et)}: {n}</span>'
        for et, n in counts.items()
    )

    return f"""
<h3>📋 Execution Log &nbsp;<small style="font-size:0.75rem;color:#2a3858">({len(entries)} entries · {_e(directive_id)})</small></h3>
<div class="{box_class}">
  {approval_html}<br>
  <span style="font-size:0.82rem;color:#3a5070;margin-top:6px;display:block">
    {badges}
  </span>
  <span style="font-size:0.78rem;color:#3a4a68;margin-top:6px;display:block">
    last entry: {last_icon} {last_type} by {last_actor}
    ({_e(str(last.get('created_at',''))[:10])})
  </span>
  <div class="log-hint">
    legal_authority_created: false · log_is_proof_of_execution: false ·
    objection_always_recordable: true · append_only: true
  </div>
</div>"""


def _render_exec_summary_panel(globe_id: str | None = None) -> str:
    """Render a cross-globe (or per-globe) execution log summary panel.

    If globe_id is given, shows only that globe's directives.
    Summary is advisory only — not proof of execution, no authority.
    """
    summary = _load_exec_summary()
    if not summary:
        return ""

    if globe_id:
        by_globe = summary.get("by_globe", [])
        g_rec = next((g for g in by_globe if g["globe_id"] == globe_id), None)
        if not g_rec:
            return ""
        directives = [
            d for d in summary.get("directives", [])
            if d["globe_id"] == globe_id
        ]
        total_entries = g_rec["total_entries"]
        total_obj = g_rec["objection_count"]
        total_rb = g_rec["rollback_request_count"]
        header = f"📋 Execution Log Summary — {_e(globe_id)}"
    else:
        directives = summary.get("directives", [])
        total_entries = summary.get("total_log_entries", 0)
        total_obj = summary.get("total_objections", 0)
        total_rb = summary.get("total_rollback_requests", 0)
        header = "📋 Cross-Globe Execution Log Summary (Phase 26)"

    if not directives:
        return ""

    rows = ""
    for d in directives:
        appr_icon = "✅" if d["has_human_approval"] else "⬜"
        last_icon = _EXEC_ENTRY_ICON.get(d.get("last_entry_type", ""), "•")
        # Phase 29 — resolution signal cell
        lrs = d.get("latest_resolution_status", "")
        rs_count = d.get("resolution_signal_count", 0)
        if rs_count and lrs:
            rs_icon = _RS_ICON.get(lrs, "•")
            sig_cell = f'<span title="self-reported · not proof">{rs_icon} {_e(lrs)}</span>'
        else:
            sig_cell = "—"
        rows += f"""
<tr>
  <td>{_e(d['directive_id'])}</td>
  <td>{_e(d['globe_id'])}</td>
  <td style="text-align:center">{d['total_entries']}</td>
  <td style="text-align:center">{appr_icon} {d['human_approval_count']}</td>
  <td style="text-align:center">⚠ {d['objection_count']}</td>
  <td style="text-align:center">↩ {d['rollback_request_count']}</td>
  <td style="text-align:center">{sig_cell}</td>
  <td>{last_icon} {_e(d.get('last_entry_type','—'))}</td>
</tr>"""

    gen = str(summary.get("generated_at", ""))[:19].replace("T", " ")
    # Phase 29 totals
    total_sig = summary.get("total_resolution_signals", 0)
    sig_html = ""
    if total_sig:
        total_sig = summary.get("total_resolution_signals", 0)
        sig_html = (
            f"&nbsp;·&nbsp; 🏳️ signals: {total_sig} "
            f"(✅ {summary.get('total_resolved',0)} "
            f"🟡 {summary.get('total_partially_resolved',0)} "
            f"⏸️ {summary.get('total_paused',0)} "
            f"🔴 {summary.get('total_unresolved',0)} "
            f"⚔️ {summary.get('total_contested',0)}) "
            f'<span style="color:#2a3050;font-size:0.72rem">self-reported · not proof</span>'
        )

    return f"""
<div class="exec-summary-panel">
  <h3>{header}</h3>
  <table class="exec-summary-table">
    <tr>
      <th>Directive</th><th>Globe</th><th>Entries</th>
      <th>Approvals</th><th>Objections</th><th>Rollbacks</th>
      <th>🏳️ Signal</th><th>Last</th>
    </tr>
    {rows}
  </table>
  <div style="margin-top:8px;font-size:0.78rem;color:#3a5070">
    Total entries: {total_entries} &nbsp;·&nbsp;
    Objections: {total_obj} &nbsp;·&nbsp;
    Rollbacks: {total_rb}
    {sig_html}
  </div>
  <div class="exec-advisory">
    Summary is advisory only · not proof of execution · creates no legal authority ·
    generated: {_e(gen)}
  </div>
</div>"""


_ADVISORY_BANNER = (
    '<div class="advisory-banner">'
    "UI display is advisory only · not proof of execution · creates no legal authority · "
    "UI display does not approve execution · objections and rollback requests are preserved."
    "</div>"
)

_EXEC_LOG_ADVISORY_BANNER = (
    '<div class="advisory-banner">'
    "Execution Log is not proof of execution · Log entry is not legal authority · "
    "Append-only: existing entries must never be rewritten · "
    "Objection and rollback request must always be recordable."
    "</div>"
)


def render_directives_list(globe_id: str) -> str | None:
    """List all Directives for a Globe. Advisory display only."""
    globes = _globes()
    g = next((x for x in globes if x["globe_id"] == globe_id), None)
    if not g:
        return None

    directives = _load_directives_for_globe(globe_id)
    items = ""
    for d in directives:
        did = d["directive_id"]
        entries = _load_exec_log_by_id(did)
        has_approval = any(e.get("entry_type") == "human_approval" for e in entries)

        last_type = "—"
        last_at = "—"
        if entries:
            last = entries[-1]
            last_type = last.get("entry_type", "—")
            last_at = str(last.get("created_at", ""))[:10]

        appr_icon = "✅" if has_approval else "⬜"
        last_icon = _EXEC_ENTRY_ICON.get(last_type, "•")

        items += f"""
<div class="card">
  <h4>
    <a href="/globe/{_e(globe_id)}/directives/{_e(did)}">{_e(d.get('title', did))}</a>
  </h4>
  <div style="font-family:monospace;font-size:0.78rem;color:#3a4a6a;margin:4px 0 6px">{_e(did)}</div>
  <div class="desc">{_e(d.get('objective',''))}</div>
  <div class="meta" style="margin-top:10px">
    <span class="tag">source: {_e(d.get('source_claim_id','?'))}</span>
    <span class="tag">steps: {len(d.get('execution_steps',[]))}</span>
    <span class="tag">log: {len(entries)} entries</span>
    <span class="tag">{appr_icon} approval</span>
    <span class="tag">last: {last_icon} {_e(last_type)} {_e(last_at)}</span>
    &nbsp;·&nbsp;
    <a href="/globe/{_e(globe_id)}/directives/{_e(did)}">Directive 詳細 →</a>
    &nbsp;·&nbsp;
    <a href="/globe/{_e(globe_id)}/logs/{_e(did)}">Execution Log →</a>
  </div>
</div>"""

    if not items:
        items = '<p class="empty">この Globe にはまだ Directive がありません。</p>'

    return _page(
        f"Directives — {g['name']}",
        f'<a href="/globe">Globe</a> › '
        f'<a href="/globe/{_e(globe_id)}">{_e(g["name"])}</a> › Directives',
        f'<h2>🗂️ Directives — {_e(g["name"])}</h2>'
        + _ADVISORY_BANNER
        + items,
    )


def _render_invariant_table(d: dict) -> str:
    """Render invariant key/value table for a directive."""
    fields = [
        "authority", "execution_allowed", "moves_money", "hard_enforcement",
        "advisory", "append_only", "contestable", "human_approval_required",
        "directive_creates_legal_authority", "directive_is_coercion",
        "directive_creates_obligation", "conversion_is_execution",
        "directive_certifies_outcome", "directive_allocates_resources",
    ]
    rows = ""
    for f in fields:
        val = d.get(f)
        if val is None:
            val_str, css = "—", "invar-none"
        elif val is False or val == "none":
            val_str, css = str(val).lower(), "invar-false"
        else:
            val_str, css = str(val).lower(), ""
        rows += f'<tr><td>{_e(f)}</td><td class="{css}">{_e(val_str)}</td></tr>'
    return f'<table class="invariant-table">{rows}</table>'


def render_directive_detail(globe_id: str, directive_id: str) -> str | None:
    """Full Directive detail page. Advisory display only."""
    globes = _globes()
    g = next((x for x in globes if x["globe_id"] == globe_id), None)
    if not g:
        return None

    d = _load_directive_by_id(directive_id)
    if not d or d.get("globe_id") != globe_id:
        return None

    entries = _load_exec_log_by_id(directive_id)
    has_approval = any(e.get("entry_type") == "human_approval" for e in entries)

    # Execution steps
    steps_html = ""
    for step in d.get("execution_steps", []):
        sid = _e(step.get("step_id", ""))
        desc_ja = _e(step.get("description", ""))
        desc_en = step.get("description_en", "")
        contribs = ", ".join(_e(c) for c in step.get("required_contributions", []))
        step_status = step.get("status", "pending")
        need_appr = step.get("human_approval_required", True)
        steps_html += f"""
<div class="directive-step">
  <div class="step-id">{sid}
    <span class="step-badge {_e(step_status)}">{_e(step_status)}</span>
    {"<span class='step-badge pending'>human approval required</span>" if need_appr else ""}
  </div>
  <div class="step-desc">{desc_ja}</div>
  {"<div class='step-desc' style='color:#5a6a80'>" + _e(desc_en) + "</div>" if desc_en else ""}
  <div class="step-meta">required contributions: {contribs or "—"}</div>
</div>"""

    # Required evidence
    ev_items = "".join(
        f'<li style="color:#6a7a90;margin-bottom:4px">{_e(ev)}</li>'
        for ev in d.get("required_evidence", [])
    )
    evidence_html = (
        f'<ul style="margin-left:18px;line-height:1.8">{ev_items}</ul>'
        if ev_items else '<p class="empty">なし</p>'
    )

    # Scope
    in_items  = "".join(f"<li>{_e(s)}</li>" for s in d.get("scope", {}).get("in_scope", []))
    out_items = "".join(f"<li>{_e(s)}</li>" for s in d.get("scope", {}).get("out_of_scope", []))
    scope_html = f"""
<div style="margin-bottom:12px">
  <div style="font-size:0.8rem;color:#3a5a40;margin-bottom:4px">✅ In Scope</div>
  <ul class="scope-list">{in_items}</ul>
</div>
<div>
  <div style="font-size:0.8rem;color:#5a3a3a;margin-bottom:4px">🚫 Out of Scope</div>
  <ul class="scope-list out">{out_items}</ul>
</div>"""

    # Log summary
    counts: dict[str, int] = {}
    for e in entries:
        et = e.get("entry_type", "unknown")
        counts[et] = counts.get(et, 0) + 1
    appr_icon = "✅" if has_approval else "⬜"
    log_badges = "".join(
        f'<span class="log-entry-badge">{_EXEC_ENTRY_ICON.get(et,"•")} {_e(et)}: {n}</span>'
        for et, n in counts.items()
    )
    box_cls = "approved" if has_approval else ("has-entries" if entries else "no-entries")
    approval_label = (
        "✅ human_approval 記録済み" if has_approval else
        "⬜ ログエントリなし" if not entries else
        "⚠ human_approval 未記録"
    )
    # Phase 29 — latest resolution signal for directive detail
    signal_entries = [e for e in entries if e.get("entry_type") == "voluntary_resolution_signal"]
    rs_chip_html = ""
    if signal_entries:
        latest_rs = signal_entries[-1].get("resolution_status", "")
        rs_icon = _RS_ICON.get(latest_rs, "•")
        rs_actor = _e(signal_entries[-1].get("actor_name", "?"))
        rs_chip_html = (
            f'<span class="rs-badge {_e(latest_rs)}" '
            f'title="self-reported · not proof · does not close support automatically">'
            f"{rs_icon} {_e(latest_rs)}</span>"
            f'<span style="font-size:0.72rem;color:#2a3050;margin-left:6px">'
            f"self-reported by {rs_actor} · not proof"
            f"</span>"
        )

    log_summary_html = f"""
<div class="log-box {box_cls}">
  {approval_label}<br>
  <span style="font-size:0.82rem;display:block;margin-top:6px">{log_badges}</span>
  {f'<div style="margin-top:8px">🏳️ Resolution Signal: {rs_chip_html}</div>' if rs_chip_html else ''}
  <div class="log-hint" style="margin-top:8px">
    Total entries: {len(entries)} &nbsp;·&nbsp;
    <a href="/globe/{_e(globe_id)}/logs/{_e(directive_id)}">Execution Log 全件表示 →</a>
  </div>
</div>"""

    body = f"""
<h2>🗂️ {_e(d.get('title', directive_id))}</h2>
<div style="font-family:monospace;font-size:0.8rem;color:#3a4a6a;margin:4px 0 12px">{_e(directive_id)}</div>
{_ADVISORY_BANNER}

<h3>基本情報</h3>
<div class="card">
  <div class="field-row"><span class="label">source_claim_id</span>
    <span class="value"><code>{_e(d.get('source_claim_id',''))}</code></span></div>
  <div class="field-row"><span class="label">source_proposal_id</span>
    <span class="value"><code>{_e(d.get('source_proposal_id',''))}</code></span></div>
  <div class="field-row"><span class="label">status</span>
    <span class="value">{_e(d.get('status',''))}</span></div>
  <div class="field-row"><span class="label">created_at</span>
    <span class="value">{_e(str(d.get('created_at',''))[:10])}</span></div>
</div>

<h3>Objective（目的）</h3>
<div class="body-block">{_e(d.get('objective',''))}</div>

<h3>Non-Authority Clause</h3>
<div class="founding" style="border-left-color:#3a2a1a">{_e(d.get('non_authority_clause',''))}</div>

<h3>不変条件 / Invariants</h3>
<div class="card" style="padding:10px 12px">
{_render_invariant_table(d)}
</div>

<h3>Execution Steps ({len(d.get('execution_steps',[]))})
  <small style="font-size:0.72rem;color:#2a3858;text-transform:none;font-weight:400">
    execution_allowed: false on all steps
  </small>
</h3>
{steps_html or '<p class="empty">ステップなし</p>'}

<h3>Required Evidence</h3>
{evidence_html}

<h3>Scope</h3>
<div class="card">{scope_html}</div>

<h3>📋 Execution Log Summary
  &nbsp;<a href="/globe/{_e(globe_id)}/logs/{_e(directive_id)}" style="font-size:0.8rem">全件表示 →</a>
</h3>
{log_summary_html}
{_render_bridge_panel(directive_id)}
{_render_link_candidates_panel(directive_id)}
"""
    return _page(
        d.get("title", directive_id),
        f'<a href="/globe">Globe</a> › '
        f'<a href="/globe/{_e(globe_id)}">{_e(g["name"])}</a> › '
        f'<a href="/globe/{_e(globe_id)}/directives">Directives</a> › '
        f'{_e(directive_id)}',
        body,
    )


def render_execution_log_page(globe_id: str, directive_id: str) -> str | None:
    """Full Execution Log viewer. Advisory display only. Preserves objections."""
    globes = _globes()
    g = next((x for x in globes if x["globe_id"] == globe_id), None)
    if not g:
        return None

    d = _load_directive_by_id(directive_id)
    if not d or d.get("globe_id") != globe_id:
        return None

    entries = _load_exec_log_by_id(directive_id)

    counts: dict[str, int] = {}
    for e in entries:
        et = e.get("entry_type", "unknown")
        counts[et] = counts.get(et, 0) + 1

    has_approval = counts.get("human_approval", 0) > 0
    appr_icon = "✅" if has_approval else "⬜"

    # Entry cards (chronological order — JSONL is append-only)
    entry_cards = ""
    for i, e in enumerate(entries, 1):
        et = e.get("entry_type", "unknown")
        icon = _EXEC_ENTRY_ICON.get(et, "•")
        actor_type = _e(e.get("actor_type", "?"))
        actor_name = _e(e.get("actor_name", "?"))
        content = _e(e.get("content", ""))
        created = _e(str(e.get("created_at", ""))[:19].replace("T", " "))
        evidence = e.get("evidence_refs", [])
        evidence_html = ""
        if evidence:
            ev_items = "".join(f"<li><code>{_e(r)}</code></li>" for r in evidence)
            evidence_html = f'<ul style="margin:6px 0 0 16px;font-size:0.78rem;color:#3a4a6a">{ev_items}</ul>'
        legal = e.get("legal_authority_created", False)
        proof = e.get("log_is_proof_of_execution", False)
        append_only = e.get("append_only", True)
        # Phase 29 — resolution signal badge
        rs = e.get("resolution_status", "")
        rs_html = ""
        if et == "voluntary_resolution_signal" and rs:
            rs_icon = _RS_ICON.get(rs, "•")
            rs_html = (
                f'<span class="rs-badge {_e(rs)}">{rs_icon} {_e(rs)}</span>'
                f'<div class="rs-self-reported">'
                f"self-reported only · not proof of resolution · "
                f"does not close support automatically · creates no legal authority"
                f"</div>"
            )
        entry_cards += f"""
<div class="log-entry-card {_e(et)}">
  <div class="entry-header">
    {icon} {_e(et.replace('_', ' '))}
    <span style="font-weight:400;font-size:0.8rem;color:#4a5a78">
      &nbsp;#{i} &nbsp;·&nbsp; {actor_type}: {actor_name} &nbsp;·&nbsp; {created}
    </span>
  </div>
  <div class="entry-content">{content}</div>
  {rs_html}
  {evidence_html}
  <div class="entry-meta">
    legal_authority_created: {str(legal).lower()} &nbsp;·&nbsp;
    log_is_proof_of_execution: {str(proof).lower()} &nbsp;·&nbsp;
    append_only: {str(append_only).lower()}
  </div>
</div>"""

    if not entry_cards:
        entry_cards = '<p class="empty">まだエントリが記録されていません。</p>'

    body = f"""
<h2>📋 Execution Log — {_e(d.get('title', directive_id))}</h2>
<div style="font-family:monospace;font-size:0.8rem;color:#3a4a6a;margin:4px 0 12px">{_e(directive_id)}</div>
{_EXEC_LOG_ADVISORY_BANNER}

<div class="card" style="padding:16px 20px;margin-bottom:18px">
  <div class="stat-grid">
    <div><div class="stat-num">{len(entries)}</div>
         <div class="stat-lbl">total entries</div></div>
    <div><div class="stat-num">{appr_icon} {counts.get('human_approval',0)}</div>
         <div class="stat-lbl">approvals</div></div>
    <div><div class="stat-num">⚠ {counts.get('objection',0)}</div>
         <div class="stat-lbl">objections</div></div>
    <div><div class="stat-num">↩ {counts.get('rollback_request',0)}</div>
         <div class="stat-lbl">rollbacks</div></div>
  </div>
  {_render_resolution_signal_stat(entries)}
  <div style="margin-top:12px;font-size:0.78rem;color:#2a3858;text-align:center">
    source: <code>{_e(d.get('source_claim_id',''))}</code>
    &nbsp;·&nbsp;
    <a href="/globe/{_e(globe_id)}/directives/{_e(directive_id)}">Directive 詳細 →</a>
  </div>
</div>

<h3>Log Entries ({len(entries)}) — chronological · append-only · objection always recordable</h3>
{entry_cards}
{_render_bridge_panel(directive_id)}
{_render_link_candidates_panel(directive_id)}
"""
    return _page(
        f"Execution Log — {directive_id}",
        f'<a href="/globe">Globe</a> › '
        f'<a href="/globe/{_e(globe_id)}">{_e(g["name"])}</a> › '
        f'<a href="/globe/{_e(globe_id)}/directives">Directives</a> › '
        f'<a href="/globe/{_e(globe_id)}/directives/{_e(directive_id)}">{_e(directive_id)}</a> › '
        f'Log',
        body,
    )


def render_proposal_detail(globe_id: str, proposal_id: str) -> str | None:
    globes = _globes()
    g = next((x for x in globes if x["globe_id"] == globe_id), None)
    if not g:
        return None
    proposals_for = _proposals()
    p = next((x for x in proposals_for if x["proposal_id"] == proposal_id), None)
    if not p:
        return None
    delibs = [d for d in _deliberations() if d.get("proposal_id") == proposal_id]

    delib_html = ""
    for d in delibs:
        stype = d.get("speaker_type", "human")
        icon = SPEAKER_ICON.get(stype, "")
        delib_html += f"""
<div class="deliberation {_e(stype)}">
  <div class="speaker">{icon} {_e(d.get('speaker_name','?'))}
    <span style="font-size:0.75rem;color:#3a4258;font-weight:400;margin-left:8px">
      {_e(d.get('created_at','')[:19])} [{_e(d.get('deliberation_id',''))}]
    </span>
  </div>
  <div class="content">{_e(d.get('content',''))}</div>
</div>"""
    if not delib_html:
        delib_html = '<p class="empty">まだ熟議エントリがありません。</p>'

    # Next actions
    status = p.get("status", "draft")
    next_steps = {
        "draft":      ["discussion フェーズに移行する", "提案本文を修正・補足する", "賛同者を募る"],
        "discussion": ["熟議ログにエントリを追加する（python3 globe/runtime/deliberation_log.py append）", "AIメディエーターによる論点整理を実施する", "voting フェーズに移行する"],
        "voting":     ["投票を実施する（Dan-Go 熟議プロセスに従う）", "結果を記録し accepted または rejected に移行する"],
        "accepted":   ["Dan-Go Claim に変換する（python3 globe/runtime/proposal_to_claim.py convert）", "Claim を Directive に変換する（python3 globe/runtime/claim_to_directive.py convert）", "人間の承認を Execution Log に記録する（python3 globe/runtime/directive_execution_log.py append … human_approval）", "実行試行・観察・フィードバック・異議を Execution Log に記録する", "GITSEA リンクを設定し Git 的に管理する"],
        "rejected":   ["反対意見を保存する（すでに保存済み）", "修正提案を新規提案として提出する", "archived に移行する"],
        "archived":   ["履歴として永続保存されています。"],
    }
    next_items = "".join(f"<li>{_e(s)}</li>" for s in next_steps.get(status, []))

    # Claim, Directive, and Execution Log status (only rendered for accepted proposals)
    claim_status_html = _render_claim_status(proposal_id, status)
    directive_status_html = _render_directive_status(proposal_id, status)
    exec_log_html = _render_execution_log_status(proposal_id, status)

    body = f"""
<h2>📋 {_e(p['title'])} &nbsp;{_badge(status)}</h2>
<div class="meta" style="margin-bottom:16px">
  Globe: <a href="/globe/{_e(globe_id)}">{_e(g['name'])}</a> &nbsp;·&nbsp;
  提案者: {_e(p.get('proposer','?'))} &nbsp;·&nbsp;
  {_e(p.get('created_at','')[:10])}
</div>

<h3>提案本文</h3>
<div class="body-block">{_e(p.get('body',''))}</div>

<h3>GITSEA 連携情報</h3>
{_gitsea_html(p.get('gitsea_link'))}
{claim_status_html}
{directive_status_html}
{exec_log_html}
<h3>次の行動案</h3>
<div class="next-actions"><ul>{next_items}</ul></div>

<h3>熟議ログ ({len(delibs)} entries) — append-only · 少数意見保存</h3>
{delib_html}
"""
    return _page(
        p["title"],
        f'<a href="/globe">Globe</a> › '
        f'<a href="/globe/{_e(globe_id)}">{_e(g["name"])}</a> › '
        f'<a href="/globe/{_e(globe_id)}/proposals">Proposals</a> › '
        f'{_e(p["proposal_id"])}',
        body
    )


# ─── HTTP Handler ───────────────────────────────────────────────────────────────

class GlobeHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # Quiet by default; uncomment below for verbose
        # sys.stderr.write(f"[globe] {self.address_string()} {fmt % args}\n")

    def _send_html(self, content: str, status: int = 200):
        encoded = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_redirect(self, location: str):
        self.send_response(302)
        self.send_header("Location", location)
        self.end_headers()

    def _404(self):
        self._send_html(
            _page("404", "404", '<h2>404 — Not Found</h2><p><a href="/globe">← Globe 一覧へ</a></p>'),
            404
        )

    def do_GET(self):
        parsed   = urlparse(self.path)
        path     = parsed.path.rstrip("/") or "/"
        qs       = parse_qs(parsed.query, keep_blank_values=False)

        def _qs(key: str) -> str | None:
            vals = qs.get(key)
            return vals[0].strip() if vals else None

        if path == "/" or path == "":
            self._send_redirect("/globe")
            return

        # Phase 31 — Search / Filter route (must appear before /globe/<id> match)
        if path == "/globe/search":
            self._send_html(render_search_page(
                query=_qs("q"),
                globe_filter=_qs("globe"),
                entry_type_filter=_qs("entry_type"),
                resolution_status_filter=_qs("resolution_status"),
                bridge_target_filter=_qs("bridge_target"),
            ))
            return

        if path == "/globe":
            self._send_html(render_globe_list())
            return

        m = re.fullmatch(r"/globe/([^/]+)", path)
        if m:
            content = render_globe_detail(m.group(1))
            if content:
                self._send_html(content)
            else:
                self._404()
            return

        m = re.fullmatch(r"/globe/([^/]+)/proposals", path)
        if m:
            content = render_proposals_list(m.group(1))
            if content:
                self._send_html(content)
            else:
                self._404()
            return

        m = re.fullmatch(r"/globe/([^/]+)/proposals/([^/]+)", path)
        if m:
            content = render_proposal_detail(m.group(1), m.group(2))
            if content:
                self._send_html(content)
            else:
                self._404()
            return

        # Phase 28 — Directive UI Routes
        m = re.fullmatch(r"/globe/([^/]+)/directives", path)
        if m:
            content = render_directives_list(m.group(1))
            if content:
                self._send_html(content)
            else:
                self._404()
            return

        m = re.fullmatch(r"/globe/([^/]+)/directives/([^/]+)", path)
        if m:
            content = render_directive_detail(m.group(1), m.group(2))
            if content:
                self._send_html(content)
            else:
                self._404()
            return

        m = re.fullmatch(r"/globe/([^/]+)/logs/([^/]+)", path)
        if m:
            content = render_execution_log_page(m.group(1), m.group(2))
            if content:
                self._send_html(content)
            else:
                self._404()
            return

        self._404()


# ─── Main ───────────────────────────────────────────────────────────────────────

def main():
    server = HTTPServer(("127.0.0.1", PORT), GlobeHandler)
    print(f"Dan-Go Globe Server")
    print(f"  → http://localhost:{PORT}/globe")
    print(f"  Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    main()
