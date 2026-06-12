# ADR-001 — Canonical Reality Feedback

- **Status:** Accepted
- **Date:** 2026-06-12
- **Context source:** [`docs/MUJIN_DISCOVERY_REPORT.md`](../MUJIN_DISCOVERY_REPORT.md) §2, §5, §7 (P-1, P-2, D-1, D-2)
- **Related:** ADR-002 (Boundary), ADR-003 (Relief Case Promotion)

---

## Context

Discovery Report §2 で、Reality Feedback には **3つの異なる実装・スキーマが併存**していることが判明した。

| # | 実装 | 書き込み先 | 状態フィールド | 条件フィールド |
|---|---|---|---|---|
| A | `runtime/reality_feedback.py`（"Mujin Protocol" を名乗る） | `sutable/feedback/<id>.json`（**実在しないディレクトリ**） | `status` ∈ {executed, partial, failed, pending} | `conditions_realized` / `conditions_still_missing` |
| B | `bridge/runtime/reality_feedback_append.py` → `bridge/sutable/reality_feedback.jsonl` | append-only JSONL（**実データ存在**, hash付き） | `result` ∈ {partial_success, …} | `conditions_met` / `conditions_unmet` |
| C | `bridge/ogi/runtime/reality_feedback_mapper.py` | OGI レイヤ | `result` | `conditions_met` / `conditions_unmet` |

問題（Discovery Report P-1, P-2）:
- 実装 A は存在しない `sutable/feedback/` を指しており、現行データから**切断された孤立実装**。
- 3者でスキーマ（状態語彙・条件フィールド名）が一致せず、結合不能。

決定しなければ、Mujin が誤って A を sink に選び、データが分裂・消失するリスクがある。

---

## Decision

**Mujin 統合における正典 Reality Feedback を `bridge/sutable/reality_feedback.jsonl`（実装 B）とする。**

1. **正典は B のみ。** Mujin は Reality Feedback の読み書きを `bridge/sutable/reality_feedback.jsonl` に対して行う。
2. **B のスキーマを基準語彙とする:** `event_type: "reality_feedback"`, `claim_id`, `result`, `conditions_met`, `conditions_unmet`, `event_hash`, `timestamp`。
3. **append-only を厳守。** 既存行の書き換え・削除は禁止。Mujin は追記のみ行う。
4. **advisory 不変条件を必ず付与:** `authority: "none"`, `execution_allowed: false`, `moves_money: false`, `not_proof_of_resolution: true`, `requires_human_review: true`。
5. **Mujin は Execution Log（`globe/logs/directive-*.jsonl`）へ直接書き込まない。** Execution Log は Dan-Go 側の決定記録であり、Mujin は読み取り専用（ADR-002 と整合）。
6. **実装 A は正典から除外。** 将来 A を廃止、または B へのアダプタ化する（本 ADR では廃止判断はせず「正典ではない」とのみ確定）。
7. **実装 C（OGI）は正典ではない。** OGI レイヤ内部の用途に限定し、Mujin 統合の sink としては使わない。

---

## Rationale

- **実データが存在する** — B のみが現行の実フィードバックを保持している。
- **append-only** — Dan-Go の `append_only: true` 不変条件に一致する。
- **hash 付き** — `event_hash` によりチェーンの改竄検知が可能。
- **Dan-Go 非破壊原則に一致** — B への追記は既存ファイルを破壊しない。
- A は参照先ディレクトリが存在せず、現行データと切断されているため、正典たり得ない。

---

## Consequences

- **正:** Mujin の読み書き先が単一化され、変換層を1箇所に集約できる。
- **正:** Dan-Go の決定記録（Execution Log）と Mujin の結果記録（Reality Feedback）が物理的に分離され、疎結合が保たれる。
- **負/要対応:** 実装 A/C との語彙差を吸収するアダプタが将来必要（Discovery Report D-1）。本 ADR ではスキーマ統一の実装は行わず、**正典の指定のみ**を確定する。
- **負/要対応:** B への書き戻し時の `event_hash` 生成方式が既存と互換である必要がある（Discovery Report U-5）。実装時に検証する。

---

## Non-goals（本 ADR がやらないこと）

- スキーマ変換層の実装。
- 実装 A の廃止作業。
- Reality Feedback の新フィールド追加。
