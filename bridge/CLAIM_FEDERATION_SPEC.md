# Claim Federation Spec — dango-gitsea-bridge

> **Status:** implemented  
> **Module:** `runtime/claim_dependency.py`, `runtime/claim_federation.py`,
> `runtime/federation_graph.py`, `runtime/federation_snapshot.py`  
> **Su-table:** `sutable/federation.jsonl`

---

## Why Federation?

Claims are not isolated statements. In a public negotiation protocol, claims
build on each other, contradict each other, refine each other, and depend on
each other becoming real.

A single claim like "this vacant house can become a shared creative space"
immediately creates a network:

- Another claim (internet access) **depends on** it being established first.
- A safety reviewer **counterclaims** it until structural assessment is done.
- A community kitchen claim is **enabled by** the shared space governance.
- A safety remediation claim is **derived from** the counterclaim.

Without a federation layer, these relationships exist only in human memory.
The federation su-table makes them machine-readable, traversable, and auditable.

---

## Core Design Principles

### 1. Disagreement is not failure

A `counterclaim` does not block or invalidate the original claim. It records
that someone publicly disagreed, with a stated reason, at a specific moment.
The original claim remains in the log. Both the claim and its counterclaim
can advance in parallel.

**Counterclaims are always permitted.** There is no circular-detection check
for counterclaims. A counterclam against something that counterclaims you is
a legitimate negotiation move — not a cycle.

### 2. The network is a reality graph

The federation map is not a workflow state machine. It does not enforce
execution order. It records *relationships as they were declared*, so that:

- Anyone can query what a claim depends on before committing resources
- Reality-feedback events can be traced back through the dependency chain
- Derived claims can acknowledge their origin without erasing it

### 3. Federation ≠ consensus

Federation records divergence. A claim with five counterclaims is not
"more invalid" than one with none — it is simply *more contested*. The
depth and breadth of federation is a signal, not a verdict.

### 4. Dignity override is a special case

A `dignity_override` relationship means the target claim's dignity constraints
are overridden by the source claim. This is a strong governance signal and
triggers circular detection: if A dignity-overrides B, then B cannot
dignity-override A in the same network.

---

## Su-Table: `federation.jsonl`

Location: `sutable/federation.jsonl`

The federation table is an append-only JSONL file. Each line is one event.
Events are linked by `event_hash` / `previous_event_hash` (same hash-chain
protocol as other su-tables).

**Append via:**
```bash
python runtime/claim_dependency.py examples/claim-dependency.json --append
```

---

## Relationship Types

| Type             | Direction       | Circular check | Description |
|------------------|-----------------|---------------|-------------|
| `depends_on`     | A → B           | ✓ checked     | A cannot proceed without B being established |
| `enables`        | B enables A     | ✗             | B (upstream) makes A (downstream) possible |
| `blocks`         | B blocks A      | ✓ checked     | B prevents A from proceeding |
| `counterclaim`   | A contests B    | ✗             | A publicly disputes B; both preserved |
| `amendment_of`   | A amends B      | ✗             | A modifies B; B still exists |
| `derived_from`   | A derives B     | ✗             | A is derived from B's content or outcome |
| `federation_link`| A ↔ B symmetric | ✗             | Symmetric association; stored both ways |
| `dignity_override`| B overrides A  | ✓ checked     | B overrides dignity constraints for A |
| `correction_of`  | A corrects A    | ✗             | Self-referential correction event |

### Semantic convention for `claim_dependency` events

In the `claim_dependency` event schema:
- `claim_id` = the **downstream** claim making the statement
- `depends_on_claim_id` = the **upstream** claim being referenced

For `dependency_type: "enables"`, this means:
> "The upstream claim (`depends_on_claim_id`) enables the downstream claim (`claim_id`)."

The federation map stores this correctly:
```
fmap[upstream].enables   = [downstream, ...]
fmap[downstream].enabled_by = [upstream, ...]
```

---

## Event Schema

### `claim_dependency`
```json
{
  "event_type": "claim_dependency",
  "claim_id": "housing-004",
  "depends_on_claim_id": "housing-001",
  "dependency_type": "enables",
  "reason": "The shared creative base enables the community kitchen claim.",
  "timestamp": "2026-05-24T01:00:00Z"
}
```

### `counterclaim`
```json
{
  "event_type": "counterclaim",
  "claim_id": "housing-003",
  "counterclaim_to": "housing-001",
  "reason": "Building safety review is incomplete.",
  "speaker": "did:key:mock-safety-reviewer",
  "timestamp": "2026-05-24T02:00:00Z"
}
```

### `federation_link`
```json
{
  "event_type": "federation_link",
  "claim_id": "housing-002",
  "linked_claim_id": "housing-004",
  "reason": "Co-located projects sharing participant coordination.",
  "timestamp": "2026-05-24T03:00:00Z"
}
```

### `federation_correction`
```json
{
  "event_type": "federation_correction",
  "claim_id": "housing-003",
  "reason": "Updated reasoning after safety inspection was completed.",
  "timestamp": "2026-05-24T05:00:00Z"
}
```

---

## Circular Dependency Detection

Circular detection applies only to directional relationship types:
`depends_on`, `blocks`, `dignity_override`.

**Rule:** If adding edge A→B would make B reachable from A via already-recorded
edges of the same type, the event is rejected.

**Rejected:**
```
housing-001 depends_on housing-002   # already in log
housing-002 depends_on housing-001   # REJECTED: would create cycle
```

**Allowed (different types):**
```
housing-003 counterclaim housing-001   # allowed
housing-001 derived_from housing-003  # allowed — different type
```

**Self-reference** (`claim_id == depends_on_claim_id`) is always rejected,
regardless of type.

---

## Federation Map Structure

`build_federation_map(events)` returns:

```python
{
  "housing-001": {
    "depends_on":       [],             # outgoing: A depends on
    "enables":          ["housing-004"],# outgoing: A enables (A is upstream)
    "blocks":           [],
    "counterclaims":    [],
    "amendment_of":     [],
    "derived_from":     [],
    "federation_link":  [],
    "dignity_override": [],
    "correction_of":    [],
    # Incoming (reverse):
    "enabled_by":       [],
    "blocked_by":       [],
    "counterclaimed_by":["housing-003"],
    "depended_on_by":   ["housing-002"],
  },
  ...
}
```

---

## Federation Depth

`compute_federation_depth(claim_id, fmap)` returns the maximum number of
hops reachable by following outgoing `enables`, `depends_on`, `derived_from`,
and `amendment_of` edges.

- Depth 1 = leaf claim (no outgoing edges of tracked types)
- Depth 2 = enables or depends_on one other claim with no further edges
- Higher = deep dependency chain

Max depth is capped at 20 to prevent runaway on large networks.
Visited nodes are tracked to handle any remaining non-circular paths.

---

## CLI Reference

### `claim_dependency.py` — Validate and append a single event

```bash
# Validate only (exit 0 = valid, exit 1 = invalid)
python runtime/claim_dependency.py examples/claim-dependency.json

# Validate and append to sutable/federation.jsonl
python runtime/claim_dependency.py examples/claim-dependency.json --append

# Validate only, no append (explicit)
python runtime/claim_dependency.py examples/claim-dependency.json --check-only
```

**Output (JSON):**
```json
{
  "valid": true,
  "reason": "ok",
  "event": { ... }
}
```

### `claim_federation.py` — Build and query the federation map

```bash
# All claims from su-table
python runtime/claim_federation.py

# From an event file
python runtime/claim_federation.py examples/claim-federation.json

# Single claim summary
python runtime/claim_federation.py --claim-id housing-001
python runtime/claim_federation.py examples/claim-federation.json --claim-id housing-001
```

### `federation_snapshot.py` — Per-claim federation snapshot

```bash
# Compact (counts only)
python runtime/federation_snapshot.py --claim-id housing-001

# Full detail
python runtime/federation_snapshot.py --claim-id housing-001 --verbose

# All claims (compact)
python runtime/federation_snapshot.py --all-claims

# All claims (verbose)
python runtime/federation_snapshot.py --all-claims --verbose
```

### `federation_graph.py` — Build and export the federation graph

```bash
# Text from su-table
python runtime/federation_graph.py --format text

# Text from event file
python runtime/federation_graph.py examples/claim-federation.json --format text

# Mermaid from su-table
python runtime/federation_graph.py --format mermaid

# Save to file
python runtime/federation_graph.py examples/claim-federation.json \
  --format mermaid --output examples/federation.graph.mmd
```

---

## Programmatic API

```python
from claim_federation import (
    load_federation_events,   # → list[dict]  (reads sutable/federation.jsonl)
    build_federation_map,     # (events) → dict[claim_id, dict]
    get_claim_summary,        # (claim_id, fmap) → dict
    list_claim_ids,           # (fmap) → list[str]
    compute_federation_depth, # (claim_id, fmap, max_depth=20) → int
)

from claim_dependency import (
    validate_federation_event,   # (event, existing_events) → (bool, str)
    append_federation_event,     # (event) → None
)

from federation_graph import (
    build_graph,    # (events) → {nodes, edges, meta, fmap}
    export_mermaid, # (graph) → str
    export_text,    # (graph) → str
)
```

---

## Federation-Aware Branching Extension

This spec covers the base federation layer: dependency relationships, federation map,
graph traversal, depth computation, and the `federation.jsonl` event log.

The **federation-aware plan branching layer** extends this with:

- **Branch status computation** (`active` / `paused` / `blocked` / `unknown`)
  derived from upstream negotiation state. See `runtime/federation_branching.py`.

- **Condition propagation** — When upstream claim reaches active plan state,
  its plan-tree conditions propagate to downstream claims as advisory events.
  See `runtime/federation_condition_propagation.py`.

- **Dignity propagation** — A `dignity_violation` objection on upstream propagates
  `blocked` status to all dependent claims immediately.

- **Ripple detection** — Cascading uncertainty (blocking chains, contest ripples,
  instability scores) made visible via `runtime/federation_ripple_detector.py`.

- **Trust propagation** — Attenuated cross-claim trust signals (0.8 per hop).
  `dignity_violation` sets propagated weight to 0, no floor.
  See `runtime/federation_trust_propagation.py`.

- **Federation memory feedback** — Cross-claim pattern synthesis: recurring
  objection types, recurring learned conditions, correction depth patterns.
  See `runtime/federation_memory_feedback.py`.

Full specification: `FEDERATION_BRANCHING_SPEC.md`.

---

## What This Spec Does Not Cover

- **Consensus mechanisms** — Federation records relationships, not votes.
  No claim is "approved" or "rejected" by federation alone.

- **Execution ordering** — `depends_on` records a declared dependency.
  Whether the execution engine enforces it is a protocol concern, not
  this layer's concern.

- **Branch status and condition propagation** — Covered in `FEDERATION_BRANCHING_SPEC.md`.
  This spec covers only the base federation graph and event types.

- **External DID resolution** — All DIDs are mock. No real DID resolver is
  contacted. See `DID_SIGNATURE_SPEC.md`.

- **Real network federation** — This implementation is local, file-based,
  append-only JSONL. No distributed ledger, no P2P protocol, no external API.

---

*dango-gitsea-bridge · su-table append-only log · no external dependencies*
