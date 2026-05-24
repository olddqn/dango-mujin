# Architecture Overview — dango-gitsea-bridge

> Protocol literature. Not a startup pitch.

---

## The Fundamental Distinction

Most software systems model *state* and *transitions between states*.

Dan-Go models *claims* and *the conditions needed to make them real*.

A claim is not a task. It is not a ticket. It is a statement of what must become true —
together with an honest account of what is currently missing.

The protocol is designed for claims that cannot be resolved by a single agent.
Claims that require negotiation, contribution, and the passage of time.
Claims where the right answer is not known in advance.

---

## System Layers

```
┌──────────────────────────────────────────────────────────────────┐
│  CLAIM LAYER                                                      │
│  Claim JSON → Dignity Guard → Repo Asset                         │
├──────────────────────────────────────────────────────────────────┤
│  REASONING LAYER (OGI surface)                                   │
│  Claim → World Model → Plan Tree → Task Bundle                   │
├──────────────────────────────────────────────────────────────────┤
│  NEGOTIATION LAYER                                               │
│  Plan Support / Objection / Contest / Correction / Selection     │
├──────────────────────────────────────────────────────────────────┤
│  MEMORY LAYER                                                    │
│  Reflective Memory Snapshot → Prior Knowledge → World Model      │
├──────────────────────────────────────────────────────────────────┤
│  TRUST LAYER                                                     │
│  Contribution Events → Temporal Decay → Trust Weight             │
├──────────────────────────────────────────────────────────────────┤
│  FEDERATION LAYER                                                │
│  Claim Dependencies / Counterclaims / Derived Claims             │
├──────────────────────────────────────────────────────────────────┤
│  IDENTITY LAYER                                                  │
│  DID Signatures → Event Authentication (mock)                    │
├──────────────────────────────────────────────────────────────────┤
│  PERSISTENCE LAYER                                               │
│  Su-table (素テーブル) — append-only JSONL + SHA256 hash chain    │
└──────────────────────────────────────────────────────────────────┘
```

---

## Why Language and Reasoning Are Separated

Dan-Go separates the *claim* (natural language statement of what must become real)
from the *world model* (structured gap analysis) from the *plan tree* (how to close the gap).

**Claim:** "A vacant building can become a shared creative space."  
**World Model:** observed={building exists, community need documented}, gap={legal_ownership, safety_review, participant_consent}  
**Plan Tree:** branch on legal_ownership → if confirmed → branch on safety → if passed → assign coordination tasks

This separation is deliberate:

1. **Natural language is ambiguous.** The plan tree must be structurally verifiable.
2. **World models can be wrong.** Plans built on incorrect world models produce incorrect tasks.
3. **Plans can be contested.** A world model and its plan are separate contestable artifacts.
4. **Memory feeds the model, not the claim.** Prior knowledge improves the gap analysis, not the original statement.

An agent that only reads the claim sees an aspiration.  
An agent that reads the world model sees the gap.  
An agent that reads the plan tree sees a proposal for closing it.  
An agent that reads the memory snapshot sees what the negotiation has learned.

---

## World Models

**Module:** `ogi/runtime/world_model_mapper.py`  
**Input:** Claim JSON  
**Output:** Structured world model dict

A world model maps a claim to:

| Field | Meaning |
|-------|---------|
| `observed_state` | States currently confirmed true |
| `desired_state` | States that must become true |
| `state_gap` | Conditions blocking transition (with category, blocking flag) |
| `dignity_surface` | Dignity constraints from the claim |
| `uncertainty` | Level and reason (high / medium / low) |
| `reality_feedback` | Post-execution observations (if available) |

State categories: `dignity`, `risk`, `resource`, `coordination`, `general`.

The world model does not choose what to do. It describes what is missing.

```bash
python ogi/runtime/world_model_mapper.py examples/refugee-story-consented.claim.json
```

**Enriched world model (with memory):**

```bash
python runtime/world_model_with_memory.py --claim-id housing-001
```

The enriched world model injects `prior_knowledge` from the memory layer
and appends `learned_conditions` to `state_gap` tagged `[learned_from_negotiation]`.

---

## Plan Trees

**Module:** `ogi/runtime/claim_plan_tree.py`  
**Input:** World model  
**Output:** Plan tree JSON

A plan tree is a proposal for closing the world model gap. It is a tree of nodes:

| Node type | Meaning |
|-----------|---------|
| `goal` | Root: the claim's target state |
| `subgoal` | Intermediate target |
| `branch` | Conditional gate (`condition`, `true`, `false` branches) |
| `assertion` | State check |
| `task` | Concrete task (not executed — only described) |
| `abstain` | Explicit non-participation (dignity-aware) |

**Abstain nodes** are first-class. Any branch that cannot proceed without violating
dignity can explicitly abstain. Abstaining is not failure.

### Why Plans Are Contestable

A plan is a proposal, not a command. Any participant may:
- **Support** it (structured evidence, not a vote)
- **Object** to it (typed signal: missing_condition, dignity_violation, etc.)
- **Contest** it with a competing counterplan
- **Correct** it (author only; structurally replaces the plan)

Plans that receive `dignity_violation` objections are automatically excluded from
active selection — regardless of how many supports they have.

Contestation is how the protocol learns. Objections surface conditions that the
original plan missed. The counterplan encodes what should have been there.

```bash
python runtime/plan_snapshot.py --claim-id housing-001
python runtime/plan_negotiation_snapshot.py --claim-id housing-001
```

---

## Task Bundles

**Module:** `ogi/runtime/plan_tree_to_tasks.py`  
**Input:** Plan tree  
**Output:** Task bundle JSON

Task bundles are extracted from plan trees. They are not generated independently —
they are derived from the plan's structure.

A task bundle contains:
- `tasks` — list of task specs with type, label, assigned agent class, dependencies
- `bundle_id` — linked to its source plan
- `dignity_flags` — inherited from the plan tree
- `dependency_graph` — which tasks block which

Task bundles are **descriptions**, not execution orders. Nothing runs them automatically.

```bash
python runtime/task_bundle_append.py examples/task-bundle-event.json
```

---

## Negotiation Graphs

**Module:** `runtime/negotiation_graph.py`, `runtime/graph_export.py`

All su-table events are renderable as a negotiation graph:

```bash
# Text (terminal)
python runtime/graph_export.py --claim-id housing-001 --format text

# Mermaid (GitHub / mermaid.live)
python runtime/graph_export.py --claim-id housing-001 --format mermaid

# HTML (local, no external deps)
python runtime/graph_export.py --claim-id housing-001 --format html \
  --output examples/housing-001.graph.html
```

The graph includes:
- All su-table events (claims, negotiations, contributions, executions, feedback)
- Plan history section (correction chain, contest graph)
- Plan negotiation section (support/objection signals, active plan)
- Claim federation section (dependency / counterclaim / derived relationships)

Node shapes encode event types. Edge kinds encode relationships (correction, contest,
support, objection, active selection, federation link).

---

## Multi-Agent Plan Negotiation

**Modules:** `runtime/plan_negotiation_append.py`, `runtime/active_plan_selector.py`,
`runtime/plan_contest_resolver.py`, `runtime/plan_negotiation_snapshot.py`

### How Negotiation Works

Multiple agents may propose competing plans. Any agent may object. Any agent may contest.

**Negotiation events (all stored in plans.jsonl):**

| Event | Description |
|-------|-------------|
| `plan_supported` | Structured support signal with reason |
| `plan_objected` | Typed objection (7 types) |
| `plan_contested` | Competing plan; can embed counterplan for auto-creation |
| `plan_rejected` | Formal rejection |
| `plan_superseded` | Author deprecates own plan |
| `active_plan_selected` | Deterministic selection result recorded |

**Objection types:**
`missing_condition`, `dignity_violation`, `insufficient_risk_coverage`,
`plan_tree_invalid`, `process_violation`, `incomplete_reasoning`, `other`

### Selection Rules (deterministic, transparent, no hidden scoring)

1. Exclude plans with status `rejected`, `superseded`, or `corrected`
2. Exclude plans with any `dignity_violation` objection
3. Fewest objections wins
4. Most supports wins (tiebreaker)
5. Shallowest correction depth wins (tiebreaker)
6. Newest timestamp wins (final tiebreaker)

These rules are stated in the event log. Anyone can verify the selection.

### Correction vs. Contest

| | Correction | Contest |
|---|---|---|
| Initiated by | Original author | Any participant |
| Original plan | Marked `corrected` (excluded from selection) | Marked `contested` (still a candidate) |
| Both preserved? | Yes | Yes |

```bash
python runtime/active_plan_selector.py --claim-id housing-001
python runtime/active_plan_selector.py --claim-id housing-001 --append
```

---

## Reflective Memory

**Modules:** `runtime/reflective_memory.py`, `runtime/memory_append.py`,
`runtime/memory_snapshot.py`, `runtime/world_model_with_memory.py`

### The Loop

```
World Model → Plan Tree → Negotiation → Memory
      ↑                                     |
      └──────────── prior_knowledge ────────┘
```

Without memory, each plan tree cycle starts from zero.  
With memory, the next cycle knows what was objected, what was learned, what is active.

### Learned Conditions Algorithm

Learned conditions are discovered by **structural plan tree diff** — not text-mining.

For each contest pair:
```
learned = extract_conditions(counterplan_tree) − extract_conditions(contested_plan_tree)
```

A condition is the value of the `"condition"` field on any `branch` node.
The algorithm walks the full tree recursively.

This is deterministic. Given the same plans.jsonl, the same learned conditions
are always computed.

### Prior Knowledge Block

```json
{
  "memory_id": "mem-housing-001-002",
  "active_plan_id": "plan-housing-001-v3",
  "negotiation_status": "contested",
  "learned_conditions": ["space_safety_assessed"],
  "known_objection_types": ["insufficient_risk_coverage"],
  "correction_depth": 1,
  "contest_count": 1,
  "summary": "1 correction(s); 1 contest(s); 1 objection(s)..."
}
```

```bash
python runtime/memory_append.py --claim-id housing-001
python runtime/memory_snapshot.py --claim-id housing-001 --diff
python runtime/world_model_with_memory.py --claim-id housing-001
```

---

## Trust Decay

**Modules:** `runtime/temporal_trust_decay.py`, `runtime/contribution_weight.py`,
`runtime/trust_snapshot.py`

Trust is a coordination signal, not a score.

The formula:

```
weight = base_weight
       × (0.5 ^ (days_since / half_life_days))  ← decay
       × verification_multiplier                 ← independent review bonus
       × dignity_multiplier                      ← dignity-alignment bonus
       × continuity_multiplier                   ← recent activity bonus
```

Default half-life: 90 days.

Hard rules:
- `dignity_violation` → trust set to exactly zero. No floor.
- Memory is permanent. Trust is revocable.
- No contributor becomes permanently privileged through history alone.

```bash
python runtime/trust_snapshot.py --claim-id housing-001
python runtime/contribution_weight.py examples/trust-decay-input.json
```

---

## Claim Federation

**Modules:** `runtime/claim_dependency.py`, `runtime/claim_federation.py`,
`runtime/federation_graph.py`, `runtime/federation_snapshot.py`

Claims are not isolated. The federation layer records relationships:

| Relationship | Meaning |
|-------------|---------|
| `depends_on` | This claim cannot proceed until the target claim is resolved |
| `enables` | Resolving this claim makes the target possible |
| `counterclaim` | Public disagreement with a stated reason |
| `derived_from` | This claim is a refinement or extension |
| `dignity_override` | Strong governance: source claim's constraints override target |

**Design principle:** Counterclaims do not invalidate. They make disagreement visible.
A claim with five counterclaims is more *contested*, not more *invalid*.

```bash
python runtime/federation_snapshot.py --claim-id housing-001
python runtime/graph_export.py --claim-id housing-001 --format text
```

---

## Dignity Guard

**Module:** `runtime/dignity_guard.py`

The dignity guard is the first layer. No transformation proceeds without it.

```
Input: Claim JSON
  └─ Has consent_unknown? → BLOCK
  └─ identity_exposure risk? → BLOCK
  └─ emergency_need? → BLOCK (escalate to direct support)
  └─ exploitation_risk? → ESCALATE
  └─ revocable_consent missing? → BLOCK
  └─ revenue_share missing + funding present? → BLOCK
  └─ all clear → PASS
```

In plan negotiation: a `dignity_violation` objection automatically disqualifies
the plan — regardless of support count.

The dignity guard cannot be bypassed by any other module.

---

## DID Signatures

**Modules:** `runtime/did_signature.py`, `runtime/sign_event.py`,
`runtime/verify_event_signature.py`

**Status: mock only.** These modules implement the signature format and
verification logic against test vectors. They do not use real cryptography.

The format is compatible with DID-key signatures. When a real DID infrastructure
is available, replacing the mock with real Ed25519 / did:key signatures
requires only updating `did_signature.py`.

```bash
python runtime/sign_event.py examples/sutable_events/claim_event.json \
  --did did:key:z6MkproposerHousing
python runtime/verify_event_signature.py examples/signed-claim-event.json
```

---

## Su-table (Append-Only Logs)

**Module:** `runtime/sutable_log.py`

The su-table (素テーブル, "plain table") is the persistence layer.

Design guarantees:
- **Append-only** — `fcntl.flock` exclusive lock on write; never overwrites
- **Hash chain** — each event carries `event_hash` (SHA256) and `previous_event_hash`
- **Stable serialization** — events are hashed with sorted keys, no whitespace
- **stdlib only** — `json`, `hashlib`, `fcntl`, `datetime`

Tables:
```
claims, negotiations, contributions, executions,
reality_feedback, federation, plans, memory
```

```bash
# Verify chain integrity
python runtime/sutable_query.py --verify

# Count events per table
python runtime/sutable_query.py --count
```

---

## Data Flow: Full Claim Lifecycle

```
[human or agent] writes claim JSON
         │
         ▼
sutable_append.py ──────────────────────→ claims.jsonl
         │
         ▼
dignity_guard.py ──────── BLOCK? ────────→ stop
         │ PASS
         ▼
world_model_mapper.py ──────────────────→ world model dict
         │
         ▼
claim_plan_tree.py ──────────────────────→ plan tree JSON
         │
plan_event_append.py ───────────────────→ plans.jsonl
         │
         ▼
plan_negotiation_append.py (×N) ─────────→ plans.jsonl
  [support | objection | contest | reject]
         │
         ▼
active_plan_selector.py ─────────────────→ selected_plan_id
         │
plan_tree_to_tasks.py ───────────────────→ task bundle JSON
task_bundle_append.py ───────────────────→ plans.jsonl
         │
         ▼
[external: tasks executed, if at all]
         │
         ▼
reality_feedback_append.py ──────────────→ reality_feedback.jsonl
         │
         ▼
memory_append.py ────────────────────────→ memory.jsonl
         │
         ▼
world_model_with_memory.py ──────────────→ enriched world model
         │
         └────────────────────────────────→ next cycle
```

---

## What This System Does Not Do

- Execute tasks (no runner, no shell, no subprocess)
- Move money (no wallet, no key, no transaction)
- Connect to GITSEA (it is a design target, not an integration)
- Guarantee consensus (disagreement is preserved, not resolved)
- Make final decisions (active plan selection is a proposal, not an order)
- Delete events (corrections and withdrawals are new events)
- Operate with hidden state (all decisions are traceable to logged events)

---

## Related Documents

| Document | What it covers |
|----------|---------------|
| `WHY_DANGO_EXISTS.md` | The argument for this protocol |
| `DANGO_GITSEA_OGI_MAP.md` | Cross-system mapping |
| `EXAMPLES_INDEX.md` | Guide to all example files |
| `VISUAL_SYSTEM_MAP.mmd` | Mermaid architecture diagram |
| `PLAN_NEGOTIATION_SPEC.md` | Negotiation layer in full detail |
| `REFLECTIVE_MEMORY_SPEC.md` | Memory loop in full detail |
| `DIGNITY_GUARD.md` | Dignity guard rules |
| `CLAIM_FEDERATION_SPEC.md` | Federation layer |
| `TEMPORAL_TRUST_DECAY_SPEC.md` | Trust decay formula |
