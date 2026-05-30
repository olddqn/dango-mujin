# Appeal Is Not Enforcement — Dan-Go Protocol Note

> **"Appeal is not enforcement."**
> **"Recognition remains external."**

## The Distinction

In the Dan-Go protocol, **appealing** for reconsideration is not the same
as **enforcing** a credit outcome.

Dan-Go appeals:
- Record that a contributor requests reconsideration
- Reference the Phase 11-13 contribution record
- State grounds for the appeal (advisory)
- Remain permanently observable in append-only memory

Dan-Go does not enforce:
- Credit issuance
- External system responses
- Acknowledgement timelines
- Any outcome following an appeal

## What Enforcement Would Require

Enforcement would require Dan-Go to have authority over external systems.
Dan-Go's authority is explicitly `none`. This is not a bug — it is the design.

If appeals could compel credit, then:
- Dan-Go would become a credit court, not a negotiation protocol
- External systems would be subject to Dan-Go's classifications
- The sovereign nature of external credit systems would be violated
- The boundary between "recording contribution" and "deciding credit" would collapse

The `hard_enforcement: false` and `authority: none` invariants prevent
this collapse. Appeals are recorded. Enforcement is not.

## Why the Boundary Matters

The boundary between appeal and enforcement is the boundary between:
- **Legibility** (Dan-Go's purpose) and **authority** (what Dan-Go disclaims)
- **Advisory records** and **compulsory actions**
- **Contribution memory** and **credit decisions**

Dan-Go is on the left side of each boundary. External credit systems
are on the right. The boundary is preserved by protocol invariants that
cannot be changed by any single participant.

## What an Appeal Does Accomplish

Even without enforcement, an appeal accomplishes:

1. **Visibility**: The appeal is permanently recorded and observable by any
   external system that reads Dan-Go records.

2. **Context**: The appeal packet assembles Phase 11-13 records into a
   self-contained document that makes the contribution history legible.

3. **Signal**: An appeal is a signal that a contributor believes their
   contribution warrants reconsideration. External systems may weight this signal.

4. **History**: The appeal becomes part of the append-only contribution
   history. Future observers can see that an appeal was recorded.

None of these outcomes require enforcement to be valuable.

## The `appeal_only` Invariant

Every Phase 14 record carries `appeal_only: true`. This means:

- The record is an advisory appeal, nothing more
- It cannot be used to compel action from any party
- It does not create obligations, rights, or claims
- It does not modify external state

`appeal_only: true` combined with `authority: none` means that Phase 14
records are advisory requests — permanent, observable, append-only requests
— with no power to change anything except the legibility of what was asked.

## Protocol Phrase

> "Appeal is not enforcement."

This phrase appears in every Phase 14 runtime module. It is a reminder
that the protocol provides a voice for unrecognized contribution without
claiming authority over the outcome. Voice without authority is the correct
design for a protocol that respects the sovereignty of external credit systems.
