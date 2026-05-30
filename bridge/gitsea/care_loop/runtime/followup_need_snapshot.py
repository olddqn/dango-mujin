"""
followup_need_snapshot.py — Phase 19: Care Loop Reopen Layer

Dan-Go records observed follow-up needs without assigning blame. A follow-up
need is an advisory observation that more care may be useful. Recording a
follow-up need does not indict the original helper, judge the original
response, or demand new action.

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
_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT   = _SCRIPT_DIR.parents[4]
_EXAMPLES    = _SCRIPT_DIR.parent / "examples"

# ── follow-up need types ──────────────────────────────────────────────────────
FOLLOWUP_NEED_TYPES = {
    "second_contact_needed":       "A second point of contact may be useful.",
    "ongoing_food_coordination":   "Food support may need to be coordinated on a recurring basis.",
    "housing_status_check":        "A check on current housing status may be warranted.",
    "supply_resupply_needed":      "Supplies may need to be replenished.",
    "shelter_extension_needed":    "Extended shelter or longer-term housing may be needed.",
    "displacement_monitoring":     "Ongoing monitoring of displacement situation may be useful.",
    "skill_session_rescheduled":   "Skill exchange session may need to be rescheduled.",
    "wellbeing_check":             "A general wellbeing check may be warranted.",
    "advocacy_continuation":       "Advocacy or negotiation may need to continue.",
    "general_followup_needed":     "General follow-up has been identified without specific type.",
}

# ── urgency levels ────────────────────────────────────────────────────────────
URGENCY_LEVELS = {
    "immediate": "Follow-up need is immediate.",
    "urgent":    "Follow-up need is urgent; within a day.",
    "medium":    "Follow-up need is medium priority; within a week.",
    "low":       "Follow-up need is low priority; when available.",
    "ongoing":   "Follow-up need is ongoing and recurring.",
}

# ── default follow-up needs — linked to reopen and case IDs ──────────────────
DEFAULT_FOLLOWUPS: list[dict[str, object]] = [
    {
        "followup_id":     "followup-001",
        "reopen_id":       "care-reopen-001",
        "relief_case_id":  "relief-case-002",
        "commons_id":      "jammy-house-001",
        "need_type":       "housing_status_check",
        "urgency":         "medium",
        "description":     "Housing advocacy initiated. A status check on tenancy "
                           "outcome would be useful. No blame is attached to the "
                           "advocate; situation remains unresolved.",
    },
    {
        "followup_id":     "followup-002",
        "reopen_id":       "care-reopen-002",
        "relief_case_id":  "relief-case-003",
        "commons_id":      "dra-001",
        "need_type":       "displacement_monitoring",
        "urgency":         "ongoing",
        "description":     "Displaced family received supplies. Displacement is ongoing. "
                           "Monitoring follow-up recorded to surface ongoing need without "
                           "blaming the supply coordination response.",
    },
    {
        "followup_id":     "followup-003",
        "reopen_id":       "care-reopen-003",
        "relief_case_id":  "relief-case-001",
        "commons_id":      "jammy-house-001",
        "need_type":       "ongoing_food_coordination",
        "urgency":         "low",
        "description":     "Food support need has recurred. Ongoing food coordination "
                           "may be useful. The original meal offer was adequate for "
                           "its moment; recurring need is a new observation.",
    },
    {
        "followup_id":     "followup-004",
        "reopen_id":       "care-reopen-004",
        "relief_case_id":  "relief-case-005",
        "commons_id":      "yacypherpunks-001",
        "need_type":       "skill_session_rescheduled",
        "urgency":         "low",
        "description":     "Skill exchange was not yet observed. Session may need "
                           "rescheduling. Follow-up is recorded; no blame attaches "
                           "to either participant.",
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


def build_followup_record(
    followup_id:    str,
    reopen_id:      str,
    relief_case_id: str,
    commons_id:     str,
    need_type:      str,
    urgency:        str,
    description:    str,
) -> dict[str, object]:
    """Build one advisory follow-up need record."""
    if need_type not in FOLLOWUP_NEED_TYPES:
        need_type = "general_followup_needed"
    if urgency not in URGENCY_LEVELS:
        urgency = "low"

    record: dict[str, object] = {
        "record_type":                 "followup_need",
        "followup_id":                 followup_id,
        "followup_date":               str(date.today()),
        "reopen_id":                   reopen_id,
        "relief_case_id":              relief_case_id,
        "commons_id":                  commons_id,
        "need_type":                   need_type,
        "need_note":                   FOLLOWUP_NEED_TYPES[need_type],
        "urgency":                     urgency,
        "urgency_note":                URGENCY_LEVELS[urgency],
        "description":                 description,
        # invariants
        **CARE_LOOP_INVARIANTS,
        # explicit follow-up invariants
        "followup_judges_prior_helper": False,
        "followup_demands_response":    False,
        "ranks_suffering":              False,
        "need_creates_debt":            False,
        # protocol phrases
        "protocol_phrases": [
            "Reopen is not failure.",
            "Follow-up is not blame.",
            "Care loop is not obligation.",
        ],
    }
    return record


def build_followup_snapshot(
    followups: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    """Build the full follow-up need snapshot."""
    if followups is None:
        followups = DEFAULT_FOLLOWUPS

    entries = [
        build_followup_record(
            followup_id    = str(f["followup_id"]),
            reopen_id      = str(f["reopen_id"]),
            relief_case_id = str(f["relief_case_id"]),
            commons_id     = str(f["commons_id"]),
            need_type      = str(f["need_type"]),
            urgency        = str(f["urgency"]),
            description    = str(f["description"]),
        )
        for f in followups
    ]

    urgency_counts: dict[str, int] = {}
    for e in entries:
        u = str(e["urgency"])
        urgency_counts[u] = urgency_counts.get(u, 0) + 1

    snapshot: dict[str, object] = {
        "record_type":     "followup_need_snapshot",
        "snapshot_id":     "followup-snapshot-001",
        "snapshot_date":   str(date.today()),
        "followup_count":  len(entries),
        "urgency_summary": urgency_counts,
        "followups":       entries,
        **CARE_LOOP_INVARIANTS,
        "protocol_phrases": [
            "Reopen is not failure.",
            "Follow-up is not blame.",
            "Care loop is not obligation.",
            "Dan-Go records follow-up needs; it does not blame participants or compel response.",
        ],
    }
    return snapshot


def print_snapshot(snap: dict[str, object]) -> None:
    print("=== followup_need_snapshot.py ===")
    print(f"  snapshot_id:    {snap['snapshot_id']}")
    print(f"  followup_count: {snap['followup_count']}")
    print(f"  urgency_summary: {snap['urgency_summary']}")
    for f in snap["followups"]:  # type: ignore[union-attr]
        print(f"  [{f['followup_id']}] case={f['relief_case_id']} "
              f"type={f['need_type']} urgency={f['urgency']} "
              f"followup_is_blame={f['followup_is_blame']} "
              f"ranks_suffering={f['ranks_suffering']}")
    print(f"  authority={snap['authority']}, followup_is_blame={snap['followup_is_blame']}, "
          f"care_loop_creates_obligation={snap['care_loop_creates_obligation']}")
    print("  Follow-up is not blame.")
    print("  Care loop is not obligation.")


def save_snapshot(snap: dict[str, object]) -> Path:
    _EXAMPLES.mkdir(parents=True, exist_ok=True)
    out = _EXAMPLES / "followup-need-snapshot.json"
    out.write_text(json.dumps(snap, indent=2))
    print(f"  saved → {out.relative_to(_REPO_ROOT)}")
    return out


if __name__ == "__main__":
    snap = build_followup_snapshot()
    print_snapshot(snap)
    if "--save" in sys.argv:
        save_snapshot(snap)
