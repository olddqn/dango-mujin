"""
need_forecast_report.py — Commons Need Forecast Memory Layer (Phase 21)
Dan-Go / GITSEA Bridge · authority: none · stdlib only

"Forecast is not certainty."
"Preparedness is not command."
"Hint is not allocation."

Generates a human-readable JSON report explaining:

  Section A: Forecast-like memory exists — and why that is not a prediction
  Section B: Pattern does not prove future need — confidence is explicit and limited
  Section C: Preparedness hint does not command action — voluntary use only
  Section D: No allocation is enforced — commons retain full resource autonomy
  Section E: Connection to Jammy House and refugee relief

The report is advisory only. It does not compel any participant.
It does not certify any outcome. It does not operate any external system.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

_REPO_ROOT = Path(__file__).resolve().parents[4]
_FORECAST_EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
_SAVE_PATH = _FORECAST_EXAMPLES / "need-forecast-report.json"

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
    "memory_certifies_resolution":  False,
}

SECTIONS = [
    {
        "section_id":  "A",
        "title":       "Forecast-Like Memory Exists — and What It Is Not",
        "body": (
            "Dan-Go records preparedness memory derived from recurring aid patterns. "
            "These records use the word 'forecast' to describe memories that point "
            "forward from observed patterns. They are not predictions. They are not "
            "certainties. They are observations about the past organized in a form "
            "that may be useful for voluntary community planning. "
            "'Forecast is not certainty' means the forecast memory record cannot be "
            "used to assert that a need will arise. It can only be used to note that "
            "a need has arisen before, and that the community may wish to hold that "
            "information for its own use. The confidence label on every forecast "
            "record — 'observed_pattern_only', 'single_observation', 'two_observations', "
            "'four_plus_observations' — communicates explicitly how weakly grounded "
            "the forecast memory is."
        ),
        "forecast_is_certainty":  False,
        "advisory":               True,
    },
    {
        "section_id":  "B",
        "title":       "Pattern Does Not Prove Future Need",
        "body": (
            "A recurring pattern of food support need in Jammy House does not prove "
            "that food support will be needed next month. A pattern of displacement "
            "relief in D.R.A. does not prove that displacement will continue. "
            "Patterns are observations about sequences of past events. They carry "
            "no causal or probabilistic weight in Dan-Go. The observed count on "
            "each forecast record is a count of past instances — not a forecast "
            "frequency, not a confidence interval, not a probability estimate. "
            "Dan-Go does not perform any statistical analysis. It records that "
            "something happened N times. The community interprets what that means."
        ),
        "forecast_is_certainty":  False,
        "forecast_compels_preparation": False,
        "advisory":               True,
    },
    {
        "section_id":  "C",
        "title":       "Preparedness Hint Does Not Command Action",
        "body": (
            "Each preparedness hint record identifies a type of capacity awareness "
            "that may be useful given the observed pattern. The hint describes "
            "what the community might consider — awareness of meal preparation "
            "capacity, awareness of shelter hosting availability, awareness of "
            "housing advocacy continuation options. The hint does not direct the "
            "community to build that capacity. It does not set a target. It does "
            "not create a timeline. It does not assign a responsibility. "
            "'Preparedness is not command' means the hint is information for "
            "voluntary consideration. Participants may read the hint and do "
            "nothing. Participants may read the hint and decide to coordinate "
            "a voluntary response. Both choices are equally valid. Dan-Go "
            "records the hint and observes. The community decides."
        ),
        "preparedness_is_command": False,
        "hint_compels_action":     False,
        "advisory":                True,
    },
    {
        "section_id":  "D",
        "title":       "No Allocation Is Enforced — Commons Retain Full Resource Autonomy",
        "body": (
            "The forecast memory layer does not allocate resources. It does not "
            "tell Jammy House how many meals to prepare. It does not tell D.R.A. "
            "how many shelter beds to maintain. It does not establish a commons "
            "budget or a reserve requirement. 'Hint is not allocation' means the "
            "preparedness hint is not a resource directive. No participant is "
            "required to acquire, hold, or commit any resource as a result of "
            "reading a forecast record or a preparedness hint. The commons retains "
            "full authority over its own resource decisions. Dan-Go observes. "
            "The commons decides."
        ),
        "hint_is_allocation":           False,
        "hint_assigns_resources":       False,
        "forecast_allocates_resources": False,
        "advisory":                     True,
    },
    {
        "section_id":  "E",
        "title":       "Connection to Jammy House and Refugee Relief",
        "body": (
            "Jammy House forecast memories: recurring food support and unresolved "
            "tenancy situation. The food support forecast memory reflects three "
            "observed instances of food need in a cooperative housing context where "
            "one provision is not a permanent solution. The tenancy forecast memory "
            "reflects two instances of an unresolved tenancy situation where housing "
            "advocacy has been initiated but not completed. Neither forecast memory "
            "tells Jammy House what to do. It tells Jammy House what has been "
            "observed. Jammy House may choose to use this information to coordinate "
            "recurring meal support or to sustain advocacy relationships. These "
            "are Jammy House's choices. "
            "D.R.A. forecast memories: ongoing displacement relief. Four instances "
            "of displacement-related need have been observed. The forecast memory "
            "reflects that the displacement is ongoing, that supply and shelter "
            "responses have been temporary, and that further coordination may be "
            "useful. D.R.A. decides what coordination, if any, to pursue. "
            "Dan-Go observes both commons. It does not govern either."
        ),
        "advisory":                 True,
        "hint_is_allocation":       False,
        "forecast_is_certainty":    False,
        "preparedness_is_command":  False,
    },
]


def _load_json_obj(path):
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}


def build_report():
    reg = _load_json_obj(_FORECAST_EXAMPLES / "need-forecast-registry.json")
    hints = _load_json_obj(_FORECAST_EXAMPLES / "preparedness-hint-snapshot.json")
    mem = _load_json_obj(_FORECAST_EXAMPLES / "forecast-memory.json")
    summary_table = {
        "forecast_is_certainty":        False,
        "preparedness_is_command":      False,
        "hint_is_allocation":           False,
        "forecast_allocates_resources": False,
        "forecast_compels_preparation": False,
        "hint_assigns_resources":       False,
        "hint_compels_action":          False,
        "memory_certifies_resolution":  False,
        "memory_compels_preparation":   False,
        "any_participant_compelled":    False,
        "commons_retain_autonomy":      True,
        "forecast_history_is_legible":  True,
        "forecasts_recorded":           reg.get("forecast_count", 4),
        "hints_recorded":               hints.get("hint_count", 4),
        "memories_recorded":            mem.get("memory_count", 4),
    }
    sections = []
    for s in SECTIONS:
        sec = dict(s)
        sec.update({k: v for k, v in PHASE_INVARIANTS.items() if k not in sec})
        sec["generated_at"] = datetime.now(timezone.utc).isoformat()
        sections.append(sec)
    return {
        "record_type":              "need_forecast_report",
        "report_id":                "need-forecast-report-001",
        "section_count":            len(sections),
        "sections":                 sections,
        "summary_table":            summary_table,
        "authority":                "none",
        "forecast_is_certainty":    False,
        "preparedness_is_command":  False,
        "hint_is_allocation":       False,
        "generated_at":             datetime.now(timezone.utc).isoformat(),
        "phase":                    21,
        "phase_phrase_1":           "Forecast is not certainty.",
        "phase_phrase_2":           "Preparedness is not command.",
        "phase_phrase_3":           "Hint is not allocation.",
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
    print(f"    forecast_is_certainty: {t['forecast_is_certainty']}", file=sys.stderr)
    print(f"    preparedness_is_command: {t['preparedness_is_command']}", file=sys.stderr)
    print(f"    hint_is_allocation: {t['hint_is_allocation']}", file=sys.stderr)
    print(f"    any_participant_compelled: {t['any_participant_compelled']}", file=sys.stderr)
    print(f"    commons_retain_autonomy: {t['commons_retain_autonomy']}", file=sys.stderr)
    print(f"    forecast_history_is_legible: {t['forecast_history_is_legible']}", file=sys.stderr)


if __name__ == "__main__":
    main()
