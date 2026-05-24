#!/usr/bin/env python3
"""
world_model_mapper.py — dango-gitsea-bridge / OGI reasoning surface

Map a Dan-Go Claim (+ optional reality_feedback events) to an OGI-style
world model representation.

Dan-Go → World Model mapping:
  observed_state    → observed_state   (what is currently true)
  required_state    → desired_state    (what must become true)
  missing_conditions→ state_gap        (delta between observed and desired)
  reality_feedback  → reality_feedback (post-execution ground truth)
  uncertainty       → inferred from missing_conditions + dignity constraints

A world model is NOT a plan. It is a structured description of the gap
between observed reality and the desired state the claim is trying to close.

The plan tree (see claim_plan_tree.py) is generated FROM the world model gap.

Design:
  - No execution, no network, no external calls
  - stdlib only
  - All state is read from the claim JSON
  - reality_feedback events are optionally loaded from sutable/reality_feedback.jsonl

CLI:
  python ogi/runtime/world_model_mapper.py ogi/examples/post-scarcity.claim.json
  python ogi/runtime/world_model_mapper.py ogi/examples/post-scarcity.claim.json > ogi/examples/world-model-state.json
  python ogi/runtime/world_model_mapper.py ogi/examples/post-scarcity.claim.json --include-feedback
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Path resolution for sutable_log import (optional)
_BRIDGE_RUNTIME = Path(__file__).parent.parent.parent / "runtime"
sys.path.insert(0, str(_BRIDGE_RUNTIME))

try:
    from sutable_log import read_all as _read_all
    _HAS_SUTABLE = True
except ImportError:
    _HAS_SUTABLE = False


# ── State classification ───────────────────────────────────────

# Known dignity-related states
_DIGNITY_STATES: frozenset[str] = frozenset({
    "revocable_consent",
    "no_identity_exposure",
    "fair_participation",
    "automation_requires_consent",
    "consent_established",
    "participant_consent",
    "owner_consent",
    "dignity_constraints",
})

# Known risk/safety states
_RISK_STATES: frozenset[str] = frozenset({
    "safety_assessment",
    "structural_assessment",
    "legal_review_complete",
    "legal_ownership_confirmed",
    "risk_assessment_complete",
})


def _classify_state(state: str) -> str:
    """Classify a state string into a category."""
    if state in _DIGNITY_STATES:
        return "dignity"
    if state in _RISK_STATES:
        return "risk"
    if "agent" in state or "coordination" in state or "negotiation" in state:
        return "coordination"
    if "feedback" in state or "memory" in state or "shared" in state:
        return "infrastructure"
    return "general"


def _uncertainty_level(missing: list[str], dignity_constraints: list[str]) -> str:
    """Compute an uncertainty level string from missing conditions."""
    n = len(missing)
    has_dignity = bool(dignity_constraints) or any(
        m in _DIGNITY_STATES for m in missing
    )
    if n == 0:
        return "low"
    if n <= 2 and not has_dignity:
        return "medium"
    if has_dignity or n > 4:
        return "high"
    return "medium"


def _feedback_from_sutable(claim_id: str) -> list[dict[str, Any]]:
    """Load reality_feedback events for this claim_id from su-table."""
    if not _HAS_SUTABLE:
        return []
    try:
        events = list(_read_all("reality_feedback"))
        return [
            e for e in events
            if e.get("claim_id") == claim_id
        ]
    except Exception:
        return []


def build_world_model(
    claim: dict[str, Any],
    include_feedback: bool = False,
) -> dict[str, Any]:
    """
    Build an OGI-style world model from a Dan-Go Claim.

    Returns:
      {
        "world_model_id":  "wm-{claim_id}",
        "claim_id":        str,
        "observed_state":  [{"state": str, "category": str}, ...],
        "desired_state":   [{"state": str, "category": str, "met": bool}, ...],
        "state_gap":       [{"condition": str, "category": str,
                             "blocking": bool, "notes": str}, ...],
        "reality_feedback": [...],
        "uncertainty":     {"level": str, "reason": str, "missing_count": int},
        "dignity_surface": [...],
        "world_model_notes": str,
      }
    """
    claim_id         = claim.get("claim_id", "unknown")
    observed         = list(claim.get("observed_state", []))
    required         = list(claim.get("required_state", []))
    missing          = list(claim.get("missing_conditions", []))
    dignity_cs       = list(claim.get("dignity_constraints", []))
    decision         = claim.get("decision", "negotiate")
    constitution     = claim.get("constitution_check", {})

    observed_set = set(observed)
    missing_set  = set(missing)

    # ── observed_state ────────────────────────────────────
    observed_nodes = [
        {
            "state":    s,
            "category": _classify_state(s),
            "source":   "claim.observed_state",
        }
        for s in observed
    ]

    # ── desired_state ─────────────────────────────────────
    desired_nodes = [
        {
            "state":    s,
            "category": _classify_state(s),
            "met":      s in observed_set and s not in missing_set,
            "source":   "claim.required_state",
        }
        for s in required
    ]

    # ── state_gap (missing conditions) ────────────────────
    gap_nodes = []
    for cond in missing:
        is_dignity = cond in _DIGNITY_STATES or cond in dignity_cs
        is_risk    = cond in _RISK_STATES
        blocking   = is_dignity or is_risk
        notes      = (
            "DIGNITY-SENSITIVE — must not proceed without resolution"
            if is_dignity else
            "RISK-SENSITIVE — requires safety/legal clearance"
            if is_risk else
            "requires negotiation or contribution to resolve"
        )
        gap_nodes.append({
            "condition": cond,
            "category":  _classify_state(cond),
            "blocking":  blocking,
            "dignity":   is_dignity,
            "risk":      is_risk,
            "notes":     notes,
        })

    # ── dignity surface ───────────────────────────────────
    dignity_surface = [
        {
            "constraint": dc,
            "in_missing": dc in missing_set,
            "in_observed": dc in observed_set,
            "status": (
                "missing"   if dc in missing_set  else
                "observed"  if dc in observed_set else
                "declared"
            ),
        }
        for dc in dignity_cs
    ]

    # ── reality_feedback ──────────────────────────────────
    feedback_events: list[dict[str, Any]] = []
    if include_feedback:
        feedback_events = _feedback_from_sutable(claim_id)

    # ── uncertainty ───────────────────────────────────────
    unc_level = _uncertainty_level(missing, dignity_cs)
    unc_reason_parts = []
    if missing:
        unc_reason_parts.append(f"{len(missing)} missing condition(s)")
    if dignity_cs:
        unc_reason_parts.append(f"{len(dignity_cs)} dignity constraint(s)")
    if constitution.get("violates_dignity"):
        unc_reason_parts.append("constitution check failed")
    unc_reason = "; ".join(unc_reason_parts) if unc_reason_parts else "no gaps identified"

    # ── world model notes ─────────────────────────────────
    notes_parts: list[str] = []
    if decision == "execute":
        notes_parts.append("Claim is in execute phase — world model reflects pre-execution state.")
    elif decision == "negotiate":
        notes_parts.append("Claim is in negotiation — world model shows conditions to resolve.")
    elif decision == "escalate":
        notes_parts.append("Claim is escalated — world model pending human review.")
    elif decision == "reject":
        notes_parts.append("Claim is rejected — world model is a historical record.")

    if gap_nodes:
        blocking = [g["condition"] for g in gap_nodes if g["blocking"]]
        if blocking:
            notes_parts.append(
                f"Blocking conditions: {', '.join(blocking)}. "
                "These must be resolved before execution."
            )

    return {
        "world_model_id":  f"wm-{claim_id}",
        "claim_id":        claim_id,
        "schema_version":  "1.0",
        "generated_from":  "world_model_mapper.py",
        "observed_state":  observed_nodes,
        "desired_state":   desired_nodes,
        "state_gap":       gap_nodes,
        "reality_feedback":feedback_events,
        "uncertainty": {
            "level":         unc_level,
            "reason":        unc_reason,
            "missing_count": len(missing),
            "dignity_count": len(dignity_cs),
        },
        "dignity_surface": dignity_surface,
        "world_model_notes": " ".join(notes_parts) if notes_parts else "No additional notes.",
    }


# ── CLI ────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Map a Dan-Go Claim to an OGI-style world model.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ogi/runtime/world_model_mapper.py ogi/examples/post-scarcity.claim.json
  python ogi/runtime/world_model_mapper.py ogi/examples/post-scarcity.claim.json > ogi/examples/world-model-state.json
  python ogi/runtime/world_model_mapper.py ogi/examples/post-scarcity.claim.json --include-feedback
        """,
    )
    p.add_argument("claim_file", metavar="CLAIM_FILE", nargs="?",
                   help="Path to a Claim JSON file (default: read stdin)")
    p.add_argument("--include-feedback", action="store_true",
                   help="Load reality_feedback events from sutable (if available)")
    p.add_argument("--indent", type=int, default=2,
                   help="JSON indent level (default: 2)")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    if args.claim_file:
        path = Path(args.claim_file)
        if not path.exists():
            print(f"Error: file not found: {path}", file=sys.stderr)
            sys.exit(1)
        with open(path, encoding="utf-8") as f:
            try:
                claim = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error: invalid JSON: {e}", file=sys.stderr)
                sys.exit(1)
    else:
        try:
            claim = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(f"Error: invalid JSON from stdin: {e}", file=sys.stderr)
            sys.exit(1)

    if not isinstance(claim, dict):
        print("Error: claim must be a JSON object.", file=sys.stderr)
        sys.exit(1)

    wm = build_world_model(claim, include_feedback=args.include_feedback)
    print(json.dumps(wm, indent=args.indent, ensure_ascii=False))

    # Human-readable summary to stderr
    print(f"✓ World model: {wm['world_model_id']}", file=sys.stderr)
    print(f"  Observed:    {len(wm['observed_state'])} state(s)", file=sys.stderr)
    print(f"  Desired:     {len(wm['desired_state'])} state(s)", file=sys.stderr)
    print(f"  Gap:         {len(wm['state_gap'])} missing condition(s)", file=sys.stderr)
    print(f"  Uncertainty: {wm['uncertainty']['level']}", file=sys.stderr)
    blocking = [g['condition'] for g in wm['state_gap'] if g['blocking']]
    if blocking:
        print(f"  Blocking:    {', '.join(blocking)}", file=sys.stderr)


if __name__ == "__main__":
    main()
