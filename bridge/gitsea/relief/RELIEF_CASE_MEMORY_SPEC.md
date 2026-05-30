# Relief Case Memory Spec — Dan-Go / GITSEA (Phase 18)

> **"Relief is not proof."**
> **"Outcome is not judgment."**
> **"Care memory is not control."**

## Overview

Phase 18 introduces the Relief Case Memory Layer — an advisory layer that
records what happened after a mutual aid route (Phase 17) was suggested.

Dan-Go does not judge outcomes. Dan-Go does not rank suffering. Dan-Go does
not certify rescue. Dan-Go only records observable relief case memory and
builds care history from the Phase 17–18 record chain.

## The Phase Chain

```
Phase 16: Cooperation Commons  → commons_recorded: true
Phase 17: Mutual Aid Routing   → aid_route_recorded: true
Phase 18: Relief Case Memory   → care_history_complete: true
```

Phase 18 closes the observable care chain. A complete care record covers:
route suggestion (Phase 17) → case observation (Phase 18) → outcome
observation (Phase 18) → care memory (Phase 18).

## Runtime Modules

| Module | Purpose |
|--------|---------|
| `relief_case_registry.py` | Record relief cases linked to Phase 17 routes |
| `relief_outcome_snapshot.py` | Record observable outcomes without judging them |
| `care_memory_builder.py` | Build care memory from route + case + outcome records |
| `relief_memory_report.py` | 6-section advisory report explaining why memory ≠ proof/judgment/control |

## Case Types

| Type | Description |
|------|-------------|
| `food_support_followup` | Follow-up after a food support route |
| `housing_support_followup` | Follow-up after a housing support route |
| `refugee_relief_followup` | Follow-up after a refugee relief route |
| `skill_exchange_followup` | Follow-up after a skill exchange route |
| `shelter_followup` | Follow-up after a shelter hosting route |
| `supply_followup` | Follow-up after a supply sharing route |
| `general_followup` | General follow-up after an aid route |

## Case Status Values

| Status | Meaning |
|--------|---------|
| `observed` | Case outcome has been observed and recorded |
| `pending` | Route was suggested; outcome not yet observed |
| `partial` | Partial assistance was observed |
| `completed` | Full assistance was observed to have occurred |
| `unresolved` | Route was suggested; no outcome observed |
| `reopened` | Case was reopened after initial recording |
| `withdrawn` | Case observation was withdrawn by the recorder |

## Observed Outcome Types

| Outcome | Description |
|---------|-------------|
| `meal_was_offered` | A meal or food item was observed to have been offered |
| `meal_was_received` | A meal or food item was observed to have been received |
| `shelter_was_offered` | Temporary shelter was observed to have been offered |
| `shelter_was_accepted` | Temporary shelter was observed to have been accepted |
| `housing_contact_made` | Contact for housing advocacy was observed to have occurred |
| `negotiation_initiated` | A negotiation process was observed to have been initiated |
| `supplies_reached_household` | Supplies were observed to have reached the household |
| `skill_session_scheduled` | A skill exchange session was observed to have been scheduled |
| `route_not_taken` | Route was suggested; no uptake was observed |
| `partial_assistance` | Partial assistance was observed without full resolution |
| `outcome_unknown` | Route outcome is not yet observable |

## Relief Case Entry Structure

```json
{
  "record_type":           "relief_case",
  "relief_case_id":        "relief-case-001",
  "route_id":              "aid-route-001",
  "commons_id":            "jammy-house-001",
  "case_type":             "food_support_followup",
  "case_status":           "observed",
  "authority":             "none",
  "relief_is_proof":       false,
  "outcome_is_judgment":   false,
  "care_memory_controls":  false,
  "certifies_rescue":      false,
  "certifies_success":     false,
  "ranks_suffering":       false,
  "case_creates_debt":     false,
  "advisory":              true,
  "relief_memory_only":    true,
  "reopenable":            true
}
```

## Care Memory Entry Structure

```json
{
  "record_type":                "care_memory",
  "care_memory_id":             "care-memory-001",
  "relief_case_id":             "relief-case-001",
  "route_id":                   "aid-route-001",
  "snapshot_id":                "outcome-snap-001",
  "commons_id":                 "jammy-house-001",
  "memory_status":              "recorded",
  "care_history_complete":      true,
  "authority":                  "none",
  "care_memory_controls":       false,
  "memory_creates_obligation":  false,
  "memory_certifies_outcome":   false,
  "memory_ranks_suffering":     false,
  "advisory":                   true,
  "reopenable":                 true
}
```

## Connection to Jammy House and Refugee Relief

Jammy House relief cases cover food support and housing support follow-ups —
the practical care that flows from cooperative living and tenant advocacy.
D.R.A. relief cases cover refugee relief and shelter follow-ups — the care
that flows from housing insecurity and displacement advocacy.

Care memory for refugee relief is particularly sensitive. Dan-Go records
what was observable without creating a surveillance record. The record
exists so that the cooperative care history is legible to the community,
not so that displaced persons can be tracked or their vulnerability quantified.

`care_memory_controls: false` is the boundary that preserves this.

## Invariants

All records in this layer carry:

```json
{
  "authority":            "none",
  "execution_allowed":    false,
  "moves_money":          false,
  "credit_issued":        false,
  "hard_enforcement":     false,
  "advisory":             true,
  "relief_memory_only":   true,
  "append_only":          true,
  "contestable":          true,
  "reopenable":           true,
  "relief_is_proof":      false,
  "outcome_is_judgment":  false,
  "care_memory_controls": false
}
```

## Required Phrases

All spec documents and runtime modules in this layer must include:

1. `"Relief is not proof."`
2. `"Outcome is not judgment."`
3. `"Care memory is not control."`
