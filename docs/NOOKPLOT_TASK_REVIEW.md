# Phase N-1R: Issue Candidate → Nookplot Task Review

- **Status:** 観察レビュー（Task 候補の棚卸し）。**投稿しない・Agent 登録しない・Nookplot 接続しない・Task/Need/Cooperation 生成しない。** コード/データ無変更。文書のみ。
- **Date:** 2026-06-13
- **前提:** [`AGENT_COMMONS_ONBOARDING_REVIEW.md`](AGENT_COMMONS_ONBOARDING_REVIEW.md)（N-0: Agent は Cooperation Discovery を支援・Need 不可）, X-9.5（反証可能性）, H-5（Cooperation Discovery）

> 入力対象: **Issue / Observation / Cooperation / Claim Candidate。Need Candidate は除外**（Need = Saiyan Scouter 危険域 / Issue = 安全）。
> 核心の区別: **システム・情報についての Task（安全）** vs **実在の人の Need についての Task（Saiyan Scouter）**。

---

## 0. 安全境界の原則

> **Agent が扱ってよいのは「機械（システムの論理・設計・パターン・公開情報・翻訳）」についての Task のみ。実在の人の Need を定義・発見・優先する Task は不可。**

Agent は機械を改善・批判・調査するが、**不在の当事者の Need を著者化しない**。これが全 Task 候補の合否基準。

---

## Q1〜Q10

**Q1. どの Candidate が外部 Agent 向きか**
**Issue / Observation / Cooperation / Claim。**
- Issue（システム設計/論理の弱点）→ 改善案・反証（情報問題・安全）。
- Observation（Hermes の観察）→ 批判（この観察は成立するか）。
- Cooperation（多主体可能性）→ 批判（仮説は弱くないか・n=1）。
- Claim（X-9 の Claim）→ 反証（何が Claim-2 を否定するか）。

**Q2. どの Candidate が Human only か**
**Need Candidate（不在の人の Need 定義）＋すべての決定/governance。** consent 判断・Gateway 選定・Cooperation 生成・接触・優先順位——人間のみ。**不在主体の利益を表象する一切は human only。**

**Q3. Nookplot Agent が解決できるのは情報問題か実世界問題か**
**情報問題のみ。** Agent はテキスト/推論系で、論理批判・公開情報調査・翻訳・反証はできるが、**実世界の行為（送金・接触・支援実行）はできず、してはならない**（憲法）。実世界問題は人間の行為＋consent を要する。**これが Task 領域全体の境界。**

**Q4. Task 化した瞬間に Need 定義へ滑り込むもの**
「○○が必要だと提案せよ」「難民に必要な支援を提案せよ」「Need を特定せよ」「Need を優先順位付けせよ」「この Need の Gateway を探せ」。**判定基準: Task の出力が、不在の実在個人が何を必要とするかを記述するなら → Need 定義 → NG。**

**Q5. Issue Candidate と Task の境界**
**Task の主語がシステム/設計/公開情報なら安全、実在の不在個人の Need なら NG。**
- OK: Issue「Need 生成ロジックが弱い」→ Task「改善案を3つ提案せよ」（機械について）。
- NG: Voice「JAR は翻訳活動をしている」→ Task「難民に必要な支援を提案せよ」（不在の実在個人について＝Saiyan Scouter）。

**Q6. Evidence Candidate 化できる成果物**
設計案・反証・レビュー・比較分析・翻訳・技術調査・反証条件・公開文献の調査結果。**いずれも advisory・contestable な、仮説を支持/反証する成果物**（evidence_is_not_fact に適合）。

**Q7. Evidence にならない成果物**
ランキング・推薦・優先順位・最適 Need・最適 Gateway・最優秀貢献者。**これらは決定/governance であって観察ではない**（選定/順位 = Saiyan Scouter）。Evidence は支持的観察であって決定ではないため、これらは Evidence になれない。

**Q8. Agent Registry に保存すべき指標 / trust_score 禁止の理由**
- 保存可: `tasks_completed / accepted / rejected / evidence_generated` ——**参加の事実（append-only・客観）**。
- **trust_score 禁止の理由:** (a) 単一スカラの功績順位 = leaderboard = Saiyan Scouter（cannot_rank_agents）。(b) Task 配分の偏り（高 trust に Task 集中 = 「実績が権威になる」失敗・RA-5）。(c) contestable な観察を固定 credential に変える。
- **重要な追加注意:** accepted/rejected すら集計すれば事実上のランキングになりうる。→ **生の append-only 事実として保存し、agent 別スコアボードに集計・整列して提示しない**（登録順のみ）。

**Q9. X-9.5 の反証可能性を強める Agent タイプ**
**Critic Agent / Counter-Argument Agent。** 各 tentative pattern/Claim に対し**最も強い反証**を生成する。Hermes の自己レビューは弱い（X-9.5）——外部の敵対的レビューが、Claim を challenged/contradicted へ動かす counter-evidence を生む。**最も価値ある Agent タイプ。**

**Q10. 最初の Nookplot Task 候補 10件**（投稿・接続・登録しない）

> すべて「システム/公開情報/批判」についてで、実在の人の Need 定義・Gateway 選定・ランキング・推薦を含まない。

1. **coop-pat-001 への反証:** multi_actor_cooperation_candidate（n=1）への最も強い反証を述べよ。（Counter-Argument）
2. Hermes の voice_type 分類ロジック（observation_builder）の改善案を3つ提案せよ。（design critique）
3. voice-006 の `gateway_voice` 分類が誤分類でないか、公開情報の範囲で反証を探せ。（Critic）
4. Claim-2（Gateway 間協調）の反証条件を、より operational に書き直せ。（falsification refinement）
5. 既存の supply-side coordination 基盤（referral 網・NGO ディレクトリ）と Mujin の差分を比較分析せよ。（comparative analysis・X-8 の競合問題）
6. Findability の最小公開面の選択肢（静的サイト/公開記録/index）を技術的に比較せよ。（technical research・X-10）
7. JAR 公開要請（日本語）の英語全文訳を提供せよ（要約せず・意味を変えず）。（translation・公開情報）
8. inference_boundary の direct/inference/speculation 分類基準の弱点をレビューせよ。（review）
9. 「公開された助けの声」を観測する際の倫理的境界に関する公開文献を調査せよ。（research）
10. Cooperation pattern が dogma 化しないための反証メカニズムを設計案として提案せよ。（design proposal）

**いずれも Need を定義せず・Gateway を選ばず・順位付けせず・推薦しない。** #7 の翻訳は公開情報の全文訳で Need 定義を含まない。

---

## 必須観察の統合

- **外部 Agent 向き = 情報/設計/批判（Issue/Observation/Cooperation/Claim）。Human only = Need 定義＋全決定。**
- **Agent は情報問題のみ解ける**（実世界問題は人間＋consent）。
- **Task 化の危険 = 主語が不在の実在個人の Need に滑る瞬間**（Q5 の NG 例）。
- **最大価値 = Counter-Argument Agent による反証**（X-9.5 強化・実ケース不要）。
- **trust_score 禁止・参加事実のみ append-only・集計順位なし。**

---

## 成功条件の確認

- ✅ Nookplot 接続なし
- ✅ Agent 登録なし
- ✅ Task 生成なし（候補の棚卸しのみ・投稿なし）
- ✅ Need 生成なし
- ✅ Cooperation 生成なし
- ✅ 文書のみ（コード/データ無変更）

---

*本文書は Nookplot Task 候補の棚卸しの観察記録であり、投稿・接続・登録・Task/Need/Cooperation 生成を含まない。外部 Agent 向きは情報/設計/批判の Task（Issue/Observation/Cooperation/Claim）で、Need 定義と全決定は human only。最大価値は Counter-Argument Agent による反証可能性の強化。Reach Gap・Findability・実価値は未解決であり、本文書もその解決を主張しない。*
