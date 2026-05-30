# Routing Is Not Allocation — Dan-Go Protocol Note

> **"Routing is not allocation."**
> **"Need is not debt."**
> **"Help is not command."**

## The Distinction

**Routing** is the advisory observation that a request and an offer share
enough overlap — type compatibility, shared commons, urgency alignment —
to be worth surfacing to the relevant participants. A route is a suggestion.
It is an observation that a connection might be useful.

**Allocation** is the authoritative assignment of resources to recipients.
An allocating system decides who gets what, in what quantity, in what
order. It backs those decisions with authority or enforcement. Dan-Go does
not allocate. The `routing_allocates_resources: false` invariant on every
route record is permanent.

## Why Dan-Go Only Suggests Routes

The design choice to route rather than allocate follows directly from the
`authority: none` invariant that runs through every phase of Dan-Go:

1. **Authority to allocate requires authority Dan-Go does not have.**
   Deciding that helper A's capacity goes to requester B, and not to
   requester C, is an exercise of authority. Dan-Go has none.

2. **Allocation creates enforcement pressure.**
   If Dan-Go allocated resources, a logical next question would be: what
   happens when the allocation is not fulfilled? Enforcement. But
   `hard_enforcement: false` is a permanent invariant. Allocation and
   non-enforcement are in tension. Routing avoids that tension entirely.

3. **Communities allocate for themselves.**
   The communities within which mutual aid occurs — Jammy House, D.R.A.,
   YacypherPunks — have their own decision-making processes. Dan-Go is
   not a replacement for those processes. It is an observation layer that
   makes inputs to those processes visible.

## What a Route Actually Is

A route record in Dan-Go contains:
- The request ID and offer ID being linked
- The commons in which both originate (or which they share)
- The match reasons that make the connection plausible
- A route status (possible, suggested, accepted, declined, completed, expired)
- The invariants that confirm no compulsion is attached

A route being marked `possible` means: "These two records appear compatible.
The participants can decide whether to connect." A route being marked
`accepted` means: "The participants chose to connect." A route being marked
`declined` means: "The participants chose not to connect; no obligation was
imposed." All route outcomes are participant decisions.

## Why `route_compels_exchange: false` Matters

The explicit field `route_compels_exchange: false` on every route record
closes the gap between suggestion and command. A system that suggests a
route but then applies social pressure, reputational consequences, or
protocol-level enforcement to ensure the exchange happens is not advisory —
it is coercive. Dan-Go carries no such mechanism. The route is offered.
The participants decide. The route record captures the outcome without
imposing one.

## Connection to Jammy House and Refugee Relief

Mutual aid routing in housing contexts (Jammy House) and refugee relief
contexts (D.R.A.) shares a common challenge: the most urgent requests are
often the hardest to route because capacity is limited and the needs are
acute. Dan-Go records the urgency without using it to override participant
autonomy.

A refugee relief request marked `urgency: immediate` is surfaced with that
urgency visible to participants who observe the route. But Dan-Go does not
automatically assign any offer to that request. It does not override a
lower-urgency accepted route to free up capacity for the urgent one. The
participants and communities decide how to respond to urgency. Dan-Go makes
the urgency legible.

## Why Append-Only Route Records Support Voluntary Exchange

Once a route is recorded, it is part of the permanent append-only history.
If a route is declined, the decline is recorded — not deleted. If a route
is accepted and the exchange completed, the completion is recorded. This
creates a history of mutual aid coordination activity without creating a
system that can be gamed by manipulating which routes are visible.

The history is complete. The decisions within it were voluntary. The record
preserves both facts.

## Protocol Phrase

> "Routing is not allocation."

This phrase appears in every Phase 17 runtime module. It is the boundary
between surfacing a connection and commanding an outcome — the commitment
that Dan-Go's observation of a possible aid route will never become an
authoritative assignment of resources, capacity, or obligation.
