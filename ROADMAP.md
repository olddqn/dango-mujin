# Roadmap

Status: Protocol Draft (v0.1.0)

This roadmap is itself subject to public negotiation.
It is a current proposal, not a commitment.

---

## Current State (v0.1.0)

- [x] Protocol specification (MUJIN_PROTOCOL.md)
- [x] Claim format (CLAIM_FORMAT.md)
- [x] Contribution specification (CONTRIBUTION_SPEC.md)
- [x] Trust model (TRUST_MODEL.md)
- [x] Sutable specification (SUTABLE_SPEC.md)
- [x] Constitution (CONSTITUTION.md)
- [x] Minimum Python runtime (claim_matcher, contribution_router, trust_score, reality_feedback)
- [x] Example claims (housing, ai-film, refugee-support, local-food-network)

---

## Near Term (v0.2.0)

- [ ] Sutable directory structure (claims/, contributions/, responses/, feedback/)
- [ ] CLI for submitting and querying claims
- [ ] Contribution matching improved (fuzzy match on condition keywords)
- [ ] Basic dispute resolution workflow
- [ ] gitlawb integration: Claims as git-signed JSON objects

---

## Medium Term (v0.3.0)

- [ ] DID-signed claim submission
- [ ] UCAN-based contribution delegation (one agent contributes on behalf of another)
- [ ] Trust score persistence and history
- [ ] Counter-claim and objection format
- [ ] Cross-node federation (claims visible across gitlawb nodes)

---

## Long Term (v1.0.0)

- [ ] Web interface for browsing claims (read-only)
- [ ] API for agents to submit and query claims programmatically
- [ ] Protocol amendment system (Claims about the protocol itself)
- [ ] YacypherPunks directory (opt-in participant registry)
- [ ] Multi-language support (protocol docs and CLI)

---

## What Will NOT Be Built

- Investment or financial instruments
- Token issuance or ICO
- Platform lock-in
- Governance by token holders
- Any mechanism that gives more power based on wealth

---

## How to Influence This Roadmap

Submit a Claim.

If you think something should be prioritized, deprioritized, or replaced:
1. Write a Claim describing the desired state transition
2. Describe what is missing and what you can contribute
3. Open it as an issue or pull request on this repository

The roadmap will be updated based on negotiated agreement, not unilateral decision.
