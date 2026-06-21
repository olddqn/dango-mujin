"""
case_registry.py — Mujin Platform MVP v1.1: Phase A Data Layer

Create and evolve Mujin Case records as append-only events.

"Registration is not proof."
"Withdrawal is not failure."
"Support is not debt."
"advisory_only is not moral immunity."

What this module does:
  - create_mujin_case(...)        draft a case (consent active / pending / deferred)
  - withdraw_mujin_case(...)      record withdrawal — never recorded as failure
  - record_objection(...)         subject objection, incl. non-technical channels (D-1)
  - record_progress(...)          append a neutral progress entry
  - record_non_mujin_support(...) honour support outside Mujin as equal (D-8)

What this module never does:
  - write to Dan-Go Execution Logs / Claims / Directives (ADR-001/002)
  - modify Relief Case Memory (ADR-003 — referenced via source_ref only)
  - write Reality Feedback (that is Phase D, through the canonical
    bridge/sutable/reality_feedback.jsonl only)
  - score, rank, or judge anyone

Demo:
  python -m bridge.mujin.case_registry        (run from the repository root)
"""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from .schemas import (
    CREATABLE_FROM,
    CREATED_FROM_VALUES,
    CASE_STATUSES,
    CONSENT_STATUSES,
    NEED_STATUSES,
    NON_MUJIN_SUPPORT_KINDS,
    OBJECTION_CHANNELS,
    OBJECTION_TARGETS,
    VISIBILITY_VALUES,
    ConsentRecord,
    DeferredConsent,
    MujinCase,
    Need,
    NonMujinSupport,
    ObjectionRecord,
    ProgressLog,
    base_invariants,
)
from .store import (
    CASES_JSONL,
    EXAMPLES_DIR,
    NON_MUJIN_JSONL,
    OBJECTIONS_JSONL,
    REPORTS_DIR,
    MujinStoreError,
    append_jsonl,
    latest_case_state,
    read_jsonl,
    utc_now_iso,
    write_json_new,
)


class MujinCaseError(Exception):
    """Raised when a case operation would violate an invariant."""


# ── create ────────────────────────────────────────────────────────────────────

def create_mujin_case(
    case_id: str,
    created_from: str,
    needs: list[dict[str, Any]] | None = None,
    source_ref: dict[str, Any] | None = None,
    consent_status: str = "pending",
    can_consent: bool = True,
    deferred: DeferredConsent | None = None,
    discovery_origin: dict[str, Any] | None = None,
    success_metric: dict[str, Any] | None = None,
    visibility: str = "participants_only",
) -> dict[str, Any]:
    """Draft a Mujin Case and append it to the case event stream.

    Rules enforced here (SPEC §4, §16; ADR-003/005):
      - created_from must be a creatable value; "scouter" is reserved (D-7).
      - a subject who cannot consent is never marked consenting (D-3):
        can_consent=False forces consent_status="deferred".
      - deferred consent requires a DeferredConsent detail with a
        confirmation-duty holder (D-2).
      - promotion from a relief case requires source_ref.relief_case_id
        (reference only — the Relief Case itself is never modified).
    """
    if created_from not in CREATED_FROM_VALUES:
        raise MujinCaseError(f"unknown created_from: {created_from!r}")
    if created_from not in CREATABLE_FROM:
        raise MujinCaseError(
            f"created_from {created_from!r} is reserved: no generation path exists "
            "in the MVP (the Saiyan Scouter question is an unresolved Dan-Go Claim)"
        )
    if consent_status not in CONSENT_STATUSES:
        raise MujinCaseError(f"unknown consent status: {consent_status!r}")
    if visibility not in VISIBILITY_VALUES:
        raise MujinCaseError(f"unknown visibility: {visibility!r}")
    if not can_consent and consent_status != "deferred":
        raise MujinCaseError(
            "a state of being unable to consent is not consent (D-3): "
            "can_consent=False requires consent_status='deferred'"
        )
    if consent_status == "deferred":
        if deferred is None or not deferred.confirmation_duty_holder:
            raise MujinCaseError(
                "deferred consent requires a DeferredConsent record naming the "
                "confirmation-duty holder (D-2)"
            )
    if created_from == "relief_case" and not (source_ref or {}).get("relief_case_id"):
        raise MujinCaseError(
            "promotion from a relief case requires source_ref.relief_case_id "
            "(ADR-003 — reference only, the Relief Case is never modified)"
        )
    if latest_case_state(case_id) is not None:
        raise MujinCaseError(f"case_id already exists in the event stream: {case_id}")

    now = utc_now_iso()
    consent = ConsentRecord(
        status=consent_status,
        can_consent=can_consent,
        obtained_at=now if consent_status == "active" else None,
        confirmation_due=(consent_status == "deferred"),
        last_confirmed_at=now if consent_status == "active" else None,
    )
    case = MujinCase(
        case_id=case_id,
        created_from=created_from,
        source_ref=source_ref or {},
        discovery_origin=discovery_origin or {
            "how": "subject-initiated" if created_from == "direct_application" else "",
            "by": "",
            "disclosed_to_subject": created_from == "direct_application",
        },
        consent=consent,
        deferred_consent=deferred,
        needs=[Need(**n) for n in (needs or [])],
        success_metric=success_metric or {
            "set_by": "default",
            "description": "defined by the parties; never economic independence by default",
        },
        visibility=visibility,
        status="open",
        created_at=now,
        updated_at=now,
    )
    record = case.to_record()
    record["event_type"] = "case_created"
    return append_jsonl(CASES_JSONL, record)


# ── withdraw ──────────────────────────────────────────────────────────────────

def withdraw_mujin_case(case_id: str, reason: str | None = None) -> dict[str, Any]:
    """Record withdrawal of consent. Withdrawal is not failure (A-3, D-5).

    The reason is optional, never required, and never used to score anyone.
    The case stops being public and stops accepting contributions. Earlier
    events remain untouched in the stream (provenance preserved).
    """
    state = latest_case_state(case_id)
    if state is None:
        raise MujinCaseError(f"unknown case: {case_id}")

    record = dict(state)
    record["event_type"] = "case_withdrawn"
    record["consent"] = dict(record.get("consent") or {})
    record["consent"]["status"] = "withdrawn"
    record["consent"]["withdrawal_reason"] = reason   # optional — may stay None
    record["visibility"] = "private"
    record["status"] = "not_pursued"                  # neutral; not failure
    record["withdrawal_is_failure"] = False           # stated explicitly, again
    record["updated_at"] = utc_now_iso()
    record.pop("event_hash", None)
    record.pop("appended_at", None)
    return append_jsonl(CASES_JSONL, record)


# ── objection ─────────────────────────────────────────────────────────────────

def record_objection(
    objection_id: str,
    target: str,
    content: str,
    channel: str = "ui",
    case_id: str | None = None,
    submitted_by: str = "subject",
) -> dict[str, Any]:
    """Record a subject's objection (SPEC §15, ADR-005 D-1).

    Objections may target Mujin, an NPO, a supporter, or an AI agent. They
    may arrive through non-technical channels (phone, in person, transcribed).
    Filing an objection never counts against the subject and is never used
    for profiling.
    """
    if target not in OBJECTION_TARGETS:
        raise MujinCaseError(f"unknown objection target: {target!r}")
    if channel not in OBJECTION_CHANNELS:
        raise MujinCaseError(f"unknown objection channel: {channel!r}")
    if case_id is not None and latest_case_state(case_id) is None:
        raise MujinCaseError(f"objection references unknown case: {case_id}")

    objection = ObjectionRecord(
        objection_id=objection_id,
        case_id=case_id,
        target=target,
        channel=channel,
        content=content,
        submitted_by=submitted_by,
        created_at=utc_now_iso(),
    )
    record = asdict(objection)
    record["record_type"] = "mujin_objection"
    record["event_type"] = "objection_recorded"
    record.update(base_invariants())
    return append_jsonl(OBJECTIONS_JSONL, record)


# ── progress ──────────────────────────────────────────────────────────────────

def record_progress(case_id: str, entry_id: str, content: str, actor: str) -> dict[str, Any]:
    """Append a neutral progress entry to a case (SPEC §4 progress_log)."""
    state = latest_case_state(case_id)
    if state is None:
        raise MujinCaseError(f"unknown case: {case_id}")
    if (state.get("consent") or {}).get("status") == "withdrawn":
        raise MujinCaseError(
            f"case {case_id} is withdrawn; no further progress is recorded "
            "(withdrawal is not failure — it is a closed door, respected)"
        )

    entry = ProgressLog(
        entry_id=entry_id, content=content, actor=actor, created_at=utc_now_iso(),
    )
    record = dict(state)
    record["event_type"] = "progress_recorded"
    record["progress_log"] = list(record.get("progress_log") or []) + [asdict(entry)]
    record["updated_at"] = entry.created_at
    record.pop("event_hash", None)
    record.pop("appended_at", None)
    return append_jsonl(CASES_JSONL, record)


# ── non-Mujin support ─────────────────────────────────────────────────────────

def record_non_mujin_support(
    record_id: str,
    kind: str,
    description: str,
    recorded_by: str,
    case_id: str | None = None,
) -> dict[str, Any]:
    """Honour support that did not pass through Mujin (SPEC §17, D-8).

    Family / friends / community mutual aid is equal in dignity to
    Mujin-mediated support. This record gives it visibility without ranking.
    """
    if kind not in NON_MUJIN_SUPPORT_KINDS:
        raise MujinCaseError(f"unknown non-Mujin support kind: {kind!r}")

    support = NonMujinSupport(
        record_id=record_id,
        case_id=case_id,
        kind=kind,
        description=description,
        recorded_by=recorded_by,
        created_at=utc_now_iso(),
    )
    record = asdict(support)
    record["record_type"] = "non_mujin_support"
    record["event_type"] = "non_mujin_support_recorded"
    record.update(base_invariants())
    return append_jsonl(NON_MUJIN_JSONL, record)


# ── demo / CLI verification ───────────────────────────────────────────────────

def run_demo() -> dict[str, Any]:
    """Generate a safe, pseudonymous demo dataset and a sample report.

    No personally identifying information. Handles are pseudonyms taken from
    the existing Dan-Go example vocabulary (commons ids, not people).
    """
    summary: dict[str, Any] = {"steps": [], "errors_demonstrated": []}

    def step(name: str, result: dict[str, Any]) -> None:
        summary["steps"].append({"step": name, "event_hash": result.get("event_hash")})
        print(f"  ✓ {name}")

    demo_case = "mujin-case-demo-001"
    if latest_case_state(demo_case) is not None:
        print(f"  · demo case {demo_case} already exists — skipping creation, demo is append-only")
    else:
        # 1. promotion from an existing relief case (reference only, ADR-003)
        step("create case (promoted from relief-case-002, consent active)", create_mujin_case(
            case_id=demo_case,
            created_from="relief_case",
            source_ref={"relief_case_id": "relief-case-002", "claim_id": "claim-proposal-002"},
            consent_status="active",
            needs=[{
                "need_id": "need-001",
                "description": "coordination help for a housing advocacy conversation",
                "addresses_condition": "coordination_channel_established_between_orgs",
                "status": "open",
            }],
            discovery_origin={
                "how": "phase-18 relief case promotion, human review",
                "by": "jammy-house-001",
                "disclosed_to_subject": True,
            },
            success_metric={
                "set_by": "subject",
                "description": "the subject defines success as: stable housing conversation continues",
            },
            visibility="participants_only",
        ))

        # 2. a deferred-consent proxy registration (D-2/D-3)
        step("create case (npo_proxy, deferred consent)", create_mujin_case(
            case_id="mujin-case-demo-002",
            created_from="npo_proxy",
            consent_status="deferred",
            can_consent=False,
            deferred=DeferredConsent(
                reason_category="language_barrier",
                registered_by="dra-001",
                confirmation_duty_holder="dra-001",
                discovery_origin={
                    "how": "existing relief route follow-up",
                    "by": "dra-001",
                    "disclosed_to_subject": False,
                },
                deferred_at=utc_now_iso(),
            ),
            needs=[{
                "need_id": "need-002",
                "description": "translation support for an upcoming consultation",
                "addresses_condition": None,
                "status": "open",
            }],
        ))

        # 3. progress on the active case
        step("record progress", record_progress(
            demo_case, "progress-001",
            "first coordination conversation scheduled by the parties",
            actor="jammy-house-001",
        ))

        # 4. an objection through a NON-TECHNICAL channel (D-1)
        step("record objection (phone, against npo)", record_objection(
            objection_id="objection-demo-001",
            target="npo",
            channel="phone",
            content="the subject objects to how their availability was described",
            case_id=demo_case,
            submitted_by="third_party_on_behalf",
        ))

        # 5. support outside Mujin, equal in dignity (D-8)
        step("record non-Mujin support (community)", record_non_mujin_support(
            record_id="nms-demo-001",
            kind="community",
            description="neighbours organised meal support without Mujin — equal in dignity",
            recorded_by="jammy-house-001",
            case_id=demo_case,
        ))

        # 6. withdrawal — not failure (D-5)
        step("withdraw demo case 002 (withdrawal is not failure)", withdraw_mujin_case(
            "mujin-case-demo-002", reason=None,   # reason optional, stays None
        ))

        # 7. demonstrate refusals (invariants hold)
        try:
            create_mujin_case("mujin-case-demo-003", created_from="scouter")
        except MujinCaseError as exc:
            summary["errors_demonstrated"].append(f"scouter refused: {exc}")
            print("  ✓ refusal demonstrated: created_from='scouter' is reserved")
        try:
            create_mujin_case("mujin-case-demo-004", created_from="npo_proxy",
                              consent_status="active", can_consent=False)
        except MujinCaseError as exc:
            summary["errors_demonstrated"].append(f"inability-to-consent refused: {exc}")
            print("  ✓ refusal demonstrated: cannot-consent is never 'active' consent")

    # snapshot of the demo case → examples/ (write-once)
    example_path = EXAMPLES_DIR / "mujin-case-demo.json"
    if not example_path.exists():
        write_json_new(example_path, latest_case_state(demo_case) or {})
        print(f"  ✓ example snapshot: {example_path.name}")

    # sample registry report → reports/ (write-once)
    report = {
        "record_type": "mujin_case_registry_report",
        "report_id": "mujin-registry-report-001",
        "generated_at": utc_now_iso(),
        "case_events": len(read_jsonl(CASES_JSONL)),
        "objection_events": len(read_jsonl(OBJECTIONS_JSONL)),
        "non_mujin_support_events": len(read_jsonl(NON_MUJIN_JSONL)),
        "notes": [
            "Counts are event counts in append-only streams, not judgments.",
            "Withdrawn cases are not failures and are not reported as such.",
            "Non-Mujin support appears here as equal in dignity, unranked.",
        ],
        **base_invariants(),
    }
    report_path = REPORTS_DIR / "mujin_case_registry_report.json"
    if not report_path.exists():
        write_json_new(report_path, report)
        print(f"  ✓ sample report: {report_path.name}")

    return summary


def main() -> None:
    print("=" * 72)
    print("MUJIN CASE REGISTRY — Phase A Data Layer demo (advisory only)")
    print('"Registration is not proof." "Withdrawal is not failure."')
    print('"Support is not debt." "advisory_only is not moral immunity."')
    print("=" * 72)
    summary = run_demo()
    print("-" * 72)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("-" * 72)
    print("This demo wrote only under bridge/mujin/. No Dan-Go file was touched.")


if __name__ == "__main__":
    main()
