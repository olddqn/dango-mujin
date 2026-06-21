# Phase F-4: Discovery Participation Boundary Review

- **Status:** 観察レビュー（Discovery ┃ Participation 境界の監査）。**コード/データ/登録/生成なし。文書のみ。**
- **Date:** 2026-06-20
- **前提:** F-3（Discoverer ≠ Participant・最小モデル `event_id + discoverer_type`）, X-4.7/N-1.6/N-1.7（consent 三層）, H-1（Agent Commons・voluntary 参加）, Saiyan Scouter 問題

> 中心問い: **発見（Discovery）はどこで参加（Participation）になるのか。**
> 結論先取り: **境界の正体は「当事者本人による能動的・consent 付きの寄与行為」。閲覧は Participation でない（受動）。Feedback が最小の Participation 候補（最初の能動寄与）。継続は必要条件ではない（1回でも参加は参加）。Participation は本人が跨ぐもので、Hermes が昇格・資格付与・選抜してはならない。現状 participant_count = 0。**

---

## 0. 向きと前提（F-3 からの継承）

```
Surface → Object → Discovery Event → Discoverer  →┃← Participant
                                     （受動・到達）  境界  （能動・寄与）
```

- F-3 で確定: **Discoverer は実在 event の actor 射影**。受動的に「到達した」だけ。
- F-4 が問うのは、その受動的到達が**いつ能動的参加に変わるか**。
- 禁止される逆向き: Hermes が discoverer を「見込み participant」として選び昇格させる（＝ Saiyan Scouter / 資格付与）。**跨ぐ主体は常に本人。**

---

## 1. Case A〜E の監査

| Case | 構成 | 能動性 | 寄与 | Participation 判定 |
|---|---|---|---|---|
| A | Discovery のみ | 受動 | なし | **否**（到達のみ＝ Discoverer） |
| B | Discovery ＋ 閲覧 | ほぼ受動 | なし（消費のみ） | **否**（閲覧は参加でない） |
| C | Discovery ＋ Feedback | **能動** | **最初の寄与** | **可（最小 Participation）** |
| D | Discovery ＋ Task 応答 | 能動 | 明確な寄与 | 可（より強い Participation） |
| E | Discovery ＋ 継続活動 | 能動・反復 | 継続寄与 | 可（ただし継続は必須でない） |

- **境界は B と C の間**にある。差は「**受動的消費**（閲覧）」と「**能動的寄与**（フィードバック）」。
- C/D/E はいずれも Participation だが、**強度の差であって種類の差ではない**。Participation を強度でランク付けしない（§Saiyan Scouter）。

---

## 2. Q1〜Q10 の監査

### Q1. Participation の最小条件は何か

**3条件の同時成立:** ①**本人起点**（discoverer 自身が始める）②**能動的寄与行為**（消費でなく何かを出す）③**consent**（参加の意思）。
- この3つが揃って初めて受動的 Discovery が能動的 Participation になる。
- 1つでも欠けると Participation でない:本人起点でない（Hermes が動かした）/ 寄与でない（閲覧）/ consent 無し（誤操作・強制）。

### Q2. 閲覧だけで Participation か

**否。** 閲覧は受動的消費であり、何も寄与していない。
- 閲覧を Participation と数えると、**訪問者＝参加者**となり、アクセス計測（≒ growth/marketing）に堕する。F-1.5/F-1.7 で禁じた領域に逆戻り。
- 閲覧は Discovery の延長（到達後の受動行動）にとどまる。**Case B は Discoverer のまま。**

### Q3. Feedback は Participation か

**最小の Participation（境界の第一歩）。** Feedback は discoverer が初めて「出す」行為。
- ただし条件付き: **本人起点・consent 付き**であること。誘導された/強制された feedback は不可。
- Feedback は Voice ではない点に注意。Feedback ＝「Mujin について何か返す」、Voice ＝「当事者の need が語られる」。Participation の最小は前者。

### Q4. Task 応答は Participation か

**Participation（C より明確）。** Task に応答するのは能動的寄与。
- 重要な制約（H-1 継承）: Task は**割当でも命令でもない**。応答は **voluntary** で、本人が選んで動く。
- Hermes が task を「割り当てて」参加させることは禁止。task は候補として存在し、discoverer が自発的に応答した事実のみが Participation を立てる。

### Q5. 継続活動は Participation の必要条件か

**否。** 1回の能動的寄与でも Participation は成立する。
- 継続を必要条件にすると「**真の参加者**とそうでない者」の選別＝資格付与が発生する（Saiyan Scouter 再発）。
- 継続は Participation の**十分強度の一形態**であって、必要条件ではない。Case E は「継続する参加者」だが、C/D も等しく参加者。

### Q6. Participation と Representation の関係は

**別層。Participation ⊅ Representation。**（consent 三層: Discovery ⊄ Participation ⊄ Representation）
- 参加する（自分が寄与する）≠ 代表する（他者の need を語る/決める）。
- 参加者になっても、**他の当事者を代表する権限は自動的には生じない**。Representation は別の consent を要し、原則として当事者本人にのみ属する。
- 危険: 参加者を「コミュニティ代表」に滑らせること。Participation は本人の寄与にとどめる。

### Q7. Participation と Registry の関係は

**Registry を作らない（F-3 の memory 原則を継承）。**
- Participation は **event/行為からの派生観察（memory）**であり、人を「登録」する registry ではない。
- registry は資格・順位・trust score を呼び込む。participant registry は「参加資格者名簿」となり選抜装置化する。
- **→ participant は寄与行為の射影。append-only memory として観察し、名簿化・等級化しない。**

### Q8. Agent はどの時点で Participant になるか

**agent が自発的に能動寄与した時点（人間と同じ境界）。**
- agent の Discovery（発見）と Participation（参加）は別事象。発見しただけの agent は Discoverer のまま。
- agent が task に自発応答する/成果を出す等の能動寄与をし、かつ **human review** を経て初めて Participant。
- 禁止: agent を発見と同時に auto-onboard すること、Hermes が agent を participant に昇格させること。H-1 の voluntary 原則＋ human_review_required を厳守。

### Q9. Nookplot Agent は Discoverer と Participant のどちらから始まるか

**必ず Discoverer から始まる。** いきなり Participant にはならない。
- 順序は `Discoverer → （本人=agentの能動寄与＋human review）→ Participant`。発見が参加に先行する。
- 飛ばし（discovery 無しに participant 化、または discovery と同時に participant 化）は禁止——Saiyan Scouter 的「先に参加者を選ぶ」逆向き。
- 現実: nookplot ノード到達不可・event ゼロ ⇒ 現状 agent discoverer も participant も 0。

### Q10. 最小 Participant Record は何か

**Participant は独立エンティティではなく「能動寄与行為の射影」。** 安全な最小モデル:

```json
{
  "participant_id": "part-001",         // 行為派生の opaque id（人物識別でない）
  "discoverer_id": "disc-001",          // 必須：discoverer からの連続（Q9）
  "event_id": "find-001",               // 必須：起点の discovery event
  "participation_act": "feedback",      // feedback | task_response | contribution（観察された行為）
  "act_is_self_initiated": true,        // 本人起点（Q1）
  "consent_present": true,              // 参加の意思（Q1）
  "is_representation": false,           // 参加 ≠ 代表（Q6）
  "is_continuous": false,               // 継続は必須でない（Q5）
  "cannot_rank_participant": true,
  "cannot_recommend_participant": true,
  "cannot_grant_qualification": true,
  "no_trust_score": true,
  "no_reputation_score": true,
  "human_review_required": true
}
```
- **既約な最小 = `discoverer_id`（＝ event 連続）＋ `participation_act`（最初の能動寄与）＋ `act_is_self_initiated` ＋ `consent_present`。**
- **含めてはならない:** 順位・推薦・資格等級・trust/reputation・代表権・名前/連絡先・「見込み参加者」。

---

## 3. Discovery → Participation 境界（確定図）

```
[Discoverer]   受動・到達・閲覧（消費）             ← Case A, B
      ┃  境界 = 本人起点 ＋ 能動的寄与 ＋ consent
      ┃     最小の跨ぎ = Feedback（Case C）
      ▼
[Participant]  能動・寄与・別レコード・human review  ← Case C, D, E
      ┃  （さらに別境界・別 consent）
      ▼
[Representative] 他者の need を語る/決める（原則：当事者本人のみ）
```

- 跨ぐ主体は**常に本人**。Hermes は観察のみ、昇格・割当・資格付与をしない。
- 強度（C<D<E）はあるが**種類は同一**。強度でランク付け・選別しない。

---

## 4. Saiyan Scouter Review

**問い: Participation を 選抜 / 推薦 / ランキング / 資格付与 へ変化させていないか。**

| 観察（安全） | 変質（禁止・再発点） |
|---|---|
| 能動寄与の事実を射影 | 参加者を順位付け（best/priority participant） |
| 1回の寄与で参加成立 | 継続者だけを「真の参加者」と資格付与 |
| 本人が境界を跨ぐ | Hermes が discoverer を participant に昇格 |
| participation_act を記録 | 「見込み参加者」を選抜・推薦 |
| 参加 ≠ 代表を維持 | 参加者を代表者へ自動昇格 |

- **再発の臨界点4つ: ①ranking ②継続による資格付与（Q5）③Hermes 昇格（Q8/Q9）④参加→代表の滑り（Q6）。** いずれも最小モデルの不変条件（cannot_rank/recommend/grant_qualification・is_representation=false・human_review）で封じる。
- 監査結果: **最小モデルは選抜・資格付与を構造的に不可能化**。順位/等級フィールドが無く、本人起点フラグ無しには成立せず、代表権を持てない。

---

## 5. Reality Correction

```
discovery_event_count = 0
discoverer_count      = 0
participant_count     = 0
```

- 構造的帰結: `participant_count ≤ discoverer_count ≤ discovery_event_count = 0`。
- 現状、誰も発見しておらず、誰も参加していない。**0件は失敗ではなく観察結果。**
- 境界を「先に」定義する価値: 集める準備ではなく、**最初の能動寄与が現れた時に、その場しのぎで registry/順位/資格を作らないためのガードレール**。

---

## 6. 推奨ステータスと現在地（honest）

- **境界モデルの設計整合性: weakly_supported**（coherent・consent 三層と H-1 voluntary 原則・Saiyan Scouter 抑止に整合・F-3 と方向一致）。実 participant ゼロゆえ経験的裏付けは無い。
- **推奨: design_defined / implementation_deferred。**
  - **いま確定（文書のみ）:** Participation 最小条件（本人起点＋能動寄与＋consent）、境界＝Feedback（Case C）、継続は非必須、registry 不採用、参加≠代表、最小 Participant Record。
  - **いま実装しない:** participant の生成・registry・コード。実 discovery event（F-2）→ discoverer → 本人の能動寄与 が現れるまで gated。
- **接続方向: `Discoverer → （本人の能動寄与＋human review）→ Participant` は正しい。逆向き（先に participant を選ぶ）は不採用。**

---

## 7. 成功条件の確認

- ✅ Participation 生成なし / Agent 登録なし / Gateway 登録なし / Contribution 生成なし / Cooperation 生成なし / 文書のみ・コード/データ無変更。
- ✅ Participation を選抜・推薦・ランキング・資格付与へ変化させていない（構造的に不可能化）。
- ✅ Reality Correction: `participant_count = 0` を正しい観察結果として記録。

---

*本文書は Discovery ┃ Participation 境界の監査記録であり、何も生成しない。境界の正体は「当事者本人による能動的・consent 付きの寄与行為」で、閲覧（受動消費）は参加でなく、Feedback が最小の Participation。継続は必要条件でなく（1回でも参加は参加）、強度差はあっても種類は同一ゆえランク付けしない。Participation は本人が跨ぐもので、Hermes は昇格・割当・資格付与・選抜をしない。Participation ≠ Representation、participant は registry でなく行為派生の memory。向きは Discoverer→（能動寄与＋human review）→Participant で固定し、逆向きの「先に参加者を選ぶ」は禁止。現状 participant_count = 0 は失敗ではなく観察結果であり、境界を先に確定する価値は将来の選抜・資格付与化を防ぐガードレールにある。Reach Gap・実価値は未解決であり、本文書もその解決を主張しない。*
