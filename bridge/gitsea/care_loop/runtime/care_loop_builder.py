"""
care_loop_builder.py — Phase 19: Care Loop Reopen Layer

Dan-Go builds a care loop by combining Phase 18 relief case, outcome, and
care memory records with Phase 19 reopen and follow-up records into a single
append-only advisory loop entry. The loop is the complete cross-phase care
record for one case from request to reopen.

"Reopen is not failure."
"Follow-up is not blame."
"Care loop is not obligation."

Invariants:
  authority: none
  execution_allowed: false
  moves_money: false
  credit_issued: false
  hard_enforcement: false
  advisory: true
  care_loop_only: true
  append_only: true
  contestable: true
  reopenable: true
  reopen_is_failure: false
  followup_is_blame: false
  care_loop_creates_obligation: false
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import date

# ── paths ─────────────────────────────────────────────────────────────────────
_SCRIPT_DIR      = Path(__file__).resolve().parent
_REPO_ROOT       = _SCRIPT_DIR.parents[4]
_EXAMPLES        = _SCRIPT_DIR.parent / "examples"
_RELIEF_EXAMPLES = _REPO_ROOT / "bridge" / "gitsea" / "relief" / "examples"
_AID_EXAMPLES    = _REPO_ROOT / "bridge" / "gitsea" / "mutual_aid" / "examples"

# ── loop event vocabulary ─────────────────────────────────────────────────────
LOOP_EVENTS = {
    # Phase 17
    "route_suggested":          "Aid route suggested (Phase 17)",
    # Phase 18
    "relief_case_recorded":     "Relief case recorded (Phase 18)",
    "outcome_observed":         "Outcome observed (Phase 18)",
    "care_memory_built":        "Care memory built (Phase 18)",
    # Phase 19
    "followup_need_observed":   "Follow-up need observed (Phase 19)",
    "reopen_requested":         "Reopen requested (Phase 19)",
    "reopen_acknowledged":      "Reopen acknowledged (Phase 19)",
    "reopen_active":            "Reopen active (Phase 19)",
    "reopen_resolved":          "Reopen resolved (Phase 19)",
}

# ── loop statuses ─────────────────────────────────────────────────────────────
LOOP_STATUSES = {
    "open":       "Care loop is open; reopen or follow-up is in progress.",
    "active":     "Reopen is active; follow-up care is being coordinated.",
    "resolved":   "Care loop resolved; situation observed as stable.",
    "ongoing":    "Care loop is ongoing; need is recurring or continuous.",
    "closed":     "Care loop closed; no further follow-up observed.",
    "contested":  "Care loop record has been contested by a participant.",
}

# ── default care loops — one per reopen ──────────────────────────────────────
DEFAULT_LOOPS: list[dict[str, object]] = [
    {
        "care_loop_id":  "care-loop-001",
        "reopen_id":     "care-reopen-001",
        "relief_case_id":"relief-case-002",
        "route_id":      "aid-route-002",
        "followup_id":   "followup-001",
        "commons_id":    "jammy-house-001",
        "loop_status":   "open",
        "events": [
            "route_suggested",
            "relief_case_recorded",
            "outcome_observed",
            "care_memory_built",
            "followup_need_observed",
            "reopen_requested",
        ],
    },
    {
        "care_loop_id":  "care-loop-002",
        "reopen_id":     "care-reopen-002",
        "relief_case_id":"relief-case-003",
        "route_id":      "aid-route-003",
        "followup_id":   "followup-002",
        "commons_id":    "dra-001",
        "loop_status":   "ongoing",
        "events": [
            "route_suggested",
            "relief_case_recorded",
            "outcome_observed",
            "care_memory_built",
            "followup_need_observed",
            "reopen_requested",
            "reopen_active",
        ],
    },
    {
        "care_loop_id":  "care-loop-003",
        "reopen_id":     "care-reopen-003",
        "relief_case_id":"relief-case-001",
        "route_id":      "aid-route-001",
        "followup_id":   "followup-003",
        "commons_id":    "jammy-house-001",
        "loop_status":   "open",
        "events": [
            "route_suggested",
            "relief_case_recorded",
            "outcome_observed",
            "care_memory_built",
            "followup_need_observed",
            "reopen_requested",
        ],
    },
    {
        "care_loop_id":  "care-loop-004",
        "reopen_id":     "care-reopen-004",
        "relief_case_id":"relief-case-005",
        "route_id":      "aid-route-005",
        "followup_id":   "followup-004",
        "commons_id":    "yacypherpunks-001",
        "loop_status":   "open",
        "events": [
            "route_suggested",
            "relief_case_recorded",
            "outcome_observed",
            "care_memory_built",
            "followup_need_observed",
            "reopen_requested",
            "reopen_acknowledged",
        ],
    },
]

# ── invariants ────────────────────────────────────────────────────────────────
CARE_LOOP_INVARIANTS: dict[str, object] = {
    "authority":                  "none",
    "execution_allowed":          False,
    "moves_money":                False,
    "credit_issued":              False,
    "hard_enforcement":           False,
    "advisory":                   True,
    "care_loop_only":             True,
    "append_only":                True,
    "contestable":                True,
    "reopenable":                 True,
    "reopen_is_failure":          False,
    "followup_is_blame":          False,
    "care_loop_creates_obligation": False,
}


def _load_json_index(path: Path, id_field: str) -> dict[str, dict[str, object]]:
    if path.exists():
        data = json.loads(path.read_text())
        # handle both list-at-root and key-in-dict patterns
        for key in ("cases", "reopens", "followups", "snapshots", "routes",
                    "memories", "records"):
            items = data.get(key)
            if isinstance(items, list):
                return {str(item[id_field]): item for item in items if id_field in item}
        # fallback: top-level list
        if isinstance(data, list):
            return {str(item[id_field]): item for item in data if id_field in item}
    return {}


def build_care_loop(
    care_loop_id:   str,
    reopen_id:      str,
    relief_case_id: str,
    route_id:       str,
    followup_id:    str,
    commons_id:     str,
    loop_status:    str,
    raw_events:     list[str],
    reopen_summary: dict[str, object] | None = None,
    followup_summary: dict[str, object] | None = None,
    case_summary:   dict[str, object] | None = None,
) -> dict[str, object]:
    """Build one care loop entry."""
    if loop_status not in LOOP_STATUSES:
        loop_status = "open"

    valid_events = [e for e in raw_events if e in LOOP_EVENTS]
    event_notes  = {e: LOOP_EVENTS[e] for e in valid_events}
    loop_complete = (
        "route_suggested" in valid_events
        and "relief_case_recorded" in valid_events
        and "care_memory_built" in valid_events
        and "reopen_requested" in valid_events
    )

    record: dict[str, object] = {
        "record_type":              "care_loop",
        "care_loop_id":             care_loop_id,
        "loop_date":                str(date.today()),
        "reopen_id":                reopen_id,
        "relief_case_id":           relief_case_id,
        "route_id":                 route_id,
        "followup_id":              followup_id,
        "commons_id":               commons_id,
        "loop_status":              loop_status,
        "status_note":              LOOP_STATUSES[loop_status],
        "events":                   valid_events,
        "event_notes":              event_notes,
        "loop_complete":            loop_complete,
        "reopen_summary":           reopen_summary or {},
        "followup_summary":         followup_summary or {},
        "case_summary":             case_summary or {},
        # invariants
        **CARE_LOOP_INVARIANTS,
        # explicit loop-level invariants
        "loop_judges_participants":    False,
        "loop_compels_new_aid":        False,
        "loop_creates_debt":           False,
        "loop_certifies_resolution":   False,
        # protocol phrases
        "protocol_phrases": [
            "Reopen is not failure.",
            "Follow-up is not blame.",
            "Care loop is not obligation.",
        ],
    }
    return record


def build_loop_log(
    loops: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    """Build the full care loop log."""
    if loops is None:
        loops = DEFAULT_LOOPS

    # load Phase 18 and Phase 19 context
    reopen_idx   = _load_json_index(_EXAMPLES / "care-reopen-registry.json", "reopen_id")
    followup_idx = _load_json_index(_EXAMPLES / "followup-need-snapshot.json", "followup_id")
    case_idx     = _load_json_index(_RELIEF_EXAMPLES / "relief-case-registry.json", "relief_case_id")

    entries: list[dict[str, object]] = []
    for lp in loops:
        rid  = str(lp["reopen_id"])
        fid  = str(lp["followup_id"])
        cid  = str(lp["relief_case_id"])

        reopen_rec  = reopen_idx.get(rid, {})
        followup_rec = followup_idx.get(fid, {})
        case_rec    = case_idx.get(cid, {})

        reopen_summary: dict[str, object] = {
            "reopen_reason": reopen_rec.get("reopen_reason"),
            "reopen_status": reopen_rec.get("reopen_status"),
        } if reopen_rec else {}
        followup_summary: dict[str, object] = {
            "need_type": followup_rec.get("need_type"),
            "urgency":   followup_rec.get("urgency"),
        } if followup_rec else {}
        case_summary: dict[str, object] = {
            "case_type":   case_rec.get("case_type"),
            "case_status": case_rec.get("case_status"),
        } if case_rec else {}

        entries.append(build_care_loop(
            care_loop_id     = str(lp["care_loop_id"]),
            reopen_id        = rid,
            relief_case_id   = cid,
            route_id         = str(lp["route_id"]),
            followup_id      = fid,
            commons_id       = str(lp["commons_id"]),
            loop_status      = str(lp["loop_status"]),
            raw_events       = list(lp.get("events", [])),  # type: ignore[arg-type]
            reopen_summary   = reopen_summary,
            followup_summary = followup_summary,
            case_summary     = case_summary,
        ))

    status_counts: dict[str, int] = {}
    for e in entries:
        s = str(e["loop_status"])
        status_counts[s] = status_counts.get(s, 0) + 1

    complete_count = sum(1 for e in entries if e.get("loop_complete"))

    log: dict[str, object] = {
        "record_type":    "care_loop_log",
        "log_id":         "care-loop-log-001",
        "log_date":       str(date.today()),
        "loop_count":     len(entries),
        "complete_count": complete_count,
        "status_summary": status_counts,
        "loops":          entries,
        **CARE_LOOP_INVARIANTS,
        "protocol_phrases": [
            "Reopen is not failure.",
            "Follow-up is not blame.",
            "Care loop is not obligation.",
            "Dan-Go builds care loops from Phase 17–19 records; it does not compel resolution.",
        ],
    }
    return log


def print_log(log: dict[str, object]) -> None:
    print("=== care_loop_builder.py ===")
    print(f"  log_id:         {log['log_id']}")
    print(f"  loop_count:     {log['loop_count']}")
    print(f"  complete_count: {log['complete_count']}")
    print(f"  status_summary: {log['status_summary']}")
    for lp in log["loops"]:  # type: ignore[union-attr]
        print(f"  [{lp['care_loop_id']}] case={lp['relief_case_id']} "
              f"status={lp['loop_status']} complete={lp['loop_complete']} "
              f"events={lp['events']}")
        print(f"    reopen_is_failure={lp['reopen_is_failure']} "
              f"care_loop_creates_obligation={lp['care_loop_creates_obligation']}")
    print(f"  authority={log['authority']}, care_loop_creates_obligation="
          f"{log['care_loop_creates_obligation']}")
    print("  Reopen is not failure.")
    print("  Care loop is not obligation.")


def save_log(log: dict[str, object]) -> Path:
    _EXAMPLES.mkdir(parents=True, exist_ok=True)
    out = _EXAMPLES / "care-loop.json"
    out.write_text(json.dumps(log, indent=2))
    print(f"  saved → {out.relative_to(_REPO_ROOT)}")
    return out


if __name__ == "__main__":
    log = build_loop_log()
    print_log(log)
    if "--save" in sys.argv:
        save_log(log)
