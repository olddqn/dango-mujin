# dango-ogi-bridge

> This is not an OGI integration yet.
> It is a Dan-Go compatibility layer for post-scarcity agent economies.

---

Robotics and physical machine control are explicitly out of scope for this bridge.

---

## What This Is

This layer translates between:

- **Dan-Go** — a public negotiation protocol for impossible-to-real state transitions
- **OGI-style agent economies** — post-scarcity coordination environments where
  money becomes less central and contribution, trust, and coordination become
  the primary signals of value

The bridge is conceptual and structural.
It does not connect to any OGI network.
It does not issue tokens.
It does not move money.
It does not control machines.

It maps Dan-Go primitives — Claim, Negotiation, Contribution, Reality Feedback —
to the concepts that a post-scarcity agent economy would need to operate:
agent tasks, credit signals, coordination protocols, and outcome records.

---

## Why This Exists

OGI imagines an economy where AI agents and humans cooperate
after money loses its position as the primary coordination mechanism.

Dan-Go already treats coordination as the hard problem:
> "What would need to change for this impossible claim to become real?"

When the answer to that question is no longer "money" —
when the answer is "consent, contribution, dignity, trust, and transparent negotiation" —
Dan-Go becomes the natural protocol layer for an OGI-style economy.

This bridge prepares for that connection.

---

## Quick Start

```bash
# Transform a Dan-Go Claim into an OGI-style agent task
python runtime/claim_to_agent_task.py examples/post-scarcity.claim.json

# Map contributions to credit signals
python runtime/contribution_to_credit.py examples/contribution-credit.json

# Run post-scarcity exploitation guard
python runtime/post_scarcity_guard.py examples/post-scarcity.claim.json

# Map reality feedback to OGI outcome record
python runtime/reality_feedback_mapper.py examples/reality-feedback.json
```

---

## Structure

```
bridge/ogi/
├── README.md                     — This file
├── DANGO_OGI_THESIS.md           — Central thesis: coordination as the scarce resource
├── POST_SCARCITY_COORDINATION.md — What changes when money loses central meaning
├── CLAIM_TO_AGENT_TASK.md        — Claim → OGI agent task specification
├── CONTRIBUTION_TO_CREDIT.md     — Non-monetary contribution → credit signal mapping
├── AGENT_ECONOMY_MAPPING.md      — Dan-Go primitive ↔ OGI concept table
├── OGI_COMPATIBILITY_NOTES.md    — What is connected, what is not, and why
├── examples/
│   ├── post-scarcity.claim.json  — Example Claim in post-scarcity context
│   ├── agent-task.json           — Example OGI-style agent task
│   ├── contribution-credit.json  — Example contribution → credit mapping
│   └── reality-feedback.json     — Example reality feedback for OGI mapping
└── runtime/
    ├── claim_to_agent_task.py    — CLI: Claim → agent task
    ├── contribution_to_credit.py — CLI: contribution → credit signal
    ├── post_scarcity_guard.py    — CLI: exploitation / false-abundance guard
    └── reality_feedback_mapper.py — CLI: reality feedback → OGI outcome
```

---

## Out of Scope (Explicitly)

- Robotics and physical machine control
- Real network connections to OGI nodes
- Token issuance or cryptographic asset creation
- Wallet management or signing
- Real financial transactions
- Personal identity storage
- Investment advice or solicitation
- Automated trading or arbitrage

---

## Principles Inherited from Dan-Go

1. Dignity before efficiency. Always.
2. Consent is required. Automation without consent is blocked.
3. Corrections are appended, not deleted.
4. Coordination is the hard problem. Money is one solution among many.
5. Reality feedback closes the loop. Intent is not outcome.
6. The protocol is public. Negotiation is public. Memory is public.
