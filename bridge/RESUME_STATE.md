# RESUME_STATE.md — GitHub-Compatible Markdown Rendering

> **STATUS: COMPLETE**

**Phase:** Scoped Issue Markdown Rendering
**Branch:** main
**Completed:** 2026-05-24

---

## All Phases Complete

- Reflective Memory Loop (commits 3e3d4e7..7d328c2)
- Documentation Phase (commits 64fecb1..dc2691d)
- Federation-Aware Branching Layer (commits b8b7d61..eab0f60)
- Housing-002 Memory Snapshot / Cross-claim Pattern Detection (commit 3f1dba6)
- Federation Prerequisite Promotion Layer (commits 7a521b3..1edc3d9)
- 3-Way Convergence Test (commit 09faf1d)
- Federation Prerequisite Deprecation Lifecycle (commits 7649826..0dd26b3)
- Scoped Prerequisite Inheritance Layer (commits 591817e..6a6d393)
- Gitlawb GITSEA Bountyless PR Market Demo (commit ca7d290)
- Scoped Plan Tree OGI Integration (commit 17b344c)
- Scoped Issue Generation (commit a93ffb0)
- **Scoped Issue Markdown Rendering** (this commit)

---

## Markdown Rendering: Results

Core principle: Human-readable negotiation is part of the protocol.

### housing-007 Markdown Result

```
github-issue-housing-007.md  (5068 chars, 17 sections)
  issue_status:      open_draft
  scope_status:      applicable
  markdown_renderable: true
  Contains:
    - Why This Prerequisite Applies (scope signals table)
    - Prerequisite Lifecycle: Weakened
    - How to Resolve (5 steps)
    - Negotiation Context (authority/contestable/hard_enforcement table)
    - Agent Task Hint
    - Dignity Guard
    - Important (advisory notice)
    - Advisory footer
```

### housing-006 Markdown Result

```
github-issue-housing-006.md  (2098 chars)
  issue_status:      suppressed
  scope_status:      bypassed
  markdown_renderable: true
  Contains:
    - Status: Issue suppressed
    - Bypass Explanation (3 bypass conditions with descriptions)
    - "A bypassed prerequisite is still memory..."
    - Transparency (how to contest the suppression)
    - Advisory footer
```

### PR Feedback Markdown Result

```
scoped-pr-markdown.md  (181 lines)
  3 events: pr_opened → pr_reviewed → pr_merged
  PR lifecycle table
  Per-event notes with negotiation_reopen, hard_enforcement, contestable
  pr_merged: "Negotiation remains reopenable."
  Advisory: "PR merge is not truth."
```

### Snapshot Result

```
python gitlawb/runtime/rendered_issue_snapshot.py
  Total: 2  Rendered: 1  Suppressed: 1
  housing-007: open_draft  · markdown_length: 5068
  housing-006: suppressed  · markdown_length: 2098
  Invariants: execution_allowed=False, moves_money=False, advisory=True
```

---

## New Files

- gitlawb/runtime/issue_markdown_renderer.py
- gitlawb/runtime/scoped_issue_markdown.py
- gitlawb/runtime/negotiation_context_renderer.py
- gitlawb/runtime/prerequisite_markdown_renderer.py
- gitlawb/runtime/rendered_issue_snapshot.py
- gitlawb/ISSUE_MARKDOWN_RENDERING_SPEC.md
- gitlawb/examples/github-issue-housing-007.md
- gitlawb/examples/github-issue-housing-006.md
- gitlawb/examples/scoped-pr-markdown.md
- gitlawb/examples/rendered-issue.snapshot.json

## Updated Files

- gitlawb/runtime/scoped_pr_feedback.py (markdown_summary field added)
- gitlawb/runtime/scoped_plan_to_issue.py (markdown_renderable: true added)
- gitlawb/examples/scoped-pr-feedback.output.json (regenerated with markdown_summary)
- README.md (Markdown Rendering section + directory tree update + Specs table)
- RESUME_STATE.md (this file)

---

## Key Invariants (all rendered output)

| Field                      | Value   |
|----------------------------|---------|
| `execution_allowed`        | `false` |
| `moves_money`              | `false` |
| `hard_enforcement`         | `false` |
| `advisory`                 | `true`  |
| `contestable`              | `true`  |
| `negotiation_reopen_allowed` | `true` |
| `authority`                | `none`  |
| `markdown_renderable`      | `true`  |

---

## Known Limitations

- DID signatures still mock
- GITSEA still hypothetical (no stream activates)
- `food_safety_reviewed` below promotion threshold (1 claim only)
- Markdown rendering is output-only — no GitHub paste automation (intentional)
- `rendered_issue_snapshot.py` scans only `gitlawb/examples/scoped-issue-*.output.json`
- HTML not generated — pure Markdown only (intentional)

---

## Next Step Candidates

1. **Plan correction event rendering** — Markdown document for `plan_correction` after PR merge
2. **Contest protocol rendering** — structured Markdown for contesting a scoped prerequisite
3. **Multi-agent negotiation rendering** — render negotiation between multiple claims
4. **GITSEA stream candidate Markdown** — human-readable preview of stream candidate
5. **Public negotiation dashboard** — render scoped plan tree + issues + PR history as HTML
6. **Federated snapshot** — aggregate `rendered_issue_snapshot` across multiple gitlawb nodes

---

*dango-gitsea-bridge · authority: none · append-only · stdlib only · hard enforcement: forbidden*
*Human-readable negotiation is part of the protocol.*
