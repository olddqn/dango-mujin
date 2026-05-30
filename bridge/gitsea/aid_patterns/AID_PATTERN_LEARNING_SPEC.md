# Aid Pattern Learning Spec — Dan-Go / GITSEA (Phase 20)

> **"Pattern is not prediction."**
> **"Learning is not prescription."**
> **"Recurrence is not ranking."**

## Overview

Phase 20 introduces the Aid Pattern Learning Layer — an advisory layer
that observes recurring care need patterns across the full Phase 17–19
care chain. Dan-Go records what has happened more than once. It does not
predict what will happen next. It does not prescribe what to do. It does
not rank which commons or which needs are most deserving.

## The Phase Chain

```
Phase 17: Mutual Aid Routing   → aid_route_recorded: true
Phase 18: Relief Case Memory   → care_history_complete: true
Phase 19: Care Loop Reopen     → care_loop_complete: true
Phase 20: Aid Pattern Learning → pattern_learning_only: true
```

Phase 20 extends the care chain. A pattern memory links the full
observable history of a recurring care situation across Phases 17–20.

## Runtime Modules

| Module | Purpose |
|--------|---------|
| `aid_pattern_registry.py` | Record recurring aid patterns with observed counts |
| `recurrence_snapshot.py` | Snapshot individual recurrence observations without ranking |
| `pattern_memory_builder.py` | Build cross-phase pattern memory from care loop / relief / route records |
| `aid_pattern_report.py` | 4-section advisory report explaining pattern ≠ prediction |

## Pattern Types

| Type | Description |
|------|-------------|
| `recurring_food_support` | Food support need observed recurring across care records |
| `ongoing_displacement_relief` | Displacement relief need observed as ongoing |
| `unresolved_tenancy_pattern` | Housing advocacy cases without tenancy resolution |
| `pending_skill_exchange` | Skill exchange session deferred or pending |
| `supply_resupply_pattern` | Supply needs observed recurring |
| `shelter_extension_pattern` | Extended shelter or housing need observed recurring |
| `wellbeing_followup_pattern` | Recurring wellbeing check needs observed |
| `advocacy_continuation_pattern` | Advocacy or negotiation needing continuation |

## Recurrence Types

| Type | Description |
|------|-------------|
| `food_need_reappeared` | Food need observed again after prior response |
| `displacement_relief_ongoing` | Displacement relief need continuing |
| `tenancy_unresolved_continued` | Tenancy situation observed as unresolved across time |
| `skill_exchange_deferred` | Skill exchange session deferred to a later date |
| `supply_need_recurring` | Supply need observed recurring |
| `shelter_need_persisting` | Shelter need persisting beyond initial response |

## Aid Pattern Entry Structure

```json
{
  "record_type":              "aid_pattern",
  "pattern_id":               "aid-pattern-001",
  "commons_id":               "jammy-house-001",
  "pattern_type":             "recurring_food_support",
  "observed_count":           3,
  "source_loops":             ["care-loop-001", "care-loop-003"],
  "source_cases":             ["relief-case-001"],
  "source_routes":            ["aid-route-001"],
  "authority":                "none",
  "pattern_is_prediction":    false,
  "learning_is_prescription": false,
  "recurrence_is_ranking":    false,
  "pattern_ranks_commons":    false,
  "pattern_compels_response": false,
  "advisory":                 true,
  "pattern_learning_only":    true,
  "contestable":              true,
  "reopenable":               true
}
```

## Recurrence Entry Structure

```json
{
  "record_type":                        "recurrence_observation",
  "recurrence_id":                      "recurrence-001",
  "pattern_id":                         "aid-pattern-001",
  "commons_id":                         "jammy-house-001",
  "recurrence_type":                    "food_need_reappeared",
  "count":                              3,
  "recurrence_is_ranking":              false,
  "ranks_suffering":                    false,
  "recurrence_judges_prior_response":   false,
  "recurrence_demands_new_response":    false,
  "recurrence_certifies_failure":       false,
  "authority":                          "none",
  "advisory":                           true,
  "pattern_learning_only":              true
}
```

## Pattern Memory Entry Structure

```json
{
  "record_type":                 "pattern_memory",
  "pattern_memory_id":           "pattern-memory-001",
  "pattern_id":                  "aid-pattern-001",
  "commons_id":                  "jammy-house-001",
  "source_loops":                ["care-loop-001", "care-loop-003"],
  "source_cases":                ["relief-case-001"],
  "source_routes":               ["aid-route-001"],
  "source_recurrences":          ["recurrence-001"],
  "memory_status":               "recorded",
  "learning_is_prescription":    false,
  "memory_prescribes_response":  false,
  "memory_certifies_resolution": false,
  "memory_compels_new_aid":      false,
  "memory_judges_participants":  false,
  "authority":                   "none",
  "advisory":                    true,
  "pattern_learning_only":       true,
  "reopenable":                  true
}
```

## Connection to Jammy House and D.R.A.

**Jammy House patterns**: Recurring food support and unresolved tenancy.
Both grounded in Phase 17–19 care records. The pattern memory does not
judge whether the community responded adequately. It records that the
situations recurred. Jammy House retains full authority over how it
responds to this information.

**D.R.A. patterns**: Ongoing displacement relief. Four observations of
displacement-related need across supply coordination and shelter hosting.
The pattern record does not certify that the relief was insufficient.
It records that the displacement is ongoing. D.R.A. retains full
authority over how it responds.

Dan-Go observes both patterns. The communities decide.

## Invariants

All records in this layer carry:

```json
{
  "authority":                  "none",
  "execution_allowed":          false,
  "moves_money":                false,
  "credit_issued":              false,
  "hard_enforcement":           false,
  "advisory":                   true,
  "pattern_learning_only":      true,
  "append_only":                true,
  "contestable":                true,
  "reopenable":                 true,
  "pattern_is_prediction":      false,
  "learning_is_prescription":   false,
  "recurrence_is_ranking":      false,
  "pattern_ranks_commons":      false,
  "pattern_compels_response":   false
}
```

## Required Phrases

All spec documents and runtime modules in this layer must include:

1. `"Pattern is not prediction."`
2. `"Learning is not prescription."`
3. `"Recurrence is not ranking."`
