"""
cooperation_treasury_bridge.py — Connect Cooperation Signals to Treasury Visibility

Reads Phase 9 cooperation signals and connects them to the observed
GITSEA RepoVault treasury context for olddqn/dango-mujin.

This file does NOT:
  - Allocate rewards
  - Distribute tokens
  - Move funds
  - Execute treasury actions
  - Score participants for payouts
  - Perform any on-chain operation

The bridge makes cooperation context and treasury visibility legible together.
It does NOT make cooperation signals into reward signals.

Core principles:
  "Signal is not reward."
  "Dan-Go observes treasury context; it does not operate the treasury."

No secrets. No private keys. No wallet operations. No network. stdlib only.

Usage:
    python bridge/gitsea/treasury/runtime/cooperation_treasury_bridge.py
    python bridge/gitsea/treasury/runtime/cooperation_treasury_bridge.py --save
    python bridge/gitsea/treasury/runtime/cooperation_treasury_bridge.py --json
    python bridge/gitsea/treasury/runtime/cooperation_treasury_bridge.py \\
        --input bridge/gitsea/lifecycle/examples/contribution-signal.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_FILE_DIR    = Path(__file__).parent
_TREASURY    = _FILE_DIR.parent
_EXAMPLES    = _TREASURY / "examples"
_REPO_ROOT   = _TREASURY.parent.parent.parent
_LC_EXAMPLES = _REPO_ROOT / "bridge" / "gitsea" / "lifecycle" / "examples"

# Known treasury facts
REPOVAULT_ADDRESS = "0x3F9c96A429697B458Fe0a16502A050E5AB50bB00"
REPO_ID           = "B93829F8829E2FFD13EF10ABA0B8442233BCF80172321B951C50E2E0C4C30D08"


# ── Bridge builder ────────────────────────────────────────────────────────────

def build_cooperation_treasury_bridge(
    issue_id: int,
    claim_id: str,
    cooperation_signal: float,
    dissent_present: bool,
    participants: list[str],
    event_count: int,
    events: dict[str, int] | None = None,
) -> dict[str, Any]:
    """
    Connect a cooperation evaluation to treasury visibility context.

    The cooperation signal is advisory. It does not trigger any treasury action.
    The treasury address is visible for context. Dan-Go does not operate it.

    Parameters
    ----------
    issue_id : int
        GitHub issue number.
    claim_id : str
        Dan-Go claim identifier.
    cooperation_signal : float
        Advisory cooperation signal (0.0–1.0) from contribution_evaluator.py.
    dissent_present : bool
        Whether any contest events occurred (healthy negotiation indicator).
    participants : list[str]
        Pseudonymous participant list.
    event_count : int
        Total negotiation events observed.
    events : dict | None
        Event type counts (optional, for detail).
    """
    return {
        "bridge_type":        "cooperation_treasury_bridge",
        "generated_at":       datetime.now(timezone.utc).isoformat(),

        # Cooperation context (from Phase 9)
        "issue_id":           issue_id,
        "claim_id":           claim_id,
        "cooperation_signal": cooperation_signal,
        "dissent_present":    dissent_present,
        "participants":       participants,
        "participant_count":  len(participants),
        "event_count":        event_count,
        "events":             events or {},

        # Treasury visibility (from Phase 10 / observed on-chain)
        "treasury_address":   REPOVAULT_ADDRESS,
        "repo_id":            REPO_ID,
        "treasury_visible":   True,
        "treasury_linked":    True,
        "chain":              "Base",

        # What this bridge does NOT do
        "recommended_allocation": None,   # always null — never allocated
        "economic_action":        False,
        "signal_becomes_reward":  False,
        "treasury_operated":      False,

        # Invariants
        "moves_money":        False,
        "execution_allowed":  False,
        "hard_enforcement":   False,
        "advisory":           True,
        "authority":          "none",
        "append_only":        True,
        "contestable":        True,
        "reopenable":         True,

        # Required phrases
        "signal_note":        "Signal is not reward.",
        "treasury_note": (
            "Dan-Go observes treasury context; it does not operate the treasury. "
            "The RepoVault address is visible for cooperation history context. "
            "No funds are allocated or moved by this bridge record."
        ),
        "principle": (
            "Cooperation signals make contribution legible. "
            "Treasury visibility makes economic context legible. "
            "Neither action moves money. "
            "Signal is not reward."
        ),
    }


# ── Load from Phase 9 output ──────────────────────────────────────────────────

def load_cooperation_signal(path: Path) -> dict[str, Any]:
    """Load a contribution-signal.json from Phase 9 lifecycle examples."""
    if not path.exists():
        # Default stub for housing-007
        return {
            "claim_id":          "housing-007",
            "issue_id":          1,
            "cooperation_signal": 0.88,
            "participant_count": 3,
            "participants":      ["alice", "bob", "carol"],
            "total_events":      6,
            "events": {
                "evidence": 2, "contest": 1, "reaffirm": 1,
                "pr_submitted": 1, "pr_merged": 1,
            },
            "healthy_negotiation": {"dissent_present": True, "contest_count": 1},
        }
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ── Save ──────────────────────────────────────────────────────────────────────

def save_bridge(doc: dict, out_path: Path | None = None) -> Path:
    if out_path is None:
        out_path = _EXAMPLES / "cooperation-treasury-bridge.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Connect cooperation signals to treasury visibility.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Signal is not reward.
Dan-Go observes treasury context; it does not operate the treasury.

Reads: bridge/gitsea/lifecycle/examples/contribution-signal.json
Connects to: RepoVault 0x3F9c96A429697B458Fe0a16502A050E5AB50bB00 (Base)

Examples:
  python bridge/gitsea/treasury/runtime/cooperation_treasury_bridge.py
  python bridge/gitsea/treasury/runtime/cooperation_treasury_bridge.py --save
  python bridge/gitsea/treasury/runtime/cooperation_treasury_bridge.py --json
  python bridge/gitsea/treasury/runtime/cooperation_treasury_bridge.py \\
      --input bridge/gitsea/lifecycle/examples/contribution-signal.json
        """,
    )
    p.add_argument("--input", metavar="PATH",
                   help="Path to contribution-signal.json")
    p.add_argument("--save", action="store_true",
                   help="Save to treasury/examples/cooperation-treasury-bridge.json")
    p.add_argument("--json", action="store_true", dest="json_output")
    args = p.parse_args()

    signal_path = (
        Path(args.input) if args.input
        else _LC_EXAMPLES / "contribution-signal.json"
    )
    cs = load_cooperation_signal(signal_path)

    hn = cs.get("healthy_negotiation", {})
    doc = build_cooperation_treasury_bridge(
        issue_id=cs.get("issue_id", 1),
        claim_id=cs.get("claim_id", "housing-007"),
        cooperation_signal=cs.get("cooperation_signal", 0.0),
        dissent_present=hn.get("dissent_present", False),
        participants=cs.get("participants", []),
        event_count=cs.get("total_events", 0),
        events=cs.get("events"),
    )

    if args.save:
        out = save_bridge(doc)
        print(f"Saved: {out}")

    if args.json_output:
        print(json.dumps(doc, indent=2, ensure_ascii=False))
        return

    # Default: human-readable
    print(f"\n{'='*60}")
    print(f"  Cooperation → Treasury Bridge: {doc['claim_id']}")
    print(f"{'='*60}")
    print(f"  Issue:              #{doc['issue_id']}")
    print(f"  Participants:       {', '.join(doc['participants'])}")
    print(f"  Total events:       {doc['event_count']}")
    print(f"  Cooperation signal: {doc['cooperation_signal']}  (advisory)")
    print(f"  Dissent present:    {'✓ (healthy)' if doc['dissent_present'] else '○ none'}")
    print(f"\n  Treasury address:   {doc['treasury_address']}")
    print(f"  Chain:              {doc['chain']}")
    print(f"  Treasury visible:   {doc['treasury_visible']}")
    print(f"\n  Recommended allocation: {doc['recommended_allocation']!r}  (always null)")
    print(f"  Economic action:    {doc['economic_action']}")
    print(f"  Signal → reward:    {doc['signal_becomes_reward']}")
    print(f"  Treasury operated:  {doc['treasury_operated']}")
    print(f"\n  moves_money:        {doc['moves_money']}")
    print(f"  execution_allowed:  {doc['execution_allowed']}")
    print(f"  advisory:           {doc['advisory']}")
    print(f"  authority:          {doc['authority']}")
    print(f"\n  \"{doc['signal_note']}\"")
    print()


if __name__ == "__main__":
    main()
