# ADR-004 — Contribution Model

- **Status:** Accepted
- **Date:** 2026-06-12
- **Context source:** [`docs/MUJIN_DISCOVERY_REPORT.md`](../MUJIN_DISCOVERY_REPORT.md) §6, §7 (D-4)
- **Related:** ADR-002 (Boundary)

---

## Context

Discovery Report §6 で以下が確定した:
- **Contribution は既に上位概念として実装済み**（`CONTRIBUTION_SPEC.md` v0.1.0-draft, `runtime/contribution_router.py`, `bridge/sutable/contributions.jsonl`）。
  - 11種の `contribution_type`: `code, compute, legal, translation, housing, funding, social_reach, reputation, care, knowledge, coordination`。
  - `status` ∈ {offered, committed, delivered, verified, disputed}、`addresses_condition` で `missing_condition` に結合。
- **SupportOffer 相当**（`event_type: "plan_supported"`）は資源を伴わない「賛同イベント」で、Contribution の下位に位置する。

したがって「Mujin のために上位概念を新設する必要があるか？」への答えは **No** —— 既に存在し、既に上位である。

---

## Decision

**Contribution を上位概念とし、Mujin は新しい Contribution システムを作らず、既存 Dan-Go Contribution モデルを活用する。**

1. **Contribution = 上位概念。** 資源・労力・能力の提供を表す統一概念。
2. **SupportOffer は Contribution の一種。** `plan_supported` 等の賛同イベントは Contribution の軽量形態（`reputation` / `care` 系の資源無し版）として正規化する。SupportOffer を独立した別系統として扱わない。
3. **Mujin は新規 Contribution システムを構築しない。** 既存の `contribution_type` 語彙・`status` 遷移・`addresses_condition` 結合・`contribution_router.py` を再利用する。
4. **金銭の境界を継承。** `funding` 型は存在するが、Dan-Go レイヤ上は `moves_money: false`・advisory 記録に留まる（ADR-002 / Discovery Report C-3, D-7）。Mujin が現実で資金を扱っても、Contribution 記録は観察記録を超えない。
5. **将来の語彙拡張は記録タイプの追加のみ。** 必要に応じ以下を `contribution_type` に追加してよい:
   - `education`（AI教育・研修）
   - `mentoring`（メンタリング）
   - `supplies`（物資 — 現状 `housing` しか近い型が無い欠落を埋める）
   - `job_referral`（求人紹介）
   - 拡張は **MAPPING_TABLE.md の制約に従う**: fixed type vocabulary を尊重し、**スコアリング・tier・earning-back・debt（債務化）を一切持ち込まない**純粋な記録タイプとして追加する。

---

## Rationale

- 既存モデルが Mujin の将来カテゴリ（資金・翻訳・AI教育・メンタリング・物資・求人紹介）の大半を既にカバーする（Discovery Report §6 カバレッジ表）。
- 上位概念を二重に作ると SupportOffer / Contribution の意味が分裂し、結合・監査が困難になる。
- 既存 `addresses_condition` 結合により、Contribution は Claim の `missing_conditions` に直接紐づく —— Mujin の実行が「どの欠落条件を埋めたか」を Reality Feedback と一貫して追跡できる（ADR-001 / ADR-002 と整合）。

---

## Consequences

- **正:** Mujin は Contribution の車輪を再発明せず、既存ルータ・語彙・ログを活用できる。
- **正:** SupportOffer と Contribution が単一モデルに統合され、監査が単純化される。
- **負/要対応:** SupportOffer（`plan_supported`）を Contribution 語彙へ正規化する写像が必要 —— ただし**本 ADR では実装しない**。
- **負/要対応:** 欠落タイプ（`supplies` 等）の追加は将来課題。追加時に「スコア・債務を持ち込まない」制約のレビューが必須。

---

## Non-goals

- Contribution 語彙の拡張実装（education / mentoring / supplies / job_referral）。
- SupportOffer → Contribution 正規化の実装。
- スコアリング・ランキング・債務システム（これらは**明示的に禁止**）。
