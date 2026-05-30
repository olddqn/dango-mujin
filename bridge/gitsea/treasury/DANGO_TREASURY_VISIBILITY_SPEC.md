# Dan-Go Treasury Visibility Spec

**Dan-Go observes treasury context; it does not operate the treasury.**

**Signal is not reward.**

This document specifies how Dan-Go makes the GITSEA RepoVault treasury
visible in the cooperation history — without moving funds, executing
transactions, or operating the treasury.

---

## 1. What Is the RepoVault

The RepoVault is a GITSEA smart contract deployed on Base.

| Fact | Value |
|------|-------|
| Contract | `0x3F9c96A429697B458Fe0a16502A050E5AB50bB00` |
| Chain | Base (chain_id 8453) |
| Repo | olddqn/dango-mujin |
| Owner wallet | `0x89b38ff776565f095b3cd46C5f35EAb27506417C` |
| Repo ID | `B93829F8...C4C30D08` |
| Splits root | `DA309748...895B959` |
| Registration event | RepoLinked |
| Registration source | GITSEA UI → MetaMask → Base |

The RepoVault is **not a user wallet**. It is a contract.

Dan-Go did not deploy this contract. Dan-Go does not hold any key to operate it.
Dan-Go did not execute the registration transaction. The repository owner did,
via the GITSEA "Link on Base" UI flow.

---

## 2. What Treasury Visibility Means

Treasury visibility in Dan-Go means:

1. The RepoVault address and repo_id are recorded in advisory snapshots.
2. Cooperation signals (Phase 9) can reference treasury context.
3. The negotiation history and the on-chain treasury are legibly connected.

Treasury visibility does NOT mean:

- Dan-Go controls the treasury
- Dan-Go can withdraw from the treasury
- Dan-Go can execute staking
- Dan-Go can distribute tokens
- Dan-Go has signing authority
- Cooperation signals trigger economic actions

**Visibility ≠ Control. Visibility ≠ Execution.**

---

## 3. Why Visibility Is Useful

Without treasury visibility, cooperation signals exist in isolation.
A participant contributing to a Dan-Go negotiation cannot see whether
their cooperation history is connected to an economic context.

With treasury visibility:
- The negotiation history and the RepoVault are legibly connected
- A participant can observe that cooperation signals reference a
  specific on-chain treasury context
- GITSEA can observe both cooperation history and treasury status

Dan-Go does not make visibility into execution.
Dan-Go records cooperation before value emerges.

---

## 4. Why Dan-Go Does Not Operate the Treasury

Dan-Go is a negotiation protocol. Its invariants are permanent:

| Invariant | Value |
|-----------|-------|
| `execution_allowed` | `false` |
| `moves_money` | `false` |
| `hard_enforcement` | `false` |
| `authority` | `none` |
| `advisory` | `true` |

These invariants mean Dan-Go cannot:
- Sign a treasury transaction
- Call a contract function
- Stake tokens
- Distribute rewards
- Enforce economic outcomes

If a Dan-Go module ever set `moves_money: true`, it would be in violation
of the protocol. This is not a policy choice — it is a protocol invariant.

---

## 5. Why the RepoVault Is Not a Wallet Import

MetaMask showed a "Stake" transaction during GITSEA registration. This
was a GITSEA contract interaction, not a wallet import.

The RepoVault is a contract address. Dan-Go records its address for
observation. Dan-Go does NOT:
- Import this address as a wallet
- Monitor this address via RPC
- Check balances on this address
- Call functions on this address

Recording an address in a JSON snapshot is observation.
Calling a contract is execution.
Dan-Go does the first. Never the second.

---

## 6. The Lifecycle with Treasury Visibility

```
Claim
  → Issue (Phase 5)
  → Negotiation (Phase 6)
  → Contribution (Phase 9)
  → Cooperation Signal (Phase 9)    ← advisory signal
  → Asset Signal (Phase 9)          ← GITSEA-observable
  │
  ╔══════════════════════════╗
  ║  Treasury Context (P10)  ║      ← Dan-Go observes
  ║  RepoVault on Base       ║
  ║  Visible, not operated   ║
  ╚══════════════════════════╝
  │
  → Economic Value (optional)        ← GITSEA's decision
```

Dan-Go territory: everything above the treasury context box.
GITSEA territory: the economic value activation.
The treasury context box is the boundary — observed by Dan-Go, operated by GITSEA.

---

## 7. Pipeline

```
repovault_reader.py
    → Known on-chain facts (static, offline)

treasury_snapshot.py
    → treasury-snapshot.json (advisory snapshot)

cooperation_treasury_bridge.py
    ← contribution-signal.json (Phase 9)
    → cooperation-treasury-bridge.json (bridge record)

treasury_visibility_report.py
    → treasury-visibility-report.json (explanation report)
```

---

## 8. Invariants

Every file in `bridge/gitsea/treasury/` maintains:

| Field | Value |
|-------|-------|
| `authority` | `none` |
| `execution_allowed` | `false` |
| `moves_money` | `false` |
| `hard_enforcement` | `false` |
| `advisory` | `true` |
| `append_only` | `true` |
| `dango_controls_treasury` | `false` |
| `dango_executes_treasury` | `false` |
| `recommended_allocation` | `null` (always) |

---

## 9. Absolute Prohibitions

- No Base RPC calls
- No wallet key import
- No contract function calls
- No token distribution
- No staking
- No treasury withdrawal
- No automatic reward allocation
- No on-chain transaction submission
- No external libraries (stdlib only)

---

*dango-gitsea-bridge · authority: none · advisory · append-only · stdlib only*
*Dan-Go observes treasury context; it does not operate the treasury.*
*Signal is not reward.*
