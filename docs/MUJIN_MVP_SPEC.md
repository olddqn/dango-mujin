# Mujin MVP Specification v1.1

- **Status:** Revised (v1.1) — ADR-005 反映版
- **Date:** 2026-06-12（v0.1: 2026-06-12 / v1.1: 2026-06-12）
- **Type:** 仕様書のみ。**実装・コード生成を含まない。**
- **Branch:** `feature/mujin-platform-mvp`

> この文書は「**何を作るか**」だけでなく「**何をまだ作らないか**」を定義する。
> **Saiyan Scouter 問題（Reach Gap）は未解決である。**
> したがって **Mujin MVP は Reach Gap 問題を解決したと主張しない。**
> **`advisory_only` は安全の必要条件であって十分条件ではない。道義的責任を免除しない。**（ADR-005 D-4）

---

## Change Log v1.1

v0.1（Specification Freeze）→ v1.1（ADR-005 反映）で変更された点。ADR-005 の決定 D-1〜D-10 と Gap Analysis の指摘を反映する。

| # | 変更点 | 対応 ADR-005 / Gap |
|---|---|---|
| C1 | タイトルを `Mujin MVP Specification v1.1` に更新。advisory≠道義的免責を冒頭に明記 | D-4 / X-2, MR-5, MA-4 |
| C2 | 不変条件を「8項目 + ADR-005 D-1〜D-10」の統一集合に再編（二重化 X-6 を解消） | D-1〜D-10 / X-6 |
| C3 | **新章 §14 Subject Rights**（当事者の権利の明文化）を追加 | D-1, D-5, D-9, D-10 / MI-1, MI-6 |
| C4 | **新章 §15 Objection Path**（非技術・Dan-Go 非依存の異議申立経路）を追加 | D-1 / MI-1, X-3 |
| C5 | **新章 §16 Deferred Consent**（同意延期状態・同意できない状態）を追加 | D-2, D-3 / MI-2 |
| C6 | **新章 §17 Non-Mujin Support**（Mujin 外共助の対等性）を追加 | D-8 / MI-7, MR-? |
| C7 | §1.2 成功条件に「当事者設定の成功指標が既定指標に優先」を追加 | D-9 / MA-3, MI-6 |
| C8 | §4 スキーマに `consent` の `deferred` 状態・`discovery_origin` を追加。`created_from: scouter` を「予約（MVP で生成経路なし）」と注記 | D-2, D-3, D-7 / X-1, X-4 |
| C9 | §8 に発見経緯の開示権・同意更新通知・同意延期を追加（§16 と連結） | D-2, D-3, D-7 / MI-3, MC-5 |
| C10 | §7 UI に異議経路の導線、`/transparency` へ「advisory は道義的免責でない／Mujin 登録は正式支援の条件でない／Reach Gap 定義は非所有」を追加 | D-4, D-6, D-8 |
| C11 | §9 Out Of Scope に「経済的独立を唯一の成功とする設計」を追加 | D-9 |
| C12 | §11 Risks に R6（道義的責任）, R7（登録＝支援価値の社会的承認）, R8（trust_score 独占）, R9（成功物語の広告消費）を追加 | D-4, D-5, D-10 / MR-1〜7 |
| C13 | §12 Open Questions を更新（原典 PDF 発見・Reach Gap 非所有・同意可能状態の判定主体・Mujin Safety Constitution 来歴） | D-2, D-6 / §0, MC-3 |
| C14 | §13 Completion Checklist に「非技術的異議経路」「同意延期状態の表現」「道義的レビュー記録」「失敗の非帰属」を追加 | D-1, D-2, D-4, D-10 |

---

## 前提資料（Provenance）

| # | 資料 | 状態 |
|---|---|---|
| 1 | [`docs/MUJIN_DISCOVERY_REPORT.md`](MUJIN_DISCOVERY_REPORT.md) | 参照済み |
| 2 | [`docs/MUJIN_MVP_SPEC_GAP_ANALYSIS.md`](MUJIN_MVP_SPEC_GAP_ANALYSIS.md) | 反映済み（本 v1.1） |
| 3 | [`docs/adr/ADR-001-CANONICAL-REALITY-FEEDBACK.md`](adr/ADR-001-CANONICAL-REALITY-FEEDBACK.md) | 参照済み |
| 4 | [`docs/adr/ADR-002-DANGO-MUJIN-BOUNDARY.md`](adr/ADR-002-DANGO-MUJIN-BOUNDARY.md) | 参照済み |
| 5 | [`docs/adr/ADR-003-RELIEF-CASE-PROMOTION.md`](adr/ADR-003-RELIEF-CASE-PROMOTION.md) | 参照済み |
| 6 | [`docs/adr/ADR-004-CONTRIBUTION-MODEL.md`](adr/ADR-004-CONTRIBUTION-MODEL.md) | 参照済み |
| 7 | [`docs/adr/ADR-005-SUBJECT-DIGNITY-OBJECTION-NON-COERCIVE-PARTICIPATION.md`](adr/ADR-005-SUBJECT-DIGNITY-OBJECTION-NON-COERCIVE-PARTICIPATION.md) | **本 v1.1 で反映** |
| 8 | `claim_saiyan_scouter.md`（Dan-Go Claim — Saiyan Scouter 問題） | **原典 PDF を発見・読込済み**（Gap Analysis で照合）。リポジトリ取り込みは OQ-1 |
| 9 | `mujin_reflections_from_saiyan_scouter.md` | **同上。** Risks（§11）・Subject Rights（§14）・Objection Path（§15）等に反映 |

> 資料 8・9 は v0.1 時点でリポジトリ未在だったが、その後 PDF 原典が発見され Gap Analysis で全章照合済み。原典のリポジトリ取り込みは OQ-1 として残す。なお両資料が前提とする「Mujin Safety Constitution（8項目）」「`ConsentRecord` scope」等はリポジトリ未在（OQ-9, Gap §0）。

---

## 設計思想（Design Philosophy）

**Mujin は寄付サイトではない。**

Mujin は「**協力を可視化し、次の一歩を発見し、現実との接続を支援する**」ためのプラットフォームである。

| | Dan-Go | Mujin |
|---|---|---|
| 役割 | 協力形成プロトコル | 共助実行プラットフォーム |
| 担当 | 問題の発見・対話・交渉・異議・検証 | 接続・協力・支援・進捗・現実フィードバック |
| データ方向 | Decision 情報を**公開** | Reality Feedback を**返す** |

**思想的には不可分。実装的には疎結合。**（ADR-002）

**Mujin は「来る人を受け入れる」プラットフォームである。「見つけに行く」機能は未解決の Dan-Go Claim（`claim-saiyan-scouter-001`）として交渉中であり、MVP には実装しない。** この立場を明示することが Mujin の誠実さの証明である。（ADR-005 D-7）

---

## MVP 全体の不変条件（統一集合）

> v1.1 で、v0.1 の「Saiyan Scouter 由来 8項目」と ADR-005 の「D-1〜D-10」を**単一の不変条件集合**に統一した（X-6 解消）。いかなる章もこれに反してはならない。これらは ADR-001〜004 および本仕様の全章に優先する。

### A. 基礎不変条件（v0.1 由来）
1. **Mujin への登録は支援価値の証明ではない。**
2. **支援拒否は失敗ではない。**
3. **撤回は正当な選択である。**
4. **Mujin を通らない支援も尊重する。**
5. **成功指標は単一化しない。**
6. **`created_from` による序列を作らない。**
7. **自動発見・自動スカウト・自動アウトリーチを実装しない。**（Saiyan Scouter 未解決）
8. **「なぜあなたに接触したのか」を説明できない接触を正当化しない。**

### B. 当事者尊厳の不変条件（ADR-005 由来）
- **D-1** 当事者は、Mujin・NPO・支援者・AI の行動に対し、**Dan-Go 参加能力や技術アクセスなしに異議を出せる。**（→ §14, §15）
- **D-2** 代理登録では**「同意延期状態」を正式に認める。**（→ §16）
- **D-3** **同意できない状態は同意ではない。**（→ §16）
- **D-4** **`advisory_only` は道義的責任を免除しない。**（→ §11 R6）
- **D-5** **非登録・撤回・拒否は失敗ではない。**（A-1〜3 を強化）
- **D-6** **Reach Gap の定義は誰か一人が所有しない。**（設計者・支援者・AI・NPO・Dan-Go の誰も）（→ §12）
- **D-7** **「なぜあなたに接触したのか」を説明できないアウトリーチは正当化しない。**（A-8 を強化）
- **D-8** **Mujin 外部の共助（家族・友人・地域）を、Mujin より劣ったものとして扱わない。**（→ §17）
- **D-9** **成功指標は当事者が設定できる。Mujin の「経済的独立」は、当事者が別指標を望む場合に自動的に後退する。**（→ §1.2, §14）
- **D-10** **失敗・中断したケースを、当事者の能力・属性・努力不足に帰属させてはならない。**（→ §11 R?, §4）

---

# 1. MVP Goal

## 1.1 目的
Mujin MVP の目的は、**Dan-Go が公開した決定情報から生まれた共助ケースについて、当事者の同意のもとで協力を可視化し、進捗と現実フィードバックを記録できる最小のプラットフォームを成立させること**である。

## 1.2 成功条件（単一化しない — A-5 / D-9）
成功は「支援成立件数」だけで測らない。MVP の成功は、**少なくとも以下すべてが一度ずつ観測可能になったこと**で定義する:

| # | 成功要素 | 観測点 |
|---|---|---|
| G1 | **協力の成立** | 少なくとも1件の Contribution が `committed` 以上に到達 |
| G2 | **当事者の同意** | 対象 Mujin Case に `consent.status = active` が記録されている |
| G3 | **進捗の記録** | `progress_log` に append-only エントリが1件以上存在 |
| G4 | **フィードバックの記録** | `bridge/sutable/reality_feedback.jsonl`（ADR-001）に対応 feedback が1件以上 append された |

**当事者設定の成功指標の優先（D-9）:** 当事者が独自の成功指標を設定した場合、それが G1〜G4 や Mujin 既定指標（「経済的独立」等）に**優先する**。Mujin は当事者の定義する「成功」を Mujin の定義する「成功」より上位に置く。「経済的独立」が不適切なゴールである当事者（障害・慢性疾患・高齢・介護状況・制度的排除）への支援設計を Mujin は持つ（§14, §9）。

## 1.3 明示的な非目標
- 支援成立件数の最大化を成功条件にしない。
- Reach Gap の解決を主張しない（§11, §12）。
- 「支援されなかったケース」を失敗として扱わない（A-2, D-5）。
- 「経済的独立」を唯一の成功とする設計を持たない（§9, D-9）。

---

# 2. Scope

## 2.1 MVP で実装するもの（IN）
- Mujin Case のデータ表現（§4 スキーマ）。
- Relief Case → Mujin Case への**手動昇格**フロー（ADR-003: verified → consent_obtained → promoted、human review 必須。同意延期状態を経由可、§16）。
- 既存 Dan-Go Contribution モデルの**再利用**（§5, ADR-004）。
- Dan-Go Decision 情報（Directive + Execution Log）の**読み取り専用エクスポート**（ADR-002）。
- Reality Feedback の append（ADR-001 の正典 `bridge/sutable/reality_feedback.jsonl`）。
- 最小 UI 5ページ（§7）。
- 同意・訂正・撤回・**同意延期**フロー（§8, §16）。
- **当事者の異議申立経路（非技術・Dan-Go 非依存を含む）**（§15）。
- 透明性ページ（透明な記録の閲覧）。

## 2.2 MVP で実装しないもの（OUT）
- 自動発見 / 自動スカウト / 自動アウトリーチ（A-7）。
- Saiyan Scouter Agent / Outreach / Education / Translation / Story Agent（§9）。
- 自動マッチング・スコアリング・ランキング・AI 自動判断（§9）。
- 寄付決済・送金（`moves_money: false`、ADR-004）。
- Dan-Go レコードへの書き込み（Reality Feedback の append を除く。Execution Log への書き込みは禁止、ADR-001/002）。
- 「経済的独立」を唯一の成功とする支援設計（D-9）。

> Scope の境界は「便利さ」で動かさない。OUT 項目を MVP に引き入れる提案は、本凍結を破る変更として扱う。

---

# 3. Data Flow

## 3.1 中核フロー
```
Relief Case (Phase 18, advisory観察)
   │   [ADR-003 昇格ゲート + ADR-005 D-2/D-3]
   ▼  verified → consent_obtained（同意延期状態を経由可・§16）→ promoted
Promotion                                  (※ human review 必須・自動化しない)
   ▼
Mujin Case        … bridge/mujin/ 配下の別レコード（relief_case_id を参照・非破壊）
   ▼
Contribution      … 既存 Dan-Go Contribution モデル（ADR-004）
   ▼
Reality Feedback  … bridge/sutable/reality_feedback.jsonl へ append（ADR-001）
```

## 3.2 Dan-Go との接続点と当事者経路
```
┌──────────────── Dan-Go（既存・advisory only・読み取り元）────────────────┐
 directive-*.json ──┐
 logs/directive-*.jsonl ──┤ READ (Export Source, ADR-002 / Discovery §4 P1)
 relief-case-registry.json ──┘
 claims/claim-*.json ── READ (Contribution の missing_conditions 結合, §5)
└──────────────────────────────────────────────────────────────────────────┘
                 │ READ ↓                                   ↑ WRITE (append only)
┌──────────────── Mujin（本MVP）────────────────────────────────────────────┐
 Mujin Case ──▶ Contribution ──▶ Reality Feedback
                                      │ append → bridge/sutable/reality_feedback.jsonl
                                      ▼
                          Phase 27 Reality Feedback Bridge（advisory ルータ）
                                      │ suggested_bridge_target + human review
                                      ▼
                          relief_case_memory / care_loop_reopen（Mujinは直接書かない）
└──────────────────────────────────────────────────────────────────────────┘
        ▲ 当事者の異議申立（D-1・§15）：Dan-Go 経由でも技術アクセスでもない第三経路
        └─ 当事者 ──(電話・対面・代筆・第三者)──▶ 異議の受理・記録
```

**接続規約（凍結）:**
- Mujin → Dan-Go の書き込みは **Reality Feedback の append のみ**。Execution Log / Claim / Directive / Relief Case は読み取り専用。
- 昇格・ケア反映は **Phase 27 Bridge + human review** を経由（自動反映しない）。
- Mujin 固有レコードは `bridge/mujin/` 配下に分離（既存ファイル非破壊）。
- **当事者の異議申立経路（§15）は、上記データ境界の外に、第三の経路として並立する**（ADR-002 の疎結合を破らない）。

---

# 4. Mujin Case Schema（最小）

> これは**仕様としてのスキーマ定義**であり、実装コードではない。MVP が満たすべき最小フィールドを凍結する。

```
MujinCase {
  case_id:        string   // 一意。例 "mujin-case-001"
  created_from:   enum     // relief_case | direct_application | npo_proxy
                           //   | scouter ← 予約。MVP に生成経路は存在しない（§9, D-7）
                           //   ※ A-6: これは"由来の記録"であり序列ではない
  source_ref:     object   // { relief_case_id?: string, claim_id?: string }（非破壊参照）
  discovery_origin: object // 発見経緯（D-7 / §16.3）。当事者が照会できる
                           //   { how: string, by: string, disclosed_to_subject: bool }
  consent:        object   // §8 / §16 と一致
                           //   {
                           //     status: enum(active | withdrawn | pending | deferred),
                           //                  // deferred = 同意延期状態（D-2/§16）
                           //     can_consent: bool,            // 同意可能な状態か（D-3）
                           //     obtained_at: ISO8601 | null,
                           //     confirmation_due: bool,        // 後日同意確認義務（D-2）
                           //     last_confirmed_at: ISO8601,    // 継続的確認（§8）
                           //     correction_log: [ ... ],       // 訂正履歴（append-only）
                           //     withdrawable: true             // 常に true（A-3）
                           //   }
  needs:          array    // [{ need_id, description, addresses_condition?, status }]
                           //   addresses_condition は Claim の missing_condition に対応（§5）
  success_metric: object   // 当事者設定の成功指標（D-9）。既定指標に優先
                           //   { set_by: enum(subject|default), description: string }
  progress_log:   array    // append-only。[{ entry_id, content, actor, created_at }]
  visibility:     enum     // public | participants_only | private
                           //   既定は participants_only（最小開示・§8）
  status:         enum     // open | in_progress | paused | resolved_by_parties
                           //   | not_pursued | interrupted
                           //   ※ "not_pursued"/"interrupted" は失敗ではない（A-2, D-5）
  closure_attribution_prohibited: true  // 閉鎖理由を個人属性に帰属しない（D-10）
  // 不変条件（全レコードに付与）
  authority:           "none"
  execution_allowed:   false
  moves_money:         false
  advisory:            true    // ※ advisory は安全の必要条件であり道義的免責ではない（D-4）
  append_only:         true
  contestable:         true
  reopenable:          true
  registration_is_not_proof: true   // A-1
}
```

**凍結ルール:**
- `created_from` の各値に**優先順位・重み・序列を与えない**（A-6）。`scouter` は**予約値**で、MVP に生成経路は無い（X-4 解消）。
- `status` に成功/失敗の含意を持たせない。`not_pursued` / `interrupted` / `resolved_by_parties` は中立記録。
- **Case 閉鎖・中断時、理由を当事者の能力・属性・努力に帰属する記述を禁ずる**（`closure_attribution_prohibited`、D-10）。原因は Mujin の設計・支援者の行動・社会的条件・Mujin 自身の限界として記録する。
- `case_id` は Relief Case を**書き換えず** `source_ref.relief_case_id` で参照する（ADR-003 非破壊）。

---

# 5. Contribution Schema

## 5.1 決定（ADR-004 準拠）
- **Contribution を上位概念とする。Mujin は新しい Contribution システムを作らない。**
- **SupportOffer は新設しない。** 既存の賛同イベント（`plan_supported` 等）は **Contribution の一種（`reputation` / `care` 系の資源無し形態）として統合**する。
- 既存 Dan-Go モデル（`CONTRIBUTION_SPEC.md`、`contribution_router.py`、`bridge/sutable/contributions.jsonl`）を再利用する。

## 5.2 既存モデルとの対応
| 項目 | 既存 Dan-Go Contribution | Mujin MVP での扱い |
|---|---|---|
| 型 | `code, compute, legal, translation, housing, funding, social_reach, reputation, care, knowledge, coordination`（11種） | そのまま再利用 |
| 状態 | `offered → committed → delivered → verified → disputed` | そのまま再利用（G1 は `committed` 以上で判定） |
| 結合 | `addresses_condition` → Claim の `missing_condition` | Mujin Case の `needs[].addresses_condition` を同キーで結合 |
| 金銭 | `funding` 型あり・`moves_money: false` | advisory 記録のみ。MVP は決済しない |
| SupportOffer | `plan_supported` イベント | Contribution へ統合（新設しない） |

## 5.3 将来拡張（MVP では実装しない）
`education` / `mentoring` / `supplies` / `job_referral` の型追加は将来課題（ADR-004）。追加時も**スコア・tier・earning-back・債務を持ち込まない**。

> **支援実績は権威にならない（D-10 / ADR-004）。** 支援実績の蓄積は認めるが、信頼の**独占**（新規 Case 割当の固定化）を設計に持ち込まない。

---

# 6. Reality Feedback Integration

## 6.1 正典（ADR-001）
- **正典 Reality Feedback = `bridge/sutable/reality_feedback.jsonl`。**
- スキーマ語彙: `event_type: "reality_feedback"`, `claim_id`, `result`, `conditions_met`, `conditions_unmet`, `event_hash`, `timestamp`。
- Mujin は **append-only** で追記。既存行の書き換え・削除は禁止。
- 付与必須: `authority: "none"`, `execution_allowed: false`, `moves_money: false`, `not_proof_of_resolution: true`, `requires_human_review: true`。
- **Mujin は Execution Log へ直接書き込まない**（ADR-001/002）。

## 6.2 Phase 27 Bridge との関係
- append された feedback は **Phase 27 Reality Feedback Bridge** が走査し、`relief_case_memory` / `care_loop_reopen` への `suggested_bridge_target` を **advisory として**提示する。
- **自動反映しない**: `feedback_bridge_does_not_reopen_case_automatically: true`、`human_review_is_required_before_any_real_world_action: true`。
- **`requires_human_review` は「advisory だから安全」の根拠ではなく、道義的責任を伴うレビューである**（D-4）。害悪が観測された Case は、advisory 不変条件の充足とは独立に道義的レビューの記録を残す。
- Mujin Case の `status` 変更と Reality Feedback は**別事象**。feedback の存在は status を自動で変えない（human review 経由）。

## 6.3 結合キー
- feedback は `claim_id` で結合。Mujin Case → Claim は `source_ref.claim_id` / `needs[].addresses_condition` 経由（Discovery §3, ADR-002 の `directive_id ⇄ claim_id` 対応）。

---

# 7. UI Pages（最小構成のみ）

> 5ページのみ。各ページに「非表示にするもの」を明記する（何を見せないかが仕様）。**異議申立は UI ページに限定されない**（§15 参照：非技術経路を含む）。

| Path | 目的 | 表示内容 | 非表示内容（凍結） |
|---|---|---|---|
| `/` | 入口・思想の提示 | Mujin の目的（寄付サイトではない／「来る人を受け入れる」立場）、進行中ケース数（中立カウント）、透明性・異議経路への導線 | 成功率・ランキング・「最も支援が必要なケース」等の序列表示 |
| `/cases` | ケース一覧（中立） | 公開許可済みケースの中立リスト（作成日時順）、各ケースの `status`・`needs` 概要 | スコア・優先度・`created_from` バッジによる序列、未同意・同意延期ケース |
| `/cases/:id` | ケース詳細 | `needs`、`progress_log`（append-only 履歴）、Contribution 状況、`visibility` 範囲内の情報、異議申立への導線 | 当事者の身元（同意範囲外）、成功/失敗ラベル、vulnerability の定量化 |
| `/contribute` | 協力の記録 | Contribution 型一覧、対象 `need` 選択、`offered/committed` 記録、撤回の説明 | 寄付決済 UI、貢献額ランキング、貢献者スコア |
| `/transparency` | 透明性 | append-only 記録の閲覧、不変条件の明示、**Reach Gap が未解決かつその定義は誰も所有しない旨**、**Mujin 登録は「正式な支援」の条件でない旨**、**Mujin を通らない支援も対等に尊重する旨**、**`advisory_only` は道義的責任を免除しない旨**、異議申立経路の案内（§15） | 個人特定可能情報、内部判断の権威化表現 |

**全ページ共通の非表示原則:**
- 成功指標の単一化表示をしない（A-5, D-9）。
- 「なぜこのケースが表示されているか」を説明できない並べ替えをしない（A-8, D-7 の UI 版）。
- 未同意・同意延期・撤回済みケースは表示しない（§8, §16）。

---

# 8. Consent & Safety

Saiyan Scouter 議論と ADR-005 を反映し、以下を凍結する。同意の詳細状態は §16（Deferred Consent）と一体。

## 8.1 本人同意（consent）
- Mujin Case の表示・Contribution 受付は **`consent.status = active` が前提**。
- 同意は**継続的確認**: `last_confirmed_at` を保持し、一定期間・重要変更時に再確認する（同意は一度きりではない）。
- `pending` / `deferred` 状態のケースは公開しない。

## 8.2 訂正（correction）
- 当事者は自分のケース情報を訂正できる。訂正は `consent.correction_log` に **append-only** で記録（上書きしない＝来歴を残す）。

## 8.3 撤回（withdrawal）
- **撤回は失敗ではない**（A-3, D-5）。
- `consent.withdrawable` は常に `true`。撤回時 `consent.status = withdrawn`、ケースは公開停止。
- 撤回理由の提出は**任意**。撤回を理由に評価を下げる仕組みを作らない。
- **撤回・非登録・拒否は、記録上「拒否」「失敗」として残さない**（D-5）。

## 8.4 登録しない自由
- **Mujin に登録しない選択を尊重する**（A-1, A-4, D-5）。登録は支援価値の証明ではない。
- Mujin を通らない支援（直接の相互扶助）を劣位に置く表示をしない（§17）。

## 8.5 接触の正当性
- **「なぜあなたに接触したのか」を説明できない接触を正当化しない**（A-8, D-7）。MVP は能動的アウトリーチを持たない（§9）ため、接触は当事者起点（`direct_application`）または同意確認を伴う昇格（`relief_case`）に限る。

## 8.6 同意更新通知（D-2 連動 / MC-5）
- Mujin の利用目的・データ扱いが変更された場合、当事者への**再同意確認を義務**とする。変更後の継続は再同意を要件とする。

> 同意できない状態・代理登録の同意延期は §16 に定義する。

---

# 9. Out Of Scope

MVP から**明示的に除外**する（実装しない）。

- **Saiyan Scouter Agent**（自動スカウト）
- **Outreach Agent**（自動アウトリーチ）
- **Education Agent** / **Translation Agent** / **Story Agent**（成功物語生成）
- **自動マッチング** / **スコアリング** / **ランキング**
- **AI 自動判断**（昇格・接触・優先度の自動決定）
- 寄付決済・送金
- Dan-Go Execution Log / Claim / Directive への書き込み
- **「経済的独立」を唯一の成功とする支援設計**（D-9）

> これらは「将来検討」ではあっても、**Saiyan Scouter 問題が未解決である限り MVP には入らない**（A-7）。
> **将来アウトリーチを設計する場合の最低限原則**（ADR-005 Non-decisions / REFL 5.2）: ①実行者は人間・AI は補助 ②接触根拠を当事者に開示 ③断られた事実を記録しない ④当事者の利益を代表 ⑤「正規経路」として権威化しない。

---

# 10. Implementation Order

> 実装は本仕様凍結の**後**に別途着手する。ここでは順序計画のみを定義する（コードは書かない）。

| Phase | 名称 | 内容 | 完了の目安 |
|---|---|---|---|
| **A** | **Data Layer** | Mujin Case スキーマ（§4）の表現、`bridge/mujin/` 配下のレコード形式、同意延期状態（§16）、Relief Case 参照（非破壊） | Mujin Case が append-only で表現・参照でき、同意延期を表せる |
| **B** | **Export Layer** | Dan-Go Decision 情報（Directive + Execution Log）の読み取り専用エクスポート（ADR-002） | `directive_id` 単位で決定情報を読める |
| **C** | **UI Layer** | 5ページ（§7）の最小実装＋異議経路導線（§15）。非表示原則の順守 | 5ページが中立表示で閲覧可能、異議経路が案内される |
| **D** | **Feedback Layer** | Reality Feedback の append（ADR-001）、Phase 27 Bridge との接続（自動反映なし）、道義的レビュー記録（D-4） | feedback が正典 JSONL に append され、Bridge が advisory に拾える |

依存順: A → B → C → D（D は A–C に依存）。各 Phase は統一不変条件（A-1〜8, D-1〜10）を満たすこと。

---

# 11. Risks

Saiyan Scouter 議論で発見されたリスクを反映する（緩和は「構造的非実装」が中心）。

| ID | リスク | 内容 | MVP での扱い |
|---|---|---|---|
| R1 | **自己申請バイアス** | `direct_application` に偏ると、申請できる者だけが可視化される | 成功指標を単一化しない（A-5）。Reach Gap 未解決を明記（§12）。経路等価性は将来監査課題（OQ-10） |
| R2 | **NPO 権力集中 / 情報＝決定の集中** | `npo_proxy` が Case 内容と登録判断の両方を持ち、ゲートキーパー化 | `created_from` に序列を与えない（A-6）。proxy も検証・同意ゲート（ADR-003）と異議経路（§15）を通す |
| R3 | **支援者権力** | 貢献者がケースに対し優位・支配を持つ | スコア・ランキング非実装（§9）。Contribution に債務・見返りを持ち込まない（ADR-004） |
| R4 | **成功物語バイアス** | 「成功したケース」だけが語られ、撤回・不成立が不可視化 | Story Agent 非実装（§9）。撤回は失敗ではない（A-3）。`not_pursued` を中立記録 |
| R5 | **Reach Gap** | そもそも Mujin に到達できない人が構造的に取り残される | **未解決。MVP は解決を主張しない**（§12）。定義は誰も所有しない（D-6）。自動アウトリーチで"解決した風"にしない（A-7） |
| **R6** | **善意の害悪への道義的責任** | 「接続→支援→失敗」の連鎖で害悪が生じうる。`advisory_only` は技術的免責で道義的責任を免除しない | **D-4 を明文化。** 害悪観測 Case に道義的レビュー記録（§6.2）。advisory を安全の証明に使わない |
| **R7** | **登録＝支援に値するの社会的承認** | 「Mujin 登録＝承認」が広まると、非登録者が「承認されなかった人」になる | 登録は「支援を求める行為」であり審査結果でない旨を `/transparency`・条件文に明記（A-1, D-5） |
| **R8** | **trust_score 独占 / 信頼の固定化** | 実績ある主体に Case が集中し、信頼が独占される | 支援者スコアを MVP で実装しない（§9）。蓄積は認めるが独占を設計に入れない（§5.3, D-10） |
| **R9** | **成功物語の広告消費** | 当事者の物語が Mujin の宣伝に消費され、非成功が対比的に不可視化 | Story Agent 非実装。物語の広告・PR 利用は追加同意を要件化（将来、§16 連動）。`/transparency` で非成功も対等に扱う |

---

# 12. Open Questions

Saiyan Scouter Claim の論点を引き継ぐ。**これらは MVP で解決されない。**

| ID | Open Question |
|---|---|
| **OQ-1** | `claim_saiyan_scouter.md` / `mujin_reflections_from_saiyan_scouter.md` の原典（PDF 発見済み）をリポジトリに正式取り込みするか。 |
| **OQ-2** | **Reach Gap をどう扱うか。** 自動アウトリーチを禁じたうえで、到達できない人の存在をどう可視化・尊重するか（解決ではなく誠実な明示）。**定義は誰も所有しない**（D-6）—— では誰が、どの公開交渉で定義を扱うか。 |
| **OQ-3** | `consent` の継続的確認の具体的周期・トリガー（`last_confirmed_at` の運用設計）。 |
| **OQ-4** | `created_from` を序列化せずに「由来の透明性」を保つ UI 表現の具体。 |
| **OQ-5** | Relief Case 昇格時の `consent_obtained` の取得・記録主体（誰が・どう同意を確認するか、ADR-003 連動）。 |
| **OQ-6** | 最初に扱う実コモンズ／実ケースの選定（Discovery Report OPEN_QUESTIONS Q1 連動）。 |
| **OQ-7** | `bridge/mujin/` 設計メモが現ブランチに無い問題（Discovery Report P-3）の解決。 |
| **OQ-8** | Mujin の `event_hash` 生成方式が既存 JSONL と互換か（Discovery Report U-5）。 |
| **OQ-9** | REFL が前提とする「Mujin Safety Constitution（8項目）」「`ConsentRecord` scope」「`independence_roadmap`」の原典がリポジトリに無い（Gap §0）。正典をどう確定するか。 |
| **OQ-10** | **同意可能な状態になったことを誰がどう判定するか**（D-2/D-3 の運用主体、§16）。 |
| **OQ-11** | 参加経路の等価性監査（年1回・PII なし・非対称性は公開交渉）の運用主体と手続き（REFL GR2）。 |
| **OQ-12** | 異議申立の非技術経路（電話・対面・代筆）の具体的運用（§15、D-1 の手段）。 |

> **Saiyan Scouter 問題は未解決である。Mujin MVP は Reach Gap 問題を解決したと主張しない。Reach Gap の定義は誰も所有しない。**

---

# 13. MVP Completion Checklist

MVP が「完成」と判定される条件。**すべて満たして初めて完成**。

## 13.1 機能（Functional）
- [ ] Mujin Case を §4 スキーマで表現でき、append-only で記録できる。
- [ ] Relief Case → Mujin Case の手動昇格が verified → consent_obtained → promoted の順で human review を経て行える（ADR-003）。
- [ ] 昇格が Relief Case Memory を**書き換えない**（`source_ref` 参照のみ）。
- [ ] Dan-Go Decision 情報（Directive + Execution Log）を**読み取り専用**で取り込める（ADR-002）。
- [ ] Contribution を既存モデルで記録でき、`offered → committed` を観測できる（§5）。
- [ ] Reality Feedback を正典 `bridge/sutable/reality_feedback.jsonl` に **append** できる（ADR-001）。
- [ ] Phase 27 Bridge が append された feedback を advisory に拾える（自動反映なし）。

## 13.2 成功要素（§1.2、単一化しない）
- [ ] G1 協力の成立（Contribution が `committed` 以上）。
- [ ] G2 当事者の同意（`consent.status = active`）。
- [ ] G3 進捗の記録（`progress_log` ≥ 1）。
- [ ] G4 フィードバックの記録（reality_feedback.jsonl ≥ 1）。
- [ ] 当事者設定の成功指標が既定指標に優先する表現が存在する（D-9）。

## 13.3 当事者尊厳・同意・安全（§8, §14, §15, §16）
- [ ] 同意なき・同意延期のケースが公開されない。
- [ ] **同意延期状態（`deferred`）と後日同意確認義務（`confirmation_due`）が表現できる**（D-2, D-3）。
- [ ] 訂正が append-only で記録される。
- [ ] 撤回がいつでも可能で、撤回・非登録・拒否が「失敗」として記録されない（D-5）。
- [ ] **当事者が Dan-Go 参加能力・技術アクセスなしに異議を出せる経路が少なくとも1つ存在する**（D-1, §15）。
- [ ] 発見経緯（`discovery_origin`）を当事者が照会できる（D-7）。
- [ ] 「登録しない自由」「Mujin を通らない支援の対等性」を尊重する表示（D-8, §17）。

## 13.4 非実装の保証（§9・不変条件）
- [ ] 自動発見・自動スカウト・自動アウトリーチが**無い**。
- [ ] スコアリング・ランキング・AI 自動判断が**無い**。
- [ ] `created_from` による序列表示が**無い**（`scouter` の生成経路も無い）。
- [ ] 決済・送金が**無い**（`moves_money: false`）。
- [ ] Execution Log / Claim / Directive への書き込みが**無い**。

## 13.5 誠実性・道義性（§6, §11, §12）
- [ ] `/transparency` に **Reach Gap が未解決かつ定義は非所有である旨**が明記されている（D-6）。
- [ ] `/transparency` に **`advisory_only` は道義的責任を免除しない旨**が明記されている（D-4）。
- [ ] 害悪が観測された Case に**道義的レビューの記録**が残せる（D-4, §6.2）。
- [ ] Case 閉鎖・中断の理由が**当事者の属性・能力・努力に帰属されていない**（D-10）。
- [ ] MVP が Reach Gap を解決したと**主張していない**。
- [ ] 統一不変条件（A-1〜8, D-1〜10）が全章で破られていない。

---

# 14. Subject Rights（当事者の権利）

当事者（支援を受ける側／受けうる側）は、Mujin において以下の権利を持つ。これらは支援提供側（Mujin・NPO・支援者・AI）に対して当事者を従属させないための不変の権利である。

| # | 権利 | 根拠 |
|---|---|---|
| SR-1 | **異議の権利。** Mujin・NPO・支援者・AI の行動に対し、Dan-Go 参加能力・技術アクセスなしに異議を出せる（§15）。 | D-1 |
| SR-2 | **同意の権利。** 同意なき登録・公開を受けない。同意できない状態では同意とみなされない（§16）。 | D-2, D-3 |
| SR-3 | **撤回の権利。** いつでも撤回でき、撤回は失敗・拒否として記録されない。 | D-5 |
| SR-4 | **非登録の権利。** Mujin に登録しない自由を持ち、それは支援価値の否定ではない。 | D-5, A-1 |
| SR-5 | **発見経緯を知る権利。** 「なぜ・どう自分が登録／接触されたか」を照会・開示請求できる（`discovery_origin`）。 | D-7 |
| SR-6 | **成功を定義する権利。** 自らの成功指標を設定でき、それが Mujin 既定指標に優先する。 | D-9 |
| SR-7 | **非帰属の権利。** 失敗・中断したケースを自分の能力・属性・努力不足に帰属されない。 | D-10 |
| SR-8 | **外部共助を選ぶ権利。** Mujin を通らない支援を選んでも劣位に置かれない（§17）。 | D-8 |

> これらの権利は、Dan-Go の Claim 提起権（Art.3）から**独立**して存在し、技術的アクセスを必要とせずに行使できる。

---

# 15. Objection Path（異議申立経路）

**D-1 の実現。当事者が支援提供側に異議を出すための経路を定義する。**

## 15.1 原則
- 異議申立経路は **Dan-Go 参加能力に依存しない**。Claim を言語化できること・Dan-Go を知っていることを前提としない。
- **技術アクセスを必要としない**形態を少なくとも1つ含む（電話・対面・代筆・第三者経由）。
- 異議の対象は **Mujin システム・NPO・支援者・AI エージェントの行動**を含む。
- **異議の提出が、当事者の評価・支援適格性・優先度に不利に作用してはならない。**

## 15.2 受理と記録
- 異議は append-only で記録し、対応の来歴を残す（上書きしない）。
- 異議記録は当事者を不利に扱うためのプロファイルに転用しない。
- 異議への対応・未対応も記録し、`/transparency` の対象とする（個人特定情報を除く）。

## 15.3 MVP での最小要件
- UI（§7 `/cases/:id`・`/transparency`）に異議申立への導線を置く。
- **加えて、UI を経由しない非技術経路を最低1つ用意する**（具体形態は OQ-12、本仕様では手段を確定しない）。

> 異議申立経路は §3.2 のデータ境界の外に並立する第三経路であり、ADR-002 の疎結合を破らない。

---

# 16. Deferred Consent（同意延期状態）

**D-2 / D-3 の実現。代理登録と「同意できない状態」を定義する。**

## 16.1 状態定義
| `consent.status` | 意味 | 公開 | Contribution 受付 |
|---|---|---|---|
| `active` | 当事者の有効な同意がある | 可 | 可 |
| `pending` | 同意取得手続き中 | 不可 | 不可 |
| `deferred` | **同意延期状態。** 代理登録され、当事者がまだ同意可能な状態にない（重篤・言語障壁・認知的制約等） | 不可 | 不可 |
| `withdrawn` | 撤回済み | 不可 | 不可 |

## 16.2 原則
- **同意できない状態は同意ではない**（D-3）。沈黙・無反応・不在を同意とみなさない。
- 代理登録（`created_from: npo_proxy` / `relief_case` 昇格）で当事者が同意可能な状態にない場合、`status = deferred`・`can_consent = false`・`confirmation_due = true` とする。
- **当事者が同意可能な状態になった時点で、登録側に同意確認を行う義務が生じる**（`confirmation_due`、D-2）。確認されるまで同意は**存在しない**。
- `deferred` は「仮の同意」ではない。`deferred` の間、ケースは公開されず Contribution も受け付けない。

## 16.3 発見経緯の開示（D-7 連動）
- 代理登録時は `discovery_origin { how, by, disclosed_to_subject }` を記録し、当事者が同意可能になった際に発見経緯を開示できるようにする。

## 16.4 運用上の未決事項
- 「同意可能な状態になった」ことを誰がどう判定するか（OQ-10）。本仕様は原則のみ確定し、判定主体・手続きは実装前の交渉に委ねる。

---

# 17. Non-Mujin Support（Mujin 外支援の扱い）

**D-8 の実現。Mujin 外部の共助の対等性を定義する。**

## 17.1 原則
- **Mujin は世界に存在する共助の一形態に過ぎない。** 家族・友人・地縁・地域コミュニティによる非公式支援を、Mujin を通る支援より**劣ったものとして扱わない**。
- **Mujin への登録は「正式な支援」の条件にならない。** 登録は「支援を求める行為」であって「支援に値するかの審査結果」ではない（R7 連動）。
- 非公式の相互扶助を「可視化されていない価値ある共助」として設計上明示的に尊重する。

## 17.2 表示・記録での扱い
- `/transparency` に「Mujin を通らない支援も対等に尊重する」「Mujin 登録は正式支援の条件でない」を明示する。
- Mujin 内のケース数・成功要素を、非公式共助に対する優越の指標として提示しない。
- 「Mujin に登録されていない」ことを欠落・未承認として表示しない（D-5, R7）。

---

*本文書は仕様（v1.1）であり、実装・コード・追加提案を含まない。実装は本仕様の承認後に別フェーズで着手する。Saiyan Scouter 問題（Reach Gap）は未解決であり、Mujin MVP はその解決を主張しない。Reach Gap の定義は誰も所有しない。これらの原則は、設計者だけの議論ではなく、到達される側の声を含む Dan-Go 公開交渉に服する。*
