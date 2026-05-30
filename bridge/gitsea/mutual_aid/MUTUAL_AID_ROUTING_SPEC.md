# Mutual Aid Routing Spec — Dan-Go / GITSEA (Phase 17)

> **"Need is not debt."**
> **"Help is not command."**
> **"Routing is not allocation."**

## Overview

Phase 17 introduces the Mutual Aid Routing Layer — an advisory layer that
records requests for help, voluntary offers of help, and possible cooperation
routes inside commons.

Dan-Go does not command assistance. Dan-Go does not allocate resources.
Dan-Go does not rank need. Dan-Go only records observable aid routes and
surfaces possible connections between requests and offers.

## The Phase Chain

```
Phase 11: Contribution Candidate      → candidate_credit: true/false
Phase 12: External Credit Observation → external_credit: false
Phase 13: Reflection Memory           → reflection_recorded: true
Phase 14: Recognition Appeal          → appeal_recorded: true
Phase 15: Recognition Ledger          → recognition_history_complete: true
Phase 16: Cooperation Commons         → commons_recorded: true
Phase 17: Mutual Aid Routing          → aid_route_recorded: true
```

Phase 17 extends the commons layer. Aid requests and offers occur within
registered commons (Jammy House, D.R.A., YacypherPunks). Routes connect
requests to offers across the commons membership.

## Why Mutual Aid Matters

Mutual aid is cooperation without obligation. It is the practice of
communities supporting each other through voluntary exchange — not
charity, not transaction, not debt. Housing cooperatives like Jammy
House, tenant advocacy networks like D.R.A., and communities responding
to refugee and displacement crises need a way to make their cooperative
activity legible without turning that legibility into surveillance,
allocation, or command.

Dan-Go makes mutual aid observable. Observability supports voluntary
coordination. Coordination supports community resilience. None of this
requires authority.

## Runtime Modules

| Module | Purpose |
|--------|---------|
| `aid_request_registry.py` | Record help requests inside commons |
| `aid_offer_registry.py` | Record voluntary offers of help |
| `aid_route_builder.py` | Build advisory routes between requests and offers |
| `mutual_aid_report.py` | 6-section report explaining why aid ≠ debt/command/allocation |

## Request Types

| Type | Description |
|------|-------------|
| `food_support` | Request for food or meal support |
| `shelter_support` | Request for temporary or emergency shelter |
| `transport_support` | Request for transport or travel assistance |
| `childcare_support` | Request for childcare or dependent care |
| `health_support` | Request for health-related assistance |
| `skill_exchange` | Request for skills, knowledge, or labour exchange |
| `emotional_support` | Request for emotional support or community care |
| `housing_support` | Request for housing assistance or negotiation support |
| `refugee_relief` | Request for relief resources for displaced persons |
| `general` | General request for assistance |

## Offer Types

| Type | Description |
|------|-------------|
| `meal_preparation` | Offer to prepare or share meals |
| `shelter_hosting` | Offer of temporary shelter or hosting |
| `transport_sharing` | Offer of transport or travel assistance |
| `childcare_sharing` | Offer of childcare or dependent care |
| `health_assistance` | Offer of health-related support |
| `skill_sharing` | Offer of skills, knowledge, or labour |
| `emotional_support` | Offer of emotional support or community care |
| `housing_advocacy` | Offer of housing advocacy or negotiation support |
| `supply_sharing` | Offer of physical supplies or resources |
| `coordination` | Offer to coordinate mutual aid activities |
| `general` | General offer of assistance |

## Route Status Values

| Status | Meaning |
|--------|---------|
| `possible` | Request and offer overlap; route is advisory and possible |
| `suggested` | Route has been surfaced to relevant participants |
| `accepted` | Participants have voluntarily agreed to connect |
| `declined` | One or both parties chose not to proceed; no obligation imposed |
| `completed` | Aid exchange completed voluntarily |
| `expired` | Route expired before connection was made |

## Aid Request Entry Structure

```json
{
  "record_type":         "aid_request",
  "request_id":          "aid-request-001",
  "commons_id":          "jammy-house-001",
  "requester_id":        "external-003",
  "request_type":        "food_support",
  "urgency":             "medium",
  "description":         "Household needs food support for the coming week.",
  "request_status":      "open",
  "authority":           "none",
  "need_creates_debt":   false,
  "request_is_command":  false,
  "requester_owes_help_received": false,
  "advisory":            true,
  "mutual_aid_only":     true,
  "moves_money":         false,
  "credit_issued":       false
}
```

## Aid Offer Entry Structure

```json
{
  "record_type":              "aid_offer",
  "offer_id":                 "aid-offer-001",
  "commons_id":               "jammy-house-001",
  "offerer_id":               "external-001",
  "offer_type":               "meal_preparation",
  "availability":             "weekly",
  "capacity":                 4,
  "offer_status":             "open",
  "voluntary":                true,
  "offer_is_command":         false,
  "control":                  false,
  "offer_creates_obligation": false,
  "offerer_may_withdraw":     true,
  "authority":                "none",
  "help_is_command":          false,
  "moves_money":              false
}
```

## Aid Route Entry Structure

```json
{
  "record_type":                "aid_route",
  "route_id":                   "aid-route-001",
  "request_id":                 "aid-request-001",
  "offer_id":                   "aid-offer-001",
  "commons_id":                 "jammy-house-001",
  "route_status":               "possible",
  "match_reasons":              ["type_overlap", "commons_shared"],
  "route_is_command":           false,
  "route_compels_exchange":     false,
  "route_allocates_capacity":   false,
  "participants_decide":        true,
  "route_may_be_declined":      true,
  "authority":                  "none",
  "routing_allocates_resources": false,
  "advisory":                   true
}
```

## Connection to Jammy House and Refugee Relief

Jammy House is a cooperative housing initiative. Its members participate
in mutual aid as a natural extension of cooperative living. Food support,
housing advocacy, and communal coordination are typical aid request and
offer types for this commons.

D.R.A. (Decentralised Renter Association) intersects with refugee relief
because housing insecurity and displacement are linked. The refugee_relief
request type and supply_sharing / shelter_hosting offer types are designed
to make cross-commons cooperation visible when a displaced person or
family needs routing to available help.

Dan-Go records these routes. The communities act on them voluntarily.

## Invariants

All records in this layer carry:

```json
{
  "authority":                   "none",
  "execution_allowed":           false,
  "moves_money":                 false,
  "credit_issued":               false,
  "hard_enforcement":            false,
  "advisory":                    true,
  "mutual_aid_only":             true,
  "append_only":                 true,
  "contestable":                 true,
  "reopenable":                  true,
  "need_creates_debt":           false,
  "help_is_command":             false,
  "routing_allocates_resources": false
}
```

## Required Phrases

All spec documents and runtime modules in this layer must include:

1. `"Need is not debt."`
2. `"Help is not command."`
3. `"Routing is not allocation."`
