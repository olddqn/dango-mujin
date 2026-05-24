# Plan Append-Only Persistence — Specification

> A plan that was wrong is still a record.
> A correction that erases the original is not a correction — it is a lie.

---

## Why Plans Are Append-Only

Dan-Go is a negotiation protocol, not a state machine.

In a state machine, a correction replaces the previous state.
In a negotiation, a correction is itself a negotiation event — it carries
a reason, a speaker, and a timestamp. The history of corrections is as
important as the current state.

Plans are append-only for the same reason su-table events are append-only:

**Negotiation requires historical memory.**

If a plan was wrong, the fact that it was wrong — and how it was corrected —
is part of the claim's record. Future participants need to see the reasoning
trajectory, not just the current approved plan.

---

## What Is a Plan?

A Dan-Go plan is a structured reasoning artifact that sits between
the language surface (claim statement) and the execution surface
(contribution events).

```
Language surface   →  claim statement  (natural language)
Reasoning surface  →  plan tree        (claim_plan_tree.py)
Task bundle        →  task candidates  (plan_tree_to_tasks.py)
Execution surface  →  contributions    (sutable/contributions.jsonl)
```

A plan tree is not a commitment. It is a proposal for how reasoning should
proceed. Multiple versions of a plan may exist for the same claim.

A task bundle is derived from a plan tree. It is a structured set of
negotiable task candidates. It is not an execution order.

Neither a plan tree nor a task bundle executes anything.

---

## Plan Event Types

All plan-related events are stored in `sutable/plans.jsonl`.

### Plan tree events

| Event type | Meaning |
|---|---|
| `plan_tree_created` | A new plan tree is proposed for a claim |
| `plan_tree_amended` | A subcomponent of the plan is amended; the original plan remains active |
| `plan_tree_corrected` | A full correction: new plan supersedes old structurally |

### Task bundle events

| Event type | Meaning |
|---|---|
| `task_bundle_created` | A task bundle is derived from a specific plan tree |
| `task_bundle_blocked` | The bundle is fully blocked (all gates unresolved) |
| `task_bundle_ready` | All gates resolved; bundle is ready for negotiation |
| `task_bundle_abandoned` | The bundle was abandoned (new plan issued or claim withdrawn) |

### Plan negotiation events

| Event type | Meaning |
|---|---|
| `plan_supported` | A speaker signals support for a plan (structured evidence) |
| `plan_objected` | A speaker signals a typed objection to a plan |
| `plan_contested` | A competing plan proposes to replace an existing plan |
| `plan_rejected` | A plan is formally rejected (with reason) |
| `plan_superseded` | A plan is marked superseded by another |
| `active_plan_selected` | Formal record of deterministic active plan selection |

These events are append-only and never deleted.
Support and objection signals are not votes — they are structured negotiation inputs.
The active plan is selected deterministically by `active_plan_selector.py`.

See `PLAN_NEGOTIATION_SPEC.md` for the full multi-agent negotiation specification.

---

## Correction vs. Amendment

### Correction (`plan_tree_corrected`)

A correction is a structural replacement. The corrected plan is superseded.

```json
{
  "event_type": "plan_tree_corrected",
  "plan_id": "plan-housing-001-v2",
  "corrects_plan_id": "plan-housing-001-v1",
  "correction_reason": "missing dignity branch for owner_consent",
  "plan_tree": { ... }
}
```

After a correction:
- `plan-housing-001-v1` is **corrected** (superseded)
- `plan-housing-001-v2` is **active**
- v1 still exists in `plans.jsonl` — it is NOT deleted
- The graph shows a dashed correction edge: v1 -.→|corrected_by| v2

### Amendment (`plan_tree_amended`)

An amendment is a partial update. The source plan remains active.
Used when a note, condition, or subcomponent is clarified without
replacing the plan's core reasoning structure.

```json
{
  "event_type": "plan_tree_amended",
  "plan_id": "plan-housing-001-v1a",
  "amends_plan_id": "plan-housing-001-v1",
  "amendment_reason": "added note to coordination phase",
  "plan_tree": { ... }
}
```

The amendment is a new plan record. The original is marked `amended`
in the snapshot view but is NOT superseded.

---

## Active Plan Semantics

The active plan for a claim is:
> The most recently created plan_tree event that has NOT been superseded
> by a `plan_tree_corrected` event referencing it as `corrects_plan_id`.

Computed by `plan_snapshot.py` via the correction chain:

```
plan-housing-001-v1  →  corrected by v2
plan-housing-001-v2  →  [no correction references this]  →  ACTIVE
```

A claim may have at most one active plan at any time (per the correction chain).
Multiple active plans across correction branches are not possible in this model.

---

## Abandoned Plan Semantics

A plan is considered abandoned when its associated task bundle receives a
`task_bundle_abandoned` event. The plan itself is not deleted. The abandoned
status is visible in the snapshot.

An abandoned plan may be superseded by a new `plan_tree_created` event for the
same claim. The correction chain documents the transition.

---

## Correction Chain

The correction chain is the sequence of plan versions from earliest to latest:

```
plan-v1  (created)
  └─ corrected by plan-v2
       └─ corrected by plan-v3
            └─ active
```

`plan_snapshot.py` computes:
- `active_plan` — the leaf of the chain
- `correction_chain_depth` — number of correction hops
- `plans` — all plan records with status (active / corrected / amended / abandoned)
- `bundles` — all task bundles with their derived_from_plan_id and status

---

## Plan Lineage

Every task bundle carries a `derived_from_plan_id` field. This creates a
traceable lineage:

```
claim-housing-001
  → plan-housing-001-v1   (created)
      corrected by
  → plan-housing-001-v2   (active)
      produces
  → bundle-housing-001-v1  (partially_blocked)
```

If a correction is issued after a task bundle has been created from the old plan,
the bundle is NOT automatically invalidated. It continues to reference the plan
it was derived from. A new task bundle should be created from the corrected plan
if needed.

---

## su-table: `plans.jsonl`

`plans.jsonl` is part of the Dan-Go su-table system.

Properties:
- Append-only — no event is ever deleted or modified
- SHA256 hash chain — each event references the hash of the previous event
- Every event has `event_type`, `claim_id`, `timestamp`, `event_hash`
- Plan events also carry `plan_id` (plan tree events) or `bundle_id` (bundle events)

Validation before append:
- `plan_tree_created`: `plan_id` must be unique; plan tree must pass structural validation
- `plan_tree_corrected`: `corrects_plan_id` must exist in plans.jsonl
- `plan_tree_amended`: `amends_plan_id` must exist in plans.jsonl
- `task_bundle_created`: `derived_from_plan_id` must exist in plans.jsonl

---

## Graph Integration

Plan events appear in the negotiation graph alongside su-table events.

Node styles:
- `plan_tree_created`   → blue node (plan)
- `plan_tree_amended`   → amber node (planAmended)
- `plan_tree_corrected` → pink/red node (planCorrected)
- `task_bundle_created` → green node (bundle)
- `task_bundle_blocked` → red node (bundleBlocked)
- `task_bundle_ready`   → bright green node (bundleReady)
- `task_bundle_abandoned`→ grey node (bundleAbandoned)

Edge types:
- `plan_correction`:   dashed arrow  plan-v1 -.→|corrected_by| plan-v2
- `plan_amendment`:    dashed arrow  plan-v1 -.→|amended_by| plan-v1a
- `bundle_derivation`: solid arrow   plan-v2 →|produces| bundle-v1

Text export includes a `── PLAN HISTORY ──` section.
HTML export includes a `Plan History` panel with status badges.
Mermaid export includes `%%` comment lines for plan metadata.

---

## CLI Reference

```bash
# Append a plan tree event
python runtime/plan_event_append.py examples/plan-event.json
python runtime/plan_event_append.py examples/plan-event.json --dry-run
python runtime/plan_event_append.py examples/plan-event.json --verbose

# Append a task bundle event
python runtime/task_bundle_append.py examples/task-bundle-event.json
python runtime/task_bundle_append.py examples/task-bundle-event.json --verbose

# Create a correction event
python runtime/plan_correction.py examples/plan-event.json \
  --reason "missing dignity branch for owner_consent"

# Create an amendment event
python runtime/plan_correction.py examples/plan-event.json \
  --amend --reason "added clarifying note to coordination phase"

# Correction with new plan tree
python runtime/plan_correction.py examples/plan-event.json \
  --new-plan examples/plan-v2-tree.json \
  --reason "full correction of dignity clearance structure"

# View plan snapshot for a claim
python runtime/plan_snapshot.py --claim-id housing-001
python runtime/plan_snapshot.py --claim-id housing-001 --json
python runtime/plan_snapshot.py --all-claims --verbose

# View plan history in graph export
python runtime/graph_export.py --claim-id housing-001 --format text
python runtime/graph_export.py --claim-id housing-001 --format html \
  --output examples/housing-001.graph.html
```

---

## Absolute Prohibitions

This layer does not:
- Execute tasks
- Delete or modify existing events
- Connect to OGI, GITSEA, blockchain, or any network
- Use API keys, wallets, or tokens
- Process real personal data

Plans are artifacts. Bundles are proposals. Neither executes anything.
The append-only log ensures that all reasoning is preserved and auditable.

---

## Related Specs

- `SUTABLE_APPEND_ONLY_SPEC.md` — core su-table append-only specification
- `PLAN_TO_TASK_SPEC.md` — plan tree → task bundle extraction rules
- `PLAN_TREE_SPEC.md` — plan tree grammar and validation rules
- `MULTI_TASK_DECOMPOSITION.md` — full pipeline architecture
- `REASONING_SURFACE_SPEC.md` — why reasoning ≠ language (ogi/)
