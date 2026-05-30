"""
aid_offer_registry.py — Phase 17: Mutual Aid Routing Layer

Dan-Go records voluntary offers of help inside commons. Offers are advisory
observations. Recording an offer does not compel the offerer, create a
binding commitment, or give Dan-Go authority over the exchange.

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

# ── paths ─────────────────────────────────────────────────────────────────────
_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT   = _SCRIPT_DIR.parents[4]
_EXAMPLES    = _SCRIPT_DIR.parent / "examples"

# ── offer types ───────────────────────────────────────────────────────────────
OFFER_TYPES = {
    "meal_preparation":   "Offer to prepare or share meals.",
    "shelter_hosting":    "Offer of temporary shelter or hosting.",
    "transport_sharing":  "Offer of transport or travel assistance.",
    "childcare_sharing":  "Offer of childcare or dependent care.",
    "health_assistance":  "Offer of health-related support.",
    "skill_sharing":      "Offer of skills, knowledge, or labour.",
    "emotional_support":  "Offer of emotional support or community care.",
    "housing_advocacy":   "Offer of housing advocacy or negotiation support.",
    "supply_sharing":     "Offer of physical supplies or resources.",
    "coordination":       "Offer to coordinate mutual aid activities.",
    "general":            "General offer of assistance.",
}

# ── availability windows ──────────────────────────────────────────────────────
AVAILABILITY = {
    "immediate":  "Available now.",
    "daily":      "Available on a daily basis.",
    "weekly":     "Available on a weekly basis.",
    "as_needed":  "Available as needed; contact to arrange.",
    "one_time":   "Single-instance offer.",
    "ongoing":    "Recurring or indefinite offer.",
}

# ── default offers ────────────────────────────────────────────────────────────
DEFAULT_OFFERS: list[dict[str, object]] = [
    {
        "offer_id":     "aid-offer-001",
        "commons_id":   "jammy-house-001",
        "offerer_id":   "external-001",
        "offer_type":   "meal_preparation",
        "availability": "weekly",
        "description":  "Able to prepare communal meals twice a week for house members.",
        "capacity":     4,
    },
    {
        "offer_id":     "aid-offer-002",
        "commons_id":   "jammy-house-001",
        "offerer_id":   "external-002",
        "offer_type":   "housing_advocacy",
        "availability": "as_needed",
        "description":  "Available to assist with tenancy negotiation and rights information.",
        "capacity":     2,
    },
    {
        "offer_id":     "aid-offer-003",
        "commons_id":   "dra-001",
        "offerer_id":   "external-001",
        "offer_type":   "supply_sharing",
        "availability": "immediate",
        "description":  "Can provide emergency supply coordination for displaced persons.",
        "capacity":     10,
    },
    {
        "offer_id":     "aid-offer-004",
        "commons_id":   "dra-001",
        "offerer_id":   "external-002",
        "offer_type":   "shelter_hosting",
        "availability": "one_time",
        "description":  "Able to host one displaced person or family for up to 7 days.",
        "capacity":     1,
    },
    {
        "offer_id":     "aid-offer-005",
        "commons_id":   "yacypherpunks-001",
        "offerer_id":   "external-001",
        "offer_type":   "skill_sharing",
        "availability": "weekly",
        "description":  "Peer security review and digital safety skills exchange.",
        "capacity":     3,
    },
]

# ── invariants ────────────────────────────────────────────────────────────────
AID_INVARIANTS: dict[str, object] = {
    "authority":                   "none",
    "execution_allowed":           False,
    "moves_money":                 False,
    "credit_issued":               False,
    "hard_enforcement":            False,
    "advisory":                    True,
    "mutual_aid_only":             True,
    "append_only":                 True,
    "contestable":                 True,
    "reopenable":                  True,
    "need_creates_debt":           False,
    "help_is_command":             False,
    "routing_allocates_resources": False,
}


def build_aid_offer(
    offer_id:     str,
    commons_id:   str,
    offerer_id:   str,
    offer_type:   str,
    availability: str,
    description:  str,
    capacity:     int = 1,
) -> dict[str, object]:
    """Build one advisory aid offer record."""
    if offer_type not in OFFER_TYPES:
        offer_type = "general"
    if availability not in AVAILABILITY:
        availability = "as_needed"

    record: dict[str, object] = {
        "record_type":          "aid_offer",
        "offer_id":             offer_id,
        "offer_date":           str(date.today()),
        "commons_id":           commons_id,
        "offerer_id":           offerer_id,
        "offer_type":           offer_type,
        "type_note":            OFFER_TYPES[offer_type],
        "availability":         availability,
        "availability_note":    AVAILABILITY[availability],
        "description":          description,
        "capacity":             capacity,
        "offer_status":         "open",
        # invariants
        **AID_INVARIANTS,
        # explicit offer-level invariants
        "voluntary":            True,
        "offer_is_command":     False,
        "control":              False,
        "offer_creates_obligation": False,
        "offerer_may_withdraw": True,
        # protocol phrases
        "protocol_phrases": [
            "Need is not debt.",
            "Help is not command.",
            "Routing is not allocation.",
        ],
    }
    return record


def build_offer_registry(
    offers: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    """Build the full aid offer registry."""
    if offers is None:
        offers = DEFAULT_OFFERS

    entries = [
        build_aid_offer(
            offer_id     = o["offer_id"],     # type: ignore[arg-type]
            commons_id   = o["commons_id"],   # type: ignore[arg-type]
            offerer_id   = o["offerer_id"],   # type: ignore[arg-type]
            offer_type   = o["offer_type"],   # type: ignore[arg-type]
            availability = o["availability"], # type: ignore[arg-type]
            description  = o["description"],  # type: ignore[arg-type]
            capacity     = int(o.get("capacity", 1)),
        )
        for o in offers
    ]

    # count by offer type
    type_counts: dict[str, int] = {}
    for e in entries:
        t = str(e["offer_type"])
        type_counts[t] = type_counts.get(t, 0) + 1

    registry: dict[str, object] = {
        "record_type":    "aid_offer_registry",
        "registry_id":    "aid-offer-registry-001",
        "registry_date":  str(date.today()),
        "offer_count":    len(entries),
        "offer_type_summary": type_counts,
        "offers":         entries,
        **AID_INVARIANTS,
        "protocol_phrases": [
            "Need is not debt.",
            "Help is not command.",
            "Routing is not allocation.",
            "Dan-Go records offers; it does not command helpers or allocate their capacity.",
        ],
    }
    return registry


def print_registry(reg: dict[str, object]) -> None:
    print("=== aid_offer_registry.py ===")
    print(f"  registry_id:  {reg['registry_id']}")
    print(f"  offer_count:  {reg['offer_count']}")
    print(f"  offer_type_summary: {reg['offer_type_summary']}")
    for o in reg["offers"]:  # type: ignore[union-attr]
        print(f"  [{o['offer_id']}] {o['commons_id']} — {o['offer_type']} "
              f"voluntary={o['voluntary']} control={o['control']} "
              f"help_is_command={o['help_is_command']}")
    print(f"  authority={reg['authority']}, moves_money={reg['moves_money']}, "
          f"help_is_command={reg['help_is_command']}")
    print("  Help is not command.")


def save_registry(reg: dict[str, object]) -> Path:
    _EXAMPLES.mkdir(parents=True, exist_ok=True)
    out = _EXAMPLES / "aid-offer-registry.json"
    out.write_text(json.dumps(reg, indent=2))
    print(f"  saved → {out.relative_to(_REPO_ROOT)}")
    return out


if __name__ == "__main__":
    reg = build_offer_registry()
    print_registry(reg)
    if "--save" in sys.argv:
        save_registry(reg)
