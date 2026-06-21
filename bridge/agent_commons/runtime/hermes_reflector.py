"""
hermes_reflector.py — Phase H-2.5: Observation → Reflection.

Hermes does not decide what should be done. It records what was learned.
A Reflection is an insight derived from an Observation. It is not a decision
and not a policy. Hermes is an Observer — not a Planner, Coordinator, or
Policy Maker.

The value of Hermes turned out to be not the Task Candidates but the learning
from Observations (e.g. voice-006 → obs-006 → "gateway voice"). That learning
is not stored in observation/task records; this layer stores it.

Forbidden: Need gen/approve/reject · Gateway/Agent selection · Task gen ·
Cooperation forming · Policy generation.

CLI:
  python -m bridge.agent_commons.runtime.hermes_reflector
"""

from __future__ import annotations

from typing import Any

from .store import (
    OBSERVATION_JSONL, REFLECTION_JSONL, append_jsonl, base_invariants,
    next_id, read_jsonl,
)


def generate_reflection(obs: dict[str, Any]) -> dict[str, Any]:
    """Derive a low-confidence insight from one observation. No decision."""
    vid = obs.get("source_voice_id")
    vtype = obs.get("voice_type")
    owner = obs.get("need_owner_present")
    bottlenecks = obs.get("observed_bottleneck", [])

    if vtype in ("gateway_voice", "intermediary_voice"):
        text = (f"Public voice {vid} originated from a gateway/intermediary "
                f"rather than a direct beneficiary; the need owner may be absent "
                f"from the voice.")
    elif vtype == "public_call":
        text = (f"Public-call voice {vid} has no clearly present first-person "
                f"need owner; the need owner may be absent.")
    else:  # direct_voice
        text = (f"Voice {vid} appears to be a direct first-person appeal; "
                f"consent and safety must be confirmed by a human.")
    if bottlenecks:
        text += f" Observed bottlenecks: {', '.join(bottlenecks)}."

    # category tags used later to aggregate learnings (not a need definition)
    categories = [vtype]
    if owner is False:
        categories.append("need_owner_absent")

    return {
        "reflection": text,
        "voice_type": vtype,
        "need_owner_present": owner,
        "categories": categories,
        "confidence": "low",
    }


def _already_reflected() -> set[str]:
    return {r.get("source_observation") for r in read_jsonl(REFLECTION_JSONL)}


def build() -> list[dict[str, Any]]:
    """Build Reflections for observations not yet reflected (idempotent)."""
    done = _already_reflected()
    created = []
    for obs in read_jsonl(OBSERVATION_JSONL):
        oid = obs.get("observation_id")
        if not oid or oid in done:
            continue
        r = generate_reflection(obs)
        record = {
            "record_type": "reflection",
            "reflection_id": next_id("refl", REFLECTION_JSONL),
            "source_voice": obs.get("source_voice_id"),
            "source_observation": oid,
            **r,
            "human_reviewed": False,        # honest: AI-generated, not yet reviewed
            "reflection_requires_human_review": True,
            "reflection_is_not_decision": True,
            "reflection_is_not_policy": True,
            "defines_need": False,
            "selects_gateway": False,
            **base_invariants(),
        }
        created.append(append_jsonl(REFLECTION_JSONL, record))
        done.add(oid)
    return created


def main() -> None:
    print("=" * 64)
    print("HERMES REFLECTOR — observation → reflection (what was learned)")
    print('  "Reflection is not decision." "Reflection is not policy."')
    print("=" * 64)
    created = build()
    if not created:
        print("  (no new observations to reflect on — append-only, idempotent)")
    for r in created:
        print(f"  ✓ {r['reflection_id']} ← {r['source_observation']} "
              f"({r['source_voice']}) · confidence={r['confidence']}")
        print(f"      {r['reflection']}")
    print("-" * 64)
    print("Hermes records what was learned, not what to do. Humans decide.")


if __name__ == "__main__":
    main()
