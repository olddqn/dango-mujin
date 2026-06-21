"""
cli.py — Edge Runtime CLI (shared entry point).

Honest command surface. Read-only and gated-action commands only; no
auto-execution, no misleading names.

Usage:
  python -m bridge.edge_runtime.cli <command> [options]
"""

from __future__ import annotations

import argparse
import json
import sys

from .store import EdgeRuntimeError
from .runtime import edge_builder, edge_memory, edge_audit, edge_report, full_stack_audit


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="edge_runtime", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("show-edges", help="list observed edges (read-only)")
    sub.add_parser("show-memory", help="list shared edge memory (read-only)")
    sub.add_parser("audit", help="run the shared edge audit (edge + routes)")
    sub.add_parser("full-audit", help="run the full stack audit (runtime + structural)")
    sub.add_parser("report", help="write the shared edge runtime report (both routes)")
    a = sub.add_parser("observe-edge", help="record an observed edge (Voice -> Edge)")
    a.add_argument("--source-voice", required=True)
    a.add_argument("--gateway-ref", required=True)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv if argv is not None else sys.argv[1:])
    if args.cmd == "show-edges":
        print(json.dumps(edge_builder.list_edges(), ensure_ascii=False, indent=2)); return 0
    if args.cmd == "show-memory":
        print(json.dumps(edge_memory.list_memory(), ensure_ascii=False, indent=2)); return 0
    if args.cmd == "audit":
        edge_audit.main(); return 0
    if args.cmd == "full-audit":
        full_stack_audit.main(); return 0
    if args.cmd == "report":
        edge_report.main(); return 0
    if args.cmd == "observe-edge":
        try:
            rec = edge_builder.record_observed_edge(args.source_voice, args.gateway_ref)
            print(json.dumps(rec, ensure_ascii=False, indent=2)); return 0
        except (EdgeRuntimeError, ValueError) as e:
            print(f"refused: {e}"); return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
