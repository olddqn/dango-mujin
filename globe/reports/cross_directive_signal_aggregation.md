# Cross-Directive Signal Aggregation (Phase 43)

generated_at: 2026-06-01T11:58:23.660236+00:00
total_signals: 4
total_globes: 2
total_directives: 2
total_members_with_signals: 3

## Invariants

- "Signal aggregation is advisory display only."
- "Signal aggregation is not proof of resolution."
- "Signal aggregation does not assign responsibility."
- "Signal aggregation creates no authority."
- "Human review is required before any real-world action."

## By Globe

### agg-globe-globe-001
- dimension: globe = globe-001
- total_signal_count: 3
- vrs: 1  unresolved: 0  partially_resolved: 1  contested: 1  objection: 1  rollback: 0
- latest_resolution_status: partially_resolved
- latest_signal_at: 2026-05-31T04:27:29
- affected_directives: directive-claim-proposal-002
- affected_members: member-founding-member-003, member-masuo-komori
- affected_globes: globe-001

### agg-globe-globe-003
- dimension: globe = globe-003
- total_signal_count: 1
- vrs: 1  unresolved: 1  partially_resolved: 0  contested: 0  objection: 0  rollback: 0
- latest_resolution_status: unresolved
- latest_signal_at: 2026-05-31T04:27:33
- affected_directives: directive-claim-proposal-005
- affected_members: member-jammy-house-steward
- affected_globes: globe-003

## By Directive

### agg-directive-directive-claim-proposal-002
- dimension: directive = directive-claim-proposal-002
- total_signal_count: 3
- vrs: 1  unresolved: 0  partially_resolved: 1  contested: 1  objection: 1  rollback: 0
- latest_resolution_status: partially_resolved
- latest_signal_at: 2026-05-31T04:27:29
- affected_directives: directive-claim-proposal-002
- affected_members: member-founding-member-003, member-masuo-komori
- affected_globes: globe-001

### agg-directive-directive-claim-proposal-005
- dimension: directive = directive-claim-proposal-005
- total_signal_count: 1
- vrs: 1  unresolved: 1  partially_resolved: 0  contested: 0  objection: 0  rollback: 0
- latest_resolution_status: unresolved
- latest_signal_at: 2026-05-31T04:27:33
- affected_directives: directive-claim-proposal-005
- affected_members: member-jammy-house-steward
- affected_globes: globe-003

## By Member

### agg-member-member-masuo-komori
- dimension: member = member-masuo-komori
- total_signal_count: 2
- vrs: 1  unresolved: 0  partially_resolved: 1  contested: 1  objection: 0  rollback: 0
- latest_resolution_status: partially_resolved
- latest_signal_at: 2026-05-31T04:27:29
- affected_directives: directive-claim-proposal-002
- affected_members: member-masuo-komori
- affected_globes: globe-001

### agg-member-member-founding-member-003
- dimension: member = member-founding-member-003
- total_signal_count: 1
- vrs: 0  unresolved: 0  partially_resolved: 0  contested: 0  objection: 1  rollback: 0
- latest_resolution_status: —
- latest_signal_at: 2026-05-30T23:12:26
- affected_directives: directive-claim-proposal-002
- affected_members: member-founding-member-003
- affected_globes: globe-001

### agg-member-member-jammy-house-steward
- dimension: member = member-jammy-house-steward
- total_signal_count: 1
- vrs: 1  unresolved: 1  partially_resolved: 0  contested: 0  objection: 0  rollback: 0
- latest_resolution_status: unresolved
- latest_signal_at: 2026-05-31T04:27:33
- affected_directives: directive-claim-proposal-005
- affected_members: member-jammy-house-steward
- affected_globes: globe-003

## By Status

### agg-status-contested
- dimension: status = contested
- total_signal_count: 1
- vrs: 0  unresolved: 0  partially_resolved: 0  contested: 1  objection: 0  rollback: 0
- latest_resolution_status: contested
- latest_signal_at: 2026-05-31T04:27:29
- affected_directives: directive-claim-proposal-002
- affected_members: member-masuo-komori
- affected_globes: globe-001

### agg-status-objection
- dimension: status = objection
- total_signal_count: 1
- vrs: 0  unresolved: 0  partially_resolved: 0  contested: 0  objection: 1  rollback: 0
- latest_resolution_status: —
- latest_signal_at: 2026-05-30T23:12:26
- affected_directives: directive-claim-proposal-002
- affected_members: member-founding-member-003
- affected_globes: globe-001

### agg-status-partially_resolved
- dimension: status = partially_resolved
- total_signal_count: 1
- vrs: 1  unresolved: 0  partially_resolved: 1  contested: 0  objection: 0  rollback: 0
- latest_resolution_status: partially_resolved
- latest_signal_at: 2026-05-31T04:27:29
- affected_directives: directive-claim-proposal-002
- affected_members: member-masuo-komori
- affected_globes: globe-001

### agg-status-unresolved
- dimension: status = unresolved
- total_signal_count: 1
- vrs: 1  unresolved: 1  partially_resolved: 0  contested: 0  objection: 0  rollback: 0
- latest_resolution_status: unresolved
- latest_signal_at: 2026-05-31T04:27:33
- affected_directives: directive-claim-proposal-005
- affected_members: member-jammy-house-steward
- affected_globes: globe-003
