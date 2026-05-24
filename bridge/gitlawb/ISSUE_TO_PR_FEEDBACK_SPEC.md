# Issue → Agent Task → PR → Reality Feedback Specification

> **Status:** Implemented
> **Part of:** dango-gitsea-bridge / Gitlawb GITSEA Demo

---

## Stage 1: Issue → Agent Task

`issue_to_agent_task.py` translates a Gitlawb issue draft into a structured
agent task specification. No task is created, submitted, or executed.

### Agent Task Shape

```json
{
  "task_type":             "risk_review",
  "claim_id":              "housing-004",
  "condition":             "space_safety_assessed",
  "required_capabilities": ["safety_review", "evidence_checking", "structural_assessment"],
  "priority":              "high",
  "execution_allowed":     false,
  "reason":                "requires human/agent negotiation before execution",
  "prerequisite_context":  {
    "is_federation_prerequisite": true,
    "state": "weakened",
    "scope": "non_precertified_spaces"
  },
  "bypass_context": {
    "bypass_available_for_this_claim": false,
    "bypass_note": "No bypass path recognised — condition must be satisfied directly."
  },
  "checklist": [
    "Verify that space_safety_assessed is not already present in the active plan.",
    "Collect evidence that space_safety_assessed is satisfied.",
    "Confirm dignity guard.",
    "Attach evidence to a PR referencing the issue.",
    "Do not execute any physical or financial action.",
    "Agent must not auto-approve. Peer review required."
  ],
  "authority": "none",
  "advisory":  true,
  "moves_money": false
}
```

### Priority Assignment

| Severity | Priority |
|---|---|
| `safety_critical` | `high` |
| `risk` | `medium` |
| `coordination` | `low` |
| `dignity` | `high` |

### `execution_allowed: false`

This is not a limitation. It is the protocol.

No agent may auto-execute a safety-critical or dignity-sensitive task.
A peer agent or human must review the evidence before it is accepted.
The checklist captures this requirement explicitly.

---

## Stage 2: PR Lifecycle → Reality Feedback

`pr_feedback_mapper.py` maps PR events to Dan-Go reality_feedback event shapes.
No su-table is written. No PR is accessed. Translation only.

### PR Event → Feedback Type

| PR event | Reality feedback type |
|---|---|
| `pr_opened` | `condition_evidence_submitted` |
| `pr_reviewed` | `condition_evidence_reviewed` |
| `pr_merged` | `condition_evidence_accepted` |
| `pr_rejected` | `condition_evidence_rejected` |
| `pr_superseded` | `condition_evidence_superseded` |

### Reality Feedback Shape

```json
{
  "event_type":    "reality_feedback",
  "feedback_type": "condition_evidence_accepted",
  "claim_id":      "housing-004",
  "condition":     "space_safety_assessed",
  "pr_id":         "pr-housing-004-safety-001",
  "source":        "pr_merged",
  "authority":     "none",
  "advisory":      true,
  "dignity_guard": "pass",
  "moves_money":   false,
  "plan_impact":   "housing-004 active plan condition space_safety_assessed may now be considered satisfied — pending plan_correction event."
}
```

### Critical: PR merge ≠ plan condition satisfied

A `pr_merged` event is **advisory evidence**. It does not auto-update the plan tree.

The plan author must append a `plan_correction` event to `sutable/plans.jsonl`
to formally mark the condition as satisfied in the negotiation record.

This separation is intentional. PR workflows and Dan-Go negotiation are
distinct protocols. Merging a PR cannot bypass the negotiation record.

---

## Stage 3: PR Stream Candidate

Each PR event also produces a stream candidate signal (see `GITSEA_STREAM_CANDIDATE_SPEC.md`):

| PR event | Credit signal | GITSEA eligible |
|---|---|---|
| `pr_opened` | `evidence_submitted` | No |
| `pr_reviewed` | `reviewed_contribution` | No |
| `pr_merged` | `accepted_contribution` | Yes |
| `pr_rejected` | `rejected_submission` | No |
| `pr_superseded` | `superseded_submission` | No |

Only `pr_merged` is GITSEA-eligible. Review and submission are recorded
as credit chain entries but do not independently activate a stream.

---

## CLI

```bash
# All PR events → reality feedback
python runtime/pr_feedback_mapper.py examples/pr-feedback.output.json

# Filter to specific event
python runtime/pr_feedback_mapper.py examples/pr-feedback.output.json --event pr_merged

# JSON output
python runtime/pr_feedback_mapper.py examples/pr-feedback.output.json --json

# Issue → agent task
python runtime/issue_to_agent_task.py examples/issue-draft.output.json

# JSON output
python runtime/issue_to_agent_task.py examples/issue-draft.output.json --json
```

---

## Related Specs

- [CLAIM_TO_ISSUE_SPEC.md](CLAIM_TO_ISSUE_SPEC.md) — claim → issue translation
- [GITSEA_STREAM_CANDIDATE_SPEC.md](GITSEA_STREAM_CANDIDATE_SPEC.md) — stream candidate structure
- [DANGO_GITLAWB_GITSEA_DEMO.md](DANGO_GITLAWB_GITSEA_DEMO.md) — full pipeline overview

---

*dango-gitsea-bridge · authority: none · append-only · stdlib only · moves_money: false*
