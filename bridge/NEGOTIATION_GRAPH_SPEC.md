# Negotiation Graph — Specification

> A graph is not proof. A graph is a window into how negotiation moved.

---

## What Is a Negotiation Graph?

A negotiation graph is a directed visualization of su-table events
for a single claim, from creation to reality feedback.

Each node is an event.
Each edge is a transition between events.
The path from the first node to the last is the negotiation's history.

In Dan-Go, a negotiation graph is not a summary.
It is a rendering of the append-only su-table log into a form
that humans and AI can navigate at a glance.

---

## Why Dan-Go Needs This

Dan-Go's public negotiation protocol (公開談合) produces event logs.
These logs are correct and permanent — but they are JSONL files.

A JSONL file is readable by machines.
It is auditable by humans with patience.
But it is not **scannable** at the speed of conversation.

A negotiation graph makes the following questions answerable in seconds:

- "Was there an objection? What was it?"
- "Was it addressed by an amendment?"
- "Did anyone support or withdraw?"
- "What was the final reality feedback?"
- "Was there a dignity violation?"
- "Were any corrections made to earlier events?"

This is important not just for human readers.
AI agents navigating Dan-Go need to understand negotiation state
without parsing every line of every table.

The graph is the AI-readable summary of the append-only log.

---

## A Graph Is Not Proof of Truth

The negotiation graph shows **what was recorded**.

It does not prove:
- That what was claimed is true
- That the objection was valid
- That the amendment was accepted in good faith
- That the execution actually occurred
- That the reality feedback is accurate

The graph shows the negotiation's visible path.
Evaluation of that path is left to the readers — human or AI.

This is by design.
Dan-Go does not adjudicate.
Dan-Go records.

The graph is a **su-table view**, not a verdict.

---

## Correction Events: Branching, Not Deletion

When a correction event is appended to the su-table,
the original event is NOT removed.

In the negotiation graph, this is represented as:

```
[original event]  ──────────────→  [next event (temporal flow)]
        │
        └──╌╌╌╌ corrects ╌╌╌╌──→  [correction event]
```

The correction appears as:
- A new node with `↩ Correction` label and gray styling
- A **dashed edge** from the original event (`|corrects|`)
- A **normal temporal edge** from the previous su-table event (hash chain)

This makes the following visible at a glance:
1. The original statement existed and was recorded
2. The speaker returned to correct it
3. The original remains — the correction does not erase it
4. The correction is positioned in time after the original

**Why this matters:**
If a party makes an objection citing a wrong statute,
then corrects themselves —
the correction shows that they caught the error and acknowledged it.
This is more honest than if the original objection had never existed.
The negotiation graph makes both visible.

---

## Dignity Violation: Automated Processing Stops

If a `reality_feedback` event has `result: dignity_violation_detected`,
the graph renders it as a **danger node** — styled in dark red.

```
[execution_started]  ──────────────→  [🛑 DIGNITY VIOLATION]
                                          ↑
                                     danger edge
                                     automated processing halted
```

Properties of a dignity violation node:
- `style: danger` (dark red in mermaid: `fill:#7f1d1d`)
- The edge into it is typed `"danger"` rather than `"temporal"`
- The su-table record includes `automated_processing_halted: true`
- `requires_human_review: true` is always set

The graph does not hide a dignity violation.
It does not minimize it with neutral styling.
It renders it as the most severe visual state in the graph.

Any system reading this graph should treat a danger node as:
**STOP. Do not continue automated processing. Route to human review.**

---

## Graph Is Read by Humans and AI

The negotiation graph is designed for dual audiences:

**Human readers:**
- Use the mermaid output, rendered in GitHub or mermaid.live
- Color coding provides instant semantic context
- Node shapes distinguish claim / objection / amendment / contribution / execution / feedback
- Correction dashed edges are visually distinct

**AI readers:**
- Use the Python dict returned by `negotiation_graph.build_graph()`
- Nodes have `style`, `event_type`, `label`, `meta` fields
- Edges have `kind`: `temporal | correction | hash_chain | danger`
- `meta.has_dignity_violation` is a boolean flag
- `meta.final_result` is the last reality feedback result
- `node.meta.signature_status` is the signature verification result for that event
- `node.meta.signer_did` is the DID of the signer (if signed)

An AI agent can:
1. Call `build_graph(claim_id)` to get the graph dict
2. Check `meta.has_dignity_violation` — if True, halt immediately
3. Check `meta.final_result` — route based on outcome
4. Iterate nodes to find unresolved objections (objection with no following amendment/support)
5. Identify correction events and trace what was corrected
6. Check `node.meta.signature_status` to identify unsigned or invalid-signature events

---

## Node Types and Styles

| event_type | shape | style class | color |
|---|---|---|---|
| claim_created | rect `["…"]` | `claim` | blue |
| objection | hex `{"…"}` | `objection` | orange |
| amendment | round `("…")` | `amendment` | purple |
| support | rect `["…"]` | `support` | green |
| escalation | hex `{"…"}` | `escalation` | amber |
| correction | asymmetric `>"…"]` | `correction` | gray |
| withdrawal | rect `["…"]` | `withdrawal` | slate |
| contribution_offer | parallelogram `[/"…"/]` | `contrib` | violet |
| contribution_accepted | parallelogram | `contrib` | violet |
| contribution_rejected | parallelogram | `contribBlocked` | red |
| execution_started | stadium `(["…"])` | `execution` | purple |
| execution_blocked | stadium | `danger` | dark red |
| reality_feedback (success) | stadium | `feedbackOk` | green |
| reality_feedback (partial) | stadium | `feedbackPartial` | yellow |
| reality_feedback (failed) | stadium | `feedbackFail` | red |
| reality_feedback (violation) | stadium | `danger` | dark red |

---

## Edge Types

| kind | mermaid | meaning |
|---|---|---|
| `temporal` | `-->` | consecutive events in time |
| `danger` | `-->` | temporal edge into a danger node |
| `correction` | `-.-> \|corrects\|` | dashed: original → correction event |
| `hash_chain` | `-.-> \|chain\|` | dashed: within-table previous_event_hash link |

---

## CLI Reference

```bash
# Text output (human-readable terminal)
python runtime/graph_export.py --claim-id housing-001 --format text

# Mermaid output (GitHub / mermaid.live)
python runtime/graph_export.py --claim-id housing-001 --format mermaid

# Save Mermaid to file
python runtime/graph_export.py --claim-id housing-001 --format mermaid \
  > examples/housing-001.graph.mmd

# HTML preview — local browser, no external dependencies
python runtime/graph_export.py --claim-id housing-001 --format html \
  --output examples/housing-001.graph.html

# List all available claim_ids
python runtime/graph_export.py --list
```

---

## Trust Weight in the Graph

Every contribution node has a `trust_weight` computed by `temporal_trust_decay.py`.

Trust weight reflects the coordination signal strength of a contribution
at the time the graph is queried. It is computed live — not stored in the JSONL.

The formula:
```
trust_weight = base_weight × decay_factor × verification_multiplier
             × dignity_multiplier × continuity_multiplier

decay_factor = max(0.05, 0.5 ^ (days_since / half_life_days))
```

Trust levels:
| trust_weight | level |
|---|---|
| ≥ 0.7 | `high` |
| ≥ 0.3 | `medium` |
| > 0.0 | `low` |
| = 0.0 | `blocked` |

Rendering per format:
- **Mermaid**: `↑trust=0.99` appended to contribution node label
- **Text**: `↑ trust=0.99  decay=0.99  level=high  [verified]`
- **HTML**: colored badge with hover tooltip (cyan=high / amber=medium / gray=low / red=blocked)

An AI agent reading the graph can:
- Check `node.meta.trust_weight` for each contribution node
- Check `node.meta.trust_level` for the tier string
- Check `meta.trust_summary` for the graph-level count by tier
- Identify dignity-blocked contributions: `trust_weight == 0.0`

See `TEMPORAL_TRUST_DECAY_SPEC.md` for the full specification.

---

## Signature Status in the Graph

Every event node exposes `meta.signature_status` and `meta.signer_did`.

These are set by `sutable_append.py` at ingest time (see `DID_SIGNATURE_SPEC.md`).

Status values and their rendering:

| Status | Text format | Mermaid | HTML badge |
|---|---|---|---|
| `mock_valid` | `✓ [signature: mock_valid]` | `✓sig` in label | Green `✓ sig` |
| `unsigned` | `○ [signature: unsigned]` | *(no suffix)* | Gray `unsigned` |
| `mock_invalid` | `✗ [signature: mock_invalid]` | *(no suffix)* | Red `✗ sig` |
| `unsupported_signature_type` | `? [signature: unsupported]` | *(no suffix)* | Indigo `? sig` |

Note: events appended before the signature layer was added will have no `signature_status`
in their raw JSONL record. The graph treats absent status the same as `unsigned`.

---

## HTML Output

The HTML preview is a **fully self-contained local file**.

### Absolute prohibitions

- No `<script src="...">` pointing to external URLs
- No `<link rel="stylesheet" href="...">` pointing to external URLs
- No CDN references (jsdelivr, unpkg, cloudflare, googleapis, etc.)
- No `fetch()` or `XMLHttpRequest` to external hosts
- No inline `import` from external modules

### What the HTML contains

| Section | Content |
|---|---|
| Summary | Total events, final result, correction count, contribution count, dignity violation count |
| Event Timeline | Human-readable numbered list with badges, actors, timestamps, and edge annotations |
| Mermaid Source | Raw Mermaid code in a `<pre>` block with copy-to-clipboard button |
| Event Table | Index, table, event_type, speaker/contributor, timestamp, summary, hash, prev_hash, corrects reference |
| Integrity Notes | Chain link count, correction count, dignity violation flag, no-network confirmation |

### Mermaid rendering

The HTML does **not** render Mermaid graphs inline.

Rendering requires JavaScript execution of mermaid.js, which would require
loading an external script (CDN) or bundling a large JS file.
Neither is acceptable under Dan-Go's local-only HTML policy.

Instead:
1. The Mermaid source is displayed in a `<pre><code>` block
2. A **Copy** button copies the code to clipboard
3. The user pastes it into [mermaid.live](https://mermaid.live) for rendering
4. The HTML clearly states this is the intended workflow

This is the correct tradeoff: the user controls rendering, not the file.

### Fallback for clipboard API

If `navigator.clipboard.writeText()` is unavailable:
- `document.execCommand('copy')` is attempted
- If that also fails, the button text changes to "Select & copy manually"
- The code block remains visible and fully selectable
- The page never breaks or throws an uncaught error

### CSS theme

Dark background (`#0d0d0d`) with cyberpunk accent palette:

| Element | Color |
|---|---|
| Background | `#0d0d0d` |
| Surface | `#141414` |
| Accent (badge, links) | `#7c3aed` (violet) |
| Contribution | `#22d3ee` (cyan) |
| Execution | `#4ade80` (green) |
| Feedback/partial | `#fbbf24` (amber) |
| Dignity violation | `#f87171` (red) |
| Correction | `#c084fc` (violet) |

All CSS is inline `<style>` — no external stylesheet.

---

## Programmatic Usage

```python
from runtime.negotiation_graph import build_graph

graph = build_graph("housing-001")

# Graph metadata
print(graph["meta"]["final_result"])        # "partial_success"
print(graph["meta"]["has_dignity_violation"])  # False

# Iterate nodes
for node in graph["nodes"]:
    print(node["event_type"], node["style"], node["label"])

# Find objections
objections = [n for n in graph["nodes"] if n["event_type"] == "objection"]

# Find corrections
corrections = [n for n in graph["nodes"] if n["event_type"] == "correction"]

# Find correction edges
corr_edges = [e for e in graph["edges"] if e["kind"] == "correction"]
```

---

## Relationship to Su-table

The negotiation graph is a **read-only view** of the su-table.

It does not write to any JSONL file.
It does not modify any event.
It does not produce new records.

The source of truth is always the su-table JSONL files.
The graph is generated fresh each time it is requested.
If new events are appended to the su-table, the next graph generation
will include them automatically.

The graph is ephemeral. The su-table is permanent.

---

> "What was said cannot be unsaid.
>  What was recorded cannot be unrecorded.
>  The graph shows you the path.
>  The su-table holds the memory."
