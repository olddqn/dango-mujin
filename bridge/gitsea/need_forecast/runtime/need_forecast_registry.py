"""
need_forecast_registry.py — Commons Need Forecast Memory Layer (Phase 21)
Dan-Go / GITSEA Bridge · authority: none · stdlib only

"Forecast is not certainty."
"Preparedness is not command."
"Hint is not allocation."

Records preparedness memories derived from recurring aid patterns observed
in Phase 20. A forecast record says: based on what has been observed,
this type of need may arise again in this commons. It does not certify that
the need will arise. It does not predict timing, frequency, or magnitude.
It does not instruct anyone to prepare. It only makes the observed pattern
legible as a preparedness memory.

Invariants (all permanent):
  authority: none
  execution_allowed: false
  moves_money: false
  credit_issued: false
  hard_enforcement: false
  advisory: true
  forecast_memory_only: true
  append_only: true
  contestable: true
  reopenable: true
  forecast_is_certainty: false
  preparedness_is_command: false
  hint_is_allocation: false
  forecast_allocates_resources: false
  forecast_compels_preparation: false
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

_REPO_ROOT = Path(__file__).resolve().parents[4]
_PATTERN_EXAMPLES = _REPO_ROOT / "bridge" / "gitsea" / "aid_patterns" / "examples"
_SAVE_PATH = Path(__file__).resolve().parents[1] / "examples" / "need-forecast-registry.json"

PHASE_INVARIANTS = {
    "authority":                    "none",
    "execution_allowed":            False,
    "moves_money":                  False,
    "credit_issued":                False,
    "hard_enforcement":             False,
    "advisory":                     True,
    "forecast_memory_only":         True,
    "append_only":                  True,
    "contestable":                  True,
    "reopenable":                   True,
    "forecast_is_certainty":        False,
    "preparedness_is_command":      False,
    "hint_is_allocation":           False,
    "forecast_allocates_resources": False,
    "forecast_compels_preparation": False,
}

# confidence_label values communicate how weakly-grounded the forecast memory is
CONFIDENCE_LABELS = {
    "observed_pattern_only":   "Derived solely from observed recurrence count; no causal analysis performed.",
    "single_observation":      "Only one observation; not yet a pattern; weakest confidence.",
    "two_observations":        "Two observations; emerging pattern; low confidence.",
    "four_plus_observations":  "Four or more observations; stronger pattern signal; still not certainty.",
}

DEFAULT_FORECASTS = [
    {
        "forecast_id":        "need-forecast-001",
        "commons_id":         "jammy-house-001",
        "source_pattern_id":  "aid-pattern-001",
        "forecast_type":      "recurring_food_support_possible",
        "observed_count":     3,
        "confidence_label":   "observed_pattern_only",
        "forecast_note":      "Food support need observed three times in Jammy House. Pattern may continue.",
    },
    {
        "forecast_id":        "need-forecast-002",
        "commons_id":         "dra-001",
        "source_pattern_id":  "aid-pattern-002",
        "forecast_type":      "ongoing_displacement_relief_possible",
        "observed_count":     4,
        "confidence_label":   "four_plus_observations",
        "forecast_note":      "Displacement relief need observed four times in D.R.A. Ongoing pattern may continue.",
    },
    {
        "forecast_id":        "need-forecast-003",
        "commons_id":         "jammy-house-001",
        "source_pattern_id":  "aid-pattern-003",
        "forecast_type":      "unresolved_tenancy_followup_possible",
        "observed_count":     2,
        "confidence_label":   "two_observations",
        "forecast_note":      "Tenancy situation unresolved across two observations. Further advocacy may be warranted.",
    },
    {
        "forecast_id":        "need-forecast-004",
        "commons_id":         "yacypherpunks-001",
        "source_pattern_id":  "aid-pattern-004",
        "forecast_type":      "skill_exchange_rescheduling_possible",
        "observed_count":     1,
        "confidence_label":   "single_observation",
        "forecast_note":      "Skill exchange recorded once as pending. Single observation only.",
    },
]


def _load_pattern_index():
    path = _PATTERN_EXAMPLES / "aid-pattern-registry.json"
    if path.exists():
        try:
            data = json.loads(path.read_text())
            records = []
            if isinstance(data, dict):
                records = data.get("patterns", [])
            elif isinstance(data, list):
                records = data
            return {r["pattern_id"]: r for r in records if "pattern_id" in r}
        except Exception:
            pass
    return {}


def build_forecast_entry(raw, pattern_index):
    """Build a full forecast entry with invariants and optional pattern enrichment."""
    entry = dict(raw)
    entry["record_type"] = "need_forecast"
    pid = entry.get("source_pattern_id", "")
    if pid in pattern_index:
        pat = pattern_index[pid]
        entry["pattern_type"] = pat.get("pattern_type", "unknown")
        entry["source_loops"] = pat.get("source_loops", [])
    cl = entry.get("confidence_label", "observed_pattern_only")
    entry["confidence_description"] = CONFIDENCE_LABELS.get(cl, "No additional confidence description.")
    entry["generated_at"] = datetime.now(timezone.utc).isoformat()
    entry.update(PHASE_INVARIANTS)
    return entry


def build_registry(forecasts=None):
    pattern_index = _load_pattern_index()
    if forecasts is None:
        forecasts = DEFAULT_FORECASTS
    records = [build_forecast_entry(f, pattern_index) for f in forecasts]
    commons_ids = sorted({r["commons_id"] for r in records})
    forecast_types = sorted({r["forecast_type"] for r in records})
    return {
        "record_type":               "need_forecast_registry",
        "registry_id":               "need-forecast-registry-001",
        "forecast_count":            len(records),
        "commons_represented":       commons_ids,
        "forecast_types_observed":   forecast_types,
        "forecasts":                 records,
        "authority":                 "none",
        "forecast_is_certainty":     False,
        "preparedness_is_command":   False,
        "hint_is_allocation":        False,
        "forecast_allocates_resources": False,
        "generated_at":              datetime.now(timezone.utc).isoformat(),
        "phase":                     21,
        "phase_phrase_1":            "Forecast is not certainty.",
        "phase_phrase_2":            "Preparedness is not command.",
        "phase_phrase_3":            "Hint is not allocation.",
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
    print(f"  forecast_count: {registry['forecast_count']}", file=sys.stderr)
    print(f"  commons_represented: {registry['commons_represented']}", file=sys.stderr)
    for f in registry["forecasts"]:
        print(
            f"    {f['forecast_id']}: {f['forecast_type']} "
            f"(observed_count={f['observed_count']}) "
            f"confidence={f['confidence_label']} "
            f"forecast_is_certainty={f['forecast_is_certainty']}",
            file=sys.stderr,
        )
    print(f"  forecast_allocates_resources={registry['forecast_allocates_resources']}", file=sys.stderr)


if __name__ == "__main__":
    main()
