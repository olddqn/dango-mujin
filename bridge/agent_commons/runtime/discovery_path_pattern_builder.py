"""
discovery_path_pattern_builder.py — Phase F-2.5: Path Learning → Pattern.

Generates tentative discovery path pattern candidates. A pattern is a
hypothesis, not a fact, not a strategy.

Permitted pattern keys:
  - repeated_discovery_path             (a path recurred)
  - surface_object_discovery_relationship (objects are discovered through surfaces
                                          in observed events)
Forbidden pattern keys (never emitted; flagged by the reviewer if present):
  - best_path, recommended_path, priority_path, conversion_funnel, growth_loop

Input (read-only): data/discovery_path_learnings.jsonl
Output: data/discovery_path_patterns.jsonl

CLI:
  python -m bridge.agent_commons.runtime.discovery_path_pattern_builder
"""

from __future__ import annotations

from typing import Any

from .store import (
    DISCOVERY_PATH_LEARNINGS_JSONL, DISCOVERY_PATH_PATTERNS_JSONL,
    append_jsonl, base_invariants, next_id, read_jsonl,
)
from .discovery_path_reflector import DISCOVERY_PATH_INVARIANTS

ALLOWED_PATTERN_KEYS = ("repeated_discovery_path", "surface_object_discovery_relationship")
FORBIDDEN_PATTERN_KEYS = ("best_path", "recommended_path", "priority_path",
                          "conversion_funnel", "growth_loop")


def _existing_keys() -> set[str]:
    return {p.get("pattern_key") for p in read_jsonl(DISCOVERY_PATH_PATTERNS_JSONL)}


def _emit(key: str, statement: str, count: int) -> dict[str, Any]:
    return append_jsonl(DISCOVERY_PATH_PATTERNS_JSONL, {
        "record_type": "discovery_path_pattern",
        "pattern_id": next_id("dpath-pat", DISCOVERY_PATH_PATTERNS_JSONL),
        "pattern_key": key,
        "statement": statement,
        "evidence_count": count,
        "status": "tentative",
        "pattern_is_not_fact": True,
        "pattern_is_not_strategy": True,
        **DISCOVERY_PATH_INVARIANTS,
        **base_invariants(),
    })


def build() -> list[dict[str, Any]]:
    """Tentative pattern candidates from learnings (idempotent by pattern_key)."""
    learnings = {l["learning_type"]: l for l in read_jsonl(DISCOVERY_PATH_LEARNINGS_JSONL)}
    existing = _existing_keys()
    created = []

    if "path_observed" in learnings and "repeated_discovery_path" not in existing:
        created.append(_emit("repeated_discovery_path",
            "A discovery path recurred across observed events. Observed recurrence; "
            "no path is named best or recommended. Tentative.",
            learnings["path_observed"]["evidence_count"]))

    if "surface_object_event_link" in learnings and \
            "surface_object_discovery_relationship" not in existing:
        created.append(_emit("surface_object_discovery_relationship",
            "Objects are discovered through surfaces in observed events; the "
            "relationship is observed, not engineered. Tentative.",
            learnings["surface_object_event_link"]["evidence_count"]))
    return created


def main() -> None:
    print("=" * 64)
    print("HERMES DISCOVERY PATH PATTERN BUILDER — learning → pattern (tentative)")
    print('  Allowed: repeated_discovery_path / surface_object_discovery_relationship.')
    print("=" * 64)
    created = build()
    if not created:
        print("  (no patterns — 0 learnings, or already built. Append-only.)")
    for p in created:
        print(f"  ✓ {p['pattern_id']} ({p['status']}) {p['pattern_key']} "
              f"evidence={p['evidence_count']}")
    print("-" * 64)
    print("Patterns describe observed paths, never a funnel or a growth loop.")


if __name__ == "__main__":
    main()
