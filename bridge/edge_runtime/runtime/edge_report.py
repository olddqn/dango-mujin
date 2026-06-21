"""
edge_report.py — Shared Edge Runtime report (both routes).

One report aggregating the shared edge layer and both routes (no per-route report
duplication for the integrated view). Writes reports/edge_runtime_report.md.

CLI:
  python -m bridge.edge_runtime.runtime.edge_report
"""

from __future__ import annotations

from typing import Any

from ..store import EDGE_REPORT_MD, utc_now_iso, write_text
from . import edge_builder, edge_memory, edge_audit


def _route_a_counts() -> list[tuple[str, int]]:
    from bridge.findability.runtime import (findability_surface_builder as fsb,
                                            consent_opportunity_builder as cob,
                                            state_reconciliation_builder as srb)
    return [("findability_surfaces", len(fsb.list_surfaces())),
            ("consent_opportunities", len(cob.list_opportunities())),
            ("state_reconciliations", len(srb.list_reconciliations()))]


def _route_b_counts() -> list[tuple[str, int]]:
    from bridge.gateway_support.runtime import (verified_bottleneck_builder as vbb,
        support_candidate_builder as scb, approval_builder as apb, consent_builder as cob2,
        execution_builder as exb, feedback_builder as fbb, ttfr_g_builder as tgb,
        withdrawal_builder as wdb)
    return [("verified_bottlenecks", len(vbb.list_verified_bottlenecks())),
            ("support_candidates", len(scb.list_candidates())),
            ("approval_records", len(apb.list_approvals())),
            ("gateway_consents", len(cob2.list_consents())),
            ("support_executions", len(exb.list_executions())),
            ("support_feedback", len(fbb.list_feedback())),
            ("ttfr_g_records", len(tgb.list_ttfr_g())),
            ("withdrawal_records", len(wdb.list_withdrawals()))]


def build_report() -> tuple[Any, dict[str, Any]]:
    edges = edge_builder.list_edges()
    audit = edge_audit.run_full_audit()
    a = _route_a_counts()
    b = _route_b_counts()
    learn = edge_memory.learn_pattern_types()

    def rows(items): return "\n".join(f"| {n} | {c} |" for n, c in items)
    route_status = "\n".join(
        f"| {name} | {'PASS' if ok else 'FAIL'} | "
        f"{len(d.get('static_violations', []) if isinstance(d, dict) else [])} | "
        f"{len(d.get('dynamic_checks', []) if isinstance(d, dict) else [])} |"
        for name, ok, d in audit["routes"])

    md = f"""# Edge Runtime Report (shared — Route A + Route B)

- Generated: {utc_now_iso()}
- Architecture: `Voice → Observed Edge → Edge Runtime ├─ Route A (Findability)  └─ Route B (Gateway Support)`
- AI proposes; humans decide. Authority none. Person Domain sealed across both routes.

## Shared edge layer
| store | records |
|---|---|
| observed_edges | {len(edges)} |
| edge_memory (episodes) | {len(edge_memory.list_memory())} |

## Route A — Findability
| store | records |
|---|---|
{rows(a)}

## Route B — Gateway Support
| store | records |
|---|---|
{rows(b)}

## Shared edge-memory learning (type-level, non-KPI, no actor)
- {learn}

## Audit
| layer | result | static violations | dynamic checks |
|---|---|---|---|
| edge layer | {'PASS' if not audit['edge_violations'] else 'FAIL'} | {len(audit['edge_violations'])} | — |
{route_status}
| **overall** | **{'PASS' if audit['passed'] else 'FAIL'}** | | |

## Shared guarantees (both routes)
Person Domain sealed · no ranking · no recommendation · no selection · no
reach-gap estimation · no Saiyan Scouter · append-only · single shared edge
records & edge memory (no duplication). Route B adds Resource-Acceptance-only,
two-key execution, TTFR-G ⟂ TTFR-P; Route A adds observation-only, owner→Mujin,
no outreach / growth / marketing / pre-exposure. Neither implements Person Relief.

---

*0 records across all layers is the valid empty-safe state: the runtime does not
fabricate. Findability opens consent opportunity; Gateway Support advances TTFR-G
only. Neither resolves the (person) Reach Gap.*
"""
    path = write_text(EDGE_REPORT_MD, md)
    return path, {"edges": len(edges), "route_a": a, "route_b": b, "audit_passed": audit["passed"]}


def main() -> None:
    print("=" * 64)
    print("EDGE RUNTIME REPORT (shared)")
    print("=" * 64)
    path, s = build_report()
    print(f"  ✓ wrote {path.name}")
    print(f"  edges={s['edges']} | route_a={dict(s['route_a'])} | route_b={dict(s['route_b'])}")
    print(f"  audit passed: {s['audit_passed']}")


if __name__ == "__main__":
    main()
