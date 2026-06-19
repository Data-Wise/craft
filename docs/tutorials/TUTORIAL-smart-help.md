# Tutorial: smart-help — Context-Aware Help

By the end of this tutorial you will have:

- Used smart-help to get command suggestions based on your current project context
- Searched for commands by topic
- Understood how smart-help differs from the standard hub

**Prerequisites:** craft installed.

---

## Step 1: Run Smart Help (No Arguments)

```
/craft:smart-help
```

Analyzes your current project state and suggests relevant commands:

```
Smart Help — Context Analysis
───────────────────────────────
Detected: git repo, recent CI failure, Python project

Suggested commands for your situation:
  /craft:ci:triage     — You have a recent failing run (3 min ago)
  /craft:ci:watch      — Monitor the current run
  /craft:ci:status     — View CI dashboard across repos

Based on recent activity:
  /craft:docs:check    — docs/ modified 2 hours ago, no check run
  /craft:check         — Last check: 47 commits ago

General:
  /craft:hub           — Browse all 112 commands
  /craft:do            — Smart routing for any task
```

---

## Step 2: Search by Topic

```
/craft:smart-help --topic ci
```

Returns all CI-related commands with descriptions:

```
Commands matching "ci":
  /craft:ci:detect      — Detect project type and CI config
  /craft:ci:generate    — Generate GitHub Actions workflow
  /craft:ci:status      — Cross-repo CI dashboard
  /craft:ci:triage      — Classify CI failures
  /craft:ci:validate    — Validate existing CI workflow
  /craft:ci:watch       — Poll CI run to completion
  /craft:code:ci-local  — Run CI mirror locally
```

---

## Step 3: Topic Suggestions

Try other topic keywords:

```
/craft:smart-help --topic docs
/craft:smart-help --topic git
/craft:smart-help --topic release
/craft:smart-help --topic test
```

---

## Step 4: Compare with Hub

Smart-help ranks by context relevance; hub shows everything organized by category:

```
/craft:hub         # Browse all commands by category
/craft:smart-help  # Get contextually ranked suggestions
```

Use smart-help when you're unsure which command fits your situation. Use hub when you want to explore or find a specific category.

---

## What's Next

- Run `/craft:do <task>` for intelligent command routing based on a natural-language task description
- Use `/craft:hub` to browse all 112 commands by category
- See [smart routing tutorial](smart-routing-tutorial.md) for advanced do command patterns
