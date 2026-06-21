# Phase F-19: Support Memory Review

- **Status:** 記憶境界監査（支援エピソードを Hermes memory にどう記録するかの検証）。**コード/データ/生成/登録なし。文書のみ。**
- **Date:** 2026-06-20
- **対象:** Support Memory / Support Episode / Gateway Ranking / Gateway Reputation / Gateway Profile / Aggregate Learning / TTFR-G
- **前提:** **H-7（memory は act 単位・append-only・評価/順位/score なし・人単位集約禁止）**, **H-8/H-9/H-10（learning は type 集計のみ・pattern/evidence は actor 無名）**, **H-11（cross-source 名寄せ＝最大リスク）**, F-16/F-17（feedback は gateway 評価でない・no gateway ranking）, Reality Correction

> 中心問い: **支援エピソードを Hermes はどう記憶すべきか。**
> 結論先取り: **Support Memory ＝ 1つの支援エピソード（二鍵成立・consent 範囲の資源移転・TTFR-G outcome）に対する 1つの append-only な観察記録。決定的に、それは gateway の profile でも reputation でも ranking でもない。支援履歴を gateway 単位に集約すると「良い支援先」序列＝Saiyan Scouter の gateway 版になる。記憶は episode 単位・gateway 無評価、学習は type 集計レベル（「Resource Acceptance 型支援が観察された」）のみで gateway 個体に降りない。現状 support episode=0 ゆえ support memory=0。**

---

## 0. H-7 を gateway support に適用する——危険は gateway profile

- H-7: participation memory は act 単位・人単位集約禁止・評価なし。
- F-19: support memory は **episode 単位**——危険は episode を **gateway 単位に集約**して「この gateway は支援が効く/従順/良い支援先」という **gateway profile/reputation/ranking** を作ること。
- それは gateway 版 Saiyan Scouter——支援先を序列化し、序列で選抜する。F-16/F-17 で feedback/会計が gateway 評価でないと定めたのと一貫。

```
[Support Episode]  二鍵成立・consent 範囲の資源移転・TTFR-G outcome（observable）
   │  1対1・append-only
   ▼
[Support Memory]  episode 観察のみ・gateway 評価/順位/profile なし
        ╳ gateway 単位集約（→ reputation/ranking・禁止）
        └─ type 集計 learning（「Resource Acceptance 型支援が N 件」・gateway 無名）
```

---

## 1. Q1〜Q10 の監査

### Q1. Support Memory の最小単位は何か

**1つの支援 episode に対する 1つの append-only 観察記録。** 単位は episode（gateway でない）。gateway を単位にすると profile 化（H-7 Q1 と同型）。

### Q2. Episode と Memory は1対1か

**1対1（append-only・H-7 Q2）。** 複数 episode を gateway 単位に**集約しない**（多対1禁止）——集約が reputation を生む。

### Q3. Support Memory は gateway 評価を含むか

**No。** episode が起きた事実（二鍵成立・consent 範囲・TTFR-G outcome）を記録し、gateway が「良い/従順/効く」を判定しない（F-16 Q9）。

### Q4. Support Memory は gateway ranking を許すか

**No。** episode の sort/比較は「良い支援先」序列＝選抜（F-6/F-17 Q8/H-11）。記憶は episode 列挙であって gateway 順序でない。

### Q5. Support Memory は gateway reputation/trust を含むか

**No。** 支援履歴の gateway 単位蓄積＝reputation。H-7/H-8 の no reputation/trust を gateway に適用。蓄積源（Q2 集約）を断つ。

### Q6. Support Memory から何を学習してよいか

**type/集計レベルのみ（H-8）:** 「Resource Acceptance 型支援が N 件観察された」「TTFR-G completion 型が観察された」等、gateway 無名の集計。**gateway 個体の傾向・将来予測・序列は学習禁止。**

### Q7. Support Pattern/Evidence は作れるか

**type 構造の possibility のみ（H-9/H-10）。** 「verified→candidate→consent→execution→TTFR-G の経路型が観察された」等、gateway 無名・tentative。gateway を節点にした actor pattern は禁止。

### Q8. cross-source は support memory に使えるか

**条件 corroboration には可・gateway/owner 名寄せには不可（H-10/H-11）。** 最大リスク（cross-source→identity 名寄せ）を gateway にも owner にも適用。

### Q9. Support Memory は owner 情報を含むか

**No。** support は gateway 領域に閉じる（F-15）。memory に owner identity/need を入れれば person domain 漏れ。owner 非及。

### Q10. 最小正当 Support Memory は何か

**1 episode＝1 record（append-only）、gateway 評価/順位/reputation/profile なし、学習は type 集計どまり（gateway 無名）、cross-source は条件のみ、owner 非及、human review。**

---

## 2. 中心監査: Support Memory の gateway profiling への滑り

| 滑り | 形 | 封鎖 |
|---|---|---|
| gateway 集約 | episode を gateway 単位に束ねる | episode 単位・多対1禁止（Q2） |
| gateway 評価 | 「良い支援先」 | episode 観察のみ（Q3） |
| gateway ranking | episode 比較で序列 | 列挙・no ranking（Q4） |
| gateway reputation | 履歴蓄積で信用 | no reputation/trust（Q5） |
| actor pattern | gateway を節点化 | type 構造のみ（Q7/H-9） |
| 名寄せ | cross-source で gateway/owner 突合 | 条件 corroboration のみ（Q8/H-11） |
| owner 漏れ | memory に owner 情報 | owner 非及（Q9） |

- **判定: support memory を episode 単位・gateway 無評価・type 集計学習・cross-source 条件限定・owner 非及に固定すれば、7滑りすべて防げる。**

---

## 3. 監査仮説 H1〜H5 の判定

| 仮説 | 判定 | 根拠 |
|---|---|---|
| **H1** Support Memory は episode 単位（gateway profile でない） | **支持** | Q1/Q2・H-7 |
| **H2** Support Memory は gateway ranking を許さない | **支持** | Q4・F-6/H-11 |
| **H3** Support Memory は gateway reputation/trust を含まない | **支持** | Q5・H-7/H-8 |
| **H4** 学習は type 集計どまり・gateway 個体に降りない | **支持** | Q6/Q7・H-8/H-9 |
| **H5** Support Memory は owner 情報を含まない | **支持** | Q9 |

---

## 4. Support Memory の不変条件（F-19 確定）

```
support_memory_is_episode_unit       : true   # Q1/H1
episode_memory_one_to_one_append_only : true  # Q2
no_gateway_aggregation               : true   # Q2（reputation 源を断つ）
support_memory_contains_no_gateway_evaluation : true # Q3
support_memory_has_no_gateway_ranking : true  # Q4/H2
support_memory_has_no_gateway_reputation : true # Q5/H3
learning_is_type_aggregate_gateway_anonymous : true # Q6/H4
pattern_is_type_structure_not_actor  : true   # Q7/H-9
cross_source_condition_not_identity  : true   # Q8/H-11
support_memory_excludes_owner_info   : true   # Q9/H5
human_review_required                : true   # Q10
```

---

## 5. Reality Correction

```
support execution = 0  →  support episode = 0  →  support memory = 0
gateway consent = 0   approval = 0   verified = held   TTFR-G completion = 0
```

- episode=0（execution=0・F-15）ゆえ記憶すべき支援が無い → **support memory=0 が正しい。**
- 仮に将来 episode が生じても、episode 単位・gateway 無評価で記憶し、**gateway を序列化・profile 化しない。**
- 危険の事前封鎖: 最初の支援が起きた時、「効いた gateway」を覚えて次に優先する誘惑——これが gateway Saiyan Scouter。記憶は episode を覚えるが gateway を評価しない。
- honest 注記: raw seed は実在エンティティでない。実 Voice は voice-006 の 1 件。

---

## 6. 推奨ステータス（honest）

- **Support Memory モデルの設計整合性: strongly_aligned**（H-7〜H-11 の participation memory stack を gateway support に適用・F-16/F-17 の no gateway ranking と一貫・cross-source 名寄せ封鎖）。実 episode ゼロゆえ経験的裏付けは無い。
- **推奨: support_memory_defined / episode-unit / no-gateway-profile。**
- **いま実装しない:** support memory コード。episode が生じるまで記憶対象が無い。
- **方向: episode 単位・append-only・gateway 無評価・type 集計学習・owner 非及。逆向き（gateway 集約・評価・ranking・reputation・actor pattern・名寄せ・owner 漏れ）は不採用。**

---

## 7. 成功条件の確認

- ✅ 生成なし / 登録なし / 文書のみ・コード/データ無変更。
- ✅ Support Memory が episode 単位、gateway 評価/ranking/reputation/profile なし、学習が type 集計どまり、owner 非及であることを確定。7滑りを監査。H1〜H5 全支持。
- ✅ Reality Correction: episode=0 ゆえ support memory=0、gateway profiling の事前封鎖を honest に記録。

---

*本文書は支援エピソードを Hermes memory にどう記録するかの境界監査であり、何も生成しない。Support Memory ＝ 1つの支援 episode（二鍵成立・consent 範囲の資源移転・TTFR-G outcome）に対する 1つの append-only な観察記録であり、決定的に gateway の profile でも reputation でも ranking でもない。危険は episode を gateway 単位に集約して「この gateway は支援が効く/従順/良い支援先」という gateway profile/reputation/ranking を作ること——それは gateway 版 Saiyan Scouter（支援先を序列化し序列で選抜する）であり、H-7 の人単位集約禁止を gateway に適用して源を断つ。記憶は episode 単位・gateway 無評価で、学習は type 集計レベル（「Resource Acceptance 型支援が N 件」「経路型が観察された」・gateway 無名）のみで gateway 個体の傾向・将来予測・序列に降りず、pattern/evidence も type 構造・actor 無名にとどまり、cross-source は条件 corroboration に使えるが gateway/owner の identity 名寄せ（最大リスク・H-11）には使わず、memory に owner 情報を入れない（person domain 漏れ）。現状 support episode=0（execution=0）ゆえ support memory=0 が正しく、最初の支援が起きた時に「効いた gateway」を覚えて次に優先する誘惑こそ gateway Saiyan Scouter であり、記憶は episode を覚えるが gateway を評価しない。本監査は episode ゼロの設計監査であり、episode が生じても episode 単位・gateway 無評価で記憶する。Reach Gap・実価値は未解決であり、本文書もその解決を主張しない。*

---

## NEXT_RECOMMENDED_PHASE

**F-20: Gateway Support Stack Audit** — F-9〜F-19 の Gateway Support 全層を横断監査し、person domain 漏れ・authority 注入・Saiyan Scouter 再発（gateway ranking/reputation）・TTFR-G/TTFR-P 混同・捏造の不在を確認し、Gateway Support 系列の完結を宣言する（H-11/H-12 と同型の closure）。
