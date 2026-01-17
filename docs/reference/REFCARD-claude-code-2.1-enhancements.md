# Claude Code 2.1.0 Enhancements - Quick Reference Card

**Version:** 2.1.0 | **Last Updated:** 2026-01-17 | **Print-Friendly** ✅

---

## 🎯 Three Key Enhancements

| Enhancement | What It Does | Your Benefit |
|------------|--------------|--------------|
| **Smart Routing** | `/craft:do` delegates to expert agents | Complex tasks handled automatically |
| **Resilient Orchestration** | `/craft:orchestrate` continues despite failures | Work doesn't stop if one step fails |
| **Hot-Reload Validators** | `/craft:check` detects new validators instantly | Add checks without restarting |

---

## 🚀 Enhancement 1: Smart Routing with Agents

### When to Use

```bash
# Complex tasks → Let agents handle it
/craft:do "add user authentication with OAuth"
/craft:do "refactor database layer for performance"
/craft:do "fix memory leak in API server"
```

### How It Works

```
Your Task → Complexity Analysis → Route Decision
                                   ├─ Simple (0-3) → Commands
                                   ├─ Medium (4-7) → Single Agent
                                   └─ Complex (8-10) → Orchestrator
```

### Agent Types

| Task Type | Agent | Example Task |
|-----------|-------|--------------|
| Feature | feature-dev | "add user notifications" |
| Architecture | backend-architect | "design API architecture" |
| Bug Fix | bug-detective | "fix login redirect issue" |
| Multi-step | orchestrator-v2 | "prepare v2.0 release" |

### Command Format

```bash
# See routing plan without executing
/craft:do "your task" --dry-run

# Execute with agent delegation
/craft:do "your task"
```

---

## 🔄 Enhancement 2: Resilient Orchestration

### When to Use

```bash
# Multi-step workflows with dependencies
/craft:orchestrate "prepare release" release
/craft:orchestrate "implement auth system" default
/craft:orchestrate "refactor codebase" optimize
```

### How It Works (Before vs After)

**Before (Brittle):**
```
Wave 1: [Agent A] [Agent B]
         ↓ denied    ↓ success
Wave 2: ❌ BLOCKED
```

**After (Resilient):**
```
Wave 1: [Agent A] [Agent B]
         ↓ denied    ↓ success
         ↓ noted
Wave 2: ✓ CONTINUES (uses Agent B results + fallback)
```

### Execution Modes

| Mode | Time | Use Case |
|------|------|----------|
| `default` | < 10s | Quick tasks |
| `debug` | < 120s | Troubleshooting |
| `optimize` | < 180s | Performance critical |
| `release` | < 300s | Thorough validation |

---

## ⚡ Enhancement 3: Hot-Reload Validators

### When to Use

```bash
# Check before commit/release
/craft:check               # Default mode
/craft:check release       # Thorough validation
/craft:check --for commit  # Pre-commit checks
```

### Add Custom Validators (No Restart!)

**Step 1:** Create validator file

```bash
# Create in: ~/.craft/validators/my-check.md
---
name: check:my-check
description: My custom validation
hot_reload: true
context: fork
---

# Your validation logic here
```

**Step 2:** Run check

```bash
/craft:check  # Auto-discovers new validator!
```

### Validator Locations

| Location | Purpose | Example |
|----------|---------|---------|
| `.claude-plugin/skills/validation/` | Plugin validators | Core checks |
| `~/.craft/validators/` | User custom | Your personal checks |
| `.craft/validators/` | Project-specific | Team standards |

---

## 📊 Quick Decision Flowchart

```
Need to do a task?
        │
        ├─ Simple command? → Run directly (/craft:code:lint)
        │
        ├─ Complex task? → /craft:do "task description"
        │                   ↓
        │                   Auto-routes to agent or orchestrator
        │
        ├─ Multi-step workflow? → /craft:orchestrate "workflow" mode
        │                          ↓
        │                          Handles dependencies & failures
        │
        └─ Validate code? → /craft:check mode
                            ↓
                            Runs all validators (including custom)
```

---

## 🎓 Common Scenarios

### Scenario 1: Adding a Feature

```bash
# Old Way (Manual)
/craft:arch:plan
# ... read output ...
/craft:code:test-gen
# ... review tests ...
/craft:git:branch feature/my-feature
# ... switch branch ...

# New Way (Automated)
/craft:do "add user profile feature"
# ✓ Agent handles architecture, tests, branch creation
```

### Scenario 2: Release Preparation

```bash
# Old Way (Stops on First Failure)
/craft:orchestrate "prepare release" release
# → Security scan fails
# → ❌ Everything stops

# New Way (Continues with Fallback)
/craft:orchestrate "prepare release" release
# → Security scan fails (user skips)
# → ✓ Tests continue
# → ✓ Build continues
# → ⚠ Note: Manual security review needed
```

### Scenario 3: Adding Quality Checks

```bash
# Old Way (Requires Code Change + Restart)
1. Edit check.md file
2. Add new validation logic
3. Restart Claude Code
4. Test

# New Way (Drop File, Instant Use)
1. Create ~/.craft/validators/api-keys.md
2. Run /craft:check
3. ✓ New validator auto-discovered!
```

---

## 🔧 Troubleshooting

### Agent Not Delegating

```bash
# Check task complexity
/craft:do "your task" --dry-run

# If too simple, be more specific:
/craft:do "design and implement OAuth2 authentication with JWT"
```

### Orchestration Stuck

```bash
# Check agent status
cat .craft/logs/orchestration.log

# Review last session
cat .craft/cache/last-orchestration.json
```

### Validator Not Loading

```bash
# Check file location
ls ~/.craft/validators/

# Verify frontmatter
head -n 10 ~/.craft/validators/your-validator.md

# Must include:
# - hot_reload: true
# - context: fork
```

---

## 📝 Cheat Sheet Commands

### Smart Routing

```bash
/craft:do "task description"              # Auto-route
/craft:do "task description" --dry-run    # Preview plan
```

### Orchestration

```bash
/craft:orchestrate "task" default    # Quick mode
/craft:orchestrate "task" release    # Thorough mode
```

### Validation

```bash
/craft:check                    # Default checks
/craft:check release           # All checks
/craft:check --for commit      # Pre-commit
```

---

## 🎯 Quick Wins (Try These First)

### 1. Test Smart Routing (2 minutes)

```bash
/craft:do "add a health check endpoint to the API" --dry-run
# Watch it analyze complexity and suggest agent
```

### 2. Add Custom Validator (5 minutes)

```bash
# Create ~/.craft/validators/changelog-check.md
# Run /craft:check
# See it auto-discovered!
```

### 3. Test Resilient Orchestration (10 minutes)

```bash
/craft:orchestrate "analyze codebase" default
# Skip one of the agent prompts
# Watch it continue with other agents
```

---

## 💡 Pro Tips

| Tip | Benefit |
|-----|---------|
| Use `--dry-run` first | Preview before executing |
| Start simple tasks manually | Save agents for complex work |
| Create project validators | Enforce team standards |
| Check logs after orchestration | Debug agent issues |
| Use `release` mode before merging | Catch issues early |

---

## 📚 Related Documentation

- Full Tutorial: `docs/tutorials/TUTORIAL-claude-code-2.1-enhancements.md`
- Technical Proposal: `docs/brainstorm/PROPOSAL-craft-enhancements-2026-01-17.md`
- Command Reference: `commands/do.md`, `commands/orchestrate.md`, `commands/check.md`

---

## 🆘 Need Help?

| Issue | Solution |
|-------|----------|
| Agent not working | Check `--dry-run` output for routing |
| Orchestration failed | Review `.craft/logs/orchestration.log` |
| Validator not found | Verify file location and frontmatter |
| Task too slow | Use simpler task description |

---

**Remember:** These enhancements make your workflow smarter, more resilient, and more customizable. Start with the Quick Wins above, then gradually explore more advanced features!

---

**Print This Card** • **Keep It Handy** • **Share With Your Team**
