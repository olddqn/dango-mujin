# Phase H-10: Participation Evidence Review

- **Status:** 観察レビュー（Participation Pattern がどんな条件で Evidence になり得るかの監査）。**コード/データ/生成/登録/ランキング/スコアなし。文書のみ。**
- **Date:** 2026-06-20
- **前提:** H-9（Pattern は actor を含まない act type 間の構造のみ・節点は type）, H-8（learning は無名集計）, H-7（memory は act 単位）, H-3.5（evidence は fact でも proof でもない candidate）, H-5（possibility only・actor 無名・Hermes 非生成）, H-4（推論開始地点で止まる）, Saiyan Scouter 問題

> 中心問い: **Participation Pattern はどのような条件で Evidence になり得るか。**
> 結論先取り: **Evidence になり得るのは「actor を含まない type 構造が、複数回・複数源で観察された」という観察の裏付けだけ——Observed Sequence/Co-occurrence・Repeated Structure・Multiple/Cross-source Observation・Pattern Confirmation。いずれも fact でも proof でもない candidate（H-3.5）であり、actor 個体に降りる Actor Evidence・Trust Evidence は禁止。境界は「観察の裏付けが actor 個体の証明に帰属した瞬間」。現状 participation_evidence_count = 0。**

---

## 0. 前提（H-9 → H-3.5 の合流）

```
[Participation Pattern]  act type 構造の仮説（tentative・actor 無名・H-9）
        │  evidence = pattern を支える「観察の裏付け」（fact でも proof でもない・H-3.5）
        ▼
[Participation Evidence]  ← H-10 が境界を定義
```

- H-9 で確定: pattern の節点は act_type、actor を含まない、possibility only。
- H-3.5 で確定: evidence は **candidate**であって fact/proof ではない。
- H-10 が問うのは「pattern を**何が裏付けるか**」。危険は「type 構造の裏付け」が「**actor の証明（この人がこういう人だという証拠）**」へ滑ること。

---

## 1. Case A〜H の監査（evidence 可否）

| Case | evidence 対象 | actor 帰属 | 判定 |
|---|---|---|---|
| A | Observed Sequence（type 列の観察） | なし（type） | **可（candidate）** |
| B | Observed Co-occurrence（type 共起の観察） | なし（type） | **可（candidate）** |
| C | Repeated Structure（type 構造の反復観察） | なし（type） | **可（candidate）** |
| D | Multiple Observation（複数回観察） | なし（集計） | **可（裏付けの強度）** |
| E | Cross-source Observation（複数源観察） | なし（集計） | **可（裏付けの強度）** |
| F | Pattern Confirmation（pattern の観察的確認） | なし（type 構造） | **可（candidate・断定でない）** |
| G | **Actor Evidence**（人の証拠） | **あり（個体）** | **禁止** |
| H | **Trust Evidence**（信頼の証拠） | **あり（個体評価）** | **禁止** |

- **境界は F と G の間**。A〜F はすべて「**type 構造が観察された**」という無名の裏付け。G/H は「**actor 個体の証明・評価の裏付け**」。
- D/E（複数回・複数源）は**裏付けの強度**であって、actor を同定する手段ではない。「複数源で同じ actor」を辿り始めると G に堕ちる——複数性は type 構造に帰属させ、actor の cross-source identity 追跡には使わない。

---

## 2. Q1〜Q10 の監査

### Q1. Evidence の最小単位は何か

**actor を含まない「type 構造が観察された」という1つの観察裏付け（candidate）。** 単位は「type 構造の観察」であって「actor の証明」ではない。
- H-3.5 と同型: evidence は fact/proof ではなく、pattern を弱く支える candidate。
- actor を裏付けの対象にした瞬間に actor evidence（個体の証拠）になる——対象は常に type 構造。

### Q2. Observed Sequence は Evidence か

**可（Case A・candidate）。** 「type X→type Y の遷移が実際に観察された」という裏付け。
- 条件: 観察対象は act_type 列。「誰の sequence を観察したか」を問わない（問えば G）。
- evidence_is_not_fact / not_proof：観察された≠真である。

### Q3. Observed Co-occurrence は Evidence か

**可（Case B・candidate）。** 「type X と type Y の共起が観察された」という裏付け。actor の共起ではない（actor の共起は Cooperation 側で無名・§Q8）。

### Q4. Repeated Structure は Evidence か

**可（Case C・candidate）。** 「ある type 構造の反復が観察された」。反復回数は**裏付けの強度**であって、断定でも actor 追跡でもない。

### Q5. Cross-source Observation は Evidence か

**可（Case E・candidate）、ただし最も危険。** 「同じ type 構造が複数源で観察された」は裏付けを強める。
- **危険の核心**: cross-source を「**同一 actor を複数源で突き合わせる**」（entity resolution / 名寄せ）に使うと、actor identity 構築＝ Saiyan Scouter。
- **規則: cross-source は type 構造の裏付けにのみ使い、actor の名寄せには絶対に使わない。** source も actor も無名で扱う。

### Q6. Actor Evidence は許可されるか

**不可（Case G・絶対禁止）。** 「この actor がこういう人だ」という証拠は人物プロファイルの確証＝最終段の Saiyan Scouter。
- pattern が actor を含まない以上、その evidence も actor を含み得ない（上流が無名なら下流も無名）。
- memory の discoverer_id は event 連続のためで、evidence の対象・キーにしない。

### Q7. Trust Evidence は許可されるか

**不可（Case H・絶対禁止）。** 「信頼に値する証拠」は actor 評価の確証＝資格付与の根拠化。
- H-7/H-8/H-9 で score/trust を禁じたのと一貫——evidence も trust を**裏付けない**。

### Q8. Participation Evidence と Cooperation Evidence の境界は何か

**Participation Evidence ＝単一 type 構造の観察裏付け、Cooperation Evidence ＝複数 actor の協働が在りうる possibility の裏付け（H-5・actor 無名）。**
```
Participation Evidence（type 構造の観察裏付け・単流）
   ┃ 境界 = 複数 actor の協働可能性の裏付け
   ▼
Cooperation Evidence（多 actor possibility の裏付け・actor 無名・Hermes 非生成・H-5）
```
- Participation Evidence は **type 構造**を裏付け、actor を結ばない。多 actor の関係の裏付けは Cooperation 層へ、そこでも actor 無名・possibility only。
- 危険: Participation Evidence が「この人たちが協働した証拠」を名指しで作ること。**結合の裏付けは Cooperation 層、無名で。**

### Q9. Hermes は Participation Evidence から何を推論してよいか

**type 構造の possibility の裏付け強度のみ。actor の証明・信頼・将来行動は推論禁止。**

| 推論してよい（type 構造・無名・candidate） | 推論禁止（actor 個体・選抜） |
|---|---|
| 「feedback→issue 構造の観察が複数ある」 | 「Aがこういう人だと証明された」 |
| 「ある共起が複数源で観察された」（無名） | 「Aは信頼できると裏付けられた」 |
| 「pattern が観察的に支持される（弱く）」 | 「Aを優先/推薦する根拠」 |
| 「協力が在りうる裏付け」（H-5・無名） | 「Aは次もこうする証拠」（将来予測） |

- H-4 の同型: 「推論が始まる地点」で止まるように、ここでは「**actor 証明が始まりうる地点**」を Hermes が検出して止まる。evidence/推論は type 構造の裏付けどまり、actor 個体へ降りない。
- すべて **evidence_is_not_fact / not_proof・candidate_only・actor 無名・human_review_required**。

### Q10. Participation Evidence の既約最小モデルは何か

**Evidence は actor を含まない type 構造の観察裏付け candidate。** 安全な最小モデル:

```json
{
  "evidence_id": "pev-001",
  "supports_pattern": "ppat-001",            // どの pattern を弱く支えるか（H-9）
  "evidence_kind": "observed_sequence",      // observed_sequence | observed_cooccurrence |
                                             //   repeated_structure | cross_source_observation |
                                             //   pattern_confirmation
  "observed_structure": ["feedback", "issue"], // 対象は act_type（actor でない）
  "observation_count": 0,                    // 裏付け強度（無名集計・現状 0）
  "source_count": 0,                         // 複数源数（actor 名寄せに使わない・Q5）
  "scope": "aggregate",
  "targets_act_type_structure": true,        // 対象は type 構造（Q1）
  "contains_actor_evidence": false,          // actor 証明を含まない（Q6）
  "contains_trust_evidence": false,          // trust を含まない（Q7）
  "contains_ranking": false,
  "links_no_actor": true,                    // actor を結ばない/名寄せしない（Q5/Q8）
  "evidence_is_not_fact": true,
  "evidence_is_not_proof": true,
  "candidate_only": true,
  "human_review_required": true
}
```
- **既約最小 = `supports_pattern` ＋ `evidence_kind` ＋ `observed_structure`（act_type・無名）＋ `scope:aggregate` ＋ `evidence_is_not_fact/proof`。**
- **含めてはならない:** actor を対象/キーにすること・cross-source の actor 名寄せ・trust/reputation の裏付け・順位・推薦・将来予測・actor 協働の名指し証拠・「証明された」断定。

---

## 3. Participation Evidence の位置（確定図）

```
[Participation Pattern]  type 構造の仮説（H-9）
        │  evidence = 観察の裏付け（fact/proof でない candidate・H-3.5）
        ▼
[Participation Evidence]  Observed Sequence/Co-occurrence / Repeated / Multiple / Cross-source / Confirmation
        ┃ 境界① = actor 個体の証明への帰属（＝禁止：Actor Evidence / Trust Evidence）
        ╳  ← 越えない（cross-source を actor 名寄せに使わない）
        ┃ 境界② = 多 actor 協働の裏付け → [Cooperation Evidence]（actor 無名・H-5）
        ▼
   許可される推論: 「type 構造が観察的に弱く支持される」（candidate・human review）
```

- evidence は type 構造の裏付けの地平にとどまる。actor 証明帰属線（F┃G・F┃H）を**構造的に越えられない**。多 actor の裏付けは Cooperation 層へ無名で委譲。

---

## 4. Saiyan Scouter Review

**問い: Participation Evidence が 人物評価 / 信頼推定 / 資格付与 / ランキング / 推薦 へ変化していないか。**

| 観察（安全） | 変質（禁止・再発点） |
|---|---|
| type 構造の観察裏付け | actor 個体の証明（Actor Evidence・G） |
| 複数性は裏付け強度 | cross-source で actor 名寄せ（Q5） |
| 対象は act_type | 対象に actor（個体証明・Q6） |
| trust を裏付けない | trust evidence で資格根拠化（H/Q7） |
| candidate・not proof | 「証明された」断定で actor 推薦（Q9） |

- **再発の臨界点5つ: ①actor を evidence 対象に取る ②cross-source の actor 名寄せ ③trust evidence ④「証明」断定 ⑤名指し協働 evidence。** いずれも最小モデルの不変条件（targets_act_type_structure・contains_actor_evidence=false・contains_trust_evidence=false・links_no_actor・evidence_is_not_proof・human_review）で封じる。
- 監査結果: **最小モデルは人物証明・信頼推定・序列・資格・名寄せを構造的に不可能化**。対象が act_type 構造に固定され、actor を対象/キーに取れず、proof を主張できず、cross-source は type 裏付け専用。

---

## 5. Reality Correction

```
discovery_event_count        = 0
participation_act_count      = 0
participation_memory_count   = 0
participation_learning_count = 0
participation_pattern_count  = 0
participation_evidence_count = 0
```

- 構造的帰結: `evidence_count` は pattern(=0) を支える裏付けゆえ実体ゼロ。裏付けるべき type 構造が無い。
- 現状、evidence 化の材料となる観察は1件も無い。**0件は失敗ではなく観察結果。**
- evidence 境界を「先に」定義する価値: 最初の観察裏付けが現れた時に、その場しのぎで actor evidence/trust evidence/名寄せを作らない**ガードレール**。

---

## 6. 推奨ステータスと現在地（honest）

- **Participation Evidence 境界モデルの設計整合性: weakly_supported**（coherent・H-9 の type 構造と一貫・H-3.5 の「fact でも proof でもない candidate」を継承・H-5 possibility-only と整合・H-4 の「推論開始地点で止まる」を「actor 証明開始地点で止まる」に写像・Saiyan Scouter 抑止）。実 evidence ゼロゆえ経験的裏付けは無い。
- **推奨: design_defined / implementation_deferred。**
  - **いま確定（文書のみ）:** evidence 化可＝Observed Sequence/Co-occurrence / Repeated Structure / Multiple / Cross-source Observation / Pattern Confirmation（actor 無名・candidate）、evidence 化不可＝Actor Evidence / Trust Evidence、境界①＝actor 証明帰属（cross-source を名寄せに使わない）、境界②＝Participation ┃ Cooperation（多 actor 無名）、最小 Evidence Record。
  - **いま実装しない:** participation_evidence の生成コード。実 pattern（H-9）が現れるまで gated。実装する場合も対象を act_type 構造に固定・actor を対象/キーに取らない・evidence_is_not_proof・cross-source は type 裏付け専用で、既存 Hermes evidence 層（H-3.5）の下に接続する。
- **接続方向: `Pattern → Evidence（type 構造の観察裏付け candidate）→（多 actor なら無名で）Cooperation Evidence` は正しい。逆向き（evidence から actor を証明・名寄せ・序列化・推薦）は不採用。**

---

## 7. 成功条件の確認

- ✅ Actor Evidence 無し / Participant Ranking 無し / Trust Evidence 無し / Contribution 生成なし / Cooperation 生成なし / 文書のみ・コード/データ無変更。
- ✅ Participation Evidence を人物評価・信頼推定・資格付与・ランキング・推薦へ変化させていない（構造的に不可能化）。
- ✅ Reality Correction: `participation_evidence_count = 0` を正しい観察結果として記録。

---

*本文書は Participation Pattern がどんな条件で Evidence になり得るかの監査記録であり、何も生成しない。Evidence になり得るのは actor を含まない type 構造が複数回・複数源で観察されたという裏付けのみ——Observed Sequence/Co-occurrence・Repeated Structure・Multiple/Cross-source Observation・Pattern Confirmation。いずれも fact でも proof でもない candidate（H-3.5）で、対象は act_type 構造であって actor ではない。複数性・cross-source は裏付けの強度であって actor の名寄せ（entity resolution）には絶対に使わない。形成してはならないのは actor 個体に降りる Actor Evidence・Trust Evidence で、境界は「観察の裏付けが actor 個体の証明に帰属した瞬間」。多 actor の協働の裏付けは Participation ┃ Cooperation 境界を越え、Cooperation Evidence 側で actor 無名・Hermes 非生成として扱う。Hermes は type 構造の possibility の裏付け強度のみ推論し、actor の証明・信頼・将来行動へ降りてはならない（actor 証明が始まる地点で止まる）。向きは Pattern→Evidence（type 構造）→（無名で）Cooperation で固定し、逆向きの証明・名寄せ・序列化・推薦は禁止。現状 participation_evidence_count = 0 は失敗ではなく観察結果であり、evidence 境界を先に確定する価値は将来の人物証明・資格化を防ぐガードレールにある。Reach Gap・実価値は未解決であり、本文書もその解決を主張しない。*
