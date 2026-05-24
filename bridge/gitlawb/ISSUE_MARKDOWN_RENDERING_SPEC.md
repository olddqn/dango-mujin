# Issue Markdown Rendering Spec

**Human-readable negotiation is part of the protocol.**

This document specifies how Dan-Go scoped issue drafts are rendered
into GitHub-compatible Markdown suitable for GitHub issues, Gitlawb
issues, or any Markdown renderer.

No real issue is created. No API is called. Markdown generation only.
stdlib only.

---

## 1. Why Markdown Matters

A scoped issue is a negotiation invitation — but only if a human can
read it.

A JSON blob with `issue_candidate: true` is machine-readable.
A Markdown document is human-readable. Both are needed.

Markdown rendering is the bridge between the machine-generated
negotiation record and the human participants who must read, evaluate,
and respond to it.

Without human-readable rendering, the protocol produces structures
that only agents can navigate. That breaks the dignity-first principle:
participants — human and agent — must be able to understand what they
are agreeing to or contesting.

**Markdown rendering makes the negotiation legible.**

---

## 2. Why Negotiation Must Be Human-Readable

The Dan-Go protocol is not a system of rules imposed by machines.
It is a negotiation protocol for impossible claims.

A federation prerequisite is an observation, not a law.
An issue draft is an invitation, not a command.
A PR review is an opinion, not a verdict.
A merge is an acknowledgement, not a truth declaration.

Every step in this pipeline can be contested, reopened, or superseded.
For a participant to contest, they must be able to understand what they
are contesting and why.

Machine-generated JSON cannot carry the context needed for a human
to make an informed decision. Markdown can.

**Human-readable negotiation is part of the protocol.**

---

## 3. Why Issue Rendering Is Distinct from Execution

Issue rendering produces text. It does not:
- create a real issue
- trigger any action
- assign authority
- move funds
- close negotiation

The rendered Markdown is a proposal — a structured way to say:
> "Here is what the protocol suggests. Here is why. Here is how to respond."

Rendering and execution are intentionally separate. An agent can render
an issue without creating it. A human can read a rendering without
being bound by it.

`execution_allowed: false` is invariant across all rendered output.

---

## 4. Why Suppression Should Still Render an Explanation

When a bypassed prerequisite suppresses issue creation, the suppression
is not silent. A bypass explanation document is rendered instead.

This is because:
- suppression is a decision, not an absence
- the bypass conditions that caused suppression are specific and auditable
- a participant may contest the bypass if they believe it was incorrect
- without an explanation, the suppression is opaque

The bypass explanation document includes:
- what bypass conditions were found
- what each bypass condition means
- why no issue was generated
- how to contest the suppression

**Transparency about suppression is part of the protocol.**

---

## 5. Why Bypass Transparency Matters

A bypassed prerequisite is still memory.
It is just not an active requirement in this context.

If the bypass is rendered transparently:
- auditors can verify the bypass was appropriate
- participants can contest if the bypass should not apply
- future claims can learn from the bypass record

If the bypass is silent:
- the suppression is undetectable
- the bypass cannot be contested
- the audit trail is incomplete

Dan-Go always renders bypass explanations. The bypass is not hidden.

---

## 6. Why Human-Readable Auditability Matters

The Dan-Go protocol is append-only. Events are recorded, not deleted.
The audit trail must be readable by humans, not just machines.

Rendered Markdown files serve as audit artifacts:
- `github-issue-housing-007.md` — the invitation to resolve a condition
- `github-issue-housing-006.md` — the explanation of why suppression occurred
- `scoped-pr-markdown.md` — the PR feedback history for a scoped condition

These files can be:
- committed to the repository (alongside JSON)
- reviewed by humans without tooling
- shared with non-technical participants
- archived as historical negotiation records

**Markdown auditability is not documentation. It is protocol output.**

---

## 7. Rendering Rules

### Applicable prerequisites → full issue body

```
# [Scoped Prerequisite] {condition} required — {claim_id}

Labels: {labels}
Claim: {claim_id}
Condition: {condition}
Scope Status: applicable — scope: {scope}

## Why This Prerequisite Applies
  [scope signals, reasoning]

## Prerequisite Lifecycle: {state}
  [lifecycle explanation]

## How to Resolve
  [steps 1-5]

## Negotiation Context
  [authority, contestable, hard_enforcement table]
  [contestability instructions]
  [reopenability note]
  [federation convergence note]

## Agent Task Hint
  [task_type, capabilities]

## Dignity Guard
  [dignity rules table]

## Important
  [advisory notice]

---
[advisory footer]
```

### Bypassed prerequisites → suppression explanation

```
# [Scoped Prerequisite] {condition} bypassed — {claim_id}

## Status
  Issue suppressed.
  scope_status: bypassed
  issue_candidate: false
  reason: {reason}

## Bypass Explanation
  [bypass conditions with descriptions]
  [why no issue was generated]
  [memory note]

## Transparency
  [how to contest the suppression]

---
[advisory footer]
```

---

## 8. Invariants on All Rendered Output

| Field | Value |
|-------|-------|
| `execution_allowed` | `false` |
| `moves_money` | `false` |
| `hard_enforcement` | `false` |
| `advisory` | `true` |
| `contestable` | `true` |
| `negotiation_reopen_allowed` | `true` |
| `authority` | `none` |
| `markdown_renderable` | `true` |

---

## 9. PR Feedback Markdown

PR events are rendered as a lifecycle table + per-event notes:

```
## PR Feedback History

| Event | Feedback Type | Scope | GITSEA Eligible |
|-------|---------------|-------|-----------------|
| pr_opened   | condition_evidence_submitted | applicable | — |
| pr_reviewed | condition_evidence_reviewed  | applicable | — |
| pr_merged   | condition_evidence_accepted  | applicable | ✓ |

### pr_merged
> PR merged. Condition evidence accepted.
  Negotiation remains reopenable.
  Append a plan_correction event to formally update the plan tree.

> PR merge is not truth. A plan_correction event by the plan author
> is needed to formally update the plan tree.
```

---

## 10. Pipeline

```
Scoped issue JSON (scoped-issue-*.output.json)
  │
  ├── issue_markdown_renderer.py
  │     issue_candidate: true  → render_issue_markdown()
  │     issue_candidate: false → render_suppressed_markdown()
  │
  ├── scoped_issue_markdown.py  [CLI]
  │     single-file rendering
  │     optional: --pr-feedback <file>
  │
  └── rendered_issue_snapshot.py
        full snapshot across all claims
        optional: --write-files (writes .md to gitlawb/examples/)
```

Supporting renderers:
- `negotiation_context_renderer.py` — authority, contestability, reopenability
- `prerequisite_markdown_renderer.py` — applicable/bypassed/weakened sections

---

## 11. Absolute Prohibitions

- No real issue is created
- No GitHub API or Gitlawb API is called
- No real PR is created
- No network access
- No token, wallet, or funds
- No external libraries (stdlib only)
- No hidden scoring
- No hard enforcement
- No auto-execution

---

## 12. Related Specs

- `bridge/gitlawb/SCOPED_ISSUE_GENERATION_SPEC.md` — issue generation pipeline
- `bridge/gitlawb/CLAIM_TO_ISSUE_SPEC.md` — unscoped issue generation
- `bridge/gitlawb/ISSUE_TO_PR_FEEDBACK_SPEC.md` — PR event → reality feedback
- `bridge/SCOPED_PREREQUISITE_SPEC.md` — scope resolution rules
- `bridge/ogi/SCOPED_PLAN_TREE_INTEGRATION.md` — plan tree generation

---

_No authority. No coordinator. Evidence only._
_authority: none · advisory · contestable · stdlib only_
_Human-readable negotiation is part of the protocol._
