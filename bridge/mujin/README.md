# Mujin Platform — Phase A: Data Layer · Phase B: Export Adapter

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

This directory contains the **data layer** (SPEC §10 Phase A) and the
**export adapter** (Phase B). No UI, no feedback writer, no automation.

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
| `exporter.py` | Phase B: read-only adapter over Dan-Go decision data → Mujin Case drafts |
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

## Phase B — Export / Import Adapter (`exporter.py`)

Reads Dan-Go decision data **read-only** and builds **Mujin Case drafts**
for human review. A draft is not a case, not a contact, and not proof.

```bash
# discover Dan-Go sources and export sample drafts (read-only on Dan-Go)
python -m bridge.mujin.exporter
```

Library use:

```python
from bridge.mujin.exporter import (
    discover_dango_sources, load_directive, load_execution_log,
    load_relief_case, build_mujin_case_draft, export_mujin_case_draft,
)

manifest = discover_dango_sources()            # missing sources skipped safely
draft = build_mujin_case_draft(
    draft_id="from-directive-claim-proposal-002",
    directive_id="directive-claim-proposal-002",   # P1 source (ADR-002)
)
export_mujin_case_draft(draft)   # → bridge/mujin/reports/mujin_export_*.json
```

Export rules:

- **Sources (read-only, priority per DISCOVERY_REPORT §4):**
  `globe/directives/*.json` (P1), `globe/logs/*.jsonl` (P1),
  `bridge/gitsea/relief/**` (P2, reference only),
  `bridge/sutable/reality_feedback.jsonl` (P3, canonical — never written).
  Missing sources are skipped safely.
- **Output:** only `bridge/mujin/reports/mujin_export_*.json`, write-once.
- **Every draft carries** `source_refs`, `advisory_only: true`,
  `human_review_required: true`, `consent.status: "deferred"`,
  `registration_is_not_proof: true`, `subject_objection_path_required: true`,
  `outreach_explanation_required: true`, `reach_gap_unresolved: true`.
- **An adapter can never manufacture consent.** Drafts with any consent
  status other than `deferred` are refused. Becoming a case requires human
  review and the subject's confirmed consent
  (`case_registry.create_mujin_case`).
- **Exporting never contacts anyone** (`draft_creates_no_contact: true`).
  Drafts are review material about *decisions*, not judgments about people.

## Contribution Commons platform (`platform/`)

A locally runnable web app (stdlib only) implementing the commons model:

```
Need → Contribution → Connection → Reality Feedback
```

```bash
python -m bridge.mujin.platform.app        # http://127.0.0.1:8787/
```

Mujin is not a donation site, charity, or marketplace — it is a
**Contribution Commons**: rescue-possibility discovery, not price
discovery. Humans, AI agents, NPOs, NGOs, companies, municipalities, and
volunteers register as peer Contribution Providers; what is registered is
capability, not status. Agents declare capability only and can never
allocate funds, select cases, rank, govern, or evaluate.

Pages: Top / Need / Contribution / **Gateway Registry** / Commons View /
Proposal View / Reality Feedback (negative feedback welcomed) / Objection
(ADR-010, proxy submission + receipt tracking) / Agent Commons (registry,
not a marketplace) / Transparency / **TTFR Dashboard** (Time To First
Rescue — the system's response speed is measured; people never are).

**Gateways (Phase D-1).** A gateway is a *connector, not a supporter* —
the door through which a person reaches Mujin (community kitchens,
churches, temples, hospitals, schools, municipal desks, NPOs/NGOs,
shelters, volunteer groups). Gateways outrank agents in TTFR terms:
agents add support capacity, but only gateways shrink the Reach Gap.
Gateway registration is not certification; gateways connect only — no
case selection, allocation, approval, ranking, or governance. The
connection path is `Need → Gateway → Contribution`: registering a need
shows candidate gateways (presentation only, never auto-connected), and
proposals carry gateway candidates alongside contribution candidates.
The dashboard adds Gateway Count / Active Gateway Count / Regions
Covered / Languages Covered — reach coverage only, never a score.

Rules: proposals are generated, never decided (`proposal ≠ decision`,
always contestable). Lists are registration-order only — no ranking,
no scores, no priority. Needs without active consent are never shown
(a representative cannot manufacture consent: proxy registration is
forced to consent-deferred). All data is append-only JSONL under
`bridge/mujin/data/`; Dan-Go files are never touched. Promotion of
platform feedback to the canonical
`bridge/sutable/reality_feedback.jsonl` goes through the existing Dan-Go
appender with human review (ADR-001).

**Solution Commons & registries (Phase D-2/D-3).** The flow widens to
`Public Call for Help → Need → Gateway → Solution Commons → Reality
Feedback`. New pages: **Solutions** (Problem / Solution / Resource /
Agent posts), **Funding** (Crypto Donation Board — Mujin holds no funds;
listing is not verification or endorsement; donation creates no debt and
no control right; send at your own risk), **Public Call for Help
Registry** (records *publicly expressed* requests — Mujin does not
search, identify, or classify people; entries are human-reviewed,
never auto-contacted; *this is not Saiyan Scouter v1*). Agent posts
auto-carry `proposal_only / cannot_allocate_funds / cannot_rank_people /
cannot_select_cases / cannot_govern / cannot_override_consent`.

**Voice Commons (Phase D-4).** The entrance widens to `Voice → Need →
Gateway → Solution Commons → Reality Feedback`. **This is not Saiyan
Scouter.** Mujin does not search for, surveil, score, rank, or classify
people. A *Voice* records a call for help that is verifiable from
**public** information, with a named human reviewer and the original
public statement required. `/voices/convert` produces a Need
**Candidate** — never a Need — carrying `candidate_only`,
`conversion_is_not_decision`, `human_confirmation_required`, with
suggested need type / gateway types / solution types. No Need is ever
auto-created; a human confirms a candidate into a Need, which then
carries `origin_voice_id` for Reality-Feedback traceability. Dashboard
adds Voice Count / Voice Categories / Need Candidates Generated / Voices
Converted To Need / **Voice Response Time** (registration → first gateway
suggestion) / Regions & Languages Represented.

**Voice Submission Network (Phase D-5).** Widens the Voice Commons
entrance, still *not a discovery system*. `/voice-submit` brings an
already-public call for help into the same voice stream (Source URL,
Original Text, and a named Reviewer required; carries
`voice_is_publicly_expressed / voice_submission_is_not_discovery /
…is_not_ranking / …is_not_case_selection / requires_source /
human_review_required / automatic_contact_prohibited /
consent_still_required`). `/voice-sources` is a list-only Voice Source
Registry (grouped by source with a Submission Count — an observation,
never a score; registration order, no ranking). `/translations` is a
Translation Commons (translator_is_connector / not_authority /
translation_is_advisory). `/voice-discussion` lets people negotiate
*how* to help (discussion_is_not_decision / not_governance /
not_case_selection). The Voice → Need-Candidate path is unchanged
(`auto_convert=false`, `human_confirmation_required`). Dashboard adds
Voice Source Count / Translation Count / Discussion Count.

**Reality Correction Layer.** Reality takes precedence over demonstration
convenience. Records are never deleted; factual corrections are appended
and logged to `data/correction_log.jsonl` and shown on Transparency. The
earlier seeded gateways (Jammy House, D.R.A.) were **corrected**: they are
*not* verified operating support organizations (a future project concept
and an online community, respectively), are excluded from active gateway
lists, and remain in append-only history. Example records are
illustrative only; listing implies neither operational status nor
verification.

## What is NOT here (SPEC §9)

No automatic discovery, scouting, or outreach. No matching, scoring,
ranking, or AI judgment. No payments. No writes to Dan-Go. No UI (Phase C).
No Reality Feedback writer (Phase D).

**The Saiyan Scouter problem (Reach Gap) is unresolved. This layer does not
claim to solve it, and the definition of Reach Gap is owned by no one.**
