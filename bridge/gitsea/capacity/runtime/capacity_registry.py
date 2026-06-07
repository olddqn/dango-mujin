"""
capacity_registry.py — Commons Capacity Memory Layer (Phase 50)
Dan-Go / GITSEA Bridge · authority: none · stdlib only

"Capacity is not commitment."
"Ability is not obligation."
"Availability is not allocation."

Records observable capacities within commons. A capacity record says:
this commons appears able to offer this kind of help, at this observed
availability. It does NOT say the commons has agreed to help, will help,
or owes help. It does not allocate the capacity to any need. It only
makes observable ability legible.

Invariants (all permanent):
  authority: none
  execution_allowed: false
  moves_money: false
  credit_issued: false
  hard_enforcement: false
  advisory: true
  capacity_only: true
  append_only: true
  contestable: true
  reopenable: true
  capacity_is_commitment: false
  ability_creates_obligation: false
  availability_allocates_resources: false
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

_REPO_ROOT = Path(__file__).resolve().parents[4]
_COMMONS_EXAMPLES = _REPO_ROOT / "bridge" / "gitsea" / "commons" / "examples"
_SAVE_PATH = Path(__file__).resolve().parents[1] / "examples" / "capacity-registry.json"

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
}

# availability_label values communicate observed rhythm, not a promise of timing
AVAILABILITY_LABELS = {
    "weekly":      "Observed roughly once per week; not a scheduled commitment.",
    "monthly":     "Observed roughly once per month; not a scheduled commitment.",
    "occasional":  "Observed irregularly; availability cannot be relied upon.",
    "on_request":  "Observed to respond when asked; no standing availability implied.",
    "seasonal":    "Observed during certain periods only; not year-round.",
    "unknown":     "Availability not yet observed; recorded as capacity existence only.",
}

DEFAULT_CAPACITIES = [
    {
        "capacity_id":    "capacity-001",
        "commons_id":     "jammy-house-001",
        "capacity_type":  "meal_preparation",
        "participants":   4,
        "availability":   "weekly",
        "capacity_note":  "Jammy House participants have prepared shared meals on a roughly weekly rhythm.",
    },
    {
        "capacity_id":    "capacity-002",
        "commons_id":     "jammy-house-001",
        "capacity_type":  "overnight_space",
        "participants":   2,
        "availability":   "on_request",
        "capacity_note":  "Two participants have offered overnight space when asked.",
    },
    {
        "capacity_id":    "capacity-003",
        "commons_id":     "dra-001",
        "capacity_type":  "displacement_relief_coordination",
        "participants":   5,
        "availability":   "occasional",
        "capacity_note":  "D.R.A. participants have coordinated relief efforts during displacement events.",
    },
    {
        "capacity_id":    "capacity-004",
        "commons_id":     "yacypherpunks-001",
        "capacity_type":  "translation_support",
        "participants":   3,
        "availability":   "on_request",
        "capacity_note":  "Three participants have provided translation when requested.",
    },
]


def _load_commons_index():
    path = _COMMONS_EXAMPLES / "commons-registry.json"
    if path.exists():
        try:
            data = json.loads(path.read_text())
            records = []
            if isinstance(data, dict):
                records = data.get("commons", []) or data.get("communities", [])
            elif isinstance(data, list):
                records = data
            return {r["commons_id"]: r for r in records if "commons_id" in r}
        except Exception:
            pass
    return {}


def build_capacity_entry(raw, commons_index):
    """Build a full capacity entry with invariants and optional commons enrichment."""
    entry = dict(raw)
    entry["record_type"] = "commons_capacity"
    cid = entry.get("commons_id", "")
    if cid in commons_index:
        cm = commons_index[cid]
        entry["commons_name"] = cm.get("commons_name", cm.get("name", cid))
    av = entry.get("availability", "unknown")
    entry["availability_description"] = AVAILABILITY_LABELS.get(
        av, "No additional availability description."
    )
    entry["generated_at"] = datetime.now(timezone.utc).isoformat()
    entry.update(PHASE_INVARIANTS)
    return entry


def build_registry(capacities=None):
    commons_index = _load_commons_index()
    if capacities is None:
        capacities = DEFAULT_CAPACITIES
    records = [build_capacity_entry(c, commons_index) for c in capacities]
    commons_ids = sorted({r["commons_id"] for r in records})
    capacity_types = sorted({r["capacity_type"] for r in records})
    return {
        "record_type":                      "commons_capacity_registry",
        "registry_id":                      "capacity-registry-001",
        "capacity_count":                   len(records),
        "commons_represented":              commons_ids,
        "capacity_types_observed":          capacity_types,
        "capacities":                       records,
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
    registry = build_registry()
    out = json.dumps(registry, indent=2)
    print(out)
    if save:
        _SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _SAVE_PATH.write_text(out)
        print(f"\n[saved → {_SAVE_PATH}]", file=sys.stderr)
    print(f"\n  registry_id: {registry['registry_id']}", file=sys.stderr)
    print(f"  capacity_count: {registry['capacity_count']}", file=sys.stderr)
    print(f"  commons_represented: {registry['commons_represented']}", file=sys.stderr)
    for c in registry["capacities"]:
        print(
            f"    {c['capacity_id']}: {c['capacity_type']} "
            f"(participants={c['participants']}) "
            f"availability={c['availability']} "
            f"capacity_is_commitment={c['capacity_is_commitment']}",
            file=sys.stderr,
        )
    print(
        f"  availability_allocates_resources={registry['availability_allocates_resources']}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
