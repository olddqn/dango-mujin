"""
commons_report.py — Phase 16: Cooperation Commons Layer

Generates a human-readable advisory report explaining:
  - why communities exist and are observable
  - why participation is voluntary
  - why community does not create authority
  - why cooperation can exist without ownership
  - why Dan-Go records without governing

"Community is not authority."
"Commons is not ownership."
"Participation is not control."

Invariants: authority=none, ownership=false, control=false,
            advisory=true, commons_only=true, judgment=false
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import date

# ── paths ────────────────────────────────────────────────────────────────────
_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT   = _SCRIPT_DIR.parents[4]
_EXAMPLES    = _SCRIPT_DIR.parent / "examples"

# ── report sections ───────────────────────────────────────────────────────────
COMMONS_REPORT_SECTIONS: list[dict[str, str]] = [
    {
        "section_id": "why-community-exists",
        "title":      "Why Community Exists and Is Observable",
        "body": (
            "Communities form when people cooperate over time around shared interests, "
            "spaces, or initiatives. Jammy House, YacypherPunks, D.R.A., and Dan-Go itself "
            "are observable facts — they have participants, activities, and histories. "
            "Dan-Go makes this cooperation legible by recording it in an advisory, "
            "append-only commons registry. Observability requires a record. A record "
            "does not create authority."
        ),
        "invariant_demonstrated": "advisory: true",
    },
    {
        "section_id": "why-participation-is-voluntary",
        "title":      "Why Participation Is Voluntary",
        "body": (
            "Participation in a commons is a voluntary act. Dan-Go records that "
            "participation occurred — when someone joined, in what role, in which commons. "
            "The record is not a contract. It does not bind the participant to obligations "
            "beyond what they chose. The membership_is_voluntary: true field in every "
            "membership record makes this explicit. Recording participation is not "
            "imposing participation."
        ),
        "invariant_demonstrated": "membership_is_voluntary: true",
    },
    {
        "section_id": "why-community-does-not-create-authority",
        "title":      "Why Community Does Not Create Authority",
        "body": (
            "The existence of a community — even a well-organised, active, historically "
            "documented one — does not create authority over its members or over external "
            "systems. Dan-Go records that Jammy House exists, that D.R.A. exists, that "
            "Dan-Go itself exists as a cooperative project. None of these records give "
            "Dan-Go the authority to govern those communities, override their decisions, "
            "or compel any outcome on their behalf. authority: none applies to every "
            "commons record without exception."
        ),
        "invariant_demonstrated": "authority: none",
    },
    {
        "section_id": "why-cooperation-exists-without-ownership",
        "title":      "Why Cooperation Can Exist Without Ownership",
        "body": (
            "A commons is defined by the absence of individual ownership. Participants "
            "cooperate within shared structures without claiming those structures as "
            "property. Dan-Go respects this by maintaining ownership: false across every "
            "commons record. Dan-Go does not own the communities it records. "
            "Participants do not own the commons by virtue of their participation record. "
            "The commons is shared. The record is advisory. Ownership is not implied "
            "at any layer."
        ),
        "invariant_demonstrated": "ownership: false",
    },
    {
        "section_id": "why-dan-go-records-without-governing",
        "title":      "Why Dan-Go Records Without Governing",
        "body": (
            "Dan-Go is an advisory, append-only protocol. Its role is to make cooperation "
            "legible — to produce a neutral, contestable, historical record of what "
            "occurred. It does not decide who belongs in a community. It does not "
            "adjudicate disputes between communities. It does not tell communities what "
            "their next action should be. Jammy House, YacypherPunks, D.R.A., and future "
            "commons govern themselves. Dan-Go records what they do, not what they must do. "
            "control: false and hard_enforcement: false are permanent invariants."
        ),
        "invariant_demonstrated": "control: false, hard_enforcement: false",
    },
]

# ── summary table ─────────────────────────────────────────────────────────────
COMMONS_REPORT_SUMMARY: dict[str, object] = {
    "commons_observed":               True,
    "participation_recorded":         True,
    "authority_implied":              False,
    "ownership_implied":              False,
    "control_implied":                False,
    "dan_go_governs_communities":     False,
    "dan_go_owns_communities":        False,
    "participation_is_voluntary":     True,
    "records_are_advisory":           True,
    "records_are_contestable":        True,
    "records_are_append_only":        True,
    "commons_remains_self_governing": True,
}


def load_snapshot() -> dict[str, object] | None:
    """Try to load snapshot for report context."""
    snap_path = _EXAMPLES / "commons-snapshot.json"
    if snap_path.exists():
        return json.loads(snap_path.read_text())   # type: ignore[return-value]
    return None


def build_report() -> dict[str, object]:
    """Build the full commons report."""
    snap = load_snapshot()

    context: dict[str, object]
    if snap:
        context = {
            "source_snapshot_id":        snap.get("snapshot_id", "commons-snap-001"),
            "commons_count":             snap.get("commons_count", 4),
            "total_participants":        snap.get("total_participants", 0),
            "total_contributions":       snap.get("total_contributions", 0),
            "total_recognition_history": snap.get("total_recognition_history", 0),
        }
    else:
        context = {
            "source_snapshot_id":        "commons-snap-001",
            "commons_count":             4,
            "total_participants":        9,
            "total_contributions":       126,
            "total_recognition_history": 98,
        }

    report: dict[str, object] = {
        "record_type":    "commons_report",
        "report_id":      "commons-report-001",
        "report_date":    str(date.today()),
        "report_subject": "Cooperation Commons Layer — Phase 16",
        "context":        context,
        "section_count":  len(COMMONS_REPORT_SECTIONS),
        "sections":       COMMONS_REPORT_SECTIONS,
        "summary_table":  COMMONS_REPORT_SUMMARY,
        # invariants
        "authority":          "none",
        "ownership":          False,
        "control":            False,
        "judgment":           False,
        "advisory":           True,
        "commons_only":       True,
        "append_only":        True,
        "contestable":        True,
        "reopenable":         True,
        "moves_money":        False,
        "credit_issued":      False,
        "execution_allowed":  False,
        "hard_enforcement":   False,
        "protocol_phrases": [
            "Community is not authority.",
            "Commons is not ownership.",
            "Participation is not control.",
            "Dan-Go records cooperation history; it does not govern communities.",
            "Dan-Go observes commons; it does not own them.",
        ],
    }
    return report


def print_report(report: dict[str, object]) -> None:
    print("=== commons_report.py ===")
    print(f"  report_id:     {report['report_id']}")
    print(f"  report_date:   {report['report_date']}")
    print(f"  section_count: {report['section_count']}")
    print("  sections:")
    for s in report["sections"]:                              # type: ignore[union-attr]
        print(f"    [{s['section_id']}] {s['title']}")
        print(f"      invariant_demonstrated: {s['invariant_demonstrated']}")
    print("  summary_table:")
    for k, v in report["summary_table"].items():              # type: ignore[union-attr]
        print(f"    {k}: {str(v).lower()}")
    print(f"  authority={report['authority']}, ownership={report['ownership']}, "
          f"control={report['control']}, judgment={report['judgment']}")
    print("  Community is not authority.")
    print("  Commons is not ownership.")
    print("  Participation is not control.")


def save_report(report: dict[str, object]) -> Path:
    _EXAMPLES.mkdir(parents=True, exist_ok=True)
    out = _EXAMPLES / "commons-report.json"
    out.write_text(json.dumps(report, indent=2))
    print(f"  saved → {out.relative_to(_REPO_ROOT)}")
    return out


if __name__ == "__main__":
    report = build_report()
    print_report(report)
    if "--save" in sys.argv:
        save_report(report)
