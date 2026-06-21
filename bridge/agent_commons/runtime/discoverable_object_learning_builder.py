"""
discoverable_object_learning_builder.py — Phase F-1.7: Object Reflection → Learning.

Aggregates object reflections into learnings. A learning is a tentative
observation, never a strategy.

Permitted learning types:
  - discoverable_object_exists   (at least one object is publicly discoverable)
  - discoverable_object_absent   (at least one object is not discoverable)
  - object_visibility_gap        (an object exists in the project but is not
                                  publicly discoverable)
Forbidden (never emitted): visibility_strategy, growth_strategy, outreach_strategy.

Input (read-only): data/discoverable_object_reflections.jsonl
Output: data/discoverable_object_learnings.jsonl

CLI:
  python -m bridge.agent_commons.runtime.discoverable_object_learning_builder
"""

from __future__ import annotations

from typing import Any

from .store import (
    DISCOVERABLE_OBJECT_LEARNING_JSONL, DISCOVERABLE_OBJECT_REFLECTION_JSONL,
    append_jsonl, base_invariants, next_id, read_jsonl,
)
from .discoverable_object_reflector import DISCOVERABLE_OBJECT_INVARIANTS

# object types that exist in the project but, when not discoverable, represent a
# visibility gap (the object is real locally yet not publicly reachable).
_PROJECT_OBJECTS = {"agent_commons", "mujin", "contribution_commons", "voice_commons"}


def _existing_types() -> set[str]:
    return {l.get("learning_type") for l in read_jsonl(DISCOVERABLE_OBJECT_LEARNING_JSONL)}


def _emit(lt: str, statement: str, count: int) -> dict[str, Any]:
    return append_jsonl(DISCOVERABLE_OBJECT_LEARNING_JSONL, {
        "record_type": "discoverable_object_learning",
        "learning_id": next_id("obj-learn", DISCOVERABLE_OBJECT_LEARNING_JSONL),
        "learning_type": lt,
        "statement": statement,
        "evidence_count": count,
        "candidate_only": True,
        **DISCOVERABLE_OBJECT_INVARIANTS,
        **base_invariants(),
    })


def build() -> list[dict[str, Any]]:
    """Aggregate reflections into learnings (idempotent by learning_type)."""
    refl = read_jsonl(DISCOVERABLE_OBJECT_REFLECTION_JSONL)
    existing = _existing_types()
    created = []

    present = [r for r in refl if r.get("discoverable")]
    absent = [r for r in refl if r.get("discoverable") is False]
    gaps = [r for r in refl if r.get("discoverable") is False
            and r.get("object_type") in _PROJECT_OBJECTS]

    if present and "discoverable_object_exists" not in existing:
        created.append(_emit("discoverable_object_exists",
            "At least one object is publicly discoverable through an existing "
            "surface. No object is ranked or recommended.", len(present)))
    if absent and "discoverable_object_absent" not in existing:
        created.append(_emit("discoverable_object_absent",
            "Some objects are not discoverable (observed, not assumed). Absence "
            "is an observation, not a failure.", len(absent)))
    if gaps and "object_visibility_gap" not in existing:
        created.append(_emit("object_visibility_gap",
            "Some objects exist in the project but are not publicly discoverable "
            "(e.g. the platform and its data live only on an unpushed branch or a "
            "local service). A gap, observed only.", len(gaps)))
    return created


def main() -> None:
    print("=" * 64)
    print("HERMES DISCOVERABLE OBJECT LEARNING BUILDER — reflection → learning")
    print('  Allowed: object_exists/absent, object_visibility_gap. No strategy.')
    print("=" * 64)
    created = build()
    if not created:
        print("  (no new learnings — append-only, idempotent)")
    for l in created:
        print(f"  ✓ {l['learning_id']} [{l['learning_type']}] evidence={l['evidence_count']}")
    print("-" * 64)
    print("Learnings observe what is visible. They never plan what to show.")


if __name__ == "__main__":
    main()
