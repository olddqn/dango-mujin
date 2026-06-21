"""
feedback_builder.py — Reality Feedback layer (F-16).

Records whether a gateway's self-stated bottleneck became observably relieved
after a support execution. Feedback is OBSERVATION ONLY: relief is a currently
observable condition (gateway's own self-stated measure), never a claim, never
success inflation, never a causal inference ("support caused relief"). If relief
is not observable, it is HELD (relief_observed=false), not claimed.

This is gateway-domain only. It never claims person relief and is wholly
separate from TTFR-P.

CLI:
  python -m bridge.gateway_support.runtime.feedback_builder
"""

from __future__ import annotations

from typing import Any

from ..store import (
    SUPPORT_FEEDBACK_JSONL, append_jsonl, base_invariants, carries_base_invariants,
    next_id, read_jsonl, utc_now_iso,
)
from .execution_builder import list_executions


def make_feedback(
    execution_id: str,
    relief_observed: bool,
    relief_source_url: str,
    observed_by: str,
) -> dict[str, Any]:
    """Pure constructor. relief_observed requires a public, currently observable,
    gateway self-stated source; otherwise it is held (relief_observed=False)."""
    if relief_observed and not relief_source_url.strip():
        raise ValueError(
            "relief_observed=True requires a public currently-observable source "
            "(gateway self-stated). No relief claim without observation (F-16).")
    if not observed_by.strip():
        raise ValueError("named human observer required")
    return {
        "record_type": "support_feedback",
        "feedback_id": None,
        "execution_id": execution_id,
        "relief_observed": bool(relief_observed),
        "relief_source_url": relief_source_url.strip(),
        "relief_measure": "gateway_self_stated",
        "observed_at": utc_now_iso(),
        "observed_by": observed_by.strip(),
        # F-16 markers
        "relief_is_observation_not_claim": True,
        "no_relief_claim": True,
        "no_success_inflation": True,
        "no_causal_inference": True,
        "gateway_self_stated_relief": True,
        "is_observable_not_proof": True,
        "no_person_relief_claim": True,
        "status": "observed" if relief_observed else "held",
        **base_invariants(),
    }


def record_feedback(**kwargs: Any) -> dict[str, Any]:
    exec_ids = {e.get("execution_id") for e in list_executions()}
    if kwargs.get("execution_id") not in exec_ids:
        raise ValueError("feedback requires an existing execution (no fabrication)")
    rec = make_feedback(**kwargs)
    rec["feedback_id"] = next_id("fb", SUPPORT_FEEDBACK_JSONL)
    return append_jsonl(SUPPORT_FEEDBACK_JSONL, rec)


def list_feedback() -> list[dict[str, Any]]:
    return read_jsonl(SUPPORT_FEEDBACK_JSONL)


def check_invariants() -> list[str]:
    violations: list[str] = []
    exec_ids = {e.get("execution_id") for e in list_executions()}
    for f in list_feedback():
        violations += carries_base_invariants(f)
        for k in ("relief_is_observation_not_claim", "no_relief_claim",
                  "no_success_inflation", "no_causal_inference",
                  "gateway_self_stated_relief", "no_person_relief_claim"):
            if f.get(k) is not True:
                violations.append(f"{f.get('feedback_id')}: missing/false {k}")
        if f.get("execution_id") not in exec_ids:
            violations.append(f"{f.get('feedback_id')}: feedback for non-existent execution")
        if f.get("relief_observed") and not (f.get("relief_source_url") or "").strip():
            violations.append(f"{f.get('feedback_id')}: relief claimed without observable source")
    return violations


def main() -> None:
    print("=" * 64)
    print("REALITY FEEDBACK BUILDER (F-16) — observation only, no relief claims")
    print("=" * 64)
    fbs = list_feedback()
    print(f"  feedback records: {len(fbs)}  (0 is valid)")
    for f in fbs:
        print(f"  · {f['feedback_id']} exec={f['execution_id']} relief_observed={f['relief_observed']} status={f['status']}")
    v = check_invariants()
    print(f"  invariant violations: {len(v)}")
    for x in v:
        print(f"    - {x}")
    print("-" * 64)
    print("Relief is observed (gateway self-stated), never claimed or inflated. Never person relief.")


if __name__ == "__main__":
    main()
