"""
agent_registry.py — Phase H-3: Agent Registry (registration only).

Agent Commons is not a job board, not a marketplace. Agents register a
capability declaration and a set of non-negotiable refusals. No agent gains
authority, governance, case selection, or funding power. No agent can define
a Need, assign a Gateway, assign a Contribution, or assign a Cooperation.

This phase: REGISTRATION ONLY. Nookplot / A0x are NOT really connected.
Codex / OpenClaw are NOT executed. No real connection, no execution.

CLI:
  python -m bridge.agent_commons.runtime.agent_registry
"""

from __future__ import annotations

from typing import Any

from .store import (
    AGENT_REGISTRY_JSONL, append_jsonl, base_invariants, next_id, read_jsonl,
)

# required refusal flags carried by every registered agent
AGENT_REFUSALS = {
    "agent_is_not_authority": True,
    "agent_is_not_governance": True,
    "agent_is_not_case_selector": True,
    "agent_is_not_funding_authority": True,
    "agent_output_requires_human_review": True,
    "cannot_define_need": True,
    "cannot_assign_gateway": True,
    "cannot_assign_contribution": True,
    "cannot_assign_cooperation": True,
}

# registry only — no real connection / no execution this phase
AGENTS = [
    {"name": "Hermes", "kind": "observer",
     "capabilities": ["voice_observation", "observation_classification",
                      "gap_observation", "safety_review"],
     "connection_status": "internal_observer (this layer)",
     "real_connection": False, "execution_enabled": False},
    {"name": "Nookplot", "kind": "external_agent",
     "capabilities": ["declared_only"],
     "connection_status": "registry_only — real connection prohibited this phase",
     "real_connection": False, "execution_enabled": False},
    {"name": "A0x", "kind": "external_agent",
     "capabilities": ["declared_only"],
     "connection_status": "registry_only — real connection prohibited this phase",
     "real_connection": False, "execution_enabled": False},
    {"name": "Codex", "kind": "code_agent",
     "capabilities": ["declared_only"],
     "connection_status": "registry_only — execution disabled this phase",
     "real_connection": False, "execution_enabled": False},
    {"name": "OpenClaw", "kind": "agent",
     "capabilities": ["declared_only"],
     "connection_status": "registry_only — execution disabled this phase",
     "real_connection": False, "execution_enabled": False},
    {"name": "Human", "kind": "human_participant",
     "capabilities": ["voluntary_task_participation", "decision_in_mujin_layer"],
     "connection_status": "humans decide (review of record happens in the Mujin "
                          "layer, not here); within Agent Commons no auto-action",
     "real_connection": False, "execution_enabled": False},
    {"name": "Other", "kind": "unspecified",
     "capabilities": ["declared_only"],
     "connection_status": "registry_only",
     "real_connection": False, "execution_enabled": False},
]


def _registered() -> set[str]:
    return {a.get("name") for a in read_jsonl(AGENT_REGISTRY_JSONL)}


def register_all() -> list[dict[str, Any]]:
    """Register the known agents (idempotent by name)."""
    done = _registered()
    created = []
    for spec in AGENTS:
        if spec["name"] in done:
            continue
        record = {
            "record_type": "agent",
            "agent_id": next_id("agent", AGENT_REGISTRY_JSONL),
            **spec,
            **AGENT_REFUSALS,
            **base_invariants(),
        }
        created.append(append_jsonl(AGENT_REGISTRY_JSONL, record))
        done.add(spec["name"])
    return created


def list_agents() -> list[dict[str, Any]]:
    return read_jsonl(AGENT_REGISTRY_JSONL)


def main() -> None:
    print("=" * 64)
    print("AGENT REGISTRY — registration only (no real connection, no execution)")
    print('  agent_is_not_authority · cannot_define_need · cannot_assign_*')
    print("=" * 64)
    created = register_all()
    if not created:
        print("  (all known agents already registered — append-only, idempotent)")
    for a in created:
        print(f"  ✓ {a['agent_id']} {a['name']} ({a['kind']}) | {a['connection_status']}")
    print("-" * 64)
    print("No agent connected. No agent executed. No authority granted.")


if __name__ == "__main__":
    main()
