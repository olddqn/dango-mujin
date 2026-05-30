# RESUME_STATE.md — Mutual Aid Routing Layer

> **STATUS: IN PROGRESS (feature/phase-17-mutual-aid-routing)**

**Phase:** Mutual Aid Routing Layer (Phase 17)
**Branch:** feature/phase-17-mutual-aid-routing
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
- **Mutual Aid Routing Layer (Phase 17)** ← current PR

---

## Phase 17: Mutual Aid Routing Layer

Core principles:
> "Need is not debt."
> "Help is not command."
> "Routing is not allocation."

**Purpose:** Records requests for help, voluntary offers of help, and
possible cooperation routes inside commons. Dan-Go does not command
assistance. Dan-Go does not allocate resources. Dan-Go does not rank need.
Dan-Go only records observable aid routes and surfaces possible connections
between requests and offers.

### Phase Chain

```
Phase 11: Contribution Candidate      → candidate_credit: true/false
Phase 12: External Credit Observation → external_credit: false
Phase 13: Reflection Memory           → reflection_recorded: true
Phase 14: Recognition Appeal          → appeal_recorded: true
Phase 15: Recognition Ledger          → recognition_history_complete: true
Phase 16: Cooperation Commons         → commons_recorded: true
Phase 17: Mutual Aid Routing          → aid_route_recorded: true
```

### Runtime Results

```
aid_request_registry.py
  registry_id: aid-request-registry-001
  request_count: 4
  urgency_summary: {medium: 1, urgent: 1, immediate: 1, low: 1}
    aid-request-001: jammy-house-001 — food_support (urgency=medium)
    aid-request-002: dra-001 — housing_support (urgency=urgent)
    aid-request-003: dra-001 — refugee_relief (urgency=immediate)
    aid-request-004: yacypherpunks-001 — skill_exchange (urgency=low)
  need_creates_debt=false on all records
  authority=none, moves_money=false

aid_offer_registry.py
  registry_id: aid-offer-registry-001
  offer_count: 5
  offer_type_summary: {meal_preparation: 1, housing_advocacy: 1,
                       supply_sharing: 1, shelter_hosting: 1, skill_sharing: 1}
    aid-offer-001: jammy-house-001 — meal_preparation, voluntary=true, control=false
    aid-offer-002: jammy-house-001 — housing_advocacy, voluntary=true, control=false
    aid-offer-003: dra-001 — supply_sharing, voluntary=true, control=false
    aid-offer-004: dra-001 — shelter_hosting, voluntary=true, control=false
    aid-offer-005: yacypherpunks-001 — skill_sharing, voluntary=true, control=false
  help_is_command=false on all records
  authority=none, moves_money=false

aid_route_builder.py
  log_id: aid-route-log-001
  route_count: 5
  status_summary: {possible: 4, suggested: 1}
    aid-route-001: aid-request-001 → aid-offer-001 (possible)
    aid-route-002: aid-request-002 → aid-offer-002 (suggested)
    aid-route-003: aid-request-003 → aid-offer-003 (possible)
    aid-route-004: aid-request-003 → aid-offer-004 (possible)
    aid-route-005: aid-request-004 → aid-offer-005 (possible)
  routing_allocates_resources=false on all records
  authority=none, moves_money=false

mutual_aid_report.py
  report_id: mutual-aid-report-001
  section_count: 6
    Help Was Requested — need_creates_debt: false
    Help Was Offered — voluntary: true, offer_creates_obligation: false
    A Route Is Possible — routing_allocates_resources: false, route_compels_exchange: false
    No One Is Commanded — help_is_command: false, authority: none
    No Debt Is Created — need_creates_debt: false, requester_owes_help_received: false
    No Allocation Is Enforced — routing_allocates_resources: false, execution_allowed: false
  summary_table:
    any_party_commanded: false
    debt_created: false
    allocation_enforced: false
    resources_moved: false
    exchange_compelled: false
    participants_decide: true
    commons_remain_self_governing: true
```

---

## New Files (Phase 17)

- bridge/gitsea/mutual_aid/MUTUAL_AID_ROUTING_SPEC.md
- bridge/gitsea/mutual_aid/NEED_NOT_DEBT.md
- bridge/gitsea/mutual_aid/ROUTING_NOT_ALLOCATION.md
- bridge/gitsea/mutual_aid/runtime/aid_request_registry.py
- bridge/gitsea/mutual_aid/runtime/aid_offer_registry.py
- bridge/gitsea/mutual_aid/runtime/aid_route_builder.py
- bridge/gitsea/mutual_aid/runtime/mutual_aid_report.py
- bridge/gitsea/mutual_aid/examples/aid-request-registry.json (generated)
- bridge/gitsea/mutual_aid/examples/aid-offer-registry.json (generated)
- bridge/gitsea/mutual_aid/examples/aid-route.json (generated)
- bridge/gitsea/mutual_aid/examples/mutual-aid-report.json (generated)

## Updated Files (Phase 17)

- bridge/gitsea/README.md (Phase 17 section + mutual_aid/ in layout + flow diagram)
- bridge/RESUME_STATE.md (this file)

---

## Key Invariants (all Phase 17 files)

| Field | Value |
|-------|-------|
| `authority` | `none` |
| `execution_allowed` | `false` |
| `moves_money` | `false` |
| `hard_enforcement` | `false` |
| `advisory` | `true` |
| `mutual_aid_only` | `true` |
| `append_only` | `true` |
| `contestable` | `true` |
| `reopenable` | `true` |
| `credit_issued` | `false` (permanent) |
| `need_creates_debt` | `false` (invariant) |
| `help_is_command` | `false` (invariant) |
| `routing_allocates_resources` | `false` (invariant) |
| `route_compels_exchange` | `false` (invariant) |
| `offer_creates_obligation` | `false` (invariant) |
| `requester_owes_help_received` | `false` (invariant) |

---

## Protocol Principle Accumulation (Phases 10–17)

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

---

## Next Step Candidates

1. **Merge Phase 17 PR** — after review
2. **Phase 18: Aid Outcome Memory** — record outcomes of accepted aid routes
3. **Commons-linked aid** — connect Phase 17 routes to Phase 16 commons membership
4. **Cross-commons routing** — routes spanning two different commons
5. **Aid history ledger** — append-only history of all aid exchanges per participant
6. **Refugee relief cluster** — aggregate D.R.A. refugee relief routes into advisory cluster view

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
*Dan-Go observes treasury context; it does not operate the treasury.*
*Dan-Go records contribution candidates; external systems may issue credit.*
*Dan-Go records commons participation; it does not govern communities.*
*Dan-Go records mutual aid routes; it does not command or allocate.*
*Contribution becomes legible before it becomes valuable.*
