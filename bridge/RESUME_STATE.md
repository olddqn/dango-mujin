# RESUME_STATE.md — Directive Dependency Map

> **STATUS: IN PROGRESS (feature/phase-37-directive-dependency-map)**

**Phase:** Directive Dependency Map (Phase 37)
**Branch:** feature/phase-37-directive-dependency-map
**Started:** 2026-05-31

---

## All Phases

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
- Scoped Issue Markdown Rendering (commit d3bbc5e)
- Issue Markdown Canonical Format Rewrite (commit a904afb)
- GitHub Issue #1 Created (https://github.com/olddqn/dango-mujin/issues/1)
- Reopenable PR Negotiation Lifecycle (commit 4533c13)
- GITSEA Asset Registration (commit 9363bf2)
- GITSEA Asset Lifecycle Bridge (commit e68b9de)
- GITSEA Registration Failure Fix / asset.toml canonical format (commit d53ee21)
- Cooperation Treasury Bridge (Phase 10) — PR #2, merged
- Contributor Credit Candidate Layer (Phase 11) — PR #3
- External Credit Adapter Layer (Phase 12) — PR #4
- Credit Reflection Memory Layer (Phase 13) — PR #5
- Recognition Appeal Layer (Phase 14) — PR #6
- Recognition Ledger Layer (Phase 15) — PR #7
- Cooperation Commons Layer (Phase 16) — PR #8
- Mutual Aid Routing Layer (Phase 17) — PR #9
- Relief Case Memory Layer (Phase 18) — PR #10
- Care Loop Reopen Layer (Phase 19) — PR #11
- Aid Pattern Learning Layer (Phase 20) — PR #12, merged
- Commons Need Forecast Memory Layer (Phase 21) — PR #13, merged
- Globe Foundation Layer (Phase 22) — PR #14, merged
- Proposal → Claim Conversion Layer (Phase 23) — PR #15, merged
- Claim → Directive Conversion Layer (Phase 24) — PR #16, merged
- Directive Execution Log Layer (Phase 25) — PR #17, merged
- Cross-Globe Execution Log Summary (Phase 26) — PR #19, merged
- Directive UI Routes (Phase 28) — PR #20, merged
- Reality Feedback Bridge (Phase 27) — PR #21, merged
- Bridge Target Detail Link (Phase 27b) — PR #22, merged
- Voluntary Resolution Signal (Phase 29) — PR #23, merged
- Cross-Phase Contribution Summary (Phase 30) — PR #24, merged
- Globe Search / Filter UI (Phase 31) — PR #25, merged
- Contribution Timeline View (Phase 32) — PR #26, merged
- Proposal Comparison View (Phase 33) — PR #27, merged
- Activity Heatmap (Phase 34) — PR #28, merged
- Directive Execution Checklist (Phase 35) — PR #29, merged
- Globe Feed / Changelog (Phase 36) — PR #30, merged
- **Directive Dependency Map (Phase 37)** ← current PR

---

## Phase 20: Aid Pattern Learning Layer

Core principles:
> "Pattern is not prediction."
> "Learning is not prescription."
> "Recurrence is not ranking."

**Purpose:** Records recurring aid patterns observed across Phase 17–19
care histories. Dan-Go does not predict future need. Dan-Go does not
rank suffering. Dan-Go does not prescribe responses. Dan-Go only records
observable patterns and cross-phase pattern memory.

---

## Phase 21: Commons Need Forecast Memory Layer

Core principles:
> "Forecast is not certainty."
> "Preparedness is not command."
> "Hint is not allocation."

**Purpose:** Records preparedness memories derived from recurring aid
patterns observed in Phase 20. Dan-Go does not predict need. Dan-Go does
not command preparation. Dan-Go does not allocate resources. Dan-Go only
records observable preparedness hints for commons, grounded in observed
care history.

### Phase Chain

```
Phase 17: Mutual Aid Routing      → aid_route_recorded: true
Phase 18: Relief Case Memory      → care_history_complete: true
Phase 19: Care Loop Reopen        → care_loop_complete: true
Phase 20: Aid Pattern Learning    → pattern_learning_only: true
Phase 21: Need Forecast Memory    → forecast_memory_only: true
```

### Runtime Results

```
aid_pattern_registry.py
  registry_id: aid-pattern-registry-001
  pattern_count: 4
  commons_represented: [dra-001, jammy-house-001, yacypherpunks-001]
    aid-pattern-001: recurring_food_support (observed_count=3) pattern_is_prediction=false
    aid-pattern-002: ongoing_displacement_relief (observed_count=4) pattern_is_prediction=false
    aid-pattern-003: unresolved_tenancy_pattern (observed_count=2) pattern_is_prediction=false
    aid-pattern-004: pending_skill_exchange (observed_count=1) pattern_is_prediction=false
  pattern_ranks_commons=false

recurrence_snapshot.py
  snapshot_id: recurrence-snapshot-001
  recurrence_count: 4
    recurrence-001: food_need_reappeared (count=3) recurrence_is_ranking=false ranks_suffering=false
    recurrence-002: displacement_relief_ongoing (count=4) recurrence_is_ranking=false ranks_suffering=false
    recurrence-003: tenancy_unresolved_continued (count=2) recurrence_is_ranking=false ranks_suffering=false
    recurrence-004: skill_exchange_deferred (count=1) recurrence_is_ranking=false ranks_suffering=false
  urgency_note: No urgency ranking applied — recurrence_is_ranking: false on all records

pattern_memory_builder.py
  log_id: pattern-memory-log-001
  memory_count: 4
  status_summary: {recorded: 4}
    pattern-memory-001: recurring_food_support (jammy-house-001) memory_status=recorded learning_is_prescription=false
    pattern-memory-002: ongoing_displacement_relief (dra-001) memory_status=recorded learning_is_prescription=false
    pattern-memory-003: unresolved_tenancy_pattern (jammy-house-001) memory_status=recorded learning_is_prescription=false
    pattern-memory-004: pending_skill_exchange (yacypherpunks-001) memory_status=recorded learning_is_prescription=false
  memory_prescribes_response=false

aid_pattern_report.py
  report_id: aid-pattern-report-001
  section_count: 4
    A: A Pattern Is an Observation, Not a Prediction
    B: Recurrence Does Not Rank Suffering
    C: Learning Does Not Prescribe a Response
    D: Connection to Jammy House and D.R.A. Care Histories
  summary_table:
    pattern_is_prediction: false
    recurrence_is_ranking: false
    learning_is_prescription: false
    ranks_suffering: false
    any_participant_compelled: false
    pattern_history_is_legible: true
    loops_referenced: 4
    patterns_recorded: 4
    recurrences_recorded: 4

need_forecast_registry.py
  registry_id: need-forecast-registry-001
  forecast_count: 4
  commons_represented: [dra-001, jammy-house-001, yacypherpunks-001]
    need-forecast-001: recurring_food_support_possible (observed_count=3)
      confidence=observed_pattern_only forecast_is_certainty=false
    need-forecast-002: ongoing_displacement_relief_possible (observed_count=4)
      confidence=four_plus_observations forecast_is_certainty=false
    need-forecast-003: unresolved_tenancy_followup_possible (observed_count=2)
      confidence=two_observations forecast_is_certainty=false
    need-forecast-004: skill_exchange_rescheduling_possible (observed_count=1)
      confidence=single_observation forecast_is_certainty=false
  forecast_allocates_resources=false

preparedness_hint_snapshot.py
  snapshot_id: preparedness-hint-snapshot-001
  hint_count: 4
    preparedness-hint-001: meal_capacity_awareness (jammy-house-001)
      preparedness_is_command=false hint_is_allocation=false
    preparedness-hint-002: displacement_relief_readiness_awareness (dra-001)
      preparedness_is_command=false hint_is_allocation=false
    preparedness-hint-003: housing_advocacy_continuation_awareness (jammy-house-001)
      preparedness_is_command=false hint_is_allocation=false
    preparedness-hint-004: skill_exchange_rescheduling_awareness (yacypherpunks-001)
      preparedness_is_command=false hint_is_allocation=false
  hint_assigns_resources=false

forecast_memory_builder.py
  log_id: forecast-memory-log-001
  memory_count: 4
  status_summary: {recorded: 4}
    forecast-memory-001 through forecast-memory-004: all memory_status=recorded
    all forecast_is_certainty=false, memory_compels_preparation=false
    all memory_certifies_resolution=false, memory_allocates_resources=false

need_forecast_report.py
  report_id: need-forecast-report-001
  section_count: 5
    A: Forecast-Like Memory Exists — and What It Is Not
    B: Pattern Does Not Prove Future Need
    C: Preparedness Hint Does Not Command Action
    D: No Allocation Is Enforced — Commons Retain Full Resource Autonomy
    E: Connection to Jammy House and Refugee Relief
  summary_table:
    forecast_is_certainty: false
    preparedness_is_command: false
    hint_is_allocation: false
    any_participant_compelled: false
    commons_retain_autonomy: true
    forecast_history_is_legible: true
    forecasts_recorded: 4
    hints_recorded: 4
    memories_recorded: 4
```

---

## New Files (Phase 20)

- bridge/gitsea/aid_patterns/AID_PATTERN_LEARNING_SPEC.md
- bridge/gitsea/aid_patterns/PATTERN_NOT_PREDICTION.md
- bridge/gitsea/aid_patterns/LEARNING_NOT_PRESCRIPTION.md
- bridge/gitsea/aid_patterns/runtime/aid_pattern_registry.py
- bridge/gitsea/aid_patterns/runtime/recurrence_snapshot.py
- bridge/gitsea/aid_patterns/runtime/pattern_memory_builder.py
- bridge/gitsea/aid_patterns/runtime/aid_pattern_report.py
- bridge/gitsea/aid_patterns/examples/aid-pattern-registry.json (generated)
- bridge/gitsea/aid_patterns/examples/recurrence-snapshot.json (generated)
- bridge/gitsea/aid_patterns/examples/pattern-memory.json (generated)
- bridge/gitsea/aid_patterns/examples/aid-pattern-report.json (generated)

## Updated Files (Phase 20)

- bridge/gitsea/README.md (Phase 20 section + aid_patterns/ in layout + flow diagram + footer)

## New Files (Phase 21)

- bridge/gitsea/need_forecast/COMMONS_NEED_FORECAST_SPEC.md
- bridge/gitsea/need_forecast/FORECAST_NOT_CERTAINTY.md
- bridge/gitsea/need_forecast/PREPAREDNESS_NOT_COMMAND.md
- bridge/gitsea/need_forecast/runtime/need_forecast_registry.py
- bridge/gitsea/need_forecast/runtime/preparedness_hint_snapshot.py
- bridge/gitsea/need_forecast/runtime/forecast_memory_builder.py
- bridge/gitsea/need_forecast/runtime/need_forecast_report.py
- bridge/gitsea/need_forecast/examples/need-forecast-registry.json (generated)
- bridge/gitsea/need_forecast/examples/preparedness-hint-snapshot.json (generated)
- bridge/gitsea/need_forecast/examples/forecast-memory.json (generated)
- bridge/gitsea/need_forecast/examples/need-forecast-report.json (generated)

## Updated Files (Phase 21)

- bridge/gitsea/README.md (Phase 21 section + need_forecast/ in layout + flow diagram + footer)
- bridge/RESUME_STATE.md (this file)

---

## Key Invariants (all Phase 20 files)

| Field | Value |
|-------|-------|
| `authority` | `none` |
| `execution_allowed` | `false` |
| `moves_money` | `false` |
| `hard_enforcement` | `false` |
| `advisory` | `true` |
| `pattern_learning_only` | `true` |
| `append_only` | `true` |
| `contestable` | `true` |
| `reopenable` | `true` |
| `credit_issued` | `false` (permanent) |
| `pattern_is_prediction` | `false` (invariant) |
| `learning_is_prescription` | `false` (invariant) |
| `recurrence_is_ranking` | `false` (invariant) |
| `pattern_ranks_commons` | `false` (invariant) |
| `pattern_compels_response` | `false` (invariant) |
| `memory_prescribes_response` | `false` (invariant) |
| `memory_certifies_resolution` | `false` (invariant) |
| `memory_compels_new_aid` | `false` (invariant) |
| `memory_judges_participants` | `false` (invariant) |
| `ranks_suffering` | `false` (invariant) |
| `recurrence_judges_prior_response` | `false` (invariant) |
| `recurrence_demands_new_response` | `false` (invariant) |
| `recurrence_certifies_failure` | `false` (invariant) |

## Key Invariants (all Phase 21 files)

| Field | Value |
|-------|-------|
| `authority` | `none` |
| `execution_allowed` | `false` |
| `moves_money` | `false` |
| `hard_enforcement` | `false` |
| `advisory` | `true` |
| `forecast_memory_only` | `true` |
| `append_only` | `true` |
| `contestable` | `true` |
| `reopenable` | `true` |
| `credit_issued` | `false` (permanent) |
| `forecast_is_certainty` | `false` (invariant) |
| `preparedness_is_command` | `false` (invariant) |
| `hint_is_allocation` | `false` (invariant) |
| `forecast_allocates_resources` | `false` (invariant) |
| `forecast_compels_preparation` | `false` (invariant) |
| `hint_compels_action` | `false` (invariant) |
| `hint_assigns_resources` | `false` (invariant) |
| `hint_creates_obligation` | `false` (invariant) |
| `memory_certifies_resolution` | `false` (invariant) |
| `memory_compels_preparation` | `false` (invariant) |
| `memory_allocates_resources` | `false` (invariant) |
| `memory_judges_commons` | `false` (invariant) |

---

## Protocol Principle Accumulation (Phases 10–35)

| Phase | Phrase |
|-------|--------|
| 10 | "Signal is not reward." |
| 10 | "Dan-Go observes treasury context; it does not operate the treasury." |
| 11 | "Contribution history is not credit." |
| 11 | "Dan-Go records contribution candidates; external systems may issue credit." |
| 12 | "Observation is not issuance." |
| 12 | "Candidate credit is not external credit." |
| 13 | "Unrecognized contribution is still observable." |
| 13 | "Reflection is not judgment." |
| 14 | "Appeal is not enforcement." |
| 14 | "Recognition remains external." |
| 15 | "Recognition history is not authority." |
| 15 | "Ledger is not judgment." |
| 16 | "Community is not authority." |
| 16 | "Commons is not ownership." |
| 16 | "Participation is not control." |
| 17 | "Need is not debt." |
| 17 | "Help is not command." |
| 17 | "Routing is not allocation." |
| 18 | "Relief is not proof." |
| 18 | "Outcome is not judgment." |
| 18 | "Care memory is not control." |
| 19 | "Reopen is not failure." |
| 19 | "Follow-up is not blame." |
| 19 | "Care loop is not obligation." |
| 20 | "Pattern is not prediction." |
| 20 | "Learning is not prescription." |
| 20 | "Recurrence is not ranking." |
| 21 | "Forecast is not certainty." |
| 21 | "Preparedness is not command." |
| 21 | "Hint is not allocation." |
| 22 | "Globe is not state." |
| 22 | "Deliberation is not majority rule." |
| 22 | "Membership is not obligation." |
| 23 | "Proposal is not execution." |
| 23 | "Claim is not command." |
| 23 | "Conversion is not allocation." |
| 24 | "Claim is not execution." |
| 24 | "Directive is not coercion." |
| 24 | "Directive creates no legal authority." |
| 24 | "Directive only describes a proposed executable path." |
| 24 | "Human approval is required before real-world execution." |
| 25 | "Execution Log is not proof of execution." |
| 25 | "Log entry is not legal authority." |
| 25 | "Objection and rollback request must always be recordable." |
| 25 | "Append-only: existing entries must never be rewritten." |
| 26 | "Summary is advisory only." |
| 26 | "Summary is not proof of execution." |
| 26 | "Summary creates no legal authority." |
| 26 | "Summary does not rank or punish participants." |
| 26 | "Summary must preserve objections and rollback requests." |
| 27 | "Reality feedback is advisory only." |
| 27 | "Feedback bridge is not proof of resolution." |
| 27 | "Feedback bridge creates no legal authority." |
| 27 | "Feedback bridge does not reopen a case automatically." |
| 27 | "Human review is required before any real-world action." |
| 27b | "Bridge target link is advisory only." |
| 27b | "Link candidate is not proof of case relation." |
| 27b | "Link candidate creates no legal authority." |
| 27b | "Link candidate does not reopen a case automatically." |
| 27b | "Human review is required before any real-world action." |
| 28 | "UI display is advisory only." |
| 28 | "UI display is not proof of execution." |
| 28 | "UI display creates no legal authority." |
| 28 | "UI display does not approve execution." |
| 28 | "UI display must preserve objections and rollback requests." |
| 29 | "Resolution signal is self-reported only." |
| 29 | "Resolution signal is not proof of resolution." |
| 29 | "Resolution signal does not close support automatically." |
| 29 | "Resolution signal creates no legal authority." |
| 29 | "Contested status must always remain recordable." |
| 30 | "Cross-phase summary is advisory only." |
| 30 | "Cross-phase summary is not proof of impact." |
| 30 | "Cross-phase summary does not rank participants." |
| 30 | "Cross-phase summary does not allocate resources." |
| 30 | "Human review is required before any real-world action." |
| 31 | "Search is advisory display only." |
| 31 | "Search result is not proof of relevance." |
| 31 | "Search result does not rank participants." |
| 31 | "Search result does not allocate resources." |
| 31 | "Human review is required before any real-world action." |
| 32 | "Timeline is advisory display only." |
| 32 | "Timeline is not proof of impact." |
| 32 | "Timeline does not rank participants." |
| 32 | "Timeline does not allocate resources." |
| 32 | "Human review is required before any real-world action." |
| 33 | "Comparison is advisory display only." |
| 33 | "Comparison is not ranking." |
| 33 | "Comparison does not score proposals." |
| 33 | "Comparison does not allocate resources." |
| 33 | "Human review is required before any real-world action." |
| 34 | "Heatmap is advisory display only." |
| 34 | "Heatmap is not proof of impact." |
| 34 | "Heatmap does not rank participants." |
| 34 | "Heatmap does not allocate resources." |
| 34 | "Human review is required before any real-world action." |
| 35 | "Checklist is advisory display only." |
| 35 | "Checklist is not proof of execution." |
| 35 | "Checklist is not proof of completion." |
| 35 | "Checklist does not approve execution." |
| 35 | "Human review is required before any real-world action." |
| 36 | "Feed is advisory display only." |
| 36 | "Feed is not proof of execution." |
| 36 | "Feed is not proof of impact." |
| 36 | "Feed does not rank participants." |
| 36 | "Feed does not allocate resources." |
| 36 | "Human review is required before any real-world action." |
| 37 | "Dependency map is advisory display only." |
| 37 | "Dependency is not execution order." |
| 37 | "Dependency does not rank directives." |
| 37 | "Dependency does not allocate responsibility." |
| 37 | "Human review is required before any real-world action." |

---

## New Files (Phase 27b)

- `globe/runtime/bridge_target_linker.py` — Link candidate builder (advisory only)
- `globe/reports/bridge_target_links.json` — Generated link candidates report
- `globe/reports/bridge_target_links.md` — Generated Markdown report

## Updated Files (Phase 27b)

- `globe/runtime/globe_server.py` — Added `_load_link_report()`, `_render_link_candidates_panel()`, Phase 27b CSS; wired into Directive detail and Execution Log pages
- `globe/spec/GLOBE_SPEC.md` — Phase 27b section
- `README.md` — Phase 27b section with invariant quotes and CLI examples
- `bridge/RESUME_STATE.md` — this file

---

## New Files (Phase 29)

_No new files — Phase 29 extends existing runtime scripts._

## Updated Files (Phase 29)

- `globe/runtime/directive_execution_log.py` — Added `voluntary_resolution_signal` entry type, `--resolution-status` flag, Phase 29 invariants
- `globe/runtime/execution_log_summary.py` — Resolution signal aggregation (per-directive + per-globe + totals)
- `globe/runtime/reality_feedback_bridge.py` — `voluntary_resolution_signal` in BRIDGE_ENTRY_TYPES; unresolved/contested/paused routed to care_loop_reopen
- `globe/runtime/globe_server.py` — `_render_resolution_signal_stat()`, `_RS_ICON`, Phase 29 CSS, resolution signal in entry cards, directive detail, and summary table
- `globe/spec/GLOBE_SPEC.md` — Phase 29 section
- `README.md` — Phase 29 section with invariant quotes and CLI examples
- `bridge/RESUME_STATE.md` — this file

---

## New Files (Phase 30)

- `globe/runtime/cross_phase_contribution_summary.py` — Cross-phase summary builder (advisory only)
- `globe/reports/cross_phase_contribution_summary.json` — Generated cross-phase summary report
- `globe/reports/cross_phase_contribution_summary.md` — Generated Markdown report

## Updated Files (Phase 30)

- `globe/runtime/globe_server.py` — Added `_load_cross_phase_summary()`, `_render_cross_phase_panel()`, Phase 30 CSS; wired into Globe list and Globe detail pages
- `globe/spec/GLOBE_SPEC.md` — Phase 30 section
- `README.md` — Phase 30 section with invariant quotes and CLI examples
- `bridge/RESUME_STATE.md` — this file

---

## New Files (Phase 31)

- `globe/runtime/globe_search.py` — Search index builder + CLI (advisory display only)
- `globe/reports/globe_search_index.json` — Generated search index (36 items)

## Updated Files (Phase 31)

- `globe/runtime/globe_server.py` — Added `_load_search_index()`, `render_search_page()`, Phase 31 CSS; wired `/globe/search` route
- `globe/spec/GLOBE_SPEC.md` — Phase 31 section
- `README.md` — Phase 31 section with invariant quotes and CLI/URL examples
- `bridge/RESUME_STATE.md` — this file

---

## New Files (Phase 32)

- `globe/runtime/contribution_timeline.py` — Timeline builder + CLI (advisory only)
- `globe/reports/contribution_timeline.json` — Generated timeline (16 items)
- `globe/reports/contribution_timeline.md` — Human-readable timeline

## Updated Files (Phase 32)

- `globe/runtime/globe_server.py` — Added `_load_timeline()`, `render_timeline_page()`, Phase 32 CSS; wired `/globe/timeline`, `/globe/<id>/timeline`, `/globe/<id>/directives/<did>/timeline` routes
- `globe/spec/GLOBE_SPEC.md` — Phase 32 section
- `README.md` — Phase 32 section with invariant quotes and CLI/URL examples
- `bridge/RESUME_STATE.md` — this file

---

## New Files (Phase 33)

- `globe/runtime/proposal_compare.py` — Comparison builder + CLI (advisory only)
- `globe/reports/proposal_comparison_proposal-002_vs_proposal-005.json` — Sample comparison
- `globe/reports/proposal_comparison_proposal-002_vs_proposal-005.md` — Markdown report

## Updated Files (Phase 33)

- `globe/runtime/globe_server.py` — Added `render_compare_page()`, Phase 33 CSS; wired `/globe/compare` route
- `globe/spec/GLOBE_SPEC.md` — Phase 33 section
- `README.md` — Phase 33 section with invariant quotes and CLI/URL examples
- `bridge/RESUME_STATE.md` — this file

---

## New Files (Phase 34)

- `globe/runtime/activity_heatmap.py` — Heatmap builder + CLI (advisory only)
- `globe/reports/activity_heatmap.json` — Generated heatmap (2 dates, 16 events)
- `globe/reports/activity_heatmap.md` — Human-readable heatmap report

## Updated Files (Phase 34)

- `globe/runtime/globe_server.py` — Added `_REPORTS_DIR` (bugfix), `_load_heatmap()`, `render_activity_page()`, Phase 34 CSS; wired `/globe/activity` route with `?date=` and `?globe=` query params; added "🗓 Activity →" to Globe list header
- `globe/spec/GLOBE_SPEC.md` — Phase 34 section
- `README.md` — Phase 34 section with invariant quotes and CLI/URL examples
- `bridge/RESUME_STATE.md` — this file

---

## New Files (Phase 35)

- `globe/runtime/directive_checklist.py` — Checklist builder + CLI (advisory only)
- `globe/reports/directive_checklists.json` — Generated checklists (2 directives, 8 steps)
- `globe/reports/directive_checklists.md` — Human-readable checklist report

## Updated Files (Phase 35)

- `globe/runtime/globe_server.py` — Added `_load_checklists()`, `_render_cl_item()`, `render_checklist_page()`, Phase 35 CSS; wired `/globe/<id>/directives/<did>/checklist` route; added "📋 Checklist (N steps) →" link and attention note to Directive detail page
- `globe/spec/GLOBE_SPEC.md` — Phase 35 section
- `README.md` — Phase 35 section with invariant quotes and CLI/URL examples
- `bridge/RESUME_STATE.md` — this file

---

## New Files (Phase 37)

- `globe/runtime/directive_dependency_map.py` — Dependency detection + CLI (7 relation_types, 4 edges)
- `globe/reports/directive_dependency_map.json` — Generated dependency map JSON
- `globe/reports/directive_dependency_map.md` — Human-readable dependency map Markdown

## Updated Files (Phase 37)

- `globe/runtime/globe_server.py` — Added `_load_dependency_map()`, `_render_dep_node()`, `_render_dep_edge()`, `render_dependencies_page()`, Phase 37 CSS; wired `/globe/dependencies` route with `?globe=`, `?directive=`, `?relation=` query params; added "🗺️ Dep →" to Globe list header; updated docstring to Phase 22–37
- `globe/spec/GLOBE_SPEC.md` — Phase 37 section (7 relation_types, edge structure, CLI/HTTP routes)
- `README.md` — Phase 37 section with invariant quotes and CLI/URL examples
- `bridge/RESUME_STATE.md` — this file

---

## New Files (Phase 36)

- `globe/runtime/globe_feed.py` — Feed builder + CLI (9 source_types, 29 items, advisory only)
- `globe/reports/globe_feed.json` — Generated feed JSON
- `globe/reports/globe_feed.md` — Human-readable feed Markdown

## Updated Files (Phase 36)

- `globe/runtime/globe_server.py` — Added `_load_feed()`, `_render_fd_item()`, `render_feed_page()`, Phase 36 CSS; wired `/globe/feed` route with `?globe=` and `?type=` query params; added "📰 Feed →" to Globe list header; updated docstring to Phase 22–36
- `globe/spec/GLOBE_SPEC.md` — Phase 36 section (9 source_types, feed item structure, CLI/HTTP routes)
- `README.md` — Phase 36 section with invariant quotes and CLI/URL examples
- `bridge/RESUME_STATE.md` — this file

---

## Next Step Candidates

1. **Merge Phase 37 PR** — after review
2. **Phase 38: Globe Member Profile View** — advisory member activity summary,
   no identity verification, no authority grants
3. **Phase 39: Cross-Phase Dependency Timeline** — timeline view of dependency
   edge changes over time, advisory only

---

*dango-gitsea-bridge · authority: none · append-only · stdlib only · hard enforcement: forbidden*
*Signal is not reward.*
*Contribution history is not credit.*
*Observation is not issuance.*
*Candidate credit is not external credit.*
*Unrecognized contribution is still observable.*
*Reflection is not judgment.*
*Appeal is not enforcement.*
*Recognition remains external.*
*Recognition history is not authority.*
*Ledger is not judgment.*
*Community is not authority.*
*Commons is not ownership.*
*Participation is not control.*
*Need is not debt.*
*Help is not command.*
*Routing is not allocation.*
*Relief is not proof.*
*Outcome is not judgment.*
*Care memory is not control.*
*Reopen is not failure.*
*Follow-up is not blame.*
*Care loop is not obligation.*
*Pattern is not prediction.*
*Learning is not prescription.*
*Recurrence is not ranking.*
*Globe is not state.*
*Deliberation is not majority rule.*
*Membership is not obligation.*
*Proposal is not execution.*
*Claim is not command.*
*Conversion is not allocation.*
*Claim is not execution.*
*Directive is not coercion.*
*Directive creates no legal authority.*
*Directive only describes a proposed executable path.*
*Human approval is required before real-world execution.*
*Execution Log is not proof of execution.*
*Log entry is not legal authority.*
*Objection and rollback request must always be recordable.*
*Append-only: existing entries must never be rewritten.*
*Summary is advisory only.*
*Summary is not proof of execution.*
*Summary creates no legal authority.*
*Summary does not rank or punish participants.*
*Summary must preserve objections and rollback requests.*
*Reality feedback is advisory only.*
*Feedback bridge is not proof of resolution.*
*Feedback bridge creates no legal authority.*
*Feedback bridge does not reopen a case automatically.*
*Human review is required before any real-world action.*
*UI display is advisory only.*
*UI display is not proof of execution.*
*UI display creates no legal authority.*
*UI display does not approve execution.*
*UI display must preserve objections and rollback requests.*
*Resolution signal is self-reported only.*
*Resolution signal is not proof of resolution.*
*Resolution signal does not close support automatically.*
*Resolution signal creates no legal authority.*
*Contested status must always remain recordable.*
*Bridge target link is advisory only.*
*Link candidate is not proof of case relation.*
*Link candidate creates no legal authority.*
*Link candidate does not reopen a case automatically.*
*Human review is required before any real-world action.*
*Dan-Go observes treasury context; it does not operate the treasury.*
*Dan-Go records contribution candidates; external systems may issue credit.*
*Dan-Go records commons participation; it does not govern communities.*
*Dan-Go records mutual aid routes; it does not command or allocate.*
*Dan-Go records relief case memory; it does not certify rescue or rank suffering.*
*Dan-Go records care loops; it does not compel resolution or judge participants.*
*Dan-Go records aid patterns; it does not predict, prescribe, or rank.*
*Forecast is not certainty.*
*Preparedness is not command.*
*Hint is not allocation.*
*Dan-Go records preparedness hints; it does not predict, command, or allocate.*
*Comparison is advisory display only.*
*Comparison is not ranking.*
*Comparison does not score proposals.*
*Comparison does not allocate resources.*
*Heatmap is advisory display only.*
*Heatmap is not proof of impact.*
*Heatmap does not rank participants.*
*Heatmap does not allocate resources.*
*Checklist is advisory display only.*
*Checklist is not proof of execution.*
*Checklist is not proof of completion.*
*Checklist does not approve execution.*
*Feed is advisory display only.*
*Feed is not proof of execution.*
*Feed is not proof of impact.*
*Feed does not rank participants.*
*Feed does not allocate resources.*
*Dependency map is advisory display only.*
*Dependency is not execution order.*
*Dependency does not rank directives.*
*Dependency does not allocate responsibility.*
*Contribution becomes legible before it becomes valuable.*
