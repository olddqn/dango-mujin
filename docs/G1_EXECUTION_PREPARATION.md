# Phase G-1: Execution Preparation (Operational Plans & Protocols)

- **Status:** 実行準備（plans / protocols / verification procedures）。**設計レビューでなく実行準備。** すべて Human Approval gate 付き。本ドキュメント自体はコード/データ/commit/push なし。
- **Date:** 2026-06-21
- **前提:** F-series（F-9〜F-25・architecturally complete）, 公開監査, 評価フレーム。**本セッションでは実行しない**——各アクションは承認後に実行する手順書。

> **検証済み現状（事実）:**
> - `bridge/mujin/data/` は 24 ファイル・全 public（gitignore なし）・`commons.py` が読込。
> - **実在の外部実体を参照するのは全 24 ファイル中 `voice-006`（refugee.or.jp / JAR）の 1 レコードのみ。** 他はすべて seed/test fixture（placeholder ドメイン or source なし）。
> - JAR は `gateway_registry` に**未登録**——voice-006 の source としてのみ存在。
> - ∴ 「実データ表面」は実質 1 レコード。分離・封印・JAR 対応は局所的で済む。

---

## 0. 現状分類（verified, no PII）

| 対象 | 分類 | 公開状態 |
|---|---|---|
| voice-001〜005 | seed/test fixture（placeholder/no source） | public |
| **voice-006** | **実在組織 JAR の既公開 NGO 声明** | public |
| 他 23 データファイル | seed/test fixture（実外部参照なし） | public |
| gateway_registry（7行） | 全 fixture（実ドメインなし・JAR 不在） | public |

**結論:** 個人 PII 露出 0。実在実体参照は voice-006 のみ。整序は局所。

---

## 1. Test Fixture Separation Plan（優先度1）

**目的:** test fixture を実データと明示分離し、公開表面が test を実需要と誤認させないようにする（Reality Correction / Jammy House 教訓）。

### オプション
| 案 | 内容 | 長所 | 短所 |
|---|---|---|---|
| A | 各 fixture に `"is_fixture": true` を付与（in-place） | 最小変更・file 構造維持 | 依然 public・誤認は弱く残る |
| B | `*.fixtures.jsonl` に分離（real は本体に残す） | 構造的に明確 | loader 変更が要る場合あり |
| **C（推奨）** | `bridge/mujin/data/fixtures/` サブツリーへ移動＋`is_fixture` 付与＋README | 最も明確・将来の real data と物理分離 | path 変更ゆえ loader/参照更新が要る |

### 推奨手順（**承認後**に実行）
1. `bridge/mujin/data/fixtures/` を作成。
2. fixture 24 ファイル中、実データ（voice-006 を含む voice_records）以外を `fixtures/` へ `git mv`。
3. voice_records は split: `voice_records.jsonl`（voice-006 のみ）＋ `fixtures/voice_records.fixtures.jsonl`（voice-001〜005、各 `is_fixture:true`）。
4. `commons.py` の loader を「本体＋（開発時のみ）fixtures」読込に更新（公開実行時は fixtures 非読込）。
5. `fixtures/README.md` に「これは試験データであり実在の需要・個人・組織を表さない」と明記。

### 検証手順
```
# 承認後の検証スクリプト（案）
python3 - <<'PY'
import json,glob
from pathlib import Path
# (1) 本体 data/*.jsonl に placeholder ドメイン由来レコードが残っていないこと
# (2) fixtures/*.jsonl は全レコード is_fixture==True
# (3) voice_records.jsonl は voice-006 のみ・refugee.or.jp
PY
```
**判定基準:** 本体に fixture 0 / fixtures に real 0 / voice_records は real 1（voice-006）。

> **承認 gate:** path 移動・data 変更ゆえ Human Approval 必須。

---

## 2. Voice Storage Policy（公開/非公開境界）（優先度2）

**分類規則（F-21/F-22/F-25 準拠）:**

| voice 種別 | 公開可否 | 保管先 |
|---|---|---|
| 実在 individual の声（非同意） | **不可（封印）** | private（gitignore / 非公開ストア） |
| 実在 individual の声（consent 済・specific） | consent 範囲で可 | consent 記録と対で |
| 実在組織の既公開声明（例: JAR/voice-006） | gateway consent 規律（F-10/F-14）に従う | §3 で決定するまで保留扱い |
| seed/test fixture | 公開可（ただし `is_fixture` 明示・§1） | `fixtures/` |

**現状適用:** 実在 individual の声は 0（封印対象なし）。voice-006 は組織の既公開声明ゆえ §3 で扱う。

### Enforcement（実装案・承認後）
1. **`.gitignore` に private 領域を追加:**
   ```
   # Sealed real person/individual voice data — never public
   bridge/mujin/data/private/
   *.sealed.jsonl
   ```
2. **pre-commit / pre-push guard（スクリプト spec）:** commit/push 対象に `original_statement` 等を持つ未分類 voice レコードが含まれたら **block**。判定: voice レコードで `is_fixture!=true` かつ source が real かつ `consent`/`gateway_consent` 不在 → reject。
3. **公開ブランチ不変条件:** public branch の voice データは `{is_fixture:true} ∪ {gateway_consent:true の組織声明}` のみ。実 individual voice は private のみ。

### 検証手順
```
# guard の単体テスト（案）: 合成の「real individual voice（consent なし）」を投入し
# guard が reject することを確認（negative control）。fixture と consent 済は pass。
```
> **承認 gate:** .gitignore 変更・guard 導入はコード/設定変更ゆえ Human Approval 必須。

---

## 3. JAR Gateway Handling Options（優先度3）

**事実:** voice-006 = JAR（refugee.or.jp）の既公開 NGO 声明。JAR は gateway_registry 未登録。gateway consent 未取得。`contact_attempted=False`・`automatic_contact_prohibited=True` 維持。

### オプション
| 案 | 内容 | consent 整合 | 推奨度 |
|---|---|---|---|
| A | JAR に association/Resource Acceptance consent を取得して継続 | 完全（F-14） | 理想・但し JAR 接触は要 approval・要 consent protocol |
| B | voice-006 を public 表面から private へ移し、observed-edge 観察のみ内部保持 | 高（晒さない・F-8 縁の内部観察は可） | **推奨（暫定）** |
| C | voice-006 を「JAR 既公開声明・未 consent association」と明示ラベルし継続 | 中（透明だが association は残る） | 次善 |
| D | voice-006 を削除 | 高（association 解消）だが observed-edge を失う | 過剰 |

### 推奨（暫定）: **B**
- 理由: JAR の声明は既に公開だが、Mujin repo で**構造化・association**するのは別行為。observed edge（F-8）の価値は内部観察で保持できる。public 表面から外せば association を露出させず、将来 A（consent 取得）に移行可能。

### JAR public bottleneck の verification（F-11 準拠・承認後）
- **public を読むのみ・引き出さない**（F-11/F-5）。refugee.or.jp の**公開ページに JAR 自身が現在述べている** bottleneck（資金/人手等）が currently observable かを確認。
- 確認できれば `verified bottleneck`（observable condition・proof でない）として記録。確認できなければ **held**（現状）。
- **承認 gate:** 外部 fetch（WebFetch 等）を行うなら outward 行為ゆえ Human Approval 必須。

---

## 4. First Real Gateway Support Simulation（DRY-RUN protocol）（優先度4）

**性質:** F-9〜F-20 のパイプラインを voice-006/JAR で**机上シミュレート**。**実支援なし・送金なし・execution なし・data 変更なし。** 目的: パイプライン論理の検証と、実投入に必要な real input の列挙。

### Dry-run steps（各 gate で halt 条件を確認）
| # | 段階（F-ref） | 入力 | gate / halt 条件 | 現状判定 |
|---|---|---|---|---|
| 1 | Observed Edge（F-9） | voice-006 | person domain 封印確認 | ✅ pass（gateway domain のみ） |
| 2 | Verified Bottleneck（F-11） | JAR 公開 bottleneck | currently observable・proof でない | ⏸ **held**（§3 verification 未実施） |
| 3 | Support Candidate（F-12） | verified bottleneck | possibility-only・複数・無順位 | ⛔ **0**（verified 不在ゆえ生成せず） |
| 4 | Approval（F-13） | candidate | gatekeeping・Action Candidate へ | ⛔ N/A（candidate 0） |
| 5 | Gateway Consent（F-14） | JAR | statement≠consent・取得要 | ⛔ **未取得** |
| 6 | Execution（F-15） | 二鍵∧verified | Resource Acceptance 範囲 | ⛔ 二鍵未成立 |
| 7 | Reality Feedback（F-16） | execution | gateway 尺度・捏造禁止 | ⛔ N/A |
| 8 | TTFR-G（F-17） | feedback | 分離会計 | ⛔ N/A |

### Simulation 結論
- **パイプラインは正しく halt する:** verified bottleneck が held ＋ gateway consent 未取得ゆえ、candidate 以降が全て 0。**無から支援を起こさない安全性が確認された。**
- **実投入に必要な real input（順序）:** (1) JAR public bottleneck の verification（§3・要 approval の外部 read）、(2) JAR の Resource Acceptance consent（要 approval の接触 protocol）。この 2 つが揃って初めて candidate→approval→execution が動く。
- **本 simulation は何も実行・生成しない。** 机上で gate を確認しただけ。

> **承認 gate:** 実 simulation を「実 JAR への接触/verification」に進めるには Human Approval 必須。dry-run（机上）は本ドキュメントで完了。

---

## 5. TTFR-G Operational Measurement（優先度5）

**目的:** TTFR-G を honest に測る運用手順。TTFR-P と分離（F-17）・捏造禁止（F-16）・gateway 無評価（F-19）。

### 計測フィールド（記録スキーマ案）
```
ttfr_g_record:
  edge_observed_at        # T0: gateway voice が最初に観察された時刻（clock start）
  bottleneck_verified_at  # verified（observable condition）になった時刻
  support_consented_at    # gateway Resource Acceptance consent 取得時刻
  support_executed_at     # 二鍵∧verified で execution 開始時刻
  relief_observed_at      # T1: gateway self-stated bottleneck が observable に解消（clock stop）
  relief_source           # gateway 自身の公開言明（self-stated・URL）
  relief_is_observable    # true（proof でなく currently observable・F-16）
  measure_owner           # "gateway_self_stated"（Mujin 推論でない）
  # 不変フラグ
  ttfr_g_not_ttfr_p: true
  not_reach_gap_reduction: true
  no_gateway_ranking: true
  excludes_owner_info: true
```

### 計測手順
1. **T0（clock start）:** observed edge（gateway voice）記録時刻。voice-006 なら既存。
2. **T1（clock stop）:** gateway が**自ら公開して**「bottleneck が解消された」と述べ、それが currently observable な時刻。**Mujin が「解消したはず」と推定してはならない**（F-16）。
3. **TTFR-G = T1 − T0。** gateway 自身の尺度。
4. **分離会計:** TTFR-G ledger は TTFR-P ledger と**別**（合算・代理・相殺禁止・F-17）。
5. **併記:** TTFR-G と Reach Gap を並置するが混ぜない（F-17 Q7）。

### Anti-fabrication 検証
- relief_is_observable が false なら TTFR-G completion を記録しない（held）。
- relief_source が public・currently observable でなければ無効。
- measure_owner が gateway_self_stated 以外なら無効（Mujin 推論禁止）。
- owner 情報が混入していたら reject（person domain 漏れ）。
- **negative control:** 「support したから解消したはず」型の合成入力で記録が reject されることを確認。

> **承認 gate:** 実 TTFR-G の記録は実 support（§4）の後にのみ発生。現状 execution 0 ゆえ TTFR-G record = 0（正しい）。スキーマ/手順は今確定、記録は実投入後。

---

## 6. Approval-gated actions（実行に承認が要る項目の一覧）

| # | アクション | 種別 | 依存 |
|---|---|---|---|
| P1 | fixtures/ への移動・voice_records split・loader 更新 | data/code 変更 | — |
| P2 | .gitignore 追加・pre-commit/pre-push guard 導入 | 設定/code | — |
| P3a | JAR public bottleneck の外部 read 検証 | outward fetch | — |
| P3b | voice-006 を private へ移動（推奨 B） | data 変更 | P2（private 領域） |
| P3c | JAR への consent 接触 | outward contact | consent protocol |
| P4 | 机上 dry-run を実 verification/接触へ進める | outward | P3a/P3c |
| P5 | 実 TTFR-G の記録 | data 生成 | 実 support 成立 |

**いずれも本セッションでは実行していない。** 上記は承認後の手順書。

---

## 7. 推奨実行順序（承認を求める際の提案）

```
1. P2（storage policy + guard）      ← 先に「実 voice が public に漏れない」防壁を立てる
2. P1（test fixture separation）     ← 誤認リスクを解消
3. P3b（voice-006 を private へ・暫定） ← association 露出を止める（可逆・将来 P3a/c へ）
   ─ ここまでで公開表面は person-data-ゼロ door に近づく ─
4. P3a（JAR public bottleneck 検証）   ← held を verified にできるか（read-only・要 approval）
5. P4（実 simulation へ）・P3c（consent） ← gateway support の実投入準備
6. P5（TTFR-G 記録）                  ← 実 support 成立後
```

- 1〜3 は防御的・可逆・person 救済を毀損しない整序。4〜6 は gateway support の実投入で、各々 consent/verification gate 付き。

---

## 8. 完了条件（本フェーズ）

- ✅ 5 優先項目すべてに concrete plan / protocol / verification procedure を提示。
- ✅ コード/データ/commit/push/公開なし——すべて承認 gate 付き手順書。
- ✅ 新規レビュー系列を作らず（constitutive 矛盾は発見されず）、実行準備に集中。
- ✅ 検証済み事実（実在実体参照は voice-006 のみ）に基づき、整序の局所性を確定。

> **次アクションは人間の承認待ち。** どの項目を承認するか（推奨順序 §7）を指示いただければ、当該手順を実行する。constitutive 矛盾は発見されていないため、新規レビュー系列は作らない。
