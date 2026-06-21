"""
cli.py — Gateway Support Runtime CLI.

Thin command surface over the runtime builders (F-9..F-20). Every command that
would advance the pipeline requires explicit human-provided arguments; nothing
is automatic, nothing is fabricated, and 0 records is always a valid state.

Usage:
  python -m bridge.gateway_support.cli <command> [args]

Commands:
  verify-bottleneck   record a verified bottleneck (all 4 F-11 conditions required)
  build-candidates    derive possibility-only candidates from verified bottlenecks
  approve             permit/block a candidate (gatekeeping only)
  consent             record obtained gateway Resource Acceptance consent
  execute             execute a candidate (requires permit ∧ consent; never auto)
  feedback            record observation-only reality feedback
  ttfr-g              build TTFR-G records from observed relief
  withdraw            halt support (consent_withdrawn|approval_revoked|verification_lost)
  build-memory        append episode memory (no gateway identity)
  report              write reports/gateway_support_report.md
  audit               run the Gateway Support Stack Audit (F-20)
"""

from __future__ import annotations

import sys

from .runtime import (bottleneck_builder, support_candidate_builder, approval_builder,
                      consent_builder, execution_builder, feedback_builder, ttfr_g_builder,
                      withdrawal_builder, memory_builder, report_builder, stack_audit)

COMMANDS = {
    "verify-bottleneck": bottleneck_builder.main,
    "build-candidates": support_candidate_builder.main,
    "approve": approval_builder.main,
    "consent": consent_builder.main,
    "execute": execution_builder.main,
    "feedback": feedback_builder.main,
    "ttfr-g": ttfr_g_builder.main,
    "withdraw": withdrawal_builder.main,
    "build-memory": memory_builder.main,
    "report": report_builder.main,
    "audit": stack_audit.main,
}


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(__doc__)
        return 0
    cmd = argv[0]
    fn = COMMANDS.get(cmd)
    if fn is None:
        print(f"unknown command: {cmd}\n")
        print(__doc__)
        return 2
    fn()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
