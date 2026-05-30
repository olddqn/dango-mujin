"""
aid_pattern_report.py — Aid Pattern Learning Layer (Phase 20)
Dan-Go / GITSEA Bridge · authority: none · stdlib only

"Pattern is not prediction."
"Learning is not prescription."
"Recurrence is not ranking."

Generates a 4-section advisory report explaining why:
  1. Observing a pattern does not predict future need.
  2. Recording a recurrence does not rank suffering.
  3. Building pattern memory does not prescribe a response.
  4. The aid pattern layer connects to Jammy House and D.R.A. histories.

The report is advisory only. It does not compel any participant.
It does not certify any outcome. It does not operate any external system.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

_REPO_ROOT = Path(__file__).resolve().parents[4]
_PATTERN_EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
_SAVE_PATH = _PATTERN_EXAMPLES / "aid-pattern-report.json"

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
    "pattern_ranks_commons":        False,
    "pattern_compels_response":     False,
    "memory_prescribes_response":   False,
    "memory_certifies_resolution":  False,
}


def _load_json_obj(path, list_keys):
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}


def _load_patterns():
    data = _load_json_obj(_PATTERN_EXAMPLES / "aid-pattern-registry.json", [])
    return data.get("patterns", [])


def _load_recurrences():
    data = _load_json_obj(_PATTERN_EXAMPLES / "recurrence-snapshot.json", [])
    return data.get("recurrences", [])


def _load_memories():
    data = _load_json_obj(_PATTERN_EXAMPLES / "pattern-memory.json", [])
    return data.get("memories", [])


SECTIONS = [
    {
        "section_id":    "A",
        "title":         "A Pattern Is an Observation, Not a Prediction",
        "body": (
            "Dan-Go records that a care need has appeared more than once. "
            "This observation is about the past — what was observed in prior care loops, "
            "relief cases, and aid routes. It says nothing about whether the need will appear "
            "again, how often it will recur, or when the next occurrence will happen. "
            "The pattern record is a description of history, not a forecast. "
            "'Pattern is not prediction' means the record cannot be used to anticipate, "
            "pre-empt, or decide in advance of a new need being expressed. Any community "
            "response to a recurring need must be initiated by the participants in that "
            "situation, not by the pattern record."
        ),
        "pattern_is_prediction":  False,
        "pattern_compels_response": False,
        "advisory": True,
    },
    {
        "section_id":    "B",
        "title":         "Recurrence Does Not Rank Suffering",
        "body": (
            "Recording that a need has appeared four times does not mean it is more urgent, "
            "more deserving, or more valid than a need that has appeared once. The recurrence "
            "count is a count of observations — it is not a priority score. Dan-Go does not "
            "rank commons, participants, or care situations against one another. "
            "'Recurrence is not ranking' means that a higher observed count does not entitle "
            "a commons to more resources, more attention, or preferential treatment in any "
            "community decision. The recurrence snapshot exists to make need histories legible, "
            "not to establish a hierarchy of deserving."
        ),
        "recurrence_is_ranking":  False,
        "ranks_suffering":        False,
        "advisory": True,
    },
    {
        "section_id":    "C",
        "title":         "Learning Does Not Prescribe a Response",
        "body": (
            "The pattern memory record links a recurring need pattern to the care loops, "
            "relief cases, and routes that generated it. This cross-phase linkage makes the "
            "history of the situation legible. It does not tell any participant what to do. "
            "Dan-Go does not prescribe responses, allocate resources, or decide which care "
            "patterns should be addressed first. 'Learning is not prescription' means the "
            "pattern memory is information, not instruction. A community that reads the "
            "pattern memory may choose to coordinate a recurring response, to change how "
            "they structure their commons, or to do nothing differently. All of these choices "
            "are the community's to make. Dan-Go records; it does not prescribe."
        ),
        "learning_is_prescription":    False,
        "memory_prescribes_response":  False,
        "memory_certifies_resolution": False,
        "advisory": True,
    },
    {
        "section_id":    "D",
        "title":         "Connection to Jammy House and D.R.A. Care Histories",
        "body": (
            "Jammy House patterns: recurring food support need and unresolved tenancy situation. "
            "Both patterns are grounded in the care loop, relief case, and route records from "
            "Phases 17–19. The pattern memory does not judge whether Jammy House handled these "
            "situations well. It records that the situations recurred. "
            "D.R.A. patterns: ongoing displacement relief. The displacement relief pattern "
            "reflects four observations of a need that has not resolved between supply coordination "
            "and shelter hosting. The pattern record does not certify that the relief was "
            "insufficient. It records that the displacement is ongoing. "
            "Both commons retain full authority over how they respond to these pattern observations. "
            "Dan-Go observes. The communities decide."
        ),
        "advisory":              True,
        "pattern_ranks_commons": False,
        "authority":             "none",
    },
]


def build_report():
    patterns = _load_patterns()
    recurrences = _load_recurrences()
    memories = _load_memories()
    # Build summary table from loaded data (or defaults)
    summary_table = {
        "pattern_is_prediction":        False,
        "recurrence_is_ranking":        False,
        "learning_is_prescription":     False,
        "ranks_suffering":              False,
        "pattern_compels_response":     False,
        "memory_prescribes_response":   False,
        "memory_certifies_resolution":  False,
        "pattern_ranks_commons":        False,
        "any_participant_compelled":    False,
        "pattern_history_is_legible":   True,
        "loops_referenced":             len({lid for m in memories for lid in m.get("source_loops", [])}),
        "patterns_recorded":            len(patterns) if patterns else 4,
        "recurrences_recorded":         len(recurrences) if recurrences else 4,
        "memories_recorded":            len(memories) if memories else 4,
    }
    sections = []
    for s in SECTIONS:
        sec = dict(s)
        sec.update({k: v for k, v in PHASE_INVARIANTS.items() if k not in sec})
        sec["generated_at"] = datetime.now(timezone.utc).isoformat()
        sections.append(sec)
    return {
        "record_type":              "aid_pattern_report",
        "report_id":                "aid-pattern-report-001",
        "section_count":            len(sections),
        "sections":                 sections,
        "summary_table":            summary_table,
        "authority":                "none",
        "pattern_is_prediction":    False,
        "learning_is_prescription": False,
        "recurrence_is_ranking":    False,
        "generated_at":             datetime.now(timezone.utc).isoformat(),
        "phase":                    20,
        "phase_phrase_1":           "Pattern is not prediction.",
        "phase_phrase_2":           "Learning is not prescription.",
        "phase_phrase_3":           "Recurrence is not ranking.",
    }


def main():
    save = "--save" in sys.argv
    report = build_report()
    out = json.dumps(report, indent=2)
    print(out)
    if save:
        _SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _SAVE_PATH.write_text(out)
        print(f"\n[saved → {_SAVE_PATH}]", file=sys.stderr)
    print(f"\n  report_id: {report['report_id']}", file=sys.stderr)
    print(f"  section_count: {report['section_count']}", file=sys.stderr)
    for s in report["sections"]:
        print(f"    {s['section_id']}: {s['title']}", file=sys.stderr)
    t = report["summary_table"]
    print(f"  summary_table:", file=sys.stderr)
    print(f"    pattern_is_prediction: {t['pattern_is_prediction']}", file=sys.stderr)
    print(f"    recurrence_is_ranking: {t['recurrence_is_ranking']}", file=sys.stderr)
    print(f"    learning_is_prescription: {t['learning_is_prescription']}", file=sys.stderr)
    print(f"    ranks_suffering: {t['ranks_suffering']}", file=sys.stderr)
    print(f"    any_participant_compelled: {t['any_participant_compelled']}", file=sys.stderr)
    print(f"    pattern_history_is_legible: {t['pattern_history_is_legible']}", file=sys.stderr)


if __name__ == "__main__":
    main()
