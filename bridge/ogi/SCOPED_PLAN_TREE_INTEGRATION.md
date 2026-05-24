# Scoped Plan Tree Integration

> **Status:** Implemented
> **Version:** 1.1
> **Part of:** dango-gitsea-bridge / OGI reasoning surface

---

## Core Principle

**A reasoning surface must plan differently when prerequisite knowledge is scoped.**

Dan-Go prerequisites are not fixed rules. They are advisory knowledge
derived from federation memory. Their applicability depends on claim context.

A plan tree that ignores scoped prerequisites is a plan tree that cannot
reason about its own context. It would impose identical requirements on
claims that are structurally different — and suppress requirements for
claims that genuinely need them.

The scoped plan tree integration ensures that reasoning is context-sensitive:
- Not heavier for precertified claims.
- Not lighter for non-precertified claims.
- Always deterministic. Always transparent.

---

## Why Scoped Prerequisites Affect Reasoning

### The universal prerequisite problem

A universal prerequisite says: all claims must satisfy X.

A reasoning surface that blindly propagates universal prerequisites
cannot distinguish between:
1. A claim that genuinely needs X (applicable)
2. A claim that has already addressed X's safety concern via a different path (bypassed)

Both would receive the same planning requirement. One of them is wrong.

### The scoped prerequisite solution

A scoped prerequisite says: claims in scope S must satisfy X.
Claims outside scope S — because they have an equivalent safety path — do not.

The reasoning surface reads the scope rule and adapts:

```
resolve_scope(condition, claim_id)
  → applicable: build subgoal + gate branch
  → bypassed:   build audit assertion + bypass validation branch
```

No hard enforcement. No coordinator. The plan tree reflects what the
federation has learned from evidence.

---

## Why Bypass Is Not Deletion

When a prerequisite is bypassed:

> **A bypassed prerequisite is still memory. It is just not an active requirement in this context.**

The bypass is not a deletion of the prerequisite from the plan tree.
The bypass is recorded as an audit assertion:

```json
{
  "node_type": "assertion",
  "label": "space_safety_assessed bypassed by scoped prerequisite resolution",
  "state": "space_safety_assessed_bypassed",
  "prerequisite_condition": "space_safety_assessed",
  "scope_status": "bypassed",
  "bypass_conditions_found": ["embedded_fire_controls", "external_safety_audit_attached", "precertified_structure"]
}
```

This ensures:
1. The bypass is visible in the plan tree — not hidden
2. The audit trail is complete — anyone can verify why the prerequisite does not apply
3. The federation's memory is preserved — the prerequisite still exists, just not here

---

## Why an Applicable Prerequisite Becomes a Branch

When a prerequisite is applicable, it becomes a gate — not a statement.
A statement says "this condition exists." A gate says "plan cannot proceed unless."

The gate is implemented as a branch:

```
branch: "is 'space_safety_assessed' complete?"
  true  → assertion: space_safety_assessed satisfied (plan continues)
  false → abstain: plan cannot advance (protocol working correctly)
```

The `false → abstain` is critical. It means the plan explicitly knows
what will happen if the prerequisite is not satisfied: it stops.
This is not a failure. Abstain is the protocol working correctly.

---

## Why a Bypassed Prerequisite Remains as an Audit Assertion

An audit assertion serves three purposes:

1. **Transparency** — anyone reading the plan tree can see that the prerequisite
   exists and why it does not apply in this context.

2. **Bypass validation** — the bypass branch (`is scoped bypass evidence valid?`)
   provides a gate for the bypass itself. If the bypass conditions are later
   found to be insufficient, the plan can abstain on the bypass branch rather
   than silently proceeding.

3. **Federation continuity** — the prerequisite's history (promoted, weakened,
   survivability score) is not erased. The plan tree records the current state
   of that history for this specific claim.

---

## Why Abstain Remains Important

Abstain is not an error state. It is the correct response when a condition
is not yet met and no capability can satisfy it.

Scoped plan trees have two kinds of abstain:

1. **Prerequisite abstain** — `is 'space_safety_assessed' complete? → false`
   Plan cannot advance until the prerequisite is satisfied. This is a planning
   gate, not a failure.

2. **Bypass abstain** — `is scoped bypass evidence valid? → false`
   The bypass path claimed by the plan cannot be verified. The plan must
   re-examine whether the bypass conditions are genuinely present.

Both abstains are honest statements about the plan's current state.
They do not block the claim permanently — they return it to negotiation.

---

## Why Hard Enforcement Is Forbidden

Hard enforcement would mean: if `space_safety_assessed` is applicable,
the plan is rejected until the condition is satisfied.

Dan-Go refuses this for two reasons:

1. **Advisory only** — prerequisites are planning hints, not mandates. A plan
   can still be submitted without satisfying an applicable prerequisite. The
   prerequisite signals what the plan *should* address, not what it *must*.

2. **Contextual error** — hard enforcement assumes the scope rule is always
   correct. But scope rules are derived from evidence and can be contested.
   A claim that disagrees with its scope classification should be able to
   submit a plan and argue the case through negotiation — not be silently blocked.

The plan tree records the applicable/bypassed resolution. The federation learns.
No coordinator decides. No plan is permanently blocked.

---

## Plan Tree Structure

### housing-006 (bypassed)

```
goal: pre-certified modular emergency kitchen
├── subgoal [dignity]: dignity clearance
│   ├── branch: is 'revocable_consent' established?
│   ├── branch: is 'no_identity_exposure' established?
│   └── branch: is 'participant_consent' established?
├── subgoal [scoped_prerequisites]: scoped prerequisite resolution
│   ├── assertion [bypassed]: space_safety_assessed bypassed by scoped prerequisite resolution
│   └── branch [bypassed]: is scoped bypass evidence valid?
│       ├── true:  assertion: bypass confirmed — not required in this context
│       └── false: abstain: bypass evidence insufficient
├── subgoal [coordination]: coordination conditions
│   ├── branch: is 'precertified_structure' established?
│   ├── branch: is 'external_safety_audit_attached' established?
│   ├── branch: is 'embedded_fire_controls' established?
│   └── ...
└── branch: can claim advance to next phase?
    ├── true:  terminal: ready_for_negotiation
    └── false: abstain
```

### housing-007 (applicable)

```
goal: modified community workspace
├── subgoal [dignity]: dignity clearance
│   ├── branch: is 'revocable_consent' established?
│   └── ...
├── subgoal [scoped_prerequisites]: scoped prerequisite resolution
│   ├── subgoal [applicable]: satisfy prerequisite: space_safety_assessed
│   │   └── action: request safety_review
│   └── branch [applicable]: is 'space_safety_assessed' complete?
│       ├── true:  assertion: space_safety_assessed satisfied
│       └── false: abstain: plan cannot advance — prerequisite not yet satisfied
├── subgoal [coordination]: coordination conditions
│   └── ...
└── branch: can claim advance to next phase?
```

---

## Module Reference

### New modules

#### `ogi/runtime/scoped_claim_plan_tree.py` — scoped plan tree generator

```python
build_scoped_plan_tree(claim_id) -> dict
    # Returns a plan tree with:
    # - applicable prerequisites as subgoal + branch
    # - bypassed prerequisites as audit assertion + bypass branch
    # - coordination conditions as regular branches
    # - dignity clearance first, always
```

#### `ogi/runtime/scoped_plan_comparison.py` — plan tree comparison

```python
compare_trees(tree_a, tree_b) -> dict
    # Returns: {per_prerequisite, differences, structural, key_insight}
    # Shows applicable/bypassed divergences between two scoped plan trees
```

### Updated modules

#### `ogi/runtime/plan_tree_validator.py`

Scoped prerequisite assertion nodes (with `prerequisite_condition` +
`scope_status`) are now tracked in `ValidationResult`:
- `has_scoped_prerequisites: bool`
- `scoped_applicable_assertions: list[str]`
- `scoped_bypassed_assertions: list[str]`

Validation rules unchanged — scoped assertion fields are extensions,
not new node types.

#### `ogi/runtime/claim_plan_tree.py`

If the claim dict contains a `federation_prerequisites` key,
the result includes `scoped_prerequisites` metadata (schema_version 1.1).
Existing behavior when `federation_prerequisites` is absent: unchanged.

---

## CLI Reference

```bash
# Generate scoped plan tree
python ogi/runtime/scoped_claim_plan_tree.py --claim-id housing-006
python ogi/runtime/scoped_claim_plan_tree.py --claim-id housing-007
python ogi/runtime/scoped_claim_plan_tree.py --claim-id housing-007 --json

# Validate scoped plan trees
python ogi/runtime/plan_tree_validator.py ogi/examples/scoped-plan-housing-006.output.json
python ogi/runtime/plan_tree_validator.py ogi/examples/scoped-plan-housing-007.output.json

# Compare two scoped plan trees
python ogi/runtime/scoped_plan_comparison.py \
  ogi/examples/scoped-plan-housing-006.output.json \
  ogi/examples/scoped-plan-housing-007.output.json

# Full pipeline: generate → validate → compare → save
python ogi/runtime/scoped_claim_plan_tree.py --claim-id housing-006 --json \
  > ogi/examples/scoped-plan-housing-006.output.json

python ogi/runtime/scoped_claim_plan_tree.py --claim-id housing-007 --json \
  > ogi/examples/scoped-plan-housing-007.output.json

python ogi/runtime/scoped_plan_comparison.py \
  ogi/examples/scoped-plan-housing-006.output.json \
  ogi/examples/scoped-plan-housing-007.output.json \
  --json > ogi/examples/scoped-plan-comparison.json
```

---

## Design Principles

1. **Context-sensitive reasoning.** The plan tree is not the same for all claims.
   It reflects what the federation knows about this claim's specific context.

2. **Bypass is memory, not deletion.** Bypassed prerequisites are recorded
   as audit assertions. The federation's evidence is preserved.

3. **Applicable becomes a gate.** An applicable prerequisite is encoded as
   a branch with an abstain on false. The plan explicitly knows what happens
   if the condition is not met.

4. **Abstain is the protocol.** Abstain is not failure. It is the plan
   returning to negotiation because the conditions for advance are not met.

5. **No hard enforcement.** Plans are proposals. Scoped prerequisites are
   advisory hints. A plan can be submitted without satisfying an applicable
   prerequisite and argue the case through negotiation.

6. **Deterministic.** Given the same federation events and plan events,
   the same scoped plan tree is always produced.

7. **Backward compatible.** `claim_plan_tree.py` behavior is unchanged when
   no scoped prior_knowledge is present. Schema 1.0 is still valid.

---

## Related Specs

- [SCOPED_PREREQUISITE_SPEC.md](../SCOPED_PREREQUISITE_SPEC.md) — scoped prerequisite inheritance
- [PLAN_TREE_SPEC.md](PLAN_TREE_SPEC.md) — plan tree grammar
- [WORLD_MODEL_MAPPING.md](WORLD_MODEL_MAPPING.md) — world model ↔ OGI mapping
- [FEDERATION_PREREQUISITE_SPEC.md](../FEDERATION_PREREQUISITE_SPEC.md) — prerequisite promotion lifecycle

---

*dango-gitsea-bridge · authority: none · append-only · stdlib only · hard enforcement: forbidden*
