"""
asset_toml_reader.py — Read asset.toml and output structured JSON

Reads the GITSEA asset.toml from the repository root (or a given path)
and outputs a structured JSON representation suitable for Dan-Go tooling.

Notes on Japanese TOML keys:
    TOML 1.0 spec requires bare keys to be ASCII. Japanese section headers
    and key names must be quoted in the file (e.g. ["リポジトリ"] not [リポジトリ]).
    Python 3.11+ tomllib parses quoted Unicode keys correctly.

No secrets. No private keys. No wallet operations. No network. stdlib only.

Usage:
    python bridge/gitsea/runtime/asset_toml_reader.py asset.toml
    python bridge/gitsea/runtime/asset_toml_reader.py asset.toml --json
    python bridge/gitsea/runtime/asset_toml_reader.py asset.toml --field split
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tomllib
from pathlib import Path
from typing import Any

_FILE_DIR   = Path(__file__).parent
_REPO_ROOT  = _FILE_DIR.parent.parent.parent


# ── Core reader ───────────────────────────────────────────────────────────────

def read_asset_toml(path: str | Path) -> dict[str, Any]:
    """
    Read and parse asset.toml. Returns a normalised dict:
    {
      repo_name, license, split, royalty_multiplier, royalty_acceptance,
      merge_insurance, raw
    }
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"asset.toml not found: {path}")

    with open(path, "rb") as f:
        raw = tomllib.load(f)

    # Extract known sections (Japanese quoted keys)
    repo_section     = raw.get("リポジトリ", {})
    split_section    = raw.get("分割", {})
    royalty_section  = raw.get("著作権料", {})
    insurance_section = raw.get("保険", {})

    repo_name  = repo_section.get("名前", "")
    license_   = repo_section.get("ライセンス", "")
    multiplier = royalty_section.get("乗数", 1.0)
    acceptance = royalty_section.get("受容度", 1.0)
    merge_ins  = insurance_section.get("merge_insurance", False)

    # Validate split: must sum to 100
    total_split = sum(split_section.values())

    return {
        "repo_name":          repo_name,
        "license":            license_,
        "split":              split_section,
        "split_total":        total_split,
        "split_valid":        total_split == 100,
        "royalty_multiplier": multiplier,
        "royalty_acceptance": acceptance,
        "merge_insurance":    merge_ins,
        "raw":                raw,
        # Invariants
        "execution_allowed":  False,
        "moves_money":        False,
        "advisory":           True,
        "note": (
            "This file declares GITSEA asset metadata only. "
            "No funds are moved by reading this file. "
            "No GITSEA API is called. No wallet operation is performed."
        ),
    }


# ── CLI display ───────────────────────────────────────────────────────────────

def _print_asset(asset: dict[str, Any]) -> None:
    print(f"\n{'='*55}")
    print(f"  GITSEA Asset: {asset['repo_name']}")
    print(f"{'='*55}")
    print(f"  License:            {asset['license']}")
    print(f"  Split entries:      {len(asset['split'])}")
    print(f"  Split total:        {asset['split_total']}  {'✓' if asset['split_valid'] else '✗ (must be 100)'}")
    for addr, pct in asset["split"].items():
        print(f"    {addr[:12]}...  {pct}%")
    print(f"  Royalty multiplier: {asset['royalty_multiplier']}")
    print(f"  Royalty acceptance: {asset['royalty_acceptance']}")
    print(f"  Merge insurance:    {asset['merge_insurance']}")
    print(f"\n  execution_allowed:  {asset['execution_allowed']}")
    print(f"  moves_money:        {asset['moves_money']}")
    print(f"  advisory:           {asset['advisory']}")
    print()


def main() -> None:
    p = argparse.ArgumentParser(
        description="Read asset.toml and output GITSEA asset metadata.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Notes:
  Japanese section headers in asset.toml must be quoted
  (e.g. ["リポジトリ"]) for compatibility with Python 3.11+ tomllib.
  The TOML 1.0 spec restricts bare keys to ASCII characters.

Examples:
  python bridge/gitsea/runtime/asset_toml_reader.py asset.toml
  python bridge/gitsea/runtime/asset_toml_reader.py asset.toml --json
  python bridge/gitsea/runtime/asset_toml_reader.py asset.toml --field split
        """,
    )
    p.add_argument("toml_file", metavar="TOML_FILE",
                   help="Path to asset.toml (usually repo root)")
    p.add_argument("--json",  action="store_true", dest="json_output")
    p.add_argument("--field", metavar="FIELD",
                   choices=["repo_name","license","split","royalty_multiplier",
                            "royalty_acceptance","merge_insurance"],
                   help="Output a single field")
    args = p.parse_args()

    try:
        asset = read_asset_toml(args.toml_file)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except tomllib.TOMLDecodeError as e:
        print(f"ERROR: TOML parse failed: {e}", file=sys.stderr)
        print(
            "  Hint: Japanese section headers must be quoted, e.g. [\"リポジトリ\"]",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.field:
        val = asset.get(args.field)
        if isinstance(val, dict):
            print(json.dumps(val, indent=2, ensure_ascii=False))
        else:
            print(val)
        return

    if args.json_output:
        # Exclude raw to keep output clean
        out = {k: v for k, v in asset.items() if k != "raw"}
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return

    _print_asset(asset)


if __name__ == "__main__":
    main()
