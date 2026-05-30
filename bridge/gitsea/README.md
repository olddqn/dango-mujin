# bridge/gitsea — GITSEA Asset Bridge

**GITSEA can make repository contribution economically legible.
Dan-Go makes contribution negotiable before it becomes economic.**

This directory connects the Dan-Go protocol to GITSEA asset registration,
lifecycle signalling, and treasury visibility.

It is advisory only. No GITSEA API is called. No funds are moved.
No on-chain operation is performed. stdlib only.

---

## Phase 18 — Relief Case Memory Layer

Dan-Go records observable relief case memory after mutual aid routes without
certifying rescue, judging outcomes, or controlling care. Cases are
reopenable. Memory is advisory.

**"Relief is not proof."**
**"Outcome is not judgment."**
**"Care memory is not control."**

```bash
# Record relief cases linked to Phase 17 aid routes
python bridge/gitsea/relief/runtime/relief_case_registry.py --save

# Record observable outcomes without judging them
python bridge/gitsea/relief/runtime/relief_outcome_snapshot.py --save

# Build care memory from route + case + outcome records
python bridge/gitsea/relief/runtime/care_memory_builder.py --save

# Generate relief memory report
python bridge/gitsea/relief/runtime/relief_memory_report.py --save
```

`relief_memory_only: true`. `relief_is_proof: false`. `outcome_is_judgment: false`. `care_memory_controls: false`. `authority: none`.

---

## Phase 17 — Mutual Aid Routing Layer

Dan-Go records help requests, voluntary offers, and possible aid routes
without creating debt, command, or allocation. Participants decide. Routes
are advisory. Routing is not allocation.

**"Need is not debt."**
**"Help is not command."**
**"Routing is not allocation."**

```bash
# Record help requests inside commons
python bridge/gitsea/mutual_aid/runtime/aid_request_registry.py --save

# Record voluntary offers of help
python bridge/gitsea/mutual_aid/runtime/aid_offer_registry.py --save

# Build advisory routes between requests and offers
python bridge/gitsea/mutual_aid/runtime/aid_route_builder.py --save

# Generate mutual aid report
python bridge/gitsea/mutual_aid/runtime/mutual_aid_report.py --save
```

`mutual_aid_only: true`. `need_creates_debt: false`. `help_is_command: false`. `routing_allocates_resources: false`. `authority: none`.

---

## Phase 16 — Cooperation Commons Layer

Dan-Go records commons participation and cooperation history without
ownership, control, or authority. Communities, projects, houses, and
shared initiatives are made legible — not governed.

**"Community is not authority."**
**"Commons is not ownership."**
**"Participation is not control."**

```bash
# Register advisory commons (communities, projects, houses, initiatives)
python bridge/gitsea/commons/runtime/commons_registry.py --save

# Record participation relationships
python bridge/gitsea/commons/runtime/commons_membership.py --save

# Aggregate commons activity snapshot
python bridge/gitsea/commons/runtime/commons_snapshot.py --save

# Generate commons report
python bridge/gitsea/commons/runtime/commons_report.py --save
```

`commons_only: true`. `ownership: false`. `control: false`. `authority: none`. Community is not authority.

---

## Phase 15 — Recognition Ledger Layer

Dan-Go links candidate, observation, reflection, and appeal records into
an advisory recognition ledger. History is complete. Authority is none.

**"Recognition history is not authority."**
**"Ledger is not judgment."**

```bash
# Build ledger entries (one per contributor, covering Phases 11–14)
python bridge/gitsea/ledger/runtime/ledger_entry_builder.py --save

# Build the combined recognition ledger for a claim
python bridge/gitsea/ledger/runtime/recognition_ledger.py --save

# Snapshot aggregate ledger counts
python bridge/gitsea/ledger/runtime/ledger_snapshot.py --save

# Generate ledger report
python bridge/gitsea/ledger/runtime/ledger_report.py --save
```

`ledger_only: true`. `judgment: false`. `authority: none`. `credit_issued: false`. Append-only history; recognition remains external.

---

## Phase 14 — Recognition Appeal Layer

Dan-Go records advisory recognition appeals without enforcing credit.
Contributors may request reconsideration of unrecognized contributions.
No appeal compels any external system to act.

**"Appeal is not enforcement."**
**"Recognition remains external."**

```bash
# Record advisory recognition appeal
python bridge/gitsea/appeal/runtime/recognition_appeal.py --save

# Assemble self-contained appeal packet (Phase 11-13 records combined)
python bridge/gitsea/appeal/runtime/appeal_packet_builder.py --save

# Snapshot appeal lifecycle status
python bridge/gitsea/appeal/runtime/appeal_status_snapshot.py --save

# Generate appeal reflection report
python bridge/gitsea/appeal/runtime/appeal_reflection_report.py --save
```

`appeal_only: true`. `hard_enforcement: false`. `credit_issued: false`. Dan-Go records; external systems decide.

---

## Phase 13 — Credit Reflection Memory Layer

Dan-Go records credit gaps and unrecognized contribution as reflection memory.
Contribution that was not credited is still observable. Gaps are not failures.

**"Unrecognized contribution is still observable."**
**"Reflection is not judgment."**

```bash
# Record full contribution lifecycle as reflection memory
python bridge/gitsea/reflection/runtime/credit_reflection_memory.py --save

# Record contributions without external credit
python bridge/gitsea/reflection/runtime/unrecognized_contribution.py --save

# Snapshot gap state across contributors
python bridge/gitsea/reflection/runtime/reflection_gap_snapshot.py --save

# Generate reflection report
python bridge/gitsea/reflection/runtime/credit_reflection_report.py --save
```

`credit_issued: false`. `reflection_only: true`. `gap_is_failure: false`. Dan-Go remembers.

---

## Phase 12 — External Credit Adapter Layer

Dan-Go now explicitly distinguishes contribution candidates from external
credit outcomes. The gap between candidate credit and external credit is
documented, observable, and by design.

**"Observation is not issuance."**
**"Candidate credit is not external credit."**

```bash
# Observe external credit systems (no credit issued)
python bridge/gitsea/external_credit/runtime/external_credit_adapter.py --save

# Snapshot external credit observation state
python bridge/gitsea/external_credit/runtime/external_credit_snapshot.py --save

# Compare Dan-Go candidates against external outcomes
python bridge/gitsea/external_credit/runtime/candidate_vs_external.py --save

# Generate human-readable observation report
python bridge/gitsea/external_credit/runtime/credit_observation_report.py --save
```

`external_credit_detected: false`. `credit_issued: false`. Dan-Go observes only.

---

## Phase 11 — Contributor Credit Candidate Layer

Dan-Go now records contributor activity and credit candidates for GITSEA
credit observability. Contribution candidates surface *who* participated and
*what* they contributed — without issuing credit.

**Contribution history is not credit.**
**Dan-Go records contribution candidates; external systems may issue credit.**

```bash
# Record contributors and roles (pseudonymous)
python bridge/gitsea/credit/runtime/contributor_registry.py --save

# Record contribution events as credit candidates
python bridge/gitsea/credit/runtime/contribution_candidate.py --save

# Aggregate candidates into advisory snapshot
python bridge/gitsea/credit/runtime/credit_candidate_snapshot.py --save

# Build append-only contribution history
python bridge/gitsea/credit/runtime/contribution_history.py --save
```

`credit_issued` is always `false`. Dan-Go never issues credit.

---

## Phase 10 — Cooperation Treasury Bridge

Dan-Go now observes the GITSEA RepoVault treasury context for
olddqn/dango-mujin on Base.

This layer connects cooperation signals to treasury visibility without
moving funds.

| Fact | Value |
|------|-------|
| RepoVault | `0x3F9c96A429697B458Fe0a16502A050E5AB50bB00` |
| Chain | Base |
| Owner | `0x89b38ff776565f095b3cd46C5f35EAb27506417C` |
| Event | RepoLinked |
| Status | linked |

**Signal is not reward.**
**Dan-Go observes treasury context; it does not operate the treasury.**

```bash
# Treasury snapshot (advisory, no RPC)
python bridge/gitsea/treasury/runtime/treasury_snapshot.py --save

# Connect cooperation signals to treasury visibility
python bridge/gitsea/treasury/runtime/cooperation_treasury_bridge.py --save

# Read observed on-chain facts (offline)
python bridge/gitsea/treasury/runtime/repovault_reader.py

# Treasury visibility report
python bridge/gitsea/treasury/runtime/treasury_visibility_report.py --save
```

---

## What This Is

The `bridge/gitsea/` layer:

1. Reads `asset.toml` from the repository root (Phase 8)
2. Validates the split, royalty, and insurance declarations (Phase 8)
3. Generates local advisory snapshots and concept mapping documents (Phase 8)
4. Documents how Dan-Go negotiation output relates to GITSEA stream eligibility (Phase 8)
5. Extends the lifecycle: Claim → Cooperation Signal → Asset Signal (Phase 9)
6. Observes the RepoVault treasury context for cooperation history (Phase 10)
7. Records contributor credit candidates for GITSEA observability (Phase 11)
8. Observes external credit systems and documents the candidate/credit gap (Phase 12)
9. Records credit gaps and unrecognized contribution as reflection memory (Phase 13)
10. Records advisory recognition appeals without enforcing credit (Phase 14)
11. Links Phases 11–14 records into an advisory recognition ledger (Phase 15)
12. Records commons participation and cooperation history across communities (Phase 16)
13. Records mutual aid requests, offers, and possible routes without debt, command, or allocation (Phase 17)
14. Records observable relief case memory after aid routes without certifying rescue or judging outcomes (Phase 18)

It does **not** submit to GITSEA, sign transactions, or move funds.

---

## Directory Layout

```
bridge/gitsea/
├── README.md                          ← this file
├── DANGO_GITSEA_INTEGRATION_SPEC.md   ← integration spec
├── GITSEA_ASSET_REGISTRATION.md       ← step-by-step guide + failure notes
├── ASSET_TOML_MAPPING.md              ← field-by-field asset.toml explanation
├── runtime/
│   ├── asset_toml_reader.py           ← read + validate asset.toml
│   ├── asset_registration_snapshot.py ← convert to registration snapshot JSON
│   └── dango_asset_mapper.py          ← map Dan-Go → GITSEA concepts
├── examples/
│   ├── asset.toml.example             ← example asset.toml template
│   ├── asset-registration.snapshot.json  (generated)
│   └── dango-to-gitsea-asset.json        (generated)
├── lifecycle/                         ← Phase 9: asset lifecycle bridge
│   ├── DANGO_GITSEA_LIFECYCLE_SPEC.md
│   ├── CONTRIBUTION_SIGNAL_SPEC.md
│   ├── NEGOTIATION_TO_ASSET_FLOW.md
│   ├── examples/
│   │   ├── asset-lifecycle-housing-007.json
│   │   ├── issue-to-asset.json
│   │   ├── contribution-signal.json
│   │   └── negotiation-snapshot.json
│   └── runtime/
│       ├── asset_lifecycle.py
│       ├── issue_asset_linker.py
│       ├── contribution_evaluator.py
│       └── negotiation_asset_snapshot.py
├── relief/                            ← Phase 18: relief case memory layer
│   ├── RELIEF_CASE_MEMORY_SPEC.md
│   ├── RELIEF_NOT_PROOF.md
│   ├── CARE_MEMORY_NOT_CONTROL.md
│   ├── examples/
│   │   ├── relief-case-registry.json
│   │   ├── relief-outcome-snapshot.json
│   │   ├── care-memory.json
│   │   └── relief-memory-report.json
│   └── runtime/
│       ├── relief_case_registry.py
│       ├── relief_outcome_snapshot.py
│       ├── care_memory_builder.py
│       └── relief_memory_report.py
├── mutual_aid/                        ← Phase 17: mutual aid routing layer
│   ├── MUTUAL_AID_ROUTING_SPEC.md
│   ├── NEED_NOT_DEBT.md
│   ├── ROUTING_NOT_ALLOCATION.md
│   ├── examples/
│   │   ├── aid-request-registry.json
│   │   ├── aid-offer-registry.json
│   │   ├── aid-route.json
│   │   └── mutual-aid-report.json
│   └── runtime/
│       ├── aid_request_registry.py
│       ├── aid_offer_registry.py
│       ├── aid_route_builder.py
│       └── mutual_aid_report.py
├── commons/                           ← Phase 16: cooperation commons layer
│   ├── COOPERATION_COMMONS_SPEC.md
│   ├── COMMUNITY_NOT_AUTHORITY.md
│   ├── COMMONS_NOT_OWNERSHIP.md
│   ├── examples/
│   │   ├── commons-registry.json
│   │   ├── commons-membership.json
│   │   ├── commons-snapshot.json
│   │   └── commons-report.json
│   └── runtime/
│       ├── commons_registry.py
│       ├── commons_membership.py
│       ├── commons_snapshot.py
│       └── commons_report.py
├── ledger/                            ← Phase 15: recognition ledger layer
│   ├── RECOGNITION_LEDGER_SPEC.md
│   ├── LEDGER_NOT_JUDGMENT.md
│   ├── HISTORY_NOT_AUTHORITY.md
│   ├── examples/
│   │   ├── recognition-ledger.json
│   │   ├── ledger-snapshot.json
│   │   ├── ledger-entry.json
│   │   └── ledger-report.json
│   └── runtime/
│       ├── recognition_ledger.py
│       ├── ledger_snapshot.py
│       ├── ledger_entry_builder.py
│       └── ledger_report.py
├── appeal/                            ← Phase 14: recognition appeal layer
│   ├── RECOGNITION_APPEAL_SPEC.md
│   ├── APPEAL_NOT_ENFORCEMENT.md
│   ├── RECOGNITION_REMAINS_EXTERNAL.md
│   ├── examples/
│   │   ├── recognition-appeal.json
│   │   ├── appeal-packet.json
│   │   ├── appeal-status-snapshot.json
│   │   └── appeal-reflection-report.json
│   └── runtime/
│       ├── recognition_appeal.py
│       ├── appeal_packet_builder.py
│       ├── appeal_status_snapshot.py
│       └── appeal_reflection_report.py
├── reflection/                        ← Phase 13: credit reflection memory layer
│   ├── CREDIT_REFLECTION_MEMORY_SPEC.md
│   ├── UNRECOGNIZED_CONTRIBUTION_SPEC.md
│   ├── REFLECTION_NOT_JUDGMENT.md
│   ├── examples/
│   │   ├── credit-reflection-memory.json
│   │   ├── unrecognized-contribution.json
│   │   ├── reflection-gap-snapshot.json
│   │   └── credit-reflection-report.json
│   └── runtime/
│       ├── credit_reflection_memory.py
│       ├── unrecognized_contribution.py
│       ├── reflection_gap_snapshot.py
│       └── credit_reflection_report.py
├── external_credit/                   ← Phase 12: external credit adapter layer
│   ├── EXTERNAL_CREDIT_SPEC.md
│   ├── OBSERVATION_NOT_ISSUANCE.md
│   ├── CANDIDATE_VS_EXTERNAL_CREDIT.md
│   ├── examples/
│   │   ├── credit-adapter.json
│   │   ├── external-credit-snapshot.json
│   │   ├── candidate-vs-external.json
│   │   └── credit-observation-report.json
│   └── runtime/
│       ├── external_credit_adapter.py
│       ├── external_credit_snapshot.py
│       ├── candidate_vs_external.py
│       └── credit_observation_report.py
├── credit/                            ← Phase 11: contributor credit candidates
│   ├── CONTRIBUTOR_CREDIT_SPEC.md
│   ├── CREDIT_CANDIDATE_SPEC.md
│   ├── CONTRIBUTION_HISTORY_SPEC.md
│   ├── examples/
│   │   ├── contributor-registry.json
│   │   ├── contribution-candidate.json
│   │   ├── credit-candidate-snapshot.json
│   │   └── contribution-history.json
│   └── runtime/
│       ├── contributor_registry.py
│       ├── contribution_candidate.py
│       ├── credit_candidate_snapshot.py
│       └── contribution_history.py
└── treasury/                          ← Phase 10: cooperation treasury bridge
    ├── DANGO_TREASURY_VISIBILITY_SPEC.md
    ├── COOPERATION_TREASURY_BRIDGE_SPEC.md
    ├── REPOVAULT_OBSERVATION_NOTES.md
    ├── examples/
    │   ├── treasury-snapshot.json
    │   ├── cooperation-treasury-bridge.json
    │   └── treasury-visibility-report.json
    └── runtime/
        ├── treasury_snapshot.py
        ├── cooperation_treasury_bridge.py
        ├── repovault_reader.py
        └── treasury_visibility_report.py
```

The `asset.toml` lives at the repository root:

```
dango-mujin/
└── asset.toml       ← GITSEA reads this directly (canonical English format)
```

---

## Quick Start

```bash
# Phase 8: Asset registration
python bridge/gitsea/runtime/asset_toml_reader.py asset.toml
python bridge/gitsea/runtime/asset_registration_snapshot.py asset.toml --save

# Phase 9: Lifecycle
python bridge/gitsea/lifecycle/runtime/asset_lifecycle.py --claim housing-007
python bridge/gitsea/lifecycle/runtime/contribution_evaluator.py --save

# Phase 10: Treasury visibility
python bridge/gitsea/treasury/runtime/treasury_snapshot.py --save
python bridge/gitsea/treasury/runtime/cooperation_treasury_bridge.py --save
python bridge/gitsea/treasury/runtime/repovault_reader.py
python bridge/gitsea/treasury/runtime/treasury_visibility_report.py --save

# Phase 11: Contributor credit candidates
python bridge/gitsea/credit/runtime/contributor_registry.py --save
python bridge/gitsea/credit/runtime/contribution_candidate.py --save
python bridge/gitsea/credit/runtime/credit_candidate_snapshot.py --save
python bridge/gitsea/credit/runtime/contribution_history.py --save

# Phase 12: External credit observation
python bridge/gitsea/external_credit/runtime/external_credit_adapter.py --save
python bridge/gitsea/external_credit/runtime/external_credit_snapshot.py --save
python bridge/gitsea/external_credit/runtime/candidate_vs_external.py --save
python bridge/gitsea/external_credit/runtime/credit_observation_report.py --save

# Phase 13: Credit reflection memory
python bridge/gitsea/reflection/runtime/credit_reflection_memory.py --save
python bridge/gitsea/reflection/runtime/unrecognized_contribution.py --save
python bridge/gitsea/reflection/runtime/reflection_gap_snapshot.py --save
python bridge/gitsea/reflection/runtime/credit_reflection_report.py --save

# Phase 14: Recognition appeals
python bridge/gitsea/appeal/runtime/recognition_appeal.py --save
python bridge/gitsea/appeal/runtime/appeal_packet_builder.py --save
python bridge/gitsea/appeal/runtime/appeal_status_snapshot.py --save
python bridge/gitsea/appeal/runtime/appeal_reflection_report.py --save

# Phase 15: Recognition ledger
python bridge/gitsea/ledger/runtime/ledger_entry_builder.py --save
python bridge/gitsea/ledger/runtime/recognition_ledger.py --save
python bridge/gitsea/ledger/runtime/ledger_snapshot.py --save
python bridge/gitsea/ledger/runtime/ledger_report.py --save

# Phase 16: Cooperation commons
python bridge/gitsea/commons/runtime/commons_registry.py --save
python bridge/gitsea/commons/runtime/commons_membership.py --save
python bridge/gitsea/commons/runtime/commons_snapshot.py --save
python bridge/gitsea/commons/runtime/commons_report.py --save

# Phase 17: Mutual aid routing
python bridge/gitsea/mutual_aid/runtime/aid_request_registry.py --save
python bridge/gitsea/mutual_aid/runtime/aid_offer_registry.py --save
python bridge/gitsea/mutual_aid/runtime/aid_route_builder.py --save
python bridge/gitsea/mutual_aid/runtime/mutual_aid_report.py --save

# Phase 18: Relief case memory
python bridge/gitsea/relief/runtime/relief_case_registry.py --save
python bridge/gitsea/relief/runtime/relief_outcome_snapshot.py --save
python bridge/gitsea/relief/runtime/care_memory_builder.py --save
python bridge/gitsea/relief/runtime/relief_memory_report.py --save
```

---

## asset.toml (repo root) — Canonical Format

```toml
[repo]
name = "olddqn/dango-mujin"
license = "MIT"

[splits]
"0x89b38ff776565f095b3cd46C5f35EAb27506417C" = 100

[royalties]
multiplier = 1.0
acceptance = 1.0

[insurance]
merge_insurance = true
```

**TOML 1.0 note:** Section names `[repo]`, `[splits]`, `[royalties]`, `[insurance]`
are ASCII bare keys. Wallet address keys must be quoted (they start with `0`).
GITSEA expects the canonical English ASCII format.

---

## Key Concept

```
Dan-Go negotiation record
    │
    │  (cooperation signals — Phase 9)
    ▼
Cooperation Signal
    │
    │  (treasury context bridge — Phase 10)
    ▼
Treasury Visibility ──────────────────► RepoVault (Base)
    │                                   (observed, not operated)
    │
    │  (credit candidates — Phase 11)
    ▼
Contribution Candidates ──────────────► GITSEA (observes, may issue credit)
    │
    │  (external credit observation — Phase 12)
    ▼
External Credit Observation
    │  candidate_credit ≠ external_credit
    │  gap_is_error: false
    │  observation_only: true
    │
    │
    │  (credit reflection memory — Phase 13)
    ▼
Reflection Memory
    │  unrecognized contributions recorded
    │  gaps observed, not judged
    │  contribution_lost: false
    │
    │  (recognition appeals — Phase 14)
    ▼
Advisory Appeal
    │  appeal_only: true
    │  hard_enforcement: false
    │  appeal_compels_response: false
    │
    │  (recognition ledger — Phase 15)
    ▼
Recognition Ledger
       ledger_only: true
       judgment: false
       authority: none
       recognition_history_complete: true
    │
    │  (cooperation commons — Phase 16)
    ▼
Cooperation Commons
       commons_only: true
       ownership: false
       control: false
       authority: none
       community_recorded: true
    │
    │  (mutual aid routing — Phase 17)
    ▼
Mutual Aid Routing
       mutual_aid_only: true
       need_creates_debt: false
       help_is_command: false
       routing_allocates_resources: false
       authority: none
    │
    │  (relief case memory — Phase 18)
    ▼
Relief Case Memory
       relief_memory_only: true
       relief_is_proof: false
       outcome_is_judgment: false
       care_memory_controls: false
       authority: none
    │
    │  (GITSEA process, not Dan-Go)
    ▼
GITSEA stream eligibility (optional)
```

Dan-Go does not activate the stream. Dan-Go observes treasury context.
Dan-Go records commons participation; it does not govern communities.
Dan-Go records mutual aid routes; it does not command or allocate.
Signal is not reward.

---

## Invariants

Every file in this directory maintains:

| Field | Value |
|-------|-------|
| `execution_allowed` | `false` |
| `moves_money` | `false` |
| `hard_enforcement` | `false` |
| `advisory` | `true` |
| `authority` | `none` |
| `dango_controls_treasury` | `false` |
| `recommended_allocation` | `null` (always) |
| `credit_issued` | `false` (always) |
| `ownership` | `false` (always) |
| `control` | `false` (always) |

No private keys. No wallet operations. No GITSEA API calls.
No Base RPC. No contract calls. stdlib only.

---

*dango-gitsea-bridge · authority: none · advisory · append-only · stdlib only*
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
*Dan-Go observes treasury context; it does not operate the treasury.*
*Dan-Go records contribution candidates; external systems may issue credit.*
*Community is not authority.*
*Commons is not ownership.*
*Participation is not control.*
*Dan-Go records commons participation; it does not govern communities.*
*Need is not debt.*
*Help is not command.*
*Routing is not allocation.*
*Dan-Go records mutual aid routes; it does not command or allocate.*
*Relief is not proof.*
*Outcome is not judgment.*
*Care memory is not control.*
*Dan-Go records relief case memory; it does not certify rescue or rank suffering.*
