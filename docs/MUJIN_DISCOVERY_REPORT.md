# Mujin Discovery Report — Dan-Go ↔ Mujin 接続境界の確定

> 調査レポート / 設計のみ。**実装は含まない。**
> 対象リポジトリ: `dango-mujin`
> 調査ブランチ: `feature/mujin-platform-mvp`（main から分岐）
> 作成日: 2026-06-12

このレポートは、既存 Dan-Go 実装と将来の Mujin Platform を接続する **境界（インターフェース）** を確定するための事前調査である。Mujin が「どこから読み」「どこへ書き戻し」「何を上位概念とすべきか」を、既存実装を壊さない前提で特定する。

---

## 0. エグゼクティブサマリ

- **Relief Case Memory は実在する。** Phase 18 の正式レイヤとして spec・runtime・example が揃う。識別子は `relief_case_id`、形式は JSON（registry）。
- **Reality Feedback は実在するが、3つの異なる実装・スキーマに分裂している。** これが最大の接続リスク。
- **Dan-Go の「決定の連鎖」は一本のパイプラインとして存在する:**
  `proposal → claim → directive → execution log(.jsonl) → reality feedback → reality_feedback_bridge(Phase 27) → relief_case_memory(Phase 18) / care_loop_reopen(Phase 19)`
- Mujin にとっての **Decision Log 相当は Directive + Execution Log の組** が最も近い（後述）。
- **Mujin が最初に読むべきソースは Directive（実行意図）と Execution Log（append-only 事実列）。**
- **Mujin が書き戻すべき先は Reality Feedback。** ただし「どの Reality Feedback 実装か」を先に決める必要がある。
- **Contribution は既に上位概念として存在する**（11種の `contribution_type`）。SupportOffer はその下位の「賛同イベント」に過ぎない。Mujin の将来カテゴリの大半を既存モデルがカバーするが、いくつか欠落タイプがある。

> **Dan-Go 全体に貫かれている不変条件**:
> `authority: none` / `execution_allowed: false` / `moves_money: false` / `advisory: true` / `append_only: true` / `contestable: true`。
> Mujin はこの不変条件を**継承・尊重**しなければならない。Mujin が金銭・物資・実行を扱うとしても、Dan-Go レイヤへの書き戻しは「観察記録（advisory）」を超えてはならない。

---

## 1. Relief Case Memory

### 実体の有無
**実在する。** Phase 18 として正式に実装されている。

### 保持ファイル
| 種別 | パス |
|---|---|
| 仕様 | `bridge/gitsea/relief/RELIEF_CASE_MEMORY_SPEC.md` |
| 原則 | `bridge/gitsea/relief/RELIEF_NOT_PROOF.md` |
| Runtime | `bridge/gitsea/relief/runtime/relief_case_registry.py` |
| Runtime | `bridge/gitsea/relief/runtime/relief_outcome_snapshot.py` |
| Runtime | `bridge/gitsea/relief/runtime/relief_memory_report.py` |
| Example | `bridge/gitsea/relief/examples/relief-case-registry.json` |
| Example | `bridge/gitsea/relief/examples/relief-outcome-snapshot.json` |
| Example | `bridge/gitsea/relief/examples/relief-memory-report.json` |

> ※ spec が言及する `care_memory_builder.py` は spec の表に記載があるが、`relief/runtime/` 直下では未確認（→ 不明点 U-3）。

### 形式
- **JSON**（registry / snapshot / report の3種。`relief-case-registry.json` が中心）。
- JSONL は使われていない。Markdown は spec のみ。

### `case_id` 相当の識別子
- **`relief_case_id`**（例: `"relief-case-001"`）が一次キー。
- 関連キー: `route_id`（Phase 17 ルートへの参照）, `commons_id`（コモンズ参照）, `snapshot_id`（outcome snapshot）, `care_memory_id`（care memory）。
- レコードは **append-only / reopenable / contestable**。

### Mujin にとっての意味
Relief Case Memory は「ルート提案後に観察された結果のケア記憶」であり、**Mujin の成果観察（feedback sink の最終到達点の一つ）に対応する**。ただし spec が強く `relief_is_proof: false` / `care_memory_controls: false` / `ranks_suffering: false` を宣言しており、Mujin はここに **証明・順位付け・義務化を持ち込んではならない**。

---

## 2. Reality Feedback

### 実体
**実在するが、3つの異なる実装が併存し、スキーマが一致していない。** これは接続上の最重要論点。

| # | 実装 | 書き込み先 | スキーマの要点 |
|---|---|---|---|
| A | `runtime/reality_feedback.py`（ルート直下、"Mujin Protocol" を名乗る） | `sutable/feedback/<feedback_id>.json`（**1ケース1ファイル**） | `feedback_id`, `claim_id`, `author_id`, `status` ∈ {executed, partial, failed, pending}, `conditions_realized`, `conditions_still_missing` |
| B | `bridge/runtime/reality_feedback_append.py` → `bridge/sutable/reality_feedback.jsonl`（**append-only JSONL**） | 1行1イベント | `event_type: "reality_feedback"`, `claim_id`, `result` ∈ {partial_success, …}, `conditions_met`, `conditions_unmet`, `event_hash` |
| C | `bridge/ogi/runtime/reality_feedback_mapper.py` / `bridge/ogi/examples/reality-feedback.json` | OGI レイヤ | `result`, `conditions_met`, `conditions_unmet`, `speaker`, `requires_human_review`, `dignity_violation`, `next_steps` |

### スキーマ不一致（重大）
- **状態フィールド名が3者で違う**: A=`status`、B/C=`result`、かつ値の語彙も違う（A: `executed/partial/failed/pending` vs B/C: `partial_success` 等）。
- **条件フィールド名が違う**: A=`conditions_realized`/`conditions_still_missing` vs B/C=`conditions_met`/`conditions_unmet`。
- A の保存先 `sutable/feedback/` は **リポジトリ内に存在しない**（トップレベル `sutable/` ディレクトリ自体が無い。実在するのは `bridge/sutable/`）。→ **A は事実上、現行データと切断された孤立実装**（→ 問題点 P-1）。

### 保存場所（実際にデータがあるのは）
- `bridge/sutable/reality_feedback.jsonl`（実データ・append-only・ハッシュ付き）← **B が一次ソース**。

### Phase 27 との関係
- **Phase 27 = Reality Feedback Bridge。** `globe/runtime/reality_feedback_bridge.py` が feedback / execution log エントリを走査し、`relief_case_memory`（Phase 18）/ `care_loop_reopen`（Phase 19）への **接続候補（suggested_bridge_target）を advisory として提案**する。
- 出力: `globe/reports/reality_feedback_bridge.json`（`phase: 27`）。
- 不変条件: `reality_feedback_is_advisory_only: true`, `feedback_bridge_is_not_proof_of_resolution: true`, `feedback_bridge_creates_no_legal_authority: true`, `human_review_is_required_before_any_real_world_action: true`, `feedback_bridge_does_not_reopen_case_automatically: true`。
- 補助: `bridge/runtime/reality_feedback_append.py`（追記）, `globe/runtime/bridge_target_linker.py`（Phase 27b、ターゲット連結）。

> つまり Reality Feedback は「**Mujin が現実の結果を書き戻す入口**」であり、Phase 27 Bridge が「その結果を Relief Case Memory 等へ橋渡しする advisory ルータ」である。

---

## 3. Decision Log 相当の評価

候補6つを実体から評価した。**結論を先に示す:**

> **Mujin の "Decision Log" = `Directive`（決定の意図）+ `Execution Log`（append-only な事実列）の組。**
> Directive 単体は「何を決めたか」、Execution Log は「決定後に何が起きたか」を担う。両者で初めて監査可能な決定ログになる。

| 候補 | 実体 / パス | 形式・キー | Decision Log 適合度 | 評価 |
|---|---|---|---|---|
| **Claim** | `globe/claims/claim-*.json` ; runtime `globe/runtime/proposal_to_claim.py` | JSON, `claim_id` | △ | 「決定」ではなく **決定の素材（提案の確定形）**。`status: claim_draft`。決定前段。 |
| **Directive** | `globe/directives/directive-*.json` ; runtime `claim_to_directive.py` | JSON, `directive_id`, `source_claim_id`, `scope.in_scope/out_of_scope`, `human_approval_required: true` | ◎ | **決定の意図そのもの。** 何を実行範囲とし、何を範囲外とするかを明示。Mujin の「やること宣言」に対応。 |
| **Execution Log** | `globe/logs/directive-*.jsonl` ; runtime `directive_execution_log.py`, `execution_log_summary.py` | **JSONL append-only**, `log_id`, `directive_id`, `entry_type` | ◎ | **決定後の append-only 事実列。** `entry_type` ∈ {human_approval, observation, objection, voluntary_resolution_signal}。監査ログの本体。 |
| **Reality Feedback Bridge** | `globe/runtime/reality_feedback_bridge.py`（Phase 27） | JSON report | ○（橋渡し） | 決定ログ「そのもの」ではなく、**ログ→ケア記憶のルータ**。Mujin の出力先選定に使う。 |
| **Resolution Signal** | **独立ファイルではない。** Execution Log 内の `entry_type: "voluntary_resolution_signal"`（例: log-006）。集計は `globe/runtime/resolution_timeline.py` → `globe/reports/resolution_timeline.*` | JSONL 内エントリ, `resolution_status` ∈ {partially_resolved, …} | ○（部分） | **「当事者が自己申告で一区切りとした」シグナル。** `resolution_signal_is_not_proof: true`, `does_not_close_support: true`。決定の「終了」ではなく「自己申告の区切り」。 |
| **Evidence Record** | `bridge/runtime/prerequisite_evidence_bundle.py` ; `bridge/examples/prerequisite-evidence-bundle.json` | JSON, `condition`, `prerequisite_threshold`, `evidence_bundle.claims[]` | ✗（別物） | これは「**前提条件の根拠束**」（plan_contest 由来の証拠集約）であり、決定ログではない。前提充足の裏付け用途。 |

### Decision Log のキー設計（Mujin が依存すべき結合キー）
```
proposal_id → claim_id → directive_id → (log_id 群: directive_id でグルーピング)
                                      → feedback (claim_id で結合)
                                      → bridge record (source_directive_id / source_log_id で結合)
```
- **`directive_id` が決定単位の主キー。** Execution Log は `directive_id` でグルーピングされた JSONL。
- Reality Feedback は `claim_id` 結合、Bridge は `source_directive_id` + `source_log_id` 結合。
  → **claim_id ⇄ directive_id の対応表が結合の要**（`directive.source_claim_id` で辿れる）。

---

## 4. Mujin Export Source（Mujin が最初に読むべきデータ）

Mujin が「現状の意思決定・コモンズ状態」を取り込むために読むべきソースを**優先順位付き**で示す。

| 優先 | ソース | パス | 理由 |
|---|---|---|---|
| **P1** | **Directive** | `globe/directives/directive-*.json` | 決定の意図と scope（in/out）。Mujin が「何が合意され、何が範囲外か」を知る一次情報。 |
| **P1** | **Execution Log** | `globe/logs/directive-*.jsonl` | 決定後の append-only 事実列。承認・異議・解決シグナルの全履歴。Directive と対で読む。 |
| **P2** | **Claim** | `globe/claims/claim-*.json` | Directive の背景・`missing_conditions`・熟議要約。Contribution マッチングに必要。 |
| **P2** | **Relief Case Memory** | `bridge/gitsea/relief/examples/relief-case-registry.json` | 既存のケア結果。Mujin が「過去に何が観察されたか」を引き継ぐ。 |
| **P3** | **Reality Feedback (実データ)** | `bridge/sutable/reality_feedback.jsonl`（実装 B） | 既存の現実フィードバック。Mujin の初期状態同期に使用（A ではなく B を読むこと）。 |
| **P3** | **Resource / Capacity Memory** | `bridge/gitsea/resource_memory/examples/*.json`（Phase 51）, Phase 50 capacity | 物資・能力の観察在庫。Mujin の「物資」カテゴリの読み取り元候補。 |
| **P4** | **Contribution History** | `bridge/sutable/contributions.jsonl`, `bridge/gitsea/credit/examples/contribution-history.json` | 既存の貢献記録。Mujin Contribution の継続性に使用。 |

> **最小構成（MVP の最初の読み取り）**: P1 の **Directive + Execution Log** のみで「決定の現状」を再構成できる。ここから始めるのが最短。

---

## 5. Mujin Feedback Sink（Mujin が書き戻すべき場所）

### 結論
**Mujin は実行結果を Reality Feedback（実装 B: `bridge/sutable/reality_feedback.jsonl`）に append する。** その後の Relief Case Memory / Care Loop への反映は **Phase 27 Bridge（advisory）に委ねる** —— Mujin が直接 Relief Case Memory を書き換えてはならない。

### Dan-Go を壊さない書き戻し方針
1. **append-only を厳守。** 既存 `.jsonl` は追記のみ。行の書き換え・削除は禁止（`append_only: true` 不変条件）。
2. **B のスキーマに合わせる。** `event_type: "reality_feedback"`, `claim_id`, `result`, `conditions_met`, `conditions_unmet`, `event_hash`, `timestamp`。新フィールドを足す場合は**任意フィールドの追加に留め、既存フィールドの意味を変えない**。
3. **advisory 不変条件を必ず付与。** `authority: "none"`, `execution_allowed: false`, `moves_money: false`, `not_proof_of_resolution`, `requires_human_review: true`。Mujin が金銭・物資を動かしても、Dan-Go ログ上は「観察記録」を超えない。
4. **Relief Case Memory / Care Loop へは直接書かない。** Phase 27 Bridge の `suggested_bridge_target` を経由させ、**human review を挟む**（`human_review_is_required_before_any_real_world_action: true`）。
5. **新規ソースは独立ファイルに分離。** Mujin 固有の出力は `bridge/mujin/` 配下の新ファイル（例: `bridge/mujin/registry/`, `bridge/mujin/feedback/`）に置き、既存 GitSea / Globe ファイルを上書きしない。これが「壊さない」最大の保証。
6. **孤立実装 A を sink にしない。** `runtime/reality_feedback.py` は存在しない `sutable/feedback/` を指しており、現行データと切断されている（→ P-1）。Mujin の sink は **B に統一**すべき。

### 推奨フロー（書き戻し）
```
Mujin 実行結果
  └─(append)→ bridge/sutable/reality_feedback.jsonl   [実装B, advisory, hashed]
        └─(scan)→ reality_feedback_bridge.py (Phase 27)
              └─ suggested_bridge_target: relief_case_memory / care_loop_reopen
                    └─(human review)→ relief_case_registry / care_loop_reopen
```

---

## 6. Contribution Model 評価（SupportOffer vs Contribution）

### 結論
**Contribution は既に上位概念として実装済みである。** 新規に「上位概念を作る」必要はない。むしろ **SupportOffer は Contribution の下位（賛同イベント）として整理されるべき**。

### 現状の2概念
| 概念 | 実体 | 性質 |
|---|---|---|
| **Contribution** | `CONTRIBUTION_SPEC.md`（v0.1.0-draft）, `runtime/contribution_router.py`, `bridge/sutable/contributions.jsonl` | **資源・労力・能力の提供**。11種の `contribution_type`、`status` ∈ {offered, committed, delivered, verified, disputed}、`addresses_condition` で missing_condition に結合。 |
| **SupportOffer 相当** | `bridge/examples/plan-support-event.json`（`event_type: "plan_supported"`）, claim 内 `possible_contributions` | **賛同/承認イベント**（「この plan を支持する」）。資源を伴わない。 |

→ **SupportOffer ⊂ Contribution。** SupportOffer は「`reputation`/`care` 型の貢献の軽量版（資源無しの賛同）」に過ぎず、Contribution の方が広い。**上位概念として Contribution が必要か？ → 既に存在し、上位である。** 統一すべきは「概念の新設」ではなく「SupportOffer を Contribution 語彙に正規化すること」。

### Mujin 将来カテゴリのカバレッジ評価
既存11種 `contribution_type`: `code, compute, legal, translation, housing, funding, social_reach, reputation, care, knowledge, coordination`。

| Mujin 将来カテゴリ | 既存タイプで表現可能か | 評価 |
|---|---|---|
| 資金 | `funding` | ✅ 既存（ただし spec は「投資ではない」と明記。金銭は advisory 記録のみ） |
| 物資 | ⚠️ 近いのは `housing` のみ。**汎用 `supplies`/`goods` 型が無い** | ❌ **欠落** → 新タイプ要検討 |
| 翻訳 | `translation` | ✅ 既存 |
| AI教育 | `knowledge`（教育内容）/ `compute`（AI実行） | ⚠️ 表現可能だが **`education`/`training` の独立タイプが無い** |
| メンタリング | `care` + `knowledge` | ⚠️ 表現可能だが **`mentoring` の独立タイプが無い** |
| 求人紹介 | `social_reach` / `coordination` | ⚠️ 表現可能だが **`job_referral`/`opportunity` の独立タイプが無い** |

### 推奨
- **Contribution を Mujin の統一上位概念として採用**し、SupportOffer をその一形態に正規化する。
- 不足タイプ（`supplies`, `education`, `mentoring`, `job_referral` 等）は **`contribution_type` 語彙の追加**で対応可能 —— ただし MAPPING_TABLE.md の警告「fixed type vocabulary を保つ／earning-back・debt を足さない」に従い、**スコアリング・債務化を伴わない純粋な記録タイプ**として追加すること。

---

## 7. 問題点・矛盾・不明点・MVP前決定事項（一覧）

### 7-1. 問題点（P）
| ID | 問題 | 影響 |
|---|---|---|
| **P-1** | `runtime/reality_feedback.py`（実装A）が存在しない `sutable/feedback/` を参照しており、現行データ（`bridge/sutable/reality_feedback.jsonl`）と切断。 | Mujin が誤って A を sink に選ぶと、データが分裂・消失する。**sink は B に統一すべき。** |
| **P-2** | Reality Feedback のスキーマが A/B/C で三分裂（`status` vs `result`、`conditions_realized` vs `conditions_met` 等）。 | Mujin の読み書きで変換層が必須。未整理だと結合不能。 |
| **P-3** | `bridge/mujin/` の設計メモ（MAPPING_TABLE, OPEN_QUESTIONS 等）は `feature/phase-51-resource-memory` のコミット 956c92f にのみ存在し、**main・現 `feature/mujin-platform-mvp` には無い**。 | MVP ブランチに設計の前提資料が無い。マージ/チェリーピックの判断が必要。 |
| **P-4** | spec 記載の `care_memory_builder.py` が `relief/runtime/` 直下で未確認。 | Relief レイヤの care_memory 生成経路が不明（spec とコードの乖離可能性）。 |

### 7-2. 矛盾（C）
| ID | 矛盾 |
|---|---|
| **C-1** | ルート直下 `runtime/`（A）は自身を "Dan-Go **Mujin Protocol**" と名乗るが、実体は孤立実装。`bridge/` 側（B）が実データの真のソース。**「Mujin」の名が既に2箇所で別物を指している。** |
| **C-2** | Reality Feedback の状態語彙が「実行ベース（executed/failed）」（A）と「成否ベース（partial_success）」（B/C）で哲学が不一致。Dan-Go の `execution_allowed: false` 原則と「executed」状態名が緊張関係。 |
| **C-3** | Contribution に `funding` 型がある一方、全レイヤで `moves_money: false`。資金は「記録される advisory」止まりで「動かせない」—— Mujin が実際に資金を扱う場合、この境界の明文化が必要。 |

### 7-3. 不明点（U）
| ID | 不明点 |
|---|---|
| **U-1** | Mujin Commons の最初の対象コモンズ（OPEN_QUESTIONS Q1: jammy-house / housing-007 / refugee_* / D.R.A. translator pool のどれか）。 |
| **U-2** | Commons manifest のファイル形式・配置（Q2: `commons.toml` か `commons/<id>.toml` か計算生成か）。 |
| **U-3** | `care_memory_builder.py` の実在と care_memory 生成フロー（→ P-4）。 |
| **U-4** | 擬名 ID を Dan-Go contributor と共有するか分離するか（Q3）。default は commons-local だが未確定。 |
| **U-5** | Mujin の `event_hash` 生成方式が B と互換か（チェーン継続性のため要確認）。 |

### 7-4. Mujin MVP 前に決めるべき事項（D）
> **これらが決まるまで実装に進まないこと。**

1. **D-1 — Reality Feedback の正典スキーマを1つに確定する。** A/B/C のどれを基準にするか。**推奨: B（`bridge/sutable/reality_feedback.jsonl`）を正典とし、A は廃止または B へのアダプタ化、変換層を1箇所に集約。**
2. **D-2 — Mujin の feedback sink を「append-only / advisory / 既存ファイル非破壊」と明文契約する。** §5 の6方針を MVP の受け入れ基準にする。
3. **D-3 — Decision Log の結合キー契約を固定する。** `directive_id` を決定主キーとし、`claim_id ⇄ directive_id` 対応を Mujin 側で保持する設計を確定。
4. **D-4 — Contribution を統一上位概念として採用し、SupportOffer を正規化、不足タイプ（supplies/education/mentoring/job_referral）の扱いを決定。** スコア・債務を持ち込まない制約付き。
5. **D-5 — `bridge/mujin/` 設計メモの所在を解決する（P-3）。** phase-51 から MVP ブランチへ取り込むか、main 経由で正規化するかを決める。
6. **D-6 — 最初の対象コモンズ（U-1）と manifest 形式（U-2）を、当該コモンズの参加者と協議して決める。** OPEN_QUESTIONS の「技術的に楽な方を選ばない」原則を守る。
7. **D-7 — 資金・物資など実世界資源を Mujin が扱う際の「Dan-Go レイヤ上は advisory 記録に留める」境界を文章化する（C-3）。** Mujin が現実で動かしても、Dan-Go への書き戻しは観察記録を超えない。

---

## 付録 A: 接続境界マップ（テキスト）

```
                          ┌─────────────────────────── Dan-Go (既存・advisory only) ───────────────────────────┐
  proposal ──▶ claim ──▶ directive ──▶ execution_log(.jsonl) ──▶ reality_feedback(B,.jsonl) ──▶ Phase27 Bridge
  (globe/data) (globe/    (globe/        (globe/logs/             (bridge/sutable/                (globe/runtime/
               claims)    directives)    directive-*.jsonl)        reality_feedback.jsonl)         reality_feedback_bridge.py)
                                                                                                        │ suggested_bridge_target
                                                                                          ┌─────────────┴─────────────┐
                                                                                  relief_case_memory          care_loop_reopen
                                                                                  (Phase18, JSON)             (Phase19)
                          └────────────────────────────────────────────────────────────────────────────────────────┘
                                  ▲ READ (Export Source: P1 directive+log)        ▲ WRITE (Feedback Sink: append to B)
                                  │                                               │
                          ┌───────┴───────────────────────────────────────────────┴───────┐
                          │                        Mujin Platform (将来)                     │
                          │   Contribution(上位概念) ⊃ SupportOffer / 資金・物資・翻訳・教育… │
                          └───────────────────────────────────────────────────────────────┘
```

## 付録 B: 主要ファイル索引
- Relief: `bridge/gitsea/relief/`
- Reality Feedback: `runtime/reality_feedback.py`(A, 孤立) / `bridge/runtime/reality_feedback_append.py` + `bridge/sutable/reality_feedback.jsonl`(B, 正典候補) / `bridge/ogi/`(C)
- Phase 27 Bridge: `globe/runtime/reality_feedback_bridge.py`, `globe/runtime/bridge_target_linker.py`
- Decision pipeline: `globe/runtime/proposal_to_claim.py`, `claim_to_directive.py`, `directive_execution_log.py`, `resolution_timeline.py`
- Contribution: `CONTRIBUTION_SPEC.md`, `runtime/contribution_router.py`, `bridge/sutable/contributions.jsonl`
- Resource/Capacity (物資): `bridge/gitsea/resource_memory/`(Phase 51), Phase 50 capacity
- Mujin 設計メモ: `bridge/mujin/`（※現状 phase-51 ブランチのみ — P-3）

---

*本レポートは調査・設計のみ。コード実装は含まない。Mujin Platform の実装は、§7-4 の決定事項（D-1〜D-7）が確定するまで開始しない。*
