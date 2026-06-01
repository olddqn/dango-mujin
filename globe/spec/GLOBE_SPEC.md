# Globe Spec — Dan-Go Phase 22

> **Globe（グローブ）** は、Dan-Go プロトコルの上位概念として追加された
> 自由参加型共同体の単位です。

## 概要 / Overview

Globe is a free-participation voluntary community unit that can encompass:
- 国家・自治体 / Nation-states, municipalities
- DAO / DAOs
- 地域共同体 / Local communities  
- プロジェクト / Projects
- 協同住宅・相互扶助グループ / Cooperative housing and mutual aid groups

**参加は自由。離脱も自由。暴力・搾取・強制は禁じられた手段。**
Participation is free. Exit is free. Violence, exploitation, and coercion are forbidden means.

## データモデル / Data Models

### Globe

```json
{
  "globe_id":            "globe-001",
  "name":                "第零国家 (State Zero)",
  "description":         "...",
  "founding_statement":  "...",
  "membership_policy":   "open",
  "governance_model":    "deliberative_consensus",
  "gitsea_link": {
    "gitsea_repo_url":   "https://...",
    "gitsea_issue_url":  null,
    "gitsea_pr_url":     null,
    "commit_hash":       null,
    "linked_rule_path":  "CONSTITUTION.md"
  },
  "created_at":          "2026-05-30T00:00:00Z",
  "updated_at":          "2026-05-30T00:00:00Z"
}
```

**membership_policy 値:**
- `open` — 誰でも参加できる
- `invite` — 招待制
- `closed` — 新規参加停止中

**governance_model 値:**
- `deliberative_consensus` — 熟議合意形成（Dan-Go 標準）
- `voting` — 多数決
- `council` — 評議会制

### Proposal（提案）

```json
{
  "proposal_id":  "proposal-001",
  "globe_id":     "globe-001",
  "title":        "...",
  "body":         "...",
  "proposer":     "founding-member-001",
  "status":       "discussion",
  "gitsea_link":  { ... },
  "created_at":   "2026-05-30T00:00:00Z",
  "updated_at":   "2026-05-30T00:00:00Z"
}
```

**status ライフサイクル:**

```
draft → discussion → voting → accepted
                            ↘ rejected
         (いつでも) → archived
```

- `draft` — 草稿。作成者が編集中。
- `discussion` — 公開熟議フェーズ。
- `voting` — 投票フェーズ。
- `accepted` — 採択。実行計画へ変換。
- `rejected` — 否決。反対意見は保存される。
- `archived` — 履歴保存。削除不可。

### Deliberation（熟議）

```json
{
  "deliberation_id": "delib-001",
  "proposal_id":     "proposal-001",
  "speaker_type":    "human",
  "speaker_name":    "founding-member-001",
  "content":         "...",
  "created_at":      "2026-05-30T00:10:00Z"
}
```

**speaker_type:**
- `human` — 人間の参加者
- `ai` — AIメディエーター・アシスタント
- `system` — プロトコルイベント（ステータス変更、記録など）

**重要原則：熟議ログはappend-only。エントリは削除不可。少数意見・反対意見は等しく保存される。**

### GITSEA Link（GITSEA連携メタ情報）

```json
{
  "gitsea_repo_url":   "https://gitlawb.com/.../dango-mujin",
  "gitsea_issue_url":  "https://...",
  "gitsea_pr_url":     "https://...",
  "commit_hash":       "abc1234",
  "linked_rule_path":  "CONSTITUTION.md"
}
```

Globe および Proposal は GITSEA / Gitlawb へのリンクを保持できる。
現段階では実接続は行わず、メタ情報のみ保存する。

## 熟議フロー / Deliberation Flow

Dan-Go は単なる投票システムではない。

```
1. 提案する (Propose)
       ↓
2. 熟議する (Deliberate)
       ↓
3. AIが論点を整理する (AI organizes key arguments)
       ↓
4. 反対意見・少数意見も保存する (Preserve minority opinions)
       ↓
5. ルールや実行計画に変換する (Convert to rules or execution plan)
       ↓
6. 履歴として残す (Record as append-only history)
       ↓
7. 必要ならGit的に修正・分岐・統合する (Fork, modify, merge as needed)
```

## Proposal → Claim 変換 / Proposal-to-Claim Conversion (Phase 23)

`accepted` 状態になった Proposal は、Dan-Go Claim 形式に変換できる。

```
Proposal (accepted)
       ↓  proposal_to_claim.py
Dan-Go Claim (claim_draft)
       ↓  contribution_router.py / claim_matcher.py
実行交渉・Contribution募集
```

### Claim JSON 形式

```json
{
  "claim_id":              "claim-proposal-002",
  "source_type":           "proposal",
  "source_proposal_id":    "proposal-002",
  "globe_id":              "globe-001",
  "title":                 "...",
  "claim_body":            "... (Proposal の body 全文)",
  "rationale":             "... (body から抽出した理由・背景)",
  "deliberation_summary":  [
    {
      "deliberation_id":   "delib-005",
      "speaker_type":      "human",
      "speaker_name":      "founding-member-002",
      "content_excerpt":   "最初の120文字...",
      "created_at":        "2026-05-30T01:10:00Z"
    }
  ],
  "deliberation_count":    2,
  "gitsea_link":           { ... },
  "status":                "claim_draft",
  "authority":             "none",
  "claim_creates_obligation": false,
  "conversion_is_allocation": false,
  "created_at":            "2026-05-30T...",
  "updated_at":            "2026-05-30T..."
}
```

### 変換の原則 / Conversion Principles

- **accepted 状態のみ変換可能。** draft / discussion / voting / rejected は変換不可。
- **変換は強制ではない。** Claim への変換はあくまで任意の次ステップ。
- **Claim は命令ではない。** Proposal is not execution. Claim is not command.
- **変換は配分ではない。** Conversion is not allocation.
- **Claim はappend-only。** 生成後のClaimは新しいファイルとして保存される。

### 出力先 / Output

```
globe/claims/
├── claim-proposal-002.json   — Claim JSON
├── claim-proposal-002.md     — Claim Markdown
├── claim-proposal-005.json
└── claim-proposal-005.md
```

## Claim → Directive 変換 / Claim-to-Directive Conversion (Phase 24)

`claim_draft` 状態の Claim は、Dan-Go Directive 形式に変換できる。
Directive は実行への提案パスを記述するが、実行そのものではない。

```
Proposal (accepted)
       ↓  proposal_to_claim.py          (Phase 23)
Dan-Go Claim (claim_draft)
       ↓  claim_to_directive.py         (Phase 24)
Dan-Go Directive (directive_draft)
       ↓  人間の承認 (Human approval)
実行ステップ (Execution steps — voluntary, non-coercive)
       ↓
Reality Feedback（実行フィードバック記録）
```

### Directive JSON 形式

```json
{
  "directive_id":                   "directive-claim-proposal-002",
  "source_type":                    "claim",
  "source_claim_id":                "claim-proposal-002",
  "source_proposal_id":             "proposal-002",
  "globe_id":                       "globe-001",
  "title":                          "...",
  "objective":                      "...",
  "scope": {
    "in_scope":                     ["..."],
    "out_of_scope":                 ["..."]
  },
  "non_authority_clause":           "...",
  "execution_steps": [
    {
      "step_id":                    "step-001",
      "description":                "...",
      "description_en":             "...",
      "required_contributions":     ["..."],
      "status":                     "pending",
      "human_approval_required":    true,
      "execution_allowed":          false
    }
  ],
  "required_evidence":              ["..."],
  "status":                         "directive_draft",
  "authority":                      "none",
  "directive_creates_legal_authority": false,
  "directive_is_coercion":          false,
  "directive_creates_obligation":   false,
  "human_approval_required":        true,
  "created_at":                     "2026-05-30T...",
  "updated_at":                     "2026-05-30T..."
}
```

### Directive の原則 / Directive Principles

- **claim_draft 状態のみ変換可能。** accepted/rejected Claim は変換不可。
- **Claim is not execution.** Directive is not coercion.
- **Directive creates no legal authority.** 法的権限は一切生じない。
- **Human approval is required.** 実世界アクションの前に人間の明示的承認が必要。
- **Directive only describes a proposed executable path.** 実行経路の提案に過ぎない。
- **Directive はappend-only。** 修正は新しいファイルとして記録される。

### 出力先 / Output

```
globe/directives/
├── directive-claim-proposal-002.json   — Directive JSON
├── directive-claim-proposal-002.md     — Directive Markdown
├── directive-claim-proposal-005.json
└── directive-claim-proposal-005.md
```

## Directive Execution Log（Phase 25）

Directive に対する承認・実行試行・観察・フィードバック・異議・差し戻し要求を
append-only の JSONL 形式で記録する基盤。

### 変換チェーン全体 / Full Conversion Chain

```
Proposal (accepted)
       ↓  proposal_to_claim.py          (Phase 23)
Dan-Go Claim (claim_draft)
       ↓  claim_to_directive.py         (Phase 24)
Dan-Go Directive (directive_draft)
       ↓  directive_execution_log.py    (Phase 25)
Execution Log (JSONL · append-only)
       ↓  human approval per step
実世界アクション (voluntary · non-coercive · human-approved)
       ↓
Reality Feedback
```

### Execution Log Entry（ログエントリ）形式

```json
{
  "log_id":                 "log-001",
  "directive_id":           "directive-claim-proposal-002",
  "globe_id":               "globe-001",
  "entry_type":             "human_approval",
  "actor_type":             "human",
  "actor_name":             "Masuo Komori",
  "content":                "試験的実施に向けた人間承認を記録する",
  "evidence_refs":          [],
  "non_coercion_confirmed": true,
  "legal_authority_created": false,
  "log_is_proof_of_execution": false,
  "log_certifies_outcome":  false,
  "log_compels_action":     false,
  "append_only":            true,
  "created_at":             "2026-05-30T..."
}
```

### Entry Types（エントリ種別）

| entry_type | 説明 | 承認ゲート |
|------------|------|-----------|
| `human_approval` | 人間による明示的承認 | 不要（常に記録可） |
| `execution_attempt` | 実行試行の記録 | 事前の human_approval が必要（WARNING） |
| `observation` | 実行中・後の観察 | 事前の human_approval が必要（WARNING） |
| `feedback` | フィードバック | 事前の human_approval が必要（WARNING） |
| `objection` | 異議申し立て | **常に記録可（承認不要）** |
| `rollback_request` | 差し戻し要求 | **常に記録可（承認不要）** |

### Execution Log の原則

- **Execution Log is not proof of execution.** ログは実行の証明ではない。
- **Log entry is not legal authority.** エントリはいかなる法的権限も生じさせない。
- **Human approval is required before real-world execution.** 実世界アクション前に人間の承認が必要。
- **Objection and rollback request must always be recordable.** 異議・差し戻し要求は常に記録可能。
- **Append-only: existing entries must never be rewritten.** 既存エントリは書き換え不可。
- **Warning, not block.** 承認なしの execution_attempt 等は警告を出すが記録は行う（強制しない）。

### 出力先 / Output

```
globe/logs/
├── directive-claim-proposal-002.jsonl  — Execution Log (JSONL · append-only)
├── directive-claim-proposal-002.md     — Exported Markdown (export-md コマンド)
├── directive-claim-proposal-005.jsonl
└── directive-claim-proposal-005.md
```

---

## Phase 26 — Cross-Globe Execution Log Summary（フェーズ26）

複数の Globe・複数の Directive にまたがる Execution Log を横断集計する advisory ダッシュボード。

Cross-globe advisory dashboard that aggregates Execution Log entries across all Directives and Globes.

### 不変条件 / Invariants

> "Summary is advisory only."
> "Summary is not proof of execution."
> "Summary creates no legal authority."
> "Summary does not rank or punish participants."
> "Summary must preserve objections and rollback requests."

| Field | Value |
|-------|-------|
| `summary_is_advisory_only` | `true` |
| `summary_is_not_proof_of_execution` | `true` |
| `summary_creates_no_legal_authority` | `true` |
| `summary_does_not_rank_participants` | `true` |
| `summary_preserves_objections` | `true` |
| `authority` | `none` |

### Summary スキーマ / Schema

```json
{
  "summary_id": "execution-log-summary-001",
  "summary_is_advisory_only": true,
  "summary_is_not_proof_of_execution": true,
  "summary_creates_no_legal_authority": true,
  "summary_does_not_rank_participants": true,
  "summary_preserves_objections": true,
  "authority": "none",
  "phase": 26,
  "generated_at": "2026-05-31T...",
  "total_directives_with_logs": 2,
  "total_log_entries": 6,
  "total_objections": 1,
  "total_rollback_requests": 0,
  "directives": [
    {
      "directive_id": "directive-claim-proposal-002",
      "globe_id": "globe-001",
      "globe_name": "第零国家 (State Zero)",
      "title": "...",
      "total_entries": 5,
      "human_approval_count": 2,
      "execution_attempt_count": 0,
      "observation_count": 2,
      "feedback_count": 0,
      "objection_count": 1,
      "rollback_request_count": 0,
      "has_human_approval": true,
      "last_entry_type": "observation",
      "last_entry_at": "2026-05-30T...",
      "all_entries_legal_authority_created_false": true,
      "all_entries_log_is_proof_of_execution_false": true
    }
  ],
  "by_globe": [
    {
      "globe_id": "globe-001",
      "globe_name": "第零国家 (State Zero)",
      "directive_count": 2,
      "total_entries": 6,
      "human_approval_count": 2,
      "objection_count": 1,
      "rollback_request_count": 0
    }
  ],
  "phase_phrases": [
    "Summary is advisory only.",
    "Summary is not proof of execution.",
    "Summary creates no legal authority.",
    "Summary does not rank or punish participants.",
    "Summary must preserve objections and rollback requests."
  ]
}
```

### CLI コマンド / CLI

```bash
# 全 Globe / 全 Directive のサマリを表示
python3 globe/runtime/execution_log_summary.py summary

# サマリを globe/reports/ に保存
python3 globe/runtime/execution_log_summary.py save

# 特定 Globe のサマリを表示
python3 globe/runtime/execution_log_summary.py show-globe globe-001

# 特定 Directive のサマリを表示
python3 globe/runtime/execution_log_summary.py show-directive directive-claim-proposal-002
```

### 出力先 / Output

```
globe/reports/
├── execution_log_summary.json  — JSON summary (advisory only)
└── execution_log_summary.md    — Markdown summary (advisory only)
```

### UI 統合 / UI Integration

- `/globe` — Globe 一覧ページに Cross-Globe Summary パネルを表示
- `/globe/<globe_id>` — Globe 詳細ページにその Globe の Summary パネルを表示

---

## Phase 27 — Reality Feedback Bridge（フェーズ27）

Execution Log の observation / feedback / objection / rollback_request エントリを
Phase 18 Relief Case Memory および Phase 19 Care Loop Reopen と接続する advisory bridge。

Connects Directive Execution Log entries (observation / feedback / objection /
rollback_request) to Phase 18 Relief Case Memory and Phase 19 Care Loop Reopen
via advisory bridge records.

### 不変条件 / Invariants

> "Reality feedback is advisory only."
> "Feedback bridge is not proof of resolution."
> "Feedback bridge creates no legal authority."
> "Feedback bridge does not reopen a case automatically."
> "Human review is required before any real-world action."

| Field | Value |
|-------|-------|
| `reality_feedback_is_advisory_only` | `true` |
| `feedback_bridge_is_not_proof_of_resolution` | `true` |
| `feedback_bridge_creates_no_legal_authority` | `true` |
| `feedback_bridge_does_not_reopen_case_automatically` | `true` |
| `human_review_is_required_before_any_real_world_action` | `true` |
| `authority` | `none` |

### Bridge 判定ルール / Bridge Determination Rules

| Entry type | キーワード | suggested_bridge_target |
|-----------|-----------|------------------------|
| any | 住居 / housing / tenant / 避難 / 難民 / relief など | `relief_case_memory` (Phase 18) |
| any | 再開 / reopen / care / follow-up / 継続 など | `care_loop_reopen` (Phase 19) |
| any | 両方含む | `both` |
| `objection` / `rollback_request` | キーワードなし | `care_loop_reopen` (default) |
| `observation` / `feedback` | キーワードなし | `none` |

### Bridge Record スキーマ / Schema

```json
{
  "feedback_id": "rfb-001",
  "source_directive_id": "directive-claim-proposal-002",
  "globe_id": "globe-001",
  "source_log_id": "log-002",
  "entry_type": "observation",
  "actor_type": "ai",
  "actor_name": "Dan-Go Agent",
  "content": "実行前提条件の確認が必要",
  "suggested_bridge_target": "none",
  "suggested_reason": "no keyword match...",
  "requires_human_review": true,
  "creates_no_legal_authority": true,
  "not_proof_of_resolution": true,
  "advisory_only": true
}
```

### CLI コマンド / CLI

```bash
# 全サマリを表示
python3 globe/runtime/reality_feedback_bridge.py summary

# globe/reports/ に保存
python3 globe/runtime/reality_feedback_bridge.py save

# Directive ごとに表示
python3 globe/runtime/reality_feedback_bridge.py show-directive directive-claim-proposal-002

# Globe ごとに表示
python3 globe/runtime/reality_feedback_bridge.py show-globe globe-001
```

### 出力先 / Output

```
globe/reports/
├── reality_feedback_bridge.json  — JSON bridge report (advisory only)
└── reality_feedback_bridge.md    — Markdown bridge report (advisory only)
```

### UI 統合 / UI Integration

- `/globe/<id>/logs/<directive_id>` — Execution Log 全件表示ページにBridgeパネルを表示
- `/globe/<id>/directives/<directive_id>` — Directive 詳細ページにBridgeパネルを表示
- 承認ボタン・実行ボタンは一切追加しない。表示は advisory のみ。

---

## Phase 27b — Bridge Target Detail Link（フェーズ27b）

Phase 27 の Reality Feedback Bridge で生成された `suggested_bridge_target` を、
Phase 18 Relief Case Memory / Phase 19 Care Loop Reopen の具体的な既存データに advisory link する。

> "Bridge target link is advisory only."
> "Link candidate is not proof of case relation."
> "Link candidate creates no legal authority."
> "Link candidate does not reopen a case automatically."
> "Human review is required before any real-world action."

### 不変条件 / Invariants

| Key | Value |
|-----|-------|
| `bridge_target_link_is_advisory_only` | `true` |
| `link_candidate_is_not_proof_of_case_relation` | `true` |
| `link_candidate_creates_no_legal_authority` | `true` |
| `link_candidate_does_not_reopen_case_automatically` | `true` |
| `human_review_is_required_before_any_real_world_action` | `true` |
| `authority` | `"none"` |

### Link Candidate スキーマ

```json
{
  "link_id": "lnk-002",
  "source_feedback_id": "rfb-002",
  "source_directive_id": "directive-claim-proposal-002",
  "globe_id": "globe-001",
  "suggested_bridge_target": "relief_case_memory",
  "candidate_target_type": "relief_case_memory",
  "candidate_path": "bridge/gitsea/relief/examples/relief-case-registry.json",
  "candidate_item_id": "relief-case-003",
  "candidate_item_type": "relief_case",
  "candidate_description": "Supply coordination was observed for displaced family...",
  "match_reason": "commons_id match (dra-001) + case_type 'refugee_relief_followup' contains refugee keyword",
  "confidence": "high",
  "requires_human_review": true,
  "creates_no_legal_authority": true,
  "does_not_reopen_case_automatically": true,
  "advisory_only": true,
  "created_at": "2026-05-31T01:00:22"
}
```

### 信頼スコア / Confidence scoring

| confidence | 条件 |
|------------|------|
| `high`   | commons_id が content にマッチ かつ ケースのtype/descに関連キーワードあり |
| `medium` | commons_id マッチ のみ、または キーワードオーバーラップ |
| `low`    | ファイルレベルの間接関連（fallback） |

### CLI

```bash
python3 globe/runtime/bridge_target_linker.py summary
python3 globe/runtime/bridge_target_linker.py save
python3 globe/runtime/bridge_target_linker.py show-feedback rfb-002
python3 globe/runtime/bridge_target_linker.py show-globe globe-001
python3 globe/runtime/bridge_target_linker.py show-target relief_case_memory
```

### 出力先 / Output directories

- `globe/reports/bridge_target_links.json` — JSONL link candidates report
- `globe/reports/bridge_target_links.md` — Markdown report

### UI統合 / UI integration

- `/globe/<id>/directives/<directive_id>` — Directive 詳細ページに Link Candidates パネルを表示
- `/globe/<id>/logs/<directive_id>` — Execution Log ページに Link Candidates パネルを表示
- 承認ボタン・再開ボタン・実行ボタンは一切追加しない。表示は advisory のみ。

---

## Phase 31 — Globe Search / Filter UI（フェーズ31）

Globe・Proposal・Directive・Execution Log・Reality Feedback・Bridge Target Link・Resolution Signal を
横断検索・フィルタできる UI と CLI を追加。

> "Search is advisory display only."
> "Search result is not proof of relevance."
> "Search result does not rank participants."
> "Search result does not allocate resources."
> "Human review is required before any real-world action."

### 不変条件 / Invariants

| Key | Value |
|-----|-------|
| `search_is_advisory_display_only` | `true` |
| `search_result_is_not_proof_of_relevance` | `true` |
| `search_result_does_not_rank_participants` | `true` |
| `search_result_does_not_allocate_resources` | `true` |
| `human_review_is_required_before_any_real_world_action` | `true` |
| `authority` | `"none"` |

### 検索対象 / Index scope

| item_type | ソース |
|-----------|--------|
| `globe` | `globe/data/globes.json` |
| `proposal` | `globe/data/proposals.json` |
| `deliberation` | `globe/data/deliberations.json` |
| `claim` | `globe/claims/*.json` |
| `directive` | `globe/directives/*.json` |
| `log` | `globe/logs/*.jsonl` |
| `feedback` | `globe/reports/reality_feedback_bridge.json` |
| `link` | `globe/reports/bridge_target_links.json` |

### 検索仕様

- stdlib のみ（外部ライブラリなし）
- lowercase simple substring search（正規表現なし）
- ranking score は使わない
- 結果順: `source_path` + `created_at` の安定ソート（関連度順ではない）
- 一致理由: `matched title / matched content / matched tag` 等、理由を説明のみ

### CLI

```bash
# インデックスを生成・保存
python3 globe/runtime/globe_search.py save-index

# テキスト検索
python3 globe/runtime/globe_search.py search 住居
python3 globe/runtime/globe_search.py search "D.R.A."

# フィルタ (組み合わせ可)
python3 globe/runtime/globe_search.py filter --globe globe-001
python3 globe/runtime/globe_search.py filter --entry-type voluntary_resolution_signal
python3 globe/runtime/globe_search.py filter --resolution-status unresolved
python3 globe/runtime/globe_search.py filter --bridge-target both
python3 globe/runtime/globe_search.py filter --type directive
```

### HTTP ルート

| URL | 内容 |
|-----|------|
| `/globe/search` | 検索フォーム + フィルタチップ |
| `/globe/search?q=<query>` | テキスト検索結果 |
| `/globe/search?globe=<globe_id>` | Globe フィルタ |
| `/globe/search?entry_type=<type>` | Entry type フィルタ |
| `/globe/search?resolution_status=<status>` | Resolution status フィルタ |
| `/globe/search?bridge_target=<target>` | Bridge target フィルタ |

### 生成ファイル

| ファイル | 説明 |
|---------|------|
| `globe/reports/globe_search_index.json` | 検索インデックス（advisory only） |

### UI特性

- 実行ボタン・承認ボタン・配分ボタンは作らない
- ランキングスコアは表示しない
- 既存ページへのリンクのみ（新しい操作機能なし）
- `advisory_only: true` を全インデックス項目に付与

---

## Phase 32 — Contribution Timeline View（フェーズ32）

Globe / Directive ごとの Execution Log・Resolution Signal・Reality Feedback・
Bridge Target Link を時系列で表示する Timeline View。

> "Timeline is advisory display only."
> "Timeline is not proof of impact."
> "Timeline does not rank participants."
> "Timeline does not allocate resources."
> "Human review is required before any real-world action."

### 不変条件 / Invariants

| Key | Value |
|-----|-------|
| `timeline_is_advisory_display_only` | `true` |
| `timeline_is_not_proof_of_impact` | `true` |
| `timeline_does_not_rank_participants` | `true` |
| `timeline_does_not_allocate_resources` | `true` |
| `human_review_is_required_before_any_real_world_action` | `true` |
| `authority` | `"none"` |

### source_type

| source_type | ソース | 件数 |
|-------------|--------|------|
| `execution_log` | `globe/logs/*.jsonl` の非 resolution_signal エントリ | 6 |
| `resolution_signal` | `globe/logs/*.jsonl` の voluntary_resolution_signal エントリ | 2 |
| `reality_feedback` | `globe/reports/reality_feedback_bridge.json` | 4 |
| `bridge_target_link` | `globe/reports/bridge_target_links.json` | 4 |

### ソート仕様

- `created_at` 昇順（ISO 文字列ソートで正確）
- 同一 `created_at` の場合: `source_type` + `source_id` で安定ソート
- score / ranking なし

### needs_attention フラグ

以下の条件に該当する item は `needs_attention: true` — 優先順位ではなく観察対象の識別子

| 条件 | 理由 |
|------|------|
| `event_type` = `objection` または `rollback_request` | 実行ログに異議・ロールバック要求 |
| `resolution_status` = `unresolved` または `contested` | 未解決・異議ある解決シグナル |
| `confidence` = `high` (bridge_target_link) | 高信頼度リンク候補 |

### CLI

```bash
# 全体サマリー
python3 globe/runtime/contribution_timeline.py summary

# レポート保存
python3 globe/runtime/contribution_timeline.py save

# Globe別タイムライン
python3 globe/runtime/contribution_timeline.py show-globe globe-001

# Directive別タイムライン
python3 globe/runtime/contribution_timeline.py show-directive directive-claim-proposal-002

# ソースタイプ別
python3 globe/runtime/contribution_timeline.py show-type resolution_signal
python3 globe/runtime/contribution_timeline.py show-type reality_feedback
```

### HTTP ルート

| URL | 内容 |
|-----|------|
| `/globe/timeline` | 全 Globe タイムライン |
| `/globe/<globe_id>/timeline` | Globe 別タイムライン |
| `/globe/<globe_id>/directives/<directive_id>/timeline` | Directive 別タイムライン |

### 生成ファイル

| ファイル | 説明 |
|---------|------|
| `globe/reports/contribution_timeline.json` | タイムライン全体 (machine-readable) |
| `globe/reports/contribution_timeline.md` | 人間可読タイムライン |

### UI特性

- 承認ボタン・実行ボタン・配分ボタンなし
- スコア・ランキングなし
- `needs_attention` は観察対象の識別のみ（優先順位付けではない）
- 既存の Directive / Log ページへのリンクのみ

---

## Phase 33 — Proposal Comparison View（フェーズ33）

2 つの Proposal を横並びで比較する advisory UI / CLI。
比較は評価・順位・優劣判定ではなく、人間が熟議の違いを確認するための表示。

> "Comparison is advisory display only."
> "Comparison is not ranking."
> "Comparison does not score proposals."
> "Comparison does not allocate resources."
> "Human review is required before any real-world action."

### 不変条件 / Invariants

| Key | Value |
|-----|-------|
| `comparison_is_advisory_display_only` | `true` |
| `comparison_is_not_ranking` | `true` |
| `comparison_does_not_score_proposals` | `true` |
| `comparison_does_not_allocate_resources` | `true` |
| `human_review_is_required_before_any_real_world_action` | `true` |
| `authority` | `"none"` |

### 比較項目

| 項目 | 説明 |
|------|------|
| `status` | Proposal ステータス |
| `globe_id` | Globe |
| `deliberation_count` | 熟議エントリ数 |
| `claim_exists` / `claim_status` | Claim 変換済み |
| `directive_exists` / `directive_status` | Directive 変換済み |
| `log_entry_count` | Execution Log エントリ数 |
| `human_approval_count` | 人間承認数 |
| `objection_count` | 異議数 |
| `rollback_request_count` | ロールバック要求数 |
| `voluntary_resolution_signal_count` | Resolution Signal 数 |
| `latest_resolution_status` | 最新 Resolution Status |
| `bridge_record_count` | Bridge Feedback 記録数 |
| `link_candidate_count` | Link Candidate 数 |
| `high_confidence_links` | 高信頼度リンク数 |
| `timeline_item_count` | Timeline Item 数 |

### 差異表示方針

- 差異は「観察上の相違」として列挙する
- 「優れている」「劣っている」は記載しない
- スコア・ランキングは生成しない

### CLI

```bash
# Proposal 一覧
python3 globe/runtime/proposal_compare.py list

# 比較表示
python3 globe/runtime/proposal_compare.py compare proposal-002 proposal-005

# レポート保存
python3 globe/runtime/proposal_compare.py save proposal-002 proposal-005
```

### HTTP ルート

| URL | 内容 |
|-----|------|
| `/globe/compare` | Proposal 選択フォーム |
| `/globe/compare?proposal_a=proposal-002&proposal_b=proposal-005` | 横並び比較 |

### 生成ファイル

| ファイル | 説明 |
|---------|------|
| `globe/reports/proposal_comparison_<id_a>_vs_<id_b>.json` | 比較レポート (machine-readable) |
| `globe/reports/proposal_comparison_<id_a>_vs_<id_b>.md` | 人間可読比較レポート |

### UI特性

- 実行ボタン・承認ボタン・配分ボタンなし
- スコア・ランキングなし
- 差異は観察表示のみ
- 既存ページへのリンクのみ

---

## Phase 37b — Dependency Edge URL Enrichment（フェーズ37b）

Phase 37 で `{}` placeholder になっていた dependency edge の directive URL を修正。
`globe_lookup`（directive_id → globe_id マップ）を node metadata から構築し、
`_render_dep_edge()` に渡すことで、正しいリンクを生成する。

- **修正前**: `href="/globe/{}/directives/directive-claim-proposal-002"` （broken）
- **修正後**: `href="/globe/globe-001/directives/directive-claim-proposal-002"` （correct）

URL enrichment は利便性改善であり、実行順序・優先順位・責任割当ではない。

### 実装変更

- `_render_dep_edge(e, globe_lookup)` — `globe_lookup: dict[str, str]` パラメーター追加
- `render_dependencies_page()` — `globe_lookup` を `all_nodes` から構築して `_render_dep_edge` に渡す
- globe_id が空の場合は `<span>` にフォールバック（リンクなし）

### 修正ファイル

- `globe/runtime/globe_server.py` — `_render_dep_edge()` と `render_dependencies_page()` を修正

---

## Phase 37 — Directive Dependency Map（フェーズ37）

Directive 間の参照関係・共有キーワード・同一Globe・同一Claim/Proposal由来などを、
advisory dependency map として可視化する。
依存関係マップは観察補助表示にすぎない。実行順序・優先順位・責任割当ではない。

> "Dependency map is advisory display only."
> "Dependency is not execution order."
> "Dependency does not rank directives."
> "Dependency does not allocate responsibility."
> "Human review is required before any real-world action."

### 不変条件 / Invariants

| Key | Value |
|-----|-------|
| `dependency_map_is_advisory_display_only` | `True` |
| `dependency_is_not_execution_order` | `True` |
| `dependency_does_not_rank_directives` | `True` |
| `dependency_does_not_allocate_responsibility` | `True` |
| `human_review_is_required_before_any_real_world_action` | `True` |
| `authority` | `none` |

### 検出関係タイプ / Detected Relation Types (7)

| relation_type | 検出方法 | 信頼度 |
|---------------|----------|--------|
| `same_globe` | globe_id 完全一致 | high |
| `shared_keyword` | scope.in_scope 共通項 (非テンプレート) | high/low |
| `shared_claim_source` | source_claim_id 一致 | high |
| `shared_proposal_source` | source_proposal_id 一致 | high |
| `shared_bridge_target` | bridge_target_links + reality_feedback共有 | high/low |
| `shared_resolution_status` | ログ resolution_status 共有 | medium |
| `shared_attention_marker` | objection / rollback_request / vrs 共有 | high/medium |

### Dependency Edge 構造

```json
{
  "edge_id":                          "edge-shared_keyword-002-005",
  "source_directive_id":              "directive-claim-proposal-002",
  "target_directive_id":              "directive-claim-proposal-005",
  "relation_type":                    "shared_keyword",
  "relation_reason":                  "Shared non-template scope item: \"住居アドボカシーの熟議フロー運用\"",
  "shared_terms":                     ["住居アドボカシーの熟議フロー運用"],
  "confidence":                       "high",
  "advisory_only":                    true,
  "not_execution_order":              true,
  "does_not_allocate_responsibility": true
}
```

### 生成結果 (2 directives)

- directive_count: 2
- edge_count: 4
  - shared_keyword (high): 住居アドボカシーの熟議フロー運用 共有
  - shared_keyword (low): プロトコルテンプレートスコープ項目共有
  - shared_bridge_target (low): relief_case_memory / both
  - shared_attention_marker (medium): voluntary_resolution_signal 共有

### CLI

```bash
python3 globe/runtime/directive_dependency_map.py summary
python3 globe/runtime/directive_dependency_map.py save
python3 globe/runtime/directive_dependency_map.py show-directive directive-claim-proposal-002
python3 globe/runtime/directive_dependency_map.py show-globe globe-001
python3 globe/runtime/directive_dependency_map.py show-relation shared_keyword
```

### HTTP ルート

| Path | 説明 |
|------|------|
| `/globe/dependencies` | 全Dependency Map |
| `/globe/dependencies?globe=globe-001` | Globe 絞り込み |
| `/globe/dependencies?directive=<id>` | Directive 絞り込み |
| `/globe/dependencies?relation=shared_keyword` | Relation type 絞り込み |

### 実装ファイル

- `globe/runtime/directive_dependency_map.py` — 関係検出・CLI
- `globe/reports/directive_dependency_map.json` — 生成済み JSON (4 edges)
- `globe/reports/directive_dependency_map.md` — 生成済み Markdown

---

## Phase 36 — Globe Feed / Changelog（フェーズ36）

Globe 全レイヤーの活動を時系列で集約した advisory フィードを提供する。
フィードは閲覧補助表示にすぎない。実行・影響・参加者ランキングの証明ではない。

> "Feed is advisory display only."
> "Feed is not proof of execution."
> "Feed is not proof of impact."
> "Feed does not rank participants."
> "Feed does not allocate resources."
> "Human review is required before any real-world action."

### 不変条件 / Invariants

| Key | Value |
|-----|-------|
| `feed_is_advisory_display_only` | `True` |
| `feed_is_not_proof_of_execution` | `True` |
| `feed_is_not_proof_of_impact` | `True` |
| `feed_does_not_rank_participants` | `True` |
| `feed_does_not_allocate_resources` | `True` |
| `human_review_is_required_before_any_real_world_action` | `True` |
| `authority` | `none` |

### データソース / Data Sources (9 source_types)

| source_type | 件数 | 主キー | タイムスタンプ |
|-------------|------|--------|--------------|
| `proposal` | 5 | proposal_id | created_at |
| `claim` | 2 | claim_id | created_at |
| `directive` | 2 | directive_id | created_at |
| `execution_log` | 8 | log_id | created_at |
| `reality_feedback` | 4 | feedback_id | source_entry_created_at |
| `bridge_target_link` | 4 | link_id | created_at |
| `timeline` | 1 | contribution_timeline (report) | generated_at |
| `activity_heatmap` | 1 | activity_heatmap (report) | generated_at |
| `directive_checklist` | 2 | checklist-{directive_id} | generated_at |

### フィードアイテム構造 / Feed Item Structure

```json
{
  "feed_id":         "feed-proposal-proposal-001",
  "globe_id":        "globe-001",
  "source_type":     "proposal",
  "source_id":       "proposal-001",
  "title":           "Proposal: 難民・避難民支援を...",
  "content_excerpt": "提案：難民・避難民支援を...",
  "created_at":      "2026-05-30 01:00:00",
  "source_path":     "globe/data/proposals.json",
  "url_path":        "/globe/globe-001/proposals/proposal-001",
  "tags":            ["closed", "globe-001"],
  "advisory_only":   true,
  "not_proof_of_execution": true
}
```

### CLI

```bash
python3 globe/runtime/globe_feed.py summary
python3 globe/runtime/globe_feed.py save
python3 globe/runtime/globe_feed.py show-globe globe-001
python3 globe/runtime/globe_feed.py show-type execution_log
```

### HTTP ルート

| Path | 説明 |
|------|------|
| `/globe/feed` | 全フィードアイテム（created_at 降順） |
| `/globe/feed?globe=<globe_id>` | Globe 絞り込み |
| `/globe/feed?type=<source_type>` | source_type 絞り込み |

### 実装ファイル

- `globe/runtime/globe_feed.py` — フィード生成・CLI
- `globe/reports/globe_feed.json` — 生成済み JSON（29 items）
- `globe/reports/globe_feed.md` — 生成済み Markdown

---

## Phase 35 — Directive Execution Checklist（フェーズ35）

Directive の execution_steps を advisory チェックリスト形式でブラウザ表示・CLI 確認する。
チェックリストは実行承認・完了証明・法的効力ではなく、確認補助表示にすぎない。

> "Checklist is advisory display only."
> "Checklist is not proof of execution."
> "Checklist is not proof of completion."
> "Checklist does not approve execution."
> "Human review is required before any real-world action."

### 不変条件 / Invariants

| Key | Value |
|-----|-------|
| `checklist_is_advisory_display_only` | `true` |
| `checklist_is_not_proof_of_execution` | `true` |
| `checklist_is_not_proof_of_completion` | `true` |
| `checklist_does_not_approve_execution` | `true` |
| `human_review_is_required_before_any_real_world_action` | `true` |
| `authority` | `"none"` |

### checklist item フィールド

| フィールド | 内容 |
|-----------|------|
| `checklist_id` | `cl-<directive_id>-<step_id>` |
| `directive_id` / `globe_id` / `step_id` | 参照元 |
| `step_title` / `step_title_en` | ステップ説明 |
| `human_approval_required` | 承認必要フラグ |
| `related_log_count` | 関連ログエントリ数 |
| `has_human_approval` / `human_approval_count` | 承認記録有無 |
| `has_execution_attempt` / `execution_attempt_count` | 実行試行 |
| `has_observation` / `observation_count` | 観察 |
| `has_feedback` / `feedback_count` | フィードバック |
| `has_objection` / `objection_count` | 異議（観察のみ、資格剥奪ではない） |
| `has_rollback_request` / `rollback_request_count` | 差し戻し要求（観察のみ） |
| `voluntary_resolution_signal_count` | Resolution Signal 数 |
| `needs_attention` | objection/rollback 観察フラグ |
| `attribution` | `step_specific` または `directive_summary` |
| `advisory_only` | `true` |
| `not_proof_of_completion` | `true` |

### ログ関連付け方針

| ケース | 方針 |
|--------|------|
| content に step_id が含まれる | step_specific として関連付け |
| step_id が含まれない | directive_summary として全ステップに同じ集計を表示 |

### CLI

```bash
# 全体サマリー
python3 globe/runtime/directive_checklist.py summary

# 保存（JSON + MD）
python3 globe/runtime/directive_checklist.py save

# Directive 別
python3 globe/runtime/directive_checklist.py show-directive directive-claim-proposal-002

# Globe 別
python3 globe/runtime/directive_checklist.py show-globe globe-001
```

### HTTP ルート

| URL | 内容 |
|-----|------|
| `/globe/<id>/directives/<did>/checklist` | Directive ステップ チェックリスト |

### 生成ファイル

| ファイル | 説明 |
|---------|------|
| `globe/reports/directive_checklists.json` | 全チェックリスト (machine-readable) |
| `globe/reports/directive_checklists.md` | 人間可読チェックリスト |

### UI特性

- 実行ボタン・承認ボタン・完了ボタンなし
- チェックボックスなし（disabled/read-only でもなく、そもそも表示しない）
- ⚠️ attention = objection/rollback の観察表示（優先度・資格剥奪ではない）
- Directive 詳細ページに「📋 Checklist (N steps) →」リンクを追加
- attribution: `directive_summary` = step_id 特定エントリなし（全ステップに同じ集計を表示）

---

## Phase 34 — Activity Heatmap（フェーズ34）

Globe 全体のイベントを日付ごとに集計し、カレンダー形式で可視化する advisory UI / CLI。
カウントは記録されたイベント数を反映するだけであり、品質・優先度・インパクトの尺度ではない。

> "Heatmap is advisory display only."
> "Heatmap is not proof of impact."
> "Heatmap does not rank participants."
> "Heatmap does not allocate resources."
> "Human review is required before any real-world action."

### 不変条件 / Invariants

| Key | Value |
|-----|-------|
| `heatmap_is_advisory_display_only` | `true` |
| `heatmap_is_not_proof_of_impact` | `true` |
| `heatmap_does_not_rank_participants` | `true` |
| `heatmap_does_not_allocate_resources` | `true` |
| `human_review_is_required_before_any_real_world_action` | `true` |
| `authority` | `"none"` |

### データソース

| 優先度 | ソース | 内容 |
|--------|--------|------|
| Primary | `globe/reports/contribution_timeline.json` | 全 16 items（Phase 32 で生成） |
| Fallback | `globe/logs/*.jsonl` | JSONL 直接スキャン |

### 集計項目（日別）

| フィールド | 内容 |
|-----------|------|
| `total_events` | 日別総イベント数 |
| `execution_log_count` | 実行ログイベント数 |
| `resolution_signal_count` | 解決シグナル数 |
| `reality_feedback_count` | Reality Feedback 数 |
| `bridge_target_link_count` | Bridge Target Link 数 |
| `objection_count` | 異議申立て数 |
| `rollback_request_count` | ロールバック要求数 |
| `unresolved_count` | 未解決数 |
| `contested_count` | 争議中数 |
| `needs_attention_count` | 注目フラグ数（優先ではなく観察） |
| `by_globe` | Globe 別カウント |
| `by_directive` | Directive 別カウント |
| `event_type_counts` | イベントタイプ別カウント |

### CLI

```bash
# 全体サマリー
python3 globe/runtime/activity_heatmap.py summary

# 保存（JSON + MD）
python3 globe/runtime/activity_heatmap.py save

# 日付フィルタ
python3 globe/runtime/activity_heatmap.py show-date 2026-05-31

# Globe フィルタ
python3 globe/runtime/activity_heatmap.py show-globe globe-001

# Directive フィルタ
python3 globe/runtime/activity_heatmap.py show-directive directive-claim-proposal-002
```

### HTTP ルート

| URL | 内容 |
|-----|------|
| `/globe/activity` | 全体ヒートマップ |
| `/globe/activity?date=2026-05-31` | 日付フィルタ |
| `/globe/activity?globe=globe-001` | Globe フィルタ |

### 生成ファイル

| ファイル | 説明 |
|---------|------|
| `globe/reports/activity_heatmap.json` | ヒートマップデータ (machine-readable) |
| `globe/reports/activity_heatmap.md` | 人間可読ヒートマップレポート |

### UI特性

- 実行ボタン・承認ボタン・配分ボタンなし
- ASCII density bar は視覚的表示のみ（スコアではない）
- ⚠️ attention フラグは objection/rollback/unresolved/contested の観察（優先度ではない）

---

## Phase 29 — Voluntary Resolution Signal（フェーズ29）

参加者が Directive Execution Log に対し、任意で解決状況を自己申告できる `voluntary_resolution_signal` entry type を追加。

> "Resolution signal is self-reported only."
> "Resolution signal is not proof of resolution."
> "Resolution signal does not close support automatically."
> "Resolution signal creates no legal authority."
> "Contested status must always remain recordable."

### 不変条件 / Invariants

| Key | Value |
|-----|-------|
| `resolution_signal_is_self_reported` | `true` |
| `resolution_signal_is_not_proof` | `true` |
| `resolution_signal_does_not_close_support` | `true` |
| `resolution_signal_creates_no_legal_authority` | `true` |
| `contested_always_recordable` | `true` |
| `append_only` | `true` |

### resolution_status 値

| status | 意味 |
|--------|------|
| `resolved` | 参加者が解決済みを自己申告 |
| `partially_resolved` | 部分的な進展を自己申告 |
| `paused` | 一時停止を自己申告 |
| `unresolved` | 未解決として継続観察を表明 |
| `contested` | 現在の状態に異議（常に記録可能） |

### CLI

```bash
# voluntary_resolution_signal を追加する
python3 globe/runtime/directive_execution_log.py \
  append directive-claim-proposal-002 voluntary_resolution_signal human "Masuo Komori" \
  "D.R.A.連携の前提整理はいったん一区切りとする" \
  --resolution-status partially_resolved

# 常に記録可能（人間承認不要）
python3 globe/runtime/directive_execution_log.py \
  append directive-claim-proposal-002 voluntary_resolution_signal human "member-001" \
  "この解決には合意できない" \
  --resolution-status contested
```

### Bridge ルーティング（Phase 27との連携）

| resolution_status | bridge 対象 |
|-------------------|-------------|
| `unresolved` | `care_loop_reopen`（content keyword で escalate） |
| `contested` | `care_loop_reopen` |
| `paused` | `care_loop_reopen` |
| `resolved` | bridge 対象外（summary に保存） |
| `partially_resolved` | bridge 対象外（summary に保存） |

### Execution Log Summary への反映（Phase 26 + 29）

```json
{
  "resolution_signal_count": 2,
  "resolved_count": 0,
  "partially_resolved_count": 1,
  "paused_count": 0,
  "unresolved_count": 1,
  "contested_count": 0,
  "latest_resolution_status": "unresolved"
}
```

### UI統合（Phase 28 + 29）

- `/globe/<id>/logs/<directive_id>` — entry card に `resolution_status` バッジと self-reported 注記
- `/globe/<id>/directives/<directive_id>` — Directive 詳細ページに最新 resolution_status チップ（self-reported 明記）
- Cross-Globe Summary テーブルに `🏳️ Signal` 列追加（self-reported 明記）
- 承認ボタン・解決確定ボタン・支援終了ボタンは一切追加しない

---

## Phase 30 — Cross-Phase Contribution Summary（フェーズ30）

Phase 20/21 の援助パターン・ニーズ予測データと、Phase 25–29 の実行ログデータを横断的に集約し、
勧告的なクロスフェーズ貢献サマリーを生成する。

> "Cross-phase summary is advisory only."
> "Cross-phase summary is not proof of impact."
> "Cross-phase summary does not rank participants."
> "Cross-phase summary does not allocate resources."
> "Human review is required before any real-world action."

### 不変条件 / Invariants

| Key | Value |
|-----|-------|
| `cross_phase_summary_is_advisory_only` | `true` |
| `cross_phase_summary_is_not_proof_of_impact` | `true` |
| `cross_phase_summary_does_not_rank_participants` | `true` |
| `cross_phase_summary_does_not_allocate_resources` | `true` |
| `human_review_is_required_before_any_real_world_action` | `true` |
| `authority` | `"none"` |

### データソース

| フェーズ | ファイル | 役割 |
|---------|---------|------|
| Phase 20 | `bridge/gitsea/aid_patterns/examples/aid-pattern-registry.json` | 援助パターン一覧 |
| Phase 20 | `bridge/gitsea/aid_patterns/examples/pattern-memory.json` | パターン記憶 |
| Phase 20 | `bridge/gitsea/aid_patterns/examples/recurrence-snapshot.json` | 再発スナップショット |
| Phase 21 | `bridge/gitsea/need_forecast/examples/need-forecast-registry.json` | ニーズ予測一覧 |
| Phase 21 | `bridge/gitsea/need_forecast/examples/forecast-memory.json` | 予測記憶 |
| Phase 21 | `bridge/gitsea/need_forecast/examples/preparedness-hint-snapshot.json` | 準備ヒント |
| Phase 25–29 | `globe/reports/execution_log_summary.json` | 実行ログサマリー |
| Phase 27 | `globe/reports/reality_feedback_bridge.json` | ブリッジ記録 |
| Phase 27b | `globe/reports/bridge_target_links.json` | リンク候補 |

### 集計指標（14指標）

| 指標 | 説明 |
|------|------|
| `aid_pattern_count` | Phase 20 援助パターン数 |
| `pattern_memory_count` | パターン記憶数 |
| `recurrence_count` | 再発スナップショット数 |
| `need_forecast_count` | Phase 21 ニーズ予測数 |
| `forecast_memory_count` | 予測記憶数 |
| `preparedness_hint_count` | 準備ヒント数 |
| `execution_log_entry_count` | Phase 25–29 実行ログエントリ数 |
| `human_approval_count` | 人間承認数 |
| `objection_count` | 異議数 |
| `voluntary_resolution_signal_count` | Phase 29 解決シグナル数（自己申告） |
| `unresolved_signal_count` | 未解決シグナル数 |
| `bridge_record_count` | Phase 27 ブリッジ記録数 |
| `bridge_target_link_count` | Phase 27b リンク候補数 |
| `high_confidence_link_count` | 高信頼度リンク候補数 |

### CLI

```bash
# サマリー表示
python3 globe/runtime/cross_phase_contribution_summary.py summary

# レポート保存 (JSON + Markdown)
python3 globe/runtime/cross_phase_contribution_summary.py save

# Globe別サマリー
python3 globe/runtime/cross_phase_contribution_summary.py show-globe globe-001

# セクション別表示
python3 globe/runtime/cross_phase_contribution_summary.py show-section aid
python3 globe/runtime/cross_phase_contribution_summary.py show-section forecast
python3 globe/runtime/cross_phase_contribution_summary.py show-section logs
python3 globe/runtime/cross_phase_contribution_summary.py show-section bridge
python3 globe/runtime/cross_phase_contribution_summary.py show-section links
python3 globe/runtime/cross_phase_contribution_summary.py show-section resolution
```

### Advisory Interpretation（勧告的解釈）

以下の4観点でパターンを列挙。スコア・ランキング・割り当ては行わない。

| 観点 | 条件 |
|------|------|
| `where_attention_is_increasing` | log entries ≥ 2 の Globe |
| `where_unresolved_signals_remain` | unresolved/contested ≥ 1 の Globe |
| `where_objections_exist` | objections ≥ 1 の Globe |
| `where_bridge_candidates_require_review` | bridge records ≥ 1 の Globe |

### 生成ファイル

| ファイル | 説明 |
|---------|------|
| `globe/reports/cross_phase_contribution_summary.json` | 機械読み取り可能な全サマリー |
| `globe/reports/cross_phase_contribution_summary.md` | 人間可読サマリー |

### UI統合（Phase 30）

- `/globe` — Globe 一覧ページに Cross-Phase Summary パネルを追加（advisory only）
- `/globe/<globe_id>` — Globe 詳細ページに per-globe Cross-Phase Summary パネルを追加
- 実行ボタン・割り当てボタンは一切追加しない
- ランキング・スコアは表示しない

---

## Phase 28 — Directive UI Routes（フェーズ28）

Phase 24〜26 で生成された Directive / Execution Log / Summary を globe_server.py 上で直接閲覧できる UI ルートを追加。

> "UI display is advisory only."
> "UI display is not proof of execution."
> "UI display creates no legal authority."
> "UI display does not approve execution."
> "UI display must preserve objections and rollback requests."

### 追加ルート / New Routes

| URL | 内容 |
|-----|------|
| `/globe/<globe_id>/directives` | Directive 一覧（directive_id, title, status, steps, log counts） |
| `/globe/<globe_id>/directives/<directive_id>` | Directive 詳細（objective, invariants, execution steps, scope, log summary） |
| `/globe/<globe_id>/logs/<directive_id>` | Execution Log 全件表示（時系列・append-only・異議保存） |

### Directive 詳細ページ表示項目

- directive_id / title / status
- objective / non_authority_clause
- 不変条件テーブル（authority, execution_allowed, directive_creates_legal_authority 等）
- execution_steps（step_id, description, required_contributions, human_approval_required）
- required_evidence
- scope（in_scope / out_of_scope）
- Execution Log サマリ（total entries, approvals, objections, rollbacks）+ 全件表示リンク

### Execution Log 詳細ページ表示項目

- total entries / approvals / objections / rollback_requests（スタットグリッド）
- 全エントリ時系列表示（entry_type, actor_type, actor_name, content, created_at）
- 各エントリの `legal_authority_created: false` / `log_is_proof_of_execution: false` を表示
- 異議（objection）・差し戻し（rollback_request）は常に表示・削除不可

### Globe 詳細ページ追加項目

- Directive 数 / Execution Log エントリ数 / approval 数
- "Directive 一覧" リンク（`/globe/<globe_id>/directives`）

---

## UIルート / UI Routes

サーバー起動: `python3 globe/runtime/globe_server.py`

| URL | 内容 |
|-----|------|
| `/globe` | Globe 一覧 |
| `/globe/<globe_id>` | Globe 詳細（founding_statement, proposals, directives count, GITSEA link） |
| `/globe/<globe_id>/proposals` | Proposal 一覧 |
| `/globe/<globe_id>/proposals/<proposal_id>` | Proposal 詳細（熟議ログ・次の行動案） |
| `/globe/<globe_id>/directives` | Directive 一覧 &nbsp;[Phase 28] |
| `/globe/<globe_id>/directives/<directive_id>` | Directive 詳細 &nbsp;[Phase 28] |
| `/globe/<globe_id>/logs/<directive_id>` | Execution Log 全件表示 &nbsp;[Phase 28] |

## ランタイム / Runtime

```bash
# Globe の一覧
python3 globe/runtime/globe_registry.py list

# Globe の詳細
python3 globe/runtime/globe_registry.py view globe-001

# 新しい Globe を作成
python3 globe/runtime/globe_registry.py create

# Proposal の一覧
python3 globe/runtime/proposal_manager.py list

# Proposal のステータスを変更
python3 globe/runtime/proposal_manager.py advance proposal-001 voting

# 熟議ログの一覧
python3 globe/runtime/deliberation_log.py list proposal-001

# 熟議ログの全文表示
python3 globe/runtime/deliberation_log.py summary proposal-001

# 熟議エントリを追加
python3 globe/runtime/deliberation_log.py append proposal-001

# Proposal → Claim 変換（accepted のみ）
python3 globe/runtime/proposal_to_claim.py convert proposal-002

# Globe 内の accepted Proposal を一括変換
python3 globe/runtime/proposal_to_claim.py convert-globe globe-001

# 変換済み Claim の一覧
python3 globe/runtime/proposal_to_claim.py list

# Claim → Directive 変換（claim_draft のみ）
python3 globe/runtime/claim_to_directive.py convert claim-proposal-002

# Globe 内の claim_draft Claim を一括変換
python3 globe/runtime/claim_to_directive.py convert-globe globe-001

# 変換済み Directive の一覧
python3 globe/runtime/claim_to_directive.py list

# Execution Log にエントリを追加
python3 globe/runtime/directive_execution_log.py \
  append directive-claim-proposal-002 human_approval human "Masuo Komori" "承認を記録"

# Execution Log の全エントリを表示
python3 globe/runtime/directive_execution_log.py list directive-claim-proposal-002

# Execution Log のサマリ
python3 globe/runtime/directive_execution_log.py summary directive-claim-proposal-002

# Execution Log を Markdown にエクスポート
python3 globe/runtime/directive_execution_log.py export-md directive-claim-proposal-002

# UIサーバーを起動
python3 globe/runtime/globe_server.py
```

## データ永続化 / Data Persistence

```
globe/
├── data/
│   ├── globes.json        — Globe records
│   ├── proposals.json     — Proposal records
│   └── deliberations.json — Deliberation log (append-only)
├── claims/                — Generated Claim files (Phase 23)
│   ├── claim-proposal-NNN.json
│   └── claim-proposal-NNN.md
├── directives/            — Generated Directive files (Phase 24)
│   ├── directive-claim-proposal-NNN.json
│   └── directive-claim-proposal-NNN.md
├── logs/                  — Directive Execution Logs (Phase 25 · append-only JSONL)
│   ├── directive-claim-proposal-NNN.jsonl
│   └── directive-claim-proposal-NNN.md
├── runtime/
│   ├── globe_registry.py
│   ├── proposal_manager.py
│   ├── deliberation_log.py
│   ├── globe_server.py
│   ├── proposal_to_claim.py           — Phase 23: Proposal → Claim conversion
│   ├── claim_to_directive.py          — Phase 24: Claim → Directive conversion
│   └── directive_execution_log.py     — Phase 25: Directive Execution Log
└── spec/
    └── GLOBE_SPEC.md      — this file
```

## 設計思想 / Design Philosophy

- **AIは統治者ではない。** AIはメディエーター・記録者・提案者だ。
  AI is not a governor. AI is a mediator, recorder, and proposer.

- **多数決だけで決めない。** 少数意見は削除されない。
  Decisions are not made by majority rule alone. Minority opinions are never deleted.

- **履歴はappend-only。** 変更は新しいエントリとして記録される。
  History is append-only. Changes are recorded as new entries.

- **GITSEA的な管理。** 提案・ルール・実行計画はGit的に管理できる。
  GITSEA-style management. Proposals, rules, and execution plans can be managed like Git.

- **参加は任意。** Globeへの参加も、提案への賛否も、熟議への参加も、すべて任意。
  Participation is voluntary. Joining a Globe, supporting/opposing proposals, and participating in deliberation are all voluntary.

---

## Phase 38 — Globe Member Profile View（フェーズ38）

フェーズ38では、Globe内メンバーの活動履歴を advisory display として可視化する
**Globe Member Profile View** を追加しました。
メンバープロフィールは観察補助表示にすぎません。身元確認ではありません。評判スコアではありません。
権限を創出しません。参加者をランク付けしません。

### 不変条件

```python
PROFILE_INVARIANTS = {
    "member_profile_is_advisory_display_only": True,
    "member_profile_is_not_identity_verification": True,
    "member_profile_is_not_reputation_score": True,
    "member_profile_creates_no_authority": True,
    "member_profile_does_not_rank_participants": True,
    "human_review_is_required_before_any_real_world_action": True,
    "authority": "none",
}
```

### Protocol Phrases

```
Member profile is advisory display only.
Member profile is not identity verification.
Member profile is not reputation score.
Member profile creates no authority.
Member profile does not rank participants.
Human review is required before any real-world action.
```

### データソース（6種）

1. `proposals.json` — 提案者 (actor_type=human)
2. `deliberations.json` — 発言者・speaker_type
3. `logs/*.jsonl` — 実行ログ actor_name / actor_type / entry_type 別カウント
4. `reality_feedback_bridge.json` — フィードバック記録
5. `contribution_timeline.json` — 補完（globe_ids / actor_types / timestamps のみ）
6. `globe_feed.json` — 補完（残余 actor 捕捉）

### メンバー集計

- 12名 (human: 8, ai: 2, system: 2)
- globe-001: 8名 / globe-002: 1名 / globe-003: 4名

### カウントフィールド

| フィールド | 説明 |
|---|---|
| proposal_count | 提案回数 |
| deliberation_count | 熟議発言回数 |
| execution_log_count | 実行ログエントリ数 |
| human_approval_count | 承認エントリ数 |
| observation_count | 観察エントリ数 |
| feedback_count | フィードバック記録数 |
| objection_count | 異議申立数 |
| rollback_request_count | ロールバック申請数 |
| voluntary_resolution_signal_count | 自発的解決シグナル数 |
| execution_attempt_count | 実行試行数 |

### HTTP Routes

```
/globe/members                    → メンバー一覧
/globe/members?globe=<globe_id>   → Globe でフィルター
/globe/members/<member_id>        → メンバー詳細
```

### CLIコマンド

```bash
python3 globe/runtime/member_profile.py summary
python3 globe/runtime/member_profile.py save
python3 globe/runtime/member_profile.py show-member member-masuo-komori
python3 globe/runtime/member_profile.py show-globe globe-001
```

### 生成ファイル

- `globe/runtime/member_profile.py` — プロフィール構築・CLI
- `globe/reports/member_profiles.json` — 生成済み JSON (12 members)
- `globe/reports/member_profiles.md` — 生成済み Markdown

---

## Phase 39 — Globe Member Activity Heatmap（フェーズ39）

フェーズ39では、Member ごとの活動を日付 × Globe × activity type の heatmap として
表示する **Globe Member Activity Heatmap** を追加しました。
これは貢献の観察補助であり、評価・ランキング・信用スコア・権限付与ではありません。

### 不変条件

```python
HEATMAP_INVARIANTS = {
    "member_activity_heatmap_is_advisory_display_only": True,
    "member_activity_heatmap_is_not_identity_verification": True,
    "member_activity_heatmap_is_not_reputation_score": True,
    "member_activity_heatmap_does_not_rank_members": True,
    "member_activity_heatmap_creates_no_authority": True,
    "human_review_is_required_before_any_real_world_action": True,
    "authority": "none",
}
```

### Protocol Phrases

```
Member activity heatmap is advisory display only.
Member activity heatmap is not identity verification.
Member activity heatmap is not reputation score.
Member activity heatmap does not rank members.
Member activity heatmap creates no authority.
Human review is required before any real-world action.
```

### Activity Types（12種）

| activity_type | ソース |
|---|---|
| proposal | proposals.json |
| deliberation | deliberations.json |
| human_approval | logs/*.jsonl |
| observation | logs/*.jsonl |
| objection | logs/*.jsonl |
| feedback | logs/*.jsonl |
| rollback_request | logs/*.jsonl |
| voluntary_resolution_signal | logs/*.jsonl |
| execution_attempt | logs/*.jsonl |
| execution_log | logs/*.jsonl (不明 entry_type のフォールバック) |
| timeline_event | contribution_timeline.json (bridge_target_link 等) |
| feed_item | globe_feed.json (未利用 — actor 情報なし) |

### 集計項目

- `total_events` — 全イベント数
- `by_activity_type` — activity type 別カウント
- `by_globe` — Globe 別カウント
- `by_date` — 日付別 activity type カウント
- `latest_activity_at` — 最終活動日時
- `objection_count` — 異議申立数（advisory only）
- `unresolved_signal_count` — 未解決シグナル数
- `contested_signal_count` — 他メンバー異議ありシグナル数

### HTTP Routes

```
/globe/member-activity                → 全メンバーヒートマップ
/globe/member-activity?member=<id>   → 特定メンバーのヒートマップ
/globe/member-activity?globe=<id>    → Globe でフィルター
/globe/member-activity?date=<date>   → 日付でフィルター
```

### CLIコマンド

```bash
python3 globe/runtime/member_activity_heatmap.py summary
python3 globe/runtime/member_activity_heatmap.py save
python3 globe/runtime/member_activity_heatmap.py show-member member-masuo-komori
python3 globe/runtime/member_activity_heatmap.py show-globe globe-001
python3 globe/runtime/member_activity_heatmap.py show-date 2026-05-31
```

### 生成ファイル

- `globe/runtime/member_activity_heatmap.py` — ヒートマップ構築・CLI (12 members, 25 events, 2 dates)
- `globe/reports/member_activity_heatmap.json` — 生成済み JSON
- `globe/reports/member_activity_heatmap.md` — 生成済み Markdown

---

## Phase 40 — Globe Member × Directive Participation Map（フェーズ40）

フェーズ40では、Member と Directive の関係を参加マップとして可視化する
**Globe Member × Directive Participation Map** を追加しました。
これは参加の観察補助であり、評価・ランキング・信用スコア・権限付与・責任割当ではありません。

### 不変条件

```python
MAP_INVARIANTS = {
    "member_directive_map_is_advisory_display_only": True,
    "member_directive_map_is_not_identity_verification": True,
    "member_directive_map_is_not_reputation_score": True,
    "member_directive_map_does_not_rank_members": True,
    "member_directive_map_does_not_allocate_responsibility": True,
    "human_review_is_required_before_any_real_world_action": True,
    "authority": "none",
}
```

### Protocol Phrases

```
Member-directive map is advisory display only.
Member-directive map is not identity verification.
Member-directive map is not reputation score.
Member-directive map does not rank members.
Member-directive map does not allocate responsibility.
Human review is required before any real-world action.
```

### 関係タイプ（11種）

| relation_type | ソース |
|---|---|
| proposer_related | proposals.json → directive source_proposal_id |
| deliberation_related | deliberations.json → proposal → directive |
| human_approval | logs/*.jsonl |
| observation | logs/*.jsonl |
| objection | logs/*.jsonl |
| feedback | logs/*.jsonl |
| rollback_request | logs/*.jsonl |
| voluntary_resolution_signal | logs/*.jsonl |
| execution_attempt | logs/*.jsonl |
| timeline_related | contribution_timeline.json (bridge_target_link) |
| feedback_bridge_related | reality_feedback_bridge.json |

### map entry フィールド

- `map_id`, `member_id`, `display_name`, `actor_types`
- `directive_id`, `directive_title`, `globe_id`
- `relation_types`, `event_count`, `latest_activity_at`
- `has_human_approval`, `has_objection`, `has_unresolved_signal`, `has_contested_signal`
- invariant flags

### HTTP Routes

```
/globe/member-directives                          → 全エントリ
/globe/member-directives?member=<id>             → メンバーでフィルター
/globe/member-directives?directive=<directive_id> → Directive でフィルター
/globe/member-directives?globe=<globe_id>         → Globe でフィルター
```

### CLIコマンド

```bash
python3 globe/runtime/member_directive_map.py summary
python3 globe/runtime/member_directive_map.py save
python3 globe/runtime/member_directive_map.py show-member member-masuo-komori
python3 globe/runtime/member_directive_map.py show-directive directive-claim-proposal-002
python3 globe/runtime/member_directive_map.py show-globe globe-001
```

### 集計結果

- 8 entries, 8 unique members, 2 directives, 2 globes
- attention entries: 3 (objection, unresolved_signal, contested_signal)

### 生成ファイル

- `globe/runtime/member_directive_map.py` — マップ構築・CLI
- `globe/reports/member_directive_map.json` — 生成済み JSON (8 entries)
- `globe/reports/member_directive_map.md` — 生成済み Markdown

## Phase 41 — Globe Attention-Required Dashboard（フェーズ41）

フェーズ41では、objection / rollback_request / unresolved_signal /
partially_resolved_signal / contested_signal / high_confidence_link /
needs_attention を一覧表示する **Attention-Required Dashboard** を追加しました。
これは注意喚起の観察補助であり、優先度スコア・義務付与・責任割当ではありません。

### 不変条件

```python
DASHBOARD_INVARIANTS = {
    "attention_dashboard_is_advisory_display_only": True,
    "attention_item_is_not_priority_score": True,
    "attention_item_creates_no_obligation": True,
    "attention_item_does_not_assign_responsibility": True,
    "human_review_is_required_before_any_real_world_action": True,
    "authority": "none",
}
```

### attention_type 一覧

| attention_type | 説明 |
|---|---|
| `objection` | メンバーによる異議 |
| `rollback_request` | ロールバック要求 |
| `unresolved_signal` | 未解決の VRS |
| `partially_resolved_signal` | 部分解決・保留中の VRS |
| `contested_signal` | VRS と objection が同一 directive に共存 |
| `high_confidence_link` | 高信頼度の bridge target link |
| `needs_attention` | その他要注意フラグ |

### データソース

1. `logs/*.jsonl` — objection / rollback_request / VRS エントリ
2. `bridge_target_links.json` — confidence=high の link candidate
3. `member_directive_map.json` — has_contested_signal=True エントリ
4. `contribution_timeline.json` — needs_attention=True の未収録 item

### attention item 構造

```python
{
    "attention_id": "attn-objection-002-log-003",
    "source_type": "log",
    "source_id": "log-003",
    "globe_id": "globe-001",
    "directive_id": "directive-claim-proposal-002",
    "member_id": "member-founding-member-003",
    "attention_type": "objection",
    "title": "⚠️ Objection recorded — founding-member-003",
    "content_excerpt": "D.R.A.との連携前にコミュニティ内の合意確認が必要と考える",
    "reason": "Objection by member — human review may be required before proceeding",
    "created_at": "2026-05-30T23:12:26",
    "source_path": "globe/logs/directive-claim-proposal-002.jsonl",
    "advisory_only": True,
    "not_priority_score": True,
    "creates_no_obligation": True,
    "does_not_assign_responsibility": True,
}
```

### CLI コマンド

```bash
python3 globe/runtime/attention_dashboard.py summary
python3 globe/runtime/attention_dashboard.py save
python3 globe/runtime/attention_dashboard.py show-globe globe-001
python3 globe/runtime/attention_dashboard.py show-directive directive-claim-proposal-002
python3 globe/runtime/attention_dashboard.py show-member member-masuo-komori
python3 globe/runtime/attention_dashboard.py show-type objection
```

### HTTP エンドポイント

| URL | 説明 |
|---|---|
| `/globe/attention` | 全 attention item |
| `/globe/attention?globe=globe-001` | globe でフィルタ |
| `/globe/attention?directive=directive-claim-proposal-002` | directive でフィルタ |
| `/globe/attention?member=member-masuo-komori` | member でフィルタ |
| `/globe/attention?type=objection` | attention_type でフィルタ |

### プロトコル句

- "Attention dashboard is advisory display only."
- "Attention item is not priority score."
- "Attention item creates no obligation."
- "Attention item does not assign responsibility."
- "Human review is required before any real-world action."

### 集計結果

- 7 items total (objection × 1, partially_resolved_signal × 1, unresolved_signal × 1,
  contested_signal × 1, high_confidence_link × 2, needs_attention × 1)
- ah_attention_events: 5 (from activity_heatmap)
- mah_members_with_attn: 3 members

### 生成ファイル

- `globe/runtime/attention_dashboard.py` — ダッシュボード構築・CLI
- `globe/reports/attention_dashboard.json` — 生成済み JSON (7 items)
- `globe/reports/attention_dashboard.md` — 生成済み Markdown

## Phase 42 — Globe Directive Resolution Timeline（フェーズ42）

フェーズ42では、Directive ごとの voluntary_resolution_signal / objection /
rollback_request / contested_signal の推移を時系列で表示する
**Resolution Timeline** を追加しました。
これは解決証明ではなく、自己申告・異議・未解決シグナルの推移を観察するための advisory view です。

### 不変条件

```python
TIMELINE_INVARIANTS = {
    "resolution_timeline_is_advisory_display_only": True,
    "resolution_timeline_is_not_proof_of_resolution": True,
    "resolution_timeline_does_not_close_support": True,
    "resolution_timeline_creates_no_authority": True,
    "human_review_is_required_before_any_real_world_action": True,
    "authority": "none",
}
```

### event_type 一覧

| event_type | 説明 |
|---|---|
|  | 自己申告型解決シグナル（proof ではない） |
|  | 異議記録 |
|  | ロールバック要求 |
|  | VRS と objection が同一 directive に共存 |
|  | 未解決として明示されたシグナル |
|  | 部分解決・保留中のシグナル |

### timeline item 構造

```python
{
    "timeline_id": "tl-rt-log-003-002",
    "directive_id": "directive-claim-proposal-002",
    "globe_id": "globe-001",
    "member_id": "member-founding-member-003",
    "actor_name": "founding-member-003",
    "source_type": "execution_log",
    "source_id": "log-003",
    "event_type": "objection",
    "resolution_status": "",
    "content_excerpt": "D.R.A.との連携前にコミュニティ内の合意確認が必要と考える",
    "created_at": "2026-05-30T23:12:26.340959+00:00",
    "advisory_only": True,
    "not_proof_of_resolution": True,
    "does_not_close_support": True,
    "creates_no_authority": True,
}
```

### CLI コマンド

```bash
python3 globe/runtime/resolution_timeline.py summary
python3 globe/runtime/resolution_timeline.py save
python3 globe/runtime/resolution_timeline.py show-directive directive-claim-proposal-002
python3 globe/runtime/resolution_timeline.py show-globe globe-001
python3 globe/runtime/resolution_timeline.py show-status unresolved
```

### HTTP エンドポイント

| URL | 説明 |
|---|---|
|  | 全 timeline items |
|  | directive でフィルタ |
|  | globe でフィルタ |
|  | resolution_status でフィルタ |

### プロトコル句

- "Resolution timeline is advisory display only."
- "Resolution timeline is not proof of resolution."
- "Resolution timeline does not close support."
- "Resolution timeline creates no authority."
- "Human review is required before any real-world action."

### 集計結果

- 4 items (voluntary_resolution_signal × 2, objection × 1, contested_signal × 1)
- 2 directives (directive-002: partially_resolved / directive-005: unresolved)

### 生成ファイル

- `globe/runtime/resolution_timeline.py` — タイムライン構築・CLI
- `globe/reports/resolution_timeline.json` — 生成済み JSON (4 items)
- `globe/reports/resolution_timeline.md` — 生成済み Markdown

## Phase 43 — Cross-Directive Signal Aggregation（フェーズ43）

フェーズ43では、resolution_status / objection / rollback / attention signal を
Globe・Directive・Member・Status 単位で横断集計する
**Cross-Directive Signal Aggregation** を追加しました。
これは状態観察の補助であり、解決証明・優先順位・責任割当ではありません。

### 不変条件

```python
AGG_INVARIANTS = {
    "signal_aggregation_is_advisory_display_only": True,
    "signal_aggregation_is_not_proof_of_resolution": True,
    "signal_aggregation_does_not_assign_responsibility": True,
    "signal_aggregation_creates_no_authority": True,
    "human_review_is_required_before_any_real_world_action": True,
    "authority": "none",
}
```

### 集計ディメンション

| dimension | 説明 |
|---|---|
| `globe` | globe_id ごとに全 directive/member を横断集計 |
| `directive` | directive_id ごとに全 member のシグナルを集計 |
| `member` | member_id ごとに全 directive のシグナルを横断集計 |
| `status` | resolution_status / event_type ごとに集計 |

### 集計項目

```python
{
    "agg_id": "agg-globe-globe-001",
    "dimension": "globe",
    "dimension_value": "globe-001",
    "total_signal_count": 3,
    "voluntary_resolution_signal_count": 1,
    "unresolved_count": 0,
    "contested_count": 1,
    "partially_resolved_count": 1,
    "resolved_count": 0,
    "paused_count": 0,
    "objection_count": 1,
    "rollback_request_count": 0,
    "latest_signal_at": "2026-05-31T04:27:29.210356+00:00",
    "latest_resolution_status": "partially_resolved",
    "affected_directive_ids": ["directive-claim-proposal-002"],
    "affected_member_ids": ["member-founding-member-003", "member-masuo-komori"],
    "affected_globe_ids": ["globe-001"],
    "advisory_only": True,
    "not_proof_of_resolution": True,
    "does_not_assign_responsibility": True,
    "creates_no_authority": True,
}
```

### CLI コマンド

```bash
python3 globe/runtime/cross_directive_signal_aggregation.py summary
python3 globe/runtime/cross_directive_signal_aggregation.py save
python3 globe/runtime/cross_directive_signal_aggregation.py show-globe globe-001
python3 globe/runtime/cross_directive_signal_aggregation.py show-member member-masuo-komori
python3 globe/runtime/cross_directive_signal_aggregation.py show-directive directive-claim-proposal-002
python3 globe/runtime/cross_directive_signal_aggregation.py show-status unresolved
```

### HTTP エンドポイント

| URL | 説明 |
|---|---|
| `/globe/signals` | 全集計 (by_globe / by_directive / by_member / by_status) |
| `/globe/signals?globe=globe-001` | globe でフィルタ |
| `/globe/signals?member=member-masuo-komori` | member でフィルタ |
| `/globe/signals?directive=directive-claim-proposal-002` | directive でフィルタ |
| `/globe/signals?status=unresolved` | resolution_status でフィルタ |

### プロトコル句

- "Signal aggregation is advisory display only."
- "Signal aggregation is not proof of resolution."
- "Signal aggregation does not assign responsibility."
- "Signal aggregation creates no authority."
- "Human review is required before any real-world action."

### 集計結果

- total_signals: 4
- by_globe: 2 records (globe-001: partially_resolved / globe-003: unresolved)
- by_directive: 2 records
- by_member: 3 records (masuo-komori × 2, founding-member-003 × 1, jammy-house-steward × 1)
- by_status: 4 records (contested, objection, partially_resolved, unresolved)

### 生成ファイル

- `globe/runtime/cross_directive_signal_aggregation.py` — 集計構築・CLI
- `globe/reports/cross_directive_signal_aggregation.json` — 生成済み JSON
- `globe/reports/cross_directive_signal_aggregation.md` — 生成済み Markdown

## Phase 44 — Globe Governance Summary（フェーズ44）

フェーズ44では、各 Globe の governance 状態を
proposals / claims / directives / logs / attention / signals / members / dependencies
の観点から横断集計する **Globe Governance Summary** を追加しました。
これは governance の観察補助であり、格付け・ランキング・配分・権限付与ではありません。

### 不変条件

```python
GOV_INVARIANTS = {
    "governance_summary_is_advisory_display_only": True,
    "governance_summary_is_not_governance_score": True,
    "governance_summary_does_not_rank_globes": True,
    "governance_summary_creates_no_authority": True,
    "governance_summary_does_not_allocate_resources": True,
    "human_review_is_required_before_any_real_world_action": True,
    "authority": "none",
}
```

### 集計項目（Globe ごと）

| 項目 | 説明 |
|---|---|
| `proposal_count` | Globe 内の提案数 |
| `accepted_proposal_count` | 採択済み提案数 |
| `claim_count` | Claim 変換済み数 |
| `directive_count` | Directive 変換済み数 |
| `execution_log_count` | 実行ログ総エントリ数 |
| `human_approval_count` | 人間承認記録数 |
| `observation_count` | 観察記録数 |
| `objection_count` | 異議記録数 |
| `rollback_request_count` | ロールバック要求数 |
| `voluntary_resolution_signal_count` | 自発的解決シグナル数 |
| `unresolved_signal_count` | 未解決シグナル数 |
| `contested_signal_count` | contested シグナル数 |
| `attention_item_count` | attention dashboard 掲載数 |
| `member_count` | 観察メンバー数 |
| `dependency_edge_count` | directive 依存関係エッジ数 |
| `governance_observation_notes` | advisory 観察メモ |

### CLI コマンド

```bash
python3 globe/runtime/governance_summary.py summary
python3 globe/runtime/governance_summary.py save
python3 globe/runtime/governance_summary.py show-globe globe-001
python3 globe/runtime/governance_summary.py show-section attention
```

### HTTP エンドポイント

| URL | 説明 |
|---|---|
| `/globe/governance` | 全 Globe governance summary |
| `/globe/governance?globe=globe-001` | globe でフィルタ |
| `/globe/governance?section=attention` | section でフィルタ |

### セクション一覧

`proposals` / `directives` / `logs` / `attention` / `signals` / `members` / `dependencies`

### プロトコル句

- "Governance summary is advisory display only."
- "Governance summary is not governance score."
- "Governance summary does not rank globes."
- "Governance summary creates no authority."
- "Governance summary does not allocate resources."
- "Human review is required before any real-world action."

### 集計結果

| globe_id | proposals | directives | logs | attention | members | dep_edges |
|---|---|---|---|---|---|---|
| globe-001 | 2 (1 accepted) | 1 | 6 | 5 | 8 | 4 |
| globe-002 | 1 (0 accepted) | 0 | 0 | 0 | 1 | 0 |
| globe-003 | 2 (1 accepted) | 1 | 2 | 2 | 4 | 4 |

### 生成ファイル

- `globe/runtime/governance_summary.py` — governance 集計・CLI
- `globe/reports/governance_summary.json` — 生成済み JSON (3 globes)
- `globe/reports/governance_summary.md` — 生成済み Markdown
