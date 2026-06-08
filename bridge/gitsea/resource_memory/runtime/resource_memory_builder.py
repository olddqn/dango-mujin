"""
resource_memory_builder.py — Resource Memory Layer (Phase 51)
Dan-Go / GITSEA Bridge · authority: none · stdlib only

"Resource is not allocation."
"Possession is not obligation."
"Availability is not transfer."

Builds resource memory records by linking:
  Phase 16 Cooperation Commons       (the community)
  Phase 21 Need Forecast Memory      (anticipated needs)
  Phase 50 Commons Capacity Memory   (observed ability)
to the Phase 51 resource records (observed possession).

A resource memory makes legible, in one place: "this commons has these
observed resources, this observed capacity, and may face this kind of
need." It does NOT match resources to needs. It does not assign anyone
to bring a resource to a need. It does not transfer ownership of any
resource. The juxtaposition is for human consideration only — Dan-Go
performs no allocation, no transfer, no command.

The memory is append-only and reopenable.

Invariants (all permanent):
  resource_is_allocation: false
  possession_creates_obligation: false
  availability_transfers_ownership: false
  memory_matches_resource_to_need: false
  memory_assigns_helpers: false
  memory_transfers_ownership: false
  append_only: true
  reopenable: true
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

_REPO_ROOT = Path(__file__).resolve().parents[4]
_RESOURCE_EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
_FORECAST_EXAMPLES = _REPO_ROOT / "bridge" / "gitsea" / "need_forecast" / "examples"
_CAPACITY_EXAMPLES = _REPO_ROOT / "bridge" / "gitsea" / "capacity" / "examples"
_SAVE_PATH = _RESOURCE_EXAMPLES / "resource-memory.json"

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
    "memory_matches_resource_to_need":  False,
    "memory_assigns_helpers":           False,
    "memory_transfers_ownership":       False,
}


def _load_resources():
    path = _RESOURCE_EXAMPLES / "resource-registry.json"
    if path.exists():
        try:
            data = json.loads(path.read_text())
            return data.get("resources", []) if isinstance(data, dict) else data
        except Exception:
            pass
    try:
        from resource_registry import build_registry  # type: ignore
        return build_registry().get("resources", [])
    except Exception:
        return []


def _load_forecast_index():
    path = _FORECAST_EXAMPLES / "need-forecast-registry.json"
    if path.exists():
        try:
            data = json.loads(path.read_text())
            records = data.get("forecasts", []) if isinstance(data, dict) else data
            return {r["forecast_id"]: r for r in records if "forecast_id" in r}
        except Exception:
            pass
    return {}


def _load_capacity_index():
    path = _CAPACITY_EXAMPLES / "capacity-registry.json"
    if path.exists():
        try:
            data = json.loads(path.read_text())
            records = data.get("capacities", []) if isinstance(data, dict) else data
            return {r["capacity_id"]: r for r in records if "capacity_id" in r}
        except Exception:
            pass
    return {}


def build_memories():
    resources = _load_resources()
    forecast_index = _load_forecast_index()
    capacity_index = _load_capacity_index()

    # Group resources by commons
    by_commons = {}
    for r in resources:
        cid = r.get("commons_id", "unknown")
        by_commons.setdefault(cid, []).append(r)

    # Map forecasts / capacities by commons (advisory juxtaposition only)
    forecasts_by_commons = {}
    for fid, f in forecast_index.items():
        cid = f.get("commons_id", "unknown")
        forecasts_by_commons.setdefault(cid, []).append(fid)

    capacities_by_commons = {}
    for caid, c in capacity_index.items():
        cid = c.get("commons_id", "unknown")
        capacities_by_commons.setdefault(cid, []).append(caid)

    memories = []
    seq = 1
    for cid in sorted(by_commons):
        res_records = by_commons[cid]
        res_ids = [r["resource_id"] for r in res_records if "resource_id" in r]
        related_forecasts  = forecasts_by_commons.get(cid, [])
        related_capacities = capacities_by_commons.get(cid, [])

        memory = {
            "record_type":                  "commons_resource_memory",
            "memory_id":                    f"resource-memory-{seq:03d}",
            "commons_id":                   cid,
            "resource_ids":                 res_ids,
            "resource_count":               len(res_ids),
            "related_forecast_ids":         related_forecasts,
            "related_capacity_ids":         related_capacities,
            "juxtaposition_note": (
                "Observed resources are recorded side by side with anticipated need "
                "and observed capacity for human consideration. Dan-Go does not match "
                "resources to needs, assign helpers, or transfer ownership."
            ),
            "authority":                        "none",
            "possession_creates_obligation":    False,
            "memory_matches_resource_to_need":  False,
            "memory_assigns_helpers":           False,
            "memory_transfers_ownership":       False,
            "generated_at":                     datetime.now(timezone.utc).isoformat(),
        }
        memory.update(PHASE_INVARIANTS)
        memories.append(memory)
        seq += 1

    return {
        "record_type":                      "commons_resource_memory_set",
        "memory_set_id":                    "resource-memory-set-001",
        "memory_count":                     len(memories),
        "memories":                         memories,
        "authority":                        "none",
        "resource_is_allocation":           False,
        "possession_creates_obligation":    False,
        "availability_transfers_ownership": False,
        "generated_at":                     datetime.now(timezone.utc).isoformat(),
        "phase":                            51,
        "phase_phrase_1":                   "Resource is not allocation.",
        "phase_phrase_2":                   "Possession is not obligation.",
        "phase_phrase_3":                   "Availability is not transfer.",
    }


def main():
    save = "--save" in sys.argv
    result = build_memories()
    out = json.dumps(result, indent=2)
    print(out)
    if save:
        _SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _SAVE_PATH.write_text(out)
        print(f"\n[saved → {_SAVE_PATH}]", file=sys.stderr)
    print(f"\n  memory_set_id: {result['memory_set_id']}", file=sys.stderr)
    print(f"  memory_count: {result['memory_count']}", file=sys.stderr)
    for m in result["memories"]:
        print(
            f"    {m['memory_id']}: commons={m['commons_id']} "
            f"resources={m['resource_ids']} "
            f"capacities={m['related_capacity_ids']} "
            f"forecasts={m['related_forecast_ids']} "
            f"possession_creates_obligation={m['possession_creates_obligation']}",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
