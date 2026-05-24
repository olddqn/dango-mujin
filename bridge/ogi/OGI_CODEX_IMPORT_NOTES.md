# OGI Codex Import Notes — dango-gitsea-bridge

> What we took. What we left. Why.

---

## What Is the OGI Codex?

The OGI Codex describes a framework for post-scarcity agent economies:
how AI agents coordinate, reason, remember, model the world, and govern
themselves in environments where traditional economic scarcity signals
are no longer the primary coordination mechanism.

This document records which concepts from the Codex were imported into
Dan-Go's bridge layer, which were deliberately excluded, and why.

---

## Imported: Reasoning / Language Separation

**From Codex:** Agents must not confuse language production with structured
reasoning. Natural language is output; plan trees are computation.

**Dan-Go import:**
- `REASONING_SURFACE_SPEC.md` — formalizes the separation
- `ogi/runtime/claim_plan_tree.py` — generates plan trees from claims
- Language surface (claim title/statement) is kept separate from
  reasoning surface (plan tree JSON)

**Why:** Dan-Go is already a language-first protocol. Without this separation,
the plan tree would just be a structured restatement of the claim text —
adding JSON syntax but no reasoning value.

---

## Imported: Structured Plan Tree

**From Codex:** Plans are not prose. They are structured, verifiable trees
with explicit branching, terminal conditions, and abstain states.

**Dan-Go import:**
- `PLAN_TREE_SPEC.md` — grammar, node types, validation rules
- Node types: `goal`, `subgoal`, `assertion`, `action`, `branch`, `terminal`, `abstain`
- `ogi/runtime/plan_tree_validator.py` — structural validation

**Why:** Unstructured plans are unverifiable. Dan-Go already has structured
state (su-table events, dignity checks) — the plan tree makes the reasoning
structure equally explicit.

---

## Imported: Self-Verification Before Execution

**From Codex:** Agents should verify their own reasoning before acting.
Verification is not optional; it is a required phase between planning and execution.

**Dan-Go import:**
- Plan tree validation is a required step before negotiation
- Validator checks: node types, branch completeness, action capability,
  terminal/abstain presence, depth limits, node count limits
- The phrase "verification before execution" is formalized in
  `REASONING_SURFACE_SPEC.md`

**Why:** Dan-Go already has dignity_guard as a pre-execution check. The
plan tree validator extends this to the reasoning phase.

---

## Imported: Abstain as a First-Class Output

**From Codex:** "I cannot proceed" is not a failure state. It is a
valid and important output of a reasoning system.

**Dan-Go import:**
- `abstain` node type is a leaf node in the plan tree grammar
- Abstain nodes are required when dignity constraints are unmet
- Abstain is treated as "plan working correctly" not "plan failed"
- The `REASONING_SURFACE_SPEC.md` section "Abstain Is a Required Output"
  codifies this

**Why:** Without explicit abstain semantics, plan trees would either:
(a) silently skip constraint checks, or (b) return errors where the correct
answer is "not now, not yet."

---

## Imported: Failure Mode Taxonomy

**From Codex:** Agents should have a structured understanding of the ways
their plans can fail, beyond generic "error."

**Dan-Go import:**
- `PLAN_TREE_SPEC.md` — Failure Modes section covers:
  - Loop detection
  - Premature terminal
  - Unexecutable action
  - Missing branch
  - Dignity-blind plan
  - Depth overrun
  - Node count overrun
- Each failure mode has a mitigation strategy

**Why:** A taxonomy of failures is the foundation of error recovery.
Without naming failure modes, they cannot be detected or corrected.

---

## Imported: World Model / Memory Separation

**From Codex:** Agents maintain a world model (current + desired state)
separately from their memory (history of what happened). These are not
the same thing.

**Dan-Go import:**
- `WORLD_MODEL_MAPPING.md` — maps Dan-Go claim fields to world model structure
- `MEMORY_SURFACE_MAPPING.md` — maps OGI memory types to Dan-Go su-table tables
- `ogi/runtime/world_model_mapper.py` — generates world model from claim JSON
- World model = observed/desired/gap (claim-scoped, point-in-time)
- Memory = su-table (historical, append-only, hash-chained)

**Why:** Without this separation, claims and their histories blur together.
A claim is a snapshot of intent; the su-table is the record of what happened.

---

## Imported: Validator Network Idea (Partial)

**From Codex:** Agent reasoning should be verifiable by a network of
validators, not just by the agent itself.

**Dan-Go import (partial):**
- The `plan_tree_validator.py` implements a local structural validator
- The existing su-table chain (hash verification) is an implicit validator
  network for events
- Trust decay (`temporal_trust_decay.py`) is a validator for contribution
  credibility over time

**Not imported:** Multi-agent validator consensus, staking, slashing,
validator registration, or any token-based incentive for validation.

**Why:** The multi-agent validator network requires token infrastructure
that is explicitly excluded from Dan-Go's scope. The local validator
captures the structural intent without the economic layer.

---

## NOT Imported: Robotics / VLA / Locomotion / Manipulation

**From Codex:** OGI includes physical world agents — visual-language-action
models, robot locomotion, manipulation planning.

**Not imported:** Any physical actuation, sensor integration, motor control,
trajectory planning, or physical-world modeling.

**Why:** Dan-Go operates entirely in the realm of human-AI coordination for
social, legal, and economic claims. Physical actuation is explicitly out of scope.
Adding robotics would require hardware dependencies and real-world safety
considerations that violate Dan-Go's design constraints.

---

## NOT Imported: Token / Governance Implementation

**From Codex:** OGI agents participate in token-based governance — staking,
voting, reward distribution, slashing for misbehavior.

**Not imported:** Any token contracts, wallet integration, on-chain voting,
token transfers, staking mechanisms, or governance token logic.

**Why:** Dan-Go's absolute prohibition on real financial infrastructure
explicitly excludes tokens, wallets, and blockchain contracts. The concept
of "coordination value" is preserved in trust weights and contribution
credit, but without any monetary implementation.

---

## NOT Imported: Real OGI Node Connection

**From Codex:** Agents connect to the OGI network for coordination,
capability discovery, and task assignment.

**Not imported:** API calls to OGI nodes, discovery protocols, real DID
resolution against OGI registries, or any live OGI network participation.

**Why:** Dan-Go is a local, file-based, append-only protocol. All examples
use mock DIDs and local JSONL files. Real network connections are prohibited
by design.

---

## Summary Table

| OGI Codex Element | Imported? | Notes |
|---|---|---|
| Reasoning / language separation | ✓ Yes | REASONING_SURFACE_SPEC.md |
| Structured plan tree | ✓ Yes | PLAN_TREE_SPEC.md + claim_plan_tree.py |
| Self-verification | ✓ Yes | plan_tree_validator.py |
| Abstain as first-class output | ✓ Yes | abstain node type + spec |
| Failure mode taxonomy | ✓ Yes | PLAN_TREE_SPEC.md |
| World model / memory separation | ✓ Yes | WORLD_MODEL_MAPPING.md + MEMORY_SURFACE_MAPPING.md |
| Validator network (structural) | ✓ Partial | local validator only |
| Robotics / VLA / locomotion | ✗ No | Out of scope |
| Token / governance | ✗ No | Prohibited |
| Real OGI network connection | ✗ No | Prohibited |
| Staking / slashing | ✗ No | Prohibited |
| Physical sensor integration | ✗ No | Out of scope |
