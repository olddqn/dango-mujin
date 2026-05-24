# Scoped Prerequisite Specification

> **Status:** Implemented
> **Version:** 1.0
> **Part of:** dango-gitsea-bridge / Scoped Prerequisite Inheritance Layer

---

## Core Principle

**A scoped prerequisite is not weaker coordination.
It is more precise coordination.**

When a prerequisite is weakened, it does not disappear — it becomes
conditional. Its applicability depends on the claim's context.

```
Universal prerequisite  →  applies to all claims
         ↓ weakened
Scoped prerequisite     →  applies where context lacks an equivalent path
```

The prerequisite gains precision: it knows where it applies and where it
doesn't. Claims that don't need it can say why.

---

## Why Weakening Creates Scope

A universal rule says: "everyone must do X."

A scoped rule says: "everyone must satisfy the safety concern behind X —
and here are the recognised ways to satisfy it."

When housing-006 (pre-certified modular kitchen) bypassed `space_safety_assessed`
using `precertified_structure + external_safety_audit_attached + embedded_fire_controls`,
it demonstrated that the safety concern is satisfiable without the specific assessment.

The prerequisite then becomes:
```
space_safety_assessed
  applies_to:  non_precertified_spaces        ← still required here
  bypassed_by: precertified_modular_spaces,   ← not required here
               externally_audited_units,
               embedded_suppression_units
```

housing-007 (modified community workspace) has no precertification and no
external audit. The prerequisite is applicable there. The federation does
not pretend otherwise.

---

## Conditional Applicability

Applicability is resolved per claim, per prerequisite, structurally:

```
resolve_scope(condition, claim_id):
  1. Load scope rules from federation_prerequisite_weakened event
     (new_scope, equivalent_safety_conditions)
  2. Read active plan conditions for the claim
  3. If any equivalent_safety_condition is in the plan → bypassed
  4. Otherwise → applicable
```

This is deterministic. Given the same plan events and federation events,
the same resolution is always produced. No text similarity. No fuzzy logic.

---

## Context-Sensitive Coordination

Traditional prerequisite systems ask: "Is condition X met?"

Dan-Go's scoped system asks: "Is the safety concern behind condition X
addressed, by any recognised path, in this claim's context?"

Two claims can address the same safety concern differently:
- housing-004: `space_safety_assessed` (local assessment)
- housing-006: `precertified_structure + external_safety_audit_attached` (external certification)

Both are acceptable. The federation learns from both. The scope rule
captures this without privileging either path.

---

## Why Context Matters More Than Rigid Rules

A rigid rule that says "all spaces must be locally assessed" would:
- Block pre-certified modular units unnecessarily
- Reduce deployment flexibility
- Create a perverse incentive to avoid certification (to avoid "extra" steps)

A scoped rule that says "spaces without external certification must be locally assessed" would:
- Let certified units proceed without redundant assessment
- Keep the requirement where it matters
- Create a correct incentive: certification is a valid alternative path

The federation can say this without a coordinator deciding it.
Convergence from independent claims produced the pattern.
The scope rule follows from the evidence.

---

## Deterministic Scope Resolution

Scope rules are read directly from the `federation_prerequisite_weakened` event:
- `new_scope`: the label for where the prerequisite still applies
- `equivalent_safety_conditions`: the bypass-signalling conditions

No hardcoded scope tables. No hidden rules. No centralized authority.

The scope tables that DO exist in the code (`BYPASS_CONDITION_LABELS`,
`SCOPE_INDICATOR_LABELS`) are human-readable label mappings only —
they translate condition strings to region names for display.
The actual logic uses only the event data.

```python
# From prerequisite_scope_resolver.py
rule = load_scope_rules()["space_safety_assessed"]
# rule = {
#   "new_scope":          "non_precertified_spaces",
#   "bypass_conditions":  ["embedded_fire_controls",
#                          "external_safety_audit_attached",
#                          "precertified_structure"],
#   "applies_to_label":   "non_precertified_spaces",
#   "bypassed_by_labels": ["embedded_suppression_units",
#                          "externally_audited_units",
#                          "precertified_modular_spaces"],
# }
```

---

## Anti-Authority Rationale

A universal prerequisite that cannot be bypassed is authority disguised as evidence.

Once `space_safety_assessed` was promoted, it could have become a permanent
gate — impossible to bypass without "permission." Dan-Go refuses this.

The weakening/scoping mechanism ensures:
1. A claim with genuine equivalent safety evidence can bypass the prerequisite.
2. The bypass is structural (plan conditions), not negotiated (authority approval).
3. The scope rule is readable by anyone from the event log.
4. The prerequisite remains for claims that don't have the bypass path.

No coordinator decides which claims are exempt. The plan tree decides.

---

## Housing Experiment: Scope in Action

| Claim | Plan includes | Scope resolution |
|---|---|---|
| housing-001 | `space_safety_assessed` (no bypass conds) | applicable |
| housing-002 | `space_safety_assessed` (no bypass conds) | applicable |
| housing-004 | `space_safety_assessed` (no bypass conds) | applicable |
| housing-006 | `precertified_structure`, `external_safety_audit_attached`, `embedded_fire_controls` | bypassed |
| housing-007 | `space_safety_assessed`, `structural_modification_documented`, `local_safety_review` | applicable |

housing-007 is the key contrast to housing-006:
- Old building, local modifications, no external audit, no precertification
- Scope indicators confirm: non-precertified space
- Prerequisite applies correctly

---

## Scope Conflict Detection

A scope conflict occurs when a plan simultaneously asserts:
- A bypass condition (signals: "this space is precertified/exempt")
- A local modification condition (signals: "this space is NOT precertified")

Example conflict:
```
plan includes: precertified_structure + structural_modification_documented
→ conflict: cannot be simultaneously pre-certified and locally modified
```

Conflicts are **advisory only** — the plan is not blocked. They are
recorded as warnings to help plan authors notice logical inconsistencies.

Current data: no scope conflicts detected.

---

## Propagation

When the federation propagates prerequisite hints to a claim:
- Applicable prerequisites are propagated with scope note and bypass path info.
- Bypassed prerequisites are suppressed for that claim.

housing-006 does NOT receive `space_safety_assessed` as a planning hint.
housing-007 DOES receive it, with the scope noted: "applies to non_precertified_spaces."

This ensures the world model prior_knowledge accurately reflects what
the federation knows about each claim's context.

---

## Module Reference

### New modules

#### `runtime/prerequisite_scope_resolver.py` — scope rule loading + resolution (read-only)

```python
load_scope_rules(fmap=None) -> dict[str, dict]
    # Reads weakened events; returns {condition: {new_scope, bypass_conditions, ...}}

resolve_scope(condition, claim_id, fmap=None) -> dict
    # Deterministically resolves: applicable or bypassed
    # Returns: {applicable, bypassed, bypass_conditions_found,
    #           scope_indicators_found, scope_reasoning, ...}

scope_summary(fmap=None) -> list[dict]
    # {condition, applies_to_label, bypassed_by_labels,
    #  applicable_claims, bypassed_claims}
```

#### `runtime/scoped_prerequisite_inheritance.py` — per-claim applicability (read-only)

```python
compute_inheritance(claim_id, fmap=None) -> dict
    # Returns: {claim_id, applicable_prerequisites, bypassed_prerequisites,
    #           unscoped_prerequisites, scope_reasoning, applicability_details}

compute_all_inheritances(fmap=None) -> list[dict]
```

#### `runtime/scope_conflict_detector.py` — contradictory scope detection (read-only)

```python
detect_conflicts(claim_id, fmap=None) -> list[dict]
    # Returns: [{condition, conflict, bypass_condition_found,
    #            local_indicator_found, reason, advisory}]

detect_all_conflicts(fmap=None) -> dict[str, list[dict]]
```

#### `runtime/scoped_condition_propagation.py` — scope-aware propagation (read-only)

```python
get_scoped_propagation_hints(claim_id, fmap=None) -> list[dict]
    # Applicable: propagated with scope note
    # Bypassed: suppressed (applicable=False)

propagate_to_all_claims(fmap=None) -> dict[str, list[dict]]
```

#### `runtime/scoped_world_model.py` — scoped prior_knowledge (read-only)

```python
build_scoped_prior_knowledge(claim_id, fmap=None) -> dict
    # {"claim_id": str, "federation_prerequisites": [...]}
    # Each hint has: applicable, scoped, scope, bypass_path

integrate_scoped_prerequisites(prior_knowledge, claim_id, fmap=None) -> dict

build_all_scoped_prior_knowledge(fmap=None) -> list[dict]
```

#### `runtime/scoped_prerequisite_snapshot.py` — full lifecycle query (read-only)

```python
scoped_snapshot(condition=None, fmap=None) -> dict | list[dict]
    # Full view: scope rules + applicable/bypassed claims + per-claim details + conflicts

applicable_for_claim(claim_id, fmap=None) -> list[str]
bypassed_for_claim(claim_id, fmap=None) -> list[str]
```

### Updated modules

#### `runtime/prerequisite_memory_integration.py`
- `get_prerequisite_planning_hints()` delegates to `scoped_condition_propagation`
- Housing-006 shows bypassed (not propagated); housing-007 shows applicable

#### `runtime/world_model_with_memory.py`
- `build_world_model_with_memory()` calls `integrate_scoped_prerequisites()`

#### `runtime/federation_condition_propagation.py`
- `compute_propagation()` attaches `scoped_prerequisite_hints` per target

#### `runtime/graph_export.py`
- Text: SCOPED PREREQUISITES section with per-claim resolution
- HTML: applicability badge, bypass reasoning, scope tag
- Mermaid: `-->|requires|` and `-.->|bypass|` based on scope resolution

#### `runtime/negotiation_graph.py`
- `scoped_requirement` edge kind
- `scoped_bypass` edge kind
- `scope_conflict` edge kind

---

## CLI Reference

```bash
# Scope resolution
python runtime/prerequisite_scope_resolver.py
python runtime/prerequisite_scope_resolver.py --condition space_safety_assessed --claim-id housing-006
python runtime/prerequisite_scope_resolver.py --condition space_safety_assessed --claim-id housing-007

# Per-claim inheritance
python runtime/scoped_prerequisite_inheritance.py
python runtime/scoped_prerequisite_inheritance.py --claim-id housing-007 --json

# Conflict detection
python runtime/scope_conflict_detector.py
python runtime/scope_conflict_detector.py --claim-id housing-007

# Propagation hints
python runtime/scoped_condition_propagation.py
python runtime/scoped_condition_propagation.py --claim-id housing-006

# Scoped world model
python runtime/scoped_world_model.py --claim-id housing-007 --json

# Full scoped snapshot
python runtime/scoped_prerequisite_snapshot.py
python runtime/scoped_prerequisite_snapshot.py --condition space_safety_assessed --json
python runtime/scoped_prerequisite_snapshot.py --claim-id housing-007

# Graph export with scoped sections
python runtime/graph_export.py --claim-id housing-006 --format text
python runtime/graph_export.py --claim-id housing-007 --format text
python runtime/graph_export.py --claim-id housing-007 --format mermaid
```

---

## New Event Types

None. Scoped prerequisite inheritance reads from existing events:
- `federation_prerequisite_weakened` — carries the scope rule
- `plan_tree_created` — carries the claim's plan conditions

The scope is derived, not declared.

---

## Design Principles

1. **Scope from evidence.** Scope rules come from the weakened event's
   `equivalent_safety_conditions`, not from a scope authority.

2. **Structural resolution.** Applicability is determined by plan
   conditions, not by argument, authority, or vote.

3. **Transparent reasoning.** Every `scope_reasoning` entry maps a
   condition to a scope region with an explicit chain.

4. **Advisory always.** Scoped prerequisites are planning hints.
   A plan can still omit an applicable prerequisite and be submitted.

5. **No scope authority.** No module assigns scope to a claim.
   The plan assigns scope to itself by including or excluding conditions.

6. **Conflict detection, not blocking.** Scope conflicts are warnings.
   The plan is never blocked by a conflict flag.

7. **Append-only.** No scope event modifies the promotion event.
   The full history is always recoverable from `federation.jsonl`.

---

## Related Specs

- [PREREQUISITE_DEPRECATION_SPEC.md](PREREQUISITE_DEPRECATION_SPEC.md) — weakening, survivability, deprecation lifecycle
- [FEDERATION_PREREQUISITE_SPEC.md](FEDERATION_PREREQUISITE_SPEC.md) — promotion, contestation, evidence lifecycle
- [FEDERATION_BRANCHING_SPEC.md](FEDERATION_BRANCHING_SPEC.md) — federation branching and condition propagation
- [REFLECTIVE_MEMORY_SPEC.md](REFLECTIVE_MEMORY_SPEC.md) — reflective memory loop

---

*dango-gitsea-bridge · authority: none · append-only · stdlib only*
