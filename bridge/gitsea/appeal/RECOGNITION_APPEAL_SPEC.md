# Recognition Appeal Spec — Dan-Go / GITSEA (Phase 14)

> **"Appeal is not enforcement."**
> **"Recognition remains external."**

## Overview

Phase 14 introduces the Recognition Appeal Layer — a structured way to
record that a contributor, agent, or observer requests reconsideration of
a contribution that was not externally credited.

Phase 13 established that unrecognized contributions are observable.
Phase 14 establishes that those contributions can be the subject of an
advisory appeal — a recorded request for reconsideration that carries no
authority and compels no response.

## What Is an Appeal?

A **recognition appeal** is an advisory record stating that:
- A contribution candidate exists (Phase 11)
- External credit was not observed (Phase 12)
- The contribution was recorded as unrecognized (Phase 13)
- The contributor or observer requests reconsideration

An appeal is a voice. It is not a lever, a claim, or a demand.

## What an Appeal Is NOT

| Claim | True? |
|-------|-------|
| An appeal compels GITSEA to act | No — Dan-Go has no authority over GITSEA |
| An appeal creates a legal claim | No — authority: none |
| An appeal is a dispute record | No — appeal_creates_authority: false |
| An appeal guarantees reconsideration | No — external systems are sovereign |
| An appeal issues credit | No — credit_issued: false, permanent |
| An appeal modifies external state | No — advisory only |

## Runtime Modules

| Module | Purpose |
|--------|---------|
| `recognition_appeal.py` | Record advisory appeal requests per contributor |
| `appeal_packet_builder.py` | Assemble Phase 11-13 records into a self-contained packet |
| `appeal_status_snapshot.py` | Snapshot appeal lifecycle state |
| `appeal_reflection_report.py` | 5-section report explaining the appeal layer |

## Appeal Grounds

| Key | Description |
|-----|-------------|
| `evidence_complete` | Evidence submitted was complete and accepted |
| `review_completed` | Review was performed and credit-eligible |
| `contested_in_good_faith` | Contest raised in good faith |
| `reaffirmation_provided` | Reaffirmation submitted with new context |
| `correction_proposed` | Plan correction proposed within protocol |
| `general_reconsideration` | General request for reconsideration |

## Appeal Lifecycle States

| State | Description |
|-------|-------------|
| `pending` | Appeal recorded; awaiting external system observation |
| `acknowledged` | External system has acknowledged the appeal |
| `reconsidered` | External system has reconsidered the contribution |
| `credited` | External credit issued following appeal |
| `not_credited` | Appeal considered; no credit issued |
| `withdrawn` | Appeal withdrawn by appellant |

## Invariants

All records in this layer carry the following invariants:

```json
{
  "credit_issued":             false,
  "moves_money":               false,
  "execution_allowed":         false,
  "hard_enforcement":          false,
  "advisory":                  true,
  "appeal_only":               true,
  "authority":                 "none",
  "append_only":               true,
  "contestable":               true,
  "reopenable":                true,
  "appeal_is_enforceable":     false,
  "appeal_compels_credit":     false,
  "appeal_modifies_external":  false,
  "appeal_creates_authority":  false,
  "packet_is_submission":      false,
  "packet_compels_response":   false,
  "compels_response":          false
}
```

## Required Phrases

All spec documents and runtime modules in this layer must include:

1. `"Appeal is not enforcement."`
2. `"Recognition remains external."`
