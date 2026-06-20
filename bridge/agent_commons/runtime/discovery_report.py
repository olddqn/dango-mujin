"""
discovery_report.py — Phase F-2 report.

Writes reports/discovery_report.md: who discovered what, where — if anyone has.
When no discovery event exists, every count is 0, recorded as an observation
("no discovery has happened"), not a failure.

CLI:
  python -m bridge.agent_commons.runtime.discovery_report
"""

from __future__ import annotations

from typing import Any

from .store import (
    DISCOVERY_EVENTS_JSONL, DISCOVERY_EVIDENCE_JSONL, DISCOVERY_LEARNINGS_JSONL,
    DISCOVERY_PATTERNS_JSONL, DISCOVERY_REFLECTIONS_JSONL, DISCOVERY_REPORT_MD,
    read_jsonl, utc_now_iso, write_text,
)
from .discovery_evidence_builder import check_invariants


def build_report() -> tuple[Any, dict[str, Any]]:
    events = read_jsonl(DISCOVERY_EVENTS_JSONL)
    refl = read_jsonl(DISCOVERY_REFLECTIONS_JSONL)
    learnings = read_jsonl(DISCOVERY_LEARNINGS_JSONL)
    patterns = read_jsonl(DISCOVERY_PATTERNS_JSONL)
    evidence = read_jsonl(DISCOVERY_EVIDENCE_JSONL)
    violations = check_invariants()

    discoverer_count = len({r.get("discoverer_type") for r in refl} - {None})
    repeated_path = sum(1 for p in patterns
                        if p.get("pattern_key") == "repeated_discovery_path")

    empty = len(events) == 0
    state = ("**No discovery event exists.** No external actor has discovered "
             "anything yet. This is the correct, current state — recorded as an "
             "observation, not a failure. Hermes generates nothing from nothing."
             if empty else
             f"{len(events)} discovery event(s) observed.")

    rows = "\n".join(
        f"| `{r['reflection_id']}` | {r['discoverer_type']} | {r['surface']} | "
        f"{r['object']} | {r.get('observed_at','')} |"
        for r in refl) or "| (none) | | | | |"

    md = f"""# Discovery Report

- Generated: {utc_now_iso()}
- Layer: `bridge/agent_commons/` (advisory only · authority none · AI proposes, human decides)
- F-2 records the **Discovery** layer above Findability: not "what *can* be
  discovered" (F-1/F-1.5/F-1.7) but "what *was actually* discovered" — who, what,
  where. Only verified events are adopted; none are invented.

## Counts
| metric | value |
|---|---|
| **discovery_event_count** | {len(events)} |
| **discoverer_count** | {discoverer_count} |
| **repeated_path_count** | {repeated_path} |
| reflections | {len(refl)} |
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

## Discoveries (descriptive only — no discoverer or surface ranked)
| reflection | discoverer | surface | object | observed at |
|---|---|---|---|---|
{rows}

## Violations
{chr(10).join(f"- {v}" for v in violations) if violations else "- (none)"}

---

*Discovery Event Memory records what actually happened, not what should happen.
No discoverer is ranked, no surface ranked, none recommended; there is no
outreach, marketing, growth, or recruitment here. Zero discovery is an
observation, not a failure — currently, no one has discovered anything. Reach
Gap is unresolved; this layer does not resolve it. It only records who, if
anyone, has found what.*
"""
    path = write_text(DISCOVERY_REPORT_MD, md)
    return path, {"events": len(events), "discoverer_count": discoverer_count,
                  "repeated_path": repeated_path, "reflections": len(refl),
                  "learnings": len(learnings), "patterns": len(patterns),
                  "evidence": len(evidence), "violations": violations}


def main() -> None:
    print("=" * 64)
    print("DISCOVERY REPORT BUILDER")
    print("=" * 64)
    path, s = build_report()
    print(f"  ✓ wrote {path.name}")
    print(f"  discovery_event_count={s['events']} discoverer_count={s['discoverer_count']} "
          f"repeated_path_count={s['repeated_path']} reflections={s['reflections']} "
          f"learnings={s['learnings']} patterns={s['patterns']} evidence={s['evidence']} "
          f"violations={len(s['violations'])}")


if __name__ == "__main__":
    main()
