# Phase H-15: Consent Boundary Review

- **Status:** 基礎境界監査（Consent とは何か・何を許可し何を許可しないかの検証）。**コード/データ/Need/Gateway/Contribution/Cooperation/Decision 生成なし・登録なし。文書のみ。**
- **Date:** 2026-06-20
- **対象:** Consent / Approval / Voice / Need / Solution / Execution / Representation / Contribution / Cooperation
- **前提:** H-14（Approval は gatekeeping・consent outranks approval）, H-13（Authority 注入）, N-1.6/N-1.7（Need→Solution→Execution・選定/定義境界）, X-4.7（consent 三層）, 評価フレーム不可侵条項（consent/異議/撤回/尊厳）, Reality Correction（Jammy House/D.R.A.・voice-006 owner 不在）

> 中心問い: **Consent とは何か。そして何を許可し、何を許可しないのか。**
> 結論先取り: **Consent ＝「当事者本人が、理解の上で、自発的に、特定の対象に与える、撤回可能な肯定的許可」。沈黙は consent ではなく、代理人も Gateway も不在者の consent を代替できない。Consent は Representation を自動許可せず、Need 定義を他者に移譲せず、Authority を移譲しない。consent は“自分自身についてのみ”与えられる（self-referential）。voice-006 は owner 不在＝consent 不在ゆえ、Gateway Voice の存在は consent の代替にならず、当事者への定義・代弁・実行・接触は禁止され続ける。**

---

## 0. なぜ Consent が要石か

- H-14: 系で唯一正当な authority は Human Approval（gatekeeping）だが、それは **consent の下位**。
- ∴ **consent の境界が、正当な行為の“天井”を決める。** consent が及ばない所には、approval も届かない（approval は consent を超えられない）。
- だが consent 自体も無制限ではない——consent は**特定・自己限定・撤回可能・肯定的**であり、万能鍵ではない。本レビューはこの「上位だが有限」な consent の輪郭を確定する。

```
不可侵条項（当事者）: Consent / Objection / Withdrawal / Dignity
   └ Consent = 自分自身についての・特定の・撤回可能な肯定的許可（上位だが有限）
        ▲
Human Approval（gatekeeping・系の行為のみ）
        ▲
AI Proposal（advisory・authority none）
```

---

## 1. Q1〜Q10 の監査

### Q1. Consent の最小条件は何か

**5条件の同時成立:** ①**本人性**（当事者本人＝affected party が与える）②**informed**（何に同意するか理解）③**voluntary**（自発的・強制/誘導なし）④**specific**（特定対象・包括同意でない）⑤**revocable**（撤回可能・Q7/Q10）。
- 加えて暗黙の⑥**capacity**（同意能力）と、本レビューの核 ⑦**self-referential**（**自分自身についてのみ**与えられる）。
- **consent ＝ 肯定的・特定・自己限定・撤回可能な許可行為。** 1つでも欠ければ consent でない。

### Q2. 沈黙は Consent か

**No（決定的）。** 沈黙・無回答・不在は consent ではない。opt-out（拒否がないこと）は yes ではない。
- consent は**肯定的（affirmative）**でなければならない（Q1②③）。「No が無い」は「Yes」ではない。
- **voice-006 への含意:** owner 不在＝沈黙＝**consent 不在**。承認でも推定でも埋められない（§2）。

### Q3. 代理人は Consent を与えられるか

**原則 No。** 代理人・参加者・Agent は、当事者本人の consent を**製造できない**。
- 狭い例外は法的後見等（capacity 欠如時）だが、これは「Mujin が不在者の need を定義する」場面には適用されない。
- proxy consent ≠ 本人の consent。**self-referential（Q1⑦）ゆえ、他者は当事者“について”同意できない。**

### Q4. Gateway は Consent を代替できるか

**No（本レビューの中心・§2）。** Gateway（例: JAR）は**自分自身（gateway-as-actor）の領域**については consent できるが、**背後の不在 need owner に代わって consent できない**。
- Gateway Voice は「gateway 自身の状況の声」であって、不在当事者の同意ではない。
- **境界: gateway consent は gateway 領域（供給側調整・Case D/E）に限り有効。person 領域（不在者の need/代弁/実行）には及ばない。**

### Q5. Need Consent と Solution Consent は同じか

**No（N-1.6）。** 「これは私の need だ」（Need Consent）と「この解法（の方向）に同意する」（Solution Consent）は別。
- need の記録に同意することは、特定の solution への同意を含まない（Q1④ specific）。
- **境界: Need Consent ⊄ Solution Consent。need を認めても解法は別途同意を要す。**

### Q6. Execution Consent は別に必要か

**Yes（N-1.7）。** 「この解法に同意」（Solution Consent）と「今それを実行してよい・私に連絡してよい」（Execution Consent）は別。
- consent 三層: **Need → Solution → Execution**、各層独立。
- **境界: Solution への同意 ≠ Execution への同意。実行（接触・提出・行動）は別の・特定の consent を要す。**

### Q7. Withdrawal はどこまで遡及するか

**将来と進行中を即時に無効化するが、既成事実（取り返せない開示）は元に戻せない。**
- 撤回は (a) 進行中/将来の行為を**即時停止**、(b) 基盤を取り消し**新たな行為を不可**にし、(c) 可能な限り**削除/中止**を要求、(d) 撤回の記録自体は残す。
- **honest な限界: 既に共有された情報は撤回で“未開示”にできない。** ゆえに person 影響行為は**事前に慎重**であるべき——「後で撤回できる」を harm の言い訳にしない。

### Q8. Consent は Representation を許可するか

**自動的には No（H2）。** 参加への同意は代弁への同意を含まず、かつ自分の consent は**他者の代弁を授権しない**。
- consent は specific（Q1④）かつ self-referential（Q1⑦）——**人は自分についてのみ同意でき、他者を代表する権利を consent から得ない**。
- **境界: Consent ┃ Representation。代弁は別の明示同意を要し、対象は常に本人自身。**

### Q9. Consent は Authority を移譲するか

**No（H4）。** consent は**特定行為への許可**であって、決定権の移譲ではない。
- ある行為への同意 ≠ 将来を決める authority を相手に渡すこと。consent は act-specific・撤回可能で、standing な権限移譲（委任状）とは別物。
- **境界: Consent ┃ Authority。consent は許可であって authority transfer でない（H-13/H-14 と一貫）。**

### Q10. Consent の不在は何を禁止するか

**person 影響行為のすべてを禁止する。**
- 禁止: need 定義・代弁（representation）・solution 実行・接触・当事者への Contribution 帰属・当事者を含む Cooperation・その人に代わる Decision。
- 許可される（consent 不在でも）: **系内観察のみ**——「ある voice が存在する」と Hermes が記録すること（人に到達せず、人を語らない範囲）。
- **境界: consent 不在 ＝ person 領域の行為は進まない。observation は可、reaching/speaking-for/deciding-for は不可。**

---

## 2. 中心問い: voice-006 — Gateway Voice は Consent を代替するか

**No。** voice-006 は **Gateway 由来・need owner 不在**。

- Gateway Voice の存在が証すのは「**gateway が自分の状況を語った**」ことだけ。不在の need owner は**何も同意していない（沈黙＝consent 不在・Q2）**。
- Gateway は gateway 自身（actor）として供給側調整（Case D/E）に consent できる。だが**不在当事者の need/代弁/実行には consent を与えられない（Q4）**。

**ゆえに禁止され続けるもの（consent 不在の帰結・Q10）:**
1. 不在 owner の **Need を定義**すること（Saiyan Scouter 核心）。
2. 不在 owner を **代弁（represent）**すること。
3. 不在 owner へ **solution を実行・接触**すること。
4. 不在 owner に **Contribution を帰属/Decision を代行**すること。
5. 不在 owner を含む **Cooperation を割当**すること。

**許可され続けるもの:**
- voice-006 が「存在する」という**観察の記録**（人に到達しない）。
- **Gateway 自身（consenting actor）との、gateway 領域に限った関与**（供給側調整）——ただし gateway の consent の範囲を超えて不在者へ到達しないこと。

---

## 3. 監査仮説 H1〜H5 の判定

| 仮説 | 判定 | 根拠 |
|---|---|---|
| **H1** Consent は Approval より上位 | **支持** | §0 序列・H-14 Q8。consent が及ばぬ所に approval も届かない |
| **H2** Consent は Representation を自動許可しない | **支持** | Q8。specific＋self-referential ゆえ代弁を授権しない |
| **H3** Consent は Need Definition を他者へ移譲しない | **支持** | Q3/Q5。need 定義は当事者のみ、consent でも移譲不可 |
| **H4** Consent は Authority Transfer と同義でない | **支持** | Q9。act-specific な許可であって権限移譲でない |
| **H5** Withdrawal は Consent を無効化しうる | **支持（限界つき）** | Q7。将来/進行中を無効化、既成の開示は遡及不能 |

---

## 4. 重要境界（Consent ┃ X）

```
Consent ┃ Approval        : consent 上位。approval は consent を超えない（H1）
Consent ┃ Representation   : 参加同意 ≠ 代弁同意。self-referential（H2/Q8）
Consent ┃ Authority        : 許可であって権限移譲でない（H4/Q9）
Consent ┃ Need Definition  : need 同意 ≠ need 定義権の移譲。定義は当事者のみ（H3/Q3/Q5）
Consent ┃ Execution        : Need→Solution→Execution 各層独立。実行は別 consent（Q6/N-1.7）
```

- 共通核: **consent は specific（特定）・self-referential（自己限定）・revocable（撤回可能）。** どの境界も「consent を万能鍵にしない」一点に帰着する。

---

## 5. Consent 不変条件（H-15 確定）

```
consent_is_affirmative      : true   # 沈黙/不在は consent でない（Q2）
consent_is_informed         : true
consent_is_voluntary        : true
consent_is_specific         : true   # 包括同意でない（Q1④）
consent_is_self_referential : true   # 自分自身についてのみ（Q3/Q4/Q8）
consent_is_revocable        : true   # 撤回可能（Q7/Q10）
proxy_cannot_consent_for_person : true # 代理人/Gateway は本人 consent を代替しない（Q3/Q4）
gateway_voice_is_not_consent : true  # Gateway Voice ≠ 不在者 consent（§2）
consent_does_not_authorize_representation : true # （Q8/H2）
consent_does_not_transfer_authority : true       # （Q9/H4）
consent_does_not_move_need_definition : true     # （Q3/Q5/H3）
need_solution_execution_consent_separate : true  # 三層独立（Q5/Q6）
absence_of_consent_prohibits_person_action : true # （Q10）
withdrawal_voids_future_not_irreversible_past : true # （Q7・honest 限界）
```

- 序列の確定: **Consent（自己限定・特定・撤回可能・最上位）＞ Human Approval（gatekeeping）＞ AI 提案（advisory）。** consent 不在では person 領域の行為が一切進まない。

---

## 6. Reality Correction

```
Voice Count        = 1   （= voice-006・Gateway 由来・need owner 不在 → consent 不在）
Need Count         = 0
Contribution Count = 0
Cooperation Count  = 0
Decision Count     = 0
Participation Count = 0
```

- 唯一の実体 voice-006 は **owner 不在＝consent 不在**。ゆえに person 領域の行為（定義・代弁・実行・接触・帰属・割当）は**現状すべて禁止**——これは欠陥ではなく consent 境界の正しい帰結。
- honest 注記: Mujin raw の seed/test fixture（voice 6行・needs 8 等）は**検証された実エンティティでない**（H-12〜H-14 と一貫）。実 Voice は voice-006 の 1 件、他は 0。
- **consent ゼロの今、許されるのは「voice-006 が存在する」観察と、gateway 自身（consenting actor）の領域での供給側関与のみ。** 不在者へは到達しない。

---

## 7. 推奨ステータスと現在地（honest）

- **Consent 境界モデルの設計整合性: weakly_supported → 中核的に堅牢**（coherent・H-14 の「consent outranks approval」に必要な consent 定義を供給・N-1.6/N-1.7 の三層と整合・不可侵条項と整合・Reality Correction と一致）。実 consent ゼロゆえ経験的裏付けは無いが、**境界自体は系の安全の要石として機能する**。
- **推奨: consent_boundary_defined / implementation_deferred。**
  - **いま確定（文書のみ）:** Consent 5（＋2）条件、沈黙≠consent、proxy/Gateway 不可、Need/Solution/Execution 三層独立、Consent ┃ Representation/Authority/Need Definition/Execution 境界、撤回の遡及限界、§5 不変条件。
  - **いま実装しない:** consent ゲートのコード。person 影響行為が生じるまで gated。実装時は §5 を全 person-affecting 点に組み込み、affirmative・specific・self-referential・revocable を必須とし、gateway consent と person consent を構造的に分離する。
- **方向: consent は当事者本人の・特定の・自己限定の・撤回可能な許可。逆向き（沈黙/Gateway/代理から consent を推定し、定義/代弁/実行/権限移譲へ）は全経路で不採用。**

---

## 8. 成功条件の確認

- ✅ Need 生成なし / Gateway 生成なし / Contribution 生成なし / Cooperation 生成なし / Decision 生成なし / 登録なし / 文書のみ・コード/データ無変更。
- ✅ Consent の最小条件と5境界を確定。沈黙・代理・Gateway が consent を代替しないこと、consent が Representation/Authority/Need Definition を許可/移譲しないことを監査。H1〜H5 を全支持。
- ✅ Reality Correction: voice-006 の owner 不在＝consent 不在ゆえ person 領域行為が禁止され続けること、seed データ非実在性を honest に記録。

---

*本文書は Consent とは何か・何を許可し何を許可しないかの基礎境界監査であり、何も生成しない。Consent ＝「当事者本人が、理解の上で、自発的に、特定の対象に与える、撤回可能な肯定的許可」であり、決定的に自己限定的（self-referential：人は自分自身についてのみ同意できる）である。沈黙・不在は consent ではなく（opt-out は yes でない）、代理人も Gateway も不在者の consent を代替できない。Consent は Representation を自動許可せず（参加同意≠代弁同意・代弁は本人のみ）、Need 定義を他者へ移譲せず（定義は当事者のみ）、Authority を移譲しない（act-specific な許可であって権限委任でない）。Need→Solution→Execution consent は各層独立で、実行は別の特定 consent を要す。Withdrawal は将来と進行中を即時無効化するが既成の開示は遡及できない（ゆえ事前の慎重さが要る）。consent の不在は person 影響行為のすべて（定義・代弁・実行・接触・帰属・割当・代行決定）を禁止し、許すのは系内観察のみ。voice-006 は owner 不在＝consent 不在ゆえ、Gateway Voice の存在は consent の代替にならず、Gateway は自分自身（actor）の供給側領域には consent できても不在当事者の need/代弁/実行には consent を与えられない——ゆえに不在者への定義・代弁・実行・接触は禁止され続け、許されるのは voice-006 の存在の観察と gateway 領域に限った関与のみである。序列は「Consent（自己限定・特定・撤回可能・最上位）＞ Human Approval（gatekeeping）＞ AI 提案」で固定され、consent を万能鍵にしないことが全境界の共通核である。本監査は consent ゼロ（実 Voice 1・owner 不在・他 0、raw seed は実在でない）の設計監査であり実運用の漏れは未検証だが、consent 境界は系の安全の要石として機能する。Reach Gap・実価値は未解決であり、本文書もその解決を主張しない。*
