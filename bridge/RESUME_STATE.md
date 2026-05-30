# RESUME_STATE.md — Cooperation Treasury Bridge

> **STATUS: IN PROGRESS (feature/phase-10-treasury-visibility)**

**Phase:** Cooperation Treasury Bridge (Phase 10)
**Branch:** feature/phase-10-treasury-visibility
**Started:** 2026-05-30

---

## All Phases

- Reflective Memory Loop (commits 3e3d4e7..7d328c2)
- Documentation Phase (commits 64fecb1..dc2691d)
- Federation-Aware Branching Layer (commits b8b7d61..eab0f60)
- Housing-002 Memory Snapshot / Cross-claim Pattern Detection (commit 3f1dba6)
- Federation Prerequisite Promotion Layer (commits 7a521b3..1edc3d9)
- 3-Way Convergence Test (commit 09faf1d)
- Federation Prerequisite Deprecation Lifecycle (commits 7649826..0dd26b3)
- Scoped Prerequisite Inheritance Layer (commits 591817e..6a6d393)
- Gitlawb GITSEA Bountyless PR Market Demo (commit ca7d290)
- Scoped Plan Tree OGI Integration (commit 17b344c)
- Scoped Issue Generation (commit a93ffb0)
- Scoped Issue Markdown Rendering (commit d3bbc5e)
- Issue Markdown Canonical Format Rewrite (commit a904afb)
- GitHub Issue #1 Created (https://github.com/olddqn/dango-mujin/issues/1)
- Reopenable PR Negotiation Lifecycle (commit 4533c13)
- GITSEA Asset Registration (commit 9363bf2)
- GITSEA Asset Lifecycle Bridge (commit e68b9de)
- GITSEA Registration Failure Fix / asset.toml canonical format (commit d53ee21)
- **Cooperation Treasury Bridge (Phase 10)** ← current PR

---

## Phase 10: Cooperation Treasury Bridge

Core principles:
> "Signal is not reward."
> "Dan-Go observes treasury context; it does not operate the treasury."

### On-Chain Facts (observed, not executed by Dan-Go)

| Field | Value |
|-------|-------|
| Chain | Base (chain_id 8453) |
| RepoVault | `0x3F9c96A429697B458Fe0a16502A050E5AB50bB00` |
| Owner wallet | `0x89b38ff776565f095b3cd46C5f35EAb27506417C` |
| Repo ID | `B93829F8829E2FFD13EF10ABA0B8442233BCF80172321B951C50E2E0C4C30D08` |
| Splits root | `DA309748EA18E9C8C99B7FC50828251D30EB65EB1817FFF6507EC6AB5895B959` |
| Event | RepoLinked |
| Status | linked |

### Runtime Results

```
treasury_snapshot.py
  treasury_visible: true
  dango_controls_treasury: false
  moves_money: false
  advisory: true

cooperation_treasury_bridge.py
  cooperation_signal: 0.88 (from Phase 9)
  dissent_present: true
  treasury_address: 0x3F9c96A429697B458Fe0a16502A050E5AB50bB00
  recommended_allocation: null (always)
  signal_becomes_reward: false
  economic_action: false

repovault_reader.py
  observation_status: linked
  source: observed_basescan
  dango_controls_vault: false
  dango_executes_vault: false

treasury_visibility_report.py
  5 sections: RepoVault Exists, Treasury Is Visible,
              Dan-Go Does Not Control Funds,
              Cooperation Signals Reference Treasury Context,
              Economic Value Remains Optional
  economic_value_automatic: false
  recommended_allocation: null
```

---

## New Files (Phase 10)

- bridge/gitsea/treasury/DANGO_TREASURY_VISIBILITY_SPEC.md
- bridge/gitsea/treasury/COOPERATION_TREASURY_BRIDGE_SPEC.md
- bridge/gitsea/treasury/REPOVAULT_OBSERVATION_NOTES.md
- bridge/gitsea/treasury/runtime/treasury_snapshot.py
- bridge/gitsea/treasury/runtime/cooperation_treasury_bridge.py
- bridge/gitsea/treasury/runtime/repovault_reader.py
- bridge/gitsea/treasury/runtime/treasury_visibility_report.py
- bridge/gitsea/treasury/examples/treasury-snapshot.json (generated)
- bridge/gitsea/treasury/examples/cooperation-treasury-bridge.json (generated)
- bridge/gitsea/treasury/examples/treasury-visibility-report.json (generated)

## Updated Files (Phase 10)

- bridge/gitsea/README.md (Phase 10 section + treasury/ in layout)
- bridge/RESUME_STATE.md (this file)

---

## Key Invariants (all Phase 10 files)

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
| `signal_becomes_reward` | `false` (always) |
| `economic_action` | `false` (always) |

---

## Next Step Candidates

1. **Merge Phase 10 PR** — after review
2. **Live su-table event ingestion** — real-time cooperation signal updates
3. **Multi-claim treasury dashboard** — aggregate across housing-006, housing-007
4. **Federation negotiation snapshot** — aggregate Issue history across gitlawb nodes
5. **GITSEA stream candidate tracking** — monitor when/if streams activate

---

*dango-gitsea-bridge · authority: none · append-only · stdlib only · hard enforcement: forbidden*
*Signal is not reward.*
*Dan-Go observes treasury context; it does not operate the treasury.*
*Contribution becomes legible before it becomes valuable.*
