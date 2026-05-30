# Recognition History Is Not Authority — Dan-Go Protocol Note

> **"Recognition history is not authority."**
> **"Ledger is not judgment."**

## The Distinction

**Recognition history** is the accumulated record of what occurred across
the Dan-Go contribution→recognition lifecycle (Phases 11–14). It is a fact
about the past.

**Authority** is the power to compel future outcomes. Dan-Go has none.

Accumulating a complete, accurate recognition history does not confer
authority over what recognition should occur next. The `authority: none`
invariant ensures this separation is permanent and unconditional.

## Why History Accumulates Without Authority

The Dan-Go protocol is designed to make contribution legible. Legibility
requires a record. A record accumulates over time. But accumulation of
records does not accumulate authority.

Consider the full Phase 11–15 chain:
1. Phase 11: contribution candidate recorded ← advisory
2. Phase 12: external credit observed (not detected) ← advisory
3. Phase 13: reflection memory stored ← advisory
4. Phase 14: recognition appeal filed ← advisory
5. Phase 15: recognition ledger complete ← advisory

At every step, the record is advisory. The ledger being complete does
not change the advisory nature of the underlying records. History is
complete. Authority is still none.

## What History Does Accomplish (Without Authority)

Even without authority, a complete recognition history:

1. **Maximises observability**: Any future observer — human or system —
   can read the complete Phase 11–15 record and understand exactly what
   occurred.

2. **Enables informed decisions by sovereign systems**: GITSEA or other
   external systems can read the recognition history and use it as input
   to their own decisions. They are not bound by it, but they can be
   informed by it.

3. **Preserves contributor participation**: The fact that a contributor
   filed an appeal, had their contribution reflected, and is in the ledger
   is a permanent observable fact, regardless of external credit outcomes.

4. **Supports future phases**: If a Phase 16 or later process wants to
   build on the recognition history, it finds a clean, complete, neutral
   record — not a partially-recorded or judgment-laden one.

## The `recognition_history_complete: true` Field

A ledger entry with `recognition_history_complete: true` means:
- Phase 11 record exists (candidate)
- Phase 12 record exists (external credit observation)
- Phase 13 record exists (reflection)
- Phase 14 record exists (appeal)
- Phase 15 entry exists (ledger)

It does NOT mean:
- External credit was issued
- The contribution was recognised by any external system
- Any obligation exists for any party
- Dan-Go has authority over future credit decisions

`recognition_history_complete: true` is a statement about the completeness
of the Dan-Go record, not about the completeness of the credit process.

## Why the Boundary Is Permanent

The boundary between history and authority is not a temporary phase
limitation. It reflects the fundamental design of Dan-Go as an advisory
protocol with no enforcement mechanism.

No future phase of Dan-Go will:
- Grant Dan-Go authority over external credit systems
- Make recognition history binding on external systems
- Turn ledger completeness into a credit obligation

The `authority: none` invariant is unconditional. It applies to every
record in every phase. Recognition history is as complete as it will
ever be. Authority remains as absent as it has always been.

## Protocol Phrase

> "Recognition history is not authority."

This phrase appears in every Phase 15 runtime module. It is the terminal
statement of what Dan-Go is: a system that makes contribution legible,
keeps complete records, and carries no authority over what those records
mean for external credit decisions. The protocol is complete when the
history is complete. Recognition is external.
