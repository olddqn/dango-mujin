"""
report_builder.py — Agent Commons report.

Writes reports/agent_commons_report.md with counts, Hermes review results,
invariant violations, and Dan-Go byte-identical / Mujin non-mutation evidence.

By construction this layer writes only under bridge/agent_commons/ (store.py
guard). The report records that fact and lists this layer's own files; the
authoritative byte-identical proof is the before/after hash comparison run
during verification.

CLI:
  python -m bridge.agent_commons.runtime.report_builder
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from .store import (
    AGENT_REGISTRY_JSONL, AGENT_RESULTS_JSONL, OBSERVATION_JSONL, REPO_ROOT,
    REPORT_MD, TASK_JSONL, MUJIN_VOICE_RECORDS, read_jsonl, utc_now_iso,
    write_text,
)
from .hermes_reviewer import run_review


def _dir_hash(root: Path, subpaths: list[str]) -> str:
    """Hash of all .json/.jsonl files under the given subpaths (for evidence)."""
    h = hashlib.sha256()
    files = []
    for sp in subpaths:
        base = root / sp
        if base.is_dir():
            files += sorted(base.rglob("*.json")) + sorted(base.rglob("*.jsonl"))
    for f in sorted(set(files)):
        h.update(f.read_bytes())
    return h.hexdigest()[:16]


def build_report() -> Path:
    voices = read_jsonl(MUJIN_VOICE_RECORDS)
    obs = read_jsonl(OBSERVATION_JSONL)
    tasks = read_jsonl(TASK_JSONL)
    agents = read_jsonl(AGENT_REGISTRY_JSONL)
    results = read_jsonl(AGENT_RESULTS_JSONL)
    review = run_review()
    from .evidence_builder import coverage as _ev_coverage
    cov = _ev_coverage()

    dango_hash = _dir_hash(REPO_ROOT, ["globe", "bridge/gitsea", "bridge/sutable"])
    mujin_hash = _dir_hash(REPO_ROOT, ["bridge/mujin"])

    viol = ("\n".join(f"- {v}" for v in review["violations"])
            if review["violations"] else "- (none)")

    md = f"""# Agent Commons Report

- Generated: {utc_now_iso()}
- Layer: `bridge/agent_commons/` (advisory only · authority none · AI proposes, human decides)

## Counts
| metric | value |
|---|---|
| Voice Count (Mujin, read-only) | {len(voices)} |
| Observation Candidate Count | {len(obs)} |
| Task Candidate Count | {len(tasks)} |
| Agent Registry Count | {len(agents)} |
| Agent Results Count | {len(results)} (no execution this phase) |
| Evidence Candidate Count | {cov['evidence_count']} |
| Evidence Coverage | {cov['evidence_coverage']} |
| Patterns With Evidence | {cov['patterns_with_evidence']} |
| Patterns Without Evidence | {cov['patterns_without_evidence']} |
| Human Reviewed Evidence Count | {cov['human_reviewed_evidence_count']} (AI-gathered; human review pending by design) |

## Hermes Review Results
- Reviewer of Record: {review['reviewer_of_record']}
- Checks:
{chr(10).join(f"  - {c}" for c in review['checks'])}
- Passed: **{review['passed']}**

## Invariant Violations
{viol}

## Dan-Go Byte-Identical Check
- Dan-Go content hash (globe, bridge/gitsea, bridge/sutable): `{dango_hash}`
- This layer writes ONLY under `bridge/agent_commons/` (store.py guard refuses
  any write to `globe/`, `bridge/gitsea/`, `bridge/sutable/`, `bridge/mujin/`).
- Authoritative proof: before/after hash comparison during verification.

## Mujin Non-Mutation Check
- Mujin content hash (bridge/mujin): `{mujin_hash}`
- Mujin `voice_records.jsonl` is opened read-only by the Voice Reader; this
  layer never writes to `bridge/mujin/`.

## Observation Candidates
{chr(10).join(f"- `{o['observation_id']}` ← {o['source_voice_id']} · type=`{o['voice_type']}` · need_owner_present={o['need_owner_present']} · bottleneck={o['observed_bottleneck']}" for o in obs) or "- (none)"}

## Task Candidates (work candidates, never assignments)
{chr(10).join(f"- `{t['task_id']}` ← {t['source_observation_id']} · `{t['task_type']}` · assigned_agent={t['assigned_agent']}" for t in tasks) or "- (none)"}

## Agent Registry (registration only — no real connection, no execution)
{chr(10).join(f"- `{a['agent_id']}` {a['name']} ({a['kind']}) · {a['connection_status']}" for a in agents) or "- (none)"}

---

*Hermes is an Observer. It does not define a Need, select a Gateway, assign an
agent, or decide anything. AI proposes; humans decide. Reach Gap is unresolved;
this layer does not claim to resolve it.*
"""
    return write_text(REPORT_MD, md)


def main() -> None:
    print("=" * 64)
    print("AGENT COMMONS REPORT BUILDER")
    print("=" * 64)
    path = build_report()
    print(f"  ✓ wrote {path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
