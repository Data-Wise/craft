---
description: "Poll a CI run to completion, then route the next action: merge if green, triage if red"
category: ci
arguments:
  - name: target
    description: "PR number (#NNN), commit SHA, or run-id to watch (default = current branch's latest run)"
    required: false
  - name: repo
    description: "Repo in OWNER/NAME form (default = Data-Wise/craft)"
    required: false
  - name: bg
    description: "Print a copy-paste background-poll snippet instead of watching inline"
    required: false
    default: false
  - name: json
    description: "Emit structured JSON (run, conclusion, next_action) instead of the box"
    required: false
    default: false
related_commands: ci:status, ci:triage, code:ci-fix
tags: ci, watch, release, debugging
---

# /craft:ci:watch - Watch a CI Run to Completion

Poll a CI run until it finishes, then **route the next action**: suggest a merge
when green, or hand off to triage when red. This wraps the `gh run watch` /
poll-then-notify pattern repeated by hand across every release.

## When to Use

- Pre-merge: confirm a PR's checks land green before merging.
- Release gate: watch the main-bound run, then jump to post-release verification.
- Background monitoring: kick off a poll and get on with other work (`--bg`).

## Implementation

### Step 1: Resolve the target → run-id

Distinguish `#NNN` (PR), a bare SHA, and a numeric run-id. **Never use
`gh pr checks` for polling** — it exits 8 while checks are in progress (see
[[gh-pr-checks-exit-code-8-means-pending-or-failing]]). Resolve to a canonical
run-id instead:

```bash
REPO="${REPO:-Data-Wise/craft}"
case "$TARGET" in
  \#*|[0-9][0-9]*)   # PR number → its branch → latest in-progress run
    BRANCH=$(gh pr view "${TARGET#\#}" --repo "$REPO" --json headRefName --jq .headRefName)
    RUN_ID=$(gh run list --repo "$REPO" --branch "$BRANCH" --limit 10 \
      --json databaseId,name,status \
      --jq 'map(select(.status!="completed")) | first | .databaseId') ;;
  *) RUN_ID=$(gh run list --repo "$REPO" --commit "$TARGET" --limit 1 --json databaseId --jq '.[0].databaseId') ;;
esac
```

When several workflows run on one push (CI + docs + validate), latch onto the
**CI** run and **print the resolved workflow name in the header** so the user
sees exactly what is being watched.

### Step 2: Poll loop (15s)

```bash
# gh run view --json status is the safe completion signal (no exit-8 surprise).
until [ "$(gh run view "$RUN_ID" --repo "$REPO" --json status --jq .status)" = "completed" ]; do
  sleep 15
done
CONCLUSION=$(gh run view "$RUN_ID" --repo "$REPO" --json conclusion --jq .conclusion)
```

Print a live progress line (elapsed time) each tick so the watch isn't silent.

### Step 3: Classify and route

`success` → **green path**; anything else → **red path**.

## Output

### Green path

```text
┌─ CI WATCH ─ Craft CI ───────────────────────────────────────────┐
│ Branch:     feature/ci-watch                                    │
│ Conclusion: SUCCESS ✓        Duration: 3m43s                    │
│ Next:       feature → dev — ready to merge:                     │
│             gh pr merge <pr> --squash                           │
└─────────────────────────────────────────────────────────────────┘
```

Next-action by target: **feature branch** → suggest `gh pr merge --squash`;
**main-bound** → `/craft:ci:status --post-release`; **dev** → integration-only,
nothing to do.

### Red path

```text
┌─ CI WATCH ─ Craft CI ───────────────────────────────────────────┐
│ Branch:     feature/ci-watch                                    │
│ Conclusion: FAILURE ✗        Duration: 3m20s                    │
│ Failed:     Validate Plugin Structure                           │
│ Next:       Pre-existing/infra? → see criteria below.           │
│             Unsure → /craft:ci:triage <pr>                      │
└─────────────────────────────────────────────────────────────────┘
```

Watch does **lightweight inline triage** for the two clear-cut cases only:

- Failure step touches a file in your PR diff → fix it: `/craft:code:ci-fix`.
- `Validate Plugin Structure` stuck/failed alone while others pass → `--admin`
  candidate (confirm unrelated first).

Anything ambiguous → forward to **`/craft:ci:triage`** for the deep,
evidence-backed classification. (Watch is the poller; triage is the analyst.)

### `--bg` (background poll)

With `--bg`, print a self-contained, copy-paste snippet (run-id substituted in)
and exit immediately instead of polling inline:

```bash
until [ "$(gh run view <run-id> --json status --jq .status)" = "completed" ]; do sleep 15; done \
  && gh run view <run-id> --json conclusion --jq .conclusion
```

## Error Handling

- **No in-progress run** for the target → report "nothing to watch; already complete?"
- **Ambiguous run** (multiple workflows) → show the resolved workflow name so the
  user can re-target.
- **`--json`** → emit `{run_id, workflow, conclusion, next_action}` and skip the box.

## See Also

- `/craft:ci:triage` — deep triage of a red run (watch forwards the ambiguous case here)
- `/craft:ci:status` — cross-repo dashboard / `--post-release` verification
- `/craft:code:ci-fix` — apply a fix once the cause is a DIFF-CAUSED failure
