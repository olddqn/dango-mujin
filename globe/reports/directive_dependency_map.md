# Directive Dependency Map (Phase 37)

generated_at: 2026-05-31 13:08:31
directive_count: 2
edge_count: 4

## Invariants

| Key | Value |
|-----|-------|
| `dependency_map_is_advisory_display_only` | `True` |
| `dependency_is_not_execution_order` | `True` |
| `dependency_does_not_rank_directives` | `True` |
| `dependency_does_not_allocate_responsibility` | `True` |
| `human_review_is_required_before_any_real_world_action` | `True` |
| `authority` | `none` |

> Dependency map is advisory display only. It is not execution order, not a ranking of directives, and does not allocate responsibility. Human review is required before any real-world action.

## Relation Type Counts

| relation_type | count |
|---------------|-------|
| `shared_attention_marker` | 1 |
| `shared_bridge_target` | 1 |
| `shared_keyword` | 2 |

## Nodes (Directives)

### directive-claim-proposal-002
**globe_id:** `globe-001` &nbsp; **steps:** 4 &nbsp; **logs:** 6
**title:** 難民・避難民支援を第零国家の優先課題として位置づける
**resolution_status:** partially_resolved
**bridge_targets:** relief_case_memory

### directive-claim-proposal-005
**globe_id:** `globe-003` &nbsp; **steps:** 4 &nbsp; **logs:** 2
**title:** 住居アドボカシー継続のための合意形成プロセスを確立する
**resolution_status:** unresolved
**bridge_targets:** both

## Edges (Relations)

### edge-shared_keyword-002-005
**directive-claim-proposal-002** ↔ **directive-claim-proposal-005**
relation_type: `shared_keyword` &nbsp; confidence: `high`
reason: Shared non-template scope item(s): "住居アドボカシーの熟議フロー運用"
shared_terms: 住居アドボカシーの熟議フロー運用

### edge-shared_keyword-002-005-1
**directive-claim-proposal-002** ↔ **directive-claim-proposal-005**
relation_type: `shared_keyword` &nbsp; confidence: `low`
reason: Shared protocol-template scope items (3 items) — these derive from the Dan-Go Directive template
shared_terms: ログへの追記, 実行フィードバック, 熟議ログに基づく未解決論点の整理と記録, 関係者への情報共有と任意参加意思の確認

### edge-shared_bridge_target-002-005
**directive-claim-proposal-002** ↔ **directive-claim-proposal-005**
relation_type: `shared_bridge_target` &nbsp; confidence: `low`
reason: One directive has 'both' bridge target; other references relief_case_memory — possible shared bridge connection
shared_terms: relief_case_memory

### edge-shared_attention_marker-002-005
**directive-claim-proposal-002** ↔ **directive-claim-proposal-005**
relation_type: `shared_attention_marker` &nbsp; confidence: `medium`
reason: Both directives' logs contain entry_type 'voluntary_resolution_signal' — shared attention signal
shared_terms: voluntary_resolution_signal

> "Dependency map is advisory display only."
> "Dependency is not execution order."
> "Dependency does not rank directives."
> "Dependency does not allocate responsibility."
> "Human review is required before any real-world action."