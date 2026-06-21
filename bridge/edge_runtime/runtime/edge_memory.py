"""
edge_memory.py — Shared append-only episode memory (Route A and Route B).

A single memory layer for BOTH routes: one append-only record per route episode,
keyed by edge + route. It stores the episode KIND (a type) and observed outcome
type only — never an actor/gateway identity (links_no_actor), so no gateway
aggregation, evaluation, ranking, reputation, or profiling is possible. Learning
is type-level only (counts by route × kind × outcome) and is explicitly NOT a KPI
(no maximization, no relief-count target).

Used by Route B (gateway support episodes) and Route A (findability episodes) so
there is no duplicated memory layer.

CLI:
  python -m bridge.edge_runtime.runtime.edge_memory
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from ..store import (
    EDGE_MEMORY_JSONL, append_jsonl, edge_base_invariants, missing_base_invariants,
    next_id, read_jsonl,
)

ROUTES = ("findability", "gateway_support")


def _already() -> set[tuple[str, str]]:
    return {(m.get("route"), m.get("episode_ref")) for m in read_jsonl(EDGE_MEMORY_JSONL)}


def record_episode(edge_id: str, route: str, episode_ref: str,
                   episode_kind: str, outcome_type: str) -> dict[str, Any] | None:
    """Append one episode-unit memory (idempotent by route+episode_ref). NO actor
    identity is stored. Returns None if already recorded."""
    if route not in ROUTES:
        raise ValueError(f"route must be one of {ROUTES}")
    if (route, episode_ref) in _already():
        return None
    rec = {
        "record_type": "edge_episode",
        "memory_id": next_id("emem", EDGE_MEMORY_JSONL),
        "edge_id": edge_id,
        "route": route,
        "episode_ref": episode_ref,
        "episode_kind": episode_kind,        # a TYPE, never an actor
        "outcome_type": outcome_type,
        # F-19 (and Route A analogue) markers
        "is_episode_unit": True,
        "links_no_actor": True,
        "no_gateway_aggregation": True,
        "no_gateway_evaluation": True,
        "no_gateway_reputation": True,
        "no_gateway_profile": True,
        "learns_only_pattern_types": True,
        "status": "remembered",
        **edge_base_invariants(),
    }
    return append_jsonl(EDGE_MEMORY_JSONL, rec)


def list_memory(route: str | None = None) -> list[dict[str, Any]]:
    mem = read_jsonl(EDGE_MEMORY_JSONL)
    return [m for m in mem if route is None or m.get("route") == route]


def learn_pattern_types(route: str | None = None) -> dict[str, Any]:
    """Type-level aggregate learning ONLY (no actor). Counts by kind/outcome.
    Explicitly non-KPI: never a target, rate, ranking, or maximization objective."""
    mem = list_memory(route)
    return {
        "by_episode_kind": dict(Counter(m.get("episode_kind") for m in mem)),
        "by_outcome_type": dict(Counter(m.get("outcome_type") for m in mem)),
        "by_route": dict(Counter(m.get("route") for m in mem)),
        "episode_count": len(mem),
        "not_a_kpi": True,
        "no_maximization": True,
        "no_ranking": True,
        "not_person_relief_accounting": True,
    }


def check_invariants() -> list[str]:
    violations: list[str] = []
    for m in list_memory():
        violations += [f"{m.get('memory_id')}: {x}" for x in missing_base_invariants(m)]
        for f in ("is_episode_unit", "links_no_actor", "no_gateway_aggregation",
                  "no_gateway_evaluation", "no_gateway_reputation", "no_gateway_profile",
                  "learns_only_pattern_types"):
            if m.get(f) is not True:
                violations.append(f"{m.get('memory_id')}: missing/false {f}")
        for f in ("gateway_ref", "gateway_id", "gateway", "actor", "owner"):
            if f in m:
                violations.append(f"{m.get('memory_id')}: stores actor identity {f}")
        if m.get("route") not in ROUTES:
            violations.append(f"{m.get('memory_id')}: unknown route {m.get('route')}")
    return violations


def main() -> None:
    print("=" * 64)
    print("EDGE MEMORY (shared) — episode-unit, append-only, no actor profiling")
    print("=" * 64)
    mem = list_memory()
    print(f"  episodes: {len(mem)}  (0 is valid)")
    for m in mem:
        print(f"  · {m['memory_id']} route={m['route']} kind={m['episode_kind']} outcome={m['outcome_type']}")
    print(f"  type-level learning: {learn_pattern_types()}")
    v = check_invariants()
    print(f"  invariant violations: {len(v)}")
    for x in v:
        print(f"    - {x}")


if __name__ == "__main__":
    main()
