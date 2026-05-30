# Cooperation Treasury Bridge Spec

**Signal is not reward.**

**Dan-Go observes treasury context; it does not operate the treasury.**

This document specifies how Phase 9 cooperation signals are connected
to Phase 10 treasury visibility — without converting signals into rewards.

---

## 1. The Problem: Signal Without Context

Phase 9 generates advisory cooperation signals:

```json
{
  "cooperation_signal": 0.88,
  "dissent_present": true,
  "participant_count": 3,
  "event_count": 6
}
```

These signals exist in isolation. A participant reviewing them cannot see:
- Whether the repository has an on-chain presence
- Whether a treasury exists
- What the relationship between cooperation and economic context is

Treasury visibility bridges this gap without creating a reward relationship.

---

## 2. What the Bridge Does

The `cooperation_treasury_bridge.py` module:

1. Reads a Phase 9 cooperation signal (`contribution-signal.json`)
2. Attaches the observed RepoVault address for context
3. Records that `recommended_allocation: null` (always)
4. Asserts that `signal_becomes_reward: false`
5. Outputs a bridge record — advisory, append-only

The bridge makes the connection legible. It does not make it economic.

---

## 3. Why Signal Must Not Become Reward

If cooperation signals automatically triggered reward allocation:

1. **Gaming incentive.** Participants would optimize for the signal,
   not for the negotiation. Contest events (healthy dissent) might be
   suppressed to avoid reducing the signal.

2. **Authority creation.** Whoever computes the signal would become a
   de facto authority over reward distribution. Dan-Go has no such authority.

3. **Irreversibility.** Rewards, once distributed on-chain, cannot be
   undone. Dan-Go's negotiation is always reopenable. Economic finality
   and negotiation reopenability are incompatible.

4. **Consent violation.** Participants may not consent to having their
   cooperation assessed for economic outcomes. The dignity guard requires
   explicit consent for such assessments.

**Signal is not reward.** The bridge records this as a protocol invariant.

---

## 4. The Bridge Record Fields

```json
{
  "bridge_type":             "cooperation_treasury_bridge",
  "issue_id":                1,
  "claim_id":                "housing-007",
  "cooperation_signal":      0.88,
  "dissent_present":         true,
  "participants":            ["alice", "bob", "carol"],
  "participant_count":       3,
  "event_count":             6,

  "treasury_address":        "0x3F9c96A429697B458Fe0a16502A050E5AB50bB00",
  "repo_id":                 "B93829F8...",
  "treasury_visible":        true,
  "treasury_linked":         true,
  "chain":                   "Base",

  "recommended_allocation":  null,
  "economic_action":         false,
  "signal_becomes_reward":   false,
  "treasury_operated":       false,

  "moves_money":             false,
  "execution_allowed":       false,
  "advisory":                true,
  "authority":               "none",
  "contestable":             true,
  "reopenable":              true,

  "signal_note":             "Signal is not reward.",
  "treasury_note":           "Dan-Go observes treasury context; ..."
}
```

Key invariants in the record:
- `recommended_allocation: null` — always, unconditionally
- `economic_action: false` — always
- `signal_becomes_reward: false` — always
- `treasury_operated: false` — always

---

## 5. What GITSEA May Do With This Context

Dan-Go does not push bridge records to GITSEA. GITSEA may observe them
from the repository.

If GITSEA observes:
- A cooperation signal of 0.88 for housing-007
- A RepoVault linked to olddqn/dango-mujin
- A RepoLinked event on Base

GITSEA may use this context when assessing stream eligibility.
That is a GITSEA decision, not a Dan-Go action.

Dan-Go does not predict, guarantee, or optimize for GITSEA stream activation.

---

## 6. Contest Events and Signal Integrity

The cooperation signal includes `dissent_present: true` when contest events occurred.
The bridge record preserves this.

A cooperation signal with dissent is more trustworthy, not less. It indicates
that the negotiation was live and that different perspectives were recorded.

When GITSEA observes a bridge record, a `dissent_present: true` signal should
be interpreted as negotiation health — not as conflict that reduces value.

---

## 7. Append-Only Bridge Records

Each bridge record is a point-in-time snapshot. If the cooperation signal
changes (e.g., new events are observed), a new bridge record is generated.
Prior records are preserved.

This matches the Dan-Go append-only principle:
- No prior record is deleted
- Each new record adds to the audit trail
- The treasury address does not change (immutable on-chain)
- The cooperation signal may change (contestable, reopenable)

---

## 8. Invariants

| Field | Value |
|-------|-------|
| `recommended_allocation` | `null` — always |
| `signal_becomes_reward` | `false` — always |
| `economic_action` | `false` — always |
| `treasury_operated` | `false` — always |
| `moves_money` | `false` — always |
| `execution_allowed` | `false` — always |
| `advisory` | `true` — always |
| `authority` | `none` — always |

---

*authority: none · advisory · append-only · stdlib only*
*Signal is not reward.*
*Dan-Go observes treasury context; it does not operate the treasury.*
