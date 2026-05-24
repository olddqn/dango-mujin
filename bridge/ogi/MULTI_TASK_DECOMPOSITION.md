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
  ↓  plan_tree_to_tasks.py          ← IMPLEMENTED
Task Bundle [task-A, task-B, task-C, ...]
  │
  ↓  task_bundle_validator.py       ← validates structure + references
  ↓  task_dependency_resolver.py    ← topological order + cycle detection
  │
  ↓  (human / agent negotiation — NOT automated)
Contributions (sutable/contributions.jsonl)
  │
  ↓  reality_feedback_mapper.py
Reality Feedback (sutable/reality_feedback.jsonl)
```

---

## From Plan Tree to Task Bundle

The extraction rules differ by node type:

| Plan tree node | Bundle output |
|---|---|
| `action` | Executable task candidate |
| `branch` (dignity: `true=assertion`) | Synthetic `condition_gate` task (priority=0, execution_allowed=true) |
| `branch` (risk: `true=action`) | Real task that is also a dependency gate (priority=0) |
| `subgoal` | Group/phase label only — no task |
| `abstain` | `blocked_record` (no task) |
| `terminal` | Updates `bundle_status` (no task) |
| `assertion` | No task (already true in world state) |

Example: an `action` node in the conditions phase becomes:

```json
{
  "node_type": "action",
  "label": "request coordination",
  "required_capability": "coordination",
  "satisfies_condition": "coordination_established"
}
```

→

```json
{
  "task_id": "task-coordination-001",
  "task_type": "coordination",
  "required_capability": "coordination",
  "group": "satisfy condition: coordination_established",
  "phase": "conditions",
  "execution_allowed": false,
  "priority": 1,
  "satisfies_condition": "coordination_established",
  "blocked_by": ["task-gate-revocable-consent", "task-gate-legal-ownership-confirmed", ...],
  "blocked_reason": "upstream_gate_not_resolved"
}
```

---

## Task Ordering via Plan Tree Phases

The plan tree's phase structure determines task dependency gates:

| Phase | Gate type | Must complete before |
|---|---|---|
| `dignity` | `condition_gate` (synthetic) | ALL other phases |
| `risk` | Real action task as gate | `conditions` + `coordination` phases |
| `conditions` | Regular task (not a gate) | — |
| `coordination` | Regular task (not a gate) | — |
| `decision` | No task — updates `bundle_status` | — |

Dependency gate rules:
- Dignity gates: always `execution_allowed=true` — parallel, independent
- Risk gates: `blocked_by=[dignity_gate_ids]`
- Regular tasks: `blocked_by=[all_dignity_gates + all_risk_gates]`

The dependency graph is fully encoded in each task's `blocked_by` field.
`task_dependency_resolver.py` computes a verifiable topological execution order.

---

## Example Decomposition

**Input claim:** `housing-plan-001` (4 dignity constraints, 5 missing conditions,
6 possible contributions)

**Generated bundle:** 15 tasks, 6 dignity gates immediately executable

| Task ID | Capability | Phase | Executable | Gate? |
|---|---|---|---|---|
| `task-gate-revocable-consent` | `condition_gate` | dignity | ✓ | dignity gate |
| `task-gate-no-identity-exposure` | `condition_gate` | dignity | ✓ | dignity gate |
| `task-gate-fair-participation` | `condition_gate` | dignity | ✓ | dignity gate |
| `task-gate-automation-requires-consent` | `condition_gate` | dignity | ✓ | dignity gate |
| `task-gate-owner-consent` | `condition_gate` | dignity | ✓ | dignity gate |
| `task-gate-participant-consent` | `condition_gate` | dignity | ✓ | dignity gate |
| `task-gate-legal-ownership-confirmed` | `legal_review` | risk | ✗ | risk gate |
| `task-gate-safety-assessment` | `safety_review` | risk | ✗ | risk gate |
| `task-coordination-001` | `coordination` | conditions | ✗ | — |
| `task-legal-review-002` | `legal_review` | coordination | ✗ | — |
| `task-coordination-003` | `coordination` | coordination | ✗ | — |
| `task-local-knowledge-004` | `local_knowledge` | coordination | ✗ | — |
| `task-compute-005` | `compute` | coordination | ✗ | — |
| `task-care-006` | `care` | coordination | ✗ | — |
| `task-translation-007` | `translation` | coordination | ✗ | — |

```bash
# Generate this bundle:
python ogi/runtime/claim_plan_tree.py ogi/examples/plan-tree.claim.json > /tmp/tree.json
python ogi/runtime/plan_tree_to_tasks.py /tmp/tree.json > /tmp/bundle.json
python ogi/runtime/task_dependency_resolver.py /tmp/bundle.json --order
```

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

- **Task assignment** — no automatic agent matching or task routing
- **Task ordering enforcement** — the dependency order is declared in `blocked_by`;
  enforcement is a coordination protocol concern (not automated here)
- **Cross-claim task deduplication** — federation records relationships;
  task merging is not automated
- **Contribution creation** — task bundles are proposals; contributions are
  created by human / agent negotiation, not by this layer

The task bundle layer (`plan_tree_to_tasks.py`) IS implemented and generates
a fully structured, validated, dependency-resolved proposal for negotiation.

---

## See Also

- `PLAN_TO_TASK_SPEC.md` — full extraction rules, schema, and CLI
- `CLAIM_TO_AGENT_TASK.md` — Claim → single Agent Task (simpler path)
- `PLAN_TREE_SPEC.md` — plan tree grammar and validation rules
- `WORLD_MODEL_MAPPING.md` — world model → plan tree input
- `CLAIM_FEDERATION_SPEC.md` — cross-claim dependencies
- `AGENT_ECONOMY_MAPPING.md` — OGI-level mapping table
