# Representation Boundary Review

- **Status:** 観察レビュー。X-4.6 の consent 二層分割を三層に精密化する。Need 作成・Gateway 選定・Contribution/Cooperation/Reality Feedback 生成なし。コード無変更。文書のみ。
- **Date:** 2026-06-13
- **検証対象:** 公開寄付募集 / 公開ボランティア募集 / 公開協力要請
- **前提:** [`GATEWAY_CONSENT_AND_BOTTLENECK_REVIEW.md`](GATEWAY_CONSENT_AND_BOTTLENECK_REVIEW.md)（X-4.6 §6: consent は「受領」と「代理表象」に分かれる）

> **核心:** 組織を Mujin の **Cooperation Participant として記録すること**と、組織が**公開で資源を募集していること**を混同しない。
> 公開募集は「受け取る」ことへの consent であって、「Mujin の構造に参加者として記録・代理表象される」ことへの consent ではない。

---

## 1. 三つの Consent の定義（段階）

| # | Consent 種別 | 何への同意か | 与えられ方 | バー |
|---|---|---|---|---|
| 1 | **Resource Acceptance Consent** | 不特定多数から**資源（資金・人手）を受け取る**こと | 公開募集そのものが与える | 最も低い |
| 2 | **Participation Consent** | **特定の協力的取り決めに当事者として参加**すること | 当事者がその取り決めに具体的に同意して初めて | 中 |
| 3 | **Representation Consent** | **第三者（Mujin）の記録・レジストリ・対外的構造に「参加者」として代理表象**されること | 当事者が表象自体に同意して初めて | 最も高い |

**入れ子（含意しない）関係:**
```
Resource Acceptance  ⊄  Participation  ⊄  Representation
（受領の同意は参加の同意を含意しない／参加の同意は表象の同意を含意しない）
```
低い consent があっても、高い consent は**自動的には生じない**。

---

## 2. 三つの公開行為 × 三つの Consent（マトリクス）

| 公開行為 | Resource Acceptance | Participation（Mujin の協力に） | Representation（Mujin の記録に） |
|---|---|---|---|
| **公開寄付募集** | ✅ 与える（資金の受領） | ❌ 与えない | ❌ 与えない |
| **公開ボランティア募集** | ✅ 与える（人手の受領・**JAR 自身の活動への**参加） | ❌ 与えない（後述の方向性に注意） | ❌ 与えない |
| **公開協力要請** | ✅（範囲内） | ⚠️ **部分的** — 当事者が**要請した範囲・条件**での参加に限る。任意の第三者が定義した協力への参加ではない | ❌ 与えない（記録・表象は別の同意） |

**読み方:**
- どの公開行為も **Resource Acceptance までは与える**。
- **Participation** は、公開協力要請が「部分的に・要請範囲で」与えるのみ。寄付/ボランティア募集は与えない。
- **Representation はどの公開行為も与えない。** 公開で募集していることは、Mujin の記録に参加者として名を載せられることへの同意ではない。

---

## 3. ボランティア募集の方向性（重要な落とし穴）

公開ボランティア募集には**参加の向き**の罠がある:

```
公開ボランティア募集が成立させる参加:
   Contribution provider ──参加──▶ JAR（組織）の活動
                                   （JAR が方向づける・JAR の内部）

Mujin の Cooperation 記録が主張する参加（X-4 Step 4）:
   JAR ──参加者として──▶ Mujin の Cooperation 構造
                         （Mujin が記録・表象する）
```

- **募集が与えるのは「協力者が JAR に参加する」consent**（下流・JAR が主体）。
- **Mujin が記録するのは「JAR が Mujin の協力に参加する」**（上流・Mujin が JAR を表象）。
- **二つは参加の向きが逆。** 前者の consent は後者を一切含意しない。「JAR がボランティアを募っている」から「JAR を Mujin の Cooperation 参加者に記録してよい」は導けない。

---

## 4. 混同してはならない二つの行為

| 行為 | 対象 | 必要な consent | voice-006 での状態 |
|---|---|---|---|
| **(α) 組織の公開募集に応じる**（資金/人手を JAR に届ける） | JAR が公開した受領窓口 | Resource Acceptance | **存在**（公開募集が与える） |
| **(β) 組織を Mujin の Cooperation Participant として記録する** | Mujin の append-only 公開記録 | **Representation** | **不在**（JAR は知らない） |

- **(α) と (β) は別の対象への別の行為。** (α) が可能でも (β) は不可。
- X-4 Step 4 が participants に「JAR public appeal」を入れるのは **(β)** であり、Representation Consent を要するが、それは**不在**。
- **Mujin の記録は公開・append-only・対外的**であり、そこに名を載ることは reputational な表象行為（X-4.5 R2: listing が正統性の裏書きに見える）。だから Representation は最も高いバーを持つ。

---

## 5. 安全な記録の形（観察・決定しない）

> 以下は「もし実行するなら」の観察であって、実行・決定ではない。

- **JAR は「参加者（participant）」ではなく「出典・参照（source / referenced public appeal）」として記録する**のが、consent に整合する形。
  - participant = Representation Consent 要 → 不在 → 記録しない。
  - source reference = 公開情報の出典の記載（事実）→ 表象ではない → 可。
- **Cooperation の participants は、Representation Consent を与えた主体のみ**（例: Contribution provider 本人、Mujin observer 自身）。第三者組織を本人の同意なく participant に入れない。
- **(α) の Contribution は、JAR を Mujin 構造に組み込まずに**、JAR の公開窓口へ直接行える（Mujin はそれを観察・参照するだけ）。

---

## 6. ADR / Saiyan Scouter との関係

- **ADR-005（当事者尊厳）の consent 階層の組織版:** ADR-005 は個人の同意を「active / pending / deferred」等で層化した。X-4.7 は**組織の同意を Resource/Participation/Representation で層化**——同じ「consent は一枚岩でない」原則の組織への適用。
- **Saiyan Scouter（不在の主体の代弁）の三階版:**
  - X-2.6: 個人（難民）が不在のまま代弁される。
  - X-4.5: 組織（JAR）が同意なく Cooperation に記録される。
  - X-4.7: その「記録」が **Representation（代理表象）** という最も高い consent を要する行為だと特定。
  - **共通構造:** 不在の主体を、その主体が与えていない consent のレベルで、構造に書き込む。Representation Consent の明示は、この再発を**最も上流で**塞ぐ。
- **Reality Correction との接続:** Mujin が JAR を participant として表象すると、JAR の正統性を Mujin が裏書きしたように見える（未検証組織なのに）。Representation Consent の不在を守ることは、Reality Correction（実在を偽らない）の consent 版でもある。

---

## 7. この検証が確定したこと

1. **Consent は三層**: Resource Acceptance ⊄ Participation ⊄ Representation。低層は高層を含意しない。
2. **公開募集が与えるのは Resource Acceptance のみ**（協力要請のみ Participation を部分的に）。**Representation はどの公開行為も与えない。**
3. **ボランティア募集の参加は向きが逆**（協力者→JAR であって JAR→Mujin ではない）。
4. **「公開募集に応じる(α)」と「Mujin 記録に participant として書く(β)」は別行為。** (α) は consent 内、(β) は Representation Consent 不在。
5. **安全形:** JAR は participant ではなく source/reference として記録。participants は Representation Consent を与えた主体のみ。

---

## 8. やらなかったことの証明

- Need を作成・承認・却下していない。
- Gateway を選定していない。
- Contribution / Cooperation / Reality Feedback を生成していない。
- 組織を participant として記録していない（むしろ「記録するな」を観察した）。
- コード/データ無変更。すべて文書内の分解。

---

*本文書は consent の三層（Resource Acceptance / Participation / Representation）の境界の観察記録であり、Need・Gateway・Contribution・Cooperation・Reality Feedback のいずれも生成しない。公開での資源募集は受領への consent であって、Mujin の記録に参加者として代理表象されることへの consent ではない——この境界を記録した。Reach Gap は未解決であり、本文書もその解決を主張しない。*
