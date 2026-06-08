"""
resource_registry.py — Resource Memory Layer (Phase 51)
Dan-Go / GITSEA Bridge · authority: none · stdlib only

"Resource is not allocation."
"Possession is not obligation."
"Availability is not transfer."

Records observable resources within commons. A resource record says:
this commons appears to have this resource, in this observed quantity.
It does NOT say the resource is allocated, owned by anyone in particular
in a transferable sense, or available for assignment. It does not commit
the resource to any need. It only makes observable possession legible.

Invariants (all permanent):
  authority: none
  execution_allowed: false
  moves_money: false
  credit_issued: false
  hard_enforcement: false
  advisory: true
  resource_memory_only: true
  append_only: true
  contestable: true
  reopenable: true
  resource_is_allocation: false
  possession_creates_obligation: false
  availability_transfers_ownership: false
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

_REPO_ROOT = Path(__file__).resolve().parents[4]
_COMMONS_EXAMPLES = _REPO_ROOT / "bridge" / "gitsea" / "commons" / "examples"
_SAVE_PATH = Path(__file__).resolve().parents[1] / "examples" / "resource-registry.json"

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
}

# observability_label values communicate how the resource was observed —
# never a claim about who controls it or who may use it.
OBSERVABILITY_LABELS = {
    "directly_observed":  "Resource directly observed by a participant; counted at time of observation.",
    "self_reported":      "Resource reported by the holder; not independently observed.",
    "inferred":           "Resource inferred from prior activity records; not directly counted.",
    "documented":         "Resource recorded in a commons document or roster; presence assumed legible.",
    "unknown":            "Observability provenance not recorded; treat with extra caution.",
}

DEFAULT_RESOURCES = [
    {
        "resource_id":    "resource-001",
        "commons_id":     "jammy-house-001",
        "resource_type":  "vacant_room",
        "quantity":       2,
        "unit":           "rooms",
        "observability":  "directly_observed",
        "resource_note":  "Two rooms at Jammy House observed unoccupied during the last week.",
    },
    {
        "resource_id":    "resource-002",
        "commons_id":     "jammy-house-001",
        "resource_type":  "kitchen_equipment",
        "quantity":       1,
        "unit":           "shared kitchen",
        "observability":  "documented",
        "resource_note":  "Shared kitchen with stove, fridge, and basic cookware; documented in house roster.",
    },
    {
        "resource_id":    "resource-003",
        "commons_id":     "dra-001",
        "resource_type":  "relief_supplies",
        "quantity":       12,
        "unit":           "boxes",
        "observability":  "self_reported",
        "resource_note":  "Relief supply boxes reported by D.R.A. coordinator; not independently verified.",
    },
    {
        "resource_id":    "resource-004",
        "commons_id":     "yacypherpunks-001",
        "resource_type":  "translation_books",
        "quantity":       8,
        "unit":           "books",
        "observability":  "documented",
        "resource_note":  "Bilingual reference materials in the YacypherPunks shared library.",
    },
    {
        "resource_id":    "resource-005",
        "commons_id":     "yacypherpunks-001",
        "resource_type":  "shared_compute",
        "quantity":       1,
        "unit":           "machine",
        "observability":  "self_reported",
        "resource_note":  "One participant has offered shared compute access in the past when asked.",
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


def build_resource_entry(raw, commons_index):
    """Build a full resource entry with invariants and optional commons enrichment."""
    entry = dict(raw)
    entry["record_type"] = "commons_resource"
    cid = entry.get("commons_id", "")
    if cid in commons_index:
        cm = commons_index[cid]
        entry["commons_name"] = cm.get("commons_name", cm.get("name", cid))
    obs = entry.get("observability", "unknown")
    entry["observability_description"] = OBSERVABILITY_LABELS.get(
        obs, "No additional observability description."
    )
    entry["generated_at"] = datetime.now(timezone.utc).isoformat()
    entry.update(PHASE_INVARIANTS)
    return entry


def build_registry(resources=None):
    commons_index = _load_commons_index()
    if resources is None:
        resources = DEFAULT_RESOURCES
    records = [build_resource_entry(r, commons_index) for r in resources]
    commons_ids = sorted({r["commons_id"] for r in records})
    resource_types = sorted({r["resource_type"] for r in records})
    return {
        "record_type":                      "commons_resource_registry",
        "registry_id":                      "resource-registry-001",
        "resource_count":                   len(records),
        "commons_represented":              commons_ids,
        "resource_types_observed":          resource_types,
        "resources":                        records,
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
    registry = build_registry()
    out = json.dumps(registry, indent=2)
    print(out)
    if save:
        _SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _SAVE_PATH.write_text(out)
        print(f"\n[saved → {_SAVE_PATH}]", file=sys.stderr)
    print(f"\n  registry_id: {registry['registry_id']}", file=sys.stderr)
    print(f"  resource_count: {registry['resource_count']}", file=sys.stderr)
    print(f"  commons_represented: {registry['commons_represented']}", file=sys.stderr)
    for r in registry["resources"]:
        print(
            f"    {r['resource_id']}: {r['resource_type']} "
            f"(qty={r['quantity']} {r.get('unit','')}) "
            f"observability={r['observability']} "
            f"resource_is_allocation={r['resource_is_allocation']}",
            file=sys.stderr,
        )
    print(
        f"  availability_transfers_ownership={registry['availability_transfers_ownership']}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
