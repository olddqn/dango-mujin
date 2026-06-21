"""
findability_audit.py — Route A audit (consumed by the shared edge audit).

Static invariant checks over Route A stores + a forbidden-field/person-data scan,
plus a dynamic in-memory check of the Route A boundaries (observation only, no
outreach, discovery≠consent gap, no remediation). Exposes run_audit() with the
same shape the shared edge audit expects.
"""

from __future__ import annotations

import importlib
from typing import Any

from bridge.edge_runtime import store as _es
from . import (findability_surface_builder as fsb,
               consent_opportunity_builder as cob,
               state_reconciliation_builder as srb)
from ..store import (SURFACES_JSONL, CONSENT_OPPORTUNITIES_JSONL,
                     STATE_RECONCILIATIONS_JSONL)


def static_violations() -> list[str]:
    out: list[str] = []
    out += fsb.check_invariants()
    out += cob.check_invariants()
    out += srb.check_invariants()
    for p in (SURFACES_JSONL, CONSENT_OPPORTUNITIES_JSONL, STATE_RECONCILIATIONS_JSONL):
        for r in _es.read_jsonl(p):
            for f in _es.FORBIDDEN_FIELDS:
                if f in r:
                    out.append(f"{p.name}: forbidden field {f}")
            for hit in _es.scan_person_data(r):
                out.append(f"{p.name}: possible person data ({hit})")
    return out


def dynamic_boundary_checks() -> list[tuple[str, bool]]:
    eb = importlib.reload(importlib.import_module("bridge.edge_runtime.runtime.edge_builder"))
    em = importlib.reload(importlib.import_module("bridge.edge_runtime.runtime.edge_memory"))
    fb = importlib.reload(fsb); co = importlib.reload(cob); sr = importlib.reload(srb)
    mem: dict[str, list[dict[str, Any]]] = {}

    def mread(p): return [dict(r) for r in mem.get(str(p), [])]

    def mappend(p, rec):
        for f in _es.FORBIDDEN_FIELDS:
            if f in rec:
                raise _es.EdgeRuntimeError(f)
        if "record_type" in rec and _es.missing_base_invariants(rec):
            raise _es.EdgeRuntimeError("base")
        if _es.scan_person_data(rec):
            raise _es.EdgeRuntimeError("pd")
        rec = dict(rec); rec.setdefault("appended_at", "t"); rec["event_hash"] = "h"
        mem.setdefault(str(p), []).append(rec); return rec

    def mnext(prefix, p): return f"{prefix}-{len(mem.get(str(p), [])) + 1:03d}"
    for m in (eb, em, fb, co, sr):
        m.append_jsonl = mappend; m.read_jsonl = mread; m.next_id = mnext

    results: list[tuple[str, bool]] = []

    def chk(n, c): results.append((n, bool(c)))

    e = eb.record_observed_edge("voice-sim", "GW")
    # surface requires publicly observable; else held
    try:
        fb.make_surface(e["edge_id"], "public_website", "https://x.test", "rev", False)
        held = False
    except ValueError:
        held = True
    chk("findability surface held when not publicly observable (F-1.5)", held)

    s = fb.record_surface(edge_id=e["edge_id"], surface_type="donation_page",
                          public_source_url="https://x.test/donate", verified_by="rev",
                          publicly_observable=True)
    chk("surface observation-only, no outreach, owner→Mujin (F-21)",
        s["is_observation_only"] and s["no_outreach"] and s["direction_owner_to_mujin"]
        and not fb.check_invariants())

    o = co.record_opportunity(s["surface_id"])
    chk("consent opportunity preserves discovery≠consent gap, no pre-exposure (F-22)",
        o["preserves_discovery_consent_gap"] and o["enables_not_compels"]
        and o["no_pre_exposure"] and not co.check_invariants())

    r = sr.record_reconciliation(edge_id=e["edge_id"], designed_state="person_data_zero_door",
                                 actual_state="dev_repo_public", divergence="large",
                                 exposure_is_benign=True, recorded_by="rev")
    chk("state reconciliation performs no remediation, requires approval (F-24)",
        r["performs_no_remediation"] and r["remediation_requires_human_approval"]
        and not sr.check_invariants())

    chk("Route A episodes recorded in SHARED edge memory, no actor identity (F-19)",
        len(em.list_memory("findability")) == 3
        and all("gateway_ref" not in m for m in em.list_memory("findability")))
    return results


def run_audit() -> dict[str, Any]:
    sv = static_violations()
    dyn = dynamic_boundary_checks()
    failures = [n for n, ok in dyn if not ok]
    return {"static_violations": sv, "dynamic_checks": dyn,
            "dynamic_failures": failures, "passed": not sv and not failures}


def main() -> None:
    print("=" * 64)
    print("ROUTE A (FINDABILITY) AUDIT")
    print("=" * 64)
    r = run_audit()
    print(f"  static violations: {len(r['static_violations'])}")
    for v in r["static_violations"]:
        print(f"    - {v}")
    for n, ok in r["dynamic_checks"]:
        print(f"    {'✓' if ok else '✗'} {n}")
    print("  RESULT:", "PASS ✓" if r["passed"] else f"FAIL ✗ ({r['dynamic_failures']})")


if __name__ == "__main__":
    main()
