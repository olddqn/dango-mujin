#!/usr/bin/env python3
"""
claim_to_directive.py — Claim → Directive Conversion (Phase 24)
Dan-Go × GITSEA — Globe Directive Layer

Converts claim_draft Claims into Dan-Go Directive format.
Only claim_draft claims are eligible for conversion.
Outputs both JSON and Markdown to globe/directives/.

Claim is not execution.
Directive is not coercion.
Directive creates no legal authority.
Directive only describes a proposed executable path.
Human approval is required before real-world execution.

authority: none · advisory only · human_approval_required: true
directive_creates_legal_authority: false · directive_is_coercion: false

Usage:
    python3 globe/runtime/claim_to_directive.py convert <claim_id>
    python3 globe/runtime/claim_to_directive.py convert-globe <globe_id>
    python3 globe/runtime/claim_to_directive.py list
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_GLOBE_DIR = Path(__file__).resolve().parents[1]
_CLAIMS_DIR = _GLOBE_DIR / "claims"
_DIRECTIVES_DIR = _GLOBE_DIR / "directives"

# Claim is not execution.
# Directive is not coercion.
# Directive creates no legal authority.
# Human approval is required before real-world execution.

PHASE_INVARIANTS = {
    "source_type": "claim",
    "authority": "none",
    "execution_allowed": False,
    "moves_money": False,
    "hard_enforcement": False,
    "advisory": True,
    "append_only": True,
    "contestable": True,
    "human_approval_required": True,
    "directive_creates_legal_authority": False,
    "directive_is_coercion": False,
    "directive_creates_obligation": False,
    "conversion_is_execution": False,
    "directive_certifies_outcome": False,
    "directive_allocates_resources": False,
}

NON_AUTHORITY_CLAUSE = (
    "このディレクティブは助言的な提案に過ぎない。"
    "実世界での実行には人間の承認が必要であり、いかなる法的権限も生じない。"
    "参加は任意であり、強制的手段は禁じられている。出力はappend-onlyであり、変更は新しいエントリとして記録される。"
    " / "
    "This directive is advisory only. Real-world execution requires human approval. "
    "No legal authority is created. Participation is voluntary. "
    "Coercion is a forbidden means. Output is append-only; changes are recorded as new entries."
)


# ─── Data helpers ───────────────────────────────────────────────────────────────

def _load_claims() -> list:
    _CLAIMS_DIR.mkdir(exist_ok=True)
    claims = []
    for f in sorted(_CLAIMS_DIR.glob("*.json")):
        try:
            claims.append(json.loads(f.read_text()))
        except Exception:
            pass
    return claims


def _load_directives() -> list:
    _DIRECTIVES_DIR.mkdir(exist_ok=True)
    directives = []
    for f in sorted(_DIRECTIVES_DIR.glob("*.json")):
        try:
            directives.append(json.loads(f.read_text()))
        except Exception:
            pass
    return directives


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─── Derivation helpers ─────────────────────────────────────────────────────────

def _derive_objective(claim: dict) -> str:
    """Extract a concise objective from the claim body."""
    body = claim.get("claim_body", "")
    title = claim.get("title", "")

    for marker in ["提案：", "Proposal: "]:
        idx = body.find(marker)
        if idx == -1:
            continue
        section = body[idx + len(marker):]
        # Stop at first sentence boundary
        positions = [section.find(e) for e in ["。", ". ", "\n\n"] if section.find(e) != -1]
        end = min(positions) if positions else min(len(section), 200)
        obj = section[:end].strip()
        if obj:
            return obj

    # Fallback: title
    return title


def _derive_scope(claim: dict) -> dict:
    """Derive in-scope and out-of-scope lists from the claim title and body."""
    title = claim.get("title", "")
    body = claim.get("claim_body", "")

    # Build in-scope items around the claim subject
    in_scope = [
        f"「{title}」の実行計画の策定と準備",
        "関係者への情報共有と任意参加意思の確認",
        "熟議ログに基づく未解決論点の整理と記録",
        "実行フィードバック（Reality Feedback）の Dan-Go ログへの追記",
    ]

    # Standard out-of-scope for all directives
    out_of_scope = [
        "参加者への強制・義務の付与（いかなる形でも）",
        "法的拘束力のある契約・合意の締結",
        "資金・資産・信用の配分または移動",
        "他の Globe・外部組織・国家機関への権限行使または命令",
        "Directive の自動実行（人間の承認なしの実世界アクション）",
    ]

    # Enrich in-scope with body-derived hints
    # Look for explicit action keywords in the body
    action_hints = []
    for kw, hint in [
        ("D.R.A.", "D.R.A.（難民支援行動）との連携調整"),
        ("住居", "住居アドボカシーの熟議フロー運用"),
        ("食料", "食料支援スケジュールの合意形成"),
        ("テナンシー", "テナンシー問題への合意形成プロセス適用"),
        ("合意形成", "合意形成プロセスの設計・試行"),
        ("プライバシー", "プライバシー保護ツールの共同開発計画"),
        ("翻訳", "多言語化・翻訳作業の調整"),
    ]:
        if kw in body and hint not in in_scope:
            action_hints.append(hint)

    if action_hints:
        in_scope.extend(action_hints)

    return {"in_scope": in_scope, "out_of_scope": out_of_scope}


def _derive_execution_steps(claim: dict) -> list:
    """Derive a generic 4-step execution template from claim content."""
    title = claim.get("title", "")

    return [
        {
            "step_id": "step-001",
            "description": f"前提条件の確認 — 「{title}」の実施に必要な条件を列挙し、現状との差異を記録する",
            "description_en": (
                f"Confirm prerequisites — list conditions required for '{title}' "
                "and record gaps between required and observed state"
            ),
            "required_contributions": ["情報提供", "状況確認"],
            "status": "pending",
            "human_approval_required": True,
            "execution_allowed": False,
        },
        {
            "step_id": "step-002",
            "description": "関係者への通知と任意参加の確認 — 強制・勧誘は禁じられた手段",
            "description_en": (
                "Notify stakeholders and confirm voluntary participation — "
                "coercion and solicitation are forbidden means"
            ),
            "required_contributions": ["連絡・情報共有", "参加意思の自発的表明"],
            "status": "pending",
            "human_approval_required": True,
            "execution_allowed": False,
        },
        {
            "step_id": "step-003",
            "description": "試験的実施の承認と観察 — 人間の承認なしに実世界アクションは行わない",
            "description_en": (
                "Approve pilot execution and observe — "
                "no real-world action without human approval"
            ),
            "required_contributions": ["人間による実施承認", "観察・記録担当者の合意"],
            "status": "pending",
            "human_approval_required": True,
            "execution_allowed": False,
        },
        {
            "step_id": "step-004",
            "description": "実行フィードバックの記録 — Dan-Go Reality Feedback へ追記（append-only）",
            "description_en": (
                "Record execution feedback — append to Dan-Go Reality Feedback log "
                "(append-only)"
            ),
            "required_contributions": ["フィードバック記録", "ケアループとの接続確認"],
            "status": "pending",
            "human_approval_required": False,
            "execution_allowed": False,
        },
    ]


def _derive_required_evidence(claim: dict) -> list:
    """Derive required evidence list for execution gate."""
    return [
        "Constitution チェック通過（いかなる参加者の dignity も侵害しないこと）",
        "関係者からの自発的な参加意思の記録（強制・期待の押しつけではないこと）",
        "熟議ログへの反対意見・懸念事項の記録（少数意見は削除されない）",
        "Dan-Go ログへの Directive 登録（append-only）",
        "人間による各ステップの明示的承認（自動実行は禁止）",
    ]


# ─── Conversion ─────────────────────────────────────────────────────────────────

def convert_claim(claim_id: str, verbose: bool = True) -> dict | None:
    """Convert a single claim_draft claim to a Directive."""
    claims = _load_claims()

    c = next((x for x in claims if x.get("claim_id") == claim_id), None)
    if not c:
        if verbose:
            print(f"ERROR: claim '{claim_id}' not found in globe/claims/.")
            print("Run: python3 globe/runtime/proposal_to_claim.py list")
        return None

    if c.get("status") != "claim_draft":
        if verbose:
            print(
                f"ERROR: claim '{claim_id}' has status '{c.get('status')}'. "
                "Only claim_draft claims can be converted to Directives."
            )
        return None

    now = _now()
    directive_id = f"directive-{claim_id}"

    # Preserve created_at if the directive already exists
    existing_path = _DIRECTIVES_DIR / f"{directive_id}.json"
    original_created_at = now
    if existing_path.exists():
        try:
            existing = json.loads(existing_path.read_text())
            original_created_at = existing.get("created_at", now)
        except Exception:
            pass

    objective = _derive_objective(c)
    scope = _derive_scope(c)
    execution_steps = _derive_execution_steps(c)
    required_evidence = _derive_required_evidence(c)

    directive = {
        "directive_id": directive_id,
        **PHASE_INVARIANTS,
        "source_claim_id": claim_id,
        "source_proposal_id": c.get("source_proposal_id", ""),
        "globe_id": c.get("globe_id", ""),
        "title": c.get("title", ""),
        "objective": objective,
        "scope": scope,
        "non_authority_clause": NON_AUTHORITY_CLAUSE,
        "execution_steps": execution_steps,
        "required_evidence": required_evidence,
        "deliberation_count": c.get("deliberation_count", 0),
        "status": "directive_draft",
        "created_at": original_created_at,
        "updated_at": now,
    }

    # Write JSON
    _DIRECTIVES_DIR.mkdir(exist_ok=True)
    json_path = _DIRECTIVES_DIR / f"{directive_id}.json"
    json_path.write_text(json.dumps(directive, ensure_ascii=False, indent=2))

    # Write Markdown
    md_path = _DIRECTIVES_DIR / f"{directive_id}.md"
    md_path.write_text(_build_markdown(directive))

    if verbose:
        print(f"directive_id:  {directive_id}")
        print(f"source:        claim/{claim_id}")
        print(f"globe:         {c.get('globe_id', '')}")
        print(f"title:         {c.get('title', '')}")
        print(f"steps:         {len(execution_steps)}")
        print(f"status:        directive_draft")
        print(f"output (json): globe/directives/{directive_id}.json")
        print(f"output (md):   globe/directives/{directive_id}.md")
        print()
        print(
            "authority: none · directive_creates_legal_authority: false"
            " · human_approval_required: true"
        )

    return directive


# ─── Markdown output ─────────────────────────────────────────────────────────────

def _build_markdown(directive: dict) -> str:
    scope = directive.get("scope", {})
    in_scope_lines = "\n".join(f"- {s}" for s in scope.get("in_scope", []))
    out_scope_lines = "\n".join(f"- {s}" for s in scope.get("out_of_scope", []))

    steps_md = ""
    for s in directive.get("execution_steps", []):
        approval_note = " *(人間の承認が必要 / human approval required)*" if s.get("human_approval_required") else ""
        contribs = "、".join(s.get("required_contributions", []))
        steps_md += (
            f"### {s['step_id']}: {s['description']}\n\n"
            f"> {s.get('description_en', '')}{approval_note}\n\n"
            f"- **貢献種別 / required contributions:** {contribs}\n"
            f"- **status:** `{s.get('status', 'pending')}`\n"
            f"- **execution_allowed:** `{str(s.get('execution_allowed', False)).lower()}`\n\n"
        )

    evidence_lines = "\n".join(f"- {e}" for e in directive.get("required_evidence", []))

    src_proposal = directive.get("source_proposal_id", "")
    src_claim = directive.get("source_claim_id", "")
    globe_id = directive.get("globe_id", "")

    return f"""# {directive['title']}

> **directive_id:** `{directive['directive_id']}`
> **status:** `{directive['status']}`
> **chain:** Proposal `{src_proposal}` → Claim `{src_claim}` → Directive `{directive['directive_id']}`
> **globe:** `{globe_id}`

---

## ⚠️ Non-Authority Clause

> {directive['non_authority_clause']}

**実世界での実行ステップを開始する前に、人間の明示的な承認が必要です。**
**Human approval is required before any real-world execution step begins.**

---

## Objective（目的）

{directive.get('objective', '')}

---

## Scope（範囲）

### In Scope（対象範囲）

{in_scope_lines}

### Out of Scope（対象外）

{out_scope_lines}

---

## Execution Steps（実行ステップ）

> すべてのステップは advisory（助言的）です。強制力はありません。
> All steps are advisory. No step has coercive force.

{steps_md}---

## Required Evidence（実行前に必要な記録）

実行ゲート：以下がすべて記録されるまで実世界アクションは開始しない。
Execution gate: no real-world action begins until all of the following are recorded.

{evidence_lines}

---

## Invariants（不変条件）

| Field | Value |
|-------|-------|
| `authority` | `none` |
| `directive_creates_legal_authority` | `false` |
| `directive_is_coercion` | `false` |
| `directive_creates_obligation` | `false` |
| `directive_allocates_resources` | `false` |
| `directive_certifies_outcome` | `false` |
| `human_approval_required` | `true` |
| `execution_allowed` | `false` (until human-approved per step) |
| `moves_money` | `false` |
| `conversion_is_execution` | `false` |
| `append_only` | `true` |
| `contestable` | `true` |

---

_Generated by Dan-Go Mujin · Phase 24 · {directive.get('created_at', '')[:10]}_

> Claim is not execution. Directive is not coercion. Directive creates no legal authority.
> Directive only describes a proposed executable path.
"""


# ─── Batch convert ───────────────────────────────────────────────────────────────

def convert_globe(globe_id: str) -> None:
    """Batch-convert all claim_draft claims for a globe into Directives."""
    claims = _load_claims()
    eligible = [
        c for c in claims
        if c.get("globe_id") == globe_id and c.get("status") == "claim_draft"
    ]

    if not eligible:
        print(f"No claim_draft claims found for globe '{globe_id}'.")
        print("Run: python3 globe/runtime/proposal_to_claim.py list")
        return

    print(f"Converting {len(eligible)} claim_draft claim(s) in globe '{globe_id}'...\n")
    converted = 0
    for c in eligible:
        cid = c["claim_id"]
        print(f"--- {cid} ---")
        result = convert_claim(cid, verbose=True)
        if result:
            converted += 1
        print()

    print(f"Done. {converted}/{len(eligible)} claims converted to Directives.")
    print()
    print(
        "Claim is not execution. Directive is not coercion. "
        "Directive creates no legal authority."
    )


# ─── List ────────────────────────────────────────────────────────────────────────

def list_directives() -> None:
    """List all generated directives in globe/directives/."""
    directives = _load_directives()
    if not directives:
        print("No directives found in globe/directives/.")
        print()
        print("Run: python3 globe/runtime/claim_to_directive.py convert <claim_id>")
        return

    print(f"globe/directives/ — {len(directives)} directive(s)\n")
    for d in directives:
        steps = len(d.get("execution_steps", []))
        print(f"  {d.get('directive_id', '?')}")
        print(f"    source:    claim/{d.get('source_claim_id', '?')}")
        print(f"    proposal:  {d.get('source_proposal_id', '?')}")
        print(f"    globe:     {d.get('globe_id', '?')}")
        print(f"    title:     {d.get('title', '?')}")
        print(f"    status:    {d.get('status', '?')}")
        print(f"    steps:     {steps}")
        print(f"    created:   {str(d.get('created_at', '?'))[:19]}")
        print()


# ─── Main ────────────────────────────────────────────────────────────────────────

def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)

    cmd = args[0]

    if cmd == "convert":
        if len(args) < 2:
            print("Usage: claim_to_directive.py convert <claim_id>")
            sys.exit(1)
        convert_claim(args[1])

    elif cmd == "convert-globe":
        if len(args) < 2:
            print("Usage: claim_to_directive.py convert-globe <globe_id>")
            sys.exit(1)
        convert_globe(args[1])

    elif cmd == "list":
        list_directives()

    else:
        print(f"Unknown command: {cmd}")
        print("Commands: convert, convert-globe, list")
        sys.exit(1)


if __name__ == "__main__":
    main()
