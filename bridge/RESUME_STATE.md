# RESUME_STATE.md — Reopenable PR Negotiation

> **STATUS: COMPLETE**

**Phase:** Reopenable PR Negotiation Lifecycle (Issue #1)
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
- Scoped Plan Tree OGI Integration (commit 17b344c)
- Scoped Issue Generation (commit a93ffb0)
- Scoped Issue Markdown Rendering (commit d3bbc5e)
- Issue Markdown Canonical Format Rewrite (commit a904afb)
- GitHub Issue #1 Created (https://github.com/olddqn/dango-mujin/issues/1)
- **Reopenable PR Negotiation Lifecycle** (this commit)

---

## Reopenable PR Negotiation: Results

Core principle: A merged PR is evidence. Not authority.

### PR Draft Result

```
issue-001.pr-draft.md
  Condition Addressed: space_safety_assessed
  Evidence:
    - local structural review
    - safety inspection notes
    - community access risk assessment
  Negotiation Context table included
  Reopenability section: 4 reopen conditions listed
  Dignity Guard: participant_consent, revocable_consent
  "A merged PR is evidence. Not authority."
```

### Reopen Event Result

```
issue-001.reopen-event.json
  event_type: "negotiation_reopened"
  claim_id:   housing-007
  condition:  space_safety_assessed
  reopens_issue: 1
  reason:     counter_evidence
  authority:  none
  contestable: true
  append_only: true
  reopenable: true
  reopen_reason_examples: [counter_evidence, bypass_equivalence,
                           dignity_violation, prerequisite_deprecation]
```

### Plan Correction Result

```
issue-001.plan-correction.json
  event_type:   "plan_correction_proposed"
  claim_id:     housing-007
  corrects_plan: plan-housing-007-v1
  proposed_plan: plan-housing-007-v2
  original_plan_preserved: true
  append_only: true
  proposed_plan_changes:
    - Re-evaluate space_safety_assessed evidence node
    - Attach counter-evidence as a sibling assertion
    - Branch: if counter-evidence invalidates original → abstain
```

### Negotiation History Result

```
issue-001.negotiation-history.md
  5 sections:
    1. Issue Created
    2. PR Draft Submitted
    3. PR Feedback (pr_opened → pr_reviewed → pr_merged)
    4. Negotiation Reopened
    5. Plan Correction Proposed
  Summary table: all steps authority=none, append_only=true
```

### Timeline Result

```
issue-001.timeline.json
  7 steps:
    Step 1: issue_created
    Step 2: pr_draft_submitted
    Step 3: pr_feedback:pr_opened
    Step 4: pr_feedback:pr_reviewed
    Step 5: pr_feedback:pr_merged   (gitsea_eligible: true)
    Step 6: negotiation_reopened
    Step 7: plan_correction_proposed
  Invariants: authority=none, execution_allowed=false, append_only=true
```

---

## New Files

- gitlawb/runtime/pr_draft_renderer.py
- gitlawb/runtime/negotiation_reopen.py
- gitlawb/runtime/plan_correction_renderer.py
- gitlawb/runtime/negotiation_history_renderer.py
- gitlawb/runtime/negotiation_timeline.py
- gitlawb/PR_NEGOTIATION_REOPEN_SPEC.md
- gitlawb/examples/issue-001.pr-draft.md
- gitlawb/examples/issue-001.pr-feedback.json
- gitlawb/examples/issue-001.reopen-event.json
- gitlawb/examples/issue-001.plan-correction.json
- gitlawb/examples/issue-001.negotiation-history.md
- gitlawb/examples/issue-001.timeline.json

## Updated Files

- gitlawb/runtime/scoped_pr_feedback.py (reopenable, reopen_reason_examples)
- runtime/negotiation_graph.py (new edge kinds: pr_draft, pr_feedback, negotiation_reopen, plan_correction)
- runtime/graph_export.py (new edge arrows and labels)
- README.md (Reopenable PR Negotiation section + directory tree)
- RESUME_STATE.md (this file)

---

## Key Invariants (all negotiation steps)

| Field | Value |
|-------|-------|
| `authority` | `none` |
| `execution_allowed` | `false` |
| `moves_money` | `false` |
| `hard_enforcement` | `false` |
| `advisory` | `true` |
| `contestable` | `true` |
| `append_only` | `true` |
| `reopenable` | `true` |
| `negotiation_reopen_allowed` | `true` |

---

## Known Limitations

- DID signatures still mock
- GITSEA still hypothetical (no stream activates)
- Negotiation timeline is generated from example files (not live su-table)
- `plan_correction_proposed` is a proposal — not yet integrated into plan tree (intentional)
- PR draft does not auto-submit to GitHub (intentional)
- Reopen event does not modify GitHub Issue #1 (intentional)

---

## Next Step Candidates

1. **Post negotiation_reopened comment on Issue #1** — use `gh issue comment` to add the reopen event to the live GitHub issue
2. **Contest protocol rendering** — structured Markdown for contesting a scoped prerequisite with a better plan tree
3. **Multi-agent negotiation rendering** — render negotiation between multiple claims side by side
4. **GITSEA stream candidate Markdown** — human-readable stream candidate preview
5. **Public negotiation dashboard** — HTML render of full negotiation lifecycle
6. **Federated negotiation snapshots** — aggregate Issue history across multiple gitlawb nodes

---

*dango-gitsea-bridge · authority: none · append-only · stdlib only · hard enforcement: forbidden*
*A merged PR is evidence. Not authority.*
