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
