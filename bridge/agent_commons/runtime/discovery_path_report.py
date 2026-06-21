"""
discovery_path_report.py — Phase F-2.5 report.

Writes reports/discovery_path_report.md: the observed Surface → Object → Event
relationships. When no discovery event exists, the path count is 0, recorded as
an observation ("no discovery path has been observed"), not a failure.

CLI:
  python -m bridge.agent_commons.runtime.discovery_path_report
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from .store import (
    DISCOVERY_EVENTS_JSONL, DISCOVERY_PATH_EVIDENCE_JSONL,
    DISCOVERY_PATH_LEARNINGS_JSONL, DISCOVERY_PATH_PATTERNS_JSONL,
    DISCOVERY_PATH_REFLECTIONS_JSONL, DISCOVERY_PATH_REPORT_MD, read_jsonl,
    utc_now_iso, write_text,
)
from .discovery_path_evidence_builder import check_invariants


def build_report() -> tuple[Any, dict[str, Any]]:
    events = read_jsonl(DISCOVERY_EVENTS_JSONL)
    refl = read_jsonl(DISCOVERY_PATH_REFLECTIONS_JSONL)
    learnings = read_jsonl(DISCOVERY_PATH_LEARNINGS_JSONL)
    patterns = read_jsonl(DISCOVERY_PATH_PATTERNS_JSONL)
    evidence = read_jsonl(DISCOVERY_PATH_EVIDENCE_JSONL)
    violations = check_invariants()

    path_links = Counter((r.get("surface_type"), r.get("object_type")) for r in refl)
    repeated_path = sum(1 for c in path_links.values() if c > 1)

    empty = len(refl) == 0
    state = ("**No discovery path has been observed.** No discovery event exists "
             "(discovery_event_count = 0), so there is no Surface→Object→Event "
             "chain to record. This is the correct, current state — an "
             "observation, not a failure. Hermes generates nothing from nothing."
             if empty else
             f"{len(refl)} discovery path(s) observed.")

    rows = "\n".join(
        f"| `{r['path_id']}` | {r['surface_type']} | {r['object_type']} | "
        f"{r['discoverer_type']} | {r['event_id']} |"
        for r in refl) or "| (none) | | | | |"

    md = f"""# Discovery Path Report

- Generated: {utc_now_iso()}
- Layer: `bridge/agent_commons/` (advisory only · authority none · AI proposes, human decides)
- F-2.5 joins F-1/F-1.5/F-1.7/F-2 to observe the **Surface → Object → Event**
  relationship: when a discovery happened, from which surface was which object
  found, by whom.
- **This is not** a marketing funnel, growth, SEO, acquisition, or conversion
  analysis. It records only the observed relationship. A path is recorded only
  when a real event matches a verified surface and object.

## Counts
| metric | value |
|---|---|
| **discovery_event_count** | {len(events)} |
| **discovery_path_count** | {len(refl)} |
| **repeated_path_count** | {repeated_path} |
| learnings | {len(learnings)} |
| patterns | {len(patterns)} |
| evidence | {len(evidence)} |
| voice generated | 0 |
| need generated | 0 |
| gateway generated | 0 |
| cooperation generated | 0 |
| decision generated | 0 |
| Violation Count | {len(violations)} |

## Observed state
{state}

## Discovery paths (descriptive only — no path ranked or recommended)
| path | surface | object | discoverer | event |
|---|---|---|---|---|
{rows}

## Violations
{chr(10).join(f"- {v}" for v in violations) if violations else "- (none)"}

---

*Discovery Path Review records the observed Surface→Object→Event relationship,
not a route to optimise. No path is ranked, recommended, or prioritised; there
is no funnel, conversion, growth, marketing, acquisition, or outreach here. Zero
paths is an observation, not a failure — currently no discovery path has been
observed. Reach Gap is unresolved; this layer does not resolve it.*
"""
    path = write_text(DISCOVERY_PATH_REPORT_MD, md)
    return path, {"events": len(events), "paths": len(refl),
                  "repeated_path": repeated_path, "learnings": len(learnings),
                  "patterns": len(patterns), "evidence": len(evidence),
                  "violations": violations}


def main() -> None:
    print("=" * 64)
    print("DISCOVERY PATH REPORT BUILDER")
    print("=" * 64)
    path, s = build_report()
    print(f"  ✓ wrote {path.name}")
    print(f"  discovery_event_count={s['events']} discovery_path_count={s['paths']} "
          f"repeated_path_count={s['repeated_path']} learnings={s['learnings']} "
          f"patterns={s['patterns']} evidence={s['evidence']} "
          f"violations={len(s['violations'])}")


if __name__ == "__main__":
    main()
