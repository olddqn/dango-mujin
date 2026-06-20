"""
discovery_pattern_builder.py — Phase F-2: Discovery Learning → Pattern.

Generates tentative discovery pattern candidates. A pattern is a hypothesis,
not a fact, not a strategy.

Permitted pattern keys:
  - repeated_discovery_path       (a (surface, object) path recurred)
  - surface_object_relationship   (objects are discovered through surfaces)
Forbidden pattern keys (never emitted; flagged by the reviewer if present):
  - best_surface, recommended_surface, priority_surface,
    conversion_path, growth_funnel

Input (read-only): data/discovery_learnings.jsonl
Output: data/discovery_patterns.jsonl

CLI:
  python -m bridge.agent_commons.runtime.discovery_pattern_builder
"""

from __future__ import annotations

from typing import Any

from .store import (
    DISCOVERY_LEARNINGS_JSONL, DISCOVERY_PATTERNS_JSONL, append_jsonl,
    base_invariants, next_id, read_jsonl,
)
from .discovery_reflector import DISCOVERY_INVARIANTS

ALLOWED_PATTERN_KEYS = ("repeated_discovery_path", "surface_object_relationship")
FORBIDDEN_PATTERN_KEYS = ("best_surface", "recommended_surface", "priority_surface",
                          "conversion_path", "growth_funnel")


def _existing_keys() -> set[str]:
    return {p.get("pattern_key") for p in read_jsonl(DISCOVERY_PATTERNS_JSONL)}


def _emit(key: str, statement: str, count: int) -> dict[str, Any]:
    return append_jsonl(DISCOVERY_PATTERNS_JSONL, {
        "record_type": "discovery_pattern",
        "pattern_id": next_id("disc-pat", DISCOVERY_PATTERNS_JSONL),
        "pattern_key": key,
        "statement": statement,
        "evidence_count": count,
        "status": "tentative",
        "pattern_is_not_fact": True,
        "pattern_is_not_strategy": True,
        **DISCOVERY_INVARIANTS,
        **base_invariants(),
    })


def build() -> list[dict[str, Any]]:
    """Tentative pattern candidates from learnings (idempotent by pattern_key)."""
    learnings = {l["learning_type"]: l for l in read_jsonl(DISCOVERY_LEARNINGS_JSONL)}
    existing = _existing_keys()
    created = []

    if ("surface_reuse" in learnings or "cross_surface_discovery" in learnings) \
            and "repeated_discovery_path" not in existing:
        ev = (learnings.get("surface_reuse")
              or learnings.get("cross_surface_discovery"))["evidence_count"]
        created.append(_emit("repeated_discovery_path",
            "A (surface, object) discovery path recurred. Observed recurrence; "
            "no path is named best or recommended. Tentative.", ev))

    if learnings and "surface_object_relationship" not in existing:
        total = sum(l.get("evidence_count", 0) for l in learnings.values())
        created.append(_emit("surface_object_relationship",
            "Objects are discovered through surfaces; the relationship is observed, "
            "not engineered. Tentative.", total))
    return created


def main() -> None:
    print("=" * 64)
    print("HERMES DISCOVERY PATTERN BUILDER — learning → pattern (tentative)")
    print('  Allowed: repeated_discovery_path / surface_object_relationship.')
    print("=" * 64)
    created = build()
    if not created:
        print("  (no patterns — 0 learnings, or already built. Append-only.)")
    for p in created:
        print(f"  ✓ {p['pattern_id']} ({p['status']}) {p['pattern_key']} "
              f"evidence={p['evidence_count']}")
    print("-" * 64)
    print("Patterns describe observed paths, never a funnel or a recommended route.")


if __name__ == "__main__":
    main()
