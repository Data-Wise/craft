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

**Resolution (revised during build).** The first reading of this finding was "fold the singular
alternation into the shared matcher" — i.e. widen the broad scan at line 345. That reopens
exactly the false-positive surface review finding 3 closed, and adds singular forms of it
("the 4 agent limit") on top.

The singular form is therefore checked **only inside check 2's line shapes**, and the broad scan
is left plural-only. `CLAUDE.md`'s Project Structure row is itself a structured shape — a table
row whose first cell names a counted directory — so E1 is caught by adding a **fourth line
shape** (`structure-table`), not by widening anything. That row's count is compared only against
the type its own first cell names, so a `commands/` row is never measured against the agent count.

### E2 — "release date" has two defensible authorities

`docs/NEWS.md` claims `**Released:** 2026-08-08` for v4.5.0; `.STATUS` has
`release_date: 2026-08-07`. Neither is wrong — the GitHub release published at
`2026-08-08T03:44:25Z`, which is 2026-08-07 21:44 local. Check 1 as written ("must match
`.STATUS`'s `release_date:`") would flag this as RED on its first run against a correct repo.

Check 1 must therefore pick **one** authority and normalize: compare against the annotated git
tag's local date (`git for-each-ref --format='%(creatordate:short)' refs/tags/vX.Y.Z`), and
accept a ±1-day window against `.STATUS`'s `release_date:` to absorb the UTC boundary. A
same-day-either-side match is not staleness.

### Severity — resolved: `warning`

Existing Phase 7 findings are emitted at severity `warning` (`add_finding 7 "warning" ...`,
line 341) while this SPEC's first draft specified checks 1–2 as blocking RED.

**Resolved to `warning`**, per ADR-007. `main()` exits 1 for warnings and errors alike, so both
already fail `/craft:check --for release` and `pre-release-check.sh` — the divergence is the
RED/YELLOW label, not whether the gate blocks. These are the first checks in this repo to judge
prose rather than structured tokens, and the first build of check 2 produced five false
positives before the 40% floor was added; ADR-003's gentle-ramp precedent applies. `error` is
earned after the checks run clean across a few real releases.

### Post-build findings (2026-08-15) — four bugs, four different catchers

Every one of these was in the first build and none was caught by the gate that "should" have.
Recorded because the pattern is the point: no single review mechanism found more than one.

| # | Bug | Caught by | Fix |
|---|---|---|---|
| B1 | Script ran at 36s against a dev baseline of 8.0s — ~1300 per-file `awk` spawns plus ~21000 `grep` calls over every line of every box block | the **existing suite** — a 30s timeout in `test_pre_release_check_runs` | one `awk` pass over the file list, an in-awk `hascount()` pre-filter, date window computed once. 8.7s |
| B2 | An unparseable authority date left an empty accept-window, and an empty window matches nothing — so **every** release-date claim in the repo was flagged at once | **self-review** of the PR | the check is vacuous unless the authority parsed, same posture as the no-tag case |
| B3 | `win = 4` scanned the version line plus only **3** more, because `win--` runs on the version line itself — one short of the 4 following lines this SPEC and the REFCARD both advertise | **`/code-review`** | `win = 5`; defect fixture placed at exactly the far edge |
| B4 | `pass2_interactive_review`'s `[f]ix` printed `-> Fixed` and incremented `TOTAL_FIXED` without touching the file | **reading adjacent code** while tracing where findings are routed | pass 1's applier extracted to `apply_line_fix`, shared by both passes |

Two of these are the same failure mode wearing different clothes — **a check that reports a
result it did not actually establish**. B2 flags without evidence; B4 claims a fix it never made.
B4 is also a *recurrence*: pass 1 had this exact bug (BSD `sed -i` exiting 0 on no match) and was
fixed for it; the sibling pass was left behind. Sharing one applier is what closes the class, not
patching the second site.

### Fix routing, decided here

Both prose checks emit `uncertain`, so they land in pass 2's interactive review rather than pass
1's auto-apply. The surrounding prose is hand-authored — a human should see the line before the
number changes under it. But the `fix_detail` is a real `s/…/…/` substitution, not a
human-readable note, so confirming one actually edits the file; it swaps the digits only, leaving
`agent definitions` intact. Phase 8's doc-coverage findings carry a `doc-coverage:surface:cmd`
marker instead, and `apply_line_fix` refuses to execute anything that is not a substitution.

### Build-time finding: the floor applies to shaped lines too

The first build of check 2 ran without the broad scan's 40%-of-expected floor, on the assumption
that structured shapes are self-limiting. They are not. Five legitimate counts were flagged on
`dev` immediately: category subtotals inside reference boxes (`SMART (4 commands)`,
`Code (12 commands)`), a bolded subset count (`` `--refine` is declared on **9 commands** ``), and
a narrative count about a different plugin (`kept shipping **0 skills**`). Shape membership
narrows *where* to look; the floor is still what separates a total from a subtotal. All five are
now `falsepos/` fixtures.

### Superseded by the prose-check hardening (2026-08-15)

This SPEC's check-1 description above (E2, and the "git tag local date" line in the Acceptance
Criteria) describes the **as-shipped-then** design, not the current one. A follow-up review found
9 more defects in the shipped checks (2 HIGH); see
[`SPEC-prose-check-hardening-2026-08-15.md`](SPEC-prose-check-hardening-2026-08-15.md) and its
[`GRILL`](GRILL-prose-check-hardening-2026-08-15.md). The load-bearing change: check 1 no longer
resolves an authority from the git tag at all (D1) — the tag doesn't exist at either point the
check actually runs, so a tag-based check never fired as a real gate. It now compares every
release-date claim for the current version against every other one, with the one-day window
surviving as the agreement tolerance between claims rather than a tolerance against a tag. Left
here rather than rewritten in place, per this repo's own "positive controls are rewritten, not
deleted, when their model goes obsolete" convention (that hardening's D8) — the checkboxes above
are a historical record of what E2 decided at the time, not a live spec.

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
    version-box-correct.md          # correct date + counts inside a ┌─┐ box
    tldr-correct.md                 # correct "2 specialized agents" TL;DR line
    structure-table-correct.md      # correct "2 agent definitions" (E1 regression)
    release-date-utc-boundary.md    # date 1 day off the tag — the UTC case (E2)
  defect/
    version-box-stale-date.md       # check 1 — date well off the tag
    release-date-far-edge.md        # check 1 — stale date at the window's last line (B3)
    tldr-eight-agents.md            # check 2 — "8 specialized agents" in a TL;DR line
    structure-table-singular.md     # check 2 — "8 agent definitions", singular form (E1)
  falsepos/
    category-subtotal-box.md        # "(4 commands)" subtotals inside a reference box
    subset-bold-count.md            # "**9 commands**" subset + "**0 skills**" narrative
    mode-limit-prose.md             # "2 agents max" / "4 agents" mode-limit prose
```

> **Revised during build.** The review's other two named false-positive sources (the
> fictional-plugin tutorial and the intentional-wrong-count troubleshooting page) are covered by
> path-keyed entries in `exclusions.txt`, so a fixture of them would re-prove the exclusion
> loader rather than this SPEC's new code. They were replaced by the three sources the first
> build of check 2 actually flagged, each isolating a distinct guard: the 40% floor
> (`category-subtotal-box`, `subset-bold-count`) and shape scoping plus exclusion inheritance
> (`mode-limit-prose`, written to its real path so the path-keyed exclusion applies). Ten
> fixtures, not nine.

### Contract

Each fixture is a **complete minimal markdown file**, not a snippet — the checks operate on
line context (fenced-box membership, TL;DR prefix), so a snippet would not exercise the same
code path. Every fixture carries a one-line HTML comment header stating what it proves, so a
later reader does not have to infer intent from filename alone.

The runner (`tests/test_docs_staleness_prose.py`, alongside the existing
`tests/test_docs_staleness.py`) is a single parametrized case over a declared table:

| Fixture | Check | Expected | Proves |
|---|---|---|---|
| `clean/version-box-correct.md` | 1 | GREEN | no false positive on correct content |
| `clean/release-date-utc-boundary.md` | 1 | GREEN | E2: a one-day gap is the UTC boundary |
| `defect/version-box-stale-date.md` | 1 | RED | planted-defect positive control |
| `defect/release-date-far-edge.md` | 1 | RED | B3: the window reaches its documented last line |
| `clean/tldr-correct.md` | 2 | GREEN | correct counts in a TL;DR line |
| `clean/structure-table-correct.md` | 2 | GREEN | E1 stays fixed |
| `defect/tldr-eight-agents.md` | 2 | RED | the original review bug |
| `defect/structure-table-singular.md` | 2 | RED | E1 would be caught, not missed |
| `falsepos/category-subtotal-box.md` | 2 | GREEN | subtotals in a box are not the total |
| `falsepos/subset-bold-count.md` | 2 | GREEN | a bolded count can be a subset |
| `falsepos/mode-limit-prose.md` | 2 | GREEN | free prose is out of shape scope |

Each case is run against a throwaway repo holding exactly one fixture document, invoked with
`--json` so the assertion reads the structured `findings[]` array rather than parsing colored
terminal output — the same reason `docs-staleness-check.sh` already ships `--json`. The
destination path inside that repo is declared per case, because the exclusion that protects
`mode-limit-prose` is path-keyed.

Two harness-level tests sit alongside the table: one asserting every check still owns a
`defect/` fixture (so a future check cannot ship happy-path-only), and one running the real
`dev` tree and asserting `count_consistency` has zero findings — the assertion that caught the
missing 40% floor.

### Harness requirements

- **The harness must be able to fail.** Adding a check without its `defect/` row is a rejected
  change; the positive control is the point (see `e2e-before-pr.md`).
- **No network, no git-history walk, no TTY.** Fixtures are self-contained files; the one git
  read check 1 needs (tag date) is injected via `CRAFT_RELEASE_DATE`, and the expected counts
  via `CRAFT_EXPECTED_{CMDS,SKILLS,AGENTS}`, so the suite is hermetic and no fixture has to
  materialize 48 command files. Both overrides are unset on every production path.
- **Fixture authority values are pinned, not derived.** The harness hardcodes 48/41/2 and the
  v4.5.0 tag date rather than reading the live repo, so a future count change cannot silently
  turn a planted defect into a non-defect (an "8 agents" defect stops proving anything the day
  craft ships 8 agents).
- **Reuse, don't fork.** `scripts/config/exclusions.txt` handling, `is_file_excluded`, and
  `is_pattern_excluded` are called as-is — the harness tests the real code path, not a copy.

## Acceptance Criteria

- [x] Checks 1 and 2 are implemented in Phase 7 at severity `warning`, with the divergence from
      the draft's "blocking RED" recorded as a deliberate choice in ADR-007's Severity section.
- [x] The **singular** noun form (`N agent definitions`) is checked (E1) — inside check 2's line
      shapes only, not by widening the broad scan; `clean/structure-table-correct.md` +
      `defect/structure-table-singular.md` prove both directions.
- [x] Check 1 resolves the release-date authority per E2 (git tag local date, one-day window)
      and does **not** flag the current `docs/NEWS.md` v4.5.0 entry — `clean/release-date-utc-boundary.md`
      pins it.
- [x] `docs/adr/ADR-007-pattern-scoped-prose-staleness-gating.md` exists and records every row
      of the ADR table above, including the rejected alternatives and the revisit trigger.
- [x] The test harness exists at `tests/fixtures/prose-staleness/` (11 fixtures — see the
      revision note in Test Harness) with a table-driven runner asserting against `--json`.
- [x] A broken release-date authority makes the check **vacuous, never universal** (B2), pinned by
      `test_unparseable_authority_date_is_vacuous_not_universal`.
- [x] The release-date window reaches the last line it documents (B3), pinned by
      `defect/release-date-far-edge.md` at exactly that boundary.
- [x] A reported fix actually edits the file (B4) — `apply_line_fix` is shared by both passes and
      pinned by two tests, including that a `false` result leaves the file byte-identical.
- [x] Runtime stays within the existing `test_pre_release_check_runs` budget (B1): 8.7s against a
      dev baseline of 8.0s, versus 36s before the fix.
- [x] Check 2's line-shape scoping is tested against real false-positive sources — revised from
      the review's 3 named files to the 3 the first build actually flagged, since two of the
      originals are covered by path-keyed exclusions rather than by this SPEC's code.
- [x] Regression fixtures restore the exact bugs (stale release date, "8 specialized agents",
      "8 agent definitions") and prove the new checks catch them. Positive controls verified by
      two planted mutations: removing the 40% floor fails 3 tests, dropping the singular
      alternation fails exactly the E1 defect test.
- [x] Running the check against current `dev` HEAD stays GREEN — asserted continuously by
      `test_live_repo_stays_green_on_count_consistency`, not just checked once by hand.
- [x] `docs/reference/REFCARD-DOCS-STALENESS.md` documents the new checks, the four line shapes,
      and the two test-only env overrides in its existing inventory.
- [x] `CHANGELOG.md` / `docs/CHANGELOG.md` `[Unreleased]` gets an entry.
- [x] No new script, no new external dependency (D1/D4) — the checks live inside
      `docs-staleness-check.sh`, using awk and the python3 it already requires.

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
