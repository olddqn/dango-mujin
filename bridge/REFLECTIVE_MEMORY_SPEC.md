# Reflective Memory Specification

> **Status:** Implemented  
> **Version:** 1.0  
> **Part of:** dango-gitsea-bridge / Multi-Agent Plan Negotiation Layer

---

## Overview

Reflective memory closes the negotiation feedback loop.

Every negotiation produces evidence: objections, supports, corrections, contests. Without
a memory layer, each new plan tree cycle starts from zero — repeating objected conditions,
ignoring learned constraints.

Reflective memory captures what the negotiation has learned and feeds it back into the
next world model cycle as **prior knowledge**.

```
World Model → Plan Tree → Negotiation → Memory
      ↑                                     |
      └──────────── prior_knowledge ────────┘
```

This loop is:
- **Append-only** — snapshots accumulate; no snapshot is ever deleted
- **Derived, not decreed** — memory is computed from plans.jsonl; no central authority writes it
- **Deterministic** — given the same plans.jsonl, the same memory record is always produced
- **Transparent** — every field has a traceable origin in a negotiation event

---

## Absolute Prohibitions

The reflective memory layer MUST NOT:
- Execute plans or bundles
- Make autonomous decisions on behalf of participants
- Act as centralized authority over what was learned
- Use hidden scoring or opaque ranking
- Modify or delete existing sutable events
- Require network access, API keys, or external libraries

All state changes are **new events, appended to memory.jsonl**. Nothing is overwritten.

---

## Memory Record

A memory record (event type `memory_snapshot_created`) captures the state of a claim's
negotiation history at the moment the snapshot is created.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `event_type` | string | Always `"memory_snapshot_created"` |
| `claim_id` | string | The claim this snapshot is for |
| `memory_id` | string | Unique ID: `mem-{claim_id}-{n:03d}` |
| `active_plan_id` | string | Currently active plan (formal selection or computed) |
| `negotiation_status` | string | `open` / `signalled` / `contested` / `active` / `empty` |
| `learned_conditions` | list[str] | Conditions in counterplans but NOT in contested plans |
| `prior_supports` | list[dict] | Support signals per plan, with counts and reasons |
| `prior_objections` | list[dict] | Objection signals per plan, typed and counted |
| `correction_chain_depth` | int | Max correction hops in the plan correction chain |
| `contest_count` | int | Number of plan contests that occurred |
| `known_contested_plans` | list[str] | plan_ids that were contested |
| `snapshot_basis` | dict | `plans_event_count`, `plan_count`, `latest_event_hash` |
| `summary` | string | Human-readable one-line summary |
| `timestamp` | string | ISO 8601 UTC timestamp |
| `event_hash` | string | SHA256 of serialized event body (chain integrity) |
| `previous_event_hash` | string | Hash of preceding event in memory.jsonl (chain link) |

### Example

```json
{
    "event_type": "memory_snapshot_created",
    "claim_id": "housing-001",
    "memory_id": "mem-housing-001-002",
    "active_plan_id": "plan-housing-001-v3",
    "negotiation_status": "contested",
    "learned_conditions": [
        "space_safety_assessed"
    ],
    "prior_supports": [
        {
            "plan_id": "plan-housing-001-v2",
            "count": 1,
            "reasons": [
                "dignity branch coverage complete"
            ]
        }
    ],
    "prior_objections": [
        {
            "plan_id": "plan-housing-001-v2",
            "count": 1,
            "by_type": {
                "insufficient_risk_coverage": 1
            },
            "reasons": [
                "risk review phase covers only legal_ownership_confirmed — shared creative spaces require a separate space_safety_assessed gate"
            ]
        }
    ],
    "correction_chain_depth": 1,
    "contest_count": 1,
    "known_contested_plans": ["plan-housing-001-v2"],
    "snapshot_basis": {
        "plans_event_count": 7,
        "plan_count": 3,
        "latest_event_hash": "69911eb1..."
    },
    "summary": "1 correction(s); 1 contest(s); 1 objection(s) (insufficient_risk_coverage); 1 support(s); learned: space_safety_assessed; active: plan-housing-001-v3"
}
```

---

## Negotiation Status Values

| Status | Meaning |
|--------|---------|
| `empty` | No plan events exist for this claim |
| `open` | Plans exist; no signals yet |
| `signalled` | At least one support or objection event exists |
| `contested` | At least one `plan_contested` event exists |
| `active` | A formal `active_plan_selected` event exists |

---

## Learned Conditions Algorithm

Learned conditions are discovered through **structural plan tree diff** — not text-mining.

For each contest pair:
```
learned = conditions(counterplan_tree) - conditions(contested_plan_tree)
```

A condition is the value of the `"condition"` field on any `branch` node in a plan tree.
The algorithm walks the full tree recursively (children, true, false branches).

**Why structural diff?**

Text-mining objection reasons is fragile: it depends on phrasing, language, and author style.
Structural diff is deterministic: it depends only on the plan tree structure, which is
a formal artifact of the negotiation protocol.

**Carry-forward rule:**

Learned conditions accumulate across snapshots. If an objection is later withdrawn, the
learned condition is not removed — it is part of the negotiation history. Withdrawals
are new events, not deletions (append-only principle).

**Example:**

- `plan-housing-001-v2` (contested): has branch condition `legal_ownership_confirmed`
- `plan-housing-001-v3` (counterplan): has branch conditions `legal_ownership_confirmed` **and** `space_safety_assessed`
- Learned: `space_safety_assessed` (present in counterplan, absent in contested plan)

---

## Prior Knowledge Block

When a world model cycle begins, the latest memory snapshot is injected as `prior_knowledge`:

```json
{
  "memory_id": "mem-housing-001-002",
  "active_plan_id": "plan-housing-001-v3",
  "negotiation_status": "contested",
  "learned_conditions": ["space_safety_assessed"],
  "known_objection_types": ["insufficient_risk_coverage"],
  "correction_depth": 1,
  "contest_count": 1,
  "summary": "..."
}
```

The world model builder (`world_model_with_memory.py`) automatically appends
`learned_conditions` to the world model's `state_gap` with category
`"learned_from_negotiation"`, so the next plan tree cycle addresses them.

---

## Storage: sutable/memory.jsonl

Memory snapshots are stored in the su-table (素テーブル) as an append-only JSONL file.

```
bridge/sutable/memory.jsonl
```

- One JSON object per line
- SHA256 event hash chain (each event links to previous)
- Never modified, never deleted
- Multiple snapshots per claim are preserved (latest is authoritative for reads)

Table name: `"memory"` (registered in `sutable_log.VALID_TABLES`)

---

## Module Reference

### `runtime/reflective_memory.py` — core computation (read-only)

```python
compute_memory(claim_id: str) -> dict
```
Derive a full memory record from `plans.jsonl` events. No files written.

```python
extract_prior_knowledge(claim_id: str) -> dict
```
Return the latest memory snapshot as a `prior_knowledge` dict.
Returns `{}` if no memory snapshots exist.

```python
next_memory_id(claim_id: str) -> str
```
Return the next sequential `memory_id` for a claim.
Format: `mem-{claim_id}-{n:03d}`.

```python
extract_conditions(plan_tree: dict) -> set[str]
```
Walk a plan tree and collect all branch condition names.

---

### `runtime/memory_append.py` — append to memory.jsonl

```python
append_memory_snapshot(claim_id, *, dry_run, verbose, json_output) -> dict
```
Compute and append a `memory_snapshot_created` event to `sutable/memory.jsonl`.

```python
build_memory_event(claim_id: str) -> dict
```
Compute and return event dict without writing.

---

### `runtime/memory_snapshot.py` — query memory state (read-only)

```python
get_snapshots(claim_id: str) -> list[dict]
get_latest_snapshot(claim_id: str) -> dict | None
all_claim_ids_with_memory() -> list[str]
compute_diff(snapshot, current) -> dict
```

---

### `runtime/world_model_with_memory.py` — enriched world model (read-only)

```python
build_world_model_with_memory(claim_id, claim, *, include_feedback) -> dict
```
Build an OGI world model enriched with reflective prior knowledge.

```python
load_claim_from_sutable(claim_id: str) -> dict | None
load_claim_from_file(path) -> dict
```

---

## CLI Reference

### Create a memory snapshot

```bash
python runtime/memory_append.py --claim-id housing-001
python runtime/memory_append.py --claim-id housing-001 --dry-run
python runtime/memory_append.py --claim-id housing-001 --json
python runtime/memory_append.py --claim-id housing-001 --verbose
```

### Query memory state

```bash
python runtime/memory_snapshot.py --claim-id housing-001
python runtime/memory_snapshot.py --claim-id housing-001 --diff
python runtime/memory_snapshot.py --claim-id housing-001 --prior-knowledge
python runtime/memory_snapshot.py --claim-id housing-001 --json
python runtime/memory_snapshot.py --all-claims
```

### Build enriched world model

```bash
python runtime/world_model_with_memory.py --claim-id housing-001
python runtime/world_model_with_memory.py --claim-id housing-001 --json
python runtime/world_model_with_memory.py --claim-id housing-001 --verbose
python runtime/world_model_with_memory.py --claim-file ogi/examples/my-claim.json
```

### Compute memory without writing

```bash
python runtime/reflective_memory.py --claim-id housing-001
python runtime/reflective_memory.py --claim-id housing-001 --json
python runtime/reflective_memory.py --claim-id housing-001 --verbose
```

---

## Integration Pipeline

Full reflective memory loop for `housing-001`:

```bash
# 1. Check negotiation state
python runtime/plan_negotiation_snapshot.py --claim-id housing-001

# 2. Create memory snapshot from negotiation history
python runtime/memory_append.py --claim-id housing-001 --verbose

# 3. Verify snapshot
python runtime/memory_snapshot.py --claim-id housing-001 --diff

# 4. Build enriched world model (closes the loop)
python runtime/world_model_with_memory.py --claim-id housing-001

# 5. Check prior knowledge (for next plan tree cycle)
python runtime/memory_snapshot.py --claim-id housing-001 --prior-knowledge
```

---

## Stale Detection

A snapshot is **stale** if `plans.jsonl` has changed since the snapshot was taken.
`memory_snapshot.py --diff` detects this by comparing `snapshot_basis.plans_event_count`.

When stale:
```
⚠ STALE — 3 new plan event(s) since snapshot
  • active_plan_id: 'plan-housing-001-v2' → 'plan-housing-001-v3'
  Run memory_append.py --claim-id housing-001 to update.
```

---

## Design Principles

### 1. Memory is derived, not decreed

The memory record is always computed from the raw negotiation event log (`plans.jsonl`).
No central authority writes the memory record. Anyone with access to `plans.jsonl` can
independently verify what the memory record should say.

### 2. Append-only history

Memory snapshots are immutable once written. Older snapshots are preserved forever.
The latest snapshot is authoritative for world model integration, but the full history
is available for audit and replay.

### 3. Structural learning, not text inference

Learned conditions are discovered by structural plan tree diff, not by text-mining
objection reason strings. This makes learning deterministic and protocol-level.

### 4. No central authority

There is no memory manager, no arbiter, no score keeper. Any participant can call
`memory_append.py` at any time. The result is always computable from the public
negotiation log.

### 5. Transparent prior knowledge

The `prior_knowledge` block in the enriched world model is fully traceable:
every field points back to a specific negotiation event in `plans.jsonl` or `memory.jsonl`.

---

## Related Specs

- [PLAN_NEGOTIATION_SPEC.md](PLAN_NEGOTIATION_SPEC.md) — multi-agent plan negotiation
- [ogi/PLAN_TREE_SPEC.md](ogi/PLAN_TREE_SPEC.md) — plan tree structure and correction
- [ogi/PLAN_TO_TASK_SPEC.md](ogi/PLAN_TO_TASK_SPEC.md) — plan-to-task bundle derivation
