"""
stack_audit.py — Gateway Support Stack Audit (F-20).

Verifies the runtime preserves every boundary:
  person-domain seal · consent boundary · approval boundary · candidate boundary ·
  execution boundary · TTFR separation · withdrawal path · memory integrity.

Two checks:
  (1) Static: invariant checks over the canonical (persisted) stores, plus a
      structural scan for forbidden fields.
  (2) Dynamic: an in-memory end-to-end simulation (never persisted) that asserts
      each boundary actually holds at runtime.

CLI:
  python -m bridge.gateway_support.runtime.stack_audit
"""

from __future__ import annotations

import importlib
from typing import Any

from .. import store as _store
from . import (bottleneck_builder, support_candidate_builder, approval_builder,
               consent_builder, execution_builder, feedback_builder, ttfr_g_builder,
               withdrawal_builder, memory_builder)


# ── (1) static checks over persisted stores ─────────────────────────────────

def static_violations() -> list[str]:
    out: list[str] = []
    out += bottleneck_builder.check_invariants()
    out += support_candidate_builder.check_invariants()
    out += approval_builder.check_invariants()
    out += consent_builder.check_invariants()
    out += execution_builder.check_invariants()
    out += feedback_builder.check_invariants()
    out += ttfr_g_builder.check_invariants()
    out += withdrawal_builder.check_invariants()
    out += memory_builder.check_invariants()
    # structural scan: no record anywhere may carry a forbidden field
    from ..store import (read_jsonl, FORBIDDEN_FIELDS,
                         VERIFIED_BOTTLENECKS_JSONL, SUPPORT_CANDIDATES_JSONL,
                         APPROVAL_RECORDS_JSONL, GATEWAY_CONSENTS_JSONL,
                         SUPPORT_EXECUTIONS_JSONL, SUPPORT_FEEDBACK_JSONL,
                         TTFR_G_RECORDS_JSONL, WITHDRAWAL_RECORDS_JSONL,
                         SUPPORT_MEMORY_JSONL)
    for p in (VERIFIED_BOTTLENECKS_JSONL, SUPPORT_CANDIDATES_JSONL,
              APPROVAL_RECORDS_JSONL, GATEWAY_CONSENTS_JSONL, SUPPORT_EXECUTIONS_JSONL,
              SUPPORT_FEEDBACK_JSONL, TTFR_G_RECORDS_JSONL, WITHDRAWAL_RECORDS_JSONL,
              SUPPORT_MEMORY_JSONL):
        for r in read_jsonl(p):
            for f in FORBIDDEN_FIELDS:
                if f in r:
                    out.append(f"{p.name}: record carries forbidden field {f}")
    return out


# ── (2) dynamic end-to-end boundary simulation (in-memory, never persisted) ──

def _patched_modules():
    """Fresh module objects with in-memory persistence (canonical stores untouched)."""
    mods = [importlib.reload(m) for m in (
        bottleneck_builder, support_candidate_builder, approval_builder,
        consent_builder, execution_builder, feedback_builder, ttfr_g_builder,
        withdrawal_builder, memory_builder)]
    mem: dict[str, list[dict[str, Any]]] = {}

    def mread(p): return [dict(r) for r in mem.get(str(p), [])]

    def mappend(p, rec):
        for f in _store.FORBIDDEN_FIELDS:
            if f in rec:
                raise _store.GatewaySupportError(f"forbidden field {f}")
        rec = dict(rec)
        rec.setdefault("appended_at", "t")
        rec["event_hash"] = "h"
        mem.setdefault(str(p), []).append(rec)
        return rec

    def mnext(prefix, p): return f"{prefix}-{len(mem.get(str(p), [])) + 1:03d}"

    for m in mods:
        m.append_jsonl = mappend
        m.read_jsonl = mread
        m.next_id = mnext
    return mods, mem


def dynamic_boundary_checks() -> list[tuple[str, bool]]:
    (bb, cb, ap, co, ex, fb, tg, wd, mb), mem = _patched_modules()
    results: list[tuple[str, bool]] = []

    def chk(name, cond): results.append((name, bool(cond)))

    # candidate boundary: held verification raises; candidates plural/unordered/no-rank; no fabrication
    try:
        bb.make_verified_bottleneck(source_edge="e", gateway_ref="X",
            public_source_url="u", bottleneck_kind="k", accepted_support_forms=["a"],
            verified_by="r", self_stated=True, public=True, currently_observable=False,
            inference_free=True)
        held_ok = False
    except ValueError:
        held_ok = True
    chk("verification held when condition missing (F-11)", held_ok)

    b = bb.record_verified_bottleneck(source_edge="e", gateway_ref="X",
        public_source_url="https://x.test", bottleneck_kind="funding",
        accepted_support_forms=["a", "b", "c"], verified_by="r",
        self_stated=True, public=True, currently_observable=True, inference_free=True)
    cands = cb.build()
    chk("candidate boundary: plural, unordered, no rank field (F-12)",
        len(cands) == 3 and all("rank" not in c and "order" not in c and c["is_unordered"] for c in cands))
    chk("candidate no fabrication: 0 forms -> 0 candidates",
        len(cb.derive_candidates_for({**b, "accepted_support_forms": []})) == 0)

    c = cands[0]
    # approval boundary: gatekeeping only
    try:
        ap.make_approval(c["candidate_id"], "recommend", "r"); ap_ok = False
    except ValueError:
        ap_ok = True
    chk("approval boundary: gatekeeping only, rejects non permit/block (F-13)", ap_ok)

    # execution boundary: no auto-execution without two keys
    try:
        ex.execute(c["candidate_id"], "x"); nokey = False
    except ValueError:
        nokey = True
    chk("execution boundary: refused without two keys (F-15)", nokey)

    # consent boundary: statement != consent (inference refused)
    try:
        co.make_gateway_consent(gateway_ref="X", bottleneck_id=c["bottleneck_id"],
            support_form=c["support_form"], consent_source="", obtained=False); co_ok = False
    except ValueError:
        co_ok = True
    chk("consent boundary: statement is not consent / obtained-not-inferred (F-14)", co_ok)

    ap.record_approval(c["candidate_id"], "permit", "r")
    co.record_gateway_consent(gateway_ref="X", bottleneck_id=c["bottleneck_id"],
        support_form=c["support_form"], consent_source="email", obtained=True)
    e = ex.execute(c["candidate_id"], "x")
    chk("execution: person-domain sealed + ttfr-p untouched (F-15)",
        e["no_person_domain_interaction"] and e["does_not_mutate_ttfr_p"] and e["no_owner_interaction"])

    # feedback boundary: observation only
    f = fb.record_feedback(execution_id=e["execution_id"], relief_observed=False,
        relief_source_url="", observed_by="o")
    chk("feedback boundary: observation only, held, no person relief (F-16)",
        f["status"] == "held" and f["no_relief_claim"] and f["no_person_relief_claim"])

    # TTFR separation: ttfr_p field structurally barred
    try:
        _store.append_jsonl(_store.TTFR_G_RECORDS_JSONL, {"record_type": "ttfr_g", "ttfr_p": 1})
        tg_ok = False
    except _store.GatewaySupportError:
        tg_ok = True
    chk("TTFR separation: store bars ttfr_p / combined_metric / kpi (F-17)", tg_ok)

    # withdrawal path: each cause halts
    halts = True
    for cause in ("consent_withdrawn", "approval_revoked", "verification_lost"):
        mem[str(_store.WITHDRAWAL_RECORDS_JSONL)] = []
        wd.record_withdrawal(bottleneck_id=c["bottleneck_id"], cause=cause, withdrawn_by="a")
        halts = halts and not ex.two_keys_present(c["candidate_id"])[0]
    chk("withdrawal path: any key lost halts support (F-18)", halts)

    # B-1 regression (F-18): a later withdrawal must NOT retroactively invalidate
    # a past valid execution. A withdrawal is present in `mem` from the loop above,
    # yet the already-persisted execution must remain valid (0 violations).
    chk("withdrawal does not invalidate past valid execution (F-18; B-1)",
        not ex.check_invariants())

    # memory integrity: episode-unit, no gateway identity, append-only
    mem[str(_store.WITHDRAWAL_RECORDS_JSONL)] = []
    mb.build()
    chk("memory integrity: no gateway identity / profiling (F-19)",
        all("gateway_ref" not in m and m["links_no_actor"] for m in mb.list_memory()))

    return results


def run_audit() -> dict[str, Any]:
    static_v = static_violations()
    dyn = dynamic_boundary_checks()
    dyn_failures = [name for name, ok in dyn if not ok]
    return {
        "static_violations": static_v,
        "dynamic_checks": dyn,
        "dynamic_failures": dyn_failures,
        "passed": not static_v and not dyn_failures,
    }


def main() -> None:
    print("=" * 64)
    print("GATEWAY SUPPORT STACK AUDIT (F-20)")
    print("=" * 64)
    r = run_audit()
    print(f"  static invariant violations (persisted stores): {len(r['static_violations'])}")
    for v in r["static_violations"]:
        print(f"    - {v}")
    print("  dynamic boundary checks (in-memory end-to-end):")
    for name, ok in r["dynamic_checks"]:
        print(f"    {'✓' if ok else '✗'} {name}")
    print("-" * 64)
    print("  RESULT:", "PASS ✓" if r["passed"] else f"FAIL ✗ ({r['dynamic_failures']})")
    print("Person domain sealed. Gateway support only. AI proposes; humans decide.")


if __name__ == "__main__":
    main()
