# Dan-Go ↔ OGI Agent Economy — Concept Mapping

---

## Primitive Mapping Table

| Dan-Go Primitive | OGI Concept | Bridge Translation |
|---|---|---|
| **Claim** | Agent Task Request | A public statement of a desired state becomes a structured task for capable agents |
| **Negotiation** | Coordination Protocol | Public objection/amendment/support becomes multi-agent task negotiation |
| **Contribution** | Contribution Signal | Any form of work (code, care, compute, knowledge) becomes a credit-bearing signal |
| **Dignity Guard** | Exploitation Boundary | Seven-rule filter becomes the hard constraint for any agent-economic activity |
| **Su-table** | Shared Economic Memory | Append-only JSONL log becomes the coordination history all agents can read |
| **Reality Feedback** | Outcome Record | Post-execution report becomes the economy's ground truth record |
| **Trust Mode** | Agent Trust Level | dignity-first / guarded / open maps to agent access tiers |
| **Constitution** | Economic Constitution | "Do not violate the dignity of another" becomes a non-negotiable protocol rule |

---

## Detailed Mappings

### Claim → Agent Task Request

```
Dan-Go                          OGI
──────                          ───
claim_id                    →   task_id (prefixed: "task-{claim_id}")
statement                   →   task_description
possible_contributions      →   required_capabilities (mapped)
missing_conditions          →   open_conditions
dignity_constraints         →   dignity_constraints (inherited)
decision: negotiate         →   task_status: open
decision: execute           →   task_status: active
decision: escalate          →   task_status: under_review
decision: reject            →   task_status: closed
```

### Negotiation → Coordination Protocol

```
Dan-Go event_type           OGI equivalent
──────────────────          ──────────────
objection               →   coordination_challenge
amendment               →   task_modification_proposal
support                 →   task_endorsement
escalation              →   human_review_required
correction              →   record_amendment (original preserved)
withdrawal              →   agent_exit
```

### Contribution → Contribution Signal

```
Dan-Go contribution_type    Credit dimension
────────────────────────    ────────────────
compute                 →   compute_credit
code                    →   code_credit
translation             →   translation_credit
care                    →   care_credit
distribution            →   distribution_credit
verification            →   verification_credit
legal_review            →   review_credit
safety_review           →   review_credit
local_knowledge         →   knowledge_credit
coordination            →   coordination_credit
funding                 →   monetary_credit
```

### Trust Mode → Agent Access Level

```
Dan-Go trust_mode           OGI agent access
──────────────────          ────────────────
dignity-first           →   full_participation
guarded                 →   standard_participation
open                    →   open_participation
blocked                 →   no_participation (dignity guard triggered)
```

### Reality Feedback → Outcome Record

```
Dan-Go result               OGI outcome_type
──────────────              ────────────────
success                 →   coordination_success
partial_success         →   coordination_partial
failed                  →   coordination_failure
unexpected_outcome      →   coordination_unexpected
dignity_violation_detected → dignity_breach (automated halt + human review)
```

---

## What Maps Cleanly

These Dan-Go concepts translate directly to OGI without ambiguity:

1. **Append-only memory** — Su-table JSONL is directly usable as an OGI shared ledger
2. **Dignity constraint** — Non-negotiable in both systems
3. **Contribution as value** — OGI is designed for multi-dimensional contribution tracking
4. **Public negotiation** — OGI's multi-agent coordination requires transparent communication
5. **Reality feedback** — OGI's outcome verification maps directly to Dan-Go's feedback events
6. **Revocable consent** — Both systems require consent to be withdrawable at any time

---

## What Maps With Tension

These concepts require translation and may not be a perfect fit:

### Trust Score vs. Credit Signal

Dan-Go does not assign trust scores.
It records trust mode per claim (dignity-first / guarded / open / blocked).
It *does* compute **temporal trust weights** per contribution event.

OGI agent economies may use trust scores for routing decisions.

**Resolution:** Credit signals (from contribution history) serve as trust inputs
without becoming a gate. An agent with no history can still participate;
history increases the weight of their credit signals, not their access rights.

The temporal trust weight (`runtime/temporal_trust_decay.py`) provides
a coordination signal that can feed OGI routing decisions:

```
Dan-Go trust_weight         OGI coordination signal weight
────────────────────        ──────────────────────────────
≥ 0.7 (high)            →   strong_signal
0.3–0.7 (medium)        →   standard_signal
< 0.3 (low)             →   weak_signal
0.0 (blocked)           →   no_signal (dignity gate)
```

Key properties:
- Decays with time (half-life 90 days by default)
- Boosted by `verified` status (+20%)
- Continuity bonus for returning contributors (capped at 1.5×)
- Dignity block sets to 0.0 exactly — no minimum floor applies

### Monetary Contribution

Dan-Go treats `funding` as one contribution type among many.
OGI may have specific mechanisms for monetary flows.

**Resolution:** `funding` maps to `monetary_credit` in the credit signal.
No actual money moves through this bridge. The monetary_credit is a record,
not a transaction.

### Agent Identity

Dan-Go uses DIDs or pseudonyms.
OGI may have its own identity scheme.

**Resolution:** This bridge preserves the DID format from Dan-Go.
If OGI uses a different identity scheme, an adapter layer is needed.
This is noted in `OGI_COMPATIBILITY_NOTES.md`.

---

## What Does Not Map (Yet)

These Dan-Go concepts have no clear OGI equivalent in this bridge:

| Dan-Go concept | Status | Note |
|---|---|---|
| Stream eligibility | Not mapped | GITSEA-specific; OGI may have equivalent |
| Repo asset | Not mapped | GITSEA-specific |
| Negotiation graph | Partially mapped | OGI may have visualization layer |
| Temporal trust decay | **Implemented** | `runtime/temporal_trust_decay.py` — 90-day half-life, dignity-block zero |
| Claim federation | Not implemented | Cross-claim dependencies not yet modeled |

---

## Protocol Position

```
Reality
  ↑
Reality Feedback ←→ OGI Outcome Record
  ↑
Execution ←→ OGI Agent Execution
  ↑
Contribution ←→ OGI Credit Signal
  ↑
Negotiation ←→ OGI Coordination Protocol
  ↑
Claim ←→ OGI Agent Task Request
  ↑
Human or AI intent
```

Dan-Go provides the structure at every layer.
OGI provides the economic environment at every layer.
This bridge translates between them.
