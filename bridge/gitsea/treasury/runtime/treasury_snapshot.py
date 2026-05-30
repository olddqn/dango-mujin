"""
treasury_snapshot.py — Static Advisory Snapshot of the GITSEA RepoVault

Creates an advisory snapshot of the known GITSEA RepoVault for
olddqn/dango-mujin on Base. All data is static / locally observed.

This file does NOT:
  - Connect to Base RPC
  - Query any wallet balance
  - Send any transaction
  - Stake tokens
  - Withdraw funds
  - Perform any on-chain operation

The snapshot records observed on-chain facts for treasury visibility.
Treasury visibility ≠ treasury operation.

Core principle:
  "Dan-Go observes treasury context; it does not operate the treasury."

No secrets. No private keys. No wallet operations. No network. stdlib only.

Usage:
    python bridge/gitsea/treasury/runtime/treasury_snapshot.py
    python bridge/gitsea/treasury/runtime/treasury_snapshot.py --save
    python bridge/gitsea/treasury/runtime/treasury_snapshot.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_FILE_DIR  = Path(__file__).parent
_TREASURY  = _FILE_DIR.parent
_EXAMPLES  = _TREASURY / "examples"
_REPO_ROOT = _TREASURY.parent.parent.parent


# ── Known on-chain facts (observed, not queried) ──────────────────────────────
# Source: GITSEA UI + BaseScan observation after "Link on Base" registration.
# Dan-Go did NOT execute this transaction. It was executed via GITSEA UI.

KNOWN_REPOVAULT = {
    "repo":              "olddqn/dango-mujin",
    "chain":             "Base",
    "chain_id":          8453,
    "owner_wallet":      "0x89b38ff776565f095b3cd46C5f35EAb27506417C",
    "repovault_address": "0x3F9c96A429697B458Fe0a16502A050E5AB50bB00",
    "repo_id":           "B93829F8829E2FFD13EF10ABA0B8442233BCF80172321B951C50E2E0C4C30D08",
    "splits_root":       "DA309748EA18E9C8C99B7FC50828251D30EB65EB1817FFF6507EC6AB5895B959",
    "event":             "RepoLinked",
    "observation_status": "linked",
    "source":            "observed_basescan",
}


# ── Snapshot builder ──────────────────────────────────────────────────────────

def build_treasury_snapshot() -> dict:
    """
    Build an advisory treasury snapshot from known on-chain facts.

    The snapshot makes the RepoVault visible in the Dan-Go context.
    It does not grant Dan-Go any control over the treasury.
    """
    return {
        "snapshot_type":     "treasury_snapshot",
        "generated_at":      datetime.now(timezone.utc).isoformat(),

        # Repository identity
        "repo":              KNOWN_REPOVAULT["repo"],
        "chain":             KNOWN_REPOVAULT["chain"],
        "chain_id":          KNOWN_REPOVAULT["chain_id"],

        # Observed on-chain facts
        "owner_wallet":      KNOWN_REPOVAULT["owner_wallet"],
        "repovault_address": KNOWN_REPOVAULT["repovault_address"],
        "repo_id":           KNOWN_REPOVAULT["repo_id"],
        "splits_root":       KNOWN_REPOVAULT["splits_root"],
        "event":             KNOWN_REPOVAULT["event"],
        "observation_status": KNOWN_REPOVAULT["observation_status"],
        "source":            KNOWN_REPOVAULT["source"],

        # Treasury visibility
        "treasury_visible":  True,
        "treasury_linked":   True,

        # What Dan-Go does and does not do
        "dango_controls_treasury": False,
        "dango_executes_treasury": False,

        # Invariants
        "moves_money":       False,
        "execution_allowed": False,
        "hard_enforcement":  False,
        "advisory":          True,
        "authority":         "none",
        "append_only":       True,

        "principle": (
            "Dan-Go observes treasury context; it does not operate the treasury."
        ),
        "note": (
            "The RepoVault is a GITSEA smart contract on Base. "
            "Dan-Go did not create or deploy this contract. "
            "Dan-Go does not control it. Dan-Go does not withdraw from it. "
            "This snapshot makes treasury context visible for cooperation history. "
            "No funds are moved by this snapshot."
        ),
    }


# ── Save ──────────────────────────────────────────────────────────────────────

def save_snapshot(snapshot: dict, out_path: Path | None = None) -> Path:
    if out_path is None:
        out_path = _EXAMPLES / "treasury-snapshot.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Create an advisory snapshot of the GITSEA RepoVault.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Known on-chain facts (observed via GITSEA UI and BaseScan):
  Repo:      olddqn/dango-mujin
  Chain:     Base (chain_id 8453)
  RepoVault: 0x3F9c96A429697B458Fe0a16502A050E5AB50bB00
  Event:     RepoLinked

Dan-Go observes treasury context; it does not operate the treasury.

Examples:
  python bridge/gitsea/treasury/runtime/treasury_snapshot.py
  python bridge/gitsea/treasury/runtime/treasury_snapshot.py --save
  python bridge/gitsea/treasury/runtime/treasury_snapshot.py --json
        """,
    )
    p.add_argument("--save", action="store_true",
                   help="Save to treasury/examples/treasury-snapshot.json")
    p.add_argument("--json", action="store_true", dest="json_output",
                   help="Print full JSON")
    args = p.parse_args()

    snapshot = build_treasury_snapshot()

    if args.save:
        out = save_snapshot(snapshot)
        print(f"Saved: {out}")

    if args.json_output:
        print(json.dumps(snapshot, indent=2, ensure_ascii=False))
        return

    # Default: human-readable
    print(f"\n{'='*60}")
    print(f"  Treasury Snapshot: {snapshot['repo']}")
    print(f"{'='*60}")
    print(f"  Chain:             {snapshot['chain']} (chain_id {snapshot['chain_id']})")
    print(f"  Owner wallet:      {snapshot['owner_wallet']}")
    print(f"  RepoVault:         {snapshot['repovault_address']}")
    print(f"  Repo ID:           {snapshot['repo_id'][:24]}...")
    print(f"  Splits root:       {snapshot['splits_root'][:24]}...")
    print(f"  Event:             {snapshot['event']}")
    print(f"  Status:            {snapshot['observation_status']}")
    print(f"  Source:            {snapshot['source']}")
    print(f"\n  Treasury visible:  {snapshot['treasury_visible']}")
    print(f"  Dan-Go controls:   {snapshot['dango_controls_treasury']}")
    print(f"  Dan-Go executes:   {snapshot['dango_executes_treasury']}")
    print(f"\n  moves_money:       {snapshot['moves_money']}")
    print(f"  execution_allowed: {snapshot['execution_allowed']}")
    print(f"  advisory:          {snapshot['advisory']}")
    print(f"  authority:         {snapshot['authority']}")
    print(f"\n  Principle: {snapshot['principle']}")
    print()


if __name__ == "__main__":
    main()
