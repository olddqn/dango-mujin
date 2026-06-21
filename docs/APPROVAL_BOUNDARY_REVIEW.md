# Phase H-14: Approval Boundary Review

- **Status:** 境界監査（Human Approval は Authority か・どこまで許されるかの検証）。**コード/データ/生成/登録なし。文書のみ。**
- **Date:** 2026-06-20
- **対象:** Human Approval / Consent / Objection / Withdrawal / Voice / Need / Gateway / Contribution / Cooperation / Decision
- **前提:** H-13（Authority Injection・J を唯一正当だが三重境界）, base_invariants（`authority: none`・`human_approval_required`）, N-1.6/N-1.7（Need 定義は当事者のみ・選定禁止）, H-5（Cooperation assign 禁止）, H-6（Hermes は決定しない）, 評価フレーム不可侵条項（consent/異議/撤回/尊厳）, X-4.7（consent 三層）

> 中心問い: **Human Approval は Authority なのか。もし Authority なら、どこまで許されるのか。**
> 結論先取り: **Yes、だが特定の限定された種類——「系の提案行為に対する gatekeeping（許可/拒否）」であって、不在者を“定義・代弁・決定”する constitutive（構成的）authority ではない。Approval は許可的（permissive）であって創造的（generative）ではなく、不可侵条項（consent/異議/撤回/尊厳）の下位に立つ。Consent は Approval の上位、Objection は Approval を停止し、Withdrawal は Approval を無効化する。voice-006 owner 不在ゆえ Q3（代表）は live——承認は不在を埋められない。**

---

## 0. 二種類の Authority

- **Gatekeeping authority（正当）:** 系が提案した行為を**許可/拒否する権利**。系（system）に対する veto＋gate。「AI proposes — Human decides」の Human がこれを行使する。
- **Constitutive authority（不在者に対しては不当）:** 不在者の need を**定義**し、voice を**代弁**し、その人に代わって**決定**する権利。これは当事者本人にのみ属し、Approval は持たない。

```
不可侵条項（当事者本人）: Consent / Objection / Withdrawal / Dignity   ← 最上位（覆せない）
        ▲
Human Approval（系への gatekeeping・許可的）                          ← 中位
        ▲
AI Proposal（advisory・authority none）                              ← 下位
```

- **Approval は中位の gatekeeping authority。** 上に不可侵条項（当事者）、下に AI 提案。**不在者に対する constitutive authority へは決して上昇しない。**

---

## 1. Q1〜Q10 の監査

### Q1. Human Approval は Authority か

**Yes——ただし「系の提案への gatekeeping authority」に限定。** 系における唯一正当な authority（H-13）だが、(1) 対象は**系の行為**であって不在者ではない、(2) **許可的**であって創造的でない（許可は事実・need・代表を生まない）、(3) **不可侵条項の下位**。
- ∴ Approval は「行為を通す/止める」権利であって、「人を定義する/代弁する/その人に代わって決める」権利ではない。

### Q2. Human Approval は Need を定義できるか

**No。** Need 定義は当事者のみ（N-1.6）。Approval は**当事者が述べた need の系内記録を許可**できるが、不在者の need を自ら定義できない。
- 「承認したのだから、この人の need はこうだ」は permissive→constitutive への変質（最も危険）。
- **境界: Approval は need の“記録/取り扱い”を許可するが、need の“内容”を構成しない。`approval_defines_no_need=true`。**

### Q3. Human Approval は Voice を代表できるか

**No——voice-006 owner 不在ゆえ live。** Voice 代表は voice owner 本人のみ。
- Approval は voice の取り扱い（記録・gateway 経由の中継）を許可できるが、**owner に代わって語れない**。owner 不在は承認では埋まらない。
- **境界: 不在の owner がいる時、Approval は「不在を承認で代替」してはならない。行為は保留するか、当事者本人にのみ属する代表を待つ。`approval_is_not_representation=true`。**

### Q4. Human Approval は Gateway を選定できるか

**単独では No。** 選定（set→1 の縮約）は当事者＋人間の協働（N-1.7）。
- Approval は系が提示した**複数候補（plural）の取り扱いを許可**できるが、不在者に代わって 1 つに選定できない。選定は当事者の参加を要す。
- **境界: Approval は複数候補の提示を許可するが、当事者不在で選定を代行しない。`approval_selects_no_gateway_for_absent=true`・複数候補維持。**

### Q5. Human Approval は Contribution を帰属できるか

**順位・功績を生む帰属は No。** Approval は act が受領された事実の**記録を許可**できるが、reputation/序列につながる attribution を作れない（H-13 Q2）。
- **境界: 無帰属・無順位の受領記録は許可可。功績・序列・reputation を生む attribution は不可。`approval_creates_no_ranked_attribution=true`。**

### Q6. Human Approval は Cooperation を割り当てできるか

**No。** Cooperation 割当は当事者本人たちが形成（H-5）。
- Approval は「協力が在りうる」possibility の記録を許可できるが、actor を割り当てられない。
- **境界: 協力は本人＋当事者が形成、Approval は assign しない。`approval_assigns_no_cooperation=true`・actor 無名。**

### Q7. Human Approval は Decision を正当化できるか

**行為を“許可（permit）”できるが、“正当（legitimate/right）”にはしない。**
- Approval は系の行為を**通す**が、その行為を**真/正しい**にする力はない。とりわけ、不在者に影響する決定は**当事者の consent から正当性を得る**のであって、承認だけでは正当化されない。
- consent/尊厳を侵す決定は、誰が承認しても不当（不可侵条項・§Q8〜Q10）。
- **境界: Approval は decision を permit する gate であって、persons に対する legitimacy の源泉ではない。`approval_permits_not_legitimizes=true`。**

### Q8. Consent は Approval の上位か

**Yes。** 当事者の consent は reviewer の approval より上位。
- 両者が衝突する時、**consent が勝つ**。Approval は consent に反して進めない。
- **境界: `consent_outranks_approval=true`。Approval は consent の上に立たない（当事者の自己決定が最終）。**

### Q9. Objection は Approval を停止できるか

**Yes。** 当事者の異議は承認済み行為を**停止**する。
- Objection は approval を覆すブレーキ（不可侵条項）。承認は異議を握りつぶせない。
- **境界: `objection_halts_approval=true`。異議が立った時点で行為は止まる。**

### Q10. Withdrawal は Approval を無効化できるか

**Yes。** consent の撤回は承認の基盤を**遡及的に無効化**する。
- consent は撤回可能であり、撤回後は approval が行為を生かし続けられない。承認は撤回に追従する。
- **境界: `withdrawal_voids_approval=true`。撤回後の継続は不可（記録は残すが行為は止め、可能なら取り消す）。**

---

## 2. 中心監査: Human Approval → Authority 変質

```
[Human Approval]  gatekeeping（系への許可・正当）
        │  変質線 = permissive → constitutive（「承認したから定義/代表/決定してよい」）
        ▼
[Constitutive Authority over persons]  不在者を定義・代弁・決定（不当）
```

- **変質の本質: gatekeeping（行為を通す）が constitutive（人を構成する）へ滑ること。** 「承認した」を根拠に need 定義（Q2）・voice 代表（Q3）・gateway 選定（Q4）・decision 正当化（Q7）を行うのが変質点。
- **唯一の構造的保証: Approval を permissive に固定する。** 承認は行為を**通す/止める**だけで、事実・need・代表・正当性を**生まない**。constitutive な領域（need/voice/selection/legitimacy over persons）には当事者 consent が必須で、approval はその下位。

---

## 3. 二鍵原則（person-affecting action）

```
系内のみの行為:           Human Approval で足りる（gate を通る）
人に影響する行為:         Human Approval ∧ 当事者 Consent（両方必須・どちらも単独では不十分）
                          かつ Objection で停止・Withdrawal で無効化されうる
```

- person-affecting な行為は **Approval と Consent の二鍵**を要し、いずれの単独でも開かない。
- voice-006（owner 不在）に影響する行為は、当事者 consent が得られないため**二鍵が揃わず開かない**——承認で代替できない（Q3）。

---

## 4. Approval 境界の不変条件（H-14 確定）

```
authority_kind            : "gatekeeping"   # 系の行為への許可/拒否のみ
approval_is_permissive    : true            # 許可的であって創造的でない
approval_is_not_constitutive : true         # 不在者を定義/代表/決定しない
approval_defines_no_need  : true            # Q2
approval_is_not_representation : true       # Q3（owner 不在を埋めない）
approval_selects_no_gateway_for_absent : true # Q4
approval_creates_no_ranked_attribution : true # Q5
approval_assigns_no_cooperation : true      # Q6
approval_permits_not_legitimizes : true     # Q7
consent_outranks_approval : true            # Q8
objection_halts_approval  : true            # Q9
withdrawal_voids_approval : true            # Q10
two_key_for_person_action : true            # Approval ∧ Consent（§3）
```

- 序列の固定: **不可侵条項（当事者） > Human Approval（gatekeeping） > AI 提案（advisory）。** Approval はこの中位を超えない。

---

## 5. Reality Correction

```
Voice Count        = 1   （= voice-006・Gateway 由来・need owner 不在）
Need Count         = 0
Contribution Count = 0
Cooperation Count  = 0
Decision Count     = 0
Participation Count = 0
```

- 承認すべき系の行為も、当事者 consent を得るべき相手も、現状ほぼ存在しない。
- **唯一の実体 voice-006 は owner 不在**——ゆえに「承認が不在を代替しうるか」（Q3/Q4/Q7）の問いが**理論でなく現実に live**。答えは一貫して No: 承認は不在を埋めない。
- honest 注記: Mujin raw の seed/test fixture（voice 6行等）は実在エンティティでない（H-12/H-13 と一貫）。実 Voice は voice-006 の 1 件、他は 0。
- **行為ゼロの今こそ、Approval の中位境界と二鍵原則を基層に固定する好機。**

---

## 6. 推奨ステータスと現在地（honest）

- **Approval 境界モデルの設計整合性: weakly_supported**（coherent・H-13 の J 三重境界を精密化・不可侵条項と整合・N-1.6/N-1.7/H-5/H-6 の各境界と整合）。行為ゼロゆえ経験的裏付けは無い。**実体ゼロの設計監査であり、実運用での漏れは未検証。**
- **推奨: approval_boundary_audited / implementation_deferred。**
  - **いま確定（文書のみ）:** Approval は gatekeeping authority（permissive・系への許可）であって constitutive authority（不在者の定義/代表/決定）でない、序列（不可侵条項 > Approval > 提案）、二鍵原則（Approval ∧ Consent）、Consent 上位・Objection 停止・Withdrawal 無効化、§4 不変条件。
  - **いま実装しない:** approval ゲートのコード。承認すべき行為が生じるまで gated。実装時は §4 を全 approval 点に組み込み、person-affecting 行為に二鍵（approval＋当事者 consent）を必須とし、objection/withdrawal の即時反映を実装する。
- **方向: Approval は系の行為を gate するのみ。逆向き（承認 → 不在者の need 定義/voice 代表/gateway 選定/decision 正当化）は全経路で不採用。**

---

## 7. 成功条件の確認

- ✅ Approval が Need 定義 / Voice 代表 / Gateway 選定 / Contribution 帰属 / Cooperation 割当 / Decision 正当化 のいずれにも変質していない（permissive 固定）。
- ✅ Consent 上位・Objection 停止・Withdrawal 無効化を確定。二鍵原則（Approval ∧ Consent）を person-affecting 行為に課す。
- ✅ Reality Correction: voice-006 owner 不在を承認で代替しない（Q3 live）こと、seed データ非実在性を honest に記録。

---

*本文書は Human Approval が Authority かつどこまで許されるかの境界監査であり、何も生成しない。Human Approval は Authority だが「系の提案行為への gatekeeping（許可/拒否）」に限定され、不在者を定義・代弁・決定する constitutive authority ではない。Approval は許可的（permissive）であって創造的（generative）でなく、事実・need・代表・正当性を生まない。序列は「不可侵条項（当事者の consent/異議/撤回/尊厳）＞ Human Approval ＞ AI 提案」で固定され、Consent は Approval の上位、Objection は Approval を停止し、Withdrawal は Approval を遡及的に無効化する。人に影響する行為は Approval と当事者 Consent の二鍵を要し、いずれの単独でも開かない。変質の本質は gatekeeping が constitutive へ滑ること（「承認したから定義/代表/決定してよい」）で、唯一の構造的保証は Approval を permissive に固定し constitutive 領域を当事者 consent に委ねることである。voice-006 が owner 不在であるため「承認が不在を代替しうるか」は現実に live であり、答えは一貫して No——承認は不在を埋めない。本監査は行為ゼロ（実 Voice 1・他 0、raw seed は実在でない）の設計監査であり実運用の漏れは未検証だが、行為がゼロの今こそ Approval の中位境界と二鍵原則を基層に固定する好機である。Reach Gap・実価値は未解決であり、本文書もその解決を主張しない。*
