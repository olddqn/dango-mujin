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
    '<nav><a href="/">Top</a><a href="/need">Need</a><a href="/contribute">Contribution</a>'
    '<a href="/commons">Commons</a><a href="/proposals">Proposals</a>'
    '<a href="/feedback">Reality Feedback</a><a href="/objection">Objection</a>'
    '<a href="/agents">Agent Commons</a><a href="/transparency">Transparency</a>'
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


def render_need_form(q) -> str:
    body = msg_block(q) + f"""
<p class="note">登録は証明ではありません。撤回は失敗ではありません。支援は債務ではありません。<br>
代理登録の場合、本人の同意は代理では成立しません（同意延期として記録され、本人の確認まで公開されません）。</p>
<form method="post" action="/need">
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
        cands = "".join(
            f"<li>{esc(c['name'])}（{esc(c['candidate_type'])} / {esc(c['provider_kind'])} / {esc(c['kind'])} / {esc(c['id'])}）</li>"
            for c in p["candidates"]) or "<li>（候補なし — Contribution の登録を待っています）</li>"
        blocks.append(
            f"<h2 id='{esc(p['proposal_id'])}'>{esc(p['proposal_id'])} — {esc(p['need_id'])}（{esc(p['need_type'])}）</h2>"
            f"<ul>{cands}</ul>"
            f"<p><small class='inv'>proposal ≠ decision — この提案は誰も拘束せず、常に"
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


def render_transparency(q) -> str:
    inv = "".join(f"<tr><td><code>{esc(k)}</code></td><td><b>{esc(str(v).lower())}</b></td></tr>"
                  for k, v in C.INVARIANT_PHRASES.items())
    body = f"""
<table><tr><th>invariant</th><th>value</th></tr>{inv}</table>
<p class="note">
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
<tr><th>Need Count</th><td>{s['need_count']}（うち公開 {s['needs_public']}）</td></tr>
<tr><th>Contribution Count</th><td>{s['contribution_count']}</td></tr>
<tr><th>Agent Count</th><td>{s['agent_count']}</td></tr>
<tr><th>Proposal Count</th><td>{s['proposal_count']}</td></tr>
<tr><th>Reality Feedback Count</th><td>{s['feedback_count']}</td></tr>
<tr><th>Objection Count</th><td>{s['objection_count']}</td></tr>
<tr><th>TTFR (Time To First Rescue)</th><td>{ttfr}</td></tr>
</table>
<p class="note">この dashboard が測るのは<b>システムの応答速度だけ</b>です。
人の価値・困窮度・貢献度は測定されず、測定可能でもありません（憲法第4条）。</p>
"""
    return page("TTFR Dashboard", body)


# ── HTTP handler ──────────────────────────────────────────────────────────────

GET_ROUTES = {
    "/": render_top,
    "/need": render_need_form,
    "/contribute": render_contribute_form,
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
        )
        note = "（同意延期のため、本人の確認まで非公開で保管されます）" \
            if rec["consent_status"] != "active" else ""
        return "/need", f"{rec['need_id']} を登録しました{note}。登録は証明ではありません。"
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
        base = {"/proposals/generate": "/commons"}.get(url.path, url.path)
        try:
            redirect, ok = handle_post(url.path, form)
            self._redirect(f"{redirect}?ok={quote(ok)}")
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
