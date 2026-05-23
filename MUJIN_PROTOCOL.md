# Mujin Protocol Specification

Version: 0.1.0-draft
Status: Open for negotiation

---

## Overview

The Mujin Protocol defines how a Claim moves from declaration to reality.

It is not a prediction engine. It is a coordination engine.

---

## Protocol Phases

### Phase 0: Claim Submission

Any participant (human or AI agent) may submit a Claim.

A Claim must contain:
- A unique `claim_id`
- A `statement` of desired state transition
- `observed_state`: what is currently verified true
- `required_state`: what must become true for the claim to be realized
- `missing_conditions`: the gap between observed and required
- `possible_contributions`: types of help that could close the gap
- `risks`: known obstacles and failure modes
- A `constitution_check`: does this violate dignity or use coercion?

A Claim may NOT contain:
- Private keys or credentials
- Investment promises or financial guarantees
- Unverified assertions presented as verified facts

### Phase 1: Negotiation

Once submitted, a Claim enters the negotiation table (素テーブル / sutable).

In this phase:
- Anyone may respond with a counter-claim, objection, or offer
- Missing conditions are matched against available contributions
- Risks are evaluated and documented
- The Claim owner may update the claim in response to feedback

Negotiation decisions:
- `negotiate` — continue, more parties needed
- `execute` — conditions are met, proceed
- `escalate` — requires resources or authority beyond current participants
- `reject` — violates constitution or is fundamentally infeasible

### Phase 2: Contribution

Contributions are not only money.

Valid contribution types:
- `code` — software, scripts, automation
- `compute` — CPU/GPU time, hosting, storage
- `legal` — legal review, contract drafting, compliance check
- `translation` — language, cultural mediation
- `housing` — physical space, shelter, venue
- `funding` — financial resources
- `social_reach` — distribution, network access, amplification
- `reputation` — vouching, endorsement, trust transfer
- `care` — emotional support, facilitation, human presence
- `knowledge` — research, documentation, expertise
- `coordination` — organizing, scheduling, connecting people

Each contribution is logged with:
- contributor_id (DID or pseudonym)
- contribution_type
- claim_id
- timestamp
- description
- verifiable (boolean): can this contribution be independently verified?

### Phase 3: Execution

When sufficient conditions are met, execution begins.

Execution is not managed by the protocol. The protocol only records:
- Who committed to what
- What was executed
- What the reality feedback was

### Phase 4: Reality Feedback

After execution, participants submit feedback:
- `executed` — the action happened as described
- `partial` — some conditions were realized, others were not
- `failed` — execution did not occur; reasons documented
- `pending` — execution has not yet been attempted

Feedback is public and auditable.
It updates the trust scores of contributors.
It informs future claims of similar type.

---

## The Sutable (素テーブル)

The sutable is the open state table of all Claims in the protocol.

Properties:
- All entries are public by default
- No hidden negotiations
- Any participant can read the full state of any Claim
- Edits are logged with timestamps and contributor IDs

The sutable is not a blockchain. It is a social contract enforced by transparency.

---

## Trust in Dan-Go Mujin

Trust is not granted. Trust is accumulated through contribution.

Trust score components:
- Number of contributions submitted
- Ratio of verified to unverified contributions
- Reality feedback: executed vs failed
- Consistency over time

Trust score is not a gate. It is information.
High trust score = more weight in negotiation, not more power to block.

---

## YacypherPunks

YacypherPunks are participants in the Dan-Go Mujin network who:
- Operate across national and institutional boundaries
- Contribute to Claims without requiring formal affiliation
- Hold their identity through DID (Decentralized Identifier), not institution
- Accept the Constitution as their operating constraint

Membership is declared, not granted.
Anyone who accepts the Constitution and submits a verifiable contribution is a YacypherPunk.

---

## State Zero (第零国家)

State Zero is not a nation-state.
It is a second affiliation — a layer that sits on top of existing states without replacing them.

You remain a citizen of wherever you are.
You additionally become a participant of State Zero by accepting the Constitution and contributing to the protocol.

State Zero has no territory, no army, no currency.
It has only: the protocol, the constitution, and the contributions of its participants.

---

## Amendment Process

This protocol may be changed through:
1. A Claim submitted to this repository
2. Public negotiation (minimum 7 days open)
3. No objection that cannot be addressed without violating Article 10
4. Commit with clear record of negotiation history

All amendments must themselves pass the constitution check.
