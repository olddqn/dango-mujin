"""
care_loop_report.py — Phase 19: Care Loop Reopen Layer

Generates a human-readable advisory report explaining:
  - care case may be reopened
  - reopen does not mean failure
  - follow-up does not imply blame
  - no one is compelled to help
  - care loop remains voluntary and contestable

"Reopen is not failure."
"Follow-up is not blame."
"Care loop is not obligation."

Invariants: authority=none, moves_money=false, execution_allowed=false,
            advisory=true, care_loop_only=true, judgment=false
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import date

# ── paths ─────────────────────────────────────────────────────────────────────
_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT   = _SCRIPT_DIR.parents[4]
_EXAMPLES    = _SCRIPT_DIR.parent / "examples"

# ── report sections ───────────────────────────────────────────────────────────
CARE_LOOP_REPORT_SECTIONS: list[dict[str, str]] = [
    {
        "section_id": "care-case-may-be-reopened",
        "title":      "A Care Case May Be Reopened",
        "body": (
            "Care situations are not sealed when a case is first recorded. A relief "
            "case with outcome_status 'full' still carries reopenable: true. When "
            "a follow-up need is observed — because the need recurred, the outcome "
            "was partial, or the situation changed — Dan-Go records a reopen request. "
            "The reopen is an advisory observation. It is not a verdict on the original "
            "response. It is the recognition that care is a loop, not a single moment."
        ),
        "invariant_demonstrated": "reopenable: true, append_only: true",
    },
    {
        "section_id": "reopen-does-not-mean-failure",
        "title":      "Reopen Does Not Mean Failure",
        "body": (
            "The reopen_is_failure: false invariant is unconditional. A care case being "
            "reopened does not mean the original assistance failed. Food was provided — "
            "that was real. Shelter was offered — that was real. The fact that the need "
            "recurred, or that more was needed, does not erase what was done. Dan-Go "
            "records both the original outcome and the new observation without using the "
            "new observation to retroactively judge the old one. Reopen is continuation, "
            "not correction."
        ),
        "invariant_demonstrated": "reopen_is_failure: false, reopen_judges_prior_response: false",
    },
    {
        "section_id": "followup-does-not-imply-blame",
        "title":      "Follow-Up Does Not Imply Blame",
        "body": (
            "When a follow-up need is recorded, it is not an accusation against any "
            "participant. The helper who provided the original assistance is not at "
            "fault for the need recurring. The requester is not at fault for continuing "
            "to need help. followup_judges_prior_helper: false and followup_is_blame: "
            "false are invariants on every follow-up need record. The follow-up is an "
            "observation about a situation, not a judgment about the people in it."
        ),
        "invariant_demonstrated": "followup_is_blame: false, followup_judges_prior_helper: false",
    },
    {
        "section_id": "no-one-is-compelled-to-help",
        "title":      "No One Is Compelled to Help",
        "body": (
            "A care loop reopen does not create an obligation for any helper to respond "
            "again. The original helper may choose to help again — voluntarily. A new "
            "helper may choose to engage — voluntarily. Dan-Go records the reopen and "
            "the follow-up need so that the community can see the situation. It does "
            "not command any participant. reopen_compels_new_aid: false and "
            "care_loop_creates_obligation: false are permanent invariants. The loop "
            "is observable. The response is voluntary."
        ),
        "invariant_demonstrated": "reopen_compels_new_aid: false, care_loop_creates_obligation: false",
    },
    {
        "section_id": "care-loop-remains-voluntary",
        "title":      "The Care Loop Remains Voluntary and Contestable",
        "body": (
            "Every entry in the care loop — the reopen request, the follow-up need, "
            "the loop itself — carries contestable: true. A participant who disagrees "
            "with how a follow-up need was characterised can contest the record. A "
            "participant who believes a reopen was wrongly requested can contest it. "
            "The append-only property means the original record is preserved, but "
            "contestation adds new information to the loop. Care memory grows with "
            "the situation. Authority remains none throughout."
        ),
        "invariant_demonstrated": "contestable: true, authority: none",
    },
    {
        "section_id": "connection-to-jammy-house-and-refugee-relief",
        "title":      "Connection to Jammy House and Refugee Relief",
        "body": (
            "Jammy House care loops cover recurring food support needs and unresolved "
            "housing situations. These are common patterns in cooperative housing: "
            "one provision is not a permanent solution. D.R.A. care loops cover "
            "ongoing displacement — where the original supply coordination or shelter "
            "hosting was a temporary response to an ongoing situation. The care loop "
            "layer makes these recurring, continuing care patterns legible without "
            "treating them as failures or creating blame for participants who did "
            "what they could at the time. Dan-Go observes the loop; the community "
            "decides how to respond."
        ),
        "invariant_demonstrated": "advisory: true, care_loop_only: true",
    },
]

# ── summary table ─────────────────────────────────────────────────────────────
CARE_LOOP_SUMMARY: dict[str, object] = {
    "care_case_reopened":               True,
    "reopen_is_failure":                False,
    "followup_implies_blame":           False,
    "any_participant_compelled":        False,
    "care_loop_creates_obligation":     False,
    "original_assistance_erased":       False,
    "loop_judges_participants":         False,
    "loop_certifies_resolution":        False,
    "records_are_voluntary":            True,
    "records_are_contestable":          True,
    "records_are_append_only":          True,
    "loop_is_reopenable":               True,
    "care_history_is_legible":          True,
}


def load_loop_log() -> dict[str, object] | None:
    path = _EXAMPLES / "care-loop.json"
    return json.loads(path.read_text()) if path.exists() else None  # type: ignore[return-value]


def load_reopen_registry() -> dict[str, object] | None:
    path = _EXAMPLES / "care-reopen-registry.json"
    return json.loads(path.read_text()) if path.exists() else None  # type: ignore[return-value]


def load_followup_snapshot() -> dict[str, object] | None:
    path = _EXAMPLES / "followup-need-snapshot.json"
    return json.loads(path.read_text()) if path.exists() else None  # type: ignore[return-value]


def build_report() -> dict[str, object]:
    """Build the full care loop report."""
    loops     = load_loop_log()
    reopens   = load_reopen_registry()
    followups = load_followup_snapshot()

    context: dict[str, object] = {
        "reopen_count":   reopens.get("reopen_count", 4)    if reopens   else 4,
        "followup_count": followups.get("followup_count", 4) if followups else 4,
        "loop_count":     loops.get("loop_count", 4)        if loops     else 4,
        "complete_count": loops.get("complete_count", 4)    if loops     else 4,
        "source_reopen_registry_id":   reopens.get("registry_id",  "care-reopen-registry-001") if reopens   else "care-reopen-registry-001",
        "source_followup_snapshot_id": followups.get("snapshot_id","followup-snapshot-001")     if followups else "followup-snapshot-001",
        "source_loop_log_id":          loops.get("log_id",         "care-loop-log-001")         if loops     else "care-loop-log-001",
    }

    report: dict[str, object] = {
        "record_type":    "care_loop_report",
        "report_id":      "care-loop-report-001",
        "report_date":    str(date.today()),
        "report_subject": "Care Loop Reopen Layer — Phase 19",
        "context":        context,
        "section_count":  len(CARE_LOOP_REPORT_SECTIONS),
        "sections":       CARE_LOOP_REPORT_SECTIONS,
        "summary_table":  CARE_LOOP_SUMMARY,
        # invariants
        "authority":                  "none",
        "execution_allowed":          False,
        "moves_money":                False,
        "credit_issued":              False,
        "hard_enforcement":           False,
        "advisory":                   True,
        "care_loop_only":             True,
        "append_only":                True,
        "contestable":                True,
        "reopenable":                 True,
        "reopen_is_failure":          False,
        "followup_is_blame":          False,
        "care_loop_creates_obligation": False,
        "judgment":                   False,
        "protocol_phrases": [
            "Reopen is not failure.",
            "Follow-up is not blame.",
            "Care loop is not obligation.",
            "Dan-Go records care loops; it does not compel resolution or judge participants.",
            "Dan-Go observes recurring care needs; it does not blame or rank them.",
        ],
    }
    return report


def print_report(report: dict[str, object]) -> None:
    print("=== care_loop_report.py ===")
    print(f"  report_id:     {report['report_id']}")
    print(f"  report_date:   {report['report_date']}")
    print(f"  section_count: {report['section_count']}")
    ctx = report["context"]
    print(f"  context: reopens={ctx['reopen_count']}, followups={ctx['followup_count']}, "  # type: ignore[index]
          f"loops={ctx['loop_count']}, complete={ctx['complete_count']}")                    # type: ignore[index]
    print("  sections:")
    for s in report["sections"]:  # type: ignore[union-attr]
        print(f"    [{s['section_id']}] {s['title']}")
        print(f"      invariant_demonstrated: {s['invariant_demonstrated']}")
    print("  summary_table:")
    for k, v in report["summary_table"].items():  # type: ignore[union-attr]
        print(f"    {k}: {str(v).lower()}")
    print(f"  authority={report['authority']}, reopen_is_failure={report['reopen_is_failure']}, "
          f"followup_is_blame={report['followup_is_blame']}, "
          f"care_loop_creates_obligation={report['care_loop_creates_obligation']}")
    print("  Reopen is not failure.")
    print("  Follow-up is not blame.")
    print("  Care loop is not obligation.")


def save_report(report: dict[str, object]) -> Path:
    _EXAMPLES.mkdir(parents=True, exist_ok=True)
    out = _EXAMPLES / "care-loop-report.json"
    out.write_text(json.dumps(report, indent=2))
    print(f"  saved → {out.relative_to(_REPO_ROOT)}")
    return out


if __name__ == "__main__":
    report = build_report()
    print_report(report)
    if "--save" in sys.argv:
        save_report(report)
