# Relief Is Not Proof — Dan-Go Protocol Note

> **"Relief is not proof."**
> **"Outcome is not judgment."**
> **"Care memory is not control."**

## The Distinction

**Relief** is the observable fact of assistance having reached a person or
household in need. A meal delivered. Shelter accepted. Supplies received.
These are events that can be observed and recorded.

**Proof** is a certified claim about what occurred — a claim strong enough
to be used as evidence in external processes: to prove a programme worked,
to demonstrate that a response was adequate, to show that a displaced
person was "handled." Dan-Go's relief records are not proof. The
`relief_is_proof: false` invariant on every relief case record is permanent.

## Why Relief Cannot Be Proof

Several reasons converge on this conclusion:

1. **Observation is not verification.** Dan-Go records what participants
   observed. Observers can be mistaken. What appeared to be a completed
   food delivery may have been partial. What appeared to be a successful
   shelter placement may have broken down the next day. The observation
   record is accurate about what was observed, not about objective reality.

2. **Relief is not resolution.** A meal addresses hunger in this moment.
   It does not resolve food insecurity. Shelter for five days does not
   resolve homelessness. Recording "shelter_was_accepted, outcome: full"
   does not mean the underlying need no longer exists. Relief is a moment
   in a longer situation. Proof claims would freeze a moment as a verdict.

3. **Proof would corrupt the record's purpose.** Dan-Go records relief
   case memory so that communities can see their own care history —
   to know what was attempted, what was observed, what remains open.
   If the record became proof, it would be used by external parties to
   certify adequacy, deny further support, or close cases that should
   remain open. The record exists for the community, not for external
   certification.

4. **Refugee relief is especially sensitive.** Records of relief for
   displaced persons can be weaponised — as evidence that someone has
   "been helped enough," as documentation that can be used in immigration
   or housing proceedings, as a basis for denying further support.
   `relief_is_proof: false` ensures that Dan-Go records cannot be
   legitimately used in this way.

## What Relief Records Accomplish (Without Proof)

Even without functioning as proof, a complete relief case record:

1. **Makes care history legible.** The community can see what was requested,
   what was offered, what route was suggested, what case was observed, and
   what outcome was noted. This is community memory — valuable for
   understanding patterns of need and coordination.

2. **Supports future routing.** If a case remains unresolved or is reopened,
   the Phase 18 record provides context for Phase 17 route suggestions in
   the future. History informs coordination without commanding it.

3. **Preserves the reopenable quality of care.** A relief case with
   `outcome_status: full` still carries `reopenable: true`. The community
   can append new observations. The situation can change. The record
   does not close the case — it records the most recent observation.

## Protocol Phrase

> "Relief is not proof."

This phrase appears in every Phase 18 runtime module. It is the boundary
between observing care and certifying outcomes — the commitment that Dan-Go
will never allow a relief case record to function as evidence of sufficiency,
adequacy, or rescue. The record is advisory. The relief is real. The proof
claim is absent.
