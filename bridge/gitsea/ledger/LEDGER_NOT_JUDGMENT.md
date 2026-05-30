# Ledger Is Not Judgment — Dan-Go Protocol Note

> **"Ledger is not judgment."**
> **"Recognition history is not authority."**

## The Distinction

A **ledger** records what occurred. A **judgment** evaluates whether what
occurred was fair, appropriate, or correct. Dan-Go maintains a ledger.
Dan-Go does not make judgments.

The `judgment: false` invariant on every Phase 15 record makes this explicit.
It is not a disclaimer — it is an architectural property of the ledger.

## What the Ledger Records

The recognition ledger records observable facts:

- Was a contribution candidate created? (`candidate_credit: true/false`)
- Was external credit detected? (`external_credit: true/false`)
- Was reflection memory stored? (`reflection_recorded: true/false`)
- Was an appeal filed? (`appeal_recorded: true/false`)
- What event sequence occurred? (`events: [...]`)
- Is the recognition history complete? (`recognition_history_complete: true/false`)

None of these facts require evaluation. They are either true or false.
The ledger records them without interpreting their significance.

## What Judgment Would Require

For the ledger to constitute judgment, it would need to:
- Classify contributions as deserving or undeserving of credit
- Rank contributors by the quality of their contributions
- Identify parties responsible for the credit gap
- Prescribe outcomes based on the gap

The ledger does none of these things. It records the gap without
attributing cause or responsibility. It records the appeal without
evaluating whether the appeal is justified. It records the history
without declaring a verdict on the history.

## Why Judgment Would Corrupt the Ledger

If the ledger made judgments, it would:
1. Introduce bias into what is meant to be a neutral historical record
2. Create authority Dan-Go explicitly disclaims
3. Produce records that could be weaponised in disputes
4. Undermine the sovereignty of external credit systems

By staying neutral — recording without evaluating — the ledger remains
a trustworthy source of historical fact rather than a source of contested
verdicts.

## Specific Invariants That Preserve Non-Judgment

| Invariant | Effect |
|-----------|--------|
| `judgment: false` | No evaluative classification in any record |
| `authority: none` | No power to impose outcomes based on ledger state |
| `entry_ranks: false` | Ledger entries are not ordered by contribution quality |
| `ledger_forces_recognition: false` | History completeness ≠ recognition compulsion |
| `ledger_issues_credit: false` | The act of recording history ≠ issuing credit |
| `hard_enforcement: false` | No mechanism exists to enforce ledger state externally |

## The Ledger and Future Observers

A neutral ledger has maximal value for future observers. An external system
reading the ledger in the future sees:

- Exactly what happened, in sequence
- No Dan-Go interpretation of whether it was fair
- No Dan-Go prescription of what should happen next

This makes the ledger useful as a data source for any future process —
whether that is GITSEA reassessing credit eligibility, a future governance
mechanism, or a human reviewer. The ledger does not prejudge what
that future process should conclude.

## Protocol Phrase

> "Ledger is not judgment."

This phrase appears in every Phase 15 runtime module. It is a commitment
to neutrality in historical recording — the principle that making
contribution legible does not mean making credit decisions, and that
a complete history can coexist with an external, sovereign recognition
process that Dan-Go does not control.
