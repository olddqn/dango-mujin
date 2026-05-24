#!/usr/bin/env python3
"""
scoped_plan_comparison.py — Compare two scoped plan trees

Shows how two claims differ in their prerequisite applicability:
  - applicable prerequisites (require active subgoal)
  - bypassed prerequisites (recorded as audit assertion only)
  - inserted scoped prerequisite subgoals
  - inserted abstain branches
  - audit assertions

CLI:
  python ogi/runtime/scoped_plan_comparison.py \\
    ogi/examples/scoped-plan-housing-006.output.json \\
    ogi/examples/scoped-plan-housing-007.output.json

  python ogi/runtime/scoped_plan_comparison.py \\
    ogi/examples/scoped-plan-housing-006.output.json \\
    ogi/examples/scoped-plan-housing-007.output.json --json

No external libraries. stdlib only. Read-only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


# ── Tree walker ───────────────────────────────────────────────────────────────

def _walk_nodes(node: Any, collector: dict[str, list]) -> None:
    """Recursively walk a plan tree and collect typed nodes."""
    if not isinstance(node, dict):
        return

    node_type    = node.get("node_type", "")
    label        = node.get("label", "")
    prereq_cond  = node.get("prerequisite_condition")
    scope_status = node.get("scope_status")
    phase        = node.get("phase", "")

    if node_type == "subgoal" and phase == "scoped_prerequisites":
        collector["scoped_phases"].append(label)

    if node_type == "subgoal" and prereq_cond and scope_status == "applicable":
        collector["applicable_subgoals"].append({
            "label":     label,
            "condition": prereq_cond,
            "scope":     node.get("scope", ""),
        })

    if node_type == "assertion" and prereq_cond and scope_status == "bypassed":
        collector["bypassed_assertions"].append({
            "label":            label,
            "condition":        prereq_cond,
            "bypass_conditions": node.get("bypass_conditions_found", []),
            "scope":            node.get("scope", ""),
        })

    if node_type == "branch" and scope_status == "applicable" and prereq_cond:
        collector["applicable_branches"].append({
            "label":     label,
            "condition": prereq_cond,
        })

    if node_type == "branch" and scope_status == "bypassed":
        collector["bypass_branches"].append({
            "label":     label,
            "condition": prereq_cond or node.get("condition", ""),
        })

    if node_type == "abstain":
        collector["abstain_nodes"].append(node.get("reason", "")[:80])

    if node_type == "action" and prereq_cond:
        collector["prerequisite_actions"].append({
            "label":      label,
            "capability": node.get("required_capability", ""),
            "condition":  prereq_cond,
        })

    # Recurse
    for child in node.get("children", []):
        _walk_nodes(child, collector)
    for key in ("true", "false"):
        if key in node:
            _walk_nodes(node[key], collector)


def extract_scoped_features(tree: dict[str, Any]) -> dict[str, Any]:
    """Extract scoped prerequisite features from a plan tree."""
    collector: dict[str, list] = {
        "scoped_phases":         [],
        "applicable_subgoals":   [],
        "bypassed_assertions":   [],
        "applicable_branches":   [],
        "bypass_branches":       [],
        "abstain_nodes":         [],
        "prerequisite_actions":  [],
    }
    _walk_nodes(tree, collector)
    return {
        "plan_tree_id":          tree.get("plan_tree_id", "unknown"),
        "claim_id":              tree.get("claim_id", "unknown"),
        "applicable_prerequisites": tree.get("applicable_prerequisites", []),
        "bypassed_prerequisites":  tree.get("bypassed_prerequisites", []),
        "scoped_prerequisites":    tree.get("scoped_prerequisites", False),
        "schema_version":          tree.get("schema_version", "1.0"),
        "node_features":          collector,
    }


# ── Comparison ────────────────────────────────────────────────────────────────

def compare_trees(tree_a: dict[str, Any], tree_b: dict[str, Any]) -> dict[str, Any]:
    """
    Compare two scoped plan trees.
    Shows applicable/bypassed prerequisite differences and structural differences.
    """
    feat_a = extract_scoped_features(tree_a)
    feat_b = extract_scoped_features(tree_b)

    appl_a = set(feat_a["applicable_prerequisites"])
    appl_b = set(feat_b["applicable_prerequisites"])
    byp_a  = set(feat_a["bypassed_prerequisites"])
    byp_b  = set(feat_b["bypassed_prerequisites"])

    all_prereqs = appl_a | appl_b | byp_a | byp_b

    per_prereq: list[dict[str, Any]] = []
    for cond in sorted(all_prereqs):
        status_a = (
            "applicable" if cond in appl_a else
            "bypassed"   if cond in byp_a  else
            "not_scoped"
        )
        status_b = (
            "applicable" if cond in appl_b else
            "bypassed"   if cond in byp_b  else
            "not_scoped"
        )
        per_prereq.append({
            "condition":                  cond,
            feat_a["claim_id"]:           status_a,
            feat_b["claim_id"]:           status_b,
            "diverges":                   status_a != status_b,
            "reasoning":                  (
                f"{feat_a['claim_id']} → {status_a}; "
                f"{feat_b['claim_id']} → {status_b}"
            ),
        })

    differences: dict[str, Any] = {
        "only_applicable_in_a": sorted(appl_a - appl_b),
        "only_applicable_in_b": sorted(appl_b - appl_a),
        "only_bypassed_in_a":   sorted(byp_a - byp_b),
        "only_bypassed_in_b":   sorted(byp_b - byp_a),
        "applicable_in_both":   sorted(appl_a & appl_b),
        "bypassed_in_both":     sorted(byp_a & byp_b),
    }

    return {
        "comparison_id":  f"cmp-{feat_a['claim_id']}-vs-{feat_b['claim_id']}",
        "claim_a":        feat_a["claim_id"],
        "claim_b":        feat_b["claim_id"],
        "plan_tree_a":    feat_a["plan_tree_id"],
        "plan_tree_b":    feat_b["plan_tree_id"],
        "per_prerequisite": per_prereq,
        "differences":    differences,
        "structural": {
            feat_a["claim_id"]: {
                "applicable_subgoals":  feat_a["node_features"]["applicable_subgoals"],
                "bypassed_assertions":  feat_a["node_features"]["bypassed_assertions"],
                "applicable_branches":  feat_a["node_features"]["applicable_branches"],
                "bypass_branches":      feat_a["node_features"]["bypass_branches"],
                "prerequisite_actions": feat_a["node_features"]["prerequisite_actions"],
                "abstain_count":        len(feat_a["node_features"]["abstain_nodes"]),
            },
            feat_b["claim_id"]: {
                "applicable_subgoals":  feat_b["node_features"]["applicable_subgoals"],
                "bypassed_assertions":  feat_b["node_features"]["bypassed_assertions"],
                "applicable_branches":  feat_b["node_features"]["applicable_branches"],
                "bypass_branches":      feat_b["node_features"]["bypass_branches"],
                "prerequisite_actions": feat_b["node_features"]["prerequisite_actions"],
                "abstain_count":        len(feat_b["node_features"]["abstain_nodes"]),
            },
        },
        "key_insight": (
            "A bypassed prerequisite is still memory. "
            "It is just not an active requirement in this context. "
            f"{feat_a['claim_id']} bypasses {sorted(byp_a)} via equivalent safety path. "
            f"{feat_b['claim_id']} must actively satisfy {sorted(appl_b)}."
        ),
        "advisory": True,
        "hard_enforcement": False,
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

def _print_comparison(cmp: dict[str, Any]) -> None:
    print(f"\n{'='*60}")
    print(f"  Scoped Plan Tree Comparison")
    print(f"  {cmp['claim_a']}  vs  {cmp['claim_b']}")
    print(f"{'='*60}\n")

    print("  Prerequisites per claim:\n")
    for p in cmp["per_prereq"] if "per_prereq" in cmp else cmp["per_prerequisite"]:
        cond    = p["condition"]
        status_a = p[cmp["claim_a"]]
        status_b = p[cmp["claim_b"]]
        divmark = "  ←DIFFERS" if p["diverges"] else ""
        icon_a  = "✓" if status_a == "applicable" else ("⊛" if status_a == "bypassed" else "–")
        icon_b  = "✓" if status_b == "applicable" else ("⊛" if status_b == "bypassed" else "–")
        print(f"  {cond}")
        print(f"    {cmp['claim_a']}: {icon_a} {status_a}")
        print(f"    {cmp['claim_b']}: {icon_b} {status_b}{divmark}")
        print()

    diff = cmp["differences"]
    print("  Structural differences:")
    if diff["only_applicable_in_a"]:
        print(f"    applicable only in {cmp['claim_a']}: {diff['only_applicable_in_a']}")
    if diff["only_applicable_in_b"]:
        print(f"    applicable only in {cmp['claim_b']}: {diff['only_applicable_in_b']}")
    if diff["only_bypassed_in_a"]:
        print(f"    bypassed only in {cmp['claim_a']}: {diff['only_bypassed_in_a']}")
    if diff["only_bypassed_in_b"]:
        print(f"    bypassed only in {cmp['claim_b']}: {diff['only_bypassed_in_b']}")

    print()
    struct = cmp["structural"]
    for claim_id, features in struct.items():
        print(f"  [{claim_id}]")
        if features["applicable_subgoals"]:
            print(f"    applicable subgoals: {[s['condition'] for s in features['applicable_subgoals']]}")
        if features["bypassed_assertions"]:
            print(f"    bypass assertions:   {[s['condition'] for s in features['bypassed_assertions']]}")
        if features["prerequisite_actions"]:
            print(f"    prerequisite actions:{[a['capability'] for a in features['prerequisite_actions']]}")
        print(f"    abstain branches:    {features['abstain_count']}")
        print()

    print(f"  Key insight:\n  {cmp['key_insight']}\n")
    print(f"  advisory: {cmp['advisory']}  hard_enforcement: {cmp['hard_enforcement']}")
    print()


def main() -> None:
    p = argparse.ArgumentParser(
        description="Compare two scoped plan trees.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ogi/runtime/scoped_plan_comparison.py \\
    ogi/examples/scoped-plan-housing-006.output.json \\
    ogi/examples/scoped-plan-housing-007.output.json

  python ogi/runtime/scoped_plan_comparison.py \\
    ogi/examples/scoped-plan-housing-006.output.json \\
    ogi/examples/scoped-plan-housing-007.output.json --json \\
    > ogi/examples/scoped-plan-comparison.json
        """,
    )
    p.add_argument("tree_a", metavar="TREE_A")
    p.add_argument("tree_b", metavar="TREE_B")
    p.add_argument("--json", action="store_true", dest="json_output")
    p.add_argument("--indent", type=int, default=2)
    args = p.parse_args()

    for path in (args.tree_a, args.tree_b):
        if not Path(path).exists():
            print(f"ERROR: file not found: {path}", file=sys.stderr)
            sys.exit(1)

    with open(args.tree_a) as f:
        tree_a = json.load(f)
    with open(args.tree_b) as f:
        tree_b = json.load(f)

    cmp = compare_trees(tree_a, tree_b)

    if args.json_output:
        print(json.dumps(cmp, indent=args.indent, ensure_ascii=False))
    else:
        _print_comparison(cmp)

    print(
        f"✓ Comparison: {cmp['claim_a']} vs {cmp['claim_b']} — "
        f"differs: {[p['condition'] for p in cmp['per_prerequisite'] if p['diverges']]}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
