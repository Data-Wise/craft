# Tutorial: git:issue-check — Check an Issue's Premise Before Fixing It

By the end of this tutorial you will have:

- Checked whether an open GitHub issue's premise still holds against current code
- Read a structured verdict (`valid` / `moot` / `unclear`) with cited evidence
- Used JSON output to script the check

**Prerequisites:** craft installed, `gh` CLI authenticated.

---

## Step 1: Check an Issue

```
/craft:git:issue-check 199
```

The command fetches the issue's live state, checks its unmet acceptance
criteria against the repo's tracked files, and returns a verdict:

```
┌─ ISSUE-CHECK ─ #199 ──────────────────────────────────────────────┐
│ Verdict:    VALID   (premise still holds)                         │
│ Evidence:   commands/dist/cowork.md — cited command not found:    │
│             "A craft command (e.g. `/craft:dist:cowork`...)"      │
│ Reasoning:  6 of 6 acceptance criteria unchecked; cited            │
│             deliverable(s) not found in the repo.                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step 2: Understand the Verdicts

| Verdict | Meaning | Recommended Action |
|---------|---------|---------------------|
| `valid` | Premise still holds — the fix described is still needed | Proceed with implementation |
| `moot` | Issue is closed, or all cited acceptance criteria are already met | Close or re-scope the issue |
| `unclear` | Cannot be mechanically verified (no checkboxes, or cited deliverables already exist) | Read the issue and repo state manually |

---

## Step 3: JSON Output

```
/craft:git:issue-check 199 --json
```

Returns:

```json
{
  "issue": 199,
  "repo": "Data-Wise/craft",
  "status": "valid",
  "evidence": [{"file": "commands/dist/cowork.md", "lines": null, "note": "..."}],
  "reasoning": "..."
}
```

---

## Step 4: Automatic Gating in `orch:drive`

If a SPEC driven by `/craft:orch:drive` cites a `#NNN` issue, the drive
loop runs this check automatically before starting and surfaces the
verdict — but never blocks. If no issue is cited, the check is skipped
entirely at zero cost.

---

## What's Next

- If `valid`, proceed with the fix.
- If `moot`, consider closing the issue instead of implementing anything.
- If `unclear`, read the issue and current code directly — the check
  won't guess.
- This command never mutates GitHub state — it never closes, edits, or
  comments on the issue.
