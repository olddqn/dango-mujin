# RESUME_STATE.md — External Credit Adapter Layer

> **STATUS: IN PROGRESS (feature/phase-12-external-credit)**

**Phase:** External Credit Adapter Layer (Phase 12)
**Branch:** feature/phase-12-external-credit
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
- Contributor Credit Candidate Layer (Phase 11) — PR #3
- **External Credit Adapter Layer (Phase 12)** ← current PR

---

## Phase 12: External Credit Adapter Layer

Core principles:
> "Observation is not issuance."
> "Candidate credit is not external credit."

**Key discovery addressed:** Phase 11 produced valid contribution candidates.
External systems did not automatically issue credit. This distinction is now
explicit in the architecture. The gap between candidate credit and external
credit is documented, observable, and by design.

### Runtime Results

```
external_credit_adapter.py
  system: gitsea
  observed: true
  credit_visible: false
  observation_status: no_credit_detected
  credit_issued: false
  advisory: true

external_credit_snapshot.py
  snapshot_id: ext-snapshot-housing-007-issue-1
  candidate_count: 3 (from Phase 11)
  credit_eligible: 2
  external_credit_detected: false
  observation_only: true
  gap_note: "2 candidate(s) exist but no external credit detected.
             This is not an error. External credit is sovereign and optional."

candidate_vs_external.py
  comparison_id: cmp-housing-007-issue-1
  candidate_credit: true
  external_credit: false
  equivalent: false
  observation: candidate_not_yet_recognized
  gap_exists: true
  gap_is_error: false

credit_observation_report.py
  report_id: obs-report-housing-007-issue-1
  summary: "Contribution candidate exists but no external credit observed."
  candidate_credit: true
  external_credit: false
  credit_issued: false
  4 sections: Candidate Exists, External Credit Absent,
              No Contradiction Exists, Observation Is Sufficient
  summary_table:
    candidate_exists: true
    external_credit_absent: true
    gap_is_error: false
    observation_sufficient: true
    dango_issues_credit: false
    external_system_sovereign: true
```

---

## New Files (Phase 12)

- bridge/gitsea/external_credit/EXTERNAL_CREDIT_SPEC.md
- bridge/gitsea/external_credit/OBSERVATION_NOT_ISSUANCE.md
- bridge/gitsea/external_credit/CANDIDATE_VS_EXTERNAL_CREDIT.md
- bridge/gitsea/external_credit/runtime/external_credit_adapter.py
- bridge/gitsea/external_credit/runtime/external_credit_snapshot.py
- bridge/gitsea/external_credit/runtime/candidate_vs_external.py
- bridge/gitsea/external_credit/runtime/credit_observation_report.py
- bridge/gitsea/external_credit/examples/credit-adapter.json (generated)
- bridge/gitsea/external_credit/examples/external-credit-snapshot.json (generated)
- bridge/gitsea/external_credit/examples/candidate-vs-external.json (generated)
- bridge/gitsea/external_credit/examples/credit-observation-report.json (generated)

## Updated Files (Phase 12)

- bridge/gitsea/README.md (Phase 12 section + external_credit/ in layout)
- bridge/RESUME_STATE.md (this file)

---

## Key Invariants (all Phase 12 files)

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
| `credit_issued` | `false` (permanent invariant) |
| `external_credit_detected` | `false` (as observed 2026-05-30) |
| `observation_only` | `true` |
| `gap_is_error` | `false` (invariant — gap is never an error) |
| `dango_issues_credit` | `false` |
| `external_system_sovereign` | `true` |

---

## Previous Phase Context

### Phase 11 Candidates (housing-007 / Issue #1)

- total_candidates: 3
- credit_eligible: 2 (external-001 reviewer, external-002 evidence_accepted)
- credit_issued: false
- external_system: gitsea

### Phase 10 On-Chain Facts (observed, not executed by Dan-Go)

| Field | Value |
|-------|-------|
| Chain | Base (chain_id 8453) |
| RepoVault | `0x3F9c96A429697B458Fe0a16502A050E5AB50bB00` |
| Owner wallet | `0x89b38ff776565f095b3cd46C5f35EAb27506417C` |
| Repo ID | `B93829F8829E2FFD13EF10ABA0B8442233BCF80172321B951C50E2E0C4C30D08` |
| Event | RepoLinked |
| Status | linked |

---

## Next Step Candidates

1. **Merge Phase 12 PR** — after review
2. **Phase 13: GITSEA Stream Candidate Tracking** — monitor stream activation events
3. **Live event ingestion** — real-time cooperation signal updates
4. **Multi-claim observation dashboard** — aggregate across housing-006, housing-007
5. **Federation credit observation** — observe credit across gitlawb nodes

---

*dango-gitsea-bridge · authority: none · append-only · stdlib only · hard enforcement: forbidden*
*Signal is not reward.*
*Contribution history is not credit.*
*Observation is not issuance.*
*Candidate credit is not external credit.*
*Dan-Go observes treasury context; it does not operate the treasury.*
*Dan-Go records contribution candidates; external systems may issue credit.*
*Contribution becomes legible before it becomes valuable.*
