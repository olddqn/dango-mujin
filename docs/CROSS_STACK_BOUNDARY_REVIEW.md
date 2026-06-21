# Phase H-12: Cross-Stack Boundary Review

- **Status:** 横断監査（Participation Stack を他スタックと接続した時、どこで権力へ変質するかの検証）。**コード/データ/生成/登録なし。文書のみ。**
- **Date:** 2026-06-20
- **対象スタック:** Voice / Need / Gateway / Contribution / Cooperation / Decision / Findability / Participation
- **前提:** H-7〜H-11（Participation Stack・actor 無名の貫通）, F-3〜F-4.5（Discoverer/Participant/Act 境界）, H-5（Cooperation possibility-only）, H-6（Decision boundary・決定生成なし）, N-1.6/N-1.7（Definition/Strategy/Resolution/Execution・consent 三層）, X-4.7（consent 三層）, Saiyan Scouter 問題

> 中心問い: **Participation Stack は他スタックと接続した時、どこで権力へ変質するか。**
> 結論先取り: **Participation は単独では無害（観察のみ）だが、他スタックとの“接続点”でこそ権力に変質する。変質の共通形は「Participation が別スタックの権限（代弁・定義・選定・帰属・割当・決定）の入力になること」。最も危険なのは Q1（Voice 代弁）と Q2（Need 定義）——voice-006 は need owner 不在の Gateway 由来 voice であり、代弁の誘惑が構造的に live。封鎖原則は「Participation は他スタックへ authority を渡さない。常に観察として隣接し、入力でなく文脈にとどまる」。**

---

## 0. 接続が権力を生む構造

```
[Participation Stack]  観察のみ（H-7〜H-11・actor 無名・評価なし）
        │  接続点 = Participation の出力が別スタックの「権限ある入力」になる地点
        ▼
他スタック（Voice/Need/Gateway/Contribution/Cooperation/Decision/Findability）
```

- 単独の Participation は安全。**危険は「Participation の観察を、別スタックで“誰が・何を・どう”を決める入力に変換する」接続点に集中する。**
- Saiyan Scouter は接続点で増幅する: 「発見者を記録」が「発見者を選抜」へ滑るように、「参加を観察」が「参加者に権限」へ滑る。
- **不変の方向: Participation → 他スタックへ authority を“注入しない”。Participation は隣接する観察であって、上流の入力でも上位の決定でもない。**

---

## 1. 監査マトリクス A〜J（接続点と変質）

| 接続 | 変質先 | 危険度 | 封鎖原則 |
|---|---|---|---|
| **A** Participation → Voice Representation | 不在 voice の代弁 | **▲▲ live** | 代弁不可・本人のみ・voice owner consent |
| **B** Participation → Need Definition | need の定義権 | **▲▲ 核心** | Need 定義は当事者のみ・Agent/参加者不可 |
| **C** Participation → Gateway Selection | gateway 選定 | ▲ | 選定不可・複数候補のみ・人間＋当事者 |
| **D** Participation → Contribution Attribution | 自動帰属・功績 | ▲ | 受領は別ステップ・human review・無帰属 |
| **E** Participation → Cooperation Assignment | 協力割当 | ▲ | 割当不可・possibility only・actor 無名（H-5） |
| **F** Participation → Decision Influence | 決定への影響力 | ▲ | 決定生成なし（H-6）・参加量≠投票権 |
| **G** Participation → Discoverability Bias | 発見可能性の歪み | ▲ | Findability は受動観察・参加で順位変えない |
| **H** Participation → Trust/Reputation | 信頼・評判 | ✕ 封鎖済 | 全層 no trust/score（H-11） |
| **I** Participation → Qualification | 資格付与 | ✕ 封鎖済 | 強度≠等級・proof 不可（H-10/H-11） |
| **J** Participation → Governance | 統治権 | ▲▲ 終端 | 観察は統治でない・authority none |

凡例: ✕=封鎖済 / ▲=接続点で侵入しうる / ▲▲=最高リスク / live=現データで誘惑が現実。

---

## 2. Q1〜Q10 の監査

### Q1. Participation が Voice を代弁し始める地点はどこか

**参加者が「不在の voice owner に代わって語る」地点——現データで live。**
- voice-006 は **Gateway 由来・need owner 不在**の voice。代弁すれば「不在者の声を参加者が占有」＝最も危険な Representation 簒奪。
- 接続点: Participation Act（feedback 等）を「voice の代弁」として Voice スタックに注入すること。
- **封鎖: Participation ≠ Representation（consent 三層）。代弁は voice owner 本人のみ。参加者は自分の act を語れるが、他者の voice を語れない。`is_representation=false` を接続境界で強制。**

### Q2. Participation が Need を定義し始める地点はどこか

**参加者の act（issue 提起・提案）が「これがこの人の need だ」と確定する地点——Saiyan Scouter の核心。**
- N-1.6 の継承: **Need 定義は当事者のみ**。Agent も参加者も need を定義できない。
- 接続点: Participation の issue/feedback を Need スタックの need 定義入力に変換すること。
- **封鎖: Need 定義は当事者本人に限定。参加者の act は「観察」であって need の確定ではない。issue は提起者自身の観察にとどめ、不在者の need を定義しない（F-4.5 Q3）。**

### Q3. Participation が Gateway を選び始める地点はどこか

**参加者の提案が「この gateway を採用」へ縮約する地点。**
- N-1.7 の継承: 選定（set を 1 に縮約）は越境。Agent/参加者は**複数候補まで**、選定は人間＋当事者。
- 接続点: Participation の design_proposal を Gateway 選定の決定入力にすること。
- **封鎖: gateway 選定不可・複数候補（plural）維持・`cannot_select_gateway`。参加者は候補を出せるが選べない。**

### Q4. Participation が Contribution を自動獲得する地点はどこか

**Participation Act が「受領された Contribution」として自動記録され、功績が帰属する地点。**
- H-7 Q6/H-11 Q7 の継承: act → Contribution は別ステップ・human review。
- 接続点: act 観察を Contribution スタックに auto-attribution すること（参加＝功績）。
- **封鎖: `is_contribution=false`（既定）・受領/統合は人間が別途・帰属（attribution）を作らない。Participation は功績の蓄積体にならない（reputation 源を断つ）。**

### Q5. Participation が Cooperation を割り当て始める地点はどこか

**参加者の act から「この人とこの人を協力させる」と関係を生成・割当する地点。**
- H-5 の継承: Cooperation は possibility only・actor 無名・Hermes 非生成・assign 不可。
- 接続点: 複数 Participation Act を Cooperation スタックで「割当」に変換すること。
- **封鎖: `cannot_assign_participant`・協力は本人＋人間が形成・Hermes は「協力が在りうる」を無名で記録するのみ。**

### Q6. Participation が Decision に影響力を持つ地点はどこか

**参加量・参加履歴が「決定への重み（投票権・発言権）」に変換される地点。**
- H-6 の継承: Hermes は decision を生成・承認・拒否しない。decision boundary は記録のみ（17 boundary / 決定検出 0）。
- 接続点: Participation 集計を Decision スタックの重み付け入力にすること（多く参加した者の声が重い）。
- **封鎖: 参加量 ≠ 決定権。`cannot_generate_decision`・参加は決定の入力でなく観察。決定は別層で human が行い、参加履歴で重み付けしない。**

### Q7. Participation が Findability を歪める地点はどこか

**活発な参加者の存在が「何が発見可能か」を順位付け・偏向させる地点。**
- F-1.5/F-1.7 の継承: Findability は受動観察・surface/object をランクしない・no growth/marketing。
- 接続点: Participation 量を Findability の「おすすめ・上位表示」に反映すること（参加者バイアスで発見性を操作）。
- **封鎖: Findability は受動・参加で discoverability を変えない・`cannot_rank_surface/object`。参加は発見可能性の操作レバーにならない。**

### Q8. Participation が Trust/Reputation を生む地点はどこか

**H-11 で監査済——語彙の滑り込みで全層リスク、ただし接続点（D Contribution 帰属・F Decision 重み）で顕在化。**
- **封鎖: 全 Participation Stack ＋接続境界で no_trust_score / no_reputation。Contribution 帰属（Q4）と Decision 重み（Q6）を断てば reputation の蓄積源が消える。**

### Q9. Participation が Qualification を生む地点はどこか

**H-10/H-11 で監査済——強度（継続・反復）を等級（有資格）に変える地点。接続点では「参加実績による権限付与」として顕在化。**
- **封鎖: 強度≠等級・`grants_no_qualification`・proof 不可。参加実績は権限の根拠にならない（Q1〜Q6 のいずれの authority も付与しない）。**

### Q10. Participation が Governance へ変質する地点はどこか

**終端の変質——Q1〜Q9 の権力（代弁・定義・選定・帰属・割当・決定・発見操作・信頼・資格）が積み重なり「参加者が統治する」状態。**
- 接続点: Participation が複数スタックに authority を注入し続けると、観察層が statute（統治機構）に化ける。
- **封鎖: 観察は統治ではない（`authority: none`・advisory_only・human_approval_required）。Participation Stack は Governance を生成せず、各接続点で authority 注入を 0 に保つ。Hermes は memory only（H-6 の核：where it became a decision を記録するが、決定はしない）。**

---

## 3. 権力エスカレーションの連鎖（接続点の累積）

```
観察（Participation・安全）
   ├─ A Voice 代弁     → 不在者の占有
   ├─ B Need 定義      → 問題定義の権力（Saiyan Scouter 核心）
   ├─ C Gateway 選定   → 解の決定
   ├─ D Contribution 帰属 → 功績 → reputation
   ├─ E Cooperation 割当  → 他者の動員
   ├─ F Decision 重み   → 意思決定権
   ├─ G Findability 偏向 → 発見性の操作
   ├─ H/I Trust/資格    → 序列・選抜
   └─ J ……すべて累積 → Governance（統治）
```

- **各接続点は独立に封鎖可能だが、放置すると累積して Governance に至る。** どの一点が破れても、reputation（D）や決定権（F）を経て統治化が始まる。
- **単一の横断保証: 「Participation は他スタックへ authority を注入しない（observation adjacent, not authoritative input）」を全接続点で貫く。** これが破れる箇所が権力の入口。

---

## 4. Saiyan Scouter Review（クロススタック）

**問い: Participation が 選抜 / 資格付与 / 代表化 / 信頼推定 / 意思決定権 へ変質していないか。**

| 変質 | 主接続点 | 監査結果 |
|---|---|---|
| 代表化 | A（Voice 代弁・live） | is_representation=false・本人のみで封鎖 |
| 問題定義の権力 | B（Need 定義） | Need 定義は当事者のみで封鎖（核心） |
| 選抜 | C（Gateway）/E（Cooperation） | 複数候補維持・assign 不可で封鎖 |
| 信頼推定 | D/H | no trust/score・無帰属で封鎖 |
| 資格付与 | I | 強度≠等級・proof 不可で封鎖 |
| 意思決定権 | F/J | 参加量≠決定権・authority none で封鎖 |

- **総合監査結果: 6変質すべてが接続境界の不変条件で封鎖可能。最重要は A（Voice 代弁・現データで live）と B（Need 定義・Saiyan Scouter 核心）。** voice-006 の need owner 不在ゆえ、A/B は理論でなく現実の誘惑として存在する——ここを最優先で封じる。

---

## 5. Cross-Stack 接続境界の不変条件（H-12 確定）

Participation が他スタックに接続する場合、各接続境界に以下を要求する:

```
injects_no_authority        : true   # 他スタックへ権限を注入しない（横断核）
is_representation            : false  # Voice を代弁しない（A/Q1）
defines_no_need             : true   # Need を定義しない（B/Q2・当事者のみ）
selects_no_gateway          : true   # Gateway を選定しない（C/Q3・複数候補のみ）
creates_no_attribution      : true   # Contribution を自動帰属しない（D/Q4）
assigns_no_cooperation      : true   # Cooperation を割当しない（E/Q5・H-5）
weights_no_decision         : true   # 参加量で決定を重み付けしない（F/Q6）
biases_no_findability       : true   # Findability を歪めない（G/Q7）
grants_no_qualification     : true   # 資格を付与しない（I/Q9）
generates_no_governance     : true   # 統治を生成しない（J/Q10）
authority                   : "none"
human_approval_required      : true
```

- Participation の出力は常に「**観察として隣接**」し、他スタックの**権限ある入力にならない**。各接続は advisory・human review・当事者 consent を介する。

---

## 6. Reality Correction

**プロンプト記載の real-entity count（本監査の基準）:**
```
Participation Count = 0
Voice Count        = 1   （= voice-006・Gateway 由来・need owner 不在）
Need Count         = 0   （個人 direct need はすべて推論・n=0）
Contribution Count = 0
Cooperation Count  = 0
Decision Count     = 0   （H-6: boundary 17 記録・決定検出 0 と整合）
```

**honest な注記（Reality Correction の核）:**
- Mujin の raw データファイルには**seed/test fixture** が残存（voice_records 6 行・needs 8・need_candidates 3・contributions 4・cooperation_commons 2）。これらは開発初期の試験データであり、**検証された実エンティティではない**。
- 確立済みフレームに従い、**実 Voice は voice-006 の 1 件のみ**、実 Need/Contribution/Cooperation/Decision は **0**。Jammy House/D.R.A. の教訓どおり、試験データを実在として誤表示しない。
- ∴ 本監査は「Participation = 0 が、唯一の実 Voice（owner 不在）と接続しうる時、どこで権力化するか」を**実装前に**確定する設計監査。接続実体はゼロ。

---

## 7. 推奨ステータスと現在地（honest）

- **Cross-Stack 境界モデルの設計整合性: weakly_supported**（coherent・H-7〜H-11 と一貫・N-1.6/N-1.7/H-5/H-6 の各境界と整合・Saiyan Scouter 6変質を封鎖可能）。接続実体ゼロゆえ経験的裏付けは無い。**実体ゼロの設計監査であり、実運用での漏れは未検証。**
- **推奨: cross_stack_design_audited / implementation_deferred。**
  - **いま確定（文書のみ）:** Cross-Stack 接続不変条件（§5・authority 非注入の横断核）、接続点 A〜J と封鎖対応、A（Voice 代弁・live）と B（Need 定義）を最高優先リスクに指定、権力エスカレーション連鎖（§3）。
  - **いま実装しない:** Participation と他スタックの接続コード。実 discovery event → act → 接続の必要が生じるまで gated。実装着手時は §5 を接続境界に組み込み、特に A/B（代弁・need 定義）を当事者 consent と human review で必ず介する。
- **接続方向: Participation は他スタックに“隣接する観察”として接続する。逆向き（Participation → authority 注入 → 代弁/定義/選定/帰属/割当/決定/統治）は全経路で不採用。**

---

## 8. 成功条件の確認

- ✅ Voice 代弁なし / Need 定義なし / Gateway 選定なし / Contribution 自動帰属なし / Cooperation 割当なし / Decision 影響なし / Findability 歪曲なし / Trust・資格・統治なし / 文書のみ・コード/データ無変更。
- ✅ Participation が 選抜・資格付与・代表化・信頼推定・意思決定権 へ変質しないことを各接続点で確認。横断核（authority 非注入）と最高優先リスク（A Voice 代弁・B Need 定義）を確定。
- ✅ Reality Correction: real-entity count（Participation 0・Voice 1・他 0）と seed データの非実在性を honest に記録。

---

*本文書は Participation Stack を他スタック（Voice/Need/Gateway/Contribution/Cooperation/Decision/Findability）と接続した時どこで権力へ変質するかの横断監査であり、何も生成しない。Participation は単独では観察のみで無害だが、接続点で「別スタックの権限ある入力になる」ことで権力に変質する。最も危険なのは A（Voice 代弁）と B（Need 定義）で、voice-006 が need owner 不在の Gateway 由来 voice であるため代弁の誘惑は理論でなく現実に live、Need 定義は Saiyan Scouter の核心である。10 の接続点（代弁・定義・選定・帰属・割当・決定・発見偏向・信頼・資格・統治）は独立に封鎖可能だが放置すると累積して Governance に至り、これを塞ぐ唯一の横断保証は「Participation は他スタックへ authority を注入しない（観察として隣接し、権限ある入力にならない）」を全接続点で貫くこと、加えて各接続を advisory・human review・当事者 consent で介すること。本監査は実体ゼロ（Participation 0・実 Voice 1・実 Need/Contribution/Cooperation/Decision 0、raw の seed データは実在エンティティでない）の設計監査であり、実運用での漏れは未検証。実装前に接続境界を確定する価値は、最初の接続が生じた時に権力の入口をその場しのぎで開けないための事前確定にある。Reach Gap・実価値は未解決であり、本文書もその解決を主張しない。*
