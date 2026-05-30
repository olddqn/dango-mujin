"""
recurrence_snapshot.py — Aid Pattern Learning Layer (Phase 20)
Dan-Go / GITSEA Bridge · authority: none · stdlib only

"Recurrence is not ranking."
"Pattern is not prediction."
"Learning is not prescription."

Records individual recurrence observations — each time a need type
appears again within a commons. A recurrence record does not rank
which need is more urgent or more deserving. It does not rank which
commons is more distressed. It does not imply that the previous
response was insufficient.

Invariants (all permanent):
  recurrence_is_ranking: false
  ranks_suffering: false
  recurrence_judges_prior_response: false
  recurrence_demands_new_response: false
  recurrence_certifies_failure: false
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

_REPO_ROOT = Path(__file__).resolve().parents[4]
_PATTERN_EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
_SAVE_PATH = _PATTERN_EXAMPLES / "recurrence-snapshot.json"

PHASE_INVARIANTS = {
    "authority":                        "none",
    "execution_allowed":                False,
    "moves_money":                      False,
    "credit_issued":                    False,
    "hard_enforcement":                 False,
    "advisory":                         True,
    "pattern_learning_only":            True,
    "append_only":                      True,
    "contestable":                      True,
    "reopenable":                       True,
    "recurrence_is_ranking":            False,
    "ranks_suffering":                  False,
    "recurrence_judges_prior_response": False,
    "recurrence_demands_new_response":  False,
    "recurrence_certifies_failure":     False,
    "pattern_is_prediction":            False,
    "learning_is_prescription":         False,
}

DEFAULT_RECURRENCES = [
    {
        "recurrence_id":   "recurrence-001",
        "pattern_id":      "aid-pattern-001",
        "commons_id":      "jammy-house-001",
        "recurrence_type": "food_need_reappeared",
        "count":           3,
        "linked_loop_ids": ["care-loop-001", "care-loop-003"],
        "linked_case_ids": ["relief-case-001"],
        "observation_note": "Food support need observed recurring across three recorded instances in Jammy House.",
    },
    {
        "recurrence_id":   "recurrence-002",
        "pattern_id":      "aid-pattern-002",
        "commons_id":      "dra-001",
        "recurrence_type": "displacement_relief_ongoing",
        "count":           4,
        "linked_loop_ids": ["care-loop-002"],
        "linked_case_ids": ["relief-case-003", "relief-case-004"],
        "observation_note": "Displacement relief need recorded across four observations in D.R.A. context.",
    },
    {
        "recurrence_id":   "recurrence-003",
        "pattern_id":      "aid-pattern-003",
        "commons_id":      "jammy-house-001",
        "recurrence_type": "tenancy_unresolved_continued",
        "count":           2,
        "linked_loop_ids": ["care-loop-001"],
        "linked_case_ids": ["relief-case-002"],
        "observation_note": "Housing advocacy cases recorded without tenancy resolution across two observations.",
    },
    {
        "recurrence_id":   "recurrence-004",
        "pattern_id":      "aid-pattern-004",
        "commons_id":      "yacypherpunks-001",
        "recurrence_type": "skill_exchange_deferred",
        "count":           1,
        "linked_loop_ids": ["care-loop-004"],
        "linked_case_ids": ["relief-case-005"],
        "observation_note": "Skill exchange session recorded once as pending; not yet a recurrence pattern.",
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


def build_recurrence_entry(raw, pattern_index):
    """Build a recurrence record with all invariants."""
    entry = dict(raw)
    entry["record_type"] = "recurrence_observation"
    pid = entry.get("pattern_id", "")
    if pid in pattern_index:
        pat = pattern_index[pid]
        entry["pattern_type"] = pat.get("pattern_type", "unknown")
    entry["generated_at"] = datetime.now(timezone.utc).isoformat()
    entry.update(PHASE_INVARIANTS)
    return entry


def build_snapshot(recurrences=None):
    pattern_index = _load_pattern_index()
    if recurrences is None:
        recurrences = DEFAULT_RECURRENCES
    records = [build_recurrence_entry(r, pattern_index) for r in recurrences]
    urgency_note = "No urgency ranking applied — recurrence_is_ranking: false on all records."
    commons_counts = {}
    for r in records:
        cid = r["commons_id"]
        commons_counts[cid] = commons_counts.get(cid, 0) + 1
    return {
        "record_type":            "recurrence_snapshot",
        "snapshot_id":            "recurrence-snapshot-001",
        "recurrence_count":       len(records),
        "commons_counts":         commons_counts,
        "urgency_note":           urgency_note,
        "recurrences":            records,
        "authority":              "none",
        "recurrence_is_ranking":  False,
        "ranks_suffering":        False,
        "pattern_is_prediction":  False,
        "learning_is_prescription": False,
        "generated_at":           datetime.now(timezone.utc).isoformat(),
        "phase":                  20,
        "phase_phrase_1":         "Pattern is not prediction.",
        "phase_phrase_2":         "Learning is not prescription.",
        "phase_phrase_3":         "Recurrence is not ranking.",
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
    print(f"  recurrence_count: {snapshot['recurrence_count']}", file=sys.stderr)
    for r in snapshot["recurrences"]:
        print(
            f"    {r['recurrence_id']}: {r['recurrence_type']} "
            f"(count={r['count']}) "
            f"recurrence_is_ranking={r['recurrence_is_ranking']} "
            f"ranks_suffering={r['ranks_suffering']}",
            file=sys.stderr,
        )
    print(f"  urgency_note: {snapshot['urgency_note']}", file=sys.stderr)


if __name__ == "__main__":
    main()
