# Bridge Target Links Report (Phase 27b)

> **Bridge target link is advisory only.**
> **Link candidate is not proof of case relation.**
> **Link candidate creates no legal authority.**
> **Link candidate does not reopen a case automatically.**
> **Human review is required before any real-world action.**

Generated: 2026-05-31 01:00:22

## Summary

| Field | Value |
|-------|-------|
| total_feedback_records | 3 |
| total_link_candidates | 4 |
| 🔴 high | 2 |
| 🟡 medium | 0 |
| ⚪ low | 2 |
| authority | none |

## By Feedback Record

- **rfb-001** → `none`  candidates: 1  (high: 0  medium: 0  low: 1)
- **rfb-002** → `relief_case_memory`  candidates: 2  (high: 2  medium: 0  low: 0)
- **rfb-003** → `none`  candidates: 1  (high: 0  medium: 0  low: 1)

## All Link Candidates

### lnk-001  ⚪ LOW
- source_feedback_id: `rfb-001`
- source_directive_id: `directive-claim-proposal-002`
- suggested_bridge_target: `none`
- **candidate_target_type:** `none`
- candidate_path: `null`
- candidate_item_id: `null`
- candidate_item_type: `null`
- candidate_description: No bridge target suggested — no link candidate generated
- match_reason: suggested_bridge_target is 'none' — no automated link candidate generated; human review may identify a Phase 18 or Phase 19 connection
- confidence: **low**
- requires_human_review: true
- creates_no_legal_authority: true
- does_not_reopen_case_automatically: true
- advisory_only: true

### lnk-002  🔴 HIGH
- source_feedback_id: `rfb-002`
- source_directive_id: `directive-claim-proposal-002`
- suggested_bridge_target: `relief_case_memory`
- **candidate_target_type:** `relief_case_memory`
- candidate_path: `bridge/gitsea/relief/examples/relief-case-registry.json`
- candidate_item_id: `relief-case-003`
- candidate_item_type: `relief_case`
- candidate_description: Supply coordination was observed for displaced family. Basic supplies reached the household.
- match_reason: commons_id match (dra-001 detected in feedback content) + case_type 'refugee_relief_followup' contains matching relief/housing keywords  [case_type: refugee_relief_followup  commons: dra-001  status: observed]
- confidence: **high**
- requires_human_review: true
- creates_no_legal_authority: true
- does_not_reopen_case_automatically: true
- advisory_only: true

### lnk-003  🔴 HIGH
- source_feedback_id: `rfb-002`
- source_directive_id: `directive-claim-proposal-002`
- suggested_bridge_target: `relief_case_memory`
- **candidate_target_type:** `relief_case_memory`
- candidate_path: `bridge/gitsea/relief/examples/relief-case-registry.json`
- candidate_item_id: `relief-case-004`
- candidate_item_type: `relief_case`
- candidate_description: Shelter hosting was observed to have been accepted. Family housed for 5 days.
- match_reason: commons_id match (dra-001 detected in feedback content) + case_type 'shelter_followup' contains matching relief/housing keywords  [case_type: shelter_followup  commons: dra-001  status: completed]
- confidence: **high**
- requires_human_review: true
- creates_no_legal_authority: true
- does_not_reopen_case_automatically: true
- advisory_only: true

### lnk-004  ⚪ LOW
- source_feedback_id: `rfb-003`
- source_directive_id: `directive-claim-proposal-002`
- suggested_bridge_target: `none`
- **candidate_target_type:** `none`
- candidate_path: `null`
- candidate_item_id: `null`
- candidate_item_type: `null`
- candidate_description: No bridge target suggested — no link candidate generated
- match_reason: suggested_bridge_target is 'none' — no automated link candidate generated; human review may identify a Phase 18 or Phase 19 connection
- confidence: **low**
- requires_human_review: true
- creates_no_legal_authority: true
- does_not_reopen_case_automatically: true
- advisory_only: true

---

*Bridge target link is advisory only.*
*Link candidate is not proof of case relation.*
*Link candidate creates no legal authority.*
*Link candidate does not reopen a case automatically.*
*Human review is required before any real-world action.*