# dango-gitsea-bridge

> 「AはAである」を超越し、「Aが非AのゆえにAである」へ。  
> Transcending "A is A" to "A is A because A is not A."

---

**Dan-Go is a negotiation protocol for impossible claims.**

A claim is a statement of what must become real — even when it currently cannot.  
The protocol asks: *what conditions are missing, and who can close the gap?*

This bridge connects Dan-Go's negotiation layer to GITSEA-style economic accounting,
OGI-compatible world models, and append-only sutable event logs.

---

## The Core Loop

```
Claim
  │
  ▼
World Model          ← what is observed vs what must become true
  │
  ▼
Plan Tree            ← how to close the gap (contestable, not final)
  │
  ▼
Task Bundle          ← derived from the plan (extracted, not executed)
  │
  ▼
Negotiation          ← agents support, object, contest, correct
  │
  ▼
Reflective Memory    ← what was learned, for the next cycle
  │
  └──────────────────► World Model (improved)
```

No step is hidden. No step is irreversible. Every event is append-only.

---

## What Dan-Go Is NOT

| NOT | WHY |
|-----|-----|
| A financial product | No tokens. No staking. No investment. |
| A DAO | No governance votes. No quorum. |
| A blockchain | Append-only JSONL files, not a chain. |
| A planning engine | Plans are proposals, not commands. |
| An AI decision system | Agents negotiate; no AI makes final decisions. |
| A promise to GITSEA | GITSEA is hypothetical. The bridge is real. |
| A consensus mechanism | Disagreement is preserved, not resolved. |

---

## Why This Exists

Most coordination systems ask: *who decides?*

Dan-Go asks: *what conditions are missing, and can they be addressed without violating dignity?*

This reframing matters because:

- Some claims are structurally impossible until upstream conditions change
- Many contributions are invisible to price-only systems
- AI agents need a public, auditable surface to negotiate — not internal hidden state
- Dignity must be protocol-level, not a policy attached to an existing system
- Corrections and objections must remain visible — silence is not resolution

See `WHY_DANGO_EXISTS.md` for the full argument.

---

## Relationship to GITSEA / OGI / gitlawb

| System | Role in Dan-Go |
|--------|---------------|
| **GITSEA** | Hypothetical economic layer. This bridge models the translation from Dan-Go claims to GITSEA-style repo assets and contribution streams. GITSEA's real implementation is unverified. |
| **OGI** | Reasoning surface. `ogi/runtime/` provides world model and plan tree generators compatible with OGI's reasoning format. |
| **gitlawb** | Source of truth. This repo is pushed to `node.gitlawb.com`. gitlawb provides DID-based identity for protocol participants. |
| **Nookplot** | Unknown. Not integrated. |

See `DANGO_GITSEA_OGI_MAP.md` for the full mapping.

---

## Dignity-First Architecture

The dignity guard is not optional. It runs before every other transformation.

```
Dignity Guard (7 rules)
  ├── PASS  → proceed to asset transformation
  ├── BLOCK → hard stop, reason logged
  └── ESCALATE → pause, request human review
```

Rules enforced:
1. Do not violate the dignity of another.
2. Do not monetize suffering without consent.
3. Do not expose location or identity of vulnerable people.
4. Do not treat refugees as content inventory.
5. Do not convert emergency need into speculative asset.
6. Consent, anonymity, revocability, and revenue sharing must be explicit.
7. If unsure, block.

`dignity_violation` objections in plan negotiation automatically disqualify a plan
from active selection — regardless of support count.

---

## Append-Only Negotiation

The **su-table** (素テーブル) is an append-only JSONL event log with SHA256 hash chains.

Nothing is deleted. Corrections are new events. Disagreement is permanently visible.

```
sutable/
├── claims.jsonl          ← claim events
├── negotiations.jsonl    ← objections, supports, decisions
├── contributions.jsonl   ← contribution records
├── executions.jsonl      ← execution events
├── reality_feedback.jsonl← post-execution ground truth
├── plans.jsonl           ← plan trees, task bundles, negotiation signals
└── memory.jsonl          ← reflective memory snapshots
```

Every event carries:
- `timestamp` — ISO 8601 UTC
- `event_hash` — SHA256 of the serialized event body
- `previous_event_hash` — link to the preceding event (chain integrity)

---

## Reflective Memory Loop

Each negotiation cycle produces evidence. The memory layer captures it.

```
memory_append.py     ← snapshot negotiation state into memory.jsonl
memory_snapshot.py   ← query state, detect staleness, view prior knowledge
world_model_with_memory.py  ← inject prior_knowledge into next world model
```

The `prior_knowledge` block carries:
- which plan is active
- what objection types were raised
- what conditions were *learned* from competing plan trees (structural diff)
- how deep the correction chain is

This lets the next plan tree automatically address what the previous one missed.

When two or more claims have memory snapshots, `federation_memory_feedback.py`
detects cross-claim patterns. In the housing network, both housing-001 and
housing-002 independently learned `space_safety_assessed` through structural
plan tree diff — with no coordination. The federation detector surfaces this
as a `federation_prerequisite`: that condition should become a federation-level
requirement. See `examples/federation-memory-feedback.snapshot.json`.

---

## Quick Start

```bash
# 1. Check dignity constraints on a claim
python runtime/dignity_guard.py examples/refugee-story-consented.claim.json

# 2. Build a world model from the claim
python ogi/runtime/world_model_mapper.py examples/refugee-story-consented.claim.json

# 3. View the plan snapshot (housing claim, pre-negotiated)
python runtime/plan_snapshot.py --claim-id housing-001

# 4. See the full negotiation state
python runtime/plan_negotiation_snapshot.py --claim-id housing-001

# 5. Query reflective memory
python runtime/memory_snapshot.py --claim-id housing-001 --prior-knowledge

# 6. Build enriched world model (closes the loop)
python runtime/world_model_with_memory.py --claim-id housing-001

# 7. Export the full negotiation graph
python runtime/graph_export.py --claim-id housing-001 --format text
```

---

## Full Pipeline (housing-001 example)

```bash
# Append a claim event
python runtime/sutable_append.py --table claims \
  --event examples/sutable_events/claim_event.json

# Build plan tree from claim
python runtime/plan_event_append.py examples/plan-event.json

# Negotiate: support a plan
python runtime/plan_negotiation_append.py examples/plan-support-event.json

# Negotiate: object to a plan
python runtime/plan_negotiation_append.py examples/plan-objection-event.json

# Contest: propose a competing plan (counterplan auto-created if embedded)
python runtime/plan_negotiation_append.py examples/plan-contest-event.json

# Select the active plan (deterministic, transparent, 6 rules)
python runtime/active_plan_selector.py --claim-id housing-001

# Snapshot memory
python runtime/memory_append.py --claim-id housing-001

# View enriched world model
python runtime/world_model_with_memory.py --claim-id housing-001
```

---

## Federation-Aware Branching

No claim exists alone. Plans branch on the negotiation state of related claims.

```
housing-001 (base space)         housing-002 (remote collaboration)
  negotiation → active plan  ──────────────┐
  space_safety_assessed ✓               depends_on housing-001
  legal_ownership_confirmed ✓        └─ [active] — conditions met
                                         branch gates satisfied
```

When housing-001 is contested, housing-002 detects a `contest_ripple`:
conditions it relies on may change if the active plan changes.
When housing-001 has a `dignity_violation`, housing-002 is `blocked`.

```bash
# Compute branch status for a claim
python runtime/federation_branching.py --claim-id housing-002

# Propagate conditions from an upstream claim
python runtime/federation_condition_propagation.py --source-claim housing-001

# Full federation activation snapshot
python runtime/federation_activation.py

# Detect ripple effects across the federation
python runtime/federation_ripple_detector.py

# Cross-claim trust propagation
python runtime/federation_trust_propagation.py --all-pairs

# Federation-wide memory feedback
python runtime/federation_memory_feedback.py

# Graph export now includes FEDERATION BRANCHING section
python runtime/graph_export.py --claim-id housing-001 --format text
```

**Spec:** `FEDERATION_BRANCHING_SPEC.md`

---

## Federation Prerequisite Promotion

A condition discovered independently by multiple claims becomes a federation prerequisite.

Not because someone declared it. Because the negotiation evidence converges.

```
housing-001: plan contested → counterplan adds space_safety_assessed
housing-002: plan contested → counterplan adds space_safety_assessed
                                    ↓
              federation_prerequisite_promoted
                authority: none
                evidence_claims: [housing-001, housing-002]
                independent_convergence: true
                contestable: true
```

`authority: "none"` is not a placeholder. It is the architecture.
No coordinator promotes a prerequisite. Structural convergence does.

A prerequisite becomes stronger when it survives independent convergence
across more claims. When housing-004 (community kitchen) independently
discovered `space_safety_assessed` through a different objector
(`z6KitchenSafetyAgent004`, distinct from `z6Object001`), the prerequisite
was reaffirmed — not re-promoted. The original event is immutable. The
evidence score rose from 6 to 8. Objector concentration fell from 2/2 to 2/3.

Every promoted prerequisite is contestable — by producing a plan tree
that achieves the claim goals without the condition. The protocol has
no permanent prerequisites.

```bash
# Detect candidates
python runtime/federation_prerequisite_detector.py --verbose

# Inspect evidence bundle
python runtime/prerequisite_evidence_bundle.py --condition space_safety_assessed

# Promote
python runtime/prerequisite_promotion.py --append

# View snapshot
python runtime/prerequisite_snapshot.py --evidence

# Contest a prerequisite
python runtime/prerequisite_contest_resolver.py \
    --contest space_safety_assessed \
    --reason "..." --speaker did:key:zContester

# Memory integration (advisory hints for next plan tree cycle)
python runtime/prerequisite_memory_integration.py --all-claims
```

**Spec:** `FEDERATION_PREREQUISITE_SPEC.md`

### Prerequisite Deprecation Lifecycle

A prerequisite must remain weakeneable, or it is no longer evidence-based.

housing-006 (pre-certified modular emergency kitchen) demonstrates this:
its plan uses `precertified_structure + external_safety_audit_attached +
embedded_fire_controls` in place of `space_safety_assessed`. This is a
**bypass with an equivalent safety path** — not a gap.

Outcome: `space_safety_assessed` is now in **weakened** state.
Scope narrowed to `non_precertified_spaces`. The prerequisite still
applies to any claim that lacks the equivalent precertification evidence.

Survivability score = `requiring / (requiring + bypassing) - 0.15 penalty`
= `4 / (4+1) - 0.15` = **0.65** (weakened, not at_risk). Updated after housing-007 added as requiring claim.

Deprecation requires a second bypass claim (bypass_count ≥ 2) plus an
explicit `federation_prerequisite_deprecated` event — no auto-removal.

```bash
# Detect bypass patterns and survivability
python runtime/prerequisite_deprecation_detector.py
python runtime/prerequisite_survivability.py

# Preview weakening (dry-run)
python runtime/prerequisite_weakening.py

# Full lifecycle snapshot
python runtime/prerequisite_deprecation_snapshot.py

# Reevaluate all signals
python runtime/prerequisite_reevaluation.py
```

**Spec:** `PREREQUISITE_DEPRECATION_SPEC.md`

### Scoped Prerequisite Inheritance

A weakened prerequisite does not disappear. Its applicability becomes conditional.

housing-006's bypass narrowed `space_safety_assessed` to `non_precertified_spaces`.
housing-007 (modified community workspace — old building, local modifications,
no external audit, no precertification) confirms the other half: the prerequisite
is **applicable** where the bypass path is absent.

Two claims, same condition, opposite resolution. The scope rule mediates:

```
space_safety_assessed
  applies_to:  non_precertified_spaces      ← housing-007: applicable
  bypassed_by: precertified_modular_spaces  ← housing-006: bypassed
```

Resolution is deterministic — no text analysis, no fuzzy scoring. Bypass
requires a `bypass_condition` in the active plan. Scope is not assigned by
any coordinator. The plan assigns it to itself.

```bash
# Scope rules + per-claim resolution
python runtime/prerequisite_scope_resolver.py
python runtime/prerequisite_scope_resolver.py --condition space_safety_assessed --claim-id housing-007

# Per-claim inheritance (applicable / bypassed / unscoped)
python runtime/scoped_prerequisite_inheritance.py --claim-id housing-007 --json

# Scope conflict detection (advisory only)
python runtime/scope_conflict_detector.py

# Scope-aware propagation hints
python runtime/scoped_condition_propagation.py --claim-id housing-006

# Full scoped snapshot
python runtime/scoped_prerequisite_snapshot.py --condition space_safety_assessed --json
```

**Spec:** `SCOPED_PREREQUISITE_SPEC.md`

### Gitlawb / GITSEA Demo

Dan-Go can turn a missing condition into an agent-readable issue.
This is a bountyless market:
not money-first,
condition-first.

A missing condition discovered through negotiation (e.g., `space_safety_assessed`
in housing-004) travels a pipeline:

```
Claim → Issue → Agent Task → PR → Reality Feedback → Stream Candidate
```

No step is automatic. No step moves money. No step creates authority.
GITSEA may later provide economic streams for accepted contributions.
This demo does not activate them.

```bash
# Claim → issue draft (no real issue created)
python bridge/gitlawb/runtime/claim_to_issue.py bridge/gitlawb/examples/claim-to-issue.input.json

# Issue → agent task spec (no task created)
python bridge/gitlawb/runtime/issue_to_agent_task.py bridge/gitlawb/examples/issue-draft.output.json

# PR events → reality feedback (no su-table written)
python bridge/gitlawb/runtime/pr_feedback_mapper.py bridge/gitlawb/examples/pr-feedback.output.json

# Contributions → GITSEA stream candidates (no funds, no connection)
python bridge/gitlawb/runtime/stream_candidate_preview.py bridge/gitlawb/examples/pr-feedback.output.json
```

**Demo:** `bridge/gitlawb/DANGO_GITLAWB_GITSEA_DEMO.md`

---

## Structure

```
dango-gitsea-bridge/
├── README.md                        ← This file
├── ARCHITECTURE_OVERVIEW.md         ← Full system architecture
├── WHY_DANGO_EXISTS.md              ← The argument for this protocol
├── DANGO_GITSEA_OGI_MAP.md         ← How Dan-Go maps to GITSEA / OGI / gitlawb
├── FEDERATION_BRANCHING_SPEC.md     ← Federation-aware plan branching
├── SCOPED_PREREQUISITE_SPEC.md      ← Scoped prerequisite inheritance layer
├── FEDERATION_PREREQUISITE_SPEC.md  ← Federation prerequisite promotion
├── VISUAL_SYSTEM_MAP.mmd            ← Mermaid architecture diagram
├── EXAMPLES_INDEX.md                ← Guide to all example files
│
├── DANGO_GITSEA_THESIS.md           ← Original thesis
├── CLAIM_TO_REPO_ASSET.md           ← Claim → repo asset mapping
├── CONTRIBUTION_STREAM_SPEC.md      ← Contribution stream spec
├── DIGNITY_GUARD.md                 ← Dignity guard (7 rules)
├── PASS_FLOW_EXAMPLE.md             ← Consent-established PASS flow walkthrough
├── RISK_ASSESSMENT.md               ← Known risks and limitations
├── REFUGEE_STORY_STREAM_ETHICS.md   ← Ethics of story-based streams
├── SUTABLE_APPEND_ONLY_SPEC.md      ← Su-table specification
├── PLAN_APPEND_ONLY_SPEC.md         ← Plan + task bundle persistence
├── PLAN_NEGOTIATION_SPEC.md         ← Multi-agent plan negotiation
├── REFLECTIVE_MEMORY_SPEC.md        ← Reflective memory loop
├── CLAIM_FEDERATION_SPEC.md         ← Claim federation
├── DID_SIGNATURE_SPEC.md            ← DID signature (mock)
├── TEMPORAL_TRUST_DECAY_SPEC.md     ← Trust decay specification
├── NEGOTIATION_GRAPH_SPEC.md        ← Negotiation graph spec
│
├── runtime/                         ← Dan-Go bridge runtime (stdlib only)
│   ├── sutable_log.py               ← JSONL append + SHA256 hash chain
│   ├── sutable_append.py            ← CLI: append event to su-table
│   ├── sutable_query.py             ← CLI: query su-table events
│   ├── claim_to_asset.py            ← Claim → repo asset
│   ├── dignity_guard.py             ← 7-rule dignity gate
│   ├── stream_preview.py            ← Stream eligibility preview
│   ├── contribution_ledger.py       ← Contribution ledger
│   ├── negotiation_event.py         ← Structured negotiation events
│   ├── reality_feedback_append.py   ← Reality feedback events
│   ├── negotiation_graph.py         ← Graph builder from su-table
│   ├── graph_export.py              ← Export: Mermaid / text / HTML
│   ├── plan_event_append.py         ← Plan tree event append
│   ├── task_bundle_append.py        ← Task bundle event append
│   ├── plan_correction.py           ← Plan correction / amendment
│   ├── plan_snapshot.py             ← View plan + correction chain
│   ├── plan_negotiation_append.py   ← Support / objection / contest events
│   ├── active_plan_selector.py      ← Deterministic active plan selection
│   ├── plan_contest_resolver.py     ← Contest chain + signal aggregation
│   ├── plan_negotiation_snapshot.py ← Negotiation state snapshot
│   ├── plan_negotiation_graph.py    ← Plan contest graph
│   ├── reflective_memory.py         ← Memory record from plans.jsonl
│   ├── memory_append.py             ← Append memory snapshot
│   ├── memory_snapshot.py           ← Query memory / stale diff
│   ├── world_model_with_memory.py   ← World model + prior_knowledge
│   ├── did_signature.py             ← Mock DID signature library
│   ├── sign_event.py                ← Attach mock signature to event
│   ├── verify_event_signature.py    ← Verify mock signature
│   ├── temporal_trust_decay.py      ← Trust decay (deterministic)
│   ├── contribution_weight.py       ← Trust weight for single event
│   ├── trust_snapshot.py            ← Contributor trust snapshot
│   ├── claim_dependency.py          ← Claim dependency events
│   ├── claim_federation.py          ← Claim federation graph
│   ├── federation_graph.py          ← Federation graph builder
│   ├── federation_snapshot.py       ← Federation state snapshot
│   ├── federation_branching.py      ← Branch activation status per claim
│   ├── federation_condition_propagation.py ← Condition propagation from active plans
│   ├── federation_trust_propagation.py ← Cross-claim trust weighting
│   ├── federation_activation.py     ← Federation-wide activation snapshot
│   ├── federation_ripple_detector.py ← Ripple effect detection
│   ├── federation_memory_feedback.py ← Cross-claim memory pattern synthesis
│   ├── federation_prerequisite_detector.py ← Cross-claim condition convergence
│   ├── prerequisite_evidence_bundle.py ← Evidence bundle per prerequisite
│   ├── prerequisite_promotion.py    ← Promote candidates to federation events
│   ├── prerequisite_contest_resolver.py ← Contest / reaffirm / deprecate / weaken
│   ├── prerequisite_snapshot.py     ← Query prerequisite state (incl. weakened)
│   ├── prerequisite_memory_integration.py ← Advisory hints → world model
│   ├── prerequisite_alternative_plan.py ← Detect bypass plans with equiv safety
│   ├── prerequisite_deprecation_detector.py ← Bypass patterns + weakening/deprecation candidates
│   ├── prerequisite_survivability.py ← Survivability score (requiring vs bypassing)
│   ├── prerequisite_weakening.py    ← Append weakened events (scope narrowing)
│   ├── prerequisite_reevaluation.py ← Lifecycle synthesis (all signals)
│   ├── prerequisite_deprecation_snapshot.py ← Full lifecycle query
│   ├── prerequisite_scope_resolver.py ← Scope rule loading + per-claim resolution
│   ├── scoped_prerequisite_inheritance.py ← Applicable / bypassed / unscoped per claim
│   ├── scope_conflict_detector.py   ← Contradictory scope condition detection (advisory)
│   ├── scoped_condition_propagation.py ← Scope-aware prerequisite propagation hints
│   ├── scoped_world_model.py        ← Scoped prior_knowledge integration
│   └── scoped_prerequisite_snapshot.py ← Full scoped lifecycle query
│
│
├── gitlawb/                         ← Gitlawb / GITSEA bountyless PR market demo
│   ├── README.md                    ← Entry point
│   ├── DANGO_GITLAWB_GITSEA_DEMO.md ← Full pipeline overview
│   ├── CLAIM_TO_ISSUE_SPEC.md       ← Claim → issue translation spec
│   ├── ISSUE_TO_PR_FEEDBACK_SPEC.md ← Issue → agent task → PR → feedback
│   ├── GITSEA_STREAM_CANDIDATE_SPEC.md ← Stream candidate structure
│   ├── examples/
│   │   ├── claim-to-issue.input.json  ← housing-004 claim with missing condition
│   │   ├── issue-draft.output.json    ← Issue draft + agent task hint
│   │   ├── pr-feedback.output.json    ← Hypothetical PR lifecycle events
│   │   └── stream-candidate.output.json ← GITSEA stream candidates (no funds)
│   └── runtime/
│       ├── claim_to_issue.py          ← Claim → Gitlawb issue draft
│       ├── issue_to_agent_task.py     ← Issue draft → agent task spec
│       ├── pr_feedback_mapper.py      ← PR events → reality feedback
│       └── stream_candidate_preview.py← Contributions → stream candidates
│
├── ogi/                             ← OGI-compatible reasoning surface
│   └── runtime/
│       ├── world_model_mapper.py    ← Claim → OGI world model
│       ├── claim_plan_tree.py       ← World model → Plan tree
│       ├── plan_tree_validator.py   ← Plan tree validation
│       ├── plan_tree_to_tasks.py    ← Plan tree → Task bundle
│       ├── task_dependency_resolver.py ← Task dependency resolution
│       └── post_scarcity_guard.py   ← Post-scarcity plan guard
│
├── sutable/                         ← Live append-only event logs
│   ├── claims.jsonl
│   ├── negotiations.jsonl
│   ├── contributions.jsonl
│   ├── executions.jsonl
│   ├── reality_feedback.jsonl
│   ├── plans.jsonl
│   └── memory.jsonl
│
└── examples/                        ← Reference JSON examples
    ├── scoped-prerequisite-event.json ← Prerequisite lifecycle: promoted→reaffirmed→weakened
    ├── scoped-inheritance.snapshot.json ← Full cross-claim scope resolution snapshot
    ├── housing-007-scope-resolution.json ← housing-007 scope resolution detail
    ├── scoped-world-model.json      ← Scoped prior_knowledge for housing-006 and housing-007
    ├── housing-001.*                ← Full housing claim lifecycle
    ├── refugee-story*.claim.json    ← Dignity-sensitive claim examples
    ├── plan-*.json                  ← Plan events
    ├── memory-snapshot.json         ← Memory snapshot example
    ├── world-model-with-memory.json ← Enriched world model example
    ├── trust-decay-*.json           ← Trust decay examples
    ├── claim-federation.json        ← Federation graph example
    └── sutable_events/              ← Raw su-table event examples
```

See `EXAMPLES_INDEX.md` for a guided tour of the examples.

---

## Runtime Overview

All runtime modules:
- **stdlib only** — no pip installs, no external dependencies
- **independently runnable** — each module has a CLI (`python runtime/module.py --help`)
- **read-only by default** — queries do not write; appends are explicit
- **no execution** — plans are proposals; no module runs tasks

---

## Principles

1. No financial product. No investment solicitation.
2. No tokens. No staking. No DAO.
3. Dignity before efficiency. Always.
4. GITSEA is hypothetical. The bridge is real.
5. If GITSEA fails, fork to another layer. Forks are valid participation.
6. Consent, anonymity, revocability — explicit or blocked.
7. Disagreement is part of the protocol. Silence is not resolution.
8. Do not violate the dignity of another.

---

## Specs

| Document | Subject |
|----------|---------|
| `ARCHITECTURE_OVERVIEW.md` | Full system architecture |
| `WHY_DANGO_EXISTS.md` | The argument for this protocol |
| `DANGO_GITSEA_OGI_MAP.md` | Dan-Go ↔ GITSEA ↔ OGI ↔ gitlawb mapping |
| `SUTABLE_APPEND_ONLY_SPEC.md` | Append-only event log |
| `PLAN_APPEND_ONLY_SPEC.md` | Plan + task bundle persistence |
| `PLAN_NEGOTIATION_SPEC.md` | Multi-agent plan negotiation |
| `REFLECTIVE_MEMORY_SPEC.md` | Reflective memory loop |
| `CLAIM_FEDERATION_SPEC.md` | Claim federation |
| `FEDERATION_BRANCHING_SPEC.md` | Federation-aware plan branching |
| `FEDERATION_PREREQUISITE_SPEC.md` | Federation prerequisite promotion |
| `DID_SIGNATURE_SPEC.md` | DID signature (mock) |
| `TEMPORAL_TRUST_DECAY_SPEC.md` | Trust decay |
| `DIGNITY_GUARD.md` | Dignity guard rules |
| `DANGO_GITSEA_THESIS.md` | Why this bridge exists |
