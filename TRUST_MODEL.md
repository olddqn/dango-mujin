# Trust Model

Version: 0.1.0-draft

---

## Philosophy

Trust in Dan-Go Mujin is not a gate. It is information.

High trust does not give you power to block others.
Low trust does not prevent you from submitting Claims.

Trust is a signal to other participants about the reliability of your contributions.

---

## Trust Score Components

```
trust_score = (
    verified_contributions * 2.0
  + committed_contributions * 1.5
  + delivered_contributions * 1.0
  + offered_contributions   * 0.5
  - disputed_contributions  * 1.0
  - withdrawn_after_commit  * 2.0
) / max(1, total_contributions) * time_factor
```

**time_factor**: consistency over time matters.
Recent contributions count slightly more than old ones.
A score built over 2 years is more reliable than a burst of activity.

---

## Score Ranges

| Range | Meaning |
|---|---|
| 0.0 – 0.2 | New participant. No history. |
| 0.2 – 0.5 | Early contributor. Some track record. |
| 0.5 – 0.8 | Established contributor. Generally reliable. |
| 0.8 – 1.0 | High trust. Consistent, verified track record. |

---

## What Trust Affects

- **Negotiation weight**: Higher trust contributions receive more attention in sutable discussions.
- **Verification requests**: High-trust participants may be asked to verify others' contributions.
- **Escalation routing**: When claims are escalated, high-trust participants are prioritized for coordination.

---

## What Trust Does NOT Affect

- Right to submit a Claim
- Right to object or counter-claim
- Right to fork the protocol
- Constitutional protections

---

## Identity and Trust

Trust is tied to a contributor ID (DID or pseudonym).

If you change your ID, your trust score does not transfer automatically.
Trust transfer requires:
1. A signed statement from the old ID linking to the new ID
2. A review period (minimum 7 days)
3. No outstanding disputes on the old ID

---

## Disputes

If a contribution is disputed:
1. The dispute is logged publicly
2. Both parties may present evidence
3. Three participants with trust score > 0.5 review the evidence
4. Majority decides the outcome
5. The decision is logged permanently

Disputes reduce trust for false claims, not for genuine disagreements.

---

## Pseudonymous Participation

You may contribute under a pseudonym.

Pseudonymous contributions can still build trust, but:
- They cannot be verified against real-world identity
- They count slightly less toward trust score (0.8x multiplier)
- If the pseudonym is abandoned, trust score is lost

This is a feature, not a bug.
Some contributions require anonymity to be possible at all.
