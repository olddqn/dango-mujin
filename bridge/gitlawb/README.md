# Dan-Go Bountyless PR Market — Gitlawb / GITSEA Demo

> **Funds:** None — this demo does not move money  
> **Authority:** None  
> **Network:** None — stdlib only

---

Dan-Go can turn a missing condition into an agent-readable issue.

This is a bountyless market:
not money-first,
condition-first.

---

## The Pipeline

```
Claim → Issue → Agent Task → PR → Reality Feedback → Stream Candidate
```

A claim has a missing condition.  
Not declared by a coordinator — discovered through structural plan tree diff.

That condition becomes a Gitlawb issue.  
The issue becomes an agent task spec.  
An agent resolves it via PR.  
The PR maps to a Reality Feedback event.  
The contribution maps to a GITSEA stream candidate.  

No step is automatic. No step moves money. No step creates authority.

---

## Quick Start

```bash
# Claim → issue draft
python bridge/gitlawb/runtime/claim_to_issue.py bridge/gitlawb/examples/claim-to-issue.input.json

# Issue draft → agent task spec
python bridge/gitlawb/runtime/issue_to_agent_task.py bridge/gitlawb/examples/issue-draft.output.json

# PR events → reality feedback
python bridge/gitlawb/runtime/pr_feedback_mapper.py bridge/gitlawb/examples/pr-feedback.output.json

# Contributions → GITSEA stream candidates
python bridge/gitlawb/runtime/stream_candidate_preview.py bridge/gitlawb/examples/pr-feedback.output.json
```

All outputs are drafts / previews. Nothing is written. Nothing is sent.

---

## Housing-004 Example

`space_safety_assessed` was discovered as a missing condition in housing-004
(community kitchen) through a `plan_objected` event by an independent safety agent.

It was later promoted to a federation prerequisite via 3-way convergence.
Its current state: **weakened** (scoped to `non_precertified_spaces`).

This demo translates that discovery into the full Gitlawb / GITSEA pipeline:

1. `claim-to-issue.input.json` — housing-004 claim with missing condition
2. `issue-draft.output.json` — Gitlawb issue draft + agent task hint
3. `pr-feedback.output.json` — hypothetical PR lifecycle (open → review → merge)
4. `stream-candidate.output.json` — GITSEA stream candidates (no funds)

---

## What "Bountyless" Means

A traditional bounty requires:
- A coordinator to set the price
- A contractor to hope the coordinator approves
- Authority to resolve disputes

The bountyless market requires none of these.

The missing condition is evidence-derived, not declared.  
The issue is generated from the evidence chain.  
The agent task is advisory, never auto-executed.  
The stream candidate is structural — ready for GITSEA if it activates.  
Money, if it ever follows, follows the evidence. Not the coordinator.

---

## Modules

| Module | What it does |
|---|---|
| `claim_to_issue.py` | Claim JSON → Gitlawb issue draft |
| `issue_to_agent_task.py` | Issue draft → agent task specification |
| `pr_feedback_mapper.py` | PR events → Dan-Go reality feedback events |
| `stream_candidate_preview.py` | PR contributions → GITSEA stream candidates |

All modules: read-only, stdlib only, no external calls, `moves_money: false`.

---

## Specs

| Spec | What it covers |
|---|---|
| `DANGO_GITLAWB_GITSEA_DEMO.md` | Full pipeline overview and design principles |
| `CLAIM_TO_ISSUE_SPEC.md` | Input/output shape, label mapping, severity → task type |
| `ISSUE_TO_PR_FEEDBACK_SPEC.md` | Agent task structure, PR event → feedback mapping |
| `GITSEA_STREAM_CANDIDATE_SPEC.md` | Credit signals, credit chain, dignity guard |

---

## Absolute Prohibitions

```
No real issue creation    No real PR creation    No GITSEA connection
No fund movement          No token               No wallet
No API key                No external network    stdlib only
```

---

*dango-gitsea-bridge · authority: none · append-only · stdlib only · moves_money: false*
