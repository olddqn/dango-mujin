#!/usr/bin/env python3
"""
task_bundle_validator.py — dango-gitsea-bridge / OGI task bundle validation

Validate the structure and constraints of a task bundle.

A valid task bundle must satisfy:
  1. Has required top-level fields: bundle_id, plan_tree_id, tasks
  2. All task dicts have required fields: task_id, task_type, execution_allowed, priority
  3. task_id values are unique within the bundle
  4. blocked_by references only existing task_ids
  5. condition_gate tasks have execution_allowed=True
  6. condition_gate tasks have priority=0
  7. No circular dependencies (calls task_dependency_resolver)
  8. At least one task exists
  9. dignity_gates listed in bundle metadata exist in tasks as condition_gate type
 10. risk_gates listed in bundle metadata exist in tasks
 11. All blocked tasks have at least one entry in blocked_by
 12. execution_allowed=False tasks all have a blocked_reason

Exit codes:
  0 — valid
  1 — invalid
  2 — error (bad JSON, missing file, etc.)

CLI:
  python ogi/runtime/task_bundle_validator.py ogi/examples/plan-to-task.output.json
  python ogi/runtime/task_bundle_validator.py ogi/examples/plan-to-task.output.json --json
  python ogi/runtime/task_bundle_validator.py ogi/examples/plan-to-task.output.json --strict
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Import dependency resolver for cycle detection
try:
    from task_dependency_resolver import build_dependency_graph, detect_cycle
except ImportError:
    # Allow running from any directory
    import importlib.util
    _here = Path(__file__).parent
    _spec = importlib.util.spec_from_file_location(
        "task_dependency_resolver",
        _here / "task_dependency_resolver.py",
    )
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    build_dependency_graph = _mod.build_dependency_graph
    detect_cycle = _mod.detect_cycle


# ── Validation result ──────────────────────────────────────────────────────────

_REQUIRED_BUNDLE_FIELDS = {"bundle_id", "plan_tree_id", "tasks"}
_REQUIRED_TASK_FIELDS   = {"task_id", "task_type", "execution_allowed", "priority"}


@dataclass
class BundleValidationResult:
    is_valid:   bool
    errors:     list[str] = field(default_factory=list)
    warnings:   list[str] = field(default_factory=list)
    task_count: int = 0

    # Structural stats
    gate_count:          int = 0
    dignity_gate_count:  int = 0
    risk_gate_count:     int = 0
    blocked_count:       int = 0
    executable_count:    int = 0
    has_cycle:           bool = False
    cycle_path:          list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_valid":          self.is_valid,
            "errors":            self.errors,
            "warnings":          self.warnings,
            "task_count":        self.task_count,
            "gate_count":        self.gate_count,
            "dignity_gate_count": self.dignity_gate_count,
            "risk_gate_count":   self.risk_gate_count,
            "blocked_count":     self.blocked_count,
            "executable_count":  self.executable_count,
            "has_cycle":         self.has_cycle,
            "cycle_path":        self.cycle_path,
        }


# ── Core validator ─────────────────────────────────────────────────────────────

def validate_bundle(
    bundle:  dict[str, Any],
    strict:  bool = False,
) -> BundleValidationResult:
    """
    Validate a task bundle dict.

    Args:
        bundle: Task bundle dict as produced by plan_tree_to_tasks.py.
        strict: If True, warnings become errors.

    Returns:
        BundleValidationResult with is_valid, errors, warnings, and stats.
    """
    result = BundleValidationResult(is_valid=True)

    # ── Check 1: Required top-level fields ────────────────────────────────────
    missing_fields = _REQUIRED_BUNDLE_FIELDS - bundle.keys()
    if missing_fields:
        result.errors.append(
            f"missing required bundle fields: {sorted(missing_fields)}"
        )
        result.is_valid = False

    tasks = bundle.get("tasks", [])
    if not isinstance(tasks, list):
        result.errors.append("'tasks' must be a list")
        result.is_valid = False
        tasks = []

    result.task_count = len(tasks)

    # ── Check 2: At least one task ────────────────────────────────────────────
    if result.task_count == 0:
        result.warnings.append("task bundle has no tasks (empty plan?)")

    # ── Check 3: Required task fields ─────────────────────────────────────────
    task_ids: set[str] = set()
    duplicate_ids: list[str] = []

    for i, task in enumerate(tasks):
        if not isinstance(task, dict):
            result.errors.append(f"tasks[{i}] is not a dict")
            result.is_valid = False
            continue

        missing = _REQUIRED_TASK_FIELDS - task.keys()
        if missing:
            tid = task.get("task_id", f"tasks[{i}]")
            result.errors.append(
                f"task '{tid}' missing required fields: {sorted(missing)}"
            )
            result.is_valid = False

        tid = task.get("task_id", "")
        if tid in task_ids:
            duplicate_ids.append(tid)
        else:
            task_ids.add(tid)

    if duplicate_ids:
        result.errors.append(f"duplicate task_ids: {duplicate_ids}")
        result.is_valid = False

    # ── Check 4: blocked_by references ────────────────────────────────────────
    for task in tasks:
        if not isinstance(task, dict):
            continue
        tid        = task.get("task_id", "?")
        blocked_by = task.get("blocked_by", [])
        if not isinstance(blocked_by, list):
            result.errors.append(f"task '{tid}': blocked_by must be a list")
            result.is_valid = False
            continue
        for ref in blocked_by:
            if ref not in task_ids:
                result.errors.append(
                    f"task '{tid}' blocked_by unknown task_id '{ref}'"
                )
                result.is_valid = False

    # ── Check 5 & 6: condition_gate constraints ────────────────────────────────
    for task in tasks:
        if not isinstance(task, dict):
            continue
        tid   = task.get("task_id", "?")
        ttype = task.get("task_type", "")
        if ttype == "condition_gate":
            result.gate_count += 1
            if not task.get("execution_allowed", False):
                result.errors.append(
                    f"condition_gate task '{tid}' has execution_allowed=False "
                    "(dignity gates must always be independently executable)"
                )
                result.is_valid = False
            if task.get("priority", -1) != 0:
                result.errors.append(
                    f"condition_gate task '{tid}' has priority={task.get('priority')} "
                    "(dignity gates must have priority=0)"
                )
                result.is_valid = False

    # ── Check 7: Circular dependency detection ────────────────────────────────
    if tasks and result.is_valid:
        try:
            graph      = build_dependency_graph(tasks)
            cycle_path = detect_cycle(graph)
            if cycle_path:
                result.has_cycle  = True
                result.cycle_path = cycle_path
                result.errors.append(
                    f"circular dependency: {' → '.join(cycle_path)}"
                )
                result.is_valid = False
        except ValueError as exc:
            result.errors.append(f"dependency graph error: {exc}")
            result.is_valid = False

    # ── Check 8: dignity_gates metadata consistency ───────────────────────────
    declared_dignity = bundle.get("dignity_gates", [])
    declared_risk    = bundle.get("risk_gates", [])

    for dgid in declared_dignity:
        matching = [t for t in tasks if isinstance(t, dict) and t.get("task_id") == dgid]
        if not matching:
            result.warnings.append(
                f"dignity_gate '{dgid}' listed in bundle metadata but not found in tasks"
            )
        elif matching[0].get("task_type") != "condition_gate":
            result.warnings.append(
                f"dignity_gate '{dgid}' has task_type "
                f"'{matching[0].get('task_type')}' instead of 'condition_gate'"
            )
        result.dignity_gate_count += 1

    for rgid in declared_risk:
        matching = [t for t in tasks if isinstance(t, dict) and t.get("task_id") == rgid]
        if not matching:
            result.warnings.append(
                f"risk_gate '{rgid}' listed in bundle metadata but not found in tasks"
            )
        result.risk_gate_count += 1

    # ── Check 9 & 10: blocked task consistency ────────────────────────────────
    for task in tasks:
        if not isinstance(task, dict):
            continue
        tid   = task.get("task_id", "?")
        exe   = task.get("execution_allowed", True)
        bby   = task.get("blocked_by", [])
        breason = task.get("blocked_reason", "")

        if exe:
            result.executable_count += 1
        else:
            result.blocked_count += 1
            if not bby and task.get("task_type") != "condition_gate":
                result.warnings.append(
                    f"task '{tid}' has execution_allowed=False but empty blocked_by"
                )
            if not breason and strict:
                result.errors.append(
                    f"task '{tid}' has execution_allowed=False but no blocked_reason"
                )
                result.is_valid = False
            elif not breason:
                result.warnings.append(
                    f"task '{tid}' has execution_allowed=False but no blocked_reason"
                )

    # Promote warnings to errors in strict mode
    if strict and result.warnings:
        result.errors.extend([f"[strict] {w}" for w in result.warnings])
        result.is_valid = False

    return result


# ── CLI ────────────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="task_bundle_validator",
        description="Validate a Dan-Go task bundle JSON.",
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
        help="Output validation result as JSON.",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Treat warnings as errors.",
    )
    return p.parse_args()


def _load(path: str | None) -> dict[str, Any]:
    try:
        raw = Path(path).read_text(encoding="utf-8") if path else sys.stdin.read()
        return json.loads(raw)
    except FileNotFoundError:
        print(f"task_bundle_validator: file not found: {path}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as exc:
        print(f"task_bundle_validator: invalid JSON — {exc}", file=sys.stderr)
        sys.exit(2)


def _print_result(result: BundleValidationResult) -> None:
    status = "✓ VALID" if result.is_valid else "✗ INVALID"
    print(f"Bundle validation: {status}")
    print(
        f"Tasks: {result.task_count}  "
        f"(executable={result.executable_count}  blocked={result.blocked_count}  "
        f"gates={result.gate_count})"
    )
    print(
        f"Gates: {result.dignity_gate_count} dignity  {result.risk_gate_count} risk"
    )

    if result.errors:
        print(f"\nErrors ({len(result.errors)}):")
        for e in result.errors:
            print(f"  ✗ {e}")

    if result.warnings:
        print(f"\nWarnings ({len(result.warnings)}):")
        for w in result.warnings:
            print(f"  ⚠ {w}")

    if result.has_cycle:
        print(f"\nCycle: {' → '.join(result.cycle_path)}")


def main() -> None:
    args   = _parse_args()
    bundle = _load(args.bundle)
    result = validate_bundle(bundle, strict=args.strict)

    if args.json or not sys.stdout.isatty():
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    else:
        _print_result(result)

    sys.exit(0 if result.is_valid else 1)


if __name__ == "__main__":
    main()
