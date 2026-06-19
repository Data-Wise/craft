# ORCHESTRATE — craft Guard Suite

> **How to use:** Open a NEW Claude Code session with this worktree as cwd
> (`cd ~/.git-worktrees/craft/feature-guard-suite && claude`), then execute the steps below.
> This session auto-loads `craft/CLAUDE.md`. Spec: `docs/specs/SPEC-craft-guard-suite-2026-06-19.md`.
> Full plan mirror: `~/.claude/plans/precious-drifting-sky.md`.

## Context

craft ships one PreToolUse guard (`scripts/branch-guard.sh`, `exit 2`+stderr). A second guard
(`no-switch-guard.sh`, harm-tiered switch/worktree/restore via native `permissionDecision` JSON) was
authored but lives personal-only in `~/.claude/hooks/`. They duplicate the destructive-restore rule
with divergent regexes, and there's no way to list/enable/disable guards. This feature promotes
no-switch-guard into craft, reconciles the dup, adds a list/enable/disable surface with an
ADHD-friendly toggle UX, softens three hard-denies to confirm, and ships docs — **keeping the two
emission mechanisms separate** (architecture review rejected a single table-driven engine).

## Decisions (resolved spec Q1–Q8)

- **Q1** destructive-restore → **no-switch-guard, click-ask**; remove branch-guard's copy.
- **Q2** generalize `install-branch-guard.sh` → `install-guards.sh` (installs both).
- **Q3** **defer Phase B** (`harm-classify.sh`) — only ~1-2 rules shared; extract when a 3rd appears.
- **Q4** new `/craft:git:guard` command (accept the ~13-file count cascade).
- **Q5** per-guard toggle, persistent + session (no per-rule).
- **Q6** registry `~/.claude/guards.json` (user-global).
- **Q7** statusline chip display-only (claude-hud renders); verify hud renderer (non-blocking).
- **Q8** default mute window 30m, per-guard configurable.

## Scope

**In:** Phase A (promote + reconcile + guard-audit ext), Phase C (command + registry + toggle UX +
validator), delete→ask, docs. **Out:** Phase B (`harm-classify.sh`) — deferred.

## Steps

### 1. A1 — Promote `no-switch-guard.sh`

- Copy `~/.claude/hooks/no-switch-guard.sh` → `scripts/no-switch-guard.sh` (+ registry preamble, Step 4).
- Generalize `scripts/install-branch-guard.sh` → `install-guards.sh`: parametrize the copy block
  (`:47-67`) + jq-append (`:70-112`). branch-guard keeps `Edit|Write`+`Bash`; no-switch-guard appends
  **one `Bash` entry AFTER branch-guard** (preserve deny>ask>allow precedence). Per-script idempotency
  check (`jq … any(test("no-switch-guard"))`).
- Add `tests/test_no_switch_guard.sh` (model on `tests/test_branch_guard.sh` harness): assert silent
  (read-only) / announce (`systemMessage`: clean-tree switch, `worktree add`) / ask
  (`permissionDecision`: dirty switch, `-c`/`-b`, onto-main, worktree remove/move, restore).

### 2. A2 — Reconcile destructive-restore (Q1)

- Delete branch-guard's `git restore` `_confirm` block (`scripts/branch-guard.sh:724-733`).
- Confirm no-switch-guard's restore rule (`~64-68`) covers `git restore` AND `git checkout -- <file>`,
  and **add the `--staged` exclusion** branch-guard had.

### 3. delete→ask (independent)

- `scripts/branch-guard.sh`: `rm -rf .git` `_hard_block` (`:471-485`) → `_confirm "git_destroy" …`;
  `reset --hard` `block` in block-all handler (`:545-552`) → `_confirm "reset_hard_main" …`.
- Flip the matching asserts in `tests/test_branch_guard.sh` (`:669` + catastrophic group) and
  `tests/test_branch_guard_e2e.sh` from expect-block → expect-confirm.

### 4. C1b — Registry + self-check

- `~/.claude/guards.json`: `{ "guards": { "<name>": { "enabled": true, "muted_until": null,
  "mute_window_min": 30 } } }`. Seed in `install-guards.sh`.
- Each guard gains a ~3-line preamble: read own `enabled`+`muted_until` (jq), **fail-OPEN**, `exit 0`
  silently if disabled or `now < muted_until`. Mirror the `.claude/branch-guard.json` read pattern.

### 5. C1c — ADHD toggle UX

- Auto-expire: `disable` writes `muted_until = now + mute_window_min`; `--permanent` → `enabled:false`.
- In-prompt mute: no-switch `ask` reason advertises the mute verb; branch-guard `[CONFIRM]` hint equiv.
- Statusline chip (Q7, non-blocking): verify claude-hud can render `🛡️/⚠️ (Nm)/⛔` from `guards.json`;
  else document the `list` fallback.

### 6. C1 — `/craft:git:guard` command (Q4)

- New `commands/git/guard.md` matching `commands/git/worktree.md` frontmatter + section skeleton.
  Actions: `list` (numbered: name/file/matcher/mechanism/gates/state), `status`, `explain "<cmd>"`
  (dry-run through both guards → tier+why), `test`, `enable`/`disable <name|#>` (+`--permanent`/
  `--session`), profiles `focus`/`yolo`/`spec`. Reads/writes `guards.json`.

### 7. C2 — `guard-consistency` validator

- New `.claude-plugin/skills/validation/guard-consistency.md` (frontmatter like
  `validation/lint-check.md`: `name: check:guard-consistency`, `category: validation`, `context: fork`,
  `hot_reload: true`). Auto-detect: `~/.claude/hooks/branch-guard.sh` exists. Check (a) duplicate
  PreToolUse matchers, (b) duplicated rule coverage. PASS/FAIL.

### 8. A3 — Extend `skills/guard-audit/SKILL.md`

- Insert Step 1b (settings.json matcher-overlap) + Step 1c (duplicated-rule-coverage + disabled/muted
  surfacing) before Step 2 (Friction Analysis). Keep the 5-step scaffold.

### 9. Docs + index cascade (spec §8)

- `docs/guide/guard-suite.md` (`/craft:docs:guide`), `docs/guide/guard-design.md`,
  `docs/tutorials/guard-suite.md` (`/craft:docs:tutorial`), `docs/REFCARD.md` guard section.
- `./scripts/bump-version.sh <next>` (13 Tier-1 files + git subtotal at `hub.md`), then
  `./scripts/docs-staleness-check.sh --fix` (Phase 6 nav, Phase 8 coverage). Add mkdocs nav for new pages.

### 10. Approve spec + tests

- Update `docs/specs/SPEC-craft-guard-suite-2026-06-19.md`: `Status: approved`, replace §9
  Open-questions with the resolved decisions, bump History.
- Run throughout: `bash tests/test_no_switch_guard.sh`, `bash tests/test_branch_guard.sh
  tests/test_branch_guard_e2e.sh`, `python3 -m pytest tests/`, `./scripts/validate-counts.sh`,
  `mkdocs build`.

## Verification

1. `bash tests/test_no_switch_guard.sh` green; branch-guard suites green with flipped confirm asserts.
2. Registry: disable a guard → its hook `exit 0` silently; delete `guards.json` → still gates (fail-open).
3. `/craft:git:guard list` shows state; `disable no-switch-guard` → muted+countdown → re-arms.
4. `/craft:check` → `guard-consistency` PASS (no dup matchers / no dup rule coverage).
5. `python3 -m pytest tests/` + `validate-counts.sh` green; `mkdocs build` clean.
6. PR `feature/guard-suite → dev`.

## Risks

- **Precedence:** append no-switch-guard AFTER branch-guard on `Bash`; don't reorder.
- **Drift:** confirm `~/.claude/hooks/branch-guard.sh` == `scripts/branch-guard.sh` before editing
  (verified IDENTICAL at worktree creation, 2026-06-19).
- **Phase B deferred:** A2 de-dupes by ownership, not extraction.
