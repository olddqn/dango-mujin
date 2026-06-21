# Phase F-22: Consent Opportunity Bridge Review (Post-Audit Correction)

- **Status:** 橋境界監査（public door が consent を強制せず可能にする仕組み）。**v2: 公開監査反映。** コード/データ/生成/登録なし。文書のみ。
- **Date:** 2026-06-21（v2 訂正）
- **対象:** Consent Opportunity / Public Door / Pre-exposure / The Gap / Public Voice Dataset / Scouter List
- **前提:** **F-21 v2（door┃data は forward-looking・公開 voice dataset は latent scouter artifact）**, F-5 §3（Discovery≠Consent・隙間保持）, H-15（consent）, H-11（identity 名寄せ＝最大リスク）, voice_records 公開監査, Reality Correction

> **v2 訂正の核:** 橋の設計（隙間保持・no pre-exposure・本人起点）は seal 前提に依存せず**そのまま有効**。だが監査は新たな論点を surface した——**公開された voice dataset（needs × region の構造化リスト）は、来訪者でなく“晒される側”の問題**。橋は「来訪者が pre-expose されない」だけでなく「**公開 surface 上の voice データが、不在者を target するための scouter list として機能しない**」ことを要する。現状は test+組織ゆえ良性だが、構造的規律として確定する。

---

## 0. 二方向の pre-exposure

```
方向A（来訪者）: door に辿る者が個人情報を要求/収集されない（F-22 v1 の主題・有効）
方向B（晒される側）: 公開 surface 上の voice データが、不在者を列挙・target 可能にしない（v2 新規）
```

- v1 は方向 A（来訪者の pre-exposure）を扱った——**有効、変更なし**。
- v2 は方向 B を追加: **公開された voice dataset 自体が、不在の need 保有者を「需要リスト」として晒し、第三者が target に使える scouter list になりうる**。現状 test+組織ゆえ実害なしだが、構造的に封じる。

---

## 1. Q1〜Q10（v1 有効分は簡約・v2 追加を明示）

### Q1〜Q5（方向A・v1 有効）

- Bridge は consent を強制せず可能にする（隙間保持）。door 到達は consent でない。door は来訪者に個人情報を要求しない（no pre-exposure）。関与は本人起点（pull）。隙間を詰めれば dark pattern。**すべて v2 でも有効。**

### Q6（v2 新規）. 公開 voice dataset は scouter list になりうるか

**構造的に Yes。** 「need カテゴリ × region」の公開リストは、第三者が「困っている人々」を地域別に列挙・target する材料になりうる。**現状は test fixture 5 + 公開組織 1 ゆえ良性**だが、実 individual voice を含めば、それ自体が「不在者の need を晒し target 可能にする」Saiyan Scouter artifact（H-11 の identity 名寄せ・X/N 系列の問題定義の権力）。

### Q7（v2）. 橋は晒される側をどう守るか

**公開 surface に実 individual voice を載せない（F-21 v2）＋ region 等を target 可能な粒度で公開しない。** 来訪者の consent opportunity（方向A）と、晒される側の非 target 化（方向B）は両立させる。

### Q8（v2）. JAR（組織）の voice は方向Bの懸念か

**個人 target の懸念は低い（組織・既公開）が、association の懸念は残る（F-21 Q4）。** 組織の既公開声明は target list でないが、Mujin との無断 association は別問題（gateway consent）。

### Q9. consent しない自由（v1 有効）

**来訪者が consent しないのは正当な自由。** 不変。

### Q10. 最小正当 Bridge（v2）

**方向A（来訪者を pre-expose しない・隙間保持・本人起点）＋ 方向B（公開 surface が不在者の scouter list として機能しない＝実 individual voice 非掲載・target 粒度回避）。**

---

## 2. consistency cross-check（H / N / X / F）

| 系列 | 整合性 |
|---|---|
| **F-5 §3**（隙間保持） | ✅ 方向A 不変 |
| **H-11**（cross-source 名寄せ最大リスク） | ✅ 方向B＝公開 dataset の scouter 化として接続 |
| **X/N 系列**（Saiyan Scouter・問題定義の権力） | ✅ 公開 need リストの構造的危険として整合 |
| **H-16**（voice 封印） | ⚠️ 訂正反映: 封印は forward-looking、現データは良性 |
| **F-21 v2** | ✅ door┃data・latent scouter artifact と一貫 |

---

## 3. Bridge の不変条件（F-22 v2 確定）

```
# 方向A（v1 有効）
bridge_preserves_the_gap            : true
no_pre_exposure_to_reach_door       : true
engagement_is_visitor_initiated_pull : true
visitor_identity_not_pre_resolved   : true
not_consenting_is_legitimate_freedom : true
# 方向B（v2 新規）
public_surface_is_not_a_scouter_list : true   # Q6
no_real_individual_voice_on_public_surface : true # Q6/F-21
no_targetable_granularity_of_need_or_region : true # Q7
org_voice_association_governed_by_consent : true # Q8
```

---

## 4. Reality Correction（v2）

- 橋の方向A設計は seal-independent ゆえ有効。
- 監査が surface した方向B（公開 voice dataset の scouter 化）は、現状 test+組織で良性だが構造的リスク。**実 individual voice を公開 surface に載せない**ことが決定的封鎖。
- target 粒度回避・JAR association 扱いは real-data 判断ゆえ本セッションでは実行しない。

---

## NEXT_RECOMMENDED_PHASE

**F-23: Findability Execution Boundary Review (v2)** — 公開が既に部分的に起きた前提で、残る findability execution（surface curate・将来公開）の境界と、test fixture labeling / JAR association / 実 voice 封印 の real-data 判断を監査する。
