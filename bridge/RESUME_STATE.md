# RESUME_STATE.md — Cooperation Commons Layer

> **STATUS: IN PROGRESS (feature/phase-16-cooperation-commons)**

**Phase:** Cooperation Commons Layer (Phase 16)
**Branch:** feature/phase-16-cooperation-commons
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
- External Credit Adapter Layer (Phase 12) — PR #4
- Credit Reflection Memory Layer (Phase 13) — PR #5
- Recognition Appeal Layer (Phase 14) — PR #6
- Recognition Ledger Layer (Phase 15) — PR #7
- **Cooperation Commons Layer (Phase 16)** ← current PR

---

## Phase 16: Cooperation Commons Layer

Core principles:
> "Community is not authority."
> "Commons is not ownership."
> "Participation is not control."

**Purpose:** Records cooperation within communities, projects, houses, and
shared initiatives. Dan-Go makes collective cooperation legible alongside
individual contribution. The commons layer is advisory only. No authority
is claimed. No ownership is implied. No governance is exercised.

### Registered Commons

| Commons ID | Name | Type |
|------------|------|------|
| `dango-001` | Dan-Go | project |
| `jammy-house-001` | Jammy House | house |
| `yacypherpunks-001` | YacypherPunks | community |
| `dra-001` | D.R.A. | initiative |

### Phase Chain

```
Phase 11: Contribution Candidate      → candidate_credit: true/false
Phase 12: External Credit Observation → external_credit: false
Phase 13: Reflection Memory           → reflection_recorded: true
Phase 14: Recognition Appeal          → appeal_recorded: true
Phase 15: Recognition Ledger          → recognition_history_complete: true
Phase 16: Cooperation Commons         → commons_recorded: true
```

### Runtime Results

```
commons_registry.py
  registry_id: commons-registry-001
  commons_count: 4
    dango-001: Dan-Go (project) — active, authority=none, ownership=false
    jammy-house-001: Jammy House (house) — active, authority=none, ownership=false
    yacypherpunks-001: YacypherPunks (community) — active, authority=none, ownership=false
    dra-001: D.R.A. (initiative) — active, authority=none, ownership=false
  Community is not authority.

commons_membership.py
  log_id: membership-log-001
  total_memberships: 9
  commons_represented: 4
    jammy-house-001: 3 members
    dra-001: 2 members
    yacypherpunks-001: 1 member
    dango-001: 3 members
  control=false, ownership=false on all records
  Participation is not control.

commons_snapshot.py
  snapshot_id: commons-snap-001
  snapshot_date: 2026-05-30
  commons_count: 4
  total_participants: 9
  total_contributions: 126
  total_recognition_history: 98
  total_ledger_entries: 8
  authority=none, ownership=false, control=false
  moves_money=false, credit_issued=false

commons_report.py
  report_id: commons-report-001
  section_count: 5
    Why Community Exists and Is Observable — advisory: true
    Why Participation Is Voluntary — membership_is_voluntary: true
    Why Community Does Not Create Authority — authority: none
    Why Cooperation Can Exist Without Ownership — ownership: false
    Why Dan-Go Records Without Governing — control: false, hard_enforcement: false
  summary_table:
    authority_implied: false
    ownership_implied: false
    control_implied: false
    dan_go_governs_communities: false
    dan_go_owns_communities: false
    commons_remains_self_governing: true
```

---

## New Files (Phase 16)

- bridge/gitsea/commons/COOPERATION_COMMONS_SPEC.md
- bridge/gitsea/commons/COMMUNITY_NOT_AUTHORITY.md
- bridge/gitsea/commons/COMMONS_NOT_OWNERSHIP.md
- bridge/gitsea/commons/runtime/commons_registry.py
- bridge/gitsea/commons/runtime/commons_membership.py
- bridge/gitsea/commons/runtime/commons_snapshot.py
- bridge/gitsea/commons/runtime/commons_report.py
- bridge/gitsea/commons/examples/commons-registry.json (generated)
- bridge/gitsea/commons/examples/commons-membership.json (generated)
- bridge/gitsea/commons/examples/commons-snapshot.json (generated)
- bridge/gitsea/commons/examples/commons-report.json (generated)

## Updated Files (Phase 16)

- bridge/gitsea/README.md (Phase 16 section + commons/ in layout + flow diagram)
- bridge/RESUME_STATE.md (this file)

---

## Key Invariants (all Phase 16 files)

| Field | Value |
|-------|-------|
| `authority` | `none` |
| `execution_allowed` | `false` |
| `moves_money` | `false` |
| `hard_enforcement` | `false` |
| `advisory` | `true` |
| `commons_only` | `true` |
| `append_only` | `true` |
| `contestable` | `true` |
| `reopenable` | `true` |
| `credit_issued` | `false` (permanent) |
| `ownership` | `false` (invariant) |
| `control` | `false` (invariant) |
| `membership_compels` | `false` (invariant) |
| `membership_grants_authority` | `false` (invariant) |
| `membership_is_voluntary` | `true` (invariant) |

---

## Protocol Principle Accumulation (Phases 10–16)

| Phase | Phrase |
|-------|--------|
| 10 | "Signal is not reward." |
| 10 | "Dan-Go observes treasury context; it does not operate the treasury." |
| 11 | "Contribution history is not credit." |
| 11 | "Dan-Go records contribution candidates; external systems may issue credit." |
| 12 | "Observation is not issuance." |
| 12 | "Candidate credit is not external credit." |
| 13 | "Unrecognized contribution is still observable." |
| 13 | "Reflection is not judgment." |
| 14 | "Appeal is not enforcement." |
| 14 | "Recognition remains external." |
| 15 | "Recognition history is not authority." |
| 15 | "Ledger is not judgment." |
| 16 | "Community is not authority." |
| 16 | "Commons is not ownership." |
| 16 | "Participation is not control." |

---

## Next Step Candidates

1. **Merge Phase 16 PR** — after review
2. **Phase 17: GITSEA Stream Candidate Tracking** — observe stream activation
3. **Commons-linked ledger** — connect Phase 15 ledger entries to their originating commons
4. **Multi-commons snapshot** — aggregate recognition history across all commons
5. **Cross-commons cooperation** — record cooperation between different commons
6. **Federation commons** — cross-node commons visibility

---

*dango-gitsea-bridge · authority: none · append-only · stdlib only · hard enforcement: forbidden*
*Signal is not reward.*
*Contribution history is not credit.*
*Observation is not issuance.*
*Candidate credit is not external credit.*
*Unrecognized contribution is still observable.*
*Reflection is not judgment.*
*Appeal is not enforcement.*
*Recognition remains external.*
*Recognition history is not authority.*
*Ledger is not judgment.*
*Community is not authority.*
*Commons is not ownership.*
*Participation is not control.*
*Dan-Go observes treasury context; it does not operate the treasury.*
*Dan-Go records contribution candidates; external systems may issue credit.*
*Dan-Go records commons participation; it does not govern communities.*
*Contribution becomes legible before it becomes valuable.*
