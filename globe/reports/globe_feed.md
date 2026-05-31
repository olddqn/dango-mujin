# Globe Feed / Changelog (Phase 36)

generated_at: 2026-05-31 12:36:49
total_items: 29

## Source Type Counts

| source_type | count |
|-------------|-------|
| `activity_heatmap` | 1 |
| `bridge_target_link` | 4 |
| `claim` | 2 |
| `directive` | 2 |
| `directive_checklist` | 2 |
| `execution_log` | 8 |
| `proposal` | 5 |
| `reality_feedback` | 4 |
| `timeline` | 1 |

## Invariants

| Key | Value |
|-----|-------|
| `feed_is_advisory_display_only` | `True` |
| `feed_is_not_proof_of_execution` | `True` |
| `feed_is_not_proof_of_impact` | `True` |
| `feed_does_not_rank_participants` | `True` |
| `feed_does_not_allocate_resources` | `True` |
| `human_review_is_required_before_any_real_world_action` | `True` |
| `authority` | `none` |

> Feed is advisory display only. It is not proof of execution, impact, or ranking. Human review is required before any real-world action.

## Feed Items (created_at desc)

### feed-cl-directive-claim-proposal-002
**type:** `directive_checklist` &nbsp; **globe:** `globe-001` &nbsp; **created_at:** `2026-05-31 12:14:50`
**title:** Checklist: 難民・避難民支援を第零国家の優先課題として位置づける — 4 steps
> log_entries: 6  ⚠️ 4 attention
source: `globe/reports/directive_checklists.json`

### feed-cl-directive-claim-proposal-005
**type:** `directive_checklist` &nbsp; **globe:** `globe-003` &nbsp; **created_at:** `2026-05-31 12:14:50`
**title:** Checklist: 住居アドボカシー継続のための合意形成プロセスを確立する — 4 steps
> log_entries: 2  no attention flags
source: `globe/reports/directive_checklists.json`

### feed-heatmap-report
**type:** `activity_heatmap` &nbsp; **globe:** `—` &nbsp; **created_at:** `2026-05-31 11:51:36`
**title:** Activity Heatmap generated — 16 events · 2 dates
> date_range: 2026-05-30 — 2026-05-31  attention_events: 5
source: `globe/reports/activity_heatmap.json`

### feed-timeline-report
**type:** `timeline` &nbsp; **globe:** `—` &nbsp; **created_at:** `2026-05-31 11:30:46`
**title:** Contribution Timeline generated — 16 items
> date_range:  —   source_types: execution_log, reality_feedback, bridge_target_link, resolution_signal
source: `globe/reports/contribution_timeline.json`

### feed-exec-log-002
**type:** `execution_log` &nbsp; **globe:** `globe-003` &nbsp; **created_at:** `2026-05-31 04:27:33`
**title:** Log: voluntary resolution signal — Jammy House Steward
> 住居アドボカシーは未解決として継続観察する
source: `globe/logs/directive-claim-proposal-005.jsonl`

### feed-rfb-rfb-004
**type:** `reality_feedback` &nbsp; **globe:** `globe-003` &nbsp; **created_at:** `2026-05-31 04:27:33`
**title:** Reality Feedback: voluntary resolution signal → bridge:both
> 住居アドボカシーは未解決として継続観察する
source: `globe/reports/reality_feedback_bridge.json`

### feed-exec-log-006
**type:** `execution_log` &nbsp; **globe:** `globe-001` &nbsp; **created_at:** `2026-05-31 04:27:29`
**title:** Log: voluntary resolution signal — Masuo Komori
> D.R.A.連携の前提整理はいったん一区切りとする
source: `globe/logs/directive-claim-proposal-002.jsonl`

### feed-lnk-lnk-001
**type:** `bridge_target_link` &nbsp; **globe:** `globe-001` &nbsp; **created_at:** `2026-05-31 01:00:22`
**title:** Bridge Link: none (confidence: low)
> No bridge target suggested — no link candidate generated
source: `globe/reports/bridge_target_links.json`

### feed-lnk-lnk-002
**type:** `bridge_target_link` &nbsp; **globe:** `globe-001` &nbsp; **created_at:** `2026-05-31 01:00:22`
**title:** Bridge Link: relief_case_memory (confidence: high)
> Supply coordination was observed for displaced family. Basic supplies reached the household.
source: `globe/reports/bridge_target_links.json`

### feed-lnk-lnk-003
**type:** `bridge_target_link` &nbsp; **globe:** `globe-001` &nbsp; **created_at:** `2026-05-31 01:00:22`
**title:** Bridge Link: relief_case_memory (confidence: high)
> Shelter hosting was observed to have been accepted. Family housed for 5 days.
source: `globe/reports/bridge_target_links.json`

### feed-lnk-lnk-004
**type:** `bridge_target_link` &nbsp; **globe:** `globe-001` &nbsp; **created_at:** `2026-05-31 01:00:22`
**title:** Bridge Link: none (confidence: low)
> No bridge target suggested — no link candidate generated
source: `globe/reports/bridge_target_links.json`

### feed-exec-log-004
**type:** `execution_log` &nbsp; **globe:** `globe-001` &nbsp; **created_at:** `2026-05-30 23:16:45`
**title:** Log: human approval — Masuo Komori
> 試験的実施に向けた人間承認を記録する
source: `globe/logs/directive-claim-proposal-002.jsonl`

### feed-exec-log-005
**type:** `execution_log` &nbsp; **globe:** `globe-001` &nbsp; **created_at:** `2026-05-30 23:16:45`
**title:** Log: observation — Dan-Go Agent
> 実行前提条件の確認が必要
source: `globe/logs/directive-claim-proposal-002.jsonl`

### feed-rfb-rfb-003
**type:** `reality_feedback` &nbsp; **globe:** `globe-001` &nbsp; **created_at:** `2026-05-30 23:16:45`
**title:** Reality Feedback: observation → bridge:none
> 実行前提条件の確認が必要
source: `globe/reports/reality_feedback_bridge.json`

### feed-exec-log-003
**type:** `execution_log` &nbsp; **globe:** `globe-001` &nbsp; **created_at:** `2026-05-30 23:12:26`
**title:** Log: objection — founding-member-003
> D.R.A.との連携前にコミュニティ内の合意確認が必要と考える
source: `globe/logs/directive-claim-proposal-002.jsonl`

### feed-rfb-rfb-002
**type:** `reality_feedback` &nbsp; **globe:** `globe-001` &nbsp; **created_at:** `2026-05-30 23:12:26`
**title:** Reality Feedback: objection → bridge:relief_case_memory
> D.R.A.との連携前にコミュニティ内の合意確認が必要と考える
source: `globe/reports/reality_feedback_bridge.json`

### feed-exec-log-001
**type:** `execution_log` &nbsp; **globe:** `globe-003` &nbsp; **created_at:** `2026-05-30 23:12:22`
**title:** Log: execution attempt — jammy-house-member-002
> テナンシー合意形成フローの試験実施を開始する
source: `globe/logs/directive-claim-proposal-005.jsonl`

### feed-exec-log-002
**type:** `execution_log` &nbsp; **globe:** `globe-001` &nbsp; **created_at:** `2026-05-30 23:12:15`
**title:** Log: observation — Dan-Go Agent
> 実行前提条件の確認が必要
source: `globe/logs/directive-claim-proposal-002.jsonl`

### feed-rfb-rfb-001
**type:** `reality_feedback` &nbsp; **globe:** `globe-001` &nbsp; **created_at:** `2026-05-30 23:12:15`
**title:** Reality Feedback: observation → bridge:none
> 実行前提条件の確認が必要
source: `globe/reports/reality_feedback_bridge.json`

### feed-exec-log-001
**type:** `execution_log` &nbsp; **globe:** `globe-001` &nbsp; **created_at:** `2026-05-30 23:12:10`
**title:** Log: human approval — Masuo Komori
> 試験的実施に向けた人間承認を記録する
source: `globe/logs/directive-claim-proposal-002.jsonl`

### feed-directive-directive-claim-proposal-005
**type:** `directive` &nbsp; **globe:** `globe-003` &nbsp; **created_at:** `2026-05-30 14:40:11`
**title:** Directive: 住居アドボカシー継続のための合意形成プロセスを確立する
> Jammy Houseにおけるテナンシー問題を、個別対応から合意形成プロセスへと移行する
source: `globe/directives/directive-claim-proposal-005.json`

### feed-directive-directive-claim-proposal-002
**type:** `directive` &nbsp; **globe:** `globe-001` &nbsp; **created_at:** `2026-05-30 14:35:26`
**title:** Directive: 難民・避難民支援を第零国家の優先課題として位置づける
> 難民・避難民支援を第零国家の中核的優先課題の一つとして正式に位置づける
source: `globe/directives/directive-claim-proposal-002.json`

### feed-claim-claim-proposal-005
**type:** `claim` &nbsp; **globe:** `globe-003` &nbsp; **created_at:** `2026-05-30 14:20:52`
**title:** Claim: 住居アドボカシー継続のための合意形成プロセスを確立する
source: `globe/claims/claim-proposal-005.json`

### feed-claim-claim-proposal-002
**type:** `claim` &nbsp; **globe:** `globe-001` &nbsp; **created_at:** `2026-05-30 14:17:24`
**title:** Claim: 難民・避難民支援を第零国家の優先課題として位置づける
source: `globe/claims/claim-proposal-002.json`

### feed-proposal-proposal-005
**type:** `proposal` &nbsp; **globe:** `globe-003` &nbsp; **created_at:** `2026-05-30 04:00:00`
**title:** Proposal: 住居アドボカシー継続のための合意形成プロセスを確立する
> 提案：Jammy Houseにおけるテナンシー問題を、個別対応から合意形成プロセスへと移行する。具体的には、住居問題が発生した場合に熟議→提案→実行のフローを通じて対応する仕組みを確立する。  Phase 17-20で観察された未解決テナン…
source: `globe/data/proposals.json`

### feed-proposal-proposal-004
**type:** `proposal` &nbsp; **globe:** `globe-003` &nbsp; **created_at:** `2026-05-30 03:00:00`
**title:** Proposal: 食料支援の定期化と相互扶助スケジュールの確立
> 提案：Jammy Houseにおける食料支援を、アドホックな対応から定期的な相互扶助スケジュールへと移行する。Phase 17-20で観察された食料支援ニーズの繰り返しパターンを踏まえ、週次の食事準備協力と月次のフードパントリー訪問をスケジ…
source: `globe/data/proposals.json`

### feed-proposal-proposal-003
**type:** `proposal` &nbsp; **globe:** `globe-002` &nbsp; **created_at:** `2026-05-30 02:00:00`
**title:** Proposal: プライバシー保護ツールの共同開発と相互扶助的配布
> 提案：YaCypherpunks Commonsとして、プライバシー保護ツールを共同開発し、技術的アクセスが困難なコミュニティへの相互扶助的配布を行う。  具体的手段： - ワークショップによる技術共有 - 翻訳・多言語化 - オフラインで…
source: `globe/data/proposals.json`

### feed-proposal-proposal-002
**type:** `proposal` &nbsp; **globe:** `globe-001` &nbsp; **created_at:** `2026-05-30 01:00:00`
**title:** Proposal: 難民・避難民支援を第零国家の優先課題として位置づける
> 提案：難民・避難民支援を第零国家の中核的優先課題の一つとして正式に位置づける。具体的には、D.R.A.（難民支援行動）との連携を深め、住居・食料・法的支援・コミュニティ統合のための相互扶助ルートを構築する。  背景：既存の国家・機関による支…
source: `globe/data/proposals.json`

### feed-proposal-proposal-001
**type:** `proposal` &nbsp; **globe:** `globe-001` &nbsp; **created_at:** `2026-05-30 00:00:00`
**title:** Proposal: Dan-Go プロトコルを第零国家の公式合意形成ルールとして採用する
> 提案：Dan-GoのMujinプロトコル（MUJIN_PROTOCOL.md参照）を第零国家の公式な合意形成・意思決定フレームワークとして正式に採用する。  理由： 1. Dan-Goは多数決ではなく熟議・合意形成を重視する。 2. AIエ…
source: `globe/data/proposals.json`

> "Feed is advisory display only."
> "Feed is not proof of execution."
> "Feed is not proof of impact."
> "Feed does not rank participants."
> "Feed does not allocate resources."
> "Human review is required before any real-world action."