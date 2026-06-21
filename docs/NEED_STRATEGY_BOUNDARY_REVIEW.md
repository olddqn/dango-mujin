# Phase N-1.6: Need Strategy Boundary Review

- **Status:** 観察レビュー（三層モデルの監査）。**Need/Gateway/Contribution/Cooperation 生成なし。** コード/データ無変更。文書のみ。
- **Date:** 2026-06-13
- **前提:** N-1.5（Need Definition ┃ Need Resolution の境界 = H-4 の direct ┃ inference）, X-3.5 / H-4（問題定義権力）, X-4.7（consent 三層）, X-8（供給側協調）

> 中心問い: **Agent は「何が必要か」を決めてはいけない。では「どう解決するか」はどこまで提案してよいのか。**
> 結論先取り: **三層（Definition / Strategy / Resolution）は妥当。Agent は Strategy と Resolution を扱え、Definition は扱えない。ただし Strategy/Resolution の入口条件（当事者確認済み direct need）は現在 n=0 で空、かつ Strategy/Resolution も consent-free ではない（追加発見）。**

---

## 1. 三層モデルの確認

```
Need Definition   「この人には翻訳が必要だ」を決める        → Agent 不可（問題定義権力）
      ↓
Need Strategy     「翻訳 Need をどう満たすか」を考える        → Agent 可（条件付き）
      ↓
Need Resolution   確定した解法の材料を作る（翻訳の実行等）    → Agent 可（条件付き）
```

- **Definition と Strategy/Resolution の違い:** 対象が **Need** か **Solution** か。Strategy は Solution についての推論（Q3: 部分的推論だが対象は Need でなく Solution）。
- **N-1.5 からの精緻化:** N-1.5 は Definition ┃ Resolution の二層だった。N-1.6 は間に Strategy を挿入し、Agent の領域を Resolution だけでなく Strategy にも広げる。**監査結果: 妥当。** ただし下記の gate と追加 consent 条件付き。

---

## 2. Q1〜Q10 の監査

**Q1. Need Strategy は Need Definition と同じか** → **違う（追認）。** Definition は「何が必要か」、Strategy は「固定された Need をどう満たすか」。**監査の補強:** Strategy が「実は別の need では」と再考した瞬間、Definition に回帰する。**Strategy は固定 Need の内側に留まること**が条件。

**Q2. Need 未確定で Strategy 生成は可能か** → **不可（追認）。** `Need Candidate → Strategy` は Need Definition の代理実行＝Saiyan Scouter 再発。**監査の補強（N-1.5 と接続）:** 「確定」は H-4 の **direct_observation かつ当事者確認済み**を要す。人間が inference を承認しただけでは確定でない。**voice-006 の個人 need（C/D/E）は全て inference ゆえ、Strategy の入口に到達しない。**

**Q3. Strategy は推論か** → **部分的に推論・対象は Solution（追認）。** Need でなく Solution についての推論なので、Definition の問題定義権力には当たらない——**ただし Solution の推論が「最適」判断に滑れば別の権力（解の選定）になる**（Q4/Q7 と連動）。

**Q4. Agent が提案できるもの** →
- Allowed: 翻訳方法**比較**・法的支援の**調査**・求人経路**比較**・教育プログラム**比較**・協力主体候補の**調査**。
- Forbidden: 何が必要か・誰を助けるべきか・どの Need を優先・どの Gateway が最適・どの人を選ぶか。
- **監査の補強（境界の鋭利化）:** 許可されるのは **enumerate / characterize（選択肢を並べ・トレードオフを示す）**。禁止は **rank / declare-best（優劣で並べる・最適と宣言）**。「比較」は OK・「最適」は NG の線は、**選択肢の提示（人間の決定を informs）** と **決定の代行** の境界。

**Q5. Funding は特別扱いか** → **Yes・最危険（追認）。** Funding Strategy は資源配分へ接続＝`Strategy → Decision` が最短。**監査の補強:** Funding Strategy は「公開に存在する資金メカニズムの調査」に留め、「我々の資金をどう配分するか」には決して触れない。比較すら配分提案に滑りやすい。

**Q6. Nookplot Agent は何を返すべきか** →
- 返す: `{solution_candidate_id, need_id, proposal, assumptions[], risks[], confidence:"low"}`。
- 返さない: `{recommended_need, priority, best_gateway, optimal_solution}`。
- **監査:** 妥当。返す側は assumptions/risks/confidence を必須にすることで、出力が「決定」でなく「吟味材料」であることを構造的に保証。返さない側は H-5/N-1R の禁止フラグ（cannot_select_gateway 等）と一致。

**Q7. Hermes は何を見るか** → Solution Candidate の**前提・飛躍・未検証部分**を見る。採用しない・決定しない（追認）。**監査の補強:** Hermes は Solution Candidate を Pattern と同様に扱う——記録し、推論境界（前提/飛躍）を観察し、決して採用・決定しない。Solution Candidate 用の inference_boundary を将来作るなら H-4 と同型。

**Q8. Nookplot の本来価値は何か** → Need Discovery ではなく `Need → 多様な Solution Candidate 生成`（追認）。**監査の統合:** Nookplot の価値は二つに分かれる——(a) **Critic/Counter-Argument**（システム級・反証可能性・常に有効・N-1R）、(b) **Solution Strategy 生成**（need 級・確定 need に gated・現在空）。両方有効だが、現在 live なのは (a) のみ。

**Q9. Saiyan Scouter との関係** →
- NG: `Need Candidate → Agent → Need 生成`。
- OK: `Human Approved Need → Agent → Solution Candidate`。
- **追認。** ただし「Human Approved」は当事者確認済み direct need を意味すること（Q2 の補強）。

**Q10. 最初の Nookplot Task 候補** → 翻訳実現方法3案・就労支援経路比較・法的支援モデル調査（追認）。**監査の但し書き:** これらは「Need が確定している場合」の例。**voice-006 にはそのような確定個人 need が無い**ため、これらは現時点で実投入できる Task ではなく、**入口条件が満たされたときの雛形**。

---

## 3. 追加発見 — Strategy / Resolution も consent-free ではない（X-4.7 への接続）

> ユーザー提示の三層モデルが明示しなかった点。

- Definition は**当事者の著者性**を要す。Strategy/Resolution は当事者の**確定 need ＋継続的同意**を要す——**当事者は Strategy を拒否できる**（「その方法では助けてほしくない」）。
- Agent が生成した Solution Strategy が当事者の入力なしに採用されれば、**X-4.5/X-4.7 の「無断表象」が解法レベルで再発**する。
- **→ Strategy/Resolution の出力は、当事者（と人間レビュア）が選ぶための advisory 材料であって、自動採用されない。当事者の consent は「助けられるか否か」だけでなく「どう助けられるか」にも及ぶ。**
- これは N-1.6 を consent シリーズ（X-4.7）に接続する。三層は**問題定義権力**だけでなく**解法表象の consent** も通過しなければならない。

---

## 4. 提案された統合フローの監査

```
Human Voice → Need Candidate → Human Review → Need → Nookplot Task
            → Agent → Solution Candidate → Hermes Review → Human Approval
            → Contribution / Cooperation
```

**構造としては妥当**（Saiyan Scouter 回避・Nookplot 活用・H-4 整合・X-8 接続）。**ただし honest な留保:**
1. **入口の "Human Voice" が今は無い。** 唯一の実 Voice（voice-006）は Gateway Voice で、個人の direct need を生まない。フローは正しいが、個人 need については**現在 enter できない**。
2. **"Human Review → Need" の Review は、当事者の need であることの確認（consent）でなければならない**——アナリストの inference を別の人間が承認しただけでは不十分（Q2/Q9 の補強）。
3. **フローは Findability を解決しない。** "Human Voice が届く"を前提するが、それは X-10 の Findability に gated。
4. **"Human Approval → Contribution/Cooperation" の前に、当事者の解法 consent（§3）を挟む必要**——Solution が当事者に押し付けられないため。

---

## 5. 推奨ステータス

- **三層モデルの設計整合性: weakly_supported**（coherent・H-4 整合・X-8 接続・consent 補強で完成度向上。だが n=0・未運用）。
- **現在の実用可能性: System Tasks/Critic（Type A）は live、Strategy/Resolution（Type B）は gated で空。**
- **統合フロー: 構造 weakly_supported / 現在の enter 可能性 unknown（入口の Human Voice が未到達）。**

---

## 6. 暫定結論

> **三層 Definition / Strategy / Resolution は妥当。Agent は Strategy と Resolution を扱え（N-1.5 を広げる）、Definition は扱えない。境界は H-4 の direct/inference に一致し、入口は当事者確認済み direct need（現在 n=0 で空）。Strategy/Resolution は問題定義権力だけでなく当事者の解法 consent も通過する。現在 live なのは System Tasks/Critic（Type A）のみ。統合フローは構造的に自然だが、入口の Human Voice は Findability に gated で未到達。**

---

## 7. 成功条件の確認

- ✅ Nookplot 接続なし / Agent 登録なし / Task 生成なし / Need 生成なし / Contribution 生成なし / Cooperation 生成なし / 文書のみ（コード/データ無変更）。

---

*本文書は Need Strategy 境界の監査記録であり、Need/Gateway/Contribution/Cooperation を生成しない。三層モデルは妥当で Agent は Strategy/Resolution を扱えるが、入口は当事者確認済み direct need（n=0 で空）に gated され、Strategy/Resolution も当事者の解法 consent を要する。現在 live は Type A（System/Critic）のみ。Reach Gap・Findability・実価値は未解決であり、本文書もその解決を主張しない。*
