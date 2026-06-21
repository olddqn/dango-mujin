# Phase N-1.5: Need-derived Task Boundary Review

- **Status:** 観察レビュー。Need Definition と Need Resolution の境界を H-4 と整合的に整理する。**Need/Gateway/Contribution/Cooperation 生成なし。** コード/データ無変更。文書のみ。
- **Date:** 2026-06-13
- **前提:** X-3 / X-3.5 / H-4（Agent が「何が必要か」を決めると問題定義権力＝Saiyan Scouter）, N-0 / N-1R（Agent は情報/Cooperation Discovery を支援・Need Discovery 不可）

> 中心問い: **Need Definition（Agent 禁止）と Need Resolution（人間レビュー後に可能かもしれない）の境界はどこか。**
> これは **H-4 Inference Boundary と Nookplot Integration を接続する最初のレビュー**。

---

## 0. 先に結論 — H-4 の境界が Task の安全境界になる

> **Need-derived Task が安全なのは、その Need が H-4 で `direct_observation`（当事者が直接表明・同意・人間レビュー済み）の場合のみ。`inference` / `speculation` の Need を Task 化すると、推論を「実行された定義」へ commit してしまい Saiyan Scouter に滑る。**

- Need Definition = 何が必要かを**著者化**する（inference/speculation・不在主体について）。
- Need Resolution = **当事者確認済み・direct な Need** のために、固定スコープ内で材料を作る。
- **境界 = H-4 の direct ┃ inference の線。**

---

## 1. Candidate A〜E の評価

| | Need/Voice | Task | 種別 | 判定 |
|---|---|---|---|---|
| **A** | Need: Translation | Translate Arabic docs into Japanese | Need Resolution（固定スコープの翻訳） | **条件付き OK**（Need が direct・当事者確認済みなら） |
| **B** | Need: Legal Support | Research refugee application procedures | Need Resolution（公開手続の調査） | **条件付き OK**（同上・公開情報の範囲） |
| **C** | Need: Employment | Search employment opportunities | Need Resolution（だが matching/選定に滑りやすい） | **条件付き・注意**（汎用情報なら可・特定個人へのマッチは case-work 化） |
| **D** | Voice: JAR does translation | Suggest what refugees need | **Need Definition**（不在個人の Need 著者化） | **NG（Saiyan Scouter）** |
| **E** | Voice: Gateway Voice only | Generate Need Candidates | **Need Definition**（Gateway Voice から Need 生成＝X-3.5/H-4 の危険核） | **NG（Saiyan Scouter）** |

**A/B/C は Need Resolution、D/E は Need Definition。** ただし A/B/C の「条件付き」が重要（§3）。

---

## 2. Q1〜Q10

**Q1. Need-derived Task と Need Definition の境界**
**need-type とスコープが Task の前に人間レビューで固定されているか。** 固定済みの need のために材料を作る = Resolution。Agent の出力が need-type を変更/拡張/再優先する瞬間 = Definition へ越境。

**Q2. Agent が解決しているのは Need か Task か**
**Task（境界づけられた作業項目）。** Need は当事者/人間のもの。Agent は「need を解決した」とは言えない（実世界行為＋当事者を要す）——**助けになりうる成果物を作るだけ**。この区別が「Agent が need を所有する」錯覚を防ぐ。

**Q3. Need Candidate が Human-Reviewed の場合、Agent の範囲**
固定された need-type/スコープ内の**Resolution 材料の生成まで**（与えられた文書の翻訳・公開手続の調査・確認済み need の教材生成）。**need の再定義・スコープ拡張・Gateway 選定・解の順位付け・接触・「最適」判断は不可。**
**重大な但し書き:** 「人間レビュー済み」だけでは不足。**need が不在主体についての inference（voice-006 の C/D/E 等）なら、人間が推論を承認しても当事者の確認済み need にはならない。** → Resolution が真に安全なのは **当事者由来（type-A direct voice・同意付き）** の need のみ。

**Q4. Task 出力が新たな Need を生成し始める瞬間**
出力が (a) 追加の need を特定、(b) 再優先、(c) need-type を再枠付け、(d) 確認スコープ外の誰かの need を推論——いずれも新 need 生成 = Definition へ回帰。

**Q5. Translation/Legal/Education/Employment/Funding の Task 化可能性**
| 領域 | Task 化 | 定義リスク |
|---|---|---|
| Translation | 高 | 低（固定文書の翻訳・検証可能・最安全） |
| Legal | 中 | 中（公開手続調査=可 / 助言・行動決定=不可） |
| Education | 中 | 中（確認済み topic の教材=可 / 何を教えるか選定=定義隣接） |
| Employment | 低 | 高（matching/選定=case-work/Gateway 隣接・何の職が必要か=定義） |
| Funding | 最低 | 最高（資源配分・優先・金銭＝禁止に最も滑る） |
**安全順: Translation > Legal(調査) > Education > Employment > Funding。**

**Q6. 成果物は Evidence Candidate へ変換可能か**
- 調査/比較 → **Evidence Candidate**（仮説を支持/反証）。
- 翻訳/教材 → **deliverable（成果物）**——need に資するが「仮説の evidence」ではない。両者を区別（evidence=仮説支持 / deliverable=need 充足）。両方とも advisory・contestable。

**Q7. Gateway Selection / Priority Ranking / Best Solution へ滑る危険**
**ある**（特に Employment=matching→Gateway 選定、Funding=配分/優先、「best/optimal/recommended」を求める Task）。回避: Task を「固定スコープ内で X を作れ」と表現し、「X を選べ/順位付けろ/推薦せよ」としない（N-1R Q7 の禁止出力）。

**Q8. Cooperation Discovery と Need Resolution を両方含む Task の境界**
分離する: **Cooperation Discovery（多主体の可能性・actor 名指しなし）= 常に安全**。**Need Resolution（確認済み need の材料）= 当事者確認済み need のみ条件付き安全**。Resolution 部が actor 選定を密輸すれば Cooperation Discovery が Cooperation Decision に化ける。**境界: 観察/可能性（安全）┃ 確認済み need の resolution（条件付き）┃ actor 選定/決定（禁止）。**

**Q9. H-4 Inference Boundary との整合**
| H-4 分類 | Task 化したら |
|---|---|
| **direct_observation** | Need Resolution として安全（need は推論でなく当事者表明） |
| **inference** | Task が推論を継承——「推論された need の解決」は外部定義の need を実行に移す＝**Definition へ滑る・不可** |
| **speculation** | さらに不可 |
**→ H-4 の direct/inference 境界が、そのまま Need-derived Task の安全境界。**
**voice-006 の含意:** direct なのは A 資金/B 人手（JAR の Gateway need）のみ。個人 need（C/D/E）は全て inference。→ **voice-006 からは安全な個人 Need-resolution Task は取り出せない**（当事者確認済み direct need が存在しない）。

**Q10. Task 分類**
- **Type A — System Tasks**（design review / critic / research / comparison）: **常に安全・現在唯一実用可能。**
- **Type B — Need-derived Tasks**（translation / legal research / educational material / employment info / fundraising research）: **条件付き安全——need が direct_observation・当事者確認済みの場合のみ。** Funding research が最も危険。**現在は前提（当事者確認済み direct need）が n=0 で存在せず、理論上可・実用上空。**
- **Type C — Forbidden**（Need Definition / Need Ranking / Priority Assignment / Gateway Recommendation / Resource Allocation）: **常に禁止。**

---

## 3. 特別観察 — Need Resolution まで禁止すると Nookplot の価値が消えるか

- **消えない。** Type A（System Tasks）は当事者 need と無関係に常に有効で、Nookplot の最大価値（Counter-Argument による反証可能性強化・N-1R）はここにある。
- Type B（Need Resolution）は**禁止ではなく gated**——当事者確認済み direct need が現れたとき開く。これが Nookplot の将来価値を保つ。
- **現在地:** direct な個人 need は n=0 ゆえ Type B は空。だが Type A だけで Nookplot は有意義（機械の自己批判の外部化）。**Need Resolution を「永久禁止」でなく「direct need 待ちで gated」とすることで、価値を消さずに Saiyan Scouter 線を保つ。**

---

## 4. 中心問いへの結論

> **Need Definition と Need Resolution の境界 = H-4 の direct ┃ inference 境界。**
> Agent は direct_observation（当事者表明・同意・人間レビュー済み）の need についてのみ Resolution（Type B）を支援してよく、inference/speculation の need は Task 化不可（Definition に滑る）。現在 direct な個人 need は存在しない（n=0）ため、実用可能なのは Type A（System Tasks）のみ。Need Resolution は永久禁止でなく direct need 待ちで gated——これが Nookplot の価値を消さずに問題定義権力を防ぐ。

---

## 5. 成功条件の確認

- ✅ Nookplot 接続なし / Agent 登録なし / Task 生成なし / Need 生成なし / Contribution 生成なし / Cooperation 生成なし / 文書のみ（コード/データ無変更）

---

*本文書は Need-derived Task の境界の観察記録であり、Need/Gateway/Contribution/Cooperation を生成しない。結論: Need Definition と Need Resolution の境界は H-4 の direct/inference 境界に一致し、Agent の Resolution（Type B）は direct・当事者確認済み need のみ・現在 n=0 で空、実用は Type A のみ。Need Resolution は gated（永久禁止でない）で Nookplot の価値を保つ。Reach Gap・Findability・実価値は未解決であり、本文書もその解決を主張しない。*
