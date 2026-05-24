# Multi-Task Decomposition — dango-gitsea-bridge / OGI

> How a single Dan-Go Claim becomes a bundle of actionable agent tasks,
> routed through a plan tree.

---

## The Problem

A Dan-Go Claim is a single statement:
> "A vacant house can become a shared creative base."

But to close the world model gap, multiple capabilities are required:
- Legal review (confirm ownership)
- Safety assessment (confirm structural soundness)
- Coordination (organize participants)
- Local knowledge (understand building history)
- Care (support vulnerable participants)

One claim → multiple tasks. Each task requires a different capability.
Each task has its own dignity constraints inherited from the parent claim.

Without structured decomposition, this becomes:
- A list of vague to-dos
- No verifiable ordering
- No dignity checks per task
- No traceable origin

With plan tree decomposition, it becomes a structured, validated bundle
where every task traces back to a specific node in the plan tree.

---

## Decomposition Pipeline

```
Claim JSON
  │
  ↓  world_model_mapper.py
World Model (observed / desired / state_gap)
  │
  ↓  claim_plan_tree.py
Plan Tree (goal → subgoals → actions → branches → terminals/abstains)
  │
  ↓  plan_tree_validator.py
Validated Plan Tree
  │
  ↓  claim_to_agent_task.py (extended)
Task Bundle [task-A, task-B, task-C, ...]
  │
  ↓  contribution layer
Contributions (sutable/contributions.jsonl)
  │
  ↓  reality_feedback_mapper.py
Reality Feedback (sutable/reality_feedback.jsonl)
```

---

## From Plan Tree to Task Bundle

Each `action` node in the validated plan tree becomes a candidate task:

```json
{
  "node_type": "action",
  "label": "request legal_review",
  "required_capability": "legal_review",
  "satisfies_condition": "legal_ownership_confirmed"
}
```

Becomes:

```json
{
  "task_id": "task-housing-001-legal_review",
  "origin_claim_id": "housing-001",
  "origin_plan_tree_id": "pt-housing-001",
  "origin_node_label": "request legal_review",
  "required_capability": "legal_review",
  "satisfies_condition": "legal_ownership_confirmed",
  "task_status": "open",
  "dignity_required": true,
  "dignity_constraints": ["revocable_consent", "no_identity_exposure"],
  "created_from": "plan_tree_action"
}
```

Key properties inherited from the plan tree:
- `origin_plan_tree_id` — which plan tree this task comes from
- `satisfies_condition` — which missing condition this task addresses
- `dignity_required` — always true if the parent claim has dignity constraints
- `dignity_constraints` — copied from parent claim

---

## Task Ordering via Plan Tree Phases

The plan tree's phase structure implies task ordering:

| Phase | Tasks produced | Must complete before |
|---|---|---|
| `dignity` | Consent verification tasks | All other phases |
| `risk` | Safety / legal review tasks | `coordination` phase |
| `conditions` | Condition-specific tasks | `coordination` phase |
| `coordination` | General contribution tasks | `decision` branch |
| `decision` | None (branch only) | Terminal / abstain |

Tasks from earlier phases must be completed before later-phase tasks begin.
This is not enforced automatically — it is declared in the plan tree
and must be respected by the coordination protocol.

---

## Example Decomposition

**Input claim:** `housing-plan-001` (4 dignity constraints, 5 missing conditions,
6 possible contributions)

**Generated tasks:**

| Task ID | Capability | Phase | Satisfies |
|---|---|---|---|
| `task-housing-001-revocable_consent` | `consent_facilitation` | dignity | `revocable_consent` |
| `task-housing-001-no_identity_exposure` | *(dignity branch only)* | dignity | `no_identity_exposure` |
| `task-housing-001-legal_review-1` | `legal_review` | risk | `legal_ownership_confirmed` |
| `task-housing-001-legal_review-2` | `legal_review` | risk | `owner_consent` |
| `task-housing-001-safety` | `safety_review` | risk | `safety_assessment` |
| `task-housing-001-coord` | `coordination` | conditions | `coordination_established` |
| `task-housing-001-legal_review-coord` | `legal_review` | coordination | — |
| `task-housing-001-local_knowledge` | `local_knowledge` | coordination | — |
| `task-housing-001-compute` | `compute` | coordination | — |
| `task-housing-001-care` | `care` | coordination | — |
| `task-housing-001-translation` | `translation` | coordination | — |

All tasks inherit:
- `dignity_required: true`
- `dignity_constraints: [revocable_consent, no_identity_exposure, fair_participation, automation_requires_consent]`
- `origin_claim_id: housing-plan-001`

---

## Abstain Tasks

When a plan tree branch reaches an `abstain` node, no task is created.
Instead, an `abstain_record` is produced:

```json
{
  "type": "abstain_record",
  "origin_claim_id": "housing-plan-001",
  "condition": "owner_consent",
  "reason": "execution blocked until 'owner_consent' is established",
  "phase": "dignity",
  "timestamp": "2026-05-24T00:00:00Z"
}
```

Abstain records explain why a task was NOT created — preserving the
reasoning even when no action is possible.

---

## Dignity Inheritance

Every task in a bundle inherits the full dignity constraint set from
the parent claim. This means:

1. A task cannot be accepted by a contributor without running dignity_guard.
2. A task cannot be executed without the contributor acknowledging
   the dignity constraints.
3. If a dignity constraint is violated during task execution, the
   entire task is marked as `blocked` and a dignity_violation event
   is appended to the su-table.

There is no mechanism to strip dignity constraints from a decomposed task.
They travel with the task always.

---

## Multi-Claim Task Bundles (Federation)

When claims are federated (via `depends_on`, `enables`, etc.), task bundles
from different claims may share tasks:

- `housing-001` enables `housing-004` (community kitchen)
- Both claims require `coordination` capability
- The task for `housing-001.coordination` and `housing-004.coordination`
  may be the same physical task, performed by the same contributor

The federation layer records this relationship. The task bundle does not
de-duplicate automatically — de-duplication is a coordination protocol concern.

---

## What Is Not Automated

The following are NOT automated by the current implementation:

- **Plan tree → task bundle conversion** — described here but not yet implemented
  as a runtime module. `claim_plan_tree.py` generates the plan tree;
  task bundle extraction is a future step.
- **Task assignment** — no automatic agent matching or task routing
- **Task ordering enforcement** — the phase order is declared; enforcement
  is a coordination protocol concern
- **Cross-claim task deduplication** — federation records relationships;
  task merging is not automated

These are described here to define the intended architecture for future
implementation.

---

## See Also

- `CLAIM_TO_AGENT_TASK.md` — Claim → single Agent Task
- `PLAN_TREE_SPEC.md` — plan tree grammar and validation rules
- `WORLD_MODEL_MAPPING.md` — world model → plan tree input
- `CLAIM_FEDERATION_SPEC.md` — cross-claim dependencies
- `AGENT_ECONOMY_MAPPING.md` — OGI-level mapping table
