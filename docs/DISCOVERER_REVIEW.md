# Phase F-3: Discoverer Review

- **Status:** 観察レビュー（発見者として記録できる最小情報の監査）。**コード/データ/登録/生成/接触なし。文書のみ。**
- **Date:** 2026-06-20
- **前提:** F-1（Findability）, F-1.5（Surface）, F-1.7（Object）, F-2（Discovery Event）, F-2.5（Discovery Path）, X-4.7/N-1.6/N-1.7（consent 三層）, Saiyan Scouter 問題（問題定義・選抜の権力）

> 中心問い: **発見者（Discoverer）として最低限何を記録できるか。**
> 結論先取り: **Discoverer は独立の登録対象ではなく「実在 Discovery Event の actor 射影」にすぎない。最小記録は `event_id + discoverer_type` の2項のみ。surface/object は event の属性であって人の属性ではない。event の無い discoverer（＝推測された人物）は記録不可。現状 discoverer_count = 0。**

---

## 0. F-3 が観察する向き（最重要の前提）

```
Surface → Object → Discovery Event → Discoverer
```

- Discoverer は**末端の派生項**である。先に人がいるのではなく、**event が起きたから「誰が」を後から観察できる**。
- 禁止される逆向き:
```
Discoverer → Target        （人を選び、目標化する ＝ Saiyan Scouter / outreach）
```
- F-3 は「**発見された主体（target）**」ではなく「**発見した主体（actor of a real event）**」を観察する。矢印が event から actor へ向いている限り安全。actor から目標へ向いた瞬間に越境する。

---

## 1. Q1〜Q10 の監査

### Q1. discoverer を識別するのに `discoverer_type` だけで十分か

**「何のために十分か」を分けて答える。**
- **個人を識別するため → 不十分、かつ不可侵。** 個人の同定は inference/surveillance であり F-3 の禁止事項。
- **「ある type の発見者が存在した」と記録するため → 十分、かつそれが安全上の上限。**
- **→ `discoverer_type` は actor 属性の floor であり同時に ceiling。** これ以上人物について足すこと（名前・地域・履歴）は profiling。type は「最小にして最大」。

### Q2. surface は discoverer の属性か event の属性か

**event の属性。** discoverer に固有の surface は存在しない。surface は「その発見が起きた場所」であり、人の特性ではない。discoverer に surface を貼ると**人物プロファイルの構築が始まる**。→ surface は event 側に置く。discoverer record には event 経由の参照（context）としてのみ複写し、actor 属性として扱わない。

### Q3. object は discoverer の属性か event の属性か

**event の属性。** 「何が発見されたか」は発見イベントの性質であって人の性質ではない。Q2 と同型。object を discoverer の属性にすると「この人はこれに興味がある」という推測（inferred interest）に滑り、Saiyan Scouter 化する。→ object も event 側。

### Q4. event の無い discoverer を記録してよいか

**不可（F-3 の核心規則）。** event の無い discoverer は「まだ発見していない誰か」＝ **predicted_actor / target_user**そのもの。記録した瞬間に「見込み発見者リスト」という outreach 装置になる。
- **規則: discoverer は実在 event からのみ派生する。** ∴ `discoverer_count ≤ discovery_event_count`。
- 現状 `discovery_event_count = 0` ⇒ `discoverer_count = 0`。これは構造的保証であり、偶然ではない。

### Q5. discoverer registry と discoverer memory は別か

**別物であり、F-3 が採るべきは memory のみ。registry は採らない。**
- **registry** = 登録・同一性・永続化・名簿。trust score / ranking / 優先度を呼び込む。`agent_registry` を人間に対して作るに等しく危険。
- **memory** = event から append-only に派生する観察。人を「登録」しない。
- **→ F-3 は event 派生の memory。独立した discoverer registry を持たない。** discoverer は event の射影であって、永続する人物エンティティではない。

### Q6. human / agent / organization 以外が必要か

**現状不要。** n=0 で細分する根拠がない。3類型で足り、細かい typing は profiling リスクを上げるだけ。
- 検討に値する唯一の追加は `unknown`（type が観測できない正直値）だが、現状は event ゼロで使い道がない。
- **→ 3類型を維持。実 event が要求するまで拡張しない（YAGNI ＋ anti-profiling）。**

### Q7. discoverer を ranking せずに観察できるか

**できる。** 観察 = **列挙 ＋ type 別カウント**。比較・順位付けを一切しない。
- discoverer を sort した瞬間に「優先発見者 / best discoverer」＝ **選抜**が発生する（§4 Saiyan Scouter）。
- 不変条件 `cannot_rank_actor` / `cannot_recommend_actor` と、禁止語彙（best/recommended/priority discoverer・trust/reputation score）で構造的に封じる。

### Q8. discoverer が participation に変化する境界はどこか

**discoverer の自発的行為が境界。Hermes は決して跨がせない。**
```
Discovery      受動的到達（相手が Mujin を見つけた）         ← F-3
   ↓  ※境界 = 当事者自身の能動的行為（consent 付き）
Participation  発見者が自ら動く（Voice 作成 / 貢献 / agent 登録）
```
- consent 三層（X-4.7）の写像: **Discovery ≠ Participation ≠ Representation**。
- 境界を跨ぐ主体は**常に discoverer 本人**。Hermes が discoverer を participant に「昇格」させることは禁止（auto-onboarding 禁止）。
- discoverer record の `participation` は既定 `false`。本人が動いた事実が観察されて初めて、別レコードとして participation が立つ。

### Q9. Nookplot Agent を discoverer として扱う場合の問題

4点:
1. **自己発見の混入。** gitlawb/nookplot ノード経由の「発見」が Mujin 自身のインフラ（loopback）由来だと、self-discovery を発見者として数える誤り。→ self/loopback を除外必須。
2. **bulk/自動発見による膨張。** crawler 的 agent が discoverer_count を無意味に増やす。→ `verified=true` のみ採用、自動取得は discoverer にしない。
3. **agent の participant 化リスク。** agent を discoverer にすると、そのまま onboarding/参加へ滑りやすい（Q8 違反）。→ discoverer と participant を厳格分離、human review 必須。
4. **現実: 現状ノードは localhost(127.0.0.1:7545) かつ到達不可（F-1.5 検証済）。** 実 agent 発見は存在しない ⇒ 現状 agent discoverer = 0。
- **→ 結論: agent も discoverer になりうるが、self除外・verified限定・participant非昇格・human review を満たす場合のみ。現状は理論的。**

### Q10. 最小 discoverer record は何か

**discoverer は独立 record ではなく event の actor 射影。** 安全な最小モデル:

```json
{
  "discoverer_id": "disc-001",          // event 派生の opaque id（人物識別ではない）
  "event_id": "find-001",               // 必須。event 無ければ discoverer 無し（Q4）
  "discoverer_type": "human",           // human | agent | organization のみ（Q6）
  "observed_via_surface": "github_repository",  // event 属性の文脈複写（Q2）
  "observed_object": "documentation",   // event 属性の文脈複写（Q3）
  "participation": false,               // 本人が動くまで false（Q8）
  "discoverer_is_not_target": true,
  "cannot_rank_actor": true,
  "cannot_recommend_actor": true,
  "cannot_recruit_actor": true,
  "no_trust_score": true,
  "no_reputation_score": true,
  "human_review_required": true
}
```
- **既約な最小は `event_id` ＋ `discoverer_type` の2項。** 他はすべて event 文脈であって人物属性ではない。
- **含めてはならない:** 名前・連絡先・地域・履歴・興味推定・trust/reputation・順位・推薦・inferred_user/predicted_actor/target_actor。

---

## 2. Discoverer 最小モデル（確定提案）

| 項目 | 値 | 性質 |
|---|---|---|
| `event_id` | 実在 verified event への参照 | **必須**・存在の前提 |
| `discoverer_type` | human / agent / organization | actor 属性（floor=ceiling） |
| `observed_via_surface` | event の surface | event 文脈（人物属性ではない） |
| `observed_object` | event の object | event 文脈 |
| `participation` | 既定 false | 境界フラグ |
| 不変条件群 | rank/recommend/recruit/trust/reputation すべて不可 | 構造的封じ込め |

> **最小モデルの本質: 「誰か」ではなく「ある event の actor が type X であった」だけを残す。** Discoverer memory は人を覚えるのではなく、event に actor-type という一筆を添えるだけ。

---

## 3. Discoverer → Participant 境界

```
[F-3 Discoverer]  受動・到達のみ・participation=false
        ┃  境界 = 当事者本人の能動行為（consent 必須）
        ┃     例: Voice を立てる / 貢献する / agent として自発登録する
        ▼
[Participant]     能動・本人起点・別レコード・human review
```
- **跨ぐのは本人のみ。** Hermes は観察するだけで昇格させない。
- consent 三層対応: Discovery 同意 ⊄ Participation 同意 ⊄ Representation 同意。
- 違反パターン（禁止）: discoverer を「見込み参加者」として扱う / 自動で participant 化する / participation=true を Hermes が立てる。

---

## 4. Saiyan Scouter 再発確認

**問い: 発見者を記録することが、発見者を選抜することへ変化していないか。**

| 観察行為（安全） | 選抜行為（禁止・再発点） |
|---|---|
| type 別に列挙・カウント | discoverer を順位付け |
| event の actor を射影 | best/recommended/priority discoverer |
| participation=false を保持 | 見込み参加者として target 化 |
| event 無し＝記録無し | event 無き「見込み発見者」を生成 |

- **再発の臨界点は3つ: ①ranking ②event無し記録 ③逆向き（Discoverer→Target）。** いずれも禁止語彙・不変条件・Q4規則で封じる。
- 監査結果: **最小モデルは選抜を構造的に不可能化している**（順位フィールドが無く、event 派生でしか存在できず、target フラグを持てない）。Saiyan Scouter 再発は設計上抑止。

---

## 5. Nookplot Agent 接続時の含意

- agent discoverer は**原理的に可能**だが、以下を満たす時のみ安全: **self/loopback 除外・`verified=true` 限定・participant 非昇格・human review 必須・bulk自動取得は非discoverer**。
- 危険: agent を discoverer にした流れで「協力者候補」「参加 agent」へ自動接続すること（Q8/Q9 違反）。Discoverer memory と Agent Commons（H-1）の registry は**接続しない**——agent が「発見した」ことと、agent が「参加する」ことは別事象。
- 現実（Reality Correction）: nookplot ノードは到達不可・voices 非公開・event ゼロ。**現状 agent discoverer = 0。** 実接続は実 event 到来に gated。

---

## 6. Reality Correction

```
discovery_event_count = 0
discovery_path_count  = 0
discoverer_count      = 0
```

- **現状の最も正直な結論は `discoverer_count = 0`。** 誰も Mujin を発見していない（F-2/F-2.5 と整合）。
- 0件は失敗ではなく観察結果。`discoverer_count ≤ discovery_event_count = 0` という構造的帰結であり、推測で埋めてはならない。
- **発見者を「先に」定義する価値はあるか → ある。** ただし価値は「集める準備」ではなく「**ガードレールを event 到来前に確定しておく**」こと。定義が無いまま最初の event が来ると、その場しのぎで registry / 順位 / profiling を作る誘惑が生じる。**最小モデルを先に固定することは、将来の Saiyan Scouter 化を防ぐ予防措置。**

---

## 7. 推奨ステータスと現在地（honest）

- **最小モデルの設計整合性: weakly_supported**（coherent・consent三層と Saiyan Scouter 抑止に整合・F-2/F-2.5 と方向一致）。実 event ゼロゆえ経験的裏付けは無い。
- **推奨: design_defined / implementation_deferred。**
  - **いま確定するもの（文書のみ）:** Discoverer 最小モデル（`event_id + discoverer_type`）、registry 不採用・memory のみ、Discoverer→Participant 境界、禁止語彙・不変条件。
  - **いま実装しないもの:** discoverer_reflector 等のコード。実 discovery event（F-2）到来まで gated。実装するとしても discoverer は event 射影として F-2 の下流に置き、独立 registry にはしない。
- **接続方向の確認: `Surface → Object → Event → Discoverer` は正しい。逆向き `Discoverer → Target` は不採用。**

---

## 8. 成功条件の確認

- ✅ コード変更なし / データ変更なし / 登録なし / 生成なし / 接触なし / Need・Gateway・Cooperation・Decision 生成なし / 文書のみ。
- ✅ discoverer 推測（user/協力者/Agent/Gateway）なし。発見「された」主体ではなく発見「した」主体のみを対象化。
- ✅ Reality Correction: `discoverer_count = 0` を正しい観察結果として記録。

---

*本文書は Discoverer として記録できる最小情報の監査記録であり、何も生成しない。Discoverer は実在 Discovery Event の actor 射影にすぎず、最小記録は `event_id + discoverer_type` の2項。surface/object は event の属性であって人の属性ではなく、event の無い discoverer（＝推測人物）は記録不可。Discoverer は registry ではなく memory、participation への昇格は本人の能動行為のみが跨ぐ。向きは Surface→Object→Event→Discoverer で固定し、逆向きの Discoverer→Target（Saiyan Scouter / outreach）は禁止。現状 discoverer_count = 0 は失敗ではなく観察結果であり、最小モデルを先に確定する価値は「集める準備」ではなく「将来の選抜化を防ぐガードレール」にある。Reach Gap・実価値は未解決であり、本文書もその解決を主張しない。*
