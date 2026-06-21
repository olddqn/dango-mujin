"""
inference_boundary_builder.py — Phase H-4: Hermes Inference Boundary Memory.

X-2.6 / X-3 / X-3.5 found that the Need problem is not "Need is missing" but
"where does inference begin". For voice-006: A (funding) and B (volunteer) are
direct observations; C/D/E (translation/legal/employment) are inference or
speculation.

Hermes does NOT define a Need, approve it, or reject it. Hermes is an
Inference Boundary Observer: it records the point where inference began —
"from here on, this is a guess." The inference itself was made by a human in
the X-3 / X-3.5 review; Hermes reads that review (read-only) and records the
boundary. Hermes invents no inference of its own.

Input (read-only): docs/NEED_DEFINITION_REVIEW.md (canonical candidate data,
authored by the human review) + memory records for cross-reference.
Output: memory/inference_boundary_records.jsonl

CLI:
  python -m bridge.agent_commons.runtime.inference_boundary_builder
"""

from __future__ import annotations

import json
import re
from typing import Any

from .store import (
    INFERENCE_BOUNDARY_JSONL, NEED_DEFINITION_REVIEW_MD, append_jsonl,
    base_invariants, next_id, read_jsonl,
)

# review_type → boundary_type
_BOUNDARY_TYPE = {
    "direct_observation": "direct_observation",
    "inferred": "inference",
    "speculative": "speculation",
}

# candidate_id → (slug, last_direct_observation, first_inference)
# These encode WHERE the human's inference began (from the X-3/X-3.5 human
# comments). For direct observations there is no inference (first_inference=None).
_CANDIDATE_BOUNDARY = {
    "A": ("funding",
          "JAR public appeal: explicit donation solicitation (stated)",
          None),
    "B": ("volunteer",
          "JAR public appeal: explicit volunteer solicitation (stated)",
          None),
    "C": ("translation",
          "JAR activity description: language support",
          "refugees may need translation"),
    "D": ("legal",
          "JAR activity description: legal support",
          "refugees may need legal support"),
    "E": ("employment",
          "JAR activity description: employment support",
          "refugees may need employment support, and this may be the current bottleneck"),
}

_NEED_FIELDS = ("need_type", "need_id", "suggested_need_type", "need_approved")


def parse_review_candidates() -> list[dict[str, Any]]:
    """Read the human review doc (read-only) and parse its candidate JSON blocks."""
    if not NEED_DEFINITION_REVIEW_MD.exists():
        return []
    text = NEED_DEFINITION_REVIEW_MD.read_text(encoding="utf-8")
    blocks = re.findall(r"```json\s*(\{.*?\})\s*```", text, re.S)
    out = []
    for b in blocks:
        try:
            d = json.loads(b)
        except json.JSONDecodeError:
            continue
        if "candidate_id" in d and "review_type" in d:
            out.append(d)
    return out


def _existing_keys() -> set[tuple[str, str]]:
    return {(r.get("voice_id"), r.get("candidate"))
            for r in read_jsonl(INFERENCE_BOUNDARY_JSONL)}


def build(voice_id: str = "voice-006") -> list[dict[str, Any]]:
    """Build inference boundary records from the human review (idempotent)."""
    done = _existing_keys()
    created = []
    for c in parse_review_candidates():
        cid = c.get("candidate_id")
        slug, last_obs, first_inf = _CANDIDATE_BOUNDARY.get(
            cid, (cid, c.get("label", ""), None))
        if (voice_id, slug) in done:
            continue
        review_type = c.get("review_type")
        boundary_type = _BOUNDARY_TYPE.get(review_type, "inference")
        requires_review = boundary_type in ("inference", "speculation")
        record = {
            "record_type": "inference_boundary",
            "boundary_id": next_id("ib", INFERENCE_BOUNDARY_JSONL),
            "voice_id": voice_id,
            "candidate": slug,
            "candidate_id": cid,
            "review_type": review_type,
            "boundary_type": boundary_type,
            "last_direct_observation": last_obs,
            "first_inference": first_inf,            # None for direct observations
            "need_owner_present": c.get("need_owner_present"),
            "gateway_need": c.get("gateway_need"),
            "individual_need": c.get("individual_need"),
            "distance_from_voice": c.get("distance_from_voice"),
            "scouter_risk": c.get("scouter_risk"),
            "boundary_requires_human_review": requires_review,
            # safety refusals (Hermes records a boundary; it never crosses it)
            "cannot_define_need": True,
            "cannot_approve_need": True,
            "cannot_reject_need": True,
            "cannot_select_gateway": True,
            "cannot_generate_task": True,
            "cannot_allocate_resources": True,
            "source": "human review (NEED_DEFINITION_REVIEW.md); Hermes records "
                      "the boundary, it does not infer",
            **base_invariants(),
        }
        created.append(append_jsonl(INFERENCE_BOUNDARY_JSONL, record))
        done.add((voice_id, slug))
    return created


def check_invariants() -> list[str]:
    violations: list[str] = []
    required = ("cannot_define_need", "cannot_approve_need", "cannot_reject_need",
                "cannot_select_gateway", "cannot_generate_task",
                "cannot_allocate_resources")
    for r in read_jsonl(INFERENCE_BOUNDARY_JSONL):
        for f in _NEED_FIELDS:
            if f in r:
                violations.append(f"{r.get('boundary_id')}: defines need ({f})")
        for f in required:
            if r.get(f) is not True:
                violations.append(f"{r.get('boundary_id')}: missing/false {f}")
        if r.get("authority") != "none":
            violations.append(f"{r.get('boundary_id')}: authority not none")
    return violations


def main() -> None:
    print("=" * 64)
    print("HERMES INFERENCE BOUNDARY BUILDER — records where inference begins")
    print('  "From here on, this is a guess." Hermes records; it does not infer.')
    print("=" * 64)
    created = build()
    if not created:
        print("  (no new candidates — append-only, idempotent; "
              "or NEED_DEFINITION_REVIEW.md not found)")
    for r in created:
        fi = r["first_inference"] or "— (no inference; direct observation)"
        print(f"  ✓ {r['boundary_id']} {r['candidate']} [{r['boundary_type']}] "
              f"risk={r['scouter_risk']} review={r['boundary_requires_human_review']}")
        print(f"      last direct obs: {r['last_direct_observation']}")
        print(f"      first inference: {fi}")
    print("-" * 64)
    print(f"  violations={len(check_invariants())}. No Need defined/approved/rejected.")


if __name__ == "__main__":
    main()
