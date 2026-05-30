# bridge/gitsea — GITSEA Asset Bridge

**GITSEA can make repository contribution economically legible.
Dan-Go makes contribution negotiable before it becomes economic.**

This directory connects the Dan-Go protocol to GITSEA asset registration,
lifecycle signalling, and treasury visibility.

It is advisory only. No GITSEA API is called. No funds are moved.
No on-chain operation is performed. stdlib only.

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
    │  (GITSEA process, not Dan-Go)
    ▼
GITSEA stream eligibility (optional)
```

Dan-Go does not activate the stream. Dan-Go observes treasury context.
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
*Dan-Go observes treasury context; it does not operate the treasury.*
*Dan-Go records contribution candidates; external systems may issue credit.*
