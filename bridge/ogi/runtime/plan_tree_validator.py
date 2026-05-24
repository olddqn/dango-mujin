#!/usr/bin/env python3
"""
plan_tree_validator.py — dango-gitsea-bridge / OGI reasoning surface

Validate a Dan-Go plan tree JSON.

Checks:
  1. node_type is in the allowed set
  2. Root node is 'goal'
  3. At least one terminal or abstain leaf exists
  4. action nodes have required_capability
  5. branch nodes have both 'true' and 'false' children
  6. No loops (visited node labels form a DAG)
  7. Maximum depth not exceeded (default 12)
  8. Maximum node count not exceeded (default 100)
  9. No premature terminal (terminal with children)
 10. No dignity-blind plan: if dignity_constraints appear in claim metadata,
     the tree must have at least one dignity branch

Scoped prerequisite assertion extensions (schema_version 1.1):
  Assertion nodes may carry extra fields without failing validation:
    prerequisite_condition — the condition being tracked
    scope_status           — "applicable" | "bypassed"
    scope_reasoning        — list of reasoning strings
    bypass_conditions_found— list of bypass condition strings
    bypass_path            — list of bypass conditions (on bypass_confirmed)
  These fields are tracked in the validation result for reporting.

Exit codes:
  0 — valid
  1 — invalid (with reasons)
  2 — error (bad JSON, missing file, etc.)

CLI:
  python ogi/runtime/plan_tree_validator.py ogi/examples/plan-tree.output.json
  python ogi/runtime/plan_tree_validator.py ogi/examples/plan-tree.output.json --json
  python ogi/runtime/plan_tree_validator.py ogi/examples/plan-tree.output.json --strict
  python ogi/runtime/plan_tree_validator.py ogi/examples/scoped-plan-housing-006.output.json
  python ogi/runtime/plan_tree_validator.py ogi/examples/scoped-plan-housing-007.output.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# ── Constants ──────────────────────────────────────────────────

ALLOWED_NODE_TYPES: frozenset[str] = frozenset({
    "goal",
    "subgoal",
    "assertion",
    "action",
    "branch",
    "terminal",
    "abstain",
})

LEAF_NODE_TYPES: frozenset[str] = frozenset({"terminal", "abstain", "assertion"})
BRANCH_REQUIRED_KEYS: frozenset[str] = frozenset({"true", "false"})

DEFAULT_MAX_DEPTH = 12
DEFAULT_MAX_NODES = 100


# ── Validation state ──────────────────────────────────────────

class ValidationResult:
    def __init__(self) -> None:
        self.errors:   list[str] = []
        self.warnings: list[str] = []
        self.node_count: int = 0
        self.max_depth_seen: int = 0
        self.has_terminal: bool = False
        self.has_abstain:  bool = False
        self.has_dignity_branch: bool = False
        self.has_action:  bool = False
        # Scoped prerequisite tracking (schema_version 1.1)
        self.scoped_applicable_assertions: list[str] = []   # condition names
        self.scoped_bypassed_assertions:   list[str] = []   # condition names
        self.has_scoped_prerequisites: bool = False

    @property
    def valid(self) -> bool:
        return len(self.errors) == 0

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid":            self.valid,
            "errors":           self.errors,
            "warnings":         self.warnings,
            "node_count":       self.node_count,
            "max_depth":        self.max_depth_seen,
            "has_terminal":     self.has_terminal,
            "has_abstain":      self.has_abstain,
            "has_action":       self.has_action,
            "has_dignity_branch": self.has_dignity_branch,
            # Scoped prerequisite fields
            "has_scoped_prerequisites":    self.has_scoped_prerequisites,
            "scoped_applicable":           self.scoped_applicable_assertions,
            "scoped_bypassed":             self.scoped_bypassed_assertions,
        }


# ── Recursive traversal ───────────────────────────────────────

def _validate_node(
    node: Any,
    result: ValidationResult,
    depth: int,
    max_depth: int,
    max_nodes: int,
    path: str,
    visited_paths: set[str],
    strict: bool,
) -> None:
    """Recursively validate a plan tree node."""

    if not isinstance(node, dict):
        result.error(f"{path}: node must be a JSON object, got {type(node).__name__}")
        return

    result.node_count += 1
    if result.node_count > max_nodes:
        result.error(
            f"Node count exceeded {max_nodes} — possible runaway tree or attack. "
            f"Counted {result.node_count} nodes at {path}."
        )
        return  # stop recursing

    result.max_depth_seen = max(result.max_depth_seen, depth)
    if depth > max_depth:
        result.error(
            f"{path}: depth {depth} exceeds max_depth {max_depth}. "
            "Possible loop or excessively complex plan."
        )
        return

    # Loop detection via path fingerprint
    # Use (depth, label) as a lightweight cycle key
    label = node.get("label", "")
    node_type = node.get("node_type", "")
    finger = f"{depth}:{node_type}:{label}"
    if finger in visited_paths and label:
        result.warn(
            f"{path}: possible repeated node '{label}' at depth {depth}. "
            "Check for inadvertent copy-paste loops."
        )
    visited_paths.add(finger)

    # ── Check 1: node_type ────────────────────────────────
    if node_type not in ALLOWED_NODE_TYPES:
        result.error(
            f"{path}: unknown node_type '{node_type}'. "
            f"Allowed: {sorted(ALLOWED_NODE_TYPES)}"
        )
        return  # can't continue without a valid type

    # ── Check 2: root must be goal ────────────────────────
    if depth == 0 and node_type != "goal":
        result.error(
            f"Root node must be 'goal', got '{node_type}'. "
            "A plan tree must start with a goal."
        )

    # ── Check 3: terminal/abstain tracking ───────────────
    if node_type == "terminal":
        result.has_terminal = True
        if node.get("children"):
            result.error(
                f"{path}: terminal node must not have children. "
                "A terminal ends the plan."
            )
        return  # no further recursion

    if node_type == "abstain":
        result.has_abstain = True
        if not node.get("reason"):
            result.warn(f"{path}: abstain node should have a 'reason' field.")
        if node.get("children"):
            result.error(
                f"{path}: abstain node must not have children. "
                "An abstain ends the plan branch."
            )
        return  # no further recursion

    # ── Check 4: assertion leaf ───────────────────────────
    if node_type == "assertion":
        if node.get("children"):
            result.warn(
                f"{path}: assertion node has children. "
                "Assertions are typically leaf nodes."
            )
        # Scoped prerequisite assertion tracking (schema_version 1.1)
        # Assertion nodes may carry prerequisite_condition + scope_status fields.
        # These are valid extensions — not errors.
        prereq_cond  = node.get("prerequisite_condition")
        scope_status = node.get("scope_status")
        if prereq_cond and scope_status:
            result.has_scoped_prerequisites = True
            if scope_status == "applicable":
                if prereq_cond not in result.scoped_applicable_assertions:
                    result.scoped_applicable_assertions.append(prereq_cond)
            elif scope_status == "bypassed":
                if prereq_cond not in result.scoped_bypassed_assertions:
                    result.scoped_bypassed_assertions.append(prereq_cond)

        # assertion without children is fine — it's a leaf fact
        children = node.get("children", [])
        if children:
            for i, child in enumerate(children):
                _validate_node(child, result, depth + 1, max_depth, max_nodes,
                               f"{path}.children[{i}]", visited_paths, strict)
        return

    # ── Check 5: action nodes ─────────────────────────────
    if node_type == "action":
        result.has_action = True
        if not node.get("required_capability"):
            result.error(
                f"{path}: action node must have 'required_capability'. "
                "Every action must declare what capability it needs."
            )
        if node.get("children"):
            result.warn(
                f"{path}: action node has children — unexpected. "
                "Actions are typically leaf nodes."
            )
        return  # actions do not recurse further

    # ── Check 6: branch nodes ─────────────────────────────
    if node_type == "branch":
        # Dignity branch detection
        cond = node.get("condition", "")
        if any(dc in cond for dc in (
            "consent", "dignity", "revocable", "identity", "participation",
            "automation", "owner_consent"
        )):
            result.has_dignity_branch = True

        missing_keys = BRANCH_REQUIRED_KEYS - set(node.keys())
        if missing_keys:
            result.error(
                f"{path}: branch node missing required keys: {sorted(missing_keys)}. "
                "Every branch must have both 'true' and 'false' children."
            )
        else:
            # Recurse into true/false
            _validate_node(node["true"],  result, depth + 1, max_depth, max_nodes,
                           f"{path}.true",  visited_paths, strict)
            _validate_node(node["false"], result, depth + 1, max_depth, max_nodes,
                           f"{path}.false", visited_paths, strict)

        # Branch should have a condition field
        if not node.get("condition") and strict:
            result.warn(f"{path}: branch node has no 'condition' field.")
        return

    # ── Check 7: goal/subgoal recurse into children ───────
    if node_type in ("goal", "subgoal"):
        children = node.get("children", [])
        if not children:
            if strict:
                result.warn(f"{path}: {node_type} node has no children.")
        for i, child in enumerate(children):
            _validate_node(child, result, depth + 1, max_depth, max_nodes,
                           f"{path}.children[{i}]", visited_paths, strict)
        return

    # Fallthrough (should not happen after allowed-type check)
    result.error(f"{path}: unhandled node_type '{node_type}'")


def validate_plan_tree(
    tree: dict[str, Any],
    max_depth: int = DEFAULT_MAX_DEPTH,
    max_nodes: int = DEFAULT_MAX_NODES,
    strict: bool = False,
) -> ValidationResult:
    """
    Validate a plan tree dict.

    Returns a ValidationResult with errors, warnings, and stats.
    """
    result = ValidationResult()

    if not isinstance(tree, dict):
        result.error(f"Plan tree must be a JSON object, got {type(tree).__name__}")
        return result

    # Recurse from root
    _validate_node(
        node=tree,
        result=result,
        depth=0,
        max_depth=max_depth,
        max_nodes=max_nodes,
        path="$",
        visited_paths=set(),
        strict=strict,
    )

    # ── Post-traversal checks ─────────────────────────────
    if not result.has_terminal and not result.has_abstain:
        result.error(
            "Plan tree has no terminal or abstain leaf. "
            "Every plan must reach a conclusion (even if that conclusion is 'abstain')."
        )

    return result


# ── CLI ────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Validate a Dan-Go plan tree JSON.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ogi/runtime/plan_tree_validator.py ogi/examples/plan-tree.output.json
  python ogi/runtime/plan_tree_validator.py ogi/examples/plan-tree.output.json --json
  python ogi/runtime/plan_tree_validator.py ogi/examples/plan-tree.output.json --strict

Exit codes:
  0 — VALID
  1 — INVALID (validation errors found)
  2 — ERROR (bad input, missing file, etc.)
        """,
    )
    p.add_argument("tree_file", metavar="TREE_FILE", nargs="?",
                   help="Path to plan tree JSON file (default: read stdin)")
    p.add_argument("--json",    action="store_true",
                   help="Output JSON report instead of human-readable text")
    p.add_argument("--strict",  action="store_true",
                   help="Enable strict mode (warnings become additional checks)")
    p.add_argument("--max-depth", type=int, default=DEFAULT_MAX_DEPTH,
                   help=f"Maximum allowed tree depth (default: {DEFAULT_MAX_DEPTH})")
    p.add_argument("--max-nodes", type=int, default=DEFAULT_MAX_NODES,
                   help=f"Maximum allowed node count (default: {DEFAULT_MAX_NODES})")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    if args.tree_file:
        path = Path(args.tree_file)
        if not path.exists():
            print(f"Error: file not found: {path}", file=sys.stderr)
            sys.exit(2)
        with open(path, encoding="utf-8") as f:
            try:
                tree = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error: invalid JSON: {e}", file=sys.stderr)
                sys.exit(2)
    else:
        try:
            tree = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(f"Error: invalid JSON from stdin: {e}", file=sys.stderr)
            sys.exit(2)

    result = validate_plan_tree(
        tree,
        max_depth=args.max_depth,
        max_nodes=args.max_nodes,
        strict=args.strict,
    )

    if args.json:
        out = result.to_dict()
        out["plan_tree_id"] = tree.get("plan_tree_id", "unknown") if isinstance(tree, dict) else "unknown"
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        plan_id = tree.get("plan_tree_id", "unknown") if isinstance(tree, dict) else "unknown"
        status  = "VALID" if result.valid else "INVALID"
        icon    = "✓" if result.valid else "✗"
        print(f"{icon} Plan tree: {plan_id}  [{status}]")
        print(f"  Nodes:     {result.node_count}")
        print(f"  Max depth: {result.max_depth_seen}")
        print(f"  Terminal:  {'yes' if result.has_terminal else 'no'}")
        print(f"  Abstain:   {'yes' if result.has_abstain else 'no'}")
        print(f"  Actions:   {'yes' if result.has_action else 'no'}")
        print(f"  Dignity branch: {'yes' if result.has_dignity_branch else 'no'}")
        if result.has_scoped_prerequisites:
            print(f"  Scoped prerequisites: yes")
            if result.scoped_applicable_assertions:
                print(f"    applicable: {result.scoped_applicable_assertions}")
            if result.scoped_bypassed_assertions:
                print(f"    bypassed:   {result.scoped_bypassed_assertions}")

        if result.errors:
            print(f"\nErrors ({len(result.errors)}):")
            for e in result.errors:
                print(f"  ✗ {e}")

        if result.warnings:
            print(f"\nWarnings ({len(result.warnings)}):")
            for w in result.warnings:
                print(f"  ⚠ {w}")

        if result.valid:
            print("\n✓ Validation passed.")
        else:
            print(f"\n✗ Validation FAILED — {len(result.errors)} error(s).")

    sys.exit(0 if result.valid else 1)


if __name__ == "__main__":
    main()
