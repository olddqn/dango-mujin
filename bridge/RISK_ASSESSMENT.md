# Risk Assessment

Version: 0.1.0-draft

---

## Purpose

This document assesses the risks of the dango-gitsea-bridge project honestly.
It does not minimize risks for promotional reasons.
It does not exaggerate risks to avoid accountability.
It states what is known and what is not.

---

## Risk 1: GITSEA Does Not Exist or Does Not Work

**Probability:** Unknown. GITSEA's implementation status is unverified.
**Impact:** High — if GITSEA is non-functional, the bridge has no financial layer to connect to.
**Mitigation:**
- The bridge is designed as a translation layer, not a GITSEA dependency
- Any equivalent protocol with the same properties can be substituted
- The bridge's value is in the Dan-Go → asset translation logic, not in GITSEA specifically
- If GITSEA is abandoned or fraudulent, fork the bridge to connect to something else

**Status:** Accepted risk. Documented. Mitigated by protocol-agnostic design.

---

## Risk 2: Dignity Guard Is Circumvented

**Probability:** Low (by design), but not zero.
**Impact:** Very high — if dignity guard fails, vulnerable people can be harmed.
**Mitigation:**
- Dignity guard runs before any transformation
- `block` decisions are logged and cannot be deleted
- Consent-unknown is an automatic block, not an escalation
- Human review is required for escalated cases
- Code is open source — anyone can audit the guard logic

**Status:** Accepted risk. Mitigation is structural, not procedural.

---

## Risk 3: Contribution Streams Are Misused as Financial Instruments

**Probability:** Medium — bad actors may attempt to frame streams as securities or investment products.
**Impact:** High — legal liability, harm to participants, reputational damage to the protocol.
**Mitigation:**
- Documentation explicitly and repeatedly states this is not a financial product
- No transaction signing, no key custody, no money movement in this bridge
- The bridge models transformation; it does not execute it
- Legal review is listed as a required contribution for high-risk Claims

**Status:** Accepted risk. Mitigation is documentation and design constraint.

---

## Risk 4: Stories of Vulnerable People Are Used Without Adequate Consent

**Probability:** Medium — the refugee story example makes this salient.
**Impact:** Very high — direct harm to specific people.
**Mitigation:**
- REFUGEE_STORY_STREAM_ETHICS.md defines seven mandatory conditions
- Dignity guard blocks consent-unknown Claims automatically
- This bridge does not collect or store stories directly
- All seven conditions must be met before a refugee story Claim can proceed

**Status:** Accepted risk. Mitigation is layered: ethics document + dignity guard + human review.

---

## Risk 5: AI Agent Makes Poor Dignity Judgments

**Probability:** Medium — AI agents can miss context that humans would catch.
**Impact:** High — AI-passed claims might harm people.
**Mitigation:**
- AI agents are explicitly prohibited from passing consent-unknown cases
- AI agents must escalate ambiguous cases to human review
- The dignity guard is a structural filter, not a replacement for human judgment
- Documentation repeatedly states AI cannot replace human ethical judgment

**Status:** Accepted risk. Mitigation is explicit limitation of AI authority.

---

## Risk 6: The Protocol Itself Becomes a Tool of Coercion

**Probability:** Low, but protocol design cannot prevent all misuse.
**Impact:** High — if Dan-Go is used to coerce participation, it violates its own constitution.
**Mitigation:**
- Constitution explicitly prohibits coercion
- Claims that require coercion fail the dignity guard
- Anyone may object, counter-claim, or reject — these are valid participation
- Forks are welcome if the protocol is captured by bad actors

**Status:** Accepted risk. No protocol is coercion-proof. Transparency is the primary defense.

---

## What This Bridge Does Not Assess

- The legal status of contribution streams in any jurisdiction
- The financial viability of any GITSEA-like system
- The security of any wallet or signing system
- The reliability of any specific node or network

These require specialized expertise beyond the scope of this document.
Seek legal, financial, and security review before connecting this bridge to real economic systems.

---

## The Honest Summary

This is a protocol-draft bridge between a social coordination protocol (Dan-Go)
and a hypothetical financial layer (GITSEA).

It is not ready for production use with real vulnerable people without:
- Independent legal review
- Independent security review
- Community review from people with lived experience
- A real, verified GITSEA-equivalent implementation

It is ready for: conceptual development, protocol negotiation, and fork-based improvement.
