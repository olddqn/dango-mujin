# Phase F-24: Findability State Reconciliation Review

- **Status:** 整合監査（設計意図と実際の公開状態の差分の accounting）。**コード/データ/生成/登録/公開なし。文書のみ。**
- **Date:** 2026-06-21
- **対象:** Designed Door / Actual Public State / Gap Accounting / Test Fixture / JAR / Review Docs Exposure
- **前提:** **F-21/F-22/F-23 v2（door┃data・curate）**, voice_records 公開監査, F-1.7（旧: platform unpushed）, H-16, Reality Correction

> 中心問い: **設計意図（person-data-ゼロ の door）と、実際に公開されている状態は、どれだけ乖離しているか。**
> 結論先取り: **設計意図は「最小限の person-data-ゼロ door」。実状は「platform 全体（構造化 voice dataset を含む）＋ review docs 群が公開」。乖離は大きいが、監査により暴露内容は良性（test fixture 5 + 公開組織 1・実個人 0）。乖離の本質は「意図した最小 door でなく、開発途中の platform 全体が de-facto surface になっている」こと。これは failure でなく“整序待ち”であり、整序（labeling/封印/JAR 扱い）は要 Human Approval。**

---

## 0. 設計 vs 実状の差分表

| 項目 | 設計意図（F-21/F-22） | 実際の公開状態（監査） | 乖離 |
|---|---|---|---|
| public surface | person-data-ゼロ の最小 door | platform 全体（mvp branch public） | **大** |
| voice data | sealed（公開しない） | voice_records.jsonl public（200） | **大**（但し中身良性） |
| voice 内容 | — | test fixture 5 + JAR 公開声明 1・実個人 0 | 良性 |
| review docs | uncommitted（私の生成分） | 一部 push 済（a97b74b "docs: add boundary and metric reviews"） | 中 |
| consent opportunity 機構 | bridge（隙間保持・pull） | 未整備（repo は dev surface であって door でない） | 大 |

---

## 1. Q1〜Q10

### Q1. 実際の findable surface は何か

**(a) Dan-Go 公開分（globe/specs/MUJIN_PROTOCOL・従前から公開）、(b) 今や公開された mvp branch（bridge/mujin platform・agent_commons・構造化 voice dataset・review docs の一部）。** 設計した「door」は別途存在せず、**dev repo がそのまま de-facto surface**。

### Q2. それは設計した door か

**No。** door は「Mujin の存在・趣旨・関与方法を示す person-data-ゼロ の意図的 surface」。実状は「開発リポジトリ全体が公開」——意図的 door でなく副作用的露出。

### Q3. 乖離は failure か

**No（calibrated・F-23 Q6）。** 実個人暴露 0 ゆえ重大 failure でない。だが「意図した surface」と「実際の surface」が一致していない整序待ち状態。

### Q4. review docs の公開は問題か

**低懸念。** review docs（H/N/X/F 系列）は設計文書で person data を含まない（一貫して docs-only・no PII）。公開は Dan-Go の透明性に資する。ただし**本セッションで私が生成した分の一部が push 済**である点は記録すべき（私は push していない）。

### Q5. 構造化 voice dataset の公開は最大の乖離か

**Yes（F-22 v2 方向B）。** 「needs × region」の公開構造は latent scouter artifact。現状良性（test+組織）だが、設計意図（voice sealed）との最大乖離。**実 individual voice を絶対入れない**規律で将来を封じる。

### Q6. JAR association の乖離は

**gateway consent 未取得のまま association が公開継続（F-23 Q3）。** 整序は consent 取得 or 分離（要 approval）。

### Q7. 乖離を埋める方向は

**二択（要 approval）:** ①実状に設計を合わせる（repo を意図的 door として再構成・voice 封印・test label）、②設計に実状を合わせる（最小 door を別途作り dev data を非公開化）。いずれも real-data/外向き execution。

### Q8. 本セッションで埋められるか

**No。** 整序はすべて real-data 変更・外向き ゆえ要 Human Approval。**accounting（差分の可視化）まで。**

### Q9. 乖離は person 救済に影響するか

**直接は No。** Reach Gap は person 領域（F-8）。findability 乖離は consent opportunity の質に関わるが、実個人暴露 0 ゆえ救済を毀損していない。

### Q10. honest な現在地は何か

**「設計は完成、実状は dev repo の副作用的公開（良性だが整序待ち）、整序は要 Human Approval」。**

---

## 2. consistency cross-check（H / N / X / F）

| 系列 | 整合性 |
|---|---|
| **F-1.7**（旧: platform unpushed） | ⚠️ **訂正**: 現在 pushed。F-1.7 の事実部分は古い |
| **H-16**（voice 封印） | ⚠️ forward-looking に保持・現データ良性 |
| **F-21/F-22/F-23 v2** | ✅ door┃data・curate・要 approval と一貫 |
| **F-8**（Reach Gap person 領域） | ✅ findability 乖離は person 救済を毀損せず |
| **Reality Correction** | ✅ 差分を誇張も矮小化もせず accounting |

---

## 3. 不変条件（F-24 確定）

```
dev_repo_is_de_facto_surface_not_designed_door : true # Q1/Q2
gap_is_large_but_exposure_is_benign     : true   # Q3（実個人 0）
review_docs_public_is_low_concern       : true   # Q4
structured_voice_dataset_is_max_divergence : true # Q5
jar_association_unconsented_continues    : true   # Q6
reconciliation_requires_human_approval   : true   # Q7/Q8
findability_gap_does_not_harm_person_relief : true # Q9
```

---

## 4. Reality Correction（F-24）

- F-1.7 の「platform unpushed」は古い——現在 pushed。findability 系列の事実基盤を更新。
- 乖離は大きいが暴露は良性（実個人 0）。誇張せず、しかし整序すべき残件として honest に記録。
- 整序は要 approval ゆえ本セッションでは accounting のみ。

---

## NEXT_RECOMMENDED_PHASE

**F-25: Findability Improvement Series Closure / Stack Audit** — F-21〜F-24（v2）を H/N/X/F 系列に対して横断監査し、整合・矛盾不在・Saiyan Scouter 不在を確認、Findability Improvement 系列の architectural closure を宣言する。
