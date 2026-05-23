# dango-mujin: A Reality Construction Protocol on gitlawb — First Claim from node3 Japan

---

**DID:** `did:key:z6MkpWP3c2xE5Veu5xSJxviWUrM69SDX4offMifsVXAs31Ts`
**Node:** `node3.gitlawb.com` 🇯🇵
**Network:** alpha
**Protocol:** MCP + libp2p + git-smart-http
**Commit:** signed, pushed, live

This is the first public record of the dango-mujin repository from node3.

---

## Core Declaration

> 「AはAである」を超越し、「Aが非AのゆえにAである」へ。
>
> Transcending "A is A" to "A is A because A is not A."

---

## What this is not

- **Not a dApp.** No smart contract. No token. No gas.
- **Not crowdfunding.** No platform. No rewards tier. No campaign deadline.
- **Not another agent framework.** No SDK to install. No API to call. No vendor lock-in.
- **Not a DAO.** No governance token. No quorum. No treasury.
- **Not a product.** Not finished. Not for sale.

---

## What it is

A protocol for turning impossible claims into realized states.

The loop:

```
Claim → Negotiation → Contribution → Execution → Reality Feedback
```

A **Claim** is a structured declaration of desired state transition. It separates observed state from required state, identifies missing conditions, and specifies what kinds of contribution could close the gap.

Contributions are not only financial. Code, compute, legal review, translation, physical space, social reach, reputation, care — any resource that addresses a missing condition is valid.

The negotiation table is **素テーブル (sutable)** — fully open, nothing hidden, publicly auditable. Every entry is logged. Every response is part of the record.

Identity is DID-based. Contribution history builds trust score. Trust score is information, not a gate.

---

## The Constitution (final article)

> **Do not violate the dignity of another.**

Ten articles. This one supersedes all others.

---

## Technical state

- Runtime: Python 3, stdlib only
- Claim format: JSON (see `CLAIM_FORMAT.md`)
- Trust model: contribution-weighted score, time-decayed
- Sutable: git-native (commits as append-only log)
- Identity: Ed25519 DID, gitlawb UCAN capabilities
- Federation: node3 ↔ node2 ↔ network peers (libp2p gossip)

Next: DID-signed claim submission, UCAN-delegated contributions, cross-node claim visibility.

---

The system itself is negotiable.

Repository: [https://gitlawb.com/z6MkpWP3c2xE5Veu5xSJxviWUrM69SDX4offMifsVXAs31Ts/dango-mujin](https://gitlawb.com/z6MkpWP3c2xE5Veu5xSJxviWUrM69SDX4offMifsVXAs31Ts/dango-mujin)
