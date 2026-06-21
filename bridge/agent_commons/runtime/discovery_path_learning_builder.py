"""
discovery_path_learning_builder.py — Phase F-2.5: Path Reflection → Learning.

Aggregates discovery path reflections into learnings. A learning is a tentative
observation, never a strategy.

Permitted learning types:
  - path_observed             (at least one Surface→Object→Event path was observed)
  - path_absent               (no discovery path has been observed yet)
  - surface_object_event_link (a surface→object→event link was observed)
Forbidden (never emitted): funnel, conversion, acquisition, growth_path, marketing_path.

Strictly data-driven: no reflections → no learnings.

Input (read-only): data/discovery_path_reflections.jsonl
Output: data/discovery_path_learnings.jsonl

CLI:
  python -m bridge.agent_commons.runtime.discovery_path_learning_builder
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from .store import (
    DISCOVERY_PATH_LEARNINGS_JSONL, DISCOVERY_PATH_REFLECTIONS_JSONL,
    append_jsonl, base_invariants, next_id, read_jsonl,
)
from .discovery_path_reflector import DISCOVERY_PATH_INVARIANTS


def _existing_types() -> set[str]:
    return {l.get("learning_type") for l in read_jsonl(DISCOVERY_PATH_LEARNINGS_JSONL)}


def _emit(lt: str, statement: str, count: int) -> dict[str, Any]:
    return append_jsonl(DISCOVERY_PATH_LEARNINGS_JSONL, {
        "record_type": "discovery_path_learning",
        "learning_id": next_id("dpath-learn", DISCOVERY_PATH_LEARNINGS_JSONL),
        "learning_type": lt,
        "statement": statement,
        "evidence_count": count,
        "candidate_only": True,
        **DISCOVERY_PATH_INVARIANTS,
        **base_invariants(),
    })


def build() -> list[dict[str, Any]]:
    """Aggregate path reflections into learnings (idempotent by learning_type).

    Note: path_absent is data-driven on the upstream events read here read-only;
    it is emitted only when an explicit observation of absence is warranted (no
    path reflections AND the layer was actually run), and is recorded once."""
    refl = read_jsonl(DISCOVERY_PATH_REFLECTIONS_JSONL)
    existing = _existing_types()
    created = []
    if not refl:
        # no paths: do not fabricate learnings. Absence is surfaced by the report
        # (path_absent there). Keeping the builder empty-in → empty-out honours
        # "no path generated from nothing".
        return created

    if "path_observed" not in existing:
        created.append(_emit("path_observed",
            "At least one Surface→Object→Event path was observed. No path is "
            "ranked or recommended.", len(refl)))

    links = Counter((r.get("surface_type"), r.get("object_type")) for r in refl)
    if "surface_object_event_link" not in existing:
        created.append(_emit("surface_object_event_link",
            "A surface→object→event link was observed. Observed relationship only.",
            len(links)))
    return created


def main() -> None:
    print("=" * 64)
    print("HERMES DISCOVERY PATH LEARNING BUILDER — reflection → learning")
    print('  Allowed: path_observed / path_absent / surface_object_event_link.')
    print("=" * 64)
    created = build()
    if not created:
        print("  (no learnings — 0 path reflections, or already built. Append-only.)")
    for l in created:
        print(f"  ✓ {l['learning_id']} [{l['learning_type']}] evidence={l['evidence_count']}")
    print("-" * 64)
    print("Learnings observe links. They never plan a funnel or conversion.")


if __name__ == "__main__":
    main()
