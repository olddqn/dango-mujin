# GITSEA Stream Candidate Specification

> **Status:** Implemented (preview only — no GITSEA connection)
> **Part of:** dango-gitsea-bridge / Gitlawb GITSEA Demo

---

## Purpose

A stream candidate is a structured record that answers:

> If GITSEA activates an economic stream for this claim/condition pair,
> who contributed, what did they do, and does the dignity guard pass?

It does not activate a stream. It does not move money.
It is a structural translation of Dan-Go contribution signals into
GITSEA-readable shape — ready to connect when the economic layer exists.

---

## Why Stream Candidates, Not Bounties

A bounty says: "someone will pay X for Y."
This requires:
1. A coordinator to decide X
2. A contractor to do Y hoping the coordinator approves
3. Authority to resolve disputes

Dan-Go refuses all three.

A stream candidate says: "this contribution is structurally eligible for
credit if an economic stream activates." No coordinator. No upfront payment.
No authority. The contribution is recorded; the stream follows evidence.

---

## Stream Candidate Shape

```json
{
  "stream_candidate": true,
  "moves_money": false,
  "contribution_type": "safety_review",
  "credit_signal": "accepted_contribution",
  "contributor": "did:key:z6MkCommunityKitchen004",
  "reviewer": "did:key:z6KitchenSafetyAgent004",
  "claim_id": "housing-004",
  "condition": "space_safety_assessed",
  "pr_event": "pr_merged",
  "dignity_guard": "pass",
  "gitsea_eligible": true,
  "advisory": true,
  "gitsea_note": "Merged safety review for a Dan-Go condition. If GITSEA activates an economic stream, this contribution is the primary credit candidate. No funds move now.",
  "credit_chain": [
    {"role": "submitter",  "did": "did:key:z6MkCommunityKitchen004", "signal": "evidence_submitted"},
    {"role": "reviewer",   "did": "did:key:z6KitchenSafetyAgent004", "signal": "reviewed_contribution"},
    {"role": "federation", "did": "none",                            "signal": "prerequisite_weakened_survivor"}
  ]
}
```

---

## Credit Signal Ladder

Contributions accumulate credit signals as the PR progresses:

```
pr_opened    → evidence_submitted          (recorded, not eligible)
     ↓
pr_reviewed  → reviewed_contribution       (recorded, not eligible)
     ↓
pr_merged    → accepted_contribution       (GITSEA-eligible)
```

If a PR is rejected or superseded, the credit signal is recorded but
`gitsea_eligible` remains `false`.

---

## Credit Chain

The credit chain captures all contributors in the resolution path:

| Role | Who | Signal |
|---|---|---|
| submitter | Plan author / agent | `evidence_submitted` |
| reviewer | Peer agent / human | `reviewed_contribution` |
| federation | None (structural) | `prerequisite_weakened_survivor` |

The federation role is a structural signal — it records that the condition
is a surviving federation prerequisite, adding weight to the contribution.
No person or coordinator holds the federation role.

---

## Dignity Guard

All stream candidates require `dignity_guard: pass`.

Structural checks (no live runtime call):
- `no_identity_exposure` — contributor DID does not expose personal identity
- `revocable_consent` — the claim has revocable consent established
- `participant_consent` — all participants have consented

If any dignity condition is not satisfied, `dignity_guard: fail` and the
candidate is not GITSEA-eligible.

---

## Contribution Types

| Type | When used |
|---|---|
| `safety_review` | Condition contains "safety" |
| `evidence_review` | All other conditions |

More types can be added by extending `SEVERITY_CAPABILITIES` in `claim_to_issue.py`
and `contrib_type` logic in `stream_candidate_preview.py`.

---

## `gitsea_eligible: true`

Means:
- The PR was merged
- The dignity guard passed
- The credit chain is complete
- The contribution type is recognised

Does NOT mean:
- A GITSEA stream is active
- Money is moving
- Any payment has been authorised
- Any coordinator has approved

---

## Full Preview Output

`stream_candidate_preview.py` produces:

```json
{
  "stream_candidates": [...],
  "dignity_summary": {
    "all_pass": true,
    "checks": ["no_identity_exposure", "revocable_consent", "participant_consent"],
    "authority": "none"
  },
  "credit_chain": [...],
  "gitsea_eligible_count": 1,
  "moves_money": false,
  "advisory": true
}
```

---

## CLI

```bash
# All stream candidates from PR events
python runtime/stream_candidate_preview.py examples/pr-feedback.output.json

# GITSEA-eligible only
python runtime/stream_candidate_preview.py examples/pr-feedback.output.json --gitsea-only

# JSON output
python runtime/stream_candidate_preview.py examples/pr-feedback.output.json --json
```

---

## Absolute Prohibitions

```
No GITSEA connection      — hypothetical layer only
No fund movement          — moves_money: false always
No token                  — no token logic
No wallet                 — no wallet logic
No API key                — no external calls
No external network       — stdlib only
```

---

## Related Specs

- [CLAIM_TO_ISSUE_SPEC.md](CLAIM_TO_ISSUE_SPEC.md) — claim → issue
- [ISSUE_TO_PR_FEEDBACK_SPEC.md](ISSUE_TO_PR_FEEDBACK_SPEC.md) — issue → PR → feedback
- [DANGO_GITLAWB_GITSEA_DEMO.md](DANGO_GITLAWB_GITSEA_DEMO.md) — full pipeline overview
- [../CONTRIBUTION_STREAM_SPEC.md](../CONTRIBUTION_STREAM_SPEC.md) — Dan-Go contribution stream (parent spec)

---

*dango-gitsea-bridge · authority: none · append-only · stdlib only · moves_money: false*
