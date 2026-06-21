"""
cooperation_pattern_builder.py — Phase H-5: Cooperation Reflection → Learning → Pattern.

Aggregates cooperation reflections into learnings, then tentative pattern
candidates. A Pattern is a hypothesis, not a fact, not a policy. No actor is
named, ranked, recommended, or prioritised. Forbidden: best/optimal/
recommended/priority gateway.

Input (read-only): memory/cooperation_reflections.jsonl
Output: memory/cooperation_learning.jsonl, memory/cooperation_patterns.jsonl

CLI:
  python -m bridge.agent_commons.runtime.cooperation_pattern_builder
"""

from __future__ import annotations

from typing import Any

from .store import (
    COOP_LEARNING_JSONL, COOP_PATTERN_JSONL, COOP_REFLECTION_JSONL,
    append_jsonl, base_invariants, next_id, read_jsonl,
)
from .cooperation_reflector import COOPERATION_INVARIANTS


def _existing_learning_types() -> set[str]:
    return {l.get("learning_type") for l in read_jsonl(COOP_LEARNING_JSONL)}


def build_learnings() -> list[dict[str, Any]]:
    """Aggregate cooperation reflections into learnings (idempotent by type)."""
    reflections = read_jsonl(COOP_REFLECTION_JSONL)
    created = []
    existing = _existing_learning_types()
    multi = [r for r in reflections
             if r.get("reflection_type") == "cooperation_observation"]
    if multi and "multi_actor_dependency" not in existing:
        created.append(append_jsonl(COOP_LEARNING_JSONL, {
            "record_type": "cooperation_learning",
            "learning_id": next_id("coop-learn", COOP_LEARNING_JSONL),
            "learning_type": "multi_actor_dependency",
            "statement": "Some voices span multiple candidate need-dimensions; "
                         "cooperation among multiple actors may be relevant. "
                         "No actor is identified.",
            "evidence_count": len(multi),
            "candidate_only": True,
            "cooperation_is_not_fact": True,
            **COOPERATION_INVARIANTS,
            **base_invariants(),
        }))
    return created


def _existing_pattern_keys() -> set[str]:
    return {p.get("pattern_key") for p in read_jsonl(COOP_PATTERN_JSONL)}


def build_patterns() -> list[dict[str, Any]]:
    """Generate tentative cooperation pattern candidates from learnings."""
    learnings = {l["learning_type"]: l for l in read_jsonl(COOP_LEARNING_JSONL)}
    existing = _existing_pattern_keys()
    created = []
    if "multi_actor_dependency" in learnings and "multi_actor_cooperation" not in existing:
        ev = learnings["multi_actor_dependency"]["evidence_count"]
        created.append(append_jsonl(COOP_PATTERN_JSONL, {
            "record_type": "cooperation_pattern",
            "pattern_id": next_id("coop-pat", COOP_PATTERN_JSONL),
            "pattern_key": "multi_actor_cooperation",
            # NOT gateway-specific: data shows multi-dimension, not multi-gateway.
            "pattern_type": "multi_actor_cooperation_candidate",
            "statement": "A voice may require cooperation among multiple actors "
                         "(no actors named, none ranked). Tentative hypothesis.",
            "evidence_count": ev,
            "status": "tentative",
            "pattern_is_not_fact": True,
            "pattern_is_not_policy": True,
            **COOPERATION_INVARIANTS,
            **base_invariants(),
        }))
    return created


def main() -> None:
    print("=" * 64)
    print("HERMES COOPERATION PATTERN BUILDER — reflection → learning → pattern")
    print('  "Pattern is not fact." "Pattern is not policy." No actor named/ranked.')
    print("=" * 64)
    learnings = build_learnings()
    patterns = build_patterns()
    for l in learnings:
        print(f"  ✓ {l['learning_id']} [{l['learning_type']}] evidence={l['evidence_count']}")
    for p in patterns:
        print(f"  ✓ {p['pattern_id']} ({p['status']}) {p['pattern_type']} evidence={p['evidence_count']}")
    if not learnings and not patterns:
        print("  (no new learnings/patterns — append-only, idempotent)")
    print("-" * 64)
    print("Hypothesis only. No best/recommended/priority/optimal gateway.")


if __name__ == "__main__":
    main()
