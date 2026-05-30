# RESUME_STATE.md — Recognition Appeal Layer

> **STATUS: IN PROGRESS (feature/phase-14-recognition-appeal)**

**Phase:** Recognition Appeal Layer (Phase 14)
**Branch:** feature/phase-14-recognition-appeal
**Started:** 2026-05-30

---

## All Phases

- Reflective Memory Loop (commits 3e3d4e7..7d328c2)
- Documentation Phase (commits 64fecb1..dc2691d)
- Federation-Aware Branching Layer (commits b8b7d61..eab0f60)
- Housing-002 Memory Snapshot / Cross-claim Pattern Detection (commit 3f1dba6)
- Federation Prerequisite Promotion Layer (commits 7a521b3..1edc3d9)
- 3-Way Convergence Test (commit 09faf1d)
- Federation Prerequisite Deprecation Lifecycle (commits 7649826..0dd26b3)
- Scoped Prerequisite Inheritance Layer (commits 591817e..6a6d393)
- Gitlawb GITSEA Bountyless PR Market Demo (commit ca7d290)
- Scoped Plan Tree OGI Integration (commit 17b344c)
- Scoped Issue Generation (commit a93ffb0)
- Scoped Issue Markdown Rendering (commit d3bbc5e)
- Issue Markdown Canonical Format Rewrite (commit a904afb)
- GitHub Issue #1 Created (https://github.com/olddqn/dango-mujin/issues/1)
- Reopenable PR Negotiation Lifecycle (commit 4533c13)
- GITSEA Asset Registration (commit 9363bf2)
- GITSEA Asset Lifecycle Bridge (commit e68b9de)
- GITSEA Registration Failure Fix / asset.toml canonical format (commit d53ee21)
- Cooperation Treasury Bridge (Phase 10) — PR #2, merged
- Contributor Credit Candidate Layer (Phase 11) — PR #3
- External Credit Adapter Layer (Phase 12) — PR #4
- Credit Reflection Memory Layer (Phase 13) — PR #5
- **Recognition Appeal Layer (Phase 14)** ← current PR

---

## Phase 14: Recognition Appeal Layer

Core principles:
> "Appeal is not enforcement."
> "Recognition remains external."

**Purpose:** Provides a structured protocol path for contributors to request
reconsideration of unrecognized contributions. No appeal compels any external
system to act. Dan-Go records the appeal; external systems decide independently.

### Runtime Results

```
recognition_appeal.py
  total_appeals: 2
  ↑ external-001: evidence_reviewed — grounds: review_completed
      enforceable=False, compels_credit=False
  ↑ external-002: evidence_accepted — grounds: evidence_complete
      enforceable=False, compels_credit=False
  credit_issued: false, appeal_only: true, hard_enforcement: false

appeal_packet_builder.py
  total_packets: 2
  ↑ external-001: phase_11 candidate_credit=True + phase_12 external_credit=False
      is_submission=False, compels_response=False
  ↑ external-002: phase_11 candidate_credit=True + phase_12 external_credit=False
      is_submission=False, compels_response=False
  credit_issued: false, appeal_only: true

appeal_status_snapshot.py
  snapshot_id: appeal-snap-housing-007-issue-1
  total_appeals: 2, pending: 2, acknowledged: 0, credited: 0
  overall_status: pending
  credit_issued: false
  credit_issued_via_appeal: false
  compels_response: false
  hard_enforcement: false

appeal_reflection_report.py
  report_id: appeal-report-housing-007-issue-1
  5 sections:
    Why Appeal Exists — appeal is a voice, not a lever
    Why Appeal Does Not Compel GITSEA — authority: none
    Why Dan-Go Cannot Issue Credit — credit_issued: false, permanent
    Why Reopenability Matters — reopenable: true
    Why Request Without Authority — appeal_is_demand: false
  summary_table:
    appeal_is_enforcement: false
    appeal_compels_gitsea: false
    dango_can_issue_credit: false
    authority_exists: false
    recognition_remains_external: true
```

---

## New Files (Phase 14)

- bridge/gitsea/appeal/RECOGNITION_APPEAL_SPEC.md
- bridge/gitsea/appeal/APPEAL_NOT_ENFORCEMENT.md
- bridge/gitsea/appeal/RECOGNITION_REMAINS_EXTERNAL.md
- bridge/gitsea/appeal/runtime/recognition_appeal.py
- bridge/gitsea/appeal/runtime/appeal_packet_builder.py
- bridge/gitsea/appeal/runtime/appeal_status_snapshot.py
- bridge/gitsea/appeal/runtime/appeal_reflection_report.py
- bridge/gitsea/appeal/examples/recognition-appeal.json (generated)
- bridge/gitsea/appeal/examples/appeal-packet.json (generated)
- bridge/gitsea/appeal/examples/appeal-status-snapshot.json (generated)
- bridge/gitsea/appeal/examples/appeal-reflection-report.json (generated)

## Updated Files (Phase 14)

- bridge/gitsea/README.md (Phase 14 section + appeal/ in layout)
- bridge/RESUME_STATE.md (this file)

---

## Key Invariants (all Phase 14 files)

| Field | Value |
|-------|-------|
| `authority` | `none` |
| `execution_allowed` | `false` |
| `moves_money` | `false` |
| `hard_enforcement` | `false` |
| `advisory` | `true` |
| `appeal_only` | `true` |
| `append_only` | `true` |
| `contestable` | `true` |
| `reopenable` | `true` |
| `credit_issued` | `false` (permanent) |
| `appeal_is_enforceable` | `false` (invariant) |
| `appeal_compels_credit` | `false` (invariant) |
| `appeal_creates_authority` | `false` (invariant) |
| `packet_is_submission` | `false` (invariant) |
| `packet_compels_response` | `false` (invariant) |
| `compels_response` | `false` (invariant) |

---

## Protocol Principle Accumulation

Each phase added a new invariant phrase:

| Phase | Phrase |
|-------|--------|
| 10 | "Signal is not reward." |
| 10 | "Dan-Go observes treasury context; it does not operate the treasury." |
| 11 | "Contribution history is not credit." |
| 11 | "Dan-Go records contribution candidates; external systems may issue credit." |
| 12 | "Observation is not issuance." |
| 12 | "Candidate credit is not external credit." |
| 13 | "Unrecognized contribution is still observable." |
| 13 | "Reflection is not judgment." |
| 14 | "Appeal is not enforcement." |
| 14 | "Recognition remains external." |

---

## Next Step Candidates

1. **Merge Phase 14 PR** — after review
2. **Phase 15: GITSEA Stream Candidate Tracking** — observe stream activation events
3. **Multi-claim appeal dashboard** — aggregate appeal state across claims
4. **Federation appeal layer** — record appeals across gitlawb nodes
5. **Appeal response observation** — if external systems respond, record the response

---

*dango-gitsea-bridge · authority: none · append-only · stdlib only · hard enforcement: forbidden*
*Signal is not reward.*
*Contribution history is not credit.*
*Observation is not issuance.*
*Candidate credit is not external credit.*
*Unrecognized contribution is still observable.*
*Reflection is not judgment.*
*Appeal is not enforcement.*
*Recognition remains external.*
*Dan-Go observes treasury context; it does not operate the treasury.*
*Dan-Go records contribution candidates; external systems may issue credit.*
*Contribution becomes legible before it becomes valuable.*
