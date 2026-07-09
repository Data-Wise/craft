# Phase 0 Recon — External-Caller Findings (T0.1 / T0.2)

**Run:** 2026-07-09, read-only. **Gate:** SPEC R1-B7.
**Headline: "delete 39" → "delete 24, keep 15 as aliases" → (Phase 1a) "delete 21, hold 3."**

> ## ⚠️ RECON GAP FOUND DURING BUILD (Phase 1a) — the through-line gate caught it
>
> The external-caller recon (below) checked flow-cli/atlas/~/.claude/homebrew/tutorials,
> but **NOT craft's own skills**. During deletion, `test_skill_referenced_commands_exist`
> surfaced that **3 of the 24 "safe" deletions carry unique logic** (ADR-002 rich-body trap):
>
> | Command | Evidence | Disposition |
> |---|---|---|
> | `git:docs:refcard` (363 ln) | content NOT in `references/` (unlike the 3 true shims) | **RESTORED — hold** |
> | `check:gen-validator` (447 ln) | command >> its 127-line skill; logic lived in the command | **RESTORED — hold** |
> | `workflow:insights` (194 ln) | functionally referenced by brainstorm-insights skill | **RESTORED — hold** |
>
> The other 3 git-docs (`learning-guide`/`safety-rails`/`undo-guide`) ARE true shims
> (content in `skills/dev/git/references/`) — safely deleted, SKILL.md table repointed.
>
> **Net: delete 21 now; 3 held pending content-migration decision (keep-as-command, or
> migrate logic into the skill THEN delete). Command count 115 → 94.**

## Safe to delete (24 — zero external callers)

`git:init` · `git:git-recap` · `git:sync` · `git:docs:safety-rails` ·
`git:docs:undo-guide` · `git:docs:learning-guide` · `git:docs:refcard` ·
`workflow:stuck` · `workflow:focus` · `workflow:recap` · `workflow:insights` ·
`workflow:spec-review` · `task:status` · `task:output` · `task:cancel` ·
`check:gen-validator` · `site:nav` · `site:init` · `site:add` · `site:audit` ·
`site:consolidate` · `site:theme` · `site:create` · `site:preview`

## Keep as alias — HAVE live external callers (15)

| Command | Refs | Caller(s) — why it can't just be deleted |
|---|---|---|
| `git:unprotect` | 6 | `~/.claude/reference/proof-tutorial-standards.md`, homebrew `manifest.json` + `Formula/craft.rb` caveats, craft tutorials — the branch-guard bypass, user-facing |
| `site:publish` | 6 | **flow-cli `teach map` tests** (`dogfood-teach-map.zsh`, `test-teach-map-unit.zsh`) assert it in output |
| `site:progress` | 5 | flow-cli `teach map` tests |
| `git:worktree` | 4 | craft tutorials |
| `site:check` | 4 | flow-cli `teach map` tests |
| `site:deploy` | 4 | flow-cli tests + `TUTORIAL-post-merge-pipeline.md` |
| `git:guard` | 3 | `TUTORIAL-guard-suite.md` (entire tutorial built on it) |
| `git:protect` | 3 | tutorials |
| `site:build` | 3 | flow-cli `teach map` tests |
| `git:status` | 2 | tutorials |
| `git:branch` | 2 | tutorials |
| `site:update` | 2 | tutorials/flow-cli |
| `git:clean` | 1 | tutorials |
| `git:protect-baseline` | 1 | tutorials |
| `site:status` | 1 | tutorials |

## Blocking implications (why this halts autonomous Phase 1a)

1. **flow-cli test breakage** — deleting `site:{publish,build,deploy,progress,check}`
   breaks flow-cli's `teach map` test suite (they assert those names appear). Cross-repo
   coordination needed, or keep-as-alias.
2. **`git:unprotect` is load-bearing** — referenced in global config + the shipped homebrew
   caveats. Not a dead alias; it's the documented branch-guard bypass.
3. **`git:guard` owns a whole tutorial** — deletion orphans `TUTORIAL-guard-suite.md`.
4. **Tutorials reference many "dead" git/site commands** — craft's own docs would break.

## Decision needed (CHECKPOINT A)

- Confirm scope: **delete 24 now, keep 15 as thin aliases** (recommended), OR
- Coordinate flow-cli + tutorial + homebrew updates first to shrink the keep-set.

Reconciles: `safe-delete (24) + keep-as-alias (15) = 39`. ✓
