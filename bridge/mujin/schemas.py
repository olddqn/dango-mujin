"""
schemas.py — Mujin Platform MVP v1.1: Phase A Data Layer

Schema definitions for Mujin-specific records (MUJIN_MVP_SPEC.md §4, §15, §16, §17).
These dataclasses are the data layer only. They hold no authority, execute
nothing, move no money, and judge no one.

"Registration is not proof."
"Withdrawal is not failure."
"Support is not debt."
"advisory_only is not moral immunity."

Invariants (ADR-001..005, carried on every record):
  authority: none
  execution_allowed: false
  moves_money: false
  advisory: true            (necessary for safety, NOT sufficient — ADR-005 D-4)
  append_only: true
  contestable: true
  reopenable: true
  human_review_required: true
  registration_is_not_proof: true
  withdrawal_is_failure: false
  support_is_debt: false
  closure_attribution_prohibited: true   (ADR-005 D-10)

Boundary rules (ADR-001/002/003):
  - Mujin never writes to Dan-Go Execution Logs, Claims, or Directives.
  - Mujin never modifies Relief Case Memory; it references it via source_ref.
  - The canonical Reality Feedback sink is bridge/sutable/reality_feedback.jsonl.
  - All Mujin-specific data lives under bridge/mujin/.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any

# ── controlled vocabularies (MUJIN_MVP_SPEC.md §4, §16) ──────────────────────

CREATED_FROM_VALUES = {
    "relief_case":        "Promoted from a Phase 18 Relief Case (ADR-003 gate, human review).",
    "direct_application": "The subject applied directly.",
    "npo_proxy":          "Registered by an NPO on the subject's behalf (deferred consent applies).",
    "scouter":            "RESERVED. No generation path exists in the MVP (SPEC §4, D-7).",
}

# created_from values that the MVP may actually create. "scouter" is reserved:
# the Saiyan Scouter question is an unresolved Dan-Go Claim, not a feature.
CREATABLE_FROM = {"relief_case", "direct_application", "npo_proxy"}

CONSENT_STATUSES = {
    "active":    "The subject's valid consent exists.",
    "pending":   "Consent acquisition is in progress.",
    "deferred":  "Proxy-registered; the subject is not yet in a state to consent (D-2/D-3).",
    "withdrawn": "Consent was withdrawn. Withdrawal is not failure.",
}

CASE_STATUSES = {
    "open":                "Case is open.",
    "in_progress":         "Cooperation is in progress.",
    "paused":              "Case is paused. Neutral record.",
    "resolved_by_parties": "Parties consider it resolved. Not a certification.",
    "not_pursued":         "Not pursued. This is not failure (A-2, D-5).",
    "interrupted":         "Interrupted. This is not failure (D-5, D-10).",
}

VISIBILITY_VALUES = {
    "public":            "Visible to everyone (requires active consent).",
    "participants_only": "Visible to case participants only (default).",
    "private":           "Visible to the subject and reviewers only.",
}

NEED_STATUSES = {
    "open":      "Need is open.",
    "addressed": "A contribution addresses this need.",
    "closed":    "Need closed by the parties. Neutral record.",
}

OBJECTION_TARGETS = {
    "mujin":     "The Mujin platform itself.",
    "npo":       "An NPO acting in or around a case.",
    "supporter": "A supporter / contributor.",
    "ai_agent":  "An AI agent's behaviour.",
}

OBJECTION_CHANNELS = {
    "ui":          "Submitted through a Mujin UI page.",
    "phone":       "Submitted by phone (non-technical path, D-1).",
    "in_person":   "Submitted in person (non-technical path, D-1).",
    "transcribed": "Written down by a third party on the subject's behalf (D-1).",
    "third_party": "Relayed by a third party (D-1).",
}

NON_MUJIN_SUPPORT_KINDS = {
    "family":    "Support by family.",
    "friends":   "Support by friends.",
    "community": "Support by neighbourhood / local community.",
    "other":     "Other informal mutual aid outside Mujin.",
}

PROTOCOL_PHRASES = [
    "Registration is not proof.",
    "Withdrawal is not failure.",
    "Support is not debt.",
    "advisory_only is not moral immunity.",
]


def base_invariants() -> dict[str, Any]:
    """The invariant block carried by every Mujin record. Never weakened."""
    return {
        "authority": "none",
        "execution_allowed": False,
        "moves_money": False,
        "advisory": True,
        "advisory_only_is_moral_immunity": False,   # ADR-005 D-4
        "append_only": True,
        "contestable": True,
        "reopenable": True,
        "human_review_required": True,
        "registration_is_not_proof": True,          # A-1
        "withdrawal_is_failure": False,             # A-3 / D-5
        "support_is_debt": False,                   # ADR-004
        "closure_attribution_prohibited": True,     # D-10
        "protocol_phrases": list(PROTOCOL_PHRASES),
    }


# ── records ───────────────────────────────────────────────────────────────────

@dataclass
class ConsentRecord:
    """Consent state for a Mujin Case (SPEC §8, §16).

    A state of being unable to consent is not consent (D-3). Silence is not
    consent. `deferred` is not provisional consent — until confirmation, no
    consent exists, the case is not public, and no contributions are accepted.
    """
    status: str = "pending"                  # active | pending | deferred | withdrawn
    can_consent: bool = True                 # False => status must be "deferred" (D-3)
    obtained_at: str | None = None           # ISO 8601, None until consent exists
    confirmation_due: bool = False           # duty to confirm once subject can consent (D-2)
    last_confirmed_at: str | None = None     # continuous confirmation (§8.1)
    correction_log: list[dict[str, Any]] = field(default_factory=list)  # append-only
    withdrawable: bool = True                # always True (A-3)
    withdrawal_reason: str | None = None     # optional; never required, never scored


@dataclass
class DeferredConsent:
    """Deferred-consent detail for proxy registration (SPEC §16, ADR-005 D-2/D-3).

    Records why the subject cannot yet consent and who carries the duty to
    confirm. Held alongside ConsentRecord while consent.status == "deferred".
    """
    reason_category: str = "unspecified"     # e.g. "acute_condition" | "language_barrier"
                                             # | "cognitive_constraint" | "unspecified"
                                             # — category only; never a diagnosis or PII
    registered_by: str = ""                  # pseudonymous handle of the proxy registrant
    confirmation_duty_holder: str = ""       # who must confirm once consent becomes possible
    discovery_origin: dict[str, Any] = field(default_factory=lambda: {
        "how": "",                           # how the subject was found (D-7)
        "by": "",                            # pseudonymous handle
        "disclosed_to_subject": False,       # must become True at confirmation (§16.3)
    })
    deferred_at: str = ""                    # ISO 8601


@dataclass
class Need:
    """A need attached to a Mujin Case (SPEC §4)."""
    need_id: str = ""
    description: str = ""
    addresses_condition: str | None = None   # joins Claim.missing_conditions (§5)
    status: str = "open"                     # NEED_STATUSES


@dataclass
class ContributionLink:
    """Reference from a Mujin Case to an existing Dan-Go Contribution (ADR-004).

    Mujin does NOT create a new contribution system. This is a link record
    only — the contribution itself lives in the existing Dan-Go model
    (bridge/sutable/contributions.jsonl). No score, no tier, no debt.
    """
    contribution_id: str = ""
    contribution_type: str = ""              # existing 11-type vocabulary
    addresses_condition: str | None = None
    status: str = "offered"                  # offered|committed|delivered|verified|disputed
    contributor: str = ""                    # pseudonymous handle


@dataclass
class ProgressLog:
    """One append-only progress entry (SPEC §4). Neutral record, no judgment."""
    entry_id: str = ""
    content: str = ""
    actor: str = ""                          # pseudonymous handle
    created_at: str = ""                     # ISO 8601


@dataclass
class ObjectionRecord:
    """An objection by the subject (SPEC §15, ADR-005 D-1).

    The subject may object to Mujin, an NPO, a supporter, or an AI agent,
    without Dan-Go participation ability and without technical access.
    Filing an objection must never count against the subject.
    """
    objection_id: str = ""
    case_id: str | None = None               # objections may also be case-independent
    target: str = "mujin"                    # OBJECTION_TARGETS
    channel: str = "ui"                      # OBJECTION_CHANNELS (phone/in_person/... = D-1)
    content: str = ""
    submitted_by: str = "subject"            # subject | third_party_on_behalf
    created_at: str = ""                     # ISO 8601
    response_log: list[dict[str, Any]] = field(default_factory=list)  # append-only
    counts_against_subject: bool = False     # always False (§15.1) — never flipped
    usable_for_profiling: bool = False       # always False (§15.2)


@dataclass
class NonMujinSupport:
    """A record honouring support that did NOT pass through Mujin (SPEC §17, D-8).

    Family, friends, and community mutual aid are equal in dignity to
    Mujin-mediated support. Recording it here gives it visibility WITHOUT
    ranking it below (or above) Mujin cases. Registration on Mujin is never
    a condition for support to be 'official'.
    """
    record_id: str = ""
    case_id: str | None = None               # optionally linked to a case
    kind: str = "community"                  # NON_MUJIN_SUPPORT_KINDS
    description: str = ""                    # no PII; consent of parties assumed by recorder
    recorded_by: str = ""                    # pseudonymous handle
    created_at: str = ""                     # ISO 8601
    equal_in_dignity: bool = True            # always True (D-8) — never flipped
    mujin_registration_required: bool = False  # always False (§17.1)


@dataclass
class MujinCase:
    """A Mujin Case (SPEC §4). Minimal MVP schema.

    A case references — and never rewrites — its Dan-Go sources
    (relief_case_id / claim_id). Closure or interruption is never attributed
    to the subject's ability, attributes, or effort (D-10): causes are
    recorded as design limits, supporter behaviour, or social conditions.
    """
    case_id: str = ""
    created_from: str = "direct_application" # CREATABLE_FROM only; "scouter" is reserved
    source_ref: dict[str, Any] = field(default_factory=dict)  # {relief_case_id?, claim_id?}
    discovery_origin: dict[str, Any] = field(default_factory=lambda: {
        "how": "", "by": "", "disclosed_to_subject": False,
    })
    consent: ConsentRecord = field(default_factory=ConsentRecord)
    deferred_consent: DeferredConsent | None = None   # present iff consent.status == deferred
    needs: list[Need] = field(default_factory=list)
    success_metric: dict[str, Any] = field(default_factory=lambda: {
        "set_by": "default",                 # subject | default — subject's metric wins (D-9)
        "description": "defined by the parties; never economic independence by default",
    })
    contribution_links: list[ContributionLink] = field(default_factory=list)
    progress_log: list[ProgressLog] = field(default_factory=list)   # append-only
    visibility: str = "participants_only"    # VISIBILITY_VALUES (minimal disclosure default)
    status: str = "open"                     # CASE_STATUSES
    closure_note: str | None = None          # structural causes only — never subject-attribution
    created_at: str = ""                     # ISO 8601
    updated_at: str = ""                     # ISO 8601

    def to_record(self) -> dict[str, Any]:
        """Serialise with the invariant block attached."""
        record = asdict(self)
        record["record_type"] = "mujin_case"
        record.update(base_invariants())
        return record


def is_publicly_visible(case: MujinCase) -> bool:
    """A case may be shown publicly only with active consent (§8.1, §16.1)."""
    return case.consent.status == "active" and case.visibility == "public"


def accepts_contributions(case: MujinCase) -> bool:
    """Contributions are accepted only with active consent (§16.1)."""
    return case.consent.status == "active"
