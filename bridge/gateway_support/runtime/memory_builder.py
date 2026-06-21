"""
memory_builder.py — Support Memory layer (F-19), on the SHARED edge memory.

Route B no longer keeps its own memory store: support episodes are recorded into
the shared edge_memory (route="gateway_support"), so there is a single memory
layer for both routes. Each support execution becomes one episode-unit record
storing the support_form TYPE and observed outcome type — with NO gateway
identity (links_no_actor), so no gateway aggregation/evaluation/ranking/
reputation/profile is possible. Learning is type-level only.

CLI:
  python -m bridge.gateway_support.runtime.memory_builder
"""

from __future__ import annotations

from typing import Any

from bridge.edge_runtime.runtime import edge_memory
from .execution_builder import list_executions
from .feedback_builder import list_feedback
from .withdrawal_builder import is_halted

ROUTE = "gateway_support"


def _outcome_type(execution_id: str, bottleneck_id: str) -> str:
    if is_halted(bottleneck_id):
        return "withdrawn"
    fbs = [f for f in list_feedback() if f.get("execution_id") == execution_id]
    if any(f.get("relief_observed") for f in fbs):
        return "relief_observed"
    if fbs:
        return "relief_held"
    return "no_feedback_yet"


def build() -> list[dict[str, Any]]:
    """One shared edge-memory episode per execution (idempotent via edge_memory)."""
    created = []
    for e in list_executions():
        rec = edge_memory.record_episode(
            edge_id=e.get("edge_id") or e.get("bottleneck_id"),
            route=ROUTE,
            episode_ref=e.get("execution_id"),
            episode_kind=e.get("support_form"),                 # TYPE, not an actor
            outcome_type=_outcome_type(e.get("execution_id"), e.get("bottleneck_id")))
        if rec is not None:
            created.append(rec)
    return created


def list_memory() -> list[dict[str, Any]]:
    return edge_memory.list_memory(ROUTE)


def learn_support_pattern_types() -> dict[str, Any]:
    """Type-level aggregate learning (Route B view of the shared memory). Non-KPI."""
    return edge_memory.learn_pattern_types(ROUTE)


def check_invariants() -> list[str]:
    # the shared edge memory enforces episode-unit / no-actor / type-level for all routes
    return edge_memory.check_invariants()


def main() -> None:
    print("=" * 64)
    print("SUPPORT MEMORY (F-19) — shared edge memory, no gateway profiling")
    print("=" * 64)
    created = build()
    mem = list_memory()
    print(f"  support episodes (route=gateway_support): {len(mem)}  (0 is valid)")
    for m in mem:
        print(f"  · {m['memory_id']} episode={m['episode_ref']} kind={m['episode_kind']} outcome={m['outcome_type']}")
    print(f"  type-level learning: {learn_support_pattern_types()}")
    v = check_invariants()
    print(f"  shared memory invariant violations: {len(v)}")
    print("-" * 64)
    print("Episode-unit, append-only, shared. No gateway score/ranking/reputation/profile.")


if __name__ == "__main__":
    main()
