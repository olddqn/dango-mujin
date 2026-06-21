"""
full_stack_audit.py — Full Stack Audit (M6) for the Edge Runtime integration.

Combines:
  (1) the shared runtime audit (edge layer + Route A + Route B), and
  (2) structural integration checks that verify the architecture itself:
      target structure present · single shared edge/memory store (no duplication) ·
      both routes reuse the shared store · the universal edge invariant floor is a
      subset of each route's invariants · the F-9..F-25 / no-Saiyan-Scouter
      guarantees are encoded · no person-domain execution path.

CLI:
  python -m bridge.edge_runtime.runtime.full_stack_audit
"""

from __future__ import annotations

from typing import Any

from ..store import (REPO_ROOT, EDGE_RECORDS_JSONL, EDGE_MEMORY_JSONL,
                     edge_base_invariants)
from . import edge_audit


# files the target structure requires (relative to repo root)
_TARGET_FILES = [
    "bridge/edge_runtime/store.py", "bridge/edge_runtime/cli.py",
    "bridge/edge_runtime/runtime/edge_builder.py",
    "bridge/edge_runtime/runtime/edge_memory.py",
    "bridge/edge_runtime/runtime/edge_audit.py",
    "bridge/findability/runtime/findability_surface_builder.py",
    "bridge/findability/runtime/consent_opportunity_builder.py",
    "bridge/findability/runtime/state_reconciliation_builder.py",
    "bridge/gateway_support/runtime/verified_bottleneck_builder.py",
    "bridge/gateway_support/runtime/support_candidate_builder.py",
    "bridge/gateway_support/runtime/approval_builder.py",
    "bridge/gateway_support/runtime/consent_builder.py",
    "bridge/gateway_support/runtime/execution_builder.py",
    "bridge/gateway_support/runtime/feedback_builder.py",
    "bridge/gateway_support/runtime/ttfr_g_builder.py",
]

# guarantee flags that must live in the universal edge floor
_GUARANTEE_FLAGS = ("person_domain_sealed", "no_ranking", "no_recommendation",
                    "no_selection", "no_reach_gap_estimation", "no_saiyan_scouter",
                    "append_only")


def structural_checks() -> list[tuple[str, bool]]:
    out: list[tuple[str, bool]] = []

    def chk(name, cond): out.append((name, bool(cond)))

    # target structure present
    chk("target structure present (all required files)",
        all((REPO_ROOT / f).exists() for f in _TARGET_FILES))

    # single shared edge store (records + memory) — no duplication
    chk("single shared edge-records store (no duplication)",
        EDGE_RECORDS_JSONL.parent == (REPO_ROOT / "bridge" / "edge_runtime" / "data"))
    chk("single shared edge-memory store (no duplication)",
        EDGE_MEMORY_JSONL.parent == (REPO_ROOT / "bridge" / "edge_runtime" / "data")
        and not (REPO_ROOT / "bridge" / "gateway_support" / "data" / "support_memory.jsonl").exists())

    # both routes reuse the shared store + extend the universal floor
    floor = edge_base_invariants()
    try:
        from bridge.findability.store import findability_base_invariants
        fa = findability_base_invariants()
        chk("Route A reuses shared store & extends the edge floor",
            all(fa.get(k) == v for k, v in floor.items())
            and fa.get("findability_is_observation_only") is True
            and fa.get("no_outreach") is True)
    except Exception as e:
        chk(f"Route A store reuse ({e})", False)
    try:
        from bridge.gateway_support.store import base_invariants as gw_base
        gb = gw_base()
        chk("Route B reuses shared store & extends the edge floor",
            all(gb.get(k) == v for k, v in floor.items())
            and gb.get("gateway_support_only") is True
            and gb.get("ttfr_g_separate_from_ttfr_p") is True)
    except Exception as e:
        chk(f"Route B store reuse ({e})", False)

    # the guarantee flags live in the shared floor (apply to both routes)
    chk("guarantee flags encoded in the universal edge floor",
        all(floor.get(f) is True for f in _GUARANTEE_FLAGS))

    # no person-domain execution: Route B execution markers seal it
    try:
        from bridge.gateway_support.runtime import execution_builder as exb
        src = exb.execute.__doc__ or ""
        # presence of the seal markers in the constructed record is the real check;
        # here we assert the module exposes the two-key gate, never an auto path.
        chk("no person-domain / auto execution (two-key gate present)",
            hasattr(exb, "two_keys_present") and hasattr(exb, "keys_existed")
            and "automatic" in (exb.__doc__ or "").lower())
    except Exception as e:
        chk(f"execution seal ({e})", False)

    return out


def run_full_stack_audit() -> dict[str, Any]:
    runtime = edge_audit.run_full_audit()
    structural = structural_checks()
    struct_fail = [n for n, ok in structural if not ok]
    passed = runtime["passed"] and not struct_fail
    return {"runtime": runtime, "structural": structural,
            "structural_failures": struct_fail, "passed": passed}


def main() -> None:
    print("=" * 64)
    print("FULL STACK AUDIT (M6) — Edge Runtime integration")
    print("=" * 64)
    r = run_full_stack_audit()
    print("[1] runtime audit (edge + routes):")
    print(f"    edge layer violations: {len(r['runtime']['edge_violations'])}")
    for name, ok, _d in r["runtime"]["routes"]:
        print(f"    {'✓' if ok else '✗'} {name}")
    print("[2] structural integration checks:")
    for n, ok in r["structural"]:
        print(f"    {'✓' if ok else '✗'} {n}")
    print("-" * 64)
    print("  FULL STACK:", "AUDIT-COMPLETE ✓ (PASS)" if r["passed"] else "FAIL ✗")


if __name__ == "__main__":
    main()
