"""
commons_snapshot.py — Phase 16: Cooperation Commons Layer

Aggregate snapshot of commons activity across all registered commons.
Reads from commons-registry.json and commons-membership.json if available;
falls back to defaults.

"Community is not authority."
"Commons is not ownership."
"Participation is not control."

Invariants:
  authority: none
  ownership: false
  control: false
  advisory: true
  commons_only: true
  moves_money: false
  credit_issued: false
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

# ── static defaults for contribution/recognition counts ───────────────────────
# These represent the observable cooperation history per commons.
COMMONS_ACTIVITY_DEFAULTS: dict[str, dict[str, int]] = {
    "dango-001": {
        "participant_count":          3,
        "contribution_count":         42,
        "recognition_history_count":  42,
        "ledger_entry_count":         3,
        "appeal_count":               3,
        "reflection_count":           3,
    },
    "jammy-house-001": {
        "participant_count":          3,
        "contribution_count":         57,
        "recognition_history_count":  44,
        "ledger_entry_count":         3,
        "appeal_count":               2,
        "reflection_count":           3,
    },
    "yacypherpunks-001": {
        "participant_count":          1,
        "contribution_count":         8,
        "recognition_history_count":  0,
        "ledger_entry_count":         0,
        "appeal_count":               0,
        "reflection_count":           0,
    },
    "dra-001": {
        "participant_count":          2,
        "contribution_count":         19,
        "recognition_history_count":  12,
        "ledger_entry_count":         2,
        "appeal_count":               2,
        "reflection_count":           2,
    },
}


def load_registry() -> list[dict[str, object]] | None:
    """Try to load commons entries from saved registry JSON."""
    reg_path = _EXAMPLES / "commons-registry.json"
    if reg_path.exists():
        data = json.loads(reg_path.read_text())
        commons_list = data.get("commons", [])
        if isinstance(commons_list, list):
            return commons_list  # type: ignore[return-value]
    return None


def load_membership_counts() -> dict[str, int]:
    """Try to load per-commons participant counts from saved membership JSON."""
    mem_path = _EXAMPLES / "commons-membership.json"
    if mem_path.exists():
        data = json.loads(mem_path.read_text())
        per = data.get("per_commons_count", {})
        if isinstance(per, dict):
            return {k: int(v) for k, v in per.items()}
    return {}


def build_commons_snapshot_entry(
    commons_id:               str,
    name:                     str,
    commons_type:             str,
    active:                   bool,
    participant_count:        int,
    contribution_count:       int,
    recognition_history_count: int,
    ledger_entry_count:       int,
    appeal_count:             int,
    reflection_count:         int,
) -> dict[str, object]:
    """Build one commons snapshot entry."""
    recognition_rate = (
        round(recognition_history_count / contribution_count, 4)
        if contribution_count > 0 else 0.0
    )
    return {
        "record_type":               "commons_snapshot_entry",
        "snapshot_entry_id":         f"snap-{commons_id}",
        "commons_id":                commons_id,
        "name":                      name,
        "commons_type":              commons_type,
        "active":                    active,
        "participant_count":         participant_count,
        "contribution_count":        contribution_count,
        "recognition_history_count": recognition_history_count,
        "recognition_rate":          recognition_rate,
        "ledger_entry_count":        ledger_entry_count,
        "appeal_count":              appeal_count,
        "reflection_count":          reflection_count,
        # invariants
        "authority":                 "none",
        "ownership":                 False,
        "control":                   False,
        "advisory":                  True,
        "commons_only":              True,
        "moves_money":               False,
        "credit_issued":             False,
        "execution_allowed":         False,
        "hard_enforcement":          False,
        "append_only":               True,
        "contestable":               True,
        "reopenable":                True,
    }


def build_snapshot() -> dict[str, object]:
    """Build the aggregate commons snapshot."""
    registry_entries = load_registry()
    membership_counts = load_membership_counts()

    if registry_entries is not None:
        commons_ids_and_meta = [
            (
                str(e["commons_id"]),
                str(e.get("name", e["commons_id"])),
                str(e.get("commons_type", "community")),
                bool(e.get("active", True)),
            )
            for e in registry_entries
        ]
    else:
        # fallback metadata
        commons_ids_and_meta = [
            ("dango-001",          "Dan-Go",          "project",   True),
            ("jammy-house-001",    "Jammy House",      "house",     True),
            ("yacypherpunks-001",  "YacypherPunks",   "community", True),
            ("dra-001",            "D.R.A.",           "initiative",True),
        ]

    entries: list[dict[str, object]] = []
    total_participants = 0
    total_contributions = 0
    total_recognition_history = 0
    total_ledger_entries = 0

    for commons_id, name, commons_type, active in commons_ids_and_meta:
        activity = COMMONS_ACTIVITY_DEFAULTS.get(commons_id, {
            "participant_count":          0,
            "contribution_count":         0,
            "recognition_history_count":  0,
            "ledger_entry_count":         0,
            "appeal_count":               0,
            "reflection_count":           0,
        })

        # prefer live membership count if available
        p_count = membership_counts.get(commons_id, activity["participant_count"])

        entry = build_commons_snapshot_entry(
            commons_id                = commons_id,
            name                      = name,
            commons_type              = commons_type,
            active                    = active,
            participant_count         = p_count,
            contribution_count        = activity["contribution_count"],
            recognition_history_count = activity["recognition_history_count"],
            ledger_entry_count        = activity["ledger_entry_count"],
            appeal_count              = activity["appeal_count"],
            reflection_count          = activity["reflection_count"],
        )
        entries.append(entry)
        total_participants         += p_count
        total_contributions        += activity["contribution_count"]
        total_recognition_history  += activity["recognition_history_count"]
        total_ledger_entries       += activity["ledger_entry_count"]

    snapshot: dict[str, object] = {
        "record_type":                    "commons_snapshot",
        "snapshot_id":                    "commons-snap-001",
        "snapshot_date":                  str(date.today()),
        "commons_count":                  len(entries),
        "total_participants":             total_participants,
        "total_contributions":            total_contributions,
        "total_recognition_history":      total_recognition_history,
        "total_ledger_entries":           total_ledger_entries,
        "commons_entries":                entries,
        # invariants
        "authority":                      "none",
        "ownership":                      False,
        "control":                        False,
        "advisory":                       True,
        "commons_only":                   True,
        "append_only":                    True,
        "contestable":                    True,
        "reopenable":                     True,
        "moves_money":                    False,
        "credit_issued":                  False,
        "execution_allowed":              False,
        "hard_enforcement":               False,
        "protocol_phrases": [
            "Community is not authority.",
            "Commons is not ownership.",
            "Participation is not control.",
            "Dan-Go records cooperation history; it does not govern communities.",
        ],
    }
    return snapshot


def print_snapshot(snap: dict[str, object]) -> None:
    print("=== commons_snapshot.py ===")
    print(f"  snapshot_id:             {snap['snapshot_id']}")
    print(f"  snapshot_date:           {snap['snapshot_date']}")
    print(f"  commons_count:           {snap['commons_count']}")
    print(f"  total_participants:      {snap['total_participants']}")
    print(f"  total_contributions:     {snap['total_contributions']}")
    print(f"  total_recognition_hist:  {snap['total_recognition_history']}")
    print(f"  total_ledger_entries:    {snap['total_ledger_entries']}")
    for e in snap["commons_entries"]:                             # type: ignore[union-attr]
        print(f"  [{e['commons_id']}] {e['name']}")
        print(f"    participants={e['participant_count']}, contributions={e['contribution_count']}, "
              f"recognition_history={e['recognition_history_count']}")
        print(f"    authority={e['authority']}, ownership={e['ownership']}, control={e['control']}")
    print(f"  authority={snap['authority']}, ownership={snap['ownership']}, control={snap['control']}")
    print(f"  moves_money={snap['moves_money']}, credit_issued={snap['credit_issued']}")
    print("  Community is not authority.")
    print("  Commons is not ownership.")


def save_snapshot(snap: dict[str, object]) -> Path:
    _EXAMPLES.mkdir(parents=True, exist_ok=True)
    out = _EXAMPLES / "commons-snapshot.json"
    out.write_text(json.dumps(snap, indent=2))
    print(f"  saved → {out.relative_to(_REPO_ROOT)}")
    return out


if __name__ == "__main__":
    snap = build_snapshot()
    print_snapshot(snap)
    if "--save" in sys.argv:
        save_snapshot(snap)
