#!/usr/bin/env python3
"""
sutable_query.py — dango-gitsea-bridge / su-table

Query and display su-table events.

Usage:
  python runtime/sutable_query.py --claim-id housing-001
  python runtime/sutable_query.py --claim-id housing-001 --table negotiations
  python runtime/sutable_query.py --event-type objection
  python runtime/sutable_query.py --timeline housing-001
  python runtime/sutable_query.py --contributions housing-001
  python runtime/sutable_query.py --verify
  python runtime/sutable_query.py --stats
"""

import argparse
import json
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from sutable_log import read_all, verify_chain, count_events, VALID_TABLES

# ── Display helpers ───────────────────────────────────────────

EVENT_ICON = {
    # claims
    "claim_created":             "📋",
    "claim_updated":             "✏",
    # negotiations
    "objection":                 "⚡",
    "amendment":                 "✏",
    "support":                   "✓",
    "escalation":                "⚠",
    "correction":                "↩",
    "withdrawal":                "↰",
    # contributions
    "contribution_offer":        "→",
    "contribution_accepted":     "✓",
    "contribution_rejected":     "✗",
    "contribution_completed":    "◉",
    # executions
    "execution_started":         "▶",
    "execution_paused":          "⏸",
    "execution_completed":       "✓",
    "execution_blocked":         "🛑",
    # reality_feedback
    "reality_feedback":          "◑",
}

RESULT_ICON = {
    "success":                   "✓",
    "partial_success":           "◑",
    "failed":                    "✗",
    "unexpected_outcome":        "⚡",
    "dignity_violation_detected":"🛑",
}


def _icon(event: dict) -> str:
    et = event.get("event_type", "")
    result = event.get("result", "")
    if et == "reality_feedback" and result:
        return RESULT_ICON.get(result, "◑")
    return EVENT_ICON.get(et, "•")


def _short_hash(h: str | None) -> str:
    return h[:12] + "…" if h and len(h) >= 12 else (h or "—")


def _print_event(event: dict, *, verbose: bool = False) -> None:
    icon   = _icon(event)
    et     = event.get("event_type", "?")
    ts     = event.get("timestamp", "")[:19].replace("T", " ")
    cid    = event.get("claim_id", "")
    speaker = event.get("speaker", "")
    result = event.get("result", "")

    label = f"[{et}]"
    if result:
        label += f" → {result}"

    print(f"  {icon} {ts}  {label}")
    if cid:
        print(f"       claim_id: {cid}")
    if speaker:
        print(f"       speaker:  {speaker}")

    # Type-specific fields
    for key in ("reason", "proposed_amendment", "note", "notes",
                "correction_reason", "disputed_condition", "amends_condition"):
        val = event.get(key)
        if val:
            truncated = str(val)[:100] + ("…" if len(str(val)) > 100 else "")
            print(f"       {key}: {truncated}")

    if event.get("dignity_violation"):
        print("       ⚠ DIGNITY VIOLATION — HUMAN REVIEW REQUIRED")
    if event.get("requires_human_review"):
        print("       ⚠ requires_human_review: true")

    if verbose:
        print(f"       hash: {_short_hash(event.get('event_hash'))}")
        if "previous_event_hash" in event:
            print(f"       prev: {_short_hash(event.get('previous_event_hash'))}")
    print()


# ── Query modes ───────────────────────────────────────────────

def query_claim_id(claim_id: str, table_filter: str | None = None) -> None:
    tables = [table_filter] if table_filter else sorted(VALID_TABLES)
    total = 0
    for table in tables:
        events = [e for e in read_all(table) if e.get("claim_id") == claim_id]
        if not events:
            continue
        print(f"── {table.upper()} ({len(events)} events) ──")
        for e in events:
            _print_event(e)
        total += len(events)
    if total == 0:
        print(f"No events found for claim_id: {claim_id}")


def query_event_type(event_type: str) -> None:
    total = 0
    for table in sorted(VALID_TABLES):
        events = [e for e in read_all(table) if e.get("event_type") == event_type]
        if not events:
            continue
        print(f"── {table.upper()} ──")
        for e in events:
            _print_event(e)
        total += len(events)
    if total == 0:
        print(f"No events found with event_type: {event_type}")


def show_timeline(claim_id: str) -> None:
    """Show all events for a claim across all tables, sorted by timestamp."""
    all_events = []
    for table in VALID_TABLES:
        for e in read_all(table):
            if e.get("claim_id") == claim_id:
                e["_table"] = table
                all_events.append(e)

    if not all_events:
        print(f"No events found for claim_id: {claim_id}")
        return

    all_events.sort(key=lambda e: e.get("timestamp", ""))

    print(f"── TIMELINE: {claim_id} ({len(all_events)} events) ──")
    print()
    for e in all_events:
        table = e.pop("_table", "?")
        icon  = _icon(e)
        et    = e.get("event_type", "?")
        ts    = e.get("timestamp", "")[:19].replace("T", " ")
        result = f" → {e['result']}" if e.get("result") else ""
        print(f"  {icon} {ts}  [{table}] {et}{result}")

        # Brief summary line
        for key in ("reason", "proposed_amendment", "notes", "note", "correction_reason"):
            val = e.get(key)
            if val:
                print(f"       └─ {str(val)[:90]}{'…' if len(str(val)) > 90 else ''}")
                break

        if e.get("dignity_violation"):
            print("       └─ ⚠ DIGNITY VIOLATION")
    print()


def show_contributions(claim_id: str) -> None:
    """Show contribution events and their statuses for a claim."""
    events = [e for e in read_all("contributions") if e.get("claim_id") == claim_id]
    if not events:
        print(f"No contribution events for claim_id: {claim_id}")
        return

    by_type: dict[str, list[dict]] = defaultdict(list)
    for e in events:
        by_type[e.get("contribution_type", "unknown")].append(e)

    print(f"── CONTRIBUTIONS: {claim_id} ──")
    print()
    for ctype, evts in sorted(by_type.items()):
        print(f"  [{ctype.upper()}]")
        for e in evts:
            icon = _icon(e)
            et   = e.get("event_type", "?")
            contributor = e.get("contributor", e.get("contributor_id", "?"))
            ts   = e.get("timestamp", "")[:19].replace("T", " ")
            print(f"    {icon} {ts}  {et}  — {contributor}")
        print()


def show_negotiation_history(claim_id: str) -> None:
    """Show full negotiation history for a claim."""
    events = [e for e in read_all("negotiations") if e.get("claim_id") == claim_id]
    if not events:
        print(f"No negotiation events for claim_id: {claim_id}")
        return

    print(f"── NEGOTIATION HISTORY: {claim_id} ({len(events)} events) ──")
    print()
    for e in events:
        _print_event(e, verbose=True)


def verify_all() -> None:
    print("── CHAIN INTEGRITY VERIFICATION ──")
    print()
    all_ok = True
    for table in sorted(VALID_TABLES):
        errors = verify_chain(table)
        count  = count_events(table)
        if errors:
            print(f"  ✗ {table}: {count} events — {len(errors)} error(s)")
            for err in errors:
                print(f"      → {err}")
            all_ok = False
        else:
            print(f"  ✓ {table}: {count} events — chain intact")
    print()
    if all_ok:
        print("All tables: chain integrity verified.")
    else:
        print("Chain integrity errors detected. Do not trust affected events.")


def show_stats() -> None:
    print("── SU-TABLE STATISTICS ──")
    print()
    total = 0
    for table in sorted(VALID_TABLES):
        events = read_all(table)
        count = len(events)
        total += count
        claim_ids = {e.get("claim_id") for e in events if e.get("claim_id")}
        print(f"  {table:20s} {count:4d} events   {len(claim_ids)} claim(s)")
    print()
    print(f"  {'TOTAL':20s} {total:4d} events")
    print()


# ── Main ──────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Query su-table JSONL event logs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python runtime/sutable_query.py --claim-id housing-001
  python runtime/sutable_query.py --claim-id housing-001 --table negotiations
  python runtime/sutable_query.py --event-type objection
  python runtime/sutable_query.py --timeline housing-001
  python runtime/sutable_query.py --contributions housing-001
  python runtime/sutable_query.py --negotiation-history housing-001
  python runtime/sutable_query.py --verify
  python runtime/sutable_query.py --stats
        """,
    )
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--claim-id",           metavar="ID",
                      help="Show all events for a claim_id")
    mode.add_argument("--event-type",         metavar="TYPE",
                      help="Show all events of a given event_type")
    mode.add_argument("--timeline",           metavar="ID",
                      help="Show chronological timeline for a claim_id")
    mode.add_argument("--contributions",      metavar="ID",
                      help="Show contribution events for a claim_id")
    mode.add_argument("--negotiation-history",metavar="ID",
                      help="Show negotiation history for a claim_id")
    mode.add_argument("--verify",             action="store_true",
                      help="Verify hash chain integrity of all tables")
    mode.add_argument("--stats",              action="store_true",
                      help="Show event count statistics for all tables")

    p.add_argument("--table", metavar="TABLE",
                   help="Filter --claim-id query to a specific table")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    print("=" * 60)
    print("SU-TABLE QUERY — dango-gitsea-bridge")
    print("=" * 60)
    print()

    if args.claim_id:
        query_claim_id(args.claim_id, args.table)
    elif args.event_type:
        query_event_type(args.event_type)
    elif args.timeline:
        show_timeline(args.timeline)
    elif args.contributions:
        show_contributions(args.contributions)
    elif args.negotiation_history:
        show_negotiation_history(args.negotiation_history)
    elif args.verify:
        verify_all()
    elif args.stats:
        show_stats()

    print("=" * 60)


if __name__ == "__main__":
    main()
