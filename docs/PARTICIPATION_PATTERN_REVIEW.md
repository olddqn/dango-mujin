# Phase H-9: Participation Pattern Review

- **Status:** 観察レビュー（Participation Learning からどんな Pattern を形成してよいかの監査）。**コード/データ/生成/登録/ランキング/スコアなし。文書のみ。**
- **Date:** 2026-06-20
- **前提:** H-8（Learning は actor を含まない type/集計のみ・学習境界＝actor 個体帰属）, H-7（memory は act 単位・評価なし）, F-4.5（act は種類で分類・等級なし）, H-2.5/H-5（pattern は tentative・possibility only・actor 無名・Hermes 非生成）, H-4（推論開始地点で止まる）, Saiyan Scouter 問題

> 中心問い: **Participation Learning からどのような Pattern を形成してよいのか。**
> 結論先取り: **形成してよいのは「act type 間の構造的・無名な関係」だけ——Act Sequence・Co-occurrence・type 遷移（Feedback→Issue 等）・Repeated Structure。いずれも actor を含まず、possibility only・tentative。形成してはならないのは actor 個体に降りる Actor Pattern・Trust Pattern。境界は「type 構造が actor 個体に帰属した瞬間」。現状 participation_pattern_count = 0。**

---

## 0. 前提（H-8 からの継承）

```
[Participation Learning]  actor を含まない type/集計（Count/Distribution/type Frequency）
        │  pattern = 集計から導く「type 構造の仮説」（tentative・actor 無名）
        ▼
[Participation Pattern]  ← H-9 が境界を定義
```

- H-8 で確定: learning は集計どまり、actor 個体帰属線を越えない。
- H-9 が問うのは「集計から**どんな仮説（pattern）を立ててよいか**」。危険は「type 構造」が「**actor の行動様式（profiling）**」へ滑ること。

---

## 1. Case A〜H の監査（pattern 可否）

| Case | pattern 対象 | actor 帰属 | 判定 |
|---|---|---|---|
| A | Act Sequence（act type の並び） | なし（type 列） | **可** |
| B | Act Co-occurrence（type の共起） | なし（type 集合） | **可** |
| C | Feedback → Issue（type 遷移） | なし（type 遷移） | **可** |
| D | Counter Argument → Proposal | なし（type 遷移） | **可** |
| E | Translation → Feedback | なし（type 遷移） | **可** |
| F | Repeated Structure（type 構造の反復） | なし（type 構造） | **可** |
| G | **Actor Pattern**（人の行動様式） | **あり（個体）** | **禁止** |
| H | **Trust Pattern**（信頼の構造） | **あり（個体評価）** | **禁止** |

- **境界は F と G の間**。A〜F はすべて「**act type の構造**」（誰がやったかを含まない type の並び/共起/遷移/反復）。G/H は「**actor 個体の様式・評価**」。
- 重要な落とし穴: C〜E の遷移を「**Aさんが feedback の後 issue を出す**」と読むと G に堕ちる。**遷移は type 列の構造であって、特定 actor の履歴ではない**——「feedback type の act の後に issue type の act が観察される」という無名・集計的構造にとどめる。

---

## 2. Q1〜Q10 の監査

### Q1. Pattern の最小単位は何か

**actor を含まない「act type 間の構造的関係」の仮説（tentative）。** 単位は「type 構造」であって「actor 様式」ではない。
- 最小の安全な pattern ＝「ある act type 構造が繰り返し観察される（仮説）」。
- actor を構造の節点に入れた瞬間に actor pattern になる（H-7/H-8 と同型：節点を人にしない）。

### Q2. Act Sequence は Pattern か

**可（Case A）。** 「type X の act の後に type Y の act が観察される」という**無名の type 列**。
- 条件: 列の要素は **act_type**であって actor ではない。「誰の sequence か」を問わない（問えば G）。
- possibility only・tentative（「順序がある」を断定しない）。

### Q3. Co-occurrence は Pattern か

**可（Case B）。** 「type X と type Y の act が同時期/同 object に共起する」という無名構造。
- 条件: 共起の主語は type/object であって actor ではない。actor の共起（「AさんとBさんが一緒に」）は Cooperation 領域（§Q7）かつ actor 無名で扱う。

### Q4. Repeated Structure は Pattern か

**可（Case F）。** 「ある type 構造（sequence/co-occurrence）が反復観察される」という仮説。
- H-2.5 の pattern と同型：反復は fact ではなく tentative な hypothesis。
- 条件: 反復の対象は type 構造。「同じ人が反復」は actor pattern（G・禁止）。

### Q5. Actor Pattern は許可されるか

**不可（Case G・絶対禁止）。** 「この actor はこう振る舞う」は人物プロファイル＝ Saiyan Scouter。
- type 遷移/共起/反復を **actor を節点にして**組んだ瞬間に actor pattern になる。pattern の節点は常に act_type/object であって actor ではない。
- memory が持つ discoverer_id は event 連続のためで、pattern の節点や集計キーにしない（H-8 Q5 と一貫）。

### Q6. Trust Pattern は許可されるか

**不可（Case H・絶対禁止）。** 「信頼の構造」は actor 個体への価値判定の構造化。
- trust pattern を作れば「信頼できる参加者の型」＝選抜・資格付与の鋳型。
- H-7/H-8 で score を禁じたのと一貫——pattern も trust/reputation を**構造化しない**。

### Q7. Participation Pattern と Cooperation Pattern の境界は何か

**Participation Pattern ＝単一 act type 流れの構造、Cooperation Pattern ＝複数 actor の act が関係しうる possibility（H-5・actor 無名）。**
```
Participation Pattern（act type の sequence/co-occurrence/反復・単流）
   ┃ 境界 = 複数 actor の act が相互に関係づく可能性
   ▼
Cooperation Pattern（多 actor 協働の possibility・actor 無名・Hermes 非生成）
```
- Participation Pattern は **type 構造**を扱い、actor を結ばない。複数 actor の関係は Cooperation 層へ、そこでも actor 無名・possibility only・Hermes は生成しない（H-5）。
- 危険: Participation Pattern が「この人とこの人の協働型」を名指しで作ること。**結合は Cooperation 層、しかも無名で。**

### Q8. Agent Participation Pattern は人間と同じか

**境界・不変条件は同じ、ただし agent 特有の前処理を要す。**
- 同じ: type 構造のみ pattern 化可、actor/trust pattern 禁止。
- 追加: ①**self/loopback 除外**②**verified 限定**③**bulk/自動出力で構造を膨張させない**（agent の機械的反復を「型」と誤認しない）④**human review**。
- 特に危険: agent の規則的 act 列から「agent の行動様式」を pattern 化すること。**反復する type 構造**としてのみ扱い、agent 個体の様式にしない。

### Q9. Hermes は Participation Pattern から何を推論してよいか

**type 構造の possibility のみ。actor の様式・信頼・将来行動は推論禁止。**

| 推論してよい（type 構造・無名・tentative） | 推論禁止（actor 個体・選抜） |
|---|---|
| 「feedback→issue の type 遷移が在りうる」 | 「Aは feedback の後 issue を出す人」 |
| 「翻訳と feedback が共起しうる」（無名） | 「Aは信頼できる型」 |
| 「ある type 構造が反復しうる」 | 「Aを優先/推薦」 |
| 「協力が在りうる」（H-5・actor 無名） | 「Aは次もこの型」（将来予測） |

- H-4 の同型: 「推論が始まる地点」を検出して止まるように、ここでは「**actor 様式化が始まりうる地点**」を Hermes が検出して止まる。pattern/推論は type 構造どまり、actor 個体へ降りない。
- すべて **possibility only・tentative・actor 無名・pattern_is_not_fact/policy・human_review_required**。

### Q10. Participation Pattern の既約最小モデルは何か

**Pattern は actor を含まない act type 構造の tentative な仮説。** 安全な最小モデル:

```json
{
  "pattern_id": "ppat-001",
  "pattern_key": "act_type_sequence",        // act_type_sequence | act_type_cooccurrence |
                                             //   repeated_act_structure のみ
  "structure": ["feedback", "issue"],        // 節点は act_type（actor ではない）
  "scope": "aggregate",                      // 常に aggregate
  "status": "tentative",
  "nodes_are_act_types": true,               // 節点は type（Q1/Q5）
  "contains_actor_node": false,              // actor を節点に取らない（Q5）
  "contains_trust_structure": false,         // trust を構造化しない（Q6）
  "contains_ranking": false,
  "is_actor_pattern": false,                 // actor pattern でない（G）
  "links_no_actor": true,                    // actor を結ばない（Q7）
  "pattern_is_not_fact": true,
  "pattern_is_not_policy": true,
  "human_review_required": true
}
```
- **既約最小 = `pattern_key`（sequence / cooccurrence / repeated_structure）＋ `structure`（act_type の列・無名）＋ `scope:aggregate` ＋ `status:tentative`。**
- **含めてはならない:** actor を節点/集計キーにすること・actor 履歴・trust/reputation 構造・順位・推薦・将来予測・actor 協働の名指し。

---

## 3. Participation Pattern の位置（確定図）

```
[Participation Learning]  無名集計（H-8）
        │  pattern = act type 構造の仮説（tentative・actor 無名）
        ▼
[Participation Pattern]  Sequence / Co-occurrence / type 遷移 / Repeated Structure  ← H-9
        ┃ 境界① = actor 個体への帰属（＝禁止：Actor Pattern / Trust Pattern）
        ╳  ← 越えない
        ┃ 境界② = 複数 actor の関係 → [Cooperation Pattern]（actor 無名・H-5）
        ▼
   許可される推論: 「type 構造が在りうる」（possibility only・human review）
```

- pattern は act type の地平にとどまる。actor 個体帰属線（F┃G・F┃H）を**構造的に越えられない**。多 actor の関係は Cooperation 層へ無名で委譲。

---

## 4. Saiyan Scouter Review

**問い: Participation Pattern が 人物評価 / 信頼推定 / 資格付与 / ランキング / 推薦 へ変化していないか。**

| 観察（安全） | 変質（禁止・再発点） |
|---|---|
| act_type の sequence/共起/反復 | actor を節点にした行動様式（G） |
| 節点は type | 節点に actor（個体追跡・Q5） |
| type 構造の possibility | 「信頼できる型」trust pattern（H/Q6） |
| pattern は tentative | actor を順位付け・推薦（Q9） |
| 多 actor 関係は無名で Cooperation へ | 人物協働を名指しで pattern 化（Q7） |

- **再発の臨界点5つ: ①actor を pattern 節点に取る ②actor 履歴の様式化 ③trust pattern ④actor ranking/推薦 ⑤名指し協働 pattern。** いずれも最小モデルの不変条件（nodes_are_act_types・contains_actor_node=false・contains_trust_structure=false・is_actor_pattern=false・links_no_actor・human_review）で封じる。
- 監査結果: **最小モデルは人物評価・信頼推定・序列・資格・名指し協働を構造的に不可能化**。節点が act_type に固定され、actor を節点/キーに取れず、trust/順位フィールドを持てず、scope は常に aggregate。

---

## 5. Reality Correction

```
discovery_event_count        = 0
participation_act_count      = 0
participation_memory_count   = 0
participation_learning_count = 0
participation_pattern_count  = 0
```

- 構造的帰結: `pattern_count` は learning(=0) からの仮説ゆえ実体ゼロ。形成すべき type 構造が無い。
- 現状、pattern 化の材料となる集計は1件も無い。**0件は失敗ではなく観察結果。**
- pattern 境界を「先に」定義する価値: 最初の type 構造が現れた時に、その場しのぎで actor pattern/trust pattern/ranking を作らない**ガードレール**。

---

## 6. 推奨ステータスと現在地（honest）

- **Participation Pattern 境界モデルの設計整合性: weakly_supported**（coherent・H-8 の type/集計と一貫・H-5 possibility-only と整合・H-4 の「推論開始地点で止まる」を「actor 様式化開始地点で止まる」に写像・Saiyan Scouter 抑止）。実 pattern ゼロゆえ経験的裏付けは無い。
- **推奨: design_defined / implementation_deferred。**
  - **いま確定（文書のみ）:** 形成可＝Act Sequence / Co-occurrence / type 遷移 / Repeated Structure（actor 無名・tentative）、形成不可＝Actor Pattern / Trust Pattern、境界①＝actor 個体帰属、境界②＝Participation ┃ Cooperation（多 actor 無名）、最小 Pattern Record。
  - **いま実装しない:** participation_pattern の生成コード。実 learning（H-8）が現れるまで gated。実装する場合も節点を act_type に固定・actor を節点/キーに取らない・trust/順位フィールド不在・status tentative で、既存 Hermes pattern 層の下に接続する。
- **接続方向: `Learning → Pattern（act type 構造の仮説）→（多 actor なら無名で）Cooperation Pattern` は正しい。逆向き（pattern から actor を評価・様式化・序列化・推薦）は不採用。**

---

## 7. 成功条件の確認

- ✅ Actor Pattern 無し / Participant Ranking 無し / Trust Pattern 無し / Contribution 生成なし / Cooperation 生成なし / 文書のみ・コード/データ無変更。
- ✅ Participation Pattern を人物評価・信頼推定・資格付与・ランキング・推薦へ変化させていない（構造的に不可能化）。
- ✅ Reality Correction: `participation_pattern_count = 0` を正しい観察結果として記録。

---

*本文書は Participation Learning からどんな Pattern を形成してよいかの監査記録であり、何も生成しない。形成してよいのは actor を含まない act type 間の構造的・無名な関係のみ——Act Sequence・Co-occurrence・type 遷移（Feedback→Issue 等）・Repeated Structure。いずれも possibility only・tentative で、節点は act_type であって actor ではない。形成してはならないのは actor 個体に降りる Actor Pattern・Trust Pattern で、境界は「type 構造が actor 個体に帰属した瞬間」。type 遷移は「ある type の後に別 type が観察される」無名構造にとどめ、特定 actor の履歴にしない。多 actor の関係は Participation ┃ Cooperation 境界を越え、Cooperation Pattern 側で actor 無名・Hermes 非生成として扱う。Hermes は type 構造の possibility のみ推論し、actor の様式・信頼・将来行動へ降りてはならない（actor 様式化が始まる地点で止まる）。向きは Learning→Pattern（type 構造）→（無名で）Cooperation で固定し、逆向きの評価・様式化・序列化・推薦は禁止。現状 participation_pattern_count = 0 は失敗ではなく観察結果であり、pattern 境界を先に確定する価値は将来の人物評価・資格化を防ぐガードレールにある。Reach Gap・実価値は未解決であり、本文書もその解決を主張しない。*
