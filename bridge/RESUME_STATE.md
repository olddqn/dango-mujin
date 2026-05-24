# RESUME_STATE.md — Scoped Prerequisite Inheritance Layer

> **STATUS: IN PROGRESS**

**Phase:** Scoped Prerequisite Inheritance Layer
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
- Federation Prerequisite Deprecation Lifecycle (commits 7649826..0dd26b3)

---

## This Phase: Scoped Prerequisite Inheritance Layer

Core principle: A weakened prerequisite does not disappear. Its applicability becomes conditional.

space_safety_assessed is NOT abolished — it is scoped:
  applies_to:   non_precertified_spaces, modified_existing_structures
  bypassed_by:  precertified_modular_spaces, externally_audited_units

---

## Implementation Steps

### Step 1: Fixture (housing-007)
- [ ] Append housing-007 plan events to sutable/plans.jsonl
  - Modified community workspace (old building, local modifications, no audit, no precert)
  - Plan includes space_safety_assessed (prerequisite applies)
  - structural_modification_documented (scope indicator: non-precertified)
- [ ] Append housing-007 memory snapshot to sutable/memory.jsonl
- [ ] Commit: checkpoint: add housing-007 modified-workspace fixture

### Step 2: Core scope modules (group A)
- [ ] runtime/prerequisite_scope_resolver.py   — deterministic scope rules from weakened events
- [ ] runtime/scoped_prerequisite_inheritance.py — per-claim applicability
- [ ] Commit: checkpoint: scoped prerequisite steps 1-2

### Step 3: Detection and propagation (group B)
- [ ] runtime/scope_conflict_detector.py       — contradictory scope declarations
- [ ] runtime/scoped_condition_propagation.py  — scope-aware federation propagation
- [ ] Commit: checkpoint: scoped prerequisite steps 3-4

### Step 4: World model + snapshot (group C)
- [ ] runtime/scoped_world_model.py            — scope-aware world model prior_knowledge
- [ ] runtime/scoped_prerequisite_snapshot.py  — full scoped query
- [ ] Commit: checkpoint: scoped prerequisite steps 5-6

### Step 5: Update existing modules
- [ ] runtime/prerequisite_memory_integration.py — scope-aware hints
- [ ] runtime/world_model_with_memory.py         — scoped inheritance
- [ ] runtime/federation_condition_propagation.py — scope-aware propagation
- [ ] runtime/graph_export.py    — SCOPED PREREQUISITES section + HTML scope panel
- [ ] runtime/negotiation_graph.py — scoped_requirement, scoped_bypass, scope_conflict edges
- [ ] Commit: checkpoint: scoped prerequisite step 7 — existing module updates

### Step 6: Examples + spec + docs
- [ ] examples/scoped-prerequisite-event.json
- [ ] examples/scoped-inheritance.snapshot.json
- [ ] examples/housing-007-scope-resolution.json
- [ ] examples/scoped-world-model.json
- [ ] SCOPED_PREREQUISITE_SPEC.md (new)
- [ ] PREREQUISITE_DEPRECATION_SPEC.md (cross-reference)
- [ ] FEDERATION_PREREQUISITE_SPEC.md (cross-reference)
- [ ] README.md (scoped section + module tree)
- [ ] Commit: feat: add scoped prerequisite inheritance layer

### Step 7: Push
- [ ] git push github main
- [ ] GITLAWB_NODE=https://node.gitlawb.com git push gitlawb main

---

## Key Design Points

- Scope rules are derived deterministically from weakened event's equivalent_safety_conditions
- bypass = active plan includes ANY equivalent_safety_condition
- applicable = active plan lacks all equivalent_safety_conditions
- scope_conflict = plan has both bypass indicators AND local-modification indicators
- No hidden scoring. No centralized scope assignment. stdlib only.
- authority: none always.

---

## Known Limitations (from prior phases)

- DID signatures still mock
- GITSEA still hypothetical
- food_safety_reviewed below promotion threshold (1 claim only)

---

*dango-gitsea-bridge · authority: none · append-only · stdlib only*
