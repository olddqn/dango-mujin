# Phase X-4: Gateway Bottleneck Cooperation Trial Protocol

- **Status:** 運用プロトコル（既存機能のみ）。新機能・新 ADR・新レイヤなし。文書のみ。
- **Date:** 2026-06-13
- **対象 Voice:** `voice-006`（JAR 公開支援要請 / https://www.refugee.or.jp/support/ ）
- **目的:** voice-006 の **Gateway Bottleneck** を `Voice → Gateway Bottleneck → Contribution → Cooperation → Reality Feedback` まで安全に一周させる手順を定義する。

> **目的の一線:** 個人 Need を外部から定義しない。不在の難民個人に「あなたに必要なのは翻訳/法的支援だ」と言わない。
> 本 Trial が扱うのは **JAR が公開している Gateway Bottleneck（資金・人手）のみ**。
> 本 Trial は **TTFR-G の検証**であり、**TTFR-P の達成ではない**。

---

## 0. 前提（X-2.5〜X-3.5 / H-4 の確定事項）

- voice-006 は **Gateway Voice**（仲介者の声）。Need Owner（難民個人）は Voice 内に不在。
- 推論境界（H-4 ib-001〜005）:
  - **A 資金 / B 人手 = direct_observation**（Gateway Need・scouter_risk: none）← 本 Trial の対象
  - **C 翻訳 / D 法的 / E 就労 = inference / speculation**（Individual Need・scouter_risk: medium〜high）← **本 Trial で扱わない**
- 最初に安全に一周できるのは C/D/E ではなく **A または B**。

---

## 1. Trial 対象と扱い

| Candidate | Gateway Bottleneck | 根拠 | 扱い |
|---|---|---|---|
| **A** | 資金 | JAR 公開寄付募集（直接観測） | **Gateway Need**（個人 Need ではない） |
| **B** | 人手 | JAR 公開ボランティア募集（直接観測） | **Gateway Need**（個人 Need ではない） |

**本 Trial で扱わないもの（禁止対象）:** 翻訳 Need / 法的 Need / 就労 Need。
**理由:** これらは JAR の活動分野から推論された**個人 Need**であり、当事者 Voice が存在しない（H-4 scouter_risk medium〜high）。

---

## 2. 運用手順（既存ページのみ）

> 各 Step は「既存ページへの記録」と「現実の人間の行為」を分ける。本 Trial は記録（意思表示）までで、支援実行は別。

### Step 1 — voice-006 を確認
- **既存:** Voice Commons（voice-006 は登録済み・`eb8442b`）。
- **確認事項:** 出典 URL が公開要請であること / 個人特定がないこと / **自動接触をしないこと**。
- **記録:** 既に存在。新規生成不要。

### Step 2 — Gateway Bottleneck を選ぶ
- **選択肢:** A 資金 / B 人手。
- **選定基準:** voice-006 に直接書かれている / 個人 Need に踏み込まない / 協力が現実に可能。
- **禁止:** 順位付け・スコア。A と B は並列。どちらを選ぶか（または両方）は**人間の判断**で、理由を記録する。

### Step 3 — Contribution Commons に記録
- **既存ページ:** `/contributions`
- **Contribution Type:** A なら `Funding`、B なら `Volunteer`（Community / Other も可）。
- **重要:** これは**支援実行ではなく、Contribution の意思表示**。`contribution_is_not_control` 等の不変条件が付与される。
- **対象は JAR の公開要請（Gateway Need）** であり、特定の難民個人への支援ではない。

### Step 4 — Cooperation Commons に記録
- **既存ページ:** `/cooperation`
- **例:** 「JAR Public Appeal Support Cooperation」
- **参加者:** JAR public appeal / Contribution provider / Mujin observer（個人当事者は含めない）。
- **重要:** Cooperation は Assignment ではない・自動参加ではない・指揮命令ではない（`cooperation_is_not_command / not_assignment / participation_is_voluntary`）。

### Step 5 — Reality Feedback を記録
- **既存ページ:** `/feedback`
- **可能な feedback 種別:** observer feedback / gateway feedback / contributor feedback（Reporter Type = Observer / Gateway / Contributor）。
- **重要:** **本人（Recipient）feedback ではない。TTFR-P ではない。** これは **TTFR-G**（Gateway Bottleneck 側の一周）。
- **失敗も記録:** 協力が成立しなければ `Negative` / `Mixed` / `Failed` として記録。**失敗は価値がある**（次の学習材料）。

---

## 3. TTFR の分離定義（本 Trial の中核）

| 指標 | 定義 | 本 Trial |
|---|---|---|
| **TTFR-G** | Time To First **Gateway** Relief — Gateway Bottleneck に対する最初の協力成立まで | **これを検証する** |
| **TTFR-P** | Time To First **Person** Relief — 困窮者個人への救済成立まで | **達成しない（対象外）** |

- 本 Trial が一周させるのは **TTFR-G**。Gateway（JAR）の資源 Bottleneck に最初の協力が成立するまでの時間。
- **TTFR-G の成立は TTFR-P の達成を意味しない。** JAR が資金/人手を得ても、それが特定の難民個人を救ったかは別問題（gap-1 の奥・未観測）。
- **混同の禁止:** ダッシュボードや報告で「Gateway が支援を受けた」を「困窮者が助かった」と読み替えない（H-4 / X-2.6 観察5 のカテゴリ錯誤）。

---

## 4. Reality Feedback の扱い

- Feedback は**成功証明ではない**。Feedback は**観察**である。
- 協力が成立しなかった場合も `failed` / `mixed` として記録する。
- 否定的・失敗の feedback を歓迎する（Reality Feedback Commons の原則）。

---

## 5. Hermes への入力（観測のみ・判断しない）

Trial 結果を Hermes が観測できるようにする。ただし **Hermes は判断しない**。Hermes が記録するもの:
- Gateway Bottleneck が **direct_observation** だったか（A/B は yes）。
- Contribution が発生したか。
- Cooperation が発生したか。
- Feedback が発生したか（種別）。
- **TTFR-G と TTFR-P を混同していないか**。

> Hermes は既存の Observation / Reflection / Learning / Evidence / Inference Boundary の各層で、この Trial を**観測材料**として扱える。Need 定義・選定・割り当ては一切しない。

---

## 6. 中止条件

- JAR（仲介者組織）が連携を望まない／公開要請の趣旨と異なる扱いになる場合は中止。
- Trial が個人 Need の定義（C/D/E）に滑り込みそうになったら中止し、§1 の境界に戻る。
- 中止は失敗ではない。中止理由を記録する。

---

## 7. 検証項目（実行時に確認）

1. 新規コードなし
2. 新規 ADR なし
3. 新規レイヤなし
4. Need Candidate JSONL 変更なし
5. 個人 Need 作成なし
6. Gateway Bottleneck（A/B）のみ扱ったこと
7. C/D/E に踏み込んでいないこと
8. TTFR-G と TTFR-P を区別したこと
9. Reality Feedback が成功証明ではなく観察として記録されていること
10. Saiyan Scouter 問題を再発させていないこと

---

## 8. この Trial の限界（隠さない）

- **TTFR-P は一切前進しない。** 個人の救済は本 Trial の対象外で、gap-1 は触れられない。Reach Gap は縮まない。
- **Gateway Bottleneck の解消が個人救済に繋がる保証はない。** JAR が資源を得ても、それが誰にどう届くかは Mujin の外（仲介者の内部）。
- **本 Trial が成立しても「Mujin は人を助けた」とは言えない。** 言えるのは「Gateway の公開要請に最初の協力が記録された」までである。
- それでも本 Trial に意味があるのは: **個人 Need を外部定義せずに、救済能力（接続の成立）を安全に検証できる最初の一周**だから。TTFR-P への道は、当事者 Voice（種類 A の Voice）が現れたときに別途開く。

---

*本文書は運用プロトコルであり、コード・新機能・新 ADR・新レイヤを含まない。個人 Need を定義せず、扱うのは JAR が公開している Gateway Bottleneck（資金・人手）のみ。TTFR-G の検証であって TTFR-P の達成ではない。Reach Gap は未解決であり、本プロトコルもその解決を主張しない。*
