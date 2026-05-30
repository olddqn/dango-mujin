# ASSET_TOML_MAPPING.md — Field-by-Field Explanation

Explains every field in `asset.toml` and how it relates to
GITSEA asset registration and Dan-Go tooling.

**Canonical format uses English ASCII section names.**
An earlier version of this repo used Japanese quoted section names
(`["リポジトリ"]`, etc.). Those are valid TOML 1.0 but GITSEA does not
recognise them. The current canonical format is shown below.

---

## Full Example (Canonical / GITSEA Format)

```toml
[repo]
name = "olddqn/dango-mujin"
license = "MIT"

[splits]
"0x89b38ff776565f095b3cd46C5f35EAb27506417C" = 100

[royalties]
multiplier = 1.0
acceptance = 1.0

[insurance]
merge_insurance = true
```

---

## Section: `[repo]` — Repository

| Key | Type | Description |
|-----|------|-------------|
| `name` | string | Repository identifier in `owner/repo` format |
| `license` | string | SPDX license identifier (e.g. `MIT`, `Apache-2.0`) |

**Dan-Go use:** `asset_toml_reader.py` extracts these for the registration snapshot.
**GITSEA use:** Used to identify the repository during asset registration.

---

## Section: `[splits]` — Split

Each key is a wallet address (Ethereum-format). Each value is an integer percentage.

```toml
[splits]
"0xWALLET_ADDRESS" = 100
```

**Rules:**
- All values must sum to exactly 100
- Wallet addresses must be quoted (they start with `0x`, which begins with a digit — not a valid bare key in TOML 1.0)
- Multiple addresses allowed: `"0xAlice" = 60`, `"0xBob" = 40`

**Dan-Go use:** `asset_toml_reader.py` validates the sum. `split_valid: true` iff sum == 100.
**GITSEA use:** Determines how stream proceeds are distributed between contributors.

**keccak256 note:** GITSEA may use keccak256 for address hashing internally.
Dan-Go does not compute keccak256. Verify on-chain hashes with a trusted
Ethereum tool (e.g. `cast keccak` from Foundry).

---

## Section: `[royalties]` — Royalty

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `multiplier` | float | 1.0 | Scales royalty yield. 1.0 = no scaling. |
| `acceptance` | float | 1.0 | Royalty acceptance rate. 1.0 = full acceptance. |

**Dan-Go use:** Read by `asset_toml_reader.py` as advisory metadata.
**GITSEA use:** Used when computing stream yield for this repository.

---

## Section: `[insurance]` — Insurance

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `merge_insurance` | bool | false | Whether merge insurance is requested |

**Dan-Go use:** Read by `asset_toml_reader.py` as a boolean flag.
**GITSEA use:** May activate merge protection for stream events.

---

## TOML 1.0 Key Rules

| Key type | Rule | Example |
|----------|------|---------|
| Bare key | ASCII letters, digits, `-`, `_` only | `merge_insurance`, `multiplier` |
| Quoted key | Any character when double-quoted | `"0x89b3..."` |
| Section header | Same rules as keys | `[repo]`, `[splits]` |

Section names `[repo]`, `[splits]`, `[royalties]`, `[insurance]` are all
valid bare keys (ASCII only). Wallet address keys must be quoted because
they start with a digit (`0`), which is only valid in the middle of a bare key,
not at the start.

---

## Reading with Dan-Go Tooling

```bash
# Human-readable summary (checks GITSEA format compatibility)
python bridge/gitsea/runtime/asset_toml_reader.py asset.toml

# Full JSON output
python bridge/gitsea/runtime/asset_toml_reader.py asset.toml --json

# Single field
python bridge/gitsea/runtime/asset_toml_reader.py asset.toml --field split

# Registration snapshot (advisory, not submitted)
python bridge/gitsea/runtime/asset_registration_snapshot.py asset.toml --save
```

---

## Legacy Japanese Format (do not use)

Earlier Dan-Go versions used quoted Japanese section names. These parse correctly
with Python 3.11+ `tomllib` but GITSEA does not recognise them:

```toml
# ✗ Not recognised by GITSEA (legacy Dan-Go format)
["リポジトリ"]
"名前" = "olddqn/dango-mujin"
"ライセンス" = "MIT"

["分割"]
"0x89b38ff776565f095b3cd46C5f35EAb27506417C" = 100

["著作権料"]
"乗数" = 1.0
"受容度" = 1.0

["保険"]
merge_insurance = true
```

```toml
# ✓ GITSEA canonical format (use this)
[repo]
name = "olddqn/dango-mujin"
license = "MIT"
```

`asset_toml_reader.py` emits a `format_warning` when it detects legacy keys.

---

*authority: none · advisory · stdlib only · no secrets · no wallet*
