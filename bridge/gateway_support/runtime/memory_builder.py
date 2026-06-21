"""
memory_builder.py — Support Memory layer (F-19).

Append-only memory of support EPISODES. One memory record per execution episode,
recording the support_form TYPE and the observed outcome type — never the gateway
identity. There is deliberately NO gateway reference: memory must not enable
gateway aggregation, evaluation, ranking, reputation, or profiling
(links_no_actor). Learning is type-level only: counts of support_form types and
outcome types across episodes — never per-gateway.

CLI:
  python -m bridge.gateway_support.runtime.memory_builder
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from ..store import (
    SUPPORT_MEMORY_JSONL, append_jsonl, base_invariants, carries_base_invariants,
    next_id, read_jsonl,
)
from .execution_builder import list_executions
from .feedback_builder import list_feedback
from .withdrawal_builder import is_halted


def _outcome_type(execution_id: str, bottleneck_id: str) -> str:
    if is_halted(bottleneck_id):
        return "withdrawn"
    fbs = [f for f in list_feedback() if f.get("execution_id") == execution_id]
    if any(f.get("relief_observed") for f in fbs):
        return "relief_observed"
    if fbs:
        return "relief_held"
    return "no_feedback_yet"


def _existing() -> set[str]:
    return {m.get("episode_ref") for m in read_jsonl(SUPPORT_MEMORY_JSONL)}


def build() -> list[dict[str, Any]]:
    """One episode-unit memory per execution (idempotent). No gateway identity stored."""
    done = _existing()
    created = []
    for e in list_executions():
        eid = e.get("execution_id")
        if eid in done:
            continue
        rec = {
            "record_type": "support_memory",
            "memory_id": next_id("pm", SUPPORT_MEMORY_JSONL),
            "episode_ref": eid,                       # the execution episode
            "support_form_type": e.get("support_form"),  # TYPE, not an actor
            "outcome_type": _outcome_type(eid, e.get("bottleneck_id")),
            # F-19 markers — note: NO gateway_ref field (links_no_actor)
            "is_episode_unit": True,
            "links_no_actor": True,
            "no_gateway_aggregation": True,
            "no_gateway_evaluation": True,
            "no_gateway_ranking_here": True,
            "no_gateway_reputation": True,
            "no_gateway_profile": True,
            "learns_only_support_pattern_types": True,
            "status": "remembered",
            **base_invariants(),
        }
        created.append(append_jsonl(SUPPORT_MEMORY_JSONL, rec))
        done.add(eid)
    return created


def list_memory() -> list[dict[str, Any]]:
    return read_jsonl(SUPPORT_MEMORY_JSONL)


def learn_support_pattern_types() -> dict[str, dict[str, int]]:
    """Type-level aggregate learning ONLY — no gateway, no actor. Counts of
    support_form types and outcome types across episodes."""
    mem = list_memory()
    return {
        "by_support_form_type": dict(Counter(m.get("support_form_type") for m in mem)),
        "by_outcome_type": dict(Counter(m.get("outcome_type") for m in mem)),
        "episode_count": len(mem),
    }


def check_invariants() -> list[str]:
    violations: list[str] = []
    for m in list_memory():
        violations += carries_base_invariants(m)
        for f in ("is_episode_unit", "links_no_actor", "no_gateway_aggregation",
                  "no_gateway_evaluation", "no_gateway_reputation", "no_gateway_profile",
                  "learns_only_support_pattern_types"):
            if m.get(f) is not True:
                violations.append(f"{m.get('memory_id')}: missing/false {f}")
        # structural: memory must NOT carry a gateway identity (no profiling)
        for f in ("gateway_ref", "gateway_id", "gateway"):
            if f in m:
                violations.append(f"{m.get('memory_id')}: stores gateway identity {f} (profiling)")
    return violations


def main() -> None:
    print("=" * 64)
    print("SUPPORT MEMORY BUILDER (F-19) — append-only episodes, no gateway profiling")
    print("=" * 64)
    created = build()
    mem = list_memory()
    print(f"  support memory episodes: {len(mem)}  (0 is valid)")
    for m in mem:
        print(f"  · {m['memory_id']} episode={m['episode_ref']} form_type={m['support_form_type']} outcome={m['outcome_type']}")
    print(f"  type-level learning: {learn_support_pattern_types()}")
    v = check_invariants()
    print(f"  invariant violations: {len(v)}")
    for x in v:
        print(f"    - {x}")
    print("-" * 64)
    print("Memory is episode-unit, append-only. No gateway score/ranking/reputation/profile. Type-level learning only.")


if __name__ == "__main__":
    main()
