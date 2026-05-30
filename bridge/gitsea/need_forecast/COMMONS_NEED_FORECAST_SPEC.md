# Commons Need Forecast Memory Spec — Dan-Go / GITSEA (Phase 21)

> **"Forecast is not certainty."**
> **"Preparedness is not command."**
> **"Hint is not allocation."**

## Overview

Phase 21 introduces the Commons Need Forecast Memory Layer — an advisory
layer that records preparedness memories derived from recurring aid patterns
observed in Phase 20. Dan-Go does not predict need. Dan-Go does not command
preparation. Dan-Go does not allocate resources. Dan-Go only records
observable preparedness hints for commons, grounded in observed care history.

## The Phase Chain

```
Phase 17: Mutual Aid Routing      → aid_route_recorded: true
Phase 18: Relief Case Memory      → care_history_complete: true
Phase 19: Care Loop Reopen        → care_loop_complete: true
Phase 20: Aid Pattern Learning    → pattern_learning_only: true
Phase 21: Need Forecast Memory    → forecast_memory_only: true
```

Phase 21 extends the care chain. A forecast memory links a preparedness
hint to the full observable history of a recurring care situation across
Phases 17–20.

## Runtime Modules

| Module | Purpose |
|--------|---------|
| `need_forecast_registry.py` | Record forecast-like preparedness memories from Phase 20 patterns |
| `preparedness_hint_snapshot.py` | Record preparedness hints without command or allocation |
| `forecast_memory_builder.py` | Build forecast memory linking Phase 17–20 records |
| `need_forecast_report.py` | 5-section advisory report explaining forecast ≠ certainty |

## Confidence Labels

Every forecast record carries a `confidence_label` that communicates
how weakly grounded the forecast memory is:

| Label | Meaning |
|-------|---------|
| `single_observation` | Only one observation; not yet a pattern; weakest confidence |
| `two_observations` | Two observations; emerging pattern; low confidence |
| `observed_pattern_only` | Derived from observed recurrence; no causal analysis |
| `four_plus_observations` | Four or more observations; stronger signal; still not certainty |

No confidence label implies certainty. All confidence labels are
descriptions of observation count, not probability estimates.

## Forecast Types

| Type | Description |
|------|-------------|
| `recurring_food_support_possible` | Food support need observed recurring; may arise again |
| `ongoing_displacement_relief_possible` | Displacement relief need ongoing; may continue |
| `unresolved_tenancy_followup_possible` | Tenancy situation unresolved; further advocacy may be warranted |
| `skill_exchange_rescheduling_possible` | Skill exchange pending; rescheduling may be needed |
| `supply_resupply_possible` | Supply need observed; resupply may be warranted |
| `shelter_extension_possible` | Extended shelter need observed; continuation may be warranted |

## Preparedness Hint Types

| Type | Description |
|------|-------------|
| `meal_capacity_awareness` | Awareness of meal preparation capacity may be useful |
| `displacement_relief_readiness_awareness` | Awareness of supply and shelter capacity may be useful |
| `housing_advocacy_continuation_awareness` | Awareness of advocacy continuation options may be useful |
| `skill_exchange_rescheduling_awareness` | Awareness of rescheduling options may be useful |
| `supply_readiness_awareness` | Awareness of supply availability may be useful |
| `shelter_hosting_awareness` | Awareness of shelter hosting capacity may be useful |

## Need Forecast Entry Structure

```json
{
  "record_type":                 "need_forecast",
  "forecast_id":                 "need-forecast-001",
  "commons_id":                  "jammy-house-001",
  "source_pattern_id":           "aid-pattern-001",
  "forecast_type":               "recurring_food_support_possible",
  "observed_count":              3,
  "confidence_label":            "observed_pattern_only",
  "authority":                   "none",
  "forecast_is_certainty":       false,
  "preparedness_is_command":     false,
  "hint_is_allocation":          false,
  "forecast_allocates_resources": false,
  "forecast_compels_preparation": false,
  "advisory":                    true,
  "forecast_memory_only":        true,
  "contestable":                 true,
  "reopenable":                  true
}
```

## Preparedness Hint Entry Structure

```json
{
  "record_type":               "preparedness_hint",
  "hint_id":                   "preparedness-hint-001",
  "forecast_id":               "need-forecast-001",
  "commons_id":                "jammy-house-001",
  "hint_type":                 "meal_capacity_awareness",
  "preparedness_is_command":   false,
  "hint_is_allocation":        false,
  "hint_compels_action":       false,
  "hint_assigns_resources":    false,
  "hint_creates_obligation":   false,
  "voluntary":                 true,
  "authority":                 "none",
  "advisory":                  true
}
```

## Forecast Memory Entry Structure

```json
{
  "record_type":                 "forecast_memory",
  "forecast_memory_id":          "forecast-memory-001",
  "forecast_id":                 "need-forecast-001",
  "hint_id":                     "preparedness-hint-001",
  "commons_id":                  "jammy-house-001",
  "source_patterns":             ["aid-pattern-001"],
  "source_loops":                ["care-loop-001", "care-loop-003"],
  "memory_status":               "recorded",
  "forecast_is_certainty":       false,
  "memory_certifies_resolution": false,
  "memory_compels_preparation":  false,
  "memory_allocates_resources":  false,
  "memory_judges_commons":       false,
  "authority":                   "none",
  "advisory":                    true,
  "forecast_memory_only":        true,
  "reopenable":                  true
}
```

## Connection to Jammy House and D.R.A.

**Jammy House forecast memories**: Recurring food support and unresolved
tenancy. The food support forecast memory reflects three observed instances
in a cooperative housing context. The tenancy forecast memory reflects two
observed instances of unresolved housing advocacy. Neither forecast tells
Jammy House what to do. Both offer voluntary preparedness information.
Jammy House retains full authority over its response.

**D.R.A. forecast memories**: Ongoing displacement relief. Four observed
instances of displacement-related need across supply coordination and
shelter hosting. The forecast memory does not certify that D.R.A. must
maintain permanent capacity. It records that the pattern has been observed.
D.R.A. retains full authority over its response.

Dan-Go observes both. The communities decide.

## Invariants

All records in this layer carry:

```json
{
  "authority":                    "none",
  "execution_allowed":            false,
  "moves_money":                  false,
  "credit_issued":                false,
  "hard_enforcement":             false,
  "advisory":                     true,
  "forecast_memory_only":         true,
  "append_only":                  true,
  "contestable":                  true,
  "reopenable":                   true,
  "forecast_is_certainty":        false,
  "preparedness_is_command":      false,
  "hint_is_allocation":           false,
  "forecast_allocates_resources": false,
  "forecast_compels_preparation": false
}
```

## Required Phrases

All spec documents and runtime modules in this layer must include:

1. `"Forecast is not certainty."`
2. `"Preparedness is not command."`
3. `"Hint is not allocation."`
