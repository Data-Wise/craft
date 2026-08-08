# Doc-Staleness Prose Gaps — Spec

**Generated:** 2026-08-07
**Context:** Craft Plugin v4.5.0 — extends `scripts/docs-staleness-check.sh` Phase 7
**Sources:** [`BRAINSTORM-doc-staleness-prose-gaps-2026-08-07.md`](BRAINSTORM-doc-staleness-prose-gaps-2026-08-07.md) (6 locked decisions, external research)
**Status:** draft

---

## Problem

`docs-staleness-check.sh`'s count-consistency phase (Phase 7) anchors on specific structured
patterns — badges (`version-X.Y.Z`), declared count lines (`N commands`) — and reported GREEN
today while two real staleness bugs sat live in `docs/REFCARD.md` and `docs/skills-agents.md`:
a version box with the right number but a wrong release date and a stale highlight line
describing the prior release, and a TL;DR line claiming "8 specialized agents" two lines above
its own correct "2 specialized agents". Both are free prose the gate doesn't watch.

## User Story

As a maintainer running `/craft:check --for release` or `docs-staleness-check.sh` directly, I
want the gate to catch the specific prose-staleness shapes that have actually bitten this repo
(stale release dates, stale agent/skill-count mentions, stale version-highlight lines) so a
release doesn't ship with correct version *numbers* sitting next to incorrect surrounding prose.

## Locked Decisions (from BRAINSTORM)

| # | Decision |
|---|---|
| D1 | Extend `docs-staleness-check.sh` directly — no new script, no new dependency. |
| D2 | Scope: craft only, not the dev-tools-wide shared tooling. |
| D3 | Targeted prose-pattern regexes, not general NLP/semantic diffing. |
| D4 | No external tool adoption (Vale/drift/LLM-in-CI) — pattern-first shape borrowed, not the tools themselves. |
| D5 | 3 concrete checks (see below), each with a clean-fixture and planted-defect-fixture regression test. |

## Scope

### New checks (Phase 7 extension)

1. **Release-date claims.** Any doc prose matching `released? \d{4}-\d{2}-\d{2}` (or
   `\(released ...\)`) tied to the *current* version token must match `.STATUS`'s
   `release_date:` field. Flag on mismatch.
2. **Agent/skill count prose.** Free-text `\d+ (specialized )?agents?` / `\d+ skills?` mentions
   must match `plugin.json`'s current counts — **except** in files that are historical logs by
   convention (`VERSION-HISTORY.md`, `CHANGELOG.md` entries under a past version heading,
   `docs/MIGRATION-v4.md`'s "was X before the split" phrasing). Exclusion list lives in
   `scripts/config/exclusions.txt` alongside the existing nav-completeness exclusions.
3. **Version-highlight staleness proxy.** For `docs/index.md`'s `!!! info "Latest: ..."` block
   and `docs/REFCARD.md`'s quick-reference box highlight line: if the version token matches
   current, but the file's last git-log touch predates the current version's `bump-version.sh`
   commit, flag as **possibly stale content, current number** (advisory, not blocking — a
   cheap proxy, not a semantic diff).

### Out of scope

- General semantic/LLM-based staleness detection (D3/D4).
- Porting the pattern to sibling dev-tools repos (D2) — revisit only if this proves out here.
- Any new CI workflow, cron job, or external service.

## Acceptance Criteria

- [ ] Checks 1 and 2 are implemented as blocking (RED) findings in Phase 7.
- [ ] Check 3 is implemented as advisory (YELLOW) — never blocks, per the existing
      YELLOW/RED convention `docs-staleness-check.sh` already uses elsewhere.
- [ ] Regression fixtures restore today's exact bugs (REFCARD.md's stale date/highlight,
      skills-agents.md's "8 specialized agents") and prove the new checks catch them
      (planted-defect positive control, same pattern used for `test_no_live_legacy_check_skill_references`).
- [ ] Running the check against current (already-fixed) `dev` HEAD stays GREEN — no
      false positive on the corrected content.
- [ ] `docs/reference/REFCARD-DOCS-STALENESS.md` documents the 3 new checks in its
      existing check inventory.
- [ ] `CHANGELOG.md` / `docs/CHANGELOG.md` `[Unreleased]` gets a one-line entry.
- [ ] No new script, no new external dependency (D1/D4).

## Test Plan

| Tier | Coverage |
|---|---|
| `unit` | New pattern-matcher functions, tested against clean + planted-defect fixtures for all 3 checks. |
| `dogfood` | `docs-staleness-check.sh` on current `dev` HEAD → GREEN. On a git-stash of the pre-fix REFCARD.md/skills-agents.md → RED (regression proof). |
| `e2e` | `/craft:check --for release` runtime unaffected (checks stay in Phase 7's existing budget). |
| `integration` | N/A — no cross-command data flow. |
| `dependency` | N/A — no new dependency. |

## Next Step

`/craft:plan docs/specs/SPEC-doc-staleness-prose-gaps-2026-08-07.md` → routes to
`plan-orchestrator` for implementation (small scope, grill optional — low ambiguity, decisions
already locked in the BRAINSTORM).
