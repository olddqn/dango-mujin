"""
resource_snapshot.py — Resource Memory Layer (Phase 51)
Dan-Go / GITSEA Bridge · authority: none · stdlib only

"Resource is not allocation."
"Possession is not obligation."
"Availability is not transfer."

Aggregates resource records into a snapshot. A snapshot says: across the
observed commons, these kinds of resource appear to exist. It does not
total resources into a pool, rank commons by resource count, or imply
that any observed resource is available for allocation or transfer.

Counting resources is not the same as having them ready to give. A
snapshot is a mirror, not a ledger of transfers.

Invariants (all permanent):
  resource_is_allocation: false
  possession_creates_obligation: false
  availability_transfers_ownership: false
  snapshot_ranks_commons: false
  snapshot_totals_pool: false
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

_RESOURCE_EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
_SAVE_PATH = _RESOURCE_EXAMPLES / "resource-snapshot.json"

PHASE_INVARIANTS = {
    "authority":                        "none",
    "execution_allowed":                False,
    "moves_money":                      False,
    "credit_issued":                    False,
    "hard_enforcement":                 False,
    "advisory":                         True,
    "resource_memory_only":             True,
    "append_only":                      True,
    "contestable":                      True,
    "reopenable":                       True,
    "resource_is_allocation":           False,
    "possession_creates_obligation":    False,
    "availability_transfers_ownership": False,
    "snapshot_ranks_commons":           False,
    "snapshot_totals_pool":             False,
}


def _load_registry():
    path = _RESOURCE_EXAMPLES / "resource-registry.json"
    if path.exists():
        try:
            data = json.loads(path.read_text())
            if isinstance(data, dict):
                return data.get("resources", [])
            if isinstance(data, list):
                return data
        except Exception:
            pass
    try:
        from resource_registry import build_registry  # type: ignore
        return build_registry().get("resources", [])
    except Exception:
        return []


def build_snapshot(resources=None):
    if resources is None:
        resources = _load_registry()

    commons_ids = sorted({r["commons_id"] for r in resources if "commons_id" in r})

    by_type = {}
    by_observability = {}
    by_commons = {}
    for r in resources:
        rtype = r.get("resource_type", "unknown")
        obs = r.get("observability", "unknown")
        cid = r.get("commons_id", "unknown")
        by_type[rtype] = by_type.get(rtype, 0) + 1
        by_observability[obs] = by_observability.get(obs, 0) + 1
        by_commons[cid] = by_commons.get(cid, 0) + 1

    return {
        "record_type":                      "commons_resource_snapshot",
        "snapshot_id":                      "resource-snapshot-001",
        "commons_count":                    len(commons_ids),
        "resource_count":                   len(resources),
        "commons_represented":              commons_ids,
        "resource_by_type":                 dict(sorted(by_type.items())),
        "resource_by_observability":        dict(sorted(by_observability.items())),
        "resource_by_commons":              dict(sorted(by_commons.items())),
        "authority":                        "none",
        "advisory":                         True,
        "resource_is_allocation":           False,
        "possession_creates_obligation":    False,
        "availability_transfers_ownership": False,
        "snapshot_ranks_commons":           False,
        "generated_at":                     datetime.now(timezone.utc).isoformat(),
        "phase":                            51,
        "phase_phrase_1":                   "Resource is not allocation.",
        "phase_phrase_2":                   "Possession is not obligation.",
        "phase_phrase_3":                   "Availability is not transfer.",
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
    print(f"  resource_count: {snapshot['resource_count']}", file=sys.stderr)
    print(f"  resource_by_type: {snapshot['resource_by_type']}", file=sys.stderr)
    print(
        f"  resource_is_allocation={snapshot['resource_is_allocation']} "
        f"availability_transfers_ownership={snapshot['availability_transfers_ownership']}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
