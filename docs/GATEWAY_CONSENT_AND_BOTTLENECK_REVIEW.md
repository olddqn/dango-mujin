# Gateway Consent & Bottleneck Observation Review

- **Status:** 観察レビュー。X-4.5 の発見「**Gateway Need にも残余推論がある**」の検証。Need を作成・承認・却下しない。Gateway 選定なし。Contribution 生成なし。文書のみ。
- **Date:** 2026-06-13
- **検証対象:** [`GATEWAY_BOTTLENECK_SIMULATION_REVIEW.md`](GATEWAY_BOTTLENECK_SIMULATION_REVIEW.md) §3（A/B の残余推論）・§4（組織 consent の不在）
- **対象 Voice:** `voice-006`（JAR 公開支援要請 / https://www.refugee.or.jp/support/ ）
- **使用事実:** 検証済み（[`VOICE_CANDIDATE_VERIFICATION.md`](VOICE_CANDIDATE_VERIFICATION.md) C4）の範囲のみ。推測で事実を足さない。

> 検証する仮説: 「A 資金 / B 人手 は direct_observation（H-4 で scouter_risk: none）」だが、**その内部にも推論の起点がある**。
> A/B を4層に分解し、**どこまでが観測で、どこから解釈（推論）か**を記録する。

---

## 1. 4層分解フレーム（定義）

| 層 | 定義 | 推論の有無 |
|---|---|---|
| **Explicitly Stated** | 公開ページに**文字どおり書かれている**こと | 推論なし（直接） |
| **Public Appeal** | それが**要請（お願い）という発話行為**であること | 推論なし（直接・発話行為の読み取り） |
| **Standing Appeal** | その要請が**常設・継続的**（日付つき緊急ではない）であること | 微推論（時間的性質の読み取り） |
| **Interpretation** | 「**これが今の binding なボトルネックだ／最も足りない**」という読み | **推論の起点** |

**境界:** Explicitly Stated・Public Appeal = 観測。Standing Appeal = 観測だが時間枠を導入。**Interpretation = ここから推論が始まる。**

---

## 2. Candidate A（資金）の分解

| 層 | 内容（観測 or 推論） | 種別 |
|---|---|---|
| **Explicitly Stated** | 寄付ページが存在し、寄付が税控除対象である旨が明示。運営資金の約7割が民間寄付と公開記載。 | 観測（事実） |
| **Public Appeal** | このページは寄付を**募っている**（発話行為＝要請）。 | 観測（発話行為） |
| **Standing Appeal** | 寄付募集は**常設**（日付つき緊急キャンペーンではなく恒常的な窓口）。 | 微推論（常設性の読み取り） |
| **Interpretation** | 「**資金が JAR の今の最大ボトルネックだ**／資金が今最も必要だ」 | **推論（ここから始まる）** |

- **観測できること:** JAR は公開で・継続的に寄付を募っている。
- **観測できないこと:** それが「今、最も足りない binding 制約」かどうか（需要規模・緊急度は voice-006 にない）。**Interpretation 層で推論が始まる。**

---

## 3. Candidate B（人手）の分解

| 層 | 内容 | 種別 |
|---|---|---|
| **Explicitly Stated** | ボランティア参加プログラム（One Action for Refugees 等）が公開で募集されている。 | 観測（事実） |
| **Public Appeal** | このページは人手（ボランティア）を**募っている**。 | 観測（発話行為） |
| **Standing Appeal** | ボランティア募集は**常設**（恒常的な参加窓口）。 | 微推論（常設性） |
| **Interpretation** | 「**人手が JAR の今のボトルネックだ**」 | **推論（ここから始まる）** |

- **観測できること:** JAR は公開で・継続的にボランティアを募っている。
- **観測できないこと:** どの活動の人手が・どれだけ足りないか。**Interpretation で推論が始まる。**

---

## 4. 検証結果 — X-4.5 仮説は支持される

> **A/B の推論境界は、Candidate の「内部」にある。**

```
Explicitly Stated │ Public Appeal │ Standing Appeal ┃ Interpretation
   観測               観測             微推論          ┃  推論
                                                      ┃
                          推論の起点 ────────────────┛
```

- **「Gateway Need は direct_observation」は、Standing Appeal 層まで**正しい。
- **Interpretation 層（=「これがボトルネックだ」）に入った瞬間、A/B でも推論が始まる。**
- よって X-4.5 の発見は支持される: **Gateway Need は monolithic な「直接観測」ではなく、内部に観測/推論の境界を持つ。**

---

## 5. 二種類の推論の区別（A/B と C/D/E は違う推論）

A/B の Interpretation と C/D/E の inference は、**どちらも推論だが対象が異なる**:

| | 推論の対象 | 主体の所在 | 危険度 |
|---|---|---|---|
| **A/B の Interpretation** | 「JAR 自身の今のボトルネックは資金/人手だ」 | **発話者（JAR）自身の状態** | **低**（語っている当事者組織についての推論） |
| **C/D/E の inference** | 「不在の難民個人が翻訳/法的支援を必要としている」 | **不在の第三者** | **中〜高**（声を持たない他者の Need の外部定義＝問題定義権力） |

**重要な区別:** A/B の推論は「**語っている本人（JAR）の優先度の推測**」——JAR は反論・訂正できる立場にいる。C/D/E の推論は「**不在の個人の Need の代弁**」——当事者は反論できない。**Saiyan Scouter 問題の核（問題定義権力）は後者にあり、A/B の Interpretation はそれより一段安全。** だが「推論ゼロ」ではない。

**H-4 の精緻化:** `scouter_risk: none`（A/B）は、より正確には **`very_low`**（Interpretation 層に入れば微推論あり・ただし対象は発話者自身）。境界は二値ではなく勾配。

---

## 6. Gateway Consent の分解（4層 × 同意）

X-4.5 R3 が露出させた「JAR は同意していない」を、4層で精密化する。**consent は一枚岩ではない。**

| 層 | その層が含意する consent | 状態 |
|---|---|---|
| **Explicitly Stated**（寄付/ボランティア募集の明示） | **不特定多数から寄付/人手を受け取ることへの同意** | **存在する**（公開募集はそれ自体が「受け取る」ことへの公開的同意） |
| **Public Appeal**（要請という発話） | 同上（要請＝受領の意思表示） | **存在する** |
| **Standing Appeal**（常設） | 継続的に受け取る意思 | **存在する** |
| **Interpretation → Mujin の構造への記録** | **Mujin の Cooperation 参加者として記録される／Mujin に代理表象されることへの同意** | **不在** |

**区別の核心:**
- **(a) Contribution を JAR に届けることへの consent = 存在する。** JAR は公開で寄付・人手を募っている＝それを受け取ることに公開的に同意している。**誰でも JAR に寄付・参加してよい**——これは JAR の公開要請が与える consent。
- **(b) JAR を Mujin の Cooperation/Registry に「参加者」として記録し、Mujin が JAR を代理表象することへの consent = 不在。** JAR はこの Trial を知らない。公開募集は「Mujin の構造に組み込まれること」への同意ではない。

→ **X-4.5 R3 の精密化:** 「JAR は同意していない」は不正確。正しくは「**JAR は寄付/人手の受領に同意しているが、Mujin に代理表象・参加者記録されることには同意していない**」。前者では一周の Contribution 段階は進められるが、後者（Cooperation に JAR を参加者として書く）には**別の組織 consent が要る**。

---

## 7. この検証が確定したこと（観察のみ・決定しない）

1. **A/B も Standing Appeal までは観測、Interpretation から推論。** 「Gateway Need = 完全な直接観測」ではない（X-4.5 支持）。
2. **A/B の推論は JAR 自身についての推測**であり、C/D/E（不在個人の代弁）より一段安全。Saiyan Scouter の核は C/D/E 側。
3. **`scouter_risk: none` は `very_low` に精緻化すべき**（H-4 の勾配化）。
4. **Gateway consent は二層に分かれる:** (a) 受領への consent = 公開募集が与える / (b) Mujin への代理表象 consent = 不在。
5. **安全に進められる範囲:** 「JAR の公開募集に応じる」までは (a) の consent 内。「JAR を Mujin の Cooperation 参加者として記録する」には (b) が要る——実行前の組織通知/同意。

---

## 8. やらなかったことの証明

- Gateway Need を作成・承認・却下していない。
- Gateway を選定していない（A/B は分解対象であって選定ではない）。
- Contribution を生成していない。
- C/D/E（個人 Need）に踏み込んでいない。
- すべて文書内の分解。データ/コード無変更。

---

*本文書は Gateway Need の観測/推論境界と Gateway consent の分解の観察記録であり、Need を作成・承認・却下せず、Gateway を選定せず、Contribution を生成しない。A/B の Interpretation 層に微推論があること、Gateway consent が「受領」と「代理表象」の二層に分かれることを記録した。Reach Gap は未解決であり、本文書もその解決を主張しない。*
