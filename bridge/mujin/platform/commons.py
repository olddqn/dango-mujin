"""
commons.py — Mujin Contribution Commons (domain logic)

Mujin is not a donation site, charity, NGO, NPO, or marketplace.
Mujin is a Contribution Commons:

    Need -> Contribution -> Connection -> Reality Feedback

This is rescue-possibility discovery, not price discovery.

"Registration is not proof."
"Withdrawal is not failure."
"Support is not debt."
"advisory_only is not moral immunity."

Top metric: TTFR — Time To First Rescue. The system's response speed is
measured. People are never measured (no ranking, no scores, no priority,
no value assessment — Constitution Art.4).

AI agents are Contribution Providers, peers of humans / NPOs / NGOs /
companies / municipalities / volunteers. What is registered is capability,
not status. Agents may explore, translate, propose, research, analyse,
and generate connection candidates. Agents may NOT allocate funds, select
cases, rank, govern, or evaluate (Art.20).

Storage: append-only JSONL under bridge/mujin/data/ (store.py guards refuse
any write into Dan-Go territory). The canonical Dan-Go reality feedback
(bridge/sutable/reality_feedback.jsonl) is NOT written here — promotion to
the canon goes through the existing Dan-Go appender with human review
(ADR-001).
"""

from __future__ import annotations

from typing import Any

from ..schemas import base_invariants, OBJECTION_TARGETS, OBJECTION_CHANNELS
from ..store import DATA_DIR, append_jsonl, read_jsonl, utc_now_iso

# ── files (all append-only, all under bridge/mujin/data/) ────────────────────
NEEDS_JSONL         = DATA_DIR / "needs.jsonl"
CONTRIBUTIONS_JSONL = DATA_DIR / "contributions.jsonl"
AGENTS_JSONL        = DATA_DIR / "agents.jsonl"
PROPOSALS_JSONL     = DATA_DIR / "proposals.jsonl"
FEEDBACK_JSONL      = DATA_DIR / "reality_feedback_platform.jsonl"
OBJECTIONS_JSONL    = DATA_DIR / "objections.jsonl"   # shared with Phase A

# ── vocabularies ──────────────────────────────────────────────────────────────
NEED_TYPES = [
    "Translation", "Housing", "Education", "Fundraising", "Legal",
    "Medical", "Technology", "Resource", "Other",
]
URGENCY_VALUES = ["now", "this_week", "this_month", "ongoing"]
CONSENT_STATUSES = ["active", "pending", "deferred"]

CONTRIBUTION_KINDS = [
    "Resource", "Skill", "Time", "Translation", "Housing", "Education",
    "Fundraising", "Legal", "Medical", "Technology", "Other",
]
PROVIDER_KINDS = [
    "human", "ai_agent", "npo", "ngo", "company", "municipality", "volunteer",
]

AGENT_CAPABILITIES = [
    "Translation", "Fundraising", "Housing", "Education",
    "Research", "Legal", "Medical",
]
AGENT_CAN = ["探索", "翻訳", "提案", "調査", "分析", "接続候補生成"]
AGENT_CANNOT = ["資金配分", "ケース選定", "順位付け", "統治", "評価"]

FEEDBACK_RESULTS = ["positive", "negative", "partial", "withdrawn", "unresolved"]
REPORTER_KINDS = ["subject", "supporter", "third_party", "npo"]

INVARIANT_PHRASES = {
    "advisory_only": True,
    "human_review_required": True,
    "execution_allowed": False,
    "support_is_not_debt": True,
    "registration_is_not_proof": True,
    "withdrawal_is_not_failure": True,
    "reach_gap_unresolved": True,
}


class CommonsError(Exception):
    pass


def _next_id(prefix: str, path) -> str:
    return f"{prefix}-{len(read_jsonl(path)) + 1:03d}"


# ── needs ─────────────────────────────────────────────────────────────────────

def register_need(
    need_type: str,
    description: str,
    urgency: str,
    location: str,
    contact_method: str,
    consent_status: str,
    representative: bool,
) -> dict[str, Any]:
    """Register a need.

    Registration is not proof. A representative cannot manufacture the
    subject's consent (ADR-005 D-2/D-3): proxy registration is always
    recorded as consent-deferred until the subject confirms.
    """
    if need_type not in NEED_TYPES:
        raise CommonsError(f"unknown need type: {need_type!r}")
    if urgency not in URGENCY_VALUES:
        raise CommonsError(f"unknown urgency: {urgency!r}")
    if consent_status not in CONSENT_STATUSES:
        raise CommonsError(f"unknown consent status: {consent_status!r}")
    if not description.strip():
        raise CommonsError("description is required")
    if representative and consent_status == "active":
        # a proxy can register, but cannot consent on the subject's behalf
        consent_status = "deferred"

    record = {
        "record_type": "need",
        "need_id": _next_id("need", NEEDS_JSONL),
        "need_type": need_type,
        "description": description.strip(),
        "urgency": urgency,            # the subject's own words; never used for ordering
        "location": location.strip(),
        "contact_method": contact_method.strip(),
        "consent_status": consent_status,
        "representative": representative,
        "confirmation_due": representative or consent_status == "deferred",
        "created_at": utc_now_iso(),
        **base_invariants(),
        **INVARIANT_PHRASES,
    }
    return append_jsonl(NEEDS_JSONL, record)


def list_needs(public_only: bool = True) -> list[dict[str, Any]]:
    """Needs in registration order (neutral; no ranking, no urgency sort).

    Needs without active consent are not listed publicly (only counted).
    """
    needs = read_jsonl(NEEDS_JSONL)
    if public_only:
        needs = [n for n in needs if n.get("consent_status") == "active"]
    return needs


# ── contributions (humans and AI agents are peers) ───────────────────────────

def register_contribution(
    provider_name: str,
    provider_kind: str,
    kind: str,
    description: str,
) -> dict[str, Any]:
    if provider_kind not in PROVIDER_KINDS:
        raise CommonsError(f"unknown provider kind: {provider_kind!r}")
    if kind not in CONTRIBUTION_KINDS:
        raise CommonsError(f"unknown contribution kind: {kind!r}")
    if not provider_name.strip():
        raise CommonsError("provider name (pseudonym is fine) is required")

    record = {
        "record_type": "contribution_offer",
        "contribution_id": _next_id("contrib", CONTRIBUTIONS_JSONL),
        "provider_name": provider_name.strip(),    # pseudonym welcome
        "provider_kind": provider_kind,            # human and ai_agent are peers
        "kind": kind,
        "description": description.strip(),
        "status": "offered",
        "created_at": utc_now_iso(),
        **base_invariants(),
        **INVARIANT_PHRASES,
    }
    return append_jsonl(CONTRIBUTIONS_JSONL, record)


def list_contributions() -> list[dict[str, Any]]:
    return read_jsonl(CONTRIBUTIONS_JSONL)


# ── agent registry (not a marketplace) ───────────────────────────────────────

def register_agent(name: str, capability: str, description: str) -> dict[str, Any]:
    """Register an AI agent by capability only.

    Agents declare what they CAN do. What they can never do is stamped on
    the record itself and is not configurable.
    """
    if capability not in AGENT_CAPABILITIES:
        raise CommonsError(f"unknown capability: {capability!r}")
    if not name.strip():
        raise CommonsError("agent name is required")

    record = {
        "record_type": "agent",
        "agent_id": _next_id("agent", AGENTS_JSONL),
        "name": name.strip(),
        "capability": capability,
        "description": description.strip(),
        "can": list(AGENT_CAN),
        "cannot": list(AGENT_CANNOT),       # 資金配分・ケース選定・順位付け・統治・評価
        "created_at": utc_now_iso(),
        **base_invariants(),
        **INVARIANT_PHRASES,
    }
    return append_jsonl(AGENTS_JSONL, record)


def list_agents() -> list[dict[str, Any]]:
    return read_jsonl(AGENTS_JSONL)


# ── proposal engine (proposal != decision) ───────────────────────────────────

# which contribution kinds can serve which need type (affinity, not ranking)
_NEED_TO_KINDS = {
    "Translation": {"Translation", "Skill"},
    "Housing":     {"Housing", "Resource"},
    "Education":   {"Education", "Skill", "Time"},
    "Fundraising": {"Fundraising"},
    "Legal":       {"Legal", "Skill"},
    "Medical":     {"Medical"},
    "Technology":  {"Technology", "Skill"},
    "Resource":    {"Resource"},
    "Other":       set(CONTRIBUTION_KINDS),
}


def generate_proposal(need_id: str) -> dict[str, Any]:
    """Generate connection candidates for a need.

    Candidates are listed in registration order — NEUTRAL. No score, no
    rank, no best-match. A proposal is generated, never decided: it binds
    no one, and it is contestable through the objection path.
    """
    need = next((n for n in read_jsonl(NEEDS_JSONL) if n.get("need_id") == need_id), None)
    if need is None:
        raise CommonsError(f"unknown need: {need_id}")
    if need.get("consent_status") != "active":
        raise CommonsError(
            f"need {need_id} has no active consent — no proposals are generated "
            "for unconsented needs (a proposal about a person is contact-adjacent)"
        )

    kinds = _NEED_TO_KINDS.get(need["need_type"], {need["need_type"]})
    candidates = []
    for c in list_contributions():                       # registration order
        if c.get("kind") in kinds:
            candidates.append({
                "candidate_type": "contribution",
                "id": c["contribution_id"],
                "name": c["provider_name"],
                "provider_kind": c["provider_kind"],
                "kind": c["kind"],
            })
    for a in list_agents():                              # agents are peers
        if a.get("capability") in kinds or a.get("capability") == need["need_type"]:
            candidates.append({
                "candidate_type": "agent",
                "id": a["agent_id"],
                "name": a["name"],
                "provider_kind": "ai_agent",
                "kind": a["capability"],
            })

    record = {
        "record_type": "proposal",
        "proposal_id": _next_id("proposal", PROPOSALS_JSONL),
        "need_id": need_id,
        "need_type": need["need_type"],
        "candidates": candidates,                # neutral order, never ranked
        "candidate_count": len(candidates),
        "proposal_is_not_decision": True,
        "binds_no_one": True,
        "contestable": True,
        "generated_at": utc_now_iso(),
        **base_invariants(),
        **INVARIANT_PHRASES,
    }
    return append_jsonl(PROPOSALS_JSONL, record)


def list_proposals() -> list[dict[str, Any]]:
    return read_jsonl(PROPOSALS_JSONL)


# ── reality feedback (negative feedback is welcome) ──────────────────────────

def record_feedback(
    ref_id: str,
    result: str,
    reporter_kind: str,
    reporter_name: str,
    content: str,
) -> dict[str, Any]:
    """Record reality feedback about a need / proposal / connection.

    Anyone may report: the subject, a supporter, a third party, an NPO.
    Negative feedback is welcome — it is the system's only way to learn.
    'withdrawn' is a neutral record: withdrawal is not failure.
    """
    if result not in FEEDBACK_RESULTS:
        raise CommonsError(f"unknown result: {result!r}")
    if reporter_kind not in REPORTER_KINDS:
        raise CommonsError(f"unknown reporter kind: {reporter_kind!r}")

    record = {
        "record_type": "reality_feedback_platform",
        "feedback_id": _next_id("feedback", FEEDBACK_JSONL),
        "ref_id": ref_id.strip(),                 # need-### / proposal-### / free ref
        "result": result,
        "reporter_kind": reporter_kind,
        "reporter_name": reporter_name.strip(),   # pseudonym welcome
        "content": content.strip(),
        "negative_feedback_is_welcome": True,
        "not_proof_of_resolution": True,
        "canonical_promotion": "via existing Dan-Go appender with human review (ADR-001)",
        "created_at": utc_now_iso(),
        **base_invariants(),
        **INVARIANT_PHRASES,
    }
    return append_jsonl(FEEDBACK_JSONL, record)


def list_feedback() -> list[dict[str, Any]]:
    return read_jsonl(FEEDBACK_JSONL)


# ── objection (ADR-010) ───────────────────────────────────────────────────────

def record_objection(
    target: str,
    channel: str,
    content: str,
    submitted_by: str,
    ref_id: str = "",
) -> dict[str, Any]:
    """Record an objection (ADR-010). Proxy submission allowed.

    Filing an objection never counts against anyone and is never used for
    profiling. A receipt id is issued immediately (D10-5: the receipt-number
    reconciliation is the first defence against suppression).
    """
    if target not in OBJECTION_TARGETS:
        raise CommonsError(f"unknown objection target: {target!r}")
    if channel not in OBJECTION_CHANNELS:
        raise CommonsError(f"unknown objection channel: {channel!r}")
    if not content.strip():
        raise CommonsError("objection content is required")

    record = {
        "record_type": "mujin_objection",
        "objection_id": _next_id("objection", OBJECTIONS_JSONL),
        "target": target,
        "channel": channel,
        "content": content.strip(),
        "submitted_by": submitted_by,             # subject | third_party_on_behalf
        "ref_id": ref_id.strip(),
        "status": "received",                     # state tracking starts here
        "response_log": [],
        "counts_against_subject": False,
        "usable_for_profiling": False,
        "created_at": utc_now_iso(),
        **base_invariants(),
        **INVARIANT_PHRASES,
    }
    return append_jsonl(OBJECTIONS_JSONL, record)


def list_objections() -> list[dict[str, Any]]:
    """Latest state per objection id (append-only stream; last event wins)."""
    latest: dict[str, dict[str, Any]] = {}
    for rec in read_jsonl(OBJECTIONS_JSONL):
        oid = rec.get("objection_id")
        if oid:
            latest[oid] = rec
    return sorted(latest.values(), key=lambda r: r.get("created_at", ""))


# ── TTFR (system speed only — people are never measured) ─────────────────────

def ttfr_status() -> dict[str, Any]:
    """Time To First Rescue.

    Achieved when the FIRST subject-authored positive/partial feedback
    exists. Until then, the clock runs from the first need registration.
    This measures the system's response speed — never a person's worth.
    """
    needs = read_jsonl(NEEDS_JSONL)
    first_need_at = min((n["created_at"] for n in needs), default=None)
    rescues = [
        f for f in list_feedback()
        if f.get("reporter_kind") == "subject" and f.get("result") in ("positive", "partial")
    ]
    first_rescue_at = min((f["created_at"] for f in rescues), default=None)
    return {
        "need_count": len(needs),
        "needs_public": len(list_needs()),
        "contribution_count": len(list_contributions()),
        "agent_count": len(list_agents()),
        "proposal_count": len(list_proposals()),
        "feedback_count": len(list_feedback()),
        "objection_count": len(list_objections()),
        "first_need_at": first_need_at,
        "first_rescue_at": first_rescue_at,
        "ttfr_achieved": first_rescue_at is not None,
        "measures_people": False,
    }
