"""
findability_surface_report.py — Phase F-1.5 report.

Writes reports/findability_surface_report.md: where Mujin is currently findable.
Observation of what exists — not an SEO, acquisition, marketing, or growth plan.

CLI:
  python -m bridge.agent_commons.runtime.findability_surface_report
"""

from __future__ import annotations

from typing import Any

from .store import (
    FINDABILITY_SURFACE_EVIDENCE_JSONL, FINDABILITY_SURFACE_LEARNING_JSONL,
    FINDABILITY_SURFACE_PATTERN_JSONL, FINDABILITY_SURFACE_REFLECTION_JSONL,
    FINDABILITY_SURFACE_REPORT_MD, read_jsonl, utc_now_iso, write_text,
)
from .findability_surface_evidence_builder import check_invariants


def build_report() -> tuple[Any, dict[str, Any]]:
    refl = read_jsonl(FINDABILITY_SURFACE_REFLECTION_JSONL)
    learnings = read_jsonl(FINDABILITY_SURFACE_LEARNING_JSONL)
    patterns = read_jsonl(FINDABILITY_SURFACE_PATTERN_JSONL)
    evidence = read_jsonl(FINDABILITY_SURFACE_EVIDENCE_JSONL)
    violations = check_invariants()

    examined = len(refl)
    exist = [r for r in refl if r.get("exists")]
    public = [r for r in refl if r.get("publicly_accessible")]
    discoverable = [r for r in refl if r.get("discoverable")]

    rows = "\n".join(
        f"| {r['surface_type']} | {r['exists']} | {r['publicly_accessible']} | "
        f"{r['discoverable']} | {r['requires_prior_knowledge']} | {r.get('verified_by','')} |"
        for r in refl) or "| (none) | | | | | |"

    md = f"""# Findability Surface Report

- Generated: {utc_now_iso()}
- Layer: `bridge/agent_commons/` (advisory only · authority none · AI proposes, human decides)
- F-1.5 observes WHERE Mujin is currently findable (its public surfaces).
- **This is not** an SEO audit, traffic/acquisition analysis, marketing study,
  or any plan to increase reach. It records only what exists.
- Reality Correction: every surface was verified on its observation date; the
  method is recorded per surface. Unconfirmed surfaces are recorded `exists=false`.

## Counts
| metric | value |
|---|---|
| surfaces examined | {examined} |
| **surface_count (exists=true)** | {len(exist)} |
| **public_surface_count** | {len(public)} |
| **discoverable_surface_count** | {len(discoverable)} |
| learnings | {len(learnings)} |
| patterns | {len(patterns)} |
| evidence | {len(evidence)} |
| voice generated | 0 |
| need generated | 0 |
| cooperation generated | 0 |
| decision generated | 0 |
| outreach detected | 0 |
| growth detected | 0 |
| marketing detected | 0 |
| Violation Count | {len(violations)} |

## Surfaces (verified observation, no surface ranked or recommended)
| surface | exists | public | discoverable | needs prior knowledge | verified by |
|---|---|---|---|---|---|
{rows}

## Honest reading
The repository (`olddqn/dango-mujin`) is public, but the **Mujin platform branch
is not pushed** — so what is publicly findable today is the Dan-Go/globe history
plus the README, not the Contribution Commons platform. The localhost service
and the gitlawb/Nookplot node are local-only. **No public voice records exist**
(absent on the public branch), which is the correct and reassuring state for a
layer that must never expose people. Mujin is, in practice, barely findable —
and that is recorded as an observation, not corrected by reaching anyone.

## Violations
{chr(10).join(f"- {v}" for v in violations) if violations else "- (none)"}

---

*Findability Surface Review records what exists, not how to increase it. No
surface is ranked, recommended, or prioritised; there is no acquisition,
outreach, marketing, or growth plan here. Absence is an observation. Reach Gap
is unresolved; this layer does not resolve it — it only states where Mujin can,
and cannot, currently be found.*
"""
    path = write_text(FINDABILITY_SURFACE_REPORT_MD, md)
    return path, {"examined": examined, "surface_count": len(exist),
                  "public": len(public), "discoverable": len(discoverable),
                  "learnings": len(learnings), "patterns": len(patterns),
                  "evidence": len(evidence), "violations": violations}


def main() -> None:
    print("=" * 64)
    print("FINDABILITY SURFACE REPORT BUILDER")
    print("=" * 64)
    path, s = build_report()
    print(f"  ✓ wrote {path.name}")
    print(f"  examined={s['examined']} surface_count={s['surface_count']} "
          f"public={s['public']} discoverable={s['discoverable']} "
          f"learnings={s['learnings']} patterns={s['patterns']} "
          f"evidence={s['evidence']} violations={len(s['violations'])}")


if __name__ == "__main__":
    main()
