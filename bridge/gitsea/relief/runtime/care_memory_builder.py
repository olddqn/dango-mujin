"""
care_memory_builder.py — Phase 18: Relief Case Memory Layer

Dan-Go builds care memory by combining Phase 17 route records, Phase 18 case
records, and Phase 18 outcome snapshots into a single, append-only advisory
memory entry per relief case. Care memory is a complete cross-phase record.
It does not control any party.

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
_SCRIPT_DIR   = Path(__file__).resolve().parent
_REPO_ROOT    = _SCRIPT_DIR.parents[4]
_EXAMPLES     = _SCRIPT_DIR.parent / "examples"
_AID_EXAMPLES = _REPO_ROOT / "bridge" / "gitsea" / "mutual_aid" / "examples"

# ── memory statuses ───────────────────────────────────────────────────────────
MEMORY_STATUSES = {
    "recorded":   "Care memory has been built and recorded.",
    "incomplete": "Some phase records are missing; memory is partial.",
    "reopened":   "Care memory was reopened after initial recording.",
    "contested":  "Care memory entry has been contested by a participant.",
}

# ── default care memory entries — one per relief case ────────────────────────
DEFAULT_MEMORIES: list[dict[str, object]] = [
    {
        "care_memory_id":  "care-memory-001",
        "relief_case_id":  "relief-case-001",
        "route_id":        "aid-route-001",
        "snapshot_id":     "outcome-snap-001",
        "memory_status":   "recorded",
        "commons_id":      "jammy-house-001",
        "phase_17_present": True,
        "phase_18_case_present": True,
        "phase_18_outcome_present": True,
    },
    {
        "care_memory_id":  "care-memory-002",
        "relief_case_id":  "relief-case-002",
        "route_id":        "aid-route-002",
        "snapshot_id":     "outcome-snap-002",
        "memory_status":   "recorded",
        "commons_id":      "jammy-house-001",
        "phase_17_present": True,
        "phase_18_case_present": True,
        "phase_18_outcome_present": True,
    },
    {
        "care_memory_id":  "care-memory-003",
        "relief_case_id":  "relief-case-003",
        "route_id":        "aid-route-003",
        "snapshot_id":     "outcome-snap-003",
        "memory_status":   "recorded",
        "commons_id":      "dra-001",
        "phase_17_present": True,
        "phase_18_case_present": True,
        "phase_18_outcome_present": True,
    },
    {
        "care_memory_id":  "care-memory-004",
        "relief_case_id":  "relief-case-004",
        "route_id":        "aid-route-004",
        "snapshot_id":     "outcome-snap-004",
        "memory_status":   "recorded",
        "commons_id":      "dra-001",
        "phase_17_present": True,
        "phase_18_case_present": True,
        "phase_18_outcome_present": True,
    },
    {
        "care_memory_id":  "care-memory-005",
        "relief_case_id":  "relief-case-005",
        "route_id":        "aid-route-005",
        "snapshot_id":     "outcome-snap-005",
        "memory_status":   "incomplete",
        "commons_id":      "yacypherpunks-001",
        "phase_17_present": True,
        "phase_18_case_present": True,
        "phase_18_outcome_present": True,
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
    case_path = _EXAMPLES / "relief-case-registry.json"
    if case_path.exists():
        data = json.loads(case_path.read_text())
        return {str(c["relief_case_id"]): c for c in data.get("cases", [])}
    return {}


def load_outcomes() -> dict[str, dict[str, object]]:
    snap_path = _EXAMPLES / "relief-outcome-snapshot.json"
    if snap_path.exists():
        data = json.loads(snap_path.read_text())
        return {str(s["relief_case_id"]): s for s in data.get("snapshots", [])}
    return {}


def load_routes() -> dict[str, dict[str, object]]:
    route_path = _AID_EXAMPLES / "aid-route.json"
    if route_path.exists():
        data = json.loads(route_path.read_text())
        return {str(r["route_id"]): r for r in data.get("routes", [])}
    return {}


def build_care_memory(
    care_memory_id:           str,
    relief_case_id:           str,
    route_id:                 str,
    snapshot_id:              str,
    memory_status:            str,
    commons_id:               str,
    phase_17_present:         bool,
    phase_18_case_present:    bool,
    phase_18_outcome_present: bool,
    case_record:              dict[str, object] | None = None,
    outcome_record:           dict[str, object] | None = None,
    route_record:             dict[str, object] | None = None,
) -> dict[str, object]:
    """Build one care memory entry combining Phase 17–18 records."""
    if memory_status not in MEMORY_STATUSES:
        memory_status = "recorded"

    care_history_complete = (
        phase_17_present and phase_18_case_present and phase_18_outcome_present
    )

    # pull key fields from records if available
    observed_outcome = None
    outcome_status   = None
    case_type        = None
    case_status      = None
    route_status     = None

    if outcome_record:
        observed_outcome = outcome_record.get("observed_outcome")
        outcome_status   = outcome_record.get("outcome_status")
    if case_record:
        case_type   = case_record.get("case_type")
        case_status = case_record.get("case_status")
    if route_record:
        route_status = route_record.get("route_status")

    record: dict[str, object] = {
        "record_type":               "care_memory",
        "care_memory_id":            care_memory_id,
        "memory_date":               str(date.today()),
        "relief_case_id":            relief_case_id,
        "route_id":                  route_id,
        "snapshot_id":               snapshot_id,
        "commons_id":                commons_id,
        "memory_status":             memory_status,
        "status_note":               MEMORY_STATUSES[memory_status],
        # phase presence flags
        "phase_17_route_present":    phase_17_present,
        "phase_18_case_present":     phase_18_case_present,
        "phase_18_outcome_present":  phase_18_outcome_present,
        "care_history_complete":     care_history_complete,
        # summary fields from linked records
        "route_status":              route_status,
        "case_type":                 case_type,
        "case_status":               case_status,
        "observed_outcome":          observed_outcome,
        "outcome_status":            outcome_status,
        # invariants
        **RELIEF_INVARIANTS,
        # explicit memory-level invariants
        "care_memory_controls":      False,
        "memory_creates_obligation": False,
        "memory_certifies_outcome":  False,
        "memory_ranks_suffering":    False,
        # protocol phrases
        "protocol_phrases": [
            "Relief is not proof.",
            "Outcome is not judgment.",
            "Care memory is not control.",
        ],
    }
    return record


def build_memory_log(
    memories: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    """Build the full care memory log."""
    if memories is None:
        memories = DEFAULT_MEMORIES

    case_index    = load_cases()
    outcome_index = load_outcomes()
    route_index   = load_routes()

    entries: list[dict[str, object]] = []
    for m in memories:
        cid = str(m["relief_case_id"])
        rid = str(m["route_id"])
        entries.append(build_care_memory(
            care_memory_id           = str(m["care_memory_id"]),
            relief_case_id           = cid,
            route_id                 = rid,
            snapshot_id              = str(m["snapshot_id"]),
            memory_status            = str(m["memory_status"]),
            commons_id               = str(m["commons_id"]),
            phase_17_present         = bool(m.get("phase_17_present", True)),
            phase_18_case_present    = bool(m.get("phase_18_case_present", True)),
            phase_18_outcome_present = bool(m.get("phase_18_outcome_present", True)),
            case_record              = case_index.get(cid),
            outcome_record           = outcome_index.get(cid),
            route_record             = route_index.get(rid),
        ))

    complete_count = sum(1 for e in entries if e.get("care_history_complete"))

    log: dict[str, object] = {
        "record_type":            "care_memory_log",
        "log_id":                 "care-memory-log-001",
        "log_date":               str(date.today()),
        "memory_count":           len(entries),
        "complete_count":         complete_count,
        "memories":               entries,
        **RELIEF_INVARIANTS,
        "protocol_phrases": [
            "Relief is not proof.",
            "Outcome is not judgment.",
            "Care memory is not control.",
            "Dan-Go builds care memory from Phase 17–18 records; it does not control any party.",
        ],
    }
    return log


def print_log(log: dict[str, object]) -> None:
    print("=== care_memory_builder.py ===")
    print(f"  log_id:         {log['log_id']}")
    print(f"  memory_count:   {log['memory_count']}")
    print(f"  complete_count: {log['complete_count']}")
    for m in log["memories"]:  # type: ignore[union-attr]
        print(f"  [{m['care_memory_id']}] case={m['relief_case_id']} "
              f"route={m['route_id']} status={m['memory_status']} "
              f"complete={m['care_history_complete']} "
              f"care_memory_controls={m['care_memory_controls']}")
    print(f"  authority={log['authority']}, care_memory_controls={log['care_memory_controls']}, "
          f"outcome_is_judgment={log['outcome_is_judgment']}")
    print("  Care memory is not control.")


def save_log(log: dict[str, object]) -> Path:
    _EXAMPLES.mkdir(parents=True, exist_ok=True)
    out = _EXAMPLES / "care-memory.json"
    out.write_text(json.dumps(log, indent=2))
    print(f"  saved → {out.relative_to(_REPO_ROOT)}")
    return out


if __name__ == "__main__":
    log = build_memory_log()
    print_log(log)
    if "--save" in sys.argv:
        save_log(log)
