# RESUME_STATE.md — Federation Prerequisite Deprecation Lifecycle

> **STATUS: COMPLETE**
> All steps done. Push pending (check git log to confirm).

**Phase:** Federation Prerequisite Deprecation Lifecycle
**Branch:** main
**Started:** 2026-05-24
**Completed:** 2026-05-24

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

Core principle: A learned prerequisite must remain contestable, or it becomes authority again.

Experiment claim: housing-006 — pre-certified modular emergency kitchen.
  Plan: precertified_structure + external_safety_audit_attached + embedded_fire_controls
  Omits: space_safety_assessed (deliberate bypass with equivalent safety path)

### Results

| Field | Before housing-006 | After housing-006 |
|---|---|---|
| lifecycle_state | reaffirmed | weakened |
| survivability | N/A | 0.60 |
| survivability_status | N/A | weakened |
| requiring_claims | housing-001, 002, 004 | housing-001, 002, 004 |
| bypassing_claims | (none) | housing-006 |
| new_scope | — | non_precertified_spaces |
| deprecation_candidate | False | False (bypass_count=1 < 2) |

### New event appended

sutable/federation.jsonl (+1 event):
  federation_prerequisite_weakened  space_safety_assessed
    new_scope: non_precertified_spaces
    bypassing_claims: [housing-006]
    equivalent_safety: [embedded_fire_controls, external_safety_audit_attached, precertified_structure]

### Key design points confirmed

- weakening is idempotent: second run returns "No weakening candidates."
- bypass requires equivalent_safety_found=True (not just omission)
- survivability = 0.75 (base) - 0.15 (shared_objector penalty) = 0.60
- status=weakened (score >= 0.50 band)
- deprecation_candidate=False (bypass_count=1 < threshold of 2)
- recommended_action: "monitor — weakened scope; watch for additional bypass evidence"
- no auto-removal; explicit federation_prerequisite_deprecated event required

---

## New Files

### runtime/
- prerequisite_alternative_plan.py   (bypass detection with equiv safety)
- prerequisite_deprecation_detector.py (bypass monitoring, candidates)
- prerequisite_survivability.py      (score: requiring/total - penalty)
- prerequisite_weakening.py          (append weakened events)
- prerequisite_reevaluation.py       (lifecycle synthesis)
- prerequisite_deprecation_snapshot.py (full lifecycle query)

### examples/
- housing-006-plan-v1.json
- housing-006-memory-snapshot.json
- prerequisite-survivability.snapshot.json
- prerequisite-deprecation-contest.json
- deprecated-prerequisite.snapshot.json   (hypothetical full deprecation)

### docs/
- PREREQUISITE_DEPRECATION_SPEC.md   (new)
- FEDERATION_PREREQUISITE_SPEC.md    (cross-reference added)
- README.md                          (deprecation section + module tree)

---

## Known Limitations

- housing-003 and housing-005 still have no plan events
- food_safety_reviewed has only 1 claim (housing-004) — below promotion threshold
- DID signatures still mock
- GITSEA still hypothetical
- Deprecation not yet triggered (bypass_count=1; need 2 for deprecation_candidate=True)

---

## Next Step Candidates

1. **Second bypass claim (housing-007)** — bring bypass_count to 2, trigger deprecation_candidate,
   test explicit deprecation lifecycle end-to-end.

2. **food_safety_reviewed promotion** — add housing-005 plan events with food_safety_reviewed
   to bring it to threshold (convergence_count ≥ 2) and test new promotion.

3. **Prerequisite decay** — a promoted prerequisite loses evidence weight over time
   if no new convergence arrives. Analogous to temporal_trust_decay.py.

4. **Validator federation network** — two agents independently compute prerequisite
   candidates from the same event log. Confirm deterministic agreement.

5. **Public negotiation UI** — HTML prerequisite panel already implemented;
   full web view with evidence graph + contest history + deprecation timeline.

6. **Prerequisite trust weighting** — factor prerequisite strength (evidence_score,
   survivability) into plan selection when multiple plans differ on prerequisites.

---

*dango-gitsea-bridge · authority: none · append-only · stdlib only*
