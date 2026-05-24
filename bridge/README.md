# dango-gitsea-bridge

> 「AはAである」を超越し、「Aが非AのゆえにAである」へ。
> Transcending "A is A" to "A is A because A is not A."

---

dango-gitsea-bridge is not a financial product.
It is a translation layer between Dan-Go Claims and GITSEA-style repo assets,
contribution streams, and agent credit records.

Dan-Go asks:
"What would need to change for this impossible claim to become real?"

GITSEA may provide:
- repository identity
- contribution accounting
- streamable value
- credit history
- agent-to-agent economic coordination

This bridge does not move money.
It does not sign transactions.
It does not custody keys.
It only models the transformation.

> **Note:** GITSEA's implementation status is unverified.
> This bridge treats GITSEA as a hypothetical financial layer.
> Even if GITSEA is abandoned or fraudulent, this bridge can be forked
> to connect Dan-Go with any equivalent protocol.
> Forks, objections, and counterclaims are valid participation.

---

## Core Loop

```
Claim → Negotiation → Contribution → Execution → Reality Feedback
         ↓
    [dango-gitsea-bridge]
         ↓
  Repo Asset → Contribution Stream → Agent Credit Record
```

---

## What this bridge does

| Input | Output |
|---|---|
| Dan-Go Claim JSON | GITSEA-style repo asset |
| Contribution list | Streamable contribution ledger |
| Dignity constraints | Dignity guard decision (pass / block / escalate) |
| Claim + contributions + guard | Stream preview report |

---

## Quick Start

```bash
# Model a claim as a repo asset
python runtime/claim_to_asset.py examples/refugee-story.claim.json

# Check dignity constraints
python runtime/dignity_guard.py examples/refugee-story.claim.json

# Preview stream eligibility
python runtime/stream_preview.py examples/refugee-story.claim.json examples/contribution-stream.json
```

---

## Su-table

Dan-Go uses a fully open, append-only state table called the **su-table** (素テーブル).

Nothing is deleted.
Corrections are appended.
Negotiation history is part of the protocol itself.

The goal is not immutable truth.
The goal is transparent state transition.

```bash
# Append a claim event
python runtime/sutable_append.py --table claims --event examples/sutable_events/claim_event.json

# Append a negotiation objection
python runtime/negotiation_event.py objection \
  --claim-id housing-001 \
  --speaker did:key:critic \
  --reason "Legal ownership unresolved."

# Append reality feedback
python runtime/reality_feedback_append.py \
  --claim-id housing-001 \
  --result partial_success \
  --notes "Internet established. Space not yet legally cleared."

# Query: full timeline for a claim
python runtime/sutable_query.py --timeline housing-001

# Verify chain integrity
python runtime/sutable_query.py --verify
```

See `SUTABLE_APPEND_ONLY_SPEC.md` for the full specification.

---

## Structure

```
dango-gitsea-bridge/
├── README.md                      — This file
├── DANGO_GITSEA_THESIS.md         — Why this bridge exists
├── CLAIM_TO_REPO_ASSET.md         — How Claims become repo assets
├── CONTRIBUTION_STREAM_SPEC.md    — How contributions become streams
├── REFUGEE_STORY_STREAM_ETHICS.md — Ethics of story-based streams
├── DIGNITY_GUARD.md               — The guard layer
├── PASS_FLOW_EXAMPLE.md           — Consent-established PASS flow walkthrough
├── RISK_ASSESSMENT.md             — Known risks and limitations
├── SUTABLE_APPEND_ONLY_SPEC.md    — Su-table append-only specification
├── DID_SIGNATURE_SPEC.md          — Mock DID signature specification
├── TEMPORAL_TRUST_DECAY_SPEC.md   — Temporal trust decay specification
├── examples/                      — Sample JSON files
│   └── sutable_events/            — Example su-table event files
├── runtime/                       — Minimum viable Python implementation
│   ├── claim_to_asset.py          — Claim → repo asset
│   ├── dignity_guard.py           — 7-rule dignity guard
│   ├── stream_preview.py          — Stream eligibility preview
│   ├── contribution_ledger.py     — Contribution stream ledger
│   ├── sutable_log.py             — JSONL append helper + hash chain
│   ├── sutable_append.py          — CLI: append event to su-table (+ signature validation)
│   ├── sutable_query.py           — CLI: query su-table events
│   ├── negotiation_event.py       — CLI: structured negotiation events
│   ├── reality_feedback_append.py — CLI: reality feedback events
│   ├── negotiation_graph.py       — Graph builder (nodes + edges from su-table)
│   ├── graph_export.py            — CLI: export graph as mermaid, text, or HTML
│   ├── did_signature.py           — Mock DID signature library (test vector, not real crypto)
│   ├── sign_event.py              — CLI: attach mock signature to event JSON
│   ├── verify_event_signature.py  — CLI: verify mock signature on event JSON
│   ├── temporal_trust_decay.py    — Trust decay library (deterministic, no I/O)
│   ├── contribution_weight.py     — CLI: compute trust weight for single event
│   └── trust_snapshot.py          — CLI: contributor trust snapshot from su-table
├── sutable/                       — Live JSONL event logs
│   ├── claims.jsonl
│   ├── negotiations.jsonl
│   ├── contributions.jsonl
│   ├── executions.jsonl
│   └── reality_feedback.jsonl
└── examples/
    ├── sutable_events/            — Example event JSON files
    ├── signed-claim-event.json    — Valid mock-signed claim event
    ├── invalid-signed-event.json  — Corrupted signature (always rejected)
    ├── trust-decay-input.json     — Contribution event for trust weight example
    ├── trust-decay-output.json    — Computed trust weight (reference_date fixed)
    ├── contributor-history.json   — Multi-contributor trust decay example
    ├── housing-001.graph.mmd      — Rendered negotiation graph (Mermaid)
    └── housing-001.graph.html     — Local HTML preview (no external deps)
```

---

## Negotiation Graph

Su-table events can be rendered as a negotiation graph.

This graph does not prove truth.
It visualizes the path from Claim to Reality Feedback.

```bash
# Text output (terminal)
python runtime/graph_export.py --claim-id housing-001 --format text

# Mermaid output (GitHub / mermaid.live)
python runtime/graph_export.py --claim-id housing-001 --format mermaid

# Save Mermaid to file
python runtime/graph_export.py --claim-id housing-001 --format mermaid \
  > examples/housing-001.graph.mmd

# HTML preview — open in browser, no external dependencies
python runtime/graph_export.py --claim-id housing-001 --format html \
  --output examples/housing-001.graph.html

# List all claim_ids in the su-table
python runtime/graph_export.py --list
```

Correction events appear as dashed edges — the original is preserved,
the correction is appended. Dignity violations render as dark-red nodes
with automated processing halted.

See `NEGOTIATION_GRAPH_SPEC.md` for the full specification.

---

## Graph HTML Preview

HTML preview is local-only and does not load external scripts or stylesheets.

The HTML file includes:
- Summary statistics (events, result, corrections, dignity violations)
- Full event timeline with speaker/contributor and edge annotations
- Mermaid source code with copy-to-clipboard button
- Event table (hash, prev_hash, corrects reference)
- Integrity notes (chain links, violations, no-network confirmation)

```bash
python runtime/graph_export.py \
  --claim-id housing-001 \
  --format html \
  --output examples/housing-001.graph.html
```

Open with `open examples/housing-001.graph.html` (macOS) or your browser.
The Mermaid code block has a **Copy** button — paste into mermaid.live to render the graph visually.

---

## Temporal Trust Decay

Dan-Go su-table contribution events carry a **time-decaying trust weight**.

Trust is not a fixed score. Trust is coordination memory that fades with time.
Ancient contributions are still recorded. Their coordination signal weakens.

```
trust_weight = base_weight × decay_factor × verification_multiplier
             × dignity_multiplier × continuity_multiplier

decay_factor = max(0.05, 0.5 ^ (days_since / half_life_days))
```

Defaults: half-life = 90 days, minimum = 0.05 (ancient contributions never fully vanish).
Dignity block is the only hard zero: trust_weight = 0.0 exactly.

```bash
# Compute trust weight for a single contribution event
python runtime/contribution_weight.py examples/trust-decay-input.json

# Contributor trust snapshot from su-table (by claim)
python runtime/trust_snapshot.py --claim-id housing-001

# With fixed reference date (for deterministic output)
python runtime/trust_snapshot.py --claim-id housing-001 --reference-date 2026-05-24
```

Trust appears in all graph export formats:
- Text: `↑ trust=0.99  decay=0.99  level=high`
- Mermaid: `↑trust=0.99` in contribution node labels
- HTML: colored badge (cyan=high / amber=medium / gray=low / red=blocked) with hover tooltip

Multipliers:
- `verified` → 1.2 | `self_reported` → 1.0 | `disputed` → 0.6
- continuity bonus: min(1.5, 1.0 + 0.1 × (count − 1)) — anti-cartel capped
- `dignity: pass` → 1.0 | `escalate` → 0.8 | `block` → 0.0

See `TEMPORAL_TRUST_DECAY_SPEC.md` for the full specification.

---

## DID Signature Layer

Su-table events support an optional mock DID signature field.

⚠ **This is NOT real cryptography.** It is a deterministic test vector
that fixes the signature interface so real Ed25519 / UCAN implementations
can be dropped in at the same entry points.

Mock formula: `signature_value = sha256(key_id + ":" + sha256(canonical_event_body))`

```bash
# Sign an event file → stdout
python runtime/sign_event.py examples/sutable_events/claim_event.json

# Sign and write to file
python runtime/sign_event.py examples/sutable_events/claim_event.json \
  --did did:key:z6MkLegalReviewer \
  --key-id legal-key-001 \
  --output examples/signed-claim-event.json

# Verify a signed event (exit 0 = valid, 1 = invalid/unsigned, 2 = error)
python runtime/verify_event_signature.py examples/signed-claim-event.json

# JSON output for pipeline use
python runtime/verify_event_signature.py examples/signed-claim-event.json --json
```

Sutable append signature policy:
- `unsigned` → append with `signature_status="unsigned"` (allowed)
- `mock_valid` → append with `signature_status="mock_valid"` (allowed)
- `mock_invalid` → **REJECTED** — possible tampering
- `unsupported_signature_type` → **REJECTED** — unknown type

Signature status appears in the negotiation graph:
- Mermaid: `✓sig` in node label if valid
- Text: `✓ [signature: mock_valid]` line per event
- HTML: colored badge + signer DID column in event table

See `DID_SIGNATURE_SPEC.md` for the full specification.

---

## Claim Federation

Claims are not isolated — they depend on, enable, block, counterclaim, and
derive from each other. The federation layer records these cross-claim
relationships in `sutable/federation.jsonl` and makes them queryable.

**Relationship types:**

| Type              | Meaning |
|-------------------|---------|
| `depends_on`      | A cannot proceed without B |
| `enables`         | B (upstream) makes A (downstream) possible |
| `blocks`          | B prevents A from proceeding |
| `counterclaim`    | A publicly disputes B — both preserved |
| `amendment_of`    | A modifies B; B still exists |
| `derived_from`    | A is derived from B's content or outcome |
| `federation_link` | Symmetric association (stored both ways) |
| `dignity_override`| B overrides dignity constraints for A |

**Circular detection:** `depends_on`, `blocks`, and `dignity_override` edges
are checked for cycles. Counterclaims are never circular-detected.

```bash
# Validate a federation event (exit 0 = valid, exit 1 = invalid)
python runtime/claim_dependency.py examples/claim-dependency.json

# Validate and append to su-table
python runtime/claim_dependency.py examples/claim-dependency.json --append

# Build federation map from su-table
python runtime/claim_federation.py

# Single claim summary
python runtime/claim_federation.py --claim-id housing-001

# Federation snapshot (compact)
python runtime/federation_snapshot.py --claim-id housing-001
python runtime/federation_snapshot.py --all-claims --verbose

# Export federation graph
python runtime/federation_graph.py --format text
python runtime/federation_graph.py --format mermaid --output examples/federation.graph.mmd
```

Federation context appears in the negotiation graph export:
- **Text:** `── CLAIM FEDERATION ──` section with depth + all relationships
- **Mermaid:** `%%` comment header with federation depth and linked claims
- **HTML:** "Claim Federation" panel with colored tags + depth stat card

See `CLAIM_FEDERATION_SPEC.md` for the full specification.

---

## OGI Compatibility Layer

Dan-Go can serve as the negotiation protocol for OGI-style post-scarcity agent economies.

This bridge is not an OGI integration yet.
It is a Dan-Go compatibility layer for post-scarcity agent economies.
Robotics and physical machine control are explicitly out of scope.

```bash
# Run post-scarcity exploitation guard
python ogi/runtime/post_scarcity_guard.py ogi/examples/post-scarcity.claim.json

# Transform Claim → OGI agent task
python ogi/runtime/claim_to_agent_task.py ogi/examples/post-scarcity.claim.json

# Map contributions → credit signals
python ogi/runtime/contribution_to_credit.py ogi/examples/contribution-credit.json

# Map reality feedback → OGI outcome record
python ogi/runtime/reality_feedback_mapper.py ogi/examples/reality-feedback.json
```

See `ogi/DANGO_OGI_THESIS.md` for the central thesis:
> When money loses central meaning, coordination becomes the scarce resource.

See `ogi/AGENT_ECONOMY_MAPPING.md` for the full Dan-Go ↔ OGI concept table.

---

## OGI Reasoning Surface Compatibility

Dan-Go now includes a structured reasoning layer between language and execution.
This separates natural language claims from structured plan trees.

**The three surfaces:**

| Surface | Form | Example |
|---|---|---|
| Language | Claim statement | "This vacant house should become shared space." |
| Reasoning | Plan tree JSON | `goal → dignity clearance → action nodes → terminal` |
| Execution | Contribution events | `sutable/contributions.jsonl` |

```bash
# Generate world model from claim (observed/desired/gap)
python ogi/runtime/world_model_mapper.py ogi/examples/post-scarcity.claim.json

# Generate plan tree from claim (reasoning structure)
python ogi/runtime/claim_plan_tree.py ogi/examples/post-scarcity.claim.json \
  > ogi/examples/plan-tree.output.json

# Validate plan tree (structural + dignity check)
python ogi/runtime/plan_tree_validator.py ogi/examples/plan-tree.output.json

# JSON validation report
python ogi/runtime/plan_tree_validator.py ogi/examples/plan-tree.output.json --json
```

**Key rules:**
- Dignity branches always precede action nodes
- `abstain` is a first-class output — not a failure state
- Action nodes declare `required_capability` but do not execute
- Invalid plan trees are rejected before negotiation begins

**Spec docs:**
- `ogi/REASONING_SURFACE_SPEC.md` — why reasoning ≠ language
- `ogi/PLAN_TREE_SPEC.md` — grammar, node types, failure modes
- `ogi/WORLD_MODEL_MAPPING.md` — claim → world model transformation
- `ogi/MEMORY_SURFACE_MAPPING.md` — su-table as agent memory
- `ogi/OGI_CODEX_IMPORT_NOTES.md` — what was imported, what was left out
- `ogi/MULTI_TASK_DECOMPOSITION.md` — plan tree → task bundle architecture

---

## Plan Tree Task Extraction

Plan trees are reasoning structures. Task bundles are negotiation proposals.
This layer converts one into the other.

```
Plan Tree → Task Bundle → Dependency Graph → Execution Order
```

```bash
# Extract task bundle from a plan tree
python ogi/runtime/plan_tree_to_tasks.py ogi/examples/plan-to-task.input.json

# JSON output
python ogi/runtime/plan_tree_to_tasks.py ogi/examples/plan-to-task.input.json \
  > ogi/examples/plan-to-task.output.json

# Human-readable summary with blocked records
python ogi/runtime/plan_tree_to_tasks.py ogi/examples/plan-to-task.input.json \
  --summary --show-blocked

# Resolve dependency graph and execution order
python ogi/runtime/task_dependency_resolver.py ogi/examples/plan-to-task.output.json

# Topological execution order only
python ogi/runtime/task_dependency_resolver.py ogi/examples/plan-to-task.output.json \
  --order

# Validate task bundle structure
python ogi/runtime/task_bundle_validator.py ogi/examples/plan-to-task.output.json
```

**Extraction rules:**
- `action` nodes → executable task candidates
- dignity `branch` (true=assertion) → synthetic `condition_gate` task (priority=0, execution_allowed=true)
- risk `branch` (true=action) → real task that is also a dependency gate (priority=0)
- `abstain` → `blocked_record` (no task)
- `terminal` → updates `bundle_status` (no task)
- `subgoal` → group/phase label only

**Gate dependency model:**
- Dignity gates are always independently executable (no cross-blocking)
- Risk gate tasks are blocked by dignity gates
- All coordination tasks are blocked by dignity + risk gates
- No circular dependencies allowed (validated)

**Full pipeline:**
```bash
python ogi/runtime/claim_plan_tree.py ogi/examples/plan-tree.claim.json > /tmp/tree.json
python ogi/runtime/plan_tree_validator.py /tmp/tree.json
python ogi/runtime/plan_tree_to_tasks.py /tmp/tree.json > /tmp/bundle.json
python ogi/runtime/task_bundle_validator.py /tmp/bundle.json
python ogi/runtime/task_dependency_resolver.py /tmp/bundle.json
```

**Spec:** `ogi/PLAN_TO_TASK_SPEC.md`

---

## Quick Start — Consent-Established (PASS) Flow

```bash
# Run dignity guard on a consent-established claim
python runtime/dignity_guard.py examples/refugee-story-consented.claim.json

# Transform claim to repo asset — expect trust_mode: dignity-first, stream_eligible: true
python runtime/claim_to_asset.py examples/refugee-story-consented.claim.json

# Preview the active contribution stream
python runtime/stream_preview.py \
  examples/refugee-story-consented.claim.json \
  examples/contribution-stream-consented.json
```

See `PASS_FLOW_EXAMPLE.md` for the full annotated walkthrough.

---

## Dignity-first execution

Dan-Go does not ask: "Can this be monetized?"
Dan-Go asks: "Can this become real without violating dignity?"

A stream is allowed only after:

- explicit, informed, revocable consent
- anonymization complete (identity not exposed)
- risk review passed
- fair participation and revenue share guaranteed
- every condition acknowledged — not assumed

When consent is unknown → stream is **blocked**. No exceptions.
When consent is established → stream enters `dignity-first` trust mode.

`dignity-first` is not a reward. It is the minimum required to proceed.

---

## Principles

1. No financial product. No investment solicitation.
2. No keys, no signatures, no transactions.
3. Dignity before efficiency. Always.
4. GITSEA is hypothetical. The bridge is real.
5. If GITSEA fails, fork to another layer.
6. Consent, anonymity, revocability — explicit or blocked.
7. Do not violate the dignity of another.
