# PASS Flow Example — Consent Established

> A worked example of the dignity guard moving from BLOCK to PASS.

## Full State Transition (Su-table Events)

```
BLOCK                   ← dignity_guard: consent_unknown
↓
  [claim_created]       → claims.jsonl
  [objection]           → negotiations.jsonl  (legal ownership unresolved)
↓
NEGOTIATE
↓
  [amendment]           → negotiations.jsonl  (add ownership requirement)
  [support]             → negotiations.jsonl  (amendment accepted)
  [contribution_offer]  → contributions.jsonl
  [contribution_accepted] → contributions.jsonl
↓
AMENDMENT EVENT ✓ → observed_state updated: explicit_consent_established
↓
CONTRIBUTION EVENT ✓ → legal_ownership_confirmed met
↓
PASS                    ← dignity_guard: all 7 checks pass
↓
  [execution_started]   → executions.jsonl
↓
EXECUTION
↓
  [reality_feedback]    → reality_feedback.jsonl  (result: partial_success)
↓
REALITY FEEDBACK ◑
```

Every arrow in this diagram is a permanent record in the su-table.
Nothing is deleted. Everything is queryable.

```bash
python runtime/sutable_query.py --timeline housing-001
```

---

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

## Negotiation Graph

The full flow above — from BLOCK to REALITY FEEDBACK —
is recorded in the su-table and can be rendered as a graph:

```bash
# Text (terminal)
python runtime/graph_export.py --claim-id housing-001 --format text

# Mermaid (paste into mermaid.live)
python runtime/graph_export.py --claim-id housing-001 --format mermaid

# HTML preview (open in browser — no external dependencies)
python runtime/graph_export.py --claim-id housing-001 \
  --format html --output examples/housing-001.graph.html
open examples/housing-001.graph.html
```

The HTML preview includes a **Copy** button for the Mermaid source.
Paste it into [mermaid.live](https://mermaid.live) to see the rendered graph.
The HTML itself loads no external scripts — it is fully local.

Mermaid output (render at mermaid.live or embed in GitHub markdown):

```mermaid
flowchart TD
  classDef claim          fill:#dbeafe,stroke:#2563eb,color:#1e3a5f
  classDef objection      fill:#ffedd5,stroke:#ea580c,color:#431407
  classDef amendment      fill:#ede9fe,stroke:#7c3aed,color:#2e1065
  classDef support        fill:#dcfce7,stroke:#16a34a,color:#14532d
  classDef contrib        fill:#f5f3ff,stroke:#8b5cf6,color:#2e1065
  classDef correction     fill:#f3f4f6,stroke:#6b7280,color:#111827
  classDef execution      fill:#ede7f6,stroke:#7c3aed,color:#2e1065
  classDef feedbackPartial fill:#fef9c3,stroke:#ca8a04,color:#422006

  n0["Claim: A vacant house can become a shared…"]:::claim
  n1{"Objection: Legal ownership unresolved"}:::objection
  n2("Amendment: Require owner consent"):::amendment
  n3["Support: Amendment accepted ✓"]:::support
  n4[/"Offer: legal_review"/]:::contrib
  n5[/"Accepted: legal_review"/]:::contrib
  n6(["Execution Started"]):::execution
  n7(["Feedback: Partial Success"]):::feedbackPartial
  n8[>"↩ Correction: Wrong statute cited"]:::correction

  n0 --> n1
  n1 --> n2
  n2 --> n3
  n3 --> n4
  n4 --> n5
  n5 --> n6
  n6 --> n7
  n7 --> n8
  n1 -.-> |corrects| n8
```

Key visual conventions:
- `{"…"}` hex nodes = objection / escalation (conflict)
- `("…")` round nodes = amendment (modification)
- `[/"…"/]` parallelogram = contribution (input flow)
- `(["…"])` stadium = execution / feedback (action)
- `-.->` dashed edge = correction (original preserved, not deleted)

---

## Files Used in This Example

| File | Purpose |
|---|---|
| `examples/refugee-story-consented.claim.json` | Claim with consent established |
| `examples/contribution-stream-consented.json` | Active stream with dignity-cleared contributors |
| `examples/housing-001.graph.mmd` | Negotiation graph in Mermaid format |
| `runtime/dignity_guard.py` | Runs all 7 dignity checks |
| `runtime/claim_to_asset.py` | Transforms Claim to repo asset |
| `runtime/stream_preview.py` | Preview stream eligibility and contributions |
| `runtime/negotiation_graph.py` | Builds graph dict from su-table |
| `runtime/graph_export.py` | Exports graph as mermaid or text |

---

> "A is A because A is not A."
> The claim that cannot proceed is the one that teaches us what must change first.
