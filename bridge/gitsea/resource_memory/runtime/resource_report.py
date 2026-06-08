"""
resource_report.py — Resource Memory Layer (Phase 51)
Dan-Go / GITSEA Bridge · authority: none · stdlib only

"Resource is not allocation."
"Possession is not obligation."
"Availability is not transfer."

Generates a human-readable report of observed commons resources. The
report explains, in plain language:
  - what resources have been observed
  - at what observability provenance they were observed
  - that no allocation has been performed
  - that no obligation is created
  - that no ownership has been transferred
  - that no command has been issued

The report is advisory text for human reading. It performs no action.

Invariants (all permanent):
  resource_is_allocation: false
  possession_creates_obligation: false
  availability_transfers_ownership: false
  report_compels_action: false
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

_RESOURCE_EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
_SAVE_PATH = _RESOURCE_EXAMPLES / "resource-report.json"

PHASE_INVARIANTS = {
    "authority":                        "none",
    "execution_allowed":                False,
    "moves_money":                      False,
    "credit_issued":                    False,
    "hard_enforcement":                 False,
    "advisory":                         True,
    "resource_memory_only":             True,
    "append_only":                      True,
    "contestable":                      True,
    "reopenable":                       True,
    "resource_is_allocation":           False,
    "possession_creates_obligation":    False,
    "availability_transfers_ownership": False,
    "report_compels_action":            False,
}


def _load_registry():
    path = _RESOURCE_EXAMPLES / "resource-registry.json"
    if path.exists():
        try:
            data = json.loads(path.read_text())
            return data if isinstance(data, dict) else {"resources": data}
        except Exception:
            pass
    try:
        from resource_registry import build_registry  # type: ignore
        return build_registry()
    except Exception:
        return {"resources": []}


def _load_snapshot():
    path = _RESOURCE_EXAMPLES / "resource-snapshot.json"
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    try:
        from resource_snapshot import build_snapshot  # type: ignore
        return build_snapshot()
    except Exception:
        return {}


def _build_lines(registry, snapshot):
    lines = []
    lines.append("Commons Resource Report (Phase 51)")
    lines.append("=" * 52)
    lines.append("")
    lines.append("Resource is not allocation.")
    lines.append("Possession is not obligation.")
    lines.append("Availability is not transfer.")
    lines.append("")
    res = registry.get("resources", [])
    lines.append(f"Observed resources: {len(res)}")
    lines.append(f"Commons represented: {', '.join(snapshot.get('commons_represented', [])) or 'none'}")
    lines.append("")
    lines.append("Observed resource records:")
    for r in res:
        lines.append(
            f"  - [{r.get('resource_id','?')}] {r.get('commons_id','?')} "
            f"holds '{r.get('resource_type','?')}' "
            f"(qty {r.get('quantity','?')} {r.get('unit','')}, "
            f"observability: {r.get('observability','unknown')})"
        )
        note = r.get("resource_note")
        if note:
            lines.append(f"      note: {note}")
    lines.append("")
    lines.append("What this report does NOT mean:")
    lines.append("  - No allocation has been performed. Resource is not allocation.")
    lines.append("  - No obligation is created. Possession does not create a duty to give.")
    lines.append("  - No ownership has been transferred. Availability is not transfer.")
    lines.append("  - No command is issued. Dan-Go does not move, assign, or instruct.")
    lines.append("")
    lines.append("This report is advisory. Human review is required before any real-world action.")
    return lines


def build_report():
    registry = _load_registry()
    snapshot = _load_snapshot()
    lines = _build_lines(registry, snapshot)
    report = {
        "record_type":                      "commons_resource_report",
        "report_id":                        "resource-report-001",
        "resource_count":                   len(registry.get("resources", [])),
        "commons_represented":              snapshot.get("commons_represented", []),
        "report_text":                      "\n".join(lines),
        "report_lines":                     lines,
        "authority":                        "none",
        "resource_is_allocation":           False,
        "possession_creates_obligation":    False,
        "availability_transfers_ownership": False,
        "report_compels_action":            False,
        "generated_at":                     datetime.now(timezone.utc).isoformat(),
        "phase":                            51,
        "phase_phrase_1":                   "Resource is not allocation.",
        "phase_phrase_2":                   "Possession is not obligation.",
        "phase_phrase_3":                   "Availability is not transfer.",
    }
    report.update(PHASE_INVARIANTS)
    return report


def main():
    save = "--save" in sys.argv
    report = build_report()
    print(report["report_text"])
    if save:
        _SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _SAVE_PATH.write_text(json.dumps(report, indent=2))
        print(f"\n[saved → {_SAVE_PATH}]", file=sys.stderr)
    print(f"\n  report_id: {report['report_id']}", file=sys.stderr)
    print(f"  resource_count: {report['resource_count']}", file=sys.stderr)
    print(
        f"  resource_is_allocation={report['resource_is_allocation']} "
        f"possession_creates_obligation={report['possession_creates_obligation']} "
        f"availability_transfers_ownership={report['availability_transfers_ownership']}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
