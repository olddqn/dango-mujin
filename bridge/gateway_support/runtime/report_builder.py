"""
report_builder.py — Gateway Support report (reports/gateway_support_report.md).

Summarises the runtime state: per-layer counts, invariant violations, the
pipeline, and the preserved boundaries. With no real input every count is 0,
which is the correct, valid state.

CLI:
  python -m bridge.gateway_support.runtime.report_builder
"""

from __future__ import annotations

from typing import Any

from ..store import REPORT_MD, utc_now_iso, write_text
from .bottleneck_builder import list_verified_bottlenecks, check_invariants as _bn_chk
from .support_candidate_builder import list_candidates, check_invariants as _cand_chk
from .approval_builder import list_approvals, check_invariants as _ap_chk
from .consent_builder import list_consents, check_invariants as _co_chk
from .execution_builder import list_executions, check_invariants as _ex_chk
from .feedback_builder import list_feedback, check_invariants as _fb_chk
from .ttfr_g_builder import list_ttfr_g, check_invariants as _tg_chk
from .withdrawal_builder import list_withdrawals, check_invariants as _wd_chk
from .memory_builder import list_memory, learn_support_pattern_types, check_invariants as _mem_chk


def collect() -> dict[str, Any]:
    layers = [
        ("verified_bottlenecks", list_verified_bottlenecks(), _bn_chk()),
        ("support_candidates", list_candidates(), _cand_chk()),
        ("approval_records", list_approvals(), _ap_chk()),
        ("gateway_consents", list_consents(), _co_chk()),
        ("support_executions", list_executions(), _ex_chk()),
        ("support_feedback", list_feedback(), _fb_chk()),
        ("ttfr_g_records", list_ttfr_g(), _tg_chk()),
        ("withdrawal_records", list_withdrawals(), _wd_chk()),
        ("support_memory", list_memory(), _mem_chk()),
    ]
    total_v = sum(len(v) for _, _, v in layers)
    return {"layers": layers, "total_violations": total_v,
            "learning": learn_support_pattern_types()}


def build_report() -> tuple[Any, dict[str, Any]]:
    s = collect()
    rows = "\n".join(
        f"| {name} | {len(recs)} | {len(v)} |" for name, recs, v in s["layers"])
    md = f"""# Gateway Support Runtime Report

- Generated: {utc_now_iso()}
- Layer: `bridge/gateway_support/` — observation-only Gateway Support (F-9..F-20).
- AI proposes; humans decide. Authority none. Person Domain sealed.

## Pipeline
```
Observed Edge → Verified Bottleneck → Support Candidate → Approval →
Gateway Consent → Support Execution → Reality Feedback → TTFR-G Accounting →
Withdrawal → Support Memory
```

## Counts & invariant violations
| layer | records | violations |
|---|---|---|
{rows}
| **TOTAL violations** | | **{s['total_violations']}** |

## Type-level learning (no gateway identity)
- {s['learning']}

## Preserved boundaries
1. Person Domain sealed (no owner fields; person_domain_sealed on every record).
2. Gateway Support only · Resource Acceptance layer only.
3. Verified = currently observable condition, **not proof** (F-11).
4. Support Candidate = possibility only · plural · unordered (F-12).
5. Approval = gatekeeping only — permit/block; never rank/recommend/select/create (F-13).
6. Gateway Consent required — explicit, revocable, obtained; statement ≠ consent (F-14).
7. Execution = two-key gate (permit ∧ consent), never automatic (F-15).
8. Feedback = observation only; no relief claim / inflation (F-16).
9. TTFR-G ⟂ TTFR-P — separate ledger; no combined metric / KPI / maximization (F-17).
10. Withdrawal always possible; any key lost halts support; not failure (F-18).
11. Memory append-only; no gateway score/ranking/reputation/profile; type-level learning (F-19).

## Not implemented (by design)
Person Relief · Need inference · Ranking · Recommendation · Selection ·
Auto-execution · Cooperation assignment · Gateway profiling/scoring/reputation ·
Reach Gap estimation.

---

*0 records across all layers is the correct, valid state with no verified real
input: the runtime does not fabricate. Gateway support advances TTFR-G only and
never resolves the (person) Reach Gap.*
"""
    path = write_text(REPORT_MD, md)
    return path, s


def main() -> None:
    print("=" * 64)
    print("GATEWAY SUPPORT REPORT BUILDER")
    print("=" * 64)
    path, s = build_report()
    print(f"  ✓ wrote {path.name}")
    for name, recs, v in s["layers"]:
        print(f"    {name:>22}: {len(recs)} records, {len(v)} violations")
    print(f"  TOTAL violations: {s['total_violations']}")


if __name__ == "__main__":
    main()
