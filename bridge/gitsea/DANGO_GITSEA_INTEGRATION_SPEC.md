# Dan-Go × GITSEA Integration Spec

**GITSEA can make repository contribution economically legible.
Dan-Go makes contribution negotiable before it becomes economic.**

This document specifies how the Dan-Go protocol connects to GITSEA
asset registration. No real GITSEA API is called. No funds are moved.
No on-chain operation is performed. stdlib only.

---

## 1. Why These Two Systems

Dan-Go and GITSEA solve adjacent problems:

| Layer | System | Question answered |
|-------|--------|------------------|
| Negotiation | Dan-Go | *Who contributed what, under what conditions, with whose consent?* |
| Economic legibility | GITSEA | *How is that contribution recognized as a stream of value?* |

Without Dan-Go, GITSEA sees commits and merges — but not the negotiation
that produced them. Without GITSEA, Dan-Go produces a complete negotiation
record — but that record has no economic expression.

**GITSEA can make repository contribution economically legible.
Dan-Go makes contribution negotiable before it becomes economic.**

Neither system is subordinate to the other. Neither system grants authority.

---

## 2. The Bridge

The bridge is read-only from Dan-Go's perspective.

Dan-Go:
1. Produces a negotiation record (append-only su-table)
2. Declares asset metadata in `asset.toml`
3. Generates registration snapshots and mapping documents (advisory)

GITSEA:
1. Reads `asset.toml` from the repository root
2. Reads the repository's contribution history
3. Determines stream eligibility based on its own criteria

Dan-Go does not push to GITSEA. Dan-Go does not call the GITSEA API.
Dan-Go does not activate any GITSEA stream.

---

## 3. asset.toml

`asset.toml` is the declaration surface. It lives at the repository root.
It is read by both Dan-Go tooling and GITSEA.

```toml
["リポジトリ"]
"名前" = "owner/repo"
"ライセンス" = "MIT"

["分割"]
"0xWALLET_ADDRESS" = 100

["著作権料"]
"乗数" = 1.0
"受容度" = 1.0

["保険"]
merge_insurance = true
```

**TOML 1.0 note:** Bare keys must be ASCII. Japanese section headers and
keys must be quoted (`["リポジトリ"]` not `[リポジトリ]`).
Python 3.11+ `tomllib` parses quoted Unicode keys correctly.

Dan-Go reads `asset.toml` with `asset_toml_reader.py` — advisory only.
GITSEA reads `asset.toml` from the repository root — its own process.

---

## 4. The Negotiation Record as Evidence

GITSEA may observe the Dan-Go negotiation record as contribution evidence.
Key signals:

| Dan-Go signal | What it means for GITSEA |
|---------------|--------------------------|
| `gitsea_eligible: true` on PR merge | Contribution event with accepted evidence |
| `split_valid: true` in asset.toml | Split configuration is internally consistent |
| `merge_insurance: true` | Contributor requested merge insurance |
| `royalty_multiplier` | Declared royalty scaling preference |
| `negotiation_reopen_allowed: true` | All negotiation steps remain contestable |

These signals do not activate any GITSEA stream. They are advisory metadata
that GITSEA may read when assessing a repository.

---

## 5. What Dan-Go Does Not Do

Dan-Go never:

- Calls the GITSEA API
- Submits asset registration on-chain
- Signs a transaction
- Moves funds
- Activates a stream
- Computes keccak256 hashes
- Stores private keys
- Performs wallet operations

Any file in `bridge/gitsea/` that claims to do these things is in violation
of this spec.

---

## 6. What GITSEA Does Not Do (from Dan-Go's perspective)

From Dan-Go's perspective, GITSEA:

- Does not adjudicate negotiation outcomes
- Does not override `authority: none`
- Does not enforce Dan-Go prerequisites
- Does not grant or revoke participant consent
- Does not modify the append-only su-table

GITSEA is an observer of Dan-Go output, not a participant in Dan-Go protocol.

---

## 7. Invariants

These invariants apply to every file in `bridge/gitsea/`:

| Field | Value |
|-------|-------|
| `execution_allowed` | `false` |
| `moves_money` | `false` |
| `hard_enforcement` | `false` |
| `advisory` | `true` |
| `authority` | `none` |

---

## 8. Pipeline

```
asset.toml  (repo root)
    │
    ├── asset_toml_reader.py
    │     → structured JSON (advisory)
    │
    ├── asset_registration_snapshot.py
    │     → examples/asset-registration.snapshot.json
    │        (local advisory snapshot, not submitted)
    │
    └── dango_asset_mapper.py
          → examples/dango-to-gitsea-asset.json
             (concept bridge document)
```

---

## 9. Absolute Prohibitions

- No real GITSEA API connection
- No on-chain submission
- No transaction signing
- No fund movement
- No private keys
- No wallet operations
- No keccak256 computation (advisory note only)
- No external libraries (stdlib only)
- No hidden scoring
- No hard enforcement
- No auto-execution

---

## 10. Related Specs

- `bridge/gitsea/GITSEA_ASSET_REGISTRATION.md` — step-by-step: asset.toml → root → commit → GITSEA
- `bridge/gitsea/ASSET_TOML_MAPPING.md` — explains each TOML field
- `bridge/gitlawb/PR_NEGOTIATION_REOPEN_SPEC.md` — PR negotiation lifecycle
- `bridge/gitlawb/SCOPED_ISSUE_GENERATION_SPEC.md` — scoped issue generation

---

*dango-gitsea-bridge · authority: none · advisory · append-only · stdlib only*
*GITSEA can make repository contribution economically legible.*
*Dan-Go makes contribution negotiable before it becomes economic.*
