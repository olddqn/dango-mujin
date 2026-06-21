"""
cooperation_reflector.py — Phase H-5: Cooperation Reflection.

X-8 found the most plausible value hypothesis is cooperation among existing
helpers (Case D: cooperators can't find each other; Case E: gateways aren't
coordinated). Hermes records the POSSIBILITY that cooperation may exist —
nothing more.

Hermes does NOT:
  - say "connect Gateway A and Gateway B"
  - say "Agent X should participate"
  - say "JAR should cooperate"
  - generate / propose / execute / assign a cooperation
  - rank or recommend actors

It only records "cooperation may exist" as a candidate, from the multiplicity
of inference boundaries (multiple candidate need-dimensions for one voice ⇒ a
single actor may not cover all ⇒ multi-actor cooperation MAY be relevant). No
actor is ever named.

Input (read-only): memory/inference_boundary_records.jsonl (+ reflections,
patterns for context).
Output: memory/cooperation_reflections.jsonl

CLI:
  python -m bridge.agent_commons.runtime.cooperation_reflector
"""

from __future__ import annotations

from typing import Any

from .store import (
    COOP_REFLECTION_JSONL, INFERENCE_BOUNDARY_JSONL, append_jsonl,
    base_invariants, next_id, read_jsonl,
)

# the 8 invariants on every cooperation record (the record never crosses them)
COOPERATION_INVARIANTS = {
    "cannot_define_need": True,
    "cannot_select_gateway": True,
    "cannot_create_cooperation": True,
    "cannot_assign_participant": True,
    "cannot_contact_actor": True,
    "cannot_allocate_resources": True,
    "cooperation_is_not_decision": True,
    "human_review_required": True,
}


def _boundaries_by_voice() -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    for b in read_jsonl(INFERENCE_BOUNDARY_JSONL):
        out.setdefault(b.get("voice_id"), []).append(b)
    return out


def _already() -> set[str]:
    return {r.get("source_voice") for r in read_jsonl(COOP_REFLECTION_JSONL)}


def build() -> list[dict[str, Any]]:
    """One cooperation reflection per voice with >=2 candidate dimensions.

    Signal = multiple inference boundaries for one voice ⇒ no single actor
    obviously covers all dimensions ⇒ cooperation MAY be relevant. No actor
    is named; this is a possibility, not a fact, not a decision.
    """
    done = _already()
    created = []
    for voice_id, boundaries in _boundaries_by_voice().items():
        if not voice_id or voice_id in done:
            continue
        dims = sorted({b.get("candidate") for b in boundaries if b.get("candidate")})
        if len(dims) < 2:
            continue
        record = {
            "record_type": "cooperation_reflection",
            "reflection_id": next_id("coop-refl", COOP_REFLECTION_JSONL),
            "source_voice": voice_id,
            "source_boundaries": sorted(b.get("boundary_id") for b in boundaries),
            "reflection_type": "cooperation_observation",
            "candidate_dimension_count": len(dims),
            "summary": (f"{voice_id} shows {len(dims)} candidate need-dimensions; "
                        "a single actor may not cover all — cooperation among "
                        "multiple actors MAY be relevant. No actor is identified."),
            "cooperation_is_not_fact": True,
            "candidate_only": True,
            "names_no_actor": True,
            **COOPERATION_INVARIANTS,
            **base_invariants(),
        }
        created.append(append_jsonl(COOP_REFLECTION_JSONL, record))
        done.add(voice_id)
    return created


def main() -> None:
    print("=" * 64)
    print("HERMES COOPERATION REFLECTOR — records that cooperation MAY exist")
    print('  "Cooperation is not fact." No actor named. No cooperation created.')
    print("=" * 64)
    created = build()
    if not created:
        print("  (no voices with >=2 candidate dimensions — append-only, idempotent)")
    for r in created:
        print(f"  ✓ {r['reflection_id']} ← {r['source_voice']} "
              f"(dimensions={r['candidate_dimension_count']})")
        print(f"      {r['summary']}")
    print("-" * 64)
    print("Possibility only. No actor named, ranked, connected, or assigned.")


if __name__ == "__main__":
    main()
