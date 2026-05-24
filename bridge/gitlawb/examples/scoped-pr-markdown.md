# [Scoped Prerequisite] space_safety_assessed required — housing-007

## Claim

housing-007

---

## Condition

space_safety_assessed

---

## Scope Status

applicable

---

## Why this issue exists

This prerequisite was identified through federation prerequisite convergence.

It is not universally enforced.

It applies in this context because the current plan includes:

- local_safety_review
- modified_existing_structure
- non_precertified_space_conditions

The scoped prerequisite layer determined that this claim does not satisfy the bypass path conditions.

---

## Federation Context

This condition emerged independently across multiple negotiation histories.

No coordinator declared it.

The prerequisite surfaced because multiple contested plan trees converged on the same structural requirement.

Current lifecycle state:

- status: weakened
- authority: none
- contestable: true
- negotiation_reopen_allowed: true

The weakened status means:

This prerequisite may not apply universally.
Equivalent safety paths may bypass it in some contexts.

Example:

housing-006 bypasses this prerequisite because it includes:

- embedded_fire_controls
- external_safety_audit_attached
- precertified_structure

housing-007 does not include those bypass conditions.

Therefore the prerequisite remains applicable here.

---

## Negotiation Context

| Field | Value |
|---|---|
| authority | none |
| contestable | true |
| hard_enforcement | false |
| advisory | true |
| execution_allowed | false |
| moves_money | false |
| negotiation_reopen_allowed | true |

---

## Suggested Agent Task

Suggested task type:

`safety_review`

Suggested capabilities:

- evidence_checking
- structural_review
- local_space_assessment

This task is advisory only.

No automatic execution is permitted.

---

## Dignity Guard

Required:

- revocable_consent
- participant_consent
- no_identity_exposure

Current status:

- no_identity_exposure: pass
- execution_allowed: false

---

## Important

This issue is not a command.

It is a negotiation invitation.

PR merge does not establish truth.

Negotiation may reopen if:

- new evidence appears
- a counterplan emerges
- equivalent safety paths are demonstrated
- federation prerequisites are contested or deprecated

---

## Structural Note

Human-readable negotiation is part of the protocol.

This issue was generated from:

Claim
→ Scoped Plan Tree
→ Federation Prerequisite Resolution
→ Scoped Issue Draft
→ Markdown Rendering

No hidden scoring.
No central authority.
No hard enforcement.

---

## Repository

GitHub:
https://github.com/olddqn/dango-mujin

gitlawb:
https://gitlawb.com/z6MkpWP3c2xE5Veu5xSJxviWUrM69SDX4offMifsVXAs31Ts/dango-mujin

## PR Feedback History

| Event | Feedback Type | Scope | GITSEA Eligible |
|-------|---------------|-------|-----------------|
| `pr_opened` | `condition_evidence_submitted` | `applicable` | — |
| `pr_reviewed` | `condition_evidence_reviewed` | `applicable` | — |
| `pr_merged` | `condition_evidence_accepted` | `applicable` | ✓ |

### `pr_opened`

> Evidence submitted. Awaiting review.

- negotiation_reopen_allowed: `True`
- hard_enforcement: `False`
- contestable: `True`
- moves_money: `False`

### `pr_reviewed`

> Evidence reviewed. Awaiting merge.

- negotiation_reopen_allowed: `True`
- hard_enforcement: `False`
- contestable: `True`
- moves_money: `False`

### `pr_merged`

> PR merged. Condition evidence accepted. Negotiation remains reopenable. Append a `plan_correction` event to formally update the plan tree.

- negotiation_reopen_allowed: `True`
- hard_enforcement: `False`
- contestable: `True`
- moves_money: `False`

**GITSEA-eligible.** No stream activates now.
Credit signal: `accepted_contribution`.

> **PR merge is not truth.** A `plan_correction` event by the plan author is needed to formally update the plan tree.

