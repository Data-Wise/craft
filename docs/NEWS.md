# News

Release announcements and notable changes for the Craft plugin.

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
