# Dan-Go × GITSEA Asset Lifecycle Spec

**GITSEA can make repository contribution economically legible.
Dan-Go makes contribution negotiable before it becomes economic.**

This document specifies the Phase 9 lifecycle extension:

```
Claim
  → Negotiation
  → Contest
  → Reaffirm
  → Contribution
  → Cooperation Signal
  → Asset Signal
  → Economic Value (optional — not set by Dan-Go)
```

No wallet integration. No token transfer. No on-chain execution.
No automatic rewards. No economic scoring. No reputation enforcement.
Only advisory cooperation signals. stdlib only.

---

## 1. Why the Lifecycle Extends Beyond PR Merge

Phase 8 established the path:

```
Claim → Issue → PR → Repository Asset
```

This is necessary but insufficient. A PR merge is evidence, not truth.
A repository asset declaration (`asset.toml`) is intent, not activation.

Phase 9 asks: what happens *between* the claim and the economic event?

Answer:

```
Claim
  → Issue (negotiation invitation)
  → Negotiation (evidence, contest, reaffirm)
  → Contribution (recorded in append-only log)
  → Cooperation Signal (advisory participation legibility)
  → Asset Signal (GITSEA-observable, not GITSEA-activated)
  → Economic Value (optional — GITSEA's decision, not Dan-Go's)
```

**Contribution becomes legible before it becomes valuable.**

Dan-Go makes the negotiation legible. GITSEA may make it economically legible.
These are different operations. Neither is subordinate to the other.

---

## 2. Why Cooperation Is Measured

Cooperation signals are generated because:

1. **Participation patterns reveal negotiation health.** A claim where multiple
   participants contributed evidence, contested positions, and reaffirmed with
   new context is more legible than one with a single submission.

2. **Legibility precedes value.** Before GITSEA can assess stream eligibility,
   the contribution pattern must be readable. Cooperation signals make it
   readable without assigning value.

3. **Dissent is a signal.** Contest events are not failures. They are evidence
   that the negotiation is live. A dissent-free negotiation may indicate
   insufficient scrutiny.

4. **The signal is not final.** Cooperation signals are append-only. A new
   evaluation can be appended as new events occur. No prior signal is deleted.

---

## 3. Why Cooperation Is NOT Reward

The cooperation signal is advisory. It is:

- **Not a reputation score.** Participants are not ranked.
- **Not a reward signal.** No funds are distributed based on it.
- **Not enforced.** No coordinator acts on it.
- **Not permanent.** New events change it. Prior versions are preserved.
- **Not irrevocable.** If new evidence shows the signal was miscalculated,
  a corrected signal is appended.

**Cooperation signals are participation legibility, not authority.**

---

## 4. Why Signals Are Advisory

Every signal produced by Dan-Go carries:

```json
{
  "authority": "none",
  "execution_allowed": false,
  "moves_money": false,
  "hard_enforcement": false,
  "advisory": true,
  "contestable": true,
  "reopenable": true
}
```

This is not a feature flag. It is a protocol invariant.

An advisory signal can be:
- Observed by GITSEA
- Contested by a participant
- Corrected by a plan correction event
- Ignored entirely

It cannot:
- Activate a GITSEA stream
- Distribute tokens
- Enforce a prerequisite
- Penalize a participant

---

## 5. Why Economic Value Is Optional

Dan-Go does not create economic value. Dan-Go records cooperation before
value emerges.

The lifecycle ends at "Asset Signal Generated." What happens after that
is a GITSEA decision, not a Dan-Go decision.

```
Dan-Go territory:    Claim → ... → Asset Signal
GITSEA territory:    Asset Signal → Stream Eligibility → Economic Value
```

These are not the same territory. Dan-Go produces advisory signals at the
boundary. GITSEA acts on those signals — or does not.

**Dan-Go does not cross the boundary. Dan-Go does not push signals to GITSEA.**

---

## 6. Why Negotiation Precedes Economics

If economic value were assigned before negotiation concluded, the incentive
structure would be inverted. Contributors would optimize for the reward
rather than for the reality.

Dan-Go separates negotiation from economics so that:

1. **Evidence is evaluated on its merits**, not its reward potential.
2. **Dissent remains credible** even when it delays economic activation.
3. **Plan corrections are honest** even when they defer a reward.
4. **Participation is genuine** even when no economic outcome is promised.

**Negotiation precedes economics. Evidence precedes reward.**

---

## 7. The Full Lifecycle

| Stage | What happens | Authority | Economic |
|-------|-------------|-----------|----------|
| `claim_created` | Claim enters Dan-Go | none | no |
| `issue_drafted` | Scoped issue generated | none | no |
| `negotiation_opened` | Evidence, contest, reaffirm | none | no |
| `pr_submitted` | PR as evidence contribution | none | no |
| `pr_merged` | Evidence accepted, gitsea_eligible possible | none | no |
| `contribution_recorded` | Recorded in append-only log | none | no |
| `cooperation_signal_generated` | Advisory signal produced | none | no |
| `asset_signal_generated` | GITSEA-observable signal | none | no |
| (Economic activation) | GITSEA's decision | GITSEA | optional |

Dan-Go operates in all rows above the dashed line.
Dan-Go does not operate below it.

---

## 8. Invariants

These must remain true at every stage:

| Field | Value |
|-------|-------|
| `authority` | `none` |
| `execution_allowed` | `false` |
| `moves_money` | `false` |
| `hard_enforcement` | `false` |
| `advisory` | `true` |
| `append_only` | `true` |
| `contestable` | `true` |
| `reopenable` | `true` |
| `economic_value` | `false` (Dan-Go never sets this to true) |

---

## 9. Pipeline

```
scoped-issue-housing-007.output.json
    │
    ├── issue_asset_linker.py
    │     → issue-to-asset.json
    │
    ├── asset_lifecycle.py
    │     → asset-lifecycle-housing-007.json
    │
    ├── contribution_evaluator.py
    │     → contribution-signal.json
    │
    └── negotiation_asset_snapshot.py
          ← issue-001.pr-feedback.json
          ← issue-001.reopen-event.json
          ← issue-001.plan-correction.json
          → negotiation-snapshot.json
```

---

## 10. Absolute Prohibitions

- No wallet integration
- No token transfer
- No on-chain execution
- No automatic rewards
- No economic scoring
- No reputation enforcement
- No GITSEA API calls
- No network access
- No external libraries (stdlib only)
- No deletion of prior events
- No hard enforcement

---

## 11. Related Specs

- `bridge/gitsea/lifecycle/CONTRIBUTION_SIGNAL_SPEC.md` — cooperation signal detail
- `bridge/gitsea/lifecycle/NEGOTIATION_TO_ASSET_FLOW.md` — flow diagrams
- `bridge/gitsea/DANGO_GITSEA_INTEGRATION_SPEC.md` — Phase 8 integration spec
- `bridge/gitlawb/PR_NEGOTIATION_REOPEN_SPEC.md` — PR negotiation lifecycle

---

*dango-gitsea-bridge · authority: none · advisory · append-only · stdlib only*
*Contribution becomes legible before it becomes valuable.*
*GITSEA can make repository contribution economically legible.*
*Dan-Go makes contribution negotiable before it becomes economic.*
