# Sutable Specification (素テーブル)

Version: 0.1.0-draft

---

## What is the Sutable?

素テーブル (sutable) is the fully open state table of Dan-Go Mujin.

It is a public record of all Claims, their current state, and their negotiation history.

"素" (su) means raw, unprocessed, transparent — nothing hidden.
"テーブル" (tēburu) means table, as in a surface where everything is laid out.

The sutable is not a database owned by one party.
It is a protocol-level commitment to radical transparency.

---

## Properties

1. **All Claims are public by default.**
   Private claims are not supported by this protocol.
   If a claim requires secrecy to function, it is not a Dan-Go claim.

2. **All negotiation is logged.**
   Every response, objection, counter-claim, and contribution offer is part of the record.

3. **The record is append-only.**
   Old states are not deleted. They are superseded.
   You can always see the full history of a Claim.

4. **Anyone can read the full sutable.**
   There is no privileged reader.

5. **Writes require identity.**
   You must have a contributor ID (DID or pseudonym) to add to the sutable.
   Anonymous writes are not accepted.

---

## Sutable Entry Format

Each entry in the sutable is either:
- A **Claim** (see CLAIM_FORMAT.md)
- A **Contribution** (see CONTRIBUTION_SPEC.md)
- A **Response** (objection, counter-claim, endorsement)
- A **Feedback** (reality feedback after execution attempt)

```json
{
  "entry_type": "claim | contribution | response | feedback",
  "entry_id": "string",
  "claim_id": "string — which claim this entry belongs to",
  "author_id": "string — DID or pseudonym",
  "timestamp": "ISO 8601",
  "content": { ... },
  "supersedes": "string — entry_id of the previous version, if updating"
}
```

---

## In This Implementation

In the current minimal implementation, the sutable is a directory of JSON files.

```
sutable/
├── claims/
│   └── {claim_id}.json
├── contributions/
│   └── {contribution_id}.json
├── responses/
│   └── {response_id}.json
└── feedback/
    └── {feedback_id}.json
```

Git provides the append-only property and the public audit trail.
Every commit is a timestamped, author-identified entry to the sutable.

---

## Future Directions

The sutable could be implemented on:
- Git (current)
- IPFS (content-addressed, decentralized)
- gitlawb (DID-signed, federated)
- Any system that guarantees append-only public access

The protocol does not require a specific implementation.
It requires the properties listed above.
