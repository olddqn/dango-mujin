# Commons Capacity Memory Layer (Phase 50)

> **Capacity is not commitment.**
> **Ability is not obligation.**
> **Availability is not allocation.**

Dan-Go / GITSEA Bridge · authority: none · advisory only · stdlib only

---

## Phase Numbering Note

This layer is **Phase 50**, not Phase 22.

The Dan-Go project uses a single unified phase counter:

- Phases 10–21 — GITSEA cooperation chain (treasury → credit → ledger →
  commons → mutual aid → relief → care loop → aid patterns → need forecast)
- Phases 22–49 — Globe governance / deliberation track
- **Phase 50 — Commons Capacity Memory Layer** (this layer)

"Phase 22" is already occupied by the **Globe Foundation Layer**. The
Commons Capacity Memory Layer therefore takes the next free global number,
**50**, even though conceptually it continues the GITSEA cooperation chain
after Phase 21 (Need Forecast Memory).

---

## Purpose

The cooperation chain already records:

| Question | Layer |
|---|---|
| What is needed? | Mutual Aid Routing (Phase 17) |
| What was given? | Relief Case Memory (Phase 18) |
| What recurred? | Aid Pattern Learning (Phase 20) |
| What may be needed again? | Need Forecast Memory (Phase 21) |
| **What ability already exists?** | **Commons Capacity Memory (Phase 50)** |

Phase 50 answers: *Who can help? What can be offered? What capabilities
already exist?* — by recording **observable latent capacity**, distinct
from any active offer or any allocation.

---

## Relationship to Existing Layers (Non-Duplication)

Capacity-adjacent data already appears in two earlier layers. Phase 50
does **not** duplicate them — it records a different thing:

### vs Phase 17 — Mutual Aid Routing (`aid_offer_registry.py`)

Phase 17 records **active offers**: "I offer to help with X (capacity: N)."
An offer is a *speech act* by a participant in response to a context.

Phase 50 records **latent ability**: "this commons has been *observed to
be able* to do X" — whether or not anyone has offered. Capacity exists
before, and independent of, any offer.

> An aid offer is an action. A capacity is a standing observation.

### vs Phase 21 — Need Forecast Memory (`preparedness_hint_snapshot.py`)

Phase 21 hints reference "capacity awareness" as something that *may be
useful to know* given a forecast. Phase 50 is the actual **record** of
that capacity, which Phase 21's hints can now point to.

> Phase 21 says "knowing the meal capacity may help." Phase 50 records
> what the meal capacity actually is.

`capacity_memory_builder.py` links Phase 16 (commons) + Phase 21
(forecast) + Phase 50 (capacity) into one juxtaposition — for human
reading only. It performs **no matching and no allocation**.

---

## Records

### Capacity record (`capacity_registry.py`)

```json
{
  "capacity_id": "capacity-001",
  "commons_id": "jammy-house-001",
  "capacity_type": "meal_preparation",
  "participants": 4,
  "availability": "weekly",
  "capacity_is_commitment": false,
  "authority": "none"
}
```

`availability` is an **observed rhythm label**, never a schedule promise:
`weekly`, `monthly`, `occasional`, `on_request`, `seasonal`, `unknown`.

### Snapshot (`capacity_snapshot.py`)

Aggregates capacity by type / availability / commons. It does **not**
total ability into a budget and does **not** rank commons.

### Capacity memory (`capacity_memory_builder.py`)

Per commons, juxtaposes observed capacity with anticipated need
(forecast). The juxtaposition is advisory; Dan-Go never matches a
capacity to a need or assigns a helper.

### Report (`capacity_report.py`)

Human-readable text explaining observed capacity and explicitly stating
what the report does **not** mean (no commitment, no obligation, no
allocation).

---

## Commons Readiness

"Readiness" here means **legibility of ability**, not preparedness to act.
A commons with high observed capacity is not thereby obligated, ready, or
volunteering. Capacity legibility helps humans deliberate; it never
decides.

---

## Invariants

```yaml
authority: none
execution_allowed: false
moves_money: false
credit_issued: false
hard_enforcement: false
advisory: true
capacity_only: true
append_only: true
contestable: true
reopenable: true
capacity_is_commitment: false
ability_creates_obligation: false
availability_allocates_resources: false
```

---

## What This Layer Does NOT Do

- Does not commit any commons to anything
- Does not create obligation from observed ability
- Does not allocate capacity to needs
- Does not match helpers to requests
- Does not rank commons by capacity
- Does not move money, issue credit, or execute anything
- Does not call any network or hold any key

Human review is required before any real-world action.
