# Unrecognized Contribution Spec — Dan-Go / GITSEA (Phase 13)

> **"Unrecognized contribution is still observable."**
> **"Reflection is not judgment."**

## What Is an Unrecognized Contribution?

An **unrecognized contribution** is a Dan-Go contribution candidate that:

1. Met the credit-eligibility threshold in Phase 11 (`candidate_credit: true`)
2. Was observed in Phase 12 external credit check
3. Was not found in any external credit system during that observation

"Unrecognized" means: present in Dan-Go records, absent in external credit
records at the time of observation. Nothing more.

## What Unrecognized Does NOT Mean

| Claim | True? |
|-------|-------|
| The contribution was poor quality | No — Dan-Go does not evaluate quality |
| The contributor did something wrong | No — Dan-Go does not assign blame |
| The external system failed | No — external systems are sovereign |
| The contribution is lost | No — it is observable here |
| The gap must be closed | No — gaps are not demands |
| This is a protocol error | No — gaps are expected |
| Dan-Go should escalate | No — Dan-Go observes only |

## Invariants on Every Unrecognized Contribution Record

```json
{
  "recognized":          false,
  "is_failure":          false,
  "is_accusation":       false,
  "contribution_lost":   false,
  "candidate_credit":    true,
  "external_credit":     false,
  "credit_issued":       false,
  "moves_money":         false,
  "execution_allowed":   false,
  "advisory":            true,
  "reflection_only":     true,
  "authority":           "none"
}
```

`is_accusation: false` is a **permanent protocol invariant**. Unrecognized
contribution records are observation facts, not dispute records.

## Why Missing GITSEA Credit Is Not Failure

GITSEA credit decisions are sovereign. GITSEA may:

- Issue credit at any time on its own schedule
- Apply eligibility criteria beyond what Dan-Go tracks
- Batch credit across multiple claims or periods
- Issue credit through mechanisms Dan-Go does not observe
- Choose not to issue credit at all

None of these outcomes represent a Dan-Go failure, a contributor failure,
or a negotiation failure. The Dan-Go protocol's job is to record contributions
accurately and make them observable. That job is complete when the record
exists. Economic outcome is external.

## Why Dan-Go Records Gaps

Dan-Go records unrecognized contributions because:

1. **Legibility**: The contribution exists and should be observable, regardless
   of external credit state.

2. **History**: Future credit systems may observe historical contribution records.
   Having a permanent, accurate record maximises future observability.

3. **Protocol completeness**: A protocol that only records credited contributions
   would be incomplete. The full picture includes what happened AND what was credited.

4. **Non-judgment**: Recording a gap without judging it is the only way to
   preserve external system sovereignty while also preserving contribution memory.

## Why Gaps Are Not Accusations

The `is_accusation: false` invariant exists because the record must not be
misread as a complaint about GITSEA, contributors, or maintainers.

Unrecognized contribution records:
- Do not allege wrongdoing by any party
- Do not create obligations for any party
- Do not generate claims or demands
- Do not contradict external credit decisions
- Do not suggest external systems erred

They simply record: this contribution existed; external credit was not detected.
That is the complete semantic content of an unrecognized contribution record.

## External Systems Remain Sovereign

Recording an unrecognized contribution does not:
- Notify GITSEA
- Request credit from GITSEA
- Create a dispute with GITSEA
- Override GITSEA decisions

GITSEA may observe these records at any time and may use them in future
eligibility decisions. Dan-Go does not push, request, or activate this
process. Observation and memory are sufficient.
