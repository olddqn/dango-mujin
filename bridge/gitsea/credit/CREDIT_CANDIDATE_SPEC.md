# Credit Candidate Spec — Dan-Go / GITSEA

> **Contribution history is not credit.**
> **Dan-Go records contribution candidates; external systems may issue credit.**

## What Is a Credit Candidate?

A **credit candidate** is an advisory record indicating that a specific
contribution event in a Dan-Go negotiation *may* qualify for external
credit consideration by GITSEA.

A credit candidate is NOT:
- A credit grant
- A reward allocation
- A token transfer
- A GITSEA stream event
- A score or ranking

The `candidate_credit` field is `true` only when:
1. `evidence_accepted` is `true` (the contribution was accepted), AND
2. The contribution type represents completed work (see table below)

Even when `candidate_credit` is `true`, `credit_issued` remains `false`.
Dan-Go never issues credit.

## candidate_credit Logic

```python
completed_types = {
    "evidence_accepted",
    "evidence_reviewed",
    "reaffirm_submitted",
    "plan_correction",
}
candidate_credit = evidence_accepted and contribution_type in completed_types
```

This logic is advisory. It informs external systems about which contributions
completed meaningful work. It does not trigger any action.

## Credit Candidate Record Structure

```json
{
  "candidate_type":       "contribution_candidate",
  "generated_at":         "2026-05-30T00:00:00+00:00",
  "claim_id":             "housing-007",
  "condition":            "space_safety_assessed",
  "issue_id":             1,
  "pr_id":                1,
  "contributor_id":       "external-001",
  "contribution_type":    "evidence_reviewed",
  "contribution_label":   "Evidence reviewed and approved",
  "evidence_accepted":    true,
  "candidate_credit":     true,
  "credit_issued":        false,
  "external_system":      "gitsea",
  "moves_money":          false,
  "execution_allowed":    false,
  "hard_enforcement":     false,
  "advisory":             true,
  "authority":            "none",
  "append_only":          true,
  "contestable":          true,
  "reopenable":           true,
  "contribution_note":    "Contribution history is not credit."
}
```

## Credit Candidate Snapshot Structure

```json
{
  "snapshot_type":        "credit_candidate_snapshot",
  "snapshot_id":          "snapshot-housing-007-issue-1",
  "claim_id":             "housing-007",
  "issue_id":             1,
  "candidate_count":      3,
  "credit_eligible":      2,
  "contributor_count":    3,
  "credit_issued":        false,
  "external_system":      "gitsea",
  "advisory":             true,
  "authority":            "none",
  "contribution_note":    "Contribution history is not credit."
}
```

## Immutability

Once a credit candidate record is created, it is **never modified**.
The `credit_issued` field starts as `false` and is never changed to `true`
by Dan-Go. The `append_only: true` invariant prohibits retroactive changes.

If a contribution is contested or a claim is reopened, new records are
appended — existing records are not altered.

## GITSEA Observability

GITSEA may read credit candidate snapshots to determine:
- Which contributors participated in a Dan-Go negotiation
- Which contributions completed meaningful work
- Whether any contribution candidates exist for a given issue/PR

GITSEA's decision to issue credit, if any, is entirely independent of Dan-Go.
Dan-Go records candidates; it does not influence or request credit outcomes.
