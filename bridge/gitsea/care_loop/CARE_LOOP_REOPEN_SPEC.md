# Care Loop Reopen Spec — Dan-Go / GITSEA (Phase 19)

> **"Reopen is not failure."**
> **"Follow-up is not blame."**
> **"Care loop is not obligation."**

## Overview

Phase 19 introduces the Care Loop Reopen Layer — an advisory layer that
records relief cases that may need follow-up, reconsideration, or renewed
assistance after the Phase 18 initial care memory was built.

Dan-Go does not judge failure. Dan-Go does not blame participants. Dan-Go
does not compel new aid. Dan-Go only records reopenable care loops.

## The Phase Chain

```
Phase 17: Mutual Aid Routing   → aid_route_recorded: true
Phase 18: Relief Case Memory   → care_history_complete: true
Phase 19: Care Loop Reopen     → care_loop_complete: true
```

Phase 19 extends the care chain. A care loop is the complete cross-phase
record from route suggestion through reopen — the full observable history
of one care situation.

## Runtime Modules

| Module | Purpose |
|--------|---------|
| `care_reopen_registry.py` | Record cases that need reopening or follow-up |
| `followup_need_snapshot.py` | Record follow-up needs without blame |
| `care_loop_builder.py` | Build care loop from Phase 17–19 records |
| `care_loop_report.py` | 6-section advisory report explaining why reopen ≠ failure |

## Reopen Reasons

| Reason | Description |
|--------|-------------|
| `partial_outcome_needs_followup` | Outcome was partial; situation may need further attention |
| `need_recurred` | The original need has recurred after initial assistance |
| `new_information_available` | New information changes the picture of what occurred |
| `participant_requested_reopen` | A participant in the care exchange requested reopening |
| `outcome_contested` | The recorded outcome has been contested |
| `situation_changed` | Circumstances have changed since the case was closed |
| `case_was_pending` | Case was pending; now has new observable activity |
| `housing_situation_unresolved` | Housing situation remained unresolved after initial response |
| `displacement_ongoing` | Displacement is ongoing; relief was temporary |
| `general_followup` | General follow-up identified; no specific reopen trigger |

## Follow-Up Need Types

| Type | Description |
|------|-------------|
| `second_contact_needed` | A second point of contact may be useful |
| `ongoing_food_coordination` | Food support may need to be coordinated on a recurring basis |
| `housing_status_check` | A check on current housing status may be warranted |
| `supply_resupply_needed` | Supplies may need to be replenished |
| `shelter_extension_needed` | Extended shelter or longer-term housing may be needed |
| `displacement_monitoring` | Ongoing monitoring of displacement situation may be useful |
| `skill_session_rescheduled` | Skill exchange session may need to be rescheduled |
| `wellbeing_check` | A general wellbeing check may be warranted |
| `advocacy_continuation` | Advocacy or negotiation may need to continue |
| `general_followup_needed` | General follow-up identified without specific type |

## Care Loop Event Sequence

| Event | Phase | Description |
|-------|-------|-------------|
| `route_suggested` | 17 | Aid route suggested |
| `relief_case_recorded` | 18 | Relief case recorded |
| `outcome_observed` | 18 | Outcome observed |
| `care_memory_built` | 18 | Care memory built |
| `followup_need_observed` | 19 | Follow-up need observed |
| `reopen_requested` | 19 | Reopen requested |
| `reopen_acknowledged` | 19 | Reopen acknowledged |
| `reopen_active` | 19 | Reopen active |
| `reopen_resolved` | 19 | Reopen resolved |

## Care Reopen Entry Structure

```json
{
  "record_type":                  "care_reopen",
  "reopen_id":                    "care-reopen-001",
  "relief_case_id":               "relief-case-002",
  "route_id":                     "aid-route-002",
  "commons_id":                   "jammy-house-001",
  "reopen_reason":                "partial_outcome_needs_followup",
  "reopen_status":                "requested",
  "authority":                    "none",
  "reopen_is_failure":            false,
  "followup_is_blame":            false,
  "reopen_judges_prior_response": false,
  "reopen_blames_participants":   false,
  "reopen_compels_new_aid":       false,
  "reopen_certifies_failure":     false,
  "care_loop_creates_obligation": false,
  "advisory":                     true,
  "care_loop_only":               true,
  "reopenable":                   true
}
```

## Care Loop Entry Structure

```json
{
  "record_type":              "care_loop",
  "care_loop_id":             "care-loop-001",
  "relief_case_id":           "relief-case-002",
  "route_id":                 "aid-route-002",
  "loop_status":              "open",
  "events": [
    "route_suggested",
    "relief_case_recorded",
    "outcome_observed",
    "care_memory_built",
    "followup_need_observed",
    "reopen_requested"
  ],
  "loop_complete":            true,
  "authority":                "none",
  "reopen_is_failure":        false,
  "care_loop_creates_obligation": false,
  "loop_judges_participants": false,
  "loop_compels_new_aid":     false,
  "loop_certifies_resolution": false,
  "contestable":              true,
  "reopenable":               true
}
```

## Connection to Jammy House and Refugee Relief

Jammy House care loops: recurring food needs and unresolved tenancy
situations. One provision is not a permanent solution in a cooperative
housing context. The care loop makes recurring need visible without
treating it as a system failure.

D.R.A. care loops: ongoing displacement. The original supply coordination
and shelter hosting were temporary responses to continuing displacement.
The care loop records the continuity of the situation — not a failure of
the initial response.

Dan-Go observes both patterns. The communities respond as they choose.

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
  "care_loop_only":             true,
  "append_only":                true,
  "contestable":                true,
  "reopenable":                 true,
  "reopen_is_failure":          false,
  "followup_is_blame":          false,
  "care_loop_creates_obligation": false
}
```

## Required Phrases

All spec documents and runtime modules in this layer must include:

1. `"Reopen is not failure."`
2. `"Follow-up is not blame."`
3. `"Care loop is not obligation."`
