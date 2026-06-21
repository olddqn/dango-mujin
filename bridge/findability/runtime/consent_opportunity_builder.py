"""
consent_opportunity_builder.py — Route A: Consent Opportunity (F-5/F-22).

From a findability surface (a door), records the consent opportunity it opens:
the door lets an owner FIND and CHOOSE to consent, preserving the discovery≠consent
gap. No pre-exposure (reaching the door collects no person data), owner→Mujin
direction, no coercion, no growth/count maximization. It enables consent; it never
compels it. 0 is valid. CLI:
  python -m bridge.findability.runtime.consent_opportunity_builder
"""

from __future__ import annotations

from typing import Any

from bridge.edge_runtime.runtime import edge_memory
from ..store import (CONSENT_OPPORTUNITIES_JSONL, SURFACES_JSONL, append_jsonl,
                     findability_base_invariants, missing_base_invariants, next_id,
                     read_jsonl, utc_now_iso)


def _surface(surface_id: str) -> dict[str, Any] | None:
    return next((s for s in read_jsonl(SURFACES_JSONL) if s.get("surface_id") == surface_id), None)


def make_opportunity(surface_id: str, edge_id: str) -> dict[str, Any]:
    return {
        "record_type": "consent_opportunity",
        "opportunity_id": None,
        "edge_id": edge_id,
        "surface_id": surface_id,
        "preserves_discovery_consent_gap": True,   # discovery != consent (F-5 §3)
        "enables_not_compels": True,
        "no_pre_exposure": True,
        "no_coercion": True,
        "no_nudge": True,
        "visitor_initiated_pull": True,
        "observed_at": utc_now_iso(),
        "status": "open",
        **findability_base_invariants(),
    }


def record_opportunity(surface_id: str) -> dict[str, Any]:
    s = _surface(surface_id)
    if s is None:
        raise ValueError(f"unknown surface {surface_id} (opportunity requires a door)")
    rec = make_opportunity(surface_id, s.get("edge_id"))
    rec["opportunity_id"] = next_id("co", CONSENT_OPPORTUNITIES_JSONL)
    stored = append_jsonl(CONSENT_OPPORTUNITIES_JSONL, rec)
    edge_memory.record_episode(rec["edge_id"], "findability", rec["opportunity_id"],
                               "consent_opportunity", "open")
    return stored


def list_opportunities() -> list[dict[str, Any]]:
    return read_jsonl(CONSENT_OPPORTUNITIES_JSONL)


def check_invariants() -> list[str]:
    out: list[str] = []
    for o in list_opportunities():
        out += [f"{o.get('opportunity_id')}: {m}" for m in
                missing_base_invariants(o, findability_base_invariants())]
        for f in ("preserves_discovery_consent_gap", "enables_not_compels",
                  "no_pre_exposure", "no_coercion", "visitor_initiated_pull"):
            if o.get(f) is not True:
                out.append(f"{o.get('opportunity_id')}: missing/false {f}")
    return out


def main() -> None:
    print("CONSENT OPPORTUNITY BUILDER (Route A, F-5/F-22)")
    o = list_opportunities()
    print(f"  opportunities: {len(o)} (0 valid) | invariant violations: {len(check_invariants())}")
    print("  Door enables consent without compelling it; gap preserved; no pre-exposure.")


if __name__ == "__main__":
    main()
