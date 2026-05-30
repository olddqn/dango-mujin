# Cooperation Commons Spec — Dan-Go / GITSEA (Phase 16)

> **"Community is not authority."**
> **"Commons is not ownership."**
> **"Participation is not control."**

## Overview

Phase 16 introduces the Cooperation Commons Layer — an advisory layer that
records cooperation not only between individuals, but within communities,
projects, houses, and shared initiatives.

Dan-Go now makes collective cooperation legible alongside individual
contribution. The commons layer is advisory only. No authority is claimed.
No ownership is implied. No governance is exercised.

## The Phase Chain

```
Phase 11: Contribution Candidate      → candidate_credit: true/false
Phase 12: External Credit Observation → external_credit: false
Phase 13: Reflection Memory           → reflection_recorded: true
Phase 14: Recognition Appeal          → appeal_recorded: true
Phase 15: Recognition Ledger          → recognition_history_complete: true
Phase 16: Cooperation Commons         → commons_recorded: true
```

Phase 16 sits alongside the Phase 11–15 individual contributor chain.
The commons layer records community-level cooperation that contextualises
and surrounds individual contribution.

## Registered Commons

| Commons ID | Name | Type |
|------------|------|------|
| `dango-001` | Dan-Go | project |
| `jammy-house-001` | Jammy House | house |
| `yacypherpunks-001` | YacypherPunks | community |
| `dra-001` | D.R.A. | initiative |

## Commons Types

| Type | Description |
|------|-------------|
| `community` | A shared community of participants with common interests |
| `project` | A cooperative software or creative project |
| `house` | A physical or virtual cooperative living/working space |
| `initiative` | A coordinated collective action or advocacy initiative |
| `network` | A loose network of cooperating individuals or groups |

## Membership Types

| Type | Description |
|------|-------------|
| `participant` | Voluntary participant in the commons |
| `contributor` | Active contributor to commons activities |
| `coordinator` | Coordinates commons activities without authority |
| `observer` | Observes and records commons activity |
| `correspondent` | External correspondent cooperating with the commons |

## Runtime Modules

| Module | Purpose |
|--------|---------|
| `commons_registry.py` | Create advisory commons records (one per community) |
| `commons_membership.py` | Record participation relationships |
| `commons_snapshot.py` | Aggregate commons activity with counts |
| `commons_report.py` | 5-section advisory report explaining commons principles |

## Commons Registry Entry Structure

```json
{
  "record_type":   "commons_registry_entry",
  "commons_id":    "jammy-house-001",
  "name":          "Jammy House",
  "commons_type":  "house",
  "active":        true,
  "founded":       "2025-03-01",
  "claim_ids":     ["housing-007"],
  "authority":     "none",
  "ownership":     false,
  "control":       false,
  "advisory":      true,
  "commons_only":  true,
  "append_only":   true,
  "contestable":   true,
  "reopenable":    true,
  "credit_issued": false,
  "moves_money":   false
}
```

## Commons Membership Entry Structure

```json
{
  "record_type":                 "commons_membership",
  "membership_id":               "membership-jammy-house-001-external-001",
  "commons_id":                  "jammy-house-001",
  "participant_id":              "external-001",
  "membership_type":             "contributor",
  "role":                        "reviewer",
  "membership_is_voluntary":     true,
  "membership_compels":          false,
  "membership_grants_authority": false,
  "authority":                   "none",
  "ownership":                   false,
  "control":                     false
}
```

## Why Commons Matter

Observable cooperation is valuable. When communities participate in
negotiation processes — as Jammy House does in housing claims, as D.R.A.
does in tenant advocacy — the community context is part of the historical
record. Making that context legible helps future observers understand not
just what individuals did, but within what collective structures they acted.

Dan-Go records this community context without claiming authority over it.

## Invariants

All records in this layer carry:

```json
{
  "authority":          "none",
  "ownership":          false,
  "control":            false,
  "execution_allowed":  false,
  "moves_money":        false,
  "credit_issued":      false,
  "hard_enforcement":   false,
  "advisory":           true,
  "commons_only":       true,
  "append_only":        true,
  "contestable":        true,
  "reopenable":         true,
  "membership_compels": false,
  "membership_grants_authority": false,
  "membership_is_voluntary":     true
}
```

## Required Phrases

All spec documents and runtime modules in this layer must include:

1. `"Community is not authority."`
2. `"Commons is not ownership."`
3. `"Participation is not control."`
