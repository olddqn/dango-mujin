"""
task_candidate_builder.py — Phase H-2: Observation Candidate → Task Candidate.

A Task Candidate is a WORK CANDIDATE, not a request, not an order, not an
assignment. No agent is assigned. Agent participation is always voluntary.
Tasks are research / discovery / counter-argument — they help humans observe.
They never define a Need, never select a Gateway, never form a Cooperation.

"Task is not assignment." "Task is not order."

CLI:
  python -m bridge.agent_commons.runtime.task_candidate_builder
"""

from __future__ import annotations

from typing import Any

from .store import (
    OBSERVATION_JSONL, TASK_JSONL, append_jsonl, base_invariants, next_id,
    read_jsonl,
)

TASK_TYPES = [
    "research", "translation", "counter_argument", "similar_case_search",
    "solution_discovery", "cooperation_discovery", "gateway_discovery",
    "legal_research", "funding_research", "technical_design",
]

# bottleneck → candidate research/discovery tasks (NOT assignments, NOT need-defs)
_BOTTLENECK_TASKS = {
    "funding":     ["funding_research", "similar_case_search"],
    "volunteer":   ["cooperation_discovery", "gateway_discovery"],
    "translation": ["translation", "similar_case_search"],
    "legal":       ["legal_research", "research"],
    "housing":     ["gateway_discovery", "solution_discovery"],
    "medical":     ["gateway_discovery", "research"],
    "food":        ["gateway_discovery", "cooperation_discovery"],
    "education":   ["solution_discovery", "similar_case_search"],
    "employment":  ["solution_discovery", "research"],
}

# task_type → neutral description (research/discovery framing; never "fulfil need")
_TASK_DESC = {
    "research":             "観測内容に関する公開情報の調査（決定ではない）",
    "translation":          "公開された声の翻訳補助（advisory・意味を変えない）",
    "counter_argument":     "この観測（voice_type・bottleneck）への反証・別解釈の探索",
    "similar_case_search":  "類似の公開支援要請・事例の調査",
    "solution_discovery":   "関連しうる解決アプローチの調査（選定ではない）",
    "cooperation_discovery":"関連しうる協力経路の調査（形成ではない）",
    "gateway_discovery":    "関連しうる公開 Gateway 類型の調査（選定ではない）",
    "legal_research":       "関連する法的論点の調査（助言ではない・参照のみ）",
    "funding_research":     "公開された資金経路・助成の調査（配分ではない）",
    "technical_design":     "観測を支援する技術的整理（実行ではない）",
}


def propose_tasks(observation: dict[str, Any]) -> list[dict[str, Any]]:
    """Propose research/discovery task candidates for one observation.

    Always includes counter_argument (contestability). Never assigns an agent."""
    types: list[str] = []
    for b in observation.get("observed_bottleneck", []):
        for t in _BOTTLENECK_TASKS.get(b, []):
            if t not in types:
                types.append(t)
    if observation.get("voice_type") in ("gateway_voice", "intermediary_voice"):
        for t in ("gateway_discovery", "similar_case_search"):
            if t not in types:
                types.append(t)
    if not types:
        types = ["research", "similar_case_search"]
    # contestability is mandatory: always offer a counter-argument task
    if "counter_argument" not in types:
        types.append("counter_argument")
    return [{"task_type": t, "description": _TASK_DESC.get(t, t)} for t in types]


def _already_tasked() -> set[str]:
    return {t.get("source_observation_id") for t in read_jsonl(TASK_JSONL)}


def build() -> list[dict[str, Any]]:
    """Build Task Candidates for observations not yet processed (idempotent)."""
    done = _already_tasked()
    created = []
    for obs in read_jsonl(OBSERVATION_JSONL):
        oid = obs.get("observation_id")
        if not oid or oid in done:
            continue
        for proposal in propose_tasks(obs):
            record = {
                "record_type": "task_candidate",
                "task_id": next_id("task", TASK_JSONL),
                "source_observation_id": oid,
                "source_voice_id": obs.get("source_voice_id"),
                "task_type": proposal["task_type"],
                "description": proposal["description"],
                "assigned_agent": None,          # never assigned
                "task_is_not_assignment": True,
                "task_is_not_order": True,
                "agent_participation_is_voluntary": True,
                "human_review_required": True,
                "defines_need": False,
                "selects_gateway": False,
                **base_invariants(),
            }
            created.append(append_jsonl(TASK_JSONL, record))
        done.add(oid)
    return created


def main() -> None:
    print("=" * 64)
    print("HERMES TASK CANDIDATE BUILDER — observations → task candidates")
    print('  "Task is not assignment." "Task is not order." voluntary · advisory')
    print("=" * 64)
    created = build()
    if not created:
        print("  (no new observations to process — append-only, idempotent)")
    for t in created:
        print(f"  ✓ {t['task_id']} ← {t['source_observation_id']} | "
              f"{t['task_type']} | assigned_agent={t['assigned_agent']}")
    print("-" * 64)
    print("No agent assigned. No Need defined. No Gateway selected.")


if __name__ == "__main__":
    main()
