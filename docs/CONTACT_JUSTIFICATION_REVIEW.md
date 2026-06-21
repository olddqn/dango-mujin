# Contact Justification Review

- **Status:** 観察レビュー。X-6 の J2「なぜ今」・J3「なぜ Mujin」の弱さを検討する。**実際の接触なし。** Gateway 登録・Need・Contribution・Cooperation・Feedback 生成なし。コード/データ無変更。文書のみ。
- **Date:** 2026-06-13
- **対象:** `voice-006`（JAR / https://www.refugee.or.jp/support/ ）
- **前提:** [`FIRST_GATEWAY_CONTACT_PROTOCOL_REVIEW.md`](FIRST_GATEWAY_CONTACT_PROTOCOL_REVIEW.md)（X-6: 接触は consent を求める層と、接触自体を正当化する層に分かれる。J2/J3 が弱い）

> 中心問い: **接触が consent を必要とする前に、接触そのものを正当化できるのか。**
> 観察のみ。結論を固定しない。

---

## 0. 「接触の正当化」と「consent」は別問題である（最重要の分離）

| | 接触の正当化 | Consent |
|---|---|---|
| 誰の問題か | **接触する側（Mujin）** の問題 | **接触される側（JAR）** の問題 |
| 問い | なぜ働きかけるのか（なぜ今・なぜ Mujin） | 働きかけられた相手が同意するか |
| 論理的順序 | **前段** | 後段 |

- **正当化は consent より前にある。** 接触の理由が無ければ、consent を求める資格もない（誰も必要としていない許可を求めるために相手の時間を使うのは、丁寧でも正当化されない）。
- X-6 では両者がやや混在していた。X-6.5 で分離: **consent を完璧に尊重する接触（X-6 Case B）でも、「なぜ今・なぜ Mujin」が空なら正当化されない。**

---

## 1. 4ケースの記録

```json
[
 {
  "case": "A — 今すぐ接触する",
  "why_now": "JAR の要請は常設で引き金がない。『今』は Mujin の process 段階のみ。",
  "why_mujin": "個人は JAR に直接寄付できる。Mujin の付加価値は未証明(n=0)。",
  "demand_driven": false,
  "agenda_driven": true,
  "contact_justified": false,
  "scouter_risk": "medium",
  "human_comment": "接触が需要でなく Mujin の段階で駆動される。v2『なぜあなたに接触したのか』に答えられない。"
 },
 {
  "case": "B — 個人 Voice が現れるまで待つ",
  "why_now": "実在の個人(種類A)の需要が『今』を固定する。需要駆動になる。",
  "why_mujin": "『あなたの提供するものを必要とする人がいる』という具体理由が立つ。",
  "demand_driven": true,
  "agenda_driven": false,
  "contact_justified": true,
  "scouter_risk": "low-medium（個人の Need は本人が表明・外部定義しない条件で）",
  "human_comment": "プロジェクトの目的(救済能力)に最も整合。ただし種類A Voice は安全ゲートで出にくい(X-2.6)→待ちが長期化しうる。"
 },
 {
  "case": "C — Gateway 側から反応が来るまで待つ",
  "why_now": "JAR 自身の働きかけが引き金。JAR が Mujin に接触/関心を示す。",
  "why_mujin": "JAR が Mujin を選んだ。接触の向きが逆転し『なぜあなたに接触したのか』が消える。",
  "demand_driven": true,
  "agenda_driven": false,
  "contact_justified": true,
  "scouter_risk": "very low（応答は働きかけではない）",
  "human_comment": "最も clean。ただし JAR は Mujin を知らない→反応の前提として Mujin の可視性が要る(別の問題)。"
 },
 {
  "case": "D — Mujin が独自価値を示せるまで待つ",
  "why_now": "Mujin が実際に価値(例: 誰かの一周を成立)を示したことが引き金。",
  "why_mujin": "『Mujin は X をした、ゆえに Y を提供できる』と J3 に直接答えられる。",
  "demand_driven": false,
  "agenda_driven": true,
  "contact_justified": true,
  "scouter_risk": "low（価値は claim でなく実在であること・Reality Correction）",
  "human_comment": "J3 を直接埋める。だが独自価値は現在 n=0。価値を生むには接続が要る→鶏卵問題に注意。"
 }
]
```

---

## 2. 8観点の比較

| 観点 | A 今接触 | B 個人 Voice 待ち | C Gateway 反応待ち | D Mujin 価値待ち |
|---|---|---|---|---|
| 1 なぜ今 | Mujin process のみ（弱） | 実在個人の需要（強） | JAR の発意（最強） | 実証価値 |
| 2 なぜ Mujin | 未証明（弱） | 「必要とする人がいる」 | JAR が Mujin を選択 | 「Mujin が X をした」 |
| 3 需要駆動か | ✗ | ✅（個人） | ✅（Gateway） | △（価値駆動） |
| 4 agenda 駆動か | ✅ | ✗ | ✗ | △（Mujin 発だが実質あり） |
| 5 説明可能な接触か | ✗ | ✅ | ✅（接触すら不要） | ✅ |
| 6 Saiyan Scouter Risk | medium | low-medium | very low | low |
| 7 TTFR-G への影響 | 薄い＋agenda リスク | 正当化付きで可能 | clean に可能 | 可能 |
| 8 TTFR-P への影響 | **ゼロ** | 前進しうる | 中立 | 中立〜正 |

---

## 3. 必須観察

- **「接触の正当化」と「consent」は別問題か:** **別問題。** 正当化は接触する側・前段、consent は接触される側・後段（§0）。
- **なぜ今なのか:** A は Mujin の段階でしか答えられない。B/C/D は実在の何か（個人需要/JAR 発意/実証価値）に固定できる。**待つほど『今』が実在に固定される。**
- **なぜ Mujin なのか:** A は未証明。C で最も強く答えられる（JAR が選ぶ）。
- **接触が需要ではなく process に駆動されていないか:** **A はまさに process 駆動**。これが J2/J3 の弱さの正体であり、Saiyan Scouter v2 の再出現。
- **実在の Voice を増やす方が先ではないか:** **YES。** TTFR-G/TTFR-P 双方のボトルネックは Gateway 接触でなく実在ケース。Voice を増やすことが、将来の接触を需要駆動（B）にする唯一の道。
- **Gateway Contact を急ぐことが TTFR に本当に寄与するか:**
  - TTFR-G: せいぜい薄い一周＋agenda リスク（X-4.5/4.6）。
  - TTFR-P: **ゼロ**（個人は gap-1 の奥）。
  - → **急ぐ価値はない。**
- **Saiyan Scouter v2 の問いとの関係:** 「なぜあなたに接触したのか」に答えられない接触は v2 が禁じたもの。B/C/D は**接触前に答えを生成する**方法。C は問いを消す（相手が来る）。
- **最も安全な次の一歩:** §5。

---

## 4. 保留のコストは誰が払うか（評価フレーム適用）

待つ（B/C/D）は接触を保留するが、その**コストの所在**を追う:
- **Case B 待ち:** コストは未到達の個人に向きうる。だが**今 JAR に接触しても個人は救われない**（TTFR-P 不変）。よって B の保留は、個人を A より悪くしない——**保留は個人に追加コストを課さない**。
- **Case C/D 待ち:** コストは主に Mujin の進捗で、誰かの需要ではない。
- **結論:** Gateway 接触の保留は**人的コストがほぼゼロ**。待つことは先延ばしではなく、真に安全。誰も「Mujin が JAR に連絡しなかったから」悪化しない。

---

## 5. 暫定結論と最も安全な次の一歩

- **今接触する（A）は正当化されない。** J2/J3 の弱さは実在し、consent より前段の正当化が空のまま。
- **最も安全な次の一歩は「接触しないこと」。** Source/Reference に留まり（X-5）、**将来の接触を需要駆動に変える作業**に投資する:
  1. **実在の Voice を増やす**（特に種類A 個人 Voice が安全に現れる経路の観察）→ Case B を可能にする。
  2. **Mujin を findable にする**（JAR が見つけて発意できる状態）→ Case C を可能にする。
  3. **実証価値を作る**（小さな実一周）→ Case D を可能にする。
- B/C/D は排他でなく、**いずれかが発火するまで接触しない**のが最善姿勢。発火を早める作業（上記1〜3）が、Gateway 接触を急ぐより TTFR に資する。
- **核心の対応:** 正当化なき接触を避ける規律は、**不在の個人の Need を定義しない規律と同型**——「自らの process のために、相手（不在/未相談）に働きかけない」。Contact Justification は問題定義権力の抑制の outreach 版。

---

## 6. やらなかったことの証明

- Gateway Contact を実施していない（メール/フォーム/SNS/通知なし）。
- Gateway 登録・Need・Contribution・Cooperation・Feedback を生成していない。
- コード/データ無変更。すべて文書内の観察。

---

*本文書は接触の正当化の観察記録であり、実際の接触・登録・生成を含まない。暫定結論: 今接触する正当化は無く、最も安全な次の一歩は接触せず、将来の接触を需要駆動に変える作業（実在 Voice を増やす・findable になる・実証価値を作る）に投資すること。Gateway 接触の保留は人的コストがほぼゼロ。Reach Gap は未解決であり、本文書もその解決を主張しない。*
