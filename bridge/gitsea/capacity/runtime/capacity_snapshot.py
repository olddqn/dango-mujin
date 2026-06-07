"""
capacity_snapshot.py — Commons Capacity Memory Layer (Phase 50)
Dan-Go / GITSEA Bridge · authority: none · stdlib only

"Capacity is not commitment."
"Ability is not obligation."
"Availability is not allocation."

Aggregates capacity records into a snapshot. A snapshot says: across the
observed commons, these kinds of ability appear to exist. It does not
total ability into a budget, rank commons by capacity, or imply that any
observed capacity is available for allocation.

Counting capacity is not the same as having it ready. A snapshot is a
mirror, not a ledger of obligations.

Invariants (all permanent):
  capacity_is_commitment: false
  ability_creates_obligation: false
  availability_allocates_resources: false
  snapshot_ranks_commons: false
  snapshot_totals_obligation: false
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

_CAPACITY_EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
_SAVE_PATH = _CAPACITY_EXAMPLES / "capacity-snapshot.json"

PHASE_INVARIANTS = {
    "authority":                        "none",
    "execution_allowed":                False,
    "moves_money":                      False,
    "credit_issued":                    False,
    "hard_enforcement":                 False,
    "advisory":                         True,
    "capacity_only":                    True,
    "append_only":                      True,
    "contestable":                      True,
    "reopenable":                       True,
    "capacity_is_commitment":           False,
    "ability_creates_obligation":       False,
    "availability_allocates_resources": False,
    "snapshot_ranks_commons":           False,
    "snapshot_totals_obligation":       False,
}


def _load_registry():
    path = _CAPACITY_EXAMPLES / "capacity-registry.json"
    if path.exists():
        try:
            data = json.loads(path.read_text())
            if isinstance(data, dict):
                return data.get("capacities", [])
            if isinstance(data, list):
                return data
        except Exception:
            pass
    # Fall back to building from the registry module directly
    try:
        from capacity_registry import build_registry  # type: ignore
        return build_registry().get("capacities", [])
    except Exception:
        return []


def build_snapshot(capacities=None):
    if capacities is None:
        capacities = _load_registry()

    commons_ids = sorted({c["commons_id"] for c in capacities if "commons_id" in c})

    by_type = {}
    by_availability = {}
    by_commons = {}
    for c in capacities:
        ctype = c.get("capacity_type", "unknown")
        avail = c.get("availability", "unknown")
        cid = c.get("commons_id", "unknown")
        by_type[ctype] = by_type.get(ctype, 0) + 1
        by_availability[avail] = by_availability.get(avail, 0) + 1
        by_commons[cid] = by_commons.get(cid, 0) + 1

    return {
        "record_type":                      "commons_capacity_snapshot",
        "snapshot_id":                      "capacity-snapshot-001",
        "commons_count":                    len(commons_ids),
        "capacity_count":                   len(capacities),
        "commons_represented":              commons_ids,
        "capacity_by_type":                 dict(sorted(by_type.items())),
        "capacity_by_availability":         dict(sorted(by_availability.items())),
        "capacity_by_commons":              dict(sorted(by_commons.items())),
        "advisory":                         True,
        "capacity_is_commitment":           False,
        "ability_creates_obligation":       False,
        "availability_allocates_resources": False,
        "snapshot_ranks_commons":           False,
        "generated_at":                     datetime.now(timezone.utc).isoformat(),
        "phase":                            50,
        "phase_phrase_1":                   "Capacity is not commitment.",
        "phase_phrase_2":                   "Ability is not obligation.",
        "phase_phrase_3":                   "Availability is not allocation.",
    }


def main():
    save = "--save" in sys.argv
    snapshot = build_snapshot()
    out = json.dumps(snapshot, indent=2)
    print(out)
    if save:
        _SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _SAVE_PATH.write_text(out)
        print(f"\n[saved → {_SAVE_PATH}]", file=sys.stderr)
    print(f"\n  snapshot_id: {snapshot['snapshot_id']}", file=sys.stderr)
    print(f"  commons_count: {snapshot['commons_count']}", file=sys.stderr)
    print(f"  capacity_count: {snapshot['capacity_count']}", file=sys.stderr)
    print(f"  capacity_by_type: {snapshot['capacity_by_type']}", file=sys.stderr)
    print(
        f"  capacity_is_commitment={snapshot['capacity_is_commitment']} "
        f"availability_allocates_resources={snapshot['availability_allocates_resources']}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
