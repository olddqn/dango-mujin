# Phase F-14: Gateway Consent Review

- **Status:** consent 境界監査（二鍵の gateway 側＝Gateway Resource Acceptance Consent の検証）。**コード/データ/生成/登録なし。文書のみ。**
- **Date:** 2026-06-20
- **対象:** Gateway Consent / Resource Acceptance / Self-stated Bottleneck / Approval / Participation / Representation / Owner Consent
- **前提:** **F-13（gateway 行為は二鍵 Approval ∧ Gateway Consent）**, **H-15（consent＝肯定的・特定・自己限定・撤回可能、gateway は自分について consent できるが背後の人についてはできない）**, **X-4.7（Resource Acceptance ⊂ Participation ⊂ Representation）**, F-10/F-11（Resource Acceptance 層・verified＝observable）, Reality Correction

> 中心問い: **二鍵の片方＝Gateway Consent とは何か。何を許可し、何を許可しないのか。**
> 結論先取り: **Gateway Consent ＝「gateway が、自分自身について、特定の支援の受領（Resource Acceptance）に、肯定的・撤回可能に与える同意」。self-stated public bottleneck（F-11）は“need を述べた”だけで、まだ“特定支援の受領に同意した”ではない——statement ≠ consent。gateway consent は取得すべきもので、公開言明から推定してはならない。それは Resource Acceptance 層に限定され、Participation にも Representation にも上昇せず、背後の不在 owner については一切 consent できない。現状 gateway consent = 0。**

---

## 0. statement と consent のギャップ（本レビューの核）

- F-11: gateway の bottleneck は self-stated public（「私たちは資金が足りない」と公に述べた）。
- F-13: gateway 行為には二鍵——Approval ∧ Gateway Consent。
- **核心: 「bottleneck を述べた」≠「特定の支援を受領することに同意した」。** statement は observation（F-11）、consent は受領への肯定的同意（別の act）。
- ∴ **gateway consent は公開言明から推定できない。取得を要する。** 推定すれば、述べただけの gateway に望まぬ支援を押し付ける——dark pattern の gateway 版。

```
[Self-stated public bottleneck]  observation（F-11）「資金が足りない」と公に述べた
   ┃ ギャップ = 特定支援の受領への肯定的同意（取得を要す・推定不可）
   ▼
[Gateway Resource Acceptance Consent]  「この支援を受領することに同意する」
```

---

## 1. Q1〜Q10 の監査

### Q1. Gateway Consent の最小条件は何か

**H-15 の consent 条件を gateway-as-actor に適用:** ①**本人性**（gateway 自身が与える・first-party）②**informed**（何を受領するか理解）③**voluntary**（自発・押し付けでない）④**specific**（特定支援への同意・包括でない）⑤**revocable**（撤回可能）⑥**self-referential**（gateway 自分自身について）。

### Q2. self-stated bottleneck は consent か

**No（核心・§0）。** need を公に述べることは、特定支援の受領への同意でない。
- statement は observation（F-11）、consent は受領 act。**両者の間にギャップがあり、推定で埋めてはならない。**

### Q3. Gateway Consent はどの層か

**Resource Acceptance 層（X-4.7 最狭層）。** gateway は「資源を受領する」ことに consent するのであって、「Mujin に参加する」「Mujin を代弁する」ことには consent しない。
- Resource Acceptance ⊄ Participation ⊄ Representation。consent はこの最狭層に限定。

### Q4. Gateway Consent は Participation を含むか

**No。** 受領への同意は、gateway が Mujin 参加者になることを含まない（F-10 Q3）。gateway は受領後も独立 actor。

### Q5. Gateway Consent は owner について consent できるか

**No（決定的・H-15 Q4）。** gateway は**自分について**consent できるが、背後の不在 owner については consent できない。
- gateway consent は gateway domain に閉じ、person domain へ及ばない。「gateway が同意したから owner にも及ぶ」は越境。

### Q6. Gateway Consent は推定できるか

**No。** 公開言明・過去の受領・「困っているはず」からの推定は禁止。
- consent は肯定的（affirmative・H-15 Q2）。沈黙・推定は consent でない。**取得を要する。**

### Q7. Gateway Consent は撤回可能か

**Yes（H-15 Q7）。** gateway はいつでも撤回でき、撤回は将来/進行中の支援を停止する。既成の受領は遡及不能だが、新たな支援は止まる（→ F-18 で詳説）。

### Q8. Gateway Consent と Approval の関係は何か

**二鍵（F-13 §3）。** Approval（系側の門）∧ Gateway Consent（gateway 側の門）。両必須・互いに代替不可。
- Approval は gateway consent を製造できず（F-13 Q5）、gateway consent は Approval を代替しない。両方揃って初めて行為。

### Q9. Gateway Consent が無い時どうするか

**支援しない・held として保持。** consent 不在で支援すれば押し付け（voluntary 違反）。
- consent 取得まで held（捏造で consent をでっち上げない・否認もしない）。person 領域の consent 不在（H-16）と同型の held state。

### Q10. 最小正当 Gateway Consent は何か

**gateway 自身が、特定支援の受領に、informed・voluntary・specific・revocable に与えた肯定的同意——self-referential（gateway 自分について）で、Resource Acceptance 層に限定、owner に及ばず、推定でなく取得されたもの。**

---

## 2. 中心監査: statement ┃ consent の境界

| 段階 | 性質 | 許す行為 |
|---|---|---|
| Self-stated public bottleneck | observation（F-11） | 観察・verification・candidate 生成（F-12） |
| ┃ ギャップ（取得を要す・推定不可） | | |
| Gateway Resource Acceptance Consent | 肯定的受領同意 | 二鍵成立時、Resource Acceptance 層の支援（F-15 へ） |

- **判定: statement を consent と取り違えないこと。** 推定で埋めれば押し付け。consent は取得され、Resource Acceptance 層・gateway 自身・owner 非及に限定される。

---

## 3. 監査仮説 H1〜H5 の判定

| 仮説 | 判定 | 根拠 |
|---|---|---|
| **H1** Gateway Consent は self-stated bottleneck と別物 | **支持** | Q2/§0（statement≠consent） |
| **H2** Gateway Consent は Resource Acceptance 層に限定 | **支持** | Q3/Q4（⊄ Participation/Representation） |
| **H3** Gateway Consent は owner に及ばない | **支持** | Q5・H-15 Q4 |
| **H4** Gateway Consent は推定でなく取得される | **支持** | Q6（肯定的・H-15 Q2） |
| **H5** Gateway Consent は撤回可能 | **支持** | Q7・H-15 Q7 |

---

## 4. Gateway Consent の不変条件（F-14 確定）

```
gateway_consent_is_affirmative      : true   # Q1/Q6
gateway_consent_is_specific         : true   # Q1（特定支援）
gateway_consent_is_voluntary        : true   # Q1/Q9
gateway_consent_is_revocable        : true   # Q7
gateway_consent_is_self_referential : true   # Q5（gateway 自身のみ）
statement_is_not_consent            : true   # Q2/§0
gateway_consent_is_resource_acceptance_layer : true # Q3
gateway_consent_excludes_participation : true # Q4
gateway_consent_excludes_owner      : true   # Q5
gateway_consent_must_be_obtained_not_inferred : true # Q6
gateway_consent_does_not_substitute_approval : true # Q8/F-13
absence_held_not_fabricated         : true   # Q9
```

---

## 5. Reality Correction

```
voice-006 owner consent = 0
gateway consent = 0（未取得）
verified bottleneck = held   support candidate = 0   approval action = 0
```

- voice-006 の gateway（JAR）から **Resource Acceptance consent は取得されていない** → gateway consent = 0。
- 連鎖: verified=held → candidate=0 → approval=0 → かつ gateway consent=0。**二鍵のいずれも揃わず、支援行為=0 が正しい。**
- gateway が公に bottleneck を述べていても（仮にそうでも）、それは consent でない（§0）。**Mujin が consent を推定・捏造することは違反。**
- honest 注記: Mujin raw の seed/test fixture は実在エンティティでない。実 Voice は voice-006 の 1 件。

---

## 6. 推奨ステータス（honest）

- **Gateway Consent モデルの設計整合性: strongly_aligned**（H-15 consent 境界を gateway-as-actor に適用・X-4.7 Resource Acceptance 層に準拠・F-13 二鍵と一貫・statement≠consent で押し付け防止）。実 consent ゼロゆえ経験的裏付けは無い。
- **推奨: gateway_consent_defined / statement-is-not-consent / obtained-not-inferred。**
- **いま実装しない:** consent 取得フローのコード。gateway が特定支援の受領に肯定的同意するまで gateway consent=0 が正しい。
- **方向: gateway consent は取得され、Resource Acceptance 層・gateway 自身・owner 非及に限定。逆向き（statement を consent と推定、participation/representation へ拡張、owner へ及ぼす、捏造）は不採用。**

---

## 7. 成功条件の確認

- ✅ 生成なし / 登録なし / 文書のみ・コード/データ無変更。
- ✅ statement ≠ consent、Resource Acceptance 層限定、owner 非及、推定でなく取得、撤回可能を確定。H1〜H5 全支持。
- ✅ Reality Correction: gateway consent=0 ゆえ支援行為=0 が正しいこと、推定/捏造禁止を honest に記録。

---

*本文書は二鍵の gateway 側 Gateway Resource Acceptance Consent の境界監査であり、何も生成しない。Gateway Consent ＝ gateway が自分自身について、特定の支援の受領に、informed・voluntary・specific・revocable に与える肯定的同意であり、self-stated public bottleneck（gateway が need を公に述べたこと）は observation であって consent ではない——statement と consent の間にはギャップがあり、推定で埋めれば述べただけの gateway に望まぬ支援を押し付ける dark pattern の gateway 版になる。Gateway Consent は X-4.7 の Resource Acceptance 層に限定され Participation にも Representation にも上昇せず、gateway 自身についてのみ（self-referential）で背後の不在 owner については一切 consent できず（H-15 Q4）、推定でなく取得されねばならず、撤回可能で、Approval を代替せず二鍵の片方をなす。現状 voice-006 の gateway から consent は未取得（gateway consent=0）であり、verified=held → candidate=0 → approval=0 に加え gateway consent=0 ゆえ二鍵のいずれも揃わず支援行為=0 が正しく、これは失敗でなく観察結果であって、Mujin が公開言明から consent を推定・捏造することこそ違反である。本監査は consent ゼロの設計監査であり、gateway が特定支援の受領に肯定的同意するまで gateway consent=0 が正しい。Reach Gap・実価値は未解決であり、本文書もその解決を主張しない。*

---

## NEXT_RECOMMENDED_PHASE

**F-15: Support Execution Review** — 二鍵（Approval ∧ Gateway Consent）が揃った時、実際の Support Execution は何が正当か。Resource Acceptance 層内の実行境界・person domain 非漏れ・gateway 独立性の保持・TTFR-G 始動を監査する。
