# Federation-Aware Plan Branching Specification

> **Status:** Implemented  
> **Version:** 1.0  
> **Part of:** dango-gitsea-bridge / Claim Federation Layer

---

## Core Principle

**No claim exists alone.**

A plan tree for claim B may branch on the negotiation result of claim A.
A dignity violation in claim A propagates risk to all claims that depend on A.
A contest in claim A requires re-evaluation of conditions already assumed by B and C.

Federation-aware branching is the mechanism by which claims become a
**negotiation ecosystem** — not isolated silos.

---

## Why Claims Are Interdependent

Coordination problems don't decompose cleanly. Real projects create webs:

- **housing-001** (vacant building as creative space) is contested
- **housing-002** (remote collaboration layer) *cannot proceed* until housing-001's
  legal ownership and safety assessment are confirmed
- **housing-003** (safety counterclaim) must be resolved for housing-005
  (remediation claim) to become meaningful
- **housing-004** (community kitchen) is *enabled by* housing-001's success

Without federation-aware branching, plans for housing-002 would generate tasks
assuming conditions that haven't been confirmed. Resources would be allocated
to infrastructure that can't be installed.

With branching, housing-002's plan tree gates on `housing-001.space_safety_assessed`
and `housing-001.legal_ownership_confirmed`. Until those conditions are met,
housing-002 is in a `paused` state — visibly, auditably, not silently.

---

## Branch Status Values

| Status | Meaning |
|--------|---------|
| `active` | All upstream dependencies satisfied; claim can proceed |
| `paused` | Upstream claim(s) still negotiating; wait for resolution |
| `blocked` | Upstream has `dignity_violation` or all plans formally rejected |
| `unknown` | Insufficient information to determine status |

**Status is computed, not assigned.** It derives from the event log.

---

## Condition Propagation

When an upstream claim reaches an active plan state, the conditions
satisfied by that plan become visible to downstream claims.

### How conditions are extracted

1. **From reflective memory** — `extract_prior_knowledge()` returns `learned_conditions`
   (conditions discovered by structural plan tree diff during negotiation)
2. **From active plan tree** — `extract_conditions()` walks the plan tree and collects
   all `condition` field values from `branch` nodes

### Propagation flow

```
housing-001 active plan (plan-housing-001-v3)
  └─ conditions: [legal_ownership_confirmed, space_safety_assessed, ...]
       │
       ▼
federation_condition_propagation.py
  └─ propagated to: housing-002 (depends_on), housing-004 (enables)
       │
       ▼
federation_condition_met event (advisory, appended to federation.jsonl)
  └─ { event_type: "federation_condition_met",
       claim_id: "housing-002",
       depends_on_claim_id: "housing-001",
       condition: "space_safety_assessed",
       source_plan_id: "plan-housing-001-v3" }
```

### Why propagation is advisory

Propagation records what conditions are **now knowable** by dependent claims.
It does not:
- Automatically start or resume any plan
- Guarantee that the condition will remain true
- Override local dignity or negotiation requirements

A downstream claim that receives a propagated condition still needs its own
plan, its own dignity gate, and its own negotiation.

---

## Dignity Propagation

A `dignity_violation` objection on an upstream plan propagates **risk** downstream.

```
housing-001 plan_objected (dignity_violation)
  └─ All claims that depend on housing-001 are marked [blocked]
  └─ federation_condition_blocked event appended
  └─ No conditions propagated (propagation is paused)
```

This is the strongest safety signal in the federation layer. A claim whose
upstream has a dignity_violation objection should not proceed —
it might be building infrastructure on a dignity-compromised foundation.

**Resolution path:** The dignity objection must be addressed (plan corrected,
objection withdrawn, or new plan proposed) before downstream claims can
become `active` again.

---

## Ripple Effects

A ripple effect is a cascade where one claim's state affects others in ways
that aren't captured by direct dependency relationships.

### Ripple types

| Type | Description | Severity |
|------|-------------|---------|
| `blocking_chain` | Claim X is blocked → all claims depending on X are also blocked | High if 3+ affected |
| `dignity_spread` | Dignity violation in X propagates risk to Y, Z | Always high |
| `contest_ripple` | Contest in X may change active plan → conditions Y,Z assumed may no longer hold | Medium/high |
| `instability` | X has many contests + objections + counterclaims AND blocks multiple claims | High if score ≥6 |

### Instability score formula

```
score = (contest_count + objection_count + counterclaim_count)
      × max(downstream_count, 1)
```

An instability score of 6 or above is `high`. A score of 3-5 is `medium`.

### Why ripple visibility matters

Without ripple detection, an agent planning housing-002 might not know that
housing-001's contested plan could change — and that the `space_safety_assessed`
condition housing-002 is relying on might disappear if a new active plan is selected.

Ripple detection makes this uncertainty visible before it causes wasted work.

---

## Federation Trust Propagation

Trust signals from contributors in upstream claims inform the starting baseline
for downstream claims.

### Formula

```
propagated_weight = base_weight × attenuation_factor (default: 0.8)
```

For contributors shared across both claims:
```
propagated_weight = min(base_weight × 0.8, 1.0)
```

For source-only contributors (not yet active in target claim):
```
propagated_weight = min(base_weight × 0.8 × 0.5, 1.0)
```

### Hard rules

- `dignity_violation` on source claim → propagated_trust_weight = 0. No floor.
- Trust is never automatically applied — it is an advisory signal
- Propagated trust does not override local trust decay computation

### Aggregate

The aggregate `propagated_trust_weight` is the mean across all contributors.
This is a baseline signal, not a threshold or gate.

---

## Federation Memory Feedback

Reflective memory from individual claims can reveal cross-claim patterns.

### Pattern detection

When the **same condition** is learned independently by ≥2 claims:
→ `federation_prerequisite` hint: this condition should be a federation-level requirement

When the **same objection type** appears across ≥2 claims:
→ `shared_risk_pattern` hint: systematic risk that individual plans aren't addressing

When **multiple claims** have high correction chain depth (≥2 hops):
→ `correction_pattern` hint: federation-wide plan quality needs review

### Planning hint example

```json
{
  "hint": "'insufficient_risk_coverage' objections recur across 2 claims — consider a federation-wide review",
  "hint_type": "shared_risk_pattern",
  "objection_type": "insufficient_risk_coverage",
  "triggered_by": ["housing-001", "housing-002"],
  "recurrence_count": 2
}
```

Hints are appended to `federation.jsonl` as `federation_memory_feedback` events.

---

## New Event Types

All new events are stored in `sutable/federation.jsonl` (append-only).

| Event type | Meaning |
|------------|---------|
| `federation_condition_met` | Upstream condition confirmed satisfied for downstream claim |
| `federation_condition_blocked` | Upstream condition blocked by dignity_violation |
| `federation_claim_activated` | Claim unblocked — all dependencies met |
| `federation_claim_paused` | Claim waiting on upstream resolution |
| `federation_ripple_detected` | Cascading effect detected (blocking_chain, dignity_spread, etc.) |
| `federation_memory_feedback` | Cross-claim planning hint from memory analysis |

### `federation_condition_met` example

```json
{
  "event_type": "federation_condition_met",
  "claim_id": "housing-002",
  "depends_on_claim_id": "housing-001",
  "condition": "space_safety_assessed",
  "source_plan_id": "plan-housing-001-v3",
  "timestamp": "..."
}
```

### `federation_claim_activated` example

```json
{
  "event_type": "federation_claim_activated",
  "claim_id": "housing-002",
  "activation_reason": "dependent claim reached dignity-safe active state: ['housing-001']",
  "activated_by_claim": "housing-001",
  "timestamp": "..."
}
```

---

## No Central Orchestrator

Federation branching has **no central authority** that decides activation.

Each module reads the public event log and computes state independently.
Any participant with access to `federation.jsonl` and `plans.jsonl` can
run the same computation and arrive at the same result.

There is no coordinator that says "now housing-002 is active."
There is a deterministic computation: given the same event log, the same
branch statuses, ripple effects, and trust propagation are always produced.

---

## CLI Reference

### Branch status

```bash
# Status for one claim
python runtime/federation_branching.py --claim-id housing-002

# All claims in federation
python runtime/federation_branching.py --all-claims --verbose

# JSON output
python runtime/federation_branching.py --claim-id housing-002 --json
```

### Condition propagation

```bash
# Compute propagation from source claim (read-only)
python runtime/federation_condition_propagation.py --source-claim housing-001

# Record propagation events (append to federation.jsonl)
python runtime/federation_condition_propagation.py --source-claim housing-001 --append

# Preview without writing
python runtime/federation_condition_propagation.py --source-claim housing-001 --dry-run
```

### Activation snapshot

```bash
# Full federation activation snapshot
python runtime/federation_activation.py

# Append activation events
python runtime/federation_activation.py --append

# Single claim
python runtime/federation_activation.py --claim-id housing-002
```

### Ripple detection

```bash
# Detect all ripples (default: all severities)
python runtime/federation_ripple_detector.py

# High severity only
python runtime/federation_ripple_detector.py --severity high

# Record ripple events
python runtime/federation_ripple_detector.py --append
```

### Trust propagation

```bash
# One pair
python runtime/federation_trust_propagation.py \
  --source-claim housing-001 --target-claim housing-002

# All connected pairs
python runtime/federation_trust_propagation.py --all-pairs
```

### Federation memory feedback

```bash
# Compute cross-claim patterns
python runtime/federation_memory_feedback.py

# Record planning hints
python runtime/federation_memory_feedback.py --append
```

### Graph export (includes federation branching)

```bash
# Text export now includes FEDERATION BRANCHING section
python runtime/graph_export.py --claim-id housing-001 --format text

# Federation-only view for claims not yet in su-table
python runtime/graph_export.py --claim-id housing-002 --format text
```

---

## Integration Pipeline

Full federation branching cycle for the housing claim network:

```bash
# 1. Check current branch statuses
python runtime/federation_branching.py --all-claims

# 2. Propagate conditions from housing-001 (which has an active plan)
python runtime/federation_condition_propagation.py --source-claim housing-001 --append

# 3. Record activation events
python runtime/federation_activation.py --append

# 4. Detect ripple effects
python runtime/federation_ripple_detector.py

# 5. Federation memory feedback (after housing-002 gets a memory snapshot)
python runtime/memory_append.py --claim-id housing-002
python runtime/federation_memory_feedback.py

# 6. View full graph with federation branching section
python runtime/graph_export.py --claim-id housing-001 --format text
```

---

## Design Principles

1. **Advisory, not executory** — propagation informs; it does not trigger.
2. **Append-only** — every state change is a new event. Nothing is overwritten.
3. **No central orchestrator** — status is computed from the event log by anyone.
4. **Dignity propagates before conditions** — dignity_violation on upstream is checked
   before any conditions are propagated.
5. **Deterministic** — same event log → same branch statuses, always.
6. **Visible disagreement** — ripples make cascading uncertainty auditable.

---

## Related Specs

- [CLAIM_FEDERATION_SPEC.md](CLAIM_FEDERATION_SPEC.md) — base federation layer
- [PLAN_NEGOTIATION_SPEC.md](PLAN_NEGOTIATION_SPEC.md) — plan negotiation (includes memory integration)
- [REFLECTIVE_MEMORY_SPEC.md](REFLECTIVE_MEMORY_SPEC.md) — memory loop
- [ARCHITECTURE_OVERVIEW.md](ARCHITECTURE_OVERVIEW.md) — full system architecture
