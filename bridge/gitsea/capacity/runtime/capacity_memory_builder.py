"""
capacity_memory_builder.py — Commons Capacity Memory Layer (Phase 50)
Dan-Go / GITSEA Bridge · authority: none · stdlib only

"Capacity is not commitment."
"Ability is not obligation."
"Availability is not allocation."

Builds capacity memory records by linking:
  Phase 16 Cooperation Commons  (the community)
  Phase 17 Mutual Aid Routing   (observed aid flows)
  Phase 21 Need Forecast Memory (anticipated needs)
to the Phase 22 capacity records (observed ability).

A capacity memory makes legible, in one place: "this commons may face
this kind of need (forecast), and this kind of ability has been observed
within it (capacity)." It does NOT match capacity to need. It does not
assign anyone to fulfil a forecast. The juxtaposition is for human
consideration only — Dan-Go performs no allocation.

The memory is append-only and reopenable. New observations extend it
without modifying prior records.

Invariants (all permanent):
  capacity_is_commitment: false
  ability_creates_obligation: false
  availability_allocates_resources: false
  memory_matches_capacity_to_need: false
  memory_assigns_helpers: false
  append_only: true
  reopenable: true
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

_REPO_ROOT = Path(__file__).resolve().parents[4]
_CAPACITY_EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
_FORECAST_EXAMPLES = _REPO_ROOT / "bridge" / "gitsea" / "need_forecast" / "examples"
_SAVE_PATH = _CAPACITY_EXAMPLES / "capacity-memory.json"

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
    "memory_matches_capacity_to_need":  False,
    "memory_assigns_helpers":           False,
}


def _load_capacities():
    path = _CAPACITY_EXAMPLES / "capacity-registry.json"
    if path.exists():
        try:
            data = json.loads(path.read_text())
            return data.get("capacities", []) if isinstance(data, dict) else data
        except Exception:
            pass
    try:
        from capacity_registry import build_registry  # type: ignore
        return build_registry().get("capacities", [])
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


def build_memories():
    capacities = _load_capacities()
    forecast_index = _load_forecast_index()

    # Group capacities by commons
    by_commons = {}
    for c in capacities:
        cid = c.get("commons_id", "unknown")
        by_commons.setdefault(cid, []).append(c)

    # Map forecasts by commons (advisory juxtaposition, NOT a match)
    forecasts_by_commons = {}
    for fid, f in forecast_index.items():
        cid = f.get("commons_id", "unknown")
        forecasts_by_commons.setdefault(cid, []).append(fid)

    memories = []
    seq = 1
    for cid in sorted(by_commons):
        cap_records = by_commons[cid]
        cap_ids = [c["capacity_id"] for c in cap_records if "capacity_id" in c]
        related_forecasts = forecasts_by_commons.get(cid, [])
        primary_forecast = related_forecasts[0] if related_forecasts else None

        memory = {
            "record_type":                  "commons_capacity_memory",
            "memory_id":                    f"capacity-memory-{seq:03d}",
            "commons_id":                   cid,
            "forecast_id":                  primary_forecast,
            "related_forecast_ids":         related_forecasts,
            "capacity_ids":                 cap_ids,
            "capacity_count":               len(cap_ids),
            "juxtaposition_note": (
                "Observed capacity and anticipated need are recorded side by side "
                "for human consideration. Dan-Go does not match them or assign helpers."
            ),
            "authority":                    "none",
            "ability_creates_obligation":   False,
            "memory_matches_capacity_to_need": False,
            "memory_assigns_helpers":       False,
            "generated_at":                 datetime.now(timezone.utc).isoformat(),
        }
        memory.update(PHASE_INVARIANTS)
        memories.append(memory)
        seq += 1

    return {
        "record_type":                      "commons_capacity_memory_set",
        "memory_set_id":                    "capacity-memory-set-001",
        "memory_count":                     len(memories),
        "memories":                         memories,
        "authority":                        "none",
        "capacity_is_commitment":           False,
        "ability_creates_obligation":       False,
        "availability_allocates_resources": False,
        "generated_at":                     datetime.now(timezone.utc).isoformat(),
        "phase":                            50,
        "phase_phrase_1":                   "Capacity is not commitment.",
        "phase_phrase_2":                   "Ability is not obligation.",
        "phase_phrase_3":                   "Availability is not allocation.",
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
            f"forecast={m['forecast_id']} "
            f"capacity_ids={m['capacity_ids']} "
            f"ability_creates_obligation={m['ability_creates_obligation']}",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
