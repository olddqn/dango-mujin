"""
findability_surface_builder.py — Route A: Findability Surface (F-1.5/F-1.7/F-21).

From an Observed Edge, records (observation only) a public surface through which
the gateway/Mujin is currently findable — verified as publicly observable, with
no outreach. No ranking, no growth, no marketing. Each surface references a
shared edge and writes a shared edge-memory episode.

0 surfaces is valid (do not fabricate). CLI:
  python -m bridge.findability.runtime.findability_surface_builder
"""

from __future__ import annotations

from typing import Any

from bridge.edge_runtime.runtime.edge_builder import edge_exists
from bridge.edge_runtime.runtime import edge_memory
from ..store import (SURFACES_JSONL, append_jsonl, findability_base_invariants,
                     missing_base_invariants, next_id, read_jsonl, utc_now_iso)


def make_surface(edge_id: str, surface_type: str, public_source_url: str,
                 verified_by: str, publicly_observable: bool) -> dict[str, Any]:
    if not publicly_observable:
        raise ValueError("a findability surface must be publicly observable (F-1.5); else held")
    if not public_source_url.strip():
        raise ValueError("public_source_url required (publicly observable)")
    if not verified_by.strip():
        raise ValueError("named human verifier required")
    return {
        "record_type": "findability_surface",
        "surface_id": None,
        "edge_id": edge_id,
        "surface_type": surface_type,
        "public_source_url": public_source_url.strip(),
        "publicly_observable": True,
        "verified_by": verified_by.strip(),
        "observed_at": utc_now_iso(),
        "is_observation_only": True,
        "requires_no_outreach": True,
        "status": "observed",
        **findability_base_invariants(),
    }


def record_surface(**kwargs: Any) -> dict[str, Any]:
    if not edge_exists(kwargs.get("edge_id")):
        raise ValueError(f"unknown edge {kwargs.get('edge_id')} (surface requires an observed edge)")
    rec = make_surface(**kwargs)
    rec["surface_id"] = next_id("fs", SURFACES_JSONL)
    stored = append_jsonl(SURFACES_JSONL, rec)
    edge_memory.record_episode(rec["edge_id"], "findability", rec["surface_id"],
                               f"surface:{rec['surface_type']}", "observed")
    return stored


def list_surfaces() -> list[dict[str, Any]]:
    return read_jsonl(SURFACES_JSONL)


def check_invariants() -> list[str]:
    out: list[str] = []
    for s in list_surfaces():
        out += [f"{s.get('surface_id')}: {m}" for m in
                missing_base_invariants(s, findability_base_invariants())]
        for f in ("is_observation_only", "requires_no_outreach", "publicly_observable"):
            if s.get(f) is not True:
                out.append(f"{s.get('surface_id')}: missing/false {f}")
    return out


def main() -> None:
    print("FINDABILITY SURFACE BUILDER (Route A, F-1.5/F-1.7/F-21)")
    s = list_surfaces()
    print(f"  surfaces: {len(s)} (0 valid)  | invariant violations: {len(check_invariants())}")
    print("  Observation only; owner→Mujin; no outreach/growth/marketing/ranking.")


if __name__ == "__main__":
    main()
