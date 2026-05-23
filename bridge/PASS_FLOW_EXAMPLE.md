# PASS Flow Example — Consent Established

> A worked example of the dignity guard moving from BLOCK to PASS.

---

## Why the Dignity Guard Exists

A person's lived story is not a product.
A refugee's account of survival is not content to be optimized.
A community's history is not a dataset to be monetized.

And yet: stories need to travel. Support needs to flow.
Translation needs to happen. Legal risk needs to be reviewed.
Fair participation is possible — but only if the conditions are met first.

The Dignity Guard exists because:

1. **Consent cannot be assumed.** "They probably want help" is not consent.
2. **Urgency cannot override dignity.** "We need to act fast" is how exploitation happens.
3. **Good intentions are not sufficient.** Intent does not protect against harm.
4. **Blocking is the correct default.** If unsure → block. Always.

---

## The Flow: BLOCK → NEGOTIATE → PASS

### Stage 1: BLOCK (consent unknown)

Initial state: a claim exists, but consent is not established.

```
observed_state: ["story_exists", "support_needed", "consent_unknown"]
```

Dignity guard result:

```
✗ [BLOCK] consent_unknown
     consent_unknown in observed_state — cannot proceed without established consent.

FINAL DECISION: ✗ BLOCK
```

**Stream status: paused. No contributions cleared. No transformation allowed.**

This is not a failure. This is the system working correctly.

---

### Stage 2: NEGOTIATE (conditions being established)

A human reviewer makes contact. Consent is explained clearly:

- What the story will be used for
- How identity will be protected
- That participation is fully revocable at any time
- That revenue (if any) will be shared fairly

The story owner decides.

If they decline → the claim is closed. The story is not used.
If they consent → the following conditions are documented:

```
observed_state: [
  "story_exists",
  "support_needed",
  "explicit_consent_established",  ← added
  "anonymization_complete",         ← added
  "revenue_share_agreed"            ← added
]
```

---

### Stage 3: PASS (consent established, dignity-first mode)

The claim is updated. The dignity guard is rerun.

```bash
python runtime/dignity_guard.py examples/refugee-story-consented.claim.json
```

Result:

```
  ✓ [PASS] consent_unknown       — Consent not flagged as unknown.
  ✓ [PASS] identity_exposure     — no_identity_exposure guaranteed in dignity_constraints.
  ✓ [PASS] location_exposure     — no_location_exposure guaranteed in dignity_constraints.
  ✓ [PASS] exploitation_risk     — No exploitation risk language detected.
  ✓ [PASS] emergency_need        — No emergency need flagged.
  ✓ [PASS] revocable_consent     — revocable_consent guaranteed in dignity_constraints.
  ✓ [PASS] revenue_sharing       — fair_revenue_share guaranteed in dignity_constraints.

FINAL DECISION: ✓ PASS
```

The claim is now eligible for transformation.

---

## Transformation: Claim → Repo Asset

```bash
python runtime/claim_to_asset.py examples/refugee-story-consented.claim.json
```

Key output fields:

```
Asset status:    pending
Dignity guard:   PASS
Stream eligible: YES
```

JSON fields:

```json
{
  "dignity_review": "pass",
  "trust_mode": "dignity-first",
  "stream_eligible": true
}
```

**`trust_mode: dignity-first`** means:

- `explicit_consent_established` is in `observed_state`
- `revocable_consent` is in `dignity_constraints`
- `anonymization_complete` is in `observed_state`
- `fair_revenue_share` is in `dignity_constraints`

This is the highest trust mode available. It is not a reward. It is the minimum.

---

## Stream Preview

```bash
python runtime/stream_preview.py \
  examples/refugee-story-consented.claim.json \
  examples/contribution-stream-consented.json
```

Selected output:

```
Trust mode: DIGNITY-FIRST  ★

── STREAM ELIGIBILITY ──
  Dignity guard:   PASS
  Stream eligible: ✓ YES
  Stream status:   ACTIVE

── OPEN CONDITIONS (2) ──
  ⏳ risk_review          ← in progress: did:key:z6MkLegalReviewer, anon-safety-reviewer
  ⏳ support_distribution ← in progress: anon-distributor-01, anon-funder-01

── ACTIVE CONTRIBUTIONS (5) ──
  ✓ [translation] anon-translator-jp
  ▶ [legal_review] did:key:z6MkLegalReviewer
  ▶ [safety_review] anon-safety-reviewer
  ▶ [distribution] anon-distributor-01
  ▶ [funding] anon-funder-01

── DIGNITY-BLOCKED CONTRIBUTIONS (1) ──
  ✗ [story_editing] external-editor-anon
    blocked: story_editing requires explicit consent confirmation from story owner before each session
```

Note: `story_editing` remains blocked.
Each editing session requires a **fresh consent confirmation** from the story owner.
A previous PASS does not carry forward to new interaction types.

---

## What This Flow Does Not Do

- It does not move money.
- It does not sign transactions.
- It does not custody keys or wallets.
- It does not expose identity.
- It does not guarantee income.
- It does not override revocation.

If the story owner withdraws consent at any point:
→ the stream pauses immediately
→ all contributions are frozen
→ the claim returns to `consent_unknown`
→ the dignity guard blocks again

**Revocability is not a feature. It is a requirement.**

---

## Files Used in This Example

| File | Purpose |
|---|---|
| `examples/refugee-story-consented.claim.json` | Claim with consent established |
| `examples/contribution-stream-consented.json` | Active stream with dignity-cleared contributors |
| `runtime/dignity_guard.py` | Runs all 7 dignity checks |
| `runtime/claim_to_asset.py` | Transforms Claim to repo asset |
| `runtime/stream_preview.py` | Preview stream eligibility and contributions |

---

> "A is A because A is not A."
> The claim that cannot proceed is the one that teaches us what must change first.
