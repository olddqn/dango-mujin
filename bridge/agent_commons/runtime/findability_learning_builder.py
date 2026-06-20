"""
findability_learning_builder.py — Phase F-1: Findability Reflection → Learning.

Aggregates findability reflections into learnings. A learning is a tentative
observation, not a strategy. Permitted learning types:
  - discoverability_exists        (at least one actor discovered Mujin)
  - passive_discovery_candidate   (discovery occurred without any outreach)
Forbidden: any growth / acquisition / outreach framing.

discoverability_absent (zero discovery) is NOT synthesised here: with no input
there is nothing to aggregate, so the builder emits nothing. The observed
absence is surfaced by findability_report.py (count = 0). This keeps the layer
strictly data-driven and avoids generating records from no input.

Input (read-only): data/findability_reflections.jsonl
Output: data/findability_learnings.jsonl

CLI:
  python -m bridge.agent_commons.runtime.findability_learning_builder
"""

from __future__ import annotations

from typing import Any

from .store import (
    FINDABILITY_LEARNING_JSONL, FINDABILITY_REFLECTION_JSONL, append_jsonl,
    base_invariants, next_id, read_jsonl,
)
from .findability_reflector import FINDABILITY_INVARIANTS


def _existing_types() -> set[str]:
    return {l.get("learning_type") for l in read_jsonl(FINDABILITY_LEARNING_JSONL)}


def build() -> list[dict[str, Any]]:
    """Aggregate reflections into learnings (idempotent by learning_type)."""
    reflections = read_jsonl(FINDABILITY_REFLECTION_JSONL)
    existing = _existing_types()
    created = []

    if reflections and "discoverability_exists" not in existing:
        created.append(append_jsonl(FINDABILITY_LEARNING_JSONL, {
            "record_type": "findability_learning",
            "learning_id": next_id("find-learn", FINDABILITY_LEARNING_JSONL),
            "learning_type": "discoverability_exists",
            "statement": "At least one actor discovered Mujin. Discovery is "
                         "possible. No channel is ranked or recommended.",
            "evidence_count": len(reflections),
            "candidate_only": True,
            **FINDABILITY_INVARIANTS,
            **base_invariants(),
        }))

    passive = [r for r in reflections if r.get("passive_discovery")]
    if passive and "passive_discovery_candidate" not in existing:
        created.append(append_jsonl(FINDABILITY_LEARNING_JSONL, {
            "record_type": "findability_learning",
            "learning_id": next_id("find-learn", FINDABILITY_LEARNING_JSONL),
            "learning_type": "passive_discovery_candidate",
            "statement": "Discovery occurred without Mujin contacting or reaching "
                         "anyone. Passive discovery may be possible. Tentative.",
            "evidence_count": len(passive),
            "candidate_only": True,
            **FINDABILITY_INVARIANTS,
            **base_invariants(),
        }))
    return created


def main() -> None:
    print("=" * 64)
    print("HERMES FINDABILITY LEARNING BUILDER — reflection → learning")
    print('  "Discoverability is observed, not engineered." No growth framing.')
    print("=" * 64)
    created = build()
    if not created:
        print("  (no learnings — 0 reflections, or already built. Append-only.)")
    for l in created:
        print(f"  ✓ {l['learning_id']} [{l['learning_type']}] evidence={l['evidence_count']}")
    print("-" * 64)
    print("Learnings observe discoverability. They never plan acquisition.")


if __name__ == "__main__":
    main()
