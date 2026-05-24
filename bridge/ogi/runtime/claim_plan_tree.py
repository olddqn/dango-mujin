#!/usr/bin/env python3
"""
claim_plan_tree.py — dango-gitsea-bridge / OGI reasoning surface

Generate a structured plan tree from a Dan-Go Claim JSON.

A plan tree separates REASONING from LANGUAGE.
  - Language surface  = claim title, statement, manifesto
  - Reasoning surface = plan tree (this module)
  - Execution surface = contribution / task layer (not this module)

Plan trees do NOT execute anything. They propose a structure for negotiation.

Node types:
  goal        — root; the overall desired state transition
  subgoal     — intermediate step toward the goal
  assertion   — observed fact (already true in world state)
  action      — proposed contribution (requires capability, does NOT execute)
  branch      — conditional split (requires true/false children)
  terminal    — leaf; plan is complete (ready_for_negotiation / ready_for_execution)
  abstain     — leaf; plan cannot proceed (execution blocked)

Design rules:
  1. Dignity branches MUST appear before any action nodes.
  2. Every consent/risk condition becomes a branch with an abstain on false.
  3. Action nodes state capability only — they do not call, invoke, or schedule.
  4. Missing conditions with no known capability yield abstain (not error).
  5. The root is always a goal node.
  6. Every tree must have at least one terminal or abstain leaf.

CLI:
  python ogi/runtime/claim_plan_tree.py examples/post-scarcity.claim.json
  python ogi/runtime/claim_plan_tree.py examples/post-scarcity.claim.json > examples/plan-tree.output.json
  python ogi/runtime/claim_plan_tree.py --claim-id post-scarcity-001 < examples/post-scarcity.claim.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


# ── Capability mappings ────────────────────────────────────────

# Maps missing_condition strings → required_capability strings
_CONDITION_TO_CAPABILITY: dict[str, str | None] = {
    "agent_negotiation":             "coordination",
    "transparent_contribution":      "coordination",
    "dignity_constraints":           None,   # handled by dignity branch, not action
    "reality_feedback":              "compute",
    "shared_memory":                 "compute",
    "legal_ownership_confirmed":     "legal_review",
    "owner_consent":                 "legal_review",
    "safety_assessment":             "safety_review",
    "structural_assessment":         "safety_review",
    "participant_consent":           "consent_facilitation",
    "funding_confirmed":             "funding",
    "distribution_ready":            "distribution",
    "translation_complete":          "translation",
    "compute_available":             "compute",
    "local_knowledge_available":     "local_knowledge",
    "verification_complete":         "verification",
}

# Dignity-related conditions that require branch + abstain treatment
_DIGNITY_CONDITIONS: frozenset[str] = frozenset({
    "revocable_consent",
    "no_identity_exposure",
    "fair_participation",
    "automation_requires_consent",
    "consent_established",
    "participant_consent",
    "owner_consent",
})

# Risk-related conditions that require branch + abstain treatment
_RISK_CONDITIONS: frozenset[str] = frozenset({
    "safety_assessment",
    "structural_assessment",
    "legal_review_complete",
    "legal_ownership_confirmed",
})


def _find_capability(condition: str, contributions: list[str]) -> str | None:
    """
    Find the best capability for a missing condition.
    First check the condition-to-capability map, then fall back to
    a direct match in the contributions list.
    """
    mapped = _CONDITION_TO_CAPABILITY.get(condition)
    if mapped and mapped in contributions:
        return mapped
    if mapped:
        return mapped  # return even if not in contributions — validator will catch
    # Direct match
    if condition in contributions:
        return condition
    # Fuzzy: prefix match
    for c in contributions:
        if condition.startswith(c) or c.startswith(condition):
            return c
    return None


def _dignity_branch(constraint: str) -> dict[str, Any]:
    """Build a branch node for a dignity constraint."""
    return {
        "node_type": "branch",
        "label": f"is '{constraint}' established?",
        "condition": constraint,
        "true": {
            "node_type": "assertion",
            "label": f"{constraint} confirmed",
            "state": constraint,
        },
        "false": {
            "node_type": "abstain",
            "reason": (
                f"execution blocked until '{constraint}' is established. "
                "This is not a failure — it is a necessary gate."
            ),
        },
    }


def _risk_branch(condition: str, capability: str | None) -> dict[str, Any]:
    """Build a branch node for a risk/safety condition."""
    true_child: dict[str, Any]
    if capability:
        true_child = {
            "node_type": "action",
            "label": f"request {capability}",
            "required_capability": capability,
            "satisfies_condition": condition,
        }
    else:
        true_child = {
            "node_type": "abstain",
            "reason": f"no known capability can satisfy '{condition}' — escalate to human review",
        }
    return {
        "node_type": "branch",
        "label": f"has '{condition}' been cleared?",
        "condition": condition,
        "true": true_child,
        "false": {
            "node_type": "abstain",
            "reason": f"execution blocked pending '{condition}' clearance",
        },
    }


def build_plan_tree(claim: dict[str, Any]) -> dict[str, Any]:
    """
    Build a plan tree from a Dan-Go Claim dict.

    Returns a plan tree rooted at a goal node.
    The tree encodes reasoning about the claim — not execution.
    """
    claim_id     = claim.get("claim_id", "unknown")
    title        = claim.get("title") or claim.get("statement", "unknown goal")
    statement    = claim.get("statement", "")
    observed     = list(claim.get("observed_state", []))
    required     = list(claim.get("required_state", []))
    missing      = list(claim.get("missing_conditions", []))
    contributions= list(claim.get("possible_contributions", []))
    dignity_cs   = list(claim.get("dignity_constraints", []))
    decision     = claim.get("decision", "negotiate")
    constitution = claim.get("constitution_check", {})

    children: list[dict[str, Any]] = []

    # ── Phase 0: Observed state (assertions) ─────────────────
    if observed:
        obs_nodes = [
            {"node_type": "assertion", "label": f"observed: {s}", "state": s}
            for s in observed
        ]
        children.append({
            "node_type": "subgoal",
            "label": "verify observed world state",
            "phase": "observation",
            "children": obs_nodes,
        })

    # ── Phase 1: Dignity clearance (ALWAYS before actions) ───
    # Rule: dignity branches must precede any action nodes.
    if dignity_cs or any(c in _DIGNITY_CONDITIONS for c in missing):
        dignity_nodes: list[dict[str, Any]] = []

        # Explicit dignity constraints from claim
        for dc in dignity_cs:
            dignity_nodes.append(_dignity_branch(dc))

        # Missing conditions that are dignity-sensitive
        for cond in missing:
            if cond in _DIGNITY_CONDITIONS and cond not in dignity_cs:
                dignity_nodes.append(_dignity_branch(cond))

        if dignity_nodes:
            children.append({
                "node_type": "subgoal",
                "label": "dignity clearance — required before any action",
                "phase": "dignity",
                "note": "All dignity branches must evaluate true before plan proceeds.",
                "children": dignity_nodes,
            })

    # ── Phase 2: Risk / safety clearance ────────────────────
    risk_missing = [c for c in missing if c in _RISK_CONDITIONS]
    if risk_missing:
        risk_nodes: list[dict[str, Any]] = []
        for cond in risk_missing:
            cap = _find_capability(cond, contributions)
            risk_nodes.append(_risk_branch(cond, cap))
        children.append({
            "node_type": "subgoal",
            "label": "risk and safety clearance",
            "phase": "risk",
            "children": risk_nodes,
        })

    # ── Phase 3: Satisfy remaining missing conditions ────────
    non_dignity_non_risk_missing = [
        c for c in missing
        if c not in _DIGNITY_CONDITIONS and c not in _RISK_CONDITIONS
    ]
    if non_dignity_non_risk_missing:
        missing_nodes: list[dict[str, Any]] = []
        for cond in non_dignity_non_risk_missing:
            cap = _find_capability(cond, contributions)
            if cap:
                missing_nodes.append({
                    "node_type": "subgoal",
                    "label": f"satisfy condition: {cond}",
                    "children": [{
                        "node_type": "action",
                        "label": f"request {cap}",
                        "required_capability": cap,
                        "satisfies_condition": cond,
                    }],
                })
            else:
                missing_nodes.append({
                    "node_type": "subgoal",
                    "label": f"satisfy condition: {cond}",
                    "children": [{
                        "node_type": "abstain",
                        "reason": (
                            f"no known contribution can satisfy '{cond}'. "
                            "This requires human negotiation to resolve."
                        ),
                    }],
                })
        children.append({
            "node_type": "subgoal",
            "label": "satisfy missing conditions",
            "phase": "conditions",
            "children": missing_nodes,
        })

    # ── Phase 4: Coordinate available contributions ──────────
    # Show all possible contributions as action proposals
    # (not just the missing-condition ones)
    if contributions:
        action_nodes: list[dict[str, Any]] = []
        for contrib in contributions:
            action_nodes.append({
                "node_type": "action",
                "label": f"propose contribution: {contrib}",
                "required_capability": contrib,
            })
        children.append({
            "node_type": "subgoal",
            "label": "coordinate available contributions",
            "phase": "coordination",
            "note": "Action nodes propose — they do not execute.",
            "children": action_nodes,
        })

    # ── Phase 5: Constitution check ──────────────────────────
    if constitution:
        violates = constitution.get("violates_dignity", False)
        uses_coercion = constitution.get("uses_coercion", False)
        const_note = constitution.get("notes", "")
        if violates or uses_coercion:
            children.append({
                "node_type": "branch",
                "label": "constitution check: does plan violate dignity?",
                "condition": "constitution_pass",
                "true": {
                    "node_type": "abstain",
                    "reason": "plan rejected by constitution: dignity violation or coercion detected",
                },
                "false": {
                    "node_type": "assertion",
                    "label": "constitution check passed",
                    "state": "constitution_pass",
                },
            })
        else:
            children.append({
                "node_type": "assertion",
                "label": "constitution check passed",
                "state": "constitution_pass",
                "note": const_note or "No dignity violations or coercion detected.",
            })

    # ── Phase 6: Decision branch ─────────────────────────────
    terminal_label = (
        "ready_for_execution"   if decision == "execute"  else
        "under_review"          if decision == "escalate" else
        "closed"                if decision == "reject"   else
        "ready_for_negotiation"
    )
    children.append({
        "node_type": "branch",
        "label": "can claim advance to next phase?",
        "condition": "all_required_conditions_met",
        "true": {
            "node_type": "terminal",
            "label": terminal_label,
            "decision": decision,
        },
        "false": {
            "node_type": "abstain",
            "reason": (
                "required conditions not yet met — plan returns to negotiation. "
                "This is not failure. It is the protocol working correctly."
            ),
        },
    })

    return {
        "plan_tree_id":    f"pt-{claim_id}",
        "claim_id":        claim_id,
        "generated_from":  "claim_plan_tree.py",
        "schema_version":  "1.0",
        "node_type":       "goal",
        "label":           title,
        "statement":       statement,
        "children":        children,
    }


# ── CLI ────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Generate a structured plan tree from a Dan-Go Claim JSON.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ogi/runtime/claim_plan_tree.py ogi/examples/post-scarcity.claim.json
  python ogi/runtime/claim_plan_tree.py ogi/examples/post-scarcity.claim.json > ogi/examples/plan-tree.output.json
  python ogi/runtime/claim_plan_tree.py ogi/examples/plan-tree.claim.json
        """,
    )
    p.add_argument("claim_file", metavar="CLAIM_FILE", nargs="?",
                   help="Path to a Claim JSON file (default: read stdin)")
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

    tree = build_plan_tree(claim)
    print(json.dumps(tree, indent=args.indent, ensure_ascii=False))
    print(f"✓ Plan tree generated: {tree['plan_tree_id']}", file=sys.stderr)


if __name__ == "__main__":
    main()
