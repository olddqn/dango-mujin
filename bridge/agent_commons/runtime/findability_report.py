"""
findability_report.py — Phase F-1 report.

Writes reports/findability_report.md: who discovered Mujin (if anyone). When no
actor has discovered Mujin yet, findability_count = 0 — which is recorded as an
observation (discoverability_absent), NOT a failure.

CLI:
  python -m bridge.agent_commons.runtime.findability_report
"""

from __future__ import annotations

from typing import Any

from .store import (
    FINDABILITY_EVENT_JSONL, FINDABILITY_EVIDENCE_JSONL,
    FINDABILITY_LEARNING_JSONL, FINDABILITY_PATTERN_JSONL,
    FINDABILITY_REFLECTION_JSONL, FINDABILITY_REPORT_MD, read_jsonl,
    utc_now_iso, write_text,
)
from .findability_evidence_builder import check_invariants


def build_report() -> tuple[Any, dict[str, Any]]:
    events = read_jsonl(FINDABILITY_EVENT_JSONL)
    reflections = read_jsonl(FINDABILITY_REFLECTION_JSONL)
    learnings = read_jsonl(FINDABILITY_LEARNING_JSONL)
    patterns = read_jsonl(FINDABILITY_PATTERN_JSONL)
    evidence = read_jsonl(FINDABILITY_EVIDENCE_JSONL)
    violations = check_invariants()
    n = len(events)

    voice_created = sum(1 for r in reflections if r.get("voice_created"))
    by_channel: dict[str, int] = {}
    for r in reflections:
        by_channel[r.get("source_channel") or "?"] = \
            by_channel.get(r.get("source_channel") or "?", 0) + 1

    absent = n == 0
    state = ("`discoverability_absent` — **no actor has discovered Mujin yet.** "
             "This is an observation, not a failure. Findability records "
             "discovery; with no discovery there is nothing to record, and "
             "Hermes generates nothing from nothing."
             if absent else
             f"`discoverability_exists` — {n} discovery event(s) observed.")

    chan_rows = "\n".join(f"| {c} | {k} |" for c, k in sorted(by_channel.items())) \
        or "| (none) | 0 |"

    md = f"""# Findability Report

- Generated: {utc_now_iso()}
- Layer: `bridge/agent_commons/` (advisory only · authority none · AI proposes, human decides)
- F-1 records WHO discovered Mujin. **Findability is not Reachability:** Mujin
  never searches for, contacts, recruits, or infers the Need of anyone. It only
  records that an actor *found* Mujin.
- Pipeline position: **Findability → Voice → Observation → … → Decision Boundary.**

## Counts
| metric | value |
|---|---|
| Findability Count (events) | {n} |
| Reflections | {len(reflections)} |
| Learnings | {len(learnings)} |
| Patterns | {len(patterns)} |
| Evidence | {len(evidence)} |
| Voice generated | {voice_created} |
| Need generated | 0 |
| Cooperation generated | 0 |
| Decision generated | 0 |
| outreach detected | 0 |
| recruitment detected | 0 |
| Violation Count | {len(violations)} |

## Observed state
{state}

## Discovery by channel (descriptive only — no channel is ranked or recommended)
| channel | discoveries |
|---|---|
{chan_rows}

## Violations
{chr(10).join(f"- {v}" for v in violations) if violations else "- (none)"}

---

*Findability records that someone found Mujin. It does not find anyone. Mujin
does not search, contact, recruit, or guess a Need. No channel is ranked, none
recommended; there is no acquisition, outreach, or growth plan here. Zero
discoveries is an observation, not a failure. Reach Gap is unresolved; this
layer does not resolve it — it only records who arrived on their own.*
"""
    path = write_text(FINDABILITY_REPORT_MD, md)
    return path, {"events": n, "reflections": len(reflections),
                  "learnings": len(learnings), "patterns": len(patterns),
                  "evidence": len(evidence), "voice_created": voice_created,
                  "violations": violations}


def main() -> None:
    print("=" * 64)
    print("FINDABILITY REPORT BUILDER")
    print("=" * 64)
    path, s = build_report()
    print(f"  ✓ wrote {path.name}")
    print(f"  events={s['events']} reflections={s['reflections']} "
          f"learnings={s['learnings']} patterns={s['patterns']} "
          f"evidence={s['evidence']} voice_created={s['voice_created']} "
          f"violations={len(s['violations'])}")


if __name__ == "__main__":
    main()
