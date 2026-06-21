"""
consent_builder.py — Gateway Consent layer (F-14).

Gateway Resource Acceptance Consent: the gateway's explicit, voluntary,
specific, REVOCABLE, self-referential agreement to RECEIVE a specific support
form. It lives in the Resource Acceptance layer only — it does NOT make the
gateway a participant or a representative, and it can never consent on behalf of
the absent owner (self-referential).

Decisive rule (F-14): a self-stated public bottleneck is NOT consent. Statement
≠ consent. Consent must be OBTAINED, never inferred from a public statement.

CLI:
  python -m bridge.gateway_support.runtime.consent_builder
"""

from __future__ import annotations

from typing import Any

from ..store import (
    GATEWAY_CONSENTS_JSONL, append_jsonl, base_invariants, carries_base_invariants,
    next_id, read_jsonl, utc_now_iso,
)


def make_gateway_consent(
    gateway_ref: str,
    bottleneck_id: str,
    support_form: str,
    consent_source: str,
    obtained: bool,
) -> dict[str, Any]:
    """Pure constructor. `obtained` must be True — consent is obtained, not inferred."""
    if not obtained:
        raise ValueError(
            "gateway consent must be OBTAINED, not inferred from a public statement "
            "(F-14: statement is not consent)")
    if not consent_source.strip():
        raise ValueError("consent_source required (how the explicit consent was obtained)")
    return {
        "record_type": "gateway_consent",
        "consent_id": None,
        "gateway_ref": gateway_ref,
        "bottleneck_id": bottleneck_id,
        "support_form": support_form,              # specific (not blanket)
        "consent_layer": "resource_acceptance",
        "consent_source": consent_source.strip(),
        "consent_given_at": utc_now_iso(),
        # F-14 markers
        "explicit": True,
        "voluntary": True,
        "specific": True,
        "revocable": True,
        "self_referential": True,                  # gateway about itself, not owner
        "obtained_not_inferred": True,
        "statement_is_not_consent": True,
        "is_resource_acceptance_layer": True,
        "excludes_participation": True,
        "excludes_representation": True,
        "excludes_owner": True,
        "status": "active",
        **base_invariants(),
    }


def record_gateway_consent(**kwargs: Any) -> dict[str, Any]:
    rec = make_gateway_consent(**kwargs)
    rec["consent_id"] = next_id("gc", GATEWAY_CONSENTS_JSONL)
    return append_jsonl(GATEWAY_CONSENTS_JSONL, rec)


def list_consents() -> list[dict[str, Any]]:
    return read_jsonl(GATEWAY_CONSENTS_JSONL)


def active_consent(bottleneck_id: str, support_form: str) -> dict[str, Any] | None:
    """Return the active (non-withdrawn) consent for a (bottleneck, form), if any."""
    for c in list_consents():
        if (c.get("bottleneck_id") == bottleneck_id
                and c.get("support_form") == support_form
                and c.get("status") == "active"):
            return c
    return None


def check_invariants() -> list[str]:
    violations: list[str] = []
    for c in list_consents():
        violations += carries_base_invariants(c)
        for f in ("explicit", "voluntary", "specific", "revocable", "self_referential",
                  "obtained_not_inferred", "statement_is_not_consent",
                  "is_resource_acceptance_layer", "excludes_participation",
                  "excludes_representation", "excludes_owner"):
            if c.get(f) is not True:
                violations.append(f"{c.get('consent_id')}: missing/false {f}")
        if c.get("consent_layer") != "resource_acceptance":
            violations.append(f"{c.get('consent_id')}: consent layer is not resource_acceptance")
    return violations


def main() -> None:
    print("=" * 64)
    print("GATEWAY CONSENT BUILDER (F-14) — Resource Acceptance, revocable, obtained")
    print("=" * 64)
    cs = list_consents()
    print(f"  gateway consents: {len(cs)}  (0 is valid — none obtained)")
    for c in cs:
        print(f"  · {c['consent_id']} gw={c['gateway_ref']} form={c['support_form']} status={c['status']}")
    v = check_invariants()
    print(f"  invariant violations: {len(v)}")
    for x in v:
        print(f"    - {x}")
    print("-" * 64)
    print("A public statement is NOT consent. Consent is explicit, specific, revocable, and never covers the owner.")


if __name__ == "__main__":
    main()
