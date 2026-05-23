# Temporal Trust Decay — Specification

> Memory is permanent. Trust is dynamic.
> What was done cannot be undone.
> What was trusted must be re-earned.

---

## Why Trust Decays

Trust in Dan-Go is not a score. It is not a rating. It is not a credential.

Trust is a coordination signal — an estimate of how much weight
to give a contributor's signal when routing work and making decisions.

A coordination signal from two years ago is meaningful.
But it is not as meaningful as one from two weeks ago.

**Why the decay matters:**

1. **The world changes.** A legal reviewer who was excellent last year
   may have changed specialization, geography, or availability.
   Their old contributions are evidence of capability — but not current capability.

2. **Trust must be earned, not hoarded.** Without decay, early contributors
   accumulate permanent advantage. The first translator to appear
   would always outrank everyone who came after.
   Decay prevents calcification.

3. **Continuity matters, but is not absolute.** A contributor who returns
   repeatedly earns a continuity bonus. But the bonus is capped.
   No one becomes untouchable through history alone.

4. **Dignity violation is the only hard reset.** A dignity block sets trust
   to exactly zero — no floor, no minimum. Memory remains. Trust is revoked.

---

## The Formula

```
trust_weight =
    base_weight
  × decay_factor
  × verification_multiplier
  × dignity_multiplier
  × continuity_multiplier
```

### Decay Factor

```
decay_factor = max(MIN_WEIGHT, 0.5 ^ (days_since / half_life_days))
```

- Default half-life: **90 days**
- Minimum weight: **0.05** (ancient contributions are still visible, just quiet)
- The minimum floor applies to all events *except* dignity-blocked ones

| days since event | decay_factor (90-day half-life) |
|---|---|
| 0 | 1.000 |
| 30 | 0.794 |
| 90 | 0.500 |
| 180 | 0.250 |
| 365 | 0.076 |
| 730 | 0.050 (floor) |

### Verification Multiplier

Reflects how well the contribution was validated:

| verification_status | multiplier |
|---|---|
| `verified` | 1.2 |
| `self_reported` | 1.0 |
| `disputed` | 0.6 |

Verification is not about moral worth — it is about how much signal reliability
to assign to the contribution.

### Dignity Multiplier

Reflects the dignity review outcome at contribution time:

| dignity_review | multiplier |
|---|---|
| `pass` | 1.0 |
| `escalate` | 0.8 |
| `block` | 0.0 (hard zero) |

The dignity multiplier is the **only** path to exact zero.
When dignity_multiplier = 0.0:
- trust_weight = 0.0 exactly
- The minimum floor (0.05) does NOT apply
- The contribution's memory remains in the su-table
- The trust weight is simply zero

This is correct. A dignity-blocked contribution is not forgotten.
It is recorded — and its signal weight is revoked.

### Continuity Multiplier

Contributors who return multiple times earn a small coordination bonus:

```
continuity = min(MAX_CONTINUITY, 1.0 + CONTINUITY_STEP × (count − 1))
```

- `CONTINUITY_STEP = 0.1`
- `MAX_CONTINUITY = 1.5` (hard cap — anti-cartel protection)

| contribution_count | continuity_multiplier |
|---|---|
| 1 | 1.0 |
| 2 | 1.1 |
| 3 | 1.2 |
| 4 | 1.3 |
| 5 | 1.4 |
| 6+ | 1.5 (capped) |

The cap exists because **repeated presence should not create untouchable status**.
Dan-Go is not a reputation cartel. Established contributors are valued;
they do not become unchallengeable.

### Base Weight

Base weight = **1.0** for all contribution types.

This is intentional. Dan-Go does not rank contribution types against each other
by default. A translation and a legal review are both contributions.
They are not on the same scale — they serve different conditions.

Trust weight reflects *temporal position and verification quality*,
not a judgment about which work is more valuable.

---

## Minimum Weight: The Floor Principle

```
trust_weight >= MIN_WEIGHT (0.05) — unless dignity-blocked
```

Ancient contributions do not disappear from coordination memory.
They become very quiet — but they do not vanish.

This reflects the append-only philosophy:
- The su-table never deletes.
- Trust computation never erases.
- Old contributions are simply less loud.

A contributor from three years ago who was excellent
still has *some* weight in the signal. Not much. But some.
This is honest. They contributed. It happened. The log says so.

---

## Trust Levels

For human display and routing, trust_weight maps to a level:

| trust_weight | trust_level |
|---|---|
| ≥ 0.7 | `high` |
| ≥ 0.3 | `medium` |
| > 0.0 | `low` |
| = 0.0 | `blocked` |

These levels are **display hints** — not routing rules.
Routing decisions are made by the dignity guard and negotiation protocol,
not by trust level alone.

A `low` trust contributor is not blocked. They have less coordination weight.
Only dignity_review = "block" creates an actual block.

---

## Dignity Violation Destroys Trust Completely

If a contribution is dignity-blocked:
- trust_weight = 0.0 (exact zero, no floor)
- The contribution record remains in the su-table
- The signal is completely suppressed

If a contributor later makes new contributions:
- Those new contributions are evaluated independently
- Past blocks do not automatically block future contributions
- But they remain in the graph, visible to human reviewers

Dan-Go does not erase history. It weights it correctly.

---

## Reputation Cartels: Why the Cap Exists

Without a continuity cap, early contributors would compound their advantage
indefinitely. The first agent to participate in a claim would build
an increasing multiplier — making newcomers structurally disadvantaged.

This creates a **reputation cartel**: a small group of established agents
accumulates coordination power that cannot be challenged by new participants.

The continuity cap (`MAX_CONTINUITY = 1.5`) prevents this:
- Returning contributors are rewarded (up to 50% bonus)
- But no one becomes infinitely privileged through history alone
- Recent, verified contributions from newcomers can exceed
  old, decayed contributions from established agents

This is the design goal: **continuity valued, cartel prevented**.

---

## Trust is Coordination Memory, Not Moral Worth

This specification is not about judging people.

A low trust weight does not mean a contributor is bad.
It means their contribution signal is old, or unverified, or from an event
that was flagged at the dignity review stage.

A high trust weight does not mean a contributor is trustworthy as a person.
It means their recent, verified contributions carry strong coordination signal.

**Trust in Dan-Go is instrumental, not moral.**

It answers: *how much weight should this signal carry right now?*
Not: *is this person good?*

The dignity guard answers the ethical questions.
Trust weight answers the coordination questions.

They are different systems. They must not be confused.

---

## Example Calculations

### Example 1: Recent, verified contribution (high trust)

```
event: contribution_accepted
timestamp: 14 days ago
verification_status: verified
dignity_review: pass
contribution_count: 1

decay_factor   = 0.5^(14/90) = 0.5^0.156 = 0.898
trust_weight   = 1.0 × 0.898 × 1.2 × 1.0 × 1.0 = 1.077
trust_level    = high
```

### Example 2: Old, self-reported contribution (medium trust)

```
event: contribution_accepted
timestamp: 112 days ago
verification_status: self_reported
dignity_review: pass
contribution_count: 1

decay_factor   = 0.5^(112/90) = 0.5^1.244 = 0.422
trust_weight   = 1.0 × 0.422 × 1.0 × 1.0 × 1.0 = 0.422
trust_level    = medium
```

### Example 3: Regular contributor (continuity bonus)

```
event: contribution_accepted (latest of 3)
timestamp: 7 days ago
verification_status: self_reported
dignity_review: pass
contribution_count: 3

decay_factor        = 0.5^(7/90) = 0.947
continuity_mult     = min(1.5, 1.0 + 0.1 × 2) = 1.2
trust_weight        = 1.0 × 0.947 × 1.0 × 1.0 × 1.2 = 1.136
trust_level         = high
```

### Example 4: Dignity-blocked offer (zero trust)

```
event: contribution_offer
timestamp: 4 days ago
verification_status: self_reported
dignity_review: block  (story_editing without consent confirmation)

dignity_multiplier = 0.0
trust_weight       = 0.0 (exact zero — floor does not apply)
trust_level        = blocked
```

### Example 5: Very old contribution (at minimum floor)

```
event: contribution_accepted
timestamp: 730 days ago (2 years)
verification_status: verified
dignity_review: pass

decay_factor (raw) = 0.5^(730/90) = 0.5^8.11 = 0.0036
decay_factor (clamped) = max(0.05, 0.0036) = 0.05
trust_weight       = 1.0 × 0.05 × 1.2 × 1.0 × 1.0 = 0.06
trust_level        = low

The contribution is 2 years old. It still has a voice — just barely.
```

---

## CLI Reference

### Single-event trust weight

```bash
# Compute with current time as reference
python runtime/contribution_weight.py examples/trust-decay-input.json

# Fixed reference date (for deterministic testing)
python runtime/contribution_weight.py examples/trust-decay-input.json \
  --reference-date 2026-05-24

# Custom half-life
python runtime/contribution_weight.py examples/trust-decay-input.json \
  --half-life 180

# With contributor history (for continuity multiplier)
python runtime/contribution_weight.py examples/trust-decay-input.json \
  --count 3
```

### Contributor trust snapshot from su-table

```bash
# Snapshot for one claim
python runtime/trust_snapshot.py --claim-id housing-001

# Snapshot with fixed reference date
python runtime/trust_snapshot.py --claim-id housing-001 \
  --reference-date 2026-05-24

# All claims
python runtime/trust_snapshot.py --all-claims
```

---

## Programmatic API — `temporal_trust_decay.py`

| Function | Signature | Returns |
|---|---|---|
| `compute_days_since(ts, ref)` | `str, Optional[datetime] → float` | Days elapsed |
| `compute_decay_factor(days, half_life)` | `float, float → float` | Decay factor (≥ 0.05) |
| `compute_continuity_multiplier(count)` | `int → float` | Continuity multiplier (≤ 1.5) |
| `compute_trust_weight(event, ref, half_life, count)` | `dict, ... → dict` | Full result dict |
| `trust_level(weight)` | `float → str` | "high" / "medium" / "low" / "blocked" |

All functions are deterministic given the same inputs and reference_date.
No I/O. No randomness. No external dependencies.

---

## Graph Export Integration

The negotiation graph (`graph_export.py`) shows trust weight in all formats:

- **Text**: `↑ trust=0.99  decay=0.99  level=high  [self_reported]`
- **Mermaid**: `↑trust=0.99` appended to contribution node labels
- **HTML**: colored trust badge with hover tooltip showing decay formula

Badge colors:
| level | color |
|---|---|
| high | cyan |
| medium | amber |
| low | gray |
| blocked | red |

---

## What This Spec Does Not Cover

- Financial scoring
- Credit ratings
- Identity verification
- Real-time trust updates (trust is computed at query time, not stored)
- Cross-claim trust aggregation (each claim's snapshot is independent;
  see `CLAIM_FEDERATION_SPEC.md` for cross-claim relationships)
- Social trust transitivity ("trusted by X therefore trusted by Y")

Trust decay is a coordination tool. It is not a social credit system.
It is not a background check. It is not a judgment of character.

If used as any of the above, it has been misused.

---

> "Old contributions are not erased.
>  They are quieter.
>  The su-table remembers everything.
>  Trust weights only what is current."
