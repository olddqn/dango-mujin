# Phase N-1.7: Solution Candidate Boundary Review

- **Status:** 観察レビュー（提案／実行の境界の監査）。**Need/Gateway/Contribution/Cooperation/Execution 生成なし。** コード/データ無変更。文書のみ。
- **Date:** 2026-06-13
- **前提:** N-1.6（Definition / Strategy / Resolution・Solution consent）, H-4（推論境界）, X-4.7（consent 三層）

> 中心問い: **Agent が生成した Solution Candidate は、どこから先が Execution になるのか。**
> 結論先取り: **境界の正体は「選択（set を 1 に減らす原子的行為）」。Agent は Solution Candidate（複数・advisory）まで。選択・推薦・優先・配分・実行指示は不可。**

---

## 1. 四層モデルの確認と精緻化

```
Need Definition  「何が必要か」          → Agent 不可
      ↓
Need Strategy    「どう満たすか」         → Agent 可（確定 need 限定）
      ↓
Need Resolution  解法の材料を作る         → Agent 可（同上）
      ↓
Need Execution   選んで実行する           → Agent 不可（人間＋当事者）
```

さらに横断する境界:
```
Solution Candidate（複数・提案） ┃ Execution Candidate（選択済み・実行）
```
**監査結果: 妥当。** N-1.6 の三層に Execution を加え、Solution ┃ Execution の境界を立てるのは正しい。以下、その境界を鋭利化する。

---

## 2. 精緻化① — 境界の正体は「選択」

> **Solution ┃ Execution の境界は曖昧ではない。それは「選択（複数の候補を 1 つに減らす）」という原子的行為に落ちる。**

- 列挙 → 比較 → 評価 までは **set（複数・advisory）= Solution**。
- 「これを採用する」= **set を 1 に縮約 = 選択 = Execution 側の最初の一歩**。
- **誰が選択するかが決定的:** Agent が `"recommended": true` / `"best"` を返した瞬間、**Agent が選択した = 越境**。Agent が set を返し、**人間＋当事者が選択**すれば境界は保たれる。
- **→ 境界保持の規則: 人間＋当事者が選ぶまで set を複数のまま保つ。** Agent の出力は常に plural。

---

## 3. Q1〜Q10 の監査

**Q1. Solution Candidate とは** → 実行可能性のある**提案**。まだ実行でない（追認）。翻訳会社A/B・AI翻訳・ボランティア翻訳の**列挙**は提案。

**Q2. どこから Execution か** → 列挙→比較→評価までは Solution。「採用する」で Execution（追認）。**補強: 採用=選択=§2 の原子的境界。**

**Q3. Funding はなぜ危険か** → Strategy→Allocation 直結（追認）。**精緻化②（重要）: Funding は候補そのものが実行である。** 「JAR へ1000ドル寄付」は既に Allocation——**translation と違い、候補と実行が分離できない**（翻訳は「方法の候補」と「翻訳の実行」が別だが、寄付は「いくら誰に」が候補にして実行）。**→ Funding には execution と分離した安全な Solution-Candidate 空間が存在しない。安全な出力は「公開に存在する資金メカニズムの一般調査」のみで、特定の「いくら誰に」は常に Execution Candidate。**

**Q4. Legal はなぜ危険か** → 「この手続きを行うべき」は法的判断に接近（追認）。許可=利用可能な法的支援制度の一覧／禁止=この制度を利用せよ。**補強: 選択肢の記述（informs）┃ 行動の指示（directs）の境界。**

**Q5. Translation はなぜ比較的安全か** → 翻訳結果は情報変換でそれ自体は Execution でない（追認）。**補強: ただし「本人へ提出」で Execution。** Resolution 成果物（翻訳文）は artifact として安全だが、**その使用（提出・行動）は Execution で当事者 consent を要す**。最安全の領域ですら使用の縁に Execution がある。

**Q6. Agent が返してよいもの** →
- Allowed: `{solution_candidates:[…], assumptions, risks, alternatives}`（複数・吟味材料）。
- Forbidden: `{recommended:true, priority:1, best, must_do:true}`（選択・順位・指示）。
- **監査: 妥当。** Allowed が `alternatives` を含み plural を強制する点が §2 の境界保持と一致。Forbidden は既存フラグ（cannot_select_gateway / cannot_allocate_resources）の Solution 版。

**Q7. Hermes は何を見るか** → 提案→前提→飛躍→**隠れた決定**（追認）。**精緻化③（重要）: Hermes の核心役割 = Solution Candidate に密輸された決定の検出。** 例「寄付すべき」→ なぜ？→ 誰が決めた？→ **Funding Allocation 発見**。これは H-4 の同型——H-4 が「推論の起点」を見つけるように、Hermes は「**決定の起点（candidate が選択/配分を隠す地点）**」を見つけ、人間に晒す。Hermes は採用も決定もしない。

**Q8. Need Owner の役割** → Need Consent だけでは不足、Solution Consent も要る（N-1.6 の §3 を採用・追認）。**精緻化④: consent は三段になりうる。**
```
Need Consent      これは私の need である
   ↓
Solution Consent  この解法（の方向）に同意する
   ↓
Execution Consent  今それを実行してよい（例: ボランティアBが私に連絡してよい）
```
Solution への同意と Execution への同意は分かれうる（解法の承認 ≠ 今すぐ実行の承認）。**当事者の agency は Definition だけでなく Solution と Execution まで及ぶ。**

**Q9. Saiyan Scouter 再発点** → `Need Definition → Agent → Best Solution` = 問題定義＋意思決定を Agent が行う・最も危険（追認）。**補強: 二つの権力（問題を定義する／解法を決定する）は別々に危険で、両方を行う Agent が最大危険。** N 系列は両者を別の人間/当事者に留めることで分解する。

**Q10. 最終境界** →
- 安全: `Need → Agent → Multiple Solution Candidates → Human Review → Need Owner Consent`。
- 危険: `Need → Agent → Recommended Solution → Execution`。
- **追認。差は plural 候補＋当事者選択 ┃ singular 推薦＋自動実行。**

---

## 4. 暫定結論（監査後）

> **四層 Definition / Strategy / Resolution / Execution に加え、Solution Candidate ┃ Execution Candidate の境界が存在する。Agent が扱えるのは Solution Candidate（複数・advisory）まで。境界の正体は「選択」で、Agent は選択・推薦・優先順位・資源配分・実行指示を行ってはならない。**
> 追加: **Funding は候補=実行で安全な Solution-Candidate 空間が無い（一般調査のみ可）。Hermes は隠れた決定の検出器。consent は Need→Solution→Execution の三段。**

---

## 5. 推奨ステータスと現在地（honest）

- **四層＋境界モデルの設計整合性: weakly_supported**（coherent・N-1.6 を鋭利化・Funding 崩壊と決定検出を追加）。
- **現在の実用可能性:** すべて**確定 direct need を前提**するが、それは **n=0（個人 direct need なし）**。→ **Solution Candidate も現時点でどの実個人 need についても生成できない。** live なのは Type A（System/Critic）のみ（N-1R）。
- **境界の作業は健全だが現在は理論的。** 実投入は実 Voice の到達（Findability・X-10）に gated。

---

## 6. 成功条件の確認

- ✅ Nookplot 接続なし / Agent 登録なし / Task・Solution・Execution 生成なし / Need 生成なし / Contribution 生成なし / Cooperation 生成なし / 文書のみ（コード/データ無変更）。

---

*本文書は Solution Candidate と Execution の境界の監査記録であり、何も生成しない。境界の正体は「選択」で、Agent は複数の Solution Candidate まで・選択/推薦/優先/配分/実行は不可。Funding は候補=実行で安全空間なし、Hermes は隠れた決定の検出器、consent は Need→Solution→Execution の三段。すべて確定 direct need を前提し、それは n=0 ゆえ現在は理論的。Reach Gap・Findability・実価値は未解決であり、本文書もその解決を主張しない。*
