#!/usr/bin/env python3
"""
task_dependency_resolver.py — dango-gitsea-bridge / OGI task dependency analysis

Build a dependency graph from a task bundle and resolve execution order.

A task bundle produced by plan_tree_to_tasks.py may contain tasks with
blocked_by references. This module:

  1. Builds a directed dependency graph (task_id → set of prerequisite task_ids)
  2. Detects circular dependencies (a plan tree extractor should never produce them,
     but this layer guards against malformed bundles)
  3. Computes a topological execution order (prerequisites first)
  4. Identifies immediately executable tasks (no unresolved prerequisites)

This module does NOT execute tasks. It only models dependencies.

Dependency semantics:
  blocked_by: [A, B] means this task CANNOT start until A and B are resolved.
  A task with no blocked_by (or an empty list) is immediately executable.

CLI:
  python ogi/runtime/task_dependency_resolver.py ogi/examples/plan-to-task.output.json
  python ogi/runtime/task_dependency_resolver.py ogi/examples/plan-to-task.output.json --json
  python ogi/runtime/task_dependency_resolver.py ogi/examples/plan-to-task.output.json --order
  python ogi/runtime/task_dependency_resolver.py ogi/examples/plan-to-task.output.json --check
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import deque
from pathlib import Path
from typing import Any


# ── Dependency graph builder ───────────────────────────────────────────────────

def build_dependency_graph(
    tasks: list[dict[str, Any]],
) -> dict[str, set[str]]:
    """
    Build a dependency graph from a list of task dicts.

    Returns:
        Dict mapping task_id → set of task_ids it depends on (prerequisites).
        A task with an empty set is immediately executable.

    Raises:
        ValueError if a blocked_by reference points to a non-existent task_id.
    """
    all_ids = {t["task_id"] for t in tasks}
    graph: dict[str, set[str]] = {t["task_id"]: set() for t in tasks}

    for task in tasks:
        task_id    = task["task_id"]
        blocked_by = task.get("blocked_by", [])
        for prereq in blocked_by:
            if prereq not in all_ids:
                raise ValueError(
                    f"task '{task_id}' blocked_by unknown task_id '{prereq}'"
                )
            graph[task_id].add(prereq)

    return graph


def detect_cycle(graph: dict[str, set[str]]) -> list[str] | None:
    """
    Detect a cycle in the dependency graph using DFS.

    Returns:
        A list of task_ids forming the cycle, or None if no cycle exists.
        The list is in cycle order (last element → first element closes the cycle).
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {node: WHITE for node in graph}
    parent: dict[str, str | None] = {node: None for node in graph}

    def dfs(node: str) -> list[str] | None:
        color[node] = GRAY
        for neighbor in graph[node]:
            if color[neighbor] == GRAY:
                # Cycle found — reconstruct it
                cycle: list[str] = [neighbor]
                cur = node
                while cur != neighbor:
                    cycle.append(cur)
                    par = parent[cur]
                    if par is None:
                        break
                    cur = par
                cycle.append(neighbor)
                cycle.reverse()
                return cycle
            if color[neighbor] == WHITE:
                parent[neighbor] = node
                result = dfs(neighbor)
                if result is not None:
                    return result
        color[node] = BLACK
        return None

    for node in graph:
        if color[node] == WHITE:
            result = dfs(node)
            if result is not None:
                return result
    return None


def topological_sort(
    graph: dict[str, set[str]],
) -> list[str]:
    """
    Compute a topological execution order using Kahn's algorithm (BFS).

    Returns:
        A list of task_ids in execution order (prerequisites before dependents).
        Tasks with equal priority appear in lexicographic order for determinism.

    Raises:
        ValueError if a cycle is detected (graph is not a DAG).
    """
    # Build in-degree counts
    in_degree: dict[str, int] = {node: 0 for node in graph}
    # Build reverse adjacency: who depends on node?
    reverse: dict[str, list[str]] = {node: [] for node in graph}

    for node, prereqs in graph.items():
        in_degree[node] += len(prereqs)
        for prereq in prereqs:
            reverse[prereq].append(node)

    # Start with nodes that have no prerequisites (sorted for determinism)
    queue: deque[str] = deque(sorted(
        n for n, d in in_degree.items() if d == 0
    ))
    order: list[str] = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for dependent in sorted(reverse[node]):
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    if len(order) != len(graph):
        raise ValueError(
            "Cycle detected during topological sort — dependency graph is not a DAG"
        )

    return order


def immediately_executable(graph: dict[str, set[str]]) -> list[str]:
    """
    Return task_ids with no prerequisites (can start immediately).

    Returns:
        Sorted list of task_ids with empty dependency sets.
    """
    return sorted(node for node, deps in graph.items() if not deps)


# ── Resolution report ──────────────────────────────────────────────────────────

def resolve(
    bundle: dict[str, Any],
) -> dict[str, Any]:
    """
    Resolve dependencies in a task bundle and produce a resolution report.

    Args:
        bundle: Task bundle dict as produced by plan_tree_to_tasks.py.

    Returns:
        Resolution report dict with:
          - dependency_graph: task_id → sorted list of prerequisites
          - execution_order: topological order list
          - immediately_executable: tasks with no prerequisites
          - cycle_detected: bool
          - cycle_path: list of task_ids forming cycle, or null
          - is_valid: bool (True if no cycles and all references resolved)
          - errors: list of error strings (empty if is_valid)
    """
    tasks  = bundle.get("tasks", [])
    errors: list[str] = []
    cycle_path: list[str] | None = None
    exec_order: list[str] = []
    immediate:  list[str] = []
    graph: dict[str, set[str]] = {}

    # Build graph
    try:
        graph = build_dependency_graph(tasks)
    except ValueError as exc:
        errors.append(str(exc))

    if not errors:
        # Check for cycles
        cycle_path = detect_cycle(graph)
        if cycle_path:
            errors.append(f"circular dependency: {' → '.join(cycle_path)}")
        else:
            try:
                exec_order = topological_sort(graph)
            except ValueError as exc:
                errors.append(str(exc))
            immediate = immediately_executable(graph)

    # Serialise graph (sets → sorted lists)
    graph_serialisable = {k: sorted(v) for k, v in graph.items()}

    return {
        "bundle_id":             bundle.get("bundle_id", "unknown"),
        "is_valid":              len(errors) == 0,
        "errors":                errors,
        "cycle_detected":        cycle_path is not None,
        "cycle_path":            cycle_path,
        "dependency_graph":      graph_serialisable,
        "execution_order":       exec_order,
        "immediately_executable": immediate,
        "task_count":            len(tasks),
    }


# ── CLI ────────────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="task_dependency_resolver",
        description="Resolve dependencies in a Dan-Go task bundle.",
    )
    p.add_argument(
        "bundle",
        metavar="BUNDLE_FILE",
        nargs="?",
        help="Path to task bundle JSON file. Reads stdin if omitted.",
    )
    p.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output full resolution report as JSON.",
    )
    p.add_argument(
        "--order",
        action="store_true",
        default=False,
        help="Print execution order list only.",
    )
    p.add_argument(
        "--check",
        action="store_true",
        default=False,
        help="Exit 0 if valid (no cycles), exit 1 if invalid.",
    )
    return p.parse_args()


def _load(path: str | None) -> dict[str, Any]:
    try:
        raw = Path(path).read_text(encoding="utf-8") if path else sys.stdin.read()
        return json.loads(raw)
    except FileNotFoundError:
        print(f"task_dependency_resolver: file not found: {path}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as exc:
        print(f"task_dependency_resolver: invalid JSON — {exc}", file=sys.stderr)
        sys.exit(2)


def _print_report(report: dict[str, Any]) -> None:
    status = "✓ valid" if report["is_valid"] else "✗ INVALID"
    print(f"Bundle: {report['bundle_id']}  [{status}]")
    print(f"Tasks:  {report['task_count']}")

    if report["errors"]:
        print("\nErrors:")
        for e in report["errors"]:
            print(f"  ✗ {e}")

    if report.get("cycle_detected"):
        print(f"\nCycle: {' → '.join(report['cycle_path'])}")

    imm = report.get("immediately_executable", [])
    if imm:
        print(f"\nImmediately executable ({len(imm)}):")
        for tid in imm:
            print(f"  → {tid}")

    order = report.get("execution_order", [])
    if order:
        print(f"\nExecution order ({len(order)} tasks):")
        for i, tid in enumerate(order, 1):
            deps = report["dependency_graph"].get(tid, [])
            dep_str = f"  [needs: {', '.join(deps)}]" if deps else ""
            print(f"  {i:2d}. {tid}{dep_str}")


def main() -> None:
    args   = _parse_args()
    bundle = _load(args.bundle)
    report = resolve(bundle)

    if args.check:
        sys.exit(0 if report["is_valid"] else 1)
    elif args.order:
        for tid in report.get("execution_order", []):
            print(tid)
    elif args.json or not sys.stdout.isatty():
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        _print_report(report)

    if not report["is_valid"] and not args.order:
        sys.exit(1)


if __name__ == "__main__":
    main()
