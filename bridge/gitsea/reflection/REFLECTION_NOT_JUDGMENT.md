# Reflection Is Not Judgment — Dan-Go Protocol Note

> **"Reflection is not judgment."**
> **"Unrecognized contribution is still observable."**

## The Distinction

In the Dan-Go protocol, **reflecting** on a credit outcome is not the
same as **judging** that outcome.

Dan-Go reflects:
- What contributions occurred (Phase 11)
- Whether external credit was observed (Phase 12)
- What the gap between candidates and external credit looks like (Phase 12)
- What the contribution lifecycle looked like end-to-end (Phase 13)

Dan-Go does not judge:
- Whether the gap is fair
- Whether external credit was deserved
- Whether contributors were treated correctly
- Whether external systems performed adequately
- Whether any party owes anything to any other party

## What Reflection Means

Reflection in Phase 13 means: Dan-Go looks back at the full lifecycle
of a contribution candidate and stores a permanent, observable record
of what was seen. That record includes:

- The candidate that was created
- The external check that was performed
- The absence of external credit that was observed
- The gap that was documented
- The reflection that is now stored

Reflection is retrospective observation. It is append-only. It is advisory.
It changes nothing about external systems. It assigns no responsibility.

## What Judgment Would Mean (and Why Dan-Go Doesn't Do It)

Judgment would mean:
- Concluding that a gap was caused by negligence or error
- Ranking contributors based on credit outcomes
- Penalising contributors whose contributions were not credited
- Penalising external systems for not issuing credit
- Declaring some contributions "real" and others not

Dan-Go does none of these things. All of them would require authority that
Dan-Go explicitly disclaims: `authority: none`.

To judge would be to claim that Dan-Go knows why a gap exists and what
should be done about it. Dan-Go knows only what it observed. It records
what it observed. Nothing more.

## Why This Matters

Contribution memory has value independent of credit outcomes. A system
that only records credited contributions has incomplete memory. A system
that judges uncredited contributions adds noise and distortion.

The right role for Dan-Go is to record accurately and without judgment,
so that:

1. Contributions are always observable, even without credit
2. Future observers can see the full picture without distortion
3. External systems retain sovereignty over their own decisions
4. Contributors are not penalised by the protocol for external outcomes
   outside their control

## The `reflection_only` Invariant

Every Phase 13 record carries `reflection_only: true`. This means:

- The record is read-only with respect to the external world
- It does not modify, request, or trigger anything external
- It is advisory input into future observation, nothing more
- It cannot be used to compel action from any party

`reflection_only: true` and `authority: none` together mean that
Phase 13 records are observations — permanent, accurate, append-only
observations — with no power to change anything except the legibility
of what happened.

## Protocol Phrase

> "Reflection is not judgment."

This phrase appears in every Phase 13 runtime module. It is a reminder
that recording a gap is not an indictment, that observing absence is
not assigning blame, and that making contribution legible is the goal —
not evaluating economic outcomes.
