# ASSET_TOML_MAPPING.md — Field-by-Field Explanation

Explains every field in `asset.toml` and how it relates to
GITSEA asset registration and Dan-Go tooling.

---

## Full Example

```toml
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

---

## Section: `["リポジトリ"]` — Repository

Japanese: リポジトリ = repository

| Key | Japanese | Type | Description |
|-----|----------|------|-------------|
| `"名前"` | 名前 = name | string | Repository identifier in `owner/repo` format |
| `"ライセンス"` | ライセンス = license | string | SPDX license identifier (e.g. `MIT`, `Apache-2.0`) |

**Dan-Go use:** `asset_toml_reader.py` extracts these for the registration snapshot.
**GITSEA use:** Used to identify the repository during asset registration.

---

## Section: `["分割"]` — Split

Japanese: 分割 = division / split

Each key is a wallet address (Ethereum-format). Each value is an integer percentage.

```toml
["分割"]
"0xWALLET_ADDRESS" = 100
```

**Rules:**
- All values must sum to exactly 100
- Wallet addresses must be quoted (they start with `0x`, not ASCII-only bare keys)
- Multiple addresses allowed: `"0xAlice" = 60`, `"0xBob" = 40`

**Dan-Go use:** `asset_toml_reader.py` validates the sum. `split_valid: true` iff sum == 100.
**GITSEA use:** Determines how stream proceeds are distributed between contributors.

**keccak256 note:** GITSEA may use keccak256 for address hashing internally.
Dan-Go does not compute keccak256.

---

## Section: `["著作権料"]` — Royalty

Japanese: 著作権料 = royalty / copyright fee

| Key | Japanese | Type | Default | Description |
|-----|----------|------|---------|-------------|
| `"乗数"` | 乗数 = multiplier | float | 1.0 | Scales royalty yield. 1.0 = no scaling. |
| `"受容度"` | 受容度 = acceptance | float | 1.0 | Royalty acceptance rate. 1.0 = full acceptance. |

**Dan-Go use:** Read by `asset_toml_reader.py` as advisory metadata.
**GITSEA use:** Used when computing stream yield for this repository.

---

## Section: `["保険"]` — Insurance

Japanese: 保険 = insurance

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `merge_insurance` | bool | false | Whether merge insurance is requested |

Note: `merge_insurance` uses an ASCII bare key — no quoting needed.

**Dan-Go use:** Read by `asset_toml_reader.py` as a boolean flag.
**GITSEA use:** May activate merge protection for stream events.

---

## TOML 1.0 Key Rules

| Key type | Rule | Example |
|----------|------|---------|
| Bare key | ASCII letters, digits, `-`, `_` only | `merge_insurance` |
| Quoted key | Any Unicode when double-quoted | `"名前"`, `"0x89b3..."` |
| Section header | Same rules as keys | `["リポジトリ"]` |

Python 3.11+ `tomllib` strictly follows TOML 1.0. Unquoted Japanese
characters in key position cause `TOMLDecodeError`.

---

## Reading with Dan-Go Tooling

```bash
# Human-readable summary
python bridge/gitsea/runtime/asset_toml_reader.py asset.toml

# Full JSON output
python bridge/gitsea/runtime/asset_toml_reader.py asset.toml --json

# Single field
python bridge/gitsea/runtime/asset_toml_reader.py asset.toml --field split

# Registration snapshot
python bridge/gitsea/runtime/asset_registration_snapshot.py asset.toml --save
```

---

*authority: none · advisory · stdlib only · no secrets · no wallet*
