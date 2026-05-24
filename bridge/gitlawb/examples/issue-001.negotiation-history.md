# Negotiation History — Issue #1

**Claim:** `housing-007`
**Condition:** `space_safety_assessed`
**GitHub:** https://github.com/olddqn/dango-mujin/issues/1

> This is an append-only record. No step is deleted or overwritten.
> A merged PR is evidence. Not authority.

---

## 1. Issue Created

Scoped prerequisite identified:
`space_safety_assessed`

- scope_status: `applicable`
- scope: `non_precertified_spaces`
- prerequisite_state: `weakened`
- authority: `none`
- contestable: `true`
- negotiation_reopen_allowed: `true`

The prerequisite was identified through federation convergence. No coordinator declared it.

---

## 2. PR Draft Submitted

Evidence added:

- local structural review
- safety inspection notes
- community access risk assessment

The PR was submitted as advisory evidence. It did not claim to establish truth.

---

## 3. PR Feedback

**`pr_opened`** → `condition_evidence_submitted`
> Evidence submitted. Awaiting peer review. Condition is not satisfied until merged.

**`pr_reviewed`** → `condition_evidence_reviewed`
> Evidence reviewed. Scope context preserved. Condition is not satisfied until merged.

**`pr_merged`** → `condition_evidence_accepted`
> PR merged. Condition evidence accepted. Negotiation remains reopenable. Append a `plan_correction` event to formally update the plan tree.

> **Advisory note on merge:**
> A merged PR is evidence. Not authority. Negotiation remained reopenable.

---

## 4. Negotiation Reopened

**Reason:** `counter_evidence`

New evidence has been submitted that contradicts or qualifies the previously accepted evidence. The condition requires re-evaluation.

The negotiation_reopened event is append-only. The merged PR is not invalidated — it remains as evidence.

- authority: `none`
- contestable: `true`
- append_only: `true`

> **A merged PR is evidence. Not authority.** The reopen event records a new negotiation phase — it does not undo the merge.

---

## 5. Plan Correction Proposed

**Original plan:** `plan-housing-007-v1`
**Proposed plan:** `plan-housing-007-v2`

Proposed changes:

- Re-evaluate `space_safety_assessed` evidence node
- Attach counter-evidence as a sibling assertion
- Branch: if counter-evidence invalidates original → abstain

The original plan `plan-housing-007-v1` is preserved in the append-only event log.

> The original plan is NOT deleted. Both versions remain in the append-only event log.

---

## Summary

| Step | Event | Authority | Append-Only |
|------|-------|-----------|-------------|
| 1 | issue_created | none | ✓ |
| 2 | pr_draft_submitted | none | ✓ |
| 3 | pr_feedback (merged) | none | ✓ |
| 4 | negotiation_reopened | none | ✓ |
| 5 | plan_correction_proposed | none | ✓ |

**Invariants across all steps:**

- `execution_allowed: false`
- `moves_money: false`
- `hard_enforcement: false`
- `authority: none`
- `append_only: true`

---

_Human-readable negotiation is part of the protocol._
_A merged PR is evidence. Not authority._

