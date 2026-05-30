#!/usr/bin/env python3
"""
directive_execution_log.py — Directive Execution Log (Phase 25)
Dan-Go × GITSEA — Globe Execution Layer

Records human approvals, execution attempts, observations, feedback,
objections, and rollback requests for a given Directive.

Execution Log is not proof of execution.
Log entry is not legal authority.
Human approval is required before real-world execution.
Objection and rollback request must always be recordable.
Append-only: existing entries must never be rewritten.

authority: none · append-only · legal_authority_created: false
non_coercive: true · objection_always_recordable: true

Usage:
    python3 globe/runtime/directive_execution_log.py \\
        append <directive_id> <entry_type> <actor_type> <actor_name> <content>
    python3 globe/runtime/directive_execution_log.py list <directive_id>
    python3 globe/runtime/directive_execution_log.py summary <directive_id>
    python3 globe/runtime/directive_execution_log.py export-md <directive_id>

Entry types:
    human_approval      — Human explicitly approves a directive step
    execution_attempt   — Record of an attempted execution step
    observation         — Observation during or after an attempt
    feedback            — Feedback from any actor on the directive
    objection           — Objection to the directive or a step (always recordable)
    rollback_request    — Request to roll back an executed step (always recordable)

Actor types:
    human   — Human participant
    ai      — AI mediator / agent
    system  — Protocol event recorder
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_GLOBE_DIR = Path(__file__).resolve().parents[1]
_DIRECTIVES_DIR = _GLOBE_DIR / "directives"
_LOGS_DIR = _GLOBE_DIR / "logs"

# ─── Constants ──────────────────────────────────────────────────────────────────

VALID_ENTRY_TYPES = {
    "human_approval",
    "execution_attempt",
    "observation",
    "feedback",
    "objection",
    "rollback_request",
}

VALID_ACTOR_TYPES = {"human", "ai", "system"}

# These entry types warn if no prior human_approval exists in the log
REQUIRES_PRIOR_APPROVAL = frozenset({"execution_attempt", "observation", "feedback"})

# These are always recordable with no approval gate (non-coercive, contestable)
ALWAYS_RECORDABLE = frozenset({"human_approval", "objection", "rollback_request"})

ENTRY_TYPE_ICON = {
    "human_approval":    "✅",
    "execution_attempt": "▶️",
    "observation":       "👁️",
    "feedback":          "💬",
    "objection":         "⚠️",
    "rollback_request":  "↩️",
}

ACTOR_TYPE_ICON = {"human": "👤", "ai": "🤖", "system": "⚙️"}

# Immutable invariants stamped onto every log entry
ENTRY_INVARIANTS = {
    "legal_authority_created":  False,
    "log_is_proof_of_execution": False,
    "log_certifies_outcome":    False,
    "log_compels_action":       False,
    "append_only":              True,
}


# ─── IO helpers ─────────────────────────────────────────────────────────────────

def _log_path(directive_id: str) -> Path:
    _LOGS_DIR.mkdir(exist_ok=True)
    return _LOGS_DIR / f"{directive_id}.jsonl"


def _load_entries(directive_id: str) -> list:
    """Read all JSONL log entries for a directive (append-only; never mutate)."""
    p = _log_path(directive_id)
    if not p.exists():
        return []
    entries = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except Exception:
                pass  # Corrupt lines are skipped; we never delete them
    return entries


def _append_to_log(directive_id: str, entry: dict) -> None:
    """Append a single JSON line to the log file. Never overwrites existing lines."""
    p = _log_path(directive_id)
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _load_directive(directive_id: str) -> dict | None:
    """Load the Directive JSON for the given directive_id."""
    p = _DIRECTIVES_DIR / f"{directive_id}.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _next_log_id(entries: list) -> str:
    """Return the next log_id by incrementing the max seen."""
    nums = []
    for e in entries:
        lid = e.get("log_id", "")
        if lid.startswith("log-"):
            try:
                nums.append(int(lid[4:]))
            except ValueError:
                pass
    return f"log-{(max(nums) + 1 if nums else 1):03d}"


def _has_human_approval(entries: list) -> bool:
    return any(e.get("entry_type") == "human_approval" for e in entries)


# ─── Append ─────────────────────────────────────────────────────────────────────

def append_entry(
    directive_id: str,
    entry_type: str,
    actor_type: str,
    actor_name: str,
    content: str,
    evidence_refs: list | None = None,
    non_coercion_confirmed: bool = True,
    verbose: bool = True,
) -> dict | None:
    """Append a new entry to the directive's execution log."""

    # ── Validate entry_type ──
    if entry_type not in VALID_ENTRY_TYPES:
        if verbose:
            print(
                f"ERROR: unknown entry_type '{entry_type}'.\n"
                f"Valid types: {', '.join(sorted(VALID_ENTRY_TYPES))}"
            )
        return None

    # ── Validate actor_type ──
    if actor_type not in VALID_ACTOR_TYPES:
        if verbose:
            print(
                f"ERROR: unknown actor_type '{actor_type}'.\n"
                f"Valid types: {', '.join(sorted(VALID_ACTOR_TYPES))}"
            )
        return None

    # ── Confirm directive exists ──
    directive = _load_directive(directive_id)
    if not directive:
        if verbose:
            print(
                f"ERROR: directive '{directive_id}' not found in globe/directives/.\n"
                "Run: python3 globe/runtime/claim_to_directive.py list"
            )
        return None

    globe_id = directive.get("globe_id", "")
    existing = _load_entries(directive_id)
    log_id = _next_log_id(existing)

    # ── Prior-approval warning ──
    if entry_type in REQUIRES_PRIOR_APPROVAL and not _has_human_approval(existing):
        if verbose:
            print(
                f"WARNING: no human_approval has been recorded for '{directive_id}'.\n"
                f"         '{entry_type}' should not proceed without prior human approval.\n"
                "         This entry is recorded as advisory only.\n"
                "         Execution Log is not proof of execution.\n"
                "         Human approval is required before real-world execution.\n"
            )

    # ── Build entry ──
    entry = {
        "log_id":                log_id,
        "directive_id":          directive_id,
        "globe_id":              globe_id,
        "entry_type":            entry_type,
        "actor_type":            actor_type,
        "actor_name":            actor_name,
        "content":               content,
        "evidence_refs":         evidence_refs or [],
        "non_coercion_confirmed": non_coercion_confirmed,
        **ENTRY_INVARIANTS,
        "created_at":            _now(),
    }

    # ── Append (never overwrites) ──
    _append_to_log(directive_id, entry)

    if verbose:
        icon = ENTRY_TYPE_ICON.get(entry_type, "•")
        actor_icon = ACTOR_TYPE_ICON.get(actor_type, "")
        print(f"{icon}  [{log_id}] {entry_type}")
        print(f"    actor:     {actor_icon} {actor_name} ({actor_type})")
        print(f"    directive: {directive_id}")
        print(f"    globe:     {globe_id}")
        print(f"    content:   {content}")
        print(f"    time:      {entry['created_at'][:19]}")
        print()
        if entry_type == "human_approval":
            print("    ✅ Human approval recorded.")
        elif entry_type in {"objection", "rollback_request"}:
            print(f"    ⚠️  {entry_type} recorded — always recordable; append-only.")
        print()
        print(
            "    legal_authority_created: false · "
            "log_is_proof_of_execution: false · "
            "append_only: true"
        )

    return entry


# ─── List ────────────────────────────────────────────────────────────────────────

def list_entries(directive_id: str) -> None:
    """Print all log entries for a directive."""
    directive = _load_directive(directive_id)
    if not directive:
        print(f"ERROR: directive '{directive_id}' not found.")
        return

    entries = _load_entries(directive_id)
    if not entries:
        print(f"{directive_id} — 0 log entries")
        print()
        print("No entries yet. Run:")
        print(
            f"  python3 globe/runtime/directive_execution_log.py "
            f"append {directive_id} human_approval human <name> <content>"
        )
        return

    title = directive.get("title", directive_id)
    print(f"{directive_id}")
    print(f"  title:   {title}")
    print(f"  globe:   {directive.get('globe_id', '?')}")
    print(f"  entries: {len(entries)}")
    print()

    for e in entries:
        icon = ENTRY_TYPE_ICON.get(e.get("entry_type", ""), "•")
        actor_icon = ACTOR_TYPE_ICON.get(e.get("actor_type", ""), "")
        print(
            f"  [{e.get('log_id', '?')}] {icon}  {e.get('entry_type', '?')}"
        )
        print(
            f"    actor:   {actor_icon} {e.get('actor_name', '?')} "
            f"({e.get('actor_type', '?')})"
        )
        print(f"    time:    {str(e.get('created_at', ''))[:19]}")
        content = e.get("content", "")
        if len(content) > 100:
            content = content[:100] + "…"
        print(f"    content: {content}")
        refs = e.get("evidence_refs", [])
        if refs:
            print(f"    refs:    {', '.join(refs)}")
        print()


# ─── Summary ────────────────────────────────────────────────────────────────────

def summary(directive_id: str) -> None:
    """Print a structured summary of the execution log for a directive."""
    directive = _load_directive(directive_id)
    if not directive:
        print(f"ERROR: directive '{directive_id}' not found.")
        return

    entries = _load_entries(directive_id)
    title = directive.get("title", directive_id)
    globe_id = directive.get("globe_id", "?")

    # Count by type
    counts: dict[str, int] = {}
    for e in entries:
        et = e.get("entry_type", "unknown")
        counts[et] = counts.get(et, 0) + 1

    has_approval = _has_human_approval(entries)
    last = entries[-1] if entries else None

    print(f"Execution Log Summary — {directive_id}")
    print(f"  title:           {title}")
    print(f"  globe:           {globe_id}")
    print(f"  total_entries:   {len(entries)}")
    print(f"  human_approval:  {'✅ recorded' if has_approval else '⬜ not yet recorded'}")
    print()

    if counts:
        print("  entry_type breakdown:")
        for et in sorted(VALID_ENTRY_TYPES):
            n = counts.get(et, 0)
            if n:
                print(f"    {ENTRY_TYPE_ICON.get(et, '•')} {et:<20} {n}")
        print()

    if last:
        actor_icon = ACTOR_TYPE_ICON.get(last.get("actor_type", ""), "")
        print(
            f"  last_entry:      [{last.get('log_id', '?')}] "
            f"{last.get('entry_type', '?')}"
        )
        print(
            f"    actor:  {actor_icon} {last.get('actor_name', '?')}"
        )
        print(
            f"    time:   {str(last.get('created_at', ''))[:19]}"
        )
    else:
        print("  last_entry:      (none)")

    print()
    print("  Invariants:")
    print("    legal_authority_created:   false")
    print("    log_is_proof_of_execution: false")
    print("    log_certifies_outcome:     false")
    print("    log_compels_action:        false")
    print("    objection_always_recordable: true")
    print("    rollback_always_recordable:  true")
    print("    append_only:               true")


# ─── Export Markdown ────────────────────────────────────────────────────────────

def export_md(directive_id: str) -> None:
    """Export the execution log as a Markdown document to globe/logs/."""
    directive = _load_directive(directive_id)
    if not directive:
        print(f"ERROR: directive '{directive_id}' not found.")
        return

    entries = _load_entries(directive_id)
    title = directive.get("title", directive_id)
    globe_id = directive.get("globe_id", "?")
    source_claim = directive.get("source_claim_id", "?")
    source_proposal = directive.get("source_proposal_id", "?")

    has_approval = _has_human_approval(entries)

    # Count by type
    counts: dict[str, int] = {}
    for e in entries:
        et = e.get("entry_type", "unknown")
        counts[et] = counts.get(et, 0) + 1

    # Build entries Markdown
    entries_md = ""
    if not entries:
        entries_md = "_No entries recorded yet._\n"
    else:
        for e in entries:
            icon = ENTRY_TYPE_ICON.get(e.get("entry_type", ""), "•")
            actor_icon = ACTOR_TYPE_ICON.get(e.get("actor_type", ""), "")
            refs = e.get("evidence_refs", [])
            refs_md = ""
            if refs:
                refs_md = "\n\n**evidence_refs:** " + ", ".join(f"`{r}`" for r in refs)

            entries_md += (
                f"### [{e.get('log_id', '?')}] {icon} {e.get('entry_type', '?')}\n\n"
                f"| Field | Value |\n"
                f"|-------|-------|\n"
                f"| `actor` | {actor_icon} {e.get('actor_name', '?')} ({e.get('actor_type', '?')}) |\n"
                f"| `created_at` | {str(e.get('created_at', ''))[:19]} |\n"
                f"| `non_coercion_confirmed` | {str(e.get('non_coercion_confirmed', True)).lower()} |\n"
                f"| `legal_authority_created` | {str(e.get('legal_authority_created', False)).lower()} |\n\n"
                f"> {e.get('content', '')}"
                f"{refs_md}\n\n---\n\n"
            )

    # Summary table
    summary_rows = ""
    for et in sorted(VALID_ENTRY_TYPES):
        n = counts.get(et, 0)
        summary_rows += f"| `{et}` | {n} |\n"

    now_str = _now()[:10]
    approval_status = "✅ recorded" if has_approval else "⬜ not yet recorded"

    md = f"""# Execution Log — {title}

> **directive_id:** `{directive_id}`
> **source chain:** Proposal `{source_proposal}` → Claim `{source_claim}` → Directive `{directive_id}`
> **globe:** `{globe_id}`
> **total_entries:** {len(entries)}
> **human_approval:** {approval_status}

---

## ⚠️ Log Invariants

| Invariant | Value |
|-----------|-------|
| `legal_authority_created` | `false` |
| `log_is_proof_of_execution` | `false` |
| `log_certifies_outcome` | `false` |
| `log_compels_action` | `false` |
| `objection_always_recordable` | `true` |
| `rollback_always_recordable` | `true` |
| `append_only` | `true` |

> Execution Log is not proof of execution.
> Log entry is not legal authority.
> Human approval is required before real-world execution.
> Objection and rollback request must always be recordable.
> Append-only: existing entries must never be rewritten.

---

## Entry Type Summary

| Type | Count |
|------|-------|
{summary_rows}
---

## Log Entries

{entries_md}---

_Exported by Dan-Go Mujin · Phase 25 · {now_str}_
"""

    out_path = _LOGS_DIR / f"{directive_id}.md"
    _LOGS_DIR.mkdir(exist_ok=True)
    out_path.write_text(md, encoding="utf-8")
    print(f"Exported: globe/logs/{directive_id}.md")
    print(f"  entries:        {len(entries)}")
    print(f"  human_approval: {approval_status}")


# ─── Main ────────────────────────────────────────────────────────────────────────

def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)

    cmd = args[0]

    if cmd == "append":
        # append <directive_id> <entry_type> <actor_type> <actor_name> <content>
        if len(args) < 6:
            print(
                "Usage: directive_execution_log.py append "
                "<directive_id> <entry_type> <actor_type> <actor_name> <content>"
            )
            sys.exit(1)
        append_entry(
            directive_id=args[1],
            entry_type=args[2],
            actor_type=args[3],
            actor_name=args[4],
            content=args[5],
        )

    elif cmd == "list":
        if len(args) < 2:
            print("Usage: directive_execution_log.py list <directive_id>")
            sys.exit(1)
        list_entries(args[1])

    elif cmd == "summary":
        if len(args) < 2:
            print("Usage: directive_execution_log.py summary <directive_id>")
            sys.exit(1)
        summary(args[1])

    elif cmd == "export-md":
        if len(args) < 2:
            print("Usage: directive_execution_log.py export-md <directive_id>")
            sys.exit(1)
        export_md(args[1])

    else:
        print(f"Unknown command: {cmd}")
        print("Commands: append, list, summary, export-md")
        sys.exit(1)


if __name__ == "__main__":
    main()
