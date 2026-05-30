# Recognition Ledger Spec — Dan-Go / GITSEA (Phase 15)

> **"Recognition history is not authority."**
> **"Ledger is not judgment."**

## Overview

Phase 15 introduces the Recognition Ledger Layer — a read-only advisory
ledger that links the records from Phases 11–14 into one complete recognition
history per contributor per claim.

The ledger is the terminal record of the Dan-Go contribution→recognition
lifecycle. It does not start new processes. It records that all prior
phases have completed.

## The Phase Chain

```
Phase 11: Contribution Candidate     candidate_credit: true/false
     ↓
Phase 12: External Credit Observation  external_credit: false
     ↓
Phase 13: Reflection Memory            reflection_recorded: true
     ↓
Phase 14: Recognition Appeal           appeal_recorded: true
     ↓
Phase 15: Recognition Ledger           recognition_history_complete: true
```

Each phase contributes one field to the ledger entry. Together they form
a complete, cross-phase record of what happened.

## Runtime Modules

| Module | Purpose |
|--------|---------|
| `recognition_ledger.py` | Build the combined Phase 11–14 recognition history |
| `ledger_snapshot.py` | Summarise all ledger entries with aggregate counts |
| `ledger_entry_builder.py` | Build one atomic ledger entry with event sequence |
| `ledger_report.py` | 5-section report explaining why ledger ≠ judgment |

## Ledger Entry Structure

```json
{
  "entry_id":                    "ledger-entry-001",
  "claim_id":                    "housing-007",
  "issue":                       3,
  "pr":                          2,
  "contributor":                 "external-001",
  "contribution_label":          "Evidence reviewed and approved",
  "candidate_credit":            true,
  "external_credit":             false,
  "reflection_recorded":         true,
  "appeal_recorded":             true,
  "events": [
    "candidate_created",
    "external_credit_not_observed",
    "reflection_recorded",
    "appeal_recorded"
  ],
  "recognition_history_complete": true,
  "authority":                   "none",
  "judgment":                    false,
  "ledger_only":                 true,
  "credit_issued":               false
}
```

## Ledger Event Sequence

| Event | Phase | Description |
|-------|-------|-------------|
| `candidate_created` | 11 | Contribution candidate recorded |
| `external_credit_not_observed` | 12 | No external credit detected |
| `external_credit_observed` | 12 | External credit detected |
| `reflection_recorded` | 13 | Reflection memory stored |
| `appeal_recorded` | 14 | Recognition appeal filed |
| `appeal_acknowledged` | 14 | Appeal acknowledged by external system |
| `appeal_credited` | 14 | External credit issued following appeal |
| `appeal_not_credited` | 14 | Appeal considered; no credit issued |

## Why History Can Be Complete While Recognition Remains External

`recognition_history_complete: true` means all four phases have contributed
a record to the ledger entry. It does not mean external credit was issued.
A ledger entry can have:

- `recognition_history_complete: true` AND `external_credit: false`

This is the expected state for contributions that went through the full
Phase 11–14 lifecycle without receiving external credit. History is
complete. Recognition is pending or absent. These are separate facts.

## Invariants

All records in this layer carry:

```json
{
  "credit_issued":            false,
  "moves_money":              false,
  "execution_allowed":        false,
  "hard_enforcement":         false,
  "advisory":                 true,
  "ledger_only":              true,
  "authority":                "none",
  "judgment":                 false,
  "append_only":              true,
  "contestable":              true,
  "reopenable":               true,
  "entry_issues_credit":      false,
  "entry_judges":             false,
  "entry_ranks":              false,
  "entry_creates_authority":  false,
  "ledger_issues_credit":     false,
  "ledger_judges":            false,
  "ledger_forces_recognition": false
}
```

## Required Phrases

All spec documents and runtime modules in this layer must include:

1. `"Recognition history is not authority."`
2. `"Ledger is not judgment."`
