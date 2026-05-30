# Contributor Credit Spec — Dan-Go / GITSEA

> **Contribution history is not credit.**
> **Dan-Go records contribution candidates; external systems may issue credit.**

## Overview

The Contributor Credit layer (Phase 11) records contribution activity
in the Dan-Go negotiation protocol and surfaces it as advisory candidate
records for GITSEA credit observability.

Dan-Go **never issues credit**. It records contribution candidates.
GITSEA or other external systems may observe those candidates and decide
independently whether to issue credit.

## What This Layer Does

- Records pseudonymous contributor identities and roles in negotiation
- Records individual contribution events (evidence submission, review, contest, etc.)
- Aggregates candidates into advisory snapshots
- Maintains an append-only contribution history log

## What This Layer Does NOT Do

- Issue credit (credit_issued is always `false`)
- Allocate rewards
- Distribute tokens
- Trigger GITSEA streams
- Score contributors for economic outcomes
- Move funds
- Call external APIs
- Connect to any network

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

`credit_issued: false` is a **permanent protocol invariant**. It is never
changed by Dan-Go, regardless of contribution type or GITSEA stream activity.

## Contributor Roles

| Role        | Description                                        |
|-------------|-----------------------------------------------------|
| author      | Submitted original evidence or PR                  |
| reviewer    | Reviewed submitted evidence or PR                  |
| contester   | Contested a claim or plan (healthy dissent)        |
| reaffirmer  | Reaffirmed a position with new context             |
| observer    | Observed the negotiation without direct contribution|
| corrector   | Proposed a plan correction                         |

## Contribution Types (Credit Candidate Events)

| Type               | Credit Eligible | Description                              |
|--------------------|----------------|------------------------------------------|
| evidence_submitted | No             | Evidence submitted via PR                |
| evidence_reviewed  | Yes            | Evidence reviewed and approved           |
| evidence_accepted  | Yes            | Evidence accepted via PR merge           |
| contest_raised     | No             | Legitimate contest raised                |
| reaffirm_submitted | Yes            | Reaffirmation submitted with new context |
| plan_correction    | Yes            | Plan correction proposed                 |

"Credit eligible" means the contribution is a **candidate** for external
credit consideration. It does not mean credit will be issued.

## Runtime Modules

| Module                        | Purpose                                   |
|-------------------------------|-------------------------------------------|
| `contributor_registry.py`     | Record contributors and their roles       |
| `contribution_candidate.py`   | Record contribution events as candidates  |
| `credit_candidate_snapshot.py`| Aggregate candidates into advisory snapshot|
| `contribution_history.py`     | Build append-only contribution history    |

## Relationship to GITSEA

GITSEA **may** observe contribution candidates when assessing stream credit.
Dan-Go does not push signals to GITSEA. Dan-Go does not activate streams.
Whether a contribution candidate translates to a GITSEA stream event is
entirely GITSEA's decision.

## Required Phrases

All spec documents and runtime modules in this layer must include:

1. `"Contribution history is not credit."`
2. `"Dan-Go records contribution candidates; external systems may issue credit."`

These phrases are protocol invariants for Phase 11.
