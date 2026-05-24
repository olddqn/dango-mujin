# RESUME_STATE.md — Scoped Issue Generation

> **STATUS: COMPLETE**

**Phase:** Scoped Issue Generation (Gitlawb pipeline)
**Branch:** main
**Completed:** 2026-05-24

---

## All Phases Complete

- Reflective Memory Loop (commits 3e3d4e7..7d328c2)
- Documentation Phase (commits 64fecb1..dc2691d)
- Federation-Aware Branching Layer (commits b8b7d61..eab0f60)
- Housing-002 Memory Snapshot / Cross-claim Pattern Detection (commit 3f1dba6)
- Federation Prerequisite Promotion Layer (commits 7a521b3..1edc3d9)
- 3-Way Convergence Test (commit 09faf1d)
- Federation Prerequisite Deprecation Lifecycle (commits 7649826..0dd26b3)
- Scoped Prerequisite Inheritance Layer (commits 591817e..6a6d393)
- Gitlawb GITSEA Bountyless PR Market Demo (commit ca7d290)
- Scoped Plan Tree OGI Integration
- **Scoped Issue Generation** (this commit)

---

## Scoped Issue Generation: Results

Core principle: A scoped issue is not a command. It is a negotiation invitation.

### housing-006 Issue Result

```
scoped-issue-housing-006.output.json
  condition:     space_safety_assessed
  scope_status:  bypassed
  issue_candidate: false
  reason: "prerequisite bypassed by scoped prerequisite resolution"
  filter_action: suppress
  filter_reason: bypass
```

### housing-007 Issue Result

```
scoped-issue-housing-007.output.json
  condition:     space_safety_assessed
  scope_status:  applicable
  issue_candidate: true
  title: "[Scoped Prerequisite] space_safety_assessed required — housing-007"
  labels: [dan-go, scoped-prerequisite, safety-critical, dignity-first, contestable, ...]
  negotiation_context:
    contestable: true
    authority: none
    hard_enforcement: false
    negotiation_reopen_allowed: true
```

### Agent Task Result (housing-007)

```
scoped-agent-task.output.json
  task_generated: true
  task_type: safety_review
  scope_status: applicable
  priority: high
  execution_allowed: false
  hard_enforcement: false
  contestable: true
  negotiation_reopen_allowed: true
  moves_money: false
```

### PR Feedback Result

```
scoped-pr-feedback.output.json
  3 events: pr_opened → pr_reviewed → pr_merged
  Every event carries:
    scope_status: applicable
    hard_enforcement: false
    contestable: true
    negotiation_reopen_allowed: true
    moves_money: false
  pr_merged note: "Negotiation can reopen — PR merge is not final truth."
  pr_merged: gitsea_eligible: true (no funds activated)
```

### Snapshot Result

```
python gitlawb/runtime/scoped_issue_snapshot.py --applicable-only
  housing-007 / space_safety_assessed → open_draft
  housing-006 / space_safety_assessed → suppressed (bypassed)
```

---

## New Files

- gitlawb/runtime/scoped_plan_to_issue.py
- gitlawb/runtime/scoped_issue_filter.py
- gitlawb/runtime/scoped_issue_to_task.py
- gitlawb/runtime/scoped_pr_feedback.py
- gitlawb/runtime/scoped_issue_snapshot.py
- gitlawb/SCOPED_ISSUE_GENERATION_SPEC.md
- gitlawb/examples/scoped-issue-housing-007.output.json
- gitlawb/examples/scoped-issue-housing-006.output.json
- gitlawb/examples/scoped-agent-task.output.json
- gitlawb/examples/scoped-pr-feedback.output.json

## Updated Files

- gitlawb/runtime/claim_to_issue.py (scoped generation preference)
- gitlawb/runtime/issue_to_agent_task.py (scope_status, hard_enforcement, negotiation fields)
- gitlawb/runtime/pr_feedback_mapper.py (scope_status, contestable, negotiation_reopen_allowed)
- README.md (Scoped Issue Generation section + gitlawb directory tree update)
- RESUME_STATE.md (this file)

---

## Key Invariants (all scoped issue records)

| Field                      | Value   |
|----------------------------|---------|
| `execution_allowed`        | `false` |
| `moves_money`              | `false` |
| `hard_enforcement`         | `false` |
| `advisory`                 | `true`  |
| `contestable`              | `true`  |
| `negotiation_reopen_allowed` | `true` |
| `authority`                | `none`  |

---

## Known Limitations

- DID signatures still mock
- GITSEA still hypothetical (no stream activates)
- `food_safety_reviewed` below promotion threshold (1 claim only)
- Scope conflict detection is advisory only (intentional)
- Deprecation requires explicit event (intentional — no auto-removal)
- Plan tree for claims without plans.jsonl entries will be empty (by design)
- scoped_issue_snapshot.py scans only `ogi/examples/scoped-plan-*.output.json`

---

## Next Step Candidates

1. **Plan correction event** — formal plan_correction flow after PR merge
2. **Contest protocol** — structured way to contest a scoped prerequisite with a
   better plan tree (without a coordinator)
3. **Federated issue snapshot** — aggregate scoped_issue_snapshot across
   multiple gitlawb nodes
4. **OGI task bundle from scoped plan** — feed housing-007 scoped plan into
   plan_tree_to_tasks.py, verify tasks respect bypass
5. **Public negotiation UI** — render scoped plan tree + issue drafts as HTML

---

*dango-gitsea-bridge · authority: none · append-only · stdlib only · hard enforcement: forbidden*
