"""
scoped_issue_filter.py — Filter and deduplicate scoped issue candidates

Applies filtering rules to a collection of issue candidates:
  1. Bypass suppression  — bypassed prerequisites are not issued
  2. Deprecation suppression — deprecated prerequisites are not issued
  3. Deduplication — same condition across claims produces one issue per claim
  4. Scope annotation — weakened prerequisites get scope note in labels

Input:  list of issue candidates (from scoped_plan_to_issue.py)
        OR paths to multiple scoped plan trees (--scan-plans)
Output: filtered list with filter_reason for suppressed records

No real issue is created. No API is called. No funds move. stdlib only.

Usage:
  python gitlawb/runtime/scoped_issue_filter.py
  python gitlawb/runtime/scoped_issue_filter.py --scan-plans
  python gitlawb/runtime/scoped_issue_filter.py --json
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
_OGI_EXAMPLES = _BRIDGE_DIR / "ogi" / "examples"
sys.path.insert(0, str(_RUNTIME_DIR))


# ── Filter rules ──────────────────────────────────────────────────────────────

def _apply_filters(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Apply all filter rules to a list of issue candidates.

    Rules (in order):
      1. Bypass suppression: scope_status=bypassed → suppress
      2. Deprecation suppression: prerequisite_state=deprecated → suppress
      3. Scope annotation: prerequisite_state=weakened → add scope-annotated label
      4. Deduplication: same (claim_id, condition) pair → keep first only
    """
    seen_pairs: set[tuple[str, str]] = set()
    results = []

    for c in candidates:
        claim_id  = c.get("claim_id", "?")
        condition = c.get("condition", "?")
        pair      = (claim_id, condition)

        # Rule 1: bypass suppression
        if c.get("scope_status") == "bypassed":
            results.append({
                **c,
                "filter_action": "suppressed",
                "filter_reason": "bypass_suppression",
            })
            continue

        # Rule 2: deprecation suppression
        if c.get("prerequisite_state") == "deprecated":
            results.append({
                **c,
                "issue_candidate": False,
                "filter_action":   "suppressed",
                "filter_reason":   "deprecation_suppression",
            })
            continue

        # Rule 3: deduplication
        if pair in seen_pairs:
            results.append({
                **c,
                "issue_candidate": False,
                "filter_action":   "suppressed",
                "filter_reason":   "duplicate_suppression",
                "duplicate_of":    list(pair),
            })
            continue
        seen_pairs.add(pair)

        # Rule 4: scope annotation for weakened prerequisites
        annotated = dict(c)
        if c.get("prerequisite_state") == "weakened":
            labels = list(annotated.get("labels", []))
            if "scope-annotated" not in labels:
                labels.append("scope-annotated")
            annotated["labels"] = labels
            nc = dict(annotated.get("negotiation_context", {}))
            nc["scope_note"] = (
                f"Prerequisite is weakened — scoped to "
                f"'{annotated.get('scope', 'unknown')}'. "
                "Bypass via equivalent safety path is possible."
            )
            annotated["negotiation_context"] = nc

        annotated["filter_action"] = "passed"
        annotated["filter_reason"] = "applicable_prerequisite"
        results.append(annotated)

    return results


# ── Plan scanner ──────────────────────────────────────────────────────────────

def _scan_plan_trees() -> list[dict[str, Any]]:
    """
    Scan ogi/examples/ for scoped plan tree JSON files and collect all issue candidates.
    """
    try:
        from scoped_plan_to_issue import issues_from_scoped_tree
    except ImportError:
        sys.path.insert(0, str(_FILE_DIR))
        from scoped_plan_to_issue import issues_from_scoped_tree

    candidates: list[dict[str, Any]] = []
    pattern = list(_OGI_EXAMPLES.glob("scoped-plan-*.output.json"))
    for path in sorted(pattern):
        try:
            with open(path) as f:
                tree = json.load(f)
            candidates.extend(issues_from_scoped_tree(tree))
        except Exception as e:
            print(f"  WARNING: could not process {path.name}: {e}", file=sys.stderr)
    return candidates


# ── CLI summary ───────────────────────────────────────────────────────────────

def _print_filter_results(results: list[dict[str, Any]]) -> None:
    passed    = [r for r in results if r.get("filter_action") == "passed"]
    suppressed = [r for r in results if r.get("filter_action") == "suppressed"]

    print(f"\n  Scoped Issue Filter Results")
    print(f"  Total:      {len(results)}")
    print(f"  Passed:     {len(passed)}")
    print(f"  Suppressed: {len(suppressed)}")
    print()

    if passed:
        print(f"  Issue Drafts (passed):")
        for r in passed:
            print(f"    ✓ [{r.get('claim_id')}] {r.get('condition')}")
            print(f"       scope: {r.get('scope','(none)')}  "
                  f"state: {r.get('prerequisite_state')}  "
                  f"labels: {r.get('labels',[])[:3]}...")

    if suppressed:
        print(f"\n  Suppressed:")
        for r in suppressed:
            icon = "⊗"
            print(f"    {icon} [{r.get('claim_id')}] {r.get('condition')} "
                  f"— {r.get('filter_reason','?')}")
    print()


def main() -> None:
    p = argparse.ArgumentParser(
        description="Filter scoped issue candidates.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gitlawb/runtime/scoped_issue_filter.py --scan-plans
  python gitlawb/runtime/scoped_issue_filter.py --scan-plans --json
        """,
    )
    p.add_argument("--scan-plans", action="store_true",
                   help="Scan ogi/examples/ for scoped plan trees")
    p.add_argument("input_file",   nargs="?", metavar="CANDIDATES_JSON",
                   help="JSON file with list of issue candidates (optional)")
    p.add_argument("--json",       action="store_true", dest="json_output")
    args = p.parse_args()

    if args.scan_plans:
        raw = _scan_plan_trees()
    elif args.input_file:
        with open(args.input_file) as f:
            raw = json.load(f)
        if isinstance(raw, dict):
            raw = [raw]
    else:
        # Default: scan plans
        raw = _scan_plan_trees()

    results = _apply_filters(raw)

    if args.json_output:
        print(json.dumps(results, indent=2))
        return

    _print_filter_results(results)


if __name__ == "__main__":
    main()
