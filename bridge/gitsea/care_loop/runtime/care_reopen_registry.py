"""
care_reopen_registry.py — Phase 19: Care Loop Reopen Layer

Dan-Go records that a relief case may need reopening, follow-up, or renewed
assistance. Reopening is not a declaration of failure. It is an advisory
observation that the care situation has more to it.

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
_SCRIPT_DIR    = Path(__file__).resolve().parent
_REPO_ROOT     = _SCRIPT_DIR.parents[4]
_EXAMPLES      = _SCRIPT_DIR.parent / "examples"
_RELIEF_EXAMPLES = _REPO_ROOT / "bridge" / "gitsea" / "relief" / "examples"

# ── reopen reasons ────────────────────────────────────────────────────────────
REOPEN_REASONS = {
    "partial_outcome_needs_followup": "Outcome was partial; situation may need further attention.",
    "need_recurred":                  "The original need has recurred after initial assistance.",
    "new_information_available":      "New information changes the picture of what occurred.",
    "participant_requested_reopen":   "A participant in the care exchange requested reopening.",
    "outcome_contested":              "The recorded outcome has been contested.",
    "situation_changed":              "Circumstances have changed since the case was closed.",
    "case_was_pending":               "Case was pending; now has new observable activity.",
    "housing_situation_unresolved":   "Housing situation remained unresolved after initial response.",
    "displacement_ongoing":           "Displacement is ongoing; relief was temporary.",
    "general_followup":               "General follow-up identified; no specific reopen trigger.",
}

# ── reopen statuses ───────────────────────────────────────────────────────────
REOPEN_STATUSES = {
    "requested":   "Reopen has been requested and recorded.",
    "acknowledged":"Reopen has been acknowledged by relevant participants.",
    "active":      "Reopen is active; follow-up is in progress.",
    "resolved":    "Reopen was resolved with further assistance or observation.",
    "withdrawn":   "Reopen request was withdrawn.",
    "closed":      "Reopen has been closed without resolution; case remains in history.",
}

# ── default reopen records — linked to Phase 18 case IDs ─────────────────────
DEFAULT_REOPENS: list[dict[str, object]] = [
    {
        "reopen_id":       "care-reopen-001",
        "relief_case_id":  "relief-case-002",
        "route_id":        "aid-route-002",
        "commons_id":      "jammy-house-001",
        "reopen_reason":   "partial_outcome_needs_followup",
        "reopen_status":   "requested",
        "description":     "Housing negotiation was initiated but tenancy outcome is still "
                           "unresolved. Reopen requested to continue advisory observation.",
    },
    {
        "reopen_id":       "care-reopen-002",
        "relief_case_id":  "relief-case-003",
        "route_id":        "aid-route-003",
        "commons_id":      "dra-001",
        "reopen_reason":   "displacement_ongoing",
        "reopen_status":   "active",
        "description":     "Supply coordination reached household but displacement is ongoing. "
                           "Reopen active to track continued relief need.",
    },
    {
        "reopen_id":       "care-reopen-003",
        "relief_case_id":  "relief-case-001",
        "route_id":        "aid-route-001",
        "commons_id":      "jammy-house-001",
        "reopen_reason":   "need_recurred",
        "reopen_status":   "requested",
        "description":     "Food support need has recurred after initial meal provision. "
                           "Household may benefit from ongoing coordination.",
    },
    {
        "reopen_id":       "care-reopen-004",
        "relief_case_id":  "relief-case-005",
        "route_id":        "aid-route-005",
        "commons_id":      "yacypherpunks-001",
        "reopen_reason":   "case_was_pending",
        "reopen_status":   "acknowledged",
        "description":     "Skill exchange case was pending. Participants have acknowledged "
                           "the reopen request and will attempt to schedule.",
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


def load_cases() -> dict[str, dict[str, object]]:
    """Try to load Phase 18 relief cases indexed by relief_case_id."""
    case_path = _RELIEF_EXAMPLES / "relief-case-registry.json"
    if case_path.exists():
        data = json.loads(case_path.read_text())
        return {str(c["relief_case_id"]): c for c in data.get("cases", [])}
    return {}


def build_reopen_record(
    reopen_id:      str,
    relief_case_id: str,
    route_id:       str,
    commons_id:     str,
    reopen_reason:  str,
    reopen_status:  str,
    description:    str,
    case_summary:   dict[str, object] | None = None,
) -> dict[str, object]:
    """Build one advisory care reopen record."""
    if reopen_reason not in REOPEN_REASONS:
        reopen_reason = "general_followup"
    if reopen_status not in REOPEN_STATUSES:
        reopen_status = "requested"

    record: dict[str, object] = {
        "record_type":          "care_reopen",
        "reopen_id":            reopen_id,
        "reopen_date":          str(date.today()),
        "relief_case_id":       relief_case_id,
        "route_id":             route_id,
        "commons_id":           commons_id,
        "reopen_reason":        reopen_reason,
        "reason_note":          REOPEN_REASONS[reopen_reason],
        "reopen_status":        reopen_status,
        "status_note":          REOPEN_STATUSES[reopen_status],
        "description":          description,
        "case_summary":         case_summary or {},
        # invariants
        **CARE_LOOP_INVARIANTS,
        # explicit reopen-level invariants
        "reopen_judges_prior_response": False,
        "reopen_blames_participants":   False,
        "reopen_compels_new_aid":       False,
        "reopen_certifies_failure":     False,
        # protocol phrases
        "protocol_phrases": [
            "Reopen is not failure.",
            "Follow-up is not blame.",
            "Care loop is not obligation.",
        ],
    }
    return record


def build_reopen_registry(
    reopens: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    """Build the full care reopen registry."""
    if reopens is None:
        reopens = DEFAULT_REOPENS

    case_index = load_cases()

    entries: list[dict[str, object]] = []
    for r in reopens:
        cid = str(r["relief_case_id"])
        case_rec = case_index.get(cid)
        case_summary: dict[str, object] = {}
        if case_rec:
            case_summary = {
                "case_type":   case_rec.get("case_type"),
                "case_status": case_rec.get("case_status"),
                "route_id":    case_rec.get("route_id"),
            }
        entries.append(build_reopen_record(
            reopen_id      = str(r["reopen_id"]),
            relief_case_id = cid,
            route_id       = str(r["route_id"]),
            commons_id     = str(r["commons_id"]),
            reopen_reason  = str(r["reopen_reason"]),
            reopen_status  = str(r["reopen_status"]),
            description    = str(r["description"]),
            case_summary   = case_summary,
        ))

    status_counts: dict[str, int] = {}
    for e in entries:
        s = str(e["reopen_status"])
        status_counts[s] = status_counts.get(s, 0) + 1

    registry: dict[str, object] = {
        "record_type":    "care_reopen_registry",
        "registry_id":    "care-reopen-registry-001",
        "registry_date":  str(date.today()),
        "reopen_count":   len(entries),
        "status_summary": status_counts,
        "reopens":        entries,
        **CARE_LOOP_INVARIANTS,
        "protocol_phrases": [
            "Reopen is not failure.",
            "Follow-up is not blame.",
            "Care loop is not obligation.",
            "Dan-Go records reopen observations; it does not judge prior responses.",
        ],
    }
    return registry


def print_registry(reg: dict[str, object]) -> None:
    print("=== care_reopen_registry.py ===")
    print(f"  registry_id:    {reg['registry_id']}")
    print(f"  reopen_count:   {reg['reopen_count']}")
    print(f"  status_summary: {reg['status_summary']}")
    for r in reg["reopens"]:  # type: ignore[union-attr]
        print(f"  [{r['reopen_id']}] case={r['relief_case_id']} "
              f"reason={r['reopen_reason']} status={r['reopen_status']} "
              f"reopen_is_failure={r['reopen_is_failure']}")
    print(f"  authority={reg['authority']}, reopen_is_failure={reg['reopen_is_failure']}, "
          f"followup_is_blame={reg['followup_is_blame']}")
    print("  Reopen is not failure.")
    print("  Follow-up is not blame.")


def save_registry(reg: dict[str, object]) -> Path:
    _EXAMPLES.mkdir(parents=True, exist_ok=True)
    out = _EXAMPLES / "care-reopen-registry.json"
    out.write_text(json.dumps(reg, indent=2))
    print(f"  saved → {out.relative_to(_REPO_ROOT)}")
    return out


if __name__ == "__main__":
    reg = build_reopen_registry()
    print_registry(reg)
    if "--save" in sys.argv:
        save_registry(reg)
