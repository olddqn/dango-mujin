#!/usr/bin/env python3
"""
did_signature.py — dango-gitsea-bridge / DID signature layer

Mock DID signature implementation for Dan-Go su-table events.

⚠ This is NOT production cryptography.
  It is a deterministic test vector that fixes the signature flow
  so future Ed25519 / UCAN / real DID-resolver implementations
  can be dropped in at the same interface.

Mock signature formula:
  signature_value = sha256(key_id + ":" + signed_event_hash)

  signed_event_hash = sha256(canonical_json(event_body_stripped))

  event_body_stripped = event minus:
    - "event_hash"          (computed by sutable_log after appending)
    - "signature"           (the field being computed / verified)
    - "signature_status"    (added post-verification, not part of content)
    - "previous_event_hash" (added by sutable_log, not known at signing time)

The signature is over event content only — independent of chain position.
This means a signed event can be verified before or after it is appended.

Signature field format (attached to event as "signature"):
  {
    "type":                "mock-ed25519-test-vector",
    "did":                 "did:key:mock-dango-agent",
    "key_id":              "mock-key-001",
    "signature_value":     "<hex>",
    "signed_event_hash":   "<hex>",
    "verification_status": "mock_valid" | "mock_invalid"
  }

verification_status values (on the event root, not inside signature):
  "mock_valid"              — signature verified against event content
  "mock_invalid"            — signature present but does not verify
  "unsigned"                — no signature field (allowed, informational)
  "unsupported_signature_type" — type not "mock-ed25519-test-vector"

Public API:
  canonical_json(obj)           → str
  compute_event_hash(event)     → str  (strips fields first)
  mock_sign_event_hash(hash, key_id) → str
  mock_verify_signature(event_hash, sig_obj) → str  (status)
  strip_for_signing(event)      → dict
  attach_signature(event, did, key_id) → dict  (new dict, original unchanged)
  check_signature_status(event) → str  (status string)
"""

import hashlib
import json
from typing import Any

# ── Fields excluded from the canonical signing body ────────────
_STRIP_FOR_SIGNING = frozenset({
    "event_hash",
    "signature",
    "signature_status",
    "previous_event_hash",
})

SUPPORTED_TYPES = {"mock-ed25519-test-vector"}

STATUS_MOCK_VALID   = "mock_valid"
STATUS_MOCK_INVALID = "mock_invalid"
STATUS_UNSIGNED     = "unsigned"
STATUS_UNSUPPORTED  = "unsupported_signature_type"


def canonical_json(obj: Any) -> str:
    """Stable, deterministic JSON serialization for hashing.
    Sorted keys, no extra whitespace, UTF-8 safe."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def strip_for_signing(event: dict) -> dict:
    """Return event without fields that are added/computed post-signing."""
    return {k: v for k, v in event.items() if k not in _STRIP_FOR_SIGNING}


def compute_event_hash(event: dict) -> str:
    """Compute sha256 of the canonical signing body of an event."""
    body = strip_for_signing(event)
    return hashlib.sha256(canonical_json(body).encode("utf-8")).hexdigest()


def mock_sign_event_hash(event_hash: str, key_id: str) -> str:
    """
    Compute a mock signature value.

    Formula: sha256(key_id + ":" + event_hash)

    This is a deterministic function — NOT real cryptography.
    The "private key" is implicit in the key_id string.
    Any real implementation would replace this with actual Ed25519 signing.
    """
    data = f"{key_id}:{event_hash}"
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def mock_verify_signature(event_hash: str, sig_obj: dict) -> str:
    """
    Verify a mock signature object against the given event_hash.

    Returns one of: mock_valid | mock_invalid | unsupported_signature_type
    """
    sig_type = sig_obj.get("type", "")
    if sig_type not in SUPPORTED_TYPES:
        return STATUS_UNSUPPORTED

    key_id        = sig_obj.get("key_id", "")
    stored_value  = sig_obj.get("signature_value", "")
    stored_hash   = sig_obj.get("signed_event_hash", "")

    # The hash must match the event's computed hash
    if stored_hash != event_hash:
        return STATUS_MOCK_INVALID

    # Recompute expected signature value
    expected = mock_sign_event_hash(event_hash, key_id)
    if expected == stored_value:
        return STATUS_MOCK_VALID
    return STATUS_MOCK_INVALID


def attach_signature(event: dict, did: str, key_id: str) -> dict:
    """
    Return a new event dict with a mock signature field attached.
    Original event is not mutated.

    The signature covers event content minus signature/event_hash/previous_event_hash.
    """
    event_hash = compute_event_hash(event)
    sig_value  = mock_sign_event_hash(event_hash, key_id)

    result = dict(event)
    result["signature"] = {
        "type":                "mock-ed25519-test-vector",
        "did":                 did,
        "key_id":              key_id,
        "signature_value":     sig_value,
        "signed_event_hash":   event_hash,
        "verification_status": STATUS_MOCK_VALID,
    }
    return result


def check_signature_status(event: dict) -> str:
    """
    Determine the signature status of an event.

    Returns: mock_valid | mock_invalid | unsigned | unsupported_signature_type
    """
    sig = event.get("signature")
    if sig is None:
        return STATUS_UNSIGNED

    event_hash = compute_event_hash(event)
    return mock_verify_signature(event_hash, sig)


def signature_summary(event: dict) -> dict:
    """
    Return a summary dict useful for display / logging.
    """
    sig    = event.get("signature", {})
    status = check_signature_status(event)
    return {
        "status":            status,
        "did":               sig.get("did", ""),
        "key_id":            sig.get("key_id", ""),
        "signed_event_hash": sig.get("signed_event_hash", ""),
        "actual_event_hash": compute_event_hash(event),
        "type":              sig.get("type", ""),
    }
