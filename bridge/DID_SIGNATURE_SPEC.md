# DID Signature Specification — dango-gitsea-bridge

> A signature is not proof of truth. A signature is proof of authorship.
> The su-table records both — the claim and who signed it.

---

## Overview

Dan-Go su-table events support an optional DID signature field.

This allows any party appending an event to declare: *"I, this DID, authored this event content."*

The current implementation is a **mock test vector** — it uses deterministic sha256 hashes
instead of real Ed25519 cryptography. The interface is designed so that a real
Ed25519 / UCAN / DID-resolver implementation can replace the mock with no API changes.

**Absolute prohibitions for this implementation:**

- ⛔ No real private keys
- ⛔ No seed phrases or wallet keys
- ⛔ No real DID resolver network calls
- ⛔ No external libraries
- ⛔ No real transaction signing

---

## Mock Signature Formula

```
signed_event_hash = sha256(canonical_json(strip_for_signing(event)))

signature_value   = sha256(key_id + ":" + signed_event_hash)
```

### Canonical JSON

- `json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))`
- Deterministic, no whitespace, sorted keys, UTF-8 safe

### Strip-for-signing

The following fields are excluded from the signed body:

| Field | Reason |
|---|---|
| `event_hash` | Computed by sutable_log after appending; not known at signing time |
| `signature` | The field being computed; cannot be self-referential |
| `signature_status` | Added by sutable_append post-verification, not part of content |
| `previous_event_hash` | Added by sutable_log during append; not part of event content |

**This means:** a signed event can be verified **before or after** it is appended to the su-table.
The signature is independent of chain position.

---

## Signature Field Format

The `"signature"` field is attached to the event object:

```json
{
  "type":                "mock-ed25519-test-vector",
  "did":                 "did:key:mock-dango-agent",
  "key_id":              "mock-key-001",
  "signature_value":     "<64-char hex>",
  "signed_event_hash":   "<64-char hex>",
  "verification_status": "mock_valid"
}
```

| Field | Description |
|---|---|
| `type` | Signature algorithm identifier |
| `did` | DID of the signer |
| `key_id` | Key identifier within the DID |
| `signature_value` | `sha256(key_id + ":" + signed_event_hash)` |
| `signed_event_hash` | `sha256(canonical_json(stripped_event))` |
| `verification_status` | Status at signing time (always `mock_valid` when created) |

---

## Verification Status Values

Status lives at the **event root** as `signature_status` (set by sutable_append during ingest).
It also appears inside the signature object as `verification_status` (set at signing time).

| Status | Meaning |
|---|---|
| `mock_valid` | Signature present and verified against event content |
| `mock_invalid` | Signature present but does not verify (content may have changed) |
| `unsigned` | No signature field (allowed — not all events require signatures) |
| `unsupported_signature_type` | Signature type is not `mock-ed25519-test-vector` |

---

## Sutable Append Policy

When `sutable_append.py` receives an event, it checks the signature before writing:

```
┌────────────────────────────────────────────┐
│ Event has no "signature" field?            │
│   → signature_status = "unsigned"          │
│   → ALLOWED (unsigned events are permitted)│
└────────────────────────────────────────────┘
┌────────────────────────────────────────────┐
│ Event has "signature" field:               │
│   type ∉ SUPPORTED_TYPES?                  │
│     → REJECTED (unsupported_signature_type)│
│   signed_event_hash ≠ actual_event_hash?   │
│     → REJECTED (mock_invalid)              │
│   expected ≠ stored signature_value?       │
│     → REJECTED (mock_invalid)              │
│   all checks pass?                         │
│     → signature_status = "mock_valid"      │
│     → ALLOWED                              │
└────────────────────────────────────────────┘
```

The `signature_status` field is written to the JSONL record on append.
It is included in the signed body for events appended to the su-table.

Wait — but `signature_status` is in `_STRIP_FOR_SIGNING`.
This means: the signature you attach **before** appending covers the event content
minus the status. After append, the chain hash covers the full record including status.
This is intentional: the signature attests to the content, the chain attests to the record.

---

## Supported Signature Types

```python
SUPPORTED_TYPES = {"mock-ed25519-test-vector"}
```

Future implementations may add:
- `ed25519` — real Ed25519 signing via libsodium or PyNaCl
- `ucan-ed25519` — UCAN-style delegation token
- `did-key-ed25519` — DID:key method with real key material

The verification pipeline in `did_signature.py` is designed to accept additional types
by extending `SUPPORTED_TYPES` and the `mock_verify_signature` dispatch logic.

---

## CLI Reference

### Sign an event

```bash
# Sign with defaults (did:key:mock-dango-agent / mock-key-001) → stdout
python runtime/sign_event.py examples/sutable_events/claim_event.json

# Sign and write to file
python runtime/sign_event.py examples/sutable_events/claim_event.json \
  --did did:key:z6MkLegalReviewer \
  --key-id legal-key-001 \
  --output examples/signed-claim-event.json

# Sign and immediately verify
python runtime/sign_event.py examples/sutable_events/claim_event.json --verify
```

### Verify a signed event

```bash
# Human-readable output (exit 0 = valid, exit 1 = invalid/unsigned)
python runtime/verify_event_signature.py examples/signed-claim-event.json

# JSON output
python runtime/verify_event_signature.py examples/signed-claim-event.json --json

# Quiet: just exit code
python runtime/verify_event_signature.py examples/signed-claim-event.json --quiet
```

### Append with signature validation

```bash
# Signed event → validates signature → appends with signature_status=mock_valid
python runtime/sutable_append.py --table claims \
  --event examples/signed-claim-event.json

# Unsigned event → appends with signature_status=unsigned
python runtime/sutable_append.py --table claims \
  --event examples/sutable_events/claim_event.json

# Invalid signature → REJECTED (exit 1, event not written)
python runtime/sutable_append.py --table claims \
  --event examples/invalid-signed-event.json

# Skip signature validation (force unsigned treatment)
python runtime/sutable_append.py --table claims \
  --event examples/sutable_events/claim_event.json \
  --no-signature
```

---

## Programmatic Usage

```python
from runtime.did_signature import (
    attach_signature,
    check_signature_status,
    signature_summary,
    compute_event_hash,
    strip_for_signing,
)

# Sign an event
event = {"event_type": "claim_created", "claim_id": "housing-002", ...}
signed = attach_signature(event, did="did:key:mock-dango-agent", key_id="mock-key-001")

# Verify
status = check_signature_status(signed)   # → "mock_valid"

# Full summary
info = signature_summary(signed)
# {
#   "status": "mock_valid",
#   "did": "did:key:mock-dango-agent",
#   "key_id": "mock-key-001",
#   "signed_event_hash": "...",
#   "actual_event_hash": "...",
#   "type": "mock-ed25519-test-vector"
# }

# Verify an unsigned event
unsigned_event = {"event_type": "objection", ...}
check_signature_status(unsigned_event)   # → "unsigned"

# Verify a tampered event (signature present, but content changed)
tampered = dict(signed)
tampered["statement"] = "Modified after signing"
check_signature_status(tampered)   # → "mock_invalid"
```

---

## Negotiation Graph Display

The negotiation graph (`graph_export.py`) renders signature status in all three formats:

### Mermaid (`--format mermaid`)

Nodes with `mock_valid` signature have `✓sig` appended to their label:

```
n0["Claim: A vacant house…  ✓sig<br/><small>2026-05-24 12:00</small>"]:::claim
```

### Text (`--format text`)

Each event shows a signature status line:

```
  1. 📋 [claims] Claim: A vacant house…
       2026-05-24 12:00:00
       speaker: did:key:z6MkproposerHousing
       ✓ [signature: mock_valid]  signer: did:key:mock-dango-agent
       │
  2. ⡡ [negotiations] Objection: Legal ownership…
       2026-05-24 12:01:00
       ○ [signature: unsigned]
```

### HTML (`--format html`)

- **Summary card**: "Signed Events" count
- **Timeline**: colored badge per event (`✓ sig` / `unsigned` / `✗ sig` / `? sig`)
- **Event table**: two new columns — `signature` and `signer did`
- **Integrity notes**: count of signed / unsigned / invalid events

Badge styles:

| Status | Color |
|---|---|
| `mock_valid` | Green on dark green |
| `unsigned` | Gray on near-black |
| `mock_invalid` | Red on dark red |
| `unsupported_signature_type` | Indigo on dark indigo |

---

## Example Files

| File | Description |
|---|---|
| `examples/signed-claim-event.json` | Valid mock-signed claim event |
| `examples/invalid-signed-event.json` | Corrupted `signature_value` (always rejects) |

---

## Public API — `did_signature.py`

| Function | Signature | Returns |
|---|---|---|
| `canonical_json(obj)` | `Any → str` | Sorted-key JSON string |
| `strip_for_signing(event)` | `dict → dict` | Event minus excluded fields |
| `compute_event_hash(event)` | `dict → str` | sha256 hex of stripped event |
| `mock_sign_event_hash(hash, key_id)` | `str, str → str` | sha256 hex mock signature |
| `mock_verify_signature(hash, sig_obj)` | `str, dict → str` | Status string |
| `attach_signature(event, did, key_id)` | `dict, str, str → dict` | New event dict with signature |
| `check_signature_status(event)` | `dict → str` | Status string |
| `signature_summary(event)` | `dict → dict` | Display dict |

---

## Why Mock, Not Real

Real Ed25519 signing requires:
- Private key material (a secret)
- A secure random number generator seeded at key-generation time
- Key storage that survives process restart
- Key distribution infrastructure (DID resolver, key server, or IPFS)

Dan-Go's bridge is a **translation layer model** — not a custody layer.
It does not hold secrets. It does not need to.

The mock signature achieves the **same interface contract** without the risks:
- The signing formula is deterministic and auditable
- The verification logic is identical to what a real implementation would use
- Any real library (PyNaCl, cryptography, libsodium) can be dropped in at the same entry points

When real signing is needed: replace `mock_sign_event_hash()` and `mock_verify_signature()`
with calls to the real library. Nothing else changes.

---

> "The signature says: I was here. I said this. I acknowledge this record."
> The su-table says: "And we remember."
