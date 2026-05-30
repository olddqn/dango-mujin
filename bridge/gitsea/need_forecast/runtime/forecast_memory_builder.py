"""
forecast_memory_builder.py — Commons Need Forecast Memory Layer (Phase 21)
Dan-Go / GITSEA Bridge · authority: none · stdlib only

"Forecast is not certainty."
"Preparedness is not command."
"Hint is not allocation."

Builds forecast memory records by linking a need forecast to the Phase 20
aid pattern records that generated it, and to the Phase 17–19 care records
in the pattern's source chain. The forecast memory record makes the full
observation chain legible in one place.

The memory is append-only and reopenable. New observations can extend the
forecast memory without modifying prior records. Dan-Go does not certify
that the forecasted need has been addressed. It records the memory.

Invariants (all permanent):
  forecast_is_certainty: false
  memory_certifies_resolution: false
  memory_compels_preparation: false
  memory_allocates_resources: false
  memory_judges_commons: false
  append_only: true
  reopenable: true
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

_REPO_ROOT = Path(__file__).resolve().parents[4]
_FORECAST_EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
_PATTERN_EXAMPLES = _REPO_ROOT / "bridge" / "gitsea" / "aid_patterns" / "examples"
_CARE_LOOP_EXAMPLES = _REPO_ROOT / "bridge" / "gitsea" / "care_loop" / "examples"
_SAVE_PATH = _FORECAST_EXAMPLES / "forecast-memory.json"

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
    "memory_certifies_resolution":  False,
    "memory_compels_preparation":   False,
    "memory_allocates_resources":   False,
    "memory_judges_commons":        False,
}

DEFAULT_MEMORIES = [
    {
        "forecast_memory_id": "forecast-memory-001",
        "forecast_id":        "need-forecast-001",
        "hint_id":            "preparedness-hint-001",
        "commons_id":         "jammy-house-001",
        "source_patterns":    ["aid-pattern-001"],
        "source_loops":       ["care-loop-001", "care-loop-003"],
        "source_cases":       ["relief-case-001"],
        "source_routes":      ["aid-route-001"],
        "memory_status":      "recorded",
        "memory_note":        "Food support forecast memory for Jammy House. Three observed instances across Phase 17–20.",
    },
    {
        "forecast_memory_id": "forecast-memory-002",
        "forecast_id":        "need-forecast-002",
        "hint_id":            "preparedness-hint-002",
        "commons_id":         "dra-001",
        "source_patterns":    ["aid-pattern-002"],
        "source_loops":       ["care-loop-002"],
        "source_cases":       ["relief-case-003", "relief-case-004"],
        "source_routes":      ["aid-route-003", "aid-route-004"],
        "memory_status":      "recorded",
        "memory_note":        "Displacement relief forecast memory for D.R.A. Four observed instances across Phase 17–20.",
    },
    {
        "forecast_memory_id": "forecast-memory-003",
        "forecast_id":        "need-forecast-003",
        "hint_id":            "preparedness-hint-003",
        "commons_id":         "jammy-house-001",
        "source_patterns":    ["aid-pattern-003"],
        "source_loops":       ["care-loop-001"],
        "source_cases":       ["relief-case-002"],
        "source_routes":      ["aid-route-002"],
        "memory_status":      "recorded",
        "memory_note":        "Tenancy advocacy forecast memory for Jammy House. Two observed instances across Phase 17–20.",
    },
    {
        "forecast_memory_id": "forecast-memory-004",
        "forecast_id":        "need-forecast-004",
        "hint_id":            "preparedness-hint-004",
        "commons_id":         "yacypherpunks-001",
        "source_patterns":    ["aid-pattern-004"],
        "source_loops":       ["care-loop-004"],
        "source_cases":       ["relief-case-005"],
        "source_routes":      ["aid-route-005"],
        "memory_status":      "recorded",
        "memory_note":        "Skill exchange forecast memory for YaCypherpunks. One observed instance; low confidence.",
    },
]


def _load_json_list(path, list_keys):
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in list_keys:
                if key in data and isinstance(data[key], list):
                    return data[key]
    except Exception:
        pass
    return []


def _load_forecast_index():
    records = _load_json_list(
        _FORECAST_EXAMPLES / "need-forecast-registry.json",
        ["forecasts", "records"],
    )
    return {r["forecast_id"]: r for r in records if "forecast_id" in r}


def _load_hint_index():
    records = _load_json_list(
        _FORECAST_EXAMPLES / "preparedness-hint-snapshot.json",
        ["hints", "records"],
    )
    return {r["hint_id"]: r for r in records if "hint_id" in r}


def _load_pattern_index():
    records = _load_json_list(
        _PATTERN_EXAMPLES / "aid-pattern-registry.json",
        ["patterns", "records"],
    )
    return {r["pattern_id"]: r for r in records if "pattern_id" in r}


def build_memory_entry(raw, forecast_index, hint_index, pattern_index):
    """Build a forecast memory entry with full cross-phase linkage."""
    entry = dict(raw)
    entry["record_type"] = "forecast_memory"
    fid = entry.get("forecast_id", "")
    if fid in forecast_index:
        fc = forecast_index[fid]
        entry["forecast_type"] = fc.get("forecast_type", "unknown")
        entry["confidence_label"] = fc.get("confidence_label", "observed_pattern_only")
        entry["observed_count"] = fc.get("observed_count", 0)
    hid = entry.get("hint_id", "")
    if hid in hint_index:
        h = hint_index[hid]
        entry["hint_type"] = h.get("hint_type", "unknown")
    # Enrich with pattern type from Phase 20 if available
    for pid in entry.get("source_patterns", []):
        if pid in pattern_index:
            entry["source_pattern_type"] = pattern_index[pid].get("pattern_type", "unknown")
            break
    entry["generated_at"] = datetime.now(timezone.utc).isoformat()
    entry.update(PHASE_INVARIANTS)
    return entry


def build_memory(memories=None):
    forecast_index = _load_forecast_index()
    hint_index = _load_hint_index()
    pattern_index = _load_pattern_index()
    if memories is None:
        memories = DEFAULT_MEMORIES
    records = [build_memory_entry(m, forecast_index, hint_index, pattern_index) for m in memories]
    status_summary = {}
    for r in records:
        s = r.get("memory_status", "unknown")
        status_summary[s] = status_summary.get(s, 0) + 1
    return {
        "record_type":                "forecast_memory_log",
        "log_id":                     "forecast-memory-log-001",
        "memory_count":               len(records),
        "status_summary":             status_summary,
        "memories":                   records,
        "authority":                  "none",
        "forecast_is_certainty":      False,
        "preparedness_is_command":    False,
        "hint_is_allocation":         False,
        "memory_certifies_resolution": False,
        "memory_compels_preparation": False,
        "generated_at":               datetime.now(timezone.utc).isoformat(),
        "phase":                      21,
        "phase_phrase_1":             "Forecast is not certainty.",
        "phase_phrase_2":             "Preparedness is not command.",
        "phase_phrase_3":             "Hint is not allocation.",
    }


def main():
    save = "--save" in sys.argv
    log = build_memory()
    out = json.dumps(log, indent=2)
    print(out)
    if save:
        _SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _SAVE_PATH.write_text(out)
        print(f"\n[saved → {_SAVE_PATH}]", file=sys.stderr)
    print(f"\n  log_id: {log['log_id']}", file=sys.stderr)
    print(f"  memory_count: {log['memory_count']}", file=sys.stderr)
    print(f"  status_summary: {log['status_summary']}", file=sys.stderr)
    for m in log["memories"]:
        print(
            f"    {m['forecast_memory_id']}: {m.get('forecast_type','?')} "
            f"({m['commons_id']}) "
            f"memory_status={m['memory_status']} "
            f"forecast_is_certainty={m['forecast_is_certainty']}",
            file=sys.stderr,
        )
    print(f"  memory_compels_preparation={log['memory_compels_preparation']}", file=sys.stderr)
    print(f"  memory_certifies_resolution={log['memory_certifies_resolution']}", file=sys.stderr)


if __name__ == "__main__":
    main()
