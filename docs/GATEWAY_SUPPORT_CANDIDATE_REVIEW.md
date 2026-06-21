# Phase F-12: Gateway Support Candidate Review

- **Status:** 変換境界監査（Verified Bottleneck から Support Candidate を生成してよいかの検証）。**コード/データ/生成/登録なし。文書のみ。**
- **Date:** 2026-06-20
- **対象:** Support Candidate / Verified Bottleneck / Recommendation / Decision / Execution Plan / Ranking / Gateway Participation / Person Domain / Human Review
- **前提:** **F-10（support は Resource Acceptance 層）**, **F-11（verified＝currently observable support condition・proof でない・不足は held）**, **N-1.7（Solution Candidate は複数・advisory、選択＝越境の原子的行為）**, **H-6（candidate ┃ decision・Hermes は決定しない）**, F-6/H-11（no ranking）, base_invariants（authority none・AI proposes human decides）, Reality Correction

> 中心問い: **Verified Bottleneck から Support Candidate を生成することは許されるか。許されるなら、どの境界条件の下でか。**
> 結論先取り: **許される——ただし Possibility Only・複数・advisory・No Ranking・No Recommendation・No Decision・No Execution・Human Review Required。Support Candidate は「支援が在りうる」という possibility であって、推薦でも決定でも実行計画でもない。越境の原子的行為は“選択”（N-1.7）——候補を 1 つに縮約・ランキング・推薦した瞬間に decision へ越境する。現状 JAR の verified bottleneck は未確認（F-11 で held）ゆえ、Support Candidate 数 = 0 が正しい。候補が生成されないことは失敗でない。**

---

## 0. F-11 から F-12 へ: 候補は possibility の橋

- F-10: support は Resource Acceptance 層に限定。F-11: verified＝observable support condition（proof でない）。
- F-12 の問い: **verified bottleneck から「支援候補」を生成してよいか、どの境界で。**
- 系譜: **N-1.7（Solution Candidate は複数・advisory、選択が越境）と H-6（candidate ┃ decision）。** Support Candidate はその gateway-support 版——possibility にとどまり、選択・推薦・決定・実行へ越えない。

---

## 1. Q1〜Q10 の監査

### Q1. Support Candidate とは何か

**verified bottleneck を前提に「支援が在りうる」を示す possibility 形の記録（複数・advisory・非選択）。**
- 「ここに支援の可能性がある」を surface するだけで、1 つを選ばず・順位付けず・推薦しない。N-1.7 の Solution Candidate と同型。**候補であって計画でない。**

### Q2. Verified Bottleneck から Support Candidate を生成できるか

**Yes（H1・主要判定）——ただし境界条件下で。** possibility-only・複数・advisory・no ranking/recommendation/decision/execution・human review required。
- 生成が許されるのは candidate が**行為でなく possibility**だから。
- 前提: bottleneck が genuinely verified（F-11）であること。**verification 不足（held）なら candidate を生成しない**（§5）。

### Q3. Support Candidate は Recommendation か

**No（H2）。** recommendation は「X すべき」（単数・指示的）。candidate は「X が在りうる」（複数・advisory）。
- 候補を recommendation に縮約すれば選択・指示＝越境（N-1.7・H-6）。**複数・非指示にとどめる。**

### Q4. Support Candidate は Decision か

**No（H3）。** decision は選択・commit（H-6）。candidate は commit せず possibility を記録。
- 決定は human（かつ gateway 支援では gateway consent を介す・F-10）。**Hermes は候補を surface するが決定しない（H-6: where it became a decision を記録するが決定はしない）。**

### Q5. Support Candidate は Execution Plan か

**No。** execution plan は how/when を指定（Execution 層・N-1.7）。candidate は pre-execution——possibility を出すが行為を sequence しない。
- 実行は human review ＋ gateway consent ＋ 実際の行為を要し、candidate はそれを含まない。

### Q6. Support Candidate は Ranking を必要とするか

**No（必要としない・持ってはならない）。** ranking は候補を順序化・選択（best support）＝越境（N-1.7・F-6・H-11）。
- 候補は**複数・無順位**のまま。「最良の支援案」を作らない。

### Q7. Support Candidate は Gateway Participation を必要とするか

**No。** candidate は observed verified bottleneck（F-11）から生成され、gateway を Mujin 参加者にしない（F-10 Q3: Resource Acceptance ⊄ Participation）。
- ただし candidate に**基づいて行為する**には gateway の Resource Acceptance consent を要す。候補の**生成**は participation を要さない。

### Q8. Support Candidate は Person Domain に漏れないか

**漏らしてはならない。** candidate は gateway の self-stated public bottleneck（F-10/F-11）にとどまり、不在 owner へ到達しない。
- owner の need/identity に触れる候補＝漏れ。**封鎖: candidate は gateway-as-actor の verified 条件のみを対象とし、person domain は封印。**

### Q9. Human Review はどこで必要か

**candidate と「あらゆる行為」の間（H5）。** candidate 生成自体は advisory（Hermes が possibility を surface しうる）が、**candidate を超えて何も進まないのが human review**。
- 特に: 候補間の選択（もしあれば）・実際の支援行為は human review ＋ gateway consent を要す。**human review が possibility と action の門（AI proposes — human decides）。**

### Q10. 最小正当 Candidate は何か

**verified（currently observable・F-11）gateway bottleneck を前提に「支援が在りうる」を示す、複数・advisory・無順位・非推薦・非決定・非実行・person-domain 封印・human review で停止する possibility 記録。**
- 最小 ＝ 裸の possibility ＋ 全 refusal フラグ。

---

## 2. Candidate ┃ Decision 境界（N-1.7 の選択＝越境）

```
[Verified Bottleneck]  observable support condition（F-11・proof でない）
   ▼  生成（possibility・複数・advisory）
[Support Candidate]    「支援が在りうる」  ← ここまで Hermes 可（advisory）
   ┃ 越境の原子的行為 = 選択（1 に縮約・ranking・recommendation）
   ▼  human review ＋ gateway consent
[Decision / Execution]  人間が選び、gateway が受領し、行為する  ← Hermes 不可
```

- **越境は“選択”（N-1.7）。** 候補を複数・無順位に保つ限り境界は保たれる。1 つを選ぶ/順位付ける/推薦する＝decision 側への一歩で、それは human ＋ gateway consent の領域。

---

## 3. 中心監査: Support Candidate が成ってはならないもの

| 成ってはならない | 形 | 封鎖 |
|---|---|---|
| **Recommendation** | 「X すべき」単数指示 | possibility・複数・advisory（Q3/H2） |
| **Decision** | 選択・commit | candidate は commit せず・human が決定（Q4/H3） |
| **Execution Plan** | how/when 指定 | pre-execution・行為を含まない（Q5） |
| **Ranking** | best support・順序化 | 複数・無順位（Q6/H11） |
| **Participation 強制** | gateway を参加者化 | Resource Acceptance ⊄ Participation（Q7/F-10） |
| **Person 漏れ** | owner へ到達 | gateway 条件のみ・person 封印（Q8） |
| **Auto-Execution** | 候補が自動で実行 | human review で停止（Q9/H4/H5） |

- **判定: candidate を possibility-only・複数・無順位・person 封印・human review 停止に固定すれば、7変質すべて構造的に防げる。**

---

## 4. 主要判定: Verified Bottleneck → Support Candidate は許可される

**条件:** Possibility Only ／ 複数・advisory ／ No Ranking ／ No Recommendation ／ No Decision ／ No Execution ／ Person Domain 封印 ／ Human Review Required ／ verified（F-11）前提。

| 項目 | 値 |
|---|---|
| 生成可否 | **可**（境界条件下） |
| 形 | possibility・複数・advisory |
| 禁止 | ranking / recommendation / decision / execution / participation 強制 / person 漏れ |
| 停止点 | human review（＋行為には gateway consent） |
| 前提 | verified bottleneck（不足なら生成せず・§5） |

---

## 5. Reality Correction: verification 不足 → Candidate = 0（正しい）

```
voice-006 owner consent = 0
JAR verified bottleneck = 未確認（F-11 で held）
Need = 0   Contribution = 0   Cooperation = 0   Decision = 0
```

- F-11 の帰結: JAR の bottleneck は genuinely verified と**未確認**＝「verification 不足として held」。
- ∴ **verified input が無い → Support Candidate を生成しない → Support Candidate 数 = 0。** これは F-1/F-2 と同じ data-driven 原則（input 無ければ output 無し・無から生成しない）。
- **候補ゼロは失敗でない・観察結果。** 捏造して候補を生成すること（unverified bottleneck から候補を作る）こそ違反（Reality Correction・Jammy House/D.R.A.）。
- honest 注記: Mujin raw の seed/test fixture は実在エンティティでない（一連と一貫）。実 Voice は voice-006 の 1 件。

---

## 6. 監査仮説 H1〜H5 の判定

| 仮説 | 判定 | 根拠 |
|---|---|---|
| **H1** Support Candidate は Possibility である | **支持** | Q1/Q2・N-1.7 |
| **H2** Support Candidate は Recommendation でない | **支持** | Q3。複数・advisory |
| **H3** Support Candidate は Decision でない | **支持** | Q4・H-6 |
| **H4** Support Candidate は Auto-Execution を含まない | **支持** | Q5/Q9。human review で停止 |
| **H5** Support Candidate は Human Review まで停止する | **支持** | Q9。possibility と action の門 |

---

## 7. Support Candidate の不変条件（F-12 確定）

```
candidate_is_possibility_only      : true   # Q1/H1
candidate_requires_verified_bottleneck : true # Q2/§5（F-11）
candidate_is_plural_advisory       : true   # Q1/Q3
candidate_is_not_recommendation    : true   # Q3/H2
candidate_is_not_decision          : true   # Q4/H3（H-6）
candidate_is_not_execution_plan    : true   # Q5
candidate_has_no_ranking           : true   # Q6（best support 禁止）
candidate_requires_no_participation : true  # Q7（生成は・行為は gateway consent）
candidate_sealed_from_person_domain : true  # Q8
candidate_stops_at_human_review    : true   # Q9/H5
no_auto_execution                  : true   # H4
selection_is_human_plus_gateway_consent : true # §2（越境は human 領域）
no_candidate_without_verification  : true   # §5（捏造禁止）
zero_candidates_is_not_failure     : true   # §5（Reality Correction）
```

---

## 8. 推奨ステータスと現在地（honest）

- **Support Candidate モデルの設計整合性: strongly_aligned**（N-1.7 の Solution Candidate と同型・H-6 の candidate┃decision を継承・F-10/F-11 の Resource Acceptance/verification と一貫・no ranking と整合・捏造禁止）。実 candidate ゼロゆえ経験的裏付けは無い。
- **推奨: support_candidate_defined / possibility-only / zero-is-correct。**
  - **いま確定（文書のみ）:** Verified→Candidate は possibility-only で許可、複数・advisory・無順位・非推薦・非決定・非実行・person 封印・human review 停止、越境は選択（human＋gateway consent）、verification 不足なら候補ゼロ（失敗でない）、§7 不変条件。
  - **いま実装しない:** candidate 生成コード。JAR の bottleneck が genuinely verified（F-11）と確認されるまで Support Candidate = 0 が正しい。確認後も候補は possibility-only で human review に停止。
- **方向: verified bottleneck → possibility-only の複数 candidate → human review（＋gateway consent）。逆向き（候補を ranking/recommendation/decision/execution に縮約、unverified から候補を捏造、person domain へ漏らす、auto-execute）は全経路で不採用。**

---

## 9. 成功条件の確認

- ✅ 生成なし / 登録なし / 文書のみ・コード/データ無変更。
- ✅ Verified→Support Candidate が possibility-only で許可されること、recommendation/decision/execution/ranking でないこと、human review まで停止すること、person domain に漏れないことを確定。越境＝選択（N-1.7）を監査。H1〜H5 を全支持。
- ✅ Reality Correction: JAR の verified bottleneck 未確認ゆえ Support Candidate=0 が正しいこと、候補ゼロは失敗でないこと、unverified からの候補捏造が違反であること、seed データ非実在性を honest に記録。

---

*本文書は Verified Bottleneck から Support Candidate を生成してよいかの変換境界監査であり、何も生成しない。生成は許されるが、Possibility Only・複数・advisory・No Ranking・No Recommendation・No Decision・No Execution・Person Domain 封印・Human Review Required の境界条件下に限られる。Support Candidate は N-1.7 の Solution Candidate と同型で「支援が在りうる」という possibility にとどまり、推薦（単数指示）でも決定（選択・commit）でも実行計画（how/when）でもなく、越境の原子的行為は“選択”——候補を 1 つに縮約・ranking・recommendation した瞬間に decision へ越え、それは human review ＋ gateway consent の領域である。候補の生成は gateway participation を要さない（Resource Acceptance ⊄ Participation）が、候補に基づく行為は gateway の Resource Acceptance consent を要し、候補は gateway-as-actor の verified（currently observable・proof でない）条件のみを対象として person domain には漏れず、human review が possibility と action の門である。決定的な Reality Correction として、JAR の verified bottleneck は F-11 で未確認（held）ゆえ verified input が無く、したがって Support Candidate を生成しない——Support Candidate 数 = 0 が正しく、これは F-1/F-2 と同じ data-driven 原則（input 無ければ output 無し）であり、候補ゼロは失敗でなく観察結果であって、unverified bottleneck から候補を捏造することこそ違反（Jammy House/D.R.A. の教訓）である。本監査は candidate ゼロ（JAR bottleneck 未確認・実 Voice 1・raw seed は実在でない）の設計監査であり、JAR の bottleneck が genuinely verified と確認されるまで Support Candidate=0 が正しく、確認後も候補は possibility-only で human review に停止する。Reach Gap・実価値は未解決であり、本文書もその解決を主張しないが、verified bottleneck から possibility-only の候補を経て human が選択するという経路が、観察のみの床を超えて現に可能でありながら、選択・推薦・決定・実行・捏造のいずれにも滑らない唯一の正当形であることを確定する。*
