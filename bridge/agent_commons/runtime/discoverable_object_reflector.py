"""
discoverable_object_reflector.py — Phase F-1.7: Discoverable Object Reflection.

Observes the Surface → Object mapping: given the surfaces that actually exist
(from F-1.5), WHAT can an external actor really discover through each one.

Central question: "What is actually discoverable?"

This is NOT branding, marketing, SEO, or growth analysis. It records only what
is visible. Reality Correction is the top priority: nothing is assumed
discoverable — each mapping below was verified against the public surface, and
the verification method is recorded on every reflection. Objects that are not
publicly reachable are recorded discoverable=false (a visibility gap), which is
an observation, not a failure.

Reads F-1.5 surface reflections READ-ONLY to link each object to its surface_id
and to honour each surface's verified exists/public state.

Output: data/discoverable_object_reflections.jsonl

CLI:
  python -m bridge.agent_commons.runtime.discoverable_object_reflector
"""

from __future__ import annotations

from typing import Any

from .store import (
    DISCOVERABLE_OBJECT_REFLECTION_JSONL, FINDABILITY_SURFACE_REFLECTION_JSONL,
    append_jsonl, base_invariants, next_id, read_jsonl,
)

# Carried by every object record; boolean FLAGS (keys), kept distinct from the
# scanned string content.
DISCOVERABLE_OBJECT_INVARIANTS = {
    "cannot_contact_actor": True,
    "cannot_recruit_actor": True,
    "cannot_rank_object": True,
    "cannot_recommend_object": True,
    "cannot_generate_voice": True,
    "cannot_generate_need": True,
    "cannot_generate_gateway": True,
    "cannot_generate_cooperation": True,
    "cannot_generate_decision": True,
    "discoverable_object_is_not_marketing": True,
    "discoverable_object_is_not_growth": True,
    "discoverable_object_is_not_outreach": True,
    "human_review_required": True,
}

# allowed / conditional object types (forbidden: inferred_* — never recorded)
ALLOWED_OBJECT_TYPES = {
    "dan_go", "globe", "agent_commons", "documentation", "repository", "source_code",
    "mujin", "contribution_commons", "voice_commons",
}
FORBIDDEN_OBJECT_TYPES = {
    "inferred_user", "inferred_need", "inferred_gateway", "inferred_actor",
}

OBSERVED_AT = "2026-06-20"

# Verified Surface → Object mapping. tuple = (object_type, discoverable, public,
# requires_prior_knowledge, verified_by). Only surfaces with exists=true (per
# F-1.5) contribute objects; the existence is re-checked at build time.
OBJECT_MAP: dict[str, list[tuple[str, bool, bool, bool, str]]] = {
    "github_repository": [
        ("dan_go", True, True, False,
         "globe/, bridge/gitsea, bridge/sutable and top-level specs present on public main (200)."),
        ("globe", True, True, False,
         "globe/ present on public main (200)."),
        ("repository", True, True, False,
         "repo root listing is public (bridge/, runtime/, examples/, manifesto/)."),
        ("source_code", True, True, False,
         "runtime/ and bridge/ source present on public main (200)."),
        ("documentation", True, True, False,
         "README, CONSTITUTION, MUJIN_PROTOCOL, CONTRIBUTION_SPEC, ROADMAP public on main (200)."),
        ("agent_commons", False, False, False,
         "bridge/agent_commons returns 404 on public main; present only on an unpushed branch."),
        ("mujin", False, False, False,
         "bridge/mujin platform returns 404 on main. Only MUJIN_PROTOCOL.md (a document) is "
         "public; the platform itself is not discoverable."),
        ("contribution_commons", False, False, False,
         "part of bridge/mujin (404 on main); not publicly discoverable."),
        ("voice_commons", False, False, False,
         "part of bridge/mujin (404 on main); no public voices — the correct, reassuring state."),
    ],
    "documentation": [
        ("documentation", True, True, False,
         "README and spec .md files (CONSTITUTION, MUJIN_PROTOCOL, CONTRIBUTION_SPEC, ROADMAP) "
         "public on main (200)."),
    ],
    "localhost_services": [
        ("mujin", False, False, True,
         "the mujin platform serves only at 127.0.0.1:8787; not externally discoverable."),
        ("contribution_commons", False, False, True,
         "served only by the local service; not externally discoverable."),
        ("voice_commons", False, False, True,
         "served only by the local service; not externally discoverable."),
    ],
    "nookplot": [
        ("repository", False, False, True,
         "the gitlawb node at 127.0.0.1:7545 was unreachable; nothing externally discoverable."),
    ],
}


def _surface_index() -> dict[str, dict[str, Any]]:
    """surface_type -> its F-1.5 reflection (read-only)."""
    return {r.get("surface_type"): r
            for r in read_jsonl(FINDABILITY_SURFACE_REFLECTION_JSONL)}


def _already() -> set[tuple[str, str]]:
    return {(r.get("surface_type"), r.get("object_type"))
            for r in read_jsonl(DISCOVERABLE_OBJECT_REFLECTION_JSONL)}


def build() -> list[dict[str, Any]]:
    """One reflection per (existing surface, object) mapping (idempotent)."""
    surfaces = _surface_index()
    done = _already()
    created = []
    for surface_type, objects in OBJECT_MAP.items():
        srec = surfaces.get(surface_type)
        # only map objects for surfaces that F-1.5 verified as existing
        if not srec or not srec.get("exists"):
            continue
        surface_id = srec.get("surface_id")
        for object_type, disc, public, prior, verified in objects:
            if object_type not in ALLOWED_OBJECT_TYPES or object_type in FORBIDDEN_OBJECT_TYPES:
                continue  # never record an inferred_* or unknown object
            if (surface_type, object_type) in done:
                continue
            record = {
                "record_type": "discoverable_object_reflection",
                "reflection_id": next_id("obj-refl", DISCOVERABLE_OBJECT_REFLECTION_JSONL),
                "object_id": next_id("obj", DISCOVERABLE_OBJECT_REFLECTION_JSONL),
                "surface_id": surface_id,
                "surface_type": surface_type,
                "object_type": object_type,
                # the four questions
                "discoverable": disc,
                "public": public,
                "requires_prior_knowledge": prior,
                "questions": ["visible_from_surface", "public", "discoverable",
                              "requires_prior_knowledge"],
                "verified_by": verified,
                "observed_at": OBSERVED_AT,
                "summary": (f"via '{surface_type}': object '{object_type}' "
                            f"discoverable={disc}, public={public}. Observed, not shaped."),
                "candidate_only": True,
                "observation_is_not_decision": True,
                **DISCOVERABLE_OBJECT_INVARIANTS,
                **base_invariants(),
            }
            created.append(append_jsonl(DISCOVERABLE_OBJECT_REFLECTION_JSONL, record))
            done.add((surface_type, object_type))
    return created


def main() -> None:
    print("=" * 64)
    print("HERMES DISCOVERABLE OBJECT REFLECTOR — what is actually discoverable?")
    print('  Surface → Object mapping. Observation, not branding/marketing/SEO.')
    print("=" * 64)
    if not read_jsonl(FINDABILITY_SURFACE_REFLECTION_JSONL):
        print("  ! F-1.5 surfaces not found — run findability_surface_reflector first.")
    created = build()
    if not created:
        print("  (objects already recorded — append-only, idempotent)")
    for r in created:
        print(f"  ✓ {r['reflection_id']} {r['surface_type']:<20}→ {r['object_type']:<20} "
              f"disc={r['discoverable']!s:<5} public={r['public']}")
    refl = read_jsonl(DISCOVERABLE_OBJECT_REFLECTION_JSONL)
    print("-" * 64)
    print(f"  object_count={len(refl)} "
          f"discoverable={sum(1 for r in refl if r['discoverable'])} "
          f"public={sum(1 for r in refl if r['public'])}")


if __name__ == "__main__":
    main()
