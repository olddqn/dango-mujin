# Phase F-23: Findability Execution Boundary Review (Post-Audit Correction)

- **Status:** 実行境界監査。**v2: 公開が既に部分的に起きた前提での訂正版。** コード/データ/生成/登録/公開なし。文書のみ。
- **Date:** 2026-06-21（v2 訂正）
- **対象:** Findability Execution / Already-Published State / Surface Curation / Test Fixture Labeling / JAR Association / Voice Sealing / Human Approval
- **前提:** **F-21 v2 / F-22 v2**, voice_records 公開監査, H-14（execution は要 approval）, F-10/F-14（gateway consent）, Reality Correction

> **v2 訂正の核:** v1 は「door 公開は未実行ゆえ Human Approval を要する execution 境界＝停止 E」と論じた。**監査により platform は既に公開済**——execution の一部は本セッション外で既に起きた。∴ 訂正後の execution 境界は「これから何を公開するか」でなく「**既公開状態をどう curate/remediate するか**」にシフトする。残る execution は3つ——test fixture の labeling、JAR association の扱い、将来の実 voice 封印——いずれも real-data 変更ゆえ **Human Approval 必須**。本セッションでは設計のみ。

---

## 0. execution の位相が変わった

```
v1 想定: door 未公開 → 公開する execution（要 approval・停止E）
v2 実状: platform 公開済（mvp branch public・voice_records 200）
          → execution は「curate / remediate / 将来封印」へシフト
```

- 既公開ゆえ「公開するか否か」でなく「**既公開を honest にどう整えるか**」が境界。

---

## 1. Q1〜Q10（v2）

### Q1. 既公開状態での findability execution とは何か

**curate/remediate:** test fixture の明示 labeling、JAR association の gateway-consent 準拠の扱い、将来の実 individual voice 封印の保証。**新規公開でなく、既公開の整序。**

### Q2. test fixture labeling は execution か

**Yes（real-data 変更）。** test fixture に明示フラグを付す/分離するのは data 変更ゆえ要 Human Approval。誤認防止（Reality Correction）の正当な remediation。

### Q3. JAR（voice-006）association はどう扱うか

**gateway consent 規律（F-10/F-14）。** JAR の既公開声明を Mujin repo に保持し続けることは、JAR の Resource Acceptance/association consent が未取得（F-14）。**選択肢（要 approval）:** ①JAR consent を取得して継続、②association を解消（data 変更）、③公開 surface から voice-006 を分離。いずれも human 判断。

### Q4. 将来の実 individual voice はどう保証するか

**public surface に絶対載せない（F-21/F-22 v2）。** これは forward-looking な execution 規律——実 voice が現れたら public branch でなく sealed 領域に置く。実装は要 approval。

### Q5. これらを本セッションで実行できるか

**No。** test fixture labeling・JAR 扱い・封印実装は real-data 変更かつ outward-facing ゆえ Human Approval 必須。**設計提示のみ。**

### Q6. 既公開は失敗か

**No（calibrated）。** 監査により実在個人暴露は 0 と判明ゆえ重大失敗でない。だが test fixture 誤認と JAR association は honest に整序すべき残件。

### Q7. curate を保留することのコストは

**誤認リスク（test が実と混同）と JAR association が継続。** person 救済の Reach Gap には直結しないが、Reality Correction と組織 consent の観点で整序が望ましい。

### Q8. 最小正当 execution は何か

**Human Approval の下で、test fixture を labeling し、JAR association を gateway consent 規律で扱い、将来の実 voice を sealed 領域に置くこと——public door は person data ゼロを保つ。**

---

## 2. consistency cross-check（H / N / X / F）

| 系列 | 整合性 |
|---|---|
| **H-14**（execution は要 approval・gatekeeping） | ✅ curate/remediate も要 approval |
| **F-10/F-14**（gateway consent） | ✅ JAR association を consent 規律で扱う |
| **H-16**（voice 封印） | ✅ forward-looking 封印として継続 |
| **F-21/F-22 v2** | ✅ door┃data・scouter list 回避と一貫 |
| **Reality Correction** | ✅ test fixture labeling で誤認防止 |

---

## 3. Findability Execution の不変条件（F-23 v2 確定）

```
publication_already_partial_externally  : true   # §0（実状）
remaining_execution_is_curation_remediation : true # Q1
test_fixture_labeling_requires_approval : true   # Q2
jar_association_governed_by_gateway_consent : true # Q3（F-14）
future_real_voice_goes_to_sealed_not_public : true # Q4
all_curation_requires_human_approval    : true   # Q5/H-14
already_published_is_not_catastrophic_but_needs_ordering : true # Q6
public_door_keeps_zero_person_data       : true  # Q8
```

---

## 4. Reality Correction（v2）

- execution の一部（platform 公開）は既に本セッション外で起きた——「これから公開」でなく「既公開の整序」。
- 残る execution（labeling / JAR 扱い / 封印）は real-data 変更・要 Human Approval ゆえ本セッションでは設計のみ。
- 実在個人暴露 0 ゆえ緊急 remediation でなく honest な整序の問題。

---

## NEXT_RECOMMENDED_PHASE

**F-24: Findability State Reconciliation Review** — 設計意図（person-data-ゼロ door）と実際の公開状態（platform 全体＋構造化 voices）の差分を honest に accounting し、整合させる。
