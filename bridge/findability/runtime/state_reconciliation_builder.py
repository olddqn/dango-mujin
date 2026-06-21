"""
state_reconciliation_builder.py — Route A: State Reconciliation (F-24).

Records (observation only) the divergence between the DESIGNED findability door
(person-data-zero) and the ACTUAL public state, for an edge. It accounts the gap
honestly; it never ranks, never exposes person data, and flags that remediation
is a human-approved action (it performs none). 0 is valid. CLI:
  python -m bridge.findability.runtime.state_reconciliation_builder
"""

from __future__ import annotations

from typing import Any

from bridge.edge_runtime.runtime.edge_builder import edge_exists
from bridge.edge_runtime.runtime import edge_memory
from ..store import (STATE_RECONCILIATIONS_JSONL, append_jsonl,
                     findability_base_invariants, missing_base_invariants, next_id,
                     read_jsonl, utc_now_iso)


def make_reconciliation(edge_id: str, designed_state: str, actual_state: str,
                        divergence: str, exposure_is_benign: bool,
                        recorded_by: str) -> dict[str, Any]:
    if not recorded_by.strip():
        raise ValueError("named human recorder required")
    return {
        "record_type": "state_reconciliation",
        "reconciliation_id": None,
        "edge_id": edge_id,
        "designed_state": designed_state,     # e.g. "person_data_zero_door"
        "actual_state": actual_state,         # e.g. "dev_repo_public"
        "divergence": divergence,             # descriptive type, e.g. "large" / "none"
        "exposure_is_benign": bool(exposure_is_benign),
        "remediation_requires_human_approval": True,
        "performs_no_remediation": True,
        "recorded_by": recorded_by.strip(),
        "observed_at": utc_now_iso(),
        "status": "reconciled",
        **findability_base_invariants(),
    }


def record_reconciliation(**kwargs: Any) -> dict[str, Any]:
    if not edge_exists(kwargs.get("edge_id")):
        raise ValueError(f"unknown edge {kwargs.get('edge_id')}")
    rec = make_reconciliation(**kwargs)
    rec["reconciliation_id"] = next_id("sr", STATE_RECONCILIATIONS_JSONL)
    stored = append_jsonl(STATE_RECONCILIATIONS_JSONL, rec)
    edge_memory.record_episode(rec["edge_id"], "findability", rec["reconciliation_id"],
                               "state_reconciliation",
                               "benign" if rec["exposure_is_benign"] else "needs_review")
    return stored


def list_reconciliations() -> list[dict[str, Any]]:
    return read_jsonl(STATE_RECONCILIATIONS_JSONL)


def check_invariants() -> list[str]:
    out: list[str] = []
    for r in list_reconciliations():
        out += [f"{r.get('reconciliation_id')}: {m}" for m in
                missing_base_invariants(r, findability_base_invariants())]
        for f in ("remediation_requires_human_approval", "performs_no_remediation"):
            if r.get(f) is not True:
                out.append(f"{r.get('reconciliation_id')}: missing/false {f}")
    return out


def main() -> None:
    print("STATE RECONCILIATION BUILDER (Route A, F-24)")
    r = list_reconciliations()
    print(f"  reconciliations: {len(r)} (0 valid) | invariant violations: {len(check_invariants())}")
    print("  Honest gap accounting; no remediation performed; human approval required.")


if __name__ == "__main__":
    main()
