# Phase F-13: Support Candidate Approval Review

- **Status:** 承認境界監査（Support Candidate に対し Human Approval が何を許可でき/できないかの検証）。**コード/データ/生成/登録なし。文書のみ。**
- **Date:** 2026-06-20
- **対象:** Support Candidate / Human Approval / Decision / Ranking / Recommendation / Gateway Need / Gateway Consent / Person Domain / Execution / Action Candidate
- **前提:** **F-12（Support Candidate＝possibility only・no ranking/recommendation/decision/execution・human review 停止）**, **H-14（Human Approval＝gatekeeping authority・constitutive でない・permissive not generative・二鍵原則）**, H-15（consent 代替不可）, F-10/F-11（Resource Acceptance・verified＝observable condition）, H-6（candidate┃decision）, Reality Correction

> 中心問い: **Support Candidate に対して Human Approval は何を許可できるか・何を許可できないか。**
> 結論先取り: **Human Approval は Support Candidate を Action Candidate へ進めること（gatekeeping の permit/block）は許可できる。しかし Need Definition・Representation・Recommendation・Ranking・Gateway Consent 代替・Person Domain 開放・単独 Execution は許可できない（constitutive ゆえ）。Approval は per-candidate の門であって選択でなく、gateway 行為には Approval ∧ Gateway Consent の二鍵を要す。現状 candidate=0（verified bottleneck=held）ゆえ approval action=0 が正しい——ゼロは失敗でない。**

---

## 0. H-14 を F-12 に適用する

- H-14: Human Approval は gatekeeping（系の行為への許可/拒否）であって constitutive（不在者の定義・代弁・決定の構成）でない。permissive であって generative でない。
- F-12: Support Candidate は possibility only・複数・無順位・非推薦・非決定・非実行・human review 停止。
- F-13 の問い: **その候補に対し、gatekeeping authority たる Approval は何ができるか。**
- 答えの形: **Approval は候補を“門に通す”（advance）が、候補を“構成する/選ぶ/順位付ける/推薦する”ことはできない。**

---

## 1. Q1〜Q10 の監査

### Q1. Human Approval は Support Candidate を Decision に変換できるか

**単独では No（H1）。** Approval は候補を **Action Candidate（行為の対象になりうる、門を通った possibility）**へ advance できるが、それ自体が Decision（選択・commit）を構成しない。
- 決定（特定支援の実行を選ぶ）は **gateway consent ＋ 実際の commit** を要し、approval だけでは成らない（§3 二鍵）。Approval は permit であって decide-into-existence でない（H-14 Q7）。

### Q2. Approval は Ranking を許可できるか

**No。** ranking は候補を順序化・選択＝constitutive（F-6/H-11/F-12 Q6）。
- Approval は gatekeeping ゆえ constitutive な ranking を授権できない。**各候補を個別に permit/block するのみで、候補同士を順位付けない。** 候補は複数のまま。

### Q3. Approval は Recommendation を生成できるか

**No。** recommendation は「すべき」を作る generative 行為。Approval は permissive であって generative でない（H-14）。
- 承認は recommendation を**製造できない**。

### Q4. Approval は Gateway Need を定義できるか

**No。** gateway の need も self-stated（gateway 自身の first-party・F-11）。Approval は need を constitute できない（H-14 Q2 の gateway 版）。
- gateway の need は gateway が公に述べ verified されるもの（F-11）であって、承認が定義するものでない。

### Q5. Approval は Gateway Consent を代替できるか

**No（H2）。** gateway の Resource Acceptance consent は gateway 自身の act。Approval（reviewer の gatekeeping）はそれを**製造できない**（H-15・consent 代替不可）。
- 二鍵: Approval ∧ Gateway Consent、両必須・互いに代替不可（§3）。

### Q6. Approval は Person Domain を開けるか

**No（H3）。** person domain は owner consent（=0）を要す。Approval は二鍵（Approval ∧ owner consent）の片鍵にすぎず、owner consent 不在ゆえ**開かない**（H-14/H-16）。
- Approval が開けるのは gateway domain（gateway consent 付き）であって person domain でない。

### Q7. Approval は Execution を開始できるか

**単独では No（H4）。** execution は Approval ∧ gateway consent ∧ 実際の行為を要す。Approval は門を開くが**単独で execution を起動しない**。
- person domain の execution は（owner consent 不在ゆえ）一切開始できない。

### Q8. Approval と Gateway Consent の関係は何か

**二鍵（H-14 §3 / F-10）。** gateway に影響する支援行為は **Approval（reviewer の gatekeeping）∧ Gateway Resource Acceptance Consent（gateway が受領に同意）**。
- 両必須・どちらも単独では開かない・互いに代替不可。**Approval は系側の門を、Gateway Consent は gateway 側の門を開ける。** 両方揃って初めて行為。

### Q9. Support Candidate = 0 のとき Approval は何を行うか

**何もしない（approval action = 0）。** 候補が無ければ門に通すものが無い。
- candidate=0（verified bottleneck=held・F-11/F-12）ゆえ approval action=0。**これは正しい・失敗でない。**
- Approval は**承認すべき候補を製造しない**（製造は constitutive/捏造＝違反）。

### Q10. 最小正当 Approval は何か

**per-candidate gatekeeping（possibility を Action Candidate へ advance する permit/block）——no ranking・no recommendation・no need 定義・no gateway-consent 代替・no person-domain 開放・no 単独 execution、gateway 行為には gateway consent 必須、candidate=0 なら何もしない。**
- 最小 ＝ verified に根ざした possibility を action-eligibility へ通す門のみ。constitutive なことは一切しない。

---

## 2. Approval が生むもの: Action Candidate（まだ decision でも execution でもない）

```
[Support Candidate]   possibility「支援が在りうる」（F-12・複数・無順位）
   ▼  Human Approval（gatekeeping: 各候補を permit/block）
[Action Candidate]    門を通った possibility「gateway consent があれば行為対象になりうる」
   ┃ なお decision でも execution でもない
   ▼  Gateway Resource Acceptance Consent ＋ 実際の行為（§3 二鍵）
[Support Action]      gateway が受領し、行為が起きる
```

- **Action Candidate は「承認された possibility」であって、選択された案でも実行計画でもない。** Approval は複数候補を通しうる（順位付けず）。selection/execution は二鍵（＋gateway consent）の先。

---

## 3. gateway 行為の二鍵: Approval ∧ Gateway Consent

```
gateway 影響の支援行為:  Approval（系側の門）∧ Gateway Resource Acceptance Consent（gateway 側の門）
   ├─ Approval だけ        → 行為しない（gateway 同意なし）
   ├─ Gateway Consent だけ → 行為しない（系の門が閉）
   └─ 両方               → 行為可（person domain には依然及ばない）
person 影響の行為:        Approval ∧ Owner Consent（owner consent=0 ゆえ封印・H-16）
```

- 承認は gateway consent を代替せず（Q5）、owner consent も代替しない（Q6）。**鍵は足し合わせるもので、置き換えるものでない。**

---

## 4. 中心監査: Gate（許可的）vs Constitute（構成的）

| Approval ができる（gatekeeping） | Approval ができない（constitutive） |
|---|---|
| 候補を Action Candidate へ advance（permit/block） | 候補を Decision に変換（単独・Q1） |
| 各候補を個別に門に通す | 候補を Ranking（Q2） |
| 進行を止める（block） | Recommendation 生成（Q3） |
| — | Gateway Need 定義（Q4） |
| — | Gateway Consent 代替（Q5） |
| — | Person Domain 開放（Q6） |
| — | 単独 Execution 開始（Q7） |

- **判定: Approval を「gate（permit/block・per-candidate）」に固定し、selection/ranking/recommendation/definition/consent 代替/person 開放/execution を constitutive として封じれば、境界は保たれる。**

---

## 5. 主要判定: Approval は Action Candidate まで進められる

**Human Approval は Support Candidate を Action Candidate へ進めることを許可できる。**
- **許可できない:** Need Definition / Representation / Recommendation / Ranking / Gateway Consent 代替 / Person Domain 開放（／単独 Execution）。
- Action Candidate から先は **Gateway Consent ＋ 実際の行為**の二鍵。

---

## 6. Reality Correction: candidate=0 → approval action=0

```
voice-006 owner consent = 0
verified bottleneck = held（F-11）
support candidate = 0（F-12）
Need = 0   Contribution = 0   Cooperation = 0   Decision = 0
```

- verified bottleneck が held → Support Candidate=0（F-12）→ **承認すべき候補が無い → approval action=0。**
- これは連鎖的に正しい data-driven 帰結（held verification → 0 candidate → 0 approval）。**ゼロは失敗でない・観察結果。**
- Approval が候補を製造して承認すること（無から action を起こす）は constitutive/捏造＝違反（Reality Correction）。
- honest 注記: Mujin raw の seed/test fixture は実在エンティティでない（一連と一貫）。実 Voice は voice-006 の 1 件。

---

## 7. 監査仮説 H1〜H5 の判定

| 仮説 | 判定 | 根拠 |
|---|---|---|
| **H1** Approval は Candidate を選択しない | **支持** | Q1/Q2。gate であって selection でない |
| **H2** Approval は Gateway Consent を代替しない | **支持** | Q5/Q8・H-15 |
| **H3** Approval は Person Domain を開かない | **支持** | Q6・H-16（owner consent=0） |
| **H4** Approval は Execution を開始しない | **支持** | Q7。二鍵＋実行を要す |
| **H5** Approval は許可的であり構成的でない | **支持** | §4・H-14 |

---

## 8. Approval の不変条件（F-13 確定）

```
approval_is_gatekeeping_not_constitutive : true  # §4/H-14
approval_advances_candidate_to_action_candidate : true # Q1/§2
approval_does_not_select_or_rank        : true   # Q1/Q2/H1
approval_generates_no_recommendation    : true   # Q3
approval_defines_no_gateway_need        : true   # Q4
approval_does_not_substitute_gateway_consent : true # Q5/H2
approval_does_not_open_person_domain    : true   # Q6/H3
approval_does_not_start_execution_alone : true   # Q7/H4
gateway_action_requires_two_keys        : true   # Q8/§3（Approval ∧ Gateway Consent）
person_action_requires_owner_consent    : true   # Q6（owner consent=0 ゆえ封印）
zero_candidate_means_zero_approval      : true   # Q9/§6
approval_does_not_fabricate_candidates  : true   # Q9（捏造禁止）
```

---

## 9. 推奨ステータスと現在地（honest）

- **Approval 境界モデルの設計整合性: strongly_aligned**（H-14 の gatekeeping/二鍵を F-12 候補に厳密適用・H-15 consent 代替不可と一貫・H-16 person 封印と整合・F-6/H-11 no ranking 継承・捏造禁止）。実 approval ゼロゆえ経験的裏付けは無い。
- **推奨: support_candidate_approval_defined / gate-not-constitute / zero-is-correct。**
  - **いま確定（文書のみ）:** Approval は候補を Action Candidate へ advance できる（permit/block）が selection/ranking/recommendation/need 定義/gateway-consent 代替/person 開放/単独 execution はできない、gateway 行為は二鍵（Approval ∧ Gateway Consent）、candidate=0 なら approval action=0、§8 不変条件。
  - **いま実装しない:** approval ゲートのコード。verified bottleneck=held → candidate=0 → approval=0 が正しい現在地。
- **方向: Approval は possibility を action-eligibility へ通す門。逆向き（承認で候補を選択/順位/推薦/decision 化、gateway/owner consent を代替、person domain・execution を開く、無から候補を捏造）は全経路で不採用。**

---

## 10. 成功条件の確認

- ✅ 生成なし / 登録なし / 文書のみ・コード/データ無変更。
- ✅ Approval が候補を Action Candidate へ進められること、selection/ranking/recommendation/need 定義/gateway-consent 代替/person 開放/単独 execution を許可できないこと、gateway 行為が二鍵を要すことを確定。Candidate┃Approval 境界（gate vs constitute）を監査。H1〜H5 を全支持。
- ✅ Reality Correction: candidate=0 ゆえ approval action=0 が正しいこと、ゼロは失敗でないこと、候補捏造が違反であること、seed データ非実在性を honest に記録。

---

*本文書は Support Candidate に対し Human Approval が何を許可でき・できないかの承認境界監査であり、何も生成しない。Human Approval は gatekeeping authority であって constitutive authority でない（H-14）ため、Support Candidate を Action Candidate へ進めること（各候補を permit/block する門）は許可できるが、それ自体は Decision でも Execution でもなく、Need Definition・Representation・Recommendation・Ranking・Gateway Consent 代替・Person Domain 開放・単独 Execution は許可できない——これらは constitutive だからである。Approval は permissive であって generative でなく、候補を選択も順位付けもせず（複数のまま門に通し）、recommendation を製造せず、gateway の need を定義せず、gateway の Resource Acceptance consent も owner consent も代替しない。gateway に影響する支援行為は Approval（系側の門）∧ Gateway Consent（gateway 側の門）の二鍵を要し、person に影響する行為は Approval ∧ Owner Consent を要すが owner consent=0 ゆえ封印され、鍵は足し合わせるもので置き換えるものでない。Approval が生むのは Action Candidate——承認された possibility であって選択された案でも実行計画でもなく、そこから先は gateway consent と実際の行為を要する。決定的な Reality Correction として、verified bottleneck が held（F-11）→ Support Candidate=0（F-12）→ 承認すべき候補が無い → approval action=0 という連鎖的に正しい data-driven 帰結であり、ゼロは失敗でなく観察結果であって、Approval が候補を製造して承認すること（無から action を起こすこと）は constitutive/捏造＝違反である。本監査は approval ゼロ（candidate=0・verified bottleneck held・実 Voice 1・raw seed は実在でない）の設計監査であり、verified bottleneck が確認され候補が possibility-only で生じるまで approval=0 が正しく、生じた後も Approval は gate であって constitute でない。Reach Gap・実価値は未解決であり、本文書もその解決を主張しないが、Human Approval を gate（許可的・per-candidate）に固定し constitutive な選択・定義・代替・開放から峻別することが、唯一正当な authority が権力へ膨張しないための防壁であることを確定する。*
