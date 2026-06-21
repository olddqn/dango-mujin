# Agent Commons Report

- Generated: 2026-06-18T20:29:53.170867Z
- Layer: `bridge/agent_commons/` (advisory only · authority none · AI proposes, human decides)

## Counts
| metric | value |
|---|---|
| Voice Count (Mujin, read-only) | 6 |
| Observation Candidate Count | 6 |
| Task Candidate Count | 25 |
| Agent Registry Count | 7 |
| Agent Results Count | 0 (no execution this phase) |
| Evidence Candidate Count | 1 |
| Evidence Coverage | 1/1 |
| Patterns With Evidence | 1 |
| Patterns Without Evidence | 0 |
| Human Reviewed Evidence Count | 0 (AI-gathered; human review pending by design) |

## Hermes Review Results
- Reviewer of Record: human (Hermes only flags; it does not decide)
- Checks:
  - no Need defined / approved / rejected
  - no Task auto-assigned to an agent
  - all agents carry refusal flags; no real connection / execution
  - evidence candidates: not fact, not proof, no need definition
  - no auto-approval / auto-execution / auto-needification
- Passed: **True**

## Invariant Violations
- (none)

## Dan-Go Byte-Identical Check
- Dan-Go content hash (globe, bridge/gitsea, bridge/sutable): `b750c6e8794443a0`
- This layer writes ONLY under `bridge/agent_commons/` (store.py guard refuses
  any write to `globe/`, `bridge/gitsea/`, `bridge/sutable/`, `bridge/mujin/`).
- Authoritative proof: before/after hash comparison during verification.

## Mujin Non-Mutation Check
- Mujin content hash (bridge/mujin): `dc3d7d765398b670`
- Mujin `voice_records.jsonl` is opened read-only by the Voice Reader; this
  layer never writes to `bridge/mujin/`.

## Observation Candidates
- `obs-001` ← voice-001 · type=`direct_voice` · need_owner_present=True · bottleneck=['housing']
- `obs-002` ← voice-002 · type=`public_call` · need_owner_present=False · bottleneck=[]
- `obs-003` ← voice-003 · type=`gateway_voice` · need_owner_present=False · bottleneck=['housing']
- `obs-004` ← voice-004 · type=`gateway_voice` · need_owner_present=False · bottleneck=[]
- `obs-005` ← voice-005 · type=`gateway_voice` · need_owner_present=False · bottleneck=[]
- `obs-006` ← voice-006 · type=`gateway_voice` · need_owner_present=False · bottleneck=['employment', 'funding', 'legal', 'translation', 'volunteer']

## Task Candidates (work candidates, never assignments)
- `task-001` ← obs-001 · `gateway_discovery` · assigned_agent=None
- `task-002` ← obs-001 · `solution_discovery` · assigned_agent=None
- `task-003` ← obs-001 · `counter_argument` · assigned_agent=None
- `task-004` ← obs-002 · `research` · assigned_agent=None
- `task-005` ← obs-002 · `similar_case_search` · assigned_agent=None
- `task-006` ← obs-002 · `counter_argument` · assigned_agent=None
- `task-007` ← obs-003 · `gateway_discovery` · assigned_agent=None
- `task-008` ← obs-003 · `solution_discovery` · assigned_agent=None
- `task-009` ← obs-003 · `similar_case_search` · assigned_agent=None
- `task-010` ← obs-003 · `counter_argument` · assigned_agent=None
- `task-011` ← obs-004 · `gateway_discovery` · assigned_agent=None
- `task-012` ← obs-004 · `similar_case_search` · assigned_agent=None
- `task-013` ← obs-004 · `counter_argument` · assigned_agent=None
- `task-014` ← obs-005 · `gateway_discovery` · assigned_agent=None
- `task-015` ← obs-005 · `similar_case_search` · assigned_agent=None
- `task-016` ← obs-005 · `counter_argument` · assigned_agent=None
- `task-017` ← obs-006 · `solution_discovery` · assigned_agent=None
- `task-018` ← obs-006 · `research` · assigned_agent=None
- `task-019` ← obs-006 · `funding_research` · assigned_agent=None
- `task-020` ← obs-006 · `similar_case_search` · assigned_agent=None
- `task-021` ← obs-006 · `legal_research` · assigned_agent=None
- `task-022` ← obs-006 · `translation` · assigned_agent=None
- `task-023` ← obs-006 · `cooperation_discovery` · assigned_agent=None
- `task-024` ← obs-006 · `gateway_discovery` · assigned_agent=None
- `task-025` ← obs-006 · `counter_argument` · assigned_agent=None

## Agent Registry (registration only — no real connection, no execution)
- `agent-001` Hermes (observer) · internal_observer (this layer)
- `agent-002` Nookplot (external_agent) · registry_only — real connection prohibited this phase
- `agent-003` A0x (external_agent) · registry_only — real connection prohibited this phase
- `agent-004` Codex (code_agent) · registry_only — execution disabled this phase
- `agent-005` OpenClaw (agent) · registry_only — execution disabled this phase
- `agent-006` Human (human_participant) · humans decide (review of record happens in the Mujin layer, not here); within Agent Commons no auto-action
- `agent-007` Other (unspecified) · registry_only

---

*Hermes is an Observer. It does not define a Need, select a Gateway, assign an
agent, or decide anything. AI proposes; humans decide. Reach Gap is unresolved;
this layer does not claim to resolve it.*
