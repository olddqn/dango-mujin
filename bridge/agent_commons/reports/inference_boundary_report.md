# Inference Boundary Report

- Generated: 2026-06-19T10:18:42.891300Z
- Layer: `bridge/agent_commons/memory/` (advisory only · authority none · AI proposes, human decides)
- Hermes is an **Inference Boundary Observer**: it records where inference began
  ("from here on, this is a guess"). It does not define / approve / reject a Need.
- Source of the inference: the human review (`docs/NEED_DEFINITION_REVIEW.md`).
  Hermes records the boundary; it invents no inference.

## Counts
| metric | value |
|---|---|
| Boundary Count | 5 |
| Direct Observation Count | 2 |
| Inference Count | 2 |
| Speculation Count | 1 |
| Need Owner Absent Count | 3 |
| Gateway Need Count | 2 |
| Individual Need Count | 3 |
| Boundary Requiring Human Review | 3 |

## Scouter Risk Breakdown
- high: 2
- medium: 1
- none: 2

## Invariant Violations
- (none)

## All Boundaries
| boundary | candidate | type | owner_present | gateway | individual | distance | risk | needs_review |
|---|---|---|---|---|---|---|---|---|
| `ib-001` | funding | direct_observation | True | True | False | 0 (gateway resource need, stated) | none | False |
| `ib-002` | volunteer | direct_observation | True | True | False | 0 (gateway resource need, stated) | none | False |
| `ib-003` | translation | inference | False | False | True | 2-layer (behind gap-1, individual) | medium | True |
| `ib-004` | legal | inference | False | False | True | 2-layer (behind gap-1, individual) | high | True |
| `ib-005` | employment | speculation | False | False | True | 2-layer (behind gap-1, individual) | high | True |

## voice-006 Boundary Analysis
- `funding` [direct_observation] — last direct obs: "JAR public appeal: explicit donation solicitation (stated)" → first inference: "— (none; direct)" (risk=none)
- `volunteer` [direct_observation] — last direct obs: "JAR public appeal: explicit volunteer solicitation (stated)" → first inference: "— (none; direct)" (risk=none)
- `translation` [inference] — last direct obs: "JAR activity description: language support" → first inference: "refugees may need translation" (risk=medium)
- `legal` [inference] — last direct obs: "JAR activity description: legal support" → first inference: "refugees may need legal support" (risk=high)
- `employment` [speculation] — last direct obs: "JAR activity description: employment support" → first inference: "refugees may need employment support, and this may be the current bottleneck" (risk=high)

> The inference boundary for voice-006 falls between B (volunteer, direct) and
> C (translation, inference): direct observation ends at JAR's stated resource
> needs; inference begins when JAR's activity areas are read as individual
> needs. Scouter risk appears exactly at that line.

---

*Hermes records "from here on, this is a guess." It defines no Need, selects no
Gateway, generates no Task, allocates no resources. Reach Gap is unresolved;
this layer does not claim to resolve it.*
