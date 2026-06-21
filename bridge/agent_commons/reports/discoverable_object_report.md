# Discoverable Object Report

- Generated: 2026-06-19T23:43:55.306668Z
- Layer: `bridge/agent_commons/` (advisory only · authority none · AI proposes, human decides)
- F-1.7 observes the **Surface → Object** mapping: given the surfaces that exist
  (F-1.5), what can an external actor actually discover.
- **This is not** branding, marketing, SEO, or growth analysis. It records only
  what is visible. Reality Correction: each mapping was verified; unconfirmed
  objects are recorded `discoverable=false` (a visibility gap).

## Counts
| metric | value |
|---|---|
| **object_count** | 14 |
| **public_object_count** | 6 |
| **discoverable_object_count** | 6 |
| learnings | 3 |
| patterns | 2 |
| evidence | 14 |
| voice generated | 0 |
| need generated | 0 |
| gateway generated | 0 |
| cooperation generated | 0 |
| decision generated | 0 |
| Violation Count | 0 |

- Discoverable object types: dan_go, documentation, globe, repository, source_code
- Not-discoverable (gap) object types: agent_commons, contribution_commons, mujin, repository, voice_commons

## Surface → Object (verified observation; no object ranked or recommended)
| surface | object | discoverable | public | needs prior knowledge | verified by |
|---|---|---|---|---|---|
| github_repository | dan_go | True | True | False | globe/, bridge/gitsea, bridge/sutable and top-level specs present on public main (200). |
| github_repository | globe | True | True | False | globe/ present on public main (200). |
| github_repository | repository | True | True | False | repo root listing is public (bridge/, runtime/, examples/, manifesto/). |
| github_repository | source_code | True | True | False | runtime/ and bridge/ source present on public main (200). |
| github_repository | documentation | True | True | False | README, CONSTITUTION, MUJIN_PROTOCOL, CONTRIBUTION_SPEC, ROADMAP public on main (200). |
| github_repository | agent_commons | False | False | False | bridge/agent_commons returns 404 on public main; present only on an unpushed branch. |
| github_repository | mujin | False | False | False | bridge/mujin platform returns 404 on main. Only MUJIN_PROTOCOL.md (a document) is public; the platform itself is not discoverable. |
| github_repository | contribution_commons | False | False | False | part of bridge/mujin (404 on main); not publicly discoverable. |
| github_repository | voice_commons | False | False | False | part of bridge/mujin (404 on main); no public voices — the correct, reassuring state. |
| documentation | documentation | True | True | False | README and spec .md files (CONSTITUTION, MUJIN_PROTOCOL, CONTRIBUTION_SPEC, ROADMAP) public on main (200). |
| localhost_services | mujin | False | False | True | the mujin platform serves only at 127.0.0.1:8787; not externally discoverable. |
| localhost_services | contribution_commons | False | False | True | served only by the local service; not externally discoverable. |
| localhost_services | voice_commons | False | False | True | served only by the local service; not externally discoverable. |
| nookplot | repository | False | False | True | the gitlawb node at 127.0.0.1:7545 was unreachable; nothing externally discoverable. |

## Honest reading
What is actually discoverable today is **Dan-Go**: `globe/`, `bridge/gitsea`,
`bridge/sutable`, the source tree, and the top-level specs/README. The **Mujin
platform, `contribution_commons`, `voice_commons`, and `agent_commons` are NOT
publicly discoverable** — they live on an unpushed branch or a local service
(404 on public main). The `MUJIN_PROTOCOL.md` document is public, but the
working platform is not. Notably, **no voices are publicly discoverable**, which
is the correct, reassuring state for a layer that must never expose people. The
visibility gap is recorded as an observation; nothing here proposes closing it.

## Violations
- (none)

---

*Discoverable Object Review records what is visible, not what should be shown.
No object is ranked, recommended, or targeted; there is no marketing, growth,
acquisition, or recruitment here. A visibility gap is an observation. Reach Gap
is unresolved; this layer does not resolve it — it only states what an outside
actor can, and cannot, currently discover.*
