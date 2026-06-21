"""
edge_builder.py — Observed Edge records (shared by Route A and Route B).

An Observed Edge is the single entry point both routes build on: it records that
a gateway voice has been observed (Voice → Observed Edge, F-9), without inferring
the absent owner's need. Both Route A (Findability) and Route B (Gateway Support)
reference an edge_id; neither re-implements the edge concept.

An edge is an observation, not a Need, not an Action permission, not a target.
Person Domain stays sealed.

CLI:
  python -m bridge.edge_runtime.runtime.edge_builder
"""

from __future__ import annotations

from typing import Any

from ..store import (
    EDGE_RECORDS_JSONL, append_jsonl, edge_base_invariants, missing_base_invariants,
    next_id, read_jsonl, utc_now_iso,
)


def make_observed_edge(source_voice: str, gateway_ref: str,
                       observed_at: str | None = None) -> dict[str, Any]:
    """Pure constructor for an observed edge. gateway_ref is a reference, not a
    registration; source_voice is a gateway voice id (gateway domain)."""
    if not source_voice.strip():
        raise ValueError("source_voice (a gateway voice id) is required")
    return {
        "record_type": "observed_edge",
        "edge_id": None,
        "source_voice": source_voice.strip(),
        "gateway_ref": gateway_ref.strip(),
        "observed_at": observed_at or utc_now_iso(),
        # edge markers
        "is_observation_not_need": True,
        "is_not_action_permission": True,
        "not_owner_need": True,
        "gateway_domain": True,
        "status": "observed",
        **edge_base_invariants(),
    }


def record_observed_edge(source_voice: str, gateway_ref: str,
                         observed_at: str | None = None) -> dict[str, Any]:
    """Construct + persist an observed edge (idempotent by source_voice)."""
    rec = make_observed_edge(source_voice, gateway_ref, observed_at)
    for existing in read_jsonl(EDGE_RECORDS_JSONL):
        if existing.get("source_voice") == rec["source_voice"]:
            return existing
    rec["edge_id"] = next_id("edge", EDGE_RECORDS_JSONL)
    return append_jsonl(EDGE_RECORDS_JSONL, rec)


def list_edges() -> list[dict[str, Any]]:
    return read_jsonl(EDGE_RECORDS_JSONL)


def get_edge(edge_id: str) -> dict[str, Any] | None:
    return next((e for e in list_edges() if e.get("edge_id") == edge_id), None)


def edge_exists(edge_id: str) -> bool:
    return get_edge(edge_id) is not None


def check_invariants() -> list[str]:
    violations: list[str] = []
    for e in list_edges():
        violations += [f"{e.get('edge_id')}: {m}" for m in missing_base_invariants(e)]
        for f in ("is_observation_not_need", "is_not_action_permission",
                  "not_owner_need", "gateway_domain"):
            if e.get(f) is not True:
                violations.append(f"{e.get('edge_id')}: missing/false {f}")
    return violations


def main() -> None:
    print("=" * 64)
    print("OBSERVED EDGE BUILDER (F-9) — Voice -> Observed Edge (shared)")
    print("=" * 64)
    edges = list_edges()
    print(f"  observed edges: {len(edges)}  (0 is valid)")
    for e in edges:
        print(f"  · {e['edge_id']} voice={e['source_voice']} gateway_ref={e['gateway_ref']}")
    v = check_invariants()
    print(f"  invariant violations: {len(v)}")
    for x in v:
        print(f"    - {x}")
    print("-" * 64)
    print("An edge is an observation, not a Need or an action permission. Person domain sealed.")


if __name__ == "__main__":
    main()
