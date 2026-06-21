# Phase H-11: Participation Stack Audit

- **Status:** 横断監査（Participation Stack 全層が Actor Profile / Trust / Reputation / Ranking へ変質しないかの検証）。**コード/データ/生成/登録なし。文書のみ。**
- **Date:** 2026-06-20
- **対象:** H-7（Memory）, H-8（Learning）, H-9（Pattern）, H-10（Evidence）
- **前提:** F-3〜F-4.5（Discoverer/Participant/Act の境界）, H-5（Cooperation possibility-only・actor 無名）, H-4（推論開始地点で止まる）, X-4.7/N-1.7（consent 三層・Representation 境界）, Saiyan Scouter 問題

> 中心問い: **Participation Stack 全体は本当に Actor Profile / Trust / Reputation / Ranking System へ変質しないか。**
> 結論先取り: **各層の不変条件は個別には健全だが、変質は「単層の違反」ではなく「層をまたぐ漏れの累積」として起きる。最大の再侵入経路は ①evidence 層の cross-source を actor 名寄せに使う（H-10 Q5）②集計を actor で割る/層別する（H-8）③多 actor を名指しで結ぶ（H-9/H-10 → Cooperation 越境）。これらを塞ぐ唯一の構造的保証は「全層で actor を集計キー/節点/対象に取らない」という単一不変条件の貫通。現状 全 count = 0。**

---

## 0. スタックの構造と「actor 無名」の貫通線

```
[Discovery Event] → [Discoverer] → [Participation Act]
        │
        ▼
H-7 [Memory]    act 単位・評価なし・人単位集約禁止
        ▼
H-8 [Learning]  actor を含まない type/集計（Count/Distribution/type Frequency）
        ▼
H-9 [Pattern]   actor を含まない act type 構造（Sequence/Co-occurrence/反復）
        ▼
H-10 [Evidence] actor を含まない type 構造の観察裏付け（candidate・not proof）
```

- **唯一にして共通の安全条件: 「actor を集計キー・節点・対象・名寄せキーに取らない」が全層を貫く。**
- 変質は単層では起きにくい。**層境界で actor の無名性が一度でも破れると、下流全体が profiling に転ぶ**——だから単層監査（H-7〜H-10）に加え、本 H-11 で**境界の漏れ**を監査する。

---

## 1. 監査マトリクス A〜J（どの層で再侵入しうるか）

| 危険 | H-7 Memory | H-8 Learning | H-9 Pattern | H-10 Evidence | 主防壁 |
|---|---|---|---|---|---|
| **A Actor Identity** | △ discoverer_id 保持 | ▲ actor 別層別で侵入 | ▲ actor を節点化で侵入 | ▲ cross-source 名寄せで侵入 | actor を集計キー/節点/名寄せに取らない |
| **B Trust** | ✕ no_*_score | ✕ trust 学習禁止 | ✕ trust_structure 禁止 | ✕ trust_evidence 禁止 | 全層 no trust/score |
| **C Reputation** | ✕ | ✕ | ✕ | ✕ | 全層 no reputation |
| **D Ranking** | ✕ cannot_rank | ✕ | ✕ | ✕ | 全層 cannot_rank |
| **E Recommendation** | ✕ | ▲ 「優先」推論で侵入 | ▲ 「best 型」で侵入 | ▲ 「証明された根拠」で侵入 | possibility only・human review |
| **F Qualification** | ✕ | ✕ | ▲ 資格鋳型化で侵入 | ▲ 証明→資格化で侵入 | 強度≠等級・proof 不可 |
| **G Auto Contribution** | ▲ 受領自動化で侵入 | — | — | — | is_contribution=false・human review |
| **H Auto Cooperation** | — | — | ▲ 多 actor 結合で侵入 | ▲ 協働裏付けで侵入 | Cooperation 層へ無名委譲・Hermes 非生成 |
| **I Cross-source Linking** | — | ▲ source 別 actor 追跡 | — | ▲▲ **最大リスク**（Q5） | cross-source は type 裏付け専用 |
| **J Participation→Representation** | — | — | — | — | 別 consent・本人のみ（§Q10） |

凡例: ✕=構造的に封鎖済 / △=保持するが無害化済 / ▲=境界が破れれば侵入しうる / ▲▲=最高リスク。

---

## 2. Q1〜Q10 の監査

### Q1. どの層で actor identity が再侵入しうるか

**H-8（actor 別層別）・H-9（actor を節点化）・H-10（cross-source 名寄せ）の3経路。**
- H-7 は discoverer_id を保持するが、それは event 連続のためで、**下流が集計キー/節点/名寄せに使わなければ無害**。
- 再侵入の本質は「discoverer_id を H-8 以降で**識別子として再利用**すること」。
- **封鎖: 全層で actor を集計キー/節点/対象に取らない。discoverer_id は連続トレース専用、集約・分類・突合に使わない。**

### Q2. どの層で trust が再生成されうるか

**原理的にどの層でも、語彙の滑り込みで起きうる。**
- 主要点: H-8（頻度→「信頼できる」）・H-10（複数源観察→「信頼の裏付け」）。
- **封鎖: 全層 no_trust_score / no_reputation_score / contains_trust_*=false。Hermes reviewer の forbidden 語彙（trust/reputation）を Participation 系レコードにも適用。**

### Q3. どの層で reputation が再生成されうるか

**trust と同型（Q2）。** reputation は trust の時間的蓄積。
- 危険点: H-7 の多対1集約（人に蓄積）→ H-8 で「実績」化。
- **封鎖: H-7 の「act 単位・人単位集約禁止」が源を断つ。集約しなければ蓄積（reputation）は生じない。**

### Q4. どの層で ranking が再生成されうるか

**集計値が現れる H-8 以降。** count/frequency に順序を入れた瞬間に ranking。
- 危険点: H-8（actor 別 frequency の sort）・H-9（best 型）・H-10（証明強度の sort）。
- **封鎖: 全層 cannot_rank / contains_ranking=false。集計は列挙であって順序でない（type 別カウントは可、序列は不可）。**

### Q5. どの層で recommendation が再生成されうるか

**推論を出す H-8/H-9/H-10。** 「優先」「best」「証明された根拠」が推薦に化ける。
- **封鎖: 全層 possibility only・human_review_required。Hermes は「在りうる」までで止まり、「すべき/推奨」を出さない（H-4 の推論停止と同型）。**

### Q6. Participation が qualification に変質する地点はどこか

**「強度を等級に変える」地点——主に H-9（資格鋳型）・H-10（証明→資格根拠）。**
- F-4.5/H-7 で確定の通り、act は**種類で分類できるが価値で序列化できない**。継続・複数性・反復は**強度**であって**資格**ではない。
- 変質の臨界: 「反復する型 ＝ 有資格者の型」と置くこと。
- **封鎖: 強度≠等級、evidence_is_not_proof、is_actor_pattern=false。資格を導ける proof/score フィールドが存在しない。**

### Q7. Participation が Contribution に自動昇格する地点はどこか

**H-7 の出口（act → 受領）。**
- act を観察した瞬間に「受領された貢献」と記録すると auto-contribution。
- **封鎖: is_contribution=false（既定）・受領/統合は別ステップ・human_review_required。Hermes は act を観察するのみで Contribution を生成しない。**

### Q8. Participation が Cooperation に自動昇格する地点はどこか

**H-9/H-10 で多 actor を結ぶ地点。**
- pattern/evidence が「この人とこの人の協働」を名指しで作ると auto-cooperation。
- **封鎖: links_no_actor=true。多 actor の関係は Participation 層では作らず、Cooperation 層（H-5）へ委譲。そこでも actor 無名・possibility only・Hermes 非生成。**

### Q9. Cross-source が actor linkage に変質する地点はどこか

**H-10（Cross-source Observation）——スタック最大のリスク（▲▲）。**
- cross-source は本来「同じ **type 構造**が複数源で観察された」という裏付け強度。
- 変質: 「同じ **actor** が複数源に現れた」と突合（entity resolution / 名寄せ）した瞬間、分散していた断片が結合し**actor profile が一気に成立**する。これがスタックで最も静かに、最も致命的に起きる。
- **封鎖: cross-source は type 構造の裏付け専用。source も actor も無名。`links_no_actor=true` ＋ source を actor キーに結びつけない。H-11 はこの一点を最優先の監査対象に指定する。**

### Q10. Participation が Representation に変質する地点はどこか

**スタック内ではなくスタックの「外」——参加者が他者を語り始める地点。**
- consent 三層（X-4.7/N-1.7）: Discovery ⊄ Participation ⊄ Representation。参加（自分が寄与）≠ 代表（他者の need を語る/決める）。
- 変質: 多く/長く参加した者を「コミュニティ代表」に滑らせること。これは Participation Stack の不変条件では直接封じられない**別層の境界**。
- **封鎖: is_representation=false を act/participant に明示。Representation は別 consent を要し、原則として当事者本人にのみ属す。Stack はこれを生成せず、境界の存在を記録するにとどめる。**

---

## 3. 変質経路の総括（層境界の漏れ）

```
安全状態:  actor 無名が H-7→H-8→H-9→H-10 を貫通
                              │
   漏れ①: H-8 で actor 別に層別  → identity 再侵入 → trust/reputation/ranking 連鎖
   漏れ②: H-9 で actor を節点化  → actor pattern → 資格鋳型
   漏れ③: H-10 cross-source 名寄せ → actor profile 一気成立（▲▲ 最大）
   漏れ④: H-7 出口で受領自動化   → auto-contribution
   漏れ⑤: H-9/H-10 で多 actor 結合 → auto-cooperation
   漏れ⑥: stack 外で長期参加→代表 → representation 簒奪
```

- **単一の構造的保証: 「actor を集計キー/節点/対象/名寄せキーに取らない」を全層で貫けば、①②③⑤は同時に塞がる。**
- ④は `is_contribution=false`＋human review、⑥は `is_representation=false`＋別 consent で個別に塞ぐ。
- **∴ Stack の安全は「各層の不変条件」＋「actor 無名の貫通」＋「2つの自動昇格禁止（Contribution/Cooperation）」＋「代表境界の明示」の4点セットで初めて成立する。**

---

## 4. Saiyan Scouter Review（スタック横断）

**問い: Stack 全体を通して 選抜 / 資格付与 / 信頼推定 / 人物評価 / 序列化 / 代表化 が再発していないか。**

| 再発形態 | 主経路 | 監査結果 |
|---|---|---|
| 選抜（recommendation） | H-8/H-9/H-10 の「優先/best/推薦」 | possibility only・human review で封鎖 |
| 資格付与（qualification） | 強度→等級（H-9/H-10） | 強度≠等級・proof 不可で封鎖 |
| 信頼推定（trust） | 語彙滑り（全層） | no trust/score 貫通で封鎖 |
| 人物評価（profile） | actor 無名破れ（H-8/H-9/H-10） | actor を集計キー/節点/名寄せに取らないで封鎖 |
| 序列化（ranking） | 集計の sort（H-8 以降） | cannot_rank 貫通で封鎖 |
| 代表化（representation） | stack 外・長期参加 | is_representation=false・別 consent で封鎖 |

- **総合監査結果: 6形態すべてが、設計上の不変条件で封鎖可能。ただし封鎖は「各層の条件」だけでは不十分で、「層境界の漏れ（特に cross-source 名寄せ）」を塞ぐ横断不変条件が必須。** H-11 はこの横断条件を Stack の必須要件として確定する。

---

## 5. Stack 不変条件（H-11 確定・全層共通）

実装する場合、全 Participation Stack レコードに以下を要求し、Hermes reviewer が横断検査する:

```
actor_not_used_as_key   : true   # 集計キー/節点/対象/名寄せに actor を取らない
contains_actor_profile  : false
contains_trust_score    : false
contains_reputation     : false
contains_ranking        : false
contains_recommendation : false
grants_no_qualification : true
is_contribution         : false  # 受領は別ステップ・human review
is_cooperation          : false  # 多 actor 結合は Cooperation 層へ無名委譲
is_representation        : false  # 代表は別 consent・本人のみ
cross_source_links_actor: false  # cross-source を actor 名寄せに使わない（▲▲）
human_review_required    : true
```

- 禁止語彙（reviewer 横断適用）: trust, reputation, ranking, rank, score, qualification, recommend, recommended, priority, best, profile, identity（actor 文脈）, entity resolution, dedup（actor 文脈）。

---

## 6. Reality Correction

```
participation_memory_count   = 0
participation_learning_count = 0
participation_pattern_count  = 0
participation_evidence_count = 0
```

- 構造的帰結: `evidence ≤ pattern ≤ learning ≤ memory ≤ act ≤ participant ≤ discoverer ≤ discovery_event = 0`。
- 現状、Stack を流れる実体は全層ゼロ。**監査対象の実データは存在せず、0件は失敗ではなく観察結果。**
- Stack 全体を実装前に監査する価値: 最初の act が流れ込んだ時に、**層境界の漏れ（特に cross-source 名寄せ）をその場しのぎで開けないための事前確定**。

---

## 7. 推奨ステータスと現在地（honest）

- **Participation Stack の設計整合性: weakly_supported**（coherent・H-7〜H-10 と一貫・consent 三層と整合・Saiyan Scouter 6形態を封鎖可能）。実データ全層ゼロゆえ経験的裏付けは無い。**監査自体は「実体ゼロの設計監査」であり、実運用での漏れは未検証**——この限界を明記する。
- **推奨: stack_design_audited / implementation_deferred。**
  - **いま確定（文書のみ）:** Stack 不変条件（§5・actor 無名の横断貫通＋2自動昇格禁止＋代表境界）、変質6経路と封鎖対応（§3/§4）、cross-source 名寄せを最高リスクとして指定。
  - **いま実装しない:** Participation Stack の生成コード（H-7〜H-10 のいずれも）。実 discovery event → act が現れるまで gated。実装着手時は §5 の横断不変条件を Hermes reviewer に組み込み、特に cross-source の actor 名寄せ検査を必須とする。
- **接続方向: `Act → Memory → Learning → Pattern → Evidence`（全層 actor 無名）は正しい。逆向き（evidence/pattern/learning から actor を profile/trust/rank/推薦/代表化）は全経路で不採用。**

---

## 8. 成功条件の確認

- ✅ Actor Profile 無し / Trust System 無し / Reputation System 無し / Ranking System 無し / Auto Contribution 無し / Auto Cooperation 無し / Cross-source actor linkage 無し / Representation 簒奪無し / 文書のみ・コード/データ無変更。
- ✅ Stack 全体を通して 選抜・資格付与・信頼推定・人物評価・序列化・代表化 が（設計上）再発しないことを確認。横断不変条件と最高リスク（cross-source 名寄せ）を確定。
- ✅ Reality Correction: 全層 count = 0 を正しい観察結果として記録。

---

*本文書は Participation Stack（H-7 Memory → H-8 Learning → H-9 Pattern → H-10 Evidence）全層が Actor Profile / Trust / Reputation / Ranking System へ変質しないかの横断監査であり、何も生成しない。変質は単層の違反ではなく層境界の漏れの累積として起き、最大の再侵入経路は cross-source 観察を actor 名寄せ（entity resolution）に転用すること——これが分散した断片を結合し actor profile を一気に成立させる、スタックで最も静かで致命的な経路である。これを含む6つの変質経路（identity 再侵入・trust/reputation 再生成・ranking・auto-contribution・auto-cooperation・representation 簒奪）は、「actor を集計キー/節点/対象/名寄せに取らない」という単一の横断不変条件を全層で貫き、2つの自動昇格（Contribution/Cooperation）を禁止し、代表境界（is_representation=false・別 consent・本人のみ）を明示することで、設計上は封鎖可能である。ただし本監査は実体ゼロの設計監査であり、実運用での漏れは未検証。現状 全層 count = 0 は失敗ではなく観察結果であり、実装前に Stack 全体を監査する価値は、最初の act が流れ込んだ時に層境界の漏れをその場しのぎで開けないための事前確定にある。Reach Gap・実価値は未解決であり、本文書もその解決を主張しない。*
