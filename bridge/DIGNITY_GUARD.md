# Dignity Guard

Version: 0.1.0-draft

---

## The One Law

> **Do not violate the dignity of another.**

The dignity guard is the operational implementation of this law.
It runs before any other transformation in this bridge.
Its decision cannot be bypassed.

---

## The Seven Principles

1. Do not violate the dignity of another.
2. Do not monetize suffering without consent.
3. Do not expose location or identity of vulnerable people.
4. Do not treat refugees as content inventory.
5. Do not convert emergency need into speculative asset.
6. Consent, anonymity, revocability, and revenue sharing must be explicit.
7. If unsure, block.

---

## Decision Logic

```
Input: Claim JSON with dignity_constraints and observed_state

IF consent_unknown in observed_state OR missing_conditions:
    → BLOCK
    reason: "Consent not established. Cannot proceed."

IF "no_identity_exposure" in dignity_constraints AND identity_exposure risk detected:
    → BLOCK
    reason: "Identity exposure risk. Cannot proceed."

IF "no_location_exposure" in dignity_constraints AND location_exposure risk detected:
    → BLOCK
    reason: "Location exposure risk. Cannot proceed."

IF exploitation_risk flagged anywhere in claim:
    → ESCALATE
    reason: "Exploitation risk detected. Human review required."

IF emergency_need flagged in observed_state:
    → BLOCK from stream
    → ESCALATE to direct support
    reason: "Emergency need cannot be channeled through monetization layer."

IF "revocable_consent" NOT in dignity_constraints:
    → BLOCK
    reason: "Revocable consent not guaranteed. Cannot proceed."

IF "fair_revenue_share" NOT in dignity_constraints AND funding in possible_contributions:
    → BLOCK
    reason: "Revenue sharing not specified. Cannot proceed."

IF all checks pass:
    → PASS
    reason: "Dignity guard cleared."
```

---

## Decision Outputs

| Decision | Meaning | Next Step |
|---|---|---|
| `pass` | All dignity checks cleared | Proceed to asset transformation |
| `block` | Hard stop — dignity violation risk | Do not proceed. Log reason. |
| `escalate` | Ambiguous — human review required | Pause. Notify human reviewer. Wait. |

---

## What Cannot Override the Guard

- Urgency cannot override the guard
- Financial opportunity cannot override the guard
- Technical capability cannot override the guard
- Agent authority cannot override the guard
- Platform policy cannot override the guard

Only explicit, documented human consent from the affected person
can change a `block` to a `pass` — and only for that specific case.

---

## Logging

Every dignity guard decision is logged with:
- Claim ID
- Decision (pass / block / escalate)
- Reason
- Timestamp
- Reviewer (if escalated)

The log is public. The log is append-only.
A `block` decision cannot be deleted. It can be superseded by a `pass`
only with documented human review attached.

---

## For AI Agents

An AI agent running the dignity guard:
- May make `pass` decisions for structurally clear cases
- Must escalate any `block` that involves a specific vulnerable person
- Must never make `pass` decisions for consent-unknown cases
- Must never substitute its judgment for human ethical review in ambiguous cases

The dignity guard is a structural filter.
It is not a substitute for human wisdom about specific situations.
