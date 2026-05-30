# Follow-Up Is Not Blame — Dan-Go Protocol Note

> **"Follow-up is not blame."**
> **"Reopen is not failure."**
> **"Care loop is not obligation."**

## The Distinction

**Follow-up** is an advisory observation that more care activity may be
useful. A follow-up need record says: here is what was observed; here is
what might help next. It points forward, not backward.

**Blame** is a retrospective judgment that someone is responsible for a
negative outcome. Dan-Go does not make blame judgments. The
`followup_is_blame: false` and `followup_judges_prior_helper: false`
invariants on every follow-up need record are permanent.

## Why Helpers Are Not Blamed for Recurring Need

The person who provided a meal, offered shelter, coordinated supplies, or
initiated housing advocacy did what they could at the time they did it.
When a follow-up need is later recorded — because the need recurred, because
the outcome was partial, because the situation changed — that recording is
not a verdict on the original helper.

The follow-up need record does not contain:
- Any assessment of whether the original response was adequate
- Any identification of the original helper as responsible for the gap
- Any requirement for the original helper to respond again
- Any social consequence attached to not responding again

`followup_demands_response: false` is an invariant. Recording the follow-up
need is an act of observation, not an act of accountability enforcement.

## Why Requesters Are Not Blamed for Continuing Need

A person who needed food support once and needs it again is not at fault for
having continuing food insecurity. A displaced family that needed shelter
once and remains displaced has not done something wrong. The follow-up need
record captures the continuation of a situation, not the failure of the
person experiencing it.

`need_creates_debt: false` carries through from Phase 17 into Phase 19.
`ranks_suffering: false` ensures that urgent recurring needs are not treated
as more blameworthy or more deserving than lower-urgency recurring needs.

## Why Blame Would Corrupt the Care Record

If follow-up need records were understood as blame:

1. **Helpers would be deterred from offering aid.** If offering help once
   creates an implicit accountability relationship for ongoing help, fewer
   people will offer in the first place.

2. **Requesters would be deterred from seeking follow-up.** If seeking
   follow-up is understood as blaming the previous helper, people in need
   will suppress their needs to protect relationships.

3. **The care record would become adversarial.** A record designed to make
   care legible would become a tool for assigning responsibility. This
   corrupts both the record and the community relationships it is meant
   to support.

Dan-Go avoids this by making the follow-up record explicitly non-judgmental.
The follow-up need exists. The participants will decide what, if anything,
to do about it. The record does not prejudge their decision.

## The Connection to Voluntary Care

The reason follow-up is not blame is the same reason help is not command
(Phase 17) and reopen is not failure (Phase 19): the entire care layer is
built on the principle that cooperation is voluntary. Voluntary cooperation
cannot coexist with blame, because blame creates obligation, and obligation
removes voluntariness.

Dan-Go preserves the voluntary character of every care interaction by
ensuring that observation — at every phase — is not judgment.

## Protocol Phrase

> "Follow-up is not blame."

This phrase appears in every Phase 19 runtime module. It is the commitment
that Dan-Go's record of a follow-up need will never be used to judge, indict,
or pressure any participant in a care exchange. The follow-up is for the
community's awareness, not for accountability enforcement.
