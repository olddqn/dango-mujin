"""directive_checklist.py — Phase 35: Directive Execution Checklist

Builds an advisory step-level checklist for each Directive, cross-referencing
Execution Log entries. The checklist is a confirmation aid display — it is not
proof of execution, not proof of completion, and does not approve execution.
Human review is required before any real-world action.

INVARIANTS (permanent, not negotiable):
  Checklist is advisory display only.
  Checklist is not proof of execution.
  Checklist is not proof of completion.
  Checklist does not approve execution.
  Human review is required before any real-world action.
  authority: none

Data sources:
  globe/directives/*.json  — execution steps
  globe/logs/*.jsonl       — execution log entries (step matching or directive summary)

Related-log matching:
  Primary: log entry content contains step_id (case-insensitive substring)
  Fallback: if no step-specific entries, all directive log entries are used as
            directive-level summary (not attributed to individual steps).

CLI:
  python3 globe/runtime/directive_checklist.py summary
  python3 globe/runtime/directive_checklist.py save
  python3 globe/runtime/directive_checklist.py show-directive <directive_id>
  python3 globe/runtime/directive_checklist.py show-globe <globe_id>
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────

_GLOBE_DIR      = Path(__file__).resolve().parents[1]
_DIRECTIVES_DIR = _GLOBE_DIR / "directives"
_LOGS_DIR       = _GLOBE_DIR / "logs"
_REPORTS_DIR    = _GLOBE_DIR / "reports"

_CHECKLISTS_JSON = _REPORTS_DIR / "directive_checklists.json"
_CHECKLISTS_MD   = _REPORTS_DIR / "directive_checklists.md"

# ─── Invariants ───────────────────────────────────────────────────────────────

CHECKLIST_INVARIANTS = {
    "checklist_is_advisory_display_only": True,
    "checklist_is_not_proof_of_execution": True,
    "checklist_is_not_proof_of_completion": True,
    "checklist_does_not_approve_execution": True,
    "human_review_is_required_before_any_real_world_action": True,
    "authority": "none",
}

CHECKLIST_PHRASES = [
    "Checklist is advisory display only.",
    "Checklist is not proof of execution.",
    "Checklist is not proof of completion.",
    "Checklist does not approve execution.",
    "Human review is required before any real-world action.",
]

# Entry types that we track in checklist items
_TRACKED_TYPES = frozenset({
    "human_approval",
    "execution_attempt",
    "observation",
    "feedback",
    "objection",
    "rollback_request",
    "voluntary_resolution_signal",
})

# Entry types that warrant attention (observation only, not priority)
_ATTENTION_TYPES = frozenset({"objection", "rollback_request"})

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _load_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except Exception:
                pass
    return entries


# ─── Data loading ─────────────────────────────────────────────────────────────

def _load_all_directives() -> list[dict]:
    result = []
    for p in sorted(_DIRECTIVES_DIR.glob("*.json")):
        d = _load_json(p)
        if isinstance(d, dict) and "directive_id" in d:
            result.append(d)
    return result


def _load_log_entries(directive_id: str) -> list[dict]:
    return _load_jsonl(_LOGS_DIR / f"{directive_id}.jsonl")


# ─── Checklist item builder ───────────────────────────────────────────────────

def _build_checklist_item(
    step: dict,
    directive_id: str,
    globe_id: str,
    all_entries: list[dict],
    directive_log_summary: dict,
) -> dict:
    """Build one checklist item for a single execution step.

    Related-log matching:
      1. Entries whose content contains step_id (case-insensitive)
      2. If none found, use directive-level log summary (not per-step attribution)

    Advisory only. Not proof of completion.
    """
    step_id = step.get("step_id", "")
    checklist_id = f"cl-{directive_id}-{step_id}"

    # Primary: step-specific entries (content contains step_id)
    step_entries = [
        e for e in all_entries
        if step_id and step_id.lower() in e.get("content", "").lower()
    ]

    # Determine attribution mode
    if step_entries:
        related_entries = step_entries
        attribution = "step_specific"
    else:
        # Fallback: directive-level summary (same counts for all steps)
        related_entries = all_entries
        attribution = "directive_summary"

    # Count by entry type
    type_counts: dict[str, int] = {}
    for e in related_entries:
        et = e.get("entry_type", "")
        if et in _TRACKED_TYPES:
            type_counts[et] = type_counts.get(et, 0) + 1

    # Latest related entry
    latest_type = ""
    latest_at = ""
    if related_entries:
        last = related_entries[-1]
        latest_type = last.get("entry_type", "")
        latest_at = str(last.get("created_at", ""))[:19].replace("T", " ")

    has_objection     = type_counts.get("objection", 0) > 0
    has_rollback      = type_counts.get("rollback_request", 0) > 0
    needs_attention   = has_objection or has_rollback

    return {
        "checklist_id":              checklist_id,
        "directive_id":              directive_id,
        "globe_id":                  globe_id,
        "step_id":                   step_id,
        "step_title":                step.get("description", ""),
        "step_title_en":             step.get("description_en", ""),
        "step_status":               step.get("status", "pending"),
        "human_approval_required":   step.get("human_approval_required", True),
        "required_contributions":    step.get("required_contributions", []),
        "related_log_count":         len(related_entries),
        "attribution":               attribution,
        "has_human_approval":        type_counts.get("human_approval", 0) > 0,
        "human_approval_count":      type_counts.get("human_approval", 0),
        "has_execution_attempt":     type_counts.get("execution_attempt", 0) > 0,
        "execution_attempt_count":   type_counts.get("execution_attempt", 0),
        "has_observation":           type_counts.get("observation", 0) > 0,
        "observation_count":         type_counts.get("observation", 0),
        "has_feedback":              type_counts.get("feedback", 0) > 0,
        "feedback_count":            type_counts.get("feedback", 0),
        "has_objection":             has_objection,
        "objection_count":           type_counts.get("objection", 0),
        "has_rollback_request":      has_rollback,
        "rollback_request_count":    type_counts.get("rollback_request", 0),
        "voluntary_resolution_signal_count": type_counts.get(
            "voluntary_resolution_signal", 0),
        "needs_attention":           needs_attention,
        "latest_related_entry_type": latest_type,
        "latest_related_entry_at":   latest_at,
        "advisory_only":             True,
        "not_proof_of_completion":   True,
    }


# ─── Main build function ──────────────────────────────────────────────────────

def build_checklists() -> dict:
    """Build and return all directive checklists.

    Advisory only. Not proof of execution or completion.
    Does not approve or reject execution steps.
    """
    directives = _load_all_directives()

    all_items: list[dict] = []
    directive_checklists: list[dict] = []
    total_steps = 0
    total_with_approval = 0
    total_with_objection = 0
    total_with_rollback = 0

    for d in directives:
        directive_id = d["directive_id"]
        globe_id = d.get("globe_id", "")
        steps = d.get("execution_steps", [])
        all_entries = _load_log_entries(directive_id)

        # Directive-level log summary (used when no step-specific match)
        dir_summary: dict[str, int] = {}
        for e in all_entries:
            et = e.get("entry_type", "")
            if et in _TRACKED_TYPES:
                dir_summary[et] = dir_summary.get(et, 0) + 1

        items: list[dict] = []
        for step in steps:
            item = _build_checklist_item(
                step, directive_id, globe_id, all_entries, dir_summary
            )
            items.append(item)
            all_items.append(item)
            total_steps += 1
            if item["has_human_approval"]:
                total_with_approval += 1
            if item["has_objection"]:
                total_with_objection += 1
            if item["has_rollback_request"]:
                total_with_rollback += 1

        directive_checklists.append({
            "directive_id":   directive_id,
            "globe_id":       globe_id,
            "title":          d.get("title", ""),
            "step_count":     len(steps),
            "log_entry_count": len(all_entries),
            "items":          items,
            **CHECKLIST_INVARIANTS,
        })

    return {
        "checklist_id":        "globe-directive-checklists",
        "generated_at":        _now(),
        "directive_count":     len(directives),
        "total_steps":         total_steps,
        "total_items":         len(all_items),
        "steps_with_approval": total_with_approval,
        "steps_with_objection": total_with_objection,
        "steps_with_rollback": total_with_rollback,
        "phase":               "35",
        "phase_phrases":       CHECKLIST_PHRASES,
        **CHECKLIST_INVARIANTS,
        "directives":          directive_checklists,
        "items":               all_items,
    }


# ─── Filtered views ───────────────────────────────────────────────────────────

def filter_by_directive(checklists: dict, directive_id: str) -> dict | None:
    for d in checklists.get("directives", []):
        if d["directive_id"] == directive_id:
            return d
    return None


def filter_by_globe(checklists: dict, globe_id: str) -> list[dict]:
    return [d for d in checklists.get("directives", [])
            if d.get("globe_id") == globe_id]


# ─── Persistence ─────────────────────────────────────────────────────────────

def _build_markdown(checklists: dict) -> str:
    lines: list[str] = []
    lines.append("# Directive Execution Checklists (Phase 35)")
    lines.append("")
    lines.append(f"generated_at: {checklists['generated_at']}")
    lines.append(f"directive_count: {checklists['directive_count']}")
    lines.append(f"total_steps: {checklists['total_steps']}")
    lines.append(f"steps_with_approval: {checklists['steps_with_approval']}")
    lines.append(f"steps_with_objection: {checklists['steps_with_objection']}")
    lines.append(f"steps_with_rollback: {checklists['steps_with_rollback']}")
    lines.append("")
    lines.append("## Invariants")
    lines.append("")
    lines.append("| Key | Value |")
    lines.append("|-----|-------|")
    for k, v in CHECKLIST_INVARIANTS.items():
        lines.append(f"| `{k}` | `{v}` |")
    lines.append("")
    lines.append(
        "> Checklist is advisory display only. It is not proof of execution "
        "or completion. Human review is required before any real-world action."
    )
    lines.append("")

    for d in checklists.get("directives", []):
        lines.append(f"## {d['directive_id']} ({d['globe_id']})")
        lines.append(f"**{d.get('title','')}**")
        lines.append(f"steps: {d['step_count']}  log_entries: {d['log_entry_count']}")
        lines.append("")
        lines.append("| Step | Description | Appr.Req | ✅ Approval | ⚠️ Obj | ↩ RB | attribution |")
        lines.append("|------|-------------|----------|-------------|--------|------|-------------|")
        for it in d.get("items", []):
            appr_req = "✅" if it["human_approval_required"] else "—"
            has_appr = "✅" if it["has_human_approval"] else "⬜"
            obj = f"⚠️ {it['objection_count']}" if it["has_objection"] else "—"
            rb = f"↩ {it['rollback_request_count']}" if it["has_rollback_request"] else "—"
            attr = it.get("attribution", "")
            lines.append(
                f"| {it['step_id']} "
                f"| {it['step_title'][:40]} "
                f"| {appr_req} | {has_appr} | {obj} | {rb} | {attr} |"
            )
        lines.append("")

    for phrase in CHECKLIST_PHRASES:
        lines.append(f'> "{phrase}"')
    return "\n".join(lines)


def save_checklists() -> tuple[Path, Path]:
    cl = build_checklists()
    _REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    _CHECKLISTS_JSON.write_text(
        json.dumps(cl, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _CHECKLISTS_MD.write_text(_build_markdown(cl), encoding="utf-8")
    return _CHECKLISTS_JSON, _CHECKLISTS_MD


def load_checklists() -> dict:
    if _CHECKLISTS_JSON.exists():
        try:
            raw = json.loads(_CHECKLISTS_JSON.read_text(encoding="utf-8"))
            if isinstance(raw, dict) and "directives" in raw:
                return raw
        except Exception:
            pass
    return build_checklists()


# ─── CLI print helpers ────────────────────────────────────────────────────────

def _print_item(it: dict, indent: str = "  ") -> None:
    appr_req = "✅ required" if it["human_approval_required"] else "— not required"
    has_appr = "✅ YES" if it["has_human_approval"] else "⬜ none"
    attn = "  ⚠️  ATTENTION" if it["needs_attention"] else ""
    print(f"{indent}{it['step_id']}  [{appr_req}]  approval: {has_appr}{attn}")
    print(f"{indent}  desc: {it['step_title'][:70]}")

    counts = []
    for et, key in [
        ("human_approval",    "human_approval_count"),
        ("execution_attempt", "execution_attempt_count"),
        ("observation",       "observation_count"),
        ("feedback",          "feedback_count"),
        ("objection",         "objection_count"),
        ("rollback_request",  "rollback_request_count"),
        ("vrs",               "voluntary_resolution_signal_count"),
    ]:
        n = it.get(key, 0)
        if n:
            counts.append(f"{et}:{n}")
    if counts:
        print(f"{indent}  log counts: {' '.join(counts)}")
    attr = it.get("attribution", "")
    if attr:
        print(f"{indent}  attribution: {attr}")
    if it.get("latest_related_entry_type"):
        print(f"{indent}  latest: {it['latest_related_entry_type']} "
              f"({it['latest_related_entry_at']})")
    print()


def print_checklists_summary(cl: dict) -> None:
    print(f"\nDirective Execution Checklists (Phase 35)")
    print("=" * 60)
    print(f"  generated_at:        {cl.get('generated_at','')}")
    print(f"  directive_count:     {cl.get('directive_count',0)}")
    print(f"  total_steps:         {cl.get('total_steps',0)}")
    print(f"  steps_with_approval: {cl.get('steps_with_approval',0)}")
    print(f"  steps_with_objection:{cl.get('steps_with_objection',0)}")
    print(f"  steps_with_rollback: {cl.get('steps_with_rollback',0)}")
    print()
    for d in cl.get("directives", []):
        print(f"  {d['directive_id']}  [{d['globe_id']}]  "
              f"steps:{d['step_count']}  log:{d['log_entry_count']}")
        for it in d.get("items", []):
            attn = " ⚠️" if it["needs_attention"] else ""
            appr = "✅" if it["has_human_approval"] else "⬜"
            print(f"    {it['step_id']}  approval:{appr}{attn}")
    print()
    for phrase in CHECKLIST_PHRASES:
        print(f'  "{phrase}"')


def print_directive_checklist(d: dict) -> None:
    print(f"\nChecklist — {d['directive_id']}  [{d['globe_id']}]")
    print("=" * 60)
    print(f"  {d.get('title','')}")
    print(f"  steps: {d['step_count']}  log_entries: {d['log_entry_count']}")
    print()
    for it in d.get("items", []):
        _print_item(it)
    for phrase in CHECKLIST_PHRASES:
        print(f'  "{phrase}"')


# ─── CLI entry point ──────────────────────────────────────────────────────────

def main(argv: list[str]) -> None:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return

    cmd = argv[0]

    if cmd == "summary":
        cl = build_checklists()
        print_checklists_summary(cl)
        return

    if cmd == "save":
        cl = build_checklists()
        print_checklists_summary(cl)
        jp, mp = save_checklists()
        print(f"Saved: {jp}")
        print(f"Saved: {mp}")
        return

    if cmd == "show-directive":
        if len(argv) < 2:
            print("Usage: directive_checklist.py show-directive <directive_id>",
                  file=sys.stderr)
            sys.exit(1)
        directive_id = argv[1]
        cl = load_checklists()
        d = filter_by_directive(cl, directive_id)
        if not d:
            print(f"No checklist for directive: {directive_id}", file=sys.stderr)
            sys.exit(1)
        print_directive_checklist(d)
        return

    if cmd == "show-globe":
        if len(argv) < 2:
            print("Usage: directive_checklist.py show-globe <globe_id>",
                  file=sys.stderr)
            sys.exit(1)
        globe_id = argv[1]
        cl = load_checklists()
        ds = filter_by_globe(cl, globe_id)
        if not ds:
            print(f"No checklists for globe: {globe_id}", file=sys.stderr)
            sys.exit(1)
        for d in ds:
            print_directive_checklist(d)
        return

    print(f"Unknown command: {cmd}", file=sys.stderr)
    print("Commands: summary | save | show-directive <id> | show-globe <id>",
          file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
