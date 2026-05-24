# Dan-Go × Gitlawb × GITSEA — Demo

> **Status:** Demo / Prototype
> **Funds:** None — this demo does not move money
> **Authority:** None

---

## What This Is

Dan-Go uses Gitlawb as an agent-native negotiation workspace.
GITSEA may later provide economic streams for accepted contributions.
This demo does not move funds.

It shows the translation path:

```
Claim → Issue → Agent Task → PR → Reality Feedback → Stream Candidate
```

Each step is a read-only translation. No step auto-executes the next.
No step moves money. No step creates authority.

---

## Why This Path

### The problem with bounty markets

Traditional bounty markets are money-first:
- A coordinator decides what work is worth funding
- A contributor does the work hoping the coordinator approves
- Money moves when the coordinator says so

This creates authority. The coordinator's approval is the gate.
Dan-Go refuses this structure.

### The bountyless alternative

A condition-first market:

1. A Claim has a missing condition (discovered through negotiation, not declaration)
2. That condition becomes a Gitlawb issue (no coordinator — the plan tree produced it)
3. An agent or human resolves the condition via PR
4. The PR maps to a Reality Feedback event (advisory — not enforcement)
5. The contribution maps to a GITSEA stream candidate (structurally — no funds yet)

Money, if it ever activates, follows the evidence. Not the other way around.

---

## The Pipeline in Detail

### Step 1: Claim → Issue

`claim_to_issue.py` reads a Dan-Go claim with a `missing_conditions` array.
For each missing condition, it produces a Gitlawb issue draft:

```json
{
  "title": "[Dan-Go Claim] space_safety_assessed is missing — housing-004",
  "labels": ["dan-go", "claim", "missing-condition", "dignity-first", "safety-critical"],
  "moves_money": false,
  "execution_allowed": false
}
```

The missing condition was not declared by a coordinator.
It was discovered through structural plan tree diff (plan_objected event by
`did:key:z6KitchenSafetyAgent004`). The issue body records the evidence chain.

### Step 2: Issue → Agent Task

`issue_to_agent_task.py` translates the issue draft into an agent task spec:

```json
{
  "task_type": "risk_review",
  "required_capabilities": ["safety_review", "evidence_checking", "structural_assessment"],
  "execution_allowed": false,
  "reason": "requires human/agent negotiation before execution"
}
```

`execution_allowed: false` is not a bug. It is the protocol.
No agent may auto-execute a safety-critical task. Peer review is required.

### Step 3: PR → Reality Feedback

`pr_feedback_mapper.py` maps PR lifecycle events to Dan-Go reality_feedback events:

| PR event     | Reality feedback type              |
|---|---|
| pr_opened    | condition_evidence_submitted       |
| pr_reviewed  | condition_evidence_reviewed        |
| pr_merged    | condition_evidence_accepted        |
| pr_rejected  | condition_evidence_rejected        |
| pr_superseded| condition_evidence_superseded      |

A merged PR does **not** auto-satisfy the condition in the plan tree.
The plan author must append a `plan_correction` event.
This is intentional: PR merges cannot bypass the negotiation protocol.

### Step 4: Contribution → Stream Candidate

`stream_candidate_preview.py` maps contributions to GITSEA-style stream candidates:

```json
{
  "stream_candidate": true,
  "moves_money": false,
  "contribution_type": "safety_review",
  "credit_signal": "accepted_contribution",
  "dignity_guard": "pass",
  "gitsea_eligible": true,
  "credit_chain": [
    {"role": "submitter",  "signal": "evidence_submitted"},
    {"role": "reviewer",   "signal": "reviewed_contribution"},
    {"role": "federation", "signal": "prerequisite_weakened_survivor"}
  ]
}
```

`gitsea_eligible: true` means: *if GITSEA activates an economic stream for
this condition, this contribution is structurally ready to receive credit.*
It does not mean money is moving. It does not mean a stream is active.

---

## Housing-004 Example

**Claim:** housing-004 (community kitchen, creative space)  
**Missing condition:** `space_safety_assessed`  
**Discovered via:** `plan_objected` by `did:key:z6KitchenSafetyAgent004`  
**Federation state:** weakened (scoped to `non_precertified_spaces`)  
**Survivability:** 0.65 (4 requiring / 1 bypassing)  
**Bypass available for housing-004:** No — no precertification path

Translation output:
- Issue draft: `examples/issue-draft.output.json`
- Agent task: produced by `issue_to_agent_task.py`
- PR events: `examples/pr-feedback.output.json`
- Stream candidates: `examples/stream-candidate.output.json`

---

## Design Principles

1. **Condition-first, not money-first.** The missing condition drives the issue.
   No coordinator assigns the work.

2. **Evidence-chain transparency.** Every step is traceable to a plan event
   in `sutable/plans.jsonl`. The issue body records the discovery path.

3. **Execution blocked by default.** No agent auto-executes. `execution_allowed: false`
   everywhere. Human or peer agent review is always required.

4. **PR ≠ plan update.** A merged PR is advisory evidence. The plan tree
   is only updated by an explicit `plan_correction` event from the plan author.

5. **Dignity guard always checked.** `no_identity_exposure`, `revocable_consent`,
   `participant_consent` are checked structurally before any stream candidate
   is produced.

6. **GITSEA is hypothetical.** No GITSEA connection is made. No stream is created.
   `gitsea_eligible: true` is a structural flag — not an activation.

7. **No funds.** `moves_money: false` on every output. Always.

---

## Absolute Prohibitions

```
No real issue creation        — drafts only
No real PR creation           — translation only
No real GITSEA connection     — preview only
No fund movement              — moves_money: false always
No token                      — no token logic exists
No wallet                     — no wallet logic exists
No API key                    — no external calls
No external network           — stdlib only
```

---

## Files

```
gitlawb/
├── README.md                      ← Entry point
├── DANGO_GITLAWB_GITSEA_DEMO.md   ← This file
├── CLAIM_TO_ISSUE_SPEC.md         ← Claim → issue translation spec
├── ISSUE_TO_PR_FEEDBACK_SPEC.md   ← Issue → agent task → PR → feedback spec
├── GITSEA_STREAM_CANDIDATE_SPEC.md← Stream candidate spec
├── examples/
│   ├── claim-to-issue.input.json  ← housing-004 claim input
│   ├── issue-draft.output.json    ← Issue draft + agent task hint
│   ├── pr-feedback.output.json    ← PR events (hypothetical)
│   └── stream-candidate.output.json ← GITSEA stream candidates
└── runtime/
    ├── claim_to_issue.py          ← Claim → issue draft
    ├── issue_to_agent_task.py     ← Issue draft → agent task spec
    ├── pr_feedback_mapper.py      ← PR events → reality feedback
    └── stream_candidate_preview.py← Contributions → stream candidates
```

---

*dango-gitsea-bridge · authority: none · append-only · stdlib only · moves_money: false*
