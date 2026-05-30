# Contribution History Spec — Dan-Go / GITSEA

> **Contribution history is not credit.**
> **Dan-Go records contribution candidates; external systems may issue credit.**

## What Is Contribution History?

**Contribution history** is the append-only audit trail of negotiation events
in a Dan-Go claim. It records who did what during a negotiation — which
contributors submitted evidence, who reviewed it, who contested it, and
what the outcome was.

Contribution history is a factual record. It is NOT:
- A credit ledger
- A reward queue
- An economic score
- A ranking or reputation record

The fact that a contribution appears in history does not mean credit was issued.
`credit_issued` is always `false`.

## Append-Only Invariant

Contribution history is **strictly append-only**:

- Entries are added chronologically as negotiation events occur
- No entry is ever deleted, modified, or retroactively altered
- If a claim is reopened, new entries are appended for the re-opened phase
- If evidence is contested, a `contest_raised` entry is appended — the
  original entries remain unchanged

This mirrors the Dan-Go negotiation protocol: all actions are observable
and contestable, none are erasable.

## History Event Types

| Event Type          | Description                              |
|---------------------|------------------------------------------|
| issue_opened        | Issue opened to start negotiation        |
| issue_reopened      | Issue reopened after contest             |
| pr_submitted        | PR submitted for evidence                |
| pr_merged           | PR merged — evidence accepted            |
| pr_closed           | PR closed without merge                  |
| evidence_submitted  | Evidence submitted via PR                |
| evidence_reviewed   | Evidence reviewed and approved           |
| evidence_accepted   | Evidence accepted via PR merge           |
| contest_raised      | Legitimate contest raised                |
| reaffirm_submitted  | Reaffirmation submitted with new context |
| plan_correction     | Plan correction proposed                 |

## Contribution History Document Structure

```json
{
  "history_type":         "contribution_history",
  "history_id":           "history-001",
  "claim_id":             "housing-007",
  "issue_id":             3,
  "pr_id":                2,
  "merged":               true,
  "reopened":             false,
  "entry_count":          7,
  "entries": [
    {
      "event_type":       "issue_opened",
      "event_label":      "Issue opened to start negotiation",
      "contributor_id":   "external-002",
      "claim_id":         "housing-007",
      "issue_id":         3,
      "pr_id":            null,
      "recorded_at":      "2026-05-30T00:00:00+00:00",
      "credit_issued":    false,
      "advisory":         true,
      "append_only":      true
    }
  ],
  "contributor_count":    3,
  "contributors":         ["external-001", "external-002", "external-003"],
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

## `merged` and `reopened` Fields

- **`merged: true`** — The primary evidence PR was merged. Evidence was accepted.
  This is a factual status of the PR, not a credit decision.
- **`reopened: false`** — The issue has not been reopened after resolution.
  `reopened: true` would indicate a second negotiation phase occurred.

Neither field affects `credit_issued`. Both remain observable regardless of
external credit decisions.

## Relationship to Contribution Candidates

Contribution history records *what happened*. Contribution candidates record
*which events may qualify for external credit consideration*. These are
separate concerns:

| Layer                | Question answered                             |
|----------------------|-----------------------------------------------|
| Contribution history | What happened in this negotiation?            |
| Contribution candidates | Which events may be credit-eligible?       |
| Credit candidate snapshot | How many candidates exist in aggregate? |
| Contributor registry | Who participated and in what role?           |

None of these layers issue credit. They collectively make the negotiation
legible for external credit systems (like GITSEA) without triggering
economic actions.
