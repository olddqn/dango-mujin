"""
findability_surface_learning_builder.py — Phase F-1.5: Surface Reflection → Learning.

Aggregates surface reflections into learnings. A learning is a tentative
observation, never a strategy.

Permitted learning types:
  - surface_exists              (at least one surface exists)
  - surface_absent              (at least one surface was confirmed absent)
  - passive_surface_candidate   (a surface is findable without Mujin reaching anyone)
  - discoverability_candidate   (a surface is discoverable)
Forbidden (never emitted): growth_opportunity, acquisition_channel, marketing_channel.

Strictly data-driven: each learning is derived from actual reflections (the
absent ones are real observations, not fabricated).

Input (read-only): data/findability_surface_reflections.jsonl
Output: data/findability_surface_learnings.jsonl

CLI:
  python -m bridge.agent_commons.runtime.findability_surface_learning_builder
"""

from __future__ import annotations

from typing import Any

from .store import (
    FINDABILITY_SURFACE_LEARNING_JSONL, FINDABILITY_SURFACE_REFLECTION_JSONL,
    append_jsonl, base_invariants, next_id, read_jsonl,
)
from .findability_surface_reflector import FINDABILITY_SURFACE_INVARIANTS


def _existing_types() -> set[str]:
    return {l.get("learning_type") for l in read_jsonl(FINDABILITY_SURFACE_LEARNING_JSONL)}


def _emit(lt: str, statement: str, count: int) -> dict[str, Any]:
    return append_jsonl(FINDABILITY_SURFACE_LEARNING_JSONL, {
        "record_type": "findability_surface_learning",
        "learning_id": next_id("surface-learn", FINDABILITY_SURFACE_LEARNING_JSONL),
        "learning_type": lt,
        "statement": statement,
        "evidence_count": count,
        "candidate_only": True,
        **FINDABILITY_SURFACE_INVARIANTS,
        **base_invariants(),
    })


def build() -> list[dict[str, Any]]:
    """Aggregate reflections into learnings (idempotent by learning_type)."""
    refl = read_jsonl(FINDABILITY_SURFACE_REFLECTION_JSONL)
    existing = _existing_types()
    created = []

    present = [r for r in refl if r.get("exists")]
    absent = [r for r in refl if r.get("exists") is False]
    passive = [r for r in refl if r.get("exists") and r.get("discoverable")
               and not r.get("requires_outreach")]
    discoverable = [r for r in refl if r.get("discoverable")]

    if present and "surface_exists" not in existing:
        created.append(_emit("surface_exists",
            "At least one public surface exists. No surface is ranked or recommended.",
            len(present)))
    if absent and "surface_absent" not in existing:
        created.append(_emit("surface_absent",
            "Some surfaces were confirmed absent (observed, not assumed). Absence "
            "is an observation, not a failure.", len(absent)))
    if passive and "passive_surface_candidate" not in existing:
        created.append(_emit("passive_surface_candidate",
            "A surface may make Mujin findable without Mujin contacting anyone. "
            "Tentative.", len(passive)))
    if discoverable and "discoverability_candidate" not in existing:
        created.append(_emit("discoverability_candidate",
            "A surface is discoverable. Possibility only; nothing planned.",
            len(discoverable)))
    return created


def main() -> None:
    print("=" * 64)
    print("HERMES FINDABILITY SURFACE LEARNING BUILDER — reflection → learning")
    print('  Allowed: surface_exists/absent, passive_surface, discoverability.')
    print("=" * 64)
    created = build()
    if not created:
        print("  (no new learnings — append-only, idempotent)")
    for l in created:
        print(f"  ✓ {l['learning_id']} [{l['learning_type']}] evidence={l['evidence_count']}")
    print("-" * 64)
    print("Learnings observe what exists. They never plan how to increase anything.")


if __name__ == "__main__":
    main()
