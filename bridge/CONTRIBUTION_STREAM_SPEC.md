# Contribution Stream Specification

Version: 0.1.0-draft

---

## What is a Contribution Stream?

A contribution stream is a continuous record of contributions flowing toward
the missing conditions of a Claim.

It is not a payment channel.
It is not a financial instrument.
It is an accounting layer that makes non-monetary contributions legible.

---

## Stream Entry Schema

```json
{
  "stream_id": "string",
  "claim_id": "string",
  "asset_id": "string",
  "contributor_id": "string — DID or pseudonym",
  "contribution_type": "string",
  "addresses_condition": "string — which missing condition",
  "volume": "string — human-readable quantity (e.g. '3 hours', '1 legal review', '500 words')",
  "verifiable": true,
  "verification_method": "string",
  "dignity_cleared": true,
  "timestamp": "ISO 8601",
  "status": "flowing | paused | completed | disputed"
}
```

---

## Contribution Types in Streams

All contribution types from CONTRIBUTION_SPEC.md are valid in streams.

| Type | Example Volume Unit |
|---|---|
| `code` | commits, lines, hours |
| `compute` | CPU hours, GB-hours |
| `legal` | hours, documents reviewed |
| `translation` | words, documents, sessions |
| `housing` | days, square meters |
| `funding` | amount (currency unspecified) |
| `social_reach` | shares, introductions, audience size |
| `reputation` | endorsements, vouches |
| `care` | hours, sessions |
| `knowledge` | hours, documents, research items |
| `coordination` | sessions, connections made |

Volume is human-readable and self-reported.
Verification method describes how it can be independently confirmed.

---

## Stream Candidates

A contribution becomes a stream candidate when:

1. It is explicitly offered for a specific Claim
2. It addresses a specific missing condition
3. It passes the dignity guard
4. It has a stated volume and verification method

Stream candidates are not yet streams.
They become streams when the Claim owner (or negotiation consensus) accepts them.

---

## Stream Statuses

| Status | Meaning |
|---|---|
| `flowing` | Contribution is actively being made |
| `paused` | Temporarily halted (contributor or claim reason) |
| `completed` | Contribution fully delivered |
| `disputed` | Delivery or quality challenged |

---

## What Streams Do Not Guarantee

- Payment or financial return
- That the Claim will be realized
- That GITSEA or any financial layer will recognize the stream
- Legal enforceability of contribution records

Streams are a coordination tool, not a contract.
They create a public record. They do not create obligations.

---

## Agent-to-Agent Streams

AI agents may contribute to streams on behalf of human principals,
provided:

- The principal has explicitly delegated this via UCAN or equivalent
- The delegation is logged and auditable
- The dignity guard applies to agent contributions as it does to human ones

An agent cannot consent on behalf of a human.
An agent cannot waive dignity constraints on behalf of a vulnerable person.
