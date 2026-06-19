# Tutorial: ci:watch — Poll a CI Run to Completion

By the end of this tutorial you will have:

- Watched a CI run poll to completion and received a routing decision
- Used background mode so the poll doesn't block your session
- Handled a green result (auto-merge suggestion) and a red result (triage routing)

**Prerequisites:** craft installed, `gh` CLI authenticated, a recent push with a CI run in progress.

---

## Step 1: Watch the Latest Run

```
/craft:ci:watch
```

Polls the most recent CI run every 30 seconds:

```
CI Watch — Data-Wise/craft (dev branch)
────────────────────────────────────────
Run #1234 · Craft CI
  [Poll 1/10] ⏳ In progress (0:30 elapsed)
  [Poll 2/10] ⏳ In progress (1:00 elapsed)
  [Poll 3/10] ✅ Completed: success (1:28 elapsed)

Result: GREEN
→ All checks passed. Safe to merge PR #176.
```

---

## Step 2: Watch a Specific Run or PR

```
/craft:ci:watch --target pr/176
/craft:ci:watch --target run/1234567
```

---

## Step 3: Run in the Background

```
/craft:ci:watch --bg
```

Starts polling in the background. You'll receive a notification when the run completes. Your session stays free for other work.

---

## Step 4: Handle a Red Result

When CI fails, `ci:watch` routes directly to triage:

```
  [Poll 5/10] ❌ Completed: failure (2:30 elapsed)

Result: RED
→ Routing to /craft:ci:triage for failure classification...

Classification: DIFF-CAUSED
  Failing step: tests (src/auth/oauth.test.ts:45)
  Recommendation: Fix the failing test before merging
```

---

## Step 5: JSON Output

```
/craft:ci:watch --json
```

Returns the final run state as structured JSON for scripting.

---

## What's Next

- If green, proceed to merge: `gh pr merge --merge`
- If red and `DIFF-CAUSED`, fix the code and push
- If red and `PRE-EXISTING`, use `/craft:ci:triage` to get the `--admin` recommendation
