"""
relief_case_registry.py — Phase 18: Relief Case Memory Layer

Dan-Go records relief cases linked to prior aid routes (Phase 17).
A relief case is an advisory observation of what followed a route suggestion.
Recording a case does not certify rescue, judge outcomes, or create authority.

"Relief is not proof."
"Outcome is not judgment."
"Care memory is not control."

Invariants:
  authority: none
  execution_allowed: false
  moves_money: false
  credit_issued: false
  hard_enforcement: false
  advisory: true
  relief_memory_only: true
  append_only: true
  contestable: true
  reopenable: true
  relief_is_proof: false
  outcome_is_judgment: false
  care_memory_controls: false
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import date

# ── paths ─────────────────────────────────────────────────────────────────────
_SCRIPT_DIR  = Path(__file__).resolve().parent
_REPO_ROOT   = _SCRIPT_DIR.parents[4]
_EXAMPLES    = _SCRIPT_DIR.parent / "examples"
_AID_EXAMPLES = _REPO_ROOT / "bridge" / "gitsea" / "mutual_aid" / "examples"

# ── case types ────────────────────────────────────────────────────────────────
CASE_TYPES = {
    "food_support_followup":    "Follow-up observation after a food support route.",
    "housing_support_followup": "Follow-up observation after a housing support route.",
    "refugee_relief_followup":  "Follow-up observation after a refugee relief route.",
    "skill_exchange_followup":  "Follow-up observation after a skill exchange route.",
    "shelter_followup":         "Follow-up observation after a shelter hosting route.",
    "supply_followup":          "Follow-up observation after a supply sharing route.",
    "general_followup":         "General follow-up observation after an aid route.",
}

# ── case statuses ─────────────────────────────────────────────────────────────
CASE_STATUSES = {
    "observed":    "Case outcome has been observed and recorded.",
    "pending":     "Route was suggested; outcome not yet observed.",
    "partial":     "Partial assistance was observed.",
    "completed":   "Full assistance was observed to have occurred.",
    "unresolved":  "Route was suggested; no outcome observed.",
    "reopened":    "Case was reopened after initial recording.",
    "withdrawn":   "Case observation was withdrawn by the recorder.",
}

# ── default cases — linked to Phase 17 route IDs ─────────────────────────────
DEFAULT_CASES: list[dict[str, object]] = [
    {
        "relief_case_id": "relief-case-001",
        "route_id":       "aid-route-001",
        "commons_id":     "jammy-house-001",
        "case_type":      "food_support_followup",
        "case_status":    "observed",
        "description":    "Meal preparation offer was observed to have been taken up. "
                          "Food support reached household.",
    },
    {
        "relief_case_id": "relief-case-002",
        "route_id":       "aid-route-002",
        "commons_id":     "jammy-house-001",
        "case_type":      "housing_support_followup",
        "case_status":    "partial",
        "description":    "Housing advocacy support was partially observed. "
                          "Tenancy negotiation initiated; outcome still unresolved.",
    },
    {
        "relief_case_id": "relief-case-003",
        "route_id":       "aid-route-003",
        "commons_id":     "dra-001",
        "case_type":      "refugee_relief_followup",
        "case_status":    "observed",
        "description":    "Supply coordination was observed for displaced family. "
                          "Basic supplies reached the household.",
    },
    {
        "relief_case_id": "relief-case-004",
        "route_id":       "aid-route-004",
        "commons_id":     "dra-001",
        "case_type":      "shelter_followup",
        "case_status":    "completed",
        "description":    "Shelter hosting was observed to have been accepted. "
                          "Family housed for 5 days.",
    },
    {
        "relief_case_id": "relief-case-005",
        "route_id":       "aid-route-005",
        "commons_id":     "yacypherpunks-001",
        "case_type":      "skill_exchange_followup",
        "case_status":    "pending",
        "description":    "Skill exchange route suggested. Outcome not yet observed.",
    },
]

# ── invariants ────────────────────────────────────────────────────────────────
RELIEF_INVARIANTS: dict[str, object] = {
    "authority":            "none",
    "execution_allowed":    False,
    "moves_money":          False,
    "credit_issued":        False,
    "hard_enforcement":     False,
    "advisory":             True,
    "relief_memory_only":   True,
    "append_only":          True,
    "contestable":          True,
    "reopenable":           True,
    "relief_is_proof":      False,
    "outcome_is_judgment":  False,
    "care_memory_controls": False,
}


def load_routes() -> dict[str, dict[str, object]]:
    """Try to load Phase 17 aid routes indexed by route_id."""
    route_path = _AID_EXAMPLES / "aid-route.json"
    if route_path.exists():
        data = json.loads(route_path.read_text())
        return {str(r["route_id"]): r for r in data.get("routes", [])}
    return {}


def build_relief_case(
    relief_case_id: str,
    route_id:       str,
    commons_id:     str,
    case_type:      str,
    case_status:    str,
    description:    str,
    route_summary:  dict[str, object] | None = None,
) -> dict[str, object]:
    """Build one advisory relief case record."""
    if case_type not in CASE_TYPES:
        case_type = "general_followup"
    if case_status not in CASE_STATUSES:
        case_status = "pending"

    record: dict[str, object] = {
        "record_type":           "relief_case",
        "relief_case_id":        relief_case_id,
        "case_date":             str(date.today()),
        "route_id":              route_id,
        "commons_id":            commons_id,
        "case_type":             case_type,
        "type_note":             CASE_TYPES[case_type],
        "case_status":           case_status,
        "status_note":           CASE_STATUSES[case_status],
        "description":           description,
        # invariants
        **RELIEF_INVARIANTS,
        # explicit case-level invariants
        "certifies_rescue":      False,
        "certifies_success":     False,
        "ranks_suffering":       False,
        "case_creates_debt":     False,
        "case_controls_parties": False,
        # optional route context
        "route_summary":         route_summary or {},
        # protocol phrases
        "protocol_phrases": [
            "Relief is not proof.",
            "Outcome is not judgment.",
            "Care memory is not control.",
        ],
    }
    return record


def build_case_registry(
    cases: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    """Build the full relief case registry."""
    if cases is None:
        cases = DEFAULT_CASES

    route_index = load_routes()

    entries: list[dict[str, object]] = []
    for c in cases:
        rid = str(c["route_id"])
        route_rec = route_index.get(rid)
        route_summary: dict[str, object] = {}
        if route_rec:
            route_summary = {
                "route_status":  route_rec.get("route_status"),
                "match_reasons": route_rec.get("match_reasons"),
            }
        entries.append(build_relief_case(
            relief_case_id = str(c["relief_case_id"]),
            route_id       = rid,
            commons_id     = str(c["commons_id"]),
            case_type      = str(c["case_type"]),
            case_status    = str(c["case_status"]),
            description    = str(c["description"]),
            route_summary  = route_summary,
        ))

    # status counts
    status_counts: dict[str, int] = {}
    for e in entries:
        s = str(e["case_status"])
        status_counts[s] = status_counts.get(s, 0) + 1

    registry: dict[str, object] = {
        "record_type":     "relief_case_registry",
        "registry_id":     "relief-case-registry-001",
        "registry_date":   str(date.today()),
        "case_count":      len(entries),
        "status_summary":  status_counts,
        "cases":           entries,
        **RELIEF_INVARIANTS,
        "protocol_phrases": [
            "Relief is not proof.",
            "Outcome is not judgment.",
            "Care memory is not control.",
            "Dan-Go records relief cases; it does not certify rescue or judge outcomes.",
        ],
    }
    return registry


def print_registry(reg: dict[str, object]) -> None:
    print("=== relief_case_registry.py ===")
    print(f"  registry_id:    {reg['registry_id']}")
    print(f"  case_count:     {reg['case_count']}")
    print(f"  status_summary: {reg['status_summary']}")
    for c in reg["cases"]:  # type: ignore[union-attr]
        print(f"  [{c['relief_case_id']}] route={c['route_id']} "
              f"type={c['case_type']} status={c['case_status']} "
              f"relief_is_proof={c['relief_is_proof']}")
    print(f"  authority={reg['authority']}, moves_money={reg['moves_money']}, "
          f"relief_is_proof={reg['relief_is_proof']}")
    print("  Relief is not proof.")
    print("  Outcome is not judgment.")


def save_registry(reg: dict[str, object]) -> Path:
    _EXAMPLES.mkdir(parents=True, exist_ok=True)
    out = _EXAMPLES / "relief-case-registry.json"
    out.write_text(json.dumps(reg, indent=2))
    print(f"  saved → {out.relative_to(_REPO_ROOT)}")
    return out


if __name__ == "__main__":
    reg = build_case_registry()
    print_registry(reg)
    if "--save" in sys.argv:
        save_registry(reg)
