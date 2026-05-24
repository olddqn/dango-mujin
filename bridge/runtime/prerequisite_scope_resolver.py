"""
prerequisite_scope_resolver.py

Resolves the scope of weakened federation prerequisites deterministically.

When a prerequisite is weakened, it does not disappear — it becomes scoped.
The scope is derived directly from the weakened event's fields:
  new_scope                   → the label for where the prerequisite still applies
  equivalent_safety_conditions → the conditions that constitute a valid bypass

Scope resolution is deterministic:
  - If a claim's active plan includes ANY bypass condition → bypassed for that claim
  - Otherwise → applicable to that claim

No hidden scoring. No centralized scope assignment. No text similarity.
Read-only. stdlib only.

Scope rules are read from federation.jsonl, not hardcoded.
The only hardcoded knowledge is the SCOPE_LABELS mapping
(human-readable names for scope regions) and SCOPE_CONFLICT_PAIRS
(logically incompatible condition combinations).
"""

import json
import os
import sys

_BRIDGE = os.path.dirname(os.path.abspath(__file__))


def _sutable_path(table: str) -> str:
    base = os.path.dirname(_BRIDGE)
    p = os.path.join(base, "sutable", f"{table}.jsonl")
    if os.path.exists(p):
        return p
    p2 = os.path.normpath(os.path.join(_BRIDGE, "..", "sutable", f"{table}.jsonl"))
    return p2 if os.path.exists(p2) else p


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
    if fmap is not None:
        return fmap
    return {
        "plans":      _read_jsonl(_sutable_path("plans")),
        "memory":     _read_jsonl(_sutable_path("memory")),
        "federation": _read_jsonl(_sutable_path("federation")),
    }


# ---------------------------------------------------------------------------
# Scope vocabulary — human-readable region labels
# ---------------------------------------------------------------------------

# Maps each bypass condition → the scope-region label it signals.
# This is the only human-readable naming layer; resolution itself is structural.
BYPASS_CONDITION_LABELS: dict[str, str] = {
    "precertified_structure":          "precertified_modular_spaces",
    "external_safety_audit_attached":  "externally_audited_units",
    "embedded_fire_controls":          "embedded_suppression_units",
    "external_food_safety_certification": "externally_certified_food_ops",
    "certified_food_handler_on_site":  "on_site_certified_food_ops",
    "health_authority_pre_clearance":  "pre_cleared_food_ops",
}

# Maps each local-assessment / non-bypass condition → scope-region label.
SCOPE_INDICATOR_LABELS: dict[str, str] = {
    "structural_modification_documented": "modified_existing_structures",
    "local_safety_review":               "non_precertified_spaces",
    "non_certified_space":               "non_precertified_spaces",
    "local_structural_assessment":       "non_precertified_spaces",
}

# Pairs of conditions that are logically incompatible in the same plan.
# Each pair is (bypass_condition, local_modification_condition).
SCOPE_CONFLICT_PAIRS: list[tuple[str, str]] = [
    ("precertified_structure",         "structural_modification_documented"),
    ("precertified_structure",         "local_structural_assessment"),
    ("external_safety_audit_attached", "local_structural_assessment"),
]


# ---------------------------------------------------------------------------
# Scope rule extraction
# ---------------------------------------------------------------------------

def load_scope_rules(fmap=None) -> dict[str, dict]:
    """
    Read weakened events from federation.jsonl and build scope rules.

    Returns: {condition: {
        "new_scope":           str,
        "bypass_conditions":   list[str],   # from equivalent_safety_conditions
        "applies_to_label":    str,         # new_scope value
        "bypassed_by_labels":  list[str],   # human-readable region names
    }}
    """
    fm = _load_fmap(fmap)
    # Also track which conditions are currently deprecated (no scope needed)
    deprecated: set[str] = set()
    rules: dict[str, dict] = {}

    for ev in fm["federation"]:
        et   = ev.get("event_type", "")
        cond = ev.get("condition", "")
        if not cond:
            continue
        if et == "federation_prerequisite_deprecated":
            deprecated.add(cond)
        elif et == "federation_prerequisite_weakened":
            bypass_conds = ev.get("equivalent_safety_conditions", [])
            new_scope    = ev.get("new_scope", "unscoped")
            bypassed_labels = sorted({
                BYPASS_CONDITION_LABELS.get(c, c)
                for c in bypass_conds
            })
            rules[cond] = {
                "new_scope":          new_scope,
                "bypass_conditions":  bypass_conds,
                "applies_to_label":   new_scope,
                "bypassed_by_labels": bypassed_labels,
            }

    # Remove deprecated conditions — their scope is moot
    for cond in deprecated:
        rules.pop(cond, None)

    return rules


# ---------------------------------------------------------------------------
# Active plan conditions per claim
# ---------------------------------------------------------------------------

def _extract_conditions_from_tree(node) -> set[str]:
    if not isinstance(node, dict):
        return set()
    conds: set[str] = set()
    if node.get("node_type") == "branch":
        c = node.get("condition")
        if c:
            conds.add(c)
    for child in node.get("children", []):
        conds |= _extract_conditions_from_tree(child)
    for key in ("true", "false"):
        if key in node:
            conds |= _extract_conditions_from_tree(node[key])
    return conds


def _active_plan_conditions(plans: list[dict]) -> dict[str, set[str]]:
    """
    For each claim_id, return the conditions of its active (non-superseded) plan.
    Returns: {claim_id: set[str]}
    """
    versions: dict[str, list[dict]] = {}
    contested: dict[str, set[str]] = {}

    for ev in plans:
        cid = ev.get("claim_id", "")
        et  = ev.get("event_type", "")
        if not cid:
            continue
        if et == "plan_tree_created":
            versions.setdefault(cid, []).append(ev)
        elif et == "plan_contested":
            cpid = ev.get("contested_plan_id", "")
            if cpid:
                contested.setdefault(cid, set()).add(cpid)

    result: dict[str, set[str]] = {}
    for cid, evs in versions.items():
        contested_ids = contested.get(cid, set())
        active = None
        for ev in reversed(evs):
            if ev.get("plan_id") not in contested_ids:
                active = ev
                break
        if active is None:
            active = evs[-1]

        flat = active.get("plan_tree_conditions")
        if flat and isinstance(flat, list):
            result[cid] = set(flat)
        else:
            tree = active.get("plan_tree")
            result[cid] = _extract_conditions_from_tree(tree) if tree else set()

    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def resolve_scope(condition: str, claim_id: str, fmap=None) -> dict:
    """
    Deterministically resolve whether `condition` applies to `claim_id`.

    Returns:
    {
      "condition":       str,
      "claim_id":        str,
      "applicable":      bool,
      "bypassed":        bool,
      "bypass_conditions_found": list[str],   # which bypass conds are in plan
      "scope_indicators_found":  list[str],   # which scope-indicator conds are in plan
      "bypassed_by_labels":      list[str],   # human-readable bypass region names
      "applies_to_label":        str,         # human-readable applicability region
      "scope_reasoning":         list[str],   # machine-readable reasoning chain
      "has_scope_rule":          bool,        # False if condition is not scoped
    }
    """
    fm    = _load_fmap(fmap)
    rules = load_scope_rules(fmap=fm)

    if condition not in rules:
        # No scope rule → treat as universally applicable (promoted, not weakened)
        return {
            "condition":               condition,
            "claim_id":                claim_id,
            "applicable":              True,
            "bypassed":                False,
            "bypass_conditions_found": [],
            "scope_indicators_found":  [],
            "bypassed_by_labels":      [],
            "applies_to_label":        "all_spaces",
            "scope_reasoning":         ["no_scope_rule: condition not weakened"],
            "has_scope_rule":          False,
        }

    rule = rules[condition]
    bypass_conds     = set(rule["bypass_conditions"])
    all_claim_plans  = _active_plan_conditions(fm["plans"])
    plan_conditions  = all_claim_plans.get(claim_id, set())

    # Which bypass conditions appear in the plan?
    bypass_found = sorted(plan_conditions & bypass_conds)
    # Which scope indicators appear in the plan?
    scope_ind_found = sorted(
        c for c in plan_conditions if c in SCOPE_INDICATOR_LABELS
    )

    bypassed   = bool(bypass_found)
    applicable = not bypassed

    # Reasoning chain (transparent, no hidden logic)
    reasoning: list[str] = []
    if bypassed:
        for bc in bypass_found:
            label = BYPASS_CONDITION_LABELS.get(bc, bc)
            reasoning.append(f"bypass_condition_present: {bc} → {label}")
    else:
        if scope_ind_found:
            for si in scope_ind_found:
                label = SCOPE_INDICATOR_LABELS.get(si, si)
                reasoning.append(f"scope_indicator_present: {si} → {label}")
        else:
            reasoning.append(
                f"no_bypass_conditions_found: prerequisite applies in scope={rule['new_scope']}"
            )

    bypassed_by_labels = [
        BYPASS_CONDITION_LABELS.get(bc, bc) for bc in bypass_found
    ]

    return {
        "condition":               condition,
        "claim_id":                claim_id,
        "applicable":              applicable,
        "bypassed":                bypassed,
        "bypass_conditions_found": bypass_found,
        "scope_indicators_found":  scope_ind_found,
        "bypassed_by_labels":      bypassed_by_labels,
        "applies_to_label":        rule["applies_to_label"],
        "scope_reasoning":         reasoning,
        "has_scope_rule":          True,
    }


def resolve_all_scopes(fmap=None) -> dict[str, dict[str, dict]]:
    """
    Resolve scope for every (scoped condition, claim) pair.
    Returns: {condition: {claim_id: resolution_record}}
    """
    fm    = _load_fmap(fmap)
    rules = load_scope_rules(fmap=fm)
    all_plans = _active_plan_conditions(fm["plans"])
    all_claims = sorted(all_plans.keys())

    result: dict[str, dict[str, dict]] = {}
    for cond in rules:
        result[cond] = {
            cid: resolve_scope(cond, cid, fmap=fm)
            for cid in all_claims
        }
    return result


def scope_summary(fmap=None) -> list[dict]:
    """
    Returns a flat list of scope-resolution summaries per condition,
    grouped with applicable and bypassed claim lists.

    Returns list of:
    {
      "condition":        str,
      "new_scope":        str,
      "applies_to_label": str,
      "bypassed_by_labels": list[str],
      "applicable_claims": list[str],
      "bypassed_claims":   list[str],
    }
    """
    fm    = _load_fmap(fmap)
    rules = load_scope_rules(fmap=fm)
    result = []
    for cond, rule in rules.items():
        all_res = {
            cid: resolve_scope(cond, cid, fmap=fm)
            for cid in _active_plan_conditions(fm["plans"])
        }
        applicable = sorted(cid for cid, r in all_res.items() if r["applicable"])
        bypassed   = sorted(cid for cid, r in all_res.items() if r["bypassed"])
        result.append({
            "condition":          cond,
            "new_scope":          rule["new_scope"],
            "applies_to_label":   rule["applies_to_label"],
            "bypassed_by_labels": rule["bypassed_by_labels"],
            "applicable_claims":  applicable,
            "bypassed_claims":    bypassed,
        })
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli():
    import argparse
    ap = argparse.ArgumentParser(description="Resolve prerequisite scope per claim")
    ap.add_argument("--condition", help="specific prerequisite to resolve")
    ap.add_argument("--claim-id", help="specific claim to resolve for")
    ap.add_argument("--summary", action="store_true", help="show summary (default)")
    ap.add_argument("--json",    action="store_true")
    args = ap.parse_args()

    if args.condition and args.claim_id:
        r = resolve_scope(args.condition, args.claim_id)
        if args.json:
            print(json.dumps(r, indent=2))
        else:
            _print_resolution(r)
        return

    summaries = scope_summary()
    if args.json:
        print(json.dumps(summaries, indent=2))
    else:
        if not summaries:
            print("No scoped prerequisites.")
        for s in summaries:
            _print_summary(s)
            print()


def _print_resolution(r: dict):
    mark = "⊛ bypass" if r["bypassed"] else "✓ applicable"
    print(f"{r['condition']}  →  {mark}  for {r['claim_id']}")
    for line in r["scope_reasoning"]:
        print(f"    {line}")


def _print_summary(s: dict):
    print(f"◈ {s['condition']}  [scoped: {s['new_scope']}]")
    print(f"  applies_to:    {s['applies_to_label']}")
    print(f"  bypassed_by:   {s['bypassed_by_labels']}")
    print(f"  applicable ({len(s['applicable_claims'])}): {s['applicable_claims']}")
    print(f"  bypassed   ({len(s['bypassed_claims'])}): {s['bypassed_claims']}")


if __name__ == "__main__":
    _cli()
