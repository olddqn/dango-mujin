# RepoVault Observation Notes

These notes document what is known about the GITSEA RepoVault for
olddqn/dango-mujin on Base, how that knowledge was obtained, and what
Dan-Go does with it.

No wallet was imported. No transaction was sent. No contract was called.

---

## How the RepoVault Was Created

1. The repository owner visited the GITSEA app
2. Selected "Link on Base" for `olddqn/dango-mujin`
3. GITSEA presented a MetaMask transaction titled **"Stake"**
4. The transaction called a function on the GITSEA RepoVault contract
5. MetaMask submitted the transaction to Base
6. The transaction succeeded (after an initial failure — see Phase 8 notes)
7. A **RepoLinked** event was emitted on-chain

Dan-Go was not involved in steps 1–7.

---

## What Was Observed

The following facts were observed from the GITSEA UI and BaseScan
after the RepoLinked event was confirmed:

| Field | Value |
|-------|-------|
| Repo | olddqn/dango-mujin |
| Chain | Base (chain_id 8453) |
| Owner wallet | `0x89b38ff776565f095b3cd46C5f35EAb27506417C` |
| RepoVault address | `0x3F9c96A429697B458Fe0a16502A050E5AB50bB00` |
| Repo ID (repoId) | `B93829F8829E2FFD13EF10ABA0B8442233BCF80172321B951C50E2E0C4C30D08` |
| Splits root | `DA309748EA18E9C8C99B7FC50828251D30EB65EB1817FFF6507EC6AB5895B959` |
| Event | RepoLinked |
| Status | linked |
| Source | observed_basescan |

---

## Why the RepoVault Is Not a User Wallet

The address `0x3F9c96A429697B458Fe0a16502A050E5AB50bB00` is a **smart contract
address**, not a user wallet address.

Key differences:

| User wallet | RepoVault contract |
|-------------|-------------------|
| Controlled by a private key | Controlled by contract code |
| Owner can sign transactions from it | Only callable via defined functions |
| Can hold and send ETH/tokens freely | Holds funds under contract rules |
| Dan-Go must never import it | Dan-Go records its address for context |

Dan-Go records the RepoVault address for treasury visibility.
Dan-Go does not call the RepoVault. Dan-Go does not hold the owner's private key.

---

## The "Stake" MetaMask Function

MetaMask showed the transaction title as **"Stake"** during registration.
This was a GITSEA-internal contract call — not a traditional token staking operation.

GITSEA's RepoVault registration uses a function that MetaMask labels as "Stake."
This function:
- Registers the repository's identity on-chain
- Associates the owner wallet with the repo
- Emits the RepoLinked event

It is not:
- Token staking for yield
- Locking funds for a minimum period
- A commitment by Dan-Go

Dan-Go did not call this function. The repository owner called it via GITSEA UI.

---

## The Initial Registration Failure

The first "Link on Base" attempt failed (MetaMask transaction failure).
Investigation revealed the `asset.toml` was using Japanese section names
(`["リポジトリ"]`, etc.) that GITSEA could not parse.

Fix applied in commit `d53ee21`:
- `asset.toml` rewritten to canonical English ASCII format
- `[repo]`, `[splits]`, `[royalties]`, `[insurance]`

After the fix, the registration succeeded.

---

## The Repo ID and keccak256

The Repo ID `B93829F8...C4C30D08` is a keccak256 hash generated internally
by GITSEA. The exact hash input is not published in GITSEA's documentation.

Dan-Go cannot reproduce this hash:
- stdlib only — no `pysha3` or `eth-hash` external library
- `hashlib.sha3_256` is NIST SHA3, which differs from Ethereum keccak256
- Attempting to reverse-engineer the hash input is out of scope

The Repo ID is recorded in Dan-Go snapshots for traceability, not for
computation. To verify it, use a trusted Ethereum tool (e.g., `cast keccak`
from Foundry) in a separate environment.

---

## The Splits Root

The Splits root `DA309748...895B959` corresponds to the Merkle root of the
splits configuration declared in `asset.toml`:

```toml
[splits]
"0x89b38ff776565f095b3cd46C5f35EAb27506417C" = 100
```

Single-address 100% splits → single-leaf Merkle root.

Dan-Go does not verify this hash independently (same keccak limitation).
The value is recorded as-observed.

---

## What Dan-Go Does With These Observations

1. **treasury_snapshot.py** — records observed facts as an advisory JSON snapshot
2. **repovault_reader.py** — makes facts available to other Dan-Go modules
3. **cooperation_treasury_bridge.py** — connects Phase 9 signals to treasury context
4. **treasury_visibility_report.py** — human-readable explanation for participants

None of these operations:
- Call the Base RPC
- Query wallet balances
- Send transactions
- Operate the RepoVault
- Distribute funds

---

## Dan-Go's Role in the Economic Layer

```
GITSEA: registered the repo on Base ←────────── external
GITSEA: manages the RepoVault contract ←──────── external
GITSEA: activates streams ←────────────────────── external
─────────────────────────────────────────────────────────
Dan-Go: observes treasury context ←──────────── advisory
Dan-Go: records cooperation signals ←────────── advisory
Dan-Go: generates treasury visibility ←──────── advisory
Dan-Go: connects signals to context ←────────── advisory
─────────────────────────────────────────────────────────
Dan-Go does NOT: move funds ←──────────────── invariant
Dan-Go does NOT: operate treasury ←────────── invariant
Dan-Go does NOT: assign rewards ←──────────── invariant
```

---

*authority: none · advisory · stdlib only · no wallet · no RPC*
*Dan-Go observes treasury context; it does not operate the treasury.*
*Signal is not reward.*
