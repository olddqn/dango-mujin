"""
prerequisite_alternative_plan.py

Detects plans that achieve claim goals WITHOUT a promoted federation prerequisite
by using an equivalent safety path instead.

No text similarity. No NLP. No external libraries. stdlib only.
Read-only — writes nothing.

Design:
  A "bypass" is when a supported or uncontested plan omits a promoted prerequisite
  but includes at least one recognized equivalent safety condition.

  Equivalent safety conditions for space_safety_assessed:
    precertified_structure, external_safety_audit_attached, embedded_fire_controls

  These are detected from memory.jsonl (bypass_conditions + equivalent_safety_conditions
  fields in memory snapshots), and confirmed against plans.jsonl.

  A plan counts as an alternative path if:
    - It is the most recent active plan for its claim (not contested by a later plan)
    - It does not include the promoted prerequisite in its plan_tree_conditions
    - It includes at least one equivalent safety condition (or the memory snapshot
      records bypass_conditions containing the prerequisite)
    - No dignity_violation objection was raised against it

Authority: none. This module only reads; callers decide what to do with findings.
"""

import json
import os
import sys

_BRIDGE = os.path.dirname(os.path.abspath(__file__))
_PLANS  = os.path.join(os.path.dirname(_BRIDGE), "bridge", "sutable", "plans.jsonl") \
          if not os.path.exists(os.path.join(os.path.dirname(_BRIDGE), "sutable", "plans.jsonl")) \
          else os.path.join(os.path.dirname(_BRIDGE), "sutable", "plans.jsonl")

def _sutable_path(table: str) -> str:
    base = os.path.dirname(_BRIDGE)
    # try bridge/sutable first (when running from repo root)
    p = os.path.join(base, "sutable", f"{table}.jsonl")
    if os.path.exists(p):
        return p
    # try sibling sutable (when bridge IS the base)
    p2 = os.path.join(_BRIDGE, "..", "sutable", f"{table}.jsonl")
    p2 = os.path.normpath(p2)
    if os.path.exists(p2):
        return p2
    return p  # return even if missing; caller handles FileNotFoundError


def _read_jsonl(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    events = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return events


def _load_fmap(fmap=None) -> dict:
    """Return {table: [events]} for plans, memory, federation."""
    if fmap is not None:
        return fmap
    return {
        "plans":      _read_jsonl(_sutable_path("plans")),
        "memory":     _read_jsonl(_sutable_path("memory")),
        "federation": _read_jsonl(_sutable_path("federation")),
    }


# ---------------------------------------------------------------------------
# Core: equivalent safety detection
# ---------------------------------------------------------------------------

# Conditions recognised as equivalent safety paths for each promoted prerequisite.
# Explicit, transparent, no fuzzy matching.
EQUIVALENT_SAFETY: dict[str, list[str]] = {
    "space_safety_assessed": [
        "precertified_structure",
        "external_safety_audit_attached",
        "embedded_fire_controls",
    ],
    "food_safety_reviewed": [
        "external_food_safety_certification",
        "certified_food_handler_on_site",
        "health_authority_pre_clearance",
    ],
}


def equivalent_safety_conditions(condition: str) -> list[str]:
    """Return the list of recognised equivalent safety conditions for a prerequisite."""
    return EQUIVALENT_SAFETY.get(condition, [])


def _promoted_conditions(fed_events: list[dict]) -> set[str]:
    """Return conditions currently in 'promoted' or 'reaffirmed' or 'weakened' state."""
    promoted: set[str] = set()
    deprecated: set[str] = set()
    for ev in fed_events:
        et = ev.get("event_type", "")
        cond = ev.get("condition", "")
        if not cond:
            continue
        if et == "federation_prerequisite_promoted":
            promoted.add(cond)
        elif et == "federation_prerequisite_deprecated":
            deprecated.add(cond)
    return promoted - deprecated


def _extract_conditions_from_tree(node) -> set[str]:
    """Recursively extract condition strings from branch nodes in a plan_tree dict."""
    conditions: set[str] = set()
    if not isinstance(node, dict):
        return conditions
    if node.get("node_type") == "branch":
        cond = node.get("condition")
        if cond:
            conditions.add(cond)
    for child in node.get("children", []):
        conditions |= _extract_conditions_from_tree(child)
    for key in ("true", "false"):
        if key in node:
            conditions |= _extract_conditions_from_tree(node[key])
    return conditions


def _extract_conditions(ev: dict) -> set[str]:
    """
    Extract plan conditions from an event.
    Handles both:
      - flat 'plan_tree_conditions' list (convenience field on fixture events)
      - nested 'plan_tree' dict (recursive branch-node extraction)
    """
    flat = ev.get("plan_tree_conditions")
    if flat and isinstance(flat, list):
        return set(flat)
    tree = ev.get("plan_tree")
    if tree and isinstance(tree, dict):
        return _extract_conditions_from_tree(tree)
    return set()


def _claim_plan_conditions(plans: list[dict]) -> dict[str, dict]:
    """
    For each claim_id, determine the *active* plan (most recent plan_tree_created
    not superseded by a plan_contested event) and return its plan_tree_conditions.

    Returns: {claim_id: {"plan_id": str, "conditions": set[str], "has_dignity_violation": bool}}

    Note: plan_contested events use 'contested_plan_id' (not 'plan_id') to identify
    the plan being superseded.
    """
    plan_versions: dict[str, list[dict]] = {}
    contested: dict[str, set[str]] = {}  # claim_id → set of contested plan_ids
    dignity_violations: dict[str, set[str]] = {}  # claim_id → set of plan_ids

    for ev in plans:
        cid = ev.get("claim_id", "")
        et  = ev.get("event_type", "")
        if not cid:
            continue
        if et == "plan_tree_created":
            plan_versions.setdefault(cid, []).append(ev)
        elif et == "plan_contested":
            # contested_plan_id is the superseded plan
            cpid = ev.get("contested_plan_id", "")
            if cpid:
                contested.setdefault(cid, set()).add(cpid)
        elif et == "plan_objected":
            if ev.get("objection_type") == "dignity_violation":
                pid = ev.get("plan_id", "")
                if pid:
                    dignity_violations.setdefault(cid, set()).add(pid)

    result: dict[str, dict] = {}
    for cid, versions in plan_versions.items():
        # The active plan: last plan_tree_created whose plan_id is NOT in the contested set
        contested_ids = contested.get(cid, set())
        active = None
        for ev in reversed(versions):
            if ev.get("plan_id") not in contested_ids:
                active = ev
                break
        if active is None:
            # All versions contested — use the last version anyway
            active = versions[-1]

        pid = active.get("plan_id", "")
        conditions = _extract_conditions(active)
        has_dignity = pid in dignity_violations.get(cid, set())
        result[cid] = {
            "plan_id":               pid,
            "conditions":           conditions,
            "has_dignity_violation": has_dignity,
        }
    return result


def _bypass_from_memory(memory: list[dict]) -> dict[str, dict]:
    """
    Read memory snapshots for bypass_conditions and equivalent_safety_conditions.
    Returns: {claim_id: {bypassed_conditions: set[str], equivalent_safety: set[str]}}
    """
    result: dict[str, dict] = {}
    for ev in memory:
        if ev.get("event_type") != "memory_snapshot_created":
            continue
        cid = ev.get("claim_id", "")
        if not cid:
            continue
        bypassed = set(ev.get("bypass_conditions", []))
        equiv    = set(ev.get("equivalent_safety_conditions", []))
        if bypassed or equiv:
            existing = result.get(cid, {"bypassed_conditions": set(), "equivalent_safety": set()})
            existing["bypassed_conditions"] |= bypassed
            existing["equivalent_safety"]   |= equiv
            result[cid] = existing
    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def detect_alternative_plans(condition: str, fmap=None) -> list[dict]:
    """
    Detect claims whose active plan omits `condition` but uses an equivalent
    safety path — a valid bypass.

    Returns list of:
    {
      "claim_id":                str,
      "plan_id":                 str,
      "condition":               str,
      "bypasses_prerequisite":   True,
      "equivalent_safety_found": bool,
      "equivalent_conditions":   list[str],  # which equiv conditions appear in plan
      "requires_local_assessment": bool,      # True if NO equiv conditions at all
      "basis":                   str,         # "plan_tree" or "memory_snapshot"
      "dignity_safe":            bool,
    }

    Only returns claims where:
      - active plan does NOT include `condition`
      - active plan IS dignity-safe (no dignity_violation objection)
    """
    fm = _load_fmap(fmap)
    plans_ev  = fm.get("plans", [])
    memory_ev = fm.get("memory", [])
    fed_ev    = fm.get("federation", [])

    promoted = _promoted_conditions(fed_ev)
    if condition not in promoted:
        return []  # only detect bypasses for promoted conditions

    claim_plans  = _claim_plan_conditions(plans_ev)
    memory_bypasses = _bypass_from_memory(memory_ev)
    equiv_known  = set(equivalent_safety_conditions(condition))

    results = []
    for cid, info in claim_plans.items():
        plan_conditions = info["conditions"]

        # Skip if the plan already includes the prerequisite
        if condition in plan_conditions:
            continue

        # Skip if dignity violation raised against active plan
        if info["has_dignity_violation"]:
            continue

        # Determine equivalent safety conditions present in the plan
        equiv_in_plan = sorted(plan_conditions & equiv_known)

        # Also check memory snapshot bypass record
        mem_bypass = memory_bypasses.get(cid, {})
        bypassed_in_mem = condition in mem_bypass.get("bypassed_conditions", set())
        equiv_in_mem    = mem_bypass.get("equivalent_safety", set()) & equiv_known

        # Combine: plan_tree evidence takes priority
        equiv_conditions = equiv_in_plan if equiv_in_plan else sorted(equiv_in_mem)
        equiv_found      = bool(equiv_in_plan) or bool(equiv_in_mem)

        basis = "plan_tree" if equiv_in_plan else ("memory_snapshot" if equiv_in_mem else "plan_tree")

        results.append({
            "claim_id":                cid,
            "plan_id":                 info["plan_id"],
            "condition":               condition,
            "bypasses_prerequisite":   True,
            "equivalent_safety_found": equiv_found,
            "equivalent_conditions":   equiv_conditions,
            "requires_local_assessment": not equiv_found,
            "basis":                   basis,
            "dignity_safe":            True,  # filtered above
        })

    return results


def detect_all_alternative_plans(fmap=None) -> dict[str, list[dict]]:
    """
    Run detect_alternative_plans for all promoted prerequisites.
    Returns: {condition: [bypass_records]}
    """
    fm = _load_fmap(fmap)
    promoted = _promoted_conditions(fm.get("federation", []))
    return {cond: detect_alternative_plans(cond, fmap=fm) for cond in promoted}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli():
    import argparse
    ap = argparse.ArgumentParser(description="Detect alternative plans that bypass a federation prerequisite")
    ap.add_argument("--condition", help="prerequisite condition to inspect (default: all)")
    ap.add_argument("--json",      action="store_true", help="output JSON")
    args = ap.parse_args()

    if args.condition:
        result = detect_alternative_plans(args.condition)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if not result:
                print(f"No bypass plans detected for: {args.condition}")
            else:
                print(f"Bypass plans for {args.condition!r}:")
                for r in result:
                    mark = "✓" if r["equivalent_safety_found"] else "?"
                    print(f"  {mark} {r['claim_id']}  plan={r['plan_id']}")
                    if r["equivalent_conditions"]:
                        print(f"      equivalent: {', '.join(r['equivalent_conditions'])}")
                    if r["requires_local_assessment"]:
                        print(f"      WARNING: no recognised equivalent safety conditions found")
    else:
        result = detect_all_alternative_plans()
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            any_found = False
            for cond, bypasses in result.items():
                if bypasses:
                    any_found = True
                    print(f"\n{cond}  ({len(bypasses)} bypass plan(s)):")
                    for r in bypasses:
                        mark = "✓" if r["equivalent_safety_found"] else "?"
                        print(f"  {mark} {r['claim_id']}  plan={r['plan_id']}")
                        if r["equivalent_conditions"]:
                            print(f"      equivalent: {', '.join(r['equivalent_conditions'])}")
            if not any_found:
                print("No bypass plans detected for any promoted prerequisite.")


if __name__ == "__main__":
    _cli()
