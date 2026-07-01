# Tutorial: `/craft:workflow:brief`

**Generate a 3-line action block from live session context**

## Overview

`/craft:workflow:brief` replaces the "always append a 3-line block" behavior
that used to auto-fire at the end of research-mode responses. Invoke it
explicitly when you want a scannable Next step / Watch out for / Connects to
summary, with optional planning and board expansions.

This tutorial walks through:

1. The default 3-line block
2. `--board` — ownership/state table
3. `--plan` — propose approach + questions + mini-plan
4. `--verbose` — expanded context per line

**Time**: 10 minutes
**Prerequisites**: Craft plugin installed, an active session with some context (branch, `.STATUS`, or an open PR)

---

## Scenario 1: Default Block

**Goal**: Get a quick "what's next" summary without leaving the conversation.

```bash
/craft:workflow:brief
```

**Expected output**:

```
Next step:     git rebase origin/dev && git push --force-with-lease feature/wasserstein-pmed
Watch out for: push rejected (diverged) → git rebase origin/dev first, then --force-with-lease
Connects to:   probmed feature/wasserstein-pmed
```

Craft synthesizes this from, in priority order: the conversation history,
`.STATUS`'s `next:` field, the current git branch + recent commits, and any
open `ORCHESTRATE-*.md` file or open PRs. Each line is constrained — `Next
step` must be a literal executable command, file+line, or named action
(never a vague gerund like "continue working on"); `Watch out for` must pair
a concrete failure condition with its exact mitigation; `Connects to` must
name a specific artifact, not a project name.

---

## Scenario 2: `--board` — Ownership Table

**Goal**: See who owns what before deciding your next move, when multiple
things are in flight (an `ORCHESTRATE-*.md` file and/or open PRs).

```bash
/craft:workflow:brief --board
```

**Expected output**:

```
🎯 RIGHT NOW: Merge PR #232

Who       | What                               | State
----------|------------------------------------|----------
You       | Merge PR #232                      | 🔵 YOUR CALL
External  | PR #233 — CI running                | ⏳ WAITING
Me        | Post-merge docs sync                | 🟢 AUTO

Next step:     gh pr merge 232 --merge
Watch out for: branch protection blocks merge → confirm --admin with user first
Connects to:   #232 Token-usage reduction
```

The board is inferred from `ORCHESTRATE-*.md` step text (classified by
keyword into 🟢 AUTO / ⏳ WAITING / 🔵 YOUR CALL / 🔴 BLOCKED) and open PR
CI status. If nothing is tracked, it prints `🎯 RIGHT NOW: nothing tracked`
instead of guessing.

---

## Scenario 3: `--plan` — Propose Approach + Questions

**Goal**: Turn the "next step" into a concrete execution path with
clarifying questions before you commit to it.

```bash
/craft:workflow:brief --plan
```

**Expected output**: the standard 3-line block, followed by a 2-3 sentence
approach proposal naming specific files/functions, an `AskUserQuestion` with
2-3 targeted questions about the most critical unknowns, and a mini-plan:

```
Plan:
1. Rebase feature branch onto origin/dev — produces: clean linear history
2. Force-push with --force-with-lease — consumes: rebased branch, produces: updated remote
3. Re-run CI — produces: green PR ready to merge

Est. time: 5-10 min
Key risk:  push rejected if remote diverged again → re-fetch and retry
```

---

## Scenario 4: `--verbose` — Expanded Context

**Goal**: Get a short "why" alongside each line, useful when picking the
brief back up after a break.

```bash
/craft:workflow:brief --verbose
```

**Expected output**:

```
Next step:     git rebase origin/dev && git push --force-with-lease feature/wasserstein-pmed
               → Branch is 3 commits behind dev; rebasing now avoids a squash-fold surprise later.

Watch out for: push rejected (diverged) → git rebase origin/dev first, then --force-with-lease
               → Check with `git status` before pushing if unsure.

Connects to:   probmed feature/wasserstein-pmed
               → Once merged, triggers the dev→main release PR.
```

---

## Combining Flags

`--board` and `--plan`/`--verbose` compose:

```bash
/craft:workflow:brief --board --plan      # board + block + planning phase
/craft:workflow:brief --board --verbose   # board + verbose-expanded block
```

`--show-context` (standalone) displays the context sources before
generating, with a `[Y/n]` confirmation gate — useful the first time you're
unsure what the block will be based on.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `Next step: nothing tracked` | No conversation topic, `.STATUS next:`, branch activity, or ORCHESTRATE/PR found | Provide context first (switch to the working branch, or state the task) |
| Board always shows `🎯 RIGHT NOW: nothing tracked` | No `ORCHESTRATE-*.md` in the repo and no open PRs under `gh pr list --author @me` | Expected when nothing is mid-flight — not an error |
| `--plan` skipped the mini-plan | Questions went unanswered (non-interactive session) | Answer inline, or re-invoke with the answers pre-stated in your next message |

---

*See also: [`/craft:do --brief`](../commands/do.md) (execute + append block), [`/craft:workflow:done`](../commands/workflow/done.md) (full session completion), [`/craft:workflow:brainstorm`](../commands/workflow/brainstorm.md) (full planning session from scratch)*
