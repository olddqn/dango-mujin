#!/usr/bin/env python3
"""
world_model_with_memory.py — dango-gitsea-bridge / reflective memory layer

Build an OGI-style world model enriched with prior knowledge from the
reflective memory layer.

The reflective memory loop:
  World Model → Plan Tree → Negotiation → Memory
       ↑                                      |
       └──────────────── prior_knowledge ─────┘

This module closes that loop:
  1. Load the claim from sutable/claims.jsonl (or a claim JSON file)
  2. Build the world model via ogi/runtime/world_model_mapper.build_world_model()
  3. Load the latest memory snapshot via reflective_memory.extract_prior_knowledge()
  4. Inject prior_knowledge into the world model dict
  5. Return the enriched world model

The prior_knowledge block tells the world model:
  - which plan is currently active
  - what objections were raised (and their types)
  - what new conditions were learned from competing plans
  - how deep the correction chain is

This lets the next plan tree cycle avoid repeating objected conditions
and incorporate learned constraints automatically.

Absolute prohibitions:
  - No execution of plans or bundles
  - No network, no API keys, no external libraries
  - No modification of existing sutable events

CLI:
  python runtime/world_model_with_memory.py --claim-id housing-001
  python runtime/world_model_with_memory.py --claim-id housing-001 --json
  python runtime/world_model_with_memory.py --claim-id housing-001 --verbose
  python runtime/world_model_with_memory.py --claim-file path/to/claim.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# ── Path setup ────────────────────────────────────────────────────────────────

_RUNTIME_DIR  = Path(__file__).parent
_OGI_RUNTIME  = _RUNTIME_DIR.parent / "ogi" / "runtime"

sys.path.insert(0, str(_RUNTIME_DIR))
sys.path.insert(0, str(_OGI_RUNTIME))

from sutable_log import read_all
from reflective_memory import extract_prior_knowledge

# world_model_mapper lives in ogi/runtime — import with graceful fallback
try:
    from world_model_mapper import build_world_model as _build_world_model
    _HAS_WORLD_MODEL = True
except ImportError:
    _HAS_WORLD_MODEL = False


# ── Claim loading ─────────────────────────────────────────────────────────────

def load_claim_from_sutable(claim_id: str) -> dict[str, Any] | None:
    """
    Load the most recent claim_created event for a claim_id from claims.jsonl.

    Returns the claim dict, or None if not found.
    """
    events = [
        ev for ev in read_all("claims")
        if ev.get("claim_id") == claim_id
        and ev.get("event_type") == "claim_created"
    ]
    return events[-1] if events else None


def load_claim_from_file(path: str | Path) -> dict[str, Any]:
    """Load a claim from a JSON file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ── World model stub (fallback when ogi/runtime unavailable) ──────────────────

def _stub_world_model(claim: dict[str, Any]) -> dict[str, Any]:
    """
    Minimal world model stub when world_model_mapper is not available.

    Used so this module is independently runnable even without ogi/runtime/.
    """
    claim_id = claim.get("claim_id", "unknown")
    observed = claim.get("observed_state", [])
    missing  = claim.get("missing_conditions", [])
    dignity  = claim.get("dignity_constraints", [])
    return {
        "world_model_id":    f"wm-{claim_id}",
        "claim_id":          claim_id,
        "observed_state":    [{"state": s, "category": "observed"} for s in observed],
        "desired_state":     [],
        "state_gap":         [{"condition": c, "category": "unknown",
                               "blocking": True, "notes": ""} for c in missing],
        "reality_feedback":  [],
        "uncertainty":       {
            "level":         "high" if missing else "low",
            "reason":        f"{len(missing)} missing condition(s)" if missing else "no gaps",
            "missing_count": len(missing),
        },
        "dignity_surface":   dignity,
        "world_model_notes": "(stub — world_model_mapper not available)",
    }


# ── Core builder ──────────────────────────────────────────────────────────────

def build_world_model_with_memory(
    claim_id: str,
    claim: dict[str, Any],
    *,
    include_feedback: bool = False,
) -> dict[str, Any]:
    """
    Build a world model enriched with reflective prior knowledge.

    Args:
        claim_id:         The claim being modelled.
        claim:            The claim dict (from claims.jsonl or a JSON file).
        include_feedback: Whether to include reality_feedback events in the
                          world model (forwarded to world_model_mapper if available).

    Returns:
        {
          "claim_id":       str,
          "world_model":    { ... OGI world model ... },
          "prior_knowledge": {
              "memory_id":             str,
              "active_plan_id":        str,
              "negotiation_status":    str,
              "learned_conditions":    [str, ...],
              "known_objection_types": [str, ...],
              "correction_depth":      int,
              "contest_count":         int,
              "summary":               str,
          } | {},
          "memory_integrated": bool,
        }
    """
    # 1. Build world model
    if _HAS_WORLD_MODEL:
        wm = _build_world_model(claim, include_feedback=include_feedback)
    else:
        wm = _stub_world_model(claim)

    # 2. Load prior knowledge from memory.jsonl
    prior_knowledge = extract_prior_knowledge(claim_id)

    # 3. Inject learned_conditions into state_gap as additional entries
    #    so the next plan tree cycle picks them up automatically.
    if prior_knowledge.get("learned_conditions"):
        existing_gap_conditions = {
            g.get("condition", "") for g in wm.get("state_gap", [])
        }
        for cond in prior_knowledge["learned_conditions"]:
            if cond not in existing_gap_conditions:
                wm.setdefault("state_gap", []).append({
                    "condition": cond,
                    "category":  "learned_from_negotiation",
                    "blocking":  False,
                    "notes":     f"learned from memory {prior_knowledge.get('memory_id', '')}",
                })

    return {
        "claim_id":        claim_id,
        "world_model":     wm,
        "prior_knowledge": prior_knowledge,
        "memory_integrated": bool(prior_knowledge),
    }


# ── Display ───────────────────────────────────────────────────────────────────

def _print_enriched(result: dict[str, Any], verbose: bool) -> None:
    claim_id = result["claim_id"]
    wm       = result["world_model"]
    pk       = result["prior_knowledge"]

    print(f"World Model (with Memory) — {claim_id}")
    print(f"  world_model_id:      {wm.get('world_model_id', '?')}")
    print(f"  uncertainty:         {wm.get('uncertainty', {}).get('level', '?')}")

    gap = wm.get("state_gap", [])
    print(f"  state_gap entries:   {len(gap)}")
    for g in gap:
        tag = " [learned]" if g.get("category") == "learned_from_negotiation" else ""
        print(f"    • {g['condition']}{tag}")

    if pk:
        print(f"\n  Prior Knowledge (mem: {pk.get('memory_id', '?')})")
        print(f"    negotiation_status:    {pk.get('negotiation_status', '?')}")
        print(f"    active_plan_id:        {pk.get('active_plan_id') or '(none)'}")
        print(f"    learned_conditions:    {pk.get('learned_conditions') or '(none)'}")
        print(f"    known_objection_types: {pk.get('known_objection_types') or '(none)'}")
        print(f"    correction_depth:      {pk.get('correction_depth', 0)}")
        print(f"    summary:               {pk.get('summary', '')}")
    else:
        print(f"\n  Prior Knowledge:     (none — run memory_append.py first)")

    if verbose:
        obs = wm.get("observed_state", [])
        print(f"\n  Observed state ({len(obs)}):")
        for o in obs:
            print(f"    ✓ {o.get('state', '')}")
        desired = wm.get("desired_state", [])
        if desired:
            print(f"\n  Desired state ({len(desired)}):")
            for d in desired:
                met = "✓" if d.get("met") else "✗"
                print(f"    {met} {d.get('state', '')}")
        dignity = wm.get("dignity_surface", [])
        if dignity:
            print(f"\n  Dignity surface: {dignity}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="world_model_with_memory",
        description=(
            "Build an OGI world model enriched with reflective memory "
            "prior knowledge. Read-only: does not write to any file."
        ),
    )
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--claim-id",   metavar="CLAIM_ID",
                     help="Load claim from sutable/claims.jsonl")
    src.add_argument("--claim-file", metavar="PATH",
                     help="Load claim from a JSON file")
    p.add_argument("--json",           action="store_true", dest="json_output")
    p.add_argument("--verbose", "-v",  action="store_true")
    p.add_argument("--include-feedback", action="store_true",
                   help="Include reality_feedback events in world model.")
    return p.parse_args()


def main() -> None:
    args = _parse_args()

    # Load claim
    if args.claim_id:
        claim = load_claim_from_sutable(args.claim_id)
        if not claim:
            print(f"✗ No claim_created event found for {args.claim_id!r}", file=sys.stderr)
            sys.exit(1)
        claim_id = args.claim_id
    else:
        claim    = load_claim_from_file(args.claim_file)
        claim_id = claim.get("claim_id", Path(args.claim_file).stem)

    result = build_world_model_with_memory(
        claim_id,
        claim,
        include_feedback=args.include_feedback,
    )

    if args.json_output:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        _print_enriched(result, verbose=args.verbose)


if __name__ == "__main__":
    main()
