# Examples Index — dango-gitsea-bridge

A guided tour of all example files in `examples/`.

---

## How to Use This Index

Examples are reference artifacts. They demonstrate what Dan-Go events, claims,
plans, and graphs look like in practice. They are not test fixtures — they model
real scenarios with realistic (if fictional) content.

To run a pipeline against an example:

```bash
# Always run from bridge/
cd bridge/
```

---

## Housing Claim (housing-001)

The primary worked example. A vacant municipal building proposed as a shared creative space.

This claim has been through the full Dan-Go lifecycle:
- Three competing plan versions (v1, v2, v3)
- Plan correction (v1 → v2)
- Plan contestation (v2 contested by v3)
- Support and objection signals
- Active plan selection (v3 selected)
- Memory snapshot
- Enriched world model

### Files

#### `examples/plan-event.json`
**What it demonstrates:** A `plan_tree_created` event — the first plan proposed for housing-001.

- Plan ID: `plan-housing-001-v1`
- Speaker: `did:key:z6MkproposerHousing`
- Structure: goal → subgoal phases (observation, ownership, safety, coordination, dignity)
- Modules involved: `plan_event_append.py`
- Expected output: event appended to `sutable/plans.jsonl`

```bash
python runtime/plan_event_append.py examples/plan-event.json --dry-run
```

#### `examples/plan-correction-event.json`
**What it demonstrates:** A `plan_tree_corrected` event — the author corrects v1 to v2.

- Corrects: `plan-housing-001-v1` → `plan-housing-001-v2`
- v1 is marked `corrected` (excluded from active plan selection)
- v2 adds a dignity branch (consent conditions)
- Modules involved: `plan_correction.py`, `plan_event_append.py`

```bash
python runtime/plan_snapshot.py --claim-id housing-001
```

#### `examples/competing-plan-a.json`
**What it demonstrates:** Reference file for `plan-housing-001-v2` (the contested plan).

- Contains the full plan tree JSON
- Has `legal_ownership_confirmed` as its risk branch condition
- Used for comparing with competing-plan-b.json

#### `examples/competing-plan-b.json`
**What it demonstrates:** Reference file for `plan-housing-001-v3` (the counterplan).

- Contains the full plan tree JSON
- Speaker: `did:key:z6Contester001`
- Adds `space_safety_assessed` as a *second* risk gate (the structural diff)
- This is the condition learned by the reflective memory layer

#### `examples/plan-support-event.json`
**What it demonstrates:** A `plan_supported` event.

- Supports: `plan-housing-001-v2`
- Support reason: dignity branch coverage is complete (all four consent conditions addressed)
- Modules involved: `plan_negotiation_append.py`
- Key insight: support is structured evidence, not a vote

```bash
python runtime/plan_negotiation_append.py examples/plan-support-event.json --dry-run
```

#### `examples/plan-objection-event.json`
**What it demonstrates:** A `plan_objected` event.

- Objection type: `insufficient_risk_coverage`
- Objects to: `plan-housing-001-v2`
- Reason: shared creative spaces require a `space_safety_assessed` gate
- Key insight: this objection is what the reflective memory layer captures as a learned condition

```bash
python runtime/plan_negotiation_append.py examples/plan-objection-event.json --dry-run
```

#### `examples/plan-contest-event.json`
**What it demonstrates:** A `plan_contested` event with embedded counterplan.

- Contests: `plan-housing-001-v2`
- Counterplan: `plan-housing-001-v3` (embedded inline as `counterplan` dict)
- Auto-creation: when appended, `plan_negotiation_append.py` first creates a
  `plan_tree_created` event for v3, then appends the contest event (with `counterplan` stripped)
- Key insight: a contestant doesn't need to pre-append their plan separately

```bash
python runtime/plan_negotiation_append.py examples/plan-contest-event.json --dry-run
```

#### `examples/plans.snapshot.json`
**What it demonstrates:** Generated output from `plan_snapshot.py`.

- Shows active plan (v3), correction chain (v1→v2), plan statuses
- Regenerate: `python runtime/plan_snapshot.py --claim-id housing-001 --json`

#### `examples/negotiation.snapshot.json`
**What it demonstrates:** Generated output from `plan_negotiation_snapshot.py`.

- Full negotiation state: status, active plan, contested plans, rejected plans,
  support/objection summaries, contest chains
- Regenerate: `python runtime/plan_negotiation_snapshot.py --claim-id housing-001 --json`

#### `examples/memory-snapshot.json`
**What it demonstrates:** A `memory_snapshot_created` event from `memory.jsonl`.

- Memory ID: `mem-housing-001-002`
- Captures: learned_conditions=['space_safety_assessed'], active=plan-housing-001-v3,
  status=contested, correction_depth=1, contest_count=1
- Key insight: `space_safety_assessed` was learned by structural tree diff (v2 vs v3),
  not text-mining
- Regenerate: `python runtime/memory_append.py --claim-id housing-001 --json`

#### `examples/world-model-with-memory.json`
**What it demonstrates:** An enriched world model with `prior_knowledge` injected.

- Contains both `world_model` (from OGI surface) and `prior_knowledge` (from memory.jsonl)
- `state_gap` includes `space_safety_assessed` tagged `learned_from_negotiation`
- Key insight: the next plan tree cycle will automatically address this gap
- Regenerate: `python runtime/world_model_with_memory.py --claim-id housing-001 --json`

#### `examples/housing-001.graph.mmd`
**What it demonstrates:** Rendered negotiation graph in Mermaid format.

- Shows full event timeline for housing-001
- Includes plan history, negotiation signals, claim federation
- View at mermaid.live or in any Mermaid-compatible renderer
- Regenerate: `python runtime/graph_export.py --claim-id housing-001 --format mermaid > examples/housing-001.graph.mmd`

#### `examples/housing-001.graph.html`
**What it demonstrates:** Interactive HTML negotiation graph.

- No external dependencies — opens in any browser
- Includes inline CSS, Mermaid CDN, and full graph
- Regenerate: `python runtime/graph_export.py --claim-id housing-001 --format html --output examples/housing-001.graph.html`

---

## Refugee Story Claim

A dignity-sensitive claim: a refugee's lived story as a potential support stream.

This claim demonstrates the dignity guard's central role. The unconsented version
is blocked. The consented version passes.

### Files

#### `examples/refugee-story.claim.json`
**What it demonstrates:** A claim with missing consent — will fail the dignity guard.

- Missing: `explicit_consent_established`, `anonymization_complete`
- `observed_state` does not include consent signals
- Problem demonstrated: the dignity guard blocks this claim before any transformation
- Modules involved: `dignity_guard.py`

```bash
python runtime/dignity_guard.py examples/refugee-story.claim.json
# Expected: BLOCK — "Consent not established. Cannot proceed."
```

#### `examples/refugee-story-consented.claim.json`
**What it demonstrates:** The same claim with explicit consent — passes the dignity guard.

- `observed_state` includes: `explicit_consent_established`, `anonymization_complete`, `revenue_share_agreed`
- `dignity_constraints` include: `revocable_consent`, `no_identity_exposure`, `fair_revenue_share`
- Decision mode: `negotiate` (not automatic execution)
- Modules involved: `dignity_guard.py`, `claim_to_asset.py`, `stream_preview.py`

```bash
python runtime/dignity_guard.py examples/refugee-story-consented.claim.json
# Expected: PASS — trust_mode: dignity-first

python runtime/claim_to_asset.py examples/refugee-story-consented.claim.json
# Expected: repo asset with stream_eligible: true, trust_mode: dignity-first

python runtime/stream_preview.py \
  examples/refugee-story-consented.claim.json \
  examples/contribution-stream-consented.json
```

#### `examples/contribution-stream.json` and `examples/contribution-stream-consented.json`
**What they demonstrate:** Contribution stream definitions for the refugee claim.

- `contribution-stream.json` — unconsented stream (blocked)
- `contribution-stream-consented.json` — consent-established stream (eligible)
- Modules involved: `stream_preview.py`, `contribution_ledger.py`

---

## Post-Scarcity Claim

**File location:** `ogi/examples/post-scarcity.claim.json`

**What it demonstrates:** An OGI-compatible world model from a post-scarcity-framed claim.

```bash
python ogi/runtime/world_model_mapper.py ogi/examples/post-scarcity.claim.json
```

---

## Claim Federation

**File:** `examples/claim-federation.json`

**What it demonstrates:** A set of federation relationship events between housing claims.

- `housing-002` depends on `housing-001` (remote collaboration requires shared space)
- `housing-004` is enabled by `housing-001` (community kitchen depends on shared space governance)
- `housing-003` is a counterclaim against `housing-001` (safety concern)
- Modules involved: `claim_federation.py`, `federation_snapshot.py`

Key insight: counterclaims do not block. They make disagreement visible.

```bash
python runtime/federation_snapshot.py --claim-id housing-001
python runtime/graph_export.py --claim-id housing-001 --format text
```

#### `examples/claim-dependency.json`
**What it demonstrates:** A single `claim_dependency` event.

#### `examples/claim-counterclaim.json`
**What it demonstrates:** A single `counterclaim` event.

---

## Trust Decay

**Files:** `examples/trust-decay-input.json`, `examples/trust-decay-output.json`,
`examples/contributor-history.json`

**What they demonstrate:** The temporal trust decay formula applied to contribution events.

#### `examples/trust-decay-input.json`
- A `contribution_accepted` event from a translator agent
- Reference date: 2026-05-24 (fixed for reproducibility)
- Event date: 2026-02-01 (112 days prior)
- Expected output: trust_weight ≈ 0.507 (decayed from 1.0 over 112 days, half-life 90)

```bash
python runtime/contribution_weight.py examples/trust-decay-input.json
```

#### `examples/trust-decay-output.json`
- Generated output with decay computation explained field by field:
  `base_weight`, `decay_factor`, `verification_multiplier`, `dignity_multiplier`,
  `continuity_multiplier`, final `trust_weight`

#### `examples/contributor-history.json`
- Multi-contributor example: several agents with different contribution histories
- Demonstrates: continuity bonus (recurring contributions), dignity multiplier,
  different half-life per contribution type
- Modules involved: `trust_snapshot.py`

```bash
python runtime/trust_snapshot.py --claim-id housing-001
```

---

## DID Signature Examples

**Files:** `examples/signed-claim-event.json`, `examples/invalid-signed-event.json`

**What they demonstrate:** Mock DID signatures on su-table events.

> ⚠ These are test vectors, not real cryptography.

#### `examples/signed-claim-event.json`
- A claim event with a valid mock DID signature
- Speaker: `did:key:z6MkproposerHousing`
- Signature field: `did_signature` with `signer`, `signature`, `signed_fields`

```bash
python runtime/verify_event_signature.py examples/signed-claim-event.json
# Expected: ✓ Signature valid
```

#### `examples/invalid-signed-event.json`
- A claim event with a corrupted signature (always rejected)
- Demonstrates: verification catches tampering

```bash
python runtime/verify_event_signature.py examples/invalid-signed-event.json
# Expected: ✗ Signature invalid
```

---

## Su-table Raw Events

**Directory:** `examples/sutable_events/`

Minimal single-event JSON files for testing `sutable_append.py`.

| File | Event type | Purpose |
|------|-----------|---------|
| `claim_event.json` | `claim_created` | Append a new claim |
| `contribution_event.json` | `contribution_accepted` | Append a contribution |
| `execution_event.json` | `execution_started` | Append an execution event |

```bash
python runtime/sutable_append.py --table claims \
  --event examples/sutable_events/claim_event.json --dry-run
```

---

## Example Generation Commands

Regenerate all derived examples from live su-table data:

```bash
# Plan snapshot
python runtime/plan_snapshot.py --claim-id housing-001 --json \
  > examples/plans.snapshot.json

# Negotiation snapshot
python runtime/plan_negotiation_snapshot.py --claim-id housing-001 --json \
  > examples/negotiation.snapshot.json

# Memory snapshot (also appends a new snapshot to memory.jsonl)
python runtime/memory_append.py --claim-id housing-001 --json \
  > examples/memory-snapshot.json

# World model with memory
python runtime/world_model_with_memory.py --claim-id housing-001 --json \
  > examples/world-model-with-memory.json

# Negotiation graph (Mermaid)
python runtime/graph_export.py --claim-id housing-001 --format mermaid \
  > examples/housing-001.graph.mmd

# Negotiation graph (HTML)
python runtime/graph_export.py --claim-id housing-001 --format html \
  --output examples/housing-001.graph.html

# Federation graph (Mermaid)
python runtime/graph_export.py --claim-id housing-001 --format mermaid \
  > examples/federation.graph.mmd
```

---

## The Worked Scenario

All housing-001 examples form a coherent timeline:

```
housing-001 claim created
  │
  ├── plan-housing-001-v1 proposed (plan-event.json)
  │     └── corrected → plan-housing-001-v2 (plan-correction-event.json)
  │
  ├── plan-housing-001-v2 supported (plan-support-event.json)
  │     └── objected: insufficient_risk_coverage (plan-objection-event.json)
  │
  ├── plan-housing-001-v3 proposed as counterplan (plan-contest-event.json)
  │     └── [auto-created] plan_tree_created for v3
  │     └── [auto-created] plan_contested: v2 contested by v3
  │
  ├── active_plan_selector → v3 selected (fewest objections, dignity-safe)
  │
  ├── memory_append → mem-housing-001-001 (learned: space_safety_assessed)
  │
  └── world_model_with_memory → state_gap includes space_safety_assessed [learned]
        └── next plan tree cycle addresses the gap automatically
```

This is the closed reflective memory loop in a real scenario.
