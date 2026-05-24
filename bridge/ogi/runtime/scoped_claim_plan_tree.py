#!/usr/bin/env python3
"""
scoped_claim_plan_tree.py — Dan-Go / OGI reasoning surface
Scoped prerequisite-aware plan tree generator.

A reasoning surface must plan differently when prerequisite knowledge is scoped.

When a federation prerequisite is applicable for a claim:
  → the plan tree includes a subgoal + branch requiring the condition

When a federation prerequisite is bypassed for a claim:
  → the plan tree includes an audit assertion recording the bypass
  → no local requirement is imposed
  → the bypass evidence is permanently visible in the tree

A bypassed prerequisite is still memory.
It is just not an active requirement in this context.

Hard enforcement: FORBIDDEN.
External network: FORBIDDEN.
Auto-execution: FORBIDDEN.

CLI:
  python ogi/runtime/scoped_claim_plan_tree.py --claim-id housing-006
  python ogi/runtime/scoped_claim_plan_tree.py --claim-id housing-007
  python ogi/runtime/scoped_claim_plan_tree.py --claim-id housing-007 --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# ── Path setup ────────────────────────────────────────────────────────────────
_FILE_DIR    = Path(__file__).parent
_BRIDGE_DIR  = _FILE_DIR.parent.parent
_RUNTIME_DIR = _BRIDGE_DIR / "runtime"

sys.path.insert(0, str(_RUNTIME_DIR))
sys.path.insert(0, str(_FILE_DIR))

# ── Capability map for known prerequisite conditions ─────────────────────────

PREREQUISITE_CAPABILITY: dict[str, str] = {
    "space_safety_assessed":        "safety_review",
    "food_safety_reviewed":         "safety_review",
    "structural_assessment":        "safety_review",
    "local_structural_assessment":  "safety_review",
    "local_safety_review":          "safety_review",
    "external_safety_audit_attached": "safety_review",
    "risk_assessment":              "risk_review",
    "legal_ownership_confirmed":    "legal_review",
    "participant_consent":          "consent_facilitation",
    "revocable_consent":            "consent_facilitation",
    "funding_confirmed":            "funding",
}

# Dignity conditions (always handled as strict branches)
DIGNITY_CONDITIONS: frozenset[str] = frozenset({
    "revocable_consent",
    "no_identity_exposure",
    "participant_consent",
    "consent_established",
})


# ── Plan data loading ─────────────────────────────────────────────────────────

def _load_plan_data(claim_id: str) -> dict[str, Any]:
    """
    Load the latest plan_tree_created event for claim_id from sutable/plans.jsonl.
    Returns a dict with claim info synthesised from plan data.
    """
    try:
        from sutable_log import read_all
        events = [
            e for e in read_all("plans")
            if e.get("claim_id") == claim_id
            and e.get("event_type") == "plan_tree_created"
        ]
        if not events:
            return {}
        ev = events[-1]
        return {
            "claim_id":    claim_id,
            "plan_id":     ev.get("plan_id", f"plan-{claim_id}"),
            "speaker":     ev.get("speaker", "unknown"),
            "statement":   ev.get("plan_tree", {}).get("statement", ""),
            "label":       ev.get("plan_tree", {}).get("label", claim_id),
            "description": ev.get("_description", ""),
            "conditions":  ev.get("plan_tree_conditions", []),
            "scope_context": ev.get("_scope_context", {}),
        }
    except ImportError:
        return {}


# ── Scoped prerequisite loading ───────────────────────────────────────────────

def _load_scoped_inheritance(claim_id: str) -> dict[str, Any]:
    """
    Load scoped prerequisite inheritance for claim_id.
    Returns compute_inheritance() dict or empty dict on failure.
    """
    try:
        from scoped_prerequisite_inheritance import compute_inheritance
        return compute_inheritance(claim_id)
    except ImportError:
        return {}


def _load_scoped_hints(claim_id: str) -> list[dict[str, Any]]:
    """
    Load scoped propagation hints for claim_id.
    Returns a list of hint dicts.
    """
    try:
        from scoped_condition_propagation import get_scoped_propagation_hints
        return get_scoped_propagation_hints(claim_id)
    except ImportError:
        return []


# ── Plan tree node builders ───────────────────────────────────────────────────

def _applicable_prerequisite_subgoal(detail: dict[str, Any]) -> dict[str, Any]:
    """
    Build a subgoal subtree for an APPLICABLE scoped prerequisite.

    Structure:
      subgoal: "satisfy prerequisite: <condition>"
        action: request <capability>
      branch: "is <condition> complete?"
        true:  assertion (condition satisfied)
        false: abstain (plan cannot advance)
    """
    cond       = detail.get("condition", "unknown")
    scope      = detail.get("applies_to_label", "")
    reasoning  = detail.get("scope_reasoning", [])
    capability = PREREQUISITE_CAPABILITY.get(cond, "safety_review")

    subgoal: dict[str, Any] = {
        "node_type": "subgoal",
        "label": f"satisfy prerequisite: {cond}",
        "phase": "scoped_prerequisite",
        "prerequisite_condition": cond,
        "scope_status": "applicable",
        "scope": scope,
        "scope_reasoning": reasoning,
        "advisory": True,
        "note": (
            f"Federation prerequisite '{cond}' is applicable in this context "
            f"(scope: {scope}). No bypass path detected for this claim."
        ),
        "children": [
            {
                "node_type": "action",
                "label": f"request {capability}",
                "required_capability": capability,
                "satisfies_condition": cond,
                "prerequisite_condition": cond,
            }
        ],
    }

    gate_branch: dict[str, Any] = {
        "node_type": "branch",
        "label": f"is '{cond}' complete?",
        "condition": cond,
        "prerequisite_condition": cond,
        "scope_status": "applicable",
        "true": {
            "node_type": "assertion",
            "label": f"{cond} satisfied",
            "state": f"{cond}_complete",
            "prerequisite_condition": cond,
            "scope_status": "applicable",
        },
        "false": {
            "node_type": "abstain",
            "reason": (
                f"plan cannot advance: '{cond}' is an applicable federation "
                f"prerequisite (scope: {scope}) and is not yet satisfied. "
                f"This is not a failure — it is the protocol working correctly."
            ),
        },
    }

    return {"subgoal": subgoal, "branch": gate_branch}


def _bypassed_prerequisite_nodes(detail: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Build plan tree nodes for a BYPASSED scoped prerequisite.

    A bypassed prerequisite is still memory.
    It is just not an active requirement in this context.

    Structure:
      assertion: "<condition> bypassed by scoped prerequisite resolution"
      branch: "is scoped bypass evidence valid?"
        true:  assertion (bypass confirmed)
        false: abstain (bypass insufficient — condition may still apply)
    """
    cond      = detail.get("condition", "unknown")
    bypassing = detail.get("bypass_conditions_found", [])
    labels    = detail.get("bypassed_by_labels", [])
    reasoning = detail.get("scope_reasoning", [])
    scope     = detail.get("applies_to_label", "")

    audit_assertion: dict[str, Any] = {
        "node_type": "assertion",
        "label": f"{cond} bypassed by scoped prerequisite resolution",
        "state": f"{cond}_bypassed",
        "prerequisite_condition": cond,
        "scope_status": "bypassed",
        "scope": scope,
        "bypass_conditions_found": bypassing,
        "bypassed_by_labels": labels,
        "scope_reasoning": reasoning,
        "advisory": True,
        "note": (
            f"A bypassed prerequisite is still memory. "
            f"It is just not an active requirement in this context. "
            f"'{cond}' is scoped to '{scope}' — this claim has bypass conditions: "
            f"{', '.join(bypassing)}."
        ),
    }

    bypass_branch: dict[str, Any] = {
        "node_type": "branch",
        "label": "is scoped bypass evidence valid?",
        "condition": "bypass_evidence_valid",
        "prerequisite_condition": cond,
        "scope_status": "bypassed",
        "true": {
            "node_type": "assertion",
            "label": f"bypass confirmed — '{cond}' not required in this context",
            "state": "bypass_confirmed",
            "prerequisite_condition": cond,
            "scope_status": "bypassed",
            "bypass_path": bypassing,
        },
        "false": {
            "node_type": "abstain",
            "reason": (
                f"bypass evidence for '{cond}' could not be verified — "
                f"condition may still apply. Re-evaluate bypass conditions: "
                f"{', '.join(bypassing)}."
            ),
        },
    }

    return [audit_assertion, bypass_branch]


def _dignity_branch(constraint: str) -> dict[str, Any]:
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


# ── Core plan tree builder ────────────────────────────────────────────────────

def build_scoped_plan_tree(claim_id: str) -> dict[str, Any]:
    """
    Build a scoped prerequisite-aware plan tree for claim_id.

    1. Load plan data (statement, conditions) from plans.jsonl
    2. Load scoped prerequisite inheritance (applicable / bypassed)
    3. Build plan tree with:
       - Dignity clearance (from plan conditions)
       - Scoped prerequisite phase (applicable → branch; bypassed → audit assertion)
       - Coordination conditions (remaining conditions)
       - Terminal/abstain decision branch
    """
    plan_data   = _load_plan_data(claim_id)
    inheritance = _load_scoped_inheritance(claim_id)

    conditions    = plan_data.get("conditions", [])
    statement     = plan_data.get("statement", "") or plan_data.get("description", "")
    label         = plan_data.get("label", claim_id)
    plan_id       = plan_data.get("plan_id", f"plan-{claim_id}")
    scope_context = plan_data.get("scope_context", {})

    applicable_prereqs = inheritance.get("applicable_prerequisites", [])
    bypassed_prereqs   = inheritance.get("bypassed_prerequisites", [])
    applicability_details = {
        d["condition"]: d
        for d in inheritance.get("applicability_details", [])
    }

    children: list[dict[str, Any]] = []

    # ── Phase 0: Dignity clearance ────────────────────────────────────────────
    dignity_conds = [c for c in conditions if c in DIGNITY_CONDITIONS]
    if dignity_conds:
        children.append({
            "node_type": "subgoal",
            "label": "dignity clearance — required before any action",
            "phase": "dignity",
            "note": "All dignity branches must evaluate true before plan proceeds.",
            "children": [_dignity_branch(c) for c in dignity_conds],
        })

    # ── Phase 1: Scoped prerequisite resolution ───────────────────────────────
    scoped_phase_nodes: list[dict[str, Any]] = []

    for cond in applicable_prereqs:
        detail = applicability_details.get(cond, {"condition": cond})
        nodes  = _applicable_prerequisite_subgoal(detail)
        scoped_phase_nodes.append(nodes["subgoal"])
        scoped_phase_nodes.append(nodes["branch"])

    for cond in bypassed_prereqs:
        detail = applicability_details.get(cond, {"condition": cond})
        scoped_phase_nodes.extend(_bypassed_prerequisite_nodes(detail))

    if scoped_phase_nodes:
        children.append({
            "node_type": "subgoal",
            "label": "scoped prerequisite resolution",
            "phase": "scoped_prerequisites",
            "advisory": True,
            "note": (
                f"Applicable: {applicable_prereqs or '(none)'}. "
                f"Bypassed: {bypassed_prereqs or '(none)'}. "
                "Bypassed prerequisites are recorded as audit assertions — "
                "not active requirements."
            ),
            "children": scoped_phase_nodes,
        })

    # ── Phase 2: Coordination conditions ─────────────────────────────────────
    skip = (
        set(DIGNITY_CONDITIONS)
        | set(applicable_prereqs)
        | set(bypassed_prereqs)
        | {"all_required_conditions_met"}
    )
    coord_conds = [c for c in conditions if c not in skip]

    if coord_conds:
        coord_nodes: list[dict[str, Any]] = []
        for cond in coord_conds:
            coord_nodes.append({
                "node_type": "branch",
                "label": f"is '{cond}' established?",
                "condition": cond,
                "true": {
                    "node_type": "assertion",
                    "label": f"{cond} confirmed",
                    "state": cond,
                },
                "false": {
                    "node_type": "abstain",
                    "reason": f"plan cannot advance: '{cond}' not yet established.",
                },
            })
        children.append({
            "node_type": "subgoal",
            "label": "coordination conditions",
            "phase": "coordination",
            "children": coord_nodes,
        })

    # ── Phase 3: Decision branch ──────────────────────────────────────────────
    children.append({
        "node_type": "branch",
        "label": "can claim advance to next phase?",
        "condition": "all_required_conditions_met",
        "true": {
            "node_type": "terminal",
            "label": "ready_for_negotiation",
            "decision": "negotiate",
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
        "plan_tree_id":    f"pt-scoped-{claim_id}",
        "claim_id":        claim_id,
        "source_plan_id":  plan_id,
        "generated_from":  "scoped_claim_plan_tree.py",
        "schema_version":  "1.1",
        "scoped_prerequisites": True,
        "applicable_prerequisites": applicable_prereqs,
        "bypassed_prerequisites":  bypassed_prereqs,
        "scope_context":   scope_context,
        "node_type":       "goal",
        "label":           label,
        "statement":       statement,
        "children":        children,
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

def _print_tree_summary(tree: dict[str, Any]) -> None:
    print(f"\nScoped Plan Tree: {tree['plan_tree_id']}")
    print(f"  claim_id:               {tree['claim_id']}")
    print(f"  source_plan_id:         {tree['source_plan_id']}")
    print(f"  applicable_prerequisites: {tree['applicable_prerequisites'] or '(none)'}")
    print(f"  bypassed_prerequisites:   {tree['bypassed_prerequisites'] or '(none)'}")
    print(f"  schema_version:         {tree['schema_version']}")
    print(f"  children (top-level):   {len(tree.get('children', []))}")
    for ch in tree.get("children", []):
        phase = ch.get("phase", "")
        phase_tag = f"  [{phase}]" if phase else ""
        print(f"    └─ [{ch['node_type']}]{phase_tag} {ch.get('label','')[:60]}")
        for sub in ch.get("children", []):
            stype = sub.get("node_type", "?")
            slabel = sub.get("label", "")[:55]
            scope_st = sub.get("scope_status", "")
            scope_tag = f" [{scope_st}]" if scope_st else ""
            print(f"         └─ [{stype}]{scope_tag} {slabel}")
    print()
    if tree["applicable_prerequisites"]:
        print(f"  APPLICABLE prerequisites (plan must satisfy):")
        for p in tree["applicable_prerequisites"]:
            print(f"    ✓ {p}")
    if tree["bypassed_prerequisites"]:
        print(f"  BYPASSED prerequisites (audit assertion only):")
        for p in tree["bypassed_prerequisites"]:
            print(f"    ⊛ {p}  (not a local requirement — bypass recorded)")
    print()


def main() -> None:
    p = argparse.ArgumentParser(
        description="Build a scoped prerequisite-aware OGI plan tree for a Dan-Go claim.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ogi/runtime/scoped_claim_plan_tree.py --claim-id housing-006
  python ogi/runtime/scoped_claim_plan_tree.py --claim-id housing-007
  python ogi/runtime/scoped_claim_plan_tree.py --claim-id housing-007 --json

Exit codes: 0 on success, 1 on error.
        """,
    )
    p.add_argument("--claim-id", required=True, metavar="CLAIM_ID")
    p.add_argument("--json", action="store_true", dest="json_output",
                   help="Output JSON (default: human-readable summary)")
    p.add_argument("--indent", type=int, default=2)
    args = p.parse_args()

    tree = build_scoped_plan_tree(args.claim_id)

    if args.json_output:
        print(json.dumps(tree, indent=args.indent, ensure_ascii=False))
    else:
        _print_tree_summary(tree)

    print(
        f"✓ Scoped plan tree generated: {tree['plan_tree_id']} "
        f"(applicable: {tree['applicable_prerequisites']}, "
        f"bypassed: {tree['bypassed_prerequisites']})",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
