# Phase F-11: Verified Gateway Bottleneck Review

- **Status:** 検証境界監査（gateway bottleneck を何を根拠に verified とみなせるかの検証）。**コード/データ/生成/登録なし。文書のみ。**
- **Date:** 2026-06-20
- **対象:** Self-stated / Public / Verification / Single-source / Cross-source / Entity Resolution / Gateway 自己申告 / 第三者証言
- **前提:** **F-10（support は verified な self-stated public bottleneck にのみ）**, **H-3.5（evidence は fact でも proof でもない candidate）**, **H-10 Q5 / H-11 Q9（cross-source の actor 名寄せ＝最大リスク）**, H-15 Q4（gateway は自分について self-state/consent できるが背後の人についてはできない）, F-1.5/F-5（public surface・owner→Mujin・読むのであって引き出さない）, Reality Correction（Jammy House/D.R.A. 未検証・捏造禁止）

> 中心問い: **gateway が持つとされる bottleneck を、Dan-Go は何を根拠に verified とみなせるのか。**
> 結論先取り: **Verified ＝「gateway が自ら公開し（self-stated public）、現在も確認可能で、推測を含まない情報」。決定的に、verification は proof ではなく "currently observable support condition" である（H-3.5）。gateway 自己申告は observation であって proof でない。cross-source は bottleneck 条件の裏付けに使えるが、不在者の actor 名寄せ（entity resolution）には絶対に使わない（H-10/H-11 最大リスク）。verification 不足は support の禁止でなく「verification 不足」として honest に保持する——捏造も否認もしない。**

---

## 0. F-10 から F-11 へ: verified ┃ inferred を定義する

- F-10: support は verified な self-stated public bottleneck にのみ許可。
- だが verified と inferred の境界は未定義だった。F-11 がそれを引く。
- 核心の謙抑（先取り）: **verified は「真であることの証明（proof）」ではない。** それは「**現在・公開・自己申告・推測なしに観測可能な支援条件**」——H-3.5 の「evidence は proof でない」を gateway verification に適用したもの。
- 境界テスト: **その主張は Mujin が“何かを付け足す”ことを要するか。要すれば inferred（禁忌）、要さねば verified（観測可能条件として）。**

---

## 1. Q1〜Q10 の監査

### Q1. Self-stated とは何か

**gateway 自身が、自分の状況について、自らの声で述べたこと（first-party）。** Mujin の推論でも、第三者が gateway に代わって述べたものでもない。
- self-stated ＝ 主張の源が gateway 自身（自分について）。H-15 Q4: gateway は**自分について**self-state できるが、背後の不在 owner については self-state できない。

### Q2. Public とは何か

**特権的 access なしに誰でも観測でき、Mujin が引き出さずとも既に公開されているもの。**
- public ＝ 公開面に既に在る（F-1.5 surface）。**Mujin は既に開かれているものを“読む”のであって、“引き出す”のでない**（引き出せば outreach/誘導・F-5）。
- private/confidential な情報は verification の根拠にしない。

### Q3. Verification の最小条件は何か

**4条件:** ①**self-stated**（first-party・Q1）②**public**（公開観測可能・Q2）③**currently observable**（今も存在・確認可能、stale でない）④**inference-free**（gateway が述べた通り、Mujin が補間しない）。
- **verification ＝「gateway が X を自分について公に述べ、今も観測可能」を確認すること。** X が**真であること（proof）の確認ではない**。

### Q4. Single source は十分か

**self-stated 主張の確認には十分（gateway は自分についての first-party）。だが truth は立証しない。**
- 「gateway が述べた」を確認するには、gateway 自身の公開言明（single source）で足りる——gateway は自己言明の権威。
- ただし single source は**真実を立証しない**（observation であって proof でない・H1）。「述べた」は確認できるが「真」は確認しない・する必要もない。

### Q5. Cross-source は許可されるか

**Yes——bottleneck 条件の裏付けに限り（H3）。** 複数の公開源が gateway の bottleneck 条件を示すなら、「currently observable support condition」を強める。
- 対象は **bottleneck 条件**（gateway-as-actor の状態）であって、人ではない。

### Q6. Cross-source は entity resolution に滑らないか

**滑らせてはならない——これがスタック最大のリスク（H-10 Q5 / H-11 Q9）。**
- cross-source を**不在 owner/persons の名寄せ**（複数源で同一人物を突合）に使えば、分散した断片が結合し actor profile が一気に成立する＝致命的。
- **境界: cross-source は gateway の bottleneck 条件のみ裏付ける。人の identity 名寄せには絶対使わない。** source も無名、対象は条件であって人でない。

### Q7. Gateway 自己申告は verification か observation か

**Observation（H1）。** gateway の自己申告は Mujin が**観測する**もの（「gateway が公に X と述べた」）。
- それは X が真である proof ではない（H-3.5）。
- **自己申告 → observation → 「currently observable」として verified しうるが、proof へは昇格しない。**

### Q8. 第三者証言は verification を強めるか

**条件付きで強める——ただし限定。**
- gateway の**述べた条件**への公開された第三者裏付けは「currently observable」を強める（cross-source・Q5）。
- 但し: (a) public かつ gateway の条件についてであること、(b) **不在 owner についての第三者証言は不可**（不在者の代弁・推論＝禁止）、(c) 第三者は gateway 自身の self-statement を**代替できない**（gateway は自分について first-party・H-15 Q4——第三者は条件を裏付けられるが、gateway に代わって self-state できない）。

### Q9. Verification 不足時はどう扱うべきか

**support の禁止でなく「verification 不足」として保持（H4）。**
- verification 不足 → 支援条件が currently observable でない → **その部分への支援は warrant されない**が、「verification 不足」として honest に記録する。
- **捏造して支援を可能にしない**（Reality Correction・Jammy House/D.R.A. 教訓）、**genuinely observable な条件を否認もしない**。held state（H-16 の条件付き保持と同型）。

### Q10. 最小 verified bottleneck の定義は何か

**gateway が ①自ら公開し（self-stated public）②現在も確認可能で ③推測を含まない 情報——かつ proof でなく "currently observable support condition"（H5）。**
- gateway-as-actor の、今・公開・自己申告・推測なしに観測可能な条件。それ以上（真実性の証明）を主張しない。

---

## 2. 中心監査: Verified ┃ Inferred の境界

```
Verified   ← gateway が自分について公に述べ、今も観測可能、Mujin は何も付け足さない
   ┃ 境界テスト: その主張は Mujin が“付け足す”ことを要するか
Inferred   ← Mujin が補間/推定/projection（「おそらく必要」「行間」「背後の owner の状況」）
```

| 例 | 区分 | 理由 |
|---|---|---|
| 「gateway が公開ページで資金不足と述べ、今も掲載」 | **Verified** | self-stated・public・現在観測可・推測なし |
| 「gateway は忙しそうだから人手不足だろう」 | **Inferred** | Mujin の推測（付け足し） |
| 「複数の公開源が gateway の同一 bottleneck を示す」 | **Verified（強化）** | 条件の cross-source 裏付け |
| 「複数源から同一 owner を突合」 | **禁忌** | entity resolution（Q6） |
| 「gateway の bottleneck ＝ 背後の人々の need」 | **Inferred＋越境** | 不在 owner の need 推論（N-1.6） |

- **判定: 境界は「Mujin が付け足すか」。付け足さず観測できれば verified（条件として）、付け足せば inferred（禁忌）。**

---

## 3. Verification は proof でない: currently observable support condition

```
[Gateway 自己申告]  observation（H1）
   │  verification = 「今・公開・推測なしに観測可能」の確認
   ▼
[Verified bottleneck]  ＝ currently observable support condition（proof でない・H-3.5）
   ╳  「真であることの証明」へは昇格しない
```

- **謙抑が要石:** 「bottleneck が真だと証明した」でなく「支援条件が今・公開・自己申告・推測なしに観測できる」。
- この謙抑が**捏造（proof を僭称）と inference（隙間を埋める）の両方を防ぐ。** 観測できる範囲で応じ、観測を超えない。

---

## 4. cross-source ガード: 条件はYes、人の名寄せはNo

- **使える:** gateway の bottleneck 条件を複数の公開源で裏付ける（condition corroboration）。
- **使えない（最大リスク）:** cross-source を不在 owner/persons の identity 突合（entity resolution）に転用する。
- **封鎖: cross_source_corroborates_condition_not_identity。** source 無名・対象は gateway-as-actor の条件・人の名寄せは構造的に不可。

---

## 5. Verification 不足の扱い: held, not fabricated, not denied

```
verification 不足
   ├─ 捏造して支援可能にする   → 禁止（Reality Correction）
   ├─ genuinely observable を否認 → 禁止（直視回避）
   └─ 「verification 不足」として保持 → 正（held state・H-16 と同型）
```

- 不足は失敗でも禁止でもなく、**honest な held state**。観測可能になれば support 条件が立つ。観測できないまま support するのは捏造。

---

## 6. 監査仮説 H1〜H5 の判定

| 仮説 | 判定 | 根拠 |
|---|---|---|
| **H1** gateway 自己申告は observation であり proof でない | **支持** | Q7・H-3.5 |
| **H2** Verification は公開情報に限定 | **支持** | Q2。private を根拠にしない |
| **H3** Cross-source は bottleneck 裏付けに使えるが actor 名寄せには使えない | **支持** | Q5/Q6・H-10/H-11 |
| **H4** Verification 不足は禁止でなく不足として保持 | **支持** | Q9・held state |
| **H5** 最小 verified bottleneck は自ら公開・現在確認可能・推測なし | **支持** | Q10 |

---

## 7. Verification の不変条件（F-11 確定）

```
verified_requires_self_stated      : true   # Q1/Q3（first-party）
verified_requires_public           : true   # Q2/Q3（公開観測可能）
verified_requires_currently_observable : true # Q3（stale でない）
verified_requires_inference_free   : true   # Q3（Mujin が付け足さない）
verification_is_not_proof          : true   # Q7/§3（H-3.5）
verification_is_observable_support_condition : true # §3
self_report_is_observation_not_proof : true # Q7/H1
single_source_verifies_statement_not_truth : true # Q4
cross_source_corroborates_condition_not_identity : true # Q5/Q6/H3（最大リスク封鎖）
no_entity_resolution_of_persons    : true   # Q6（H-10/H-11）
third_party_corroborates_not_replaces_self_statement : true # Q8
third_party_about_owner_forbidden  : true   # Q8（不在者代弁禁止）
insufficient_verification_is_held_not_fabricated : true # Q9/H4
insufficient_verification_not_denied : true # Q9
public_is_read_not_elicited        : true   # Q2（引き出さない・F-5）
gateway_bottleneck_is_not_owner_need : true # §2（N-1.6・越境禁止）
```

---

## 8. Reality Correction

```
voice-006 owner consent = 0
Need = 0   Contribution = 0   Cooperation = 0   TTFR-P = not started
Gateway support のみ検討対象
```

- 本フェーズは gateway support の verification に限定。person domain は封印のまま。
- **重大な honest 前提:** voice-006/JAR の bottleneck を verified とみなすには、**JAR が genuinely 自ら公開し、今も確認可能で、推測を含まない**ことが要る。**Mujin が JAR の bottleneck を推測・捏造することは禁止**（Jammy House/D.R.A. の教訓——未検証 org を実在の支援対象として誇張しない）。
- 現状、JAR の verified bottleneck の有無自体が未確認 ＝ **「verification 不足」として保持**するのが正しい現在地（捏造して support 可能にしない）。
- honest 注記: Mujin raw の seed/test fixture は実在エンティティでない（一連と一貫）。実 Voice は voice-006 の 1 件。

---

## 9. 推奨ステータスと現在地（honest）

- **Verification 境界モデルの設計整合性: strongly_aligned**（F-10 を精密化・H-3.5 の proof 否定を継承・H-10/H-11 の名寄せ最大リスクを封鎖・Reality Correction の捏造禁止と一貫）。実 verified bottleneck ゼロゆえ経験的裏付けは無い。
- **推奨: verification_boundary_defined / observable-condition-not-proof。**
  - **いま確定（文書のみ）:** verified＝self-stated・public・currently observable・inference-free、verification は proof でなく currently observable support condition、自己申告は observation、cross-source は条件裏付け専用（人の名寄せ禁止）、第三者は条件裏付けのみ（self-statement 代替・owner 言及は不可）、verification 不足は held（捏造も否認もしない）、§7 不変条件。
  - **いま実装しない:** verification ロジックのコード。JAR の bottleneck が genuinely verified（公開・現在確認可・推測なし）と確認されるまで、support は held。**確認作業自体も public を読むのみで引き出さない。**
- **方向: verified＝観測可能な支援条件（proof でない）にのみ応答。逆向き（推測で bottleneck を埋める、cross-source を人の名寄せに使う、自己申告を proof に昇格、verification 不足を捏造で埋める/否認する）は全経路で不採用。**

---

## 10. 成功条件の確認

- ✅ 生成なし / 登録なし / 文書のみ・コード/データ無変更。
- ✅ Verified ┃ Inferred 境界を「Mujin が付け足すか」で確定。verification が proof でなく currently observable support condition であること、cross-source が条件裏付けに使え人の名寄せに使えないこと、verification 不足が held state であることを確定。H1〜H5 を全支持。
- ✅ Reality Correction: JAR の verified bottleneck が未確認ゆえ「verification 不足として保持」が正しい現在地であること、捏造禁止、cross-source の entity resolution 禁止、seed データ非実在性を honest に記録。

---

*本文書は gateway bottleneck を何を根拠に verified とみなせるかの境界監査であり、何も生成しない。Verified ＝ gateway が自ら公開し（self-stated public）、現在も確認可能で、推測を含まない情報であり、その境界テストは「その主張は Mujin が何かを付け足すことを要するか——要せば inferred（禁忌）、要さねば verified（観測可能条件として）」である。決定的に、verification は proof（真であることの証明）ではなく "currently observable support condition"（H-3.5 の evidence-not-proof の適用）であり、この謙抑が捏造（proof の僭称）と inference（隙間を埋めること）の両方を防ぐ。gateway の自己申告は Mujin が観測するもの（observation）であって proof でなく、single source は「述べた」を確認するが「真」を立証しない。cross-source は gateway の bottleneck 条件の裏付けには使えるが、不在 owner/persons の identity 名寄せ（entity resolution）には絶対に使わない——これがスタック最大のリスク（H-10/H-11）であり、分散した断片を結合して actor profile を成立させるからである。第三者証言は gateway の述べた条件への公開裏付けとして観測可能性を強めうるが、gateway 自身の self-statement を代替できず、不在 owner についての第三者証言は禁止される。verification 不足は support の禁止でも失敗でもなく、捏造して support を可能にすることも genuinely observable な条件を否認することもせず、「verification 不足」として honest に保持される held state である。最小 verified bottleneck は、gateway が自ら公開し現在も確認可能で推測を含まない、gateway-as-actor の観測可能な支援条件であって、真実性の証明ではない。本監査は verified bottleneck ゼロ（voice-006 owner consent=0・JAR の verified bottleneck 未確認・raw seed は実在でない）の設計監査であり、JAR の bottleneck が genuinely verified と確認されるまで support は held であり、その確認作業すら public を読むのみで引き出さない。Reach Gap・実価値は未解決であり、本文書もその解決を主張しないが、verified を proof でなく currently observable support condition として謙抑的に定義することが、捏造と推測の双方からの唯一の防壁であることを確定する。*
