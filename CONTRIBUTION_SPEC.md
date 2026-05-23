# Contribution Specification

Version: 0.1.0-draft

---

## What Counts as a Contribution?

In Dan-Go Mujin, contribution is not only money.

Any resource, effort, or capacity that helps close a missing condition is a valid contribution.

---

## Contribution Types

| Type | Examples |
|---|---|
| `code` | Software, scripts, automation, data pipelines |
| `compute` | CPU/GPU time, server hosting, storage, bandwidth |
| `legal` | Legal review, contract drafting, compliance research, rights clarification |
| `translation` | Language translation, cultural mediation, accessibility adaptation |
| `housing` | Physical space, shelter, workshop venue, meeting space |
| `funding` | Financial resources (not investment — contribution to a specific condition) |
| `social_reach` | Distribution networks, community access, amplification, introductions |
| `reputation` | Vouching, endorsement, trust transfer, institutional credibility |
| `care` | Emotional support, facilitation, human presence, conflict mediation |
| `knowledge` | Research, documentation, domain expertise, lived experience |
| `coordination` | Organizing, scheduling, connecting people, logistics |

---

## Contribution Record Format

```json
{
  "contribution_id": "string",
  "claim_id": "string — which claim this contributes to",
  "contributor_id": "string — DID or pseudonym",
  "contribution_type": "string — from the list above",
  "description": "string — what specifically is being contributed",
  "addresses_condition": "string — which missing_condition this closes",
  "verifiable": true,
  "verification_method": "string — how can this be independently verified?",
  "timestamp": "ISO 8601",
  "status": "offered | committed | delivered | verified | disputed"
}
```

---

## Contribution Statuses

**offered** — The contributor has stated they can provide this.
**committed** — The contributor has formally committed to provide this.
**delivered** — The contributor reports delivery.
**verified** — Another participant has independently verified delivery.
**disputed** — Someone has challenged whether this was actually delivered.

---

## What Is NOT a Contribution

- Promises without specificity ("I'll help somehow")
- Commitments that require coercing others
- Endorsements of the Claim's outcome without contributing to conditions
- Financial instruments or investment-like structures

---

## Trust and Contribution

Contributions build trust score over time.

Verified contributions count more than unverified ones.
Delivered contributions count more than offered ones.
Disputed contributions are investigated before counting.

See `TRUST_MODEL.md` for the full model.

---

## Contribution Matching

The runtime (`contribution_router.py`) matches contribution offers to missing conditions.

When you run:
```bash
python runtime/contribution_router.py examples/housing.claim.json
```

It will show:
- Which conditions are missing
- Which contribution types are needed
- Which offered contributions address which conditions

---

## Principles

1. Contributions are voluntary. There is no obligation to contribute.
2. Contributions may be partial. Partial help is still help.
3. Contributions may be withdrawn before commitment, not after.
4. All contributions are logged. The log is public.
5. You cannot contribute on behalf of someone else without their explicit agreement.
