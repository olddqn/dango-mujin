# RESUME_STATE.md — Contributor Credit Candidate Layer

> **STATUS: IN PROGRESS (feature/phase-11-credit-candidate)**

**Phase:** Contributor Credit Candidate Layer (Phase 11)
**Branch:** feature/phase-11-credit-candidate
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
- Cooperation Treasury Bridge (Phase 10) — PR #2, merged
- **Contributor Credit Candidate Layer (Phase 11)** ← current PR

---

## Phase 11: Contributor Credit Candidate Layer

Core principles:
> "Contribution history is not credit."
> "Dan-Go records contribution candidates; external systems may issue credit."

`credit_issued: false` is a permanent protocol invariant. It is never changed by Dan-Go.

### Runtime Results

```
contributor_registry.py
  contributors: 3 (external-001 reviewer, external-002 author, external-003 contester)
  credit_issued: false
  advisory: true
  authority: none

contribution_candidate.py
  total_candidates: 3
  credit_eligible: 2  (candidate status only)
  credit_issued: false  (permanent: never by Dan-Go)
  advisory: true

credit_candidate_snapshot.py
  snapshot_id: snapshot-housing-007-issue-1
  candidate_count: 3
  credit_eligible: 2
  credit_issued: false
  external_system: gitsea
  advisory: true

contribution_history.py
  history_id: history-001
  issue: #3  pr: 2
  merged: true
  reopened: false
  entry_count: 7
  contributors: external-001, external-002, external-003
  credit_issued: false
  append_only: true
```

---

## New Files (Phase 11)

- bridge/gitsea/credit/CONTRIBUTOR_CREDIT_SPEC.md
- bridge/gitsea/credit/CREDIT_CANDIDATE_SPEC.md
- bridge/gitsea/credit/CONTRIBUTION_HISTORY_SPEC.md
- bridge/gitsea/credit/runtime/contributor_registry.py
- bridge/gitsea/credit/runtime/contribution_candidate.py
- bridge/gitsea/credit/runtime/credit_candidate_snapshot.py
- bridge/gitsea/credit/runtime/contribution_history.py
- bridge/gitsea/credit/examples/contributor-registry.json (generated)
- bridge/gitsea/credit/examples/contribution-candidate.json (generated)
- bridge/gitsea/credit/examples/credit-candidate-snapshot.json (generated)
- bridge/gitsea/credit/examples/contribution-history.json (generated)

## Updated Files (Phase 11)

- bridge/gitsea/README.md (Phase 11 section + credit/ in layout)
- bridge/RESUME_STATE.md (this file)

---

## Key Invariants (all Phase 11 files)

| Field | Value |
|-------|-------|
| `authority` | `none` |
| `execution_allowed` | `false` |
| `moves_money` | `false` |
| `hard_enforcement` | `false` |
| `advisory` | `true` |
| `append_only` | `true` |
| `contestable` | `true` |
| `reopenable` | `true` |
| `credit_issued` | `false` (always — permanent invariant) |
| `external_system` | `"gitsea"` |

---

## Previous Phase Context

### Phase 10 On-Chain Facts (observed, not executed by Dan-Go)

| Field | Value |
|-------|-------|
| Chain | Base (chain_id 8453) |
| RepoVault | `0x3F9c96A429697B458Fe0a16502A050E5AB50bB00` |
| Owner wallet | `0x89b38ff776565f095b3cd46C5f35EAb27506417C` |
| Repo ID | `B93829F8829E2FFD13EF10ABA0B8442233BCF80172321B951C50E2E0C4C30D08` |
| Splits root | `DA309748EA18E9C8C99B7FC50828251D30EB65EB1817FFF6507EC6AB5895B959` |
| Event | RepoLinked |
| Status | linked |

---

## Next Step Candidates

1. **Merge Phase 11 PR** — after review
2. **Phase 12: GITSEA Stream Candidate Tracking** — monitor when/if streams activate
3. **Live event ingestion** — real-time cooperation signal updates
4. **Multi-claim credit dashboard** — aggregate across housing-006, housing-007
5. **Federation negotiation snapshot** — aggregate Issue history across gitlawb nodes

---

*dango-gitsea-bridge · authority: none · append-only · stdlib only · hard enforcement: forbidden*
*Signal is not reward.*
*Contribution history is not credit.*
*Dan-Go observes treasury context; it does not operate the treasury.*
*Dan-Go records contribution candidates; external systems may issue credit.*
*Contribution becomes legible before it becomes valuable.*
