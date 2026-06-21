# Gateway Consent Gap Review

- **Status:** 観察レビュー。Gateway Consent が独立概念か、Representation Consent の特殊ケース／複合かを検討する。結論を急がない。新コード・新 ADR・新レイヤなし。Gateway 登録なし。データ無変更。文書のみ。
- **Date:** 2026-06-13
- **対象:** `voice-006`（JAR / https://www.refugee.or.jp/support/ ）
- **前提:** [`GATEWAY_COOPERATION_ELIGIBILITY_REVIEW.md`](GATEWAY_COOPERATION_ELIGIBILITY_REVIEW.md)（X-5: 安全に記録できるのは Source/Reference まで。境界は Reference↓Gateway Candidate の間）, [`REPRESENTATION_BOUNDARY_REVIEW.md`](REPRESENTATION_BOUNDARY_REVIEW.md)（X-4.7: Resource Acceptance ⊄ Participation ⊄ Representation）

> 中心問い: **Gateway Consent は (A) Representation Consent の特殊ケースか / (B) Participation + Representation の複合か / (C) 独立した consent 概念か。**
> 観察として記録し、結論を固定しない。

---

## 1. Gateway Registry は単なる索引ではなく Representation Layer でもある（X-5 の深掘り）

- D-1 で Gateway は「**接続者**（人と Mujin をつなぐ扉）」と定義された。registry への登録は二つを同時に行う:
  - (i) JAR の名を Mujin の構造に **actor として列挙**する（索引機能）。
  - (ii) JAR を「**Mujin に関連づく接続者**」として**性格づける**（表象機能）。
- (ii) があるため、Gateway Registry は中立な索引ではない。**「これは Gateway だ」と記すことは、その組織を Mujin の接続網の一部として表象する。** よって registry は Representation を発生させる。
- 実装上の裏付け: `gateway_registry.jsonl` は `gateway_registration_is_not_certification` を持つ＝「Mujin の主張の制限」は表すが、**被表象組織の同意は表さない**（X-5 §3 の欠落）。索引が中立なら consent は不要なはず——consent が問題になること自体が、これが表象であることの証拠。

---

## 2. Source / Reference と Gateway Candidate の境界

```
   引用（JAR の公開事実を指す）        ┃   表象（JAR を Mujin の actor として性格づける）
   ① Source   ② Reference            ┃   ③ Gateway Candidate ④ Gateway …
   ────────────────────────────────┃────────────────────────────────────
   記録主体=Mujin / 表象される主体=なし ┃   記録主体=Mujin / 表象される主体=JAR
   「JAR がこう公開している」（事実）   ┃   「JAR は Mujin の接続者だ」（性格づけ）
```

- ①② は「JAR の公開した事実を指す」だけ——JAR を Mujin の何かとして**性格づけない**。表象される主体はいない（指されるのは公開 URL という事実）。
- ③ から、Mujin が JAR を「接続者」と**性格づける**。**表象される主体が JAR になる。** ここで consent が必要になる。
- **境界は「事実の引用」と「主体の性格づけ」の間。** これが Reference↓Gateway Candidate に落ちる理由。

---

## 3. 位置別レビュー（6位置 × 観点）

| 位置 | 記録主体 | 表象される主体 | 必要 consent | 現在ある consent | 不足 | 誤読リスク |
|---|---|---|---|---|---|---|
| **① Source** | Mujin | なし（公開事実） | なし | — | なし | 低（提携と誤読され得る程度） |
| **② Reference** | Mujin | なし（公開事実への参照） | なし | — | なし | 低〜中（関係性の示唆） |
| **③ Gateway Candidate** | Mujin | JAR（接続者候補として性格づけ） | **Representation** | 公開役割（受領）のみ | **Representation**（不在） | 中〜高（「載っている=提携/裏書き」） |
| **④ Gateway（実働）** | Mujin | JAR（機能する接続者・かつ参加） | **Representation + Participation** | 公開役割のみ | 両方（不在） | 高（JAR が Mujin の提携先で難民を誘導すると見える） |
| **⑤ Cooperation Participant** | Mujin | JAR（協力の当事者） | **Participation + Representation** | 公開役割のみ | 両方（不在） | 高 |
| **⑥ Represented Actor** | Mujin | JAR（全面代弁） | 完全な代理権 | なし | すべて（不在） | 最高 |

> Saiyan Scouter / Representation Problem との関係（全位置共通）: ③以降は「**不在の主体（JAR）を、その主体が与えていない consent のレベルで構造に書き込む**」。④⑥ では、JAR が「難民を受け入れる接続者」として表象されることで、**routed される個人（難民）への関係**まで Mujin が暗黙に編成し始める——組織表象を経由して個人表象の問題（X-2.6）に再接続する。

---

## 4. Resource Acceptance Consent は Gateway Consent を含意しない

- JAR の公開募集が与えるのは **Resource Acceptance**（資金・人手・難民の来訪を受け入れる）。
- これは「JAR が誰からでも受け取る／難民が JAR に来てよい」を意味するが、「**JAR を Mujin の接続者として性格づけ・列挙してよい**」は意味しない。
- 具体例: JAR が寄付を公開で募る ≠ JAR が「Mujin の Gateway」として registry に載ることへの同意。前者は受領、後者は表象。**Resource Acceptance ⊄ Gateway Consent。**

---

## 5. Gateway Consent と Representation Consent の関係（中心問いの検討）

Gateway であることを consent の言葉で分解する:

| Gateway であることの要素 | 対応する consent | voice-006 での状態 |
|---|---|---|
| (i) 助けを求める個人を受け入れる（接続先になる） | 公開役割の consent（Resource Acceptance 隣接） | **概ね存在**（JAR は公開で難民を受け入れている） |
| (ii) Mujin の registry に接続者として列挙・性格づけされる | **Representation** | **不在** |
| (iii) Mujin の接続フローで実際に接続者として機能する | **Participation** | **不在** |

**観察:**
- **③ Gateway Candidate では、Gateway Consent ≈ Representation Consent の特殊ケース（A）**——「接続者候補」という特定の性格での表象。
- **④ Gateway（実働）では、Gateway Consent ≈ Representation + Participation の複合（B）**——表象に加え、接続者として機能する参加。
- **独立概念（C）に見える理由:** (i) の「routed される個人への接続先になる」という**第三者（個人）に向いた関係**が、純粋な Representation/Participation には収まらない独自の手触りを与える。だが (i) は JAR の公開役割で**概ね既に consent 済み**であり、Mujin が新たに足すのは (ii)(iii)。よって**独立 atom ではなく、既存三層に分解できる**——独自性は (i) の第三者次元にあるが、それは新概念ではなく「最も誤読されやすい部分」。

**暫定回答:** **Gateway Consent は独立概念（C）ではない。** ③では Representation の特殊ケース（A）、④では Representation+Participation の複合（B）として分解できる。独立に見えるのは「接続先＝個人への関係」次元のためだが、それは組織の公開役割で大半が既存 consent であり、Mujin 固有の不足分は Representation（と実働なら Participation）。

---

## 6. 独立概念なら将来どのデータモデルに影響するか／吸収できるか

- **もし独立概念（C）だった場合の影響:** `gateway_registry.jsonl` に専用の `gateway_consent` 状態機械（例: not_requested / requested / granted / withdrawn）が要り、登録フロー自体が組織への問い合わせを前提とする設計に変わる。Cooperation 側にも別途 participation consent が要る。consent 種別が増え、各レコードと UI が複雑化。
- **独立でない（暫定回答）場合の吸収:** **Representation Consent に吸収できる。** gateway/cooperation レコードに `representation_consent`（状態）＋実働 gateway/participant には `participation_consent` を併記すれば足りる。Gateway Consent という別概念を立てず、「表象 consent の一適用」として扱える。(i) の第三者次元は「representation の対象に個人が含まれうる」という注記で捕捉。

---

## 7. 現時点で実装変更しない理由

1. **n=1。** 実在の Gateway 組織が「Mujin に載りたい／載ってよい」と表明した事例はゼロ。consent 機構を仮説の1件の上に建てるのは早計（観察なき設計）。
2. **今のボトルネックではない。** voice-006 の安全な記録範囲は Source/Reference で、そこに留まる限り Representation は発生せず、consent 機構は不要。
3. **運用規律で足りる段階。** 「③以降を書かない」という規律で境界は守れる（X-5 §3）。フィールド追加は、実在組織との consent のやり取りを一度観察してからで遅くない。
4. **保留の思想的一貫性。** Saiyan Scouter / Hermes と同じく、未確定は確定を急がず保存する。Gateway Consent の (A)/(B)/(C) も、実データが出るまで暫定回答のまま保持。

---

## 8. Saiyan Scouter 問題との関係

- 三階構造（X-4.7 で確立）の継続: 個人の代弁（X-2.6）→ 組織の無断記録（X-4.5）→ 表象という最高位 consent の特定（X-4.7）→ **データモデルのどの位置で表象が発生するか（X-5）→ Gateway という性格づけが表象の特殊形だと特定（本 X-5.5）**。
- 本レビューの貢献: **「Gateway」という一見中立な索引語が、実は表象行為であること**を consent の言葉で確定。Saiyan Scouter の核（不在主体を外部が性格づける）は、個人 Need だけでなく**「この組織は Gateway だ」という組織の性格づけにも宿る**。
- (i) の第三者次元（routed される個人）を通じて、組織表象は個人表象に再接続する——**Gateway を無断で立てることは、その先の個人への誘導路を無断で編成すること**でもある。これが Gateway Consent を最も慎重に扱うべき理由。

---

## 9. やらなかったことの証明

- Gateway を登録・選定していない（③④ は「書かない」と観察したのみ）。
- Need / Contribution / Cooperation / Reality Feedback を生成していない。
- コード/データ/レコード無変更。すべて文書内の分解。

---

*本文書は Gateway Consent の位置づけの観察記録であり、Gateway 登録・Need・Contribution・Cooperation・Reality Feedback の生成を含まない。暫定回答: Gateway Consent は独立概念ではなく、Representation Consent の特殊ケース（候補）／Representation+Participation の複合（実働）として分解でき、当面は Representation Consent に吸収しうる——ただし「接続先＝個人への関係」次元が最も誤読されやすい。実装変更は保留。Reach Gap は未解決であり、本文書もその解決を主張しない。*
