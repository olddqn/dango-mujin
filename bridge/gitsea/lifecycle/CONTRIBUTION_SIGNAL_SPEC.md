# Contribution Signal Spec

**Contribution becomes legible before it becomes valuable.**

This document specifies how Dan-Go generates advisory cooperation signals
from negotiation participation patterns.

Signals are not scores. Signals are not rewards.
Signals are not enforced. Signals are advisory participation legibility.

---

## 1. What a Signal Is

A cooperation signal is a number between 0.0 and 1.0.

It represents:

> "How much of the expected participation pattern was observed in this
> negotiation?"

It does NOT represent:
- How good the contribution was
- Whether the participant deserves a reward
- Whether the negotiation succeeded
- Whether the claim should be approved

**Participation legibility ≠ judgment.**

---

## 2. What a Signal Is Not

| It is NOT | Why |
|-----------|-----|
| A reputation score | Participants are not ranked against each other |
| A quality signal | Dan-Go cannot measure contribution quality |
| A reward trigger | No funds are distributed based on it |
| An authority signal | No coordinator enforces it |
| A final verdict | It is contestable and reopenable |
| A permanent record | New signals can be appended |

---

## 3. Signal Components

The cooperation signal has two components:

### Event Coverage (weight: 0.70)

Measures how many of the expected event types were observed.

Event types with advisory weights:

| Event | Weight | Meaning |
|-------|--------|---------|
| `evidence` | 0.30 | Evidence contribution |
| `contest` | 0.20 | Contesting a claim or plan |
| `reaffirm` | 0.20 | Reaffirming with new context |
| `pr_submitted` | 0.15 | PR submitted as evidence |
| `pr_merged` | 0.10 | PR merged (evidence accepted) |
| `plan_correction` | 0.05 | Plan correction proposed |

Each event type caps at 3 occurrences (diminishing returns).

### Participation Diversity (weight: 0.30)

Measures how many distinct participants contributed.
Caps at 5 participants for the multiplier.

```
diversity_multiplier = min(participant_count, 5) / 5.0
```

### Blended Signal

```
cooperation_signal = (0.70 × event_coverage) + (0.30 × diversity_multiplier)
```

Rounded to 2 decimal places. Capped at 1.0.

---

## 4. Why Contest Events Have Positive Weight

Contest events (a participant challenging a claim or plan) have a weight
of 0.20 — the same as a reaffirm event.

This is intentional.

A negotiation where no one contests anything may indicate:
- Insufficient scrutiny
- Participant disengagement
- Missing voices

A negotiation where someone contests something indicates:
- Active engagement
- Real disagreement being surfaced
- The protocol is working

**Dissent is a signal of negotiation health.**

A participant who contests a position is participating in the protocol,
not undermining it. Contest weight = 0.20 ensures dissent is rewarded
with cooperation signal, not penalized.

---

## 5. Why There Is No Threshold

There is no minimum cooperation signal required for:
- Issue creation
- PR submission
- PR merge
- GITSEA asset signal eligibility
- Any Dan-Go protocol action

A signal of 0.10 does not block anything.
A signal of 1.00 does not guarantee anything.

The signal is advisory. It is information, not a gate.

---

## 6. Signal Lifecycle

Signals are append-only:

```
Event occurs
    → New evaluation generated
    → Appended to log
    → Prior evaluation preserved
```

If a participant contests a cooperation signal:
- A reopen event is appended
- A new evaluation is generated with updated evidence
- Both evaluations remain in the log

No evaluation is ever deleted.

---

## 7. Signal Fields

```json
{
  "evaluation_type":    "cooperation_evaluation",
  "cooperation_signal": 0.75,
  "signal_components": {
    "event_coverage":       0.714,
    "diversity_multiplier": 0.600
  },
  "healthy_negotiation": {
    "contest_count":   1,
    "dissent_present": true,
    "note": "Contest events are a sign of healthy negotiation, not failure."
  },
  "advisory":           true,
  "contestable":        true,
  "reopenable":         true,
  "economic_value":     false,
  "authority":          "none",
  "execution_allowed":  false,
  "moves_money":        false,
  "hard_enforcement":   false
}
```

---

## 8. Invariants

| Field | Value |
|-------|-------|
| `advisory` | `true` — always |
| `contestable` | `true` — any signal can be challenged |
| `reopenable` | `true` — new events trigger new evaluations |
| `economic_value` | `false` — Dan-Go never assigns economic value |
| `authority` | `none` — no coordinator enforces signals |
| `hard_enforcement` | `false` — signals do not gate actions |

---

## 9. Absolute Prohibitions

- No threshold enforcement (signals do not block protocol actions)
- No reputation persistence (no cross-claim signal accumulation)
- No reward assignment
- No penalty for low signals
- No identity linkage (participants are pseudonymous)
- No external ranking systems

---

*authority: none · advisory · contestable · append-only · stdlib only*
*Contribution becomes legible before it becomes valuable.*
