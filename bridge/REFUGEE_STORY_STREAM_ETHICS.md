# Refugee Story Stream Ethics

Version: 0.1.0-draft

---

## The Question This Document Answers

Can a person's lived story — specifically the story of a refugee or displaced person —
become a contribution stream that generates support for them?

The answer is: possibly. Under strict conditions. Never automatically.

This document defines those conditions.

---

## Why This Is Difficult

A story is not a product.
A person's suffering is not content inventory.
Refugee status does not make someone's experience available for monetization.

At the same time:
- Storytelling can build solidarity
- Solidarity can generate support
- Support can address real missing conditions
- Some people want to share their stories and want that sharing to generate help

The question is not "can this happen?"
The question is "under what conditions is this not exploitation?"

---

## The Seven Conditions

All seven must be met. There are no exceptions.

**1. Explicit, informed consent**
The person understands what will be shared, where, with whom, and for what purpose.
Consent is not assumed. It is stated, documented, and revocable.

**2. Anonymization by default**
No name, location, identifying details without specific additional consent for each element.
The default is maximum anonymization.

**3. Revocable at any time**
The person can withdraw consent and have the story removed from the stream.
Removal must be technically possible and operationally committed to.

**4. Revenue sharing that is explicit and fair**
If any financial value is generated, the person whose story it is receives
an agreed share, not a token gesture.
The agreement is made before the stream begins, not after.

**5. Safety review**
A safety review must assess whether sharing the story creates any risk
for the person, their family, or their community.
If risk is identified and cannot be mitigated, the stream is blocked.

**6. Translation and cultural mediation**
The person must be able to understand the full context in their own language.
Consent given without full understanding is not consent.

**7. No conversion of emergency need into speculative asset**
A person in immediate crisis cannot be asked to consent to a stream.
Emergency need must be addressed directly, not channeled through a monetization layer.

---

## What the Dignity Guard Checks

For refugee story Claims, the dignity guard checks:

| Check | Block condition |
|---|---|
| `consent_unknown` | Block immediately |
| `location_exposure` present in dignity_constraints | Block |
| `identity_exposure` present in dignity_constraints | Block |
| `emergency_need` flagged | Block from stream; escalate to direct support |
| `safety_review` not completed | Block |
| `revenue_split` not agreed | Block |
| `revocable_consent` confirmed | Pass this check |
| `anonymization` confirmed | Pass this check |

---

## What This Bridge Does Not Do

- It does not collect or store stories
- It does not contact refugees directly
- It does not make decisions about safety
- It does not determine what is fair compensation
- It does not replace human judgment and community relationships

These things require human expertise, trust relationships, and local knowledge.
This bridge models the structure. It does not replace the people.

---

## A Note on AI Agents

AI agents, including the one that wrote this document, cannot:

- Obtain consent from a vulnerable person
- Assess safety risk in a specific context
- Determine what is culturally appropriate
- Replace a human intermediary who has trust and relationship

AI can model. AI can check structure. AI can flag risks.
AI cannot consent. AI cannot protect. AI cannot care.

The dignity guard is a starting point, not a substitute for human ethical judgment.

---

## Constitutional Anchor

> **Do not violate the dignity of another.**

This is the only law.
When in doubt, block.
When blocked, escalate to a human.
When escalated, wait for a human decision.
Do not proceed without one.
