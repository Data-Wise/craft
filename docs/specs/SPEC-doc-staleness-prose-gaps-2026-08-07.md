# Doc-Staleness Prose Gaps — Spec

**Generated:** 2026-08-07
**Context:** Craft Plugin v4.5.0 — extends `scripts/docs-staleness-check.sh` Phase 7
**Sources:** [`BRAINSTORM-doc-staleness-prose-gaps-2026-08-07.md`](BRAINSTORM-doc-staleness-prose-gaps-2026-08-07.md) (6 locked decisions, external research)
**Status:** draft — revised post adversarial review (see "Review Outcome" below); amended
2026-08-15 with an ADR requirement, a test-harness design, and two new pieces of live evidence
(see "Amendment" below)

---

## Amendment (2026-08-15)

Two real staleness bugs surfaced during a `/savant:restore` currency read on `dev` at
`7db7b565c`. Both sharpen this SPEC's design rather than changing its scope.

### E1 — Phase 7's existing regex misses the singular noun form

`CLAUDE.md`'s Project Structure table row for the `agents/` directory read
**8 agent definitions** while the real count had been 2 since v4.0.0. Phase 7 reported **GREEN** over it for five minors. Cause:
the scan pattern is `\b[0-9]+ ${ctype}\b` where `ctype ∈ {commands, skills, agents}` — strictly
plural (`scripts/docs-staleness-check.sh:345`). `8 agent definitions` never matched. The 40%
minimum threshold (line 302) was not the cause; 8 clears it.

This is not a check-2 line-shape case — it is a **pre-existing gap in the check-2 predecessor**.
Fold the singular alternation into the shared matcher rather than shipping check 2 on top of a
pattern that still can't see half the noun forms.

### E2 — "release date" has two defensible authorities

`docs/NEWS.md` claims `**Released:** 2026-08-08` for v4.5.0; `.STATUS` has
`release_date: 2026-08-07`. Neither is wrong — the GitHub release published at
`2026-08-08T03:44:25Z`, which is 2026-08-07 21:44 local. Check 1 as written ("must match
`.STATUS`'s `release_date:`") would flag this as RED on its first run against a correct repo.

Check 1 must therefore pick **one** authority and normalize: compare against the annotated git
tag's local date (`git for-each-ref --format='%(creatordate:short)' refs/tags/vX.Y.Z`), and
accept a ±1-day window against `.STATUS`'s `release_date:` to absorb the UTC boundary. A
same-day-either-side match is not staleness.

### Severity divergence to resolve at build time

Existing Phase 7 findings are emitted at severity `warning` (`add_finding 7 "warning" ...`,
line 341) while this SPEC specifies checks 1–2 as blocking RED. Whichever way this lands, it is
an intentional choice and belongs in the ADR below, not in a silent code default.

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

## ADR — ADR-007: pattern-scoped prose gating in the existing staleness script

This SPEC commits craft to a position it has not written down anywhere: that documentation
*prose* is gated by narrow, hand-authored line-shape patterns inside
`scripts/docs-staleness-check.sh`, and explicitly **not** by a prose linter (Vale), a semantic
differ, or an LLM-in-CI pass. That choice constrains every future staleness check, so it gets a
record rather than living implicitly across D1/D3/D4 in a BRAINSTORM.

**File:** `docs/adr/ADR-007-pattern-scoped-prose-staleness-gating.md`, following the existing
ADR-001…ADR-006 format in that directory.

Content it must record:

| Element | Substance |
|---|---|
| **Context** | Phase 7 anchors on structured patterns and reported GREEN over four real bugs: REFCARD.md's stale release date, skills-agents.md's "8 specialized agents", CLAUDE.md's "8 agent definitions" (E1), README.md's v2.36.0 highlight block five minors after v4.5.0. |
| **Decision** | Extend Phase 7 in place with line-shape-scoped regexes. No new script (D1), no external prose tool (D4), no semantic layer (D3). Craft-only (D2). |
| **Consequences — accepted** | Coverage is exactly as good as the enumerated line shapes; every genuinely new prose shape needs a code change, not a config change. `scripts/config/exclusions.txt` grows over time (accepted tradeoff, review finding 4). |
| **Consequences — rejected alternatives** | Vale/`drift`/LLM-in-CI (D4) — rejected for dependency weight and non-determinism in a release gate. Whole-file git-log-touch proxy — rejected as *falsified*, not merely unattractive: `bump-version.sh` touches REFCARD.md every release, so the proxy reads "fresh" on the file that motivated this work. |
| **Severity posture** | Records whether checks 1–2 emit `error` (blocking) or `warning`, and why — the divergence flagged in the Amendment above. |
| **Revisit trigger** | A prose staleness bug that lands despite checks 1–2, whose shape cannot be expressed as a line-shape regex. That, and only that, reopens the D3/D4 rejection. |

## Test Harness

The Test Plan below names tiers; this section specifies the rig they run on. Both checks need
the same three-way verdict pattern (clean → GREEN, planted defect → RED, known false-positive
source → GREEN), and the adversarial review's three false-positive sources are currently prose
in an acceptance criterion rather than executable rows. A table-driven harness makes them
first-class.

### Layout

```text
tests/fixtures/prose-staleness/
  clean/
    refcard-version-box.md          # correct date + counts inside a ┌─┐ box
    skills-agents-tldr.md           # correct "2 specialized agents" TL;DR line
    claude-md-structure-table.md    # correct "2 agent definitions" (E1 regression)
  defect/
    refcard-stale-date.md           # check 1 — date ≠ tag date
    tldr-eight-agents.md            # check 2 — "8 specialized agents" in a TL;DR line
    structure-table-singular.md     # check 2 — "8 agent definitions", singular form (E1)
  falsepos/
    orch-flag-usage.md              # "2 agents max" / "4 agents" mode-limit prose
    fictional-plugin-tutorial.md    # intentionally fictional example counts
    troubleshooting-wrong-count.md  # deliberately-wrong count teaching the bug
```

### Contract

Each fixture is a **complete minimal markdown file**, not a snippet — the checks operate on
line context (fenced-box membership, TL;DR prefix), so a snippet would not exercise the same
code path. Every fixture carries a one-line HTML comment header stating what it proves, so a
later reader does not have to infer intent from filename alone.

The runner (`tests/test_docs_staleness_prose.py`, alongside the existing
`tests/test_docs_staleness.py`) is a single parametrized case over a declared table:

| Fixture | Check | Expected | Proves |
|---|---|---|---|
| `clean/refcard-version-box.md` | 1 | GREEN | no false positive on correct content |
| `defect/refcard-stale-date.md` | 1 | RED | planted-defect positive control |
| `clean/claude-md-structure-table.md` | 2 | GREEN | E1 stays fixed |
| `defect/structure-table-singular.md` | 2 | RED | E1 would be caught, not missed |
| `defect/tldr-eight-agents.md` | 2 | RED | the original review bug |
| `falsepos/*.md` (×3) | 2 | GREEN | review finding 3's sources stay unflagged |

Invoked via `--json` against a fixture directory so the assertion reads the structured
`findings[]` array rather than parsing colored terminal output — the same reason
`docs-staleness-check.sh` already ships `--json`.

### Harness requirements

- **The harness must be able to fail.** Adding a check without its `defect/` row is a rejected
  change; the positive control is the point (see `e2e-before-pr.md`).
- **No network, no git-history walk, no TTY.** Fixtures are self-contained files; the one git
  read check 1 needs (tag date) is injected as a parameter, not shelled out to, so the suite is
  hermetic and runs identically in CI.
- **Reuse, don't fork.** `scripts/config/exclusions.txt` handling, `is_file_excluded`, and
  `is_pattern_excluded` are called as-is — the harness tests the real code path, not a copy.

## Acceptance Criteria

- [ ] Checks 1 and 2 are implemented as blocking (RED) findings in Phase 7, or the divergence
      from Phase 7's existing `warning` severity is recorded as a deliberate choice in ADR-007.
- [ ] The shared count matcher handles the **singular** noun form (`N agent definitions`), not
      only the plural (E1) — with `clean/` + `defect/` fixtures proving both directions.
- [ ] Check 1 resolves the release-date authority per E2 (git tag local date, ±1-day window
      against `.STATUS`) and does **not** flag the current `docs/NEWS.md` v4.5.0 entry.
- [ ] `docs/adr/ADR-007-pattern-scoped-prose-staleness-gating.md` exists and records every row
      of the ADR table above, including the rejected alternatives and the revisit trigger.
- [ ] The test harness exists at `tests/fixtures/prose-staleness/` with all 9 fixtures and a
      table-driven runner asserting against `--json` output.
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
