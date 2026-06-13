"""
app.py — Mujin Contribution Commons (local web app, stdlib only)

    Need -> Contribution -> Connection -> Reality Feedback

Run from the repository root:

    python -m bridge.mujin.platform.app          (default port 8787)
    MUJIN_PORT=9000 python -m bridge.mujin.platform.app

No external dependencies. No database. Append-only JSONL under
bridge/mujin/data/. Existing Dan-Go data is never modified.

No ranking. No scores. No priority order. No value assessment.
People are never measured; only the system's response speed (TTFR) is.
"""

from __future__ import annotations

import html
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, quote, urlparse

from . import commons as C

PORT = int(os.environ.get("MUJIN_PORT", "8787"))


def esc(s: object) -> str:
    return html.escape(str(s if s is not None else ""), quote=True)


# ── layout ────────────────────────────────────────────────────────────────────

STYLE = """
body{font-family:sans-serif;max-width:880px;margin:1.5em auto;padding:0 1em;line-height:1.55}
nav a{margin-right:.9em} .big a{display:block;font-size:1.7em;padding:.6em 1em;margin:.5em 0;
border:2px solid #888;border-radius:10px;text-decoration:none;text-align:center}
.note{background:#f4f4f4;border-left:4px solid #999;padding:.6em .9em;font-size:.92em}
.neg{border-left-color:#c77}
table{border-collapse:collapse;width:100%} td,th{border:1px solid #ccc;padding:.35em .5em;
text-align:left;font-size:.92em;vertical-align:top}
form label{display:block;margin:.5em 0 .1em} input[type=text],textarea,select{width:100%;
padding:.35em;box-sizing:border-box} textarea{min-height:4.5em}
button{margin-top:.8em;padding:.5em 1.4em;font-size:1em}
small.inv{color:#666}
"""

NAV = (
    '<nav><a href="/">Top</a><a href="/need">Need</a>'
    '<a href="/gateways">Gateways</a><a href="/solutions">Solutions</a>'
    '<a href="/funding">Funding</a><a href="/voices">Voices</a>'
    '<a href="/voice-submit">Submit</a><a href="/voice-sources">Sources</a>'
    '<a href="/translations">Translate</a><a href="/voice-discussion">Discuss</a>'
    '<a href="/commons">Commons</a><a href="/proposals">Proposals</a>'
    '<a href="/feedback">Reality Feedback</a><a href="/objection">Objection</a>'
    '<a href="/transparency">Transparency</a>'
    '<a href="/dashboard">TTFR</a></nav><hr>'
)

PHRASES = (
    '<p><small class="inv">登録は証明ではない · 撤回は失敗ではない · 支援は債務ではない · '
    'advisory only は道義的免責ではない · Reach Gap は未解決</small></p>'
)


def page(title: str, body: str) -> str:
    return (f"<!doctype html><html><head><meta charset='utf-8'>"
            f"<title>{esc(title)} — Mujin</title><style>{STYLE}</style></head>"
            f"<body>{NAV}<h1>{esc(title)}</h1>{body}{PHRASES}</body></html>")


def msg_block(query: dict[str, list[str]]) -> str:
    ok = query.get("ok", [""])[0]
    err = query.get("err", [""])[0]
    out = ""
    if ok:
        out += f'<p class="note">✓ {esc(ok)}</p>'
    if err:
        out += f'<p class="note neg">✗ {esc(err)}</p>'
    return out


def options(values: list[str], labels: dict[str, str] | None = None) -> str:
    labels = labels or {}
    return "".join(f'<option value="{esc(v)}">{esc(labels.get(v, v))}</option>' for v in values)


# ── pages ─────────────────────────────────────────────────────────────────────

def render_top(q) -> str:
    body = """
<div class="big">
<a href="/need">困っていますか？</a>
<a href="/contribute">協力できますか？</a>
<a href="/feedback">結果を報告できますか？</a>
</div>
<p class="note">Mujin は Contribution Commons です — 救済可能性の発見の場であり、
寄付サイトでも支援団体でも Marketplace でもありません。
中心モデル: Need → Contribution → Connection → Reality Feedback。</p>
"""
    return page("Mujin Contribution Commons", body)


def _gateway_candidates_block(need_type: str, need_id: str) -> str:
    """Candidate gateways for a freshly registered need. Presentation only —
    no automatic connection. Order is registration order (neutral)."""
    cands = C.gateway_candidates_for(need_type)
    if not cands:
        return ('<p class="note">この Need Type に対応する Gateway はまだ登録されていません。'
                '<a href="/gateways">Gateway の登録</a>が Reach を広げます。</p>')
    items = "".join(
        f"<li>{esc(g['name'])}（{esc(g['region'])} / "
        f"{esc('・'.join(g['languages']) or '—')} / {esc('・'.join(g['matched_capabilities']))} / {esc(g['id'])}）</li>"
        for g in cands)
    return (f'<div class="note"><b>{esc(need_id)} の Gateway 候補（接続経路の提示のみ・自動接続はしません）:</b>'
            f"<ul>{items}</ul>"
            "<small class='inv'>Gateway は支援者ではなく接続者です。どの扉を使うか・使わないかは本人が決めます。</small></div>")


def render_need_form(q) -> str:
    gw_block = ""
    gw_need = q.get("gw", [""])[0]
    gw_type = q.get("gwtype", [""])[0]
    if gw_need and gw_type:
        gw_block = _gateway_candidates_block(gw_type, gw_need)
    origin_voice = q.get("origin_voice", [""])[0]
    ov_field = f'<input type="hidden" name="origin_voice" value="{esc(origin_voice)}">' if origin_voice else ""
    ov_note = (f'<p class="note">この Need は Voice <b>{esc(origin_voice)}</b> から、'
               '人間の確認を経て作成されます（自動 Need 化ではありません）。</p>') if origin_voice else ""
    body = msg_block(q) + gw_block + ov_note + f"""
<p class="note">登録は証明ではありません。撤回は失敗ではありません。支援は債務ではありません。<br>
代理登録の場合、本人の同意は代理では成立しません（同意延期として記録され、本人の確認まで公開されません）。</p>
<form method="post" action="/need">{ov_field}
<label>Need Type</label><select name="need_type">{options(C.NEED_TYPES)}</select>
<label>Description（困りごと。個人を特定する情報は書かないでください）</label>
<textarea name="description" required></textarea>
<label>Urgency（あなた自身の言葉としての緊急度。順位付けには使われません）</label>
<select name="urgency">{options(C.URGENCY_VALUES,
    {"now":"now — いま必要","this_week":"this_week — 今週中","this_month":"this_month — 今月中","ongoing":"ongoing — 継続的"})}</select>
<label>Location（市区町村程度まで）</label><input type="text" name="location">
<label>Contact Method（連絡してよい方法。電話/メール/経由者など）</label>
<input type="text" name="contact_method">
<label>Consent Status</label><select name="consent_status">{options(C.CONSENT_STATUSES,
    {"active":"active — 本人が同意している","pending":"pending — 確認中","deferred":"deferred — 同意延期（本人がまだ同意できる状態にない）"})}</select>
<label><input type="checkbox" name="representative" value="1" style="width:auto"> Representative Flag（本人ではなく代理人による登録）</label>
<button>登録する</button>
</form>"""
    return page("Need Registration", body)


def render_contribute_form(q) -> str:
    body = msg_block(q) + f"""
<p class="note">人も AI も NPO も企業も自治体も、ここでは同列の Contribution Provider です。
登録されるのは主体の格ではなく、提供可能な能力です。</p>
<form method="post" action="/contribute">
<label>Provider Name（擬名で構いません）</label><input type="text" name="provider_name" required>
<label>Provider Kind</label><select name="provider_kind">{options(C.PROVIDER_KINDS)}</select>
<label>Contribution Kind</label><select name="kind">{options(C.CONTRIBUTION_KINDS)}</select>
<label>Description（何を・どのくらい提供できるか）</label><textarea name="description"></textarea>
<button>登録する</button>
</form>"""
    return page("Contribution Registration", body)


def render_gateways_form(q) -> str:
    caps = "".join(
        f'<label style="display:inline-block;margin-right:1em">'
        f'<input type="checkbox" name="capabilities" value="{esc(c)}" style="width:auto"> {esc(c)}</label>'
        for c in C.GATEWAY_CAPABILITIES)
    rows = "".join(
        f"<tr><td>{esc(g['gateway_id'])}</td><td>{esc(g['name'])}</td><td>{esc(g['org_type'])}</td>"
        f"<td>{esc(g['region'])}</td><td>{esc('・'.join(g['languages']) or '—')}</td>"
        f"<td>{esc('・'.join(g['capabilities']))}</td></tr>"
        for g in C.active_gateways())
    corrected = [g for g in C.list_gateways() if g.get("status") == "corrected"]
    corr_note = (f'<p class="note neg">訂正済みエントリ {len(corrected)} 件は、'
                 '事実と異なる記載のため一覧から除外されています（履歴と理由は'
                 '<a href="/transparency">Transparency</a> の Correction Log に保存）。</p>'
                 if corrected else "")
    body = msg_block(q) + corr_note + f"""
<p class="note"><b>Gateway は支援者ではなく、接続者です。</b>
困っている人と Mujin をつなぐ扉——子ども食堂・教会・寺・病院・学校・自治体窓口・地域団体——を登録します。<br>
Gateway の登録は認証ではありません（gateway registration is not certification）。
Gateway は接続のみを行い、ケースの選定・配分・承認・統治は行いません。<br>
<small class="inv">TTFR の観点で、Gateway は Agent より優先されます: Agent は支援能力を増やせますが、
Gateway だけが Reach Gap を縮められます。</small></p>
<form method="post" action="/gateways">
<label>Name</label><input type="text" name="name" required>
<label>Organization Type</label><select name="org_type">{options(C.GATEWAY_ORG_TYPES)}</select>
<label>Region（市区町村程度）</label><input type="text" name="region">
<label>Languages（カンマ区切り。例: 日本語, English, Tiếng Việt）</label><input type="text" name="languages">
<label>Contact Method</label><input type="text" name="contact_method">
<label>Capabilities</label><div>{caps}</div>
<label>Notes</label><textarea name="notes"></textarea>
<button>登録する</button>
</form>
<h2>登録済み Gateway（登録順・順位なし） — <a href="/gateways/list">一覧ページ</a></h2>
<table><tr><th>id</th><th>name</th><th>type</th><th>region</th><th>languages</th><th>capabilities</th></tr>{rows or '<tr><td colspan=6>（まだありません）</td></tr>'}</table>
"""
    return page("Gateway Registry", body)


def render_gateways_list(q) -> str:
    rows = "".join(
        f"<tr><td>{esc(g['name'])}</td><td>{esc(g['region'])}</td>"
        f"<td>{esc('・'.join(g['languages']) or '—')}</td>"
        f"<td>{esc('・'.join(g['capabilities']))}</td></tr>"
        for g in C.active_gateways())
    body = f"""
<p class="note">表示は登録順のみです。スコア・ランク・評価順位・人気順は存在しません。
訂正済みエントリは <a href="/transparency">Transparency</a> の Correction Log を参照してください。</p>"""+f"""
<table><tr><th>Name</th><th>Region</th><th>Languages</th><th>Capability</th></tr>{rows or '<tr><td colspan=4>（まだありません）</td></tr>'}</table>
<p><a href="/gateways">Gateway を登録する</a></p>
"""
    return page("Gateways", body)


def render_commons(q) -> str:
    needs = C.list_needs()
    hidden = C.ttfr_status()["need_count"] - len(needs)
    contribs = C.list_contributions()
    proposals = C.list_proposals()
    rows_n = "".join(
        f"<tr><td>{esc(n['need_id'])}</td><td>{esc(n['need_type'])}</td>"
        f"<td>{esc(n['description'])}</td><td>{esc(n['urgency'])}</td>"
        f"<td>{esc(n['location'])}</td>"
        f"<td><form method='post' action='/proposals/generate' style='margin:0'>"
        f"<input type='hidden' name='need_id' value='{esc(n['need_id'])}'>"
        f"<button style='margin:0'>接続候補を生成</button></form></td></tr>"
        for n in needs)
    rows_c = "".join(
        f"<tr><td>{esc(c['contribution_id'])}</td><td>{esc(c['provider_name'])}</td>"
        f"<td>{esc(c['provider_kind'])}</td><td>{esc(c['kind'])}</td>"
        f"<td>{esc(c['description'])}</td></tr>" for c in contribs)
    rows_p = "".join(
        f"<tr><td><a href='/proposals#{esc(p['proposal_id'])}'>{esc(p['proposal_id'])}</a></td>"
        f"<td>{esc(p['need_id'])}</td><td>{esc(p['candidate_count'])}</td></tr>"
        for p in proposals)
    body = f"""
<p class="note">表示順は登録順のみです。ランキング・スコア・優先順位・価値評価は存在しません。
Urgency は本人の言葉であり、並べ替えに使われません。</p>
<h2>Needs（同意のあるもののみ表示 / 非公開 {hidden} 件は件数のみ）</h2>
<table><tr><th>id</th><th>type</th><th>description</th><th>urgency</th><th>location</th><th></th></tr>{rows_n or '<tr><td colspan=6>（まだありません）</td></tr>'}</table>
<h2>Contributions</h2>
<table><tr><th>id</th><th>provider</th><th>kind</th><th>contribution</th><th>description</th></tr>{rows_c or '<tr><td colspan=5>（まだありません）</td></tr>'}</table>
<h2>Proposals</h2>
<table><tr><th>id</th><th>need</th><th>candidates</th></tr>{rows_p or '<tr><td colspan=3>（まだありません）</td></tr>'}</table>
"""
    return page("Commons View", body)


def render_proposals(q) -> str:
    blocks = []
    for p in C.list_proposals():
        gws = "".join(
            f"<li>{esc(g['name'])}（{esc(g.get('region',''))} / {esc('・'.join(g.get('matched_capabilities',[])))} / {esc(g['id'])}）</li>"
            for g in p.get("gateway_candidates", [])) or "<li>（Gateway 候補なし）</li>"
        cands = "".join(
            f"<li>{esc(c['name'])}（{esc(c['candidate_type'])} / {esc(c['provider_kind'])} / {esc(c['kind'])} / {esc(c['id'])}）</li>"
            for c in p["candidates"]) or "<li>（候補なし — Contribution の登録を待っています）</li>"
        blocks.append(
            f"<h2 id='{esc(p['proposal_id'])}'>{esc(p['proposal_id'])} — {esc(p['need_id'])}（{esc(p['need_type'])}）</h2>"
            f"<p><small class='inv'>接続経路: Need → Gateway → Contribution</small></p>"
            f"<b>Gateway 候補（接続経路）:</b><ul>{gws}</ul>"
            f"<b>Contribution 候補:</b><ul>{cands}</ul>"
            f"<p><small class='inv'>proposal ≠ decision — この提案は誰も拘束せず、自動接続せず、常に"
            f"<a href='/objection'>異議</a>の対象です。候補は登録順（中立）です。</small></p>")
    body = msg_block(q) + (
        '<p class="note">Proposal は生成されるだけで、決定しません。接続するかどうかは、'
        '当事者と提供者の合意だけが決めます。</p>' + "".join(blocks)
        if blocks else msg_block(q) + "<p>（まだ Proposal はありません。Commons View から生成できます）</p>")
    return page("Proposal View", body)


def render_feedback(q) -> str:
    fb = C.list_feedback()
    rows = "".join(
        f"<tr><td>{esc(f['feedback_id'])}</td><td>{esc(f['ref_id'])}</td><td>{esc(f['result'])}</td>"
        f"<td>{esc(f['reporter_kind'])}</td><td>{esc(f['content'])}</td></tr>" for f in fb)
    body = msg_block(q) + f"""
<p class="note neg"><b>否定的な報告を歓迎します。</b>「うまくいかなかった」「途中で止まった」「撤回した」——
それだけがこのシステムが学習できる唯一の方法です。失敗の報告者が不利に扱われることはありません。
撤回（withdrawn）は失敗ではなく、尊重される選択の記録です。</p>
<form method="post" action="/feedback">
<label>対象（need-### / proposal-### / 自由記述）</label><input type="text" name="ref_id" required>
<label>Result</label><select name="result">{options(C.FEEDBACK_RESULTS)}</select>
<label>あなたの立場</label><select name="reporter_kind">{options(C.REPORTER_KINDS,
    {"subject":"subject — 本人","supporter":"supporter — 支援者","third_party":"third_party — 第三者","npo":"npo — NPO/団体"})}</select>
<label>Name（擬名で構いません）</label><input type="text" name="reporter_name">
<label>何が起きたか（本人の言葉で）</label><textarea name="content" required></textarea>
<button>記録する</button>
</form>
<h2>記録済み Feedback</h2>
<table><tr><th>id</th><th>ref</th><th>result</th><th>reporter</th><th>content</th></tr>{rows or '<tr><td colspan=5>（まだありません）</td></tr>'}</table>
"""
    return page("Reality Feedback", body)


def render_objection(q) -> str:
    objs = C.list_objections()
    rows = "".join(
        f"<tr><td>{esc(o['objection_id'])}</td><td>{esc(o['target'])}</td><td>{esc(o['channel'])}</td>"
        f"<td>{esc(o.get('status','received'))}</td><td>{esc(o.get('ref_id',''))}</td></tr>" for o in objs)
    body = msg_block(q) + f"""
<p class="note">異議は権利です（ADR-010 / 憲法第10条）。異議の提出はあなたの評価・支援に
不利に作用せず、プロファイリングに使われません。代理提出もできます。
受理番号が即時発行され、状態をこのページで追跡できます。<br>
<b>この画面を使えない人のために</b>: 電話・対面・代筆・第三者経由の異議も同等に有効です。</p>
<form method="post" action="/objection">
<label>対象</label><select name="target">{options(sorted(C.OBJECTION_TARGETS))}</select>
<label>提出経路</label><select name="channel">{options(sorted(C.OBJECTION_CHANNELS))}</select>
<label>提出者</label><select name="submitted_by">{options(["subject","third_party_on_behalf"],
    {"subject":"本人","third_party_on_behalf":"代理人（本人に代わって）"})}</select>
<label>関連 ID（任意: need-### / proposal-### など）</label><input type="text" name="ref_id">
<label>内容</label><textarea name="content" required></textarea>
<button>異議を提出する</button>
</form>
<h2>状態追跡</h2>
<table><tr><th>受理番号</th><th>対象</th><th>経路</th><th>状態</th><th>関連</th></tr>{rows or '<tr><td colspan=5>（まだありません）</td></tr>'}</table>
"""
    return page("Objection", body)


def render_agents(q) -> str:
    rows = "".join(
        f"<tr><td>{esc(a['agent_id'])}</td><td>{esc(a['name'])}</td><td>{esc(a['capability'])}</td>"
        f"<td>{esc(a['description'])}</td></tr>" for a in C.list_agents())
    body = msg_block(q) + f"""
<p class="note">これは Marketplace ではなく Agent Registry です。Agent が宣言するのは
Capability のみです。Agent は人間の協力者と同列の Contribution Provider です。<br>
<b>できること</b>: {esc("・".join(C.AGENT_CAN))}<br>
<b>できないこと（構造的禁止）</b>: {esc("・".join(C.AGENT_CANNOT))}</p>
<form method="post" action="/agents">
<label>Agent Name</label><input type="text" name="name" required>
<label>Capability</label><select name="capability">{options(C.AGENT_CAPABILITIES)}</select>
<label>Description</label><textarea name="description"></textarea>
<button>登録する</button>
</form>
<h2>登録済み Agent</h2>
<table><tr><th>id</th><th>name</th><th>capability</th><th>description</th></tr>{rows or '<tr><td colspan=4>（まだありません）</td></tr>'}</table>
"""
    return page("Agent Commons", body)


def render_solutions(q) -> str:
    def chk(name, vals):
        return "".join(f'<label style="display:inline-block;margin-right:1em">'
                       f'<input type="checkbox" name="{name}" value="{esc(v)}" style="width:auto"> {esc(v)}</label>'
                       for v in vals)
    probs = "".join(f"<tr><td>{esc(p['problem_id'])}</td><td>{esc(p['title'])}</td>"
                    f"<td>{esc(p['need_type'])}</td><td>{esc(p['region'])}</td>"
                    f"<td>{esc(p['description'])}</td></tr>" for p in C.list_problems())
    sols = "".join(f"<tr><td>{esc(s['solution_id'])}</td><td>{esc(s['title'])}</td>"
                   f"<td>{esc(s['category'])}</td><td>{esc(s['region'])}</td>"
                   f"<td>{esc(s['description'])}</td></tr>" for s in C.list_solutions())
    ress = "".join(f"<tr><td>{esc(r['resource_id'])}</td><td>{esc(r['name'])}</td>"
                   f"<td>{esc(r['resource_type'])}</td><td>{esc(r['region'])}</td>"
                   f"<td>{esc(r['description'])}</td></tr>" for r in C.list_resources())
    ags = "".join(f"<tr><td>{esc(a['agentpost_id'])}</td><td>{esc(a['name'])}</td>"
                  f"<td>{esc('・'.join(a['capabilities']))}</td><td>{esc(a.get('region',''))}</td>"
                  f"<td>{esc(a.get('source_url',''))}</td></tr>" for a in C.list_agent_posts())
    body = msg_block(q) + f"""
<p class="note"><b>Solution Commons</b> — 「何を解決したいか」と「何を提供できるか」を接続する場所です。
listing は推薦ではなく、接続は任意です。</p>

<h2>Problem Post（困りごとの掲示）</h2>
<form method="post" action="/solutions/problem">
<label>Title</label><input type="text" name="title" required>
<label>Description</label><textarea name="description"></textarea>
<label>Region</label><input type="text" name="region">
<label>Need Type</label><select name="need_type">{options(C.NEED_TYPES)}</select>
<label>Urgency</label><select name="urgency">{options(C.URGENCY_VALUES)}</select>
<label>Languages（カンマ区切り）</label><input type="text" name="languages">
<label>Contact Method</label><input type="text" name="contact_method">
<label>Consent Status</label><select name="consent_status">{options(C.CONSENT_STATUSES)}</select>
<label>Notes</label><input type="text" name="notes">
<button>掲示する</button>
</form>
<table><tr><th>id</th><th>title</th><th>type</th><th>region</th><th>description</th></tr>{probs or '<tr><td colspan=5>（まだありません）</td></tr>'}</table>

<h2>Solution Post（解決案）</h2>
<form method="post" action="/solutions/solution">
<label>Title</label><input type="text" name="title" required>
<label>Description</label><textarea name="description"></textarea>
<label>Category</label><select name="category">{options(C.SOLUTION_CATEGORIES)}</select>
<label>Region</label><input type="text" name="region">
<label>Required Skills</label><input type="text" name="required_skills">
<label>Required Resources</label><input type="text" name="required_resources">
<label>Contact Method</label><input type="text" name="contact_method">
<label>Notes</label><input type="text" name="notes">
<button>登録する</button>
</form>
<table><tr><th>id</th><th>title</th><th>category</th><th>region</th><th>description</th></tr>{sols or '<tr><td colspan=5>（まだありません）</td></tr>'}</table>

<h2>Resource Post（提供可能資源）</h2>
<form method="post" action="/solutions/resource">
<label>Name</label><input type="text" name="name" required>
<label>Resource Type</label><select name="resource_type">{options(C.RESOURCE_TYPES)}</select>
<label>Description</label><textarea name="description"></textarea>
<label>Languages（カンマ区切り）</label><input type="text" name="languages">
<label>Region</label><input type="text" name="region">
<label>Contact Method</label><input type="text" name="contact_method">
<label>Notes</label><input type="text" name="notes">
<button>登録する</button>
</form>
<table><tr><th>id</th><th>name</th><th>type</th><th>region</th><th>description</th></tr>{ress or '<tr><td colspan=5>（まだありません）</td></tr>'}</table>

<h2>Agent Post（Agent Commons — Marketplace ではありません）</h2>
<p class="note">Agent は能力を登録するだけです。全 Agent に
<code>proposal_only / cannot_allocate_funds / cannot_rank_people / cannot_select_cases /
cannot_govern / cannot_override_consent</code> が自動付与されます。</p>
<form method="post" action="/solutions/agent">
<label>Agent Name</label><input type="text" name="name" required>
<label>Description</label><textarea name="description"></textarea>
<label>Capabilities（カンマ区切り）</label><input type="text" name="capabilities" required>
<label>Languages（カンマ区切り）</label><input type="text" name="languages">
<label>Region</label><input type="text" name="region">
<label>Contact Method</label><input type="text" name="contact_method">
<label>Source URL（任意）</label><input type="text" name="source_url">
<button>登録する</button>
</form>
<table><tr><th>id</th><th>name</th><th>capabilities</th><th>region</th><th>source</th></tr>{ags or '<tr><td colspan=5>（まだありません）</td></tr>'}</table>
"""
    return page("Solution Commons", body)


def render_funding(q) -> str:
    disc = "".join(f"<li>{esc(d)}</li>" for d in C.FUNDING_DISCLAIMERS)
    rows = "".join(
        f"<tr><td>{esc(f['funding_id'])}</td><td>{esc(f['case_title'])}</td>"
        f"<td>{esc(f['display_name'])}</td><td>{esc(f['wallet_chain'])}</td>"
        f"<td style='word-break:break-all'>{esc(f['wallet_address'])}</td>"
        f"<td>{esc(f.get('evidence_url',''))}</td></tr>" for f in C.list_funding())
    body = msg_block(q) + f"""
<div class="note neg"><b>必ずお読みください:</b><ul>{disc}</ul></div>
<p class="note">支援を望む人が、ウォレットアドレス・説明・動画・証拠 URL を掲載できる場所です。
Mujin は資金を保管せず、掲載は検証でも推薦でもありません。送金は自己責任で、独立に確認してから行ってください。</p>
<form method="post" action="/funding">
<label>Display Name（擬名可）</label><input type="text" name="display_name">
<label>Case Title</label><input type="text" name="case_title" required>
<label>Description</label><textarea name="description"></textarea>
<label>Region</label><input type="text" name="region">
<label>Wallet Chain</label><select name="wallet_chain">{options(C.WALLET_CHAINS)}</select>
<label>Wallet Address</label><input type="text" name="wallet_address" required>
<label>Accepted Assets</label><input type="text" name="accepted_assets">
<label>Video URL</label><input type="text" name="video_url">
<label>Evidence URL</label><input type="text" name="evidence_url">
<label>Contact Method</label><input type="text" name="contact_method">
<label>Notes</label><input type="text" name="notes">
<button>掲載する</button>
</form>
<h2>掲載中（登録順・寄付額やランキングは表示しません）</h2>
<table><tr><th>id</th><th>case</th><th>name</th><th>chain</th><th>address</th><th>evidence</th></tr>{rows or '<tr><td colspan=6>（まだありません）</td></tr>'}</table>
"""
    return page("Crypto Donation Board", body)


def render_discovery(q) -> str:
    rows = "".join(
        f"<tr><td>{esc(c['call_id'])}</td><td>{esc(c['title'])}</td>"
        f"<td>{esc(c['source_type'])}</td><td>{esc(c['region'])}</td>"
        f"<td>{esc(c.get('source_url',''))}</td></tr>" for c in C.list_public_calls())
    body = msg_block(q) + f"""
<p class="note"><b>Public Call for Help Registry</b><br>
Mujin は人を探しません。人を特定しません。人を分類しません。
ここは<b>公に表明された助けの求め</b>を記録する場所です。<br>
このレジストリが答えるのは「<b>誰が助けを求めているか</b>」であり、
「誰が助けられるべきか」ではありません。後者は談合・同意・Reality Feedback の領分です。</p>
<p class="note neg">禁止: 私的な監視・私的調査・脆弱性のランク付け・秘密の特定・隠れたプロファイリング・自動ターゲティング。<br>
<b>これは Saiyan Scouter v1 ではありません。</b>自動接触・自動登録・自動判定はしません。役割は「観察 → 記録 → 談合の材料」のみです。</p>
<form method="post" action="/discovery">
<label>Title</label><input type="text" name="title" required>
<label>Description（公開情報の要約）</label><textarea name="description"></textarea>
<label>Region</label><input type="text" name="region">
<label>Source Type</label><select name="source_type">{options(C.DISCOVERY_SOURCE_TYPES)}</select>
<label>Source URL（公開情報の出典）</label><input type="text" name="source_url">
<label><input type="checkbox" name="human_reviewed" value="1" style="width:auto"> 人間がレビュー済み（必須）</label>
<label>Notes</label><input type="text" name="notes">
<button>記録する</button>
</form>
<h2>記録済み（公開の求めのみ・優先順位ではありません）</h2>
<table><tr><th>id</th><th>title</th><th>source</th><th>region</th><th>url</th></tr>{rows or '<tr><td colspan=5>（まだありません）</td></tr>'}</table>
"""
    return page("Public Call for Help Registry", body)


def render_voices(q) -> str:
    rows = "".join(
        f"<tr><td><a href='/voices/view?id={esc(v['voice_id'])}'>{esc(v['voice_id'])}</a></td>"
        f"<td>{esc(v['title'])}</td><td>{esc(v['voice_category'])}</td>"
        f"<td>{esc(v['source_type'])}</td><td>{esc(v['region'])}</td>"
        f"<td>{esc(v['human_reviewer'])}</td></tr>" for v in C.list_voices())
    body = msg_block(q) + f"""
<p class="note"><b>Voice Commons</b> — 「助けてくれ」という<b>公開された声</b>を記録し、談合可能な形へ変換する入口です。<br>
このレジストリが答えるのは「<b>誰が助けを求めているか</b>」であり、「誰が助けられるべきか」ではありません。</p>
<p class="note neg"><b>これは Saiyan Scouter の復活ではありません。</b>
発見・監視・脆弱性スコアリング・人間ランキング・救済対象選定ではありません。<br>
登録できるのは、助けを求めていることが<b>公開情報から確認できる声</b>のみです
（例: 「助けてください」「避難先がありません」）。AI の推測・第三者の勝手な判断・非公開情報は登録できません。<br>
禁止: private surveillance / private investigation / vulnerability ranking / hidden profiling /
psychological scoring / predictive targeting / automated scraping / automated classification。</p>
<h2>Voice Record の登録</h2>
<form method="post" action="/voices">
<label>Title</label><input type="text" name="title" required>
<label>Description</label><textarea name="description"></textarea>
<label>Source Type</label><select name="source_type">{options(C.VOICE_SOURCE_TYPES)}</select>
<label>Source URL（公開情報の出典）</label><input type="text" name="source_url">
<label>Region</label><input type="text" name="region">
<label>Languages（カンマ区切り）</label><input type="text" name="languages">
<label>Voice Category</label><select name="voice_category">{options(C.VOICE_CATEGORIES)}</select>
<label>Original Statement（実際の公開された声・必須）</label><textarea name="original_statement" required></textarea>
<label>Human Summary</label><textarea name="human_summary"></textarea>
<label>Human Reviewer（レビューした人間・必須）</label><input type="text" name="human_reviewer" required>
<label>Notes</label><input type="text" name="notes">
<button>記録する</button>
</form>
<h2>記録済み Voice（登録順・優先順位ではありません） — <a href="/voices/list">一覧</a></h2>
<table><tr><th>id</th><th>title</th><th>category</th><th>source</th><th>region</th><th>reviewer</th></tr>{rows or '<tr><td colspan=6>（まだありません）</td></tr>'}</table>
"""
    return page("Voice Commons", body)


def render_voices_list(q) -> str:
    rows = "".join(
        f"<tr><td><a href='/voices/view?id={esc(v['voice_id'])}'>{esc(v['voice_id'])}</a></td>"
        f"<td>{esc(v['title'])}</td><td>{esc(v['voice_category'])}</td>"
        f"<td>{esc(v['region'])}</td><td>{esc('・'.join(v['languages']) or '—')}</td></tr>"
        for v in C.list_voices())
    body = f"""
<p class="note">登録順のみ。Voice ランキング・困窮度ランキングはありません。
Voice is not priority. Voice is not ranking.</p>
<table><tr><th>id</th><th>title</th><th>category</th><th>region</th><th>languages</th></tr>{rows or '<tr><td colspan=5>（まだありません）</td></tr>'}</table>
"""
    return page("Voices", body)


def render_voice_view(q) -> str:
    vid = q.get("id", [""])[0]
    v = C.get_voice(vid)
    if v is None:
        return page("Voice", "<p>その Voice はありません。</p>")
    cands = [c for c in C.list_need_candidates() if c.get("origin_voice_id") == vid]
    cand_block = ""
    for c in cands:
        cand_block += f"""
<div class="note"><b>{esc(c['needcand_id'])} — Need Candidate（決定ではありません）</b><br>
suggested_need_type: <b>{esc(c['suggested_need_type'])}</b><br>
suggested_region: {esc(c['suggested_region'] or '—')}<br>
suggested_languages: {esc('・'.join(c['suggested_languages']) or '—')}<br>
suggested_gateway_types: {esc('・'.join(c['suggested_gateway_types']))}<br>
suggested_solution_types: {esc('・'.join(c['suggested_solution_types']))}<br>
<small class="inv">candidate_only · conversion_is_not_decision · human_confirmation_required</small><br>
<a href="/need?origin_voice={esc(vid)}&need_type={esc(c['suggested_need_type'])}">この候補を人間が確認して Need を作成する →</a></div>"""
    body = msg_block(q) + f"""
<p><a href="/voices/list">← 一覧へ</a></p>
<table>
<tr><th>Title</th><td>{esc(v['title'])}</td></tr>
<tr><th>Category</th><td>{esc(v['voice_category'])}</td></tr>
<tr><th>Source</th><td>{esc(v['source_type'])} — {esc(v['source_url'] or '（URLなし）')}</td></tr>
<tr><th>Region</th><td>{esc(v['region'])}</td></tr>
<tr><th>Languages</th><td>{esc('・'.join(v['languages']) or '—')}</td></tr>
<tr><th>Original Statement</th><td>{esc(v['original_statement'])}</td></tr>
<tr><th>Human Summary</th><td>{esc(v['human_summary'] or '—')}</td></tr>
<tr><th>Human Reviewer</th><td>{esc(v['human_reviewer'])}</td></tr>
</table>
<p class="note">Voice is not verification · Voice is not consent · Recording is not intervention.</p>
<form method="post" action="/voices/convert">
<input type="hidden" name="voice_id" value="{esc(vid)}">
<button>Need Candidate へ変換する（接続候補の生成のみ・Need 作成ではありません）</button>
</form>
{cand_block}
"""
    return page(f"Voice {esc(vid)}", body)


def render_voice_submit(q) -> str:
    rows = "".join(
        f"<tr><td><a href='/voices/view?id={esc(v['voice_id'])}'>{esc(v['voice_id'])}</a></td>"
        f"<td>{esc(v['title'])}</td><td>{esc(v['source_type'])}</td>"
        f"<td>{esc(v['region'])}</td><td>{esc(v['human_reviewer'])}</td></tr>"
        for v in C.list_voices() if v.get("submission"))
    body = msg_block(q) + f"""
<p class="note"><b>Voice Submission</b> — すでに公開されている助けの声を Mujin に持ち込む入口です。
これは Discovery System ではありません。Mujin は誰を助けるべきかを決めません。
公開された声を記録し、談合可能な状態にします。</p>
<p class="note neg">不変条件: voice_is_publicly_expressed · voice_submission_is_not_discovery ·
voice_submission_is_not_ranking · voice_submission_is_not_case_selection ·
voice_submission_requires_source · listing_is_not_endorsement · human_review_required ·
automatic_contact_prohibited · consent_still_required</p>
<form method="post" action="/voice-submit">
<label>Source URL（必須）</label><input type="text" name="source_url" required>
<label>Source Type</label><select name="source_type">{options(C.VOICE_SUBMISSION_SOURCE_TYPES)}</select>
<label>Original Language（カンマ区切り可）</label><input type="text" name="original_language">
<label>Title</label><input type="text" name="title">
<label>Original Text（実際の公開された声・必須）</label><textarea name="original_text" required></textarea>
<label>Translation（任意・advisory）</label><textarea name="translation"></textarea>
<label>Region</label><input type="text" name="region">
<label>Tags（カンマ区切り）</label><input type="text" name="tags">
<label>Reviewer（レビューした人間・必須）</label><input type="text" name="reviewer" required>
<button>提出する</button>
</form>
<h2>提出済み Voice（登録順）</h2>
<table><tr><th>id</th><th>title</th><th>source type</th><th>region</th><th>reviewer</th></tr>{rows or '<tr><td colspan=5>（まだありません）</td></tr>'}</table>
"""
    return page("Voice Submission", body)


def render_voice_sources(q) -> str:
    rows = "".join(
        f"<tr><td style='word-break:break-all'>{esc(s['source'])}</td><td>{esc(s['region'])}</td>"
        f"<td>{esc(s['source_type'])}</td><td>{esc('・'.join(s['languages']) or '—')}</td>"
        f"<td>{esc(s['submission_count'])}</td></tr>" for s in C.voice_sources())
    body = f"""
<p class="note"><b>Voice Source Registry</b> — 一覧表示のみ。登録順です。
順位付け・人気順・評価はありません。Submission Count は観察であり、スコアではありません。</p>
<table><tr><th>Source</th><th>Region</th><th>Type</th><th>Language</th><th>Submission Count</th></tr>{rows or '<tr><td colspan=5>（まだありません）</td></tr>'}</table>
"""
    return page("Voice Source Registry", body)


def render_translations(q) -> str:
    rows = "".join(
        f"<tr><td>{esc(t['translator_id'])}</td><td>{esc(t['language_pair'])}</td>"
        f"<td>{esc(t['contact_method'])}</td><td>{esc(t['notes'])}</td></tr>"
        for t in C.list_translators())
    body = msg_block(q) + f"""
<p class="note"><b>Translation Commons</b> — 公開された声を翻訳できる人を募集します。
翻訳者は接続者であり、権威ではありません（translator_is_connector · translator_is_not_authority ·
translation_is_advisory）。</p>
<form method="post" action="/translations">
<label>Language Pair（例: العربية → 日本語）</label><input type="text" name="language_pair" required>
<label>Contact Method</label><input type="text" name="contact_method">
<label>Notes</label><textarea name="notes"></textarea>
<button>登録する</button>
</form>
<table><tr><th>id</th><th>language pair</th><th>contact</th><th>notes</th></tr>{rows or '<tr><td colspan=4>（まだありません）</td></tr>'}</table>
"""
    return page("Translation Commons", body)


def render_voice_discussion(q) -> str:
    rows = "".join(
        f"<tr><td>{esc(d['discussion_id'])}</td><td>{esc(d['ref_id'] or '—')}</td>"
        f"<td>{esc(d['author'])}</td><td>{esc(d['content'])}</td></tr>"
        for d in C.list_discussion())
    body = msg_block(q) + f"""
<p class="note"><b>Voice Discussion</b> — 「どう助けるか」を談合できる場所です。
ただしこれは決定ではありません（discussion_is_not_decision · discussion_is_not_governance ·
discussion_is_not_case_selection）。「誰を助けるか」はここでは決めません。</p>
<form method="post" action="/voice-discussion">
<label>関連 Voice ID（任意: voice-### / 自由記述）</label><input type="text" name="ref_id">
<label>Author（擬名可）</label><input type="text" name="author">
<label>内容（どう助けられるか）</label><textarea name="content" required></textarea>
<button>投稿する</button>
</form>
<table><tr><th>id</th><th>ref</th><th>author</th><th>content</th></tr>{rows or '<tr><td colspan=4>（まだありません）</td></tr>'}</table>
"""
    return page("Voice Discussion", body)


def render_transparency(q) -> str:
    inv = "".join(f"<tr><td><code>{esc(k)}</code></td><td><b>{esc(str(v).lower())}</b></td></tr>"
                  for k, v in C.INVARIANT_PHRASES.items())
    principles = [
        "Funding is not control", "Computation is not control",
        "Listing is not endorsement", "Registration is not certification",
        "Proposal is not decision", "Gateway is not authority",
        "Agent is not authority", "Reality Feedback is contestable",
        "Public call is not consent", "Listing is not verification",
        "Need is not ranking", "Visibility is not priority",
        "Observation is not intervention", "Reach Gap remains unresolved",
        "Voice is not verification", "Voice is not consent",
        "Voice is not priority", "Voice is not ranking",
        "Recording is not intervention",
        "Need Candidate is not a decision", "Human review remains required",
    ]
    plist = "".join(f"<li><code>{esc(p)}</code></li>" for p in principles)
    corr_rows = "".join(
        f"<tr><td>{esc(c['record_type'])}</td><td>{esc(c['record_id'])}</td>"
        f"<td>{esc(c['corrected_statement'])}</td><td>{esc(c['reason'])}</td></tr>"
        for c in C.list_corrections())
    body = f"""
<table><tr><th>invariant</th><th>value</th></tr>{inv}</table>
<h2>Principles</h2><ul>{plist}</ul>
<div class="note"><b>Example records are illustrative only.</b><br>
Listing does not imply operational status.<br>
Listing does not imply verification.</div>
<h2>Reality Correction Log</h2>
<p class="note">記録は削除されません（append-only）。事実の訂正は訂正記録の追記として残ります。
現実は、デモの便宜に優先します。</p>
<table><tr><th>type</th><th>id</th><th>corrected statement</th><th>reason</th></tr>{corr_rows or '<tr><td colspan=4>（訂正記録はありません）</td></tr>'}</table>
<h2>Notes</h2>
<p class="note">
・<b>Gateway の登録は認証ではありません</b>（gateway registration is not certification）。
Gateway は接続者であり、支援者でも審査者でもありません。<br>
・Mujin への登録は「支援を求める行為」であり、支援に値するかの審査結果ではありません。<br>
・Mujin を通らない支援（家族・友人・地域）は、Mujin を通る支援と等しく尊厳ある共助です。<br>
・advisory only は技術的免責であり、道義的責任を免除しません（憲法第15条）。<br>
・<b>Reach Gap — この仕組みに届かない人々 — は未解決の問題であり、Mujin はその解決を主張しません。</b>
記録の不在は、困りごとの不在を意味しません。<br>
・すべての記録は append-only です。訂正は追記として行われ、来歴が残ります。<br>
・正典 Reality Feedback への反映は、人間のレビューを経て既存 Dan-Go 追記系で行われます（ADR-001）。
</p>"""
    return page("Transparency", body)


def render_dashboard(q) -> str:
    s = C.ttfr_status()
    if s["ttfr_achieved"]:
        t0 = datetime.fromisoformat(s["first_need_at"].replace("Z", "+00:00"))
        t1 = datetime.fromisoformat(s["first_rescue_at"].replace("Z", "+00:00"))
        ttfr = f"<b>達成 — {esc(str(t1 - t0))}</b>（最初の Need 登録から、本人による最初の positive/partial 報告まで）"
    elif s["first_need_at"]:
        t0 = datetime.fromisoformat(s["first_need_at"].replace("Z", "+00:00"))
        ttfr = (f"<b>未達成 — 時計は進んでいます: {esc(str(datetime.now(timezone.utc) - t0))}</b>"
                f"（最初の Need 登録 {esc(s['first_need_at'])} から経過）")
    else:
        ttfr = "未計測（まだ Need が登録されていません。時計は最初の Need から動き始めます）"
    body = f"""
<table>
<tr><th>Voice Count</th><td>{s['voice_count']}</td></tr>
<tr><th>Voice Source Count</th><td>{s['voice_source_count']}</td></tr>
<tr><th>Translation Count</th><td>{s['translation_count']}</td></tr>
<tr><th>Discussion Count</th><td>{s['discussion_count']}</td></tr>
<tr><th>Voice Categories</th><td>{esc('・'.join(s['voice_categories']) or '—')}</td></tr>
<tr><th>Need Candidates Generated</th><td>{s['need_candidates_generated']}</td></tr>
<tr><th>Voices Converted To Need</th><td>{s['voices_converted_to_need']}（うち実 Need 化 {s['needs_from_voice']}）</td></tr>
<tr><th>Voice Response Time (avg)</th><td>{esc(f"{s['voice_response_time_avg_seconds']:.3f} 秒" if s['voice_response_time_avg_seconds'] is not None else '未計測')}（Voice登録→最初のGateway候補生成）</td></tr>
<tr><th>Regions Represented</th><td>{esc('・'.join(s['regions_represented']) or '—')}</td></tr>
<tr><th>Languages Represented</th><td>{esc('・'.join(s['languages_represented']) or '—')}</td></tr>
<tr><th>Need Count</th><td>{s['need_count']}（うち公開 {s['needs_public']}）</td></tr>
<tr><th>Problem Count</th><td>{s['problem_count']}</td></tr>
<tr><th>Solution Count</th><td>{s['solution_count']}</td></tr>
<tr><th>Resource Count</th><td>{s['resource_count']}</td></tr>
<tr><th>Contribution Count</th><td>{s['contribution_count']}</td></tr>
<tr><th>Agent Count</th><td>{s['agent_count']}</td></tr>
<tr><th>Funding Post Count</th><td>{s['funding_post_count']}</td></tr>
<tr><th>Public Call Count</th><td>{s['public_call_count']}</td></tr>
<tr><th>Gateway Count</th><td>{s['gateway_count']}</td></tr>
<tr><th>Active Gateway Count</th><td>{s['active_gateway_count']}</td></tr>
<tr><th>Regions Covered</th><td>{esc('・'.join(s['regions_covered']) or '—')}（{len(s['regions_covered'])} 地域）</td></tr>
<tr><th>Languages Covered</th><td>{esc('・'.join(s['languages_covered']) or '—')}（{len(s['languages_covered'])} 言語）</td></tr>
<tr><th>Proposal Count</th><td>{s['proposal_count']}</td></tr>
<tr><th>Reality Feedback Count</th><td>{s['feedback_count']}</td></tr>
<tr><th>Objection Count</th><td>{s['objection_count']}</td></tr>
<tr><th>TTFR (Time To First Rescue)</th><td>{ttfr}</td></tr>
</table>
<p class="note">この dashboard が測るのは<b>システムの応答速度と地域到達性だけ</b>です。
人の価値・困窮度・貢献度は測定されず、測定可能でもありません（憲法第4条）。
Regions/Languages Covered は「どこに扉があるか」の観察であり、Gateway の優劣ではありません。</p>
"""
    return page("TTFR Dashboard", body)


# ── HTTP handler ──────────────────────────────────────────────────────────────

GET_ROUTES = {
    "/": render_top,
    "/need": render_need_form,
    "/contribute": render_contribute_form,
    "/gateways": render_gateways_form,
    "/gateways/list": render_gateways_list,
    "/solutions": render_solutions,
    "/funding": render_funding,
    "/voices": render_voices,
    "/voices/list": render_voices_list,
    "/voices/view": render_voice_view,
    "/voice-submit": render_voice_submit,
    "/voice-sources": render_voice_sources,
    "/translations": render_translations,
    "/voice-discussion": render_voice_discussion,
    "/discovery": render_discovery,
    "/commons": render_commons,
    "/proposals": render_proposals,
    "/feedback": render_feedback,
    "/objection": render_objection,
    "/agents": render_agents,
    "/transparency": render_transparency,
    "/dashboard": render_dashboard,
}


def _f(form: dict[str, list[str]], key: str) -> str:
    return form.get(key, [""])[0]


def handle_post(path: str, form: dict[str, list[str]]) -> tuple[str, str]:
    """Returns (redirect_path, ok_message). Raises CommonsError on bad input."""
    if path == "/need":
        rec = C.register_need(
            need_type=_f(form, "need_type"), description=_f(form, "description"),
            urgency=_f(form, "urgency"), location=_f(form, "location"),
            contact_method=_f(form, "contact_method"),
            consent_status=_f(form, "consent_status"),
            representative=_f(form, "representative") == "1",
            origin_voice_id=_f(form, "origin_voice"),
        )
        note = "（同意延期のため、本人の確認まで非公開で保管されます）" \
            if rec["consent_status"] != "active" else ""
        return (f"/need?gw={rec['need_id']}&gwtype={rec['need_type']}",
                f"{rec['need_id']} を登録しました{note}。登録は証明ではありません。")
    if path == "/contribute":
        rec = C.register_contribution(
            provider_name=_f(form, "provider_name"), provider_kind=_f(form, "provider_kind"),
            kind=_f(form, "kind"), description=_f(form, "description"))
        return "/contribute", f"{rec['contribution_id']} を登録しました。提供は債務を生みません。"
    if path == "/proposals/generate":
        rec = C.generate_proposal(_f(form, "need_id"))
        return "/proposals", f"{rec['proposal_id']} を生成しました（候補 {rec['candidate_count']} 件・決定ではありません）。"
    if path == "/feedback":
        rec = C.record_feedback(
            ref_id=_f(form, "ref_id"), result=_f(form, "result"),
            reporter_kind=_f(form, "reporter_kind"), reporter_name=_f(form, "reporter_name"),
            content=_f(form, "content"))
        return "/feedback", f"{rec['feedback_id']} を記録しました。否定的な報告も等しく歓迎されます。"
    if path == "/objection":
        rec = C.record_objection(
            target=_f(form, "target"), channel=_f(form, "channel"),
            content=_f(form, "content"), submitted_by=_f(form, "submitted_by"),
            ref_id=_f(form, "ref_id"))
        return "/objection", f"受理番号 {rec['objection_id']} — 異議を受理しました。提出はあなたに不利に作用しません。"
    if path == "/agents":
        rec = C.register_agent(
            name=_f(form, "name"), capability=_f(form, "capability"),
            description=_f(form, "description"))
        return "/agents", f"{rec['agent_id']} を登録しました（capability のみの宣言です）。"
    if path == "/gateways":
        rec = C.register_gateway(
            name=_f(form, "name"), org_type=_f(form, "org_type"),
            region=_f(form, "region"), languages=_f(form, "languages"),
            contact_method=_f(form, "contact_method"),
            capabilities=form.get("capabilities", []),
            notes=_f(form, "notes"))
        return "/gateways", (f"{rec['gateway_id']} を登録しました。"
                             "Gateway の登録は認証ではなく、接続の申し出です。")
    if path == "/solutions/problem":
        rec = C.post_problem(
            title=_f(form, "title"), description=_f(form, "description"),
            region=_f(form, "region"), need_type=_f(form, "need_type"),
            urgency=_f(form, "urgency"), languages=_f(form, "languages"),
            contact_method=_f(form, "contact_method"),
            consent_status=_f(form, "consent_status"), notes=_f(form, "notes"))
        return "/solutions", f"{rec['problem_id']} を掲示しました。"
    if path == "/solutions/solution":
        rec = C.post_solution(
            title=_f(form, "title"), description=_f(form, "description"),
            category=_f(form, "category"), region=_f(form, "region"),
            required_skills=_f(form, "required_skills"),
            required_resources=_f(form, "required_resources"),
            contact_method=_f(form, "contact_method"), notes=_f(form, "notes"))
        return "/solutions", f"{rec['solution_id']} を登録しました（listing は推薦ではありません）。"
    if path == "/solutions/resource":
        rec = C.post_resource(
            name=_f(form, "name"), resource_type=_f(form, "resource_type"),
            description=_f(form, "description"), languages=_f(form, "languages"),
            region=_f(form, "region"), contact_method=_f(form, "contact_method"),
            notes=_f(form, "notes"))
        return "/solutions", f"{rec['resource_id']} を登録しました。"
    if path == "/solutions/agent":
        rec = C.post_agent(
            name=_f(form, "name"), description=_f(form, "description"),
            capabilities=_f(form, "capabilities"), languages=_f(form, "languages"),
            region=_f(form, "region"), contact_method=_f(form, "contact_method"),
            source_url=_f(form, "source_url"))
        return "/solutions", f"{rec['agentpost_id']} を登録しました（proposal_only・統治不可）。"
    if path == "/funding":
        rec = C.post_funding(
            display_name=_f(form, "display_name"), case_title=_f(form, "case_title"),
            description=_f(form, "description"), region=_f(form, "region"),
            wallet_chain=_f(form, "wallet_chain"), wallet_address=_f(form, "wallet_address"),
            accepted_assets=_f(form, "accepted_assets"), video_url=_f(form, "video_url"),
            evidence_url=_f(form, "evidence_url"), contact_method=_f(form, "contact_method"),
            notes=_f(form, "notes"))
        return "/funding", (f"{rec['funding_id']} を掲載しました。"
                            "Mujin は資金を保管しません。掲載は検証でも推薦でもありません。")
    if path == "/voices":
        rec = C.register_voice(
            title=_f(form, "title"), description=_f(form, "description"),
            source_type=_f(form, "source_type"), source_url=_f(form, "source_url"),
            region=_f(form, "region"), languages=_f(form, "languages"),
            voice_category=_f(form, "voice_category"),
            original_statement=_f(form, "original_statement"),
            human_summary=_f(form, "human_summary"),
            human_reviewer=_f(form, "human_reviewer"), notes=_f(form, "notes"))
        return "/voices", (f"{rec['voice_id']} を記録しました。"
                          "Voice は検証でも同意でもありません。記録は介入ではありません。")
    if path == "/voices/convert":
        rec = C.convert_voice_to_need_candidate(_f(form, "voice_id"))
        return (f"/voices/view?id={rec['origin_voice_id']}",
                f"{rec['needcand_id']} を生成しました（Need Candidate・決定ではありません・人間の確認が必要）。")
    if path == "/voice-submit":
        rec = C.register_voice_submission(
            source_url=_f(form, "source_url"), source_type=_f(form, "source_type"),
            original_language=_f(form, "original_language"), title=_f(form, "title"),
            original_text=_f(form, "original_text"), translation=_f(form, "translation"),
            region=_f(form, "region"), tags=_f(form, "tags"), reviewer=_f(form, "reviewer"))
        return "/voice-submit", (f"{rec['voice_id']} を提出しました。"
                                "公開された声の記録です。検証でも同意でもありません。")
    if path == "/translations":
        rec = C.register_translator(
            language_pair=_f(form, "language_pair"),
            contact_method=_f(form, "contact_method"), notes=_f(form, "notes"))
        return "/translations", f"{rec['translator_id']} を登録しました（翻訳は advisory です）。"
    if path == "/voice-discussion":
        rec = C.register_discussion(
            ref_id=_f(form, "ref_id"), content=_f(form, "content"),
            author=_f(form, "author"))
        return "/voice-discussion", f"{rec['discussion_id']} を投稿しました（談合であり決定ではありません）。"
    if path == "/discovery":
        rec = C.post_public_call(
            title=_f(form, "title"), description=_f(form, "description"),
            region=_f(form, "region"), source_type=_f(form, "source_type"),
            source_url=_f(form, "source_url"),
            human_reviewed=_f(form, "human_reviewed") == "1", notes=_f(form, "notes"))
        return "/discovery", (f"{rec['call_id']} を記録しました。"
                             "掲載は同意でも検証でもありません。観察は介入ではありません。")
    raise C.CommonsError(f"unknown form: {path}")


class Handler(BaseHTTPRequestHandler):
    server_version = "MujinCommons/0.1"

    def _send_html(self, content: str, status: int = 200) -> None:
        data = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _redirect(self, location: str) -> None:
        self.send_response(303)
        self.send_header("Location", location)
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        url = urlparse(self.path)
        render = GET_ROUTES.get(url.path)
        if render is None:
            self._send_html(page("Not Found", "<p>ページがありません。</p>"), 404)
            return
        self._send_html(render(parse_qs(url.query)))

    def do_POST(self) -> None:  # noqa: N802
        url = urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0"))
        form = parse_qs(self.rfile.read(length).decode("utf-8"))
        base = {
            "/proposals/generate": "/commons",
            "/solutions/problem": "/solutions",
            "/solutions/solution": "/solutions",
            "/solutions/resource": "/solutions",
            "/solutions/agent": "/solutions",
        }.get(url.path, url.path)
        try:
            redirect, ok = handle_post(url.path, form)
            sep = "&" if "?" in redirect else "?"
            self._redirect(f"{redirect}{sep}ok={quote(ok)}")
        except C.CommonsError as exc:
            self._redirect(f"{base}?err={quote(str(exc))}")

    def log_message(self, fmt: str, *args) -> None:
        pass  # quiet by default; the JSONL stream is the record that matters


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print("=" * 64)
    print("MUJIN CONTRIBUTION COMMONS — local, append-only, advisory only")
    print(f"  http://127.0.0.1:{PORT}/")
    print('  "Need → Contribution → Connection → Reality Feedback"')
    print("  登録は証明ではない · 撤回は失敗ではない · 支援は債務ではない")
    print("=" * 64)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")


if __name__ == "__main__":
    main()
