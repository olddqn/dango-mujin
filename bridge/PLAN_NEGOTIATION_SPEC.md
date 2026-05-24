# Multi-Agent Plan Negotiation — Specification

> A plan is not accepted because it is generated.
> A plan is accepted because it survives negotiation.

---

## Why Plans Must Be Contestable

Dan-Go is a negotiation protocol, not an authority.

A plan tree is a proposal for how reasoning should proceed. No single agent
or system has the authority to declare a plan correct simply by generating it.
Any participant may contest a plan. Any participant may propose a better one.

This is not a failure condition. This is the protocol working correctly.

**Disagreement is signal, not noise.**

A plan that is contested forces the negotiation to surface its assumptions,
reveal its gaps, and justify its structure. A plan that cannot survive
contestation should not become active.

---

## Negotiation ≠ Voting

Plan negotiation is not a vote.

Votes aggregate numerical preferences. Negotiation surfaces structured reasons.

The distinction matters:

| Voting | Negotiation |
|---|---|
| Count ballots | Record typed objections |
| Majority decides | Deterministic rules apply |
| Silent preference | Required justification |
| Opaque outcome | Transparent selection log |
| Winner takes all | Minority objections preserved forever |

A plan with 100 support signals and 1 dignity_violation objection does NOT
win. The dignity objection is a blocking signal that cannot be outvoted.

---

## Objection Is Signal

An objection is not an attack. An objection is structured evidence.

Every objection carries:
- `objection_type` — typed categorization (see valid types below)
- `objection_reason` — human-readable explanation
- `speaker` — who raised the objection (accountability)

An objection does not automatically reject a plan. It adds to the record.
The selection algorithm weighs objections deterministically.

A `dignity_violation` objection is the strongest signal — it disqualifies
a plan from active selection regardless of support count.

**Valid objection types:**
- `missing_condition` — a required condition is not covered
- `dignity_violation` — the plan violates a dignity constraint
- `insufficient_risk_coverage` — risk phase is inadequate
- `plan_tree_invalid` — structural validation failure
- `process_violation` — the plan was proposed improperly
- `incomplete_reasoning` — reasoning chain is incomplete
- `other` — catch-all with mandatory reason text

---

## Support Is Evidence

A support signal is structured evidence that a plan is adequate.

Every support carries:
- `plan_id` — which plan is supported
- `speaker` — who is signalling support (accountability)
- `support_reason` — why this plan is adequate

Support signals do not automatically activate a plan. They contribute
to the deterministic selection score.

Multiple support signals from the same speaker count as one.
(Deduplication by `speaker` is enforced in signal aggregation.)

---

## Correction vs. Contest

A **correction** (`plan_tree_corrected`) is an author's own revision:
> "I proposed plan A. I now propose plan B instead. A is superseded."

A **contest** (`plan_contested`) is a competing proposal from another agent:
> "I disagree that plan A should be active. I propose plan B instead."

The key difference:

| | Correction | Contest |
|---|---|---|
| Who initiates | Original author or delegated agent | Any participant |
| Effect on original | Original marked `corrected` | Original marked `contested` |
| Both preserved | Yes — append-only | Yes — append-only |
| Selection impact | Corrected plan excluded from selection | Contested plan remains candidate with lower priority |

A correction is structural. A contest is a claim.

---

## Deterministic Selection

The active plan is selected deterministically. No hidden ranking. No opaque weights.

Selection rules (applied in priority order):

1. **Exclude structural exclusions:**
   Plans with status `rejected`, `superseded`, or `corrected` are not candidates.

2. **Exclude dignity violations:**
   Plans with any `dignity_violation` objection are disqualified.

3. **Fewest objections (ASC):**
   Plans with fewer objections are preferred.

4. **Most supports (DESC):**
   Plans with more support signals are preferred.

5. **Shallowest correction depth (ASC):**
   Plans that are not corrections (depth=0) are preferred over corrections.
   Fresh competing proposals are valued over correction chains.

6. **Newest timestamp (DESC):**
   Most recently proposed plan wins the final tiebreak.

These rules are:
- Documented in this spec
- Printed by `active_plan_selector.py --verbose`
- Stored in the `selection_rules` field of the selection result
- NOT overridable by any agent or system

---

## Active ≠ Final Truth

The active plan is not the final answer to a claim. It is the current best proposal.

An active plan can be:
- **Contested** → a new competing plan proposes an alternative
- **Amended** → a subcomponent is clarified without replacement
- **Corrected** → the author issues a structural revision
- **Rejected** → a formal rejection event is appended

None of these states delete the previous plan. The full history remains in
`plans.jsonl` — immutable, auditable, permanent.

The correction chain documents not just where reasoning arrived,
but how it got there.

---

## Plan Event Types (Negotiation Layer)

All negotiation events are stored in `sutable/plans.jsonl`.

| Event type | Meaning |
|---|---|
| `plan_supported` | A speaker signals support for a plan |
| `plan_objected` | A speaker signals a typed objection |
| `plan_contested` | A competing plan proposes to replace an existing one |
| `plan_rejected` | A plan is formally rejected (with reason) |
| `plan_superseded` | A plan is marked superseded by another |
| `active_plan_selected` | Formal record of deterministic selection result |

### `plan_supported`

```json
{
  "event_type": "plan_supported",
  "claim_id": "housing-001",
  "plan_id": "plan-housing-001-v2",
  "speaker": "did:key:z6Support001",
  "support_reason": "dignity branch coverage complete"
}
```

### `plan_objected`

```json
{
  "event_type": "plan_objected",
  "claim_id": "housing-001",
  "plan_id": "plan-housing-001-v2",
  "speaker": "did:key:z6Object001",
  "objection_type": "insufficient_risk_coverage",
  "objection_reason": "risk review phase covers only one gate; shared spaces require two"
}
```

### `plan_contested`

```json
{
  "event_type": "plan_contested",
  "claim_id": "housing-001",
  "contested_plan_id": "plan-housing-001-v2",
  "counterplan_id": "plan-housing-001-v3",
  "contest_reason": "improved risk phase with space_safety_assessed gate",
  "speaker": "did:key:z6Contester001",
  "counterplan": {
    "plan_id": "plan-housing-001-v3",
    "plan_tree": { "..." : "..." }
  }
}
```

If `counterplan_id` does not yet exist in `plans.jsonl`, the embedded
`counterplan` is automatically appended as `plan_tree_created` before
the `plan_contested` event. This ensures both events are in the log.

### `active_plan_selected`

```json
{
  "event_type": "active_plan_selected",
  "claim_id": "housing-001",
  "selected_plan_id": "plan-housing-001-v3",
  "selection_basis": {
    "support_count": 0,
    "objection_count": 0,
    "correction_depth": 0,
    "dignity_score": "pass",
    "validator_status": "valid"
  }
}
```

---

## Plan Status Values

| Status | Meaning |
|---|---|
| `open` | Proposed, no negotiation signals yet |
| `corrected` | Structurally replaced by `plan_tree_corrected` event |
| `contested` | Has an active `plan_contested` event targeting it |
| `amended` | Has a `plan_tree_amended` event (original still active) |
| `rejected` | Formally rejected by `plan_rejected` event |
| `superseded` | Marked superseded by `plan_superseded` event |
| `active` | Named in the most recent `active_plan_selected` event |

---

## Negotiation Status Values

Overall negotiation status for a claim:

| Status | Condition |
|---|---|
| `empty` | No plan_tree events for this claim |
| `open` | Plans exist, no negotiation signals |
| `signalled` | Support or objection signals, no contest |
| `contested` | At least one `plan_contested` event |
| `active` | Formal `active_plan_selected` event exists |

---

## No Central Authority

There is no authority that:
- Decides which plan is correct
- Overrides the selection algorithm
- Silences an objection
- Prevents a contest

Any participant may submit a competing plan. Any participant may object.
The selection algorithm is public, deterministic, and applies without exception.

The `active_plan_selected` event is a formal record, not a command.
It records what the algorithm concluded at the time it was run.
A new contest can be filed after selection. The process continues.

---

## Graph Representation

Plan negotiation events appear in the negotiation graph.

Contest graph:
```
plan-v2 -.->|contested_by| contest-event → plan-v3
plan-v2 -.->|supported_by| support-event
plan-v2 -.->|objected_by| objection-event
plan-v3 -->|selected_as_active| selection-event
```

Node styles:
- `plan_supported`       → green (planSupported)
- `plan_objected`        → orange (planObjected)
- `plan_contested`       → pink/red (planContested)
- `plan_rejected`        → grey (planRejected)
- `plan_superseded`      → grey (planSuperseded)
- `active_plan_selected` → bright green (planActive)

Text export: `── PLAN NEGOTIATION ──` section after `── PLAN HISTORY ──`
HTML export: `Plan Negotiation` panel with status badges and contest chains
Mermaid export: contest edges with `-.->|contested_by|` notation

---

## CLI Reference

```bash
# Append a support signal
python runtime/plan_negotiation_append.py examples/plan-support-event.json

# Append an objection
python runtime/plan_negotiation_append.py examples/plan-objection-event.json

# Append a contest (auto-creates counterplan if embedded)
python runtime/plan_negotiation_append.py examples/plan-contest-event.json

# Dry run (validate only, no write)
python runtime/plan_negotiation_append.py examples/plan-contest-event.json --dry-run

# Select active plan (deterministic, no write)
python runtime/active_plan_selector.py --claim-id housing-001

# Select and record the result
python runtime/active_plan_selector.py --claim-id housing-001 --append

# Show verbose selection with candidate list
python runtime/active_plan_selector.py --claim-id housing-001 --verbose

# Negotiation snapshot
python runtime/plan_negotiation_snapshot.py --claim-id housing-001
python runtime/plan_negotiation_snapshot.py --claim-id housing-001 --json
python runtime/plan_negotiation_snapshot.py --all-claims --verbose

# Plan negotiation graph (focused graph)
python runtime/plan_negotiation_graph.py --claim-id housing-001
python runtime/plan_negotiation_graph.py --claim-id housing-001 --json

# Full negotiation graph export (includes plan negotiation section)
python runtime/graph_export.py --claim-id housing-001 --format text
python runtime/graph_export.py --claim-id housing-001 --format html \
  --output examples/housing-001.graph.html
```

---

## Absolute Prohibitions

This layer does not:
- Execute tasks
- Make final decisions automatically
- Override selection rules
- Silence objections
- Connect to OGI, GITSEA, blockchain, or any network
- Use API keys, wallets, or tokens
- Process real personal data
- Implement hidden scoring or opaque ranking
- Implement token-based voting
- Designate a central authority

Plans are proposals. Negotiation is a transparent process. Selection is deterministic.
No agent may bypass the contestation record. No agent may delete an objection.

---

## Memory Integration

Negotiation produces evidence. Reflective memory captures that evidence and feeds it
back into the next world model cycle as **prior knowledge**.

```
World Model → Plan Tree → Negotiation → Memory
      ↑                                     |
      └──────────── prior_knowledge ────────┘
```

After negotiation activity, create a memory snapshot:

```bash
python runtime/memory_append.py --claim-id housing-001
```

The snapshot records:
- `learned_conditions` — conditions in counterplans but not in contested plans
- `prior_objections` — typed objection signals per plan
- `active_plan_id` — the currently selected plan

On the next world model cycle, load the enriched world model:

```bash
python runtime/world_model_with_memory.py --claim-id housing-001
```

This injects `learned_conditions` directly into the world model's `state_gap`,
so the next plan tree automatically addresses objected constraints.

**Spec:** `REFLECTIVE_MEMORY_SPEC.md`

---

## Related Specs

- `PLAN_APPEND_ONLY_SPEC.md` — append-only persistence for plans and bundles
- `PLAN_TREE_SPEC.md` — grammar and validation rules for plan trees
- `PLAN_TO_TASK_SPEC.md` — plan tree → task bundle extraction
- `SUTABLE_APPEND_ONLY_SPEC.md` — core su-table append-only specification
- `MULTI_TASK_DECOMPOSITION.md` — full pipeline architecture
- `REFLECTIVE_MEMORY_SPEC.md` — reflective memory loop specification
