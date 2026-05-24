"""
scoped_plan_to_issue.py — Scoped Plan Tree → Gitlawb Issue Draft

Reads a scoped OGI plan tree (output of scoped_claim_plan_tree.py) and
produces issue drafts for applicable prerequisites and suppression records
for bypassed prerequisites.

Core rules:
  applicable prerequisite  → issue draft generated (advisory, contestable)
  bypassed prerequisite    → issue suppressed (bypass recorded, not issued)
  weakened prerequisite    → scope note added to issue body
  deprecated prerequisite  → issue suppressed (lifecycle ended)

"A scoped issue is not a command. It is a negotiation invitation."

No real issue is created. No API is called. No funds move. stdlib only.

Usage:
  python gitlawb/runtime/scoped_plan_to_issue.py <scoped-plan.json>
  python gitlawb/runtime/scoped_plan_to_issue.py <scoped-plan.json> --json
  python gitlawb/runtime/scoped_plan_to_issue.py <scoped-plan.json> --all
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

# ── Path setup ────────────────────────────────────────────────────────────────
_FILE_DIR    = Path(__file__).parent
_BRIDGE_DIR  = _FILE_DIR.parent.parent
_RUNTIME_DIR = _BRIDGE_DIR / "runtime"
sys.path.insert(0, str(_RUNTIME_DIR))

# ── Capability map ────────────────────────────────────────────────────────────
CONDITION_CAPABILITY: dict[str, list[str]] = {
    "space_safety_assessed":         ["safety_review", "evidence_checking"],
    "food_safety_reviewed":          ["safety_review", "evidence_checking"],
    "structural_assessment":         ["safety_review", "structural_review"],
    "local_structural_assessment":   ["safety_review", "structural_review"],
    "local_safety_review":           ["safety_review"],
    "risk_assessment":               ["risk_review", "evidence_checking"],
    "legal_ownership_confirmed":     ["legal_review"],
    "participant_consent":           ["consent_facilitation"],
}

DEFAULT_CAPABILITY = ["evidence_checking"]

# ── Prerequisite status loader ────────────────────────────────────────────────

def _load_prereq_status(condition: str) -> dict[str, Any]:
    """Load prerequisite snapshot status for a condition. Graceful fallback."""
    try:
        from prerequisite_snapshot import get_prerequisite_status
        snap = get_prerequisite_status(condition)
        return snap or {}
    except (ImportError, Exception):
        return {}


# ── Tree walker: extract scoped prerequisite nodes ────────────────────────────

def _walk_scoped_nodes(node: Any, seen: dict[str, dict]) -> None:
    """
    Recursively walk a plan tree and collect unique prerequisite_condition entries.
    Priority: first occurrence wins for scope_status.
    """
    if not isinstance(node, dict):
        return

    prereq_cond  = node.get("prerequisite_condition")
    scope_status = node.get("scope_status")

    if prereq_cond and scope_status and prereq_cond not in seen:
        seen[prereq_cond] = {
            "condition":             prereq_cond,
            "scope_status":          scope_status,
            "scope":                 node.get("scope", ""),
            "bypass_conditions_found": node.get("bypass_conditions_found", []),
            "scope_reasoning":       node.get("scope_reasoning", []),
            "bypass_path":           node.get("bypass_path", []),
            "note":                  node.get("note", ""),
        }

    for child in node.get("children", []):
        _walk_scoped_nodes(child, seen)
    for key in ("true", "false"):
        if key in node:
            _walk_scoped_nodes(node[key], seen)


def extract_scoped_conditions(tree: dict[str, Any]) -> dict[str, dict]:
    """
    Extract all unique prerequisite conditions from a scoped plan tree.
    Returns { condition: { scope_status, scope, bypass_conditions_found, ... } }
    """
    seen: dict[str, dict] = {}
    _walk_scoped_nodes(tree, seen)

    # Also use the root-level metadata as a source of truth
    for cond in tree.get("applicable_prerequisites", []):
        if cond not in seen:
            seen[cond] = {"condition": cond, "scope_status": "applicable",
                          "scope": "", "bypass_conditions_found": [],
                          "scope_reasoning": [], "bypass_path": [], "note": ""}

    for cond in tree.get("bypassed_prerequisites", []):
        if cond not in seen:
            seen[cond] = {"condition": cond, "scope_status": "bypassed",
                          "scope": "", "bypass_conditions_found": [],
                          "scope_reasoning": [], "bypass_path": [], "note": ""}

    return seen


# ── Issue body builder ────────────────────────────────────────────────────────

def _build_issue_body(
    claim_id: str,
    condition: str,
    scope_info: dict,
    prereq_snap: dict,
    tree: dict,
) -> str:
    scope        = scope_info.get("scope", "")
    reasoning    = scope_info.get("scope_reasoning", [])
    status       = prereq_snap.get("status", "unknown")
    contestable  = prereq_snap.get("contestable", True)
    convergence  = prereq_snap.get("evidence_claims_count", "?")
    reaffirmed   = prereq_snap.get("reaffirm_count", 0)
    statement    = tree.get("statement", "")
    source_plan  = tree.get("source_plan_id", "unknown")

    scope_line = f"**Scope:** `{scope}`" if scope else "**Scope:** (universal)"
    reasoning_block = "\n".join(f"  - {r}" for r in reasoning) if reasoning else "  (none)"
    contestable_line = "Yes — any claim can contest by producing a better plan tree." if contestable else "No"

    body = f"""## Scoped Prerequisite: `{condition}`

**Claim:** {claim_id}
**Active plan:** {source_plan}
{scope_line}

### Why This Issue Exists

`{condition}` is a federation prerequisite in state `{status}`.
It was discovered independently by {convergence} claim(s) through structural plan tree diff.
It has been reaffirmed {reaffirmed} time(s).

This issue is generated because `{condition}` is **applicable** for {claim_id}.
No bypass path was detected. The condition must be actively satisfied.

### Scope Reasoning

{reasoning_block}

### How to Resolve

1. Gather evidence that `{condition}` is satisfied.
2. Open a PR attaching the evidence.
3. A peer agent or human reviews the PR.
4. On merge, append a `plan_correction` event to update the plan tree.
5. A merged PR is advisory — it does not auto-satisfy the condition.

### Claim Statement

{statement or '_No statement recorded._'}

### Contestability

**Contestable:** {contestable_line}

To contest: produce a plan tree that addresses the safety concern behind
`{condition}` via an alternative path (equivalent safety evidence).
If accepted, the prerequisite will be weakened and scoped.

---
_This issue draft was generated by Dan-Go scoped_plan_to_issue.py._
_No authority. No coordinator. Evidence only._
_A scoped issue is not a command. It is a negotiation invitation._
_authority: none · advisory · execution_allowed: false · moves_money: false_"""

    return body


# ── Core: generate issue candidate ───────────────────────────────────────────

def generate_issue_candidate(
    tree: dict[str, Any],
    condition: str,
    scope_info: dict,
) -> dict[str, Any]:
    """
    Generate a single issue candidate from a scoped plan tree condition.
    Applicable → issue draft. Bypassed → suppression record.
    """
    claim_id     = tree.get("claim_id", "unknown")
    scope_status = scope_info.get("scope_status", "unknown")
    scope        = scope_info.get("scope", "")
    bypassing    = scope_info.get("bypass_conditions_found", [])
    prereq_snap  = _load_prereq_status(condition)
    prereq_state = prereq_snap.get("status", "unknown")
    contestable  = prereq_snap.get("contestable", True)
    deprecated   = prereq_snap.get("deprecated", False)
    capabilities = CONDITION_CAPABILITY.get(condition, DEFAULT_CAPABILITY)

    # ── Suppression cases ─────────────────────────────────────────────────────
    if scope_status == "bypassed":
        return {
            "issue_candidate":    False,
            "claim_id":           claim_id,
            "condition":          condition,
            "scope_status":       "bypassed",
            "reason":             "prerequisite bypassed by scoped resolution",
            "bypass_conditions":  bypassing,
            "scope":              scope,
            "advisory":           True,
            "markdown_renderable": True,
        }

    if deprecated:
        return {
            "issue_candidate":    False,
            "claim_id":           claim_id,
            "condition":          condition,
            "scope_status":       scope_status,
            "reason":             "prerequisite deprecated — lifecycle ended",
            "advisory":           True,
            "markdown_renderable": True,
        }

    # ── Issue draft for applicable prerequisite ───────────────────────────────
    labels = ["dan-go", "scoped-prerequisite", "dignity-first", "contestable"]
    if prereq_state == "weakened":
        labels.append("weakened-prerequisite")
    if prereq_state in ("promoted", "reaffirmed", "weakened"):
        labels.append("federation-prerequisite")

    body = _build_issue_body(claim_id, condition, scope_info, prereq_snap, tree)

    return {
        "issue_candidate":    True,
        "claim_id":           claim_id,
        "condition":          condition,
        "scope_status":       "applicable",
        "scope":              scope,
        "prerequisite_state": prereq_state,
        "title": f"[Scoped Prerequisite] {condition} required — {claim_id}",
        "body":               body,
        "labels":             labels,
        "assignees":          [],
        "negotiation_context": {
            "contestable":       contestable,
            "authority":         "none",
            "source":            "federation_prerequisite_" + prereq_state,
            "prerequisite_state": prereq_state,
            "scope":             scope,
            "hard_enforcement":  False,
            "negotiation_reopen_allowed": True,
        },
        "agent_task_hint": {
            "task_type":             "safety_review" if "safety" in condition else "evidence_review",
            "required_capabilities": capabilities,
            "scope_status":          "applicable",
            "execution_allowed":     False,
            "reason":                "requires human/agent negotiation before execution",
        },
        "execution_allowed":   False,
        "moves_money":         False,
        "advisory":            True,
        "markdown_renderable": True,
    }


def issues_from_scoped_tree(tree: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Generate all issue candidates from a scoped plan tree.
    Returns one record per unique prerequisite condition.
    """
    scoped_conds = extract_scoped_conditions(tree)
    results = []
    for cond, scope_info in sorted(scoped_conds.items()):
        results.append(generate_issue_candidate(tree, cond, scope_info))
    return results


# ── CLI ───────────────────────────────────────────────────────────────────────

def _print_result(r: dict) -> None:
    candidate = r.get("issue_candidate", False)
    cond      = r.get("condition", "?")
    claim_id  = r.get("claim_id", "?")
    icon      = "✓" if candidate else "⊗"
    print(f"\n  {icon}  condition: {cond}   claim: {claim_id}")
    if candidate:
        print(f"     scope_status:       {r.get('scope_status')}")
        print(f"     scope:              {r.get('scope', '(none)')}")
        print(f"     prerequisite_state: {r.get('prerequisite_state')}")
        print(f"     title:              {r.get('title','')}")
        print(f"     labels:             {r.get('labels',[])}")
        nc = r.get("negotiation_context", {})
        print(f"     contestable:        {nc.get('contestable')}")
        print(f"     hard_enforcement:   {nc.get('hard_enforcement')}")
        print(f"     negotiation_reopen: {nc.get('negotiation_reopen_allowed')}")
        print(f"     execution_allowed:  {r.get('execution_allowed')}")
        print(f"     moves_money:        {r.get('moves_money')}")
    else:
        print(f"     SUPPRESSED — {r.get('reason','')}")
        if r.get("bypass_conditions"):
            print(f"     bypass_conditions:  {r['bypass_conditions']}")


def main() -> None:
    p = argparse.ArgumentParser(
        description="Generate Gitlawb issue drafts from a scoped OGI plan tree.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gitlawb/runtime/scoped_plan_to_issue.py ogi/examples/scoped-plan-housing-006.output.json
  python gitlawb/runtime/scoped_plan_to_issue.py ogi/examples/scoped-plan-housing-007.output.json
  python gitlawb/runtime/scoped_plan_to_issue.py ogi/examples/scoped-plan-housing-007.output.json --json
        """,
    )
    p.add_argument("tree_file", metavar="TREE_FILE")
    p.add_argument("--json",    action="store_true", dest="json_output")
    p.add_argument("--all",     action="store_true",
                   help="Include suppressed records in output")
    args = p.parse_args()

    if not os.path.exists(args.tree_file):
        print(f"ERROR: file not found: {args.tree_file}", file=sys.stderr)
        sys.exit(1)

    with open(args.tree_file) as f:
        tree = json.load(f)

    results = issues_from_scoped_tree(tree)

    if not args.all:
        display = results
    else:
        display = results

    if args.json_output:
        if len(display) == 1:
            print(json.dumps(display[0], indent=2))
        else:
            print(json.dumps(display, indent=2))
        for r in results:
            status = "ISSUE DRAFT" if r["issue_candidate"] else "SUPPRESSED"
            print(f"  {r.get('condition','?')}: {status}", file=sys.stderr)
        return

    claim_id = tree.get("claim_id", "?")
    print(f"\nScoped Plan → Issue Draft Generator")
    print(f"Input:   {args.tree_file}")
    print(f"Claim:   {claim_id}")
    print(f"Results: {len(results)} condition(s)")
    print(f"(No real issue created — draft only)")
    for r in display:
        _print_result(r)
    print()

    issued    = sum(1 for r in results if r["issue_candidate"])
    suppressed = sum(1 for r in results if not r["issue_candidate"])
    print(f"  Summary: {issued} issue draft(s) · {suppressed} suppressed")
    print()


if __name__ == "__main__":
    main()
