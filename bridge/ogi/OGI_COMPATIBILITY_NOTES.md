# OGI Compatibility Notes

> Honest accounting of what is connected, what is not, and why.

---

## What This Bridge Actually Does

This bridge translates **concepts and data structures**.

It does not:
- Connect to any OGI network or node
- Issue tokens or credit in any live system
- Move money or assets
- Communicate over any network protocol
- Access any external API

It does:
- Define the mapping between Dan-Go primitives and OGI-style concepts
- Provide Python runtime for the transformation (standard library only)
- Produce JSON output suitable for a future OGI adapter
- Document the dignity constraints that must survive any OGI integration

---

## OGI Implementation Status

The exact implementation status of OGI is unverified.

This bridge does not assume OGI exists in a working form.
It treats OGI as a **reference architecture** — a description of what a
post-scarcity agent economy would need, and how Dan-Go would fit into it.

If OGI exists and is accessible:
- This bridge's output format can serve as the handoff layer
- The dignity constraints defined here must be respected by any real OGI integration
- The su-table JSONL format is directly usable as shared memory

If OGI does not yet exist:
- This bridge still has value as a conceptual specification
- It can be adapted to any equivalent protocol (other agent economies, DAOs, etc.)
- The dignity constraints and post-scarcity guard are reusable regardless

---

## Connected

| Concept | Connection | How |
|---|---|---|
| Dan-Go Claim | OGI Agent Task | `claim_to_agent_task.py` |
| Dan-Go Contribution | OGI Credit Signal | `contribution_to_credit.py` |
| Dan-Go Reality Feedback | OGI Outcome Record | `reality_feedback_mapper.py` |
| Dan-Go Dignity Guard | Post-scarcity exploitation boundary | `post_scarcity_guard.py` |
| Su-table JSONL | Shared economic memory | direct format compatibility |
| Trust modes | Agent access levels | mapping table in `AGENT_ECONOMY_MAPPING.md` |

---

## Not Connected (Explicitly)

| Dan-Go / OGI element | Why not connected |
|---|---|
| GITSEA stream assets | GITSEA implementation status unverified; not OGI-specific |
| Repo assets | GITSEA-specific structure; no OGI equivalent defined |
| Robotics / machine control | Explicitly out of scope for this bridge |
| Cryptographic token issuance | Prohibited; not needed for this layer |
| Real monetary transactions | Prohibited; credit signals are records, not payments |
| Live OGI API calls | Not attempted; OGI network status unverified |
| Agent-to-agent direct communication | Protocol-level; not yet defined |
| Claim federation | Cross-claim dependencies not yet modeled |
| Temporal trust decay | Would require time-series credit analysis; not yet implemented |
| Negotiation graph → OGI visualization | Graph format exists; OGI visual layer not defined |

---

## Dignity Constraints That Must Survive OGI Integration

These are non-negotiable. Any real OGI integration must preserve them:

1. **No automation without consent** — agents cannot act on a person's behalf without explicit, revocable consent
2. **No identity exposure** — contributor identity is never exposed without explicit consent
3. **No monetizing vulnerability** — exploiting distress, poverty, or displacement to extract value is blocked
4. **Correction is not deletion** — all records are append-only; corrections are events, not erasures
5. **Dignity violation halts processing** — `dignity_violation_detected` stops all automated processing immediately
6. **Revocable participation** — any participant can withdraw at any time; contributions up to that point are credited but no further work is required
7. **Fair participation** — if funding is involved, revenue sharing must be explicit and agreed before execution

If a proposed OGI integration would require violating any of these,
the integration should not proceed.

---

## Known Gaps

### Identity Scheme Mismatch

Dan-Go uses DIDs (`did:key:z6Mk...`) or pseudonyms.
OGI may use a different identity scheme.

**Current state:** This bridge preserves Dan-Go DID format.
An identity adapter layer would be needed for a real OGI integration.

### Credit Signal Exchangeability

Dan-Go does not define how credit signals are exchanged between agents.
CONTRIBUTION_TO_CREDIT.md defines the credit signal format but not the exchange protocol.

**Current state:** Credit signals are records in JSON format.
An exchange protocol (if needed) would be defined in a future spec.

### Multi-Agent Negotiation Routing

Dan-Go's negotiation model is public and append-only.
OGI may have mechanisms for routing tasks to specific agents based on capability matching.

**Current state:** This bridge produces `required_capabilities` in the agent task.
Capability matching and task routing are not yet implemented.

### Temporal Trust Decay

Credit signals currently have no time dimension.
An older contribution does not decay; a newer one is not weighted higher.

**Current state:** Noted as a future implementation step.
See `AGENT_ECONOMY_MAPPING.md` for the concept; `runtime/` does not yet implement it.

---

## How to Extend This Bridge

When an OGI implementation becomes available:

1. **Add a network adapter** — translate JSON output from `claim_to_agent_task.py` to OGI API calls
2. **Add an identity adapter** — translate DIDs to OGI identity format
3. **Add a real-time listener** — watch the su-table JSONL for new events and forward them
4. **Preserve the dignity guard** — `post_scarcity_guard.py` must run before any OGI API call
5. **Add credit signal routing** — forward credit signals to OGI's contribution tracking layer

None of these extensions modify the core Dan-Go protocol.
The su-table remains the source of truth.
The dignity guard remains non-negotiable.

---

## Explicit Non-Endorsements

This bridge does not endorse:
- OGI as an investment vehicle
- OGI's economic claims (post-scarcity arrival timeline)
- Any specific OGI implementation
- The view that AI agents are equivalent to human participants in all respects
- The view that money is obsolete

It endorses only:
- The value of non-monetary contribution tracking
- Dignity as a non-negotiable constraint in any economic system
- Public, append-only negotiation as a coordination protocol
- The possibility of designing economic systems where money is not the only signal

These are design principles, not predictions.
