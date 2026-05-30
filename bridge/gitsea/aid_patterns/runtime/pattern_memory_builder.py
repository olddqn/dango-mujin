"""
pattern_memory_builder.py — Aid Pattern Learning Layer (Phase 20)
Dan-Go / GITSEA Bridge · authority: none · stdlib only

"Learning is not prescription."
"Pattern is not prediction."
"Recurrence is not ranking."

Builds a pattern memory record by linking an observed aid pattern to
its source care loops (Phase 19), relief cases (Phase 18), and aid
routes (Phase 17). The pattern memory record makes care history legible
across phases. It does not prescribe a response. It does not compel
future aid. It does not certify that the pattern has been addressed.

The memory is append-only and reopenable. New care loop events can
extend the memory without modifying prior records.

Invariants (all permanent):
  learning_is_prescription: false
  memory_prescribes_response: false
  memory_certifies_resolution: false
  memory_compels_new_aid: false
  memory_judges_participants: false
  append_only: true
  reopenable: true
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

_REPO_ROOT = Path(__file__).resolve().parents[4]
_PATTERN_EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
_CARE_LOOP_EXAMPLES = _REPO_ROOT / "bridge" / "gitsea" / "care_loop" / "examples"
_RELIEF_EXAMPLES = _REPO_ROOT / "bridge" / "gitsea" / "relief" / "examples"
_AID_EXAMPLES = _REPO_ROOT / "bridge" / "gitsea" / "mutual_aid" / "examples"
_SAVE_PATH = _PATTERN_EXAMPLES / "pattern-memory.json"

PHASE_INVARIANTS = {
    "authority":                    "none",
    "execution_allowed":            False,
    "moves_money":                  False,
    "credit_issued":                False,
    "hard_enforcement":             False,
    "advisory":                     True,
    "pattern_learning_only":        True,
    "append_only":                  True,
    "contestable":                  True,
    "reopenable":                   True,
    "pattern_is_prediction":        False,
    "learning_is_prescription":     False,
    "recurrence_is_ranking":        False,
    "memory_prescribes_response":   False,
    "memory_certifies_resolution":  False,
    "memory_compels_new_aid":       False,
    "memory_judges_participants":   False,
}

DEFAULT_MEMORIES = [
    {
        "pattern_memory_id": "pattern-memory-001",
        "pattern_id":        "aid-pattern-001",
        "commons_id":        "jammy-house-001",
        "source_loops":      ["care-loop-001", "care-loop-003"],
        "source_cases":      ["relief-case-001"],
        "source_routes":     ["aid-route-001"],
        "source_recurrences": ["recurrence-001"],
        "memory_status":     "recorded",
        "memory_note":       "Recurring food support pattern in Jammy House. Three observations across Phase 17–19.",
    },
    {
        "pattern_memory_id": "pattern-memory-002",
        "pattern_id":        "aid-pattern-002",
        "commons_id":        "dra-001",
        "source_loops":      ["care-loop-002"],
        "source_cases":      ["relief-case-003", "relief-case-004"],
        "source_routes":     ["aid-route-003", "aid-route-004"],
        "source_recurrences": ["recurrence-002"],
        "memory_status":     "recorded",
        "memory_note":       "Ongoing displacement relief pattern in D.R.A. Four observations across Phase 17–19.",
    },
    {
        "pattern_memory_id": "pattern-memory-003",
        "pattern_id":        "aid-pattern-003",
        "commons_id":        "jammy-house-001",
        "source_loops":      ["care-loop-001"],
        "source_cases":      ["relief-case-002"],
        "source_routes":     ["aid-route-002"],
        "source_recurrences": ["recurrence-003"],
        "memory_status":     "recorded",
        "memory_note":       "Unresolved tenancy pattern in Jammy House. Two observations; housing advocacy ongoing.",
    },
    {
        "pattern_memory_id": "pattern-memory-004",
        "pattern_id":        "aid-pattern-004",
        "commons_id":        "yacypherpunks-001",
        "source_loops":      ["care-loop-004"],
        "source_cases":      ["relief-case-005"],
        "source_routes":     ["aid-route-005"],
        "source_recurrences": ["recurrence-004"],
        "memory_status":     "recorded",
        "memory_note":       "Pending skill exchange in YaCypherpunks. Single observation; not yet a recurrence.",
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


def _load_pattern_index():
    records = _load_json_list(
        _PATTERN_EXAMPLES / "aid-pattern-registry.json",
        ["patterns", "records"],
    )
    return {r["pattern_id"]: r for r in records if "pattern_id" in r}


def _load_recurrence_index():
    records = _load_json_list(
        _PATTERN_EXAMPLES / "recurrence-snapshot.json",
        ["recurrences", "records"],
    )
    return {r["recurrence_id"]: r for r in records if "recurrence_id" in r}


def _load_loop_index():
    records = _load_json_list(
        _CARE_LOOP_EXAMPLES / "care-loop.json",
        ["loops", "care_loops", "records"],
    )
    return {r["care_loop_id"]: r for r in records if "care_loop_id" in r}


def build_memory_entry(raw, pattern_index, recurrence_index, loop_index):
    """Build a pattern memory entry with all invariants and cross-phase links."""
    entry = dict(raw)
    entry["record_type"] = "pattern_memory"
    pid = entry.get("pattern_id", "")
    if pid in pattern_index:
        pat = pattern_index[pid]
        entry["pattern_type"] = pat.get("pattern_type", "unknown")
        entry["observed_count"] = pat.get("observed_count", 0)
    # Summarise recurrence data
    rec_counts = []
    for rid in entry.get("source_recurrences", []):
        if rid in recurrence_index:
            rec_counts.append(recurrence_index[rid].get("count", 0))
    if rec_counts:
        entry["total_recurrence_count"] = sum(rec_counts)
    # Summarise loop statuses
    loop_statuses = []
    for lid in entry.get("source_loops", []):
        if lid in loop_index:
            loop_statuses.append(loop_index[lid].get("loop_status", "unknown"))
    if loop_statuses:
        entry["source_loop_statuses"] = loop_statuses
    entry["generated_at"] = datetime.now(timezone.utc).isoformat()
    entry.update(PHASE_INVARIANTS)
    return entry


def build_memory(memories=None):
    pattern_index = _load_pattern_index()
    recurrence_index = _load_recurrence_index()
    loop_index = _load_loop_index()
    if memories is None:
        memories = DEFAULT_MEMORIES
    records = [build_memory_entry(m, pattern_index, recurrence_index, loop_index) for m in memories]
    status_summary = {}
    for r in records:
        s = r.get("memory_status", "unknown")
        status_summary[s] = status_summary.get(s, 0) + 1
    return {
        "record_type":              "pattern_memory_log",
        "log_id":                   "pattern-memory-log-001",
        "memory_count":             len(records),
        "status_summary":           status_summary,
        "memories":                 records,
        "authority":                "none",
        "pattern_is_prediction":    False,
        "learning_is_prescription": False,
        "recurrence_is_ranking":    False,
        "memory_prescribes_response": False,
        "memory_certifies_resolution": False,
        "generated_at":             datetime.now(timezone.utc).isoformat(),
        "phase":                    20,
        "phase_phrase_1":           "Pattern is not prediction.",
        "phase_phrase_2":           "Learning is not prescription.",
        "phase_phrase_3":           "Recurrence is not ranking.",
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
            f"    {m['pattern_memory_id']}: {m.get('pattern_type','?')} "
            f"({m['commons_id']}) "
            f"memory_status={m['memory_status']} "
            f"learning_is_prescription={m['learning_is_prescription']}",
            file=sys.stderr,
        )
    print(f"  memory_prescribes_response={log['memory_prescribes_response']}", file=sys.stderr)


if __name__ == "__main__":
    main()
