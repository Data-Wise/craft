# Doc-Staleness Prose Gaps — Spec

**Generated:** 2026-08-07
**Context:** Craft Plugin v4.5.0 — extends `scripts/docs-staleness-check.sh` Phase 7
**Sources:** [`BRAINSTORM-doc-staleness-prose-gaps-2026-08-07.md`](BRAINSTORM-doc-staleness-prose-gaps-2026-08-07.md) (6 locked decisions, external research)
**Status:** draft — revised post adversarial review (see "Review Outcome" below)

---

## Review Outcome (adversarial review, 2026-08-07)

Original draft (checks 1–3 as first written) was adversarially reviewed before build. 3
blocking findings, all fixed in this revision — see inline `> **Review:**` notes below for
what changed and why:

1. **Check 3's proxy was falsified by the exact incident it targets.** `bump-version.sh`
   touches `docs/REFCARD.md`'s version line in every release commit — so REFCARD.md's
   "last git-log touch" always coincides with the bump commit, meaning the whole-file proxy
   would report "not stale" on the file that caused this SPEC to exist. **Fix: dropped
   check 3 entirely** — a per-line/per-span version would work but adds real complexity for
   an advisory-only signal; not worth building until a simpler check proves insufficient
   (gentle-ramp, not preemptive).
2. **Check 3's stated target (`docs/index.md`) was already whole-file excluded** from Phase 7
   via `exclusions.txt`'s "curated hub page" entry — moot once check 3 is dropped.
3. **Check 2's false-positive surface was far larger than the 3-file exclusion list.** A grep
   of `docs/**/*.md` found 90+ hits for count-shaped prose outside the proposed exclusions,
   including legitimate non-count-of-agents phrases (`docs/guide/orch-flag-usage.md`: "2
   agents max", "4 agents" in orchestration mode-limit prose), a tutorial with an
   intentionally fictional example plugin, and a troubleshooting page that intentionally
   shows a wrong count to illustrate the exact bug it's teaching. **Fix: check 2 rescoped
   to structured line shapes only** (TL;DR lines, quick-reference/version boxes, badge
   lines) — not a blanket `\d+ agents?` search anywhere in prose. See revised check 2 below.
4. **`exclusions.txt` maintainability concern raised, accepted as a known tradeoff** — not
   blocking. It's already craft's established mechanism for this class of exception (used by
   nav-completeness today); rescoping check 2 to structured lines (finding 3's fix) also
   shrinks how much the exclusion list needs to grow.
5. **Scope (craft-only) and acceptance criteria confirmed fine as-is** — no changes.

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
   `release_date:` field. Flag on mismatch. Blocking (RED).

2. **Agent/skill count prose — structured lines only.**
   > **Review:** rescoped from a blanket `\d+ agents?`/`\d+ skills?` search (which false-positived
   > on orchestration mode-limit prose, a fictional-plugin tutorial, and an intentional-bug
   > troubleshooting example) to specific known-good line shapes only:
   - Lines matching a "TL;DR"-prefixed sentence (e.g. `docs/skills-agents.md`'s pattern).
   - Lines inside a fenced quick-reference/version box (`┌─...─┐` ... `└─...─┘` block, e.g.
     `docs/REFCARD.md`'s header box).
   - Lines matching an explicit badge/count-summary pattern already used elsewhere
     (`**N commands** · **N skills** · **N agents**`, as in `docs/QUICK-START.md`/`docs/index.md`).

   Within those line shapes only, `\d+ (specialized )?agents?` / `\d+ skills?` mentions must
   match `plugin.json`'s current counts. Historical-log files (`VERSION-HISTORY.md`,
   `CHANGELOG.md` past-version sections, `docs/MIGRATION-v4.md`) stay excluded via
   `scripts/config/exclusions.txt`, same mechanism as today's nav-completeness exclusions —
   a smaller list now that the check is line-shape-scoped, not file-wide. Blocking (RED).

3. ~~Version-highlight staleness proxy~~ — **dropped.**
   > **Review:** the proposed whole-file git-log-touch proxy is falsified by
   > `bump-version.sh` itself, which touches `docs/REFCARD.md`'s version line on every
   > release — the exact file this check was meant to catch would always read "recently
   > touched, not stale." A correct version requires per-line/per-span touch tracking,
   > which is real complexity for an advisory-only signal. Not building until checks 1–2
   > prove insufficient on their own (gentle-ramp).

### Out of scope

- General semantic/LLM-based staleness detection (D3/D4).
- Porting the pattern to sibling dev-tools repos (D2) — revisit only if this proves out here.
- Any new CI workflow, cron job, or external service.

### Follow-up (found 2026-08-07, not in this SPEC's scope)

`homebrew-tap`'s `generator/manifest.json` has the same prose-staleness blind spot, in a
different repo: `command_count` is auto-synced by `homebrew-release.yml` on every version
release, but each formula's `caveats_extra` fixed prose (command names, feature bullets) is
hand-authored and never re-verified — confirmed live when craft's own caveats text still
referenced the removed `/craft:git:unprotect` command (fixed in `homebrew-tap#211`). Neither
`check-drift.sh` (formula-matches-manifest) nor `check-revision-bump.sh` (content-changed-needs-
revision) checks prose *accuracy*, only structural consistency. This SPEC's checks 1–2 don't
reach `homebrew-tap` (out of scope per D2 — craft only). If this pattern proves out here,
consider a parallel prose-accuracy check in `homebrew-tap` itself (different repo, different
owner of that decision) — not assumed, not scheduled.

## Acceptance Criteria

- [ ] Checks 1 and 2 are implemented as blocking (RED) findings in Phase 7.
- [ ] Check 2's line-shape scoping is itself tested against the 3 false-positive sources the
      review found (`docs/guide/orch-flag-usage.md`, the fictional-plugin tutorial, the
      intentional-bug troubleshooting page) — must NOT flag any of them.
- [ ] Regression fixtures restore today's exact bugs (REFCARD.md's stale date,
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
| `unit` | New pattern-matcher functions, tested against clean + planted-defect fixtures for both checks, plus the 3 false-positive-source fixtures the review found for check 2. |
| `dogfood` | `docs-staleness-check.sh` on current `dev` HEAD → GREEN. On a git-stash of the pre-fix REFCARD.md/skills-agents.md → RED (regression proof). |
| `e2e` | `/craft:check --for release` runtime unaffected (checks stay in Phase 7's existing budget). |
| `integration` | N/A — no cross-command data flow. |
| `dependency` | N/A — no new dependency. |

## Next Step

`/craft:plan docs/specs/SPEC-doc-staleness-prose-gaps-2026-08-07.md` → routes to
`plan-orchestrator` for implementation (small scope, grill optional — low ambiguity, decisions
already locked in the BRAINSTORM).
