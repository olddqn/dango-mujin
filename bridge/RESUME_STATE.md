# RESUME_STATE.md — Care Loop Reopen Layer

> **STATUS: IN PROGRESS (feature/phase-20-aid-pattern-learning)**

**Phase:** Aid Pattern Learning Layer (Phase 20)
**Branch:** feature/phase-20-aid-pattern-learning
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
- Cooperation Commons Layer (Phase 16) — PR #8
- Mutual Aid Routing Layer (Phase 17) — PR #9
- Relief Case Memory Layer (Phase 18) — PR #10
- Care Loop Reopen Layer (Phase 19) — PR #11
- **Aid Pattern Learning Layer (Phase 20)** ← current PR

---

## Phase 20: Aid Pattern Learning Layer

Core principles:
> "Pattern is not prediction."
> "Learning is not prescription."
> "Recurrence is not ranking."

**Purpose:** Records recurring aid patterns observed across Phase 17–19
care histories. Dan-Go does not predict future need. Dan-Go does not
rank suffering. Dan-Go does not prescribe responses. Dan-Go only records
observable patterns and cross-phase pattern memory.

### Phase Chain

```
Phase 17: Mutual Aid Routing   → aid_route_recorded: true
Phase 18: Relief Case Memory   → care_history_complete: true
Phase 19: Care Loop Reopen     → care_loop_complete: true
Phase 20: Aid Pattern Learning → pattern_learning_only: true
```

### Runtime Results

```
aid_pattern_registry.py
  registry_id: aid-pattern-registry-001
  pattern_count: 4
  commons_represented: [dra-001, jammy-house-001, yacypherpunks-001]
    aid-pattern-001: recurring_food_support (observed_count=3) pattern_is_prediction=false
    aid-pattern-002: ongoing_displacement_relief (observed_count=4) pattern_is_prediction=false
    aid-pattern-003: unresolved_tenancy_pattern (observed_count=2) pattern_is_prediction=false
    aid-pattern-004: pending_skill_exchange (observed_count=1) pattern_is_prediction=false
  pattern_ranks_commons=false

recurrence_snapshot.py
  snapshot_id: recurrence-snapshot-001
  recurrence_count: 4
    recurrence-001: food_need_reappeared (count=3) recurrence_is_ranking=false ranks_suffering=false
    recurrence-002: displacement_relief_ongoing (count=4) recurrence_is_ranking=false ranks_suffering=false
    recurrence-003: tenancy_unresolved_continued (count=2) recurrence_is_ranking=false ranks_suffering=false
    recurrence-004: skill_exchange_deferred (count=1) recurrence_is_ranking=false ranks_suffering=false
  urgency_note: No urgency ranking applied — recurrence_is_ranking: false on all records

pattern_memory_builder.py
  log_id: pattern-memory-log-001
  memory_count: 4
  status_summary: {recorded: 4}
    pattern-memory-001: recurring_food_support (jammy-house-001) memory_status=recorded learning_is_prescription=false
    pattern-memory-002: ongoing_displacement_relief (dra-001) memory_status=recorded learning_is_prescription=false
    pattern-memory-003: unresolved_tenancy_pattern (jammy-house-001) memory_status=recorded learning_is_prescription=false
    pattern-memory-004: pending_skill_exchange (yacypherpunks-001) memory_status=recorded learning_is_prescription=false
  memory_prescribes_response=false

aid_pattern_report.py
  report_id: aid-pattern-report-001
  section_count: 4
    A: A Pattern Is an Observation, Not a Prediction
    B: Recurrence Does Not Rank Suffering
    C: Learning Does Not Prescribe a Response
    D: Connection to Jammy House and D.R.A. Care Histories
  summary_table:
    pattern_is_prediction: false
    recurrence_is_ranking: false
    learning_is_prescription: false
    ranks_suffering: false
    any_participant_compelled: false
    pattern_history_is_legible: true
    loops_referenced: 4
    patterns_recorded: 4
    recurrences_recorded: 4
    memories_recorded: 4
```

---

## New Files (Phase 20)

- bridge/gitsea/aid_patterns/AID_PATTERN_LEARNING_SPEC.md
- bridge/gitsea/aid_patterns/PATTERN_NOT_PREDICTION.md
- bridge/gitsea/aid_patterns/LEARNING_NOT_PRESCRIPTION.md
- bridge/gitsea/aid_patterns/runtime/aid_pattern_registry.py
- bridge/gitsea/aid_patterns/runtime/recurrence_snapshot.py
- bridge/gitsea/aid_patterns/runtime/pattern_memory_builder.py
- bridge/gitsea/aid_patterns/runtime/aid_pattern_report.py
- bridge/gitsea/aid_patterns/examples/aid-pattern-registry.json (generated)
- bridge/gitsea/aid_patterns/examples/recurrence-snapshot.json (generated)
- bridge/gitsea/aid_patterns/examples/pattern-memory.json (generated)
- bridge/gitsea/aid_patterns/examples/aid-pattern-report.json (generated)

## Updated Files (Phase 20)

- bridge/gitsea/README.md (Phase 20 section + aid_patterns/ in layout + flow diagram + footer)
- bridge/RESUME_STATE.md (this file)

---

## Key Invariants (all Phase 20 files)

| Field | Value |
|-------|-------|
| `authority` | `none` |
| `execution_allowed` | `false` |
| `moves_money` | `false` |
| `hard_enforcement` | `false` |
| `advisory` | `true` |
| `care_loop_only` | `true` |
| `append_only` | `true` |
| `contestable` | `true` |
| `reopenable` | `true` |
| `credit_issued` | `false` (permanent) |
| `pattern_is_prediction` | `false` (invariant) |
| `learning_is_prescription` | `false` (invariant) |
| `recurrence_is_ranking` | `false` (invariant) |
| `pattern_learning_only` | `true` |
| `pattern_ranks_commons` | `false` (invariant) |
| `pattern_compels_response` | `false` (invariant) |
| `memory_prescribes_response` | `false` (invariant) |
| `memory_certifies_resolution` | `false` (invariant) |
| `memory_compels_new_aid` | `false` (invariant) |
| `memory_judges_participants` | `false` (invariant) |
| `ranks_suffering` | `false` (invariant) |
| `recurrence_judges_prior_response` | `false` (invariant) |
| `recurrence_demands_new_response` | `false` (invariant) |
| `recurrence_certifies_failure` | `false` (invariant) |

---

## Protocol Principle Accumulation (Phases 10–20)

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
| 17 | "Need is not debt." |
| 17 | "Help is not command." |
| 17 | "Routing is not allocation." |
| 18 | "Relief is not proof." |
| 18 | "Outcome is not judgment." |
| 18 | "Care memory is not control." |
| 19 | "Reopen is not failure." |
| 19 | "Follow-up is not blame." |
| 19 | "Care loop is not obligation." |
| 20 | "Pattern is not prediction." |
| 20 | "Learning is not prescription." |
| 20 | "Recurrence is not ranking." |

---

## Next Step Candidates

1. **Merge Phase 20 PR** — after review
2. **Phase 21: Cross-Phase Care Summary** — aggregate Phase 16–20 care history
   and pattern memory into a single advisory summary per commons
3. **Pattern clustering** — aggregate D.R.A. displacement patterns into a
   cluster view across commons
4. **Jammy House pattern snapshot** — dedicated summary of Jammy House Phase 16–20
   activity with pattern memory
5. **Voluntary pattern annotation** — allow participants to annotate pattern
   memory records with their own observations (without Dan-Go certifying accuracy)

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
*Need is not debt.*
*Help is not command.*
*Routing is not allocation.*
*Relief is not proof.*
*Outcome is not judgment.*
*Care memory is not control.*
*Reopen is not failure.*
*Follow-up is not blame.*
*Care loop is not obligation.*
*Pattern is not prediction.*
*Learning is not prescription.*
*Recurrence is not ranking.*
*Dan-Go observes treasury context; it does not operate the treasury.*
*Dan-Go records contribution candidates; external systems may issue credit.*
*Dan-Go records commons participation; it does not govern communities.*
*Dan-Go records mutual aid routes; it does not command or allocate.*
*Dan-Go records relief case memory; it does not certify rescue or rank suffering.*
*Dan-Go records care loops; it does not compel resolution or judge participants.*
*Dan-Go records aid patterns; it does not predict, prescribe, or rank.*
*Contribution becomes legible before it becomes valuable.*
