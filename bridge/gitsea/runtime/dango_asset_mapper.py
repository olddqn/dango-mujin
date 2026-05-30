"""
dango_asset_mapper.py — Map Dan-Go concepts to GITSEA asset concepts

Produces a structured mapping document showing how Dan-Go protocol concepts
(negotiation, prerequisites, claims, plan corrections) correspond to GITSEA
asset concepts (split, royalty, merge insurance, stream eligibility).

This file does NOT:
  - Connect to the GITSEA API
  - Activate any GITSEA stream
  - Sign any transaction
  - Move any funds
  - Perform any on-chain operation

The output is advisory only — a conceptual bridge document.

Core insight:
  GITSEA can make repository contribution economically legible.
  Dan-Go makes contribution negotiable before it becomes economic.

No secrets. No private keys. No wallet operations. No network. stdlib only.

Usage:
    python bridge/gitsea/runtime/dango_asset_mapper.py
    python bridge/gitsea/runtime/dango_asset_mapper.py --save
    python bridge/gitsea/runtime/dango_asset_mapper.py --json
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


# ── Mapping table ─────────────────────────────────────────────────────────────

DANGO_TO_GITSEA_MAPPING = [
    {
        "dango_concept":      "Negotiation (su-table)",
        "dango_description": (
            "Append-only event log. Authority: none. "
            "Records claims, prerequisites, PRs, plan corrections."
        ),
        "gitsea_concept":     "Stream candidate record",
        "gitsea_description": (
            "GITSEA records contribution events for stream eligibility assessment. "
            "Each event is auditable."
        ),
        "bridge_note": (
            "A Dan-Go negotiation produces contribution evidence. "
            "GITSEA may read that evidence to determine stream eligibility. "
            "Dan-Go does not activate the stream."
        ),
    },
    {
        "dango_concept":      "Scoped prerequisite (applicable)",
        "dango_description": (
            "A prerequisite that applies to a claim. "
            "Generates an issue draft. Negotiation required."
        ),
        "gitsea_concept":     "Contribution condition",
        "gitsea_description": (
            "GITSEA may require contribution conditions before "
            "a split becomes active."
        ),
        "bridge_note": (
            "Meeting a scoped prerequisite in Dan-Go is not the same as "
            "activating a GITSEA stream. It is evidence toward that activation."
        ),
    },
    {
        "dango_concept":      "Scoped prerequisite (bypassed)",
        "dango_description": (
            "A prerequisite that does not apply in scope. "
            "Audit assertion only. No issue generated."
        ),
        "gitsea_concept":     "Waived condition",
        "gitsea_description": (
            "A condition that GITSEA does not require for this contribution type."
        ),
        "bridge_note": (
            "Bypass in Dan-Go = audit log that the condition was assessed "
            "and found non-applicable. Not a waiver from an authority."
        ),
    },
    {
        "dango_concept":      "PR merge (gitsea_eligible: true)",
        "dango_description": (
            "A merged PR with gitsea_eligible flag. "
            "Evidence accepted. Negotiation may still reopen."
        ),
        "gitsea_concept":     "Stream candidate event",
        "gitsea_description": (
            "A contribution event that may qualify for GITSEA stream inclusion."
        ),
        "bridge_note": (
            "PR merge is evidence. Not authority. "
            "gitsea_eligible: true signals potential stream candidacy only. "
            "No GITSEA stream is activated by this flag."
        ),
    },
    {
        "dango_concept":      "Plan correction (append-only)",
        "dango_description": (
            "plan_correction_proposed event appended to su-table. "
            "Original plan preserved. Correction is a proposal."
        ),
        "gitsea_concept":     "Contribution amendment",
        "gitsea_description": (
            "GITSEA may record amendments to contribution claims "
            "when evidence is updated."
        ),
        "bridge_note": (
            "Dan-Go plan correction does not modify the GITSEA stream. "
            "It adds a new negotiation record that GITSEA can observe."
        ),
    },
    {
        "dango_concept":      "asset.toml split",
        "dango_description": (
            "Declares wallet address(es) and percentage splits for this repo. "
            "Advisory. No funds moved by Dan-Go."
        ),
        "gitsea_concept":     "Split configuration",
        "gitsea_description": (
            "GITSEA reads split configuration to determine how stream "
            "proceeds are distributed."
        ),
        "bridge_note": (
            "Dan-Go reads and validates the split. "
            "GITSEA applies the split when a stream activates. "
            "These are separate operations."
        ),
    },
    {
        "dango_concept":      "asset.toml royalty multiplier",
        "dango_description": (
            "乗数 (multiplier): scales royalty yield. "
            "Declared. Not computed. Not applied by Dan-Go."
        ),
        "gitsea_concept":     "Royalty yield parameter",
        "gitsea_description": (
            "GITSEA uses royalty parameters to compute stream yield."
        ),
        "bridge_note": (
            "Dan-Go records the declared multiplier as advisory metadata. "
            "Yield computation is a GITSEA operation, not a Dan-Go operation."
        ),
    },
    {
        "dango_concept":      "asset.toml merge_insurance",
        "dango_description": (
            "保険 (insurance): merge_insurance = true. "
            "Declared intent. Not enforced by Dan-Go."
        ),
        "gitsea_concept":     "Merge insurance flag",
        "gitsea_description": (
            "GITSEA may offer merge insurance as a stream protection mechanism."
        ),
        "bridge_note": (
            "Dan-Go records the merge_insurance declaration. "
            "Whether it activates depends on GITSEA, not Dan-Go."
        ),
    },
    {
        "dango_concept":      "Dignity guard",
        "dango_description": (
            "participant_consent, revocable_consent fields. "
            "Checked at every negotiation step."
        ),
        "gitsea_concept":     "Contributor consent layer",
        "gitsea_description": (
            "GITSEA may require contributor consent before "
            "activating a split."
        ),
        "bridge_note": (
            "Dan-Go's dignity guard is protocol-level, not API-level. "
            "It does not call GITSEA consent APIs. "
            "It asserts consent in the negotiation record."
        ),
    },
    {
        "dango_concept":      "Negotiation authority: none",
        "dango_description": (
            "No coordinator. No adjudicator. No enforcement. "
            "Evidence only."
        ),
        "gitsea_concept":     "Trustless audit trail",
        "gitsea_description": (
            "GITSEA may use an authority-free audit trail for "
            "stream eligibility decisions."
        ),
        "bridge_note": (
            "Dan-Go's authority: none is a protocol invariant, not a feature flag. "
            "GITSEA can read the Dan-Go audit trail without becoming an authority."
        ),
    },
]


# ── Output builder ────────────────────────────────────────────────────────────

def build_mapping_document() -> dict:
    return {
        "document_type":  "dango_gitsea_concept_mapping",
        "generated_at":   datetime.now(timezone.utc).isoformat(),
        "core_insight": (
            "GITSEA can make repository contribution economically legible. "
            "Dan-Go makes contribution negotiable before it becomes economic."
        ),
        "mapping_count":  len(DANGO_TO_GITSEA_MAPPING),
        "mappings":       DANGO_TO_GITSEA_MAPPING,

        # Invariants
        "execution_allowed":  False,
        "moves_money":        False,
        "hard_enforcement":   False,
        "advisory":           True,

        "note": (
            "This mapping is advisory only. No GITSEA API is called. "
            "No stream is activated. No funds are moved. "
            "No wallet operation is performed."
        ),
    }


# ── Save ──────────────────────────────────────────────────────────────────────

def save_mapping(doc: dict, out_path: Path | None = None) -> Path:
    if out_path is None:
        out_path = _EXAMPLES / "dango-to-gitsea-asset.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Map Dan-Go concepts to GITSEA asset concepts.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Core insight:
  GITSEA can make repository contribution economically legible.
  Dan-Go makes contribution negotiable before it becomes economic.

Examples:
  python bridge/gitsea/runtime/dango_asset_mapper.py
  python bridge/gitsea/runtime/dango_asset_mapper.py --save
  python bridge/gitsea/runtime/dango_asset_mapper.py --json
        """,
    )
    p.add_argument("--save", action="store_true",
                   help="Save to bridge/gitsea/examples/dango-to-gitsea-asset.json")
    p.add_argument("--json", action="store_true", dest="json_output",
                   help="Print full JSON")
    args = p.parse_args()

    doc = build_mapping_document()

    if args.save:
        out = save_mapping(doc)
        print(f"Saved: {out}")

    if args.json_output:
        print(json.dumps(doc, indent=2, ensure_ascii=False))
        return

    # Default: human-readable summary
    print(f"\n{'='*60}")
    print(f"  Dan-Go → GITSEA Concept Mapping")
    print(f"{'='*60}")
    print(f"  {doc['core_insight']}")
    print(f"\n  {doc['mapping_count']} concept pairs:\n")
    for m in doc["mappings"]:
        print(f"  Dan-Go:  {m['dango_concept']}")
        print(f"  GITSEA:  {m['gitsea_concept']}")
        print(f"  Bridge:  {m['bridge_note']}")
        print()
    print(f"  execution_allowed:  {doc['execution_allowed']}")
    print(f"  moves_money:        {doc['moves_money']}")
    print(f"  advisory:           {doc['advisory']}")
    print()


if __name__ == "__main__":
    main()
