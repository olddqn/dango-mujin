#!/usr/bin/env python3
"""
prerequisite_snapshot.py — dango-gitsea-bridge / prerequisite promotion

Query the current state of all promoted federation prerequisites.

Reads federation.jsonl for promoted, contested, reaffirmed, and deprecated events.
This module is read-only.

CLI:
  python runtime/prerequisite_snapshot.py
  python runtime/prerequisite_snapshot.py --condition space_safety_assessed
  python runtime/prerequisite_snapshot.py --json
  python runtime/prerequisite_snapshot.py --all
  python runtime/prerequisite_snapshot.py --promoted-only
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from claim_federation import load_federation_events
from prerequisite_contest_resolver import (
    all_prerequisite_statuses,
    get_prerequisite_status,
)
from prerequisite_evidence_bundle import build_evidence_bundle


def snapshot(
    condition: str | None = None,
    *,
    include_evidence: bool = False,
) -> dict[str, Any] | list[dict[str, Any]]:
    """
    Return a snapshot of one or all prerequisite statuses.

    If condition is given: returns a single status dict (or None).
    Otherwise: returns list of all status dicts.

    include_evidence: if True, attach the full evidence_bundle to each status.
    """
    fed_events = load_federation_events()

    if condition:
        status = get_prerequisite_status(condition, fed_events)
        if status is None:
            return {}
        if include_evidence:
            bundle = build_evidence_bundle(condition)
            status["evidence_bundle"] = bundle.get("evidence_bundle", {})
        return status

    statuses = all_prerequisite_statuses(fed_events)
    if include_evidence:
        for s in statuses:
            bundle = build_evidence_bundle(s["condition"])
            s["evidence_bundle"] = bundle.get("evidence_bundle", {})
    return statuses


def promoted_prerequisites(fed_events: list[dict[str, Any]] | None = None) -> list[str]:
    """Return list of condition names currently in 'promoted' or 'reaffirmed' status."""
    if fed_events is None:
        fed_events = load_federation_events()
    statuses = all_prerequisite_statuses(fed_events)
    return [
        s["condition"]
        for s in statuses
        if s["status"] in ("promoted", "reaffirmed")
    ]


# ── CLI ───────────────────────────────────────────────────────────────────────

def _main() -> None:
    parser = argparse.ArgumentParser(
        description="Query federation prerequisite state."
    )
    parser.add_argument("--condition", metavar="COND", help="Single condition")
    parser.add_argument("--all", action="store_true", help="All prerequisites (default)")
    parser.add_argument("--promoted-only", action="store_true",
                        help="Only show promoted/reaffirmed prerequisites")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--evidence", action="store_true",
                        help="Include evidence bundle in output")
    args = parser.parse_args()

    if args.condition:
        result = snapshot(args.condition, include_evidence=args.evidence)
        if not result:
            print(f"No prerequisite found for '{args.condition}'.", file=sys.stderr)
            sys.exit(1)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            _print_status(result, verbose=args.evidence)
        return

    all_statuses = snapshot(include_evidence=args.evidence)
    if args.promoted_only:
        all_statuses = [s for s in all_statuses if s["status"] in ("promoted", "reaffirmed")]

    if args.json:
        print(json.dumps(all_statuses, indent=2))
        return

    if not all_statuses:
        print("No promoted prerequisites found.")
        print("Run: python runtime/prerequisite_promotion.py --append")
        return

    print("Federation Prerequisite Snapshot")
    print()
    for s in all_statuses:
        _print_status(s, verbose=args.evidence)


def _print_status(s: dict[str, Any], *, verbose: bool = False) -> None:
    sym = {
        "promoted":   "✓",
        "reaffirmed": "✓✓",
        "contested":  "⚠",
        "deprecated": "✗",
    }.get(s.get("status", ""), "?")
    ind = "independent" if s.get("independent_convergence") else "shared authors"
    print(f"  {sym} {s['condition']}  [{s.get('status')}]")
    print(f"      authority:       {s.get('authority', 'none')}")
    print(f"      evidence claims: {s.get('evidence_claims_count')}  [{ind}]")
    print(f"      triggered by:    {', '.join(s.get('evidence_claims', []))}")
    print(f"      evidence score:  {s.get('evidence_score', 0)}")
    print(f"      contest_count:   {s.get('contest_count', 0)}")
    print(f"      reaffirmed:      {s.get('reaffirm_count', 0)}")
    print(f"      deprecated:      {s.get('deprecated', False)}")
    print(f"      contestable:     True")

    if verbose:
        eb = s.get("evidence_bundle", {})
        if eb:
            print(f"      evidence bundle:")
            for cl in eb.get("claims", []):
                print(f"        {cl['claim_id']}: learned via {cl.get('learned_via')}, "
                      f"objection={cl.get('objection_type') or '—'}")
    print()


if __name__ == "__main__":
    _main()
