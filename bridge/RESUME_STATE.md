# RESUME_STATE.md — Federation-Aware Plan Branching Layer

> If implementation is interrupted, start here.

**Phase:** Federation-Aware Plan Branching Layer  
**Branch:** main  
**Started:** 2026-05-24  
**Last checkpoint:** starting — survey done, RESUME_STATE updated

---

## Previous Phase Complete

Documentation phase complete. See commits 3525160..d2f543c.
All prior runtime modules implemented. See docs for details.

---

## Current Phase: Federation Branching

Goal: claims influence each other. Plans branch on federation state.
Dependency resolution is advisory, not orchestrated. Everything append-only.

Federation claim network in sutable/federation.jsonl:
  housing-002 depends_on housing-001
  housing-003 counterclaims housing-001
  housing-004 depends_on housing-001 (enables), federation_link housing-002
  housing-005 derived_from housing-003

| Step | File | Status | Commit |
|------|------|--------|--------|
| 0 | RESUME_STATE.md | ✓ DONE | TBD |
| 1 | `runtime/federation_branching.py` | ⏳ PENDING | — |
| 2 | `runtime/federation_condition_propagation.py` | ⏳ PENDING | — |
| 3 | `runtime/federation_trust_propagation.py` | ⏳ PENDING | — |
| 4 | `runtime/federation_activation.py` | ⏳ PENDING | — |
| 5 | `runtime/federation_ripple_detector.py` | ⏳ PENDING | — |
| 6 | `runtime/federation_memory_feedback.py` | ⏳ PENDING | — |
| 7 | `examples/federation-branching.claim.json` + events | ⏳ PENDING | — |
| 8 | `runtime/graph_export.py` update | ⏳ PENDING | — |
| 9 | `runtime/negotiation_graph.py` update | ⏳ PENDING | — |
| 10 | `FEDERATION_BRANCHING_SPEC.md` | ⏳ PENDING | — |
| 11 | Doc updates (README, CLAIM_FEDERATION_SPEC, REFLECTIVE_MEMORY_SPEC) | ⏳ PENDING | — |
| 12 | Final RESUME_STATE.md + push | ⏳ PENDING | — |

---

## Architecture Decisions (for resume context)

### New event types (all in sutable/federation.jsonl)
- `federation_condition_met`    — upstream condition confirmed satisfied
- `federation_condition_blocked` — upstream condition blocked (dignity/rejection)
- `federation_claim_activated`  — dependent claim now unblocked
- `federation_claim_paused`     — claim waiting on upstream
- `federation_ripple_detected`  — blocking chain or dignity spread detected
- `federation_memory_feedback`  — federation-wide memory hint

### Branch status values
- `active`  — all dependencies met, claim can proceed
- `paused`  — upstream claims still in negotiation
- `blocked` — upstream has dignity violation or formal rejection
- `unknown` — insufficient information

### Key design invariants
- propagation is advisory — no execution triggered
- no central orchestrator — each module reads events and computes
- append-only — new condition events do NOT modify existing ones
- dignity_violation objection on upstream → downstream is blocked
- computation is deterministic given the same event log

### Module dependency graph
```
federation_branching.py
  ← claim_federation.py (federation map)
  ← active_plan_selector.py (computed active plan)
  ← sutable_log.py (read plans + federation events)
  ← reflective_memory.py (extract_prior_knowledge)

federation_condition_propagation.py
  ← federation_branching.py (branch status)
  ← reflective_memory.py (learned conditions)
  ← active_plan_selector.py

federation_trust_propagation.py
  ← sutable_log.py (contributions + plans)
  ← temporal_trust_decay.py

federation_activation.py
  ← federation_branching.py
  ← federation_condition_propagation.py

federation_ripple_detector.py
  ← federation_branching.py
  ← claim_federation.py

federation_memory_feedback.py
  ← reflective_memory.py
  ← federation_branching.py
  ← sutable_log.py (memory)
```

---

## Next Command (if resuming)

```bash
cd /Users/olddqn/dango-mujin/bridge

# Check which modules exist
ls runtime/federation_*.py

# Smoke test whichever exist:
python runtime/federation_branching.py --claim-id housing-002
python runtime/federation_activation.py
python runtime/federation_ripple_detector.py

# Then continue with next step in table above
```

---

## Blockers

None. All dependencies available.

---

## Known Limitations After This Phase

- DID signatures still mock
- GITSEA still hypothetical
- federation condition propagation is advisory (no formal trigger mechanism)
- trust propagation uses contributions.jsonl which is mostly empty in current data
