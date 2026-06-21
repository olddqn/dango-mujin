"""
bottleneck_builder.py — Verified Bottleneck layer (F-9 / F-11).

A Verified Bottleneck records that a gateway's OWN, publicly self-stated
operational bottleneck is *currently observable* — without inference. Per F-11,
verified is NOT proof; it is a "currently observable support condition". The
four minimal conditions (all required): self-stated · public · currently
observable · inference-free. If any is missing the bottleneck is HELD (not
recorded).

This is the Observed Edge → Gateway Domain entry. Person Domain stays sealed:
the record concerns the gateway-as-actor's self-stated public need, never the
absent owner's need (no need inference).

CLI:
  python -m bridge.gateway_support.runtime.bottleneck_builder
"""

from __future__ import annotations

from typing import Any

from ..store import (
    VERIFIED_BOTTLENECKS_JSONL, append_jsonl, base_invariants, carries_base_invariants,
    next_id, read_jsonl, utc_now_iso,
)


def make_verified_bottleneck(
    source_edge: str,
    gateway_ref: str,
    public_source_url: str,
    bottleneck_kind: str,
    accepted_support_forms: list[str],
    verified_by: str,
    self_stated: bool,
    public: bool,
    currently_observable: bool,
    inference_free: bool,
    edge_observed_at: str | None = None,
) -> dict[str, Any]:
    """Pure constructor. Raises if the four verification conditions are not all
    satisfied (the bottleneck would be HELD, not verified)."""
    if not (self_stated and public and currently_observable and inference_free):
        raise ValueError(
            "verification HELD: requires self_stated ∧ public ∧ currently_observable "
            "∧ inference_free (F-11). Not all satisfied — do not record as verified.")
    if not public_source_url.strip():
        raise ValueError("public_source_url required (public, currently observable)")
    if not verified_by.strip():
        raise ValueError("named human verifier required (human_review_required)")
    rec = {
        "record_type": "verified_bottleneck",
        "bottleneck_id": None,  # assigned at persist
        "source_edge": source_edge,
        "gateway_ref": gateway_ref,           # a reference, NOT a registration
        "bottleneck_kind": bottleneck_kind,   # gateway's self-stated kind (e.g. funding/staffing)
        "accepted_support_forms": list(accepted_support_forms),  # gateway self-stated
        "public_source_url": public_source_url.strip(),
        "edge_observed_at": edge_observed_at or utc_now_iso(),
        "verified_at": utc_now_iso(),
        "verified_by": verified_by.strip(),
        # F-11 markers
        "self_stated": True,
        "public": True,
        "currently_observable": True,
        "inference_free": True,
        "is_observable_condition_not_proof": True,
        "verification_is_not_proof": True,
        "not_owner_need": True,
        "gateway_not_registered_by_this_record": True,
        "status": "verified",
        **base_invariants(),
    }
    return rec


def record_verified_bottleneck(**kwargs: Any) -> dict[str, Any]:
    """Construct + persist a verified bottleneck (idempotent by source_edge+kind)."""
    rec = make_verified_bottleneck(**kwargs)
    key = (rec["source_edge"], rec["bottleneck_kind"])
    for existing in read_jsonl(VERIFIED_BOTTLENECKS_JSONL):
        if (existing.get("source_edge"), existing.get("bottleneck_kind")) == key:
            return existing
    rec["bottleneck_id"] = next_id("vb", VERIFIED_BOTTLENECKS_JSONL)
    return append_jsonl(VERIFIED_BOTTLENECKS_JSONL, rec)


def list_verified_bottlenecks() -> list[dict[str, Any]]:
    return read_jsonl(VERIFIED_BOTTLENECKS_JSONL)


def check_invariants() -> list[str]:
    violations: list[str] = []
    for r in list_verified_bottlenecks():
        violations += carries_base_invariants(r)
        for f in ("self_stated", "public", "currently_observable", "inference_free",
                  "is_observable_condition_not_proof", "not_owner_need"):
            if r.get(f) is not True:
                violations.append(f"{r.get('bottleneck_id')}: missing/false {f}")
        if r.get("verification_is_not_proof") is not True:
            violations.append(f"{r.get('bottleneck_id')}: claims proof (must be observable condition)")
    return violations


def main() -> None:
    print("=" * 64)
    print("VERIFIED BOTTLENECK BUILDER (F-9/F-11) — observable condition, not proof")
    print("=" * 64)
    bns = list_verified_bottlenecks()
    print(f"  verified bottlenecks: {len(bns)}  (0 is valid — none verified / held)")
    for b in bns:
        print(f"  · {b['bottleneck_id']} edge={b['source_edge']} kind={b['bottleneck_kind']}")
    v = check_invariants()
    print(f"  invariant violations: {len(v)}")
    for x in v:
        print(f"    - {x}")
    print("-" * 64)
    print("Verification is a currently observable support condition. Held if not all four conditions hold.")


if __name__ == "__main__":
    main()
