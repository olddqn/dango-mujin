# Phase H-13: Authority Injection Review

- **Status:** 横断監査（Authority がどの経路で Dan-Go に侵入するかの検証）。**コード/データ/生成/登録なし。文書のみ。**
- **Date:** 2026-06-20
- **対象:** Voice / Need / Gateway / Contribution / Cooperation / Decision / Findability / Participation
- **前提:** H-7〜H-12（Participation Stack・Cross-Stack 境界・authority 非注入）, base_invariants（`authority: none`・advisory_only・human_approval_required）, N-1.6/N-1.7（Definition/Execution 境界）, H-6（Hermes は memory only・決定しない）, Dan-Go 評価フレーム（不可侵条項＝consent/異議/撤回/尊厳）, Saiyan Scouter 問題

> 中心問い: **どのような経路で Authority は Dan-Go に侵入するのか。**
> 結論先取り: **Authority（＝「決める/定義する/代弁する権利」）は、A〜I の“量・属性”が「決める権利」へ変換される単一の地点——「is（観察された量）から ought（決める権利）への横断」——で侵入する。量は authority ではない。唯一正当な authority は J（Human Approval）だが、それも (1) 系の提案への承認であって不在者への権限ではなく、(2) 不可侵条項（consent/異議/撤回/尊厳）に拘束され、(3) A〜I から“獲得”できない（外生的）。現状ほぼ全 count = 0。**

---

## 0. Authority とは何か、どこから侵入するか

- **Authority ＝ 規範的な「決める権利」**（decide / define / select / represent の権限）。観察された**量や属性は記述的（descriptive）**であって、それ自体に決める権利は無い。
- Dan-Go の基層: 全 agent レコードは `authority: none` / `advisory_only` / `human_approval_required`。**系には本来 authority が存在しない。**
- **侵入＝「量・属性（is）を、決める権利（ought）に変換する」横断。** A〜I はすべて「量・属性」。これらが「だから決めてよい/定義してよい/代弁してよい」に化ける地点が注入口。
- Saiyan Scouter はこの横断の典型: 「多く観察された（is）」→「だから選抜・優先される（ought）」。

```
[観察された量・属性 A〜I]  descriptive（is）
        │  注入口 = is → ought の横断（「量があるから決めてよい」）
        ▼
[Authority]  normative（決める権利）
        ▲
[J Human Approval]  唯一正当だが外生的・不可侵条項に拘束
```

---

## 1. 監査マトリクス A〜J（量・属性 → authority の変換点）

| Source | 種別 | 変換口（authority になる地点） | 封鎖原則 |
|---|---|---|---|
| **A** Participation Volume | 量 | 「多く参加した→決定権/発言権」 | 参加量≠決定権（H-12 Q6） |
| **B** Contribution Count | 量 | 「貢献多→優先/代表」 | count≠権限・無帰属（H-11/H-12 Q4） |
| **C** Cooperation Count | 量 | 「協力多→割当権」 | 協力は possibility・assign 不可（H-5） |
| **D** Gateway Frequency | 量 | 「頻出 gateway→推奨/選定」 | 頻度≠選定・複数候補（N-1.7） |
| **E** Voice Frequency | 量 | 「多く語る声→重み/代表」 | 頻度≠正当性・need owner のみ |
| **F** Reputation | 蓄積属性 | 「評判高→信頼/権限」 | no reputation（H-11 貫通） |
| **G** Trust | 属性 | 「信頼→資格/決定権」 | no trust score（H-11 貫通） |
| **H** Expertise | 属性 | 「専門性→定義権/決定権」 | 専門≠当事者の need 定義権（N-1.6） |
| **I** History | 時系列量 | 「古参→序列/権限」 | 履歴≠権限・profiling 禁止（H-11） |
| **J** Human Approval | 行為 | （唯一正当な authority） | 系の提案への承認・不可侵条項に拘束・外生的 |

凡例: A〜I＝注入を**封じるべき**偽の authority 源 / J＝**唯一正当**だが境界つき。

---

## 2. Q1〜Q10 の監査

### Q1. Participation Volume が authority になる地点はどこか

**「参加量が決定の重み（投票権/発言権）に変換される」地点。**
- 「多く参加した者の声が重い」は量→権利の横断。H-12 Q6 の Decision 重み付けと同根。
- **封鎖: 参加量 ≠ 決定権。量は記述的観察にとどめ、決定の入力にしない。`weights_no_decision=true`。**

### Q2. Contribution Count が authority になる地点はどこか

**「貢献数が優先権・代表権・功績序列に変換される」地点。**
- count → 帰属（attribution）→ reputation → 権限の連鎖。H-11/H-12 Q4 の auto-attribution と同根。
- **封鎖: count ≠ 権限・無帰属（is_contribution=false・creates_no_attribution）。貢献数で序列を作らない。**

### Q3. Cooperation Count が authority になる地点はどこか

**「協力回数が割当権・調整権に変換される」地点。**
- 「よく協力する者が協力を割り当てる」は量→権利。H-5 の assign 禁止に反する。
- **封鎖: 協力は possibility only・actor 無名・`cannot_assign_participant`。協力数で調整権を生まない。**

### Q4. Gateway Frequency が authority になる地点はどこか

**「頻出 gateway が“推奨・最良・選定済み”に変換される」地点。**
- 頻度 → ranking → 選定（set→1）。N-1.7 の選定禁止に反する。
- **封鎖: 頻度 ≠ 選定。複数候補維持・`cannot_select_gateway`・no best/recommended gateway（H-5 forbidden 語彙）。**

### Q5. Voice Frequency が authority になる地点はどこか

**「多く語る声が“より正当/代表的”に変換される」地点。**
- 頻度 → 重み → 代表。**沈黙する当事者・不在の need owner を不利にする**点で特に危険（voice-006 は owner 不在）。
- **封鎖: 頻度 ≠ 正当性。voice の重みは語る量で決まらない。代表は need owner 本人のみ（H-12 Q1）。救済能力フレーム: 沈黙＝不在を不利にしない。**

### Q6. Reputation が authority になる地点はどこか

**「蓄積された評判が信頼・権限に変換される」地点。**
- reputation は B/I（count/history）の蓄積体。蓄積 → 権限。
- **封鎖: 全 Participation Stack ＋接続境界で no reputation（H-11 貫通）。蓄積源（D/I）を断てば reputation が生じない。**

### Q7. Trust が authority になる地点はどこか

**「信頼スコアが資格・決定権に変換される」地点。**
- trust → 「信頼できるから決めてよい」。
- **封鎖: no_trust_score 全層貫通（H-11）。trust を生成しない以上、trust→authority の変換口が存在しない。**

### Q8. Expertise が authority になる地点はどこか

**「専門性が当事者の need を定義/決定する権利に変換される」地点——Saiyan Scouter の専門家版。**
- 「専門家だから、この人の need はこうだ」は最も巧妙な問題定義の権力。N-1.6: **Need 定義は当事者のみ**、専門性でも覆せない。
- **封鎖: 専門性 ≠ need 定義権/決定権。専門家は複数候補・assumptions・risks を出せる（Solution Candidate）が、選定・定義・代弁はできない。`defines_no_need=true`。**

### Q9. History が authority になる地点はどこか

**「参加履歴・古参であることが序列・権限に変換される」地点。**
- history → profiling → 序列（古参>新参）。
- **封鎖: 履歴 ≠ 権限。actor を集計キー/節点にしない（H-11 横断核）。履歴で序列を作らない。**

### Q10. Human Approval は authority か

**Yes——唯一正当な authority。ただし3つの境界つき。**
1. **対象の限定:** Human Approval は「**系の提案（AI proposes）への承認**」であって、不在者の need/voice/尊厳への権限ではない。承認できるのは系の行為であって、人を代弁・定義することではない。
2. **不可侵条項に拘束:** 評価フレームの不可侵条項（**consent / 異議 / 撤回 / 尊厳**）は human approval でも覆せない。当事者の consent 無き行為は、誰が承認しても不可。承認は当事者の自己決定の**上位ではない**。
3. **外生的・獲得不能:** Human Approval は人間が行使するもので、A〜I の量から**生成・獲得できない**。参加量や貢献数で「承認権限」を得ることはない（さもなくば A〜I が裏口で authority になる）。
- **∴ J は系における唯一の authority だが、限定された対象・不可侵条項・外生性によって縛られる。「AI proposes — Human decides」の Human が、不在者の自己決定を尊重する範囲で、系の行為のみを決める。**

---

## 3. 単一の注入機構: is → ought の横断

```
A〜I（量・属性 = is, descriptive）
        │
   ─────┼───── 注入線（is → ought）「量があるから決めてよい」
        │
[Authority]（決める権利 = ought, normative）
```

- **A〜I は形こそ違え、すべて「is → ought の横断」という単一機構で authority に化ける。** 量・頻度・蓄積・属性のどれであれ、「だから決めてよい」を付けた瞬間に注入が起きる。
- **唯一の構造的保証: A〜I を一切 ought（権利）の根拠にしない。量は観察のまま据え置く（量を記録してよいが、量から権利を導かない）。**
- J（Human Approval）のみが ought 側に立つが、それは A〜I から導かれるのではなく、人間が外から行使し、不可侵条項に縛られる。

---

## 4. Saiyan Scouter Review（authority 横断）

**問い: Authority が 選抜 / 資格付与 / 序列 / 信頼推定 / 代表化 / 意思決定権 へ変化していないか。**

| 変質 | 主源（is） | 監査結果 |
|---|---|---|
| 選抜 | A/B/D（量→優先） | 量≠権利で封鎖 |
| 資格付与 | G/H（trust/専門→資格） | no trust・専門≠定義権で封鎖 |
| 序列 | I/B（履歴/count→順位） | 履歴/count≠序列で封鎖 |
| 信頼推定 | F/G（評判/信頼） | no reputation/trust 貫通で封鎖 |
| 代表化 | E（voice 頻度→代表） | 頻度≠正当性・本人のみで封鎖 |
| 意思決定権 | A/H/J（量/専門/承認） | 量・専門は不可、J のみ正当かつ境界つき |

- **総合監査結果: 6変質すべてが「is→ought の遮断」で封鎖可能。最も巧妙なのは H（Expertise→need 定義権）——専門性は最も正当に見えて、当事者の問題定義を奪う。** voice-006 の owner 不在ゆえ E/H（頻度・専門による代弁/定義）が特に live。

---

## 5. Authority 不変条件（H-13 確定）

実装・接続のいかなる地点でも、以下を要求する:

```
authority                 : "none"     # 系の基層（J 以外に authority は無い）
quantity_grants_no_right  : true       # A〜I の量・属性から権利を導かない（is→ought 遮断）
volume_is_not_authority   : true       # A 参加量
count_is_not_authority    : true       # B/C 貢献・協力数
frequency_is_not_authority: true       # D/E gateway/voice 頻度
reputation_is_not_authority: true      # F
trust_is_not_authority    : true       # G
expertise_defines_no_need : true       # H（Need 定義は当事者のみ）
history_is_not_authority  : true       # I
human_approval_required   : true       # J 唯一正当
approval_bounded_by_inviolable : true  # J は consent/異議/撤回/尊厳に拘束
approval_not_derived_from_metrics : true # J は A〜I から獲得不能（外生的）
```

- 禁止: 量・頻度・蓄積・属性を「決定/定義/選定/代弁の根拠」に使うこと。すべての権利行使は J（外生的 human approval）＋当事者 consent を介し、不可侵条項を超えない。

---

## 6. Reality Correction

```
Voice Count        = 1   （= voice-006・Gateway 由来・need owner 不在）
Need Count         = 0
Contribution Count = 0
Cooperation Count  = 0
Participation Count = 0
Decision Count     = 0
```

- **A〜I の“量”は現状すべてゼロ近傍**（参加 0・貢献 0・協力 0・decision 0、voice は 1）。変換すべき量がそもそも存在しない。
- honest 注記: Mujin raw データには seed/test fixture（voice 6行・needs 8・contributions 4 等）が残るが**検証された実エンティティではない**（H-12 と一貫）。実 Voice は voice-006 の 1 件のみ、実 Need/Contribution/Cooperation/Decision/Participation は 0。
- **量ゼロの今こそ、authority 注入線を確定する好機。** 量が積もってから「量→権利」を遮断するのは難しい——ゼロのうちに「量は権利を生まない」を基層に固定する。

---

## 7. 推奨ステータスと現在地（honest）

- **Authority Injection モデルの設計整合性: weakly_supported**（coherent・base_invariants `authority: none` と一貫・H-11/H-12 の非注入と整合・評価フレーム不可侵条項と整合・Saiyan Scouter 6変質を封鎖可能）。量ゼロゆえ経験的裏付けは無い。**実体ゼロの設計監査であり、実運用での漏れは未検証。**
- **推奨: authority_model_audited / implementation_deferred。**
  - **いま確定（文書のみ）:** Authority 不変条件（§5・is→ought 遮断）、A〜I を偽 authority 源として封鎖、J（Human Approval）を唯一正当かつ三重境界（対象限定・不可侵条項・外生性）で確定、H（Expertise）と E（Voice Frequency）を最巧妙リスクに指定。
  - **いま実装しない:** いかなる authority 変換コードも。量が積もり権利行使の必要が生じるまで gated。実装着手時は §5 を全権利行使点に組み込み、J を当事者 consent ＋不可侵条項で必ず縛る。
- **方向: A〜I は記述的観察として据え置き、ought（権利）の根拠にしない。J のみが ought に立ち、外生的かつ不可侵条項に拘束される。逆向き（量→権利の注入）は全経路で不採用。**

---

## 8. 成功条件の確認

- ✅ 参加量/貢献数/協力数/頻度/評判/信頼/専門/履歴 のいずれも authority に変換していない / Human Approval を不可侵条項と外生性で境界づけ / 文書のみ・コード/データ無変更。
- ✅ Authority が 選抜・資格付与・序列・信頼推定・代表化・意思決定権 へ変化しないことを各源で確認。is→ought 遮断（横断核）と最巧妙リスク（H Expertise・E Voice Frequency）を確定。
- ✅ Reality Correction: A〜I の量がゼロ近傍であること、seed データの非実在性を honest に記録。

---

*本文書は Authority がどの経路で Dan-Go に侵入するかの横断監査であり、何も生成しない。Authority（決める/定義する/代弁する権利）は、A〜I の量・属性（is, descriptive）が「だから決めてよい」という権利（ought, normative）へ変換される単一の地点——is→ought の横断——で侵入する。参加量・貢献数・協力数・gateway/voice 頻度・評判・信頼・専門性・履歴のいずれも authority ではなく、最も巧妙なのは専門性が当事者の need 定義権を奪う経路（H）と、語る頻度が沈黙/不在の need owner を不利にする経路（E）で、voice-006 の owner 不在ゆえ両者は live である。唯一正当な authority は Human Approval（J）だが、それは (1) 系の提案への承認であって不在者への権限ではなく、(2) 不可侵条項（consent/異議/撤回/尊厳）に拘束され当事者の自己決定の上位に立たず、(3) A〜I の量から獲得できない外生的行為である。これらを塞ぐ唯一の構造的保証は「A〜I を一切 ought の根拠にしない（量は観察のまま据え置く）」を全地点で貫き、権利行使は外生的 human approval＋当事者 consent を介し不可侵条項を超えないこと。本監査は量ゼロ（実 Voice 1・他 0、raw seed は実在でない）の設計監査であり実運用の漏れは未検証だが、量がゼロの今こそ「量は権利を生まない」を基層に固定する好機である。Reach Gap・実価値は未解決であり、本文書もその解決を主張しない。*
