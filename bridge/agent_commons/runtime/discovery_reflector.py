"""
discovery_reflector.py — Phase F-2: Discovery Reflection.

Discovery sits above Findability. Findability (F-1/F-1.5/F-1.7) records what
*can* be discovered; Discovery records what *was actually* discovered: who, what,
where.

Reality Correction is the top priority. No discovery event is invented. The
input is a read-only log of real, verified events; if it is empty (the current
true state), this layer produces nothing — recording the fact that no discovery
has happened, which is an observation, not a failure.

Hermes does NOT search, contact, recruit, rank or recommend a surface or an
actor, and does NOT generate a Voice / Need / Cooperation / Decision.

Input (read-only): data/discovery_events.jsonl
Output: data/discovery_reflections.jsonl  (only verified=true events adopted)

CLI:
  python -m bridge.agent_commons.runtime.discovery_reflector
"""

from __future__ import annotations

from typing import Any

from .store import (
    DISCOVERY_EVENTS_JSONL, DISCOVERY_REFLECTIONS_JSONL, append_jsonl,
    base_invariants, next_id, read_jsonl,
)

# Carried by every discovery record; boolean FLAGS (keys), kept distinct from
# the scanned string content.
DISCOVERY_INVARIANTS = {
    "cannot_contact_actor": True,
    "cannot_recruit_actor": True,
    "cannot_rank_surface": True,
    "cannot_rank_actor": True,
    "cannot_recommend_surface": True,
    "cannot_recommend_actor": True,
    "discovery_is_not_outreach": True,
    "discovery_is_not_marketing": True,
    "discovery_is_not_growth": True,
    "discovery_is_not_recruitment": True,
    "human_review_required": True,
}

# allowed discoverer types (forbidden ones are inferred/predicted/recommended/
# target — never adopted, because they would mean inventing an actor)
ALLOWED_DISCOVERER_TYPES = {"human", "agent", "organization"}
FORBIDDEN_DISCOVERER_TYPES = {"inferred_user", "predicted_actor",
                              "recommended_actor", "target_user"}


def _already() -> set[str]:
    return {r.get("source_event") for r in read_jsonl(DISCOVERY_REFLECTIONS_JSONL)}


def build() -> list[dict[str, Any]]:
    """One reflection per real, verified discovery event (idempotent).

    Adopts only verified=true events whose discoverer_type is allowed. Strictly
    data-driven: no events → no reflections.
    """
    done = _already()
    created = []
    for ev in read_jsonl(DISCOVERY_EVENTS_JSONL):
        eid = ev.get("event_id")
        if not eid or eid in done:
            continue
        if ev.get("verified") is not True:
            continue  # never adopt an unverified (possibly invented) event
        dtype = ev.get("discoverer_type")
        if dtype in FORBIDDEN_DISCOVERER_TYPES or dtype not in ALLOWED_DISCOVERER_TYPES:
            continue  # never record an inferred/predicted/recommended actor
        record = {
            "record_type": "discovery_reflection",
            "reflection_id": next_id("disc-refl", DISCOVERY_REFLECTIONS_JSONL),
            "source_event": eid,
            # who / what / where (descriptive only; no ranking, no judgement)
            "discoverer_type": dtype,
            "surface": ev.get("surface"),
            "object": ev.get("object"),
            "observed_at": ev.get("observed_at"),
            "verified": True,
            "questions": ["who_discovered", "what_object", "which_surface", "verified"],
            "summary": (f"a {dtype} discovered '{ev.get('object')}' via "
                        f"'{ev.get('surface')}'. Recorded as observed; nothing initiated."),
            "candidate_only": True,
            "observation_is_not_decision": True,
            **DISCOVERY_INVARIANTS,
            **base_invariants(),
        }
        created.append(append_jsonl(DISCOVERY_REFLECTIONS_JSONL, record))
        done.add(eid)
    return created


def main() -> None:
    print("=" * 64)
    print("HERMES DISCOVERY REFLECTOR — who discovered what, where (verified only)")
    print('  Discovery is what actually happened, not what could happen. None invented.')
    print("=" * 64)
    events = read_jsonl(DISCOVERY_EVENTS_JSONL)
    created = build()
    if not events:
        print("  discovery events = 0 — no discovery has happened.")
        print("  0 is an observation, not a failure. Nothing generated.")
    for r in created:
        print(f"  ✓ {r['reflection_id']} ← {r['source_event']} "
              f"[{r['discoverer_type']}] {r['surface']} → {r['object']}")
    print("-" * 64)
    print("Discovery records real events. It never invents a discoverer or a path.")


if __name__ == "__main__":
    main()
