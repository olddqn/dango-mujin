# World Model Mapping — Dan-Go ↔ OGI

> **Status:** implemented  
> **Module:** `ogi/runtime/world_model_mapper.py`

---

## What Is a World Model?

In OGI-style agent cognition, a **world model** is a structured representation
of what the agent believes to be true about the world at a given moment:
- What states are observed (current reality)
- What states are desired (target reality)
- What the gap is between them (what must change)
- How certain the agent is about its observations

Dan-Go does not use the term "world model" — but every Dan-Go Claim is
implicitly a world model assertion. The `world_model_mapper.py` module makes
this structure explicit.

---

## The Mapping

### Dan-Go → World Model

| Dan-Go Claim field | World Model field | Meaning |
|---|---|---|
| `observed_state` | `observed_state` | States confirmed to be currently true |
| `required_state` | `desired_state` | States that must become true for the claim to succeed |
| `missing_conditions` | `state_gap` | Delta between observed and desired — what must change |
| `reality_feedback` (su-table) | `reality_feedback` | Post-execution ground truth from su-table |
| `dignity_constraints` | `dignity_surface` | Dignity constraints (always blocking if unmet) |
| `constitution_check` | `uncertainty` (partial) | Whether a dignity violation is flagged |

### State Gap Classification

Each gap entry is classified by blocking status:

```
state_gap: [
  {
    "condition": "agent_negotiation",
    "category":  "coordination",
    "blocking":  false,
    "dignity":   false,
    "risk":      false,
    "notes":     "requires negotiation or contribution to resolve"
  },
  {
    "condition": "owner_consent",
    "category":  "dignity",
    "blocking":  true,
    "dignity":   true,
    "risk":      false,
    "notes":     "DIGNITY-SENSITIVE — must not proceed without resolution"
  }
]
```

**Blocking conditions** (`blocking: true`) are conditions where proceeding
without resolution would violate dignity constraints or safety requirements.
They are not merely important — they are hard gates.

---

## Uncertainty

The world model computes an uncertainty level from the state gap:

| Level | Condition |
|---|---|
| `low` | No missing conditions |
| `medium` | 1–2 missing conditions, none dignity-sensitive |
| `high` | Any dignity constraints, or more than 4 missing conditions |

Uncertainty is not a probability. It is a categorical signal that tells
the reasoning surface how much caution to apply when building the plan tree.

---

## Dignity Surface

The `dignity_surface` field makes dignity constraints explicitly visible
as a separate layer:

```json
"dignity_surface": [
  {
    "constraint": "revocable_consent",
    "in_missing": true,
    "in_observed": false,
    "status": "missing"
  },
  {
    "constraint": "no_identity_exposure",
    "in_missing": false,
    "in_observed": false,
    "status": "declared"
  }
]
```

Status values:
- `missing` — declared as a constraint, also in missing_conditions
- `observed` — declared and also confirmed in observed_state
- `declared` — declared but not yet observable (future condition)

---

## Reality Feedback Integration

When `--include-feedback` is passed, the mapper reads `reality_feedback`
events from `sutable/reality_feedback.jsonl` for the claim's `claim_id`
and includes them in the world model.

This allows the world model to show the **post-execution state** alongside
the **pre-execution gap** — giving a complete picture of whether the plan
closed the gap it identified.

```json
"reality_feedback": [
  {
    "event_type": "reality_feedback",
    "claim_id": "post-scarcity-001",
    "result": "partial_success",
    "notes": "Coordination established. Contribution transparency not yet verified.",
    "timestamp": "2026-05-24T12:00:00Z"
  }
]
```

---

## Example Output

```json
{
  "world_model_id": "wm-post-scarcity-001",
  "claim_id": "post-scarcity-001",
  "observed_state": [
    {"state": "resource_abundance_documented", "category": "general"},
    {"state": "coordination_gap_identified",   "category": "coordination"},
    {"state": "agent_capacity_available",      "category": "general"},
    {"state": "human_ai_cooperation_possible", "category": "general"}
  ],
  "desired_state": [
    {"state": "agent_negotiation",        "category": "coordination", "met": false},
    {"state": "dignity_constraints",      "category": "dignity",      "met": false},
    {"state": "transparent_contribution", "category": "general",      "met": false},
    {"state": "reality_feedback",         "category": "infrastructure","met": false},
    {"state": "shared_memory",            "category": "infrastructure","met": false}
  ],
  "state_gap": [
    {"condition": "agent_negotiation",        "blocking": false, "dignity": false},
    {"condition": "transparent_contribution", "blocking": false, "dignity": false}
  ],
  "reality_feedback": [],
  "uncertainty": {
    "level": "high",
    "reason": "2 missing condition(s); 4 dignity constraint(s)",
    "missing_count": 2,
    "dignity_count": 4
  },
  "dignity_surface": [
    {"constraint": "no_identity_exposure",        "status": "declared"},
    {"constraint": "revocable_consent",           "status": "declared"},
    {"constraint": "fair_participation",          "status": "declared"},
    {"constraint": "automation_requires_consent", "status": "declared"}
  ]
}
```

---

## World Model → Plan Tree

The world model is the **input** to the plan tree generator:

```
Claim JSON
  ↓
world_model_mapper.py     → world model (gap analysis)
  ↓
claim_plan_tree.py        → plan tree (proposed reasoning structure)
  ↓
plan_tree_validator.py    → validation result
  ↓
negotiation (human + agent)
  ↓
contribution (execution surface)
  ↓
reality_feedback → world model updated
```

This pipeline separates:
- **What is** (world model observed state)
- **What must be** (world model desired state / state gap)
- **How to close the gap** (plan tree)
- **Whether the closing happened** (reality feedback → world model update)

---

## CLI

```bash
# Map a claim to a world model
python ogi/runtime/world_model_mapper.py ogi/examples/post-scarcity.claim.json

# Save to file
python ogi/runtime/world_model_mapper.py ogi/examples/post-scarcity.claim.json \
  > ogi/examples/world-model-state.json

# Include reality_feedback from su-table
python ogi/runtime/world_model_mapper.py ogi/examples/post-scarcity.claim.json \
  --include-feedback
```

---

## What This Spec Does Not Cover

- **Dynamic world model updates** — world models are generated from claim
  snapshots; they do not update in real-time
- **Probabilistic state** — all states are binary (observed / not observed)
- **Sensor integration** — no physical world sensing
- **Cross-claim world models** — each world model is claim-scoped; federation
  is handled separately
- **World model persistence** — world models are generated fresh; the su-table
  is the persistent store
