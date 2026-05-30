# bridge/gitsea — GITSEA Asset Bridge

**GITSEA can make repository contribution economically legible.
Dan-Go makes contribution negotiable before it becomes economic.**

This directory connects the Dan-Go protocol to GITSEA asset registration.
It is advisory only. No GITSEA API is called. No funds are moved.
No on-chain operation is performed. stdlib only.

---

## What This Is

The `bridge/gitsea/` layer:

1. Reads `asset.toml` from the repository root
2. Validates the split, royalty, and insurance declarations
3. Generates local advisory snapshots and concept mapping documents
4. Documents how Dan-Go negotiation output relates to GITSEA stream eligibility

It does **not** submit to GITSEA, sign transactions, or move funds.

---

## Directory Layout

```
bridge/gitsea/
├── README.md                          ← this file
├── DANGO_GITSEA_INTEGRATION_SPEC.md   ← integration spec + required phrase
├── GITSEA_ASSET_REGISTRATION.md       ← step-by-step registration guide
├── ASSET_TOML_MAPPING.md              ← field-by-field asset.toml explanation
├── runtime/
│   ├── asset_toml_reader.py           ← read + validate asset.toml
│   ├── asset_registration_snapshot.py ← convert to registration snapshot JSON
│   └── dango_asset_mapper.py          ← map Dan-Go → GITSEA concepts
└── examples/
    ├── asset.toml.example             ← example asset.toml template
    ├── asset-registration.snapshot.json  (generated)
    └── dango-to-gitsea-asset.json        (generated)
```

The `asset.toml` itself lives at the repository root:

```
dango-mujin/
└── asset.toml       ← GITSEA reads this directly
```

---

## Quick Start

```bash
# Validate asset.toml
python bridge/gitsea/runtime/asset_toml_reader.py asset.toml

# Generate registration snapshot (advisory — not submitted)
python bridge/gitsea/runtime/asset_registration_snapshot.py asset.toml --save

# Generate Dan-Go → GITSEA concept mapping
python bridge/gitsea/runtime/dango_asset_mapper.py --save

# JSON output
python bridge/gitsea/runtime/asset_toml_reader.py asset.toml --json
python bridge/gitsea/runtime/asset_registration_snapshot.py asset.toml --json
```

---

## asset.toml (repo root)

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

**TOML 1.0 note:** Japanese section headers and keys must be quoted
(`["リポジトリ"]` not `[リポジトリ]`). Bare keys must be ASCII.

---

## Key Concept

```
Dan-Go negotiation record
    │
    │  (advisory evidence)
    ▼
asset.toml  ←─── GITSEA reads this
    │
    │  (GITSEA process, not Dan-Go)
    ▼
GITSEA stream eligibility
```

Dan-Go does not activate the stream. Dan-Go produces the evidence
that GITSEA may consider.

---

## Invariants

Every file in this directory maintains:

| Field | Value |
|-------|-------|
| `execution_allowed` | `false` |
| `moves_money` | `false` |
| `hard_enforcement` | `false` |
| `advisory` | `true` |
| `authority` | `none` |

No private keys. No wallet operations. No GITSEA API calls. stdlib only.

---

*dango-gitsea-bridge · authority: none · advisory · append-only · stdlib only*
