# Claim Falsification Review

- **Status:** 観察レビュー（反証条件の整理）。実装・接触・登録・Need 作成なし。観察のみ。コード/データ無変更。文書のみ。
- **Date:** 2026-06-13
- **対象:** X-9 の Claim-1〜5
- **前提:** [`CLAIM_AUDIT_REVIEW.md`](CLAIM_AUDIT_REVIEW.md)（status: 1=challenged, 2/3/5=unknown, 4=weakly_supported）

> 中心: **何が起きれば、その Claim を否定すべきか。**
> 反証条件を持たない Claim は仮説ではなく信仰。本レビューは各 Claim を反証可能にする——できないものは「反証不能」と明記する。

---

## 1. Claim 別の反証整理

### Claim-1 — Reach Gap を縮められる
1. **Claim:** Mujin は未到達の個人への到達を増やせる。
2. **Current Evidence:** なし。
3. **Counter Evidence:** 構造的（gap-2 で作動・gap-1 でない／X-2.6）／唯一の実 Voice は仲介者／X-8（供給側価値で Reach を広げない）。
4. **Falsification Condition:** Mujin が findable になり期間 T 稼働しても、Mujin 経由で（他では助からなかった）未到達個人がゼロなら contradicted。**だが致命的問題: Mujin は gap-1 へ到達する機構を持たない（アウトリーチは禁止＝Saiyan Scouter 未実装）。試行機構が無いため、この Claim は現設計では試せない。**
5. **Observation Needed:** 個人が Mujin を**自力で見つけて**現れること（Mujin が探さずに）。これが永遠に起きなければ、反証も支持もできない。
6. **Current Status:** **challenged（かつ現設計では反証不能）**

### Claim-2 — Gateway 間協調を増やせる
1. **Claim:** Mujin は繋がっていない複数 Gateway を協調させられる。
2. **Current Evidence:** なし（創設 Claim・X-8 で最も擁護可能）。
3. **Counter Evidence:** 協調実績ゼロ／既存 referral 網と競合。
4. **Falsification Condition:** 繋がっていない ≥2 Gateway を Mujin に持ち込んだ実ケースが R 件あり、いずれも（Mujin 無しでは起きなかった）協調を生まなければ contradicted。
5. **Observation Needed:** 未協調の複数 Gateway が Mujin に現れる実ケース。
6. **Current Status:** **unknown（反証可能）**

### Claim-3 — 協力者同士を繋げられる
1. **Claim:** Mujin は互いを知らない協力者を繋げられる。
2. **Current Evidence:** 機構実装済み・実ゼロ。
3. **Counter Evidence:** 実 Cooperation ゼロ。
4. **Falsification Condition:** 互いを知らない複数協力者の実ケースが K 件あり、Mujin がいずれも（独自に）繋げなければ contradicted。
5. **Observation Needed:** 未協調の協力者が Mujin に現れる実ケース。
6. **Current Status:** **unknown（反証可能）**

### Claim-4 — Reality Feedback が循環する
1. **Claim:** feedback → 次の Voice の循環が回る。
2. **Current Evidence:** テスト機構は実証（D-8）。
3. **Counter Evidence:** 実循環ゼロ。
4. **Falsification Condition:** 実データで Voice→…→feedback→新 Voice が試行され、循環が繰り返し閉じなければ challenged→contradicted。**ただし一度も試行されなければ unknown のまま滑る。**
5. **Observation Needed:** 実データでの一周。
6. **Current Status:** **weakly_supported（機構）/ unknown（実循環）**

### Claim-5 — TTFR を短縮できる
1. **Claim:** Mujin は救済までの時間を短縮できる。
2. **Current Evidence:** なし（時計未始動）。
3. **Counter Evidence:** TTFR-P 一貫してゼロ。
4. **Falsification Condition:** 「短縮」には**比較基準（Mujin 無しの所要時間）が要る**。基準も Mujin 測定も無いため、現状この Claim は**反証不能**。基準＋Mujin 測定が揃い、Mujin が短くなければ contradicted。
5. **Observation Needed:** 測定可能な実救済1件＋反実仮想の基準。
6. **Current Status:** **unknown（基準が無い間は反証不能）**

---

## 2. 必須観察

### unknown と challenged の違い
- **unknown:** まだ見ていない。試行も反証もゼロ。データの不在。
- **challenged:** 見た上で旗色が悪い。反対の構造的論拠 or 実失敗がある（決定的否定ではない）。
- **要点:** unknown =「試していない」、challenged =「試した/論じた結果、疑わしい」。Claim-1 が challenged なのは、試行ゼロでも**構造的論拠（X-2.6, X-8）が能動的に反対する**から。Claim-2/3/5 は何も試していないので unknown。

### 何回失敗したら challenged になるか
- 厳密な閾値はないが目安: **1つの明確な構造的論拠**、または**公正な条件下での実失敗 2〜3件**で challenged。
- Claim-1 は実失敗 0 でも構造論拠だけで challenged に達した（反証不能性が論拠）。

### 何回失敗したら contradicted になるか
- contradicted = 疑いでなく**反駁**。不可能性の証明、または公正条件下の**多様な実失敗の集積**（claimの機構が十分な機会を得て一度も働かなかった）が要る。
- **重要: n=0（実試行ゼロ）では、どの Claim も contradicted に到達できない。** 不在では反駁できない。contradicted は実際に試して繰り返し失敗して初めて。

### 実証可能性（反証可能性）
| Claim | 反証可能か |
|---|---|
| 1 Reach Gap | **不可**（到達機構が禁止・試せない） |
| 2 Gateway 協調 | 可（実ケースを持ち込めば） |
| 3 協力者接続 | 可 |
| 4 Feedback 循環 | 可（一周を試せば） |
| 5 TTFR 短縮 | **基準が無い間は不可** |

### 永遠に unknown のまま残る危険（中心の危険）
- **試されない Claim は無期限に unknown に留まり、それが隠れ家になる。** 体系は未証明の価値を信じ続けながら、一度も反証されない——**反証不能の信仰の罠**。
- 最も鋭いのは Claim-1（設計上試せない）と Claim-5（基準が無い）。
- **解毒剤:** 反証条件＋試行回数/期限を**事前にコミット**すること。「N 回試して一度も働かなかった」が unknown→challenged→contradicted を駆動する。コミットが無ければ、Claim は仮説でなく信仰。
- **Active Suspension の核心との接続:** 保留が正当なのは「いつ・何で否定するか」を持つ場合のみ。それが無い保留は、放置（永遠の unknown）である。

### Reach Gap Claim の否定条件
- Claim-1 の唯一の正直な否定条件: **Mujin が findable になり稼働しても、自力で到達した個人が（他では助からなかった形で）誰も助からない**。
- だが現状 Mujin は findable でも稼働でもないため、**否定条件が発火しない＝永遠の unknown に最も近い**。**設計が反証を不可能にしている**（アウトリーチ禁止の代償）。

### Cooperation Claim の否定条件
- Claim-2/3 の否定条件: **未協調の助け手の実ケースを Mujin に持ち込み、Mujin が独自には一件も繋げない**——これが繰り返されれば contradicted。
- **これは到達可能な否定条件。** だから X-9 が「次に検証すべき」と指したのは Cooperation Claim。**反証可能性こそが、それを次に試す理由。**

### Mujin の最小生存条件
- **Mujin が継続に値する最小条件 = 反証可能な価値 Claim（2/3/4）の少なくとも一つが supported になること**——即ち、Mujin 無しでは起きなかった協力/一周/救済が**実在で一件**示されること（限界救済 > 0 or 限界協調 > 0）。
- 公正な試行の後、反証可能な全 Claim が contradicted なら、Mujin に実証価値は無く、評価フレーム（救済能力）上、生存は正当化されない。
- **最深の含意: 最小生存条件は実ケースを要し、実ケースは Mujin が到達可能であることを要する。** ゆえに Mujin の生存は**自らの到達可能性で gated される**（X-8 の価値 gate と同一）。Mujin が永遠に到達不能なら、永遠に unknown のまま生存条件を満たせない。

---

## 3. 統合 — 試行可能性 vs 信仰

> **本レビューが暴いた選択:** Mujin は (a) 実ケースを生む（findable になる・実 Voice を待つ）か、(b) 永遠に反証不能な信仰に留まるか、の岐路にある。

- 反証可能な Claim（2/3/4）は、実ケースさえ流れれば supported/contradicted に決着できる——**それらを試すことが、信仰から仮説への唯一の道。**
- 反証不能な Claim（1, 5）は、設計（到達機構の禁止／基準の不在）が反証を阻んでいる。これらは「未解決として保存」（Reach Gap）するのが正直で、**価値命題として持ち出すべきではない**。
- **Mujin の生存は、反証可能な価値 Claim を一つ supported にできるかにかかる。** それは実ケース、それは到達可能性。**到達可能性が、価値・反証・生存のすべての上流ゲート。**

---

## 4. 観察の限界

- 本レビューは反証条件を定義しただけで、反証を実行していない（実試行ゼロのまま）。
- 反証条件＋試行コミットが無ければ、Claim は unknown のまま信仰化する——その危険を記録したが、解消はしていない。
- Reach Gap は本レビューでも縮まない。むしろ「設計上反証不能」という最も厳しい認識に至った。

---

## 5. やらなかったことの証明

- 実装・接触・募集・寄付・Gateway 登録・Need 登録のいずれも行っていない。
- コード/データ無変更。すべて文書内の観察。

---

*本文書は Claim の反証条件の観察記録であり、実装・接触・登録・Need 作成を含まない。要点: Claim-2/3/4 は反証可能（実ケースで決着可）、Claim-1/5 は現設計で反証不能。最大の危険は永遠の unknown（反証不能の信仰）。Mujin の最小生存条件は反証可能な価値 Claim を一つ supported にすることで、それは到達可能性に gated される。Reach Gap は未解決であり、本文書もその解決を主張しない。*
