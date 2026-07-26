# News

Release announcements and notable changes for the Craft plugin.

---

## v4.4.0 — smart-help --refine + exhaustive Default Policy table

**Released:** 2026-07-26 · **Type:** Minor · **PR:** [#313](https://github.com/Data-Wise/craft/pull/313)

### Highlights

- **`smart-help` declares `--refine`** (D7) — opt-in, default-OFF, closing the last dangling item
  on #268's prompt-refiner umbrella (originally from `SPEC-interactive-commands-2026-06-25.md`
  §8).
- **`prompt-refiner`'s Default Policy table is now exhaustive and file-path-keyed** — fixed 3
  stale display names (`workflow:brainstorm`, `orchestrate`, `orchestrate:workflow`) and added 2
  live callers the table was silently missing (`commands/plan.md`, `commands/arch/plan.md`). A
  new dogfood test (`test_refine_default_policy_table_exhaustive`) keeps it from drifting again.

### Notes

Issue #268's other two proposed items (named "Copy for elsewhere" destinations, `--scope global`)
and #266 (multi-round grill mode) were grilled, then killed on adversarial review before
implementation — see `docs/specs/GRILL-prompt-refiner-remaining-2026-07-26.md`'s amendment for
the reasoning.

---

## v4.3.0 — Guard-Bypass Escape Hatch + Reference-Scope Guard

**Released:** 2026-07-25 · **Type:** Minor · **PRs:** [#305](https://github.com/Data-Wise/craft/pull/305), [#306](https://github.com/Data-Wise/craft/pull/306)

### Highlights

- **`CRAFT_GUARD_ALLOW_DEV_EDIT`** (#281) — closes a self-referential deadlock: creating the
  `.claude/allow-once`/`allow-dev-edit` branch-guard bypass marker was itself gated by the guard it
  was meant to bypass. Reuses the `CRAFT_GUARD_ALLOW_FORCE_DELETE` (#168) env-var
  pre-authorization pattern.
- **`reference-scope-guard.sh`** (#286, NEW) — advisory-only PreToolUse hook warning (never
  blocking) when a Write/Edit targets `~/.claude/reference/` with a non-conforming filename.
  Shares `install-guards.sh` and the `guards.json` registry with `branch-guard`/`no-switch-guard`.

See the [full changelog](CHANGELOG.md) for details.

---

## v4.2.0 — /craft:finish Rename + Homebrew CI Gate Repair

**Released:** 2026-07-19 · **Type:** Patch (breaking rename, no version-major bump) · **PR:** [#296](https://github.com/Data-Wise/craft/pull/296)

**BREAKING:** `/craft:done` renamed to `/craft:finish` ([ADR-006](adr/ADR-006-done-renamed-to-finish.md))
— matches the existing zsh `finish` alias, no back-compat shim. Command count unchanged (48; a
rename, not an addition).

### Highlights

- **`/craft:finish`** replaces `/craft:done` everywhere — the old slash entry point no longer resolves.
- **`/craft:restore` docs corrected** — its spec/report status fixed from `DRAFT` to `SHIPPED` (it had
  already shipped in v4.1.0, below — this NEWS page itself was one of the places that correction never
  reached until now).
- **Homebrew tap recovery** — `homebrew-tap`'s `main` gained branch protection since
  `homebrew-release.yml` was last touched, breaking the automated formula push; recovered manually,
  fixed the workflow to push via a bot-branch PR instead of a direct push, and closed 2 latent
  CI-gate bugs surfaced in `homebrew-tap` along the way.

See the [full changelog](CHANGELOG.md) for details.

---

## v4.1.0 — /craft:restore + /craft:refine Confirm-Flow Fix

**Released:** 2026-07-17 · **Type:** Minor · **PR:** [#295](https://github.com/Data-Wise/craft/pull/295)

### Highlights

- **`/craft:restore`** (NEW) — combines git-activity recap (`dev/git` skill) with `.STATUS`-based
  session recap (`adhd-workflow` skill) into one read-only "restore my context" entry point.
  Replaces the deleted `git-recap`/`recap` commands. See the
  [architecture doc](architecture/craft-restore-pipeline.md).
- **`/craft:refine` confirm-flow fix** — the fenced refined-prompt block + 4-way confirm
  (Execute now / Copy for elsewhere / Edit first / Skip) design was locked but never implemented;
  now shipped across all 5 `--refine` callers plus the standalone command.
- **Full post-v4.0.0 doc-staleness cleanup** — 47→48 count-drift sweep across ~35 files, mermaid
  diagram health score 82.3→100.

See the [full changelog](CHANGELOG.md) for details.

---

## v4.0.0 — Folio Split

**Released:** 2026-07-16 · **Type:** Major (breaking) · **PR:** [#294](https://github.com/Data-Wise/craft/pull/294)

### Highlights

- **BREAKING: docs/publishing surface extracted** to the new standalone [`folio`](https://github.com/Data-Wise/folio)
  plugin — 24 commands, 6 agents, 6 skills moved out. See
  [docs/MIGRATION-v4.md](https://github.com/Data-Wise/craft/blob/main/docs/MIGRATION-v4.md) for the
  full command migration table.
- **Counts: 94→47 commands / 45→40 skills / 8→2 agents.**
- **Guard suite hardening bundled** — `cd`-target resolution across compound Bash commands,
  `guards.json` write-race lock, orchestrate-dispatch self-containment (closes 4 live false
  positives).
- **`ci-bash-suites` validator** — closes the gap where `/craft:check` never ran the shell test
  suites CI invokes directly (pytest doesn't collect them).

See the [full changelog](CHANGELOG.md) for details.

---

## v2.61.1 — Guard Suite Consolidation

**Released:** 2026-07-08 · **Type:** Patch · **PR:** [#272](https://github.com/Data-Wise/craft/pull/272)

The branch-guard and no-switch-guard systems are now unified under a single
skill-driven operations layer. Four stale shims were thinned and 62 new tests
added.

### Highlights

- **`--classify` / `GUARD_DRY_RUN=1`** — ground-truth output for both guard
  hooks, useful for testing and debugging guard rules without side effects.
- **Portable `sedi()` wrapper** — detects GNU/BSD sed at runtime; replaces all
  inline `sed -i` calls for cross-platform compatibility.
- **`baseline.json`** — drift detection for guard configuration state.
- **4 stale shims thinned** — `git/branch.md`, `git/clean.md`, `git/status.md`,
  `git/sync.md` reduced to redirect-only stubs.

### Documentation

- 3 orphan docs archived to `docs/archive/`.
- `VALIDATOR-BEST-PRACTICES.md` added to nav with corrected `.claude-plugin`
  paths.
- Tutorial and refcard contents updated for PR #270 and #272 features.

See the [full changelog](CHANGELOG.md) for details.

---

## v2.61.0 — Token-Usage Reduction & Post-Release Follow-ups

**Released:** 2026-07-06 · **Type:** Minor · **PRs:** [#232](https://github.com/Data-Wise/craft/pull/232), [#270](https://github.com/Data-Wise/craft/pull/270)

Cuts the always-loaded orchestration path by moving procedure out of
commands/agents and into skills that load conditionally. Introduces the
`command-skill-token-efficiency` skill for future authoring.

### Highlights

- **Orchestration token reduction** — `/refine` 631→42 lines, `/brainstorm` split
  with 4→2 decision points, `orchestrator-v2.md` 1473→1212 lines.
- **Model-pinned orchestrator agents** — `sonnet`/`haiku` for the first time.
- **Dead agent-dispatch removed** from `/craft:do` and `/release`.
- **`verify-surfaces.sh --report-only` / `--version`** — never-blocking
  drift inspection for release-state verification.
- **`release-rollback.md` runbook** — manual per-surface undo steps for a bad
  release.

See the [full changelog](CHANGELOG.md) for details.

---

## v2.60.0 — Command Namespace Reorganization

**Released:** 2026-07-05 · **Type:** Minor

Major namespace cleanup: root-level promotions, `orchestrate` → `orch` rename,
`ci:` consolidation, and dead commands removed.

### Highlights

- **Root promotions** — `/craft:next`, `/craft:done`, `/craft:refine`,
  `/craft:brief`, `/craft:brainstorm` promoted from `workflow:`.
- **`orchestrate` → `orch`** — renamed across ~110 files.
- **`docs:generate` router** — unified entry point for all 9 doc generators.
- **`task:` namespace** — `task-cancel`/`task-output`/`task-status` dedicated.
- **`/craft:quota` deleted** — logic folded into `/craft:orch` Step 1.5.

See the [full changelog](CHANGELOG.md) for details.

---

## Older Releases

For releases prior to v2.60.0, see the [Changelog](CHANGELOG.md) or
[Version History](VERSION-HISTORY.md).
