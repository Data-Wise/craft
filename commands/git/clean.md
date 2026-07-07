---
description: Clean up merged branches safely
category: git
arguments:
  - name: dry-run
    description: Preview branches that would be deleted without executing
    required: false
    default: false
    alias: -n
deprecated: true
replaced-by: "skills/dev/git/"
---

# /craft:git:clean - Remove merged branches

> **This command is a thin shim.** The canonical behavior lives in the
> `git-workflow` skill (`skills/dev/git/SKILL.md`, Operation 4: Branch
> Cleanup). This file exists only to preserve the explicit
> `/craft:git:clean` slash entry point through the v2.34.0 → v3.0.0
> migration.

> **Naming note:** this command governs **branch deletion** (removing merged
> `git branch`es). It is unrelated to `git clean -f` (removing untracked
> *working-tree files*), which `branch-guard.sh` gates separately as a
> MEDIUM-risk Bash command on protected branches. Same word, two different
> operations — no behavioral conflict, just a naming collision worth knowing
> about (found during `SPEC-branch-protection-consolidation-2026-07-07`'s
> `commands/git/*.md` sweep).

## Flags

```bash
/craft:git:clean --dry-run   # Preview what would be deleted
/craft:git:clean -n
/craft:git:clean              # Delete merged branches (with confirmation)
```

## When invoked

1. **Load the canonical procedure:** read
   [`skills/dev/git/SKILL.md`](../../skills/dev/git/SKILL.md), Operation 4
   (Branch Cleanup), and follow it exactly — the two-pass merged-branch
   detection (`git branch --merged` + `is_squash_merged`), the ORCHESTRATE
   stray-file warning, and the safety rules in Cross-Operation Patterns.
2. **Do not reimplement here.** Protected-branch exclusion, the
   uncommitted/unpushed skip checks, and the confirm-before-delete gate all
   live in Operation 4 and the skill's Cross-Operation Patterns section — do
   not restate them in this shim.

## Why this is a shim

`/craft:git:clean` was a standalone 85-line command that already claimed
`replaced-by: "skills/dev/git/"` in its frontmatter without actually being
thinned — a stale-shim drift found and fixed by
`SPEC-branch-protection-consolidation-2026-07-07` §4.7. Both entry paths —
the explicit `/craft:git:clean` slash command and natural-language triggers
("clean merged branches", "delete merged") — route to the same skill
Operation.

## See Also

- `/craft:git:branch` - Branch management
- `/craft:git:worktree` - Worktree cleanup (`clean`/`finish` sub-actions)
- `/craft:git:protect-baseline` - Apply GitHub-side branch protection (PR required, no force-push, no delete) to any repo
