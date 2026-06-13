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
GATEWAYS_JSONL      = DATA_DIR / "gateway_registry.jsonl"
PROPOSALS_JSONL     = DATA_DIR / "proposals.jsonl"
FEEDBACK_JSONL      = DATA_DIR / "reality_feedback_platform.jsonl"
OBJECTIONS_JSONL    = DATA_DIR / "objections.jsonl"   # shared with Phase A
PROBLEM_JSONL       = DATA_DIR / "problem_posts.jsonl"
SOLUTION_JSONL      = DATA_DIR / "solution_posts.jsonl"
RESOURCE_JSONL      = DATA_DIR / "resource_posts.jsonl"
AGENT_POSTS_JSONL   = DATA_DIR / "agent_posts.jsonl"
FUNDING_JSONL       = DATA_DIR / "funding_posts.jsonl"
DISCOVERY_JSONL     = DATA_DIR / "discovery_posts.jsonl"
CORRECTION_JSONL    = DATA_DIR / "correction_log.jsonl"
VOICE_JSONL         = DATA_DIR / "voice_records.jsonl"
NEED_CANDIDATE_JSONL = DATA_DIR / "need_candidates.jsonl"

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

FEEDBACK_RESULTS = [
    "positive", "negative", "partial", "withdrawn", "unresolved",
    "mixed", "failed", "unknown",
]
REPORTER_KINDS = ["subject", "supporter", "third_party", "npo"]

# ── solution commons / post-type vocabularies ────────────────────────────────
RESOURCE_TYPES = [
    "Human Skill", "Organization", "Translation", "Education",
    "Research", "Material", "Funding", "Community", "Other",
]
SOLUTION_CATEGORIES = [
    "Funding", "Material", "Education", "Translation", "Human Skill",
    "AI Agent", "Research", "Community", "Other",
]
DISCOVERY_SOURCE_TYPES = [
    "news_report", "ngo_report", "refugee_report", "disaster_report",
    "public_appeal", "public_interview", "public_statement",
    "public_video", "public_social_media",
]
WALLET_CHAINS = ["BTC", "ETH", "SOL", "XMR", "Other"]

AGENT_POST_INVARIANTS = {
    "proposal_only": True,
    "cannot_allocate_funds": True,
    "cannot_rank_people": True,
    "cannot_select_cases": True,
    "cannot_govern": True,
    "cannot_override_consent": True,
}

FUNDING_DISCLAIMERS = [
    "Mujin does not hold funds",
    "Listing is not verification",
    "Listing is not endorsement",
    "Donation is voluntary",
    "Donation creates no debt",
    "Donor has no control right",
    "Send at your own risk",
    "Verify independently before sending",
]

# ── gateways ──────────────────────────────────────────────────────────────────
# A gateway is a CONNECTOR, not a supporter: an entity through which a person
# in need reaches Mujin. Gateways outrank agents in TTFR terms: agents can
# add support capacity, but only gateways can shrink the Reach Gap.
GATEWAY_ORG_TYPES = [
    "npo", "ngo", "community_kitchen", "church", "temple", "hospital",
    "school", "municipality_desk", "volunteer_group", "shelter", "other",
]
GATEWAY_CAPABILITIES = [
    "Food", "Housing", "Translation", "Education", "Employment", "Legal",
    "Medical", "Refugee Support", "Elder Care", "Child Support",
    "Emergency Response",
]

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
    origin_voice_id: str = "",
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
        "origin_voice_id": origin_voice_id.strip(),   # traceable to a Voice (D-4)
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


# ── gateway registry (connectors, not supporters) ────────────────────────────

def register_gateway(
    name: str,
    org_type: str,
    region: str,
    languages: str,
    contact_method: str,
    capabilities: list[str],
    notes: str,
) -> dict[str, Any]:
    """Register a gateway — an entity that connects people to Mujin.

    Gateway registration is not certification. A gateway holds no authority,
    selects no cases, allocates nothing, and governs nothing. It is a door,
    and doors are listed in the order they were registered — never ranked.
    """
    if org_type not in GATEWAY_ORG_TYPES:
        raise CommonsError(f"unknown organization type: {org_type!r}")
    if not name.strip():
        raise CommonsError("gateway name is required")
    caps = [c for c in capabilities if c]
    bad = [c for c in caps if c not in GATEWAY_CAPABILITIES]
    if bad:
        raise CommonsError(f"unknown capabilities: {bad}")
    if not caps:
        raise CommonsError("at least one capability is required")

    record = {
        "record_type": "gateway",
        "gateway_id": _next_id("gateway", GATEWAYS_JSONL),
        "name": name.strip(),
        "org_type": org_type,
        "region": region.strip(),
        "languages": [l.strip() for l in languages.split(",") if l.strip()],
        "contact_method": contact_method.strip(),
        "capabilities": caps,
        "notes": notes.strip(),
        "status": "active",
        "gateway_is_connector_not_supporter": True,
        "gateway_registration_is_not_certification": True,
        "created_at": utc_now_iso(),
        **base_invariants(),
        **INVARIANT_PHRASES,
    }
    return append_jsonl(GATEWAYS_JSONL, record)


def list_gateways() -> list[dict[str, Any]]:
    """Latest state per gateway id (append-only; corrections supersede).

    Never ranked, never scored. Order is first-registration order.
    """
    latest: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for rec in read_jsonl(GATEWAYS_JSONL):
        gid = rec.get("gateway_id")
        if gid and gid not in latest:
            order.append(gid)
        if gid:
            latest[gid] = rec
    return [latest[g] for g in order]


def active_gateways() -> list[dict[str, Any]]:
    return [g for g in list_gateways() if g.get("status") == "active"]


# ── reality correction layer ─────────────────────────────────────────────────
# Reality must take precedence over demonstration convenience. Records are
# never deleted (append-only); corrections are appended and logged.

def record_correction(
    record_type: str,
    record_id: str,
    original_statement: str,
    corrected_statement: str,
    reason: str,
) -> dict[str, Any]:
    rec = {
        "record_type": record_type,
        "record_id": record_id,
        "original_statement": original_statement,
        "corrected_statement": corrected_statement,
        "reason": reason,
        "timestamp": utc_now_iso(),
    }
    return append_jsonl(CORRECTION_JSONL, rec)


def correct_gateway(
    gateway_id: str,
    operational_status: str,
    corrected_statement: str,
    reason: str,
) -> dict[str, Any]:
    """Supersede a gateway record with a corrected one (history preserved).

    The corrected record carries status='corrected' so it no longer appears
    as an active gateway, and records its true operational status and that it
    is not verified.
    """
    current = next((g for g in list_gateways() if g.get("gateway_id") == gateway_id), None)
    if current is None:
        raise CommonsError(f"unknown gateway: {gateway_id}")
    original = (f"{current.get('name')} listed as active {current.get('org_type')} "
                f"gateway providing {', '.join(current.get('capabilities', []))}")
    corrected = dict(current)
    corrected.update({
        "status": "corrected",
        "operational_status": operational_status,   # e.g. future_project_concept
        "verified": False,
        "verified_as_support_provider": False,
        "corrected": True,
        "correction_note": corrected_statement,
        "corrected_at": utc_now_iso(),
    })
    append_jsonl(GATEWAYS_JSONL, corrected)
    record_correction("gateway", gateway_id, original, corrected_statement, reason)
    return corrected


def list_corrections() -> list[dict[str, Any]]:
    return read_jsonl(CORRECTION_JSONL)


# ── solution commons: problem / solution / resource / agent / funding posts ──

def _post(path, prefix: str, record_type: str, fields: dict[str, Any],
          extra: dict[str, Any] | None = None) -> dict[str, Any]:
    record = {
        "record_type": record_type,
        f"{prefix}_id": _next_id(prefix, path),
        **fields,
        "created_at": utc_now_iso(),
        **base_invariants(),
        **INVARIANT_PHRASES,
        "listing_is_not_endorsement": True,
    }
    if extra:
        record.update(extra)
    return append_jsonl(path, record)


def post_problem(title, description, region, need_type, urgency, languages,
                 contact_method, consent_status, notes) -> dict[str, Any]:
    if need_type not in NEED_TYPES:
        raise CommonsError(f"unknown need type: {need_type!r}")
    if urgency not in URGENCY_VALUES:
        raise CommonsError(f"unknown urgency: {urgency!r}")
    if consent_status not in CONSENT_STATUSES:
        raise CommonsError(f"unknown consent status: {consent_status!r}")
    if not title.strip():
        raise CommonsError("title is required")
    return _post(PROBLEM_JSONL, "problem", "problem_post", {
        "title": title.strip(), "description": description.strip(),
        "region": region.strip(), "need_type": need_type, "urgency": urgency,
        "languages": [l.strip() for l in languages.split(",") if l.strip()],
        "contact_method": contact_method.strip(), "consent_status": consent_status,
        "notes": notes.strip(),
    })


def list_problems() -> list[dict[str, Any]]:
    return read_jsonl(PROBLEM_JSONL)


def post_solution(title, description, category, region, required_skills,
                  required_resources, contact_method, notes) -> dict[str, Any]:
    if category not in SOLUTION_CATEGORIES:
        raise CommonsError(f"unknown category: {category!r}")
    if not title.strip():
        raise CommonsError("title is required")
    return _post(SOLUTION_JSONL, "solution", "solution_post", {
        "title": title.strip(), "description": description.strip(),
        "category": category, "region": region.strip(),
        "required_skills": required_skills.strip(),
        "required_resources": required_resources.strip(),
        "contact_method": contact_method.strip(), "notes": notes.strip(),
    })


def list_solutions() -> list[dict[str, Any]]:
    return read_jsonl(SOLUTION_JSONL)


def post_resource(name, resource_type, description, languages, region,
                  contact_method, notes) -> dict[str, Any]:
    if resource_type not in RESOURCE_TYPES:
        raise CommonsError(f"unknown resource type: {resource_type!r}")
    if not name.strip():
        raise CommonsError("name is required")
    return _post(RESOURCE_JSONL, "resource", "resource_post", {
        "name": name.strip(), "resource_type": resource_type,
        "description": description.strip(),
        "languages": [l.strip() for l in languages.split(",") if l.strip()],
        "region": region.strip(), "contact_method": contact_method.strip(),
        "notes": notes.strip(),
    })


def list_resources() -> list[dict[str, Any]]:
    return read_jsonl(RESOURCE_JSONL)


def post_agent(name, description, capabilities, languages, region,
               contact_method, source_url) -> dict[str, Any]:
    """Agent Commons: an agent registers capability only. The constraints
    (cannot allocate funds / rank people / select cases / govern / override
    consent) are auto-attached and not configurable."""
    if not name.strip():
        raise CommonsError("agent name is required")
    caps = [c.strip() for c in capabilities.split(",") if c.strip()]
    if not caps:
        raise CommonsError("at least one capability is required")
    return _post(AGENT_POSTS_JSONL, "agentpost", "agent_post", {
        "name": name.strip(), "description": description.strip(),
        "capabilities": caps,
        "languages": [l.strip() for l in languages.split(",") if l.strip()],
        "region": region.strip(), "contact_method": contact_method.strip(),
        "source_url": source_url.strip(),
    }, extra=dict(AGENT_POST_INVARIANTS))


def list_agent_posts() -> list[dict[str, Any]]:
    return read_jsonl(AGENT_POSTS_JSONL)


def post_funding(display_name, case_title, description, region, wallet_chain,
                 wallet_address, accepted_assets, video_url, evidence_url,
                 contact_method, notes) -> dict[str, Any]:
    """Crypto Donation Board. Mujin does not hold funds. A listing is not
    verification and not endorsement. Donating is voluntary and creates no
    debt; the donor gains no control right. Send at your own risk."""
    if wallet_chain not in WALLET_CHAINS:
        raise CommonsError(f"unknown wallet chain: {wallet_chain!r}")
    if not case_title.strip():
        raise CommonsError("case title is required")
    if not wallet_address.strip():
        raise CommonsError("wallet address is required")
    return _post(FUNDING_JSONL, "funding", "funding_post", {
        "display_name": display_name.strip(), "case_title": case_title.strip(),
        "description": description.strip(), "region": region.strip(),
        "wallet_chain": wallet_chain, "wallet_address": wallet_address.strip(),
        "accepted_assets": accepted_assets.strip(),
        "video_url": video_url.strip(), "evidence_url": evidence_url.strip(),
        "contact_method": contact_method.strip(), "notes": notes.strip(),
    }, extra={
        "mujin_holds_funds": False,
        "listing_is_verification": False,
        "donation_creates_debt": False,
        "donor_has_control_right": False,
        "disclaimers": list(FUNDING_DISCLAIMERS),
    })


def list_funding() -> list[dict[str, Any]]:
    return read_jsonl(FUNDING_JSONL)


# ── Public Call for Help Registry (formerly "Discovery") ─────────────────────
# Mujin does not search for, identify, or classify people. It records
# PUBLICLY EXPRESSED requests for help. Listing is not consent, not
# verification, not priority. Observation is not intervention.

def post_public_call(title, description, region, source_type, source_url,
                     human_reviewed, notes) -> dict[str, Any]:
    if source_type not in DISCOVERY_SOURCE_TYPES:
        raise CommonsError(f"unknown source type: {source_type!r}")
    if not title.strip():
        raise CommonsError("title is required")
    if not human_reviewed:
        raise CommonsError(
            "a public-call entry must be human-reviewed before listing "
            "(no automated targeting — this is not Saiyan Scouter v1)")
    return _post(DISCOVERY_JSONL, "call", "public_call", {
        "title": title.strip(), "description": description.strip(),
        "region": region.strip(), "source_type": source_type,
        "source_url": source_url.strip(), "notes": notes.strip(),
    }, extra={
        "public_call_detected": True,
        "human_reviewed": True,
        "contact_attempted": False,        # never auto-contact
        "listing_is_not_verification": True,
        "listing_is_not_consent": True,
        "observation_is_not_intervention": True,
        "answers_question": "Who is asking for help?",
        "not_question": "Who should be helped?",
    })


def list_public_calls() -> list[dict[str, Any]]:
    return read_jsonl(DISCOVERY_JSONL)


# ── Voice Commons (Public Call → Need-Candidate pipeline) ─────────────────────
# This is NOT Saiyan Scouter. Mujin does not search for people likely to be in
# need, does not score vulnerability, does not rank or classify people. A Voice
# is recorded ONLY when a request for help is verifiable from PUBLIC
# information ("help us", "we need support", "we have nowhere to flee"). A
# guess by an AI, a third party's unilateral judgment, or any non-public
# information is never a Voice. Conversion produces a Need CANDIDATE, never a
# Need: human confirmation is always required, and no Need is ever auto-created.

VOICE_SOURCE_TYPES = [
    "public_interview", "news_report", "ngo_report", "refugee_appeal",
    "disaster_appeal", "community_request", "social_media_post",
    "video_statement", "other",
]
VOICE_CATEGORIES = [
    "Housing", "Food", "Water", "Medical", "Education", "Translation",
    "Employment", "Legal", "Safety", "Community", "Other",
]

# category -> suggested Need type (NEED_TYPES vocabulary)
_VOICE_TO_NEED = {
    "Housing": "Housing", "Food": "Resource", "Water": "Resource",
    "Medical": "Medical", "Education": "Education", "Translation": "Translation",
    "Employment": "Other", "Legal": "Legal", "Safety": "Other",
    "Community": "Other", "Other": "Other",
}
# category -> suggested Gateway capability types (GATEWAY_CAPABILITIES)
_VOICE_TO_GATEWAY = {
    "Housing": ["Housing", "Emergency Response"],
    "Food": ["Food", "Emergency Response"],
    "Water": ["Emergency Response", "Medical"],
    "Medical": ["Medical", "Emergency Response"],
    "Education": ["Education", "Child Support"],
    "Translation": ["Translation", "Refugee Support"],
    "Employment": ["Employment", "Education"],
    "Legal": ["Legal", "Refugee Support"],
    "Safety": ["Emergency Response", "Refugee Support"],
    "Community": ["Food", "Education"],
    "Other": ["Emergency Response"],
}
# source type that implies refugee context -> add refugee-oriented gateways
_REFUGEE_SOURCES = {"refugee_appeal"}
# category -> suggested Solution Commons categories (SOLUTION_CATEGORIES)
_VOICE_TO_SOLUTION = {
    "Housing": ["Material", "Community", "Funding"],
    "Food": ["Material", "Community"],
    "Water": ["Research", "AI Agent", "Community", "Funding"],
    "Medical": ["Funding", "Human Skill", "Material"],
    "Education": ["Education", "Human Skill"],
    "Translation": ["Translation", "AI Agent"],
    "Employment": ["Education", "Community"],
    "Legal": ["Human Skill", "Research"],
    "Safety": ["Community", "Research"],
    "Community": ["Community", "Research"],
    "Other": ["Research", "Community"],
}


def register_voice(title, description, source_type, source_url, region,
                   languages, voice_category, original_statement,
                   human_summary, human_reviewer, notes) -> dict[str, Any]:
    """Record a publicly-expressed call for help.

    Requires a named human reviewer: a Voice attests that a request for help
    is verifiable from public information. It is not surveillance, not
    vulnerability scoring, not targeting. Recording is not intervention.
    """
    if source_type not in VOICE_SOURCE_TYPES:
        raise CommonsError(f"unknown source type: {source_type!r}")
    if voice_category not in VOICE_CATEGORIES:
        raise CommonsError(f"unknown voice category: {voice_category!r}")
    if not title.strip():
        raise CommonsError("title is required")
    if not human_reviewer.strip():
        raise CommonsError(
            "a named human reviewer is required (Voice is human-reviewed; "
            "no automated scraping or classification)")
    if not original_statement.strip():
        raise CommonsError(
            "the original public statement is required (a Voice records an "
            "actual public call for help, not an inference)")
    return _post(VOICE_JSONL, "voice", "voice_record", {
        "title": title.strip(), "description": description.strip(),
        "source_type": source_type, "source_url": source_url.strip(),
        "region": region.strip(),
        "languages": [l.strip() for l in languages.split(",") if l.strip()],
        "voice_category": voice_category,
        "original_statement": original_statement.strip(),
        "human_summary": human_summary.strip(),
        "human_reviewer": human_reviewer.strip(),
        "notes": notes.strip(),
    }, extra={
        "public_call_detected": True,
        "human_reviewed": True,
        "contact_attempted": False,
        "voice_is_verification": False,
        "voice_is_consent": False,
        "voice_is_priority": False,
        "voice_is_ranking": False,
        "recording_is_intervention": False,
        "answers_question": "Who is asking for help?",
        "not_question": "Who should be helped?",
    })


def list_voices() -> list[dict[str, Any]]:
    return read_jsonl(VOICE_JSONL)


def get_voice(voice_id: str) -> dict[str, Any] | None:
    return next((v for v in list_voices() if v.get("voice_id") == voice_id), None)


def convert_voice_to_need_candidate(voice_id: str) -> dict[str, Any]:
    """Convert a Voice into a Need CANDIDATE (not a Need).

    Produces suggestions only. No Need is created. Human confirmation is
    always required before a candidate becomes a Need.
    """
    v = get_voice(voice_id)
    if v is None:
        raise CommonsError(f"unknown voice: {voice_id}")
    cat = v.get("voice_category", "Other")
    gw = list(_VOICE_TO_GATEWAY.get(cat, ["Emergency Response"]))
    if v.get("source_type") in _REFUGEE_SOURCES:
        for extra in ("Refugee Support", "Translation", "Legal", "Housing"):
            if extra not in gw:
                gw.append(extra)
    return _post(NEED_CANDIDATE_JSONL, "needcand", "need_candidate", {
        "origin_voice_id": voice_id,
        "suggested_need_type": _VOICE_TO_NEED.get(cat, "Other"),
        "suggested_region": v.get("region", ""),
        "suggested_languages": v.get("languages", []),
        "suggested_gateway_types": gw,
        "suggested_solution_types": list(_VOICE_TO_SOLUTION.get(cat, ["Research", "Community"])),
        "human_summary": v.get("human_summary", ""),
    }, extra={
        "candidate_only": True,
        "conversion_is_not_decision": True,
        "human_confirmation_required": True,
        "need_candidate_is_not_a_decision": True,
    })


def list_need_candidates() -> list[dict[str, Any]]:
    return read_jsonl(NEED_CANDIDATE_JSONL)


def voice_response_times() -> list[dict[str, Any]]:
    """For each Voice, time from registration to first candidate generation
    (first gateway suggestion). System speed only — never a person's worth."""
    from datetime import datetime
    cands_by_voice: dict[str, str] = {}
    for c in list_need_candidates():
        vid = c.get("origin_voice_id")
        ts = c.get("created_at")
        if vid and ts and (vid not in cands_by_voice or ts < cands_by_voice[vid]):
            cands_by_voice[vid] = ts
    out = []
    for v in list_voices():
        vid = v.get("voice_id")
        first = cands_by_voice.get(vid)
        delta = None
        if first:
            t0 = datetime.fromisoformat(v["created_at"].replace("Z", "+00:00"))
            t1 = datetime.fromisoformat(first.replace("Z", "+00:00"))
            delta = (t1 - t0).total_seconds()
        out.append({"voice_id": vid, "responded": first is not None,
                    "response_seconds": delta})
    return out


# which gateway capabilities can connect which need type (affinity, not ranking)
_NEED_TO_GATEWAY_CAPS = {
    "Translation": {"Translation", "Refugee Support"},
    "Housing":     {"Housing", "Refugee Support", "Emergency Response"},
    "Education":   {"Education", "Child Support"},
    "Fundraising": {"Emergency Response"},
    "Legal":       {"Legal", "Refugee Support"},
    "Medical":     {"Medical", "Elder Care", "Emergency Response"},
    "Technology":  {"Education", "Employment"},
    "Resource":    {"Food", "Emergency Response"},
    "Other":       set(GATEWAY_CAPABILITIES),
}


def gateway_candidates_for(need_type: str) -> list[dict[str, Any]]:
    """Candidate gateways for a need type. Presentation only — never an
    automatic connection. Order is registration order (neutral)."""
    caps = _NEED_TO_GATEWAY_CAPS.get(need_type, {need_type})
    out = []
    for g in list_gateways():
        if g.get("status") != "active":
            continue
        matched = sorted(set(g.get("capabilities", [])) & caps)
        if matched:
            out.append({
                "candidate_type": "gateway",
                "id": g["gateway_id"],
                "name": g["name"],
                "region": g.get("region", ""),
                "languages": g.get("languages", []),
                "matched_capabilities": matched,
            })
    return out


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
    for r in list_resources():                           # Solution Commons: resources
        if r.get("resource_type") in kinds | {"Other"} or r.get("resource_type") == need["need_type"]:
            candidates.append({
                "candidate_type": "resource_post",
                "id": r["resource_id"],
                "name": r["name"],
                "provider_kind": "resource",
                "kind": r["resource_type"],
            })
    for ap in list_agent_posts():                        # Solution Commons: agent posts
        if any(c in kinds or c == need["need_type"] for c in ap.get("capabilities", [])):
            candidates.append({
                "candidate_type": "agent_post",
                "id": ap["agentpost_id"],
                "name": ap["name"],
                "provider_kind": "ai_agent",
                "kind": "・".join(ap.get("capabilities", [])),
            })

    gateway_candidates = gateway_candidates_for(need["need_type"])

    record = {
        "record_type": "proposal",
        "proposal_id": _next_id("proposal", PROPOSALS_JSONL),
        "need_id": need_id,
        "need_type": need["need_type"],
        "connection_path": "Need -> Gateway -> Solution Commons",
        "gateway_candidates": gateway_candidates,  # connectors, presented first
        "gateway_candidate_count": len(gateway_candidates),
        "candidates": candidates,                # neutral order, never ranked
        "candidate_count": len(candidates),
        "proposal_is_not_decision": True,
        "listing_is_not_endorsement": True,
        "connection_is_voluntary": True,
        "no_automatic_connection": True,
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
    gateways = list_gateways()
    active = active_gateways()
    voices = list_voices()
    candidates = list_need_candidates()
    converted_voice_ids = {c.get("origin_voice_id") for c in candidates}
    needs_from_voice = [n for n in needs if n.get("origin_voice_id")]
    vrt = [r["response_seconds"] for r in voice_response_times() if r["response_seconds"] is not None]
    # reach coverage = gateways + resources + voices, regions/languages observed
    reach = active + list_resources() + voices
    regions = sorted({r.get("region", "") for r in reach if r.get("region")})
    languages = sorted({l for r in active + list_resources() + voices for l in r.get("languages", [])})
    return {
        "voice_count": len(voices),
        "voice_categories": sorted({v.get("voice_category", "") for v in voices if v.get("voice_category")}),
        "need_candidates_generated": len(candidates),
        "voices_converted_to_need": len(converted_voice_ids),
        "needs_from_voice": len(needs_from_voice),
        "voice_response_time_avg_seconds": (sum(vrt) / len(vrt)) if vrt else None,
        "regions_represented": regions,
        "languages_represented": languages,
        "need_count": len(needs),
        "needs_public": len(list_needs()),
        "problem_count": len(list_problems()),
        "solution_count": len(list_solutions()),
        "resource_count": len(list_resources()),
        "contribution_count": len(list_contributions()),
        "agent_count": len(list_agent_posts()) + len(list_agents()),
        "funding_post_count": len(list_funding()),
        "public_call_count": len(list_public_calls()),
        "gateway_count": len(gateways),
        "active_gateway_count": len(active),
        "regions_covered": regions,        # reach coverage, not a score of anyone
        "languages_covered": languages,
        "proposal_count": len(list_proposals()),
        "feedback_count": len(list_feedback()),
        "objection_count": len(list_objections()),
        "correction_count": len(list_corrections()),
        "first_need_at": first_need_at,
        "first_rescue_at": first_rescue_at,
        "ttfr_achieved": first_rescue_at is not None,
        "measures_people": False,
    }
