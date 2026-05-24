#!/usr/bin/env python3
"""
prerequisite_memory_integration.py — dango-gitsea-bridge / prerequisite promotion

Integrate promoted federation prerequisites into world model prior knowledge.

A promoted prerequisite is advisory — it does not enforce or gate anything.
This module provides the bridge between the prerequisite layer and the
world model layer (world_model_with_memory.py).

What this does:
  - Reads promoted prerequisites from federation.jsonl
  - Formats them as planning hints for a claim's world model prior_knowledge
  - Appends federation_prerequisites list to prior_knowledge (advisory)

What this does NOT do:
  - Hard-enforce prerequisites (enforcement is always forbidden)
  - Modify existing memory snapshots (append-only)
  - Remove or override claim-specific learned conditions

CLI:
  python runtime/prerequisite_memory_integration.py --claim-id housing-001
  python runtime/prerequisite_memory_integration.py --claim-id housing-001 --json
  python runtime/prerequisite_memory_integration.py --all-claims
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from claim_federation import load_federation_events, build_federation_map
from prerequisite_snapshot import snapshot, promoted_prerequisites


# ── Planning hint format ──────────────────────────────────────────────────────

def get_prerequisite_planning_hints(
    claim_id: str,
    fed_events: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """
    Return promoted prerequisites as planning hints for a specific claim.

    Each hint includes:
      condition      — the prerequisite condition name
      hint_type      — always "federation_prerequisite"
      authority      — always "none"
      evidence_claims— list of claims that independently discovered this
      status         — current prerequisite status
      advisory       — always True (never enforced)
      note           — human-readable context
    """
    if fed_events is None:
        fed_events = load_federation_events()

    all_statuses = snapshot()
    if not all_statuses:
        return []

    # Use scope-aware propagation if available
    try:
        from scoped_condition_propagation import get_scoped_propagation_hints
        scoped_hints = get_scoped_propagation_hints(claim_id)
        # Enrich with evidence_claims from snapshot statuses
        status_map = {s["condition"]: s for s in all_statuses}
        hints_out: list[dict[str, Any]] = []
        for h in scoped_hints:
            cond = h["condition"]
            s = status_map.get(cond, {})
            entry: dict[str, Any] = {
                "condition":            cond,
                "hint_type":            "federation_prerequisite",
                "authority":            "none",
                "evidence_claims":      s.get("evidence_claims", []),
                "convergence_count":    s.get("evidence_claims_count", 0),
                "independent_convergence": s.get("independent_convergence"),
                "status":               s.get("status", ""),
                "advisory":             True,
                "applicable":           h.get("applicable", True),
                "scoped":               h.get("scoped", False),
                "scope":                h.get("scope", "all_spaces"),
                "note":                 h["note"],
            }
            hints_out.append(entry)
        return hints_out
    except ImportError:
        pass

    # Fallback: unscoped hints (pre-weakening compatibility)
    hints: list[dict[str, Any]] = []
    for s in all_statuses:
        if s.get("status") not in ("promoted", "reaffirmed", "weakened"):
            continue

        cond = s["condition"]
        evidence_claims = s.get("evidence_claims", [])

        hints.append({
            "condition": cond,
            "hint_type": "federation_prerequisite",
            "authority": "none",
            "evidence_claims": evidence_claims,
            "convergence_count": s.get("evidence_claims_count", 0),
            "independent_convergence": s.get("independent_convergence"),
            "status": s["status"],
            "advisory": True,
            "applicable": True,
            "scoped": False,
            "scope": "all_spaces",
            "note": (
                f"'{cond}' was independently discovered by {len(evidence_claims)} claim(s) "
                f"via structural plan tree diff. Federation-level consideration recommended."
            ),
        })

    return hints


def integrate_into_prior_knowledge(
    prior_knowledge: dict[str, Any],
    claim_id: str,
    fed_events: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Inject federation prerequisites into a prior_knowledge dict.

    Adds/extends:
      prior_knowledge["federation_prerequisites"] — list of promoted prerequisites
      prior_knowledge["federation_prerequisite_conditions"] — list of condition strings

    Returns the enriched prior_knowledge dict (copy — never mutates input).
    """
    pk = dict(prior_knowledge)
    hints = get_prerequisite_planning_hints(claim_id, fed_events=fed_events)

    pk["federation_prerequisites"] = hints
    # Only list conditions that are actually applicable (not bypassed for this claim)
    applicable = [h["condition"] for h in hints if h.get("applicable", True)]
    pk["federation_prerequisite_conditions"] = applicable

    if hints:
        existing_note = pk.get("summary", "")
        prereq_summary = f"federation prerequisites: {', '.join(applicable)}" if applicable else "all prerequisites bypassed for this claim"
        if existing_note:
            pk["summary"] = f"{existing_note}; {prereq_summary}"
        else:
            pk["summary"] = prereq_summary

    return pk


def build_enriched_prior_knowledge(
    claim_id: str,
    fed_events: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Build a prior_knowledge dict with federation prerequisites integrated.

    Returns:
      {
        "claim_id": str,
        "federation_prerequisites": [...],
        "federation_prerequisite_conditions": [...],
        "summary": str,
        "source": "prerequisite_memory_integration"
      }
    """
    if fed_events is None:
        fed_events = load_federation_events()

    hints = get_prerequisite_planning_hints(claim_id, fed_events=fed_events)
    conditions = [h["condition"] for h in hints]

    return {
        "claim_id": claim_id,
        "federation_prerequisites": hints,
        "federation_prerequisite_conditions": conditions,
        "summary": (
            f"{len(hints)} federation prerequisite(s): {', '.join(conditions)}"
            if hints else "no promoted federation prerequisites"
        ),
        "source": "prerequisite_memory_integration",
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

def _main() -> None:
    parser = argparse.ArgumentParser(
        description="Integrate federation prerequisites into world model prior knowledge."
    )
    parser.add_argument("--claim-id", metavar="ID", help="Claim ID to generate hints for")
    parser.add_argument("--all-claims", action="store_true", help="All claims in federation")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--verbose", action="store_true", help="Verbose")
    args = parser.parse_args()

    fed_events = load_federation_events()
    fmap = build_federation_map(fed_events)

    if args.all_claims:
        results = {}
        for cid in sorted(fmap.keys()):
            results[cid] = build_enriched_prior_knowledge(cid, fed_events=fed_events)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            for cid, pk in results.items():
                _print_pk(cid, pk, verbose=args.verbose)
        return

    if not args.claim_id:
        parser.error("--claim-id or --all-claims required")

    pk = build_enriched_prior_knowledge(args.claim_id, fed_events=fed_events)

    if args.json:
        print(json.dumps(pk, indent=2))
    else:
        _print_pk(args.claim_id, pk, verbose=args.verbose)


def _print_pk(claim_id: str, pk: dict[str, Any], *, verbose: bool) -> None:
    hints = pk.get("federation_prerequisites", [])
    applicable = [h for h in hints if h.get("applicable", True)]
    bypassed   = [h for h in hints if not h.get("applicable", True)]
    print(f"  {claim_id}  federation prerequisites: {len(hints)}"
          f"  (applicable: {len(applicable)}, bypassed: {len(bypassed)})")
    for h in applicable:
        ind   = "independent" if h.get("independent_convergence") else "shared authors"
        scope = f"  [scope: {h['scope']}]" if h.get("scoped") else "  [universal]"
        print(f"    ✓ [{h['status']}] {h['condition']}{scope}")
        print(f"      authority: none  [{ind}]")
        print(f"      evidence:  {', '.join(h.get('evidence_claims', []))}")
        if verbose:
            print(f"      note: {h['note']}")
    for h in bypassed:
        print(f"    ⊛ [{h['status']}] {h['condition']}  [bypassed — not propagated]")
        if verbose:
            print(f"      note: {h['note']}")
    print()


if __name__ == "__main__":
    _main()
