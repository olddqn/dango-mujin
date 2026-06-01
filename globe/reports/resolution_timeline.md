# Globe Resolution Timeline (Phase 42)

generated_at: 2026-06-01T11:39:49.407412+00:00
total_items: 4
total_directives: 2

## Invariants

- "Resolution timeline is advisory display only."
- "Resolution timeline is not proof of resolution."
- "Resolution timeline does not close support."
- "Resolution timeline creates no authority."
- "Human review is required before any real-world action."

## By Directive

### directive-claim-proposal-002
- globe: globe-001
- latest_resolution_status: partially_resolved
- resolution_signal_count: 1
- unresolved_count: 0
- contested_count: 1
- partially_resolved_count: 1
- objection_count: 1
- rollback_request_count: 0
- latest_event_at: 2026-05-31T04:27:29.210356+00:00

### directive-claim-proposal-005
- globe: globe-003
- latest_resolution_status: unresolved
- resolution_signal_count: 1
- unresolved_count: 1
- contested_count: 0
- partially_resolved_count: 0
- objection_count: 0
- rollback_request_count: 0
- latest_event_at: 2026-05-31T04:27:33.201255+00:00

## Timeline Items

### tl-rt-log-003-002
- directive: directive-claim-proposal-002 (globe: globe-001)
- member: member-founding-member-003 (founding-member-003)
- event_type: objection
- resolution_status: 
- source: execution_log / log-003
- created_at: 2026-05-30T23:12:26.340959+00:00
- excerpt: D.R.A.との連携前にコミュニティ内の合意確認が必要と考える

### tl-rt-log-006-002
- directive: directive-claim-proposal-002 (globe: globe-001)
- member: member-masuo-komori (Masuo Komori)
- event_type: voluntary_resolution_signal
- resolution_status: partially_resolved
- source: execution_log / log-006
- created_at: 2026-05-31T04:27:29.210356+00:00
- excerpt: D.R.A.連携の前提整理はいったん一区切りとする

### tl-rt-attn-contested-masuo-komori-002
- directive: directive-claim-proposal-002 (globe: globe-001)
- member: member-masuo-komori (masuo-komori)
- event_type: contested_signal
- resolution_status: contested
- source: attention_dashboard / attn-contested-masuo-komori-002
- created_at: 2026-05-31T04:27:29.210356+00:00
- excerpt: VRS from member-masuo-komori is contested because member-founding-member-003 objected in the same di

### tl-rt-log-002-005
- directive: directive-claim-proposal-005 (globe: globe-003)
- member: member-jammy-house-steward (Jammy House Steward)
- event_type: voluntary_resolution_signal
- resolution_status: unresolved
- source: execution_log / log-002
- created_at: 2026-05-31T04:27:33.201255+00:00
- excerpt: 住居アドボカシーは未解決として継続観察する
