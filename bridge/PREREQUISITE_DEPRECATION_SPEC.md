# Prerequisite Deprecation Lifecycle Specification

> **Status:** Implemented
> **Version:** 1.0
> **Part of:** dango-gitsea-bridge / Federation Prerequisite Deprecation Layer

---

## Core Principle

**A learned prerequisite must remain contestable, or it becomes authority again.**

If a promoted prerequisite cannot be weakened or deprecated in response to new plan tree
evidence, it has ceased to be evidence-based coordination and has become governance.

Dan-Go implements deprecation as evidence-first lifecycle management:
- A prerequisite is weakened when a claim bypasses it with an equivalent safety path.
- A prerequisite is deprecated when bypass evidence is sufficient AND the deprecation
  event is explicitly appended (no auto-removal).
- All events are append-only. The promotion event is never deleted.

---

## Absolute Prohibitions

```
No prerequisite auto-removal         — deprecation events are explicit, never automatic
No centralized override              — no admin can declare a prerequisite deprecated
No hidden scoring                    — the survivability formula is fully transparent
No governance vote                   — no voting mechanism exists
No deleting prerequisite history     — federation.jsonl is append-only
No mutating old promotion events     — promoted events are immutable
No external libraries                — stdlib only
No external network                  — all reads from local sutable/
```

---

## Lifecycle

```
promoted
    │
    │  3-way convergence (housing-004)
    ▼
reaffirmed  ◄──── new convergence evidence always reaffirms
    │
    │  bypass claim (housing-006) with equivalent_safety=True
    │  bypass_count >= 1
    ▼
weakened            (scope narrowed to non_precertified_spaces)
    │
    │  second bypass claim (hypothetical housing-007)
    │  bypass_count >= 2 AND equivalent_safety=True
    ▼
[deprecation_candidate]
    │
    │  explicit: prerequisite_contest_resolver.py --deprecate
    ▼
deprecated          (permanent event in federation.jsonl; still queryable)
    │
    │  new convergence evidence in future cycle
    ▼
[re-promotable — new federation_prerequisite_promoted event]
```

---

## The Bypass Distinction

A bypass is **not** simply a plan that omits the prerequisite.
A bypass requires an **equivalent safety path** — conditions that provide
the same safety guarantee through a different mechanism.

For `space_safety_assessed`, recognised equivalent conditions:
- `precertified_structure` — modular unit certified before deployment
- `external_safety_audit_attached` — third-party audit document attached
- `embedded_fire_controls` — fire suppression embedded in the modular unit

A plan that omits `space_safety_assessed` without any of the above is a **gap**,
not a bypass. The detector distinguishes these:

```
bypass_details[].equivalent_safety_found = True   → valid bypass
bypass_details[].requires_local_assessment = True  → gap (missing equiv safety)
```

---

## Survivability Score

```
base_score    = requiring_count / (requiring_count + bypassing_count)
penalty       = 0.15  if shared_objector in the promotion event
survivability = base_score - penalty  (floor: 0.0)
```

Status bands:

| survivability | status |
|---|---|
| >= 0.80 | strong |
| >= 0.50 | weakened |
| >= 0.20 | at_risk |
| < 0.20 | deprecated_candidate |

Current state of `space_safety_assessed`:

| field | value |
|---|---|
| requiring_count | 3 (housing-001, housing-002, housing-004) |
| bypassing_count | 1 (housing-006) |
| base_score | 0.75 |
| objector_penalty | 0.15 (shared_objector=True) |
| survivability | **0.60** |
| status | **weakened** |

Score is a transparent derived metric. It does not make decisions.

---

## Weakening

When `bypass_count >= 1 AND equivalent_safety = True`:

- `prerequisite_weakening.py` appends a `federation_prerequisite_weakened` event.
- The prerequisite is **not deprecated** — it remains active for non-precertified cases.
- `new_scope` narrows the applicability: `"non_precertified_spaces"`.
- Idempotent: a second bypass claim does not create a second weakened event.
- `authority: "none"` and `contestable: True` are always enforced.

```json
{
  "event_type": "federation_prerequisite_weakened",
  "condition": "space_safety_assessed",
  "new_scope": "non_precertified_spaces",
  "reason": "equivalent_safe_alternative_detected",
  "bypassing_claims": ["housing-006"],
  "equivalent_safety_conditions": [
    "embedded_fire_controls",
    "external_safety_audit_attached",
    "precertified_structure"
  ],
  "authority": "none",
  "contestable": true
}
```

---

## Deprecation Candidate Threshold

```
bypass_count >= 2  AND  equivalent_safety = True
```

At this threshold:
- `detect_bypass_patterns()` returns `deprecation_candidate: True`.
- `reevaluate()` recommends `"consider deprecation — bypass_count >= threshold with equivalent safety"`.
- **No auto-deprecation.** A participant must explicitly invoke:

```bash
python runtime/prerequisite_contest_resolver.py \
    --deprecate space_safety_assessed \
    --reason "Two independent claims bypassed via certified external audit path" \
    --speaker did:key:zDeprecater
```

The deprecation event is then appended to `sutable/federation.jsonl`.

---

## Re-promotion

A deprecated prerequisite can be re-promoted if new convergence evidence emerges.
The promotion event is a new event. The deprecation event is never deleted.
The full lifecycle is permanently queryable from `federation.jsonl`.

```bash
# After deprecation, if new convergence evidence emerges:
python runtime/prerequisite_promotion.py --append
# → produces a new federation_prerequisite_promoted event
# → the old promoted + deprecated events remain untouched
```

---

## Module Reference

### New modules

#### `runtime/prerequisite_alternative_plan.py` — bypass detection (read-only)

```python
detect_alternative_plans(condition, fmap=None) -> list[dict]
    # Returns: [{claim_id, plan_id, condition, bypasses_prerequisite, equivalent_safety_found,
    #            equivalent_conditions, requires_local_assessment, basis, dignity_safe}]

detect_all_alternative_plans(fmap=None) -> dict[str, list[dict]]
    # {condition: [bypass_records]}

equivalent_safety_conditions(condition) -> list[str]
    # EQUIVALENT_SAFETY table: space_safety_assessed → [precertified_structure, ...]
```

#### `runtime/prerequisite_deprecation_detector.py` — bypass monitoring (read-only)

```python
detect_bypass_patterns(condition, fmap=None) -> dict
    # Returns: {condition, requiring_claims, bypassing_claims, gap_claims,
    #           bypass_count, equivalent_safety, weakening_candidate,
    #           deprecation_candidate, already_weakened, bypass_details}

detect_all_bypass_patterns(fmap=None) -> list[dict]
weakening_candidates(fmap=None) -> list[dict]
deprecation_candidates(fmap=None) -> list[dict]
```

#### `runtime/prerequisite_survivability.py` — scoring (read-only)

```python
compute_survivability(condition, fmap=None) -> dict
    # Returns: {condition, requiring_count, bypassing_count, base_score,
    #           objector_penalty, survivability, status, shared_objector,
    #           requiring_claims, bypassing_claims}

compute_all_survivability(fmap=None) -> list[dict]
    # Ordered by survivability ascending (most at-risk first)
```

#### `runtime/prerequisite_weakening.py` — weakening events (writes federation.jsonl)

```python
build_weakening_event(condition, bypassing_claims, equivalent_safety_conditions,
                      *, reason, speaker) -> dict

compute_weakening_candidates(fmap=None) -> list[dict]

append_weakening_events(candidates, *, dry_run, verbose, speaker, fmap) -> list[dict]

weaken_prerequisites(*, dry_run, verbose, json_output, speaker) -> dict
```

#### `runtime/prerequisite_reevaluation.py` — lifecycle synthesis (read-only)

```python
reevaluate(condition, fmap=None) -> dict
    # Returns: {condition, lifecycle_state, survivability, survivability_status,
    #           bypass_count, requiring_count, weakening_candidate,
    #           deprecation_candidate, recommended_action, lifecycle_events}

reevaluate_all(fmap=None) -> list[dict]
    # Ordered by survivability ascending
```

#### `runtime/prerequisite_deprecation_snapshot.py` — full lifecycle query (read-only)

```python
deprecation_snapshot(condition=None, fmap=None) -> dict | list[dict]
    # Full snapshot: state + scope + survivability + bypass details + events

weakened_prerequisites(fmap=None) -> list[str]
deprecated_prerequisites(fmap=None) -> list[str]
```

### Updated modules

#### `runtime/prerequisite_contest_resolver.py`
- Added `WEAKENED = "federation_prerequisite_weakened"` constant
- Added `WEAKENED` to `_PREREQ_TYPES`
- `get_prerequisite_status()` returns `status="weakened"` and `new_scope`

#### `runtime/prerequisite_snapshot.py`
- `promoted_prerequisites()` includes `"weakened"` status
- `_print_status()` shows `✓~` symbol for weakened prerequisites

#### `runtime/graph_export.py`
- Text: FEDERATION PREREQUISITES shows `✓~`, new_scope, weaken_count
- Text: PREREQUISITE LIFECYCLE section with bypass/requires edges
- Mermaid: bypass edges `housing_006 -.->|bypass| prereq_space-safety-assessed`

#### `runtime/negotiation_graph.py`
- Virtual prerequisite nodes include `weakened` status and `new_scope`
- Adds `prerequisite_bypass` edge kind for bypassing claims

---

## CLI Reference

```bash
# Detect bypass patterns
python runtime/prerequisite_deprecation_detector.py
python runtime/prerequisite_deprecation_detector.py --condition space_safety_assessed
python runtime/prerequisite_deprecation_detector.py --weakening-candidates
python runtime/prerequisite_deprecation_detector.py --deprecation-candidates --json

# Detect alternative plans
python runtime/prerequisite_alternative_plan.py
python runtime/prerequisite_alternative_plan.py --condition space_safety_assessed --json

# Compute survivability
python runtime/prerequisite_survivability.py
python runtime/prerequisite_survivability.py --condition space_safety_assessed --json

# Preview + append weakening events
python runtime/prerequisite_weakening.py              # dry-run preview
python runtime/prerequisite_weakening.py --append     # write to federation.jsonl
python runtime/prerequisite_weakening.py --append --verbose

# Reevaluate lifecycle signals
python runtime/prerequisite_reevaluation.py
python runtime/prerequisite_reevaluation.py --condition space_safety_assessed --json

# Full deprecation lifecycle snapshot
python runtime/prerequisite_deprecation_snapshot.py
python runtime/prerequisite_deprecation_snapshot.py --condition space_safety_assessed
python runtime/prerequisite_deprecation_snapshot.py --weakened
python runtime/prerequisite_deprecation_snapshot.py --json

# Explicit deprecation (after manual review of bypass evidence)
python runtime/prerequisite_contest_resolver.py \
    --deprecate space_safety_assessed \
    --reason "Two independent claims bypassed via certified external audit" \
    --speaker did:key:zDeprecater
```

---

## Integration Pipeline

```bash
# 1. Check for bypass patterns
python runtime/prerequisite_deprecation_detector.py --verbose

# 2. Inspect alternative plans
python runtime/prerequisite_alternative_plan.py --condition space_safety_assessed

# 3. Compute survivability
python runtime/prerequisite_survivability.py

# 4. Reevaluate lifecycle
python runtime/prerequisite_reevaluation.py

# 5. Weaken if evidence is sufficient (bypass_count >= 1)
python runtime/prerequisite_weakening.py              # preview
python runtime/prerequisite_weakening.py --append     # write

# 6. Full deprecation snapshot
python runtime/prerequisite_deprecation_snapshot.py

# 7. (When bypass_count >= 2) — explicit deprecation after review
python runtime/prerequisite_contest_resolver.py --deprecate ... --reason ... --speaker ...
```

---

## Current State (housing-006 scenario)

`space_safety_assessed` is currently in `weakened` state.

To reach `deprecated`:
1. A second claim (e.g. housing-007) must submit a plan omitting `space_safety_assessed`
   with equivalent safety conditions attached.
2. That plan must pass negotiation without `insufficient_risk_coverage` objection.
3. `detect_bypass_patterns()` must return `deprecation_candidate: True`.
4. A participant must explicitly append a `federation_prerequisite_deprecated` event.

There is no shortcut. No auto-deprecation. No governance vote.
The only valid deprecation evidence is a plan tree that achieves the claim goals
without the condition.

---

## New Event Type

### `federation_prerequisite_weakened`

```json
{
  "event_type": "federation_prerequisite_weakened",
  "condition": "space_safety_assessed",
  "new_scope": "non_precertified_spaces",
  "reason": "equivalent_safe_alternative_detected",
  "bypassing_claims": ["housing-006"],
  "equivalent_safety_conditions": [
    "embedded_fire_controls",
    "external_safety_audit_attached",
    "precertified_structure"
  ],
  "promotion_basis": "independent_plan_tree_diff_convergence",
  "authority": "none",
  "contestable": true,
  "speaker": "did:key:zSystemDetector"
}
```

`authority: "none"` and `contestable: True` are enforced by
`prerequisite_weakening.py` at write time. No code path sets them to anything else.

---

## Design Principles

1. **No auto-removal.** `federation_prerequisite_deprecated` is always an explicit event.
   The system can detect candidates; it cannot decide.

2. **Evidence only.** The only valid weakening/deprecation evidence is a plan tree
   that achieves claim goals without the condition, using an equivalent safety path.

3. **Transparent scoring.** The survivability formula is `requiring/(requiring+bypassing) - penalty`.
   Every term is traceable to a specific plan event.

4. **Append-only.** Promoted, weakened, and deprecated events all coexist in
   `federation.jsonl`. History is never modified.

5. **Advisory always.** Even after weakening, the prerequisite is a hint,
   not a gate. Plans that omit it can still be submitted.

6. **Scope, not erasure.** Weakening narrows the prerequisite to
   `non_precertified_spaces`. It does not tell non-precertified claims to ignore
   the condition — it tells them the condition still applies to their context.

---

## Related Specs

- [FEDERATION_PREREQUISITE_SPEC.md](FEDERATION_PREREQUISITE_SPEC.md) — promotion, contestation, evidence lifecycle
- [FEDERATION_BRANCHING_SPEC.md](FEDERATION_BRANCHING_SPEC.md) — federation branching and condition propagation
- [REFLECTIVE_MEMORY_SPEC.md](REFLECTIVE_MEMORY_SPEC.md) — reflective memory loop (source of learned_conditions)
- [PLAN_NEGOTIATION_SPEC.md](PLAN_NEGOTIATION_SPEC.md) — plan negotiation (source of plan tree diffs)

---

*dango-gitsea-bridge · authority: none · append-only · stdlib only*
