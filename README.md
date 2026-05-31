# Dan-Go Mujin Protocol

> **Dan-Go Mujin Protocol is not crowdfunding.**
> It is a public negotiation protocol for turning impossible claims into reality.

**gitlawb (decentralized):** [https://gitlawb.com/z6MkpWP3c2xE5Veu5xSJxviWUrM69SDX4offMifsVXAs31Ts/dango-mujin](https://gitlawb.com/z6MkpWP3c2xE5Veu5xSJxviWUrM69SDX4offMifsVXAs31Ts/dango-mujin)

---

## What is a Claim?

A claim is not true or false by default.
**A claim is a proposed state transition.**

The protocol asks:

- What is missing?
- Who can help?
- What resources are needed?
- What contradictions exist?
- What can be executed now?
- What must be escalated?
- What must be rejected?

## Core Loop

```
Claim → Negotiation → Contribution → Execution → Reality Feedback
```

## Ordinary crowdfunding vs Dan-Go Mujin

| Crowdfunding | Dan-Go Mujin |
|---|---|
| Collect money | Submit a Claim |
| Return rewards | Decompose required conditions |
| Platform decides | Negotiation decides |
| Money only | Code, compute, translation, housing, legal review, distribution, social reach, reputation, care |

## Inspiration

Dan-Go Mujin is inspired by the Japanese concept of **無尽 (mujin)**:
a rotating mutual-credit association based on trust, contribution, and shared realization.

**Dan-Go (談合)** is not corruption.
It is **public resonance, agreement formation, and cooperative design**.

This version is for AI agents and humans working together:
not only money, but any form of contribution can become part of the negotiation.

## Key Concepts

| Term | Meaning |
|---|---|
| **Dan-Go** | Public negotiation — not secret collusion |
| **Lie** | An unrealized state transition, not an error to be eliminated |
| **Impossible** | A state where not enough negotiation has happened yet |
| **素テーブル (sutable)** | A fully open state table — no hidden information |
| **YacypherPunks** | A cooperative community beyond national and institutional boundaries |
| **第零国家 (State Zero)** | A second affiliation that sits on top of existing states without destroying them |
| **Constitution** | One clause: Do not violate the dignity of another |

## Participation

- Fork this repo
- Submit a Claim (see `CLAIM_FORMAT.md`)
- Contribute to an open Claim
- Object, counter-claim, or propose alternatives
- All are valid participation

## Quick Start

```bash
# Read a claim and see what is missing
python runtime/claim_matcher.py examples/housing.claim.json

# Route contributions to missing conditions
python runtime/contribution_router.py examples/housing.claim.json

# Check trust score from contribution history
python runtime/trust_score.py

# Record execution feedback
python runtime/reality_feedback.py
```

## Phase 22 — Globe（グローブ）基盤

Dan-Go は、AIエージェントと人間が協働して合意形成を行うためのシステムです。
フェーズ22では、その先にある自由参加型共同体「グローブ」の基盤を追加しました。
グローブは、国家・自治体・DAO・地域共同体・プロジェクトなどを包含できる単位であり、
提案・熟議・ルール・実行履歴をGit的に管理することで、政治家中心ではない
新しい共同体運営の可能性を探ります。

Dan-Go is a system for humans and AI agents to collaboratively build consensus.
In Phase 22, we added the foundation for "Globe" — a free-participation voluntary community.
A Globe can encompass nation-states, municipalities, DAOs, local communities, and projects,
managing proposals, deliberations, rules, and execution history in a Git-like manner,
exploring new possibilities for community governance beyond politician-centric models.

```bash
# Globe 一覧を見る
python3 globe/runtime/globe_registry.py list

# 熟議ログを読む
python3 globe/runtime/deliberation_log.py summary proposal-001

# UIサーバーを起動して /globe ページを開く
python3 globe/runtime/globe_server.py
# → http://localhost:7422/globe
```

## Phase 23 — Proposal → Claim 変換

フェーズ23では、採択（accepted）された Proposal を Dan-Go Claim 形式へ変換する仕組みを追加しました。
変換は強制ではなく、実行の起点となる任意のステップです。

In Phase 23, we added the ability to convert accepted Globe Proposals into Dan-Go Claim format.
Conversion is optional and advisory — it creates no obligation and allocates no resources.

> "Proposal is not execution. Claim is not command. Conversion is not allocation."

```bash
# accepted Proposal を Claim に変換する
python3 globe/runtime/proposal_to_claim.py convert proposal-002

# Globe 内の accepted Proposal を一括変換する
python3 globe/runtime/proposal_to_claim.py convert-globe globe-001

# 変換済み Claim の一覧を見る
python3 globe/runtime/proposal_to_claim.py list
```

変換結果は `globe/claims/` に JSON と Markdown の両形式で保存されます。
UIサーバー（`/globe/<id>/proposals/<proposal_id>`）では Claim 変換状況が確認できます。

## Phase 24 — Claim → Directive 変換

フェーズ24では、Claim を Dan-Go Directive（実行ディレクティブ）形式へ変換する基盤を追加しました。
Directive は実行への提案パスを記述しますが、それ自体は実行ではなく、いかなる法的権限も生じません。
実世界アクションの開始には、すべてのステップで人間の明示的な承認が必要です。

In Phase 24, we added the ability to convert Claim documents into Dan-Go Directive format.
A Directive describes a proposed executable path — it is not execution, it creates no legal authority,
and human approval is required before any real-world action begins.

> "Claim is not execution. Directive is not coercion. Directive creates no legal authority."
> "Directive only describes a proposed executable path."
> "Human approval is required before real-world execution."

```bash
# claim_draft Claim を Directive に変換する
python3 globe/runtime/claim_to_directive.py convert claim-proposal-002

# Globe 内の claim_draft Claim を一括変換する
python3 globe/runtime/claim_to_directive.py convert-globe globe-001

# 変換済み Directive の一覧を見る
python3 globe/runtime/claim_to_directive.py list
```

変換結果は `globe/directives/` に JSON と Markdown の両形式で保存されます。
UIサーバーの Proposal 詳細ページでは Claim・Directive の変換状況が一覧表示されます。

## Phase 25 — Directive Execution Log

フェーズ25では、Directive に対する承認・実行試行・観察・フィードバック・異議・差し戻し要求を
append-only の JSONL 形式で記録する Execution Log 基盤を追加しました。

**Execution Log は実行の証明ではありません。ログエントリは法的権限を生じさせません。**
実世界アクションの前には、常に人間の明示的な承認が必要です。
異議と差し戻し要求は常に記録可能です（人間承認ゲートなし）。

In Phase 25, we added an append-only JSONL Execution Log for each Directive.
The log records human approvals, execution attempts, observations, feedback,
objections, and rollback requests — but is never proof of execution and creates
no legal authority.

> "Execution Log is not proof of execution."
> "Log entry is not legal authority."
> "Objection and rollback request must always be recordable."
> "Append-only: existing entries must never be rewritten."

```bash
# 人間承認を記録する
python3 globe/runtime/directive_execution_log.py \
  append directive-claim-proposal-002 human_approval human "Masuo Komori" \
  "試験的実施に向けた人間承認を記録する"

# 観察を記録する（事前の human_approval が必要）
python3 globe/runtime/directive_execution_log.py \
  append directive-claim-proposal-002 observation ai "Dan-Go Agent" \
  "実行前提条件の確認が必要"

# 異議を記録する（常に記録可能）
python3 globe/runtime/directive_execution_log.py \
  append directive-claim-proposal-002 objection human "founding-member-003" \
  "合意確認が必要"

# ログ一覧・サマリ・Markdownエクスポート
python3 globe/runtime/directive_execution_log.py list    directive-claim-proposal-002
python3 globe/runtime/directive_execution_log.py summary directive-claim-proposal-002
python3 globe/runtime/directive_execution_log.py export-md directive-claim-proposal-002
```

ログは `globe/logs/{directive_id}.jsonl` に JSONL 形式で保存されます。
UIサーバーでは Proposal 詳細ページに Execution Log の状況（エントリ数・承認状況・最終エントリ）が表示されます。

## Phase 26 — Cross-Globe Execution Log Summary

フェーズ26では、複数の Globe・複数の Directive にまたがる Execution Log を横断集計する
advisory ダッシュボードを追加しました。

**Summary は advisory のみです。Summary は実行の証明ではありません。法的権限を生じません。
参加者をランク付けしません。異議と差し戻し要求を保存します。**

In Phase 26, we added a cross-globe advisory dashboard that aggregates all Execution Log
entries across all Directives and Globes. The summary is never proof of execution and
creates no legal authority.

> "Summary is advisory only."
> "Summary is not proof of execution."
> "Summary creates no legal authority."
> "Summary does not rank or punish participants."
> "Summary must preserve objections and rollback requests."

```bash
# 全 Globe / 全 Directive のサマリを表示する
python3 globe/runtime/execution_log_summary.py summary

# サマリを globe/reports/ に保存する
python3 globe/runtime/execution_log_summary.py save

# 特定 Globe のサマリを表示する
python3 globe/runtime/execution_log_summary.py show-globe globe-001

# 特定 Directive のサマリを表示する
python3 globe/runtime/execution_log_summary.py show-directive directive-claim-proposal-002
```

サマリは `globe/reports/execution_log_summary.json` と `globe/reports/execution_log_summary.md` に保存されます。
UIサーバーの Globe 一覧ページと Globe 詳細ページにサマリテーブルが表示されます。

## Phase 27 — Reality Feedback Bridge

フェーズ27では、Directive Execution Log の観察・フィードバック・異議・差し戻し要求エントリを
Phase 18（Relief Case Memory）および Phase 19（Care Loop Reopen）に接続する
advisory ブリッジ層を追加しました。

In Phase 27, we added an advisory Reality Feedback Bridge that reads Execution Log entries
(observation / feedback / objection / rollback_request) and generates advisory bridge records
suggesting connections to Phase 18 Relief Case Memory or Phase 19 Care Loop Reopen.

> "Reality feedback is advisory only."
> "Feedback bridge is not proof of resolution."
> "Feedback bridge creates no legal authority."
> "Feedback bridge does not reopen a case automatically."
> "Human review is required before any real-world action."

```bash
# Bridge サマリを表示する
python3 globe/runtime/reality_feedback_bridge.py summary

# レポートを globe/reports/ に保存する
python3 globe/runtime/reality_feedback_bridge.py save

# Directive ごとのブリッジ候補を表示する
python3 globe/runtime/reality_feedback_bridge.py show-directive directive-claim-proposal-002

# Globe ごとのブリッジ候補を表示する
python3 globe/runtime/reality_feedback_bridge.py show-globe globe-001
```

変換結果は `globe/reports/reality_feedback_bridge.json` と `.md` に保存されます。
UIサーバーの Execution Log ページと Directive 詳細ページにブリッジパネルが表示されます。

## Phase 27b — Bridge Target Detail Link

フェーズ27bでは、Phase 27 の Reality Feedback Bridge レコードから、Phase 18 Relief Case Memory および
Phase 19 Care Loop Reopen の具体的な既存データへの advisory link を生成する Bridge Target Linker を追加しました。

**Link candidate は advisory のみです。Link candidate は case 関係の証明ではありません。法的権限を生じません。
ケースを自動的に再開しません。実世界アクションの前には、常に人間の明示的な承認が必要です。**

In Phase 27b, we added a Bridge Target Detail Linker that generates advisory link candidates
from Phase 27 bridge records to specific Phase 18 / Phase 19 data items with confidence scoring.

> "Bridge target link is advisory only."
> "Link candidate is not proof of case relation."
> "Link candidate creates no legal authority."
> "Link candidate does not reopen a case automatically."
> "Human review is required before any real-world action."

```bash
# Link サマリを表示する
python3 globe/runtime/bridge_target_linker.py summary

# レポートを globe/reports/ に保存する
python3 globe/runtime/bridge_target_linker.py save

# Feedback レコードごとの link candidates を表示する
python3 globe/runtime/bridge_target_linker.py show-feedback rfb-002

# Globe ごとの link candidates を表示する
python3 globe/runtime/bridge_target_linker.py show-globe globe-001

# target_type ごとの link candidates を表示する
python3 globe/runtime/bridge_target_linker.py show-target relief_case_memory
```

変換結果は `globe/reports/bridge_target_links.json` と `.md` に保存されます。
UIサーバーの Directive 詳細ページと Execution Log ページに Link Candidates パネルが表示されます。

## Phase 28 — Directive UI Routes

フェーズ28では、Directive・Execution Log・Summary を globe_server.py 上で直接閲覧できる
3つのUIルートを追加しました。

Phase 28 adds three new UI routes to globe_server.py for viewing Directives,
Execution Logs, and per-Globe directive counts directly in the browser.

> "UI display is advisory only."
> "UI display is not proof of execution."
> "UI display creates no legal authority."
> "UI display does not approve execution."
> "UI display must preserve objections and rollback requests."

```bash
# UIサーバーを起動する
python3 globe/runtime/globe_server.py
# → http://localhost:7422/globe

# Directive 一覧
# → http://localhost:7422/globe/globe-001/directives

# Directive 詳細（objective / invariants / execution steps / scope / log summary）
# → http://localhost:7422/globe/globe-001/directives/directive-claim-proposal-002

# Execution Log 全件表示（時系列 · append-only · 異議保存）
# → http://localhost:7422/globe/globe-001/logs/directive-claim-proposal-002
```

## Phase 29 — Voluntary Resolution Signal

フェーズ29では、参加者が Directive Execution Log に対して任意で解決状況を自己申告できる
`voluntary_resolution_signal` エントリタイプを追加しました。

**Resolution signal は自己申告のみです。解決の証明ではありません。
支援を自動的に終了させません。法的権限を生じません。
Contested status は常に記録可能です。**

In Phase 29, participants can voluntarily self-report their perceived resolution status
in the Directive Execution Log. Dan-Go does not certify resolution. The signal is
advisory only and does not close support or create legal authority.

> "Resolution signal is self-reported only."
> "Resolution signal is not proof of resolution."
> "Resolution signal does not close support automatically."
> "Resolution signal creates no legal authority."
> "Contested status must always remain recordable."

```bash
# 解決シグナルを記録する（人間承認不要・常に記録可能）
python3 globe/runtime/directive_execution_log.py \
  append directive-claim-proposal-002 voluntary_resolution_signal human "Masuo Komori" \
  "D.R.A.連携の前提整理はいったん一区切りとする" \
  --resolution-status partially_resolved

# 未解決として継続観察を表明する
python3 globe/runtime/directive_execution_log.py \
  append directive-claim-proposal-005 voluntary_resolution_signal human "Jammy House Steward" \
  "住居アドボカシーは未解決として継続観察する" \
  --resolution-status unresolved

# 異議を記録する（常に記録可能）
python3 globe/runtime/directive_execution_log.py \
  append directive-claim-proposal-002 voluntary_resolution_signal human "member-001" \
  "この解決には合意できない" \
  --resolution-status contested
```

`unresolved` / `contested` / `paused` シグナルは Phase 27 Reality Feedback Bridge の対象となります。
`resolved` / `partially_resolved` はサマリに保存されますが bridge 対象外です。

---

## Phase 30 — Cross-Phase Contribution Summary

フェーズ30では、Phase 20/21 の援助パターン・ニーズ予測データと、Phase 25–29 の実行ログデータを
横断的に集約する**クロスフェーズ貢献サマリー**を追加しました。

**Cross-Phase Summary は勧告的です。影響の証明ではありません。
参加者をランク付けしません。資源を配分しません。
実世界での行動の前に人間によるレビューが必要です。**

In Phase 30, Dan-Go generates an advisory cross-phase contribution summary connecting
Phase 20 aid pattern learning, Phase 21 commons need forecasts, and Phase 25–29
execution log data. This summary is purely advisory — it is not proof of impact,
does not rank participants, and does not allocate resources.

> "Cross-phase summary is advisory only."
> "Cross-phase summary is not proof of impact."
> "Cross-phase summary does not rank participants."
> "Cross-phase summary does not allocate resources."
> "Human review is required before any real-world action."

```bash
# クロスフェーズ サマリー表示
python3 globe/runtime/cross_phase_contribution_summary.py summary

# レポート保存 (JSON + Markdown)
python3 globe/runtime/cross_phase_contribution_summary.py save

# Globe別サマリー
python3 globe/runtime/cross_phase_contribution_summary.py show-globe globe-001

# セクション別表示 (aid / forecast / logs / bridge / links / resolution)
python3 globe/runtime/cross_phase_contribution_summary.py show-section aid
python3 globe/runtime/cross_phase_contribution_summary.py show-section resolution
```

生成ファイル:
- `globe/reports/cross_phase_contribution_summary.json` — 全サマリー (machine-readable)
- `globe/reports/cross_phase_contribution_summary.md` — 人間可読サマリー

UI: `/globe` Globe 一覧ページおよび `/globe/<id>` Globe 詳細ページに
Cross-Phase Summary パネルが追加されます。実行ボタン・割り当てボタンなし。

---

## Phase 31 — Globe Search / Filter UI

フェーズ31では、Globe・Proposal・Directive・Execution Log・Reality Feedback・
Bridge Target Link・Resolution Signal を横断検索・フィルタできる **検索 UI と CLI** を追加しました。

**Search は advisory display のみです。検索結果は関連性の証明ではありません。
参加者をランク付けしません。資源を配分しません。
実世界での行動の前に人間によるレビューが必要です。**

In Phase 31, Dan-Go adds a cross-layer search and filter system across all Globe
artifacts. The search index is built from all available data files and is advisory
display only — no relevance ranking, no allocation, no execution buttons.

> "Search is advisory display only."
> "Search result is not proof of relevance."
> "Search result does not rank participants."
> "Search result does not allocate resources."
> "Human review is required before any real-world action."

```bash
# インデックス生成
python3 globe/runtime/globe_search.py save-index

# テキスト検索
python3 globe/runtime/globe_search.py search 住居
python3 globe/runtime/globe_search.py search "D.R.A."

# フィルタ
python3 globe/runtime/globe_search.py filter --globe globe-001
python3 globe/runtime/globe_search.py filter --entry-type voluntary_resolution_signal
python3 globe/runtime/globe_search.py filter --resolution-status unresolved
python3 globe/runtime/globe_search.py filter --bridge-target both
```

HTTP 検索 URL:
- `http://localhost:7422/globe/search` — 検索フォーム + フィルタ
- `http://localhost:7422/globe/search?q=住居`
- `http://localhost:7422/globe/search?globe=globe-001`
- `http://localhost:7422/globe/search?entry_type=voluntary_resolution_signal`
- `http://localhost:7422/globe/search?resolution_status=unresolved`
- `http://localhost:7422/globe/search?bridge_target=both`

生成ファイル: `globe/reports/globe_search_index.json` (36 items · advisory only)

---

## Phase 32 — Contribution Timeline View

フェーズ32では、Globe / Directive ごとの Execution Log・Resolution Signal・
Reality Feedback・Bridge Target Link を時系列表示する **Timeline View** を追加しました。

**Timeline は advisory display のみです。影響の証明ではありません。
参加者をランク付けしません。資源を配分しません。
実世界での行動の前に人間によるレビューが必要です。**

In Phase 32, Dan-Go generates a chronological contribution timeline across all
execution log entries, resolution signals, bridge feedback records, and link
candidates. Sorted by created_at ascending (stable, no relevance score).

> "Timeline is advisory display only."
> "Timeline is not proof of impact."
> "Timeline does not rank participants."
> "Timeline does not allocate resources."
> "Human review is required before any real-world action."

```bash
# タイムライン サマリー
python3 globe/runtime/contribution_timeline.py summary

# レポート保存 (JSON + Markdown)
python3 globe/runtime/contribution_timeline.py save

# Globe別
python3 globe/runtime/contribution_timeline.py show-globe globe-001

# Directive別
python3 globe/runtime/contribution_timeline.py show-directive directive-claim-proposal-002

# ソースタイプ別 (execution_log / resolution_signal / reality_feedback / bridge_target_link)
python3 globe/runtime/contribution_timeline.py show-type resolution_signal
```

HTTP URL:
- `http://localhost:7422/globe/timeline` — 全 Globe タイムライン (16 items)
- `http://localhost:7422/globe/globe-001/timeline` — Globe-001 (13 items)
- `http://localhost:7422/globe/globe-001/directives/directive-claim-proposal-002/timeline` — Directive (13 items)

生成ファイル:
- `globe/reports/contribution_timeline.json` — 全タイムライン (16 items · advisory only)
- `globe/reports/contribution_timeline.md` — 人間可読

---

## Phase 33 — Proposal Comparison View

フェーズ33では、2 つの Proposal を横並びで比較できる **advisory 比較 UI / CLI** を追加しました。
比較は評価・順位・優劣判定ではなく、人間が熟議の違いを確認するための表示です。

**Comparison は advisory display のみです。ランキングではありません。
Proposal をスコア付けしません。資源を配分しません。
実世界での行動の前に人間によるレビューが必要です。**

In Phase 33, Dan-Go adds a side-by-side advisory comparison of two Proposals
across all Globe-layer artifacts (deliberations, claim, directive, execution log,
bridge feedback, link candidates, timeline). Differences are observable distinctions
only — not scores, not rankings, not judgements of quality.

> "Comparison is advisory display only."
> "Comparison is not ranking."
> "Comparison does not score proposals."
> "Comparison does not allocate resources."
> "Human review is required before any real-world action."

```bash
# Proposal 一覧
python3 globe/runtime/proposal_compare.py list

# 比較表示
python3 globe/runtime/proposal_compare.py compare proposal-002 proposal-005

# レポート保存
python3 globe/runtime/proposal_compare.py save proposal-002 proposal-005
```

HTTP URL:
- `http://localhost:7422/globe/compare` — 選択フォーム
- `http://localhost:7422/globe/compare?proposal_a=proposal-002&proposal_b=proposal-005` — 横並び比較

生成ファイル:
- `globe/reports/proposal_comparison_proposal-002_vs_proposal-005.json`
- `globe/reports/proposal_comparison_proposal-002_vs_proposal-005.md`

---

## Phase 38 — Globe Member Profile View

フェーズ38では、Globe内メンバーの活動履歴を advisory display として可視化する
**Globe Member Profile View** を追加しました。

> **"Member profile is advisory display only."**
> **"Member profile is not identity verification."**
> **"Member profile is not reputation score."**
> **"Member profile creates no authority."**
> **"Member profile does not rank participants."**

### データ収集

6ソース（proposals / deliberations / logs / reality_feedback / contribution_timeline / globe_feed）から
12名のメンバープロフィールを構築。actor_type: human(8), ai(2), system(2)。

### CLIコマンド

```bash
python3 globe/runtime/member_profile.py summary
# member_count: 12, actor_types: 3

python3 globe/runtime/member_profile.py show-member member-masuo-komori
# execution_log_count: 3, human_approval_count: 2, voluntary_resolution_signal_count: 1

python3 globe/runtime/member_profile.py show-globe globe-001
# 8 members in globe-001
```

### URL確認

- http://localhost:7422/globe/members
- http://localhost:7422/globe/members/member-masuo-komori
- http://localhost:7422/globe/members?globe=globe-001

### 生成ファイル

- `globe/runtime/member_profile.py` — プロフィール構築・CLI (12 members, 6 sources)
- `globe/reports/member_profiles.json` — 生成済み JSON
- `globe/reports/member_profiles.md` — 生成済み Markdown

---

## Phase 37b — Dependency Edge URL Enrichment

フェーズ37b では、Phase 37 の未実装部分として残っていた
dependency edge の `{}` placeholder URL を修正しました。

- **修正前**: `/globe/{}/directives/directive-claim-proposal-002` （broken）
- **修正後**: `/globe/globe-001/directives/directive-claim-proposal-002` （correct）

`_render_dep_edge()` に `globe_lookup: dict[str, str]` パラメーターを追加し、
`render_dependencies_page()` で `all_nodes` から lookup を構築して渡します。

**URL enrichment は advisory display のみです。実行順序ではありません。
Directiveをランク付けしません。責任を割り当てません。**

---

## Phase 37 — Directive Dependency Map

フェーズ37では、Directive 間の参照関係・共有キーワード・同一Globe・同一Claim/Proposal由来・
共有ブリッジターゲット・共有解決ステータス・共有注意フラグを検出し、
advisory dependency map として可視化する **Directive Dependency Map** を追加しました。
依存関係マップは観察補助表示にすぎません。実行順序・優先順位・責任割当ではありません。

**Dependency map は advisory display のみです。実行順序ではありません。
Directiveをランク付けしません。責任を割り当てません。
実世界での行動の前に人間によるレビューが必要です。**

### 追加ファイル

- `globe/runtime/directive_dependency_map.py` — 関係検出・CLI (7 relation_types, 4 edges)
- `globe/reports/directive_dependency_map.json` — 生成済み JSON
- `globe/reports/directive_dependency_map.md` — 生成済み Markdown

### CLI

```bash
python3 globe/runtime/directive_dependency_map.py summary
python3 globe/runtime/directive_dependency_map.py show-directive directive-claim-proposal-002
python3 globe/runtime/directive_dependency_map.py show-globe globe-001
python3 globe/runtime/directive_dependency_map.py show-relation shared_keyword
```

### HTTP

| Route | Description |
|-------|-------------|
| `/globe/dependencies` | Full dependency map |
| `/globe/dependencies?globe=globe-001` | Filter by globe |
| `/globe/dependencies?directive=<id>` | Filter by directive |
| `/globe/dependencies?relation=shared_keyword` | Filter by relation type |

---

## Phase 36 — Globe Feed / Changelog

フェーズ36では、Globe 全レイヤー（Proposal / Claim / Directive / Execution Log /
Reality Feedback / Bridge Target Link / Timeline / Activity Heatmap / Directive Checklist）
の活動を created_at 降順で集約した **Globe Feed / Changelog** を追加しました。
フィードは閲覧補助表示にすぎません。実行・影響・参加者ランキングの証明ではありません。

**Feed は advisory display のみです。実行の証明ではありません。
影響の証明ではありません。参加者をランク付けしません。
リソースを配分しません。実世界での行動の前に人間によるレビューが必要です。**

### 追加ファイル

- `globe/runtime/globe_feed.py` — フィード生成・CLI（9 source_types, 29 items）
- `globe/reports/globe_feed.json` — 生成済み JSON
- `globe/reports/globe_feed.md` — 生成済み Markdown

### CLI

```bash
python3 globe/runtime/globe_feed.py summary
python3 globe/runtime/globe_feed.py save
python3 globe/runtime/globe_feed.py show-globe globe-001   # 18 items
python3 globe/runtime/globe_feed.py show-type execution_log # 8 items
```

### HTTP

| Route | Description |
|-------|-------------|
| `/globe/feed` | Full feed, created_at desc |
| `/globe/feed?globe=globe-001` | Filter by globe |
| `/globe/feed?type=execution_log` | Filter by source_type |

---

## Phase 35 — Directive Execution Checklist

フェーズ35では、Directive の execution_steps を advisory チェックリスト形式でブラウザ表示・CLI 確認できる
**Directive Execution Checklist UI / CLI** を追加しました。
チェックリストは実行承認・完了証明・法的効力ではなく、確認補助表示にすぎません。

**Checklist は advisory display のみです。実行の証明ではありません。
完了の証明ではありません。実行を承認しません。
実世界での行動の前に人間によるレビューが必要です。**

In Phase 35, Dan-Go generates an advisory step-by-step checklist for each Directive,
cross-referencing Execution Log entries by step_id (or directive-level summary if no
step-specific entries exist). The checklist is a confirmation aid display only — it
creates no obligation and approves no action.

> "Checklist is advisory display only."
> "Checklist is not proof of execution."
> "Checklist is not proof of completion."
> "Checklist does not approve execution."
> "Human review is required before any real-world action."

```bash
# チェックリスト サマリー
python3 globe/runtime/directive_checklist.py summary

# レポート保存 (JSON + Markdown)
python3 globe/runtime/directive_checklist.py save

# Directive 別
python3 globe/runtime/directive_checklist.py show-directive directive-claim-proposal-002

# Globe 別
python3 globe/runtime/directive_checklist.py show-globe globe-001
```

HTTP URL:
- `http://localhost:7422/globe/globe-001/directives/directive-claim-proposal-002/checklist`

生成ファイル:
- `globe/reports/directive_checklists.json` — 全チェックリスト (machine-readable)
- `globe/reports/directive_checklists.md` — 人間可読チェックリスト

---

## Phase 34 — Activity Heatmap

フェーズ34では、Globe 全体のイベントを日付ごとに集計し、カレンダー形式で可視化する
**Activity Heatmap UI / CLI** を追加しました。
カウントは記録されたイベント数を反映するだけであり、品質・優先度・インパクトの尺度ではありません。

**Heatmap は advisory display のみです。影響の証明ではありません。
参加者をランク付けしません。資源を配分しません。
実世界での行動の前に人間によるレビューが必要です。**

In Phase 34, Dan-Go generates a date-aggregated activity heatmap across all Globe-layer
events (execution_log, resolution_signal, reality_feedback, bridge_target_link). Counts
are what was recorded — not measures of quality, priority, or impact.

> "Heatmap is advisory display only."
> "Heatmap is not proof of impact."
> "Heatmap does not rank participants."
> "Heatmap does not allocate resources."
> "Human review is required before any real-world action."

```bash
# ヒートマップ サマリー
python3 globe/runtime/activity_heatmap.py summary

# レポート保存 (JSON + Markdown)
python3 globe/runtime/activity_heatmap.py save

# 日付フィルタ
python3 globe/runtime/activity_heatmap.py show-date 2026-05-31

# Globe フィルタ
python3 globe/runtime/activity_heatmap.py show-globe globe-001

# Directive フィルタ
python3 globe/runtime/activity_heatmap.py show-directive directive-claim-proposal-002
```

HTTP URL:
- `http://localhost:7422/globe/activity` — 全体ヒートマップ
- `http://localhost:7422/globe/activity?date=2026-05-31` — 日付フィルタ
- `http://localhost:7422/globe/activity?globe=globe-001` — Globe フィルタ

生成ファイル:
- `globe/reports/activity_heatmap.json` — ヒートマップデータ (machine-readable)
- `globe/reports/activity_heatmap.md` — 人間可読ヒートマップレポート

---

## Structure

```
dango-mujin/
├── README.md              — This file
├── asset.toml             — GITSEA asset registration (split, royalty, insurance)
├── CONSTITUTION.md        — The one law
├── MUJIN_PROTOCOL.md      — Full protocol specification
├── CLAIM_FORMAT.md        — How to write a Claim
├── CONTRIBUTION_SPEC.md   — What counts as a contribution
├── TRUST_MODEL.md         — How trust is calculated
├── SUTABLE_SPEC.md        — The open state table format
├── ROADMAP.md             — Where this goes next
├── examples/              — Sample claims
├── runtime/               — Minimum viable Python runtime
├── globe/                 — Phase 22–25: Globe foundation + Claim + Directive + Log
│   ├── data/              — Globe, Proposal, Deliberation JSON data
│   ├── claims/            — Phase 23: Generated Claim files (JSON + Markdown)
│   ├── directives/        — Phase 24: Generated Directive files (JSON + Markdown)
│   ├── logs/              — Phase 25: Execution Logs (JSONL · append-only)
│   ├── runtime/           — CLI tools + HTTP server (stdlib only)
│   └── spec/              — Globe specification
└── bridge/                — Dan-Go bridge layer (GITSEA, OGI, gitlawb)
    └── gitsea/            — GITSEA asset registration bridge (advisory only)
```

## GITSEA Asset

This repository declares itself as a GITSEA asset via `asset.toml`.
GITSEA can make repository contribution economically legible.
Dan-Go makes contribution negotiable before it becomes economic.

No private keys. No wallet operations. No on-chain submissions from Dan-Go tooling.
See `bridge/gitsea/` for the advisory bridge layer.

## Principles

1. Not a finished product. A participable protocol.
2. Dan-Go itself evolves through public negotiation.
3. Forks welcome. Objections welcome. Claims welcome.
4. AI is not a governor. AI is a missionary, mediator, and recorder.
5. Do not present unobserved states as observed.
6. No exaggeration.
7. No private keys, API keys, or seed phrases ever.
8. No investment solicitation. This is a thought and cooperation protocol.
9. Violence, exploitation, and coercion are forbidden means.
10. All negotiation is publicly auditable whenever possible.

---

*Dan-Go Mujin is in protocol-draft state. Everything here is subject to public negotiation.*
