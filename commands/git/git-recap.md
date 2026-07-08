---
description: Git activity summary - recent commits, branch status, and productivity insights
category: git
arguments:
  - name: mode
    description: Display mode (default|detailed|summary)
    required: false
    default: default
  - name: dry-run
    description: Preview git commands that will be executed without running them
    required: false
    default: false
    alias: -n
deprecated: true
replaced-by: "skills/dev/git/"
---

# /git-recap - Git Activity Summary

> **This command is a thin shim.** The canonical behavior lives in the
> `git-workflow` skill (`skills/dev/git/SKILL.md`, Operation 7: Git Activity
> Recap). This file exists only to preserve the explicit `/craft:git:git-recap`
> slash entry point through the v2.34.0 → v3.0.0 migration.

## Flags

```bash
/craft:git:git-recap                 # Default mode
/craft:git:git-recap --detailed      # This week's commits, breakdown, stashes
/craft:git:git-recap --summary       # One-line summary
/craft:git:git-recap --dry-run       # Preview the read-only git commands, no execution
```

## When invoked

1. **Load the canonical procedure:** read
   [`skills/dev/git/SKILL.md`](../../skills/dev/git/SKILL.md), Operation 7
   (Git Activity Recap), and follow it exactly — today's/this-week's
   commits, ahead/behind, unpushed work, open PRs (`gh pr list --author @me`),
   and the `default`/`detailed`/`summary` modes.
2. **Do not reimplement here.** The recap-output formatting, productivity
   insights, and warning-flag logic all live in Operation 7 — do not
   duplicate them in this shim.

## Learning material

The progressive "start every session with a git recap" habit-building
content (4-week learning path, memory strategies, practice exercises) lives
in [`skills/dev/git/references/learning-guide.md`](../../skills/dev/git/references/learning-guide.md)
— surfaced by Operation 11 (Reference Docs) when the user asks to "teach me
git" or "learn git workflow". It is not restated here.

## Why this is a shim

`/craft:git:git-recap` was a standalone 508-line command that already
claimed `replaced-by: "skills/dev/git/"` in its frontmatter without actually
being thinned, and duplicated the "Learning & Practice" pedagogical section
that already lives in full in `skills/dev/git/references/learning-guide.md`
— a stale-shim drift found and fixed by
`SPEC-branch-protection-consolidation-2026-07-07` §4.7. Both entry paths —
the explicit `/craft:git:git-recap` slash command and natural-language
triggers ("git activity", "git recap", "what did I commit today") — route to
the same skill Operation.

## See Also

- `/craft:git:status` - Enhanced git status
- `/craft:git:sync` - Sync with remote
- `skills/dev/git/references/learning-guide.md` - Progressive git-workflow learning path
