#!/usr/bin/env python3
"""
post_scarcity_guard.py — dango-ogi-bridge

Post-scarcity exploitation guard for OGI-compatible agent tasks.

Detects and blocks claims that violate post-scarcity ethics:
  - exploitation_risk
  - dignity_violation
  - coercion
  - false_abundance_claim
  - monetizing_vulnerability
  - automation_without_consent

Decision: PASS | ESCALATE | BLOCK

If unsure: BLOCK.

This is an extension of Dan-Go's dignity_guard.py,
applied specifically to post-scarcity and agent-economy contexts.

Usage:
  python runtime/post_scarcity_guard.py examples/post-scarcity.claim.json
  python runtime/post_scarcity_guard.py examples/post-scarcity.claim.json --json
"""

import json
import sys
from pathlib import Path


def load_claim(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def run_guard(claim: dict) -> list[dict]:
    """Run all post-scarcity checks. Return list of check results."""
    results = []
    observed      = claim.get("observed_state", [])
    missing       = claim.get("missing_conditions", [])
    constraints   = claim.get("dignity_constraints", [])
    contributions = claim.get("possible_contributions", [])
    statement     = claim.get("statement", "").lower()
    title         = claim.get("title", "").lower()
    risks         = claim.get("risks", [])
    constitution  = claim.get("constitution_check", {})
    text_fields   = f"{statement} {title} {' '.join(str(r) for r in risks)}"

    def check(rule: str, decision: str, detail: str) -> None:
        results.append({"rule": rule, "result": decision, "detail": detail})

    # ── Rule 1: Exploitation risk ──────────────────────────────
    exploitation_keywords = [
        "exploit", "exploiting", "exploitation",
        "trafficking", "coerce", "coercion",
        "force", "forced", "manipulation", "manipulate",
    ]
    exploitation_found = [k for k in exploitation_keywords if k in text_fields]
    uses_coercion = constitution.get("uses_coercion", False)

    if exploitation_found or uses_coercion:
        check(
            "exploitation_risk",
            "BLOCK",
            f"Exploitation language detected: {exploitation_found or 'coercion flag in constitution_check'}. "
            "Human review required before any agent task is created.",
        )
    else:
        check("exploitation_risk", "PASS", "No exploitation language detected.")

    # ── Rule 2: Dignity violation ──────────────────────────────
    dignity_violation_keywords = ["dignity violation", "dignity_violation", "violates dignity"]
    violates_dignity = constitution.get("violates_dignity", False)
    dignity_found = any(k in text_fields for k in dignity_violation_keywords)

    if violates_dignity or dignity_found:
        check(
            "dignity_violation",
            "BLOCK",
            "Dignity violation detected in claim statement or constitution_check. "
            "Cannot create agent task.",
        )
    else:
        check("dignity_violation", "PASS", "No dignity violation detected.")

    # ── Rule 3: Coercion ──────────────────────────────────────
    coercion_keywords = [
        "must participate", "required to contribute", "no choice",
        "forced contribution", "mandatory labor", "unpaid obligation",
    ]
    coercion_found = [k for k in coercion_keywords if k in text_fields]

    if coercion_found:
        check(
            "coercion",
            "BLOCK",
            f"Coercive language detected: {coercion_found}. "
            "Participation in Dan-Go contributions must be voluntary.",
        )
    else:
        check("coercion", "PASS", "No coercive language detected.")

    # ── Rule 4: False abundance claim ─────────────────────────
    false_abundance_keywords = [
        "no cost forever", "infinite resources", "unlimited abundance",
        "free forever", "zero cost always", "never runs out",
    ]
    false_abundance_found = [k for k in false_abundance_keywords if k in text_fields]
    # Also flag: abundance claimed but no coordination mechanism specified
    abundance_without_protocol = (
        any(w in text_fields for w in ["abundance", "post-scarcity", "post scarcity"])
        and "agent_negotiation" not in observed + list(constraints)
        and "agent_negotiation" not in (claim.get("required_state") or [])
    )

    if false_abundance_found:
        check(
            "false_abundance_claim",
            "BLOCK",
            f"False abundance claim detected: {false_abundance_found}. "
            "Post-scarcity does not mean infinite or free. "
            "Coordination is still required.",
        )
    elif abundance_without_protocol:
        check(
            "false_abundance_claim",
            "ESCALATE",
            "Abundance referenced but no coordination protocol specified in required_state. "
            "Abundance without negotiation structure risks collapse. "
            "Add agent_negotiation to required_state.",
        )
    else:
        check("false_abundance_claim", "PASS", "No false abundance claim detected.")

    # ── Rule 5: Monetizing vulnerability ──────────────────────
    vulnerability_keywords = [
        "refugee", "displaced", "homeless", "victim", "survivor",
        "crisis", "emergency", "poverty", "destitute", "desperate",
    ]
    profit_keywords = [
        "profit", "revenue", "monetize", "monetizing", "earn from",
        "sell their", "sell the story", "sell access",
    ]
    vulnerability_present = any(k in text_fields for k in vulnerability_keywords)
    profit_present        = any(k in text_fields for k in profit_keywords)
    fair_share_protected  = "fair_revenue_share" in constraints or "fair_participation" in constraints

    if vulnerability_present and profit_present and not fair_share_protected:
        check(
            "monetizing_vulnerability",
            "BLOCK",
            "Vulnerable population referenced with profit motive, but fair_revenue_share / "
            "fair_participation not in dignity_constraints. "
            "Add fair_participation or fair_revenue_share to dignity_constraints.",
        )
    elif vulnerability_present and profit_present and fair_share_protected:
        check(
            "monetizing_vulnerability",
            "PASS",
            "Vulnerable population present with fair_participation/fair_revenue_share guaranteed.",
        )
    else:
        check("monetizing_vulnerability", "PASS",
              "No monetizing-vulnerability pattern detected.")

    # ── Rule 6: Automation without consent ────────────────────
    automation_in_contributions = any(
        w in c for c in contributions for w in ("compute", "automation", "ai", "agent")
    )
    automation_in_statement = any(
        w in text_fields for w in ("automat", "autonomous agent", "without human")
    )
    automation_present = automation_in_contributions or automation_in_statement
    consent_protected  = (
        "automation_requires_consent" in constraints
        or "explicit_consent_established" in observed
        or "revocable_consent" in constraints
    )
    consent_unknown    = "consent_unknown" in observed

    if automation_present and consent_unknown:
        check(
            "automation_without_consent",
            "BLOCK",
            "Automation present and consent_unknown in observed_state. "
            "Cannot proceed with automated contributions until consent is established.",
        )
    elif automation_present and not consent_protected:
        check(
            "automation_without_consent",
            "ESCALATE",
            "Automation present but automation_requires_consent / revocable_consent "
            "not in dignity_constraints. "
            "Add automation_requires_consent to dignity_constraints before proceeding.",
        )
    else:
        check(
            "automation_without_consent",
            "PASS",
            "Automation is either absent or appropriately consent-gated.",
        )

    return results


def final_decision(checks: list[dict]) -> tuple[str, str]:
    decisions = [c["result"] for c in checks]
    if "BLOCK" in decisions:
        blocking = [c for c in checks if c["result"] == "BLOCK"]
        return "block", blocking[0]["detail"]
    if "ESCALATE" in decisions:
        escalating = [c for c in checks if c["result"] == "ESCALATE"]
        return "escalate", escalating[0]["detail"]
    return "pass", "All post-scarcity guard checks passed."


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python post_scarcity_guard.py <claim.json> [--json]")
        sys.exit(1)

    path = sys.argv[1]
    as_json = "--json" in sys.argv

    if not Path(path).exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    claim  = load_claim(path)
    checks = run_guard(claim)
    decision, reason = final_decision(checks)

    if as_json:
        print(json.dumps({
            "claim_id": claim.get("claim_id"),
            "decision": decision,
            "reason":   reason,
            "checks":   checks,
        }, indent=2, ensure_ascii=False))
        sys.exit({"pass": 0, "block": 1, "escalate": 2}.get(decision, 1))

    ICON = {"pass": "✓", "block": "✗", "escalate": "⚠"}
    RESULT_ICON = {"PASS": "✓", "BLOCK": "✗", "ESCALATE": "⚠"}

    print("=" * 60)
    print("POST-SCARCITY GUARD — dango-ogi-bridge")
    print(f"Claim: {claim.get('claim_id', '?')}")
    print("=" * 60)

    for c in checks:
        icon = RESULT_ICON.get(c["result"], "?")
        print(f"  {icon} [{c['result']}] {c['rule']}")
        print(f"       {c['detail']}")

    print()
    print("-" * 60)
    icon = ICON.get(decision, "?")
    print(f"FINAL DECISION: {icon} {decision.upper()}")
    print(f"Reason: {reason}")

    if decision == "block":
        print()
        print("BLOCKED. No agent task can be created from this Claim.")
        print("Resolve the blocking condition and rerun the guard.")
    elif decision == "escalate":
        print()
        print("ESCALATE. Human review required before agent task creation.")
        print("Do not automate processing of this Claim.")
    else:
        print()
        print("PASSED. This Claim may proceed to agent task creation.")
        print("Run claim_to_agent_task.py to generate the agent task.")

    print("=" * 60)

    sys.exit({"pass": 0, "block": 1, "escalate": 2}.get(decision, 1))


if __name__ == "__main__":
    main()
