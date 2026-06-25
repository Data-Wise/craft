---
name: preflight-check
description: This skill should be used when the user asks to "pre-flight check", "validate before commit", "validate before PR", "validate before deploy", "is this ready to ship", "check readiness", "run pre-flight", "validate project state", or wants context-aware validation across commit/PR/release/deploy boundaries. Orchestrates universal validators (lint, tests, types, version sync, stale refs, docs, hook conflicts) and supports generating new custom validators.
---

# Pre-flight Check

Universal pre-flight validation across commit, PR, release, and deploy boundaries. Orchestrates the validator suite that lives under `.claude-plugin/skills/validation/` and dispatches the right check set for the current context.

## When to Use

- User asks "is this ready to commit / PR / release / deploy?"
- User says "pre-flight", "validate", "check readiness", or runs `/craft:check`
- Before staging a commit, opening a PR, or kicking off the release pipeline
- After a session of edits, to confirm nothing regressed
- When the user wants to scaffold a new custom validator (`gen-validator` flow)

## Scope Boundary (Read This First)

This skill is broader than its siblings — understand the seams:

| Skill | Concern | Does NOT cover |
|---|---|---|
| **preflight-check** (this) | Cross-cutting validators: lint, tests, types, version sync, stale refs, link integrity, hook conflicts, CLAUDE.md health, docs staleness, badge URLs, formula desc, skill standards (release-gated) | Detection logic, release orchestration, guard rule editing |
| `project-detector` (`skills/ci/`) | Detect project type / build tool / test framework to recommend a CI template | Validation orchestration. It answers "what kind of project is this?" not "is it ready?" |
| `release` (`skills/release/`) | The full release pipeline (version bump → PR → merge → GitHub release → Homebrew → verify). Calls this skill internally for its Step 2 pre-flight gate | Standalone commit/PR validation |
| `guard-audit` (`skills/guard-audit/`) | Tune `branch-guard.sh` rules via `.claude/branch-guard.json` to reduce false positives | Running checks. It edits guard config, doesn't validate the project |

**Rule of thumb:** if the user wants to *run validators*, use this skill. If they want to *change which rules block them*, route to `guard-audit`. If they want a *release*, route to `release` (which calls back into this skill).

## Backing Commands

- `/craft:check` — primary entry point; mode-aware, context-aware orchestrator
- `/craft:check:gen-validator` — scaffold a new validator into `.claude-plugin/skills/validation/`

The skill should prefer invoking the commands rather than re-implementing their logic. The commands handle dry-run, orchestration, and hot-reload validator discovery.

## Context Flags (`--for ...`)

Pick the check set by what the user is preparing for. This is the primary axis of behavior:

| `--for` | Run when user is about to... | Adds beyond default |
|---|---|---|
| `commit` | Stage and commit on a feature branch | Fast lint on changed files, fail-fast tests, basic version-sync, no-secrets scan |
| `pr` | Open a PR to dev/main | Full lint, full test suite, coverage ≥ 80%, internal links, merge-conflict detect, stale-ref scan, hook-conflict audit, CLAUDE.md health |
| `release` | Cut a release (called by `skills/release/`) | Full audit: strict lint, all tests + coverage ≥ 90%, all links, full version audit (fatal on drift), security audit, badge URL both-branch check, formula desc count check |
| `deploy` | Deploy docs site or downstream artifact | Same as `release` minus formula-desc; plus tag-exists check |

If no `--for` is specified, run the "general" check set (lint + tests + git status + docs if changed).

## Mode-Aware Behavior

Modes are orthogonal to `--for` — they tune verbosity, fail-fast, and threshold strictness:

| Mode | Budget | Behavior |
|---|---|---|
| `default` | < 30s | Fast path, fail-fast, summary output |
| `debug` | < 120s | Verbose output, no fail-fast, surface all warnings |
| `thorough` | < 180s | Full lint + types + security + docs sweep |
| `release` | < 300s | Strictest thresholds (coverage ≥ 90%, version drift = fatal) |

Mode applies to the hot-reload validators too via `$CRAFT_MODE` — see the validator template generator output for the per-mode threshold table.

## Recommended Flow

1. **Confirm intent.** Ask which context (`commit`/`pr`/`release`/`deploy`) if the user didn't say. Default to the most conservative reasonable guess based on the current branch (`feature/*` → `commit` or `pr`; `dev` → `release`).
2. **Dry-run first when stakes are high.** For `--for release` or `--for deploy`, suggest `/craft:check --for release --dry-run` to preview the validator plan and time estimate before executing.
3. **Run the appropriate command.** Invoke `/craft:check --for <context> [mode]`. Let the command's Step 0 plan + AskUserQuestion gate handle confirmation.
4. **On failure, route specifically.** Don't just dump errors — point at the right follow-up:
   - Lint failures → suggest `/craft:code:ci-fix` or `/craft:code:lint`
   - Version drift → suggest `/craft:check --version release` for the focused validator
   - Stale refs from a rename → list the files that need updating
   - CLAUDE.md staleness → suggest `/craft:docs:claude-md:sync`
   - Hook-conflict false positives → route to `guard-audit` skill
5. **On all-green, summarize and stop.** Don't recommend "next steps" past the immediate gate the user asked about (per feature-branch-workflow rules: no PR-merge nudging).

## Validator Generation (Separate Operation)

Generating a new custom validator is a *distinct* workflow from running checks. Trigger conditions:

- User says "create a validator", "add a custom validator", "generate a validator template"
- User wants to extend `/craft:check` with project-specific validation logic

In that flow:

1. Use `/craft:check:gen-validator <name> [--languages ...] [--interactive]`
2. The command scaffolds a file under `.claude-plugin/skills/validation/<name>.md` with `hot_reload: true` so `/craft:check` picks it up on next run with no restart.
3. After generation, suggest a smoke test: `CRAFT_MODE=default bash .claude-plugin/skills/validation/<name>.md` then `/craft:check` to confirm auto-discovery.

**Do not** auto-generate a validator while the user is running checks — these are independent concerns. If both are in flight, finish the check pass first.

## Context Header (`--context`)

The check command supports a `--context` flag that *skips* validation and emits only a one-screen session header (project, branch, worktree, base, guard status, phase, test count, docs status, insights). When the user asks "what's the state of this branch?" or "what session am I in?", prefer `/craft:check --context` over running validators. It's read-only and < 1s.

## Output Conventions

The backing command uses box-drawing output (see `commands/check.md`). When this skill summarizes results in chat, mirror that structure compactly:

```text
Project: <name> (<type>)        Context: <for-value>      Mode: <mode>
Lint:    PASS / N issues
Tests:   N/M passed
Version: in sync / DRIFT (file:line)
Docs:    GREEN / YELLOW / RED
Status:  READY / BLOCKED — <reason>
Next:    <single actionable suggestion or none>
```

Keep summaries terse. The command's own output is the system of record.

## Anti-Patterns

- **Don't** re-implement project detection here — defer to `project-detector` via the command.
- **Don't** edit branch-guard rules — that's `guard-audit`.
- **Don't** chain into the release pipeline — let the user invoke `release` explicitly. This skill stops at "READY FOR RELEASE."
- **Don't** silently expand scope. If the user asked `--for commit`, don't also run the release-tier validators just because "they're cheap." Mode budgets exist for a reason.
- **Don't** fix issues the validators report unless the user asks. Surface, then wait.

## See Also

- `commands/check.md` — full check command spec (validators, modes, dry-run output)
- `commands/check/gen-validator.md` — validator scaffolding
- `.claude-plugin/skills/validation/` — hot-reload validator directory
- `skills/release/SKILL.md` — orchestrates this skill at Step 2 of releases
- `skills/ci/SKILL.md` — project detection (used internally to pick check set)
- `skills/guard-audit/SKILL.md` — tune what blocks operations (not what validates them)
