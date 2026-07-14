# /craft:git:issue-check

> **Check whether an open GitHub issue's premise still holds against current code**

---

## Synopsis

```bash
/craft:git:issue-check <issue> [options]
```

**Quick examples:**

```bash
# Check issue #199 against current code
/craft:git:issue-check 199

# Structured JSON output
/craft:git:issue-check 199 --json

# Check an issue in a different repo
/craft:git:issue-check 42 --repo Data-Wise/other-repo
```

---

## Description

Before implementing a fix requested by an open GitHub issue, this command
checks whether the issue's own premise still holds against current code.
It fetches the issue's live state (never cached — always a fresh
`gh issue view`), checks its unmet acceptance-criteria checkboxes against
the repo's tracked files, and returns a structured verdict with cited
evidence — never a bare label.

**Advisory only.** This command never closes, edits, comments on, or
otherwise mutates the issue — it only reads.

---

## Options

| Option     | Description                                       | Default            |
|------------|----------------------------------------------------|---------------------|
| `issue`    | Issue number (required, e.g. `199`)                 | —                   |
| `--repo`   | Repo in `OWNER/NAME` form                           | `Data-Wise/craft`   |
| `--json`   | Output structured JSON instead of the verdict box   | `false`             |

---

## Verdicts

| Verdict   | Meaning                                                                 | Recommended Action                        |
|-----------|--------------------------------------------------------------------------|--------------------------------------------|
| `valid`   | Premise still holds — the fix described is still needed                  | Proceed with implementation                 |
| `moot`    | Issue is closed, or all cited acceptance criteria are already met        | Close or re-scope the issue                 |
| `unclear` | Cannot be mechanically verified (no checkboxes, or deliverables already exist) | Read the issue and repo state manually |

---

## Output

```text
┌─ ISSUE-CHECK ─ #199 ──────────────────────────────────────────────┐
│ Verdict:    VALID   (premise still holds)                         │
│ Evidence:   commands/dist/cowork.md — cited command not found:    │
│             "A craft command (e.g. `/craft:dist:cowork`...)"      │
│ Reasoning:  6 of 6 acceptance criteria unchecked; cited            │
│             deliverable(s) not found in the repo.                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Automatic Gating

`/craft:orch:drive` runs this check automatically when the driven SPEC
cites a `#NNN` issue — the verdict is surfaced but never blocks the drive
loop. If no issue is cited, the check is skipped entirely at zero cost.

---

## Exit Codes

| Code | Meaning                                          |
|------|---------------------------------------------------|
| 0    | Verdict computed (regardless of status)            |
| 0    | Issue not found / `gh issue view` failed (nothing to triage) |

---

## See Also

- [/craft:ci:triage](../ci/triage.md) — the CI-failure analog this pattern mirrors
- [/craft:orch:drive](../orch/drive.md) — pre-filtered gate consumer
