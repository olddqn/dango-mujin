# Phase G-2: Operational Hardening (Implementation-Ready Spec)

- **Status:** 実装準備仕様。**設計レビューでなく、承認後に実行する exact な手順・差分・検証・rollback。** 本ドキュメント自体はコード/データ/commit/push なし。
- **Date:** 2026-06-21
- **Source of truth:** [G1_EXECUTION_PREPARATION.md](G1_EXECUTION_PREPARATION.md)
- **検証済み前提（code-level）:**
  - `store.py`: `DATA_DIR = MUJIN_DIR/"data"`、`read_jsonl/append_jsonl`、**append-only 不変条件（既存行を rewrite/delete しない・ADR-001/002）**。
  - `commons.py`: `VOICE_JSONL = DATA_DIR/"voice_records.jsonl"`、`list_voices()→read_jsonl(VOICE_JSONL)`、`get_voice`、`register_voice`/`register_voice_submission`（→`_post(VOICE_JSONL,...)`）。
  - `.gitignore`: `data/` 非対象。git hooks: 稼働なし。
  - 実在外部参照は `voice-006`（JAR）の 1 レコードのみ。

> **append-only との整合（重要）:** store の append-only は**runtime 書込規律**。本フェーズの voice 再配置（privacy redaction / sealing）は**repo メンテナンス操作**であり、(1) 既存ファイルは可能な限り `git mv`（intact 移動・行 rewrite なし）で扱い、(2) public ファイルからの除去は `correction_log.jsonl` に redaction event を append して記録する。**redaction は append-only の例外でなく、append-only の記録規律に従って明示ログする。**

---

## A. Implementation Plan

### A.1 目標 storage layout
```
bridge/mujin/data/
  voice_records.jsonl                     # PUBLIC: consented/public-safe な real voice のみ（移行後は空）
  fixtures/
    voice_records.fixtures.jsonl          # voice-001..005（is_fixture:true 付与）= 公開だが明示 test
    README.md                             # 「試験データ・実在の需要/個人/組織を表さない」
  private/                                # GITIGNORED（追跡しない）
    .gitkeep
    voice_records.private.jsonl           # voice-006（JAR）= sealed・gateway consent 待ち
```

### A.2 分類規則（guard と list_voices が共有）
- `is_voice_record(r)` := `r.get("record_type")=="voice_record"` または `original_statement` 非空。
- `is_fixture(r)` := `r.get("is_fixture") is True` または `source_url` ドメイン ∈ PLACEHOLDER(`example.org/.com/.net, ngo.example, gov.example`) または `source_url` 空。
- `is_public_safe(r)` := `is_fixture(r)` または `r.get("gateway_consent") is True` または `r.get("public_safe") is True`。
- **public ファイルに許されるのは `is_public_safe(r)` のみ。** それ以外（real・未 consent）は private 行。**fail-closed**（不明は private 扱い）。

### A.3 実装順序（承認後・防御優先）
1. **guard 導入（A.4-3）** ← 先に防壁。これ以降 public への real voice 混入を push 段階で阻止。
2. **storage 分離（A.4-1, A.4-2）** ← fixtures/private へ再配置。
3. **コード routing（A.4-4）** ← list_voices/get_voice を分離レイアウト対応に。
4. **gitignore（A.4-5）** ← private/ 非追跡。
5. （別承認）既 push 済 voice_records.jsonl の remote/history 整序は separate op（A.6）。

---

## B. File Diff Plan（exact・承認後に適用）

### B.1 新規: `bridge/mujin/data/fixtures/voice_records.fixtures.jsonl`
内容 = 現 `voice_records.jsonl` の voice-001..005 各行に `"is_fixture": true` を追加したもの（**新規ファイル・既存行 rewrite でない**）。生成コマンド（承認後）:
```bash
mkdir -p bridge/mujin/data/fixtures bridge/mujin/data/private
python3 - <<'PY'
import json
from pathlib import Path
src=Path('bridge/mujin/data/voice_records.jsonl')
rows=[json.loads(l) for l in src.read_text().splitlines() if l.strip()]
fix=[r for r in rows if r.get('voice_id') in {'voice-001','voice-002','voice-003','voice-004','voice-005'}]
priv=[r for r in rows if r.get('voice_id')=='voice-006']
with open('bridge/mujin/data/fixtures/voice_records.fixtures.jsonl','w',encoding='utf-8') as f:
    for r in fix:
        r['is_fixture']=True
        f.write(json.dumps(r,ensure_ascii=False)+'\n')
with open('bridge/mujin/data/private/voice_records.private.jsonl','w',encoding='utf-8') as f:
    for r in priv:
        r['sealed']=True; r['public_safe']=False
        f.write(json.dumps(r,ensure_ascii=False)+'\n')
Path('bridge/mujin/data/private/.gitkeep').write_text('')
print('fixtures:',len(fix),'private:',len(priv))
PY
```

### B.2 新規: `bridge/mujin/data/fixtures/README.md`
```
# Mujin test fixtures
These records are SEED/TEST DATA. They do NOT represent real needs, real
individuals, or real organizations. Source domains are RFC-reserved
placeholders (example.org / ngo.example / gov.example). Do not treat as real
Voices. Marked is_fixture:true.
```

### B.3 公開 `voice_records.jsonl` の redaction（exact）
- 6 行 → 0 行（consented/public-safe 行のみ残す。現状そのような行は無いので空）。
- **append-only 整合:** 行の in-place mutation でなく「公開ファイルの内容除去」。`correction_log.jsonl` に redaction event を append:
```bash
python3 - <<'PY'
import json,hashlib
from datetime import datetime,timezone
from pathlib import Path
ev={"record_type":"correction","correction_type":"voice_redaction_for_privacy",
    "reason":"separate fixtures + seal real org voice (voice-006/JAR) from public surface",
    "removed_voice_ids":["voice-001","voice-002","voice-003","voice-004","voice-005","voice-006"],
    "moved_to":{"fixtures":["voice-001..005"],"private":["voice-006"]},
    "append_only_note":"public file content removed as privacy maintenance; originals preserved in fixtures/ (test) and private/ (sealed)",
    "human_review_required":True,"created_at":datetime.now(timezone.utc).isoformat().replace('+00:00','Z')}
ev["event_hash"]=hashlib.sha256(json.dumps({k:v for k,v in ev.items() if k!='event_hash'},sort_keys=True,ensure_ascii=False).encode()).hexdigest()
with open('bridge/mujin/data/correction_log.jsonl','a',encoding='utf-8') as f:
    f.write(json.dumps(ev,ensure_ascii=False)+'\n')
open('bridge/mujin/data/voice_records.jsonl','w',encoding='utf-8').close()  # truncate to empty (public real-consented only)
print('redaction logged; public voice_records.jsonl truncated')
PY
```

### B.4 `commons.py` 差分（exact）
**after 既存 `VOICE_JSONL = DATA_DIR / "voice_records.jsonl"`（line 55）に追加:**
```python
FIXTURES_DIR         = DATA_DIR / "fixtures"
PRIVATE_DIR          = DATA_DIR / "private"
VOICE_FIXTURES_JSONL = FIXTURES_DIR / "voice_records.fixtures.jsonl"
VOICE_PRIVATE_JSONL  = PRIVATE_DIR  / "voice_records.private.jsonl"
```
**`list_voices()` を置換:**
```python
def list_voices(include_fixtures: bool = False,
                include_private: bool = False) -> list[dict[str, Any]]:
    """Public dashboard default: consented/public-safe real voices only.
    Fixtures and sealed (private) voices are opt-in for internal/dev use."""
    voices = read_jsonl(VOICE_JSONL)
    if include_fixtures:
        voices += read_jsonl(VOICE_FIXTURES_JSONL)
    if include_private:
        voices += read_jsonl(VOICE_PRIVATE_JSONL)
    return voices
```
**`get_voice()` を置換（内部 lookup は全ソース横断・但し private は明示時のみ表示用に使わない）:**
```python
def get_voice(voice_id: str) -> dict[str, Any] | None:
    return next((v for v in list_voices(include_fixtures=True, include_private=True)
                 if v.get("voice_id") == voice_id), None)
```
**（任意・belt-and-suspenders）write-time routing:** `register_voice`/`register_voice_submission` の `_post(VOICE_JSONL, ...)` を、`is_public_safe` 判定で `VOICE_JSONL`（public）か `VOICE_PRIVATE_JSONL`（sealed）に振り分けるヘルパ `_voice_target(extra)` 経由に変更（実 individual・未 consent は private へ）。コア分離には必須でないが、push 前に write 段で阻止できる。

### B.5 `.gitignore` 追加（末尾）
```
# Sealed real/individual voice data — never tracked, never public
bridge/mujin/data/private/
!bridge/mujin/data/private/.gitkeep
```

### B.6 新規 guard: `bridge/mujin/tools/voice_exposure_guard.py`（full・spec）
```python
#!/usr/bin/env python3
"""Pre-push guard: refuse to expose real, unconsented voice data publicly.
Scans tracked public data files for voice records that are neither fixtures
nor public-safe (gateway_consent/public_safe). Fail-closed."""
import json, sys, glob
from pathlib import Path
from urllib.parse import urlparse

PLACEHOLDER = {"example.org","example.com","example.net","ngo.example","gov.example",""}
PUBLIC_DATA = sorted(glob.glob("bridge/mujin/data/*.jsonl"))  # private/ excluded (subdir)

def is_voice(r):     return r.get("record_type")=="voice_record" or bool((r.get("original_statement") or "").strip())
def is_fixture(r):
    if r.get("is_fixture") is True: return True
    u=r.get("source_url") or ""
    d=urlparse(u).netloc.lower().replace("www.","") if u else ""
    return d in PLACEHOLDER
def is_public_safe(r):
    return is_fixture(r) or r.get("gateway_consent") is True or r.get("public_safe") is True

def main():
    violations=[]
    for f in PUBLIC_DATA:
        for i,line in enumerate(Path(f).read_text(encoding="utf-8").splitlines(),1):
            line=line.strip()
            if not line: continue
            try: r=json.loads(line)
            except Exception: continue
            if is_voice(r) and not is_public_safe(r):
                violations.append(f"{f}:{i} voice_id={r.get('voice_id')} (real/unconsented voice in public file)")
    # also block staging of anything under data/private/
    for f in glob.glob("bridge/mujin/data/private/*.jsonl"):
        violations.append(f"{f} (private voice data must never be tracked/pushed)")
    if violations:
        sys.stderr.write("VOICE EXPOSURE GUARD: push refused.\n")
        for v in violations: sys.stderr.write("  - "+v+"\n")
        sys.stderr.write("Fix: move to fixtures/ (is_fixture) or private/, or set gateway_consent after consent.\n")
        sys.stderr.write("Override (deliberate, audited): VOICE_GUARD_OVERRIDE=1\n")
        return 1
    return 0

if __name__=="__main__":
    import os
    sys.exit(0 if os.environ.get("VOICE_GUARD_OVERRIDE")=="1" else main())
```

### B.7 新規 hook: `.githooks/pre-push`（tracked）＋ 設定
```bash
# .githooks/pre-push
#!/bin/sh
python3 bridge/mujin/tools/voice_exposure_guard.py || exit 1
```
有効化（承認後）:
```bash
chmod +x .githooks/pre-push bridge/mujin/tools/voice_exposure_guard.py
git config core.hooksPath .githooks
```

---

## C. Verification Checklist（承認後・各 ✓ を確認）

| # | 検証 | コマンド | 期待 |
|---|---|---|---|
| C1 | 公開 voice_records.jsonl に real/未 consent voice が無い | `python3 bridge/mujin/tools/voice_exposure_guard.py; echo $?` | `0`（guard pass） |
| C2 | fixtures は全て is_fixture | `python3 -c "import json,pathlib;print(all(json.loads(l).get('is_fixture') for l in pathlib.Path('bridge/mujin/data/fixtures/voice_records.fixtures.jsonl').read_text().splitlines() if l.strip()))"` | `True` |
| C3 | private に voice-006 がある | `python3 -c "import json,pathlib;print([json.loads(l).get('voice_id') for l in pathlib.Path('bridge/mujin/data/private/voice_records.private.jsonl').read_text().splitlines() if l.strip()])"` | `['voice-006']` |
| C4 | private/ は gitignored | `git check-ignore bridge/mujin/data/private/voice_records.private.jsonl && echo IGNORED` | `IGNORED` |
| C5 | 公開 voice_records.jsonl は空 | `wc -l < bridge/mujin/data/voice_records.jsonl` | `0` |
| C6 | list_voices() default が public のみ | `python3 -c "from bridge.mujin.platform import commons as c; print(len(c.list_voices()))"` | `0`（現状 public 0） |
| C7 | get_voice は private/fixtures も解決 | `python3 -c "from bridge.mujin.platform import commons as c; print(bool(c.get_voice('voice-006')), bool(c.get_voice('voice-001')))"` | `True True` |
| C8 | guard negative control（合成 real voice を public に投入→reject） | 合成行を一時投入し guard 実行 | exit `1`・対象を列挙 |
| C9 | guard positive control（fixture/consented は pass） | is_fixture/gateway_consent 行のみで guard 実行 | exit `0` |
| C10 | correction_log に redaction event | `tail -1 bridge/mujin/data/correction_log.jsonl | python3 -c "import json,sys;print(json.load(sys.stdin)['correction_type'])"` | `voice_redaction_for_privacy` |
| C11 | Dan-Go byte-identical（store 外触れず） | globe/gitsea/sutable のハッシュ比較 | 不変（101 files） |
| C12 | core.hooksPath 設定 | `git config core.hooksPath` | `.githooks` |

---

## D. Rollback Checklist（各変更は可逆・承認後の適用を取り消す手順）

| # | 取消対象 | コマンド | 結果 |
|---|---|---|---|
| D1 | guard 無効化 | `git config --unset core.hooksPath` | hook 無効 |
| D2 | private/ gitignore 取消 | `.gitignore` の private 行 2 行を削除 | 元状態 |
| D3 | commons.py 差分取消 | `git checkout -- bridge/mujin/platform/commons.py`（未 commit なら）／該当 4 ブロックを手動 revert | 元の list_voices/get_voice/path |
| D4 | storage 復元（最重要・可逆） | `python3 - <<'PY'`：fixtures+private を結合し `voice_records.jsonl` を 6 行に復元（is_fixture/sealed フラグ除去） | 元の 6 行 voice_records.jsonl |
| D5 | 生成物削除 | `rm -rf bridge/mujin/data/fixtures bridge/mujin/data/private bridge/mujin/tools/voice_exposure_guard.py .githooks` | 新規物消去 |
| D6 | correction_log の redaction event | append-only ゆえ削除せず、打消し event を append（`correction_type:"voice_redaction_rollback"`） | 履歴整合 |

**D4 復元スクリプト（exact）:**
```bash
python3 - <<'PY'
import json
from pathlib import Path
out=[]
for p in ['bridge/mujin/data/fixtures/voice_records.fixtures.jsonl',
          'bridge/mujin/data/private/voice_records.private.jsonl']:
    pp=Path(p)
    if pp.exists():
        for l in pp.read_text().splitlines():
            if l.strip():
                r=json.loads(l); r.pop('is_fixture',None); r.pop('sealed',None); r.pop('public_safe',None)
                out.append(r)
out.sort(key=lambda r:r.get('voice_id',''))
with open('bridge/mujin/data/voice_records.jsonl','w',encoding='utf-8') as f:
    for r in out: f.write(json.dumps(r,ensure_ascii=False)+'\n')
print('restored', len(out), 'voices')
PY
```
- **rollback 安全性:** すべて未 commit の working-tree 変更ゆえ `git checkout/restore` と D4 で完全復元可。commit 済でなければ remote 影響なし。

---

## E. Scope boundary（本フェーズで扱わない・別承認）

- **既 push 済 `voice_records.jsonl`（remote tip + history）からの除去:** B.3 は working-tree とローカル次 commit を整序するが、**既に public github に push された 6 レコードの除去は別 op**（approved commit で tip から消す＋必要なら history scrub `git filter-repo`/force-push）。これは destructive・outward ゆえ **本フェーズ外・要 separate Human Approval**。
- **JAR consent 取得 / 外部 fetch（G-1 P3a/P3c）:** outward 行為ゆえ本フェーズ外。
- 本フェーズは「**今後 real voice を public に出さない防壁＋既存の test/real を working-tree で分離する exact 手順**」までを fully specify する。

---

## F. 完了条件（本フェーズ）

- ✅ fixture-separation 実装設計（A.1/A.4/B.1-B.3）= exact。
- ✅ pre-push voice-data guard 設計（B.6/B.7）= full script + hook + 有効化。
- ✅ public/private storage boundary 設計（A.1/A.2/B.4/B.5）= layout + routing + gitignore。
- ✅ file diff plan（B）= per-file exact（新規ファイル全文・commons.py 差分・gitignore 行）。
- ✅ verification checklist（C・12項）= コマンド + 期待値、negative/positive control 含む。
- ✅ rollback checklist（D・6項）= exact 逆操作、完全復元スクリプト。
- ✅ append-only 整合（redaction を correction_log に明示ログ）。
- ✅ scope boundary（既 push 分の除去は別承認）= 明示。
- ✅ コード/データ/commit/push なし——全て承認後手順。新規レビュー文書なし。

> **Operational hardening fully specified.** 承認をいただければ A.3 の順序（guard→分離→routing→gitignore）で実行する。既 push 済レコードの remote/history 整序を含めるかは E の別承認事項として併せて確認されたい。
