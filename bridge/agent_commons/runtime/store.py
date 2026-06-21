"""
store.py — Agent Commons Core: shared storage (append-only) with hard guards.

Agent Commons is NOT a job board and NOT a marketplace. It is a Commons that
agents may join voluntarily. Hermes is an Observer, not a Planner, not a
Coordinator, not the Reviewer of Record.

"authority = none" · "advisory only" · "human approval required"
"AI proposes — Human decides."

Boundary rules:
  - This layer READS Mujin voice records read-only (bridge/mujin/data/...).
  - This layer WRITES only under bridge/agent_commons/. The write guard refuses
    any path outside it, and explicitly refuses Dan-Go (globe/, bridge/gitsea/,
    bridge/sutable/) and Mujin (bridge/mujin/).
  - Nothing here defines a Need, approves/rejects a Need, selects a Gateway,
    assigns an Agent, forms a Cooperation, allocates Funding, or executes.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── paths ─────────────────────────────────────────────────────────────────────
AGENT_COMMONS_DIR = Path(__file__).resolve().parent.parent      # bridge/agent_commons
REPO_ROOT         = AGENT_COMMONS_DIR.parents[1]                 # repo root
DATA_DIR          = AGENT_COMMONS_DIR / "data"
REPORTS_DIR       = AGENT_COMMONS_DIR / "reports"
MEMORY_DIR        = AGENT_COMMONS_DIR / "memory"

# read-only source (Mujin) — never written from this layer
MUJIN_VOICE_RECORDS = REPO_ROOT / "bridge" / "mujin" / "data" / "voice_records.jsonl"

# this layer's own append-only files
OBSERVATION_JSONL = DATA_DIR / "observation_candidates.jsonl"
TASK_JSONL        = DATA_DIR / "task_candidates.jsonl"
AGENT_REGISTRY_JSONL = DATA_DIR / "agent_registry.jsonl"
AGENT_RESULTS_JSONL  = DATA_DIR / "agent_results.jsonl"   # empty this phase (no execution)

REPORT_MD = REPORTS_DIR / "agent_commons_report.md"

# Hermes Reflective Memory (H-2.5)
REFLECTION_JSONL = MEMORY_DIR / "reflection_records.jsonl"
LEARNING_JSONL   = MEMORY_DIR / "learning_records.jsonl"
PATTERN_JSONL    = MEMORY_DIR / "pattern_records.jsonl"
EVIDENCE_JSONL   = MEMORY_DIR / "evidence_candidates.jsonl"   # H-3.5
INFERENCE_BOUNDARY_JSONL = MEMORY_DIR / "inference_boundary_records.jsonl"  # H-4
# Cooperation Discovery Memory (H-5)
COOP_REFLECTION_JSONL = MEMORY_DIR / "cooperation_reflections.jsonl"
COOP_LEARNING_JSONL   = MEMORY_DIR / "cooperation_learning.jsonl"
COOP_PATTERN_JSONL    = MEMORY_DIR / "cooperation_patterns.jsonl"
COOP_EVIDENCE_JSONL   = MEMORY_DIR / "cooperation_evidence_candidates.jsonl"
MEMORY_REPORT_MD = REPORTS_DIR / "hermes_memory_report.md"
INFERENCE_BOUNDARY_REPORT_MD = REPORTS_DIR / "inference_boundary_report.md"  # H-4
COOP_MEMORY_REPORT_MD = REPORTS_DIR / "cooperation_memory_report.md"  # H-5
# Decision Boundary Memory (H-6) — data/ + reports/ per spec
DECISION_BOUNDARY_JSONL = DATA_DIR / "decision_boundaries.jsonl"
DECISION_BOUNDARY_REPORT_MD = REPORTS_DIR / "decision_boundary_report.md"

# Findability Observation Layer (F-1) — records that someone discovered Mujin.
# Findability is NOT Reachability: Mujin never searches, contacts, recruits, or
# infers a Need. FINDABILITY_EVENT_JSONL is a READ-ONLY input that records the
# bare fact "an actor discovered Mujin"; it may not exist yet (then count = 0,
# which is an observation, not a failure). It sits BEFORE Voice in the pipeline.
FINDABILITY_EVENT_JSONL      = DATA_DIR / "findability_events.jsonl"        # read-only input
FINDABILITY_REFLECTION_JSONL = DATA_DIR / "findability_reflections.jsonl"
FINDABILITY_LEARNING_JSONL   = DATA_DIR / "findability_learnings.jsonl"
FINDABILITY_PATTERN_JSONL    = DATA_DIR / "findability_patterns.jsonl"
FINDABILITY_EVIDENCE_JSONL   = DATA_DIR / "findability_evidence.jsonl"
FINDABILITY_REPORT_MD        = REPORTS_DIR / "findability_report.md"

# Findability Surface Review (F-1.5) — observes WHERE Mujin is findable (its
# public surfaces). Observation of what exists, NOT an SEO/acquisition/marketing
# /growth analysis. Each surface is verified; unconfirmed surfaces → exists=false.
FINDABILITY_SURFACE_REFLECTION_JSONL = DATA_DIR / "findability_surface_reflections.jsonl"
FINDABILITY_SURFACE_LEARNING_JSONL   = DATA_DIR / "findability_surface_learnings.jsonl"
FINDABILITY_SURFACE_PATTERN_JSONL    = DATA_DIR / "findability_surface_patterns.jsonl"
FINDABILITY_SURFACE_EVIDENCE_JSONL   = DATA_DIR / "findability_surface_evidence.jsonl"
FINDABILITY_SURFACE_REPORT_MD        = REPORTS_DIR / "findability_surface_report.md"

# Discoverable Object Review (F-1.7) — observes the Surface → Object mapping:
# given the surfaces that exist, WHAT can an external actor actually discover.
# Observation of what is visible, NOT branding/marketing/SEO/growth. Reads F-1.5
# surfaces read-only; never assumes an object is discoverable.
DISCOVERABLE_OBJECT_REFLECTION_JSONL = DATA_DIR / "discoverable_object_reflections.jsonl"
DISCOVERABLE_OBJECT_LEARNING_JSONL   = DATA_DIR / "discoverable_object_learnings.jsonl"
DISCOVERABLE_OBJECT_PATTERN_JSONL    = DATA_DIR / "discoverable_object_patterns.jsonl"
DISCOVERABLE_OBJECT_EVIDENCE_JSONL   = DATA_DIR / "discoverable_object_evidence.jsonl"
DISCOVERABLE_OBJECT_REPORT_MD        = REPORTS_DIR / "discoverable_object_report.md"

# Discovery Event Memory (F-2) — the Discovery layer above F-1/F-1.5/F-1.7.
# Findability is "can be discovered"; Discovery is "was actually discovered".
# DISCOVERY_EVENTS_JSONL is a READ-ONLY input of real, verified discovery events;
# it may be empty (then everything downstream is 0 — recording that no discovery
# has happened, never fabricating one). Central question: who discovered what, where.
DISCOVERY_EVENTS_JSONL      = DATA_DIR / "discovery_events.jsonl"        # read-only input
DISCOVERY_REFLECTIONS_JSONL = DATA_DIR / "discovery_reflections.jsonl"
DISCOVERY_LEARNINGS_JSONL   = DATA_DIR / "discovery_learnings.jsonl"
DISCOVERY_PATTERNS_JSONL    = DATA_DIR / "discovery_patterns.jsonl"
DISCOVERY_EVIDENCE_JSONL    = DATA_DIR / "discovery_evidence.jsonl"
DISCOVERY_REPORT_MD         = REPORTS_DIR / "discovery_report.md"

# Discovery Path Review (F-2.5) — joins Discovery Events (F-2) with verified
# Surfaces (F-1.5) and Objects (F-1.7) to observe the Surface → Object → Event
# relationship: when a discovery happened, from which surface was which object
# found. This is NOT a marketing funnel / growth / SEO / acquisition / conversion
# analysis. With 0 events the path count is 0 — an observation, not a failure.
DISCOVERY_PATH_REFLECTIONS_JSONL = DATA_DIR / "discovery_path_reflections.jsonl"
DISCOVERY_PATH_LEARNINGS_JSONL   = DATA_DIR / "discovery_path_learnings.jsonl"
DISCOVERY_PATH_PATTERNS_JSONL    = DATA_DIR / "discovery_path_patterns.jsonl"
DISCOVERY_PATH_EVIDENCE_JSONL    = DATA_DIR / "discovery_path_evidence.jsonl"
DISCOVERY_PATH_REPORT_MD         = REPORTS_DIR / "discovery_path_report.md"

# read-only input from the human review (X-3.5)
NEED_DEFINITION_REVIEW_MD = REPO_ROOT / "docs" / "NEED_DEFINITION_REVIEW.md"

# paths this layer must never write to
_FORBIDDEN_WRITE_PARTS = (
    ("globe",),
    ("bridge", "gitsea"),
    ("bridge", "sutable"),
    ("bridge", "mujin"),
)


class AgentCommonsError(Exception):
    pass


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def event_hash(record: dict[str, Any]) -> str:
    body = {k: v for k, v in record.items() if k != "event_hash"}
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def base_invariants() -> dict[str, Any]:
    """Carried by every Agent Commons record. Never weakened."""
    return {
        "authority": "none",
        "advisory": True,
        "advisory_only": True,
        "human_approval_required": True,
        "ai_proposes_human_decides": True,
        "execution_allowed": False,
        "auto_approval": False,
        "auto_execution": False,
        "auto_needification": False,
        "auto_task_assignment": False,
    }


def _guard_path(path: Path) -> Path:
    resolved = path.resolve()
    parts = resolved.parts
    for forbidden in _FORBIDDEN_WRITE_PARTS:
        for i in range(len(parts) - len(forbidden) + 1):
            if tuple(parts[i:i + len(forbidden)]) == forbidden:
                raise AgentCommonsError(
                    f"refusing to write to protected path: {resolved} "
                    "(Agent Commons never writes to Dan-Go or Mujin)"
                )
    try:
        resolved.relative_to(AGENT_COMMONS_DIR)
    except ValueError:
        raise AgentCommonsError(
            f"refusing to write outside bridge/agent_commons/: {resolved}"
        ) from None
    return resolved


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read a JSONL file (read-only; allowed for any path including Mujin)."""
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def append_jsonl(path: Path, record: dict[str, Any]) -> dict[str, Any]:
    """Append one record under bridge/agent_commons/ only. Adds hash + ts."""
    resolved = _guard_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    stored = dict(record)
    stored.setdefault("appended_at", utc_now_iso())
    stored["event_hash"] = event_hash(stored)
    with open(resolved, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(stored, ensure_ascii=False) + "\n")
    return stored


def write_text(path: Path, text: str) -> Path:
    resolved = _guard_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with open(resolved, "w", encoding="utf-8") as fh:
        fh.write(text)
    return resolved


def next_id(prefix: str, path: Path) -> str:
    return f"{prefix}-{len(read_jsonl(path)) + 1:03d}"
