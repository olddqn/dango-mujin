# Memory Surface Mapping — Dan-Go ↔ OGI

> **Status:** specified (implementation: su-table append-only log)  
> **Storage:** `sutable/*.jsonl`

---

## What Is Memory in an Agent System?

In OGI-style agent cognition, memory is the substrate that allows agents to
act consistently over time. Without memory:
- Agents repeat past mistakes
- Trust cannot be established
- Coordination is stateless (and therefore fragile)
- Outcomes cannot be evaluated against intentions

Dan-Go does not have a "memory module" — but the su-table is memory.
It is append-only, timestamped, hash-chained, and queryable.
This mapping makes the correspondence explicit.

---

## Memory Type Mapping

| OGI Memory Type | Dan-Go Equivalent | Storage | Notes |
|---|---|---|---|
| **Episodic memory** | Individual su-table events | `sutable/*.jsonl` | What happened, to whom, when |
| **Procedural memory** | Plan trees | `ogi/examples/*.output.json` | How to approach a class of problem |
| **Semantic memory** | Spec documents | `bridge/*.md`, `ogi/*.md` | What concepts mean, how the system works |
| **Reflective memory** | Reality feedback summaries | `sutable/reality_feedback.jsonl` | What happened vs. what was expected |
| **Working memory** | Current claim + negotiation graph | in-memory graph (negotiation_graph.py) | Live state of active negotiation |
| **Associative memory** | Federation map | `sutable/federation.jsonl` | Which claims are related to which |

---

## Episodic Memory: Su-table Events

Every event in the su-table is an episodic memory record:
- It captures a specific moment
- It records who was involved (speaker DID, contributor DID)
- It has a timestamp and an event hash
- It is permanently stored (no deletes)

**Tables:**
- `claims.jsonl` — original claims (what was proposed)
- `negotiations.jsonl` — objections, amendments, support (what was contested)
- `contributions.jsonl` — accepted work (what was done)
- `executions.jsonl` — execution records (how execution was attempted)
- `reality_feedback.jsonl` — outcome records (what actually happened)
- `federation.jsonl` — cross-claim relationships (what is connected to what)

**Hash chain integrity:**
Each event links to the previous via `previous_event_hash`, making the
episodic record tamper-evident. Corrupted memories can be detected.

---

## Procedural Memory: Plan Trees

A plan tree is a **procedure** — a structured approach to closing a world
model gap for a class of problem.

Once generated and validated, a plan tree can be:
- Reused for similar claims (with appropriate adaptation)
- Extended via amendment (new plan tree, old one preserved)
- Cited by federation events as the basis for a dependency

Plan trees are NOT stored in the su-table by default (they are generated
fresh from claims). Future implementations may append plan tree events to
a dedicated `plans.jsonl` table.

---

## Semantic Memory: Specification Documents

The markdown spec documents are the system's semantic memory:
- What is a Claim?
- What is a dignity violation?
- What does `abstain` mean?
- How does trust decay work?

Specs are versioned via git. When specs change, the git history is the
semantic memory of what the concepts used to mean and why they changed.

This is why specs are never deleted — only amended.

---

## Reflective Memory: Reality Feedback

Reality feedback events are the system's reflective memory — the record
of what actually happened versus what was expected.

```
Claim: "shared creative base will be established"
  ↓ (negotiation, contribution, execution)
Reality feedback: "partial_success — internet access established, kitchen delayed"
```

This mismatch between intent and outcome is the most valuable memory in the
system. It is how the system (and its participants) learn.

In OGI terms, reality feedback is an **outcome record** that closes the
loop between planning and execution. It feeds back into the world model
for the next planning cycle.

---

## Working Memory: Negotiation Graph

The negotiation graph (built by `negotiation_graph.py`) is the system's
working memory — the live, in-memory state of an active claim.

It is:
- Ephemeral (generated fresh on each query)
- Comprehensive (includes all su-table events for a claim)
- Queryable (by event type, speaker, timestamp, trust weight)
- Not stored (the su-table is the source of truth)

Working memory in Dan-Go is intentionally ephemeral. Persistence is the
su-table's job. Computation is the graph's job.

---

## Associative Memory: Federation Map

The federation map (built by `claim_federation.py` from `federation.jsonl`)
is the system's associative memory — it answers the question:

> "What does this claim connect to?"

Federation links are the associative bonds between episodic memories (claims).
They allow the system to reason about cross-claim dependencies without
duplicating information in each claim.

---

## Memory Integrity Properties

| Property | Mechanism | Notes |
|---|---|---|
| **Immutability** | Append-only JSONL | Events are never overwritten |
| **Tamper detection** | SHA256 hash chain | `event_hash` + `previous_event_hash` |
| **Attribution** | DID speaker field | Who said what (mock, not real crypto) |
| **Temporal ordering** | Timestamps + chain order | When things happened |
| **Trust weighting** | Temporal trust decay | How much to weight old contributions |
| **Signature** | Mock Ed25519 | Which events were intentionally signed |

---

## What Memory Cannot Do

- **Forget** — the su-table has no delete operation
- **Update** — events are immutable; corrections are new events
- **Merge** — two su-tables cannot be merged automatically
- **Verify DIDs** — mock signatures only, no real DID resolution
- **Store secrets** — everything in the su-table is plaintext JSONL
- **Search full-text** — no index; search via grep or Python filter

These constraints are features, not bugs. They reflect the design philosophy:
what was recorded cannot be unrecorded. Memory is a responsibility.
