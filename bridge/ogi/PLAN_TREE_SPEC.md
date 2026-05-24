# Plan Tree Specification — dango-gitsea-bridge / OGI

> **Status:** implemented  
> **Validator:** `ogi/runtime/plan_tree_validator.py`  
> **Generator:** `ogi/runtime/claim_plan_tree.py`

---

## Overview

A plan tree is a structured, machine-readable representation of the reasoning
behind a Dan-Go Claim. It is the **reasoning surface** — separate from the
language surface (the claim statement) and the execution surface (contributions).

Plan trees are:
- Derived from a Claim's world model (observed/required/missing states)
- Validated before use in negotiation
- Append-only when superseded (old trees go to the su-table, not the trash)
- Contestable by any participant via the federation layer

---

## Grammar

### Root

Every plan tree is a JSON object with `"node_type": "goal"` at the root.
No other node type may appear at depth 0.

### Node Types

| Type | Children | Required fields | Leaf? |
|------|----------|-----------------|-------|
| `goal` | list | `label` | No |
| `subgoal` | list | `label` | No |
| `assertion` | none (or list) | `label` | Usually yes |
| `action` | none | `label`, `required_capability` | Yes |
| `branch` | `true`, `false` | `label`, `condition`, `true`, `false` | No (has true/false, not children) |
| `terminal` | none | `label` | Yes |
| `abstain` | none | `reason` | Yes |

### Field Definitions

**`node_type`** (string, required on every node)  
One of: `goal`, `subgoal`, `assertion`, `action`, `branch`, `terminal`, `abstain`

**`label`** (string, required on most nodes)  
Human-readable description of the node. Not used for logic.

**`condition`** (string, required on `branch`)  
The condition being evaluated. Used for audit and federation context.

**`required_capability`** (string, required on `action`)  
The capability this action proposes. Does not invoke, schedule, or assign.

**`reason`** (string, required on `abstain`)  
Why the plan cannot proceed at this branch. Must be human-readable.

**`state`** (string, optional on `assertion`)  
The observed state this assertion references.

**`satisfies_condition`** (string, optional on `action`)  
Which missing condition this action would address, if accepted.

**`phase`** (string, optional on `subgoal`)  
Semantic phase label: `observation`, `dignity`, `risk`, `conditions`, `coordination`

---

## Structural Rules

1. **Root must be `goal`**  
   Every plan tree starts with a `goal` node. No exceptions.

2. **Every tree must have at least one `terminal` or `abstain`**  
   A plan with no conclusion is an incomplete plan.

3. **`terminal` and `abstain` are leaves**  
   They must not have children.

4. **`action` nodes are leaves**  
   They propose capability; they do not recurse.

5. **`branch` must have both `true` and `false`**  
   Missing either is a validation error.

6. **`action` must have `required_capability`**  
   An action without a declared capability cannot be evaluated.

7. **Dignity branches precede action nodes**  
   The generator enforces this. Validators should flag violations.

---

## Phase Ordering (Enforced by Generator)

The plan tree generator (`claim_plan_tree.py`) produces phases in this order:

```
Phase 0: observe        — assertion nodes for observed_state
Phase 1: dignity        — branch+abstain for each dignity constraint
Phase 2: risk           — branch+abstain for each risk/safety condition
Phase 3: conditions     — subgoal+action for missing conditions
Phase 4: coordination   — action nodes for all possible contributions
Phase 5: constitution   — assertion or branch for constitution check
Phase 6: decision       — branch → terminal / abstain
```

This ordering is not enforced by the validator (structural check only),
but it is the canonical form. Deviation from this order should be logged
as a warning in strict mode.

---

## Example

```json
{
  "plan_tree_id": "pt-housing-001",
  "claim_id": "housing-001",
  "node_type": "goal",
  "label": "turn a vacant house into a shared creative base",
  "children": [
    {
      "node_type": "subgoal",
      "label": "dignity clearance",
      "phase": "dignity",
      "children": [
        {
          "node_type": "branch",
          "label": "is 'revocable_consent' established?",
          "condition": "revocable_consent",
          "true":  {"node_type": "assertion", "label": "revocable_consent confirmed"},
          "false": {"node_type": "abstain",
                    "reason": "execution blocked until 'revocable_consent' is established"}
        }
      ]
    },
    {
      "node_type": "subgoal",
      "label": "satisfy missing conditions",
      "phase": "conditions",
      "children": [
        {
          "node_type": "subgoal",
          "label": "satisfy condition: legal_ownership_confirmed",
          "children": [
            {
              "node_type": "action",
              "label": "request legal_review",
              "required_capability": "legal_review",
              "satisfies_condition": "legal_ownership_confirmed"
            }
          ]
        }
      ]
    },
    {
      "node_type": "branch",
      "label": "can claim advance to next phase?",
      "condition": "all_required_conditions_met",
      "true":  {"node_type": "terminal", "label": "ready_for_negotiation"},
      "false": {"node_type": "abstain",
                "reason": "required conditions not yet met — return to negotiation"}
    }
  ]
}
```

---

## Failure Modes and Mitigations

### Loop Detection

**What:** A node that recursively references itself or a parent, creating
an infinite traversal.

**Mitigation:** The validator tracks `(depth, node_type, label)` fingerprints.
A repeated fingerprint at the same depth raises a warning (strict) or error
depending on severity.

**Note:** Because trees are acyclic by construction, true loops cannot occur
in well-formed JSON. The check is for inadvertent copy-paste repetition.

---

### Premature Terminal

**What:** A `terminal` node that appears before dignity or risk clearance
phases, allowing the plan to "succeed" without checking constraints.

**Mitigation:**
- The generator enforces phase ordering (dignity before coordination).
- The validator checks that `terminal` has no children.
- A `terminal` appearing as a direct child of `goal` (with no other children)
  in strict mode raises a warning: "plan terminates without any conditions".

---

### Unexecutable Action

**What:** An `action` node with `required_capability` pointing to a capability
that no participant has declared, making the action permanently blocked.

**Mitigation:**
- The validator checks that `required_capability` is present (structural).
- Capability availability checking is NOT the validator's job — it belongs
  to the contribution/federation layer.
- The world model's `state_gap` captures which conditions have no known capability.

---

### Missing Branch

**What:** A `branch` node with only `true` or only `false` — a conditional
with only one outcome, which is not a condition.

**Mitigation:** The validator rejects any `branch` missing `true` or `false`.
This is a hard error.

---

### Dignity-Blind Plan

**What:** A plan tree generated from a claim that has dignity constraints, but
the tree contains no dignity branch nodes — the constraints are silently ignored.

**Mitigation:**
- The generator always emits dignity branches before any action phases.
- The validator tracks `has_dignity_branch` and reports it in output.
- Strict mode: if the claim has dignity constraints and the tree has no
  dignity branch, raise a warning.

---

### Depth Overrun

**What:** A plan tree that exceeds the maximum allowed depth, either through
genuine complexity or through a bug in the generator.

**Default limit:** 12 levels  
**Mitigation:** The validator counts depth and errors at `max_depth + 1`.

---

### Node Count Overrun

**What:** A plan tree with more nodes than the maximum, indicating runaway
generation or an attack.

**Default limit:** 100 nodes  
**Mitigation:** The validator counts nodes and stops recursion at `max_nodes + 1`.

---

## Validation CLI

```bash
# Human-readable output (exit 0 = valid, 1 = invalid)
python ogi/runtime/plan_tree_validator.py ogi/examples/plan-tree.output.json

# JSON report
python ogi/runtime/plan_tree_validator.py ogi/examples/plan-tree.output.json --json

# Strict mode (extra warnings)
python ogi/runtime/plan_tree_validator.py ogi/examples/plan-tree.output.json --strict

# Custom limits
python ogi/runtime/plan_tree_validator.py ogi/examples/plan-tree.output.json \
  --max-depth 8 --max-nodes 50
```

---

## Competing Plans

Multiple agents may propose competing plan trees for the same claim.
A competing plan is a `plan_tree_created` event from a different speaker
that proposes an alternative reasoning structure.

Competing plans do not automatically replace each other. The negotiation
layer (`plan_negotiation_append.py`) tracks:

- `plan_supported` events — structured support signals
- `plan_objected` events — typed objections with reasons
- `plan_contested` events — formal competing proposals

The active plan is selected deterministically by `active_plan_selector.py`
using transparent rules (fewest objections → most supports → shallowest
correction depth → newest timestamp).

No plan wins by authority. A plan wins by surviving negotiation.

A `plan_contested` event may carry an embedded `counterplan` dict.
When appended via `plan_negotiation_append.py`, the counterplan is
automatically created as `plan_tree_created` before the contest event.

```bash
# Append a competing plan
python runtime/plan_negotiation_append.py examples/plan-contest-event.json

# Select the active plan (deterministic, transparent)
python runtime/active_plan_selector.py --claim-id housing-001 --verbose

# View negotiation state
python runtime/plan_negotiation_snapshot.py --claim-id housing-001
```

See `PLAN_NEGOTIATION_SPEC.md` for the full specification.

---

## Append-Only Persistence

Plan trees are reasoning artifacts. Like all su-table events, they are
**never deleted or modified** after they are written. Corrections and
amendments are appended as new events.

### Storage

Plan tree events are stored in `sutable/plans.jsonl`.

| Event type | Meaning |
|---|---|
| `plan_tree_created` | A new plan tree is proposed for a claim |
| `plan_tree_amended` | A subcomponent is amended; original plan remains active |
| `plan_tree_corrected` | Full correction: new plan supersedes old structurally |

### Appending a plan tree event

```bash
# Append a new plan tree event (validates structure before write)
python runtime/plan_event_append.py examples/plan-event.json

# Dry run (validate + print, no write)
python runtime/plan_event_append.py examples/plan-event.json --dry-run

# Skip structural validation (not recommended)
python runtime/plan_event_append.py examples/plan-event.json --no-validate
```

### Correction and amendment

```bash
# Issue a correction (full structural replacement)
python runtime/plan_correction.py examples/plan-event.json \
  --reason "missing dignity branch for owner_consent"

# Issue an amendment (partial update, original remains active)
python runtime/plan_correction.py examples/plan-event.json \
  --amend --reason "added clarifying note to coordination phase"
```

### Snapshot

```bash
# View active plan, correction chain, and bundle status
python runtime/plan_snapshot.py --claim-id housing-001
python runtime/plan_snapshot.py --claim-id housing-001 --json
```

### Correction semantics

After a `plan_tree_corrected` event:
- The original plan still exists in `plans.jsonl` — it is NOT deleted
- The correction is computed by `plan_snapshot.py` via `corrects_plan_id` reference
- The active plan is the last plan in the chain not referenced by any correction
- The graph shows a dashed edge: v1 -.→|corrected_by| v2

See `PLAN_APPEND_ONLY_SPEC.md` for the full append-only persistence specification.

---

## Scoped Prerequisite Extensions (schema_version 1.1)

When a claim has scoped prerequisite knowledge from the federation memory,
the plan tree may carry additional fields:

### Root-level metadata

| Field | Type | Meaning |
|---|---|---|
| `schema_version` | `"1.1"` | Signals scoped prerequisite extensions present |
| `scoped_prerequisites` | `bool` | True if scoped prerequisite logic was applied |
| `applicable_prerequisites` | `list[str]` | Prerequisites requiring active subgoal |
| `bypassed_prerequisites` | `list[str]` | Prerequisites recorded as audit assertions only |

### Extended assertion fields

Assertion nodes may carry additional fields (valid, not errors):

| Field | Type | Meaning |
|---|---|---|
| `prerequisite_condition` | `str` | The tracked prerequisite condition name |
| `scope_status` | `"applicable"` \| `"bypassed"` | Resolution result for this claim |
| `scope_reasoning` | `list[str]` | Chain of reasoning from federation events |
| `bypass_conditions_found` | `list[str]` | Bypass conditions present in the active plan |
| `bypass_path` | `list[str]` | Bypass conditions on a bypass_confirmed assertion |

### Extended branch fields

Branch nodes in scoped prerequisite sections carry:

| Field | Type | Meaning |
|---|---|---|
| `prerequisite_condition` | `str` | The condition being gated |
| `scope_status` | `"applicable"` \| `"bypassed"` | Scope resolution context |

### Scoped node phases

New phase labels used in subgoal nodes:

| Phase | Meaning |
|---|---|
| `scoped_prerequisites` | Contains applicable/bypassed prerequisite resolution |

### Generator

`ogi/runtime/scoped_claim_plan_tree.py` — reads `compute_inheritance()` from
the scoped prerequisite layer and builds the scoped tree.

**Spec:** `SCOPED_PLAN_TREE_INTEGRATION.md`

---

## What This Spec Does Not Cover

- **Cross-plan federation** — see `CLAIM_FEDERATION_SPEC.md`
- **Plan execution** — see the contribution layer
- **Natural language → plan tree** — not specified; LLM territory
- **Plan scoring or ranking** — no scoring, no competition between plans
