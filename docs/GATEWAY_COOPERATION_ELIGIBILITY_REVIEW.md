# Gateway Cooperation Eligibility Review

- **Status:** 観察レビュー。X-4.7 の Representation Boundary を実装済みデータモデルへ写像する。Gateway 選定・Need/Contribution/Cooperation 生成なし。コード無変更。文書のみ。
- **Date:** 2026-06-13
- **対象:** `voice-006`（JAR / https://www.refugee.or.jp/support/ ）
- **前提:** [`REPRESENTATION_BOUNDARY_REVIEW.md`](REPRESENTATION_BOUNDARY_REVIEW.md)（X-4.7: consent は Resource Acceptance ⊄ Participation ⊄ Representation）

> 目的: 5つの記録位置（Source / Reference / Gateway Candidate / Cooperation Participant / Represented Actor）について、(1) 記録可能か (2) どの consent が必要か (3) 現時点で不足は何か、を整理する。
> **これは記録可能範囲の観察であって、記録・選定・生成ではない。**

---

## 0. 写像の原則

X-4.7 の三層 consent を、実装済みの具体的な記録位置に対応づける:

| consent 層 | 記録行為の性質 | データモデル上の位置 |
|---|---|---|
| （consent 不要：公開事実の引用） | 引用・参照 | Source / Reference |
| **Representation** | Mujin の actor として列挙 | Gateway Candidate（registry 登録） |
| **Participation + Representation** | Mujin の協力の当事者として列挙 | Cooperation Participant |
| **完全な Representation / 代理権** | Mujin が JAR を代弁・表象 | Represented Actor |

---

## 1. 位置別の整理（voice-006 / JAR）

### ① Source（出典）
- **データモデル位置:** `voice_records.jsonl` の `source_url` / `source_type`（voice-006 は既に `source_url=refugee.or.jp/support` を保持）。
- **(1) 記録可能か:** ✅ **可能（既に記録済み）**。公開 URL の引用は事実の記載。
- **(2) 必要 consent:** **なし**。公開情報の出典を引くことは Representation ではない。
- **(3) 不足:** なし。ただし Reality Correction として、実行前に URL の現行性を人間が再確認すべき。

### ② Reference（参照）
- **データモデル位置:** 他レコードからの読み取り専用ポインタ（例: agent_commons の observation `source_url`、または注記としての「JAR 公開要請を参照」）。
- **(1) 記録可能か:** ✅ **可能**。公開情報への参照。
- **(2) 必要 consent:** **なし**（公開事実の参照）。
- **(3) 不足:** なし。ただし `listing_is_not_endorsement` の枠で「参照であって推薦ではない」と明示する必要（X-4.5 R2）。

### ③ Gateway Candidate（Gateway 候補 = registry 登録）
- **データモデル位置:** `gateway_registry.jsonl` の gateway レコード（`register_gateway`）。登録された gateway が proposal の `gateway_candidates` に現れる。
- **(1) 記録可能か:** ⚠️ **技術的には可能だが、consent 上は不可**。registry への登録は「JAR を Mujin の actor（接続者）として列挙する」行為＝**Representation**。
- **(2) 必要 consent:** **Representation Consent**。JAR を Mujin のレジストリに gateway として載せることは、JAR の名を Mujin の構造に表象する。
- **(3) 不足:**
  - JAR の Representation Consent（**不在** — JAR はこの登録を知らない）。
  - **データモデルに組織 consent のフィールドが存在しない**（後述 §3）。
  - 正直な検証状態（Reality Correction: JAR は Mujin が検証した組織ではない）。

### ④ Cooperation Participant（協力の参加者）
- **データモデル位置:** `cooperation_commons.jsonl` の `participants[]`（`register_cooperation`）。
- **(1) 記録可能か:** ⚠️ **技術的には可能だが、consent 上は不可**。participant として列挙は **Participation + Representation** の両方を主張する。
- **(2) 必要 consent:** **Participation Consent**（JAR が当事者として協力に参加する同意）＋ **Representation Consent**（Mujin の記録に参加者として表象される同意）。
- **(3) 不足:**
  - JAR の Participation Consent（**不在**）。
  - JAR の Representation Consent（**不在**）。
  - 参加の向きの不整合（X-4.7 §3: 公開募集は「協力者→JAR」を与えるが、ここで主張されるのは「JAR→Mujin」で逆）。

### ⑤ Represented Actor（代理表象される主体）
- **データモデル位置:** 明示的なレコードはないが、Mujin が JAR の Need・状態・優先度を**代弁して記述する**こと全般（例: Need を JAR の代わりに定義する、JAR の bottleneck を断定する）。
- **(1) 記録可能か:** ❌ **記録すべきでない**。
- **(2) 必要 consent:** **完全な Representation / 代理権の consent**。
- **(3) 不足:** JAR の明示的な代理権付与（**不在**）。加えて、これは X-3.5/H-4 で確定した「不在主体の Need を外部定義しない」原則にも抵触しうる（C/D/E への滑り込み）。**consent があっても慎重であるべき領域。**

---

## 2. データモデル上の境界線

```
   引用・参照（consent 不要）        ┃   表象（consent 必要・現状不在）
   ────────────────────────────────┃────────────────────────────────────
   ① Source   ② Reference          ┃  ③ Gateway Candidate
                                    ┃  ④ Cooperation Participant
                                    ┃  ⑤ Represented Actor
                                    ┃
              記録可能（今）         ┃  Representation Consent が要・不在
```

- **現時点で（新たな consent なしに）記録可能なのは ① Source と ② Reference のみ。**
- **③④⑤ は Representation（または Participation+Representation）Consent を要し、それは voice-006 について不在。**
- **境界は Reference と Gateway Candidate の間に落ちる。** registry 登録の時点で、引用から表象へ越える。

---

## 3. 現時点で不足しているもの（データモデルの欠落）

> 観察であって、追加提案ではない。

- **組織 consent を表現するフィールドが、`gateway_registry.jsonl` にも `cooperation_commons.jsonl` にも存在しない。**
  - 既存の不変条件（`gateway_registration_is_not_certification`, `cooperation_is_not_command` 等）は **Mujin 自身の主張の制限**を表現するが、**被表象組織がその列挙に同意したか**は表現できない。
  - つまり現モデルは「Mujin はこの gateway を検証していない」とは言えるが、「この gateway は載ることに同意した」とは言えない。
- **結果:** ③④ は技術的に書けてしまう（ガードがない）が、書けば Representation Consent 不在のまま JAR を表象する。**データモデルが consent 境界を強制していない。**
- **不足の核心:** Representation Consent を記録・要求する仕組み（組織 consent ゲート）。これが無いため、現状は「書かない」という**運用規律**でのみ境界を守るしかない。

---

## 4. voice-006 について今安全に記録できる範囲

- ✅ **Source:** 既に voice-006 が JAR 公開要請を出典として保持（追加不要）。
- ✅ **Reference:** 他の観察レコードから JAR 公開要請を「参照（出典・非推薦）」として指すこと。
- ❌ **Gateway 登録:** JAR を gateway として登録しない（Representation Consent 不在）。
- ❌ **Cooperation 参加者:** JAR を participant に入れない（Participation+Representation 不在）。
- ❌ **代理表象:** JAR の Need・bottleneck を Mujin が断定的に代弁しない。

> X-4.7 §5 の「安全な記録の形」と一致: **JAR は participant ではなく source/reference として記録する。**

---

## 5. Reality Correction / ADR-005 / Saiyan Scouter との関係

- **Reality Correction:** ③ Gateway 登録は、Jammy House/D.R.A. の訂正（未検証を稼働中と偽った）と同根。consent も検証も無いまま JAR を gateway として載せれば、同じ過ち（正統性の無断裏書き）を繰り返す。①② に留まることがその回避。
- **ADR-005（当事者尊厳の consent 層化）:** 本レビューはその**組織版の写像**。個人 consent（active/pending/deferred）に対応する組織 consent（Resource/Participation/Representation）を、データモデルの記録位置に対応づけた。
- **Saiyan Scouter:** ⑤ Represented Actor は、不在主体の代弁＝問題定義権力の最も濃い形。データモデル上「ここには書かない」を明示することが、再発の最上流の防壁。

---

## 6. やらなかったことの証明

- Gateway を登録・選定していない（③ は「書かない」と観察したのみ）。
- Need を生成していない。
- Contribution / Cooperation / Reality Feedback を生成していない。
- 組織を participant として記録していない。
- コード/データ無変更。すべて文書内の写像。

---

*本文書は Representation Boundary のデータモデルへの写像の観察記録であり、Gateway 選定・Need・Contribution・Cooperation の生成を含まない。現時点で consent なしに安全に記録できるのは Source と Reference のみで、Gateway Candidate 以降は Representation Consent（不在）を要する——その境界とデータモデルの欠落（組織 consent フィールドの不在）を記録した。Reach Gap は未解決であり、本文書もその解決を主張しない。*
