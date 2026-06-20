"""
discoverable_object_report.py — Phase F-1.7 report.

Writes reports/discoverable_object_report.md: the Surface → Object mapping —
what an external actor can actually discover. Observation of what is visible,
not branding/marketing/SEO/growth.

CLI:
  python -m bridge.agent_commons.runtime.discoverable_object_report
"""

from __future__ import annotations

from typing import Any

from .store import (
    DISCOVERABLE_OBJECT_EVIDENCE_JSONL, DISCOVERABLE_OBJECT_LEARNING_JSONL,
    DISCOVERABLE_OBJECT_PATTERN_JSONL, DISCOVERABLE_OBJECT_REFLECTION_JSONL,
    DISCOVERABLE_OBJECT_REPORT_MD, read_jsonl, utc_now_iso, write_text,
)
from .discoverable_object_evidence_builder import check_invariants


def build_report() -> tuple[Any, dict[str, Any]]:
    refl = read_jsonl(DISCOVERABLE_OBJECT_REFLECTION_JSONL)
    learnings = read_jsonl(DISCOVERABLE_OBJECT_LEARNING_JSONL)
    patterns = read_jsonl(DISCOVERABLE_OBJECT_PATTERN_JSONL)
    evidence = read_jsonl(DISCOVERABLE_OBJECT_EVIDENCE_JSONL)
    violations = check_invariants()

    public = [r for r in refl if r.get("public")]
    discoverable = [r for r in refl if r.get("discoverable")]
    disc_types = sorted({r["object_type"] for r in discoverable})
    gap_types = sorted({r["object_type"] for r in refl if r.get("discoverable") is False})

    rows = "\n".join(
        f"| {r['surface_type']} | {r['object_type']} | {r['discoverable']} | "
        f"{r['public']} | {r['requires_prior_knowledge']} | {r.get('verified_by','')} |"
        for r in refl) or "| (none) | | | | | |"

    md = f"""# Discoverable Object Report

- Generated: {utc_now_iso()}
- Layer: `bridge/agent_commons/` (advisory only · authority none · AI proposes, human decides)
- F-1.7 observes the **Surface → Object** mapping: given the surfaces that exist
  (F-1.5), what can an external actor actually discover.
- **This is not** branding, marketing, SEO, or growth analysis. It records only
  what is visible. Reality Correction: each mapping was verified; unconfirmed
  objects are recorded `discoverable=false` (a visibility gap).

## Counts
| metric | value |
|---|---|
| **object_count** | {len(refl)} |
| **public_object_count** | {len(public)} |
| **discoverable_object_count** | {len(discoverable)} |
| learnings | {len(learnings)} |
| patterns | {len(patterns)} |
| evidence | {len(evidence)} |
| voice generated | 0 |
| need generated | 0 |
| gateway generated | 0 |
| cooperation generated | 0 |
| decision generated | 0 |
| Violation Count | {len(violations)} |

- Discoverable object types: {', '.join(disc_types) or '(none)'}
- Not-discoverable (gap) object types: {', '.join(gap_types) or '(none)'}

## Surface → Object (verified observation; no object ranked or recommended)
| surface | object | discoverable | public | needs prior knowledge | verified by |
|---|---|---|---|---|---|
{rows}

## Honest reading
What is actually discoverable today is **Dan-Go**: `globe/`, `bridge/gitsea`,
`bridge/sutable`, the source tree, and the top-level specs/README. The **Mujin
platform, `contribution_commons`, `voice_commons`, and `agent_commons` are NOT
publicly discoverable** — they live on an unpushed branch or a local service
(404 on public main). The `MUJIN_PROTOCOL.md` document is public, but the
working platform is not. Notably, **no voices are publicly discoverable**, which
is the correct, reassuring state for a layer that must never expose people. The
visibility gap is recorded as an observation; nothing here proposes closing it.

## Violations
{chr(10).join(f"- {v}" for v in violations) if violations else "- (none)"}

---

*Discoverable Object Review records what is visible, not what should be shown.
No object is ranked, recommended, or targeted; there is no marketing, growth,
acquisition, or recruitment here. A visibility gap is an observation. Reach Gap
is unresolved; this layer does not resolve it — it only states what an outside
actor can, and cannot, currently discover.*
"""
    path = write_text(DISCOVERABLE_OBJECT_REPORT_MD, md)
    return path, {"object_count": len(refl), "public": len(public),
                  "discoverable": len(discoverable), "learnings": len(learnings),
                  "patterns": len(patterns), "evidence": len(evidence),
                  "violations": violations}


def main() -> None:
    print("=" * 64)
    print("DISCOVERABLE OBJECT REPORT BUILDER")
    print("=" * 64)
    path, s = build_report()
    print(f"  ✓ wrote {path.name}")
    print(f"  object_count={s['object_count']} public={s['public']} "
          f"discoverable={s['discoverable']} learnings={s['learnings']} "
          f"patterns={s['patterns']} evidence={s['evidence']} "
          f"violations={len(s['violations'])}")


if __name__ == "__main__":
    main()
