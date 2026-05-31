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
    return _page(
        "Globe 一覧",
        '<a href="/globe">Globe</a>',
        f'<h2>🌐 Globe 一覧 <small style="font-size:0.7em;color:#3a4258">({len(globes)})</small></h2>'
        + items
        + exec_summary_html
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
    "human_approval":    "✅",
    "execution_attempt": "▶",
    "observation":       "👁",
    "feedback":          "💬",
    "objection":         "⚠",
    "rollback_request":  "↩",
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
        last_icon = {
            "human_approval": "✅", "execution_attempt": "▶",
            "observation": "👁", "feedback": "💬",
            "objection": "⚠", "rollback_request": "↩",
        }.get(d.get("last_entry_type", ""), "•")
        rows += f"""
<tr>
  <td>{_e(d['directive_id'])}</td>
  <td>{_e(d['globe_id'])}</td>
  <td style="text-align:center">{d['total_entries']}</td>
  <td style="text-align:center">{appr_icon} {d['human_approval_count']}</td>
  <td style="text-align:center">⚠ {d['objection_count']}</td>
  <td style="text-align:center">↩ {d['rollback_request_count']}</td>
  <td>{last_icon} {_e(d.get('last_entry_type','—'))}</td>
</tr>"""

    gen = str(summary.get("generated_at", ""))[:19].replace("T", " ")
    return f"""
<div class="exec-summary-panel">
  <h3>{header}</h3>
  <table class="exec-summary-table">
    <tr>
      <th>Directive</th><th>Globe</th><th>Entries</th>
      <th>Approvals</th><th>Objections</th><th>Rollbacks</th><th>Last</th>
    </tr>
    {rows}
  </table>
  <div style="margin-top:8px;font-size:0.78rem;color:#3a5070">
    Total entries: {total_entries} &nbsp;·&nbsp;
    Objections: {total_obj} &nbsp;·&nbsp;
    Rollbacks: {total_rb}
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
    log_summary_html = f"""
<div class="log-box {box_cls}">
  {approval_label}<br>
  <span style="font-size:0.82rem;display:block;margin-top:6px">{log_badges}</span>
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
        entry_cards += f"""
<div class="log-entry-card {_e(et)}">
  <div class="entry-header">
    {icon} {_e(et.replace('_', ' '))}
    <span style="font-weight:400;font-size:0.8rem;color:#4a5a78">
      &nbsp;#{i} &nbsp;·&nbsp; {actor_type}: {actor_name} &nbsp;·&nbsp; {created}
    </span>
  </div>
  <div class="entry-content">{content}</div>
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
  <div style="margin-top:12px;font-size:0.78rem;color:#2a3858;text-align:center">
    source: <code>{_e(d.get('source_claim_id',''))}</code>
    &nbsp;·&nbsp;
    <a href="/globe/{_e(globe_id)}/directives/{_e(directive_id)}">Directive 詳細 →</a>
  </div>
</div>

<h3>Log Entries ({len(entries)}) — chronological · append-only · objection always recordable</h3>
{entry_cards}
{_render_bridge_panel(directive_id)}
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
        path = self.path.split("?")[0].rstrip("/") or "/"

        if path == "/" or path == "":
            self._send_redirect("/globe")
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
