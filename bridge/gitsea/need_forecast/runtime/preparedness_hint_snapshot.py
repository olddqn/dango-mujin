"""
preparedness_hint_snapshot.py — Commons Need Forecast Memory Layer (Phase 21)
Dan-Go / GITSEA Bridge · authority: none · stdlib only

"Preparedness is not command."
"Forecast is not certainty."
"Hint is not allocation."

Records preparedness hints for commons without commanding action or
allocating resources. A hint record says: given the observed pattern,
this type of capacity awareness may be useful to the commons. It does
not tell the commons what to do. It does not require any participant to
act. It does not assign resources. It does not create obligation.

A hint is information for voluntary consideration. Nothing more.

Invariants (all permanent):
  preparedness_is_command: false
  hint_is_allocation: false
  hint_compels_action: false
  hint_assigns_resources: false
  hint_creates_obligation: false
  voluntary: true
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

_REPO_ROOT = Path(__file__).resolve().parents[4]
_FORECAST_EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
_SAVE_PATH = _FORECAST_EXAMPLES / "preparedness-hint-snapshot.json"

PHASE_INVARIANTS = {
    "authority":                 "none",
    "execution_allowed":         False,
    "moves_money":               False,
    "credit_issued":             False,
    "hard_enforcement":          False,
    "advisory":                  True,
    "forecast_memory_only":      True,
    "append_only":               True,
    "contestable":               True,
    "reopenable":                True,
    "forecast_is_certainty":     False,
    "preparedness_is_command":   False,
    "hint_is_allocation":        False,
    "hint_compels_action":       False,
    "hint_assigns_resources":    False,
    "hint_creates_obligation":   False,
    "voluntary":                 True,
}

DEFAULT_HINTS = [
    {
        "hint_id":              "preparedness-hint-001",
        "forecast_id":          "need-forecast-001",
        "commons_id":           "jammy-house-001",
        "hint_type":            "meal_capacity_awareness",
        "hint_description":     (
            "Food support need has been observed recurring in this commons. "
            "Awareness of available meal preparation capacity may be useful."
        ),
        "suggested_awareness":  "meal_preparation_capacity",
        "hint_note":            "This hint does not require any action. Commons may voluntarily consider it.",
    },
    {
        "hint_id":              "preparedness-hint-002",
        "forecast_id":          "need-forecast-002",
        "commons_id":           "dra-001",
        "hint_type":            "displacement_relief_readiness_awareness",
        "hint_description":     (
            "Displacement relief need has been observed as ongoing across four instances. "
            "Awareness of available supply sharing and shelter hosting capacity may be useful."
        ),
        "suggested_awareness":  "supply_and_shelter_capacity",
        "hint_note":            "This hint does not require any action. Commons may voluntarily consider it.",
    },
    {
        "hint_id":              "preparedness-hint-003",
        "forecast_id":          "need-forecast-003",
        "commons_id":           "jammy-house-001",
        "hint_type":            "housing_advocacy_continuation_awareness",
        "hint_description":     (
            "Tenancy situation has remained unresolved across two observations. "
            "Awareness of ongoing advocacy continuation options may be useful."
        ),
        "suggested_awareness":  "housing_advocacy_capacity",
        "hint_note":            "This hint does not require any action. Commons may voluntarily consider it.",
    },
    {
        "hint_id":              "preparedness-hint-004",
        "forecast_id":          "need-forecast-004",
        "commons_id":           "yacypherpunks-001",
        "hint_type":            "skill_exchange_rescheduling_awareness",
        "hint_description":     (
            "Skill exchange session was recorded as pending. "
            "Awareness of rescheduling options may be useful if session has not occurred."
        ),
        "suggested_awareness":  "skill_sharing_availability",
        "hint_note":            "This hint does not require any action. Commons may voluntarily consider it.",
    },
]


def _load_forecast_index():
    path = _FORECAST_EXAMPLES / "need-forecast-registry.json"
    if path.exists():
        try:
            data = json.loads(path.read_text())
            records = []
            if isinstance(data, dict):
                records = data.get("forecasts", [])
            elif isinstance(data, list):
                records = data
            return {r["forecast_id"]: r for r in records if "forecast_id" in r}
        except Exception:
            pass
    return {}


def build_hint_entry(raw, forecast_index):
    """Build a preparedness hint with all invariants."""
    entry = dict(raw)
    entry["record_type"] = "preparedness_hint"
    fid = entry.get("forecast_id", "")
    if fid in forecast_index:
        fc = forecast_index[fid]
        entry["forecast_type"] = fc.get("forecast_type", "unknown")
        entry["source_pattern_id"] = fc.get("source_pattern_id", "unknown")
        entry["forecast_confidence_label"] = fc.get("confidence_label", "observed_pattern_only")
    entry["generated_at"] = datetime.now(timezone.utc).isoformat()
    entry.update(PHASE_INVARIANTS)
    return entry


def build_snapshot(hints=None):
    forecast_index = _load_forecast_index()
    if hints is None:
        hints = DEFAULT_HINTS
    records = [build_hint_entry(h, forecast_index) for h in hints]
    hint_types = sorted({r["hint_type"] for r in records})
    commons_counts = {}
    for r in records:
        cid = r["commons_id"]
        commons_counts[cid] = commons_counts.get(cid, 0) + 1
    return {
        "record_type":              "preparedness_hint_snapshot",
        "snapshot_id":              "preparedness-hint-snapshot-001",
        "hint_count":               len(records),
        "hint_types":               hint_types,
        "commons_counts":           commons_counts,
        "hints":                    records,
        "authority":                "none",
        "preparedness_is_command":  False,
        "hint_is_allocation":       False,
        "hint_compels_action":      False,
        "hint_assigns_resources":   False,
        "forecast_is_certainty":    False,
        "generated_at":             datetime.now(timezone.utc).isoformat(),
        "phase":                    21,
        "phase_phrase_1":           "Forecast is not certainty.",
        "phase_phrase_2":           "Preparedness is not command.",
        "phase_phrase_3":           "Hint is not allocation.",
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
    print(f"  hint_count: {snapshot['hint_count']}", file=sys.stderr)
    for h in snapshot["hints"]:
        print(
            f"    {h['hint_id']}: {h['hint_type']} "
            f"({h['commons_id']}) "
            f"preparedness_is_command={h['preparedness_is_command']} "
            f"hint_is_allocation={h['hint_is_allocation']}",
            file=sys.stderr,
        )
    print(f"  hint_assigns_resources={snapshot['hint_assigns_resources']}", file=sys.stderr)


if __name__ == "__main__":
    main()
