"""
ttfr_g_builder.py — TTFR-G Accounting layer (F-17).

TTFR-G (Time To First Rescue — Gateway) measures, for a gateway's self-stated
bottleneck, the interval from the edge being observed (T0 = execution.edge_observed_at)
to the gateway's self-stated relief being observable (T1 = feedback.observed_at,
when relief_observed is True).

This is a SEPARATE ledger from TTFR-P. It is permanently separated:
  - no combined metric, no relief-count KPI, no maximization logic,
  - it does not reduce the (person) Reach Gap and is never a person-relief proxy,
  - no gateway ranking, excludes all owner information.
The store structurally forbids the fields ttfr_p / combined_metric /
relief_count_kpi / reach_gap_estimate, so they can never be persisted here.

A TTFR-G record is created only from a feedback record with observed relief
(currently observable, gateway self-stated). 0 records is valid.

CLI:
  python -m bridge.gateway_support.runtime.ttfr_g_builder
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from ..store import (
    TTFR_G_RECORDS_JSONL, append_jsonl, base_invariants, carries_base_invariants,
    next_id, read_jsonl,
)
from .execution_builder import list_executions
from .feedback_builder import list_feedback


def _parse(ts: str) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def _existing() -> set[str]:
    return {r.get("feedback_id") for r in read_jsonl(TTFR_G_RECORDS_JSONL)}


def build() -> list[dict[str, Any]]:
    """One TTFR-G record per feedback with observed relief (idempotent). 0 in → 0 out."""
    execs = {e.get("execution_id"): e for e in list_executions()}
    done = _existing()
    created = []
    for f in list_feedback():
        if not f.get("relief_observed"):
            continue  # held: no completion, no TTFR-G
        if f.get("feedback_id") in done:
            continue
        e = execs.get(f.get("execution_id"))
        if e is None:
            continue
        t0 = _parse(e.get("edge_observed_at"))
        t1 = _parse(f.get("observed_at"))
        # B-3: a clock inversion (T1 < T0) is held, never persisted as a negative
        # interval. Valid T1 >= T0 records the non-negative interval as usual.
        inversion = bool(t0 and t1 and t1 < t0)
        secs = (t1 - t0).total_seconds() if (t0 and t1 and not inversion) else None
        rec = {
            "record_type": "ttfr_g",
            "ttfr_g_id": next_id("tg", TTFR_G_RECORDS_JSONL),
            "feedback_id": f.get("feedback_id"),
            "execution_id": f.get("execution_id"),
            "bottleneck_id": e.get("bottleneck_id"),
            "edge_observed_at": e.get("edge_observed_at"),     # T0
            "relief_observed_at": f.get("observed_at"),        # T1
            "ttfr_g_seconds": secs,
            "clock_inversion": inversion,
            "measure_owner": "gateway_self_stated",
            # F-17 separation markers (and store FORBIDDEN_FIELDS bars ttfr_p etc.)
            "ttfr_g_not_ttfr_p": True,
            "separate_ledger": True,
            "not_combined_metric": True,
            "not_reach_gap_reduction": True,
            "not_a_person_relief_proxy": True,
            "not_a_kpi": True,
            "no_maximization": True,
            "no_gateway_ranking": True,
            "excludes_owner_info": True,
            "status": "held_clock_inversion" if inversion else "recorded",
            **base_invariants(),
        }
        created.append(append_jsonl(TTFR_G_RECORDS_JSONL, rec))
        done.add(f.get("feedback_id"))
    return created


def list_ttfr_g() -> list[dict[str, Any]]:
    return read_jsonl(TTFR_G_RECORDS_JSONL)


def check_invariants() -> list[str]:
    violations: list[str] = []
    for r in list_ttfr_g():
        violations += carries_base_invariants(r)
        for f in ("ttfr_g_not_ttfr_p", "separate_ledger", "not_combined_metric",
                  "not_reach_gap_reduction", "not_a_person_relief_proxy", "not_a_kpi",
                  "no_maximization", "no_gateway_ranking", "excludes_owner_info"):
            if r.get(f) is not True:
                violations.append(f"{r.get('ttfr_g_id')}: missing/false {f}")
        if r.get("measure_owner") != "gateway_self_stated":
            violations.append(f"{r.get('ttfr_g_id')}: measure_owner is not gateway_self_stated")
        # B-3: a recorded interval must never be negative; inversions are held.
        secs = r.get("ttfr_g_seconds")
        if secs is not None and secs < 0:
            violations.append(f"{r.get('ttfr_g_id')}: negative ttfr_g_seconds ({secs})")
        if r.get("status") == "held_clock_inversion" and r.get("ttfr_g_seconds") is not None:
            violations.append(f"{r.get('ttfr_g_id')}: clock inversion held but seconds persisted")
    return violations


def main() -> None:
    print("=" * 64)
    print("TTFR-G ACCOUNTING BUILDER (F-17) — separate ledger, ⟂ TTFR-P")
    print("=" * 64)
    created = build()
    recs = list_ttfr_g()
    print(f"  ttfr-g records: {len(recs)}  (0 is valid)")
    for r in recs:
        print(f"  · {r['ttfr_g_id']} bottleneck={r['bottleneck_id']} ttfr_g_seconds={r['ttfr_g_seconds']}")
    v = check_invariants()
    print(f"  invariant violations: {len(v)}")
    for x in v:
        print(f"    - {x}")
    print("-" * 64)
    print("TTFR-G is gateway-domain only. No combined metric, no KPI, no maximization, no ranking. Never TTFR-P / Reach Gap.")


if __name__ == "__main__":
    main()
