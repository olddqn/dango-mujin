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
from bridge.edge_runtime.runtime import edge_builder, edge_memory
from . import (verified_bottleneck_builder, support_candidate_builder, approval_builder,
               consent_builder, execution_builder, feedback_builder, ttfr_g_builder,
               withdrawal_builder, memory_builder)


# ── (1) static checks over persisted stores ─────────────────────────────────

def static_violations() -> list[str]:
    out: list[str] = []
    out += verified_bottleneck_builder.check_invariants()
    out += support_candidate_builder.check_invariants()
    out += approval_builder.check_invariants()
    out += consent_builder.check_invariants()
    out += execution_builder.check_invariants()
    out += feedback_builder.check_invariants()
    out += ttfr_g_builder.check_invariants()
    out += withdrawal_builder.check_invariants()
    out += memory_builder.check_invariants()   # delegates to shared edge memory
    # structural scan: no Route B record may carry a forbidden field or person data
    from ..store import (read_jsonl, scan_person_data, FORBIDDEN_FIELDS,
                         VERIFIED_BOTTLENECKS_JSONL, SUPPORT_CANDIDATES_JSONL,
                         APPROVAL_RECORDS_JSONL, GATEWAY_CONSENTS_JSONL,
                         SUPPORT_EXECUTIONS_JSONL, SUPPORT_FEEDBACK_JSONL,
                         TTFR_G_RECORDS_JSONL, WITHDRAWAL_RECORDS_JSONL)
    for p in (VERIFIED_BOTTLENECKS_JSONL, SUPPORT_CANDIDATES_JSONL,
              APPROVAL_RECORDS_JSONL, GATEWAY_CONSENTS_JSONL, SUPPORT_EXECUTIONS_JSONL,
              SUPPORT_FEEDBACK_JSONL, TTFR_G_RECORDS_JSONL, WITHDRAWAL_RECORDS_JSONL):
        for r in read_jsonl(p):
            for f in FORBIDDEN_FIELDS:
                if f in r:
                    out.append(f"{p.name}: record carries forbidden field {f}")
            for hit in scan_person_data(r):       # B-6: no person data in persisted records
                out.append(f"{p.name}: possible person data ({hit})")
    return out


# ── (2) dynamic end-to-end boundary simulation (in-memory, never persisted) ──

def _patched_modules():
    """Fresh module objects with in-memory persistence (canonical stores untouched).
    Edge modules are reloaded first so the gateway builders rebind their edge
    imports (get_edge / edge_memory) to the patched edge runtime."""
    edge_mods = [importlib.reload(m) for m in (edge_builder, edge_memory)]
    gw_mods = [importlib.reload(m) for m in (
        verified_bottleneck_builder, support_candidate_builder, approval_builder,
        consent_builder, execution_builder, feedback_builder, ttfr_g_builder,
        withdrawal_builder, memory_builder)]
    mem: dict[str, list[dict[str, Any]]] = {}

    def mread(p): return [dict(r) for r in mem.get(str(p), [])]

    def mappend(p, rec):
        for f in _store.FORBIDDEN_FIELDS:
            if f in rec:
                raise _store.GatewaySupportError(f"forbidden field {f}")
        if "record_type" in rec and _store.missing_base_invariants(rec):
            raise _store.GatewaySupportError("missing base invariants")
        if _store.scan_person_data(rec):
            raise _store.GatewaySupportError("person data")
        rec = dict(rec)
        rec.setdefault("appended_at", "t")
        rec["event_hash"] = "h"
        mem.setdefault(str(p), []).append(rec)
        return rec

    def mnext(prefix, p): return f"{prefix}-{len(mem.get(str(p), [])) + 1:03d}"

    for m in edge_mods + gw_mods:
        m.append_jsonl = mappend
        m.read_jsonl = mread
        m.next_id = mnext
    eb, em = edge_mods
    return (eb, em, *gw_mods), mem


def dynamic_boundary_checks() -> list[tuple[str, bool]]:
    (eb, em, bb, cb, ap, co, ex, fb, tg, wd, mb), mem = _patched_modules()
    results: list[tuple[str, bool]] = []

    def chk(name, cond): results.append((name, bool(cond)))

    # shared edge: Route B consumes an Observed Edge (not a duplicated edge concept)
    edge = eb.record_observed_edge("voice-sim", "X")
    eid = edge["edge_id"]
    chk("Route B consumes a shared Observed Edge", bool(eid) and not eb.check_invariants())

    # candidate boundary: held verification raises; candidates plural/unordered/no-rank; no fabrication
    try:
        bb.make_verified_bottleneck(edge_id=eid, gateway_ref="X",
            public_source_url="u", bottleneck_kind="k", accepted_support_forms=["a"],
            verified_by="r", self_stated=True, public=True, currently_observable=False,
            inference_free=True)
        held_ok = False
    except ValueError:
        held_ok = True
    chk("verification held when condition missing (F-11)", held_ok)

    b = bb.record_verified_bottleneck(edge_id=eid, gateway_ref="X",
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

    # B-4: persistence boundary enforces base invariants (pure helper, no write)
    chk("store enforces base invariants at persistence boundary (B-4)",
        bool(_store.missing_base_invariants({"record_type": "x"})) and
        not _store.missing_base_invariants({"record_type": "x", **_store.base_invariants()}))

    # B-6: person-data guard detects email/phone in free text; clean text passes
    chk("store detects person data in free text (B-6)",
        bool(_store.scan_person_data({"reason": "contact a@b.com"})) and
        bool(_store.scan_person_data({"phone": "09012345678"})) and
        not _store.scan_person_data({"reason": "email confirmation from the gateway",
                                     "source_url": "https://x.test/a?id=123"}))

    # B-5: type-level learning is non-KPI annotated (no maximization / person-relief accounting)
    learn = mb.learn_support_pattern_types()
    chk("memory learning is non-KPI, not person-relief accounting (B-5)",
        learn.get("not_a_kpi") is True and learn.get("no_maximization") is True
        and learn.get("not_person_relief_accounting") is True)

    # B-3: TTFR-G clock inversion is held, never persisted as a negative interval
    mem[str(_store.SUPPORT_EXECUTIONS_JSONL)] = [
        {"execution_id": "ex-inv", "bottleneck_id": "b", "edge_observed_at": "2026-06-21T00:00:00Z"}]
    mem[str(_store.SUPPORT_FEEDBACK_JSONL)] = [
        {"feedback_id": "fb-inv", "execution_id": "ex-inv", "relief_observed": True,
         "observed_at": "2026-06-20T00:00:00Z"}]
    mem[str(_store.TTFR_G_RECORDS_JSONL)] = []
    inv = tg.build()
    chk("TTFR-G clock inversion held, not negative (B-3)",
        len(inv) == 1 and inv[0]["status"] == "held_clock_inversion"
        and inv[0]["ttfr_g_seconds"] is None)

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
