# Claim Format Specification

Version: 0.1.0-draft

---

## What is a Claim?

A Claim is a proposed state transition.

It is not a promise. It is not a prediction. It is not a request for money.

It is a structured declaration of:
- What is currently true (observed state)
- What needs to become true (required state)
- What is missing (the gap)
- What kinds of help could close the gap

---

## JSON Schema

```json
{
  "claim_id": "string — unique identifier, e.g. claim-{topic}-{sequence}",
  "title": "string — one sentence summary",
  "speaker": "string — DID or pseudonym of claim submitter",
  "claim_type": "declarative | interrogative | imperative",
  "statement": "string — the full claim in plain language",
  "observed_state": ["string — verified facts about current reality"],
  "required_state": ["string — conditions that must be true for realization"],
  "missing_conditions": ["string — subset of required_state not yet met"],
  "possible_contributions": ["string — contribution types that could help"],
  "risks": ["string — known obstacles and failure modes"],
  "decision": "negotiate | execute | escalate | reject",
  "constitution_check": {
    "violates_dignity": false,
    "uses_coercion": false,
    "notes": "optional explanation"
  },
  "created_at": "ISO 8601 timestamp",
  "updated_at": "ISO 8601 timestamp",
  "version": "integer — increments with each update"
}
```

---

## Claim Types

**declarative** — "This thing can happen."
Use when asserting that a state transition is possible.

**interrogative** — "Can this thing happen?"
Use when genuinely uncertain and seeking negotiation to determine feasibility.

**imperative** — "This thing must happen."
Use when asserting urgency. Requires stronger justification.

---

## The Constitution Check

Every Claim must answer two questions:

1. `violates_dignity` — Does realizing this Claim require violating the dignity of any person?
2. `uses_coercion` — Does realizing this Claim require forcing anyone to participate?

If either is `true`, the Claim is invalid and cannot proceed.

This check is self-reported. The community may challenge it.

---

## Observed vs Required vs Desired State

This distinction is critical.

| Field | Question |
|---|---|
| `observed_state` | What do we know is currently true, and how do we know it? |
| `required_state` | What must become true for the claim to be realized? |
| `missing_conditions` | Which required conditions are not yet met? |

Do not put desired outcomes in `observed_state`.
Do not present speculation as fact.

---

## Writing a Good Claim

**Too vague:**
```
"statement": "People should have better housing."
```

**Too specific/prescriptive:**
```
"statement": "The government must build 100,000 units by 2027."
```

**Good:**
```
"statement": "This vacant building at [address] can become transitional housing
             for 12 families through a combination of owner permission,
             volunteer renovation, and municipal exemption."
```

A good Claim:
- Names a specific situation
- Separates what is known from what is needed
- Invites concrete contributions
- Does not require coercion to realize

---

## Updating a Claim

Claims are versioned. When you update a Claim:
- Increment `version`
- Update `updated_at`
- Keep the original `claim_id`
- Document what changed and why

Old versions should be preserved in git history.

---

## Submitting a Claim

1. Copy an example from `examples/`
2. Fill in all required fields
3. Run `python runtime/claim_matcher.py your-claim.json` to check what is missing
4. Submit as a pull request or open an issue
5. Participate in negotiation
