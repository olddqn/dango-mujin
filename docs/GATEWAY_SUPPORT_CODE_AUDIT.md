# Gateway Support Runtime — Code Audit (F-9〜F-20 準拠監査)

- **Status:** コード監査報告。**実装変更なし・commit なし・push なし。** 修正はコミット単位で提案のみ。
- **Date:** 2026-06-21
- **対象:** `bridge/gateway_support/`（store.py, runtime/*.py, cli.py）
- **規範:** F-9〜F-20（closed）
- **監査軸:** 仕様違反 / 境界漏れ / Ranking・Recommendation 混入 / TTFR-G・TTFR-P 混同 / 人間承認回避経路

> **総括:** コア境界は概ね健全（二鍵ゲート・FORBIDDEN_FIELDS による ranking/score/recommendation/owner/ttfr_p の構造的禁止・候補の非順序化・consent≠statement・memory の actor 無名化はいずれも成立）。ただし **1 件の実バグ（F-18 履歴セマンティクス）** と、**CLI のアクション不在（誤認リスク）**、TTFR-G 時計反転の未ガード、防御多重化の不足を検出。Ranking/Recommendation 混入と TTFR-G/TTFR-P 混同の実害は検出されず。人間承認の主要回避経路は execute() の二鍵ゲートで防止されているが、store 直書きという detective-only の残余あり。

---

## A. 準拠が確認できた点（合格）

| 監査軸 | 結果 | 根拠 |
|---|---|---|
| Ranking 混入 | **なし** | `FORBIDDEN_FIELDS` が `rank/ranking/score/priority/best/selected_candidate` を persist 時に拒否。候補に order/rank フィールド無し・`is_unordered=True`。ランク計算ロジック皆無 |
| Recommendation 混入 | **なし** | `recommendation/recommended` を構造的禁止。approval は permit/block のみ。候補 `is_not_recommendation` |
| TTFR-G/TTFR-P 混同 | **なし** | store が `ttfr_p/combined_metric/relief_count_kpi/reach_gap_estimate` を persist 拒否。ttfr_g に分離フラグ群。合算/平均/KPI 計算はコード上存在しない |
| 人間承認回避（主経路） | **防止** | execution は `execute()` の二鍵ゲート（permit ∧ active consent ∧ verified ∧ not halted）のみが SUPPORT_EXECUTIONS に append。候補は accepted_support_forms からのみ派生（捏造なし）、検証は4条件未充足で raise（held） |
| Person Domain seal（フィールド） | **成立** | `owner_id/owner_need/person_relief` を構造的禁止。execution に `no_person_domain_interaction/no_owner_interaction` |
| consent 境界 | **成立** | `obtained=False` で raise（statement≠consent）、`excludes_owner/participation/representation`、Resource Acceptance 層固定 |
| memory profiling | **なし** | memory に gateway 識別子フィールド無し（`links_no_actor`）、check が `gateway_ref/gateway_id/gateway` の混入を違反検出。学習は type 集計のみ |
| append-only / 書込ガード | **成立** | append のみ。`_guard_path` が Dan-Go/Mujin/agent_commons/サブツリー外を拒否 |

---

## B. 検出された問題（重要度順）

### B-1 【Medium・実バグ】F-18 履歴セマンティクス違反（execution check_invariants）
- **場所:** `execution_builder.check_invariants()` L112-115 が `two_keys_present()`（L42-59・`is_halted` を含む）を**過去の execution に再適用**する。
- **問題:** ある execution が作成時には有効でも、後に当該 bottleneck に対し withdrawal が記録されると、`two_keys_present` が `(False, "halted")` を返し、**過去の有効な execution が「persisted but two keys not present (halted)」として偽陽性の違反になる。**
- **F-18 違反:** 「Withdrawal voids future not irreversible past」。過去の正当な execution を遡って無効扱いするのは仕様違反。stack_audit の static_violations が withdrawal 後に虚偽の違反を報告する。
- **再現:** verify→candidate→permit→consent→execute（OK）→ withdraw(bottleneck) → `execution_builder.check_invariants()` が当該 execution を違反列挙。
- **影響:** 監査の正確性を損なう（虚偽違反）。runtime の安全性自体は損なわれない（execute は正しく halt する）。

### B-2 【Medium・誤認リスク】CLI のアクションコマンドが status-only
- **場所:** `cli.py` の `COMMANDS` が `execute/approve/consent/withdraw/...` を各 builder の `main()`（**状態表示のみ**）に対応付けている。
- **問題:** `python -m bridge.gateway_support.cli execute` は execution を**実行しない**——記録一覧を print するだけ。引数も取らない。アクション関数（`execute()/record_approval()/record_gateway_consent()/record_withdrawal()`）は CLI から到達不能。
- **評価:** 「自動実行なし」「承認回避経路なし」という観点では**安全側**（CLI から実行できない＝便利な回避経路が無い）。しかし**コマンド名がアクションを示唆**し、オペレータが「実行された」と誤認しうる（honesty 問題・Reality Correction の精神に反する）。
- **影響:** 機能不全＋誤認。仕様上の危険ではないが、運用上の明確性を欠く。

### B-3 【Low-Med・正確性】TTFR-G 時計反転の未ガード
- **場所:** `ttfr_g_builder.build()` の `secs = (t1 - t0).total_seconds() if (t0 and t1) else None`。
- **問題:** `relief_observed_at < edge_observed_at`（T1<T0）の場合、**負の ttfr_g_seconds** を記録する。データ誤りや timezone 不整合時に無意味/負の TTFR-G が persist される。
- **F-17 整合:** 会計の整合性を欠く。負の TTFR-G は held とすべき。

### B-4 【Low・防御多重化不足】二鍵ゲートは preventive だが store 直書きで回避可能
- **場所:** `store.append_jsonl` は `FORBIDDEN_FIELDS` のみ検査。二鍵ゲート・base_invariants の有無は検査しない。
- **問題:** `store.append_jsonl(SUPPORT_EXECUTIONS_JSONL, {...})` を直接呼べば二鍵ゲートを回避して execution を persist できる（検出は B-1 のバグを抱える check_invariants のみ＝detective-only）。
- **評価:** コード runtime では直書き回避は原理的に避けにくいが、現状は preventive 層が builder にしか無い。**store レベルの最小限の構造ガード**が望ましい。

### B-5 【Low・F-17 衛生】memory 学習が relief_observed の生カウントを露出
- **場所:** `memory_builder.learn_support_pattern_types()` の `by_outcome_type` が `relief_observed` の件数を含む。
- **問題:** F-19 の type 集計は許可されるが、`relief_observed` 件数は **relief-count（F-17 が KPI 化を禁ずる）** に隣接する surface。最大化ロジックは存在しないが、この値を KPI/目標に使えば F-17 違反になる。
- **評価:** 現状違反ではないが、ガード/明示ラベルが望ましい。

### B-6 【Low・person-domain 衛生】自由テキストの person-data 未スキャン
- **場所:** `reason`（withdrawal）, `consent_source`（consent）, `public_source_url`, `gateway_ref` 等のオペレータ入力文字列。
- **問題:** Person Domain seal は**フィールド名**（owner_id 等）に対しては構造的だが、**自由テキスト内容**の person-data 混入は検査しない（G-3 の voice 露出ガードのような content scan が無い）。
- **評価:** オペレータ責任の領域だが、軽量スキャン or 運用ガイダンスが望ましい。

---

## C. 情報提供（設計上の前提・残余・違反ではない）

- **C-1 verified status は静的:** `verified_bottleneck.status` は append-only で "verified" のまま。観測性の喪失は明示的 `verification_lost` withdrawal を要し、自動失効/再検証は無い（human-driven・設計通り）。文書化推奨。
- **C-2 検証・relief は operator-asserted bool:** `self_stated/public/currently_observable/inference_free` と `relief_observed` は人間の主張を記録するのみで、runtime は独立 fetch/確認しない（F-11 の human-reviewed observable condition と整合・JAR レポートと同型）。trust boundary として文書化推奨。
- **C-3 withdrawal は bottleneck 粒度で over-halt:** 1 つの support_form の consent 撤回が当該 bottleneck の全 form を halt する（fail-closed・安全側）。F-18 の per-key 意味論より粗いが、安全側ゆえ許容。
- **C-4 consent の status="active" フィルタは実質的に常時 active:** 撤回は別 withdrawal レコードで表現され consent 行は不変（append-only）。halt は `is_halted` が担保。`active_consent` の status フィルタは現状ほぼ no-op（誤解を招くため文書化 or 撤回参照に統一を検討）。

---

## D. 修正提案（コミット単位・未実装）

> いずれも `bridge/gateway_support/` 内に閉じる。Dan-Go/Mujin/agent_commons へ影響なし。実装は承認後。

### Commit 1 【Medium】fix: F-18 history semantics in execution audit
- `execution_builder` に halt を含まない `keys_existed(candidate_id)`（permit ∧ active consent ∧ verified、`is_halted` を除く）を追加。
- `check_invariants()` の再検証を `two_keys_present` → `keys_existed` に変更（過去 execution に halt を遡及適用しない）。
- `is_halted` は `execute()` の**新規** execution ゲートにのみ残す。
- 追加テスト: execute→withdraw 後に `check_invariants()` が 0 違反であること（F-18 履歴不変）。
- 影響範囲: `execution_builder.py` のみ。

### Commit 2 【Low-Med】fix: guard TTFR-G clock inversion
- `ttfr_g_builder.build()` で `t1 >= t0` を要件化。反転時は `ttfr_g_seconds=None` ＋ `status="held_clock_inversion"` ＋ `clock_inversion=True` とし、負値を記録しない。
- `check_invariants()` に「ttfr_g_seconds が負でないこと」を追加。
- 影響範囲: `ttfr_g_builder.py` のみ。

### Commit 3 【Medium】feat/clarify: CLI honest action surface
- 案A（最小・明確化）: status 系コマンドを `show-<layer>` にリネームし、`COMMANDS` の docstring に「これらは read-only。アクションは Python API を要する」と明記。
- 案B（推奨・機能化）: 引数を取るアクション subcommand を追加（`verify-bottleneck/approve/consent/execute/withdraw`）。各々が named-human 引数を必須化し、実行前に内容を表示して明示確認（自動実行なし・二鍵ゲートは execute() を経由）。`report/audit/show-*` は read-only のまま。
- 影響範囲: `cli.py`（＋必要なら各 builder に薄い `parse_args`）。
- 監査観点: 案B でも回避経路を増やさない（execute() の二鍵ゲートを必ず経由）。

### Commit 4 【Low】harden: store-level write invariant
- `store.append_jsonl` に base_invariants 必須化を追加（不足なら raise）。execution など主要レコードは builder 経由を前提とする旨を docstring に明記。
- （任意）execution レコードは「append 前に candidate/approval/consent 参照が存在する」軽量チェックを store ではなく専用 appender に置く案も併記。
- 影響範囲: `store.py`（＋docstring）。

### Commit 5 【Low】hygiene: keep relief outcome out of KPI surface
- `learn_support_pattern_types()` の戻り値に `not_a_kpi: True`/`no_maximization: True` を付与し、`relief_observed` カウントを「観測アウトカム種別の頻度（F-19 type 集計）であり KPI/目標ではない」と明示。必要なら relief 件数を別関数に隔離。
- 影響範囲: `memory_builder.py` のみ。

### Commit 6 【Low】doc/hygiene: trust boundaries + free-text person-data note
- C-1/C-2/C-4 を各 module docstring と `gateway_support_report.md` に明記（verified 静的・operator-asserted・active フィルタ）。
- 自由テキストフィールドへの person-data 混入禁止を運用ガイダンス化（任意で軽量 content scan のフックを設計）。
- 影響範囲: docstring / report テンプレート（コードロジック不変）。

---

## E. 優先度と結論

| 優先 | コミット | 理由 |
|---|---|---|
| 1 | Commit 1 | 実バグ（F-18 違反・監査の虚偽違反） |
| 2 | Commit 3 | 誤認リスク（CLI がアクションを示唆して実行しない） |
| 3 | Commit 2 | TTFR-G 会計の正確性 |
| 4 | Commit 4 | 防御多重化（直書き回避の preventive 化） |
| 5 | Commit 5, 6 | 衛生・文書化 |

- **重大な仕様違反・境界漏れ・Ranking/Recommendation 混入・TTFR 混同・人間承認の主要回避経路は検出されず。** コア runtime（F-9〜F-20）の安全境界は成立している。
- 検出された問題は (1) 監査ロジックの履歴バグ、(2) CLI の明確性、(3) 会計の端数ガード、(4) 防御多重化の不足が中心で、いずれも `bridge/gateway_support/` に閉じた局所修正で解消可能。
- **本報告は監査のみ。実装・commit・push は行っていない。** Commit 1〜6 は承認後に着手する。

---

*本監査は実 record ゼロ（全層空・正当）の静的＋構造監査である。最重要修正は Commit 1（F-18 履歴セマンティクス）。Ranking/Recommendation/TTFR 混同/承認回避の主経路は構造的に封鎖されており、Reach Gap・person relief を実装しない非目標も保持されている。*
