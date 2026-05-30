"""
mutual_aid_report.py — Phase 17: Mutual Aid Routing Layer

Generates a human-readable advisory report explaining:
  - help was requested
  - help was offered
  - a route is possible
  - no one is commanded
  - no debt is created
  - no allocation is enforced

"Need is not debt."
"Help is not command."
"Routing is not allocation."

Invariants: authority=none, moves_money=false, execution_allowed=false,
            advisory=true, mutual_aid_only=true, judgment=false
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

# ── report sections ───────────────────────────────────────────────────────────
MUTUAL_AID_REPORT_SECTIONS: list[dict[str, str]] = [
    {
        "section_id": "help-was-requested",
        "title":      "Help Was Requested",
        "body": (
            "Help requests exist in the record. Participants in Jammy House, D.R.A., "
            "and YacypherPunks have surfaced needs: food support, housing advocacy, "
            "refugee relief, skill exchange. These requests are advisory observations — "
            "Dan-Go records that a need was expressed. Recording a need does not rank "
            "it, prioritise it over others, or impose any obligation on any party. "
            "The request is a signal, not a command."
        ),
        "invariant_demonstrated": "need_creates_debt: false",
    },
    {
        "section_id": "help-was-offered",
        "title":      "Help Was Offered",
        "body": (
            "Offers of help exist in the record. Participants have volunteered meal "
            "preparation, housing advocacy, supply coordination, shelter hosting, and "
            "skill sharing. All offers are voluntary. Recording an offer does not bind "
            "the offerer to fulfil it, give Dan-Go authority over the offerer's capacity, "
            "or create a commitment that can be enforced. The offerer may withdraw at any "
            "time. The offer is a signal of willingness, not a contract."
        ),
        "invariant_demonstrated": "voluntary: true, offer_creates_obligation: false",
    },
    {
        "section_id": "a-route-is-possible",
        "title":      "A Route Is Possible",
        "body": (
            "Where requests and offers share compatible types, availability, and commons "
            "membership, Dan-Go records a possible route. A route is an advisory "
            "observation: this request and this offer appear to overlap. Dan-Go surfaces "
            "the overlap. Whether the participants connect is their decision entirely. "
            "The route does not allocate the offerer's capacity to the requester. "
            "The route does not schedule an exchange. The route does not compel contact."
        ),
        "invariant_demonstrated": "routing_allocates_resources: false, route_compels_exchange: false",
    },
    {
        "section_id": "no-one-is-commanded",
        "title":      "No One Is Commanded",
        "body": (
            "Dan-Go has no authority over any participant. It cannot command a helper "
            "to fulfil an offer. It cannot require a requester to accept a particular "
            "route. It cannot mandate that any exchange take place. The help_is_command: "
            "false invariant is permanent and unconditional. Mutual aid is defined by "
            "its voluntary character. The moment a system commands assistance, it "
            "becomes something other than mutual aid. Dan-Go preserves the voluntary "
            "character of every exchange it observes."
        ),
        "invariant_demonstrated": "help_is_command: false, authority: none",
    },
    {
        "section_id": "no-debt-is-created",
        "title":      "No Debt Is Created",
        "body": (
            "Receiving help through a mutual aid route does not create a debt. The "
            "need_creates_debt: false invariant on every request record makes this "
            "explicit. Mutual aid is not a loan, not a credit, and not a transaction "
            "that produces an obligation for later repayment. A person who requested "
            "food support and received it does not owe help to the person who provided it. "
            "They may choose to participate in other ways — but that participation is "
            "voluntary, not owed. Dan-Go records help received without recording "
            "obligation created."
        ),
        "invariant_demonstrated": "need_creates_debt: false, requester_owes_help_received: false",
    },
    {
        "section_id": "no-allocation-is-enforced",
        "title":      "No Allocation Is Enforced",
        "body": (
            "Dan-Go does not allocate resources. It does not assign a helper's capacity "
            "to a requester. It does not decide who receives help first. It does not "
            "queue requests by urgency and dispatch helpers against them. The "
            "routing_allocates_resources: false invariant is permanent. Allocation "
            "decisions — if any are made — belong to the participants and communities "
            "themselves. Dan-Go records what was requested, what was offered, and where "
            "a possible route exists. The rest is the commons deciding for itself."
        ),
        "invariant_demonstrated": "routing_allocates_resources: false, execution_allowed: false",
    },
]

# ── summary table ─────────────────────────────────────────────────────────────
MUTUAL_AID_SUMMARY: dict[str, object] = {
    "help_requested":                True,
    "help_offered":                  True,
    "routes_possible":               True,
    "any_party_commanded":           False,
    "debt_created":                  False,
    "allocation_enforced":           False,
    "resources_moved":               False,
    "exchange_compelled":            False,
    "participants_decide":           True,
    "offers_are_voluntary":          True,
    "records_are_advisory":          True,
    "records_are_append_only":       True,
    "records_are_contestable":       True,
    "commons_remain_self_governing": True,
}


def load_route_log() -> dict[str, object] | None:
    """Try to load aid route log for report context."""
    route_path = _EXAMPLES / "aid-route.json"
    if route_path.exists():
        return json.loads(route_path.read_text())  # type: ignore[return-value]
    return None


def load_request_registry() -> dict[str, object] | None:
    req_path = _EXAMPLES / "aid-request-registry.json"
    if req_path.exists():
        return json.loads(req_path.read_text())  # type: ignore[return-value]
    return None


def load_offer_registry() -> dict[str, object] | None:
    off_path = _EXAMPLES / "aid-offer-registry.json"
    if off_path.exists():
        return json.loads(off_path.read_text())  # type: ignore[return-value]
    return None


def build_report() -> dict[str, object]:
    """Build the full mutual aid report."""
    routes   = load_route_log()
    requests = load_request_registry()
    offers   = load_offer_registry()

    context: dict[str, object] = {
        "request_count": requests.get("request_count", 4) if requests else 4,
        "offer_count":   offers.get("offer_count", 5)     if offers   else 5,
        "route_count":   routes.get("route_count", 5)     if routes   else 5,
        "source_route_log_id":    routes.get("log_id",      "aid-route-log-001") if routes else "aid-route-log-001",
        "source_request_registry": requests.get("registry_id","aid-request-registry-001") if requests else "aid-request-registry-001",
        "source_offer_registry":   offers.get("registry_id", "aid-offer-registry-001")    if offers   else "aid-offer-registry-001",
    }

    report: dict[str, object] = {
        "record_type":    "mutual_aid_report",
        "report_id":      "mutual-aid-report-001",
        "report_date":    str(date.today()),
        "report_subject": "Mutual Aid Routing Layer — Phase 17",
        "context":        context,
        "section_count":  len(MUTUAL_AID_REPORT_SECTIONS),
        "sections":       MUTUAL_AID_REPORT_SECTIONS,
        "summary_table":  MUTUAL_AID_SUMMARY,
        # invariants
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
        "judgment":                    False,
        "protocol_phrases": [
            "Need is not debt.",
            "Help is not command.",
            "Routing is not allocation.",
            "Dan-Go records mutual aid routes; it does not command or allocate.",
            "Dan-Go observes voluntary cooperation; it does not enforce exchange.",
        ],
    }
    return report


def print_report(report: dict[str, object]) -> None:
    print("=== mutual_aid_report.py ===")
    print(f"  report_id:     {report['report_id']}")
    print(f"  report_date:   {report['report_date']}")
    print(f"  section_count: {report['section_count']}")
    ctx = report["context"]
    print(f"  context: requests={ctx['request_count']}, offers={ctx['offer_count']}, "  # type: ignore[index]
          f"routes={ctx['route_count']}")  # type: ignore[index]
    print("  sections:")
    for s in report["sections"]:  # type: ignore[union-attr]
        print(f"    [{s['section_id']}] {s['title']}")
        print(f"      invariant_demonstrated: {s['invariant_demonstrated']}")
    print("  summary_table:")
    for k, v in report["summary_table"].items():  # type: ignore[union-attr]
        print(f"    {k}: {str(v).lower()}")
    print(f"  authority={report['authority']}, moves_money={report['moves_money']}, "
          f"need_creates_debt={report['need_creates_debt']}")
    print("  Need is not debt.")
    print("  Help is not command.")
    print("  Routing is not allocation.")


def save_report(report: dict[str, object]) -> Path:
    _EXAMPLES.mkdir(parents=True, exist_ok=True)
    out = _EXAMPLES / "mutual-aid-report.json"
    out.write_text(json.dumps(report, indent=2))
    print(f"  saved → {out.relative_to(_REPO_ROOT)}")
    return out


if __name__ == "__main__":
    report = build_report()
    print_report(report)
    if "--save" in sys.argv:
        save_report(report)
