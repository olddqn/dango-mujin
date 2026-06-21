# Findability Review

- **Status:** 観察レビュー（Findability Gap）。実装・接触・登録・Need/Gateway 作成なし。観察のみ。コード/データ無変更。文書のみ。
- **Date:** 2026-06-13
- **前提:** [`CLAIM_FALSIFICATION_REVIEW.md`](CLAIM_FALSIFICATION_REVIEW.md)（到達可能性が価値・反証・生存の上流ゲート。Reach Gap は現設計で反証不能）

> **定義（混同しない）:**
> - **Reachability** = 困窮者・Gateway・協力者へ Mujin が**到達する**能力。（本フェーズで扱わない）
> - **Findability** = 困窮者・Gateway・協力者が **Mujin を発見する**能力。（本フェーズの唯一の対象）
>
> 中心問い: **Mujin はどのように発見されるのか。** 副問い: 現在発見可能か／誰が発見できるか／発見は実際に観測されたか。
> 評価基準（唯一）: **Mujin の存在を知らなかった主体が、Mujin を発見し、何らかの行動（Voice 投稿・問い合わせ・協力申し出・Gateway 登録希望・Contribution 提案）を取れるか。** 実救済は不要。

---

## 0. 事実確認（Reality Correction・検証済み）

| 項目 | 確認結果 |
|---|---|
| プラットフォーム公開状態 | **127.0.0.1（localhost）バインド・非公開**（`app.py:1251`） |
| GitHub 公開 | remote は存在（github.com/olddqn/dango-mujin）だが **feature/mujin-platform-mvp は upstream 無し＝未 push**。Mujin コードは GitHub に載っていない |
| Telegram Bot | **存在しない**（grep の "bot" は "contri**but**ion" の偽陽性。実装なし） |
| voice-006 | **ローカルファイル**（bridge/mujin/data/）・非公開 |
| 検索/参照/被発見の公開面 | **なし** |

> **結論の地: 現在、Mujin に外部から発見可能な面は事実上存在しない。**

---

## 1. Findability Map（主体 × チャネル）

各チャネルの現状を、主体別に「発見可能か」で評価。

| チャネル | Individual | Gateway Org | Contribution Provider | Cooperation Partner | Observer/Researcher |
|---|---|---|---|---|---|
| **GitHub Repository** | ✗（未 push・技術前提） | ✗ | △（技術者・**push されれば**） | ✗ | △（技術者・**push されれば**） |
| **Dan-Go Documentation** | ✗ | ✗ | △（repo 経由） | ✗ | △（repo 経由） |
| **Voice Commons** | ✗（localhost） | ✗ | ✗ | ✗ | ✗ |
| **Telegram Bot** | — 存在しない | — | — | — | — |
| **Public Voice Record** | ✗（非公開） | ✗ | ✗ | ✗ | ✗ |
| **Searchability**（検索） | ✗ | ✗ | ✗ | ✗ | ✗（非公開で索引されない） |
| **Referralability**（紹介） | ✗ | ✗ | ✗ | ✗ | ✗（紹介先の公開面が無い） |
| **Discoverability**（偶然） | ✗ | ✗ | ✗ | ✗ | ✗（偶然出会う面が無い） |

→ **唯一の細い可能性は、GitHub repo が公開かつ push された場合の技術者（Contribution Provider/Researcher）のみ。** 現状は未 push なのでそれも閉じている。**個人・Gateway・協力者には発見経路がゼロ。**

---

## 2. Findability Bottlenecks

1. **公開デプロイの不在（最大）。** プラットフォームは localhost のみ。これが解けるまで他は無意味。
2. **公開面の不在。** 検索・紹介・偶然の対象になる URL/記録が無い。
3. **技術専用の入口。** 唯一あり得る GitHub は git/開発リテラシーを要し、個人・大半の Gateway を排除。
4. **概念の難解さ。** 「協力形成プロトコル」「Voice Commons」等は、助けを求める人が検索する語ではない。
5. **構造的束縛（最重要）:** Mujin はアウトリーチを禁じる（反 Saiyan Scouter・正しい）**かつ**公開面が無い。→ **誰も Mujin を発見できず、唯一の到達路は『ユーザーが直接見せる』＝アウトリーチ**。発見可能性が、禁じているはずのアウトリーチに完全依存している。

---

## 3. Claim-F1〜F4 監査

### Claim-F1 — "Mujin is findable"
- **Current Evidence:** なし。localhost・未 push・公開面ゼロ。
- **Missing Evidence:** 公開面＋外部1名の発見。
- **Falsification Condition:** 公開面が期間 T 存在しても外部発見ゼロなら contradicted。
- **Current Status:** **challenged**（現状は事実上 false。ただしこれは**デプロイの事実**で、永続的不可能性ではなく可修正）。

### Claim-F2 — "Gateways can discover Mujin"
- **Current Evidence:** なし。Gateway は非技術組織で、唯一のチャネル（GitHub）が排除する。
- **Missing Evidence:** Gateway 向けの非技術的公開面＋Gateway 1組織の発見。
- **Falsification Condition:** 公開面が T 存在しても Gateway 発見ゼロなら contradicted。
- **Current Status:** **challenged**（現在 Gateway 向けの実行可能チャネルが無い）。

### Claim-F3 — "Contribution providers can discover Mujin"
- **Current Evidence:** なし。技術的提供者は GitHub repo を**公開・push されれば**見つけうる（細い可能性）。
- **Missing Evidence:** push された公開 repo＋技術者の発見の実証。
- **Falsification Condition:** 公開 repo が T 存在しても提供者の発見ゼロなら contradicted。
- **Current Status:** **unknown**（技術者には原理的に可・未 push で未検証）／非技術提供者には challenged。

### Claim-F4 — "Mujin can be discovered without direct outreach"
- **Current Evidence:** なし。有機的発見はゼロ。知っているのはユーザーと（直接見せられた者＝アウトリーチ）のみ。
- **Missing Evidence:** 有機的発見を可能にする公開面＋アウトリーチ無しの発見1件。
- **Falsification Condition:** 公開面が T 存在してもアウトリーチ無しの発見がゼロなら contradicted。
- **Current Status:** **challenged**（有機的発見面が存在せず、唯一の発見路がアウトリーチ）。**最重要 Claim——現在支持されない。**

---

## 4. 必須観察（10点）

1. **現在発見できる入口:** 実質ゼロ。GitHub（公開・push 時のみ、技術者向け）だけが理論上あり得るが、現状未 push で閉。
2. **経路ごとの摩擦:** GitHub=高（技術）。他=遮断/不在。
3. **経路ごとの前提知識:** GitHub=git/開発＋Dan-Go の存在を知っていること。個人・Gateway には越えられない。
4. **発見者が存在する実証:** **ゼロ。** Mujin を知らずに発見し行動した外部主体は観測されていない（ユーザーは作成者・私は repo 内で稼働＝発見ではない）。
5. **発見後に何ができるか:** 仮に researcher が GitHub repo を見つけても、読む・localhost で動かす・git でコメントは可。だが**誰にも届く Voice は投稿できない（localhost）・live な接続は無い**。
6. **発見しても何もできない経路:** **現状すべて。** repo を見つけても稼働する公開インスタンスが無く、行動が空回り。**公開稼働インスタンス無しの発見は行き止まり。**
7. **Mujin が発見されない理由:** 公開デプロイ不在・公開面不在・概念の難解さ・技術専用入口・反アウトリーチ束縛。
8. **Dan-Go が発見されない理由:** 同じ——repo 内の概念/プロトコル枠組みで公開面が無く、対象（助けを求める人）は「協力形成プロトコル」を検索しない。
9. **Reach Gap と Findability Gap の違い:**
   - Reach Gap = Mujin が相手に**到達できない**（かつ到達を禁じている）。
   - Findability Gap = 相手が Mujin を**発見できない**（発見する面が無いから）。
   - **決定的差:** Findability Gap は**アウトリーチを侵さずに解ける**（公開面を作る＝受動・アウトリーチではない）。Reach Gap は能動的アウトリーチ（禁止）を要する。→ **Findability は反証可能で対処可能なゲート、Reach Gap は不可能。**
10. **Findability が価値検証の上流ゲートである理由:** 発見が無ければ外部主体が来ない→実 Voice/Need/Contribution/Cooperation が生じない→Claim-2/3/4 を試せない→永遠の unknown。**Findability は、下流の全てが必要とする実ケースを生む前提条件。**

---

## 5. 最小 Findability 条件

- **公開された受動的な面**（デプロイされたインスタンス、または公開され索引可能な記録）が少なくとも一つ存在し、
- Mujin を知らない主体が、それを**検索/紹介/偶然**で（アウトリーチ無しに）出会え、
- 一つの**行動**（Voice 投稿・問い合わせ）を取れること。
- **最小 = 公開面1つ ＋ 有機的発見者1人 ＋ 行動1件。** 現状は三つともゼロ。

---

## 6. 現在の Mujin の Findability Status

> **Findability Status = 事実上ゼロ（外部の誰も発見できない）。**

- localhost・未 push・非公開記録・Telegram なし・検索/紹介/偶然の面なし。
- **唯一の到達路がアウトリーチ**であり、それは Mujin が禁じるもの——**反アウトリーチと公開面ゼロの組み合わせが、Mujin を構造的に発見不能にしている。**
- ただし Reach Gap と違い、**これは可修正**: 公開の受動的な面（デプロイ／公開記録）を作ることはアウトリーチではない。それが、憲法を侵さずに発見可能性を開く唯一の道。

---

## 7. 統合（結論を急がない・実証と未実証の分離）

- **実証されたこと:** 現在 Mujin は外部から発見不能（localhost・未 push 等の事実）。発見者ゼロ。
- **未実証のこと:** 公開面を作れば有機的に発見されるか（概念の難解さ・SEO 不在で、面があっても発見ゼロの可能性は残る——だが**反証可能**になる）。
- **核心の区別:** **受動的 Findability（公開面を作る）≠ 能動的 Outreach（相手に働きかける）。** 前者は憲法に反せず、後者は反する。Mujin の前進路は、能動的アウトリーチでなく**受動的に findable になり、有機的発見を待つ**こと（X-6.5 の Case C を具体化）。
- **ただし保証はない:** findable にしても、難解さゆえ発見が永遠に起きない危険は残る。だが少なくとも**反証可能**になる——Reach Gap が永遠の unknown だったのに対し、Findability は試せる。

---

## 8. やらなかったことの証明

- Outreach/Contact/Recruitment/Marketing/Advertisement のいずれも行っていない。
- Gateway Contact・Need 作成/承認/却下・Contribution/Cooperation 作成のいずれも行っていない。
- コード/データ無変更。すべて文書内の観察と事実確認。

---

*本文書は Findability の観察記録であり、実装・接触・登録・Need/Gateway 作成を含まない。現在の Findability Status は事実上ゼロ（localhost・未 push・公開面なし・発見者ゼロ）。Reach Gap と異なり Findability はアウトリーチを侵さず可修正・反証可能で、価値検証の上流ゲート。最小条件は公開面1＋有機的発見者1＋行動1で、現状すべてゼロ。Reach Gap は未解決であり、本文書もその解決を主張しない。*
