# Contribution → Credit Signal Mapping

> In an OGI-style economy, money is one contribution among many.
> Credit signals make all contributions visible to the coordination layer.

---

## Why Non-Monetary Contributions Need Credit Signals

In a market economy, contributions that cannot be priced are invisible.

A translator who works for a refugee support network may receive payment.
A community elder who provides local knowledge may not.
A safety reviewer who flags a dignity violation protects everyone —
and may receive nothing for that protection.

An OGI-style economy needs to track all contributions
that move a claim forward, regardless of whether they involve money.

A **credit signal** is not payment.
It is an acknowledgment — a record in the shared economy's memory
that a contribution was made, what kind it was, and what it addressed.

Credit signals accumulate over time and serve as:
- Evidence of contribution history for trust-building
- Inputs to reputation and coordination capacity
- The economy's memory of who did what under what conditions

Credit signals are not:
- Currency (they are not exchangeable by default)
- Score (they are not ranked against each other)
- Guarantee (they do not promise future reward)

---

## Contribution Types and Credit Dimensions

| Contribution type | Credit dimension | Description |
|---|---|---|
| `compute` | `compute_credit` | CPU/GPU cycles, storage, bandwidth contributed |
| `code` | `code_credit` | Software, automation, tooling contributed |
| `translation` | `translation_credit` | Language translation, cross-cultural mediation |
| `care` | `care_credit` | Emotional support, coordination of human needs |
| `distribution` | `distribution_credit` | Routing, delivery, network access |
| `verification` | `verification_credit` | Fact-checking, authenticity review |
| `legal_review` | `review_credit` | Legal analysis, risk assessment |
| `safety_review` | `review_credit` | Safety assessment, risk flagging |
| `risk_review` | `review_credit` | General risk review |
| `local_knowledge` | `knowledge_credit` | Community-specific, geographic, cultural knowledge |
| `story_editing` | `content_credit` | Editing, curation, narrative support |
| `coordination` | `coordination_credit` | Organizing, facilitating, bridging parties |
| `funding` | `monetary_credit` | Direct monetary contribution |
| `support` | `care_credit` | General support and affirmation |

---

## Credit Signal Format

```json
{
  "credit_id": "credit-{contribution_id}",
  "origin_claim_id": "post-scarcity-001",
  "contributor": "did:key:z6Mk...",
  "contribution_type": "translation",
  "credit_dimension": "translation_credit",
  "volume": "1200 words, 2 sessions",
  "addresses_condition": "translation",
  "dignity_cleared": true,
  "verified": false,
  "verification_method": "self-reported",
  "credit_weight": "standard",
  "timestamp": "2026-05-24T00:00:00Z",
  "origin_contribution_hash": "sha256:..."
}
```

### Field Definitions

- `credit_id` — unique identifier for this credit signal
- `origin_claim_id` — which Dan-Go Claim this contribution serves
- `contributor` — DID or pseudonym of the contributor
- `contribution_type` — raw type from Dan-Go contribution event
- `credit_dimension` — OGI credit category (see table above)
- `volume` — human-readable description of contribution size
- `addresses_condition` — which required condition this contribution moves forward
- `dignity_cleared` — **must be true for credit to be issued**
- `verified` — whether the contribution has been independently verified
- `verification_method` — how it was or could be verified
- `credit_weight` — `"standard"` | `"verified"` | `"high"` | `"disputed"`
- `timestamp` — when the contribution was made
- `origin_contribution_hash` — sha256 of the su-table contribution event

---

## Dignity Requirement

**Credit is not issued for dignity-blocked contributions.**

If `dignity_cleared: false` in the Dan-Go contribution event,
no credit signal is generated.

The reason:
- Dignity-blocked contributions have not passed the coordination protocol
- Issuing credit for them would incentivize bypassing dignity constraints
- The economy must not reward protocol violations

When a dignity block is resolved and the contribution is accepted,
a new contribution event is appended with `dignity_cleared: true`
and credit is issued for the accepted event.

---

## Credit Weight Levels

| Weight | Condition |
|---|---|
| `standard` | Contribution reported but not independently verified |
| `verified` | Contribution verified by third party or reviewable artifact |
| `high` | Verified + addresses a critical missing condition |
| `disputed` | Contribution contested via negotiation event |

Credit weight affects how coordination systems can use the signal.
It does not change the existence of the credit in the su-table.

---

## Contribution → Credit: Multi-Dimensional Value

A single contribution may produce credit across multiple dimensions.

Example: A community elder who provides **local knowledge** for a safety review:
- `knowledge_credit` (primary — local knowledge)
- `review_credit` (secondary — the knowledge serves a safety assessment)

Both credits are recorded.
Both are linked to the same origin contribution event.
Neither cancels the other.

This multi-dimensionality is what allows the OGI layer to hold
non-monetary contributions as first-class values.

---

## Temporal Trust Decay: Credit Signals Are Not Fixed

Credit signals are records of what was done. They are permanent.

But the **coordination weight** of those signals changes with time.

`temporal_trust_decay.py` implements a time-decaying trust weight for each
contribution event. This weight is separate from the credit signal itself —
it is a coordination utility, not a judgment of value.

```
trust_weight = base_weight × decay_factor × verification_mult
             × dignity_mult × continuity_mult

decay_factor = max(0.05, 0.5 ^ (days_since / half_life_days))
```

### What This Means for Credit Signals

A credit signal issued 2 years ago is still in the su-table.
The contribution happened. It is remembered.

But when an OGI coordination system queries *how much weight to give it today*,
the answer reflects the time since the contribution:

| days since contribution | trust_weight (verified, no bonus) |
|---|---|
| 0 (today) | 1.2 |
| 30 | 0.95 |
| 90 (one half-life) | 0.60 |
| 180 | 0.30 |
| 365 | 0.091 |
| 730+ | 0.05 (floor) |

### The Anti-Cartel Property

Without decay, early contributors accumulate permanent coordination advantage.
The first agent to appear in a claim would always outweight newcomers.

Decay prevents this:
- Old high-quality contributions still count (floor = 0.05)
- But they do not permanently block new contributors
- Continuity bonus rewards regular return (up to 1.5×, capped)
- No agent becomes untouchable through history alone

### Dignity Block Is the Only Zero

`dignity_cleared: false` → trust_weight = 0.0 exactly.

The minimum floor (0.05) does NOT apply to dignity-blocked contributions.
The credit record remains. The coordination weight is zero.

```bash
# Compute trust weight for a single contribution event
python runtime/contribution_weight.py examples/trust-decay-input.json

# View contributor trust snapshot for a claim
python runtime/trust_snapshot.py --claim-id housing-001
```

See `TEMPORAL_TRUST_DECAY_SPEC.md` in the bridge root for the full specification.

---

## What Credit Is Not

Credit signals are not:
- A promise of future payment
- A governance vote
- A basis for discrimination or ranking agents against each other
- A replacement for dignity constraints
- A reputation score that gates participation
- A fixed value that never changes (trust weights decay with time)

An agent with no credit history can still participate in Dan-Go negotiations.
Credit signals are **additional information** about the economy's coordination history.
They are not a prerequisite for participation.
