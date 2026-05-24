# RESUME_STATE.md — Federation Prerequisite Deprecation Lifecycle

> **STATUS: IN PROGRESS**

**Phase:** Federation Prerequisite Deprecation Lifecycle
**Branch:** main
**Started:** 2026-05-24

---

## Previous Phases Complete

- Reflective Memory Loop (commits 3e3d4e7..7d328c2)
- Documentation Phase (commits 64fecb1..dc2691d)
- Federation-Aware Branching Layer (commits b8b7d61..eab0f60)
- Housing-002 Memory Snapshot / Cross-claim Pattern Detection (commit 3f1dba6)
- Federation Prerequisite Promotion Layer (commits 7a521b3..1edc3d9)
- 3-Way Convergence Test (commit 09faf1d)

---

## This Phase: Prerequisite Deprecation Lifecycle

Core philosophy: A learned prerequisite must remain contestable, or it becomes authority again.

Experiment claim: housing-006 — pre-certified modular emergency kitchen.
  - Conditions: precertified_structure, external_safety_audit_attached, embedded_fire_controls
  - Deliberately omits: space_safety_assessed
  - Outcome: bypass detected → weakening → potential deprecation

---

## Implementation Steps

### Step 1: Fixture (housing-006)
- [ ] Append housing-006 plan events to sutable/plans.jsonl
  - plan_tree_created  housing-006  plan-housing-006-v1  did:key:z6MkPrefabKitchen006
  - plan_supported     housing-006  plan-housing-006-v1  did:key:z6PrefabSupport006
- [ ] Append housing-006 memory snapshot to sutable/memory.jsonl
  - learned_conditions = [] (no contest, no diff)
- [ ] Commit: checkpoint: add housing-006 prefab kitchen fixture

### Step 2: New modules (group A — detection)
- [ ] runtime/prerequisite_alternative_plan.py
  - detect plans achieving goals without a prerequisite condition
  - check for equivalent safety conditions
- [ ] runtime/prerequisite_deprecation_detector.py
  - monitors promoted prerequisites for bypass patterns
  - threshold: bypass_claims >= 2 AND equivalent_safety = True → deprecation_candidate
  - threshold: bypass_claims >= 1 AND equivalent_safety = True → weakening_candidate
- [ ] Commit: checkpoint: prerequisite deprecation steps 1-2

### Step 3: New modules (group B — scoring + events)
- [ ] runtime/prerequisite_survivability.py
  - survivability = requiring/(requiring+bypassing) - (0.15 if shared_objector)
  - status: >=0.8=strong, >=0.5=weakened, >=0.2=at_risk, <0.2=deprecated_candidate
- [ ] runtime/prerequisite_weakening.py
  - appends federation_prerequisite_weakened events
  - new_scope: "non_precertified_spaces"
  - reason: "equivalent_safe_alternative_detected"
- [ ] Commit: checkpoint: prerequisite deprecation steps 3-4

### Step 4: New modules (group C — synthesis + query)
- [ ] runtime/prerequisite_reevaluation.py
  - synthesizes: reaffirmed / weakened / deprecated / unresolved
- [ ] runtime/prerequisite_deprecation_snapshot.py
  - full lifecycle query including weakening, bypass, survivability
- [ ] Commit: checkpoint: prerequisite deprecation steps 5-6

### Step 5: Update existing modules
- [ ] prerequisite_contest_resolver.py: add WEAKENED constant + _PREREQ_TYPES
- [ ] prerequisite_snapshot.py: show weakened status (✓~ symbol)
- [ ] graph_export.py: PREREQUISITE LIFECYCLE section, bypass edges
- [ ] negotiation_graph.py: prerequisite_bypass, weaken, deprecate edge kinds
- [ ] Commit: checkpoint: prerequisite deprecation step 7 — existing module updates

### Step 6: Example files + spec + docs
- [ ] examples/housing-006-plan-v1.json
- [ ] examples/housing-006-memory-snapshot.json
- [ ] examples/prerequisite-survivability.snapshot.json
- [ ] examples/prerequisite-deprecation-contest.json (weakened lifecycle)
- [ ] examples/deprecated-prerequisite.snapshot.json (hypothetical full deprecation)
- [ ] PREREQUISITE_DEPRECATION_SPEC.md
- [ ] Update FEDERATION_PREREQUISITE_SPEC.md (cross-reference)
- [ ] Update README.md (deprecation paragraph)
- [ ] Commit: feat: add prerequisite deprecation lifecycle

### Step 7: Push
- [ ] git push github main
- [ ] GITLAWB_NODE=https://node.gitlawb.com git push gitlawb main

---

## New Event Types

- `federation_prerequisite_weakened` — scope narrowed; still active for non-precertified spaces

## New Files

### runtime/
- prerequisite_alternative_plan.py
- prerequisite_deprecation_detector.py
- prerequisite_survivability.py
- prerequisite_weakening.py
- prerequisite_reevaluation.py
- prerequisite_deprecation_snapshot.py

### examples/
- housing-006-plan-v1.json
- housing-006-memory-snapshot.json
- prerequisite-survivability.snapshot.json
- prerequisite-deprecation-contest.json
- deprecated-prerequisite.snapshot.json

### docs/
- PREREQUISITE_DEPRECATION_SPEC.md (new)
- FEDERATION_PREREQUISITE_SPEC.md (updated)
- README.md (updated)

---

## Known Limitations (from prior phases)

- housing-003 and housing-005 still have no plan events
- DID signatures still mock
- GITSEA still hypothetical

---

*dango-gitsea-bridge · authority: none · append-only · stdlib only*
