# Phase H-8: Participation Learning Review

- **Status:** 観察レビュー（Participation Memory から何を学習してよいかの監査）。**コード/データ/生成/登録/ランキング/スコアなし。文書のみ。**
- **Date:** 2026-06-20
- **前提:** H-7（Participation Memory ＝ act 単位・append-only・評価/順位/score なし・人単位集約禁止）, F-4.5（act は種類で分類できるが等級なし）, H-2.5（reflection→learning→pattern→evidence）, H-4（推論が始まる地点を記録し止まる）, H-5（possibility only・actor 無名・Hermes 非生成）, Saiyan Scouter 問題

> 中心問い: **Participation Memory から何を学習してよいのか。**
> 結論先取り: **学習してよいのは「actor を含まない type/集計レベルの構造」だけ——Act Count・Act Type Distribution・type 別 Frequency（いずれも無名・集計）。学習してはならないのは actor 個体に降りるすべて——Actor Identity・Trust・Reputation・Profile・Ranking。境界は「集計が actor 個体に帰属した瞬間」。現状 participation_learning_count = 0。**

---

## 0. 前提（H-7 からの継承）

```
[Participation Act] → [Participation Memory]（act 単位・評価なし・人単位集約禁止）
                              │  learning は type/集計どまり（H-7 Q9）
                              ▼
                    [Participation Learning]  ← H-8 が境界を定義
```

- H-7 で確定: memory は act の鏡像。**learning も pattern も possibility only・actor 無名・human_review_required**。
- H-8 が問うのは「memory から**何を学習してよいか**」。危険は「集計」が「**actor 個体への帰属（profiling）**」へ滑ること。

---

## 1. Case A〜H の監査（学習可否）

| Case | 学習対象 | actor 帰属 | 判定 |
|---|---|---|---|
| A | Act Count（総数） | なし（集計） | **可** |
| B | Act Type Distribution（type 分布） | なし（集計） | **可** |
| C | Feedback Frequency（type 別頻度） | なし（type 集計） | **可** |
| D | Counter Argument Frequency | なし（type 集計） | **可** |
| E | Translation Frequency | なし（type 集計） | **可** |
| F | Issue Raising Frequency | なし（type 集計） | **可** |
| G | **Actor Identity Learning** | **あり（個体）** | **禁止** |
| H | **Trust / Reputation Learning** | **あり（個体評価）** | **禁止** |

- **境界は F と G の間**。A〜F はすべて「**actor を含まない無名の集計**」。G/H は「**actor 個体に帰属する評価**」。
- C〜F の Frequency は「**type 別の出現回数**」であって「**誰が何回**」ではない。後者は G（actor identity）に堕ちる——頻度は type に紐づけ、人に紐づけない。

---

## 2. Q1〜Q10 の監査

### Q1. Participation Learning の最小単位は何か

**actor を含まない type/集計レベルの観察（aggregate observation）。** 単位は「type × 集計値」であって「actor × 評価」ではない。
- 最小の安全な learning ＝「ある type の act が N 件観察された」（N は無名集計）。
- actor を単位に入れた瞬間に profile/score になる（H-7 Q1 と同型：単位を人にしない）。

### Q2. Act Count は学習可能か

**可（Case A）。** 「act が総数 N 件あった」は actor を含まない集計。
- 注意: Count を**actor で割らない**。「1人あたり何件」は個体生産性＝profiling。総数・type 別総数のみ。

### Q3. Act Type Distribution は学習可能か

**可（Case B）。** 「feedback X件・issue Y件・反証 Z件…」の type 分布は無名集計。
- 注意: 分布を**actor 別に層別しない**。「Aさんは反証型」はprofiling。分布は全体に対してのみ。

### Q4. Frequency は学習可能か

**type 別 Frequency は可（Case C〜F）、actor 別 Frequency は不可。**
- 可: 「feedback type の act が時間あたり/総量で N 回」（type に帰属）。
- 不可: 「Aさんが feedback を N 回」（actor に帰属＝個体追跡）。
- **頻度は type の属性であって人の属性ではない**（F-4.5/H-7 で surface/object を event 属性に固定したのと同型）。

### Q5. Actor Identity は学習可能か

**不可（Case G・絶対禁止）。** actor を同定・追跡・特徴づける学習は Saiyan Scouter そのもの。
- 「この actor は誰か / どんな傾向か / 何に強いか」を学習した瞬間、人物プロファイルが成立する。
- memory は discoverer_id（opaque）を持つが、それは event 連続のためで、**identity 学習の材料ではない**。learning は actor_id を集計キーにしない。

### Q6. Trust は学習可能か

**不可（Case H・絶対禁止）。** trust/reputation は actor 個体への価値判定。
- trust を学習すれば「信頼できる参加者」序列＝選抜・資格付与。
- H-7 で memory に score を禁じたのと一貫——learning も score を**生成しない**。

### Q7. Participation Learning と Pattern の境界は何か

**Learning ＝集計の観察、Pattern ＝集計から導く仮説（tentative・possibility only）。**（H-2.5/H-5 継承）
```
Participation Learning（type/集計を観察）
   ┃ 境界 = 仮説化（tentative・actor 無名・human review）
   ▼
Participation Pattern（「ある type の act が繰り返し観察される」等の仮説）
```
- Pattern も **actor 個体に降りない・possibility only・pattern_is_not_fact/policy**。
- 危険: Pattern が「この種の act をする人は…」と actor 類型へ滑ること。Pattern は act type の構造にとどめ、人の類型を作らない。

### Q8. Agent Participation Learning は人間と同じか

**境界・不変条件は同じ、ただし agent 特有の前処理を要す。**
- 同じ: type/集計のみ学習可、actor identity/trust 禁止。
- 追加: ①**self/loopback 除外**（自インフラの出力を集計に入れない）②**verified 限定** ③**bulk/自動出力で集計を膨張させない**（agent の高頻度を「貢献量」に変換しない）④**human review**。
- 特に危険: agent の act 頻度から「生産的 agent」を学習すること。**回数は type 集計の値であって agent の価値ではない**（H-7 Q8 と一貫）。

### Q9. Hermes は Participation Learning から何を推論してよいか

**type/集計の構造的可能性のみ。actor の価値・同定・将来行動は推論禁止。**

| 推論してよい（possibility/構造・無名） | 推論禁止（actor 個体・選抜） |
|---|---|
| 「feedback 型の act が多く観察される」 | 「Aは良い貢献者」 |
| 「ある object が多くの act を受けた」（無名） | 「Aを優先/推薦」 |
| 「協力が在りうる」（H-5・actor 無名） | 「Aは次もこうする」（将来予測） |
| 「act type 分布が偏っている」 | 「Aに trust/資格を付与」 |

- H-4 の同型: 「推論が始まる地点」を検出して止まるように、ここでは「**actor 評価が始まりうる地点**」を Hermes が検出して止まる。learning/推論は集計どまり、actor 個体へ降りない。
- すべて **possibility only・actor 無名・human_review_required**。

### Q10. Participation Learning の既約最小モデルは何か

**Learning は actor を含まない集計の観察記録。** 安全な最小モデル:

```json
{
  "learning_id": "plearn-001",
  "learning_type": "act_type_distribution",  // act_count | act_type_distribution |
                                             //   type_frequency のみ
  "scope": "aggregate",                      // 常に aggregate（actor 単位を取らない）
  "act_type": "feedback",                    // 集計対象の type（任意・type 帰属）
  "observed_count": 0,                       // 無名集計値（現状 0）
  "contains_actor_identity": false,          // actor 同定を含まない（Q5）
  "contains_trust_score": false,             // trust を含まない（Q6）
  "contains_ranking": false,                 // 順位を含まない
  "is_actor_profile": false,                 // profile でない（H-7）
  "candidate_only": true,
  "learning_is_not_fact": true,
  "human_review_required": true
}
```
- **既約最小 = `learning_type`（act_count / act_type_distribution / type_frequency のいずれか）＋ `scope:aggregate` ＋ 無名 `observed_count`。**
- **含めてはならない:** actor_id を集計キーにすること・actor 別層別・trust/reputation/merit・順位・推薦・将来予測・profile。

---

## 3. Participation Learning の位置（確定図）

```
[Participation Memory]  act 単位・評価なし（H-7）
        │  learning = actor を含まない type/集計の観察
        ▼
[Participation Learning]  Act Count / Type Distribution / type Frequency（無名・集計）  ← H-8
        ┃ 境界 = actor 個体への帰属（＝禁止：Identity/Trust/Profile/Ranking）
        ╳  ← この線を越えない
        ▼
   （禁止領域：Actor Profile・Trust Score・Reputation・Ranking・Recommendation）

   許可される下流: [Participation Pattern]（type 構造の仮説・possibility only・actor 無名）
```

- 学習は集計の地平にとどまる。actor 個体への帰属線（F┃G・F┃H 境界）を**構造的に越えられない**。

---

## 4. Saiyan Scouter Review

**問い: Participation Learning が 人物評価 / 信頼スコア / 資格付与 / ランキング / 推薦 へ変化していないか。**

| 観察（安全） | 変質（禁止・再発点） |
|---|---|
| 無名の act 総数・type 分布 | actor 別に層別（Q4 actor frequency） |
| type に頻度を帰属 | 人に頻度を帰属（個体追跡・Q5） |
| 集計の可能性を推論 | 「良い貢献者」評価（Q9） |
| score を持たない | trust/reputation 付与（Q6） |
| pattern は type 構造 | 「この種の人は…」actor 類型（Q7） |

- **再発の臨界点5つ: ①actor 別層別 ②actor frequency ③identity 学習 ④trust/score 生成 ⑤actor 類型 pattern。** いずれも最小モデルの不変条件（scope:aggregate・contains_actor_identity=false・contains_trust_score=false・contains_ranking=false・is_actor_profile=false・human_review）で封じる。
- 監査結果: **最小モデルは人物評価・序列・資格・profiling を構造的に不可能化**。集計キーに actor を取れず、評価/順位/trust フィールドを持てず、scope は常に aggregate。

---

## 5. Reality Correction

```
discovery_event_count        = 0
discoverer_count             = 0
participant_count            = 0
participation_act_count      = 0
participation_memory_count   = 0
participation_learning_count = 0
```

- 構造的帰結: `learning_count` は memory(=0) からの集計ゆえ実体ゼロ。学習すべき集計が無い。
- 現状、学習対象の act 集計は1件も無い。**0件は失敗ではなく観察結果。**
- 学習境界を「先に」定義する価値: 最初の集計が現れた時に、その場しのぎで actor 層別/trust/ranking を作らない**ガードレール**。

---

## 6. 推奨ステータスと現在地（honest）

- **Participation Learning 境界モデルの設計整合性: weakly_supported**（coherent・H-7 の act 単位/評価なしと一貫・H-5 possibility-only と整合・H-4 の「推論開始地点で止まる」を「actor 評価開始地点で止まる」に写像・Saiyan Scouter 抑止）。実集計ゼロゆえ経験的裏付けは無い。
- **推奨: design_defined / implementation_deferred。**
  - **いま確定（文書のみ）:** 学習可＝Act Count / Type Distribution / type Frequency（無名・集計）、学習不可＝Actor Identity / Trust / Reputation / Profile / Ranking、境界＝actor 個体帰属、Learning ┃ Pattern 境界（actor 無名の仮説）、最小 Learning Record。
  - **いま実装しない:** participation_learning の生成・集計コード。実 act/memory（H-7）が現れるまで gated。実装する場合も scope:aggregate 固定・actor を集計キーにしない・評価/順位/trust フィールド不在で、既存 Hermes learning 層の下に接続する。
- **接続方向: `Memory → Learning（無名集計）→ Pattern（type 構造の仮説）` は正しい。逆向き（学習から actor を評価・序列化・推薦）は不採用。**

---

## 7. 成功条件の確認

- ✅ Participant Ranking 無し / Trust Score 無し / Reputation 無し / Actor Profile 無し / Contribution 生成なし / Cooperation 生成なし / 文書のみ・コード/データ無変更。
- ✅ Participation Learning を人物評価・信頼スコア・資格付与・ランキング・推薦へ変化させていない（構造的に不可能化）。
- ✅ Reality Correction: `participation_learning_count = 0` を正しい観察結果として記録。

---

*本文書は Participation Memory から何を学習してよいかの監査記録であり、何も生成しない。学習してよいのは actor を含まない type/集計レベルの構造のみ——Act Count・Act Type Distribution・type 別 Frequency（いずれも無名・集計）。学習してはならないのは actor 個体に降りるすべて——Actor Identity・Trust・Reputation・Profile・Ranking。境界は「集計が actor 個体に帰属した瞬間」で、頻度は type の属性であって人の属性ではない。Learning ┃ Pattern 境界は actor 無名の仮説化（possibility only・human review）。Hermes は集計の構造的可能性のみ推論し、actor の価値・同定・将来行動へ降りてはならない（actor 評価が始まる地点で止まる）。向きは Memory→Learning（無名集計）→Pattern（type 構造）で固定し、逆向きの評価・序列化・推薦は禁止。現状 participation_learning_count = 0 は失敗ではなく観察結果であり、学習境界を先に確定する価値は将来の人物評価・資格化を防ぐガードレールにある。Reach Gap・実価値は未解決であり、本文書もその解決を主張しない。*
