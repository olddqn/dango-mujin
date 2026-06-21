# Decision Boundary Report

- Generated: 2026-06-19T17:01:51.511631Z
- Layer: `bridge/agent_commons/` (advisory only · authority none · AI proposes, human decides)
- H-6 operationalises N-1.7: Hermes records WHERE a candidate became a decision
  (selection / allocation / execution). It never makes, approves, or rejects a
  decision. Detection is negation-aware (anti-decision disclaimers are not
  decisions).

## Counts
| metric | value |
|---|---|
| Decision Boundary Count | 17 |
| Decision Detected (fired) | 0 |
| candidate_only | 17 |
| selection | 0 |
| allocation | 0 |
| execution | 0 |
| Violation Count | 0 |
| Human Reviewed Count | 0 (AI-generated; human review pending by design) |

## Interpretation
All source records resolve to `candidate_only`: **no decision has entered Hermes's memory.** Hermes can answer 'where did this become a decision?' — the answer is: nowhere. That is memory, not governance.

## Violations
- (none)

## Boundaries
| boundary | source | type | candidate_count | decision_detected | marker |
|---|---|---|---|---|---|
| `db-001` | refl-001 | candidate_only | 0 | False | — |
| `db-002` | refl-002 | candidate_only | 0 | False | — |
| `db-003` | refl-003 | candidate_only | 0 | False | — |
| `db-004` | refl-004 | candidate_only | 0 | False | — |
| `db-005` | refl-005 | candidate_only | 0 | False | — |
| `db-006` | refl-006 | candidate_only | 0 | False | — |
| `db-007` | learn-001 | candidate_only | 0 | False | — |
| `db-008` | learn-002 | candidate_only | 0 | False | — |
| `db-009` | learn-003 | candidate_only | 0 | False | — |
| `db-010` | learn-004 | candidate_only | 0 | False | — |
| `db-011` | pat-001 | candidate_only | 0 | False | — |
| `db-012` | ib-001 | candidate_only | 0 | False | — |
| `db-013` | ib-002 | candidate_only | 0 | False | — |
| `db-014` | ib-003 | candidate_only | 0 | False | — |
| `db-015` | ib-004 | candidate_only | 0 | False | — |
| `db-016` | ib-005 | candidate_only | 0 | False | — |
| `db-017` | coop-pat-001 | candidate_only | 0 | False | — |

---

*Hermes records where a candidate became a decision. It chooses no candidate,
ranks none, recommends none, allocates nothing, executes nothing. The first
question (where did this become a decision?) is memory; the second (what should
we decide?) is governance. Hermes remains memory only. Reach Gap is unresolved;
this layer does not resolve it.*
