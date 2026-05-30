"""
aid_pattern_registry.py — Aid Pattern Learning Layer (Phase 20)
Dan-Go / GITSEA Bridge · authority: none · stdlib only

"Pattern is not prediction."
"Learning is not prescription."
"Recurrence is not ranking."

Records recurring aid patterns observed across care loops (Phase 19),
relief cases (Phase 18), and aid routes (Phase 17). A pattern record
says: this type of need has appeared more than once in this commons.
It does not predict future need. It does not prescribe a response.
It does not rank which commons needs more help.

Invariants (all permanent):
  authority: none
  execution_allowed: false
  moves_money: false
  credit_issued: false
  hard_enforcement: false
  advisory: true
  pattern_learning_only: true
  append_only: true
  contestable: true
  reopenable: true
  pattern_is_prediction: false
  learning_is_prescription: false
  recurrence_is_ranking: false
  pattern_ranks_commons: false
  pattern_compels_response: false
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

_REPO_ROOT = Path(__file__).resolve().parents[4]
_CARE_LOOP_EXAMPLES = _REPO_ROOT / "bridge" / "gitsea" / "care_loop" / "examples"
_RELIEF_EXAMPLES = _REPO_ROOT / "bridge" / "gitsea" / "relief" / "examples"
_AID_EXAMPLES = _REPO_ROOT / "bridge" / "gitsea" / "mutual_aid" / "examples"
_SAVE_PATH = Path(__file__).resolve().parents[1] / "examples" / "aid-pattern-registry.json"

PHASE_INVARIANTS = {
    "authority":                  "none",
    "execution_allowed":          False,
    "moves_money":                False,
    "credit_issued":              False,
    "hard_enforcement":           False,
    "advisory":                   True,
    "pattern_learning_only":      True,
    "append_only":                True,
    "contestable":                True,
    "reopenable":                 True,
    "pattern_is_prediction":      False,
    "learning_is_prescription":   False,
    "recurrence_is_ranking":      False,
    "pattern_ranks_commons":      False,
    "pattern_compels_response":   False,
}

DEFAULT_PATTERNS = [
    {
        "pattern_id":      "aid-pattern-001",
        "commons_id":      "jammy-house-001",
        "pattern_type":    "recurring_food_support",
        "observed_count":  3,
        "source_loops":    ["care-loop-001", "care-loop-003"],
        "source_cases":    ["relief-case-001"],
        "source_routes":   ["aid-route-001"],
        "first_observed":  "2025-11-01",
        "last_observed":   "2026-03-15",
        "pattern_note":    "Food support need observed multiple times in Jammy House context.",
    },
    {
        "pattern_id":      "aid-pattern-002",
        "commons_id":      "dra-001",
        "pattern_type":    "ongoing_displacement_relief",
        "observed_count":  4,
        "source_loops":    ["care-loop-002"],
        "source_cases":    ["relief-case-003", "relief-case-004"],
        "source_routes":   ["aid-route-003", "aid-route-004"],
        "first_observed":  "2025-09-10",
        "last_observed":   "2026-04-02",
        "pattern_note":    "Displacement-related relief need observed as ongoing across D.R.A. cases.",
    },
    {
        "pattern_id":      "aid-pattern-003",
        "commons_id":      "jammy-house-001",
        "pattern_type":    "unresolved_tenancy_pattern",
        "observed_count":  2,
        "source_loops":    ["care-loop-001"],
        "source_cases":    ["relief-case-002"],
        "source_routes":   ["aid-route-002"],
        "first_observed":  "2025-12-05",
        "last_observed":   "2026-02-20",
        "pattern_note":    "Housing advocacy cases recorded without final tenancy resolution.",
    },
    {
        "pattern_id":      "aid-pattern-004",
        "commons_id":      "yacypherpunks-001",
        "pattern_type":    "pending_skill_exchange",
        "observed_count":  1,
        "source_loops":    ["care-loop-004"],
        "source_cases":    ["relief-case-005"],
        "source_routes":   ["aid-route-005"],
        "first_observed":  "2026-01-14",
        "last_observed":   "2026-01-14",
        "pattern_note":    "Skill exchange session recorded as pending; may need rescheduling.",
    },
]


def _load_care_loops():
    path = _CARE_LOOP_EXAMPLES / "care-loop.json"
    if path.exists():
        try:
            data = json.loads(path.read_text())
            if isinstance(data, list):
                return {r["care_loop_id"]: r for r in data if "care_loop_id" in r}
            if isinstance(data, dict):
                for key in ("loops", "care_loops", "records"):
                    if key in data and isinstance(data[key], list):
                        return {r["care_loop_id"]: r for r in data[key] if "care_loop_id" in r}
        except Exception:
            pass
    return {}


def build_pattern_entry(raw, loops_index):
    """Build a full aid pattern entry with all invariants."""
    entry = dict(raw)
    entry["record_type"] = "aid_pattern"
    # Enrich with loop summary data if available
    loop_statuses = []
    for lid in entry.get("source_loops", []):
        if lid in loops_index:
            loop_statuses.append(loops_index[lid].get("loop_status", "unknown"))
    if loop_statuses:
        entry["source_loop_statuses"] = loop_statuses
    entry["generated_at"] = datetime.now(timezone.utc).isoformat()
    entry.update(PHASE_INVARIANTS)
    return entry


def build_registry(patterns=None):
    loops_index = _load_care_loops()
    if patterns is None:
        patterns = DEFAULT_PATTERNS
    records = [build_pattern_entry(p, loops_index) for p in patterns]
    commons_ids = sorted({r["commons_id"] for r in records})
    pattern_types = sorted({r["pattern_type"] for r in records})
    return {
        "record_type":             "aid_pattern_registry",
        "registry_id":             "aid-pattern-registry-001",
        "pattern_count":           len(records),
        "commons_represented":     commons_ids,
        "pattern_types_observed":  pattern_types,
        "patterns":                records,
        "authority":               "none",
        "pattern_is_prediction":   False,
        "learning_is_prescription": False,
        "recurrence_is_ranking":   False,
        "pattern_ranks_commons":   False,
        "generated_at":            datetime.now(timezone.utc).isoformat(),
        "phase":                   20,
        "phase_phrase_1":          "Pattern is not prediction.",
        "phase_phrase_2":          "Learning is not prescription.",
        "phase_phrase_3":          "Recurrence is not ranking.",
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
    # Print summary to stderr
    print(f"\n  registry_id: {registry['registry_id']}", file=sys.stderr)
    print(f"  pattern_count: {registry['pattern_count']}", file=sys.stderr)
    print(f"  commons_represented: {registry['commons_represented']}", file=sys.stderr)
    for p in registry["patterns"]:
        print(
            f"    {p['pattern_id']}: {p['pattern_type']} "
            f"(observed_count={p['observed_count']}) "
            f"pattern_is_prediction={p['pattern_is_prediction']}",
            file=sys.stderr,
        )
    print(f"  pattern_ranks_commons={registry['pattern_ranks_commons']}", file=sys.stderr)


if __name__ == "__main__":
    main()
