"""
findability_surface_reflector.py — Phase F-1.5: Findability Surface Reflection.

Records WHERE Mujin is currently findable (its public "surfaces"). This is an
OBSERVATION of what exists, not an SEO audit, not a traffic/acquisition
analysis, not a marketing study, not a plan to increase anything.

Central question: "Where is Mujin discoverable right now?"

Reality Correction is the top priority: no surface is assumed. Each surface
below was actually verified on the observation date; the verification method is
recorded on every reflection. Surfaces that could not be confirmed are recorded
with exists=false — absence is an observation, not a failure.

Hermes does NOT search, contact, recruit, rank a surface, recommend a surface,
or generate a Voice / Need / Cooperation / Decision.

Output: data/findability_surface_reflections.jsonl

CLI:
  python -m bridge.agent_commons.runtime.findability_surface_reflector
"""

from __future__ import annotations

from typing import Any

from .store import (
    FINDABILITY_SURFACE_REFLECTION_JSONL, append_jsonl, base_invariants,
    next_id, read_jsonl,
)

# Carried by every surface record; boolean FLAGS (keys), kept distinct from the
# scanned string content so the layer can declare what it is NOT without
# tripping its own forbidden-term scan.
FINDABILITY_SURFACE_INVARIANTS = {
    "cannot_contact_actor": True,
    "cannot_recruit_actor": True,
    "cannot_rank_surface": True,
    "cannot_recommend_surface": True,
    "cannot_generate_voice": True,
    "cannot_generate_need": True,
    "cannot_generate_cooperation": True,
    "cannot_generate_decision": True,
    "findability_surface_is_not_outreach": True,
    "findability_surface_is_not_growth": True,
    "findability_surface_is_not_marketing": True,
    "human_review_required": True,
}

# Observation date of the verification snapshot below.
OBSERVED_AT = "2026-06-20"

# Verified surface snapshot. Each entry records the actual verification method.
# exists/publicly_accessible/externally_accessible/discoverable/
# requires_prior_knowledge/requires_outreach are point-in-time observations.
SURFACES: list[dict[str, Any]] = [
    {
        "surface_type": "github_repository",
        "exists": True, "publicly_accessible": True, "externally_accessible": True,
        "discoverable": True, "requires_prior_knowledge": False, "requires_outreach": False,
        "verified_by": "github api unauthenticated returned 200; visibility public "
                       "(olddqn/dango-mujin). Note: the Mujin platform branch is "
                       "unpushed, so public content is the Dan-Go/globe history.",
    },
    {
        "surface_type": "documentation",
        "exists": True, "publicly_accessible": True, "externally_accessible": True,
        "discoverable": True, "requires_prior_knowledge": False, "requires_outreach": False,
        "verified_by": "readme.md present on public main (200). docs/ directory "
                       "absent on main (404) — review docs live on an unpushed "
                       "local branch.",
    },
    {
        "surface_type": "localhost_services",
        "exists": True, "publicly_accessible": False, "externally_accessible": False,
        "discoverable": False, "requires_prior_knowledge": True, "requires_outreach": False,
        "verified_by": "mujin platform binds 127.0.0.1:8787 in code; local branch "
                       "only, not pushed. Reachable only by someone running it locally.",
    },
    {
        "surface_type": "nookplot",
        "exists": True, "publicly_accessible": False, "externally_accessible": False,
        "discoverable": False, "requires_prior_knowledge": True, "requires_outreach": False,
        "verified_by": "a gitlawb remote is configured to a localhost did node "
                       "(127.0.0.1:7545); the node was unreachable at observation "
                       "time, so it is not a public discovery surface.",
    },
    {
        "surface_type": "github_pages",
        "exists": False, "publicly_accessible": False, "externally_accessible": False,
        "discoverable": False, "requires_prior_knowledge": False, "requires_outreach": False,
        "verified_by": "no gh-pages branch; no CNAME or _config.yml; no Pages site files.",
    },
    {
        "surface_type": "public_website",
        "exists": False, "publicly_accessible": False, "externally_accessible": False,
        "discoverable": False, "requires_prior_knowledge": False, "requires_outreach": False,
        "verified_by": "no deploy/hosting config (vercel/netlify/procfile/dockerfile) found.",
    },
    {
        "surface_type": "telegram",
        "exists": False, "publicly_accessible": False, "externally_accessible": False,
        "discoverable": False, "requires_prior_knowledge": False, "requires_outreach": False,
        "verified_by": "no bot in code; the only mention is inside a review document. "
                       "Reality Correction: no telegram presence exists.",
    },
    {
        "surface_type": "discord",
        "exists": False, "publicly_accessible": False, "externally_accessible": False,
        "discoverable": False, "requires_prior_knowledge": False, "requires_outreach": False,
        "verified_by": "no discord reference found in the tree.",
    },
    {
        "surface_type": "sns",
        "exists": False, "publicly_accessible": False, "externally_accessible": False,
        "discoverable": False, "requires_prior_knowledge": False, "requires_outreach": False,
        "verified_by": "no social-network reference found in the tree.",
    },
    {
        "surface_type": "search_engine",
        "exists": False, "publicly_accessible": False, "externally_accessible": False,
        "discoverable": False, "requires_prior_knowledge": False, "requires_outreach": False,
        "verified_by": "indexing not confirmed; would depend on the public repo "
                       "being crawled. Cannot confirm, so recorded as absent.",
    },
    {
        "surface_type": "public_voice_records",
        "exists": False, "publicly_accessible": False, "externally_accessible": False,
        "discoverable": False, "requires_prior_knowledge": False, "requires_outreach": False,
        "verified_by": "voice_records.jsonl returns 404 on public main; present only "
                       "on an unpushed local branch. No public voice records exist.",
    },
    {
        "surface_type": "referral_surfaces",
        "exists": False, "publicly_accessible": False, "externally_accessible": False,
        "discoverable": False, "requires_prior_knowledge": False, "requires_outreach": False,
        "verified_by": "no inbound referral links to Mujin found.",
    },
]


def _already() -> set[str]:
    return {r.get("surface_type") for r in read_jsonl(FINDABILITY_SURFACE_REFLECTION_JSONL)}


def build() -> list[dict[str, Any]]:
    """One reflection per surface_type (idempotent). Records the five questions:
    does the surface exist, is it public, is it externally accessible, is it
    discoverable, does discovery need prior knowledge."""
    done = _already()
    created = []
    for s in SURFACES:
        st = s["surface_type"]
        if st in done:
            continue
        record = {
            "record_type": "findability_surface_reflection",
            "reflection_id": next_id("surface-refl", FINDABILITY_SURFACE_REFLECTION_JSONL),
            "surface_id": next_id("surface", FINDABILITY_SURFACE_REFLECTION_JSONL),
            "surface_type": st,
            # the five questions
            "exists": s["exists"],
            "publicly_accessible": s["publicly_accessible"],
            "externally_accessible": s["externally_accessible"],
            "discoverable": s["discoverable"],
            "requires_prior_knowledge": s["requires_prior_knowledge"],
            "requires_outreach": s["requires_outreach"],
            "questions": ["exists", "publicly_accessible", "externally_accessible",
                          "discoverable", "requires_prior_knowledge"],
            "verified_by": s["verified_by"],
            "observed_at": OBSERVED_AT,
            "summary": (f"surface '{st}': exists={s['exists']}, "
                        f"public={s['publicly_accessible']}, "
                        f"discoverable={s['discoverable']}. Observed, not engineered."),
            "candidate_only": True,
            "observation_is_not_decision": True,
            **FINDABILITY_SURFACE_INVARIANTS,
            **base_invariants(),
        }
        created.append(append_jsonl(FINDABILITY_SURFACE_REFLECTION_JSONL, record))
        done.add(st)
    return created


def main() -> None:
    print("=" * 64)
    print("HERMES FINDABILITY SURFACE REFLECTOR — where is Mujin findable now?")
    print('  Observation, not SEO/acquisition/marketing. No surface assumed.')
    print("=" * 64)
    created = build()
    if not created:
        print("  (surfaces already recorded — append-only, idempotent)")
    for r in created:
        print(f"  ✓ {r['reflection_id']} {r['surface_type']:<22} "
              f"exists={r['exists']!s:<5} public={r['publicly_accessible']!s:<5} "
              f"discoverable={r['discoverable']}")
    refl = read_jsonl(FINDABILITY_SURFACE_REFLECTION_JSONL)
    print("-" * 64)
    print(f"  surfaces examined={len(refl)} exists={sum(1 for r in refl if r['exists'])} "
          f"public={sum(1 for r in refl if r['publicly_accessible'])} "
          f"discoverable={sum(1 for r in refl if r['discoverable'])}")


if __name__ == "__main__":
    main()
