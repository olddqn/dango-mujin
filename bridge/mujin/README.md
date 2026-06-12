# Mujin Platform — Phase A: Data Layer

> **"Registration is not proof."**
> **"Withdrawal is not failure."**
> **"Support is not debt."**
> **"advisory_only is not moral immunity."**

Mujin MVP v1.1 · Phase A (Data Layer) · stdlib only · advisory only

Mujin is not a donation site. It is a platform that **makes cooperation
visible, helps discover the next step, and supports connection to
reality** — the execution-side counterpart to Dan-Go's cooperation-formation
protocol. Philosophically inseparable, implementationally loosely coupled
(ADR-002).

This directory contains the **data layer only** (SPEC §10 Phase A). No UI,
no export layer, no feedback writer, no automation.

## Specification & decisions

| Document | Role |
|---|---|
| [`docs/MUJIN_MVP_SPEC.md`](../../docs/MUJIN_MVP_SPEC.md) | The v1.1 specification this implements |
| [`docs/adr/ADR-001`](../../docs/adr/ADR-001-CANONICAL-REALITY-FEEDBACK.md)–[`005`](../../docs/adr/ADR-005-SUBJECT-DIGNITY-OBJECTION-NON-COERCIVE-PARTICIPATION.md) | Boundary, promotion, contribution, dignity decisions |
| [`docs/MUJIN_MVP_SPEC_GAP_ANALYSIS.md`](../../docs/MUJIN_MVP_SPEC_GAP_ANALYSIS.md) | Why §15/§16/§17 exist |

## Invariants (carried on every record)

```json
{
  "authority": "none",
  "execution_allowed": false,
  "moves_money": false,
  "advisory": true,
  "advisory_only_is_moral_immunity": false,
  "append_only": true,
  "contestable": true,
  "reopenable": true,
  "human_review_required": true,
  "registration_is_not_proof": true,
  "withdrawal_is_failure": false,
  "support_is_debt": false,
  "closure_attribution_prohibited": true
}
```

`advisory: true` is a **necessary** condition for safety, **not a
sufficient** one. It is a technical disclaimer and does **not** discharge
moral responsibility (ADR-005 D-4).

## Boundary rules (enforced by `store.py`)

- Mujin-specific data lives **only** under `bridge/mujin/` (`data/`,
  `examples/`, `reports/`). The store **refuses** writes anywhere else.
- The store refuses writes into `globe/` (Execution Logs, Claims,
  Directives), `bridge/gitsea/` (Relief Case Memory), and `bridge/sutable/`
  (canonical JSONLs).
- JSONL streams are **append-only**: state changes are new events; existing
  lines are never rewritten. JSON snapshots are write-once.
- The canonical Reality Feedback sink is
  `bridge/sutable/reality_feedback.jsonl` (ADR-001). The data layer does
  **not** write feedback — that is Phase D, through that canon only.
- Relief Cases are **referenced** via `source_ref.relief_case_id`, never
  modified (ADR-003).

## Files

| File | Purpose |
|---|---|
| `schemas.py` | Dataclasses: `MujinCase`, `ConsentRecord`, `DeferredConsent`, `Need`, `ContributionLink`, `ProgressLog`, `ObjectionRecord`, `NonMujinSupport` + vocabularies |
| `store.py` | Append-only JSON/JSONL utilities with Dan-Go write guards |
| `case_registry.py` | `create_mujin_case`, `withdraw_mujin_case`, `record_objection`, `record_progress`, `record_non_mujin_support` + CLI demo |
| `data/` | Append-only event streams (`mujin_cases.jsonl`, `objections.jsonl`, `non_mujin_support.jsonl`) |
| `examples/` | Safe pseudonymous example snapshots (no PII) |
| `reports/` | Sample advisory reports |

## What the data layer enforces

- **Deferred consent (SPEC §16, D-2/D-3).** A subject who cannot consent is
  never marked as consenting: `can_consent=False` forces
  `consent.status="deferred"`, which requires a named confirmation-duty
  holder. Deferred cases are not public and accept no contributions.
- **Withdrawal is not failure (D-5).** `withdraw_mujin_case` sets a neutral
  `not_pursued` status, makes the case private, never requires a reason, and
  leaves all prior events untouched.
- **Objection path (SPEC §15, D-1).** Objections may target Mujin, an NPO,
  a supporter, or an AI agent, and may arrive through **non-technical
  channels** (`phone`, `in_person`, `transcribed`, `third_party`). They
  never count against the subject and are never used for profiling.
- **Non-Mujin support is equal (SPEC §17, D-8).** Family / friends /
  community aid is recorded as `equal_in_dignity: true`, unranked.
- **`created_from: "scouter"` is reserved.** No generation path exists; the
  Saiyan Scouter question remains an unresolved Dan-Go Claim. Attempting it
  raises an error.
- **No subject-attribution on closure (D-10).** Records carry
  `closure_attribution_prohibited: true`; closure notes describe structural
  causes, never the subject's ability, attributes, or effort.

## Usage

From the repository root:

```bash
# run the demo (creates pseudonymous demo data under bridge/mujin/ only)
python -m bridge.mujin.case_registry
```

Library use:

```python
from bridge.mujin.case_registry import (
    create_mujin_case, withdraw_mujin_case, record_objection,
    record_progress, record_non_mujin_support,
)

create_mujin_case(
    case_id="mujin-case-101",
    created_from="direct_application",
    consent_status="active",
    needs=[{"need_id": "need-1", "description": "translation for one consultation"}],
)
record_progress("mujin-case-101", "p-1", "first conversation held", actor="handle-a")
record_objection("obj-1", target="supporter", channel="in_person",
                 content="…", case_id="mujin-case-101")
record_non_mujin_support("nms-1", kind="family",
                         description="family arranged transport", recorded_by="handle-a")
withdraw_mujin_case("mujin-case-101")   # reason optional — withdrawal is not failure
```

The demo also **demonstrates refusals**: creating a `scouter` case and
marking a cannot-consent subject as consenting both raise errors by design.

## What is NOT here (SPEC §9)

No automatic discovery, scouting, or outreach. No matching, scoring,
ranking, or AI judgment. No payments. No writes to Dan-Go. No UI (Phase C).
No Reality Feedback writer (Phase D).

**The Saiyan Scouter problem (Reach Gap) is unresolved. This layer does not
claim to solve it, and the definition of Reach Gap is owned by no one.**
