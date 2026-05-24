# Claim → OGI Agent Task — Transformation Specification

---

## What Is an Agent Task?

In an OGI-style agent economy, an **agent task** is a structured
request for coordination that any capable agent (human or AI) can
accept, execute, and report on.

It differs from a Dan-Go Claim in scope:
- A **Claim** is a public statement about a desired state transition
- An **Agent Task** is an actionable assignment derived from that claim —
  specific enough for an agent to know if it can contribute

A single Claim may produce multiple Agent Tasks.
An Agent Task always traces back to a Claim.

---

## Transformation Rules

| Claim field | Agent Task field | Rule |
|---|---|---|
| `claim_id` | `origin_claim_id` | direct copy |
| `claim_id` + prefix | `task_id` | `"task-" + claim_id` |
| `statement` | `task_description` | direct copy |
| `possible_contributions` | `required_capabilities` | mapped (see below) |
| `missing_conditions` | `open_conditions` | direct copy |
| `dignity_constraints` | `dignity_required` | true if non-empty |
| `dignity_constraints` | `dignity_constraints` | direct copy |
| `decision` | `task_status` | mapped (see below) |
| `required_state` | `required_conditions` | direct copy |

### Contribution → Capability Mapping

| Claim contribution | Agent capability |
|---|---|
| `coordination` | `negotiation` |
| `translation` | `translation` |
| `compute` | `compute` |
| `legal_review` | `risk_review` |
| `safety_review` | `risk_review` |
| `distribution` | `distribution` |
| `funding` | `monetary_contribution` |
| `story_editing` | `content_review` |
| `verification` | `verification` |
| `local_knowledge` | `local_knowledge` |
| `care` | `care` |
| `code` | `code` |
| (default) | unchanged |

### Decision → Task Status Mapping

| Claim decision | Task status |
|---|---|
| `negotiate` | `open` |
| `execute` | `active` |
| `escalate` | `under_review` |
| `reject` | `closed` |
| (default) | `open` |

### Task Type Inference

`task_type` is inferred from `possible_contributions`:

| Dominant contribution | task_type |
|---|---|
| `coordination` present | `coordination_analysis` |
| `legal_review` or `safety_review` | `risk_assessment` |
| `translation` | `translation_task` |
| `compute` | `compute_task` |
| `distribution` | `distribution_task` |
| `funding` present | `resource_allocation` |
| (default) | `general_coordination` |

---

## Example

### Input: Dan-Go Claim

```json
{
  "claim_id": "post-scarcity-001",
  "title": "Abundance without coordination becomes collapse.",
  "statement": "A community that gains access to abundant resources without a negotiation protocol will default to extraction, not cooperation.",
  "decision": "negotiate",
  "observed_state": ["resource_abundance_documented", "coordination_gap_identified"],
  "required_state": [
    "agent_negotiation",
    "dignity_constraints",
    "transparent_contribution",
    "reality_feedback"
  ],
  "missing_conditions": [
    "agent_negotiation",
    "transparent_contribution"
  ],
  "possible_contributions": [
    "coordination",
    "translation",
    "compute",
    "legal_review",
    "distribution"
  ],
  "dignity_constraints": [
    "no_identity_exposure",
    "revocable_consent",
    "fair_participation"
  ]
}
```

### Output: OGI-style Agent Task

```json
{
  "task_id": "task-post-scarcity-001",
  "origin_claim_id": "post-scarcity-001",
  "task_type": "coordination_analysis",
  "task_description": "A community that gains access to abundant resources without a negotiation protocol will default to extraction, not cooperation.",
  "task_status": "open",
  "required_capabilities": [
    "negotiation",
    "translation",
    "compute",
    "risk_review",
    "distribution"
  ],
  "open_conditions": [
    "agent_negotiation",
    "transparent_contribution"
  ],
  "required_conditions": [
    "agent_negotiation",
    "dignity_constraints",
    "transparent_contribution",
    "reality_feedback"
  ],
  "dignity_required": true,
  "dignity_constraints": [
    "no_identity_exposure",
    "revocable_consent",
    "fair_participation"
  ],
  "post_scarcity_guard_required": true,
  "created_from": "dango_claim"
}
```

---

## Dignity in Agent Tasks

A Dan-Go Claim always carries dignity constraints into the Agent Task.

If `dignity_constraints` is non-empty:
- `dignity_required: true` is set
- `post_scarcity_guard_required: true` is set
- The agent accepting the task must run `post_scarcity_guard` before execution

An agent that accepts a task without checking dignity constraints
is in violation of Dan-Go's constitution:
> "Do not violate the dignity of another."

This applies to AI agents as much as to human agents.

---

## Multi-Task Decomposition

A complex Claim may produce multiple Agent Tasks.

Example: A refugee story support Claim may produce:
1. A `translation_task` for the translation contribution
2. A `risk_assessment` for legal_review and safety_review
3. A `distribution_task` for the distribution contribution
4. A `coordination_analysis` for the overall coordination

Each task:
- Shares the same `origin_claim_id`
- Has its own `task_id` (e.g., `task-refugee-001-translation`)
- Inherits the dignity constraints from the parent Claim
- Reports reality feedback to the same su-table claim

Multi-task decomposition is now structured via the plan tree layer.
See `MULTI_TASK_DECOMPOSITION.md` for the full architecture.

---

## Extended Pipeline: Claim → Plan Tree → Task Bundle

The claim-to-task transformation now has an intermediate reasoning step:

```
Claim JSON
  ↓  world_model_mapper.py
World Model (observed_state / desired_state / state_gap)
  ↓  claim_plan_tree.py
Plan Tree (structured reasoning, not execution)
  ↓  plan_tree_validator.py
Validated Plan Tree
  ↓  (task bundle extraction — see MULTI_TASK_DECOMPOSITION.md)
Task Bundle [task-A, task-B, task-C, ...]
  ↓
Contribution Layer (sutable/contributions.jsonl)
```

The plan tree layer does **not** replace `claim_to_agent_task.py`.
It adds a structured reasoning step **before** task creation:
- The world model identifies the gap
- The plan tree proposes how to close it
- Validation confirms the plan is structurally sound
- Tasks are extracted from `action` nodes only

`action` nodes in the plan tree become tasks.
`abstain` nodes in the plan tree become abstain records (no task).
`branch` nodes gate task creation on condition evaluation.

### CLI — Full Pipeline

```bash
# Step 1: Generate world model
python ogi/runtime/world_model_mapper.py ogi/examples/post-scarcity.claim.json

# Step 2: Generate plan tree
python ogi/runtime/claim_plan_tree.py ogi/examples/post-scarcity.claim.json \
  > ogi/examples/plan-tree.output.json

# Step 3: Validate plan tree
python ogi/runtime/plan_tree_validator.py ogi/examples/plan-tree.output.json

# Step 4: Transform claim to agent task (single task, existing pipeline)
python ogi/runtime/claim_to_agent_task.py ogi/examples/post-scarcity.claim.json
```
