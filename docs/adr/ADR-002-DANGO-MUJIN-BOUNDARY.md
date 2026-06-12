# ADR-002 — Dan-Go / Mujin Boundary

- **Status:** Accepted
- **Date:** 2026-06-12
- **Context source:** [`docs/MUJIN_DISCOVERY_REPORT.md`](../MUJIN_DISCOVERY_REPORT.md) §3, §4, §5, §7 (D-2, D-3, D-7)
- **Related:** ADR-001 (Canonical Reality Feedback), ADR-003, ADR-004

---

## Context

Dan-Go と Mujin は思想的に同一プロジェクトの一部だが、実装上は別レイヤである。境界を明文化しないと、Mujin が Dan-Go の決定記録を直接書き換えたり、Dan-Go が実行責任を負ったりして、両者の不変条件（`authority: none` / `execution_allowed: false` / `moves_money: false` / `advisory: true`）が崩れる。

Discovery Report §3 で、決定情報のパイプラインが確定している:

```
proposal → claim → directive → execution_log(.jsonl) → reality_feedback → Phase27 Bridge → relief_case_memory / care_loop_reopen
```

---

## Decision

**Dan-Go と Mujin を「思想的に不可分・実装的に疎結合」として定義し、両者の責務と接続方向を固定する。**

### 役割定義
- **Dan-Go = 協力形成プロトコル（cooperation-formation protocol）。** 提案→クレーム→ディレクティブ→実行ログという**決定（Decision）情報を形成・公開**する。
- **Mujin = 共助実行プラットフォーム（mutual-aid execution platform）。** Dan-Go が公開した決定を読み、現実世界での共助を実行し、その**結果（Reality Feedback）を返す**。

### 思想 vs 実装
- **思想的には不可分。** 同一の価値体系（非強制・尊厳・advisory・append-only）を共有する。Mujin は Dan-Go の不変条件を継承する。
- **実装的には疎結合。** 両者は共有データファイルのみを介して接続し、コード依存・同期呼び出しを持たない。

### 接続方向（一方向ずつ）
1. **Dan-Go → Mujin（READ）:** Dan-Go は Decision 情報を公開する。Mujin はそれを**読み取り専用**で取り込む。
   - 一次ソース（Discovery Report §4 P1）: `globe/directives/directive-*.json`（決定意図）+ `globe/logs/directive-*.jsonl`（append-only 事実列）。
   - 決定主キー: **`directive_id`**。結合は `directive.source_claim_id` で `claim_id ⇄ directive_id` を辿る（Discovery Report D-3）。
2. **Mujin → Dan-Go（WRITE）:** Mujin は Reality Feedback を返す。
   - sink: `bridge/sutable/reality_feedback.jsonl`（ADR-001 で確定）。append-only・advisory のみ。

### 境界の不変則
- Mujin は **Execution Log / Claim / Directive を書き換えない**（読み取り専用）。
- Mujin が現実で資金・物資を動かしても、**Dan-Go レイヤへの書き戻しは observation（advisory 記録）を超えない**（Discovery Report D-7, C-3）。
- Relief Case Memory / Care Loop への反映は Mujin が直接書かず、**Phase 27 Bridge + human review を経由**する（ADR-003 と整合）。
- Mujin 固有の出力・状態は `bridge/mujin/` 配下の独立ファイルに置き、既存 GitSea / Globe ファイルを破壊しない。

---

## Rationale

- 疎結合により、Dan-Go の決定形成と Mujin の実行が互いの障害・変更で壊れない。
- 一方向の READ / WRITE 分離により、責任境界（誰が決定を持ち、誰が実行を持つか）が明確になる。
- 共有ファイルのみを介すことで、Dan-Go の append-only / advisory 不変条件が Mujin 側からも保たれる。

---

## Consequences

- **正:** Dan-Go と Mujin を独立に開発・テストできる。
- **正:** 監査可能性が高い（決定は Dan-Go、結果は Mujin、両者とも append-only）。
- **負/要対応:** 共有ファイルのスキーマ契約（ADR-001 の B スキーマ、`directive_id` 結合キー）を双方が厳守する必要がある。破ると疎結合が崩れる。
- **負/要対応:** Mujin が現実世界で行う実行（資金・物資）の責任は Mujin プラットフォーム側にあり、Dan-Go はその証明・認可を行わない —— この責任分界を Mujin の利用規約・UI で明示する必要がある（将来）。

---

## Non-goals

- Mujin UI / 実行ロジックの設計。
- Dan-Go と Mujin の間の同期 API / RPC（疎結合方針に反するため作らない）。
