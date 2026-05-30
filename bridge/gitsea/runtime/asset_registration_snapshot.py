"""
asset_registration_snapshot.py — Convert asset.toml to a GITSEA registration snapshot

Reads asset.toml, converts it to a structured registration snapshot JSON,
and saves the result to bridge/gitsea/examples/asset-registration.snapshot.json.

This file does NOT:
  - Connect to the GITSEA API
  - Submit the snapshot to any network
  - Sign any transaction
  - Move any funds
  - Perform any on-chain operation

The snapshot is a local advisory document only.

Note on keccak256:
  GITSEA may use keccak256 to hash wallet addresses or content identifiers
  internally. This module does NOT compute keccak256. It is advisory only.
  If you need to verify an on-chain address hash, use a trusted local tool
  (e.g. eth-hash with keccak-backend) — never this file.

No secrets. No private keys. No wallet operations. No network. stdlib only.

Usage:
    python bridge/gitsea/runtime/asset_registration_snapshot.py asset.toml
    python bridge/gitsea/runtime/asset_registration_snapshot.py asset.toml --save
    python bridge/gitsea/runtime/asset_registration_snapshot.py asset.toml --json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_FILE_DIR  = Path(__file__).parent
_REPO_ROOT = _FILE_DIR.parent.parent.parent
_EXAMPLES  = _FILE_DIR.parent / "examples"

# Import sibling module
sys.path.insert(0, str(_FILE_DIR))
from asset_toml_reader import read_asset_toml


# ── Snapshot builder ──────────────────────────────────────────────────────────

def build_registration_snapshot(asset: dict) -> dict:
    """
    Convert a parsed asset dict (from read_asset_toml) into a GITSEA
    registration snapshot.

    The snapshot is advisory. It is not submitted anywhere by this function.
    """
    split = asset["split"]
    split_entries = [
        {
            "address": addr,
            "percent": pct,
            "note": (
                "This address is declared in asset.toml. "
                "No funds are moved by this snapshot."
            ),
        }
        for addr, pct in split.items()
    ]

    snapshot = {
        "snapshot_type":   "gitsea_asset_registration",
        "generated_at":    datetime.now(timezone.utc).isoformat(),
        "repo_name":       asset["repo_name"],
        "license":         asset["license"],

        # Split
        "split": {
            "entries":        split_entries,
            "total_percent":  asset["split_total"],
            "valid":          asset["split_valid"],
        },

        # Royalty
        "royalty": {
            "multiplier":  asset["royalty_multiplier"],
            "acceptance":  asset["royalty_acceptance"],
        },

        # Insurance
        "merge_insurance": asset["merge_insurance"],

        # GITSEA readiness
        "gitsea_registration_ready": (
            asset["split_valid"]
            and bool(asset["repo_name"])
            and bool(asset["license"])
        ),

        # Invariants — hard constraints, never change
        "execution_allowed":  False,
        "moves_money":        False,
        "hard_enforcement":   False,
        "advisory":           True,

        # keccak256 note
        "keccak256_note": (
            "GITSEA may use keccak256 for address or content hashing internally. "
            "This snapshot does NOT compute keccak256. "
            "Verify on-chain address hashes with a trusted local tool, never this file."
        ),

        "note": (
            "This snapshot is advisory only. It is not submitted to GITSEA. "
            "No API is called. No wallet operation is performed. "
            "No transaction is signed. No funds are moved."
        ),
    }

    return snapshot


# ── Save ──────────────────────────────────────────────────────────────────────

def save_snapshot(snapshot: dict, out_path: Path | None = None) -> Path:
    """Save snapshot JSON to examples/asset-registration.snapshot.json."""
    if out_path is None:
        out_path = _EXAMPLES / "asset-registration.snapshot.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Convert asset.toml to a GITSEA registration snapshot.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Note on keccak256:
  GITSEA may use keccak256 for address or content hashing internally.
  This script does NOT compute keccak256.
  Use a trusted local tool for on-chain verification.

Examples:
  python bridge/gitsea/runtime/asset_registration_snapshot.py asset.toml
  python bridge/gitsea/runtime/asset_registration_snapshot.py asset.toml --save
  python bridge/gitsea/runtime/asset_registration_snapshot.py asset.toml --json
        """,
    )
    p.add_argument("toml_file", metavar="TOML_FILE",
                   help="Path to asset.toml")
    p.add_argument("--save", action="store_true",
                   help="Save snapshot to bridge/gitsea/examples/asset-registration.snapshot.json")
    p.add_argument("--json", action="store_true", dest="json_output",
                   help="Print snapshot as JSON")
    args = p.parse_args()

    try:
        asset = read_asset_toml(args.toml_file)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    snapshot = build_registration_snapshot(asset)

    if args.save:
        out = save_snapshot(snapshot)
        print(f"Saved: {out}")

    if args.json_output:
        print(json.dumps(snapshot, indent=2, ensure_ascii=False))
        return

    # Default: human-readable summary
    print(f"\n{'='*55}")
    print(f"  GITSEA Registration Snapshot")
    print(f"{'='*55}")
    print(f"  Repo:               {snapshot['repo_name']}")
    print(f"  License:            {snapshot['license']}")
    print(f"  Split valid:        {'✓' if snapshot['split']['valid'] else '✗'}")
    for entry in snapshot["split"]["entries"]:
        print(f"    {entry['address'][:12]}...  {entry['percent']}%")
    print(f"  Royalty multiplier: {snapshot['royalty']['multiplier']}")
    print(f"  Royalty acceptance: {snapshot['royalty']['acceptance']}")
    print(f"  Merge insurance:    {snapshot['merge_insurance']}")
    print(f"  Registration ready: {'✓' if snapshot['gitsea_registration_ready'] else '✗'}")
    print(f"\n  execution_allowed:  {snapshot['execution_allowed']}")
    print(f"  moves_money:        {snapshot['moves_money']}")
    print(f"  advisory:           {snapshot['advisory']}")
    print(f"\n  Note: {snapshot['note']}")
    print()


if __name__ == "__main__":
    main()
