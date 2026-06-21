"""
cli.py — Gateway Support Runtime CLI (F-9..F-20).

Honest command surface (B-2). Commands are explicitly one of three kinds:

  read-only  : show-<layer>, report, audit         (display only, no writes)
  derivation : build-candidates, build-ttfr-g, build-memory
               (deterministic derivation from EXISTING verified records; 0 in -> 0 out)
  action     : verify-bottleneck, approve, consent, execute, feedback, withdraw
               (mutating; require explicit human-provided arguments)

There is NO auto-execution: `execute` is a single explicit invocation that passes
through the two-key gate (PERMIT approval ∧ ACTIVE gateway consent ∧ verified ∧
not withdrawn). Nothing schedules or chains actions. 0 records is always valid.

Usage:
  python -m bridge.gateway_support.cli <command> [options]
  python -m bridge.gateway_support.cli --help
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .store import GatewaySupportError
from .runtime import (verified_bottleneck_builder as bn, support_candidate_builder as sc,
                      approval_builder as ap, consent_builder as co,
                      execution_builder as ex, feedback_builder as fb,
                      ttfr_g_builder as tg, withdrawal_builder as wd,
                      memory_builder as mb, report_builder as rp, stack_audit as sa)

_SHOW = {
    "bottlenecks": bn.list_verified_bottlenecks,
    "candidates": sc.list_candidates,
    "approvals": ap.list_approvals,
    "consents": co.list_consents,
    "executions": ex.list_executions,
    "feedback": fb.list_feedback,
    "ttfr-g": tg.list_ttfr_g,
    "withdrawals": wd.list_withdrawals,
    "memory": mb.list_memory,
}


def _emit(label: str, rec: Any) -> int:
    print(f"{label}:")
    print(json.dumps(rec, ensure_ascii=False, indent=2))
    return 0


def _run_action(fn, label: str) -> int:
    try:
        return _emit(label, fn())
    except (GatewaySupportError, ValueError) as e:
        print(f"refused / held: {e}")
        return 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="gateway_support", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    # read-only
    s = sub.add_parser("show", help="display records of a layer (read-only)")
    s.add_argument("layer", choices=sorted(_SHOW))
    sub.add_parser("report", help="write the gateway support report (read-only of data)")
    sub.add_parser("audit", help="run the Gateway Support Stack Audit (F-20)")

    # derivation (deterministic from existing verified records)
    sub.add_parser("build-candidates", help="derive possibility-only candidates (F-12)")
    sub.add_parser("build-ttfr-g", help="derive TTFR-G records from observed relief (F-17)")
    sub.add_parser("build-memory", help="append episode memory (F-19)")

    # actions (mutating, explicit args)
    a = sub.add_parser("verify-bottleneck", help="record a verified bottleneck (F-11)")
    a.add_argument("--edge-id", required=True, help="a shared Observed Edge id")
    a.add_argument("--gateway-ref", required=True)
    a.add_argument("--public-source-url", required=True)
    a.add_argument("--kind", required=True, help="gateway self-stated bottleneck kind")
    a.add_argument("--accepted-forms", required=True, help="comma-separated, gateway self-stated")
    a.add_argument("--verified-by", required=True, help="named human verifier")
    a.add_argument("--self-stated", action="store_true")
    a.add_argument("--public", action="store_true")
    a.add_argument("--currently-observable", action="store_true")
    a.add_argument("--inference-free", action="store_true")

    a = sub.add_parser("approve", help="permit/block a candidate (gatekeeping only, F-13)")
    a.add_argument("--candidate-id", required=True)
    a.add_argument("--decision", required=True, choices=("permit", "block"))
    a.add_argument("--reviewer", required=True)

    a = sub.add_parser("consent", help="record obtained gateway consent (F-14)")
    a.add_argument("--gateway-ref", required=True)
    a.add_argument("--bottleneck-id", required=True)
    a.add_argument("--support-form", required=True)
    a.add_argument("--consent-source", required=True)
    a.add_argument("--obtained", action="store_true", help="explicit consent obtained (not inferred)")

    a = sub.add_parser("execute", help="execute a candidate (two-key gate; never auto, F-15)")
    a.add_argument("--candidate-id", required=True)
    a.add_argument("--executor", required=True)

    a = sub.add_parser("feedback", help="record observation-only reality feedback (F-16)")
    a.add_argument("--execution-id", required=True)
    a.add_argument("--relief-observed", action="store_true")
    a.add_argument("--relief-source-url", default="")
    a.add_argument("--observed-by", required=True)

    a = sub.add_parser("withdraw", help="halt support (F-18)")
    a.add_argument("--bottleneck-id", required=True)
    a.add_argument("--cause", required=True, choices=wd.CAUSES)
    a.add_argument("--withdrawn-by", required=True)
    a.add_argument("--reason", default="")
    return p


def main(argv: list[str] | None = None) -> int:
    p = build_parser()
    args = p.parse_args(argv if argv is not None else sys.argv[1:])
    cmd = args.cmd

    # read-only
    if cmd == "show":
        return _emit(f"{args.layer} ({len(_SHOW[args.layer]())} records)", _SHOW[args.layer]())
    if cmd == "report":
        rp.main(); return 0
    if cmd == "audit":
        sa.main(); return 0

    # derivation
    if cmd == "build-candidates":
        return _emit("candidates built", sc.build())
    if cmd == "build-ttfr-g":
        return _emit("ttfr-g built", tg.build())
    if cmd == "build-memory":
        return _emit("memory built", mb.build())

    # actions
    if cmd == "verify-bottleneck":
        return _run_action(lambda: bn.record_verified_bottleneck(
            edge_id=args.edge_id, gateway_ref=args.gateway_ref,
            public_source_url=args.public_source_url, bottleneck_kind=args.kind,
            accepted_support_forms=[f.strip() for f in args.accepted_forms.split(",") if f.strip()],
            verified_by=args.verified_by, self_stated=args.self_stated, public=args.public,
            currently_observable=args.currently_observable, inference_free=args.inference_free),
            "verified bottleneck recorded")
    if cmd == "approve":
        return _run_action(lambda: ap.record_approval(args.candidate_id, args.decision, args.reviewer),
                           "approval recorded")
    if cmd == "consent":
        return _run_action(lambda: co.record_gateway_consent(
            gateway_ref=args.gateway_ref, bottleneck_id=args.bottleneck_id,
            support_form=args.support_form, consent_source=args.consent_source,
            obtained=args.obtained), "gateway consent recorded")
    if cmd == "execute":
        return _run_action(lambda: ex.execute(args.candidate_id, args.executor),
                           "support executed")
    if cmd == "feedback":
        return _run_action(lambda: fb.record_feedback(
            execution_id=args.execution_id, relief_observed=args.relief_observed,
            relief_source_url=args.relief_source_url, observed_by=args.observed_by),
            "feedback recorded")
    if cmd == "withdraw":
        return _run_action(lambda: wd.record_withdrawal(
            bottleneck_id=args.bottleneck_id, cause=args.cause,
            withdrawn_by=args.withdrawn_by, reason=args.reason), "withdrawal recorded")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
