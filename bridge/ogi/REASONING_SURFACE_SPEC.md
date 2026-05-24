# Reasoning Surface Specification — dango-gitsea-bridge / OGI

> **Status:** implemented  
> **Module:** `ogi/runtime/claim_plan_tree.py`, `ogi/runtime/plan_tree_validator.py`  
> **Depends on:** `PLAN_TREE_SPEC.md`, `WORLD_MODEL_MAPPING.md`

---

## Why Separate Reasoning from Language?

Dan-Go is a language-first protocol. Claims are written in natural language.
They are meant to be read, spoken, contested, and remembered by humans.

But natural language is not reasoning. Natural language can be ambiguous,
incomplete, emotionally loaded, and contradictory — all at once. This is a
feature of language, not a defect.

The problem is that when systems treat natural language as reasoning,
they make invisible assumptions:
- "sounds right" replaces "is verifiable"
- Rhetorical force replaces structural validity
- Confidence replaces groundedness

Dan-Go avoids this confusion by making the separation explicit.

---

## The Three Surfaces

| Surface | Form | Examples |
|---|---|---|
| **Language surface** | Natural language | Claim statement, manifesto, title, reason |
| **Reasoning surface** | Structured plan tree | Goal → subgoal → action → branch → abstain |
| **Execution surface** | Contribution / task | Accepted contribution, execution record |

These surfaces are **not convertible into each other**. A plan tree is not
a summary of the language. It is a separate artifact, derived from the
world model gap, that proposes a structure for negotiation.

---

## Language Says What. Reasoning Asks How.

Language surface:
> "This impossible thing should become real."

Reasoning surface:
```
goal: turn impossible thing into real
  subgoal: identify what is currently true
    assertion: A is observed
    assertion: B is not yet observed
  subgoal: dignity clearance
    branch: is consent established?
      true: consent confirmed
      false: abstain — cannot proceed without consent
  subgoal: close the gap
    action: request legal_review
    action: request coordination
  branch: all conditions met?
    true: terminal — ready_for_negotiation
    false: abstain — return to negotiation
```

The claim can be eloquent and the plan tree can be sparse. They coexist
because they serve different functions.

---

## Reasoning Is Not Execution

A plan node does **not** execute anything.

An `action` node with `required_capability: legal_review` means:
> "This plan proposes that a legal review should be requested."

It does not mean:
- A legal review has been requested
- An agent has been assigned
- A contribution has been recorded
- Any su-table event has been written

Execution is handled by the contribution layer (`sutable/contributions.jsonl`).
The plan tree is input to negotiation — not a script for execution.

---

## Reasoning Is Not Authority

A plan tree does not grant permission. It does not override dignity constraints.
It does not have decision-making power.

A plan tree is a **proposed structure for negotiation**. Any participant can:
- Accept the plan as a starting point
- Counterclaim it (via federation)
- Amend it
- Abstain from it

The plan tree is as contestable as any other Dan-Go claim.

---

## Plan Failure Is Not Failure

When a plan tree reaches an `abstain` node, it has not failed. It has
correctly identified that a condition is not met and that proceeding
would violate the protocol.

An `abstain` is a positive outcome. It means the reasoning surface
correctly detected a gate that must not be crossed.

When a plan is superseded by a newer plan, the old plan is not deleted.
It is appended to the su-table as a correction or rejected_plan event.
The su-table remembers everything.

---

## Abstain Is a Required Output

A plan tree that never abstains is a plan tree that does not check constraints.

Every reasoning path that encounters:
- An unmet dignity condition
- A missing safety clearance
- An unresolvable missing condition
- An explicit consent requirement

...must branch into an `abstain` node, not an `action` node.

`abstain` is not a fallback. It is a first-class output of the reasoning surface.

---

## Verification Before Execution

The correct order:

1. **Language surface** — publish claim
2. **World model** — map observed/desired/gap states
3. **Reasoning surface** — generate plan tree
4. **Validation** — validate plan tree (structural + dignity check)
5. **Negotiation** — present plan to participants
6. **Execution surface** — only after negotiation succeeds

Skipping steps 2–4 and jumping from language to execution is the most
common failure mode in agent coordination systems.

Dan-Go's plan tree layer makes it structurally impossible to accidentally
skip the verification step — because validation is a required gate.

---

## What This Spec Does Not Cover

- **Automatic plan approval** — plan trees are proposals, not decisions
- **Multi-agent plan negotiation** — out of scope for this layer
- **Plan versioning** — plans are point-in-time; history is in the su-table
- **Natural language → plan tree translation** — this is LLM territory,
  not specified here; the generator reads structured claim JSON
- **Real OGI integration** — this is a local, file-based compatibility layer
- **Robotics or physical actuation** — explicitly out of scope
