# Su-table — Append-Only Negotiation Log Specification

> 素テーブル (su-table) — 完全公開状態遷移テーブル

---

## What Is the Su-table?

The su-table is Dan-Go's fully open, append-only state transition record.

It is not a database.
It is not a blockchain.
It is not an audit trail bolted onto a system that operates privately.

It is the negotiation itself — made legible, permanent, and queryable.

In Dan-Go, the negotiation is not separate from the record.
The record **is** the negotiation.

Every claim, every objection, every amendment, every contribution offer,
every execution, every feedback from reality —
all of it is written once, and never erased.

---

## What Is Append-Only?

Append-only means:

1. Events are added. They are never removed.
2. The past is not rewritten. Ever.
3. If something was said, it was said. The log preserves it.
4. If something was wrong, a **correction event** is appended.
   The original remains. The correction points to it.

This is not a technical constraint.
It is a design philosophy.

The question Dan-Go asks is:
> "What actually happened?"

Not:
> "What do we want to say happened?"

---

## Why We Do Not Delete

Deletion is the mechanism of denial.

In negotiation between parties with unequal power,
the stronger party can delete inconvenient history.
The weaker party cannot.

If the su-table allowed deletion:
- An objection could be silenced
- A withdrawal could be erased
- A dignity violation could be hidden
- An amendment that was rejected could be made to look like it never existed

Append-only makes this impossible.

**History is part of the protocol itself.**
Not a byproduct. Not an audit log. The protocol.

---

## Why Correction Events Are Required

Humans make mistakes. Agents make mistakes.

A correction event is the right way to handle them:

```json
{
  "event_type": "correction",
  "claim_id": "housing-001",
  "speaker": "did:key:z6Mkcritic001",
  "corrects_event_hash": "9e83cab09a5dbe4f...",
  "correction_reason": "Previous objection cited wrong statute. Correct statute is Land Use Act §12.",
  "original_still_in_log": true
}
```

The correction:
- References the original event by `event_hash`
- Explains what was wrong
- Does not remove the original
- Is itself permanent

Anyone reading the log can see:
1. What was originally said
2. That it was later corrected
3. Why it was corrected
4. Who made the correction

This is more honest than deletion.
It is also more useful — the original statement is preserved as evidence
of the state of knowledge at that moment.

---

## Negotiation Transparency

The su-table makes negotiation transparent by design.

Every participant can see:
- Who made a claim (`claim_created`)
- Who objected and why (`objection`)
- What amendments were proposed (`amendment`)
- Who supported or opposed (`support`, `withdrawal`)
- What contributions were offered and accepted (`contribution_offer`, `contribution_accepted`)
- What actually happened in reality (`reality_feedback`)

This is called **公開談合** (public negotiation) — not secret bargaining.

Public negotiation is not consensus.
It is not majority rule.
It is the full visibility of who said what, when, and why —
so that the negotiation can be evaluated honestly.

---

## Reputation and Memory

The su-table is not a reputation system.
It does not assign scores.
It does not rank contributors.

But it does preserve memory.

If a party has consistently objected without reason,
that is visible in the log.

If a contributor has consistently completed high-quality work,
that is visible in the log.

If a claim was funded, executed, and succeeded — that is visible.
If a claim was funded, executed, and violated dignity — that is also visible.

Memory is not punishment.
Memory is context.

Dan-Go does not punish past behavior.
Dan-Go makes past behavior legible for future negotiation.

---

## History Is Part of the Protocol

In most systems, history is a byproduct:
"We stored logs in case we need them later."

In Dan-Go, history is constitutive:
"The negotiation only exists because it was recorded."

A claim that was never recorded in the su-table did not happen
as far as Dan-Go is concerned.

A negotiation that was held privately, without public record,
is not a Dan-Go negotiation.
It is a private agreement — which may be valid,
but cannot claim the transparency and auditability of Dan-Go.

This is intentional.

> If you want to negotiate under Dan-Go, you negotiate publicly.
> If you want to negotiate privately, you use a different protocol.
> Both are legitimate. They are different things.

---

## The Five Tables

| Table               | Records |
|---|---|
| `claims.jsonl`         | Claim creation, updates |
| `negotiations.jsonl`   | Objections, amendments, support, escalations, corrections, withdrawals |
| `contributions.jsonl`  | Contribution offers, acceptances, rejections, completions |
| `executions.jsonl`     | Execution start, pause, completion, blocking |
| `reality_feedback.jsonl` | Outcomes: success, partial, failure, unexpected, dignity violation |

---

## Event Anatomy

Every event has:

```json
{
  "event_type": "required — always present",
  "timestamp": "ISO 8601 UTC — auto-generated if absent",
  "event_hash": "sha256 of event body — computed on write",
  "previous_event_hash": "sha256 of previous event in same table — optional chain link"
}
```

Most events also have:
- `claim_id` — which claim this event belongs to
- `speaker` — who made the event (DID or pseudonym)

The `event_hash` enables:
- Tamper detection (was the log modified?)
- Cross-references (correction → original, etc.)
- Chain integrity verification

---

## Chain Integrity

Each table forms a hash chain:

```
event_1  (event_hash: aaa, no previous_event_hash)
event_2  (event_hash: bbb, previous_event_hash: aaa)
event_3  (event_hash: ccc, previous_event_hash: bbb)
```

If any event in the chain is modified, its hash will no longer match
what the next event expects as `previous_event_hash`.

This does not make the su-table a blockchain.
It does not provide Byzantine fault tolerance.
It does not use consensus.

It provides:
- **Local tamper detection**: if the JSONL file is edited, verification catches it
- **Audit traceability**: any event can be located by hash
- **Correction accountability**: corrections must reference a real event hash

---

## Dignity Violations Are Escalated, Not Silenced

If a dignity violation is detected during execution:

```json
{
  "event_type": "reality_feedback",
  "claim_id": "...",
  "result": "dignity_violation_detected",
  "notes": "Identity of participant was exposed without consent.",
  "dignity_violation": true,
  "requires_human_review": true,
  "automated_processing_halted": true
}
```

The violation is:
1. **Recorded** — in the permanent log
2. **Escalated** — flagged for human review
3. **Halting** — automated processing stops
4. **Searchable** — queryable by event_type and result

It is **not** deleted.
It is **not** hidden.
It is **not** excused by subsequent good behavior.

The dignity violation is part of the record.
Any future negotiation involving the same parties will see it.

---

## Absolute Prohibitions

The su-table does not store:

- Private keys or seed phrases
- Real personal identity (names, addresses, biometrics)
- Financial account details
- Real survivor or refugee data
- Any information that creates surveillance risk
- Anything that cannot be safely made public

If it cannot be public, it does not go in the su-table.
Private information belongs in separate, consent-governed storage.
The su-table holds only what is legitimately public under Dan-Go.

---

## Implementation Notes

- Format: JSONL (one JSON object per line, UTF-8, no BOM)
- One table = one `.jsonl` file
- Append is atomic (file lock on write)
- Read is always full-scan or sequential (no indexing required at this scale)
- Git commits serve as additional append checkpoints
- No database required — plain files, plain Python, plain git

---

> The su-table does not promise truth.
> It promises transparency.
> Truth is negotiated between parties.
> The su-table ensures the negotiation cannot be denied.
