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

## UIルート / UI Routes

サーバー起動: `python3 globe/runtime/globe_server.py`

| URL | 内容 |
|-----|------|
| `/globe` | Globe 一覧 |
| `/globe/<globe_id>` | Globe 詳細（founding_statement, proposals, GITSEA link） |
| `/globe/<globe_id>/proposals` | Proposal 一覧 |
| `/globe/<globe_id>/proposals/<proposal_id>` | Proposal 詳細（熟議ログ・次の行動案） |

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
├── runtime/
│   ├── globe_registry.py
│   ├── proposal_manager.py
│   ├── deliberation_log.py
│   ├── globe_server.py
│   └── proposal_to_claim.py  — Phase 23: Proposal → Claim conversion
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
