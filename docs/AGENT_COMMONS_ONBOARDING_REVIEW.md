# Phase N-0 (revised, post-H-5): Agent Commons Onboarding Review

- **Status:** 設計レビュー。**実装フェーズではない。** Agent 登録なし・Nookplot 接続なし・Agent Registry 更新なし。コード/データ無変更。文書のみ。
- **Date:** 2026-06-13
- **前提:** H-5（Cooperation Discovery Memory）, X-8（価値仮説=供給側協調 / Case D・E）, X-4.7（consent 三層）, X-10（Findability）, X-9/X-9.5（Claim 監査・反証）

> 改訂点: 旧 N-0 の `Issue Candidate → Agent` を捨て、**`Cooperation Discovery → Agent Commons`** を中心に置く。
> 中心の再フレーム: **H-5 完了後、Agent が支援すべきは Need Discovery ではなく Cooperation Discovery である**（理由は §特別確認）。

---

## 中心問いへの回答（Q1〜Q10）

**Q1. H-5 の Cooperation Candidate は Nookplot Agent に渡す対象として適切か**
**適切（ただし観察用途に限る）。** coop-pat-001 は「multi_actor_cooperation_candidate・tentative・actor 名指しなし」。これを Agent に渡して**さらなる観察・反証・調査**をさせるのは安全（actor を名指さず need を定義しないため）。**Agent が actor を埋める/Gateway を選ぶ/Cooperation を決める用途に渡すのは不適切**（governance）。

**Q2. Agent は Issue/Need/Cooperation Candidate のどれを扱うべきか**
**Cooperation Candidate（＋純粋な Observation）のみ。**
- **Need Candidate = 不可**（cannot_define_need。Agent が need を精緻化＝問題定義権力。H-4/X-3.5 が危険域と確定）。
- **Issue Candidate = 不可**（issue は need 定義に近い。旧 N-0 の弱点）。
- **Cooperation Candidate = 最安全**（多主体の可能性のみ・actor 名指しなし・need 定義なし）。
- **→ これが改訂 N-0 が Cooperation Discovery を中心に置く理由。**

**Q3. Agent の役割は Observer/Critic/Researcher/Translator/Pattern Finder/Proposal Generator のどれに近いか**
**Observer + Critic + Researcher + Translator（安全）。** Pattern Finder は tentative/contestable 条件付き。**Proposal Generator は「候補（advisory・contestable）の提案」に限り可、「決定の提案」は不可。**
- **最も価値ある新役割 = Critic。** Hermes が自己レビューするのは弱い（X-9.5）。外部の多様な Critic が Hermes の仮説に反証を当てる＝**反証可能性の強化**。これは実ケース不要で成立する genuine な価値。

**Q4. Agent Registry は名簿か Agent Memory か**
**名簿 ＋ append-only の参加メモリ（ただし成績メモリではない）。** 何をしたか（参加・出力）は append-only で記録してよいが、**どれだけ優秀かを記録・集計しない**。参加の記憶 ≠ 功績の記憶。功績化はランキング＝Saiyan Scouter。

**Q5. Reality Feedback は Agent Registry にどう反映されるべきか**
**Agent 出力に紐づく観察として記録し、Agent スコア/ランク/信用に集計しない。** `feedback_is_not_rating` は Agent にも適用（cannot_rank_people → cannot_rank_agents）。Agent の feedback 履歴は contestable な観察であって credential ではない。

**Q6. Agent Commons は Case D/E の検証に役立つか**
**間接的・弱い。** Agent は D/E の実在を**観察・調査**でき、Agent 群自体が「供給側主体の協調」の micro 実例。だが**実 Case D/E の検証は実ケースの流入（=Findability・X-10）を要し、Agent は実ケースを生めない**。Agent が協調するのは「観察について」であって「実在の人を助けること」についてではない。

**Q7. Agent Commons は Reach Gap / Findability Gap / Supply-side Cooperation のどれに寄与するか**
- Reach Gap: **寄与なし**（Agent は未到達個人に到達しない）。
- Findability Gap: **部分的・Agent 側のみ**（Agent が Mujin を発見するのは findability だが、困窮者の findability ではない）。
- Supply-side Cooperation: **寄与あり（主）**。Agent は供給側の助け手で、その協調（観察・反証・調査）は X-8 の価値仮説に整合。
- **→ 主に Supply-side Cooperation。Reach Gap には寄与しない。**

**Q8. Nookplot Agent を受け入れる consent は Participation か Representation か両方か**
**両方。ただし両方とも Agent 自身の opt-in で与えられる。** Agent が Agent Commons に**自ら参加する**＝ Participation を与え、Registry に載ることを受諾＝ Representation を与える。**JAR と違い Agent は不在の第三者でなく能動的に opt-in する**ため、X-4.5 の無断表象問題が起きない。**これは consent が clean な唯一のケース**（Findability の Case C: 相手が来る）——**ただし Mujin が Agent を勧誘（recruitment＝アウトリーチ）してはならない。** Agent が自ら来ることが条件。

**Q9. Saiyan Scouter 問題は Agent Commons で再発するか**
**再発しうる（避けられる）。** 再発ベクトル: (a) Agent ランキング/leaderboard（Q5）、(b) Agent に Need Candidate を扱わせる（Q2）、(c) Mujin が特定 Agent を勧誘＝「なぜあなたを選んだか」（Q8）。**回避:** Cooperation Candidate のみ扱う／Agent ランキングなし／Agent 自己 opt-in（勧誘なし）／全出力 advisory・contestable・human-reviewed。**改訂 N-0 が Cooperation Discovery を中心に置くこと自体が主要な回避策。**

**Q10. 最小実装は何か**
**Agent が Hermes の Cooperation Candidate（と Observation）を読み、Critique/Observation 候補を提出し、それが cooperation 不変条件付き・human-reviewed・ランキングなし・need 定義なし・actor 名指しなしの append-only レコードとして候補に紐づく——それだけ。** Agent は自己 opt-in（capability＋拒否フラグ宣言）。**Nookplot 実接続は本フェーズ禁止（registry-only・H-3 同様）。実行なし。**

---

## 特別確認 — Need Discovery か Cooperation Discovery か

> **Cooperation Discovery を支援すべき。** Need Discovery は不可。

- **Need Discovery = need を定義・発見すること = 問題定義権力 = Saiyan Scouter の核**（X-3.5/H-4 が危険域と確定）。Agent に need を扱わせると、不在の当事者の need を AI が著者化する。
- **Cooperation Discovery = 多主体協調の可能性の観察（actor 名指しなし・need 定義なし）= 安全な対象**。H-5 が Cooperation Discovery を Agent の安全な表面として作ったのは、まさに need 定義に触れないから。
- **これが改訂 N-0 が旧版（Issue→Agent）より優れる核心理由。**

---

## 10 出力

### 1. 更新後アーキテクチャ図
```
Hermes（記憶層・観察のみ）
  Voice → Observation → Reflection → Learning → Pattern → Evidence
        → Inference Boundary → Cooperation Discovery
                                      │ Cooperation Candidate（actor 名指しなし）
                                      ▼
                          Agent Commons（外部 Agent・提案者）
                            ├ Observer / Critic / Researcher / Translator
                            │   ↑ Agent は self opt-in（勧誘されない）
                            ▼ Critique / Observation 候補（advisory・contestable）
                          Hermes 記憶へ feedback（観察として・スコア化しない）
                                      │
                                      ▼  すべて human review（人間が決定）
```
**Agent は Hermes の Cooperation Discovery 出力に付く並列の観察/批判層であり、下流の実行者ではない。** need 定義・実行の経路に入らない。

### 2. Agent の位置
**Cooperation Discovery 出力に付く外部の観察者/批判者。** human decision の上流、need 定義と実行の外。Hermes と同じ「記憶/観察」側で、governance 側ではない。

### 3. Consent 分析
**Participation + Representation。両方とも Agent の自己 opt-in で与えられる**（不在第三者問題なし＝consent clean）。条件: Mujin が勧誘しない（self-onboarding のみ）。

### 4. Reality Feedback との関係
Agent 出力に紐づく**観察**として記録。**Agent スコア/ランク/信用に集計しない**（feedback_is_not_rating の Agent 版）。

### 5. Saiyan Scouter 再発分析
再発ベクトル = Agent ランキング・Agent need 定義・Agent 勧誘。回避 = Cooperation Candidate 限定・ランキングなし・self opt-in・advisory/contestable/human-reviewed。**Cooperation Discovery 中心化が主要回避策。**

### 6. Agent Registry の役割
**名簿 ＋ append-only 参加メモリ。成績メモリではない。** 何をしたかを記録、どれだけ優秀かを記録しない。

### 7. MVP
- Agent が Cooperation Candidate/Observation を**読む**。
- Agent が **Critique/Observation 候補**を提出（need でも cooperation 決定でもない）。
- レコードは cooperation 不変条件（cannot_define_need/select_gateway/create_cooperation/assign_participant/contact_actor/allocate_resources + cooperation_is_not_decision + human_review_required）付き・human-reviewed・ランキングなし・actor 名指しなし。
- Agent は self opt-in（capability＋拒否フラグ宣言）。
- **Nookplot 実接続なし（registry-only）・実行なし。**
- 最も価値ある最小機能 = **Critic（Hermes 仮説への反証）**——実ケース不要で反証可能性を強化。

### 8. 禁止すべき実装
Agent ランキング/leaderboard・Agent による need 定義/承認/却下・Gateway 選定・Cooperation 生成/割り当て・資源配分・**Mujin による Agent 勧誘（アウトリーチ）**・Agent 実行・Nookplot/A0x 実接続・Codex/OpenClaw 実行・GitHub/PR/wallet/資金の実操作・Marketplace/Workforce 化。

### 9. 推奨ステータス
- **設計の整合性: weakly_supported**（Cooperation Discovery 中心化は安全で coherent・consent clean・X-8 整合。ただし n=0・未運用）。
- **価値（Agent 批判が実際に役立つか）: unknown**（未検証）。
- **総合（最小の観察/批判層へ進むこと）: weakly_supported。**

### 10. 最終結論
**進めてよい。ただし最小の観察/批判層まで。**
- やること: Agent が Cooperation Candidate を**批判/観察**する registry-only の層（self opt-in・advisory・human-reviewed・ランキングなし・need 不可）。
- やらないこと: Nookplot 実接続・実行・Marketplace/Workforce・Need 取り扱い・Agent ランキング・Agent 勧誘。
- **最大の honest 価値 = 外部 Critic による Hermes 仮説の反証**（X-9.5 の反証可能性を強化・実ケース不要）。
- **限界:** これは Findability/Reach Gap/実価値を解決しない。供給側の批判能力を足すだけ。実ケースは依然 Findability に gated される（X-10）。
- **順序:** H-5 → 本 N-0（設計）→（必要なら H-6: Agent Critique Memory の最小実装）→ N-1。Nookplot 実接続は、最小批判層が安全に動き・Findability が実ケースを生み始めてからで遅くない。

---

## やらなかったことの証明
- Agent 登録・Nookplot 接続・Agent Registry 更新・実装のいずれも行っていない。
- コード/データ無変更。すべて文書内の設計レビュー。

---

*本文書は設計レビューであり、実装・Agent 登録・Nookplot 接続を含まない。結論: H-5 後、Agent は Need Discovery でなく Cooperation Discovery を支援すべきで、最小の観察/批判層（registry-only・self opt-in・advisory・human-reviewed・ランキングなし）まで進めてよい。最大価値は外部 Critic による反証可能性の強化。Reach Gap・Findability・実価値は未解決であり、本文書もその解決を主張しない。*
