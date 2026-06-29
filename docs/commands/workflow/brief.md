# /craft:workflow:brief

> **Generate a 3-line action block (Next step / Watch out for / Connects to) from live session context.**

---

## Synopsis

```bash
/craft:workflow:brief
/craft:workflow:brief --plan
/craft:workflow:brief --verbose
/craft:workflow:brief --show-context
/craft:workflow:brief --board
```

---

## Description

Generates a concise 3-line action block from the live session context. Invoke explicitly when you want the block — it reads conversation history, `.STATUS`, git branch, and open PRs to produce an actionable summary.

**Replaces** the auto-fire block formerly at the end of every research response.

---

## Block Format

```
Next step:     [concrete executable action — shell command, file+line, or named ask]
Watch out for: [failure condition → exact mitigation]
Connects to:   [exact artifact — branch, package, file, PR, or —]
```

---

## Arguments

| Flag | Effect |
|------|--------|
| *(none)* | 3-line block only |
| `--plan` | Block + approach proposal + 2–3 targeted questions + mini-plan |
| `--verbose` | Expand each line with 1–2 sentences of context |
| `--show-context` | Display context sources (conversation, .STATUS, git, PRs) before generating |
| `--board` | Ownership/state table (`🎯 RIGHT NOW:` + Who/What/State rows) above the block |
| `--board --plan` | Board + block + full planning expansion |
| `--board --verbose` | Board + verbose-expanded block |

---

## Context Priority

The command reads sources in this order, stopping at the first that gives enough signal:

1. **Conversation history** — what was just discussed?
2. **`.STATUS next:` field** — what's on deck?
3. **Git branch + recent commits** — what's being worked on?
4. **ORCHESTRATE file + open PRs** — what's in flight?

---

## Examples

**Default — get the block:**

```
/craft:workflow:brief
```

```
Next step:     git rebase origin/dev && git push --force-with-lease feature/my-feature
Watch out for: push rejected (diverged) → rebase origin/dev first, then --force-with-lease
Connects to:   craft feature/my-feature
```

**With `--board` — see ownership table first:**

```
/craft:workflow:brief --board
```

```
🎯 RIGHT NOW: Merge PR #219

Who       | What                        | State
----------|-----------------------------|----------
You       | PR #219 — feat: hooks skill | 🔵 YOUR CALL
External  | CI on main                  | ⏳ WAITING

Next step:     gh pr merge 219 --merge
Watch out for: branch protection blocks merge → use --admin after confirming CI green
Connects to:   #219 feat: hooks skill
```

**With `--plan` — expand to a mini-plan:**

```
/craft:workflow:brief --plan
```

Outputs the 3-line block, then proposes an execution path, asks 2–3 targeted questions via AskUserQuestion, and generates a mini-plan with estimated time and key risk.

---

## Integration

**With `/craft:do --brief`:** `do` executes the task, then appends the 3-line block automatically.

**Suggested `do` footer:** After every `do` completion, a reminder appears:

```
💡 /craft:workflow:brief --plan to plan next steps.
```

---

## See Also

- [`/craft:do`](../do.md) — smart task routing with optional `--brief` footer
- [`/craft:workflow:done`](done.md) — full session completion flow
- [`/craft:workflow:brainstorm`](brainstorm.md) — full planning session from scratch
