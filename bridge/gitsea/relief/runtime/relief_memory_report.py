"""
relief_memory_report.py — Phase 18: Relief Case Memory Layer

Generates a human-readable advisory report explaining:
  - a relief case was recorded
  - an outcome was observed
  - no proof of rescue is claimed
  - no suffering is ranked
  - no one is controlled
  - the case can be reopened

"Relief is not proof."
"Outcome is not judgment."
"Care memory is not control."

Invariants: authority=none, moves_money=false, execution_allowed=false,
            advisory=true, relief_memory_only=true, judgment=false
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
RELIEF_REPORT_SECTIONS: list[dict[str, str]] = [
    {
        "section_id": "relief-case-was-recorded",
        "title":      "A Relief Case Was Recorded",
        "body": (
            "When a mutual aid route is suggested and acted upon, Dan-Go records a "
            "relief case as a follow-up observation. The relief case links the Phase 17 "
            "route to what happened next. This creates a continuous chain: request → "
            "offer → route → case → outcome → care memory. The chain is advisory at "
            "every link. Recording a case does not certify the assistance, create a "
            "liability, or produce an obligation on any party."
        ),
        "invariant_demonstrated": "advisory: true, certifies_rescue: false",
    },
    {
        "section_id": "outcome-was-observed",
        "title":      "An Outcome Was Observed",
        "body": (
            "Outcomes are observable facts: a meal was received, shelter was accepted, "
            "supplies reached a household, a negotiation was initiated. Dan-Go records "
            "these observations. It does not certify them as proof of anything beyond "
            "what was directly observed. An observed outcome of 'full' means the "
            "assistance appeared to address the request — not that the underlying need "
            "is permanently resolved, not that the recipient is no longer vulnerable, "
            "not that the situation is closed."
        ),
        "invariant_demonstrated": "outcome_is_judgment: false, certifies_success: false",
    },
    {
        "section_id": "no-proof-of-rescue-claimed",
        "title":      "No Proof of Rescue Is Claimed",
        "body": (
            "The relief_is_proof: false invariant is permanent. Dan-Go's record of a "
            "relief case and its outcome is not a certificate of rescue. It is not "
            "evidence to be used in claims about who was saved, who saved them, or "
            "whether a sufficient response was provided. The record exists for "
            "community legibility — so that mutual aid history is observable — not "
            "for external certification. Any party who attempts to use a Dan-Go relief "
            "case record as proof of rescue or sufficiency is misusing the record."
        ),
        "invariant_demonstrated": "relief_is_proof: false",
    },
    {
        "section_id": "no-suffering-is-ranked",
        "title":      "No Suffering Is Ranked",
        "body": (
            "The relief case registry records urgency (from the Phase 17 request) "
            "without converting urgency into a ranking of whose suffering matters more. "
            "A refugee_relief case marked 'immediate' is not positioned above a "
            "food_support case marked 'medium' in any authoritative queue. Dan-Go "
            "makes urgency visible to participants; it does not rank suffering or "
            "adjudicate who deserves priority response. ranks_suffering: false is "
            "an invariant on every case record."
        ),
        "invariant_demonstrated": "ranks_suffering: false, outcome_is_judgment: false",
    },
    {
        "section_id": "no-one-is-controlled",
        "title":      "No One Is Controlled",
        "body": (
            "Care memory does not control any participant. The person who received "
            "food support is not in a relationship of obligation to the commons that "
            "provided it. The person who offered shelter is not accountable to Dan-Go "
            "for whether they offer again. The commons is not governed by its care "
            "memory records. care_memory_controls: false applies to every memory "
            "entry. The record observes what happened; it does not prescribe what "
            "must happen next."
        ),
        "invariant_demonstrated": "care_memory_controls: false, authority: none",
    },
    {
        "section_id": "case-can-be-reopened",
        "title":      "The Case Can Be Reopened",
        "body": (
            "Every relief case carries reopenable: true. A case marked 'completed' "
            "can be reopened if circumstances change — if the assistance did not hold, "
            "if the need recurred, if new information becomes available about what "
            "actually occurred. The append-only constraint means the original record "
            "is never deleted, but new entries can be appended that update the "
            "observable picture. Care memory grows with the situation. It does not "
            "lock the situation into a single past observation."
        ),
        "invariant_demonstrated": "reopenable: true, append_only: true",
    },
]

# ── summary table ─────────────────────────────────────────────────────────────
RELIEF_REPORT_SUMMARY: dict[str, object] = {
    "relief_case_recorded":         True,
    "outcome_observed":             True,
    "proof_of_rescue_claimed":      False,
    "suffering_ranked":             False,
    "any_party_controlled":         False,
    "case_creates_obligation":      False,
    "memory_certifies_outcome":     False,
    "record_is_advisory":           True,
    "record_is_append_only":        True,
    "record_is_contestable":        True,
    "case_is_reopenable":           True,
    "care_history_is_legible":      True,
}


def load_memory_log() -> dict[str, object] | None:
    mem_path = _EXAMPLES / "care-memory.json"
    if mem_path.exists():
        return json.loads(mem_path.read_text())  # type: ignore[return-value]
    return None


def load_case_registry() -> dict[str, object] | None:
    case_path = _EXAMPLES / "relief-case-registry.json"
    if case_path.exists():
        return json.loads(case_path.read_text())  # type: ignore[return-value]
    return None


def load_outcome_log() -> dict[str, object] | None:
    out_path = _EXAMPLES / "relief-outcome-snapshot.json"
    if out_path.exists():
        return json.loads(out_path.read_text())  # type: ignore[return-value]
    return None


def build_report() -> dict[str, object]:
    """Build the full relief memory report."""
    memory   = load_memory_log()
    cases    = load_case_registry()
    outcomes = load_outcome_log()

    context: dict[str, object] = {
        "case_count":            cases.get("case_count", 5)         if cases    else 5,
        "snapshot_count":        outcomes.get("snapshot_count", 5)  if outcomes else 5,
        "memory_count":          memory.get("memory_count", 5)      if memory   else 5,
        "complete_count":        memory.get("complete_count", 4)    if memory   else 4,
        "source_registry_id":    cases.get("registry_id",   "relief-case-registry-001")    if cases    else "relief-case-registry-001",
        "source_outcome_log_id": outcomes.get("log_id",     "outcome-snapshot-log-001")    if outcomes else "outcome-snapshot-log-001",
        "source_memory_log_id":  memory.get("log_id",       "care-memory-log-001")         if memory   else "care-memory-log-001",
    }

    report: dict[str, object] = {
        "record_type":    "relief_memory_report",
        "report_id":      "relief-memory-report-001",
        "report_date":    str(date.today()),
        "report_subject": "Relief Case Memory Layer — Phase 18",
        "context":        context,
        "section_count":  len(RELIEF_REPORT_SECTIONS),
        "sections":       RELIEF_REPORT_SECTIONS,
        "summary_table":  RELIEF_REPORT_SUMMARY,
        # invariants
        "authority":            "none",
        "execution_allowed":    False,
        "moves_money":          False,
        "credit_issued":        False,
        "hard_enforcement":     False,
        "advisory":             True,
        "relief_memory_only":   True,
        "append_only":          True,
        "contestable":          True,
        "reopenable":           True,
        "relief_is_proof":      False,
        "outcome_is_judgment":  False,
        "care_memory_controls": False,
        "judgment":             False,
        "protocol_phrases": [
            "Relief is not proof.",
            "Outcome is not judgment.",
            "Care memory is not control.",
            "Dan-Go records relief case memory; it does not certify rescue or rank suffering.",
            "Dan-Go observes care history; it does not control any party.",
        ],
    }
    return report


def print_report(report: dict[str, object]) -> None:
    print("=== relief_memory_report.py ===")
    print(f"  report_id:     {report['report_id']}")
    print(f"  report_date:   {report['report_date']}")
    print(f"  section_count: {report['section_count']}")
    ctx = report["context"]
    print(f"  context: cases={ctx['case_count']}, snapshots={ctx['snapshot_count']}, "  # type: ignore[index]
          f"memories={ctx['memory_count']}, complete={ctx['complete_count']}")  # type: ignore[index]
    print("  sections:")
    for s in report["sections"]:  # type: ignore[union-attr]
        print(f"    [{s['section_id']}] {s['title']}")
        print(f"      invariant_demonstrated: {s['invariant_demonstrated']}")
    print("  summary_table:")
    for k, v in report["summary_table"].items():  # type: ignore[union-attr]
        print(f"    {k}: {str(v).lower()}")
    print(f"  authority={report['authority']}, relief_is_proof={report['relief_is_proof']}, "
          f"outcome_is_judgment={report['outcome_is_judgment']}, "
          f"care_memory_controls={report['care_memory_controls']}")
    print("  Relief is not proof.")
    print("  Outcome is not judgment.")
    print("  Care memory is not control.")


def save_report(report: dict[str, object]) -> Path:
    _EXAMPLES.mkdir(parents=True, exist_ok=True)
    out = _EXAMPLES / "relief-memory-report.json"
    out.write_text(json.dumps(report, indent=2))
    print(f"  saved → {out.relative_to(_REPO_ROOT)}")
    return out


if __name__ == "__main__":
    report = build_report()
    print_report(report)
    if "--save" in sys.argv:
        save_report(report)
