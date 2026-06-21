# Phase F-21: Findability Improvement Boundary Review (Post-Audit Correction)

- **Status:** 改善境界監査（正当な findability 改善とは何か）。**v2: voice_records 公開監査の結果を反映した訂正版。** コード/データ/生成/登録なし。文書のみ。
- **Date:** 2026-06-21（v2 訂正）
- **対象:** Findability Improvement / Public Door / Private Data / Voice Exposure / Outreach / Growth / Public Voice Dataset
- **前提:** **voice_records 公開監査（2026-06-21）**, F-5（findability＝consent infrastructure）, H-16（consent 不在の person data 取扱い）, F-1（findability ≠ reachability）, F-10/F-14（gateway consent）, F-6/F-7（救済能力・findability 封鎖は失敗）, Reality Correction

> **v2 訂正の核:** v1 は「voice_records は非公開・封印＝正しい状態」を前提に「platform 公開＝封印破り」と論じた。**監査によりこの前提は falsify された**——`feature/mujin-platform-mvp` は既に公開され `voice_records.jsonl` は public（HTTP 200）。ただし監査結果は**良性**: 6 件中 5 件は seed/test fixture（RFC 予約ドメイン）、1 件（voice-006）は実在組織 JAR の**既公開** NGO report。**実在個人の声の非同意暴露は起きていない。** ∴ 訂正後の中心問い: door┃data 分離は「未来の実 individual voice」への forward-looking 原則として保持しつつ、既公開の現状（test fixture の誤認リスク・JAR association）をどう扱うか。

---

## 0. 訂正後の事実状態（監査準拠）

```
feature/mujin-platform-mvp = 公開済（pushed 2026-06-21）
voice_records.jsonl = public（main + branch で HTTP 200）
  voice-001..005 = seed/test fixture（example.org / ngo.example / gov.example = RFC 予約）
  voice-006 = 実在組織 JAR（refugee.or.jp）の既公開 NGO report
実在個人の声 = 0（非同意暴露なし）
```

- v1 の「門を開く＝封印を破る」緊張は、**門は既に開いており、晒されたのは test fixture と公開組織声明だった**——個人は晒されていない。
- ∴ 訂正後の論点は3つ: ①**door┃data 分離は未来の実 individual voice に forward-looking に適用**（原則は生きている）②**test fixture の公開＝誤認リスク**（Reality Correction）③**JAR association**（gateway consent 未取得・F-10/F-14）。

---

## 1. Q1〜Q10（訂正反映）

### Q1. Findability Improvement とは何か

**求める者が Mujin を発見できる public door を outreach/growth に転じず保つこと**——加えて v2 では「既に公開された surface を、誤認・無断 association を生まないよう curate すること」。

### Q2. door┃data 分離は無効になったか

**No——forward-looking に有効。** 現データは良性（test+公開組織）だが、**未来に実 individual voice を扱う時、それを public door に載せてはならない**原則は不変（H-16）。分離は「過去の封印」でなく「未来の規律」として生きる。

### Q3. test fixture が公開されていることは問題か

**Reality Correction 上の問題（中）。** 実在者は晒されていないが、**test fixture が実 Voice と一見区別できず、Mujin が実需要を保持していると誤認させうる**（Jammy House/D.R.A. 教訓: 未検証を実在と誤認させない）。**→ test fixture は明示マーキングすべき**（実装は要 approval）。

### Q4. voice-006（JAR）の公開は問題か

**association の懸念（中）。** 個人 PII でなく実在組織の**既公開**声明だが、JAR の内容を Mujin 公開 repo に構造化して取り込むことは、**JAR の consent なき Mujin との association**（H-15 Q4・gateway は自分について consent していない／F-10 gateway consent 未取得）。`contact_attempted=False`・`automatic_contact_prohibited=True` は維持。

### Q5. Findability Improvement は outreach/growth/marketing か

**No（F-5 不変）。** door は受動・no count・最小限。v2 でも変わらず。

### Q6. 既公開の voice dataset は Saiyan Scouter artifact か

**構造的には Yes（重要・F-22 で詳説）。** 「needs（housing/water）× region」の公開構造化リストは、本プロジェクトが最も警戒する「不在者の need を列挙する registry」の形。**現状は test+組織ゆえ良性だが、構造が実 individual non-consenting voice を保持すれば Saiyan Scouter artifact になる。** 公開 dataset に実 individual voice を入れない原則が決定的。

### Q7. door を開かないことは失敗か

**条件付き Yes（F-7 不変）。** だが v2 では「門は既に（過剰に）開いている」——課題は「開く」でなく「適切に curate する」方向にシフト。

### Q8. 現状の findability surface は consent opportunity に資するか

**部分的——だが誤認・association リスクを伴う。** 公開 repo は Mujin を発見可能にするが、test fixture の誤認と JAR association が surface の質を損なう。curate が改善の中身。

### Q9. door 改善はどこまで person 救済に効くか

**necessary・非十分（F-5 §3 不変）。** door は consent opportunity を開くのみ。

### Q10. 最小正当 Findability Improvement は何か（訂正）

**(a) 未来の実 individual voice を public door に載せない（forward-looking 分離）、(b) test fixture を明示マーキングし誤認を防ぐ、(c) JAR 等実在組織は gateway consent 規律で扱う、(d) public door は person data ゼロ・受動・no growth——を満たすよう既公開 surface を curate すること。**

---

## 2. consistency cross-check（H / N / X / F 系列）

| 系列 | 整合性 | 訂正点 |
|---|---|---|
| **H-16**（consent 不在・voice 封印） | ⚠️ **訂正**: 「voice 非公開＝reassuring」は falsify。但し監査で「実 individual voice は 0」と判明ゆえ実害なし。原則は forward-looking に保持 |
| **F-8**（observed edge・voice-006） | ✅ voice-006＝JAR＝observed edge と整合 |
| **F-10/F-14**（gateway consent） | ✅ JAR association を gateway consent 未取得として扱う点で整合 |
| **F-5/F-6**（findability＝consent infra・no growth） | ✅ door 受動・no count 不変 |
| **Saiyan Scouter**（X/N 系列） | ⚠️ 公開 voice dataset の構造的リスクを新規に surface（Q6） |
| **Reality Correction**（Jammy House/D.R.A.） | ✅ test fixture 誤認防止として適用 |

---

## 3. Findability Improvement の不変条件（F-21 v2 確定）

```
door_data_separation_is_forward_looking : true  # Q2（未来の実 voice に適用）
no_real_individual_voice_in_public_door : true  # Q2/Q6（H-16 forward）
test_fixtures_must_be_labeled           : true  # Q3（誤認防止）
real_org_content_governed_by_gateway_consent : true # Q4（F-10/F-14）
public_voice_dataset_is_latent_scouter_artifact : true # Q6
door_is_passive_no_growth_no_count      : true  # Q5（F-5）
improvement_now_means_curation          : true  # Q1/Q8/Q10
door_is_necessary_not_sufficient        : true  # Q9
```

---

## 4. Reality Correction（v2）

- **falsify された前提:** 「voice_records 非公開」。実状: 公開済。
- **救済的訂正:** 公開されたのは test fixture 5 + 実在組織 JAR の既公開声明 1。**実在個人の非同意暴露は 0。** v1 の警報深刻度は下方修正。
- **残る正当な懸念:** ①test fixture の誤認リスク（label すべき）②JAR association（gateway consent 未取得）③公開 voice dataset の構造的 Saiyan Scouter リスク（実 individual voice を絶対入れない）。
- いずれも remediation/labeling は real-data 変更・要 Human Approval ゆえ本セッションでは実行しない。

---

## NEXT_RECOMMENDED_PHASE

**F-22: Consent Opportunity Bridge Review (v2)** — 公開 surface が既に存在する前提で、来訪者を pre-expose せず・公開 voice dataset が scouter list として機能しない bridge を再監査する。
