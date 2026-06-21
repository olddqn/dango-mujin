"""
discovery_path_reflector.py — Phase F-2.5: Discovery Path Reflection.

Joins the four lower layers — Findability (F-1), Surfaces (F-1.5), Objects
(F-1.7), Discovery Events (F-2) — to observe the relationship:

    Surface → Object → Discovery Event

i.e. when a discovery actually happened, from which (verified) surface was which
(verified) object found, by whom.

This is NOT a marketing funnel, growth, SEO, acquisition, or conversion
analysis. It records only the observed relationship. Reality Correction is the
top priority: no path is invented. A path is recorded only when a real discovery
event exists AND its surface and object match a verified surface/object record.
With no discovery events (the current true state), this layer produces nothing —
recording that no discovery path has been observed, an observation, not a failure.

Input (read-only):
  data/discovery_events.jsonl                 (F-2 — real events)
  data/findability_surface_reflections.jsonl  (F-1.5 — verified surfaces)
  data/discoverable_object_reflections.jsonl  (F-1.7 — verified objects)
Output: data/discovery_path_reflections.jsonl

CLI:
  python -m bridge.agent_commons.runtime.discovery_path_reflector
"""

from __future__ import annotations

from typing import Any

from .store import (
    DISCOVERABLE_OBJECT_REFLECTION_JSONL, DISCOVERY_EVENTS_JSONL,
    DISCOVERY_PATH_REFLECTIONS_JSONL, FINDABILITY_SURFACE_REFLECTION_JSONL,
    append_jsonl, base_invariants, next_id, read_jsonl,
)
from .discovery_reflector import ALLOWED_DISCOVERER_TYPES, FORBIDDEN_DISCOVERER_TYPES

# Carried by every path record; boolean FLAGS (keys), kept distinct from scanned
# string content.
DISCOVERY_PATH_INVARIANTS = {
    "cannot_contact_actor": True,
    "cannot_recruit_actor": True,
    "cannot_rank_path": True,
    "cannot_recommend_path": True,
    "cannot_generate_voice": True,
    "cannot_generate_need": True,
    "cannot_generate_gateway": True,
    "cannot_generate_cooperation": True,
    "cannot_generate_decision": True,
    "path_is_not_outreach": True,
    "path_is_not_marketing": True,
    "path_is_not_growth": True,
    "path_is_not_funnel": True,
    "human_review_required": True,
}


def _surface_index() -> dict[str, dict[str, Any]]:
    """surface_type -> verified F-1.5 surface reflection (exists=true only)."""
    return {r.get("surface_type"): r
            for r in read_jsonl(FINDABILITY_SURFACE_REFLECTION_JSONL) if r.get("exists")}


def _object_index() -> dict[str, dict[str, Any]]:
    """object_type -> a verified F-1.7 object reflection (any)."""
    out: dict[str, dict[str, Any]] = {}
    for r in read_jsonl(DISCOVERABLE_OBJECT_REFLECTION_JSONL):
        out.setdefault(r.get("object_type"), r)
    return out


def _already() -> set[str]:
    return {r.get("event_id") for r in read_jsonl(DISCOVERY_PATH_REFLECTIONS_JSONL)}


def build() -> list[dict[str, Any]]:
    """One path per real discovery event whose surface/object are verified.

    Strictly data-driven: no events → no paths. A path is recorded only when the
    event is verified, its discoverer_type is allowed, and both its surface and
    object match a verified record (a true Surface→Object→Event chain).
    """
    surfaces = _surface_index()
    objects = _object_index()
    done = _already()
    created = []
    for ev in read_jsonl(DISCOVERY_EVENTS_JSONL):
        eid = ev.get("event_id")
        if not eid or eid in done:
            continue
        if ev.get("verified") is not True:
            continue
        dtype = ev.get("discoverer_type")
        if dtype in FORBIDDEN_DISCOVERER_TYPES or dtype not in ALLOWED_DISCOVERER_TYPES:
            continue
        s = surfaces.get(ev.get("surface"))
        o = objects.get(ev.get("object"))
        surface_match = s is not None
        object_match = o is not None
        # only record a path where the chain is actually verified end-to-end
        if not (surface_match and object_match):
            continue
        record = {
            "record_type": "discovery_path_reflection",
            "path_id": next_id("dpath", DISCOVERY_PATH_REFLECTIONS_JSONL),
            "event_id": eid,
            "surface_id": s.get("surface_id"),
            "object_id": o.get("object_id"),
            "surface_type": ev.get("surface"),
            "object_type": ev.get("object"),
            "discoverer_type": dtype,
            # the five questions
            "event_exists": True,
            "surface_match": surface_match,
            "object_match": object_match,
            "path_observed": True,
            "not_caused_by_outreach": True,
            "questions": ["event_exists", "surface_match", "object_match",
                          "relationship_observed", "not_caused_by_outreach"],
            "summary": (f"observed path: surface '{ev.get('surface')}' → object "
                        f"'{ev.get('object')}' → event '{eid}' (a {dtype}). "
                        "Observed relationship, not engineered."),
            "candidate_only": True,
            "observation_is_not_decision": True,
            **DISCOVERY_PATH_INVARIANTS,
            **base_invariants(),
        }
        created.append(append_jsonl(DISCOVERY_PATH_REFLECTIONS_JSONL, record))
        done.add(eid)
    return created


def main() -> None:
    print("=" * 64)
    print("HERMES DISCOVERY PATH REFLECTOR — surface → object → event (observed)")
    print('  Not a funnel/growth/SEO. No path invented; verified chains only.')
    print("=" * 64)
    events = read_jsonl(DISCOVERY_EVENTS_JSONL)
    created = build()
    if not events:
        print("  discovery events = 0 — no discovery path has been observed.")
        print("  0 is an observation, not a failure. Nothing generated.")
    for r in created:
        print(f"  ✓ {r['path_id']} ← {r['event_id']} "
              f"{r['surface_type']} → {r['object_type']} [{r['discoverer_type']}]")
    print("-" * 64)
    print("Discovery paths are observed relationships, never proposed routes.")


if __name__ == "__main__":
    main()
