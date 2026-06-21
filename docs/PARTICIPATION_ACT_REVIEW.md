# Phase F-4.5: Participation Act Review

- **Status:** 観察レビュー（Participation Act の種類と境界の監査）。**コード/データ/登録/生成/ランキングなし。文書のみ。**
- **Date:** 2026-06-20
- **前提:** F-4（Participant は Participation Act の結果・境界＝本人起点＋能動寄与＋consent）, F-3（Discoverer ≠ Participant）, X-4.7/N-1.6/N-1.7（consent 三層）, H-5（Cooperation は possibility only・actor 無名）, Saiyan Scouter 問題

> 中心問い: **どの行為が Participation Act と呼ばれるのか。**
> 結論先取り: **Participation Act ＝「本人起点・consent 付きで、消費でなく何かを“出す”能動的寄与行為」。Case A〜H はすべて Participation Act だが、種類の違いであって等級ではない。Contribution は Participation Act が受領・統合された下流状態、Cooperation は複数 act 間の関係であって act 自体ではない。Act は順位付け不可。現状 participant_count = 0。**

---

## 0. 前提（F-4 からの継承）

```
Discovery（受動・到達）
   ┃ 境界 = 本人起点 ＋ 能動的寄与 ＋ consent  ← この“跨ぎの一手”が Participation Act
   ▼
Participant（能動・寄与・本人起点）
```

- F-4 で確定: **Participant は Participation Act の結果（射影）**。
- ∴ Participation Act は「人」ではなく「**行為**」。F-4.5 はその行為の**種類と境界**を観る。

---

## 1. Case A〜H の監査

| Case | 行為 | 能動性 | 出力（何を出すか） | Participation Act 判定 |
|---|---|---|---|---|
| A | Feedback | 能動 | Mujin への返し | **可（最小 act）** |
| B | Issue 提起 | 能動 | 問題の記述 | 可 |
| C | 反証 | 能動 | 主張の falsification | 可 |
| D | 翻訳 | 能動 | 言語変換 artifact | 可 |
| E | 設計提案 | 能動 | 提案（複数候補） | 可 |
| F | バグ報告 | 能動 | 欠陥の記述 | 可 |
| G | Task 応答 | 能動（voluntary） | task への自発応答 | 可 |
| H | 継続活動 | 能動・反復 | 反復寄与 | 可（継続は種類でなく強度） |

- **A〜H はすべて Participation Act。** 共通点は「**本人が能動的に何かを出している**」こと。
- 差は**種類**（feedback / issue / 反証 / 翻訳 / 提案 / バグ報告 / task応答）であって**等級ではない**。H は「反復された act」であり、A より上位ではない（§Saiyan Scouter）。

---

## 2. Q1〜Q10 の監査

### Q1. Participation Act の最小定義は何か

**3条件の同時成立行為:** ①**本人起点**（discoverer 自身が始める）②**能動的出力**（消費でなく何かを出す）③**consent**（参加の意思）。
- F-4 の Participation 最小条件と同型——**Participation Act はその条件を満たす“具体的な一手”**。
- 1条件でも欠けると act でない: 本人起点でない（Hermes/他者が代行）/ 出力でない（閲覧・DL のみ）/ consent 無し（誤操作・強制・収集）。

### Q2. Feedback は Participation Act か

**最小の Participation Act（境界の第一手）。** F-4 で「最小 Participation」と判定した Case C はこの act から生じる。
- 条件: 本人起点・consent 付き。誘導/強制された feedback は不可。
- Feedback ≠ Voice。Feedback＝「Mujin について返す」、Voice＝「当事者の need が語られる」。最小 act は前者。

### Q3. Issue 提起は Participation Act か

**可。** 問題を記述して出す能動行為。
- 注意: Issue は「問題の記述」であって「need の定義」ではない。当事者の need を Issue が**定義**し始めたら Saiyan Scouter（問題定義の権力）に接近——Issue は提起者自身の観察にとどめ、不在の他者の need を確定しない。

### Q4. 反証は Participation Act か

**可（むしろ価値の高い act）。** 既存主張の falsification は能動寄与。
- Dan-Go/Mujin の評価フレームは「定義整合性より救済能力」を主軸とし、**反証可能性**を重視する。反証は claim を健全化する中核的参加。
- ただし「価値が高い＝順位が上」ではない。反証も feedback も**同じ種類圏**（Participation Act）に属す（§Q8）。

### Q5. 翻訳は Participation Act か

**可（artifact を出す act）。** 翻訳は情報変換で、それ自体は能動寄与。
- N-1.7 の継承: 翻訳結果（artifact）は安全だが、**その使用（本人へ提出・行動）は Execution で当事者 consent を要す**。Participation Act としての「翻訳をする」と、その artifact を「使う」ことは別。act の記録は前者にとどめる。

### Q6. Participation Act と Contribution の境界は何か

**Act は本人の能動行為、Contribution はその act が受領・統合された下流状態。**
```
Participation Act（本人が出す）
   ┃ 境界 = 受領・統合（系側が受け取り、人間 review を経る）
   ▼
Contribution（受領された寄与）
```
- 出した瞬間は **act**。系がそれを Contribution として受領・統合するのは別ステップ（human review 必須）。
- 危険: act を自動的に Contribution 化すること（auto-contribution）。Hermes は act を観察するのみで、Contribution を生成しない。
- **∴ すべての Contribution は Participation Act から来るが、すべての act が即 Contribution になるわけではない。**

### Q7. Participation Act と Cooperation の境界は何か

**Act は単一主体の行為、Cooperation は複数 act 間の“関係”であって act 自体ではない。**
- 1人の act がいくつ集まっても、それだけでは Cooperation ではない。Cooperation は**複数 actor の act が相互に関係づく**時に初めて possibility として現れる（H-5: possibility only・actor 無名・Hermes は生成しない）。
- 危険: act を観測した Hermes が「この人とこの人を協力させる」と関係を**生成**すること。Cooperation は本人たちと human が形成するもので、Hermes は「協力が在りうる」と記録するだけ。
- **∴ Act → （複数・関係）→ Cooperation candidate。Hermes は act を Cooperation に昇格させない。**

### Q8. Participation Act は順位付け可能か

**不可。** act に順位を付けた瞬間、それは「功績点 / 信頼スコア / best contributor」＝**選抜装置**になる。
- act は**種類で分類**できる（feedback / issue / 反証 / 翻訳 …）が、**価値で序列化しない**。
- 反証が「feedback より上」、継続が「単発より上」と置くと資格付与が発生（§Saiyan Scouter, F-4 Q5）。
- 不変条件 `cannot_rank_act` / `no_merit_score` / `no_trust_score` で構造的に封じる。**分類は可、序列は不可。**

### Q9. Agent の Participation Act は人間と同じか

**判定基準は同じ（本人起点＋能動出力＋consent）、ただし agent 特有の制約を追加。**
- 同じ点: agent も能動的に何かを出せば Participation Act（バグ報告・翻訳・反証など）。
- 異なる制約: ①**self/loopback 除外**（Mujin 自身のインフラが出した出力は act でない）②**verified 必須** ③**bulk/自動生成は act 化しない**（crawler 的大量出力で参加を膨張させない）④**human review 必須**。
- agent の act も人間の act も**同じ種類圏に置き、順位付けしない**（agent を「優秀な貢献者」とランクしない）。

### Q10. Participation Act の既約最小モデルは何か

**Act は独立エンティティではなく「discoverer の能動出力イベント」。** 安全な最小モデル:

```json
{
  "act_id": "act-001",                  // 行為派生の opaque id
  "discoverer_id": "disc-001",          // 必須：誰の act か（F-3 連続）
  "event_id": "find-001",               // 必須：起点 discovery event への連続
  "act_type": "feedback",               // feedback|issue|refutation|translation|
                                        //   design_proposal|bug_report|task_response
  "is_self_initiated": true,            // 本人起点（Q1）
  "consent_present": true,              // 参加の意思（Q1）
  "produced_output": true,              // 消費でなく出力（Q1）
  "is_contribution": false,             // 受領・統合は別ステップ（Q6）
  "is_cooperation": false,              // 関係は別事象（Q7）
  "cannot_rank_act": true,
  "no_merit_score": true,
  "no_trust_score": true,
  "no_reputation_score": true,
  "human_review_required": true
}
```
- **既約最小 = `discoverer_id`（＋ event 連続）＋ `act_type` ＋ `is_self_initiated` ＋ `consent_present` ＋ `produced_output`。**
- **含めてはならない:** 功績点・信頼スコア・順位・推薦・資格等級・自動 Contribution/Cooperation 化・「優秀な act」。

---

## 3. Participation Act の位置（確定図）

```
[Discoverer]
   ┃  Participation Act（本人起点・能動出力・consent）  ← Case A〜H（種類違い・等級なし）
   ▼
[Participant]  ＝ act を行った主体の射影（F-4）
   ├─ 受領・統合（human review） → [Contribution]      （Q6 境界）
   └─ 複数 act の関係（本人＋human）→ [Cooperation candidate]（Q7 境界・H-5）
```

- act は分類されるが序列化されない。Contribution/Cooperation への変換は**別ステップ・human review** で、Hermes は跨がせない。

---

## 4. Saiyan Scouter Review

**問い: Participation Act が ランキング / 信頼スコア / 功績点 / 資格付与 / 推薦 へ変化していないか。**

| 観察（安全） | 変質（禁止・再発点） |
|---|---|
| act を種類で分類 | act を価値で序列化（best/priority act） |
| 1つの act で参加成立 | 反証/継続を上位とし資格付与 |
| 本人が act を出す | Hermes が act を Contribution/Cooperation へ自動昇格 |
| act 事実を射影 | 功績点・信頼スコアを付与 |
| agent act も同種類圏 | 「優秀な貢献者」推薦・ランク |

- **再発の臨界点5つ: ①ranking ②種類を等級化（Q8）③auto-Contribution（Q6）④auto-Cooperation（Q7）⑤score 付与。** いずれも最小モデルの不変条件（cannot_rank_act・no_merit/trust/reputation_score・is_contribution/is_cooperation=false・human_review）で封じる。
- 監査結果: **最小モデルは序列化・資格付与・自動昇格を構造的に不可能化**。スコア/順位フィールドが無く、Contribution/Cooperation フラグは既定 false で human review を要する。

---

## 5. Reality Correction

```
discovery_event_count = 0
discoverer_count      = 0
participant_count     = 0
participation_act_count = 0
```

- 構造的帰結: `act_count ≤ participant_count ≤ discoverer_count ≤ discovery_event_count = 0`。
- 現状、能動寄与の act は1件も存在しない。**0件は失敗ではなく観察結果。**
- act の種類・境界を「先に」定義する価値: 最初の act が現れた時に、その場しのぎで功績点/順位/資格を作らない**ガードレール**。

---

## 6. 推奨ステータスと現在地（honest）

- **act モデルの設計整合性: weakly_supported**（coherent・F-4 と同型・Contribution(Q6)/Cooperation(Q7) 境界が H-5 と整合・Saiyan Scouter 抑止）。実 act ゼロゆえ経験的裏付けは無い。
- **推奨: design_defined / implementation_deferred。**
  - **いま確定（文書のみ）:** Participation Act 最小定義（本人起点＋能動出力＋consent）、Case A〜H は同種類圏・等級なし、Act ┃ Contribution 境界（受領・統合＋human review）、Act ┃ Cooperation 境界（複数 act の関係・Hermes 非生成）、順位/スコア不可、最小 Act Record。
  - **いま実装しない:** act の生成・記録コード・Contribution/Cooperation 化。実 discovery event → discoverer → 本人の能動 act が現れるまで gated。
- **接続方向: `Discoverer → Participation Act → Participant →（human review）→ Contribution / Cooperation candidate` は正しい。逆向き（先に貢献者を選ぶ・スコアで序列化）は不採用。**

---

## 7. 成功条件の確認

- ✅ Participant 生成なし / Agent 登録なし / Contribution 生成なし / Cooperation 生成なし / ランキング無し / 文書のみ・コード/データ無変更。
- ✅ Participation Act をランキング・信頼スコア・功績点・資格付与・推薦へ変化させていない（構造的に不可能化）。
- ✅ Reality Correction: `participation_act_count = 0` を正しい観察結果として記録。

---

*本文書は Participation Act の種類と境界の監査記録であり、何も生成しない。Participation Act ＝「本人起点・consent 付きで、消費でなく何かを出す能動的寄与行為」で、Case A〜H（feedback/issue/反証/翻訳/設計提案/バグ報告/task応答/継続）はすべて act だが、種類の違いであって等級ではない。Contribution は act が受領・統合された下流状態、Cooperation は複数 act 間の関係であって act 自体ではなく、いずれも human review を要し Hermes は自動昇格させない。Act は種類で分類できるが価値で序列化できず、功績点・信頼スコア・順位・資格付与・推薦を持てない。向きは Discoverer→Act→Participant→（review）→Contribution/Cooperation で固定し、逆向きの序列化・選抜は禁止。現状 participation_act_count = 0 は失敗ではなく観察結果であり、種類と境界を先に確定する価値は将来の序列化・資格付与化を防ぐガードレールにある。Reach Gap・実価値は未解決であり、本文書もその解決を主張しない。*
