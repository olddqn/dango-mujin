"""
findability_pattern_builder.py — Phase F-1: Findability Learning → Pattern.

Generates tentative findability pattern candidates from learnings. A pattern is
a hypothesis, not a fact, not a strategy.

Permitted pattern keys:
  - passive_findability_candidate
  - organic_discovery_candidate
Forbidden pattern keys (must never be emitted):
  - best_channel, recommended_channel, acquisition_strategy,
    outreach_strategy, growth_strategy

The forbidden keys are enforced both here (we never write them) and in the
Hermes reviewer (it flags them if they ever appear).

Input (read-only): data/findability_learnings.jsonl
Output: data/findability_patterns.jsonl

CLI:
  python -m bridge.agent_commons.runtime.findability_pattern_builder
"""

from __future__ import annotations

from typing import Any

from .store import (
    FINDABILITY_LEARNING_JSONL, FINDABILITY_PATTERN_JSONL, append_jsonl,
    base_invariants, next_id, read_jsonl,
)
from .findability_reflector import FINDABILITY_INVARIANTS

# pattern keys this builder is allowed to emit (nothing else is ever written)
ALLOWED_PATTERN_KEYS = ("passive_findability_candidate", "organic_discovery_candidate")
FORBIDDEN_PATTERN_KEYS = ("best_channel", "recommended_channel",
                          "acquisition_strategy", "outreach_strategy",
                          "growth_strategy")


def _existing_keys() -> set[str]:
    return {p.get("pattern_key") for p in read_jsonl(FINDABILITY_PATTERN_JSONL)}


def build() -> list[dict[str, Any]]:
    """Tentative pattern candidates from learnings (idempotent by pattern_key)."""
    learnings = {l["learning_type"]: l for l in read_jsonl(FINDABILITY_LEARNING_JSONL)}
    existing = _existing_keys()
    created = []

    if "passive_discovery_candidate" in learnings and \
            "passive_findability_candidate" not in existing:
        ev = learnings["passive_discovery_candidate"]["evidence_count"]
        created.append(append_jsonl(FINDABILITY_PATTERN_JSONL, {
            "record_type": "findability_pattern",
            "pattern_id": next_id("find-pat", FINDABILITY_PATTERN_JSONL),
            "pattern_key": "passive_findability_candidate",
            "statement": "Mujin may be findable without Mujin reaching anyone. "
                         "No channel is named best or recommended. Tentative.",
            "evidence_count": ev,
            "status": "tentative",
            "pattern_is_not_fact": True,
            "pattern_is_not_strategy": True,
            **FINDABILITY_INVARIANTS,
            **base_invariants(),
        }))

    if "discoverability_exists" in learnings and \
            "organic_discovery_candidate" not in existing:
        ev = learnings["discoverability_exists"]["evidence_count"]
        created.append(append_jsonl(FINDABILITY_PATTERN_JSONL, {
            "record_type": "findability_pattern",
            "pattern_id": next_id("find-pat", FINDABILITY_PATTERN_JSONL),
            "pattern_key": "organic_discovery_candidate",
            "statement": "Actors may discover Mujin on their own. A possibility, "
                         "not a plan. No channel ranked. Tentative.",
            "evidence_count": ev,
            "status": "tentative",
            "pattern_is_not_fact": True,
            "pattern_is_not_strategy": True,
            **FINDABILITY_INVARIANTS,
            **base_invariants(),
        }))
    return created


def main() -> None:
    print("=" * 64)
    print("HERMES FINDABILITY PATTERN BUILDER — learning → pattern (tentative)")
    print('  Allowed: passive_findability / organic_discovery. No best/'
          'recommended channel, no acquisition/outreach/growth strategy.')
    print("=" * 64)
    created = build()
    if not created:
        print("  (no patterns — 0 learnings, or already built. Append-only.)")
    for p in created:
        print(f"  ✓ {p['pattern_id']} ({p['status']}) {p['pattern_key']} "
              f"evidence={p['evidence_count']}")
    print("-" * 64)
    print("Patterns are hypotheses about discoverability, never a growth plan.")


if __name__ == "__main__":
    main()
