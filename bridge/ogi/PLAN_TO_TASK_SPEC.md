# Plan Tree → Task Bundle — Specification

> A plan that correctly abstains is more valuable than one that proceeds without checking constraints.

---

## What This Layer Does

The Plan Tree → Task Bundle layer sits between the reasoning surface and the execution surface.

```
Language surface   →  claim statement        (natural language)
Reasoning surface  →  plan tree              (claim_plan_tree.py)
Task bundle        →  THIS LAYER             (plan_tree_to_tasks.py)
Execution surface  →  contribution events    (sutable/contributions.jsonl)
```

A plan tree proposes HOW to reason about a claim.
A task bundle proposes WHAT to negotiate.

Neither executes anything.
Neither moves money.
Neither touches real systems.

---

## Core Rule: Plan Nodes Are Not Tasks

A plan tree `action` node declares a required capability.
It does NOT schedule, invoke, or execute anything.

A task bundle `task` declares a negotiable candidate for contribution.
It does NOT execute the contribution.

The task bundle is a structured proposal:
> "These are the things that need to happen, in this order, subject to these gates."

Human and agent negotiation decide which tasks to accept and in what form.

---

## Extraction Rules

### action → task

Every `action` node in the plan tree becomes a task candidate.

```json
// Plan tree action node
{
  "node_type": "action",
  "label": "propose contribution: coordination",
  "required_capability": "coordination",
  "satisfies_condition": "agent_negotiation"
}

// Extracted task
{
  "task_id": "task-coordination-001",
  "task_type": "coordination",
  "required_capability": "coordination",
  "group": "satisfy missing conditions",
  "phase": "conditions",
  "execution_allowed": false,
  "priority": 1,
  "satisfies_condition": "agent_negotiation",
  "blocked_by": ["task-gate-no-identity-exposure", "task-gate-revocable-consent", ...],
  "blocked_reason": "upstream_gate_not_resolved"
}
```

### branch (dignity) → condition_gate task

A dignity branch (`true` child = `assertion`) generates a **synthetic** `condition_gate` task.

Dignity gates are always `execution_allowed=true` — they are independent prerequisites
that can be established in parallel without blocking each other.

```json
// Plan tree dignity branch
{
  "node_type": "branch",
  "condition": "revocable_consent",
  "true": { "node_type": "assertion", "label": "revocable_consent confirmed" },
  "false": { "node_type": "abstain", "reason": "..." }
}

// Extracted gate task
{
  "task_id": "task-gate-revocable-consent",
  "task_type": "condition_gate",
  "condition": "revocable_consent",
  "phase": "dignity",
  "execution_allowed": true,
  "priority": 0,
  "note": "Dignity gate: 'revocable_consent' must be established before downstream tasks proceed."
}
```

### branch (risk) → real task that is also a gate

A risk branch (`true` child = `action`) generates a real task that also functions as a gate.

Risk gate tasks are blocked by all dignity gates but NOT by sibling risk gates.

```json
// Plan tree risk branch
{
  "node_type": "branch",
  "condition": "legal_ownership_confirmed",
  "true": {
    "node_type": "action",
    "required_capability": "legal_review",
    "satisfies_condition": "legal_ownership_confirmed"
  },
  "false": { "node_type": "abstain", "reason": "..." }
}

// Extracted risk gate task
{
  "task_id": "task-gate-legal-ownership-confirmed",
  "task_type": "legal_review",
  "required_capability": "legal_review",
  "condition": "legal_ownership_confirmed",
  "satisfies_condition": "legal_ownership_confirmed",
  "phase": "risk",
  "execution_allowed": false,
  "priority": 0,
  "blocked_by": ["task-gate-revocable-consent", "task-gate-no-identity-exposure", ...],
  "blocked_reason": "dignity_gate_not_resolved"
}
```

### branch (decision) → bundle_status update + blocked_record

The final decision branch (`true` child = `terminal`, condition = `all_required_conditions_met`)
updates the bundle's `terminal_decision` field and generates a `bundle_blocked` record
from the `false=abstain` path.

This branch does NOT generate a task.

### subgoal → task_group label only

A `subgoal` node provides the `group` and `phase` labels for the tasks extracted from
its children. It does not itself become a task.

### assertion → no task

An `assertion` node records an already-true world state fact. It generates no task.

### abstain → blocked_record

An `abstain` node (from a branch's false path, or standalone) generates a
`blocked_record` in the `blocked_records` list. It does not generate a task.

### terminal → bundle_status

A `terminal` node updates the `terminal_decision` field in the bundle.

---

## Dependency Gate Rules

### Dignity gates (condition_gate tasks)

- Generated from dignity phase branches
- Always `execution_allowed=true`
- Never in `blocked_by` of another dignity gate
- All downstream tasks carry `blocked_by` referencing all dignity gate IDs

### Risk gate tasks

- Generated from risk phase branches (real action tasks that gate others)
- `execution_allowed=false` when dignity gates exist
- `blocked_by=[dignity_gate_ids]` — blocked by dignity gates only
- All subsequent (conditions + coordination) tasks carry `blocked_by` referencing
  all dignity AND risk gate IDs

### Regular tasks

- Generated from conditions and coordination phase action nodes
- `execution_allowed=false` when any gates exist
- `blocked_by=[all_dignity_gate_ids + all_risk_gate_ids]`

---

## Priority Scheme

Priority 0 tasks must be resolved before priority 1 tasks can proceed meaningfully.
Lower number = higher urgency.

| Priority | Task types |
|----------|-----------|
| 0 | `condition_gate`, `legal_review`, `safety_review`, `consent_facilitation`, `risk_review`, `verification` |
| 1 | `coordination`, `negotiation` |
| 2 | `compute`, `code`, `translation`, `local_knowledge`, `care`, `distribution`, `funding` |
| 3 | `feedback`, `reality_feedback` |

Phase override: tasks in `dignity` or `risk` phases always receive priority 0,
regardless of capability type.

---

## Bundle Status Values

| Status | Meaning |
|--------|---------|
| `fully_blocked` | All tasks have `execution_allowed=false` |
| `partially_blocked` | Some tasks blocked, some executable |
| `ready` | No tasks blocked |
| `negotiate` | Terminal decision from plan tree (all conditions not yet met) |
| `execute` | Terminal decision — plan fully approved |
| `escalate` | Terminal decision — requires human review |
| `empty` | No tasks extracted (unusual, may indicate a claim with no contributions) |

`bundle_status` reflects the **current blocking state**.
`terminal_decision` reflects what the plan tree decided should happen next
(e.g., "negotiate" means return to negotiation, "execute" means proceed to contribution).

---

## Task Bundle Structure

```json
{
  "bundle_id":         "bundle-{claim_id}",
  "plan_tree_id":      "pt-{claim_id}",
  "claim_id":          "{claim_id}",
  "generated_from":    "plan_tree_to_tasks.py",
  "schema_version":    "1.0",
  "bundle_status":     "partially_blocked",
  "terminal_decision": "negotiate",
  "summary": {
    "task_count":         15,
    "executable_count":   6,
    "blocked_count":      9,
    "gate_count":         6,
    "dignity_gate_count": 6,
    "risk_gate_count":    2
  },
  "dignity_gates": ["task-gate-revocable-consent", ...],
  "risk_gates":    ["task-gate-legal-ownership-confirmed", ...],
  "tasks":         [...],
  "blocked_records": [...]
}
```

---

## Task Structure

```json
{
  "task_id":             "task-coordination-001",
  "task_type":           "coordination",
  "required_capability": "coordination",
  "group":               "satisfy condition: agent_negotiation",
  "phase":               "conditions",
  "execution_allowed":   false,
  "priority":            1,
  "satisfies_condition": "agent_negotiation",
  "label":               "request coordination",
  "blocked_by":          ["task-gate-revocable-consent", ...],
  "blocked_reason":      "upstream_gate_not_resolved"
}
```

Required fields: `task_id`, `task_type`, `execution_allowed`, `priority`
Optional fields: `required_capability`, `condition`, `satisfies_condition`, `group`, `phase`,
                 `label`, `blocked_by`, `blocked_reason`, `note`

---

## Blocked Record Structure

```json
{
  "record_type":       "abstain",
  "execution_allowed": false,
  "reason":            "execution blocked until 'revocable_consent' is established.",
  "phase":             "dignity",
  "condition":         "revocable_consent"
}
```

`record_type` values:
- `abstain` — from a branch's `false=abstain` path
- `bundle_blocked` — from the final decision branch's `false=abstain` path

---

## What abstain means

An `abstain` outcome is not a failure. It is the protocol working correctly.

A `blocked_record` from an `abstain` node records:
> "This path is currently inaccessible. The reason is known. The gate is clear."

The presence of `blocked_records` does not invalidate a bundle.
The presence of tasks with `execution_allowed=false` does not make a bundle unusable.

A bundle with all dignity gates `execution_allowed=true` and everything else blocked
is a **correctly structured bundle** — it tells participants exactly what needs to
happen first (establish consent) and what comes next (risk clearance, then coordination).

---

## Validation Rules

`task_bundle_validator.py` enforces:

1. Required bundle fields present: `bundle_id`, `plan_tree_id`, `tasks`
2. Required task fields present: `task_id`, `task_type`, `execution_allowed`, `priority`
3. Unique `task_id` values
4. All `blocked_by` references point to existing task_ids
5. `condition_gate` tasks have `execution_allowed=true`
6. `condition_gate` tasks have `priority=0`
7. No circular dependencies
8. `dignity_gates` metadata consistent with tasks
9. Blocked tasks (`execution_allowed=false`) carry a `blocked_by` list

---

## Dependency Resolution

`task_dependency_resolver.py` provides:
- Dependency graph: `task_id → set of prerequisite task_ids`
- Cycle detection (DFS-based)
- Topological execution order (Kahn's algorithm, deterministic)
- Immediately executable task list (no prerequisites)

For the housing plan tree, immediately executable tasks are all 6 dignity gates.
After all dignity gates resolve, the 2 risk gates become executable.
After risk gates resolve, all 7 coordination/conditions tasks become executable.

---

## CLI

```bash
# Extract task bundle from plan tree
python ogi/runtime/plan_tree_to_tasks.py ogi/examples/plan-to-task.input.json

# JSON output (piped or explicit)
python ogi/runtime/plan_tree_to_tasks.py ogi/examples/plan-to-task.input.json --json
python ogi/runtime/plan_tree_to_tasks.py ogi/examples/plan-to-task.input.json > bundle.json

# Summary with blocked records
python ogi/runtime/plan_tree_to_tasks.py ogi/examples/plan-to-task.input.json --show-blocked

# Resolve dependencies from a bundle
python ogi/runtime/task_dependency_resolver.py ogi/examples/plan-to-task.output.json

# Execution order only
python ogi/runtime/task_dependency_resolver.py ogi/examples/plan-to-task.output.json --order

# Check validity (exit 0/1)
python ogi/runtime/task_dependency_resolver.py ogi/examples/plan-to-task.output.json --check

# Validate bundle structure
python ogi/runtime/task_bundle_validator.py ogi/examples/plan-to-task.output.json

# Strict validation (warnings become errors)
python ogi/runtime/task_bundle_validator.py ogi/examples/plan-to-task.output.json --strict

# Full pipeline: claim → plan tree → task bundle
python ogi/runtime/claim_plan_tree.py ogi/examples/plan-tree.claim.json > /tmp/tree.json
python ogi/runtime/plan_tree_validator.py /tmp/tree.json
python ogi/runtime/plan_tree_to_tasks.py /tmp/tree.json > /tmp/bundle.json
python ogi/runtime/task_bundle_validator.py /tmp/bundle.json
python ogi/runtime/task_dependency_resolver.py /tmp/bundle.json
```

---

## Full Pipeline

```
Claim JSON
  ↓  world_model_mapper.py
World Model (observed / desired / gap)
  ↓  claim_plan_tree.py
Plan Tree (structured reasoning, not execution)
  ↓  plan_tree_validator.py
Validated Plan Tree
  ↓  plan_tree_to_tasks.py         ← THIS LAYER
Task Bundle (negotiable candidates)
  ↓  task_bundle_validator.py       ← validates bundle structure
  ↓  task_dependency_resolver.py    ← resolves execution order
Task Bundle ready for negotiation
  ↓  (human / agent negotiation — NOT automated)
Contribution events → sutable/contributions.jsonl
```

---

## Bundle Persistence

Task bundles are append-only artifacts stored in `sutable/plans.jsonl`
alongside the plan tree events they were derived from.

A bundle references its source plan via `derived_from_plan_id`. If the
source plan is corrected, the old bundle is NOT invalidated — it continues
to reference the plan it was derived from. A new bundle should be created
from the corrected plan.

### Bundle event types

| Event type | Meaning |
|---|---|
| `task_bundle_created` | A bundle is derived from a specific plan tree |
| `task_bundle_blocked` | The bundle is fully blocked (all gates unresolved) |
| `task_bundle_ready` | All gates resolved; bundle is ready for negotiation |
| `task_bundle_abandoned` | The bundle was abandoned (new plan issued or claim withdrawn) |

### Appending bundle events

```bash
# Append a task_bundle_created event (validates derived_from_plan_id exists)
python runtime/task_bundle_append.py examples/task-bundle-event.json

# Status update events
python runtime/task_bundle_append.py examples/task-bundle-blocked.json
python runtime/task_bundle_append.py examples/task-bundle-ready.json
```

### Bundle lineage

```
claim-housing-001
  → plan-housing-001-v1   (created)
      corrected by
  → plan-housing-001-v2   (active)
      produces
  → bundle-housing-001-v1  (partially_blocked)
```

### Snapshot

```bash
# View plan history + bundle status for a claim
python runtime/plan_snapshot.py --claim-id housing-001
python runtime/plan_snapshot.py --claim-id housing-001 --json
```

See `PLAN_APPEND_ONLY_SPEC.md` for the full persistence specification.

---

## Absolute Prohibitions

This layer does not:
- Execute tasks
- Schedule or invoke external systems
- Connect to OGI, GITSEA, blockchain, or any network
- Use API keys, wallets, or tokens
- Process real personal data
- Perform credit scoring or identity verification
- Control robots or physical systems

Task bundles are negotiation proposals, not execution instructions.

---

## Related Specs

- `PLAN_TREE_SPEC.md` — grammar and validation rules for plan trees
- `PLAN_APPEND_ONLY_SPEC.md` — append-only persistence for plans and bundles
- `REASONING_SURFACE_SPEC.md` — why reasoning ≠ language
- `WORLD_MODEL_MAPPING.md` — claim → world model transformation
- `MULTI_TASK_DECOMPOSITION.md` — architecture of plan tree → task bundle
- `AGENT_ECONOMY_MAPPING.md` — Dan-Go ↔ OGI concept mapping
