# Hermes Memory Report

- Generated: 2026-06-18T20:06:46.088030Z
- Layer: `bridge/agent_commons/memory/` (advisory only · authority none · AI proposes, human decides)
- Hermes records *what was learned*, not *what to do*. Pattern is hypothesis, not fact.

## Counts
| metric | value |
|---|---|
| Observation Count | 6 |
| Reflection Count | 6 |
| Learning Count | 4 |
| Pattern Count | 1 |
| Tentative Pattern Count | 1 |
| Human Reviewed Count | 0 (reflections are AI-generated; human review pending by design) |

## Invariant Violations
- (none)

## Reflections
- `refl-001` ← obs-001 (voice-001) · confidence=low · Voice voice-001 appears to be a direct first-person appeal; consent and safety must be confirmed by a human. Observed bottlenecks: housing.
- `refl-002` ← obs-002 (voice-002) · confidence=low · Public-call voice voice-002 has no clearly present first-person need owner; the need owner may be absent.
- `refl-003` ← obs-003 (voice-003) · confidence=low · Public voice voice-003 originated from a gateway/intermediary rather than a direct beneficiary; the need owner may be absent from the voice. Observed bottlenecks: housing.
- `refl-004` ← obs-004 (voice-004) · confidence=low · Public voice voice-004 originated from a gateway/intermediary rather than a direct beneficiary; the need owner may be absent from the voice.
- `refl-005` ← obs-005 (voice-005) · confidence=low · Public voice voice-005 originated from a gateway/intermediary rather than a direct beneficiary; the need owner may be absent from the voice.
- `refl-006` ← obs-006 (voice-006) · confidence=low · Public voice voice-006 originated from a gateway/intermediary rather than a direct beneficiary; the need owner may be absent from the voice. Observed bottlenecks: employment, funding, legal, translation, volunteer.

## Learnings (reusable, advisory — not authority)
- `learn-001` [direct_voice] evidence=1 · Some voices appear to be direct first-person appeals (consent review required).
- `learn-002` [gateway_voice] evidence=4 · Public voices may originate from a gateway/intermediary rather than a direct beneficiary.
- `learn-003` [need_owner_absent] evidence=5 · Need owner may be absent from a public voice.
- `learn-004` [public_call] evidence=1 · Public-call voices may lack a clearly present need owner.

## Pattern Candidates (tentative hypotheses — not facts)
- `pat-001` (tentative) evidence=5 · Public voices tend to originate from intermediaries; the need owner is often absent from the voice.

## voice-006 chain
`voice-006` → `obs-006` → `refl-006` → `learn-002` → `pat-001`

---

*A Pattern is not a fact and not a policy; it requires human review. Hermes is
an Observer, not a Planner / Coordinator / Policy Maker. Reach Gap is
unresolved; this layer does not claim to resolve it.*
