# Candidate Credit vs External Credit — Dan-Go Protocol Note

> **"Candidate credit is not external credit."**
> **"Observation is not issuance."**

## Two Distinct Concepts

### Candidate Credit (Phase 11 — Dan-Go)

A **contribution candidate** with `candidate_credit: true` is:
- A Dan-Go advisory classification
- Based on whether the contribution completed accepted work
- Recorded in `contribution_candidate.py` and `credit_candidate_snapshot.py`
- Scoped to a specific issue, PR, and contributor
- Permanent (append-only; never retracted)
- **Not a credit grant**

### External Credit (Phase 12 — External System)

**External credit** is:
- A decision made by an external system (e.g. GITSEA)
- Independent of Dan-Go candidate classifications
- Issued on the external system's own schedule and criteria
- Visible (if at all) through the external system's interface
- **Not controlled by Dan-Go**

## Why They Are Different

```
Dan-Go candidate credit:
  candidate_credit = evidence_accepted AND type in completed_types
  → Advisory. Always false for credit_issued. Permanent.

External credit (GITSEA example):
  Determined by GITSEA stream logic, on-chain conditions,
  RepoVault state, and GITSEA's own eligibility rules.
  → Sovereign. May or may not correspond to Dan-Go candidates.
```

These are different systems making different classifications for different
purposes. Their outputs may partially overlap but are not equivalent.

## Why Candidate Credit May Never Become External Credit

Several reasons why a Dan-Go contribution candidate may never result in
external credit:

1. **External system criteria differ** — GITSEA may require conditions
   beyond what Dan-Go tracks (stake amounts, time windows, governance votes).

2. **External systems are not obligated** — No external system is bound
   by Dan-Go candidate classifications. Candidates are advisory.

3. **Economic decisions are external** — Whether contribution work has
   economic value is a market and governance question, not a protocol question.

4. **Dan-Go does not notify** — Dan-Go does not push candidates to external
   systems. Systems must choose to observe them independently.

5. **Timing is external** — Even if all conditions are met, external credit
   may be delayed, batched, or subject to external governance timelines.

None of these reasons represent a failure of the Dan-Go protocol.
The protocol's job is to make contribution legible — not to guarantee
that legibility translates into economic value.

## The Comparison Record

`candidate_vs_external.py` records the comparison explicitly:

```json
{
  "candidate_credit": true,
  "external_credit":  false,
  "equivalent":       false,
  "observation":      "candidate_not_yet_recognized",
  "gap_exists":       true,
  "gap_is_error":     false
}
```

The `gap_is_error: false` field is a protocol invariant. The gap between
candidate credit and external credit is never classified as an error.
It is a documented, expected, architecturally-intended state.

## What Dan-Go Does With the Gap

Dan-Go:
- Records the gap explicitly in comparison records
- Explains the gap in observation reports
- Does not attempt to close the gap through actions
- Does not treat the gap as a reason to escalate or intervene

The gap is information. It is advisory. It is observable. It is sufficient.

## Protocol Phrase

> "Candidate credit is not external credit."

This phrase appears in every Phase 12 runtime module. It makes explicit
that the advisory classifications Dan-Go produces are distinct from the
economic credit that external systems may issue. Conflating them would
misrepresent both Dan-Go's role and the external system's sovereignty.
