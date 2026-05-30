# GITSEA Asset Registration — Step by Step

This document explains how to register `dango-mujin` as a GITSEA asset.

Dan-Go produces advisory metadata only. The actual GITSEA registration
is a separate process performed by the repository owner on the GITSEA
platform. No private keys belong in this repository. No wallet operations
are performed by Dan-Go tooling.

---

## Step 1: Prepare asset.toml

`asset.toml` must live at the repository root. It is already present:

```
dango-mujin/
└── asset.toml        ← here
```

Verify it parses correctly:

```bash
python bridge/gitsea/runtime/asset_toml_reader.py asset.toml
```

Expected: no errors, split total = 100, registration ready.

---

## Step 2: Validate the Split

The `["分割"]` section must sum to exactly 100. If it does not,
GITSEA registration will fail.

```bash
python bridge/gitsea/runtime/asset_toml_reader.py asset.toml --field split
```

---

## Step 3: Generate Registration Snapshot (Advisory)

This step produces a local advisory document. It does NOT submit anything.

```bash
python bridge/gitsea/runtime/asset_registration_snapshot.py asset.toml --save
```

Output: `bridge/gitsea/examples/asset-registration.snapshot.json`

This file is for reference only. It is not sent to GITSEA.

---

## Step 4: Review the Concept Mapping (Optional)

To understand how Dan-Go concepts map to GITSEA asset concepts:

```bash
python bridge/gitsea/runtime/dango_asset_mapper.py --save
```

Output: `bridge/gitsea/examples/dango-to-gitsea-asset.json`

---

## Step 5: Commit asset.toml to the Repository

```bash
git add asset.toml
git commit -m "feat: add GITSEA asset.toml"
git push origin main
```

`asset.toml` must be committed and pushed before GITSEA can read it.

---

## Step 6: Register on the GITSEA Platform

1. Visit the GITSEA platform (separate from this repository)
2. Connect your wallet — this is a GITSEA operation, not a Dan-Go operation
3. Point GITSEA at `olddqn/dango-mujin`
4. GITSEA reads `asset.toml` from the repository root
5. Review split, royalty, and insurance settings
6. Submit registration — this is a GITSEA operation

**Dan-Go has no role in steps 6.1–6.6. No Dan-Go tooling is called.**

---

## Step 7: Verify (On GITSEA Platform)

After registration, verify on the GITSEA platform:

- Split configuration matches `["分割"]` in asset.toml
- Royalty multiplier matches `"乗数"` in `["著作権料"]`
- Merge insurance matches `merge_insurance` in `["保険"]`

---

## What Dan-Go Does and Does Not Do

| Action | Dan-Go | GITSEA |
|--------|--------|--------|
| Read asset.toml | ✓ (advisory) | ✓ (registration) |
| Validate split sum | ✓ (advisory) | ✓ (enforced) |
| Submit registration | ✗ | ✓ |
| Sign transaction | ✗ | ✓ |
| Move funds | ✗ | ✓ (stream) |
| Store private keys | ✗ | ✗ (wallet, not repo) |
| Generate snapshots | ✓ (advisory) | — |
| Activate stream | ✗ | ✓ |

---

## TOML 1.0 Note

Japanese section headers and keys must be quoted in asset.toml.
TOML 1.0 requires bare keys to be ASCII.

```toml
# ✓ Correct
["リポジトリ"]
"名前" = "olddqn/dango-mujin"

# ✗ Wrong (bare Unicode keys — fails Python tomllib)
[リポジトリ]
名前 = "olddqn/dango-mujin"
```

---

## GITSEA Registration Failure: Troubleshooting Note

This section documents a known failure mode and its resolution.

### What Happened

Attempting to "Link on Base" via the GITSEA app resulted in a MetaMask
transaction failure. The GITSEA screen showed:

> "One on-chain transaction registers your repo with the RepoVault contract.
> After this lands, your repo has an on-chain treasury."

MetaMask showed the transaction title as **"Stake"**.
The transaction `0x443e6d48...d433d647` failed.

### Dan-Go Side Root Cause

The `asset.toml` file previously used **Japanese section names and keys**
(`["リポジトリ"]`, `"名前"`, etc.) which are valid TOML 1.0 but are
**not recognised by GITSEA**. GITSEA expects English ASCII section names.

**Before (incorrect for GITSEA):**
```toml
["リポジトリ"]
"名前" = "olddqn/dango-mujin"
```

**After (correct GITSEA canonical format):**
```toml
[repo]
name = "olddqn/dango-mujin"
```

This has been corrected. The current `asset.toml` uses the canonical
English format.

### What Dan-Go Does NOT Do

- Dan-Go does **not** execute wallet actions.
- Dan-Go does **not** submit transactions to Base or any other network.
- Dan-Go only prepares advisory asset metadata (`asset.toml` + snapshots).
- Failed on-chain registration should be **retried from the GITSEA UI only**
  after verifying `asset.toml` is in the canonical format.

### MetaMask "Stake" Function

MetaMask showing **"Stake"** as the transaction title indicates GITSEA is
calling a specific function on the RepoVault smart contract. This is an
**external GITSEA UI / contract behavior** — not caused by Dan-Go tooling.

The "Stake" call may have failed because:
1. GITSEA could not parse `asset.toml` (Japanese keys → malformed params)
2. Base network gas issue at time of transaction
3. GITSEA app or contract issue unrelated to `asset.toml`

Dan-Go cannot diagnose the contract-level failure. Once `asset.toml` is
corrected, retry the GITSEA UI registration.

### Repo ID and keccak256

GITSEA showed Repo ID: `0xb93829f8829e2ffd13ef10aba0b8442233bcf80172321b951c50...`

This is a keccak256 hash generated internally by GITSEA.
Dan-Go cannot compute keccak256 (stdlib only — no `pysha3` or `eth-hash`).
The Repo ID cannot be verified or reproduced from Dan-Go tooling.

To verify the Repo ID, use a trusted Ethereum tooling environment
(e.g. `cast keccak` from Foundry) — outside Dan-Go tooling.

### Verification Checklist (before retrying GITSEA registration)

```bash
# 1. Verify asset.toml format
python3 bridge/gitsea/runtime/asset_toml_reader.py asset.toml
#    Expect: GITSEA format OK: ✓

# 2. Verify split totals to 100
python3 bridge/gitsea/runtime/asset_toml_reader.py asset.toml --field split
#    Expect: {"0x89b38ff...": 100}

# 3. Regenerate registration snapshot
python3 bridge/gitsea/runtime/asset_registration_snapshot.py asset.toml --save
#    Expect: gitsea_registration_ready: true

# 4. Verify asset.toml is committed and pushed to GitHub
git log --oneline -1
#    Expect: latest commit includes asset.toml changes
```

If all checks pass: retry the GITSEA "Link on Base" flow from the GITSEA UI.
If the transaction still fails: the issue is GITSEA-internal (contract/network).

---

## Absolute Prohibitions

- **No private keys in this repository** — ever
- **No wallet operations by Dan-Go tooling**
- **No GITSEA API calls from Dan-Go tooling**
- **No on-chain submissions from Dan-Go tooling**
- **No fund movements by Dan-Go tooling**

---

*authority: none · advisory · stdlib only · no secrets · no wallet*
