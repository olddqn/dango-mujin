# External Credit Spec — Dan-Go / GITSEA (Phase 12)

> **"Observation is not issuance."**
> **"Candidate credit is not external credit."**

## Overview

Phase 12 introduces the External Credit Adapter Layer — a set of modules
that make the distinction between Dan-Go contribution candidates and
external credit outcomes explicit in the architecture.

Phase 11 established that Dan-Go records contribution candidates.
Phase 12 establishes that external credit systems decide independently
whether to issue credit, and that Dan-Go's role is to observe — not decide.

## Core Distinction

| Concept | Source | Dan-Go Role |
|---------|--------|-------------|
| Contribution candidate | Dan-Go (Phase 11) | Records |
| External credit | GITSEA or other external system | Observes only |

These are not the same thing. A contribution candidate existing in Dan-Go
does not mean external credit was issued, is owed, or will ever be issued.
External systems are sovereign.

## What This Layer Does

- Represents external credit systems as adapter records
- Snapshots the current observed external credit state
- Compares Dan-Go candidates against external outcomes
- Generates human-readable observation reports explaining the gap

## What This Layer Does NOT Do

- Issue credit (credit_issued is always `false`)
- Request credit issuance from external systems
- Activate GITSEA streams
- Push candidates to external systems
- Modify any external state
- Move funds
- Perform wallet operations
- Call any external API

## Runtime Modules

| Module | Purpose |
|--------|---------|
| `external_credit_adapter.py` | Represent external systems and their observed state |
| `external_credit_snapshot.py` | Snapshot external credit observation for a claim |
| `candidate_vs_external.py` | Compare Dan-Go candidates against external outcomes |
| `credit_observation_report.py` | Human-readable report explaining the observation state |

## Invariants

All records in this layer carry the following invariants:

```json
{
  "credit_issued":      false,
  "moves_money":        false,
  "execution_allowed":  false,
  "hard_enforcement":   false,
  "advisory":           true,
  "authority":          "none",
  "append_only":        true,
  "contestable":        true,
  "reopenable":         true
}
```

`credit_issued: false` is a **permanent protocol invariant** inherited from
Phase 11 and extended here. It is never changed by Dan-Go.

## The Gap Is Not an Error

When Dan-Go records contribution candidates but no external credit is observed,
this is **expected and by design**. It is not a bug, a failure, or a protocol
violation. The gap reflects:

1. External credit systems are sovereign — they decide on their own schedule.
2. Candidate credit is a Dan-Go classification — it is advisory only.
3. Dan-Go does not guarantee credit will ever be issued.
4. Observation is sufficient — Dan-Go has fulfilled its protocol role
   by recording candidates accurately and making them observable.

## External System Sovereignty

External systems such as GITSEA:
- May observe Dan-Go contribution candidates at any time
- May issue credit independently, on their own schedule
- May choose not to issue credit for any reason
- Are not bound by Dan-Go candidate classifications
- Are not notified or activated by Dan-Go

Dan-Go observes. External systems decide.

## Required Phrases

All spec documents and runtime modules in this layer must include:

1. `"Observation is not issuance."`
2. `"Candidate credit is not external credit."`
