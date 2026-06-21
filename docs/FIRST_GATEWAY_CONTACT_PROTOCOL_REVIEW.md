# First Gateway Contact Protocol Review

- **Status:** 観察レビュー。Mujin が初めて Gateway（JAR）に接触する場合に**何の consent を求めることになるか**を観察する。**実際の接触は行わない。** Gateway 登録・Need・Contribution・Cooperation・Feedback 生成なし。メール/フォーム/SNS/実世界通知なし。コード/データ無変更。文書のみ。
- **Date:** 2026-06-13
- **対象:** `voice-006`（JAR Public Voice / https://www.refugee.or.jp/support/ ）
- **前提:** X-2.5 / X-2.6 / X-3 / X-3.5 / H-4 / X-4 / X-4.5 / X-4.6(Gateway Consent) / X-4.7(Representation Boundary) / X-5(Eligibility) / X-5.5(Consent Gap)

> 新しい次元: これまでは**記録**の consent を観察した。本フェーズは**接触行為そのもの**を観察する。
> 接触は Saiyan Scouter v2 の問い「**なぜあなたに接触したのか**」を組織レベルで再起動する。

---

## 0. 二層構造 — 接触は「求める consent」と「接触自体の正当化」を分けて見る

| 層 | 問い |
|---|---|
| **(1) 接触が求める consent** | この連絡は Resource Acceptance / Participation / Representation のどれを求めているか |
| **(2) 接触自体の正当化** | なぜ JAR に・なぜ今・なぜ Mujin が連絡するのか（Saiyan Scouter v2） |

(1) が妥当でも (2) が説明不能なら、接触は正当化されない。

---

## 1. Contact Case A〜D の観察

### Case A — 「JAR を Voice Source として参照しています」と通知
- **求める consent:** **なし**（公開情報の引用は許可不要・X-5 §1）。
- **representation 発生:** なし（source 引用は表象でない）。**participation:** なし。
- **観察:** これは consent を求めない**任意の儀礼的接触**。だが「引用するだけ」なのに連絡する理由が弱い（**なぜ今・なぜ連絡するのか**が説明しにくい）。不要な接触になりうる。

### Case B — 「Gateway Candidate として掲載してよいですか」
- **求める consent:** **Representation Consent**（X-5.5: gateway candidate = 表象の特殊ケース）。掲載 ≠ 実働なので **Participation はまだ**。
- **観察:** これは X-5 で「不在」と判明した Representation Consent を**正しく求める**接触。**「載せてよいか」と問うこと自体が、無断表象の解毒剤。** 接触は consent-seeking で、構造的に正当。

### Case C — 「Mujin の協力実験に参加しますか」
- **求める consent:** **Participation + Representation の両方**（実働接続者＝参加＋記録への表象）。
- **観察:** Participation Consent と Representation Consent の関係がここで現れる: **参加を求めれば、参加者として記録する＝表象も同時に求めることになる。** 両者は接触の中で束ねて問われる。やはり「問う」ことが解毒剤。

### Case D — 「寄付したい」「ボランティアしたい」
- **求める consent:** **Resource Acceptance**（JAR が公開で既に与えている）。
- **観察（境界）:**
  - **個人が JAR の公開窓口に寄付/参加する**なら → 接触すら不要・consent 既存。Mujin は要らない。
  - **Mujin が組織として「Mujin が貢献を届けたい」と連絡する**なら → Mujin-JAR の関係性が生じ、participation/representation が滲む。
  - **Resource Acceptance と Participation の境界:** 資源を受け取る同意（既存）と、Mujin と継続的に協働する同意（未取得）は別。

---

## 2. Consent Mapping（各ケース）

```json
[
 {
  "case": "A — notify source citation",
  "resource_acceptance": false,
  "participation": false,
  "representation": false,
  "contact_justification_present": false,
  "contact_justification_comment": "公開引用は許可不要。連絡する理由（なぜ今・なぜ連絡）が弱い。任意の儀礼。",
  "representation_risk": "low",
  "scouter_risk": "low",
  "human_comment": "接触しないのが最も整合的。引用は連絡を要しない。"
 },
 {
  "case": "B — propose gateway candidate listing",
  "resource_acceptance": false,
  "participation": false,
  "representation": true,
  "contact_justification_present": true,
  "contact_justification_comment": "Representation Consent を明示的に求める。具体的な ask があり説明可能。",
  "representation_risk": "medium (asking mitigates)",
  "scouter_risk": "low-medium (問うこと自体が解毒剤)",
  "human_comment": "X-5 で不在だった consent を正しく求める形。ただし Mujin の都合を JAR に課す。"
 },
 {
  "case": "C — propose cooperation trial participation",
  "resource_acceptance": false,
  "participation": true,
  "representation": true,
  "contact_justification_present": true,
  "contact_justification_comment": "Participation を求めると Representation も束ねて求めることになる。",
  "representation_risk": "medium (asking mitigates)",
  "scouter_risk": "medium (mitigated by explicit ask)",
  "human_comment": "参加と表象が接触の中で同時に立ち上がる。JAR の時間を要求する。"
 },
 {
  "case": "D — offer contribution (donate/volunteer)",
  "resource_acceptance": true,
  "participation": false,
  "representation": false,
  "contact_justification_present": false,
  "contact_justification_comment": "個人なら接触不要(公開窓口で完結)。Mujin が組織として連絡する正当化(なぜMujin)が弱い。",
  "representation_risk": "low (individual) / medium (Mujin-qua-Mujin)",
  "scouter_risk": "low",
  "human_comment": "最も接触を要しないケース。Mujin の介在が不要かもしれない。"
 }
]
```

---

## 3. Contact Justification（Saiyan Scouter v2 分析）

| # | 問い | voice-006/JAR での答え | 評価 |
|---|---|---|---|
| **J1** | なぜ JAR なのか | voice-006 が JAR の公開要請であり、人間が X-2 で選定したから | ✅ 答えられる |
| **J2** | なぜ今なのか | **弱点。** JAR の要請は**常設**（X-4.6）。引き金となる出来事がない。正直な答えは「Mujin がこの段階に達したから」＝**Mujin 中心**の理由 | ⚠️ 説明困難 |
| **J3** | なぜ Mujin が接触するのか | **構造的問い。** 個人は JAR に直接寄付できる(Case D)。Mujin が何を足すか未証明(n=0)。Mujin の介在の必要性が不明 | ⚠️ 説明困難 |
| **J4** | なぜ consent を求めるのか | Representation/Participation が不在(X-5/X-5.5)で、求めなければ無断表象になるから | ✅ 答えられる（B/C で明確） |
| **J5** | 説明不能な接触になっていないか | Case A・D(Mujin として)は「なぜ連絡?」が弱く**説明不能に近い**。Case B・C は「○○の許可を求める」と明確で説明可能 | A/D=危険・B/C=可 |

**核心:** **接触の正当化が最も弱いのは J2(なぜ今)と J3(なぜ Mujin)。** JAR の要請が常設のため「今」を需要が駆動せず、接触は **Mujin の process 段階**が駆動する。これは Saiyan Scouter v2 の再出現——**接触が、接触される側の需要ではなく接触する側の agenda で正当化される**危険。

---

## 4. 必須観察項目（8点）

1. **Source と Contact の境界:** source 引用は接触を要しない。Case A の「通知接触」は任意で、正当化が弱い。
2. **Reference と Contact の境界:** 参照も接触を要しない。記録（引用/参照）と接触（働きかけ）は別の行為。
3. **Gateway Candidate は接触を必要とするか:** **YES** — Representation Consent を得るため（Case B）。**問うことが無断表象の正しい代替。**
4. **Participation は接触を必要とするか:** **YES** — Participation Consent を得るため（Case C）。
5. **Representation Consent はどの段階で必要になるか:** **Gateway Candidate（Case B）の段階**から。そしてそれを求める接触が、X-5 の「不在」を埋める正当な機構。
6. **Contact Justification はどの段階で必須になるか:** **最初の接触から**（Case A の通知ですら）。そして A/D で最も難しく、B/C で容易。**接触する以上、J1〜J5 に答えられねばならない。**
7. **Saiyan Scouter 問題は接触時にどう再出現するか:** v2「なぜあなたに接触したのか」として組織レベルで再起動。常設要請が「なぜ今」を需要から切り離し、**接触が Mujin の agenda で正当化されるリスク**。
8. **実際の Gateway Contact 前に不足している観察:**
   - JAR が**そもそも連絡されたいか**（組織の接触選好）。
   - Mujin が JAR/個人が単独でできないことを足すか（J3 が未証明・n=0）。
   - 「なぜ今」を答えられる**実在の個人需要**（あれば J2 が需要駆動になる）。
   - JAR の時間を尊重する**明確で最小の ask**。

---

## 5. Saiyan Scouter 分析（まとめ）

- 三階構造の到達点: 個人の代弁(X-2.6) → 組織の無断記録(X-4.5) → 表象 consent の特定(X-4.7) → データモデル写像(X-5) → Gateway=表象の特殊形(X-5.5) → **接触行為そのものの正当化(本 X-6)**。
- **最大の発見:** consent を**求める**接触(B/C)は、何も求めない/既存 consent に乗る接触(A/D)より**正当化しやすい**——明確な ask があるから。だが B/C は **Mujin の agenda を JAR に課す**。逆説: 最も丁寧に consent を求める行為が、最も JAR の時間を要求する。
- **v2 の問いへの正直な現在地:** Mujin は今、JAR への接触について J2(なぜ今)と J3(なぜ Mujin)に**強くは答えられない**。常設要請に対し、需要でなく自らの段階で接触しようとしている。**この自覚こそが、説明不能な接触を防ぐ。**

---

## 6. 暫定結論

- **最も安全な「最初の接触」は、接触しないこと**かもしれない——Source/Reference に留まり（X-5）、(a) 実在の個人需要が現れて「なぜ今」が需要駆動になるか、(b) Mujin が JAR/個人の単独では不可能な価値を articulate できるまで待つ。
- **もし接触するなら、Case B（Representation Consent を明示的に求める）が最も整合的**——X-5 の「不在 consent」を正しく埋める。ただし J2/J3 に答えてから。
- **Case A（通知）と Case D（Mujin として貢献を申し出る）は避ける**——前者は不要、後者は Mujin の介在の必要性が未証明。個人の寄付は Mujin を要しない。
- **接触は記録より重い。** 記録は「書かない」で保留できるが、接触は取り消せない（JAR の時間と注意を既に使う）。だから接触の閾値は記録より高く置く。

---

## 7. やらなかったことの証明

- Gateway Contact を実施していない（メール/フォーム/SNS/実世界通知なし）。
- Gateway 登録・Need・Contribution・Cooperation・Feedback を生成していない。
- コード/データ/レコード無変更。すべて文書内の観察。

---

*本文書は最初の Gateway 接触が求める consent の観察記録であり、実際の接触・登録・生成を一切含まない。暫定結論: 最も安全な最初の接触は接触しないことかもしれず、接触するなら Representation Consent を明示的に求める Case B が整合的だが、その前に「なぜ今・なぜ Mujin」に答えねばならない。接触は記録より重く、取り消せない。Reach Gap は未解決であり、本文書もその解決を主張しない。*
