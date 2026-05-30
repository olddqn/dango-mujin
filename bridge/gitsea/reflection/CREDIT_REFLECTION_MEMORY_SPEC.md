# Credit Reflection Memory Spec — Dan-Go / GITSEA (Phase 13)

> **"Unrecognized contribution is still observable."**
> **"Reflection is not judgment."**

## Overview

Phase 13 introduces the Credit Reflection Memory Layer — a set of modules
that record what happened after a contribution candidate was created and an
external credit check was performed.

The reflection records:

```
candidate created          → Phase 11 (contribution_candidate.py)
external credit checked    → Phase 12 (external_credit_adapter.py)
credit not observed        → Phase 12 (external_credit_snapshot.py)
gap recorded               → Phase 12 (candidate_vs_external.py)
reflection stored          → Phase 13 (credit_reflection_memory.py)
```

Dan-Go does not punish, rank, or decide. It remembers.

## Purpose

The purpose of credit reflection memory is to ensure that contribution
remains permanently observable, regardless of whether external credit
was ever issued. Contribution memory matters independently of economic
recognition.

## What This Layer Does

- Records the full lifecycle of a contribution candidate as reflection memory
- Records contributions that were not externally credited as unrecognized
- Snapshots the gap state across all contributors for a claim
- Generates a human-readable reflection report explaining the gap

## What This Layer Does NOT Do

- Issue credit (credit_issued: false — permanent invariant)
- Appeal to external systems
- Resolve or close gaps
- Judge contributors or external systems
- Punish, rank, or score contributors
- Move funds
- Perform wallet operations
- Call any external API

## Runtime Modules

| Module | Purpose |
|--------|---------|
| `credit_reflection_memory.py` | Record full candidate lifecycle as reflection memory |
| `unrecognized_contribution.py` | Record candidates without external credit |
| `reflection_gap_snapshot.py` | Snapshot gap state across all contributors |
| `credit_reflection_report.py` | Human-readable report explaining the observation |

## Invariants

All records in this layer carry the following invariants:

```json
{
  "credit_issued":      false,
  "moves_money":        false,
  "execution_allowed":  false,
  "hard_enforcement":   false,
  "advisory":           true,
  "reflection_only":    true,
  "authority":          "none",
  "append_only":        true,
  "contestable":        true,
  "reopenable":         true
}
```

New Phase 13 invariants (additional):

```json
{
  "gap_is_failure":    false,
  "gap_is_accusation": false,
  "is_accusation":     false,
  "contribution_lost": false,
  "memory_sufficient": true
}
```

## Reflection Memory Lifecycle

Every credit reflection memory record tracks five stages:

| Stage | Description |
|-------|-------------|
| `candidate_created` | Contribution candidate recorded in Phase 11 |
| `external_credit_checked` | External system observed in Phase 12 |
| `credit_not_observed` | No external credit detected |
| `gap_recorded` | Gap documented in Phase 12 comparison |
| `reflection_stored` | Reflection memory stored in Phase 13 |

All five stages are completed by default in the standard workflow.

## Required Phrases

All spec documents and runtime modules in this layer must include:

1. `"Unrecognized contribution is still observable."`
2. `"Reflection is not judgment."`
