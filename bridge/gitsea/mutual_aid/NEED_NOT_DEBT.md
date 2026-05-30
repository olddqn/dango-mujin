# Need Is Not Debt — Dan-Go Protocol Note

> **"Need is not debt."**
> **"Help is not command."**
> **"Routing is not allocation."**

## The Distinction

**Need** is the observable state of a person or household lacking something
necessary for wellbeing — food, shelter, safety, support. Need is a fact
about present circumstances. It does not carry moral weight, and it does
not generate financial or social obligation.

**Debt** is an obligation created between parties through agreement,
transaction, or imposition — the receiver of something owes something
in return. Dan-Go's mutual aid layer creates no debt. The `need_creates_debt:
false` invariant on every aid request record is unconditional.

## Why Need Does Not Create Obligation

Several assumptions conflate need with debt:

1. **Gift economy thinking**: In a gift economy, giving creates social
   obligation to reciprocate. Dan-Go does not model mutual aid as a gift
   economy. Receiving help through a mutual aid route creates no
   obligation — social, financial, or otherwise — to the specific person
   who provided it.

2. **Credit thinking**: In credit systems, receiving something now creates
   a future obligation to repay. Mutual aid is not credit. A person who
   receives food support through Jammy House does not owe food back.
   They do not owe labour, participation, or contribution.

3. **Charity thinking**: Charity often implies a power differential and
   a latent expectation of gratitude or compliance. Mutual aid is peers
   cooperating, not donors and recipients. The record of help received
   carries no social hierarchy and no obligation.

## What `need_creates_debt: false` Means in Practice

When an aid request is recorded in Dan-Go:
- The requester is not accruing a debt to be repaid.
- The commons is not recording a credit against the requester.
- If no help is provided, the requester has no unfulfilled obligation.
- If help is provided, the requester does not owe the helper anything.
- Future participation by the requester in mutual aid is voluntary —
  not a repayment.

The field `requester_owes_help_received: false` makes this explicit on
every request record. It is not merely a default — it is an invariant
that cannot be overridden.

## Why This Matters for Refugee Relief and Housing Crisis

In contexts of acute need — refugee displacement, eviction, food
insecurity — framing need as debt is harmful. It deters people from
seeking help. It creates shame around vulnerability. It turns moments
of crisis into instruments of control.

Jammy House and D.R.A. exist in the space where housing insecurity and
community cooperation intersect. Dan-Go records the cooperation facts
without layering on obligation narratives. A displaced person who
requests emergency shelter routing through D.R.A. is not entering a
credit relationship. They are expressing a need in a community that
observes it without judgment.

## The `judgment: false` Companion Invariant

The mutual aid layer inherits the `judgment: false` principle from the
recognition ledger (Phase 15). Dan-Go does not evaluate whether a request
is deserving. It does not score the requester's situation. It does not
rank need by severity and allocate accordingly. It records. Recording
is not ranking. Observation is not judgment.

## Protocol Phrase

> "Need is not debt."

This phrase appears in every Phase 17 runtime module. It is the boundary
between observation and obligation — the commitment that Dan-Go's record
of a help request will never be used to create, imply, or enforce an
obligation on the person who expressed the need.
