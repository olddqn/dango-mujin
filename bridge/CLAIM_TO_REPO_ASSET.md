# Claim to Repo Asset

Version: 0.1.0-draft

---

## Overview

A Dan-Go Claim is a proposed state transition.
A GITSEA repo asset is an economic identity attached to a repository.

This document specifies how one becomes the other.

---

## The Transformation

A Claim becomes a repo asset when:

1. It passes the dignity guard (see DIGNITY_GUARD.md)
2. It has at least one `possible_contribution` that is not purely financial
3. Its `decision` is `negotiate` or `execute` (not `reject`)

A rejected Claim cannot become a repo asset.
A Claim under dignity review is blocked until review completes.

---

## Field Mapping

| Claim Field | Repo Asset Field | Notes |
|---|---|---|
| `claim_id` | `asset_id` | Direct mapping |
| `title` | `name` | Direct mapping |
| `statement` | `description` | Direct mapping |
| `speaker` | `origin_contributor` | The DID or pseudonym that submitted the Claim |
| `required_state` | `required_conditions` | Full list |
| `missing_conditions` | `open_conditions` | Subset of required_conditions not yet met |
| `possible_contributions` | `eligible_stream_types` | What kinds of contribution can be streamed |
| `dignity_constraints` | `dignity_guard_flags` | Constraints that the guard enforces |
| `decision` | `asset_status` | negotiate→pending, execute→active, reject→invalid |
| `created_at` | `created_at` | Direct mapping |

---

## Repo Asset Schema

```json
{
  "asset_id": "string",
  "name": "string",
  "description": "string",
  "origin_contributor": "string — DID or pseudonym",
  "asset_status": "pending | active | invalid | under_review",
  "required_conditions": ["string"],
  "open_conditions": ["string"],
  "eligible_stream_types": ["string"],
  "dignity_guard_flags": ["string"],
  "dignity_guard_status": "pass | block | escalate | pending",
  "stream_eligible": true,
  "created_at": "ISO 8601",
  "source_claim_id": "string"
}
```

---

## Stream Eligibility

A repo asset is stream-eligible when:

- `dignity_guard_status` is `pass`
- `asset_status` is `active` or `pending`
- At least one `eligible_stream_type` exists
- No `open_conditions` requires coercion or exploitation to meet

Stream eligibility does not mean a stream exists.
It means a stream can be proposed and negotiated.

---

## What a Stream Is Not

- Not a payment
- Not a dividend
- Not a yield
- Not a return on investment

A stream is an accounting of contribution flow.
It records: who contributed what, in what form, toward which condition.
That record becomes a credit history.
Credit history may inform future reciprocity.
It does not guarantee it.
