# dango-gitsea-bridge

> 「AはAである」を超越し、「Aが非AのゆえにAである」へ。
> Transcending "A is A" to "A is A because A is not A."

---

dango-gitsea-bridge is not a financial product.
It is a translation layer between Dan-Go Claims and GITSEA-style repo assets,
contribution streams, and agent credit records.

Dan-Go asks:
"What would need to change for this impossible claim to become real?"

GITSEA may provide:
- repository identity
- contribution accounting
- streamable value
- credit history
- agent-to-agent economic coordination

This bridge does not move money.
It does not sign transactions.
It does not custody keys.
It only models the transformation.

> **Note:** GITSEA's implementation status is unverified.
> This bridge treats GITSEA as a hypothetical financial layer.
> Even if GITSEA is abandoned or fraudulent, this bridge can be forked
> to connect Dan-Go with any equivalent protocol.
> Forks, objections, and counterclaims are valid participation.

---

## Core Loop

```
Claim → Negotiation → Contribution → Execution → Reality Feedback
         ↓
    [dango-gitsea-bridge]
         ↓
  Repo Asset → Contribution Stream → Agent Credit Record
```

---

## What this bridge does

| Input | Output |
|---|---|
| Dan-Go Claim JSON | GITSEA-style repo asset |
| Contribution list | Streamable contribution ledger |
| Dignity constraints | Dignity guard decision (pass / block / escalate) |
| Claim + contributions + guard | Stream preview report |

---

## Quick Start

```bash
# Model a claim as a repo asset
python runtime/claim_to_asset.py examples/refugee-story.claim.json

# Check dignity constraints
python runtime/dignity_guard.py examples/refugee-story.claim.json

# Preview stream eligibility
python runtime/stream_preview.py examples/refugee-story.claim.json examples/contribution-stream.json
```

---

## Structure

```
dango-gitsea-bridge/
├── README.md                    — This file
├── DANGO_GITSEA_THESIS.md       — Why this bridge exists
├── CLAIM_TO_REPO_ASSET.md       — How Claims become repo assets
├── CONTRIBUTION_STREAM_SPEC.md  — How contributions become streams
├── REFUGEE_STORY_STREAM_ETHICS.md — Ethics of story-based streams
├── DIGNITY_GUARD.md             — The guard layer
├── RISK_ASSESSMENT.md           — Known risks and limitations
├── examples/                    — Sample JSON files
└── runtime/                     — Minimum viable Python implementation
```

---

## Quick Start — Consent-Established (PASS) Flow

```bash
# Run dignity guard on a consent-established claim
python runtime/dignity_guard.py examples/refugee-story-consented.claim.json

# Transform claim to repo asset — expect trust_mode: dignity-first, stream_eligible: true
python runtime/claim_to_asset.py examples/refugee-story-consented.claim.json

# Preview the active contribution stream
python runtime/stream_preview.py \
  examples/refugee-story-consented.claim.json \
  examples/contribution-stream-consented.json
```

See `PASS_FLOW_EXAMPLE.md` for the full annotated walkthrough.

---

## Dignity-first execution

Dan-Go does not ask: "Can this be monetized?"
Dan-Go asks: "Can this become real without violating dignity?"

A stream is allowed only after:

- explicit, informed, revocable consent
- anonymization complete (identity not exposed)
- risk review passed
- fair participation and revenue share guaranteed
- every condition acknowledged — not assumed

When consent is unknown → stream is **blocked**. No exceptions.
When consent is established → stream enters `dignity-first` trust mode.

`dignity-first` is not a reward. It is the minimum required to proceed.

---

## Principles

1. No financial product. No investment solicitation.
2. No keys, no signatures, no transactions.
3. Dignity before efficiency. Always.
4. GITSEA is hypothetical. The bridge is real.
5. If GITSEA fails, fork to another layer.
6. Consent, anonymity, revocability — explicit or blocked.
7. Do not violate the dignity of another.
