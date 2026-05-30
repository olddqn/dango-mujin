"""
aid_request_registry.py — Phase 17: Mutual Aid Routing Layer

Dan-Go records help requests inside commons. Requests are advisory observations.
Recording a request does not create debt, obligation, or authority.

"Need is not debt."
"Help is not command."
"Routing is not allocation."

Invariants:
  authority: none
  execution_allowed: false
  moves_money: false
  credit_issued: false
  hard_enforcement: false
  advisory: true
  mutual_aid_only: true
  append_only: true
  contestable: true
  reopenable: true
  need_creates_debt: false
  help_is_command: false
  routing_allocates_resources: false
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import date

# ── paths ────────────────────────────────────────────────────────────────────
_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT   = _SCRIPT_DIR.parents[4]
_EXAMPLES    = _SCRIPT_DIR.parent / "examples"

# ── request types ─────────────────────────────────────────────────────────────
REQUEST_TYPES = {
    "food_support":       "Request for food or meal support.",
    "shelter_support":    "Request for temporary or emergency shelter.",
    "transport_support":  "Request for transport or travel assistance.",
    "childcare_support":  "Request for childcare or dependent care.",
    "health_support":     "Request for health-related assistance.",
    "skill_exchange":     "Request for skills, knowledge, or labour exchange.",
    "emotional_support":  "Request for emotional support or community care.",
    "housing_support":    "Request for housing assistance or negotiation support.",
    "refugee_relief":     "Request for relief resources for displaced persons.",
    "general":            "General request for assistance.",
}

# ── urgency levels ────────────────────────────────────────────────────────────
URGENCY_LEVELS = {
    "immediate": "Needed within hours.",
    "urgent":    "Needed within a day.",
    "medium":    "Needed within a week.",
    "low":       "Needed when available.",
    "ongoing":   "Recurring or continuous need.",
}

# ── default requests ──────────────────────────────────────────────────────────
DEFAULT_REQUESTS: list[dict[str, object]] = [
    {
        "request_id":  "aid-request-001",
        "commons_id":  "jammy-house-001",
        "requester_id":"external-003",
        "request_type":"food_support",
        "urgency":     "medium",
        "description": "Household needs food support for the coming week.",
        "claim_id":    "housing-007",
    },
    {
        "request_id":  "aid-request-002",
        "commons_id":  "dra-001",
        "requester_id":"external-002",
        "request_type":"housing_support",
        "urgency":     "urgent",
        "description": "Tenant facing eviction risk; needs negotiation support.",
        "claim_id":    "housing-007",
    },
    {
        "request_id":  "aid-request-003",
        "commons_id":  "dra-001",
        "requester_id":"external-001",
        "request_type":"refugee_relief",
        "urgency":     "immediate",
        "description": "Displaced family needs emergency shelter and supply routing.",
        "claim_id":    None,
    },
    {
        "request_id":  "aid-request-004",
        "commons_id":  "yacypherpunks-001",
        "requester_id":"external-001",
        "request_type":"skill_exchange",
        "urgency":     "low",
        "description": "Community member seeking peer review for security audit.",
        "claim_id":    None,
    },
]

# ── invariants ────────────────────────────────────────────────────────────────
AID_INVARIANTS: dict[str, object] = {
    "authority":                "none",
    "execution_allowed":        False,
    "moves_money":              False,
    "credit_issued":            False,
    "hard_enforcement":         False,
    "advisory":                 True,
    "mutual_aid_only":          True,
    "append_only":              True,
    "contestable":              True,
    "reopenable":               True,
    "need_creates_debt":        False,
    "help_is_command":          False,
    "routing_allocates_resources": False,
}


def build_aid_request(
    request_id:  str,
    commons_id:  str,
    requester_id: str,
    request_type: str,
    urgency:      str,
    description:  str,
    claim_id:     str | None = None,
) -> dict[str, object]:
    """Build one advisory aid request record."""
    if request_type not in REQUEST_TYPES:
        request_type = "general"
    if urgency not in URGENCY_LEVELS:
        urgency = "medium"

    record: dict[str, object] = {
        "record_type":        "aid_request",
        "request_id":         request_id,
        "request_date":       str(date.today()),
        "commons_id":         commons_id,
        "requester_id":       requester_id,
        "request_type":       request_type,
        "type_note":          REQUEST_TYPES[request_type],
        "urgency":            urgency,
        "urgency_note":       URGENCY_LEVELS[urgency],
        "description":        description,
        "claim_id":           claim_id,
        "request_status":     "open",
        # invariants
        **AID_INVARIANTS,
        # explicit request-level invariants
        "need_creates_debt":  False,
        "request_is_command": False,
        "requester_owes_help_received": False,
        # protocol phrases
        "protocol_phrases": [
            "Need is not debt.",
            "Help is not command.",
            "Routing is not allocation.",
        ],
    }
    return record


def build_request_registry(
    requests: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    """Build the full aid request registry."""
    if requests is None:
        requests = DEFAULT_REQUESTS

    entries = [
        build_aid_request(
            request_id   = r["request_id"],   # type: ignore[arg-type]
            commons_id   = r["commons_id"],   # type: ignore[arg-type]
            requester_id = r["requester_id"], # type: ignore[arg-type]
            request_type = r["request_type"], # type: ignore[arg-type]
            urgency      = r["urgency"],      # type: ignore[arg-type]
            description  = r["description"],  # type: ignore[arg-type]
            claim_id     = r.get("claim_id"), # type: ignore[arg-type]
        )
        for r in requests
    ]

    # count by urgency
    urgency_counts: dict[str, int] = {}
    for e in entries:
        u = str(e["urgency"])
        urgency_counts[u] = urgency_counts.get(u, 0) + 1

    registry: dict[str, object] = {
        "record_type":    "aid_request_registry",
        "registry_id":    "aid-request-registry-001",
        "registry_date":  str(date.today()),
        "request_count":  len(entries),
        "urgency_summary": urgency_counts,
        "requests":       entries,
        **AID_INVARIANTS,
        "protocol_phrases": [
            "Need is not debt.",
            "Help is not command.",
            "Routing is not allocation.",
            "Dan-Go records requests; it does not rank need or command assistance.",
        ],
    }
    return registry


def print_registry(reg: dict[str, object]) -> None:
    print("=== aid_request_registry.py ===")
    print(f"  registry_id:   {reg['registry_id']}")
    print(f"  request_count: {reg['request_count']}")
    print(f"  urgency_summary: {reg['urgency_summary']}")
    for r in reg["requests"]:  # type: ignore[union-attr]
        print(f"  [{r['request_id']}] {r['commons_id']} — {r['request_type']} "
              f"(urgency={r['urgency']}) need_creates_debt={r['need_creates_debt']}")
    print(f"  authority={reg['authority']}, moves_money={reg['moves_money']}, "
          f"need_creates_debt={reg['need_creates_debt']}")
    print("  Need is not debt.")
    print("  Help is not command.")


def save_registry(reg: dict[str, object]) -> Path:
    _EXAMPLES.mkdir(parents=True, exist_ok=True)
    out = _EXAMPLES / "aid-request-registry.json"
    out.write_text(json.dumps(reg, indent=2))
    print(f"  saved → {out.relative_to(_REPO_ROOT)}")
    return out


if __name__ == "__main__":
    reg = build_request_registry()
    print_registry(reg)
    if "--save" in sys.argv:
        save_registry(reg)
