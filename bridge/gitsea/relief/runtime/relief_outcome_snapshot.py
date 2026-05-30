"""
relief_outcome_snapshot.py — Phase 18: Relief Case Memory Layer

Dan-Go records observable outcomes of relief cases without judging them.
An outcome snapshot captures what was observed — not what was certified,
not what was deserved, not what should have happened.

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
_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT   = _SCRIPT_DIR.parents[4]
_EXAMPLES    = _SCRIPT_DIR.parent / "examples"

# ── observed outcome types ────────────────────────────────────────────────────
OBSERVED_OUTCOMES = {
    "meal_was_offered":           "A meal or food item was observed to have been offered.",
    "meal_was_received":          "A meal or food item was observed to have been received.",
    "shelter_was_offered":        "Temporary shelter was observed to have been offered.",
    "shelter_was_accepted":       "Temporary shelter was observed to have been accepted.",
    "housing_contact_made":       "Contact for housing advocacy was observed to have occurred.",
    "negotiation_initiated":      "A negotiation process was observed to have been initiated.",
    "supplies_reached_household": "Supplies were observed to have reached the household.",
    "skill_session_scheduled":    "A skill exchange session was observed to have been scheduled.",
    "route_not_taken":            "Route was suggested; no uptake was observed.",
    "partial_assistance":         "Partial assistance was observed without full resolution.",
    "outcome_unknown":            "Route outcome is not yet observable.",
}

# ── outcome statuses ──────────────────────────────────────────────────────────
OUTCOME_STATUSES = {
    "full":      "Observed assistance appears to have fully addressed the request.",
    "partial":   "Observed assistance addressed part of the request.",
    "pending":   "Outcome not yet observed.",
    "unresolved":"Assistance was attempted; request remains unresolved.",
    "declined":  "Route was declined by one or both parties.",
    "unknown":   "Outcome cannot be determined from current observation.",
}

# ── default outcome snapshots — linked to Phase 18 case IDs ──────────────────
DEFAULT_OUTCOMES: list[dict[str, object]] = [
    {
        "snapshot_id":       "outcome-snap-001",
        "relief_case_id":    "relief-case-001",
        "observed_outcome":  "meal_was_received",
        "outcome_status":    "full",
        "observation_note":  "Household member confirmed meal was received. "
                             "Dan-Go records the observation; does not certify it.",
    },
    {
        "snapshot_id":       "outcome-snap-002",
        "relief_case_id":    "relief-case-002",
        "observed_outcome":  "negotiation_initiated",
        "outcome_status":    "partial",
        "observation_note":  "Advocacy contact observed. Tenancy outcome not yet resolved. "
                             "Case remains open.",
    },
    {
        "snapshot_id":       "outcome-snap-003",
        "relief_case_id":    "relief-case-003",
        "observed_outcome":  "supplies_reached_household",
        "outcome_status":    "full",
        "observation_note":  "Supply coordination observed for displaced family. "
                             "Dan-Go records; does not certify rescue.",
    },
    {
        "snapshot_id":       "outcome-snap-004",
        "relief_case_id":    "relief-case-004",
        "observed_outcome":  "shelter_was_accepted",
        "outcome_status":    "full",
        "observation_note":  "Shelter hosting observed and completed. "
                             "Family housed for 5 days. Record is advisory.",
    },
    {
        "snapshot_id":       "outcome-snap-005",
        "relief_case_id":    "relief-case-005",
        "observed_outcome":  "outcome_unknown",
        "outcome_status":    "pending",
        "observation_note":  "Skill exchange route suggested. No outcome yet observable.",
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


def load_cases() -> dict[str, dict[str, object]]:
    """Try to load Phase 18 relief cases indexed by relief_case_id."""
    case_path = _EXAMPLES / "relief-case-registry.json"
    if case_path.exists():
        data = json.loads(case_path.read_text())
        return {str(c["relief_case_id"]): c for c in data.get("cases", [])}
    return {}


def build_outcome_snapshot(
    snapshot_id:      str,
    relief_case_id:   str,
    observed_outcome: str,
    outcome_status:   str,
    observation_note: str,
    case_summary:     dict[str, object] | None = None,
) -> dict[str, object]:
    """Build one advisory outcome snapshot."""
    if observed_outcome not in OBSERVED_OUTCOMES:
        observed_outcome = "outcome_unknown"
    if outcome_status not in OUTCOME_STATUSES:
        outcome_status = "unknown"

    record: dict[str, object] = {
        "record_type":       "relief_outcome_snapshot",
        "snapshot_id":       snapshot_id,
        "snapshot_date":     str(date.today()),
        "relief_case_id":    relief_case_id,
        "observed_outcome":  observed_outcome,
        "outcome_note":      OBSERVED_OUTCOMES[observed_outcome],
        "outcome_status":    outcome_status,
        "status_note":       OUTCOME_STATUSES[outcome_status],
        "observation_note":  observation_note,
        # invariants
        **RELIEF_INVARIANTS,
        # explicit snapshot-level invariants
        "certifies_success":          False,
        "certifies_rescue":           False,
        "certifies_failure":          False,
        "ranks_outcome":              False,
        "observation_is_endorsement": False,
        "case_summary":               case_summary or {},
        # protocol phrases
        "protocol_phrases": [
            "Relief is not proof.",
            "Outcome is not judgment.",
            "Care memory is not control.",
        ],
    }
    return record


def build_outcome_snapshot_log(
    outcomes: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    """Build the full outcome snapshot log."""
    if outcomes is None:
        outcomes = DEFAULT_OUTCOMES

    case_index = load_cases()

    entries: list[dict[str, object]] = []
    for o in outcomes:
        cid = str(o["relief_case_id"])
        case_rec = case_index.get(cid)
        case_summary: dict[str, object] = {}
        if case_rec:
            case_summary = {
                "case_type":   case_rec.get("case_type"),
                "case_status": case_rec.get("case_status"),
                "route_id":    case_rec.get("route_id"),
            }
        entries.append(build_outcome_snapshot(
            snapshot_id      = str(o["snapshot_id"]),
            relief_case_id   = cid,
            observed_outcome = str(o["observed_outcome"]),
            outcome_status   = str(o["outcome_status"]),
            observation_note = str(o["observation_note"]),
            case_summary     = case_summary,
        ))

    # aggregate outcome status counts
    status_counts: dict[str, int] = {}
    for e in entries:
        s = str(e["outcome_status"])
        status_counts[s] = status_counts.get(s, 0) + 1

    log: dict[str, object] = {
        "record_type":    "relief_outcome_snapshot_log",
        "log_id":         "outcome-snapshot-log-001",
        "log_date":       str(date.today()),
        "snapshot_count": len(entries),
        "status_summary": status_counts,
        "snapshots":      entries,
        **RELIEF_INVARIANTS,
        "protocol_phrases": [
            "Relief is not proof.",
            "Outcome is not judgment.",
            "Care memory is not control.",
            "Dan-Go records outcomes; it does not certify them or rank them.",
        ],
    }
    return log


def print_log(log: dict[str, object]) -> None:
    print("=== relief_outcome_snapshot.py ===")
    print(f"  log_id:          {log['log_id']}")
    print(f"  snapshot_count:  {log['snapshot_count']}")
    print(f"  status_summary:  {log['status_summary']}")
    for s in log["snapshots"]:  # type: ignore[union-attr]
        print(f"  [{s['snapshot_id']}] case={s['relief_case_id']} "
              f"outcome={s['observed_outcome']} status={s['outcome_status']} "
              f"outcome_is_judgment={s['outcome_is_judgment']}")
    print(f"  authority={log['authority']}, outcome_is_judgment={log['outcome_is_judgment']}, "
          f"certifies_rescue — absent")
    print("  Outcome is not judgment.")
    print("  Relief is not proof.")


def save_log(log: dict[str, object]) -> Path:
    _EXAMPLES.mkdir(parents=True, exist_ok=True)
    out = _EXAMPLES / "relief-outcome-snapshot.json"
    out.write_text(json.dumps(log, indent=2))
    print(f"  saved → {out.relative_to(_REPO_ROOT)}")
    return out


if __name__ == "__main__":
    log = build_outcome_snapshot_log()
    print_log(log)
    if "--save" in sys.argv:
        save_log(log)
