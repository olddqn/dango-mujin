# RESUME_STATE.md — Federation Prerequisite Promotion Layer

> If implementation is interrupted, start here.

**Phase:** Federation Prerequisite Promotion Layer
**Branch:** main
**Started:** 2026-05-24
**Last checkpoint:** starting — survey done, RESUME_STATE updated

---

## Previous Phases Complete

- Reflective Memory Loop (commits 3e3d4e7..7d328c2)
- Documentation Phase (commits 64fecb1..dc2691d)
- Federation-Aware Branching Layer (commits b8b7d61..eab0f60)
- Housing-002 Memory Snapshot / Cross-claim Pattern Detection (commit 3f1dba6)

---

## Current Phase: Federation Prerequisite Promotion

Goal: A condition independently discovered by ≥2 claims through plan tree diff
becomes a federation prerequisite candidate — then a promoted prerequisite —
then contestable. Evidence-based, not authority-based. Append-only.

Key data currently in sutable:
  housing-001 learned: [space_safety_assessed]
  housing-002 learned: [space_safety_assessed, network_security_assessed]
  → space_safety_assessed: independent convergence across 2 claims ✓

| Step | File | Status | Commit |
|------|------|--------|--------|
| 0 | RESUME_STATE.md | ✓ DONE | this commit |
| 1 | `runtime/federation_prerequisite_detector.py` | ⏳ PENDING | — |
| 2 | `runtime/prerequisite_evidence_bundle.py` | ⏳ PENDING | — |
| 3 | `runtime/prerequisite_promotion.py` | ⏳ PENDING | — |
| 4 | `runtime/prerequisite_contest_resolver.py` | ⏳ PENDING | — |
| 5 | `runtime/prerequisite_snapshot.py` | ⏳ PENDING | — |
| 6 | `runtime/prerequisite_memory_integration.py` | ⏳ PENDING | — |
| 7 | `runtime/graph_export.py` update | ⏳ PENDING | — |
| 8 | `runtime/negotiation_graph.py` update | ⏳ PENDING | — |
| 9 | example files (4 files) | ⏳ PENDING | — |
| 10 | `FEDERATION_PREREQUISITE_SPEC.md` | ⏳ PENDING | — |
| 11 | doc updates (README, FEDERATION_BRANCHING_SPEC, REFLECTIVE_MEMORY_SPEC) | ⏳ PENDING | — |
| 12 | `runtime/federation_memory_feedback.py` update | ⏳ PENDING | — |
| 13 | Final RESUME_STATE.md + push | ⏳ PENDING | — |

---

## Architecture Decisions

### New event types (sutable/federation.jsonl)
- `federation_prerequisite_promoted`  — condition meets promotion criteria
- `federation_prerequisite_contested` — a participant contests a promoted prerequisite
- `federation_prerequisite_reaffirmed`— contest resolved: prerequisite stands
- `federation_prerequisite_deprecated`— contest resolved: prerequisite withdrawn

### Promotion criteria
- independent_convergence_count >= 2 (INDEPENDENT_CLAIM_THRESHOLD)
- all evidence claims dignity-safe (no dignity_violation objections on any plan)
- condition not already promoted (dedup: check existing promoted events)
- authority: always "none"

### Independence check
- `plan_author_overlap`: bool — whether plan proposers overlap across claims
- `objector_overlap`: bool — whether same objector appears in multiple claims
  (metadata only — not a disqualifier; same agent can legitimately find same gap twice)
- `independent_convergence`: True when different plan authors + different claims

### Module dependency graph
```
federation_prerequisite_detector.py
  ← sutable_log.py (read_all: memory, plans)
  ← claim_federation.py (federation map)

prerequisite_evidence_bundle.py
  ← federation_prerequisite_detector.py
  ← sutable_log.py (read_all: plans, memory)

prerequisite_promotion.py
  ← federation_prerequisite_detector.py
  ← prerequisite_evidence_bundle.py
  ← sutable_log.py (append_event: federation)

prerequisite_contest_resolver.py
  ← sutable_log.py (read_all: federation; append_event: federation)

prerequisite_snapshot.py
  ← sutable_log.py (read_all: federation)
  ← prerequisite_evidence_bundle.py

prerequisite_memory_integration.py
  ← prerequisite_snapshot.py
  ← sutable_log.py (read_all: memory)

graph_export.py
  ← prerequisite_snapshot.py (optional import)

negotiation_graph.py
  ← prerequisite_snapshot.py (optional import)
```

### Key invariants
- authority: always "none" on every promoted event
- contestable: always true on promoted events
- append-only: contests and deprecations are new events
- no text similarity: structure only (learned_conditions, plan_tree conditions)
- advisory only: promoted prerequisites are hints, never hard gates

---

## Next Command (if resuming)

```bash
cd /Users/olddqn/dango-mujin/bridge

# Check what exists
ls runtime/federation_prerequisite_detector.py runtime/prerequisite_*.py 2>/dev/null

# Smoke test existing modules
python3 runtime/federation_prerequisite_detector.py --json 2>/dev/null || echo "not yet"

# Continue with next step in table above
```

---

## Blockers

None. Housing-001 and housing-002 both have memory snapshots.
space_safety_assessed is ready to be detected and promoted.

---

## Known Limitations After This Phase

- DID signatures still mock
- GITSEA still hypothetical
- Only housing-001 and housing-002 have memory snapshots
  (housing-003/004/005 have no plan events)
- prerequisite_decay not implemented (future step candidate)
- cross-federation exchange not implemented (future step candidate)
