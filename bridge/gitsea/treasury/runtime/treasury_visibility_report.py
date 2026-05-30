"""
treasury_visibility_report.py — Treasury Visibility Explanation Report

Generates a human-readable JSON report explaining:
  - The RepoVault exists on Base for olddqn/dango-mujin
  - Treasury is visible from the Dan-Go perspective
  - Dan-Go does not control or move funds
  - Cooperation signals may reference treasury context
  - Economic value remains optional and external

This file does NOT:
  - Execute treasury actions
  - Move funds
  - Allocate rewards
  - Connect to any network
  - Call any wallet

Core principles:
  "Dan-Go observes treasury context; it does not operate the treasury."
  "Signal is not reward."

No secrets. No private keys. No wallet operations. No network. stdlib only.

Usage:
    python bridge/gitsea/treasury/runtime/treasury_visibility_report.py
    python bridge/gitsea/treasury/runtime/treasury_visibility_report.py --save
    python bridge/gitsea/treasury/runtime/treasury_visibility_report.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_FILE_DIR = Path(__file__).parent
_TREASURY = _FILE_DIR.parent
_EXAMPLES = _TREASURY / "examples"


# ── Report sections ───────────────────────────────────────────────────────────

VISIBILITY_SECTIONS = [
    {
        "section":   "RepoVault Exists",
        "summary":   "The GITSEA RepoVault for olddqn/dango-mujin is live on Base.",
        "detail": (
            "The RepoVault contract (0x3F9c96A429697B458Fe0a16502A050E5AB50bB00) was "
            "registered via the GITSEA 'Link on Base' UI. The RepoLinked event confirmed "
            "successful on-chain registration. The repository owner executed this "
            "transaction from their own wallet via MetaMask. Dan-Go did not execute it."
        ),
        "dango_action": "observe",
        "economic_action": False,
    },
    {
        "section":   "Treasury Is Visible",
        "summary":   "Dan-Go can reference the treasury address for cooperation context.",
        "detail": (
            "Treasury visibility means the RepoVault address and repo_id are recorded "
            "in Dan-Go advisory snapshots. This allows cooperation signals to reference "
            "treasury context without triggering economic actions. Visibility ≠ control."
        ),
        "dango_action": "observe",
        "economic_action": False,
    },
    {
        "section":   "Dan-Go Does Not Control Funds",
        "summary":   "Dan-Go has no signing authority over the RepoVault.",
        "detail": (
            "The RepoVault is a GITSEA smart contract. It is NOT a user wallet. "
            "Dan-Go does not hold any private key that could operate it. "
            "Dan-Go does not call the RepoVault contract. Dan-Go does not withdraw, "
            "stake, or distribute from it. All economic operations require the "
            "owner wallet (0x89b38ff776565f095b3cd46C5f35EAb27506417C) via GITSEA UI."
        ),
        "dango_action": "none",
        "economic_action": False,
    },
    {
        "section":   "Cooperation Signals Reference Treasury Context",
        "summary":   "Phase 9 cooperation signals are linked to the treasury for legibility.",
        "detail": (
            "The cooperation_treasury_bridge.py module links Phase 9 cooperation signals "
            "(participation patterns, event coverage, diversity) to the treasury address "
            "for context. This makes it visible that the negotiation history and the "
            "on-chain treasury belong to the same repository. Signal is not reward. "
            "No allocation is triggered. The recommended_allocation field is always null."
        ),
        "dango_action": "link_context",
        "economic_action": False,
    },
    {
        "section":   "Economic Value Remains Optional",
        "summary":   "Whether cooperation signals translate to economic value is GITSEA's decision.",
        "detail": (
            "GITSEA may read cooperation context when determining stream eligibility. "
            "Dan-Go does not push signals to GITSEA. Dan-Go does not activate streams. "
            "Economic value is optional: a high cooperation signal does not guarantee "
            "a stream event. A low signal does not block one. "
            "Dan-Go records cooperation before value emerges."
        ),
        "dango_action": "observe",
        "economic_action": False,
    },
]


# ── Report builder ────────────────────────────────────────────────────────────

def build_visibility_report() -> dict:
    return {
        "report_type":       "treasury_visibility_report",
        "generated_at":      datetime.now(timezone.utc).isoformat(),

        # Treasury identity
        "repo":              "olddqn/dango-mujin",
        "chain":             "Base",
        "repovault_address": "0x3F9c96A429697B458Fe0a16502A050E5AB50bB00",
        "owner_wallet":      "0x89b38ff776565f095b3cd46C5f35EAb27506417C",

        # Report content
        "section_count":     len(VISIBILITY_SECTIONS),
        "sections":          VISIBILITY_SECTIONS,

        # Summary table
        "summary_table": {
            "repovault_exists":           True,
            "treasury_visible":           True,
            "dango_controls_funds":       False,
            "dango_executes_actions":     False,
            "cooperation_signals_linked": True,
            "economic_value_automatic":   False,
            "recommended_allocation":     None,
        },

        # Invariants
        "moves_money":       False,
        "execution_allowed": False,
        "hard_enforcement":  False,
        "advisory":          True,
        "authority":         "none",
        "append_only":       True,

        # Required phrases
        "principle_1": "Dan-Go observes treasury context; it does not operate the treasury.",
        "principle_2": "Signal is not reward.",
        "principle_3": "Contribution becomes legible before it becomes valuable.",
    }


# ── Save ──────────────────────────────────────────────────────────────────────

def save_report(report: dict, out_path: Path | None = None) -> Path:
    if out_path is None:
        out_path = _EXAMPLES / "treasury-visibility-report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Generate a treasury visibility explanation report.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Dan-Go observes treasury context; it does not operate the treasury.
Signal is not reward.

Examples:
  python bridge/gitsea/treasury/runtime/treasury_visibility_report.py
  python bridge/gitsea/treasury/runtime/treasury_visibility_report.py --save
  python bridge/gitsea/treasury/runtime/treasury_visibility_report.py --json
        """,
    )
    p.add_argument("--save", action="store_true",
                   help="Save to treasury/examples/treasury-visibility-report.json")
    p.add_argument("--json", action="store_true", dest="json_output")
    args = p.parse_args()

    report = build_visibility_report()

    if args.save:
        out = save_report(report)
        print(f"Saved: {out}")

    if args.json_output:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    # Default: human-readable
    print(f"\n{'='*60}")
    print(f"  Treasury Visibility Report: {report['repo']}")
    print(f"{'='*60}")
    print(f"  RepoVault: {report['repovault_address']}")
    print(f"  Chain:     {report['chain']}")
    print()
    for sec in report["sections"]:
        print(f"  ▶  {sec['section']}")
        print(f"     {sec['summary']}")
        print()
    st = report["summary_table"]
    print(f"  Summary:")
    print(f"    RepoVault exists:           {st['repovault_exists']}")
    print(f"    Treasury visible:           {st['treasury_visible']}")
    print(f"    Dan-Go controls funds:      {st['dango_controls_funds']}")
    print(f"    Dan-Go executes actions:    {st['dango_executes_actions']}")
    print(f"    Cooperation signals linked: {st['cooperation_signals_linked']}")
    print(f"    Economic value automatic:   {st['economic_value_automatic']}")
    print(f"    Recommended allocation:     {st['recommended_allocation']!r}")
    print(f"\n  moves_money:       {report['moves_money']}")
    print(f"  execution_allowed: {report['execution_allowed']}")
    print(f"  advisory:          {report['advisory']}")
    print(f"  authority:         {report['authority']}")
    print(f"\n  \"{report['principle_1']}\"")
    print(f"  \"{report['principle_2']}\"")
    print()


if __name__ == "__main__":
    main()
