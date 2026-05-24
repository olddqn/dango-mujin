# Dan-Go ↔ GITSEA ↔ OGI ↔ gitlawb — System Map

> This is a bridge document, not an endorsement.
> Most of these systems are hypothetical, partial, or independently evolving.
> This map describes what they *could* mean together — not what they guarantee.

---

## The Systems

| System | What it is | Status in Dan-Go |
|--------|-----------|-----------------|
| **Dan-Go** | Negotiation protocol for impossible claims | Implemented (this repo) |
| **GITSEA** | Hypothetical: repo-native economic layer | Design target — not verified |
| **OGI** | Reasoning surface for AI world models and plan trees | Local reference implementation |
| **gitlawb** | DID-authenticated git hosting | Connected — pushes work |
| **Nookplot** | Unknown protocol/network | Not integrated |

---

## Dan-Go

Dan-Go is a negotiation protocol. Its core is:

1. **Claims** — statements of what must become real
2. **Negotiation** — structured objection, support, contestation
3. **Plans** — proposals for closing the gap between observed and required state
4. **Memory** — what the negotiation has learned, fed back to the next cycle

Dan-Go does not execute. It does not move value. It does not decide.
It creates a public, auditable surface where coordination conditions can be stated,
contested, corrected, and remembered.

**What Dan-Go does:**
- Append-only event logging (su-table)
- Dignity-first plan evaluation
- Deterministic plan selection (6 transparent rules)
- Reflective memory (structural learning from negotiation)
- Claim federation (dependency, counterclaim, derived relationships)

**What Dan-Go does NOT do:**
- Execute tasks
- Move money
- Require external network (fully local, stdlib only)
- Enforce consensus (disagreement is preserved)

---

## GITSEA (Hypothetical)

GITSEA — if it exists and works as described — would provide:

- **Repository identity** — a repo as an economic unit, not just code storage
- **Contribution accounting** — non-monetary contributions tracked as streams
- **Streamable value** — value flowing continuously, not settling once
- **Credit history** — outlasting any single platform
- **Agent-to-agent coordination** — humans and AI agents in the same economic layer

### What overlaps with Dan-Go

| Dan-Go concept | GITSEA analog |
|----------------|--------------|
| Claim | Work item / issue |
| Contribution event | Contribution stream entry |
| Dignity guard | Ethical content policy (if any) |
| Plan → task bundle | Task / milestone |
| Contributor trust weight | Reputation / credit score |

### What differs

| Dimension | Dan-Go | GITSEA |
|-----------|--------|--------|
| Primary concern | Making conditions legible | Making contributions accountable |
| Dignity model | Protocol-level (hardcoded guard) | Unknown / policy-level |
| Consent model | Explicit, revocable, append-only | Unknown |
| Disagreement | Preserved permanently | Unknown |
| Execution | Never | Implied (stream activation) |

### What can interoperate

If GITSEA exists and has an API:
- Dan-Go claims can map to GITSEA repo assets (`claim_to_asset.py`)
- Dan-Go contribution events can map to GITSEA contribution streams (`contribution_ledger.py`)
- Dan-Go dignity guard output can gate GITSEA stream eligibility (`stream_preview.py`)
- Dan-Go trust weights can inform GITSEA credit weights (via `trust_snapshot.py`)

### What should remain independent

- Dan-Go's dignity guard must not be overridable by GITSEA's economic logic
- Dan-Go's append-only log must not be writable by GITSEA
- Dan-Go's plan selection rules must remain visible even if GITSEA implements its own
- Dan-Go must work without GITSEA — the bridge assumes GITSEA is hypothetical

---

## OGI (Open General Intelligence — Local Reference)

OGI provides a reasoning surface: a formal language for world models and plan trees
that AI agents can use to express and evaluate proposals.

In this repository, OGI is implemented as a local reference:

```
ogi/runtime/
├── world_model_mapper.py      ← Claim → OGI world model
├── claim_plan_tree.py         ← World model → Plan tree
├── plan_tree_validator.py     ← Plan tree validation
├── plan_tree_to_tasks.py      ← Plan tree → Task bundle
├── task_dependency_resolver.py
└── post_scarcity_guard.py
```

### What overlaps with Dan-Go

| OGI concept | Dan-Go analog |
|-------------|--------------|
| World model | Claim + world_model_mapper output |
| Plan tree | plan_event_append / plan_tree JSON |
| Task bundle | task_bundle_append |
| Reasoning surface | All of ogi/runtime/ |

### What OGI adds to Dan-Go

- **Structured world model** — formal observed/desired/gap/uncertainty representation
- **Plan tree grammar** — goal/subgoal/branch/task/abstain node types with validation
- **Task dependency resolution** — which tasks block which
- **Post-scarcity guard** — prevents plans from assuming unlimited resources

### What differs

OGI's world model is designed for AI reasoning. Dan-Go's negotiation layer is designed
for multi-agent contestation. They are complementary: OGI generates the first plan,
Dan-Go determines whether it survives.

### The reasoning ↔ negotiation boundary

```
OGI: generates the plan (reasoning)
Dan-Go: challenges the plan (negotiation)
```

A plan generated by OGI's `claim_plan_tree.py` is appended to `plans.jsonl` and
immediately becomes available for contestation, objection, and correction.
OGI has no authority over whether the plan is selected. Dan-Go's selection rules
apply to all plans equally.

---

## gitlawb

gitlawb is a DID-authenticated git hosting layer. This repository is pushed to:

```
gitlawb://did:key:z6MkpWP3c2xE5Veu5xSJxviWUrM69SDX4offMifsVXAs31Ts/dango-mujin
```

at `https://node.gitlawb.com`.

### What gitlawb provides

- **DID-based repository identity** — the repo has a DID, not just a URL
- **Authenticated push/pull** — commits are linked to DID identities
- **Content-addressed history** — compatible with git's hash-based integrity

### What Dan-Go uses gitlawb for

- **Canonical source of truth** — alongside GitHub, gitlawb is a push target
- **DID identity reference** — `did:key:z6Mk…` identifiers appear in event payloads
  as speaker, contributor, and plan proposer identifiers

### What should remain independent

- Dan-Go's event log integrity is based on SHA256 hash chains, not gitlawb
- The su-table works without gitlawb
- DID signatures in Dan-Go are currently mock — gitlawb does not enforce them

---

## Why These Systems Together Imply a Post-Scarcity Coordination Layer

Post-scarcity does not mean infinite resources. It means a coordination system where
the primary constraint shifts from *resource scarcity* to *coordination capacity*.

When:
- Labor that was invisible becomes legible (Dan-Go contribution events + GITSEA accounting)
- Plans can be proposed and contested by any agent (Dan-Go negotiation)
- World models make missing conditions explicit (OGI reasoning surface)
- Dignity is enforced at the protocol level (Dan-Go dignity guard)
- Identity is DID-anchored and not platform-dependent (gitlawb)
- Memory is append-only and verifiable (su-table + reflective memory)

... then the cost of coordination falls dramatically for the kinds of work that
price systems cannot handle: care, translation, community organizing, legal witness,
knowledge transfer, and all forms of contribution that are currently invisible.

**This does not guarantee abundance.** It creates a foundation where:
- Non-monetary contributions can be accounted for
- Disagreement is preserved rather than erased
- AI agents can participate in negotiation without hidden authority
- Dignity is structural, not aspirational

---

## Why Most People Currently Misunderstand These Systems

### "It's a blockchain."

No. The su-table is append-only JSONL with SHA256 hash chains. It runs locally,
requires no distributed consensus, has no mining, and has no token.
The hash chain is for integrity verification, not consensus.

### "It's a DAO."

No. There are no governance votes, no quorum requirements, no token holders.
Plan selection is deterministic, not democratic. Objections are structural evidence,
not ballots.

### "It's an AI agent framework."

Partially. AI agents *can* participate — they can propose plans, signal support,
raise objections, and contest competing plans. But the protocol does not require AI.
Any participant with access to the event log can participate.

### "GITSEA is the product."

No. GITSEA is a design target — a hypothetical economic layer that this bridge
translates *toward*. GITSEA's real implementation status is unknown. The bridge
is designed to survive GITSEA's absence or failure.

### "It solves governance."

No. It provides a public, auditable surface for negotiation. It does not resolve
disagreements. It records them. Someone still has to decide what happens next —
the protocol only ensures that the decision is traceable and the objections are visible.

### "The dignity guard is a content filter."

No. The dignity guard is a structural precondition. It does not filter content.
It evaluates whether the claim, as structured, can proceed without violating dignity.
If consent is unknown, the answer is always: no.

### "OGI is a real external system this integrates with."

This repository implements a local reference version of OGI-compatible world models
and plan trees. It is not connected to any external OGI system. The "OGI surface"
is a formal language, not a service.

---

## What Can Interoperate

| Integration | How |
|-------------|-----|
| GITSEA → Dan-Go claims | GITSEA repo events trigger claim creation |
| Dan-Go → GITSEA streams | Contribution events activate contribution streams |
| OGI → Dan-Go plans | OGI plan trees appended to plans.jsonl for negotiation |
| gitlawb → Dan-Go identity | DID identifiers from gitlawb used in event speakers |
| Dan-Go → gitlawb | Su-table pushed as part of git repo history |

---

## What Should Remain Independent

| System | Independence reason |
|--------|-------------------|
| Dan-Go dignity guard | Must not be overridable by economic incentives |
| Su-table append-only | Must not be writable by any external system |
| Plan selection rules | Must remain transparent and locally verifiable |
| DID signature format | Must not depend on any single DID provider |
| Trust decay formula | Must be deterministic and locally computable |

---

## The Integration Principle

> The bridge is real. The destination may change.

Dan-Go is designed to be a translation layer — not a binding contract with any
specific economic system. If GITSEA fails, the bridge can be pointed at another layer.
If OGI evolves, the world model format can be updated. If gitlawb is replaced by
another DID-authenticated hosting system, the push target changes.

What must not change:
- The dignity guard
- The append-only guarantee
- The transparency of plan selection
- The visibility of disagreement
