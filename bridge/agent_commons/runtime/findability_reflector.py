"""
findability_reflector.py — Phase F-1: Findability Reflection.

Findability sits BEFORE Voice. It records the bare fact that an actor
*discovered* Mujin — nothing about who they are, what they need, or how to
reach them.

Findability is NOT Reachability. Mujin does not search for people, does not
contact them, does not recruit them, does not infer their Need. This layer
only records "the actor found Mujin" from a read-only Findability Event.

Hermes does NOT:
  - search for / contact / recruit an actor
  - rank or recommend a channel
  - generate a Voice / Need / Cooperation / Decision

Input (read-only): data/findability_events.jsonl (may not exist → 0 events,
which is an observation, not a failure).
Output: data/findability_reflections.jsonl

CLI:
  python -m bridge.agent_commons.runtime.findability_reflector
"""

from __future__ import annotations

from typing import Any

from .store import (
    FINDABILITY_EVENT_JSONL, FINDABILITY_REFLECTION_JSONL, append_jsonl,
    base_invariants, next_id, read_jsonl,
)

# Carried by every findability record; never weakened. These are boolean FLAGS
# (keys), deliberately distinct from the scanned string content, so that the
# layer can declare what it is NOT without tripping its own forbidden-term scan.
FINDABILITY_INVARIANTS = {
    "cannot_contact_actor": True,
    "cannot_recruit_actor": True,
    "cannot_rank_channel": True,
    "cannot_recommend_channel": True,
    "cannot_generate_voice": True,
    "cannot_generate_need": True,
    "cannot_generate_cooperation": True,
    "cannot_generate_decision": True,
    "findability_is_not_outreach": True,
    "findability_is_not_reachability": True,
    "findability_is_not_marketing": True,
    "human_review_required": True,
}


def _already() -> set[str]:
    return {r.get("source_event") for r in read_jsonl(FINDABILITY_REFLECTION_JSONL)}


def build() -> list[dict[str, Any]]:
    """One reflection per Findability Event (idempotent by source_event).

    Records four questions only: where from, what seen, was a Voice created,
    did nothing happen. It passively mirrors what the actor did; it never
    initiates anything. Strictly data-driven: no events → no reflections.
    """
    done = _already()
    created = []
    for ev in read_jsonl(FINDABILITY_EVENT_JSONL):
        eid = ev.get("event_id")
        if not eid or eid in done:
            continue
        voice_created = bool(ev.get("voice_created"))
        # passive_discovery is true iff Mujin neither contacted nor reached out
        passive = not (ev.get("contact_initiated_by_mujin") or ev.get("outreach_used"))
        record = {
            "record_type": "findability_reflection",
            "reflection_id": next_id("find-refl", FINDABILITY_REFLECTION_JSONL),
            "source_event": eid,
            "reflection_type": "findability_observation",
            # the four questions (descriptive, no judgement, no channel ranking)
            "discoverer_type": ev.get("discoverer_type"),
            "source_channel": ev.get("source_channel"),
            "source_reference": ev.get("source_reference"),
            "voice_created": voice_created,
            "nothing_occurred": not voice_created,
            "questions": ["where_from", "what_seen", "voice_created", "nothing_occurred"],
            # observed passivity flags (booleans; checked, never weakened)
            "passive_discovery": passive,
            "source_contact_initiated_by_mujin": bool(ev.get("contact_initiated_by_mujin")),
            "source_outreach_used": bool(ev.get("outreach_used")),
            "summary": (f"An actor discovered Mujin via {ev.get('source_channel')} "
                        f"({ev.get('source_reference')}); voice_created="
                        f"{voice_created}. The actor came; Mujin did not go."),
            "candidate_only": True,
            "observation_is_not_decision": True,
            **FINDABILITY_INVARIANTS,
            **base_invariants(),
        }
        created.append(append_jsonl(FINDABILITY_REFLECTION_JSONL, record))
        done.add(eid)
    return created


def main() -> None:
    print("=" * 64)
    print("HERMES FINDABILITY REFLECTOR — records that an actor found Mujin")
    print('  "The actor came; Mujin did not go." No search, no contact, no Voice.')
    print("=" * 64)
    n_events = len(read_jsonl(FINDABILITY_EVENT_JSONL))
    created = build()
    if n_events == 0:
        print("  findability events = 0 (no actor has discovered Mujin yet).")
        print("  0 is an observation, not a failure. Nothing generated.")
    for r in created:
        print(f"  ✓ {r['reflection_id']} ← {r['source_event']} "
              f"[{r['source_channel']}] voice_created={r['voice_created']}")
    print("-" * 64)
    print("Findability records discovery. It never reaches, contacts, or recruits.")


if __name__ == "__main__":
    main()
