# Report: Doc-Staleness Prose Gaps

**Source:** [`SPEC-doc-staleness-prose-gaps-2026-08-07.md`](../specs/SPEC-doc-staleness-prose-gaps-2026-08-07.md)
**Status:** draft — revised post adversarial review

## tl;dr

| Metric | Value |
|---|---|
| Checks proposed | 3 |
| Checks kept after review | 2 |
| Blocking review findings | 3 |
| New dependencies | 0 |
| New scripts | 0 |
| Acceptance criteria | 7 |
| Test tiers covered | 5 |

## Problem

`docs-staleness-check.sh`'s count-consistency phase (Phase 7) anchors on specific structured
patterns — badges (`version-X.Y.Z`), declared count lines (`N commands`) — and reported GREEN
while two real staleness bugs sat live in `docs/REFCARD.md` and `docs/skills-agents.md`: a
version box with the right number but a wrong release date and a stale highlight line
describing the prior release, and a TL;DR line claiming "8 specialized agents" two lines above
its own correct "2 specialized agents." Both are free prose the gate doesn't watch.

## Locked Decisions

| # | Decision |
|---|---|
| D1 | Extend `docs-staleness-check.sh` directly — no new script, no new dependency. |
| D2 | Scope: craft only, not the dev-tools-wide shared tooling. |
| D3 | Targeted prose-pattern regexes, not general NLP/semantic diffing. |
| D4 | No external tool adoption (Vale/drift/LLM-in-CI) — pattern-first shape borrowed, not the tools themselves. |
| D5 | Concrete checks, each with a clean-fixture and planted-defect-fixture regression test. |

## What's Being Built (post-review)

1. **Release-date claims** — prose matching `released? YYYY-MM-DD` tied to the current version
   must match `.STATUS`'s `release_date:` field. Blocking (RED).
2. **Agent/skill count prose, structured lines only** — TL;DR lines, quick-reference/version
   boxes, and badge/count-summary lines must match `plugin.json`'s current counts. Historical-log
   files stay excluded via `scripts/config/exclusions.txt`. Blocking (RED).

## Review Outcome — Adversarial Review Findings

| Finding | Problem | Fix |
|---|---|---|
| Check 3's proxy falsified by its own target | `bump-version.sh` touches `docs/REFCARD.md`'s version line on every release, so a whole-file "last git-log touch" proxy would always read "not stale" on the exact file that caused this SPEC to exist | Dropped check 3 entirely — a per-line proxy would work but isn't worth the complexity for an advisory-only signal until checks 1–2 prove insufficient |
| Check 3's target already excluded | `docs/index.md` was already whole-file excluded from Phase 7 via `exclusions.txt`'s "curated hub page" entry | Moot once check 3 dropped |
| Check 2's false-positive surface far larger than proposed exclusions | A grep of `docs/**/*.md` found 90+ hits outside the 3-file exclusion list, including orchestration mode-limit prose, a fictional-plugin tutorial, and a troubleshooting page that intentionally shows a wrong count | Rescoped from blanket `\d+ agents?` search to structured line shapes only (TL;DR / version box / badge lines) |

## Acceptance Criteria

- [ ] Checks 1 and 2 implemented as blocking (RED) findings in Phase 7.
- [ ] Check 2's line-shape scoping tested against the 3 false-positive sources the review found — must NOT flag any of them.
- [ ] Regression fixtures restore today's exact bugs (REFCARD.md's stale date, skills-agents.md's "8 specialized agents") and prove the new checks catch them.
- [ ] Current (already-fixed) `dev` HEAD stays GREEN — no false positive on corrected content.
- [ ] `docs/reference/REFCARD-DOCS-STALENESS.md` documents the 2 new checks.
- [ ] `CHANGELOG.md` / `docs/CHANGELOG.md` `[Unreleased]` gets a one-line entry.
- [ ] No new script, no new external dependency.

## Test Plan

| Tier | Coverage |
|---|---|
| `unit` | New pattern-matcher functions, tested against clean + planted-defect fixtures for both checks, plus the 3 false-positive-source fixtures the review found for check 2. |
| `dogfood` | `docs-staleness-check.sh` on current `dev` HEAD → GREEN. On a git-stash of the pre-fix REFCARD.md/skills-agents.md → RED (regression proof). |
| `e2e` | `/craft:check --for release` runtime unaffected. |
| `integration` | N/A — no cross-command data flow. |
| `dependency` | N/A — no new dependency. |

## Next Steps

1. `/craft:plan docs/specs/SPEC-doc-staleness-prose-gaps-2026-08-07.md` — routes to `plan-orchestrator` for implementation. Grill optional (low ambiguity, decisions already locked).
