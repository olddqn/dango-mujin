# Dan-Go Mujin Protocol

> **Dan-Go Mujin Protocol is not crowdfunding.**
> It is a public negotiation protocol for turning impossible claims into reality.

**gitlawb (decentralized):** [https://gitlawb.com/z6MkpWP3c2xE5Veu5xSJxviWUrM69SDX4offMifsVXAs31Ts/dango-mujin](https://gitlawb.com/z6MkpWP3c2xE5Veu5xSJxviWUrM69SDX4offMifsVXAs31Ts/dango-mujin)

---

## What is a Claim?

A claim is not true or false by default.
**A claim is a proposed state transition.**

The protocol asks:

- What is missing?
- Who can help?
- What resources are needed?
- What contradictions exist?
- What can be executed now?
- What must be escalated?
- What must be rejected?

## Core Loop

```
Claim → Negotiation → Contribution → Execution → Reality Feedback
```

## Ordinary crowdfunding vs Dan-Go Mujin

| Crowdfunding | Dan-Go Mujin |
|---|---|
| Collect money | Submit a Claim |
| Return rewards | Decompose required conditions |
| Platform decides | Negotiation decides |
| Money only | Code, compute, translation, housing, legal review, distribution, social reach, reputation, care |

## Inspiration

Dan-Go Mujin is inspired by the Japanese concept of **無尽 (mujin)**:
a rotating mutual-credit association based on trust, contribution, and shared realization.

**Dan-Go (談合)** is not corruption.
It is **public resonance, agreement formation, and cooperative design**.

This version is for AI agents and humans working together:
not only money, but any form of contribution can become part of the negotiation.

## Key Concepts

| Term | Meaning |
|---|---|
| **Dan-Go** | Public negotiation — not secret collusion |
| **Lie** | An unrealized state transition, not an error to be eliminated |
| **Impossible** | A state where not enough negotiation has happened yet |
| **素テーブル (sutable)** | A fully open state table — no hidden information |
| **YacypherPunks** | A cooperative community beyond national and institutional boundaries |
| **第零国家 (State Zero)** | A second affiliation that sits on top of existing states without destroying them |
| **Constitution** | One clause: Do not violate the dignity of another |

## Participation

- Fork this repo
- Submit a Claim (see `CLAIM_FORMAT.md`)
- Contribute to an open Claim
- Object, counter-claim, or propose alternatives
- All are valid participation

## Quick Start

```bash
# Read a claim and see what is missing
python runtime/claim_matcher.py examples/housing.claim.json

# Route contributions to missing conditions
python runtime/contribution_router.py examples/housing.claim.json

# Check trust score from contribution history
python runtime/trust_score.py

# Record execution feedback
python runtime/reality_feedback.py
```

## Structure

```
dango-mujin/
├── README.md              — This file
├── CONSTITUTION.md        — The one law
├── MUJIN_PROTOCOL.md      — Full protocol specification
├── CLAIM_FORMAT.md        — How to write a Claim
├── CONTRIBUTION_SPEC.md   — What counts as a contribution
├── TRUST_MODEL.md         — How trust is calculated
├── SUTABLE_SPEC.md        — The open state table format
├── ROADMAP.md             — Where this goes next
├── examples/              — Sample claims
└── runtime/               — Minimum viable Python runtime
```

## Principles

1. Not a finished product. A participable protocol.
2. Dan-Go itself evolves through public negotiation.
3. Forks welcome. Objections welcome. Claims welcome.
4. AI is not a governor. AI is a missionary, mediator, and recorder.
5. Do not present unobserved states as observed.
6. No exaggeration.
7. No private keys, API keys, or seed phrases ever.
8. No investment solicitation. This is a thought and cooperation protocol.
9. Violence, exploitation, and coercion are forbidden means.
10. All negotiation is publicly auditable whenever possible.

---

*Dan-Go Mujin is in protocol-draft state. Everything here is subject to public negotiation.*
