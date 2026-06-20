"""
discovery_learning_builder.py — Phase F-2: Discovery Reflection → Learning.

Aggregates discovery reflections into learnings. A learning is a tentative
observation, never a strategy.

Permitted learning types:
  - surface_reuse            (the same surface produced more than one discovery)
  - object_reuse             (the same object was discovered more than once)
  - cross_surface_discovery  (the same object was discovered via >1 surface)
Forbidden (never emitted): growth, marketing, acquisition, recruitment.

Strictly data-driven: no reflections → no learnings.

Input (read-only): data/discovery_reflections.jsonl
Output: data/discovery_learnings.jsonl

CLI:
  python -m bridge.agent_commons.runtime.discovery_learning_builder
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from .store import (
    DISCOVERY_LEARNINGS_JSONL, DISCOVERY_REFLECTIONS_JSONL, append_jsonl,
    base_invariants, next_id, read_jsonl,
)
from .discovery_reflector import DISCOVERY_INVARIANTS


def _existing_types() -> set[str]:
    return {l.get("learning_type") for l in read_jsonl(DISCOVERY_LEARNINGS_JSONL)}


def _emit(lt: str, statement: str, count: int) -> dict[str, Any]:
    return append_jsonl(DISCOVERY_LEARNINGS_JSONL, {
        "record_type": "discovery_learning",
        "learning_id": next_id("disc-learn", DISCOVERY_LEARNINGS_JSONL),
        "learning_type": lt,
        "statement": statement,
        "evidence_count": count,
        "candidate_only": True,
        **DISCOVERY_INVARIANTS,
        **base_invariants(),
    })


def build() -> list[dict[str, Any]]:
    """Aggregate reflections into learnings (idempotent by learning_type)."""
    refl = read_jsonl(DISCOVERY_REFLECTIONS_JSONL)
    existing = _existing_types()
    created = []
    if not refl:
        return created

    surface_counts = Counter(r.get("surface") for r in refl)
    object_counts = Counter(r.get("object") for r in refl)
    object_surfaces: dict[Any, set] = {}
    for r in refl:
        object_surfaces.setdefault(r.get("object"), set()).add(r.get("surface"))

    reused_surfaces = sum(1 for c in surface_counts.values() if c > 1)
    reused_objects = sum(1 for c in object_counts.values() if c > 1)
    cross = sum(1 for s in object_surfaces.values() if len(s) > 1)

    if reused_surfaces and "surface_reuse" not in existing:
        created.append(_emit("surface_reuse",
            "A surface produced more than one discovery. Observed reuse; no "
            "surface is ranked or recommended.", reused_surfaces))
    if reused_objects and "object_reuse" not in existing:
        created.append(_emit("object_reuse",
            "An object was discovered more than once. Observed reuse only.",
            reused_objects))
    if cross and "cross_surface_discovery" not in existing:
        created.append(_emit("cross_surface_discovery",
            "An object was discovered through more than one surface. Observed "
            "only; nothing planned.", cross))
    return created


def main() -> None:
    print("=" * 64)
    print("HERMES DISCOVERY LEARNING BUILDER — reflection → learning")
    print('  Allowed: surface_reuse / object_reuse / cross_surface_discovery.')
    print("=" * 64)
    created = build()
    if not created:
        print("  (no learnings — 0 reflections, or already built. Append-only.)")
    for l in created:
        print(f"  ✓ {l['learning_id']} [{l['learning_type']}] evidence={l['evidence_count']}")
    print("-" * 64)
    print("Learnings observe reuse. They never plan how to increase anything.")


if __name__ == "__main__":
    main()
