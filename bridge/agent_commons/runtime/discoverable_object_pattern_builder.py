"""
discoverable_object_pattern_builder.py — Phase F-1.7: Object Learning → Pattern.

Generates tentative object pattern candidates. A pattern is a hypothesis, not a
fact, not a strategy.

Permitted pattern keys:
  - surface_object_mapping       (objects are tied to the surfaces that expose them)
  - discoverability_dependency   (an object's discoverability depends on its surface)
Forbidden pattern keys (never emitted; flagged by the reviewer if present):
  - best_object, recommended_object, acquisition_target, recruitment_target

Input (read-only): data/discoverable_object_learnings.jsonl
Output: data/discoverable_object_patterns.jsonl

CLI:
  python -m bridge.agent_commons.runtime.discoverable_object_pattern_builder
"""

from __future__ import annotations

from typing import Any

from .store import (
    DISCOVERABLE_OBJECT_LEARNING_JSONL, DISCOVERABLE_OBJECT_PATTERN_JSONL,
    append_jsonl, base_invariants, next_id, read_jsonl,
)
from .discoverable_object_reflector import DISCOVERABLE_OBJECT_INVARIANTS

ALLOWED_PATTERN_KEYS = ("surface_object_mapping", "discoverability_dependency")
FORBIDDEN_PATTERN_KEYS = ("best_object", "recommended_object",
                          "acquisition_target", "recruitment_target")


def _existing_keys() -> set[str]:
    return {p.get("pattern_key") for p in read_jsonl(DISCOVERABLE_OBJECT_PATTERN_JSONL)}


def _emit(key: str, statement: str, count: int) -> dict[str, Any]:
    return append_jsonl(DISCOVERABLE_OBJECT_PATTERN_JSONL, {
        "record_type": "discoverable_object_pattern",
        "pattern_id": next_id("obj-pat", DISCOVERABLE_OBJECT_PATTERN_JSONL),
        "pattern_key": key,
        "statement": statement,
        "evidence_count": count,
        "status": "tentative",
        "pattern_is_not_fact": True,
        "pattern_is_not_strategy": True,
        **DISCOVERABLE_OBJECT_INVARIANTS,
        **base_invariants(),
    })


def build() -> list[dict[str, Any]]:
    """Tentative pattern candidates from learnings (idempotent by pattern_key)."""
    learnings = {l["learning_type"]: l for l in read_jsonl(DISCOVERABLE_OBJECT_LEARNING_JSONL)}
    existing = _existing_keys()
    created = []

    # any learning implies a surface→object mapping was observed
    if learnings and "surface_object_mapping" not in existing:
        total = sum(l.get("evidence_count", 0) for l in learnings.values())
        created.append(_emit("surface_object_mapping",
            "What is discoverable is determined by which surfaces exist; each "
            "object is visible only through its surface. Observed mapping. Tentative.",
            total))

    if ("discoverable_object_absent" in learnings or "object_visibility_gap" in learnings) \
            and "discoverability_dependency" not in existing:
        ev = (learnings.get("object_visibility_gap")
              or learnings.get("discoverable_object_absent"))["evidence_count"]
        created.append(_emit("discoverability_dependency",
            "An object's discoverability depends on its surface being public; "
            "objects on absent or local surfaces are not discoverable. Tentative.",
            ev))
    return created


def main() -> None:
    print("=" * 64)
    print("HERMES DISCOVERABLE OBJECT PATTERN BUILDER — learning → pattern")
    print('  Allowed: surface_object_mapping / discoverability_dependency.')
    print("=" * 64)
    created = build()
    if not created:
        print("  (no new patterns — append-only, idempotent)")
    for p in created:
        print(f"  ✓ {p['pattern_id']} ({p['status']}) {p['pattern_key']} "
              f"evidence={p['evidence_count']}")
    print("-" * 64)
    print("Patterns describe the mapping, never a target to acquire or recruit.")


if __name__ == "__main__":
    main()
