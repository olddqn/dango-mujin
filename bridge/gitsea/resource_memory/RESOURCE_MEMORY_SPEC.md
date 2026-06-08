# Resource Memory Layer (Phase 51)

> **Resource is not allocation.**
> **Possession is not obligation.**
> **Availability is not transfer.**

Dan-Go / GITSEA Bridge · authority: none · advisory only · stdlib only

---

## Phase Numbering Note

This layer is **Phase 51**, following Phase 50 (Commons Capacity Memory).
The Dan-Go project uses a single unified phase counter:

- Phases 10–21 — GITSEA cooperation chain (treasury → credit → ledger →
  commons → mutual aid → relief → care loop → aid patterns → need forecast)
- Phases 22–49 — Globe governance / deliberation track
- Phase 50 — Commons Capacity Memory Layer (observable latent ability)
- **Phase 51 — Resource Memory Layer** (observable resources)

---

## Purpose

The cooperation chain now records:

| Question | Layer |
|---|---|
| What is needed? | Phase 17 — Mutual Aid Routing |
| What was given? | Phase 18 — Relief Case Memory |
| What recurred? | Phase 20 — Aid Pattern Learning |
| What may be needed again? | Phase 21 — Need Forecast Memory |
| What ability exists? | Phase 50 — Commons Capacity Memory |
| **What resources exist?** | **Phase 51 — Resource Memory** |

Phase 51 answers: *What resources actually exist? What resources are
observable? What resources may be available?* — by recording **observable
possession**, distinct from any active offer, any latent capacity, or any
allocation.

---

## Relationship to Existing Layers (Non-Duplication)

Resource-adjacent data exists in earlier layers. Phase 51 records a
**different** thing:

### vs Phase 17 — Mutual Aid Routing (`aid_offer_registry.py`)
Phase 17 records **active offers**: "I offer to help with X." An offer
is a *speech act* in response to a context.
Phase 51 records **observed possession**: "this commons has X." A
resource exists in the world before and independent of any offer.

### vs Phase 21 — Need Forecast Memory (`preparedness_hint_snapshot.py`)
Phase 21 records *what may be needed*. Phase 51 records *what is held*.
A forecast and a resource are opposite sides of the same legibility act:
forecast points forward, resource points to the present.

### vs Phase 50 — Commons Capacity Memory (`capacity_registry.py`)
Phase 50 records **latent ability** ("this commons has been observed to
*be able* to prepare meals"). Phase 51 records **observable possession**
("this commons holds a kitchen with a stove"). Capacity is what the
commons *can do*; resource is what the commons *has*. They overlap
sometimes (a kitchen enables meal capacity) but are not the same: a
commons can have capacity without resources (skill but no equipment)
and resources without capacity (equipment but no skilled participants).

> **Layer distinctions:**
> Phase 17 = active offer  Phase 21 = preparedness hint
> Phase 50 = latent capacity  Phase 51 = observable resource

`resource_memory_builder.py` links Phase 16 (commons) + Phase 21
(forecast) + Phase 50 (capacity) + Phase 51 (resource) into one
juxtaposition — for human reading only. It performs **no matching, no
allocation, no transfer**.

---

## Records

### Resource record (`resource_registry.py`)

```json
{
  "resource_id": "resource-001",
  "commons_id": "jammy-house-001",
  "resource_type": "vacant_room",
  "quantity": 2,
  "unit": "rooms",
  "observability": "directly_observed",
  "resource_is_allocation": false,
  "possession_creates_obligation": false,
  "availability_transfers_ownership": false,
  "authority": "none"
}
```

`observability` is an **observability provenance label**, never a claim
about who controls or may use the resource:
`directly_observed`, `self_reported`, `inferred`, `documented`, `unknown`.

### Snapshot (`resource_snapshot.py`)
Aggregates resources by type / observability / commons. It does **not**
total resources into a pool and does **not** rank commons.

### Resource memory (`resource_memory_builder.py`)
Per commons, juxtaposes observed resources with anticipated needs and
observed capacities. The juxtaposition is advisory; Dan-Go never matches
a resource to a need, assigns a helper, or transfers ownership.

### Report (`resource_report.py`)
Human-readable text explaining observed resources and explicitly stating
what the report does **not** mean (no allocation, no obligation, no
transfer, no command).

---

## Observability provenance

"Observability" here means **how Dan-Go came to know** the resource exists.
A `directly_observed` resource was counted by a participant; a
`self_reported` one was reported by the holder; a `documented` one was
recorded in a commons roster; an `inferred` one is suggested by activity
records.

The provenance label exists to keep the legibility *honest*: someone
reviewing a resource record should be able to see how strong the
observation is, and act with appropriate caution.

---

## Invariants

```yaml
authority: none
execution_allowed: false
moves_money: false
credit_issued: false
hard_enforcement: false
advisory: true
resource_memory_only: true
append_only: true
contestable: true
reopenable: true
resource_is_allocation: false
possession_creates_obligation: false
availability_transfers_ownership: false
```

---

## What This Layer Does NOT Do

- Does not allocate any resource to any need
- Does not create obligation from observed possession
- Does not transfer ownership of any resource
- Does not command anyone to give a resource
- Does not match resources to helpers or to needs
- Does not rank commons by resource count
- Does not move money, issue credit, or execute anything
- Does not call any network or hold any key

Human review is required before any real-world action.
