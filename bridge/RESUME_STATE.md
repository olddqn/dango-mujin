# RESUME_STATE.md — Current Status

> If implementation is interrupted, start here.
> This file is always up to date as of the last commit.

**Phase:** Documentation + Presentation — COMPLETE  
**Branch:** main  
**Last push:** GitHub + gitlawb (see git log)

---

## What Is Implemented

Dan-Go is a negotiation protocol for impossible claims.  
All core subsystems are implemented. No new runtime logic is needed at this time.

### Implemented Subsystems

| Subsystem | Key modules | Status |
|-----------|-------------|--------|
| **Su-table persistence** | `sutable_log.py`, `sutable_append.py`, `sutable_query.py` | ✓ |
| **Dignity guard** | `dignity_guard.py` | ✓ |
| **Claim → repo asset** | `claim_to_asset.py`, `stream_preview.py`, `contribution_ledger.py` | ✓ |
| **Negotiation events** | `negotiation_event.py`, `reality_feedback_append.py` | ✓ |
| **Negotiation graph** | `negotiation_graph.py`, `graph_export.py` | ✓ |
| **World model** (OGI) | `ogi/runtime/world_model_mapper.py` | ✓ |
| **Plan tree** (OGI) | `ogi/runtime/claim_plan_tree.py`, `plan_tree_validator.py` | ✓ |
| **Task bundle** (OGI) | `ogi/runtime/plan_tree_to_tasks.py`, `task_dependency_resolver.py` | ✓ |
| **Plan persistence** | `plan_event_append.py`, `plan_correction.py`, `plan_snapshot.py` | ✓ |
| **Multi-agent negotiation** | `plan_negotiation_append.py`, `active_plan_selector.py`, `plan_contest_resolver.py`, `plan_negotiation_snapshot.py`, `plan_negotiation_graph.py` | ✓ |
| **Reflective memory** | `reflective_memory.py`, `memory_append.py`, `memory_snapshot.py`, `world_model_with_memory.py` | ✓ |
| **DID signatures** (mock) | `did_signature.py`, `sign_event.py`, `verify_event_signature.py` | ✓ mock |
| **Trust decay** | `temporal_trust_decay.py`, `contribution_weight.py`, `trust_snapshot.py` | ✓ |
| **Claim federation** | `claim_dependency.py`, `claim_federation.py`, `federation_graph.py`, `federation_snapshot.py` | ✓ |
| **Task bundle persistence** | `task_bundle_append.py` | ✓ |

### Su-table logs

| File | Contents |
|------|---------|
| `sutable/claims.jsonl` | Claim events |
| `sutable/negotiations.jsonl` | Negotiation events |
| `sutable/contributions.jsonl` | Contribution events |
| `sutable/executions.jsonl` | Execution events |
| `sutable/reality_feedback.jsonl` | Reality feedback events |
| `sutable/plans.jsonl` | Plan tree + task bundle + negotiation signal events |
| `sutable/memory.jsonl` | Reflective memory snapshots |
| `sutable/federation.jsonl` | Claim federation events |

### Documentation (completed this phase)

| Document | Purpose |
|----------|---------|
| `README.md` | Rewritten landing page — clean, engineer-readable |
| `ARCHITECTURE_OVERVIEW.md` | Full system architecture with data flow diagrams |
| `WHY_DANGO_EXISTS.md` | Manifesto: coordination collapse, dignity, AI negotiation |
| `DANGO_GITSEA_OGI_MAP.md` | Cross-system mapping + common misunderstandings |
| `VISUAL_SYSTEM_MAP.mmd` | Mermaid architecture diagram (all 11+ subsystems) |
| `EXAMPLES_INDEX.md` | Guide to all 25+ example files |

### Earlier specs

| Document | Purpose |
|----------|---------|
| `SUTABLE_APPEND_ONLY_SPEC.md` | Su-table specification |
| `PLAN_APPEND_ONLY_SPEC.md` | Plan + task bundle persistence |
| `PLAN_NEGOTIATION_SPEC.md` | Multi-agent negotiation (with memory integration note) |
| `REFLECTIVE_MEMORY_SPEC.md` | Reflective memory loop |
| `CLAIM_FEDERATION_SPEC.md` | Claim federation |
| `DID_SIGNATURE_SPEC.md` | DID signatures (mock) |
| `TEMPORAL_TRUST_DECAY_SPEC.md` | Trust decay formula |
| `DIGNITY_GUARD.md` | 7-rule dignity guard |
| `DANGO_GITSEA_THESIS.md` | Original bridge thesis |
| `NEGOTIATION_GRAPH_SPEC.md` | Negotiation graph |
| `PASS_FLOW_EXAMPLE.md` | Consent-established PASS flow walkthrough |

---

## Known Limitations

1. **DID signatures are mock** — test vectors only, not real cryptography
2. **GITSEA is hypothetical** — real implementation status unverified
3. **No execution layer** — plans are proposals; nothing runs tasks automatically
4. **world_model_mapper requires a claim file** — does not auto-load from claims.jsonl directly (workaround: `world_model_with_memory.py --claim-id` does this)
5. **federation.jsonl** — populated from examples only; no live federation network
6. **No real OGI connection** — ogi/runtime/ is a local reference implementation

---

## Recommended Next Steps

These are directions, not commitments. Each is independent.

### Near-term (protocol hardening)

1. **Real DID signatures** — replace mock with Ed25519 / did:key proper
2. **Reality feedback auto-trigger** — when `reality_feedback` event arrives, auto-run `memory_append.py`
3. **Claim lifecycle query** — `claim_lifecycle.py` that returns computed state: open / active / resolved / blocked
4. **Plan tree schema validation** — stricter validation in `plan_tree_validator.py` with JSON Schema

### Medium-term (integration)

5. **Federation network stub** — connect `federation.jsonl` to a real peer list via gitlawb
6. **Web reader** — minimal static HTML for reading negotiation graphs without Python
7. **Su-table streaming** — tail-mode for live negotiation event display
8. **Agent manifest** — `agent_manifest.py` declaring what an agent can do in Dan-Go

### Longer-term (ecosystem)

9. **GITSEA bridge** — if/when GITSEA has a real API, wire up `claim_to_asset.py` and `stream_preview.py`
10. **WASM build** — compile `sutable_log.py` logic to WASM for browser use
11. **RSS/Atom feed** — su-table events as a feed for external subscribers

---

## Pending Ideas

- `abstain_registry.py` — track which plans have abstain nodes and why
- `dignity_audit.py` — summarize dignity constraint coverage across all plans
- Multi-claim memory — reflective memory that spans related claims in a federation
- Contribution stream → GITSEA mapping unit test harness
- Plan tree diff visualization (show what changed between v1 and v2)

---

## External Integration Status

| System | Status |
|--------|--------|
| GITSEA | Hypothetical — design target only |
| OGI | Local reference implementation only |
| gitlawb | ✓ Connected — pushes to node.gitlawb.com |
| Nookplot | Not integrated |
| DID network | Mock only — test vectors |

---

## If Resuming: Quick Orientation

```bash
# Where is everything?
cd bridge/

# What's in the event logs?
python runtime/sutable_query.py --count

# Housing-001 full state
python runtime/plan_negotiation_snapshot.py --claim-id housing-001
python runtime/memory_snapshot.py --claim-id housing-001 --prior-knowledge

# Check all remotes
git remote -v
git log --oneline -10

# Push to both remotes (if needed)
git push github main
GITLAWB_NODE=https://node.gitlawb.com git push gitlawb main
```

---

## Invariants (never change these)

- Su-table is append-only. Corrections are new events. Nothing is deleted.
- Dignity guard runs first. It cannot be bypassed.
- Plan selection is deterministic and transparent. No hidden scoring.
- Memory is derived from plans.jsonl. It can be independently verified.
- `dignity_violation` objections disqualify a plan regardless of support count.
- Trust falls to exactly zero on dignity violation. No floor.
