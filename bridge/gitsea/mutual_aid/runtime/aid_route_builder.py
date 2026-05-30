"""
aid_route_builder.py — Phase 17: Mutual Aid Routing Layer

Dan-Go builds advisory routes between aid requests and aid offers.
A route is an observation that a request and an offer share enough
overlap to be worth surfacing to the relevant participants. Dan-Go
suggests the route; it does not compel the exchange, allocate resources,
or guarantee any outcome.

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

# ── route statuses ────────────────────────────────────────────────────────────
ROUTE_STATUSES = {
    "possible":    "Request and offer overlap; route is advisory and possible.",
    "suggested":   "Route has been surfaced to relevant participants.",
    "accepted":    "Participants have voluntarily agreed to connect.",
    "declined":    "One or both parties chose not to proceed; no obligation imposed.",
    "completed":   "Aid exchange completed voluntarily.",
    "expired":     "Route expired before connection was made.",
}

# ── match reasons ─────────────────────────────────────────────────────────────
MATCH_REASONS = {
    "type_overlap":       "Request type and offer type are compatible.",
    "commons_shared":     "Request and offer originate in the same commons.",
    "urgency_compatible": "Offer availability matches request urgency.",
    "capacity_available": "Offer has capacity that covers the request.",
    "cross_commons":      "Route spans two commons with shared participation.",
}

# ── default routes ────────────────────────────────────────────────────────────
# Each route links one request to one offer. Dan-Go observes the overlap
# and records it as an advisory suggestion. No compulsion. No allocation.
DEFAULT_ROUTES: list[dict[str, object]] = [
    {
        "route_id":       "aid-route-001",
        "request_id":     "aid-request-001",
        "offer_id":       "aid-offer-001",
        "commons_id":     "jammy-house-001",
        "route_status":   "possible",
        "match_reasons":  ["type_overlap", "commons_shared"],
        "route_note":     "food_support request may align with meal_preparation offer.",
    },
    {
        "route_id":       "aid-route-002",
        "request_id":     "aid-request-002",
        "offer_id":       "aid-offer-002",
        "commons_id":     "jammy-house-001",
        "route_status":   "suggested",
        "match_reasons":  ["type_overlap", "commons_shared", "urgency_compatible"],
        "route_note":     "housing_support request may align with housing_advocacy offer.",
    },
    {
        "route_id":       "aid-route-003",
        "request_id":     "aid-request-003",
        "offer_id":       "aid-offer-003",
        "commons_id":     "dra-001",
        "route_status":   "possible",
        "match_reasons":  ["type_overlap", "commons_shared", "urgency_compatible", "capacity_available"],
        "route_note":     "refugee_relief request may align with supply_sharing offer.",
    },
    {
        "route_id":       "aid-route-004",
        "request_id":     "aid-request-003",
        "offer_id":       "aid-offer-004",
        "commons_id":     "dra-001",
        "route_status":   "possible",
        "match_reasons":  ["commons_shared", "urgency_compatible"],
        "route_note":     "refugee_relief request may align with shelter_hosting offer.",
    },
    {
        "route_id":       "aid-route-005",
        "request_id":     "aid-request-004",
        "offer_id":       "aid-offer-005",
        "commons_id":     "yacypherpunks-001",
        "route_status":   "possible",
        "match_reasons":  ["type_overlap", "commons_shared"],
        "route_note":     "skill_exchange request may align with skill_sharing offer.",
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


def build_aid_route(
    route_id:      str,
    request_id:    str,
    offer_id:      str,
    commons_id:    str,
    route_status:  str,
    match_reasons: list[str],
    route_note:    str,
) -> dict[str, object]:
    """Build one advisory aid route record."""
    if route_status not in ROUTE_STATUSES:
        route_status = "possible"

    valid_reasons = [r for r in match_reasons if r in MATCH_REASONS]
    reason_notes  = {r: MATCH_REASONS[r] for r in valid_reasons}

    record: dict[str, object] = {
        "record_type":          "aid_route",
        "route_id":             route_id,
        "route_date":           str(date.today()),
        "request_id":           request_id,
        "offer_id":             offer_id,
        "commons_id":           commons_id,
        "route_status":         route_status,
        "status_note":          ROUTE_STATUSES[route_status],
        "match_reasons":        valid_reasons,
        "match_reason_notes":   reason_notes,
        "route_note":           route_note,
        # invariants
        **AID_INVARIANTS,
        # explicit route-level invariants
        "route_is_command":         False,
        "route_compels_exchange":   False,
        "route_allocates_capacity": False,
        "participants_decide":      True,
        "route_may_be_declined":    True,
        # protocol phrases
        "protocol_phrases": [
            "Need is not debt.",
            "Help is not command.",
            "Routing is not allocation.",
        ],
    }
    return record


def load_requests() -> dict[str, dict[str, object]]:
    """Try to load request registry from saved JSON; return indexed by request_id."""
    req_path = _EXAMPLES / "aid-request-registry.json"
    if req_path.exists():
        data = json.loads(req_path.read_text())
        return {str(r["request_id"]): r for r in data.get("requests", [])}
    return {}


def load_offers() -> dict[str, dict[str, object]]:
    """Try to load offer registry from saved JSON; return indexed by offer_id."""
    off_path = _EXAMPLES / "aid-offer-registry.json"
    if off_path.exists():
        data = json.loads(off_path.read_text())
        return {str(o["offer_id"]): o for o in data.get("offers", [])}
    return {}


def build_route_log(
    routes: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    """Build the full aid route log."""
    if routes is None:
        routes = DEFAULT_ROUTES

    request_index = load_requests()
    offer_index   = load_offers()

    entries: list[dict[str, object]] = []
    for r in routes:
        entry = build_aid_route(
            route_id      = str(r["route_id"]),
            request_id    = str(r["request_id"]),
            offer_id      = str(r["offer_id"]),
            commons_id    = str(r["commons_id"]),
            route_status  = str(r["route_status"]),
            match_reasons = list(r.get("match_reasons", [])),  # type: ignore[arg-type]
            route_note    = str(r.get("route_note", "")),
        )
        # attach request/offer summaries if available
        req = request_index.get(str(r["request_id"]))
        off = offer_index.get(str(r["offer_id"]))
        if req:
            entry["request_summary"] = {
                "request_type": req.get("request_type"),
                "urgency":      req.get("urgency"),
                "commons_id":   req.get("commons_id"),
            }
        if off:
            entry["offer_summary"] = {
                "offer_type":   off.get("offer_type"),
                "availability": off.get("availability"),
                "capacity":     off.get("capacity"),
            }
        entries.append(entry)

    # status counts
    status_counts: dict[str, int] = {}
    for e in entries:
        s = str(e["route_status"])
        status_counts[s] = status_counts.get(s, 0) + 1

    log: dict[str, object] = {
        "record_type":     "aid_route_log",
        "log_id":          "aid-route-log-001",
        "log_date":        str(date.today()),
        "route_count":     len(entries),
        "status_summary":  status_counts,
        "routes":          entries,
        **AID_INVARIANTS,
        "protocol_phrases": [
            "Need is not debt.",
            "Help is not command.",
            "Routing is not allocation.",
            "Dan-Go suggests routes; participants decide whether to connect.",
        ],
    }
    return log


def print_log(log: dict[str, object]) -> None:
    print("=== aid_route_builder.py ===")
    print(f"  log_id:        {log['log_id']}")
    print(f"  route_count:   {log['route_count']}")
    print(f"  status_summary: {log['status_summary']}")
    for r in log["routes"]:  # type: ignore[union-attr]
        print(f"  [{r['route_id']}] {r['request_id']} → {r['offer_id']} "
              f"status={r['route_status']} routing_allocates_resources={r['routing_allocates_resources']}")
    print(f"  authority={log['authority']}, moves_money={log['moves_money']}, "
          f"routing_allocates_resources={log['routing_allocates_resources']}")
    print("  Routing is not allocation.")


def save_log(log: dict[str, object]) -> Path:
    _EXAMPLES.mkdir(parents=True, exist_ok=True)
    out = _EXAMPLES / "aid-route.json"
    out.write_text(json.dumps(log, indent=2))
    print(f"  saved → {out.relative_to(_REPO_ROOT)}")
    return out


if __name__ == "__main__":
    log = build_route_log()
    print_log(log)
    if "--save" in sys.argv:
        save_log(log)
