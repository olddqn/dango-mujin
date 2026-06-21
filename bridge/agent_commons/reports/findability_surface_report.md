# Findability Surface Report

- Generated: 2026-06-19T23:20:59.904108Z
- Layer: `bridge/agent_commons/` (advisory only · authority none · AI proposes, human decides)
- F-1.5 observes WHERE Mujin is currently findable (its public surfaces).
- **This is not** an SEO audit, traffic/acquisition analysis, marketing study,
  or any plan to increase reach. It records only what exists.
- Reality Correction: every surface was verified on its observation date; the
  method is recorded per surface. Unconfirmed surfaces are recorded `exists=false`.

## Counts
| metric | value |
|---|---|
| surfaces examined | 12 |
| **surface_count (exists=true)** | 4 |
| **public_surface_count** | 2 |
| **discoverable_surface_count** | 2 |
| learnings | 4 |
| patterns | 3 |
| evidence | 4 |
| voice generated | 0 |
| need generated | 0 |
| cooperation generated | 0 |
| decision generated | 0 |
| outreach detected | 0 |
| growth detected | 0 |
| marketing detected | 0 |
| Violation Count | 0 |

## Surfaces (verified observation, no surface ranked or recommended)
| surface | exists | public | discoverable | needs prior knowledge | verified by |
|---|---|---|---|---|---|
| github_repository | True | True | True | False | github api unauthenticated returned 200; visibility public (olddqn/dango-mujin). Note: the Mujin platform branch is unpushed, so public content is the Dan-Go/globe history. |
| documentation | True | True | True | False | readme.md present on public main (200). docs/ directory absent on main (404) — review docs live on an unpushed local branch. |
| localhost_services | True | False | False | True | mujin platform binds 127.0.0.1:8787 in code; local branch only, not pushed. Reachable only by someone running it locally. |
| nookplot | True | False | False | True | a gitlawb remote is configured to a localhost did node (127.0.0.1:7545); the node was unreachable at observation time, so it is not a public discovery surface. |
| github_pages | False | False | False | False | no gh-pages branch; no CNAME or _config.yml; no Pages site files. |
| public_website | False | False | False | False | no deploy/hosting config (vercel/netlify/procfile/dockerfile) found. |
| telegram | False | False | False | False | no bot in code; the only mention is inside a review document. Reality Correction: no telegram presence exists. |
| discord | False | False | False | False | no discord reference found in the tree. |
| sns | False | False | False | False | no social-network reference found in the tree. |
| search_engine | False | False | False | False | indexing not confirmed; would depend on the public repo being crawled. Cannot confirm, so recorded as absent. |
| public_voice_records | False | False | False | False | voice_records.jsonl returns 404 on public main; present only on an unpushed local branch. No public voice records exist. |
| referral_surfaces | False | False | False | False | no inbound referral links to Mujin found. |

## Honest reading
The repository (`olddqn/dango-mujin`) is public, but the **Mujin platform branch
is not pushed** — so what is publicly findable today is the Dan-Go/globe history
plus the README, not the Contribution Commons platform. The localhost service
and the gitlawb/Nookplot node are local-only. **No public voice records exist**
(absent on the public branch), which is the correct and reassuring state for a
layer that must never expose people. Mujin is, in practice, barely findable —
and that is recorded as an observation, not corrected by reaching anyone.

## Violations
- (none)

---

*Findability Surface Review records what exists, not how to increase it. No
surface is ranked, recommended, or prioritised; there is no acquisition,
outreach, marketing, or growth plan here. Absence is an observation. Reach Gap
is unresolved; this layer does not resolve it — it only states where Mujin can,
and cannot, currently be found.*
