# Negotiation to Asset Flow

This document describes how Dan-Go negotiation output becomes
an advisory GITSEA asset signal.

No step in this flow activates a GITSEA stream.
No step moves funds.
No step requires a network connection.
All steps are append-only and advisory.

---

## Full Flow Diagram

```
Claim
  │
  │  claim_created
  │  (authority: none, advisiry: true)
  ▼
Scoped Prerequisite Assessment
  │
  ├── scope: applicable ──────────────────────────────┐
  │                                                    │
  └── scope: bypassed → audit assertion only          │
                          (no issue generated)         │
                                                       ▼
                                                  Issue Drafted
                                                    │
                                                    │  negotiation_invited
                                                    │  (contestable: true)
                                                    ▼
                                                  Negotiation
                                                    │
                                                    ├── evidence contributed
                                                    ├── contest raised
                                                    ├── reaffirm submitted
                                                    ├── PR drafted
                                                    ├── PR reviewed
                                                    └── PR merged (evidence accepted)
                                                          │
                                                          │  gitsea_eligible: true (possible)
                                                          │  negotiation_reopen_allowed: true (always)
                                                          │  "A merged PR is evidence. Not authority."
                                                          ▼
                                                    Negotiation Reopen (if needed)
                                                          │
                                                          └──► Plan Correction Proposed
                                                                    │
                                                                    ▼
                                                              Contribution Recorded
                                                                    │
                                                                    ▼
                                                              Cooperation Signal Generated
                                                                    │  (advisory only)
                                                                    │  (not a score, not enforced)
                                                                    ▼
                                                              Asset Signal Generated
                                                                    │
                                                    ╔═════════════════════════════╗
                                                    ║  Dan-Go territory ends here ║
                                                    ╚═════════════════════════════╝
                                                                    │
                                                                    ▼
                                                    (GITSEA may observe this signal)
                                                    (GITSEA decides stream eligibility)
                                                    (Economic value: optional)
                                                    (Dan-Go does not cross this line)
```

---

## Step-by-Step

### Step 1: Claim Created

A Dan-Go claim enters the protocol. No commitment is made.
No economic value is implied.

```json
{ "authority": "none", "advisory": true, "economic_value": false }
```

### Step 2: Scoped Prerequisite Assessment

For each federation prerequisite:
- `applicable` → issue is drafted (negotiation invitation)
- `bypassed` → audit assertion only (no issue)

Source: `bridge/runtime/prerequisite_scope_resolver.py`

### Step 3: Issue Drafted

A scoped issue is generated. It is a negotiation invitation, not a command.

```json
{
  "issue_candidate": true,
  "scope_status": "applicable",
  "negotiation_reopen_allowed": true,
  "contestable": true
}
```

Source: `bridge/gitlawb/runtime/scoped_plan_to_issue.py`

### Step 4: Negotiation

Participants contribute evidence, contest, reaffirm. All events are
append-only. No adjudicator.

Source: `bridge/gitlawb/runtime/scoped_pr_feedback.py`

### Step 5: PR Submitted and Merged

A PR is submitted as an evidence contribution. If merged, the PR is
recorded with `gitsea_eligible: true` (possible). The negotiation
remains reopenable.

```json
{
  "gitsea_eligible": true,
  "negotiation_reopen_allowed": true,
  "note": "A merged PR is evidence. Not authority."
}
```

Source: `bridge/gitlawb/runtime/pr_feedback_mapper.py`

### Step 6: Negotiation Reopen (if needed)

Any participant may append a reopen event. No coordinator needed.

Source: `bridge/gitlawb/runtime/negotiation_reopen.py`

### Step 7: Contribution Recorded

The contribution is recorded in the append-only event log. No reward
is assigned. No reputation is updated.

Source: su-table JSONL (`bridge/sutable/`)

### Step 8: Cooperation Signal Generated

An advisory signal is generated from the participation pattern.
Not a score. Not enforced. Contestable.

```json
{
  "cooperation_signal": 0.75,
  "advisory": true,
  "authority": "none",
  "economic_value": false
}
```

Source: `bridge/gitsea/lifecycle/runtime/contribution_evaluator.py`

### Step 9: Asset Signal Generated

A GITSEA-observable signal is generated. Dan-Go does not push this
to GITSEA. GITSEA reads it from the repository if it chooses.

```json
{
  "asset_signal": true,
  "gitsea_eligible": true,
  "economic_value": false,
  "cooperation_signal": true,
  "note": "GITSEA may observe this signal. Dan-Go does not activate streams."
}
```

Source: `bridge/gitsea/lifecycle/runtime/negotiation_asset_snapshot.py`

---

## File Trace

```
Input files:
  bridge/gitlawb/examples/scoped-issue-housing-007.output.json
  bridge/gitlawb/examples/issue-001.pr-feedback.json
  bridge/gitlawb/examples/issue-001.reopen-event.json
  bridge/gitlawb/examples/issue-001.plan-correction.json

Output files (advisory, not submitted):
  bridge/gitsea/lifecycle/examples/issue-to-asset.json
  bridge/gitsea/lifecycle/examples/contribution-signal.json
  bridge/gitsea/lifecycle/examples/negotiation-snapshot.json
  bridge/gitsea/lifecycle/examples/asset-lifecycle-housing-007.json
```

---

## What Dan-Go Does and Does Not Do

| Action | Dan-Go | GITSEA |
|--------|--------|--------|
| Record negotiation events | ✓ | — |
| Generate cooperation signals | ✓ (advisory) | — |
| Produce asset signal | ✓ (advisory) | — |
| Push signals to GITSEA | ✗ | — |
| Activate stream | ✗ | ✓ |
| Assign economic value | ✗ | ✓ (optional) |
| Move funds | ✗ | ✓ (stream) |
| Enforce prerequisites | ✗ | — |

---

## Invariants at Every Step

```
authority:         none
execution_allowed: false
moves_money:       false
hard_enforcement:  false
advisory:          true
append_only:       true
contestable:       true
reopenable:        true
economic_value:    false
```

---

*dango-gitsea-bridge · authority: none · advisory · append-only · stdlib only*
*Contribution becomes legible before it becomes valuable.*
