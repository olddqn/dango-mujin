#!/usr/bin/env python3
"""
plan_tree_to_tasks.py — dango-gitsea-bridge / OGI task bundle extractor

Extract a task bundle from a validated plan tree.

A plan tree proposes reasoning — a task bundle proposes what to negotiate.
This module is the bridge between the reasoning surface and the execution surface.

  Language surface   → claim statement  (natural language)
  Reasoning surface  → plan tree        (claim_plan_tree.py)
  Task bundle        → THIS MODULE      (negotiable task candidates)
  Execution surface  → contributions    (sutable/contributions.jsonl — NOT this module)

Core extraction rules:
  action node      → executable task candidate
  branch (dignity) → synthetic condition_gate task (priority=0, execution_allowed=True)
  branch (risk)    → real task that is also a dependency gate (priority=0)
  subgoal          → task_group label only (no task)
  abstain          → blocked_record (execution_allowed=False, no task)
  terminal         → sets bundle_status (not a task)
  assertion        → no task (fact already true in world state)

Dependency gate rules:
  dignity gates  → always execution_allowed=True (parallel, independent)
  risk gates     → blocked_by=[dignity_gate_ids]
  regular tasks  → blocked_by=[all_dignity_gates + all_risk_gates]

Priority scheme (lower = higher priority):
  0 — condition_gate / consent / risk / legal / safety
  1 — coordination / negotiation
  2 — distribution / compute / translation / local_knowledge / care / funding
  3 — feedback / reality_feedback

Bundle status:
  fully_blocked     — all tasks have execution_allowed=False
  partially_blocked — some tasks blocked, some executable
  ready             — no tasks blocked (all gates resolved)
  <terminal.decision> — set from plan tree terminal node (e.g. "negotiate")

CLI:
  python ogi/runtime/plan_tree_to_tasks.py ogi/examples/plan-tree.output.json
  python ogi/runtime/plan_tree_to_tasks.py ogi/examples/plan-tree.output.json > out.json
  python ogi/runtime/plan_tree_to_tasks.py ogi/examples/plan-tree.output.json --json
  python ogi/runtime/plan_tree_to_tasks.py ogi/examples/plan-tree.output.json --show-blocked
  python ogi/runtime/plan_tree_to_tasks.py --summary ogi/examples/plan-tree.output.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# ── Priority table ─────────────────────────────────────────────────────────────

_CAPABILITY_PRIORITY: dict[str, int] = {
    "condition_gate":       0,
    "legal_review":         0,
    "safety_review":        0,
    "consent_facilitation": 0,
    "risk_review":          0,
    "verification":         0,
    "coordination":         1,
    "negotiation":          1,
    "compute":              2,
    "code":                 2,
    "translation":          2,
    "local_knowledge":      2,
    "care":                 2,
    "distribution":         2,
    "funding":              2,
    "feedback":             3,
    "reality_feedback":     3,
}

_PHASE_PRIORITY_OVERRIDE: dict[str, int] = {
    "dignity": 0,
    "risk":    0,
}


def _priority(capability: str, phase: str | None) -> int:
    if phase and phase in _PHASE_PRIORITY_OVERRIDE:
        return _PHASE_PRIORITY_OVERRIDE[phase]
    return _CAPABILITY_PRIORITY.get(capability, 2)


def _slugify(s: str) -> str:
    return s.lower().replace("_", "-").replace(" ", "-")


# ── TaskExtractor ──────────────────────────────────────────────────────────────

class TaskExtractor:
    """
    Stateful walker that converts a plan tree into a task bundle.

    Usage:
        extractor = TaskExtractor()
        bundle    = extractor.extract(plan_tree_dict)
    """

    def __init__(self) -> None:
        self._tasks:           list[dict[str, Any]] = []
        self._blocked_records: list[dict[str, Any]] = []
        self._bundle_state:    dict[str, Any]       = {"status": "pending"}
        self._dignity_gates:   list[str]            = []
        self._risk_gates:      list[str]            = []
        self._counter:         int                  = 0
        self._seen_gate_ids:   set[str]             = set()

    # ── Public ────────────────────────────────────────────────────────────────

    def extract(self, tree: dict[str, Any]) -> dict[str, Any]:
        """
        Walk a plan tree and return a task bundle dict.

        Args:
            tree: Validated plan tree JSON dict (root node must be 'goal').

        Returns:
            Task bundle with tasks, blocked_records, bundle_status, and metadata.
        """
        if tree.get("node_type") != "goal":
            raise ValueError(
                f"plan_tree_to_tasks: root node_type must be 'goal', got {tree.get('node_type')!r}"
            )

        self._walk_goal(tree)

        # Compute bundle_status from task state + terminal decision
        terminal_decision = self._bundle_state.get("terminal_decision")
        tasks = self._tasks
        n_total    = len(tasks)
        n_blocked  = sum(1 for t in tasks if not t.get("execution_allowed", True))
        n_gates    = sum(1 for t in tasks if t.get("task_type") == "condition_gate")

        if n_total == 0:
            bundle_status = "empty"
        elif n_blocked == n_total:
            bundle_status = "fully_blocked"
        elif n_blocked > 0:
            bundle_status = "partially_blocked"
        elif terminal_decision:
            bundle_status = terminal_decision
        else:
            bundle_status = "ready"

        return {
            "bundle_id":        f"bundle-{tree.get('claim_id', 'unknown')}",
            "plan_tree_id":     tree.get("plan_tree_id", f"pt-{tree.get('claim_id', 'unknown')}"),
            "claim_id":         tree.get("claim_id", "unknown"),
            "generated_from":   "plan_tree_to_tasks.py",
            "schema_version":   "1.0",
            "bundle_status":    bundle_status,
            "terminal_decision": terminal_decision,
            "summary": {
                "task_count":         n_total,
                "executable_count":   n_total - n_blocked,
                "blocked_count":      n_blocked,
                "gate_count":         n_gates,
                "dignity_gate_count": len(self._dignity_gates),
                "risk_gate_count":    len(self._risk_gates),
            },
            "dignity_gates": list(self._dignity_gates),
            "risk_gates":    list(self._risk_gates),
            "tasks":         self._tasks,
            "blocked_records": self._blocked_records,
        }

    # ── Walk methods ──────────────────────────────────────────────────────────

    def _walk_goal(self, node: dict[str, Any]) -> None:
        """Walk a goal node's children phase by phase."""
        children = node.get("children", [])

        # Separate subgoal phases from top-level non-subgoal nodes
        # Process them in order, accumulating dignity/risk gates between phases.
        for child in children:
            nt = child.get("node_type", "")
            if nt == "subgoal":
                phase = child.get("phase")
                if phase == "dignity":
                    self._walk_dignity_phase(child)
                elif phase == "risk":
                    self._walk_risk_phase(child)
                elif phase in ("conditions", "coordination", "observation"):
                    self._walk_regular_phase(child, phase)
                else:
                    # Unknown phase — treat as regular with all accumulated gates
                    self._walk_regular_phase(child, phase)
            elif nt == "branch":
                self._walk_top_level_branch(child)
            elif nt == "assertion":
                pass  # top-level assertion: no task
            elif nt == "terminal":
                self._bundle_state["terminal_decision"] = child.get("decision", "ready")
                self._bundle_state["terminal_label"]    = child.get("label", "")
            elif nt == "abstain":
                self._blocked_records.append(self._make_abstain_record(child, None))

    def _walk_dignity_phase(self, subgoal: dict[str, Any]) -> None:
        """
        Walk dignity subgoal.
        Each branch produces an independent condition_gate task (no cross-blocking).
        All resulting gate IDs are accumulated into self._dignity_gates.
        """
        group = subgoal.get("label", "dignity")
        for child in subgoal.get("children", []):
            nt = child.get("node_type", "")
            if nt == "branch":
                self._process_dignity_branch(child, "dignity", group)
            elif nt == "subgoal":
                self._walk_dignity_phase(child)  # nested dignity subgoal
            elif nt == "abstain":
                self._blocked_records.append(self._make_abstain_record(child, "dignity"))
            # assertions: no task

    def _process_dignity_branch(
        self,
        node: dict[str, Any],
        phase: str,
        group: str,
    ) -> None:
        """
        Process a dignity branch.
        true=assertion  → synthetic condition_gate task (execution_allowed=True, no blocked_by)
        false=abstain   → blocked_record
        """
        condition   = node.get("condition", "")
        true_child  = node.get("true", {})
        false_child = node.get("false", {})

        if true_child.get("node_type") == "assertion":
            gate_id = f"task-gate-{_slugify(condition)}"
            if gate_id not in self._seen_gate_ids:
                self._seen_gate_ids.add(gate_id)
                gate_task: dict[str, Any] = {
                    "task_id":           gate_id,
                    "task_type":         "condition_gate",
                    "condition":         condition,
                    "group":             group,
                    "phase":             phase,
                    "execution_allowed": True,
                    "priority":          0,
                    "note": (
                        f"Dignity gate: '{condition}' must be established "
                        "before downstream tasks may proceed."
                    ),
                }
                self._tasks.append(gate_task)
                self._dignity_gates.append(gate_id)

        if false_child.get("node_type") == "abstain":
            self._blocked_records.append(
                self._make_abstain_record(false_child, phase, condition)
            )

    def _walk_risk_phase(self, subgoal: dict[str, Any]) -> None:
        """
        Walk risk subgoal.
        Each branch produces a task blocked by dignity gates (but not by sibling risk gates).
        All resulting gate IDs are accumulated into self._risk_gates.
        """
        group = subgoal.get("label", "risk")
        for child in subgoal.get("children", []):
            nt = child.get("node_type", "")
            if nt == "branch":
                self._process_risk_branch(child, "risk", group)
            elif nt == "subgoal":
                self._walk_risk_phase(child)  # nested risk subgoal
            elif nt == "abstain":
                self._blocked_records.append(self._make_abstain_record(child, "risk"))

    def _process_risk_branch(
        self,
        node: dict[str, Any],
        phase: str,
        group: str,
    ) -> None:
        """
        Process a risk branch.
        true=action  → real task (priority=0) blocked by dignity gates only
        true=abstain → blocked_record (no capability to satisfy condition)
        false=abstain → blocked_record
        """
        condition   = node.get("condition", "")
        true_child  = node.get("true", {})
        false_child = node.get("false", {})

        if true_child.get("node_type") == "action":
            capability   = true_child.get("required_capability", "unknown")
            satisfies    = true_child.get("satisfies_condition", condition)
            gate_id      = f"task-gate-{_slugify(condition)}"

            if gate_id not in self._seen_gate_ids:
                self._seen_gate_ids.add(gate_id)
                gate_task: dict[str, Any] = {
                    "task_id":             gate_id,
                    "task_type":           capability,
                    "required_capability": capability,
                    "condition":           condition,
                    "satisfies_condition": satisfies,
                    "group":               group,
                    "phase":               phase,
                    "execution_allowed":   len(self._dignity_gates) == 0,
                    "priority":            0,
                    "note": (
                        f"Risk gate: '{condition}' must be cleared "
                        "before downstream tasks may proceed."
                    ),
                }
                if self._dignity_gates:
                    gate_task["blocked_by"]     = list(self._dignity_gates)
                    gate_task["blocked_reason"] = "dignity_gate_not_resolved"

                self._tasks.append(gate_task)
                self._risk_gates.append(gate_id)

        elif true_child.get("node_type") == "abstain":
            # No capability — escalate
            self._blocked_records.append(
                self._make_abstain_record(true_child, phase, condition)
            )

        if false_child.get("node_type") == "abstain":
            self._blocked_records.append(
                self._make_abstain_record(false_child, phase, condition)
            )

    def _walk_regular_phase(
        self,
        subgoal: dict[str, Any],
        phase: str | None,
    ) -> None:
        """
        Walk a non-dignity, non-risk subgoal.
        All tasks are blocked by all accumulated dignity + risk gates.
        """
        group      = subgoal.get("label", phase or "coordination")
        all_gates  = list(self._dignity_gates) + list(self._risk_gates)

        for child in subgoal.get("children", []):
            self._walk_node_regular(child, phase, group, all_gates)

    def _walk_node_regular(
        self,
        node: dict[str, Any],
        phase: str | None,
        group: str | None,
        gates: list[str],
    ) -> None:
        """
        Walk a single node in a regular (non-dignity, non-risk) context.
        """
        nt = node.get("node_type", "")

        if nt == "goal":
            for child in node.get("children", []):
                self._walk_node_regular(child, phase, group, gates)

        elif nt == "subgoal":
            child_phase = node.get("phase", phase)
            child_group = node.get("label", group)
            if child_phase == "dignity":
                self._walk_dignity_phase(node)
            elif child_phase == "risk":
                self._walk_risk_phase(node)
            else:
                # Recurse into nested subgoal with current gate list
                for grandchild in node.get("children", []):
                    self._walk_node_regular(grandchild, child_phase, child_group, gates)

        elif nt == "action":
            task = self._make_action_task(node, phase, group, gates)
            self._tasks.append(task)

        elif nt == "branch":
            condition  = node.get("condition", "")
            true_child = node.get("true", {})
            false_child = node.get("false", {})
            true_type   = true_child.get("node_type", "")

            if true_type == "terminal":
                # Decision branch
                self._bundle_state["terminal_decision"] = true_child.get("decision", "ready")
                self._bundle_state["terminal_label"]    = true_child.get("label", "")
                if false_child.get("node_type") == "abstain":
                    record = self._make_abstain_record(false_child, phase, condition)
                    record["record_type"] = "bundle_blocked"
                    self._blocked_records.append(record)

            elif true_type == "assertion":
                # Dignity gate encountered outside dignity phase — treat as gate
                self._process_dignity_branch(node, phase or "dignity", group or "")

            elif true_type == "action":
                # Risk gate encountered outside risk phase — treat as risk gate
                self._process_risk_branch(node, phase or "risk", group or "")

            elif true_type == "abstain":
                # Both paths blocked
                if false_child.get("node_type") == "abstain":
                    self._blocked_records.append(
                        self._make_abstain_record(false_child, phase, condition)
                    )
                self._blocked_records.append(
                    self._make_abstain_record(true_child, phase, condition)
                )

            else:
                # Generic branch — walk true path
                self._walk_node_regular(true_child, phase, group, gates)
                if false_child.get("node_type") == "abstain":
                    self._blocked_records.append(
                        self._make_abstain_record(false_child, phase, condition)
                    )

        elif nt == "assertion":
            pass  # already true, no task

        elif nt == "abstain":
            self._blocked_records.append(self._make_abstain_record(node, phase))

        elif nt == "terminal":
            self._bundle_state["terminal_decision"] = node.get("decision", "ready")
            self._bundle_state["terminal_label"]    = node.get("label", "")

    def _walk_top_level_branch(self, node: dict[str, Any]) -> None:
        """
        Handle a branch that is a direct child of the goal node (not inside a subgoal).
        Typically this is the final decision branch (all_required_conditions_met).
        """
        condition   = node.get("condition", "")
        true_child  = node.get("true", {})
        false_child = node.get("false", {})
        true_type   = true_child.get("node_type", "")

        if true_type == "terminal":
            self._bundle_state["terminal_decision"] = true_child.get("decision", "ready")
            self._bundle_state["terminal_label"]    = true_child.get("label", "")
            if false_child.get("node_type") == "abstain":
                record = self._make_abstain_record(false_child, None, condition)
                record["record_type"] = "bundle_blocked"
                self._blocked_records.append(record)

        elif true_type == "assertion":
            self._process_dignity_branch(node, "dignity", "")

        elif true_type == "action":
            self._process_risk_branch(node, "risk", "")

        elif true_type == "abstain":
            self._blocked_records.append(self._make_abstain_record(true_child, None, condition))
            if false_child.get("node_type") == "abstain":
                self._blocked_records.append(
                    self._make_abstain_record(false_child, None, condition)
                )

    # ── Task factory helpers ───────────────────────────────────────────────────

    def _make_action_task(
        self,
        node: dict[str, Any],
        phase: str | None,
        group: str | None,
        gates: list[str],
    ) -> dict[str, Any]:
        capability = node.get("required_capability", "unknown")
        self._counter += 1
        slug = _slugify(capability)
        tid  = f"task-{slug}-{self._counter:03d}"
        pri  = _priority(capability, phase)

        task: dict[str, Any] = {
            "task_id":             tid,
            "task_type":           capability,
            "required_capability": capability,
            "group":               group or phase or "coordination",
            "phase":               phase or "coordination",
            "execution_allowed":   len(gates) == 0,
            "priority":            pri,
        }
        if node.get("satisfies_condition"):
            task["satisfies_condition"] = node["satisfies_condition"]
        if node.get("label"):
            task["label"] = node["label"]
        if gates:
            task["blocked_by"]     = list(gates)
            task["blocked_reason"] = "upstream_gate_not_resolved"
        return task

    def _make_abstain_record(
        self,
        node: dict[str, Any],
        phase: str | None,
        condition: str | None = None,
    ) -> dict[str, Any]:
        record: dict[str, Any] = {
            "record_type":       "abstain",
            "execution_allowed": False,
            "reason":            node.get("reason", "execution blocked"),
        }
        if phase:
            record["phase"] = phase
        if condition:
            record["condition"] = condition
        return record


# ── Module-level convenience function ─────────────────────────────────────────

def extract_task_bundle(tree: dict[str, Any]) -> dict[str, Any]:
    """
    Extract a task bundle from a plan tree dict.

    Args:
        tree: Plan tree JSON dict.

    Returns:
        Task bundle dict.

    Raises:
        ValueError if root node_type is not 'goal'.
    """
    return TaskExtractor().extract(tree)


# ── CLI ────────────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="plan_tree_to_tasks",
        description="Extract a task bundle from a Dan-Go plan tree JSON.",
    )
    p.add_argument(
        "plan_tree",
        metavar="PLAN_TREE_FILE",
        nargs="?",
        help="Path to plan tree JSON file. Reads stdin if omitted.",
    )
    p.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output full bundle JSON (default when stdout is not a terminal).",
    )
    p.add_argument(
        "--summary",
        action="store_true",
        default=False,
        help="Print a human-readable summary only.",
    )
    p.add_argument(
        "--show-blocked",
        action="store_true",
        default=False,
        help="Include blocked_records in text output.",
    )
    return p.parse_args()


def _load_tree(path: str | None) -> dict[str, Any]:
    try:
        if path:
            raw = Path(path).read_text(encoding="utf-8")
        else:
            raw = sys.stdin.read()
        return json.loads(raw)
    except FileNotFoundError:
        print(f"plan_tree_to_tasks: file not found: {path}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as exc:
        print(f"plan_tree_to_tasks: invalid JSON — {exc}", file=sys.stderr)
        sys.exit(2)


_PRIORITY_LABELS = {0: "P0-critical", 1: "P1-coordination", 2: "P2-standard", 3: "P3-feedback"}
_STATUS_SYMBOLS  = {True: "✓", False: "✗"}


def _print_summary(bundle: dict[str, Any], show_blocked: bool) -> None:
    summary = bundle.get("summary", {})
    print(f"Bundle:  {bundle['bundle_id']}")
    print(f"Status:  {bundle['bundle_status']}")
    if bundle.get("terminal_decision"):
        print(f"Terminal decision: {bundle['terminal_decision']}")
    print(
        f"Tasks:   {summary.get('task_count', 0)} total  "
        f"({summary.get('executable_count', 0)} executable / "
        f"{summary.get('blocked_count', 0)} blocked)"
    )
    print(
        f"Gates:   {summary.get('dignity_gate_count', 0)} dignity  "
        f"{summary.get('risk_gate_count', 0)} risk"
    )
    print()

    tasks = bundle.get("tasks", [])
    if tasks:
        # Group by priority
        by_pri: dict[int, list[dict]] = {}
        for t in tasks:
            p = t.get("priority", 2)
            by_pri.setdefault(p, []).append(t)

        for pri in sorted(by_pri):
            label = _PRIORITY_LABELS.get(pri, f"P{pri}")
            print(f"── {label} ──────────────────────────")
            for t in by_pri[pri]:
                ok       = t.get("execution_allowed", True)
                sym      = _STATUS_SYMBOLS[ok]
                tid      = t["task_id"]
                ttype    = t.get("task_type", "?")
                phase    = t.get("phase", "?")
                sat      = t.get("satisfies_condition", "")
                sat_str  = f"  → satisfies:{sat}" if sat else ""
                print(f"  {sym} [{phase}] {tid}  ({ttype}){sat_str}")
                if not ok:
                    blocked_by = t.get("blocked_by", [])
                    print(f"      blocked_by: {blocked_by}")
        print()

    if show_blocked:
        records = bundle.get("blocked_records", [])
        if records:
            print(f"── Blocked records ({len(records)}) ──────────────────────────")
            for r in records:
                cond   = r.get("condition", "")
                cond_s = f"[{cond}] " if cond else ""
                phase  = r.get("phase", "")
                ph_s   = f"({phase}) " if phase else ""
                rtype  = r.get("record_type", "abstain")
                reason = r.get("reason", "")
                print(f"  ✗ {rtype}  {ph_s}{cond_s}")
                if reason:
                    # Truncate long reason strings
                    print(f"      {reason[:80]}{'…' if len(reason)>80 else ''}")
            print()

    dg = bundle.get("dignity_gates", [])
    rg = bundle.get("risk_gates", [])
    if dg:
        print(f"Dignity gates : {dg}")
    if rg:
        print(f"Risk gates    : {rg}")


def main() -> None:
    args = _parse_args()
    tree = _load_tree(args.plan_tree)

    try:
        bundle = extract_task_bundle(tree)
    except ValueError as exc:
        print(f"plan_tree_to_tasks: {exc}", file=sys.stderr)
        sys.exit(1)

    # Output mode
    json_mode    = args.json or not sys.stdout.isatty()
    summary_mode = args.summary

    if summary_mode:
        _print_summary(bundle, args.show_blocked)
    elif json_mode:
        print(json.dumps(bundle, indent=2, ensure_ascii=False))
    else:
        _print_summary(bundle, args.show_blocked)


if __name__ == "__main__":
    main()
