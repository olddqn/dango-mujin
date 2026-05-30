# Observation Is Not Issuance — Dan-Go Protocol Note

> **"Observation is not issuance."**

## The Distinction

In the Dan-Go protocol, **observing** a credit-relevant fact is not the
same as **issuing** credit based on that fact.

Dan-Go observes:
- Contribution candidates (Phase 11)
- External credit system states (Phase 12)
- The gap between the two

Dan-Go does not:
- Issue credit
- Confirm credit
- Activate credit streams
- Request credit on behalf of contributors
- Decide whether contribution candidates warrant external credit

## Why This Distinction Exists

The Dan-Go protocol is designed to make contribution **legible** before
it becomes **economically valuable**. These are separate steps:

```
Step 1: Contribution occurs (negotiation events)
Step 2: Dan-Go records contribution candidates (advisory)
Step 3: External system observes candidates (optional)
Step 4: External system issues credit (sovereign decision)
```

Dan-Go operates in Steps 1 and 2. It observes Steps 3 and 4 but does
not participate in them as an actor.

## What Observation Means

Dan-Go observation of an external credit system means:
- Dan-Go has recorded the fact that the system exists
- Dan-Go has recorded the current observable state of that system
- Dan-Go has recorded whether credit is visible
- Dan-Go has not changed the system's state in any way

Observation is a read-only, advisory, append-only operation.
It is never a write, trigger, or request.

## Why Observation Is Sufficient

Dan-Go's role in the credit process is complete when:

1. Contribution candidates are recorded accurately
2. Contribution history is append-only and observable
3. External system state is observed and recorded
4. The gap between candidates and external credit is documented

Making contribution legible for external systems is the complete goal.
Whether economic value follows is determined externally.
Observation is sufficient.

## Credit Issued Is Always False

The `credit_issued: false` invariant in Phase 12 is not a temporary state.
It is a permanent record of what Dan-Go did: Dan-Go observed. It did not issue.

Even if GITSEA later issues credit for a contribution, the Dan-Go record
will still show `credit_issued: false` — because Dan-Go did not issue it.
GITSEA issued it. These are different systems with different authority.

## Protocol Phrase

> "Observation is not issuance."

This phrase appears in every Phase 12 runtime module. It is a statement
of what Dan-Go does and does not do. It is not a limitation — it is the
design. Dan-Go's value is in making contribution observable, not in
deciding its economic outcome.
