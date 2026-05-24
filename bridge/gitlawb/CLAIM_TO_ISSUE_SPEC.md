# Claim → Issue Specification

> **Status:** Implemented
> **Part of:** dango-gitsea-bridge / Gitlawb GITSEA Demo

---

## Purpose

Translate a Dan-Go Claim with missing conditions into Gitlawb issue drafts.

A missing condition is not a failure. It is a negotiation signal:
the plan tree discovered, through structural diff and agent objection,
that a condition must be satisfied before the claim can advance.

The issue is not created by a coordinator. It is created by the evidence.

---

## Input Shape

```json
{
  "claim_id": "housing-004",
  "speaker": "did:key:z6MkCommunityKitchen004",
  "active_plan_id": "plan-housing-004-v2",
  "claim_statement": "...",
  "dignity_guard": "pass",
  "negotiation_status": "contested",
  "missing_conditions": [
    {
      "condition": "space_safety_assessed",
      "discovered_via": "plan_objection",
      "objection_reason": "...",
      "objector": "did:key:z6KitchenSafetyAgent004",
      "severity": "safety_critical",
      "phase": "risk",
      "federation_prerequisite": true,
      "prerequisite_state": "weakened",
      "prerequisite_scope": "non_precertified_spaces"
    }
  ],
  "federation_context": {
    "prerequisite_status": "weakened",
    "survivability": 0.65,
    "convergence_count": 3,
    "bypassing_claims": ["housing-006"],
    "bypass_path_available": false
  }
}
```

---

## Output Shape

```json
{
  "issue_draft": {
    "title": "[Dan-Go Claim] space_safety_assessed is missing — housing-004",
    "body": "...",
    "labels": ["dan-go", "claim", "missing-condition", "dignity-first", "safety-critical", "federation-prerequisite"],
    "assignees": [],
    "moves_money": false,
    "execution_allowed": false
  },
  "source_claim_id": "housing-004",
  "missing_condition": "space_safety_assessed",
  "severity": "safety_critical",
  "federation_prerequisite": true,
  "prerequisite_state": "weakened",
  "prerequisite_scope": "non_precertified_spaces",
  "bypass_available": false,
  "agent_task_hint": {
    "task_type": "risk_review",
    "required_capabilities": ["safety_review", "evidence_checking"],
    "execution_allowed": false,
    "reason": "requires human/agent negotiation before execution"
  }
}
```

---

## Label Assignment

| Condition property | Label added |
|---|---|
| Always | `dan-go`, `claim`, `missing-condition`, `dignity-first` |
| `severity: safety_critical` | `safety-critical` |
| `severity: risk` | `risk` |
| `severity: dignity` | `dignity-required` |
| `federation_prerequisite: true` + state promoted/reaffirmed/weakened | `federation-prerequisite` |
| `federation_prerequisite: true` + state deprecated | `federation-prerequisite-deprecated` |

---

## Severity → Task Type Mapping

| Severity | Task type | Capabilities |
|---|---|---|
| `safety_critical` | `risk_review` | `safety_review`, `evidence_checking` |
| `risk` | `risk_review` | `risk_review`, `evidence_checking` |
| `coordination` | `coordination_task` | `coordination_review` |
| `dignity` | `dignity_review` | `dignity_review`, `consent_verification` |

---

## Discovery Source

`discovered_via` is recorded from the plan event chain:
- `plan_objection` — `plan_objected` event in `sutable/plans.jsonl`
- `prerequisite_hint` — propagated from `federation_prerequisite_weakened`
- `manual` — declared in the claim input directly

The discovery source and objector DID are included in the issue body.
No coordinator is attributed. The evidence chain is attributed.

---

## Bypass Handling

If `bypass_path_available: false`:
- Issue body notes: "No bypass path recognised for this claim."
- The full condition must be satisfied.

If `bypass_path_available: true`:
- Issue body lists recognised bypass conditions.
- Agent task checklist includes a bypass verification step.

---

## What This Is Not

- Not a real issue submission (`execution_allowed: false`)
- Not a governance declaration (no authority field is set to anything but `"none"`)
- Not a bounty (no money, no token, no wallet)
- Not auto-executable (agent task requires peer review)

---

## CLI

```bash
# All missing conditions for a claim
python runtime/claim_to_issue.py examples/claim-to-issue.input.json

# Specific condition
python runtime/claim_to_issue.py examples/claim-to-issue.input.json --condition space_safety_assessed

# JSON output
python runtime/claim_to_issue.py examples/claim-to-issue.input.json --json
```

---

## Related Specs

- [ISSUE_TO_PR_FEEDBACK_SPEC.md](ISSUE_TO_PR_FEEDBACK_SPEC.md) — issue → agent task → PR → feedback
- [GITSEA_STREAM_CANDIDATE_SPEC.md](GITSEA_STREAM_CANDIDATE_SPEC.md) — stream candidate structure
- [DANGO_GITLAWB_GITSEA_DEMO.md](DANGO_GITLAWB_GITSEA_DEMO.md) — full pipeline overview

---

*dango-gitsea-bridge · authority: none · append-only · stdlib only · moves_money: false*
