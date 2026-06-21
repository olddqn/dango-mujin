"""
support_candidate_builder.py — Support Candidate layer (F-12).

From a Verified Bottleneck, derive Support Candidates: one per support form the
gateway ITSELF publicly stated accepting (verified_bottleneck.accepted_support_forms).
Candidates are possibility-only · multiple · advisory · UNORDERED · carry refusal
flags · contain no recommendation and no ranking. They never select, decide, or
plan execution.

Strictly data-driven (F-12): no verified bottleneck → no candidate. Candidates
are derived ONLY from the gateway's self-stated accepted forms — never invented
(do not fabricate candidates). Support Candidate Count = 0 is valid.

CLI:
  python -m bridge.gateway_support.runtime.support_candidate_builder
"""

from __future__ import annotations

from typing import Any

from ..store import (
    SUPPORT_CANDIDATES_JSONL, append_jsonl, base_invariants, carries_base_invariants,
    next_id, read_jsonl,
)
from .verified_bottleneck_builder import list_verified_bottlenecks


def make_candidate(bottleneck_id: str, support_form: str) -> dict[str, Any]:
    """Pure constructor for one possibility-only candidate (no rank field)."""
    return {
        "record_type": "support_candidate",
        "candidate_id": None,
        "bottleneck_id": bottleneck_id,
        "support_form": support_form,            # one of gateway's self-stated forms
        # F-12 markers — note: NO rank / order / recommendation field exists
        "possibility_only": True,
        "is_advisory": True,
        "is_unordered": True,
        "is_not_recommendation": True,
        "is_not_decision": True,
        "is_not_execution_plan": True,
        "is_not_selection": True,
        "requires_human_review": True,
        "requires_gateway_consent_for_action": True,
        "requires_approval_for_action": True,
        "status": "possibility",
        **base_invariants(),
    }


def _existing_pairs() -> set[tuple[str, str]]:
    return {(c.get("bottleneck_id"), c.get("support_form"))
            for c in read_jsonl(SUPPORT_CANDIDATES_JSONL)}


def derive_candidates_for(bottleneck: dict[str, Any]) -> list[dict[str, Any]]:
    """Pure: one candidate per gateway self-stated accepted form. Plural, unordered."""
    forms = bottleneck.get("accepted_support_forms") or []
    return [make_candidate(bottleneck["bottleneck_id"], f) for f in forms]


def build() -> list[dict[str, Any]]:
    """Persist candidates for each verified bottleneck (idempotent). 0 in → 0 out."""
    done = _existing_pairs()
    created = []
    for b in list_verified_bottlenecks():
        if b.get("status") != "verified":
            continue
        for cand in derive_candidates_for(b):
            key = (cand["bottleneck_id"], cand["support_form"])
            if key in done:
                continue
            cand["candidate_id"] = next_id("sc", SUPPORT_CANDIDATES_JSONL)
            created.append(append_jsonl(SUPPORT_CANDIDATES_JSONL, cand))
            done.add(key)
    return created


def list_candidates() -> list[dict[str, Any]]:
    return read_jsonl(SUPPORT_CANDIDATES_JSONL)


def check_invariants() -> list[str]:
    violations: list[str] = []
    for c in list_candidates():
        violations += carries_base_invariants(c)
        for f in ("possibility_only", "is_advisory", "is_unordered",
                  "is_not_recommendation", "is_not_decision", "is_not_selection",
                  "requires_human_review", "requires_gateway_consent_for_action",
                  "requires_approval_for_action"):
            if c.get(f) is not True:
                violations.append(f"{c.get('candidate_id')}: missing/false {f}")
        # structural: no ordering / preference field may exist
        for f in ("order", "rank", "preference", "recommended", "selected"):
            if f in c:
                violations.append(f"{c.get('candidate_id')}: has ordering/selection field {f}")
    return violations


def main() -> None:
    print("=" * 64)
    print("SUPPORT CANDIDATE BUILDER (F-12) — possibility only, plural, unordered")
    print("=" * 64)
    created = build()
    cands = list_candidates()
    print(f"  support candidates: {len(cands)}  (0 is valid — do not fabricate)")
    for c in cands:
        print(f"  · {c['candidate_id']} ← {c['bottleneck_id']} form={c['support_form']} [possibility]")
    v = check_invariants()
    print(f"  invariant violations: {len(v)}")
    for x in v:
        print(f"    - {x}")
    print("-" * 64)
    print("Candidates are possibilities, never recommendations or rankings. Human review + gateway consent gate any action.")


if __name__ == "__main__":
    main()
