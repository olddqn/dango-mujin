"""
capacity_report.py — Commons Capacity Memory Layer (Phase 50)
Dan-Go / GITSEA Bridge · authority: none · stdlib only

"Capacity is not commitment."
"Ability is not obligation."
"Availability is not allocation."

Generates a human-readable report of observed commons capacity. The
report explains, in plain language:
  - what capacity has been observed
  - at what availability it has been observed
  - that no commitment is implied
  - that no obligation is created
  - that no resource allocation has been performed

The report is advisory text for human reading. It performs no action.

Invariants (all permanent):
  capacity_is_commitment: false
  ability_creates_obligation: false
  availability_allocates_resources: false
  report_compels_action: false
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

_CAPACITY_EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
_SAVE_PATH = _CAPACITY_EXAMPLES / "capacity-report.json"

PHASE_INVARIANTS = {
    "authority":                        "none",
    "execution_allowed":                False,
    "moves_money":                      False,
    "credit_issued":                    False,
    "hard_enforcement":                 False,
    "advisory":                         True,
    "capacity_only":                    True,
    "append_only":                      True,
    "contestable":                      True,
    "reopenable":                       True,
    "capacity_is_commitment":           False,
    "ability_creates_obligation":       False,
    "availability_allocates_resources": False,
    "report_compels_action":            False,
}


def _load_registry():
    path = _CAPACITY_EXAMPLES / "capacity-registry.json"
    if path.exists():
        try:
            data = json.loads(path.read_text())
            return data if isinstance(data, dict) else {"capacities": data}
        except Exception:
            pass
    try:
        from capacity_registry import build_registry  # type: ignore
        return build_registry()
    except Exception:
        return {"capacities": []}


def _load_snapshot():
    path = _CAPACITY_EXAMPLES / "capacity-snapshot.json"
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    try:
        from capacity_snapshot import build_snapshot  # type: ignore
        return build_snapshot()
    except Exception:
        return {}


def _build_lines(registry, snapshot):
    lines = []
    lines.append("Commons Capacity Report (Phase 50)")
    lines.append("=" * 52)
    lines.append("")
    lines.append("Capacity is not commitment.")
    lines.append("Ability is not obligation.")
    lines.append("Availability is not allocation.")
    lines.append("")
    cap = registry.get("capacities", [])
    lines.append(f"Observed capacities: {len(cap)}")
    lines.append(f"Commons represented: {', '.join(snapshot.get('commons_represented', [])) or 'none'}")
    lines.append("")
    lines.append("Observed capacity records:")
    for c in cap:
        lines.append(
            f"  - [{c.get('capacity_id','?')}] {c.get('commons_id','?')} "
            f"can offer '{c.get('capacity_type','?')}' "
            f"({c.get('participants','?')} participants, "
            f"availability: {c.get('availability','unknown')})"
        )
        note = c.get("capacity_note")
        if note:
            lines.append(f"      note: {note}")
    lines.append("")
    lines.append("What this report does NOT mean:")
    lines.append("  - No commitment is implied. A commons may have capacity and choose not to act.")
    lines.append("  - No obligation is created. Being able to help does not create a duty to help.")
    lines.append("  - No resource allocation has been performed. Availability is not allocation.")
    lines.append("")
    lines.append("This report is advisory. Human review is required before any real-world action.")
    return lines


def build_report():
    registry = _load_registry()
    snapshot = _load_snapshot()
    lines = _build_lines(registry, snapshot)
    report = {
        "record_type":                      "commons_capacity_report",
        "report_id":                        "capacity-report-001",
        "capacity_count":                   len(registry.get("capacities", [])),
        "commons_represented":              snapshot.get("commons_represented", []),
        "report_text":                      "\n".join(lines),
        "report_lines":                     lines,
        "authority":                        "none",
        "capacity_is_commitment":           False,
        "ability_creates_obligation":       False,
        "availability_allocates_resources": False,
        "report_compels_action":            False,
        "generated_at":                     datetime.now(timezone.utc).isoformat(),
        "phase":                            50,
        "phase_phrase_1":                   "Capacity is not commitment.",
        "phase_phrase_2":                   "Ability is not obligation.",
        "phase_phrase_3":                   "Availability is not allocation.",
    }
    report.update(PHASE_INVARIANTS)
    return report


def main():
    save = "--save" in sys.argv
    report = build_report()
    # Human-readable text to stdout
    print(report["report_text"])
    if save:
        _SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _SAVE_PATH.write_text(json.dumps(report, indent=2))
        print(f"\n[saved → {_SAVE_PATH}]", file=sys.stderr)
    print(f"\n  report_id: {report['report_id']}", file=sys.stderr)
    print(f"  capacity_count: {report['capacity_count']}", file=sys.stderr)
    print(
        f"  capacity_is_commitment={report['capacity_is_commitment']} "
        f"ability_creates_obligation={report['ability_creates_obligation']} "
        f"availability_allocates_resources={report['availability_allocates_resources']}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
