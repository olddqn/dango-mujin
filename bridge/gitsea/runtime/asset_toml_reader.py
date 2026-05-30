"""
asset_toml_reader.py — Read asset.toml and output structured JSON

Reads the GITSEA asset.toml from the repository root (or a given path)
and outputs a structured JSON representation suitable for Dan-Go tooling.

Expected asset.toml format (GITSEA standard — English ASCII section names):

    [repo]
    name = "owner/repo"
    license = "MIT"

    [splits]
    "0xWALLET" = 100

    [royalties]
    multiplier = 1.0
    acceptance = 1.0

    [insurance]
    merge_insurance = true

Note on TOML 1.0:
    Bare keys must be ASCII. Section headers [repo], [splits], [royalties],
    [insurance] are all ASCII — no quoting required.
    Wallet address keys (0x...) must be quoted because they start with a digit.

Note on legacy Japanese keys:
    Earlier versions of this repo used quoted Japanese section headers
    (["リポジトリ"], etc.). These are valid TOML 1.0 but GITSEA does not
    recognise them. The canonical format uses English ASCII section names.

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

    # Extract known sections.
    # Canonical format: English ASCII section names ([repo], [splits], etc.)
    # Legacy fallback: quoted Japanese section names (["リポジトリ"], etc.)
    # GITSEA only recognises the canonical English format.
    repo_section      = raw.get("repo", raw.get("リポジトリ", {}))
    split_section     = raw.get("splits", raw.get("分割", {}))
    royalty_section   = raw.get("royalties", raw.get("著作権料", {}))
    insurance_section = raw.get("insurance", raw.get("保険", {}))

    # Canonical English keys, with legacy Japanese fallback
    repo_name  = repo_section.get("name",       repo_section.get("名前", ""))
    license_   = repo_section.get("license",    repo_section.get("ライセンス", ""))
    multiplier = royalty_section.get("multiplier", royalty_section.get("乗数", 1.0))
    acceptance = royalty_section.get("acceptance", royalty_section.get("受容度", 1.0))
    merge_ins  = insurance_section.get("merge_insurance", False)

    # Detect format for advisory warning
    _using_legacy = "リポジトリ" in raw or "分割" in raw

    # Validate split: must sum to 100
    total_split = sum(split_section.values())

    result: dict = {
        "repo_name":          repo_name,
        "license":            license_,
        "split":              split_section,
        "split_total":        total_split,
        "split_valid":        total_split == 100,
        "royalty_multiplier": multiplier,
        "royalty_acceptance": acceptance,
        "merge_insurance":    merge_ins,
        "raw":                raw,
        # Format advisory
        "format":             "legacy_japanese" if _using_legacy else "canonical_english",
        "gitsea_format_ok":   not _using_legacy,
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
    if _using_legacy:
        result["format_warning"] = (
            "asset.toml uses legacy Japanese section names. "
            "GITSEA expects English ASCII section names: "
            "[repo], [splits], [royalties], [insurance]. "
            "Update asset.toml to the canonical format before re-attempting GITSEA registration."
        )
    return result


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
    print(f"\n  TOML format:        {asset['format']}")
    print(f"  GITSEA format OK:   {'✓' if asset['gitsea_format_ok'] else '✗'}")
    if not asset["gitsea_format_ok"]:
        print(f"  FORMAT WARNING:     {asset.get('format_warning', '')}")
    print(f"\n  execution_allowed:  {asset['execution_allowed']}")
    print(f"  moves_money:        {asset['moves_money']}")
    print(f"  advisory:           {asset['advisory']}")
    print()


def main() -> None:
    p = argparse.ArgumentParser(
        description="Read asset.toml and output GITSEA asset metadata.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Expected asset.toml format (GITSEA canonical):
  [repo]
  name = "owner/repo"
  license = "MIT"

  [splits]
  "0xWALLET" = 100

  [royalties]
  multiplier = 1.0
  acceptance = 1.0

  [insurance]
  merge_insurance = true

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
            "  Hint: Use ASCII section names: [repo], [splits], [royalties], [insurance]",
            file=sys.stderr,
        )
        print(
            "  Hint: Wallet address keys (0x...) must be quoted: \"0xABC...\" = 100",
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
