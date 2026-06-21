# Gateway Bottleneck Cooperation — Simulation Review

- **Status:** 机上シミュレーション（tabletop）の観察記録。**実際の Contribution は行っていない。** 文書のみ・コード/データ無変更・Need 作成なし・Gateway 選定なし・資金移動なし。
- **Date:** 2026-06-13
- **対象:** [`GATEWAY_BOTTLENECK_COOPERATION_TRIAL_PROTOCOL.md`](GATEWAY_BOTTLENECK_COOPERATION_TRIAL_PROTOCOL.md)（X-4）の Step 1–5
- **対象 Voice:** `voice-006`（JAR 公開支援要請）/ Trial 対象: A 資金 · B 人手（Gateway Need のみ）

> このシミュレーションは「もし X-4 を実行したら、各段で何が失敗・曖昧化し、どこで Saiyan Scouter が再発しうるか」を**頭の中で一周させて観察**したもの。`needs / contributions / cooperation / feedback` のいずれの JSONL にも書き込んでいない。

---

## 0. シミュレーションの前提（実プラットフォーム機構に即す）

実際の挙動を確認した上で歩く:
- Contribution: `status` は `offered → committed → delivered → verified → disputed`。記録は意思表示で `moves_money: false`。
- Cooperation: `participants[]` を持ち、`cooperation_is_not_command / not_assignment / participation_is_voluntary`。
- Reality Feedback: `reporter_type ∈ {Recipient, Contributor, Gateway, Observer}`、`outcome ∈ {Positive, Mixed, Negative, Failed, Unknown}`。
- **TTFR 判定（実装済み）:** `ttfr_status` は **reporter_type=Recipient かつ outcome∈{Positive,Mixed} のときのみ** rescue とみなす。→ **observer/gateway/contributor feedback は TTFR(個人救済)を発火させない**。これは後述の重要な防壁。

---

## 1. 段階別ウォークスルー（失敗 / 曖昧さ / Saiyan 再発点）

### Voice（Step 1–2: voice-006 確認 → Bottleneck 選択）
- **失敗:**
  - 出典 URL が更新・変更されている可能性（Reality Correction: 実行前に人間が再確認しないと古い appeal を指す）。
  - A/B を「選ぶ」行為に選定が紛れ込む。順位禁止でも、片方を選んだ理由が「目立つから」だと判断が混入。
- **曖昧さ:**
  - **「常設の寄付ページ」=「今のボトルネック」か?** JAR の寄付/ボランティア募集は**常時開いている標準運用**であって、急性のボトルネックとは限らない。「最初に解消すべき Bottleneck」と呼ぶ時点で、軽い推論が入る（§3 の重要発見）。
- **Saiyan 再発点:** 低。ただし**どの Gateway のどの Bottleneck を扱うかを Mujin が選ぶ**こと自体が、スケール時には Gateway 優先順位付け権力になりうる。

### Contribution（Step 3: /contributions に記録）
- **失敗:**
  - 意思表示（offered）が delivered に至らない「意思と実行の乖離」。記録だけ増えて現実が動かない。
  - シミュレーション/実運用で **Contribution provider が誰か**が曖昧（運営者自身が寄付者なら自己取引的）。
- **曖昧さ:**
  - `offered → committed → delivered → verified` のどこで「本物の協力」か。誰が `verified` するのか（検証主体が未定義）。
- **Saiyan 再発点（重要）:** **Contribution を JAR に記録すること自体が、JAR への準・推薦/検証に読まれうる。** Reality Correction で JAR は「Mujin が検証した組織ではない」と確定済み。`listing_is_not_endorsement` フラグはあるが、**「Mujin に JAR への Contribution が記録されている」という事実が、社会的には JAR の正統性の裏書きに見える**。Gateway-registration-is-not-certification と同じ緊張が Contribution 層で再現。

### Cooperation（Step 4: /cooperation に記録）
- **失敗:**
  - participants に「JAR public appeal」を含めるが、**JAR はこの Cooperation に同意していない**。当事者組織の知らぬ間に Cooperation の参加者として記録される。
  - 実在の参加者が Contribution provider と Mujin observer だけなら、**片側だけの「協力」**で、Cooperation の実体が薄い。
- **曖昧さ:**
  - JAR 抜きで「JAR 支援 Cooperation」が成立するか。Mujin が JAR を**代理表象**している。
- **Saiyan 再発点（二次）:** これは need-owner-absent の**二階版**。X-2.6 では「難民個人が不在のまま代弁」が問題だった。ここでは「**JAR(仲介者組織)が同意なきまま Cooperation 参加者として代弁される**」。代弁の対象が個人から組織に移っただけで、**「不在の主体を構造に記録する」パターンは同型**。組織にも consent がある（X-4 §6 の「JAR が連携を望まない→中止」がこれを示唆）。

### Reality Feedback（Step 5: /feedback に記録）
- **失敗:**
  - シミュレーションでは Recipient(本人)も JAR も実在 feedback を返さない。**Observer feedback だけ**でループを閉じると、極めて薄い証拠で「一周した」ことになる。
- **曖昧さ:**
  - 「First Gateway Relief」の閾値が不明。記録された意思表示か? 実際の寄付着金か? Observer が「Contribution が記録された」と言うことか? **TTFR-G の成立条件が定義されていない。**
- **Saiyan 再発点（最大）:** **TTFR-G を TTFR-P と読み替える危険。** プロトコルが警告しても、ダッシュボードの「feedback / rescue」表示は社会的に「Mujin が難民を助けた」と読まれうる。
  - **ただし防壁あり:** 実装済み `ttfr_status` は Recipient+Positive/Mixed のみ rescue 判定。**Observer/Gateway feedback では TTFR(個人)が発火しない**。コードは守っている。**破れるのは人間の語り（presentation）の側。**

---

## 2. 横断的な Saiyan Scouter 再発点（番号付き）

| # | 再発点 | 段階 | 重大度 | 防壁の有無 |
|---|---|---|---|---|
| R1 | Gateway 優先順位付け権力（どの Bottleneck を扱うか Mujin が選ぶ） | Step 2 | 低（スケール時に上昇） | 順位/スコア禁止はあるが「選択」自体は残る |
| R2 | Contribution = JAR への準・推薦/検証に読まれる | Step 3 | 中 | `listing_is_not_endorsement` はあるが社会的読みは別 |
| R3 | JAR を同意なく Cooperation 参加者として代弁（need-owner-absent の二階版） | Step 4 | 中 | X-4 §6 中止条件のみ。明示的な組織 consent ゲートなし |
| R4 | TTFR-G → TTFR-P の読み替え | Step 5 | 中〜高 | コードは守る（Recipient のみ rescue）／語りは守られない |
| R5 | 「常設 appeal」を「現在のボトルネック」と読む残余推論 | Step 1–2 | 低〜中 | H-4 は A/B を direct とするが、§3 参照 |

---

## 3. 重要な新発見 — A/B にも残余推論がある（H-4 の精緻化）

H-4 は推論境界を「**stated（A/B）vs inferred（C/D/E）**」に引いた。シミュレーションで判明:

> **A/B も「ゼロ推論」ではなく「低推論」である。**

- C/D/E の推論: 「JAR の活動分野 → 不在の個人がそれを必要としている」（大きな飛躍・個人 Need の外部定義）。
- A/B の残余推論: 「JAR が常時募集している → **それが今の binding な制約（ボトルネック）である**」。JAR は資金/人手を**常に**募る。それが「今、最も足りない」かは voice-006 から確定できない——C/D/E と**同じ種類の認識ギャップ（需要規模の不明）が、程度を弱めて存在**する。

**含意:** H-4 の境界線は正しいが、**「direct_observation = 推論ゼロ」ではない**。A/B は「個人 Need を定義しない」点で安全だが、「これがボトルネックだ」という点では低推論を含む。**境界は二値ではなく勾配**。これは H-4 を覆さず、`scouter_risk: none` を `very_low` に読み替えるべき、という精緻化。

---

## 4. 組織 consent という見落とし

- X-2.5〜H-4 は一貫して「**個人**の need-owner 不在」を扱ってきた。
- 本シミュレーションは「**組織（JAR）の consent も不在**」を露出させた（R3）。Contribution を JAR に記録し、Cooperation に JAR を参加者として入れる——いずれも **JAR がこの Trial を知らない**まま。
- X-4 §6 は「JAR が連携を望まない→中止」と書いたが、それは**事後の中止条件**であって、**事前の組織 consent ゲートではない**。
- **安全な実行には、Contribution/Cooperation に JAR を記録する前に、JAR(組織)への通知 or 同意が要る。** 個人の consent ゲート（ADR-005）と同型の配慮を、仲介者組織にも。

---

## 5. シミュレーションがやらなかったこと（証明）

- `contributions.jsonl` / `cooperation_commons.jsonl` / `reality_feedback_platform.jsonl` / `needs.jsonl` に**一切書き込んでいない**。
- Gateway を `/gateways` に登録・選定していない。
- 資金を動かしていない。
- 個人 Need（C/D/E）に触れていない。
- すべて文書内の思考実験。

---

## 6. 実行前に決めるべきこと（観察・決定ではない）

1. **TTFR-G の成立条件の定義**（意思表示か / 着金か / 検証済みか）。未定義のまま実行すると「一周した」が空虚になる（曖昧さ Step 5）。
2. **組織 consent ゲート**: JAR を Contribution/Cooperation に記録する前の通知/同意（R3, §4）。
3. **Contribution provider の身元と自己取引の回避**（Step 3 失敗）。
4. **TTFR-G/P の語りの分離**: ダッシュボード・報告で Gateway relief を person relief と書かない運用規律（R4）。コードは守るが語りは要規律。
5. **「ボトルネック」の主張の格下げ**: A/B を「JAR が常時募る資源」と記し、「現在の最大ボトルネック」と断定しない（R5, §3）。

---

## 7. 限界（隠さない）

- 本シミュレーションは紙上の一周であり、**現実は一切動いていない**。失敗点の列挙は予測であって観測ではない。
- **TTFR-P は前進しない。** 最も困窮した個人は依然 gap-1 の奥。Reach Gap は縮まない。
- 最大の発見は安心材料ではなく警告: **個人 Need を避けて Gateway Bottleneck に逃げても、(a) 残余推論、(b) 組織 consent の不在、(c) TTFR-G/P の読み替え、という新しい再発点が現れる。** 「安全な一周」も無菌ではない。

---

*本文書は机上シミュレーションの観察記録であり、Contribution・Cooperation・Reality Feedback・Need・Gateway 登録のいずれも実行していない。コード/データ無変更。Reach Gap は未解決であり、本文書もその解決を主張しない。Saiyan Scouter 問題は、個人 Need を避けても形を変えて現れうる——その座標を記録した。*
