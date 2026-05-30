# Dan-Go Mujin Protocol

> **Dan-Go Mujin Protocol is not crowdfunding.**
> It is a public negotiation protocol for turning impossible claims into reality.

**gitlawb (decentralized):** [https://gitlawb.com/z6MkpWP3c2xE5Veu5xSJxviWUrM69SDX4offMifsVXAs31Ts/dango-mujin](https://gitlawb.com/z6MkpWP3c2xE5Veu5xSJxviWUrM69SDX4offMifsVXAs31Ts/dango-mujin)

---

## What is a Claim?

A claim is not true or false by default.
**A claim is a proposed state transition.**

The protocol asks:

- What is missing?
- Who can help?
- What resources are needed?
- What contradictions exist?
- What can be executed now?
- What must be escalated?
- What must be rejected?

## Core Loop

```
Claim → Negotiation → Contribution → Execution → Reality Feedback
```

## Ordinary crowdfunding vs Dan-Go Mujin

| Crowdfunding | Dan-Go Mujin |
|---|---|
| Collect money | Submit a Claim |
| Return rewards | Decompose required conditions |
| Platform decides | Negotiation decides |
| Money only | Code, compute, translation, housing, legal review, distribution, social reach, reputation, care |

## Inspiration

Dan-Go Mujin is inspired by the Japanese concept of **無尽 (mujin)**:
a rotating mutual-credit association based on trust, contribution, and shared realization.

**Dan-Go (談合)** is not corruption.
It is **public resonance, agreement formation, and cooperative design**.

This version is for AI agents and humans working together:
not only money, but any form of contribution can become part of the negotiation.

## Key Concepts

| Term | Meaning |
|---|---|
| **Dan-Go** | Public negotiation — not secret collusion |
| **Lie** | An unrealized state transition, not an error to be eliminated |
| **Impossible** | A state where not enough negotiation has happened yet |
| **素テーブル (sutable)** | A fully open state table — no hidden information |
| **YacypherPunks** | A cooperative community beyond national and institutional boundaries |
| **第零国家 (State Zero)** | A second affiliation that sits on top of existing states without destroying them |
| **Constitution** | One clause: Do not violate the dignity of another |

## Participation

- Fork this repo
- Submit a Claim (see `CLAIM_FORMAT.md`)
- Contribute to an open Claim
- Object, counter-claim, or propose alternatives
- All are valid participation

## Quick Start

```bash
# Read a claim and see what is missing
python runtime/claim_matcher.py examples/housing.claim.json

# Route contributions to missing conditions
python runtime/contribution_router.py examples/housing.claim.json

# Check trust score from contribution history
python runtime/trust_score.py

# Record execution feedback
python runtime/reality_feedback.py
```

## Phase 22 — Globe（グローブ）基盤

Dan-Go は、AIエージェントと人間が協働して合意形成を行うためのシステムです。
フェーズ22では、その先にある自由参加型共同体「グローブ」の基盤を追加しました。
グローブは、国家・自治体・DAO・地域共同体・プロジェクトなどを包含できる単位であり、
提案・熟議・ルール・実行履歴をGit的に管理することで、政治家中心ではない
新しい共同体運営の可能性を探ります。

Dan-Go is a system for humans and AI agents to collaboratively build consensus.
In Phase 22, we added the foundation for "Globe" — a free-participation voluntary community.
A Globe can encompass nation-states, municipalities, DAOs, local communities, and projects,
managing proposals, deliberations, rules, and execution history in a Git-like manner,
exploring new possibilities for community governance beyond politician-centric models.

```bash
# Globe 一覧を見る
python3 globe/runtime/globe_registry.py list

# 熟議ログを読む
python3 globe/runtime/deliberation_log.py summary proposal-001

# UIサーバーを起動して /globe ページを開く
python3 globe/runtime/globe_server.py
# → http://localhost:7422/globe
```

## Phase 23 — Proposal → Claim 変換

フェーズ23では、採択（accepted）された Proposal を Dan-Go Claim 形式へ変換する仕組みを追加しました。
変換は強制ではなく、実行の起点となる任意のステップです。

In Phase 23, we added the ability to convert accepted Globe Proposals into Dan-Go Claim format.
Conversion is optional and advisory — it creates no obligation and allocates no resources.

> "Proposal is not execution. Claim is not command. Conversion is not allocation."

```bash
# accepted Proposal を Claim に変換する
python3 globe/runtime/proposal_to_claim.py convert proposal-002

# Globe 内の accepted Proposal を一括変換する
python3 globe/runtime/proposal_to_claim.py convert-globe globe-001

# 変換済み Claim の一覧を見る
python3 globe/runtime/proposal_to_claim.py list
```

変換結果は `globe/claims/` に JSON と Markdown の両形式で保存されます。
UIサーバー（`/globe/<id>/proposals/<proposal_id>`）では Claim 変換状況が確認できます。

---

## Structure

```
dango-mujin/
├── README.md              — This file
├── asset.toml             — GITSEA asset registration (split, royalty, insurance)
├── CONSTITUTION.md        — The one law
├── MUJIN_PROTOCOL.md      — Full protocol specification
├── CLAIM_FORMAT.md        — How to write a Claim
├── CONTRIBUTION_SPEC.md   — What counts as a contribution
├── TRUST_MODEL.md         — How trust is calculated
├── SUTABLE_SPEC.md        — The open state table format
├── ROADMAP.md             — Where this goes next
├── examples/              — Sample claims
├── runtime/               — Minimum viable Python runtime
├── globe/                 — Phase 22–23: Globe foundation + Claim conversion
│   ├── data/              — Globe, Proposal, Deliberation JSON data
│   ├── claims/            — Phase 23: Generated Claim files (JSON + Markdown)
│   ├── runtime/           — CLI tools + HTTP server (stdlib only)
│   └── spec/              — Globe specification
└── bridge/                — Dan-Go bridge layer (GITSEA, OGI, gitlawb)
    └── gitsea/            — GITSEA asset registration bridge (advisory only)
```

## GITSEA Asset

This repository declares itself as a GITSEA asset via `asset.toml`.
GITSEA can make repository contribution economically legible.
Dan-Go makes contribution negotiable before it becomes economic.

No private keys. No wallet operations. No on-chain submissions from Dan-Go tooling.
See `bridge/gitsea/` for the advisory bridge layer.

## Principles

1. Not a finished product. A participable protocol.
2. Dan-Go itself evolves through public negotiation.
3. Forks welcome. Objections welcome. Claims welcome.
4. AI is not a governor. AI is a missionary, mediator, and recorder.
5. Do not present unobserved states as observed.
6. No exaggeration.
7. No private keys, API keys, or seed phrases ever.
8. No investment solicitation. This is a thought and cooperation protocol.
9. Violence, exploitation, and coercion are forbidden means.
10. All negotiation is publicly auditable whenever possible.

---

*Dan-Go Mujin is in protocol-draft state. Everything here is subject to public negotiation.*
