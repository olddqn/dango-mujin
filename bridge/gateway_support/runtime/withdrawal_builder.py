"""
withdrawal_builder.py — Withdrawal layer (F-18).

Support for a verified bottleneck is HALTED when any of the three keys is lost:
  - consent_withdrawn   (the gateway revokes its Resource Acceptance consent)
  - approval_revoked    (the human reviewer revokes the permit)
  - verification_lost   (the bottleneck is no longer currently observable)

Withdrawal voids future / in-progress support; it does not (and cannot) undo an
already-completed irreversible transfer. Withdrawal is NOT failure. It stays in
the gateway domain. Append-only: a withdrawal is a new record (nothing is mutated).

`is_halted(bottleneck_id)` is the runtime halt signal consulted by the execution
gate: once a withdrawal targets a bottleneck, no further execution may occur.

CLI:
  python -m bridge.gateway_support.runtime.withdrawal_builder
"""

from __future__ import annotations

from typing import Any

from ..store import (
    WITHDRAWAL_RECORDS_JSONL, append_jsonl, base_invariants, carries_base_invariants,
    next_id, read_jsonl,
)

CAUSES = ("consent_withdrawn", "approval_revoked", "verification_lost")


def make_withdrawal(
    bottleneck_id: str,
    cause: str,
    withdrawn_by: str,
    reason: str = "",
    target_kind: str | None = None,
    target_id: str | None = None,
) -> dict[str, Any]:
    """Pure constructor. cause must be one of the three halting causes."""
    if cause not in CAUSES:
        raise ValueError(f"withdrawal cause must be one of {CAUSES}")
    if not withdrawn_by.strip():
        raise ValueError("named human actor required")
    return {
        "record_type": "withdrawal",
        "withdrawal_id": None,
        "bottleneck_id": bottleneck_id,
        "cause": cause,
        "target_kind": target_kind,         # consent | approval | bottleneck (optional)
        "target_id": target_id,
        "withdrawn_by": withdrawn_by.strip(),
        "reason": reason.strip(),
        # F-18 markers
        "halts_support": True,
        "is_not_failure": True,
        "voids_future_not_irreversible_past": True,
        "stays_in_gateway_domain": True,
        "always_possible": True,
        "status": "halted",
        **base_invariants(),
    }


def record_withdrawal(**kwargs: Any) -> dict[str, Any]:
    rec = make_withdrawal(**kwargs)
    rec["withdrawal_id"] = next_id("wd", WITHDRAWAL_RECORDS_JSONL)
    return append_jsonl(WITHDRAWAL_RECORDS_JSONL, rec)


def list_withdrawals() -> list[dict[str, Any]]:
    return read_jsonl(WITHDRAWAL_RECORDS_JSONL)


def is_halted(bottleneck_id: str) -> bool:
    """Runtime halt signal: any withdrawal targeting this bottleneck halts support."""
    return any(w.get("bottleneck_id") == bottleneck_id for w in list_withdrawals())


def halt_cause(bottleneck_id: str) -> str | None:
    for w in list_withdrawals():
        if w.get("bottleneck_id") == bottleneck_id:
            return w.get("cause")
    return None


def check_invariants() -> list[str]:
    violations: list[str] = []
    for w in list_withdrawals():
        violations += carries_base_invariants(w)
        if w.get("cause") not in CAUSES:
            violations.append(f"{w.get('withdrawal_id')}: invalid cause {w.get('cause')}")
        for f in ("halts_support", "is_not_failure", "voids_future_not_irreversible_past",
                  "stays_in_gateway_domain", "always_possible"):
            if w.get(f) is not True:
                violations.append(f"{w.get('withdrawal_id')}: missing/false {f}")
    return violations


def main() -> None:
    print("=" * 64)
    print("WITHDRAWAL BUILDER (F-18) — any key lost halts support; not failure")
    print("=" * 64)
    ws = list_withdrawals()
    print(f"  withdrawals: {len(ws)}  (0 is valid)")
    for w in ws:
        print(f"  · {w['withdrawal_id']} bottleneck={w['bottleneck_id']} cause={w['cause']}")
    v = check_invariants()
    print(f"  invariant violations: {len(v)}")
    for x in v:
        print(f"    - {x}")
    print("-" * 64)
    print("Consent withdrawn / approval revoked / verification lost -> support halts. Withdrawal is not failure.")


if __name__ == "__main__":
    main()
