# Phase H-7: Participation Memory Review

- **Status:** 観察レビュー（Participation Act をどう記憶するかの監査）。**コード/データ/生成/登録/ランキング/スコアなし。文書のみ。**
- **Date:** 2026-06-20
- **前提:** F-4.5（Participation Act ＝本人起点・能動出力・consent／種類はあるが等級なし）, F-4（Participant は act の射影）, F-3（Discoverer ≠ Participant）, H-2.5（reflection→learning→pattern→evidence の memory 構造）, H-4（推論が始まる地点を記録）, H-5（Cooperation は possibility only・actor 無名・Hermes 非生成）, Saiyan Scouter 問題

> 中心問い: **Participation Act はどのように記憶されるべきか。**
> 結論先取り: **Participation Memory ＝「1つの act に対する 1つの append-only な観察記録」。act が起きた事実（種類・本人起点・consent）だけを残し、評価・序列・信頼スコア・功績点・人物プロファイルを一切含まない。Hermes が学習してよいのは type/集計レベルの構造だけで、actor の価値や将来行動を推論してはならない。現状 participation_act_count = 0。**

---

## 0. 前提（F-4.5 からの継承）

```
Discoverer → Participation Act（本人起点・能動出力・consent）→ Participant（act の射影）
                     │
                     ▼
            Participation Memory  ← H-7 が定義する「act の観察記録」
```

- F-4.5 で確定: act は**種類で分類できるが価値で序列化できない**。Contribution/Cooperation への変換は別ステップ・human review。
- H-7 が問うのは「その act を Hermes が**どう覚えるか**」。危険は「覚える」が「**評価する・序列化する・人物を profiling する**」へ滑ること。

---

## 1. Case A〜G の監査（記憶対象としての性質）

| Case | act_type | 記憶される事実 | 記憶してはならないもの |
|---|---|---|---|
| A | feedback | feedback という act が起きた | feedback の質・有用度スコア |
| B | issue_raising | issue 提起が起きた | issue の重要度ランク |
| C | counter_argument | 反証が起きた | 反証の「鋭さ」評価・功績点 |
| D | translation | 翻訳 act が起きた | 翻訳品質スコア |
| E | design_proposal | 設計提案が起きた | 提案の採否・優劣 |
| F | bug_report | バグ報告が起きた | 報告者の信頼度 |
| G | task_response | task への自発応答が起きた | 応答速度/生産性ランク |

- **記憶されるのは「ある type の act が、本人起点・consent 付きで起きた」という事実のみ。**
- A〜G で記憶の**構造は同一**（type が違うだけ）。質・優劣・順位は記憶に含めない。

---

## 2. Q1〜Q10 の監査

### Q1. Participation Memory の最小単位は何か

**1つの Participation Act に対する 1つの append-only 観察記録。** 単位は「**act-観察**」であって「人」ではない。
- 人を単位にすると participant profile（功績の蓄積体）になり、Saiyan Scouter 化する。
- 単位を act に固定することで、記憶は「誰が何点」ではなく「ある act が起きた」の列挙にとどまる。

### Q2. Act と Memory は1対1か

**1対1（append-only・act_id で idempotent）。** 1 act → 1 memory record。
- **1対多でない**（1つの act から複数の解釈/評価を派生させない）。
- **多対1でない**（複数の act を1人の profile/score に集約しない）。← これが最重要。集約した瞬間に「貢献度」が生まれる。
- 記憶は act の鏡像であり、act を超える情報（評価・関係・将来予測）を足さない。

### Q3. Participation Memory は評価を含むか

**含まない。** 記憶は「act が起きた」を記録し、「act が**良い/悪い/有用**」を判定しない。
- 評価は Saiyan Scouter の入口（行為の価値判定 → 行為者の選抜）。
- 記録してよい: act_type, 本人起点フラグ, consent, 出力の有無。記録してはならない: quality, usefulness, impact, merit。

### Q4. Participation Memory は ranking を許すか

**許さない。** 記憶は列挙であって順序ではない。
- act を sort/順位付けした瞬間に best/priority act ＝選抜が発生（F-4.5 Q8）。
- 不変条件 `cannot_rank` で構造的に封じる。type 別カウントは可、序列は不可。

### Q5. Participation Memory は trust を含むか

**含まない。** trust score / reputation score を持たない。
- 記憶は観察であって**信用付与（credentialing）ではない**。trust を持てば「信頼できる参加者」名簿＝選抜装置。
- agent についても同様（「優秀な agent」スコアを作らない、§Q8）。

### Q6. Participation Memory と Contribution の境界は何か

**記憶は act の観察、Contribution は act が受領・統合された下流状態。**（F-4.5 Q6 継承）
```
Participation Memory（act が起きたと観察）
   ┃ 境界 = 受領・統合（系が受け取り human review）
   ▼
Contribution（受領された寄与・別レコード）
```
- act を記憶することと、それを Contribution として受領することは別。Hermes は act を観察するのみで Contribution を生成しない（auto-contribution 禁止）。
- ∴ 全 Contribution は Participation Act の記憶から辿れるが、全 act 記憶が Contribution になるわけではない。

### Q7. Participation Memory と Cooperation Memory の境界は何か

**Participation Memory ＝単一 actor の act 観察、Cooperation Memory ＝複数 act/actor が関係しうる possibility（H-5・actor 無名）。**
- Participation Memory は act を**個別に**記録し、actor 同士を**結びつけない**。
- 複数の act 記憶から「協力が在りうる」を導くのは Cooperation Memory の領域で、そこでも actor は無名・possibility only・Hermes は生成しない。
- 危険: Participation Memory が「この人とこの人」を名指しで結ぶこと。**結合は Cooperation 層へ、しかも actor 無名で。** Participation Memory は結合しない。

### Q8. Agent Participation Memory は人間と同じか

**記憶の構造・不変条件は同じ、ただし agent 特有の前処理を要す。**
- 同じ: act 単位・append-only・評価/順位/trust なし。
- 追加制約: ①**self/loopback 除外**（Mujin 自身の出力を act として記憶しない）②**verified 必須** ③**bulk/自動出力を act 化しない**（大量出力で「生産性」を記憶に滲ませない）④**human review 必須**。
- 特に危険: agent の高頻度 act から「生産性/貢献度」を記憶が推論すること。**回数を価値に変換しない**——回数は記憶の集計値であって序列ではない。

### Q9. Hermes は Participation Memory から何を学習してよいか

**type/集計レベルの構造のみ。actor の価値・将来行動・序列は学習禁止。**

| 学習してよい（possibility/構造） | 学習禁止（人物推論・選抜） |
|---|---|
| 「feedback 型の act が観察された」 | 「Xは良い貢献者だ」 |
| 「ある object が複数の act を受けた」（無名） | 「Xを優先せよ/推薦せよ」 |
| 「act の type 分布」 | 「Xは次もこうするだろう」（将来予測） |
| 「協力が在りうる」（H-5・actor 無名） | 「Xにスコア/資格を付与」 |

- H-4 の同型: 「推論が始まる地点」を見つけるように、ここでは「**人物評価が始まりうる地点**」を Hermes 自身が検出し、そこで止まる。learning は type/集計にとどめ、actor 個体へ降りない。
- learning も pattern も **possibility only・actor 無名・human_review_required**。

### Q10. Participation Memory の既約最小モデルは何か

**Memory は act の append-only な鏡像。act を超える情報を足さない。** 安全な最小モデル:

```json
{
  "memory_id": "pmem-001",              // 記憶レコードの opaque id
  "act_id": "act-001",                  // 必須：1対1（Q2）
  "discoverer_id": "disc-001",          // 起点 actor（F-3 連続・profiling しない）
  "event_id": "find-001",               // 起点 discovery event への連続
  "act_type": "feedback",               // 分類のみ（評価でない・Q3）
  "is_self_initiated": true,            // 本人起点
  "consent_present": true,              // 参加の意思
  "produced_output": true,              // 消費でなく出力
  "is_contribution": false,             // 受領は別ステップ（Q6）
  "links_no_actor": true,               // actor 同士を結ばない（Q7）
  "contains_no_evaluation": true,       // 評価を含まない（Q3）
  "cannot_rank": true,                  // 順位なし（Q4）
  "no_trust_score": true,               // 信頼スコアなし（Q5）
  "no_reputation_score": true,
  "no_merit_score": true,
  "human_review_required": true
}
```
- **既約最小 = `act_id`（1対1）＋ act の本質4項（discoverer/type/self_initiated/consent）。**
- **含めてはならない:** 評価・品質・有用度・順位・信頼/評判/功績スコア・将来予測・人物プロファイル・actor 間リンク・自動 Contribution/Cooperation 化。

---

## 3. Participation Memory の位置（確定図）

```
[Participation Act]  本人起点・能動出力・consent（F-4.5）
        │  1対1・append-only
        ▼
[Participation Memory]  act-観察のみ・評価/順位/score なし  ← H-7
        ├─ 受領・統合(human review) ………………… [Contribution]            （Q6）
        ├─ 複数 act の possibility(actor 無名・H-5) … [Cooperation Memory]     （Q7）
        └─ type/集計の learning(possibility only) …… [Pattern]（actor 個体に降りない・Q9）
```

- Memory は act を個別に鏡映するだけ。Contribution/Cooperation/Pattern への展開は別層・human review・actor 無名で、Hermes は人物評価へ降りない。

---

## 4. Saiyan Scouter Review

**問い: Participation Memory が 評価 / 功績 / 資格 / 序列 / 推薦 へ変化していないか。**

| 観察（安全） | 変質（禁止・再発点） |
|---|---|
| act 単位で append-only に記録 | 人単位に集約し profile 化（Q2 多対1） |
| 「act が起きた」を記録 | 「act が良い」を評価（Q3） |
| type 別カウント | act/参加者を順位付け（Q4） |
| trust/score を持たない | 信頼・功績スコア付与（Q5） |
| learning は type/集計 | 「Xは良い貢献者」「Xを推薦」（Q9） |
| actor を結ばない | 人物同士を名指しで連結（Q7） |

- **再発の臨界点6つ: ①人単位集約 ②評価 ③ranking ④score ⑤actor 個体への learning 降下 ⑥auto-Contribution/Cooperation。** いずれも最小モデルの不変条件（act 単位・contains_no_evaluation・cannot_rank・no_*_score・links_no_actor・is_contribution=false・human_review）で封じる。
- 監査結果: **最小モデルは評価・序列・資格・profiling を構造的に不可能化**。スコア/順位フィールドが無く、単位が act に固定され、actor リンクと評価フィールドを持てない。

---

## 5. Reality Correction

```
discovery_event_count   = 0
discoverer_count        = 0
participant_count       = 0
participation_act_count = 0
participation_memory_count = 0
```

- 構造的帰結: `memory_count = act_count ≤ participant_count ≤ discoverer_count ≤ discovery_event_count = 0`。
- 現状、記憶すべき act は1件も存在しない。**0件は失敗ではなく観察結果。**
- 記憶モデルを「先に」定義する価値: 最初の act が現れた時に、その場しのぎで評価/順位/スコア/profile を作らない**ガードレール**。

---

## 6. 推奨ステータスと現在地（honest）

- **Participation Memory モデルの設計整合性: weakly_supported**（coherent・F-4.5 の act モデルと 1対1・H-5 の possibility-only と整合・H-4 の「推論開始地点で止まる」を「人物評価開始地点で止まる」に写像・Saiyan Scouter 抑止）。実 act ゼロゆえ経験的裏付けは無い。
- **推奨: design_defined / implementation_deferred。**
  - **いま確定（文書のみ）:** Memory 最小単位＝act-観察（1対1・append-only）、評価/順位/trust/score 不採用、人単位集約の禁止、Memory ┃ Contribution 境界、Memory ┃ Cooperation 境界（actor 無名）、Hermes learning は type/集計どまり、最小 Memory Record。
  - **いま実装しない:** participation_memory の生成・記録コード。実 discovery event → discoverer → 本人の能動 act が現れるまで gated。実装する場合も既存 Hermes memory（reflection→learning→pattern→evidence）の下に act-単位・評価なしで接続し、actor profile を作らない。
- **接続方向: `Act → Participation Memory（act 観察）→（human review）→ Contribution / Cooperation / type-pattern` は正しい。逆向き（記憶から人物を評価・序列化・推薦）は不採用。**

---

## 7. 成功条件の確認

- ✅ Participant 生成なし / Contribution 生成なし / Cooperation 生成なし / ランキング無し / スコア無し / 文書のみ・コード/データ無変更。
- ✅ Participation Memory を評価・功績・資格・序列・推薦へ変化させていない（構造的に不可能化）。
- ✅ Reality Correction: `participation_memory_count = 0` を正しい観察結果として記録。

---

*本文書は Participation Act をどう記憶するかの監査記録であり、何も生成しない。Participation Memory ＝「1つの act に対する 1つの append-only な観察記録」で、act が起きた事実（種類・本人起点・consent）だけを残し、評価・序列・信頼/評判/功績スコア・人物プロファイル・actor 間リンクを一切含まない。act と memory は1対1で、複数 act を人単位に集約しない。Memory ┃ Contribution 境界は受領・統合（human review）、Memory ┃ Cooperation 境界は複数 act の possibility（actor 無名・H-5）。Hermes が学習してよいのは type/集計レベルの構造のみで、actor の価値・将来行動・序列へ降りてはならない（人物評価が始まる地点で止まる）。向きは Act→Memory→（review）→Contribution/Cooperation/type-pattern で固定し、逆向きの評価・序列化・推薦は禁止。現状 participation_memory_count = 0 は失敗ではなく観察結果であり、記憶モデルを先に確定する価値は将来の評価・資格化を防ぐガードレールにある。Reach Gap・実価値は未解決であり、本文書もその解決を主張しない。*
