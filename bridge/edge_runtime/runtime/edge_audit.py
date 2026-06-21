"""
edge_audit.py — Shared edge audit (foundation; routes wired in M4).

Audits the shared edge layer (edge records + edge memory): base invariants,
structural forbidden-field scan, and person-data scan over the edge stores.
The cross-route harness (run_full_audit) additionally invokes each route's own
audit if present, so Route A and Route B share one audit entry point.
"""

from __future__ import annotations

from typing import Any, Callable

from ..store import (read_jsonl, scan_person_data, FORBIDDEN_FIELDS,
                     EDGE_RECORDS_JSONL, EDGE_MEMORY_JSONL)
from . import edge_builder, edge_memory


def edge_static_violations() -> list[str]:
    out: list[str] = []
    out += edge_builder.check_invariants()
    out += edge_memory.check_invariants()
    for p in (EDGE_RECORDS_JSONL, EDGE_MEMORY_JSONL):
        for r in read_jsonl(p):
            for f in FORBIDDEN_FIELDS:
                if f in r:
                    out.append(f"{p.name}: forbidden field {f}")
            for hit in scan_person_data(r):
                out.append(f"{p.name}: possible person data ({hit})")
    return out


# Route audit hooks registered by routes (M4). Each returns (name, passed, detail).
_ROUTE_AUDITS: list[tuple[str, Callable[[], dict[str, Any]]]] = []


def register_route_audit(name: str, fn: Callable[[], dict[str, Any]]) -> None:
    if name not in {n for n, _ in _ROUTE_AUDITS}:
        _ROUTE_AUDITS.append((name, fn))


def _discover_routes() -> None:
    """Lazily import route audits so the shared audit can run them. Safe if a
    route is absent."""
    try:
        from bridge.findability.runtime import findability_audit  # noqa
        register_route_audit("Route A (findability)", findability_audit.run_audit)
    except Exception:
        pass
    try:
        from bridge.gateway_support.runtime import stack_audit  # noqa
        register_route_audit("Route B (gateway_support)", stack_audit.run_audit)
    except Exception:
        pass


def run_full_audit() -> dict[str, Any]:
    _discover_routes()
    edge_v = edge_static_violations()
    routes = []
    for name, fn in _ROUTE_AUDITS:
        try:
            r = fn()
            routes.append((name, bool(r.get("passed")), r))
        except Exception as e:  # an audit that errors is a failure, surfaced
            routes.append((name, False, {"error": str(e)}))
    passed = not edge_v and all(ok for _, ok, _ in routes)
    return {"edge_violations": edge_v, "routes": routes, "passed": passed}


def main() -> None:
    print("=" * 64)
    print("SHARED EDGE AUDIT")
    print("=" * 64)
    r = run_full_audit()
    print(f"  edge layer violations: {len(r['edge_violations'])}")
    for v in r["edge_violations"]:
        print(f"    - {v}")
    for name, ok, _detail in r["routes"]:
        print(f"  {'✓' if ok else '✗'} {name}")
    print("-" * 64)
    print("  RESULT:", "PASS ✓" if r["passed"] else "FAIL ✗")


if __name__ == "__main__":
    main()
