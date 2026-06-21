"""
execution_builder.py — Support Execution layer (F-15).

A Support Execution is the actual transfer of a gateway-consented support form,
within the Resource Acceptance layer. It can only be created when BOTH keys are
present for the same candidate (F-13 ∧ F-14):
  (1) a PERMIT approval for the candidate, and
  (2) an ACTIVE gateway consent for the candidate's (bottleneck, support_form),
and only while the underlying bottleneck is still verified.

It is NEVER automatic: it must be invoked explicitly and re-checks the two keys
each time. It performs no person-domain interaction, preserves gateway autonomy,
advances TTFR-G only, and never mutates TTFR-P.

CLI:
  python -m bridge.gateway_support.runtime.execution_builder
"""

from __future__ import annotations

from typing import Any

from ..store import (
    SUPPORT_EXECUTIONS_JSONL, append_jsonl, base_invariants, carries_base_invariants,
    next_id, read_jsonl, utc_now_iso,
)
from .bottleneck_builder import list_verified_bottlenecks
from .support_candidate_builder import list_candidates
from .approval_builder import permitted_candidate_ids
from .consent_builder import active_consent


def _candidate(candidate_id: str) -> dict[str, Any] | None:
    return next((c for c in list_candidates() if c.get("candidate_id") == candidate_id), None)


def _bottleneck(bottleneck_id: str) -> dict[str, Any] | None:
    return next((b for b in list_verified_bottlenecks()
                 if b.get("bottleneck_id") == bottleneck_id), None)


def keys_existed(candidate_id: str) -> tuple[bool, str]:
    """Historical eligibility check (F-18): the two keys (PERMIT approval ∧ ACTIVE
    gateway consent) plus a verified bottleneck. It deliberately IGNORES any later
    withdrawal — a withdrawal voids FUTURE support, not an irreversible PAST
    execution. Used to audit already-persisted executions, which remain valid even
    after the support is later halted."""
    cand = _candidate(candidate_id)
    if cand is None:
        return False, "unknown candidate"
    if candidate_id not in permitted_candidate_ids():
        return False, "no PERMIT approval (key 1 missing)"
    consent = active_consent(cand["bottleneck_id"], cand["support_form"])
    if consent is None:
        return False, "no ACTIVE gateway consent (key 2 missing)"
    b = _bottleneck(cand["bottleneck_id"])
    if b is None or b.get("status") != "verified":
        return False, "bottleneck not verified"
    return True, "keys existed"


def two_keys_present(candidate_id: str) -> tuple[bool, str]:
    """New-execution gate (F-15 ∧ F-18): the two keys must exist AND support must
    not be halted by a withdrawal. The halt check blocks only NEW executions; it
    never retroactively invalidates a past execution (see keys_existed)."""
    from .withdrawal_builder import is_halted, halt_cause  # local import avoids cycle
    cand = _candidate(candidate_id)
    if cand is None:
        return False, "unknown candidate"
    if is_halted(cand["bottleneck_id"]):
        return False, f"support halted by withdrawal ({halt_cause(cand['bottleneck_id'])})"
    return keys_existed(candidate_id)


def execute(candidate_id: str, executor: str) -> dict[str, Any]:
    """Explicit, non-automatic execution. Refuses unless both keys present."""
    ok, reason = two_keys_present(candidate_id)
    if not ok:
        raise ValueError(f"execution refused: {reason} (no auto-execution; two-key gate F-15)")
    if not executor.strip():
        raise ValueError("named human executor required (human_review_required)")
    cand = _candidate(candidate_id)
    b = _bottleneck(cand["bottleneck_id"])
    consent = active_consent(cand["bottleneck_id"], cand["support_form"])
    rec = {
        "record_type": "support_execution",
        "execution_id": next_id("ex", SUPPORT_EXECUTIONS_JSONL),
        "candidate_id": candidate_id,
        "bottleneck_id": cand["bottleneck_id"],
        "consent_id": consent["consent_id"],
        "support_form": cand["support_form"],
        "edge_observed_at": b.get("edge_observed_at"),   # T0 for TTFR-G
        "executed_at": utc_now_iso(),
        "executor": executor.strip(),
        # F-15 markers
        "two_keys_present": True,
        "within_consent_scope": True,
        "is_not_automatic": True,
        "no_person_domain_interaction": True,
        "no_owner_interaction": True,
        "gateway_autonomy_preserved": True,
        "advances_ttfr_g_only": True,
        "does_not_mutate_ttfr_p": True,
        "is_resource_acceptance_layer": True,
        "status": "executed",
        **base_invariants(),
    }
    return append_jsonl(SUPPORT_EXECUTIONS_JSONL, rec)


def list_executions() -> list[dict[str, Any]]:
    return read_jsonl(SUPPORT_EXECUTIONS_JSONL)


def check_invariants() -> list[str]:
    violations: list[str] = []
    for e in list_executions():
        violations += carries_base_invariants(e)
        for f in ("two_keys_present", "within_consent_scope", "is_not_automatic",
                  "no_person_domain_interaction", "no_owner_interaction",
                  "gateway_autonomy_preserved", "advances_ttfr_g_only",
                  "does_not_mutate_ttfr_p"):
            if e.get(f) is not True:
                violations.append(f"{e.get('execution_id')}: missing/false {f}")
        # Audit past executions by HISTORICAL eligibility (keys existed), NOT by the
        # halt gate: a later withdrawal voids future support, not an already-valid
        # past execution (F-18). Using two_keys_present here would wrongly flag a
        # valid past execution once its bottleneck is withdrawn (B-1).
        ok, reason = keys_existed(e.get("candidate_id"))
        if not ok:
            violations.append(f"{e.get('execution_id')}: persisted but keys never existed ({reason})")
    return violations


def main() -> None:
    print("=" * 64)
    print("SUPPORT EXECUTION BUILDER (F-15) — two-key gate, never automatic")
    print("=" * 64)
    exs = list_executions()
    print(f"  executions: {len(exs)}  (0 is valid — two keys not present)")
    for e in exs:
        print(f"  · {e['execution_id']} candidate={e['candidate_id']} form={e['support_form']}")
    v = check_invariants()
    print(f"  invariant violations: {len(v)}")
    for x in v:
        print(f"    - {x}")
    print("-" * 64)
    print("Execution requires PERMIT ∧ CONSENT ∧ verified. No automatic execution. No person domain. TTFR-G only.")


if __name__ == "__main__":
    main()
