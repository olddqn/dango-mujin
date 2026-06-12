# ADR-003 — Relief Case Promotion

- **Status:** Accepted
- **Date:** 2026-06-12
- **Context source:** [`docs/MUJIN_DISCOVERY_REPORT.md`](../MUJIN_DISCOVERY_REPORT.md) §1, §2 (Phase 27), §5
- **Related:** ADR-001 (Canonical Reality Feedback), ADR-002 (Boundary)

---

## Context

Discovery Report §1 で、Relief Case Memory（Phase 18）が実在することが確認された。
- 識別子: `relief_case_id`、形式: JSON、append-only / reopenable / contestable。
- spec は強く宣言する: `relief_is_proof: false`, `outcome_is_judgment: false`, `care_memory_controls: false`, `ranks_suffering: false`, `certifies_rescue: false`。

Relief Case Memory は「Phase 17 ルート提案後に**観察された**ケア記憶」であり、Dan-Go の advisory レイヤである。

リスク: Mujin が**すべての Relief Case を無条件に Mujin Case として取り込む**と、
- 観察記録（advisory）が実行対象（actionable case）に**意味的に格上げ**され、
- `relief_is_proof: false` / `care_memory_controls: false` の不変条件が崩れ、
- 当事者の同意なく vulnerability が Mujin 上で可視化・追跡される（Discovery Report の refugee 記録に関する懸念）。

---

## Decision

**Relief Case Memory は Mujin Case ではない。Relief Case のうち、明示的な昇格（promotion）プロセスを経たものだけが Mujin Case になる。**

### 昇格ゲート（順序付き、すべて必須）

```
relief_case (advisory observation)
   │
   ├─ [1] verified        … 観察結果が独立に確認された
   │
   ├─ [2] consent_obtained … 当事者の明示的同意が得られた
   │
   └─ [3] promoted        … 昇格が人間レビューで承認された
            │
            ▼
        Mujin Case
```

1. **verified** — Relief Case の観察が独立に確認されている（単なる `observed` ではなく検証済み）。
2. **consent_obtained** — 当該ケースの**当事者の明示的同意**が記録されている。同意なき昇格は禁止（特に refugee / displacement ケースで厳格）。
3. **promoted** — 上記2条件を満たした上で、**human review による昇格承認**が記録されている（Phase 27 Bridge の `human_review_is_required` 原則に整合）。

### 不変則
- **すべての Relief Case が Mujin に昇格するわけではない。** 昇格は例外的・明示的・可逆的。
- 昇格は Relief Case Memory を**書き換えない**。Relief Case はそのまま append-only で残り、Mujin Case は `bridge/mujin/` 配下の**別レコード**として `relief_case_id` を参照する（ADR-002 の非破壊原則）。
- 昇格レコードは contestable / reopenable を維持し、`relief_is_proof: false` を継承する。Mujin Case 化は「証明」でも「順位付け」でもない。
- 昇格経路は **Phase 27 Reality Feedback Bridge の `suggested_bridge_target` + human review** を通す。Mujin が Relief Case Memory を直接昇格判定しない。

---

## Rationale

- Relief Case Memory の advisory / non-judgment / non-control の不変条件を、Mujin 統合後も保つため。
- 同意ゲート（consent_obtained）により、vulnerability の無断可視化を構造的に防ぐ。
- 検証ゲート（verified）により、未確認の観察が実行対象に昇格するのを防ぐ。
- 「すべてが昇格しない」ことを明文化し、Mujin が Relief Case を一括取り込みする設計を排除する。

---

## Consequences

- **正:** Relief Case Memory の倫理的不変条件が Mujin でも保たれる。
- **正:** 当事者同意が昇格の必須条件になり、refugee / displacement ケースの保護が構造化される。
- **負/要対応:** 昇格状態（verified / consent_obtained / promoted）を記録するレコード形式が必要 —— ただし**本 ADR では形式の実装はしない**。Mujin Case レコードのスキーマ設計は MVP 実装フェーズの課題。
- **負/要対応:** `consent_obtained` の取得・記録方法（誰が・どう同意を確認するか）は運用設計が必要（Discovery Report の OPEN_QUESTIONS と連動）。

---

## Non-goals

- Mujin Case レコードのスキーマ実装。
- 昇格 UI / 同意取得フローの実装。
- 既存 Relief Case Memory の変更。
