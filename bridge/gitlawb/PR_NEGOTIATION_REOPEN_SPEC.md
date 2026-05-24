# PR Negotiation Reopen Spec

**A merged PR is evidence. Not authority.**

This document specifies the append-only negotiation lifecycle
for Dan-Go scoped issue PRs: from issue creation through
PR merge, negotiation reopen, and plan correction.

No real PR is modified. No real issue is modified.
All steps are append-only. stdlib only.

---

## 1. Why Merge ≠ Truth

A PR merge in the Dan-Go protocol records one thing:
> Evidence was accepted by reviewers present at a point in time.

It does not record:
- that the condition is permanently satisfied
- that the plan tree is updated
- that the negotiation is closed
- that the prerequisite no longer applies

The plan tree is updated by a `plan_correction` event appended
by the plan author — not by the PR merge itself.

**PR merge is a signal. The su-table is truth.**

If no `plan_correction` event follows a merge, the plan tree
has not changed. The merge is recorded as an orphaned signal:
real, auditable, but not yet integrated.

---

## 2. Why Reopenability Matters

Negotiation must be reopenable because:

1. **Evidence is imperfect.** The reviewers who approved a PR
   had access to the evidence available at that moment.
   New evidence may qualify, contradict, or supersede it.

2. **Scope can be contested.** A claim may later demonstrate
   that the prerequisite does not apply in its context.
   Bypass equivalence may be found after a merge.

3. **Federation prerequisites evolve.** A prerequisite that
   was promoted may be weakened, deprecated, or scoped out
   after a PR was merged against it.

4. **Dignity violations can emerge.** Evidence accepted in
   good faith may later be found to expose participant identity
   or violate revocable consent. The negotiation must be
   reopenable to correct this.

5. **Authority remains none.** If merge were final truth,
   it would create an authority — the merge reviewer.
   Dan-Go has no such authority. Merge is advisory.

---

## 3. Why Correction Is Append-Only

The Dan-Go protocol is append-only. Events are recorded,
not deleted. This means:

- The original plan remains visible alongside the correction
- The correction chain can be traversed forward and backward
- No version of history is lost
- An auditor can reconstruct any past state of the plan tree

When a `plan_correction_proposed` event is generated:

```
plan-housing-007-v1   (original, preserved)
        ↓
plan-housing-007-v2   (correction, proposed)
```

Both are in the event log. The plan tree generator selects
the most recent active version — but can be asked to
reconstruct from any prior version.

**Append-only means: corrections add, not replace.**

---

## 4. Why Negotiation History Must Remain Visible

The negotiation history is not documentation.
It is protocol output.

A participant who wants to contest a correction must be able to:
- see the original issue that triggered the PR
- see the PR feedback that led to the merge
- see the reopen event and its stated reason
- see the proposed correction and what it changes

Without visible history, contestation is impossible.
A participant cannot contest what they cannot see.

**Visible history is part of the protocol.**

The negotiation history Markdown (`issue-001.negotiation-history.md`)
renders all steps in sequence. It is human-readable. It is
produced from the append-only event log. It cannot lie.

---

## 5. Why PRs Are Evidence Contributions, Not Final Verdicts

In a judicial system, a verdict ends a case.
In Dan-Go, a PR merge opens a new negotiation phase.

A PR is:
- a structured evidence contribution
- a proposal to update the plan tree
- a request for peer review
- an advisory signal in the negotiation record

A PR is not:
- a declaration that a condition is satisfied
- an authority over the plan tree
- a final resolution of the negotiation
- a binding commitment

The reviewers who approve a PR are contributing their opinion.
They are not adjudicating. They have no authority to enforce.

**A merged PR is evidence. Not authority.**

---

## 6. Reopen Reasons

| Reason | Description |
|--------|-------------|
| `counter_evidence` | New evidence contradicts or qualifies accepted evidence |
| `bypass_equivalence` | Claim demonstrates an equivalent bypass path was missed |
| `dignity_violation` | A dignity guard breach was identified in the evidence |
| `prerequisite_deprecation` | Prerequisite deprecated after merge |
| `scope_contest` | Scope applicability of the prerequisite is contested |

Any participant may submit a reopen event.
No coordinator is needed.
The reopen event is append-only.

---

## 7. Negotiation Lifecycle

```
Issue Created
    │  (advisory, contestable, no authority)
    ▼
PR Draft Submitted
    │  (evidence only, merge does not establish truth)
    ▼
PR Opened → PR Reviewed → PR Merged
    │  (gitsea_eligible: true at merge, no funds activated)
    │  (negotiation_reopen_allowed: true always)
    ▼
Negotiation Reopened              ← append-only event
    │  (reason: counter_evidence, bypass_equivalence, etc.)
    │  (original PR not invalidated — it remains as evidence)
    ▼
Plan Correction Proposed          ← append-only proposal
    │  (plan-v1 preserved, plan-v2 proposed)
    │  (human/agent review required before acceptance)
    ▼
[Next negotiation phase]
```

---

## 8. Invariants Across All Steps

| Field | Value |
|-------|-------|
| `execution_allowed` | `false` |
| `moves_money` | `false` |
| `hard_enforcement` | `false` |
| `advisory` | `true` |
| `contestable` | `true` |
| `negotiation_reopen_allowed` | `true` |
| `authority` | `none` |
| `append_only` | `true` |
| `reopenable` | `true` |

---

## 9. Pipeline

```
scoped-issue-housing-007.output.json
  │
  ├── pr_draft_renderer.py
  │     → issue-001.pr-draft.md
  │
  ├── issue-001.pr-feedback.json  (PR lifecycle events)
  │
  ├── negotiation_reopen.py
  │     issue-001.pr-feedback.json → issue-001.reopen-event.json
  │
  ├── plan_correction_renderer.py
  │     issue-001.reopen-event.json → issue-001.plan-correction.json
  │
  ├── negotiation_history_renderer.py
  │     → issue-001.negotiation-history.md
  │
  └── negotiation_timeline.py
        → issue-001.timeline.json (7 steps, append-only)
```

---

## 10. Absolute Prohibitions

- No real PR is created or modified
- No real issue is created or modified
- No GitHub API or Gitlawb API
- No network access
- No token, wallet, or funds
- No external libraries (stdlib only)
- No hidden scoring
- No hard enforcement
- No auto-execution
- No deletion of prior events

---

## 11. Related Specs

- `bridge/gitlawb/SCOPED_ISSUE_GENERATION_SPEC.md`
- `bridge/gitlawb/ISSUE_MARKDOWN_RENDERING_SPEC.md`
- `bridge/gitlawb/ISSUE_TO_PR_FEEDBACK_SPEC.md`
- `bridge/SCOPED_PREREQUISITE_SPEC.md`

---

_No authority. No coordinator. Evidence only._
_A merged PR is evidence. Not authority._
_authority: none · advisory · append-only · stdlib only_
