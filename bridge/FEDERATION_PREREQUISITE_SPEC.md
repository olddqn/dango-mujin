# Federation Prerequisite Promotion Specification

> **Status:** Implemented
> **Version:** 1.0
> **Part of:** dango-gitsea-bridge / Federation Prerequisite Promotion Layer

---

## Core Distinction

**A declared prerequisite is authority-based.**

Someone — a coordinator, a committee, a governance process — decides that condition X
must be satisfied before a claim can proceed. You must trust the declarer.
If you distrust the authority, you have no recourse except to leave.

**A learned prerequisite is evidence-based.**

No one declares it. It emerges when multiple independent negotiation processes
converge on the same condition through structural plan tree diff.
You can verify the evidence yourself. You can contest it with a better plan tree.
You can deprecate it if the evidence no longer holds.

Dan-Go implements only learned prerequisites.

```
Declared prerequisite: coordinator says X is required.
Learned prerequisite:  two independent plan trees, through negotiation, both
                       concluded that X must gate the next phase.
                       No coordinator. No declaration. Evidence only.
```

---

## Why This Matters

Most coordination systems conflate authority with knowledge.
If a rule is imposed by a trusted authority, it is assumed to be correct.
Challenging the rule means challenging the authority.

Dan-Go separates them.

A federation prerequisite carries no authority. It carries a traceable evidence
bundle: which claims converged, through which objections, through which plan trees.
Contesting the prerequisite means contesting the evidence — by producing a better plan.

This makes prerequisites contestable in the only meaningful way:
not by voting, not by argument, but by producing a plan tree that
achieves the claim goals without the supposedly necessary condition.

*"A learned prerequisite can be contested by producing a better plan tree."*

---

## Promotion Criteria

A condition becomes a federation prerequisite candidate when:

| Criterion | Value |
|-----------|-------|
| Independent claims that learned the condition | ≥ 2 (`INDEPENDENT_CLAIM_THRESHOLD`) |
| All evidence claims are dignity-safe | True (no `dignity_violation` objection on any plan) |
| Discovery method | Structural plan tree diff only (no text matching) |

A candidate is promoted to `federation_prerequisite_promoted` status when:

- It meets the threshold above
- It is not already promoted (dedup — append-only)
- `authority` is set to `"none"` (always; never overrideable)
- `contestable` is set to `True` (always; never overrideable)

---

## Evidence Strengthens with Convergence

A prerequisite becomes stronger when it survives independent convergence across more claims.

The housing federation demonstrates this progression:

| State | Claims | Plan authors | Objectors | evidence_score |
|-------|--------|-------------|-----------|----------------|
| Promoted (initial) | housing-001, housing-002 | z6MkproposerHousing, z6Contester001, z6MkremoteCollab001 | z6Object001 (×2) | 6 |
| Reaffirmed (3-way) | + housing-004 | + z6MkCommunityKitchen004 | + z6KitchenSafetyAgent004 | 8 |

The third claim (housing-004, community kitchen) introduced a new objector —
`z6KitchenSafetyAgent004` — independent of the `z6Object001` who objected in the first two.
This reduces objector concentration from 2/2 to 2/3 claims and increases the evidence score.

The promoted event is **not modified** (append-only). A `federation_prerequisite_reaffirmed`
event records the new evidence. The historical record is preserved: the promoted event
reflects the state at promotion time; the reaffirm event carries the strengthened case.

See `examples/prerequisite-3way.snapshot.json` for the full 3-way evidence bundle.
See `examples/housing-004-plan-v1.json` through `housing-004-memory-snapshot.json`
for the housing-004 negotiation sequence.

---

## Why Text Similarity is Forbidden

Conditions are detected by structural plan tree diff, not by text analysis.

**Why?**

Text similarity is fragile. It depends on:
- Language (English, Japanese, etc.)
- Author style
- Synonym choice
- Abbreviation conventions

A structural diff is deterministic. It depends only on:
- The `"condition"` field value on `branch` nodes
- Whether that condition appears in the counterplan tree but not the contested plan tree

Two plans written by different authors in different contexts, using identical condition
strings, will always produce the same learned condition — regardless of the surrounding
prose.

If two plan authors chose different condition names for the same concept
(`space_safety_check` vs `safety_assessed`), those are different conditions.
That is correct behavior: the protocol does not assume authors share vocabulary.
Convergence on terminology is itself a meaningful signal.

---

## Independence Detection

**`independent_convergence`** is the key signal. It is True when:
- The plan authors who proposed the converging plans are different across claims.

**`shared_authorship`** (False = stronger evidence):
- The same person authored plans in multiple evidence claims.
- Not a disqualifier, but weakens the independence claim.
  (If the same author wrote plans for housing-001 and housing-002, they may have
  deliberately included the same condition — that's coordination, not convergence.)

**`shared_objector`** (metadata only, not a disqualifier):
- The same agent raised objections in multiple evidence claims.
- This is recorded as evidence, not used to block promotion.
  A skilled agent may legitimately find the same structural gap in multiple claims.

**Evidence score:**
```
score = convergence_count × 2
      + 2  if independent_convergence
      + 1  if dignity_safe
      - 1  if objector_overlap
```

Score is transparent. It is a derived metric, not a hidden ranking.

---

## Evidence Bundle

Every promoted prerequisite has a traceable evidence bundle:

```json
{
  "condition": "space_safety_assessed",
  "evidence_bundle": {
    "claims": [
      {
        "claim_id": "housing-001",
        "objection_type": "insufficient_risk_coverage",
        "objector": "did:key:z6Object001",
        "contested_plan_id": "plan-housing-001-v2",
        "counterplan_id": "plan-housing-001-v3",
        "contested_plan_author": "did:key:z6MkproposerHousing",
        "counterplan_author": "did:key:z6Contester001",
        "learned_via": "plan_contest"
      },
      {
        "claim_id": "housing-002",
        "objection_type": "insufficient_risk_coverage",
        "objector": "did:key:z6Object001",
        "contested_plan_id": "plan-housing-002-v1",
        "counterplan_id": "plan-housing-002-v2",
        "contested_plan_author": "did:key:z6MkremoteCollab001",
        "counterplan_author": "did:key:z6MkremoteCollab001",
        "learned_via": "plan_contest"
      }
    ],
    "independent_convergence": true,
    "shared_authorship": false,
    "shared_objector": true,
    "dignity_safe": true,
    "evidence_score": 6
  }
}
```

Every field is traceable to a specific plan event in `plans.jsonl`.
Anyone can verify the bundle by re-running the structural diff.

---

## Prerequisite Lifecycle

```
candidate (below threshold)
    │
    │  convergence_count reaches threshold
    ▼
promoted  ◄──────────────────────────────────────────────────────┐
    │                                                            │
    │  contest event                                             │
    ▼                                                            │
contested                                                        │
    │                                                            │
    ├──► reaffirmed (new convergence evidence, or contest        │
    │               withdrawn) ───────────────────────────────────┘ (stays active)
    │
    └──► deprecated (plan tree evidence refutes the condition)
              │
              │  new convergence evidence in future cycle
              ▼
          (re-promotable — append-only, new promoted event)
```

---

## Promotion Event

```json
{
  "event_type": "federation_prerequisite_promoted",
  "condition": "space_safety_assessed",
  "evidence_claims": ["housing-001", "housing-002"],
  "promotion_basis": "independent_plan_tree_diff_convergence",
  "authority": "none",
  "contestable": true,
  "convergence_count": 2,
  "independent_convergence": true,
  "shared_authorship": false,
  "shared_objector": true,
  "dignity_safe": true,
  "evidence_score": 6,
  "timestamp": "...",
  "event_hash": "..."
}
```

`authority` is always `"none"`. This is not optional. It is enforced by
`prerequisite_promotion.py` at write time. No code path sets it to anything else.

---

## Prerequisite Status Values

| Status | Meaning |
|--------|---------|
| `promoted` | Meets threshold; active federation-level consideration |
| `contested` | Under contest; still advisory but marked as disputed |
| `reaffirmed` | Contest resolved in favor of the prerequisite |
| `deprecated` | Withdrawn — evidence no longer supports convergence |

---

## Contestability

Any participant can contest a promoted prerequisite:

```bash
python runtime/prerequisite_contest_resolver.py \
    --contest space_safety_assessed \
    --reason "pre-certified modular equipment bypasses space safety gate" \
    --speaker did:key:zContester
```

**The only valid form of contestation in this protocol is producing a better plan tree.**

A contest event records the claim. It does not automatically deprecate the prerequisite.
Resolution requires evidence — a plan tree that achieves the claim goals without the
condition. If that plan tree is accepted (supported without `insufficient_risk_coverage`
objection) in a negotiation cycle, it becomes structural evidence for deprecation.

---

## Prerequisite Lineage Tracking

Every promotion event is append-only and carries:
- `evidence_claims` — which claims provided convergence evidence
- `promotion_basis` — always `"independent_plan_tree_diff_convergence"`
- `convergence_count` — how many claims contributed
- Full independence metrics

Contest, reaffirm, and deprecate events chain off the same `condition` field.
The full lineage is always recoverable from `federation.jsonl`.

---

## Prerequisite Propagation

Promoted prerequisites are injected into world model prior knowledge as
**advisory planning hints** via `prerequisite_memory_integration.py`.

```json
{
  "federation_prerequisites": [
    {
      "condition": "space_safety_assessed",
      "hint_type": "federation_prerequisite",
      "authority": "none",
      "evidence_claims": ["housing-001", "housing-002"],
      "advisory": true,
      "note": "Independently discovered by 2 claims via structural plan tree diff."
    }
  ]
}
```

Advisory means: the plan tree builder should consider including this condition.
It does not mean: the plan tree is invalid if it omits the condition.
There is no enforcement. A plan that omits a promoted prerequisite can be submitted,
negotiated, and selected. The prerequisite is a signal, not a gate.

---

## Prerequisite Deprecation

When new plan tree evidence refutes a promoted prerequisite:

1. A participant submits a plan tree that achieves the claim goals without the condition.
2. That plan tree passes negotiation (no `insufficient_risk_coverage` objection).
3. The participant contests the prerequisite, citing the new plan as evidence.
4. If the contestation is accepted (reaffirm fails, new plan stands), a
   `federation_prerequisite_deprecated` event is appended.
5. The deprecated prerequisite remains in `federation.jsonl` forever (append-only).
6. Future plan trees are no longer prompted to include the condition.
7. If new convergence evidence emerges, the prerequisite can be re-promoted.

---

## Storage: sutable/federation.jsonl

All prerequisite events are stored in the federation su-table (append-only):

```
bridge/sutable/federation.jsonl
```

New event types:
- `federation_prerequisite_promoted`
- `federation_prerequisite_contested`
- `federation_prerequisite_reaffirmed`
- `federation_prerequisite_deprecated`

---

## Module Reference

### `runtime/federation_prerequisite_detector.py` — detection (read-only)

```python
detect_prerequisite_candidates(fmap=None, fed_events=None) -> list[dict]
detect_single(condition, fmap=None) -> dict | None
```

### `runtime/prerequisite_evidence_bundle.py` — evidence (read-only)

```python
build_evidence_bundle(condition, fmap=None) -> dict
build_all_evidence_bundles(fmap=None) -> list[dict]
```

### `runtime/prerequisite_promotion.py` — promotion (writes to federation.jsonl)

```python
compute_promotion_candidates(fmap=None, fed_events=None) -> list[dict]
build_promotion_event(condition, evidence_claims, evidence_bundle) -> dict
append_promotion_events(candidates, *, dry_run, verbose) -> list[dict]
promote_prerequisites(*, dry_run, verbose, json_output) -> dict
```

### `runtime/prerequisite_contest_resolver.py` — contest lifecycle

```python
get_prerequisite_events(condition=None, fed_events=None) -> list[dict]
get_prerequisite_status(condition, fed_events=None) -> dict | None
all_prerequisite_statuses(fed_events=None) -> list[dict]
build_contest_event(condition, reason, speaker) -> dict
build_reaffirm_event(condition, reason, speaker) -> dict
build_deprecate_event(condition, reason, speaker) -> dict
append_prerequisite_event(event, *, dry_run, verbose) -> dict
```

### `runtime/prerequisite_snapshot.py` — query (read-only)

```python
snapshot(condition=None, *, include_evidence=False) -> dict | list[dict]
promoted_prerequisites(fed_events=None) -> list[str]
```

### `runtime/prerequisite_memory_integration.py` — world model integration

```python
get_prerequisite_planning_hints(claim_id, fed_events=None) -> list[dict]
integrate_into_prior_knowledge(prior_knowledge, claim_id, fed_events=None) -> dict
build_enriched_prior_knowledge(claim_id, fed_events=None) -> dict
```

---

## CLI Reference

```bash
# Detect candidates
python runtime/federation_prerequisite_detector.py
python runtime/federation_prerequisite_detector.py --verbose
python runtime/federation_prerequisite_detector.py --condition space_safety_assessed

# Build evidence bundle
python runtime/prerequisite_evidence_bundle.py --condition space_safety_assessed
python runtime/prerequisite_evidence_bundle.py --all --json

# Promote
python runtime/prerequisite_promotion.py              # preview
python runtime/prerequisite_promotion.py --dry-run    # explicit preview
python runtime/prerequisite_promotion.py --append     # write to federation.jsonl

# Query snapshot
python runtime/prerequisite_snapshot.py
python runtime/prerequisite_snapshot.py --condition space_safety_assessed --evidence
python runtime/prerequisite_snapshot.py --promoted-only --json

# Contest lifecycle
python runtime/prerequisite_contest_resolver.py
python runtime/prerequisite_contest_resolver.py \
    --contest space_safety_assessed \
    --reason "..." \
    --speaker did:key:zContester

python runtime/prerequisite_contest_resolver.py \
    --reaffirm space_safety_assessed \
    --reason "..." \
    --speaker did:key:zReaffirmer

python runtime/prerequisite_contest_resolver.py \
    --deprecate space_safety_assessed \
    --reason "..." \
    --speaker did:key:zDeprecater

# Memory integration
python runtime/prerequisite_memory_integration.py --claim-id housing-001
python runtime/prerequisite_memory_integration.py --all-claims
python runtime/prerequisite_memory_integration.py --all-claims --json

# Graph export (includes FEDERATION PREREQUISITES section)
python runtime/graph_export.py --claim-id housing-001 --format text
python runtime/graph_export.py --claim-id housing-001 --format mermaid
python runtime/graph_export.py --claim-id housing-001 --format html --output ...
```

---

## Integration Pipeline

```bash
# 1. Check for prerequisite candidates
python runtime/federation_prerequisite_detector.py --verbose

# 2. Inspect evidence bundle
python runtime/prerequisite_evidence_bundle.py --condition space_safety_assessed

# 3. Promote (if evidence is sufficient)
python runtime/prerequisite_promotion.py --append --verbose

# 4. View snapshot
python runtime/prerequisite_snapshot.py --evidence

# 5. View in graph export
python runtime/graph_export.py --claim-id housing-001 --format text

# 6. Check memory integration hints
python runtime/prerequisite_memory_integration.py --all-claims

# 7. (Optional) Contest a prerequisite
python runtime/prerequisite_contest_resolver.py \
    --contest space_safety_assessed \
    --reason "..." \
    --speaker did:key:zContester
```

---

## Design Principles

1. **Authority: none.** Every promoted prerequisite has `authority: "none"`.
   This field is non-overrideable. There is no path in the codebase that sets it
   to anything else.

2. **Contestable: always.** Prerequisites are not permanent. Every promoted
   prerequisite has `contestable: true`. This also cannot be overridden.

3. **Structure only.** Condition detection uses structural plan tree diff.
   No text similarity. No NLP. No fuzzy matching.

4. **Append-only.** All lifecycle events (promoted, contested, reaffirmed, deprecated)
   are new events in `federation.jsonl`. Nothing is deleted or modified.

5. **Transparent.** Every field in a promotion event is traceable to a specific
   plan event in `plans.jsonl`. Anyone can re-run the computation and verify.

6. **Advisory.** Promoted prerequisites are planning hints, never hard gates.
   A plan that omits a promoted prerequisite can still be negotiated and selected.

7. **Deterministic.** Given the same `plans.jsonl` and `memory.jsonl`, the same
   candidates are always detected, the same evidence bundles are always built,
   the same promotion events are always generated.

---

## Related Specs

- [FEDERATION_BRANCHING_SPEC.md](FEDERATION_BRANCHING_SPEC.md) — federation branching and condition propagation
- [REFLECTIVE_MEMORY_SPEC.md](REFLECTIVE_MEMORY_SPEC.md) — reflective memory loop (source of learned_conditions)
- [PLAN_NEGOTIATION_SPEC.md](PLAN_NEGOTIATION_SPEC.md) — plan negotiation (source of plan tree diffs)
- [ogi/PLAN_TREE_SPEC.md](ogi/PLAN_TREE_SPEC.md) — plan tree structure (branch node conditions)
