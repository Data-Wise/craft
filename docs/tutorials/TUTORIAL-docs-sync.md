# Tutorial: docs:sync — Detect Code Changes and Classify Documentation Needs

By the end of this tutorial you will have:

- Run a sync scan to detect which code changes need documentation updates
- Understood the classification output
- Triggered the update pipeline from the sync results

**Prerequisites:** craft installed, a git repository with recent commits.

---

## Step 1: Run a Sync Scan

```
/craft:docs:sync
```

Analyzes recent code changes and classifies what documentation needs updating:

```
Docs Sync Scan
───────────────
Analyzing changes since last doc sync (HEAD~15)...

Changes detected:

[AUTO]   commands/quota.md — new command, no REFCARD row
[AUTO]   commands/git/guard.md — new arguments added
[MANUAL] New feature: /craft:quota pre-flight check
           → needs tutorial in docs/tutorials/
           → needs entry in docs/guide/quota.md
[MANUAL] Expanded: /craft:git:guard skill (explain, profile)
           → tutorial TUTORIAL-guard-suite.md may need updating

Classification:
  AUTO:   2 mechanical updates (REFCARD rows, count bumps)
  MANUAL: 2 items needing content

Run /craft:docs:update to apply AUTO fixes and prompt for MANUAL items.
```

---

## Step 2: Get Verbose Output

```
/craft:docs:sync --verbose
```

Shows every file analyzed, not just the ones with changes.

---

## Step 3: Limit the Commit Range

```
/craft:docs:sync --since HEAD~5
/craft:docs:sync --since 2026-06-01
```

---

## Step 4: JSON Output

```
/craft:docs:sync --json
```

Returns structured classification data for scripting.

---

## Step 5: Headless Mode (CI)

```
/craft:docs:sync --headless
```

No interactive prompts. Exits 1 if any MANUAL items are detected — useful for blocking a CI step until docs are updated.

---

## Step 6: Trigger Update

After reviewing the sync report:

```
/craft:docs:update
```

This runs the full update pipeline using the sync classification to drive which steps to execute.

---

## What's Next

- Run after every PR merge as part of the post-merge pipeline
- Use `--headless` in CI to detect docs drift on the main branch
- See [interactive-docs-update-tutorial.md](interactive-docs-update-tutorial.md) for the full docs update workflow
