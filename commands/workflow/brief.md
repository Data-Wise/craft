---
description: Generate a 3-line action block (Next step / Watch out for / Connects to) with optional planning expansion
category: workflow
arguments:
  - name: plan
    description: Expand to propose approach, ask 2-3 questions, and output a mini-plan
    required: false
    default: false
  - name: verbose
    description: Expand each block line with 1-2 sentences of context
    required: false
    default: false
  - name: show-context
    description: Show which context sources would be used before generating
    required: false
    default: false
  - name: board
    description: Show ownership/state table (who owns what, what state) above the 3-line block
    required: false
    default: false
---

# /craft:workflow:brief

Generate the 3-line action block from live session context. Invoke explicitly when you want the block — replaces the auto-fire behavior formerly in `research-session-defaults.md`.

## Block format

```
Next step:     [concrete executable action]
Watch out for: [failure condition → exact mitigation]
Connects to:   [exact artifact — branch, package, file, PR, or —]
```

## Flags

| Flag | Effect |
|---|---|
| (none) | 3-line block only |
| `--plan` | Block + propose approach + 2–3 questions + mini-plan |
| `--verbose` | Expand each line with 1–2 sentences of context |
| `--show-context` | Display context sources before generating |
| `--board` | Ownership/state table above the 3-line block |
| `--board --plan` | Board + 3-line block + planning expansion |
| `--board --verbose` | Board + verbose-expanded 3-line block |

## When invoked

### Step 1: Synthesize context

Read sources in priority order. Stop at the first source that gives enough signal:

1. **Conversation history** (primary) — what topic was just discussed, what problem was active?
2. **`.STATUS next:` field** (secondary) — what's on deck?

   ```bash
   grep "^next:" .STATUS 2>/dev/null | head -1
   ```

3. **Git branch + recent commits** (tertiary) — what's being worked on?

   ```bash
   git branch --show-current
   git log --oneline -3
   ```

4. **ORCHESTRATE file + open PRs** (quaternary) — what's in flight?

   ```bash
   ls ORCHESTRATE-*.md 2>/dev/null | head -1
   gh pr list --author @me --state open --limit 3 2>/dev/null
   ```

### Step 1.5: If `--board` flag — infer owner/state rows

Read two sources already fetched in Step 1:

**Source A: ORCHESTRATE-*.md** (if present) — parse numbered list items and classify each:

| Pattern in item text | Owner | State |
|---|---|---|
| "auto", "agent will", "runs automatically", or git/CI shell commands | Me | 🟢 AUTO |
| "wait for CI", "checks", "pending", or `gh pr` with no user action needed | External | ⏳ WAITING |
| "merge", "approve", "decide", "review", "confirm", "choose" | You | 🔵 YOUR CALL |
| "blocked", "waiting on [external]" | You | 🔴 BLOCKED |
| Leading `✅` | — | ✅ DONE — omit unless `--verbose` |

**Source B: Open PRs** — `gh pr list --author @me --state open --json number,title,statusCheckRollup`

- PR with CI in progress / pending → owner: **External**, state: ⏳ WAITING
- PR with CI passed, not yet merged → owner: **You**, state: 🔵 YOUR CALL

**Leader line derivation** (`🎯 RIGHT NOW:`)

Pick the first item from: 🔵 YOUR CALL → ⏳ WAITING → 🟢 AUTO.
If no items found: `🎯 RIGHT NOW: nothing tracked`.

**Row cap:** 6 rows maximum. If more: `… (N more)`.

---

### Step 2: If `--show-context` flag

Before generating, display the source map and wait for confirmation:

```
Context sources:
  Primary:   conversation (last 4 exchanges re: [topic])
  Secondary: .STATUS next: "[value or none]"
  Tertiary:  branch = [branch-name], last commit: "[msg]"
  Connects:  [PR or ORCHESTRATE reference, or none detected]

Generate block? [Y/n]
```

Proceed on Y or Enter. On n, exit cleanly.

### Step 3: Generate the block

Apply ALL constraints below WITHOUT EXCEPTION. They override any tendency toward vague or generic output. Read every constraint before generating.

---

#### `Next step` — EXECUTABLE ACTION CONSTRAINT

MUST be a concrete executable. Use exactly one of these forms:

- **Shell command** — the literal command including flags
- **File + line** — `Open <file>:<line> and [do X]`
- **Named action** — `[Person] — [specific ask, name the artifact]`

**NEVER output:**

- Gerunds without a specific target: "continue working on", "make progress on", "keep implementing"
- Project-level descriptions: "work on the auth feature", "continue the manuscript"
- Conditional hedges: "consider doing X", "you might want to..."

Examples — CORRECT:

```
ssh hopper && sbatch submit_p4.sh
Open missingmed/R/bound_estimator.R:89 and add NULL guard before lapply
git rebase origin/dev && git push --force-with-lease feature/wasserstein-pmed
```

Examples — WRONG:

```
Continue implementing the estimator           ← no specific target
Work on the simulation                        ← project-level
Consider reviewing the PR                     ← hedge, not an action
```

---

#### `Watch out for` — CONDITION → MITIGATION CONSTRAINT

MUST contain two parts joined by `→`:

- **Left** — the specific failure condition that can actually occur given this context
- **Right** — the exact command, step, or action to take when it fires

If you only know the risk but not the mitigation, look it up from the `.STATUS` file or conversation before generating. Do not output a risk without its mitigation.

Examples — CORRECT:

```
If n=8000 task hits 24h wall → scontrol update JobId=<id> TimeLimit=2-00:00:00 before it kills
push rejected (diverged) → git rebase origin/dev first, then --force-with-lease
NA propagation in bound_estimator.R → add is.null(x) guard at line 89 before lapply
```

Examples — WRONG:

```
Be careful about walltime limits              ← no mitigation
Watch out for merge conflicts                 ← no action step
NA values might cause issues                  ← no fix named
```

---

#### `Connects to` — EXACT ARTIFACT CONSTRAINT

MUST reference a specific, named artifact. No project-level or vague references.

Accepted forms — pick the most specific that applies:

- **Git branch**: `<repo> <branch-name>`
- **R package + file**: `<package-name> <path/file>` or `<package-name> (MediationVerse)`
- **Manuscript section**: `<repo> §<section-name>`
- **PR number**: `#<number> [short title]`
- **File range**: `<path>/<file>:<line-range>`
- **No downstream work**: `—`

**NEVER output:**

- Project name without artifact: "the probmed package", "the research project"
- Vague connections: "the related research", "downstream work", "future work"
- Future-tense planning as the entry: "once this is done we'll need to..."

Examples — CORRECT:

```
probmed feature/wasserstein-pmed
missingmed R/bound_estimator.R (MediationVerse)
pmed-modern §Simulation Study
#34 feat: DR estimator promotion
—
```

Examples — WRONG:

```
the related package work                      ← no artifact named
downstream research                           ← vague
the probmed repo                              ← project, not artifact
```

---

### Step 3.5: If `--board` flag — render board above the 3-line block

Output BEFORE the 3-line block:

```text
🎯 RIGHT NOW: [leader item from Step 1.5]

Who       | What                               | State
----------|------------------------------------|----------
Me        | [ORCHESTRATE step — short label]   | 🟢 AUTO
External  | PR #N — [title, max 40 chars]      | ⏳ WAITING
You       | [decision or merge action]         | 🔵 YOUR CALL
```

Empty fallback (no ORCHESTRATE, no open PRs):

```text
🎯 RIGHT NOW: nothing tracked

(No ORCHESTRATE file found and no open PRs. Add an ORCHESTRATE-*.md or open a PR to populate this board.)
```

Then proceed to output the 3-line block (Step 4).

---

### Step 4: Output the block

**Default (no flags):**

```
Next step:     [executable action]
Watch out for: [condition → mitigation]
Connects to:   [exact artifact or —]
```

**With `--verbose`**, expand each line with a short follow-on:

```
Next step:     [executable action]
               → [1–2 sentences: why this step, what state it starts from]

Watch out for: [condition → mitigation]
               → [1 sentence: how to detect before it fires, or how likely]

Connects to:   [exact artifact]
               → [1 sentence: what happens downstream once this step completes]
```

### Step 5: If `--plan` flag

After outputting the block, continue with the planning phase.

**Propose:** 2–3 sentences expanding the Next step into a concrete execution path. Name the specific files, functions, or commands involved.

**Ask 2–3 targeted questions** via AskUserQuestion. Focus on the most critical unknowns — things that would change the approach, reveal blockers, or force a different path:

```json
{
  "questions": [
    {
      "question": "[Most critical unknown for this step]",
      "header": "[Short label, ≤12 chars]",
      "multiSelect": false,
      "options": [
        {"label": "[Option A] (Recommended)", "description": "[why A is the likely right choice]"},
        {"label": "[Option B]", "description": "[trade-off]"},
        {"label": "[Option C]", "description": "[trade-off]"}
      ]
    }
  ]
}
```

**Output mini-plan:**

```
Plan:
1. [Step] — produces: [artifact]
2. [Step] — consumes: [artifact from 1], produces: [artifact]
3. [Step] — produces: [artifact]

Est. time: [X–Y min]
Key risk:  [condition → mitigation]
```

## Integration

**With `--board`:** Reads ORCHESTRATE-*.md step list and open PRs to build an ownership table. The table appears above the 3-line block. Use when you need a quick status scan: who owns what, what's blocking, what requires your decision right now.

**With `/craft:do --brief`:** `do` executes the task, then appends the 3-line block. No `--plan` phase. Block only.

**Suggested footer on `/craft:do` output:** After every `do` completion, a one-line reminder appears:

```
💡 /craft:workflow:brief --plan to plan next steps.
```

**Replaces:** `## End every research response with the action block` in `~/.claude/rules/research-session-defaults.md`. That section has been removed; invoke this command explicitly.

## See Also

- `/craft:do <task> --brief` — execute + append block
- `/craft:workflow:done` — full session completion flow
- `/craft:workflow:brainstorm` — full planning session from scratch
