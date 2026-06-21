# Edge Runtime Report (shared — Route A + Route B)

- Generated: 2026-06-21T07:02:24.201139Z
- Architecture: `Voice → Observed Edge → Edge Runtime ├─ Route A (Findability)  └─ Route B (Gateway Support)`
- AI proposes; humans decide. Authority none. Person Domain sealed across both routes.

## Shared edge layer
| store | records |
|---|---|
| observed_edges | 0 |
| edge_memory (episodes) | 1 |

## Route A — Findability
| store | records |
|---|---|
| findability_surfaces | 1 |
| consent_opportunities | 1 |
| state_reconciliations | 1 |

## Route B — Gateway Support
| store | records |
|---|---|
| verified_bottlenecks | 1 |
| support_candidates | 3 |
| approval_records | 1 |
| gateway_consents | 1 |
| support_executions | 1 |
| support_feedback | 1 |
| ttfr_g_records | 1 |
| withdrawal_records | 0 |

## Shared edge-memory learning (type-level, non-KPI, no actor)
- {'by_episode_kind': {'a': 1}, 'by_outcome_type': {'relief_held': 1}, 'by_route': {'gateway_support': 1}, 'episode_count': 1, 'not_a_kpi': True, 'no_maximization': True, 'no_ranking': True, 'not_person_relief_accounting': True}

## Audit
| layer | result | static violations | dynamic checks |
|---|---|---|---|
| edge layer | PASS | 0 | — |
| Route A (findability) | PASS | 0 | 5 |
| Route B (gateway_support) | PASS | 0 | 17 |
| **overall** | **PASS** | | |

## Shared guarantees (both routes)
Person Domain sealed · no ranking · no recommendation · no selection · no
reach-gap estimation · no Saiyan Scouter · append-only · single shared edge
records & edge memory (no duplication). Route B adds Resource-Acceptance-only,
two-key execution, TTFR-G ⟂ TTFR-P; Route A adds observation-only, owner→Mujin,
no outreach / growth / marketing / pre-exposure. Neither implements Person Relief.

---

*0 records across all layers is the valid empty-safe state: the runtime does not
fabricate. Findability opens consent opportunity; Gateway Support advances TTFR-G
only. Neither resolves the (person) Reach Gap.*
