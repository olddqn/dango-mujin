"""
approval_builder.py — Approval layer (F-13).

Human Approval is GATEKEEPING only: it permits or blocks a Support Candidate
advancing to an "action candidate". It never ranks, never recommends, never
creates candidates, never selects among them (permitting several keeps them
plural). It is permissive, not constitutive: approval does not define a need,
represent the gateway, substitute gateway consent, open the person domain, or
start execution by itself.

Strictly data-driven: no candidate → no approval. Approval Count = 0 is valid.

CLI:
  python -m bridge.gateway_support.runtime.approval_builder
"""

from __future__ import annotations

from typing import Any

from ..store import (
    APPROVAL_RECORDS_JSONL, append_jsonl, base_invariants, carries_base_invariants,
    next_id, read_jsonl,
)
from .support_candidate_builder import list_candidates

DECISIONS = ("permit", "block")


def make_approval(candidate_id: str, decision: str, reviewer: str) -> dict[str, Any]:
    """Pure constructor. decision is gatekeeping: 'permit' or 'block' only."""
    if decision not in DECISIONS:
        raise ValueError(f"approval decision must be one of {DECISIONS} (gatekeeping only)")
    if not reviewer.strip():
        raise ValueError("named human reviewer required")
    return {
        "record_type": "approval",
        "approval_id": None,
        "candidate_id": candidate_id,
        "decision": decision,                  # permit | block — gatekeeping
        "reviewer": reviewer.strip(),
        "produces": "action_candidate" if decision == "permit" else "blocked",
        # F-13 markers
        "is_gatekeeping_not_constitutive": True,
        "is_permissive_not_generative": True,
        "does_not_rank": True,
        "does_not_recommend": True,
        "does_not_create_candidate": True,
        "does_not_select": True,
        "does_not_define_need": True,
        "does_not_substitute_gateway_consent": True,
        "does_not_open_person_domain": True,
        "does_not_start_execution": True,
        "requires_gateway_consent_for_action": True,
        "status": decision,
        **base_invariants(),
    }


def record_approval(candidate_id: str, decision: str, reviewer: str) -> dict[str, Any]:
    """Persist an approval. Refuses if candidate does not exist (no fabrication)."""
    if not any(c.get("candidate_id") == candidate_id for c in list_candidates()):
        raise ValueError(f"unknown candidate {candidate_id}: approval cannot create candidates")
    rec = make_approval(candidate_id, decision, reviewer)
    rec["approval_id"] = next_id("ap", APPROVAL_RECORDS_JSONL)
    return append_jsonl(APPROVAL_RECORDS_JSONL, rec)


def list_approvals() -> list[dict[str, Any]]:
    return read_jsonl(APPROVAL_RECORDS_JSONL)


def permitted_candidate_ids() -> set[str]:
    return {a["candidate_id"] for a in list_approvals() if a.get("decision") == "permit"}


def check_invariants() -> list[str]:
    violations: list[str] = []
    cand_ids = {c.get("candidate_id") for c in list_candidates()}
    for a in list_approvals():
        violations += carries_base_invariants(a)
        if a.get("decision") not in DECISIONS:
            violations.append(f"{a.get('approval_id')}: non-gatekeeping decision {a.get('decision')}")
        for f in ("is_gatekeeping_not_constitutive", "does_not_rank", "does_not_recommend",
                  "does_not_create_candidate", "does_not_select",
                  "does_not_substitute_gateway_consent", "does_not_start_execution"):
            if a.get(f) is not True:
                violations.append(f"{a.get('approval_id')}: missing/false {f}")
        if a.get("candidate_id") not in cand_ids:
            violations.append(f"{a.get('approval_id')}: approves a non-existent candidate (fabrication)")
    return violations


def main() -> None:
    print("=" * 64)
    print("APPROVAL BUILDER (F-13) — gatekeeping only (permit/block)")
    print("=" * 64)
    aps = list_approvals()
    print(f"  approvals: {len(aps)}  (0 is valid)")
    for a in aps:
        print(f"  · {a['approval_id']} candidate={a['candidate_id']} decision={a['decision']}")
    v = check_invariants()
    print(f"  invariant violations: {len(v)}")
    for x in v:
        print(f"    - {x}")
    print("-" * 64)
    print("Approval permits/blocks; it never ranks, recommends, selects, creates candidates, or executes.")


if __name__ == "__main__":
    main()
