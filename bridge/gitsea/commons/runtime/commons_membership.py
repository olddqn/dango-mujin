"""
commons_membership.py — Phase 16: Cooperation Commons Layer

Dan-Go records participation relationships between contributors and commons.
Participation is voluntary and advisory. No control or ownership is implied.

"Community is not authority."
"Commons is not ownership."
"Participation is not control."

Invariants:
  authority: none
  ownership: false
  control: false
  membership_compels: false
  advisory: true
  commons_only: true
  append_only: true
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

# ── membership types ──────────────────────────────────────────────────────────
MEMBERSHIP_TYPES = {
    "participant":   "Voluntary participant in the commons.",
    "contributor":   "Active contributor to commons activities.",
    "coordinator":   "Coordinates commons activities without authority.",
    "observer":      "Observes and records commons activity.",
    "correspondent": "External correspondent cooperating with the commons.",
}

# ── participation roles ───────────────────────────────────────────────────────
PARTICIPATION_ROLES = {
    "negotiator":    "Participates in Dan-Go negotiation records.",
    "reviewer":      "Reviews contributions within the commons.",
    "planner":       "Contributes to planning activities.",
    "author":        "Authors contributions or proposals.",
    "archivist":     "Maintains commons records.",
    "advocate":      "Advocates for commons interests.",
}

# ── default memberships ───────────────────────────────────────────────────────
DEFAULT_MEMBERSHIPS: list[dict[str, object]] = [
    # Jammy House
    {
        "commons_id":      "jammy-house-001",
        "participant_id":  "external-001",
        "membership_type": "contributor",
        "role":            "reviewer",
        "joined":          "2025-03-10",
    },
    {
        "commons_id":      "jammy-house-001",
        "participant_id":  "external-002",
        "membership_type": "contributor",
        "role":            "author",
        "joined":          "2025-03-10",
    },
    {
        "commons_id":      "jammy-house-001",
        "participant_id":  "external-003",
        "membership_type": "participant",
        "role":            "advocate",
        "joined":          "2025-03-12",
    },
    # D.R.A.
    {
        "commons_id":      "dra-001",
        "participant_id":  "external-001",
        "membership_type": "coordinator",
        "role":            "negotiator",
        "joined":          "2025-01-15",
    },
    {
        "commons_id":      "dra-001",
        "participant_id":  "external-002",
        "membership_type": "contributor",
        "role":            "planner",
        "joined":          "2025-01-20",
    },
    # YacypherPunks
    {
        "commons_id":      "yacypherpunks-001",
        "participant_id":  "external-001",
        "membership_type": "correspondent",
        "role":            "advocate",
        "joined":          "2024-06-15",
    },
    # Dan-Go project
    {
        "commons_id":      "dango-001",
        "participant_id":  "external-001",
        "membership_type": "contributor",
        "role":            "negotiator",
        "joined":          "2025-01-01",
    },
    {
        "commons_id":      "dango-001",
        "participant_id":  "external-002",
        "membership_type": "contributor",
        "role":            "author",
        "joined":          "2025-01-01",
    },
    {
        "commons_id":      "dango-001",
        "participant_id":  "external-003",
        "membership_type": "participant",
        "role":            "advocate",
        "joined":          "2025-01-05",
    },
]


def build_membership_record(
    commons_id:      str,
    participant_id:  str,
    membership_type: str,
    role:            str,
    joined:          str | None = None,
) -> dict[str, object]:
    """Build one advisory membership record."""
    if membership_type not in MEMBERSHIP_TYPES:
        membership_type = "participant"
    if role not in PARTICIPATION_ROLES:
        role = "participant"

    record: dict[str, object] = {
        "record_type":     "commons_membership",
        "membership_id":   f"membership-{commons_id}-{participant_id}",
        "commons_id":      commons_id,
        "participant_id":  participant_id,
        "membership_type": membership_type,
        "type_note":       MEMBERSHIP_TYPES[membership_type],
        "role":            role,
        "role_note":       PARTICIPATION_ROLES[role],
        "joined":          joined or str(date.today()),
        # invariants
        "authority":           "none",
        "ownership":           False,
        "control":             False,
        "membership_compels":  False,
        "membership_grants_authority": False,
        "membership_is_voluntary":     True,
        "execution_allowed":   False,
        "moves_money":         False,
        "credit_issued":       False,
        "hard_enforcement":    False,
        "advisory":            True,
        "commons_only":        True,
        "append_only":         True,
        "contestable":         True,
        "reopenable":          True,
        # protocol phrases
        "protocol_phrases": [
            "Community is not authority.",
            "Commons is not ownership.",
            "Participation is not control.",
        ],
    }
    return record


def build_membership_log(
    membership_list: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    """Build the full membership log."""
    if membership_list is None:
        membership_list = DEFAULT_MEMBERSHIPS

    records = [
        build_membership_record(
            commons_id      = m["commons_id"],       # type: ignore[arg-type]
            participant_id  = m["participant_id"],    # type: ignore[arg-type]
            membership_type = m["membership_type"],   # type: ignore[arg-type]
            role            = m["role"],              # type: ignore[arg-type]
            joined          = m.get("joined"),        # type: ignore[arg-type]
        )
        for m in membership_list
    ]

    # count per commons
    commons_seen: dict[str, int] = {}
    for r in records:
        cid = str(r["commons_id"])
        commons_seen[cid] = commons_seen.get(cid, 0) + 1

    log: dict[str, object] = {
        "record_type":          "commons_membership_log",
        "log_id":               "membership-log-001",
        "total_memberships":    len(records),
        "commons_represented":  len(commons_seen),
        "per_commons_count":    commons_seen,
        "memberships":          records,
        # invariants
        "authority":            "none",
        "ownership":            False,
        "control":              False,
        "membership_compels":   False,
        "advisory":             True,
        "commons_only":         True,
        "append_only":          True,
        "contestable":          True,
        "reopenable":           True,
        "moves_money":          False,
        "credit_issued":        False,
        "execution_allowed":    False,
        "hard_enforcement":     False,
        "protocol_phrases": [
            "Community is not authority.",
            "Commons is not ownership.",
            "Participation is not control.",
            "Dan-Go records participation; it does not assign control.",
        ],
    }
    return log


def print_log(log: dict[str, object]) -> None:
    print("=== commons_membership.py ===")
    print(f"  log_id:                {log['log_id']}")
    print(f"  total_memberships:     {log['total_memberships']}")
    print(f"  commons_represented:   {log['commons_represented']}")
    per = log["per_commons_count"]
    for cid, cnt in per.items():                                  # type: ignore[union-attr]
        print(f"    {cid}: {cnt} member(s)")
    for rec in log["memberships"]:                                # type: ignore[union-attr]
        r = rec  # type: ignore[assignment]
        print(f"  [{r['commons_id']}] {r['participant_id']} "
              f"({r['membership_type']}/{r['role']}) control={r['control']} ownership={r['ownership']}")
    print(f"  authority={log['authority']}, ownership={log['ownership']}, control={log['control']}")
    print("  Participation is not control.")


def save_log(log: dict[str, object]) -> Path:
    _EXAMPLES.mkdir(parents=True, exist_ok=True)
    out = _EXAMPLES / "commons-membership.json"
    out.write_text(json.dumps(log, indent=2))
    print(f"  saved → {out.relative_to(_REPO_ROOT)}")
    return out


if __name__ == "__main__":
    log = build_membership_log()
    print_log(log)
    if "--save" in sys.argv:
        save_log(log)
