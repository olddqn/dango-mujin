"""
decision_boundary_report.py — Phase H-6 report.

Writes reports/decision_boundary_report.md: where (if anywhere) a candidate
turned into a decision across Hermes's memory. Hermes records the boundary; it
never decides.

CLI:
  python -m bridge.agent_commons.runtime.decision_boundary_report
"""

from __future__ import annotations

from typing import Any

from .store import (
    DECISION_BOUNDARY_JSONL, DECISION_BOUNDARY_REPORT_MD, read_jsonl,
    utc_now_iso, write_text,
)
from .decision_boundary_builder import check_invariants


def build_report() -> tuple[Any, dict[str, Any]]:
    records = read_jsonl(DECISION_BOUNDARY_JSONL)
    by_type: dict[str, int] = {}
    for r in records:
        by_type[r.get("boundary_type", "?")] = by_type.get(r.get("boundary_type", "?"), 0) + 1
    fired = [r for r in records if r.get("decision_detected")]
    human_reviewed = [r for r in records if r.get("human_reviewed") is True]
    violations = check_invariants()

    rows = "\n".join(
        f"| `{r['decision_boundary_id']}` | {r['source_record']} | {r['boundary_type']} | "
        f"{r['candidate_count']} | {r['decision_detected']} | {r.get('decision_marker') or '—'} |"
        for r in records) or "| (none) | | | | | |"

    md = f"""# Decision Boundary Report

- Generated: {utc_now_iso()}
- Layer: `bridge/agent_commons/` (advisory only · authority none · AI proposes, human decides)
- H-6 operationalises N-1.7: Hermes records WHERE a candidate became a decision
  (selection / allocation / execution). It never makes, approves, or rejects a
  decision. Detection is negation-aware (anti-decision disclaimers are not
  decisions).

## Counts
| metric | value |
|---|---|
| Decision Boundary Count | {len(records)} |
| Decision Detected (fired) | {len(fired)} |
| candidate_only | {by_type.get('candidate_only', 0)} |
| selection | {by_type.get('selection', 0)} |
| allocation | {by_type.get('allocation', 0)} |
| execution | {by_type.get('execution', 0)} |
| Violation Count | {len(violations)} |
| Human Reviewed Count | {len(human_reviewed)} (AI-generated; human review pending by design) |

## Interpretation
{("All source records resolve to `candidate_only`: **no decision has entered "
  "Hermes's memory.** Hermes can answer 'where did this become a decision?' — "
  "the answer is: nowhere. That is memory, not governance.")
 if not fired else
 f"{len(fired)} record(s) show a decision marker; see the table. Hermes records "
 "this and stops. It does not decide."}

## Violations
{chr(10).join(f"- {v}" for v in violations) if violations else "- (none)"}

## Boundaries
| boundary | source | type | candidate_count | decision_detected | marker |
|---|---|---|---|---|---|
{rows}

---

*Hermes records where a candidate became a decision. It chooses no candidate,
ranks none, recommends none, allocates nothing, executes nothing. The first
question (where did this become a decision?) is memory; the second (what should
we decide?) is governance. Hermes remains memory only. Reach Gap is unresolved;
this layer does not resolve it.*
"""
    path = write_text(DECISION_BOUNDARY_REPORT_MD, md)
    return path, {"count": len(records), "fired": len(fired), "by_type": by_type,
                  "violations": violations}


def main() -> None:
    print("=" * 64)
    print("DECISION BOUNDARY REPORT BUILDER")
    print("=" * 64)
    path, s = build_report()
    print(f"  ✓ wrote {path.name}")
    print(f"  boundaries={s['count']} fired={s['fired']} by_type={s['by_type']} "
          f"violations={len(s['violations'])}")


if __name__ == "__main__":
    main()
