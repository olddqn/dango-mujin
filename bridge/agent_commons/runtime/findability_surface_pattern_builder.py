"""
findability_surface_pattern_builder.py — Phase F-1.5: Surface Learning → Pattern.

Generates tentative surface pattern candidates. A pattern is a hypothesis, not
a fact, not a strategy.

Permitted pattern keys:
  - passive_findability_surface
  - discoverability_dependency
  - public_surface_candidate
Forbidden pattern keys (never emitted; flagged by the reviewer if present):
  - best_surface, recommended_surface, growth_surface,
    acquisition_strategy, marketing_strategy, seo_strategy

Input (read-only): data/findability_surface_learnings.jsonl
Output: data/findability_surface_patterns.jsonl

CLI:
  python -m bridge.agent_commons.runtime.findability_surface_pattern_builder
"""

from __future__ import annotations

from typing import Any

from .store import (
    FINDABILITY_SURFACE_LEARNING_JSONL, FINDABILITY_SURFACE_PATTERN_JSONL,
    append_jsonl, base_invariants, next_id, read_jsonl,
)
from .findability_surface_reflector import FINDABILITY_SURFACE_INVARIANTS

ALLOWED_PATTERN_KEYS = ("passive_findability_surface", "discoverability_dependency",
                        "public_surface_candidate")
FORBIDDEN_PATTERN_KEYS = ("best_surface", "recommended_surface", "growth_surface",
                          "acquisition_strategy", "marketing_strategy", "seo_strategy")


def _existing_keys() -> set[str]:
    return {p.get("pattern_key") for p in read_jsonl(FINDABILITY_SURFACE_PATTERN_JSONL)}


def _emit(key: str, statement: str, count: int) -> dict[str, Any]:
    return append_jsonl(FINDABILITY_SURFACE_PATTERN_JSONL, {
        "record_type": "findability_surface_pattern",
        "pattern_id": next_id("surface-pat", FINDABILITY_SURFACE_PATTERN_JSONL),
        "pattern_key": key,
        "statement": statement,
        "evidence_count": count,
        "status": "tentative",
        "pattern_is_not_fact": True,
        "pattern_is_not_strategy": True,
        **FINDABILITY_SURFACE_INVARIANTS,
        **base_invariants(),
    })


def build() -> list[dict[str, Any]]:
    """Tentative pattern candidates from learnings (idempotent by pattern_key)."""
    learnings = {l["learning_type"]: l for l in read_jsonl(FINDABILITY_SURFACE_LEARNING_JSONL)}
    existing = _existing_keys()
    created = []

    if "passive_surface_candidate" in learnings and \
            "passive_findability_surface" not in existing:
        created.append(_emit("passive_findability_surface",
            "Mujin may be findable via existing public surfaces without Mujin "
            "contacting anyone. No surface named best or recommended. Tentative.",
            learnings["passive_surface_candidate"]["evidence_count"]))

    if "discoverability_candidate" in learnings and \
            "discoverability_dependency" not in existing:
        created.append(_emit("discoverability_dependency",
            "Discoverability depends on which surfaces are public; absent surfaces "
            "carry no discoverability. A dependency, not a plan. Tentative.",
            learnings["discoverability_candidate"]["evidence_count"]))

    if "surface_exists" in learnings and "public_surface_candidate" not in existing:
        created.append(_emit("public_surface_candidate",
            "One or more public surfaces exist through which actors could discover "
            "Mujin on their own. Possibility only. Tentative.",
            learnings["surface_exists"]["evidence_count"]))
    return created


def main() -> None:
    print("=" * 64)
    print("HERMES FINDABILITY SURFACE PATTERN BUILDER — learning → pattern")
    print('  Allowed: passive_findability_surface / discoverability_dependency / '
          'public_surface_candidate. No best/recommended/growth surface.')
    print("=" * 64)
    created = build()
    if not created:
        print("  (no new patterns — append-only, idempotent)")
    for p in created:
        print(f"  ✓ {p['pattern_id']} ({p['status']}) {p['pattern_key']} "
              f"evidence={p['evidence_count']}")
    print("-" * 64)
    print("Patterns are hypotheses about what exists, never a plan to grow it.")


if __name__ == "__main__":
    main()
