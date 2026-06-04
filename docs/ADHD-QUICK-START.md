<!-- markdownlint-disable MD046 MD051 -->
# ADHD Quick Start

⏱️ **Under 2 minutes** • 🟢 Beginner • ✓ Fastest path to success

> **TL;DR** (30 seconds)
>
> - **What:** Ultra-fast guide to craft with zero cognitive load - install, verify, and run in under 2 minutes
> - **Why:** ADHD-optimized workflow with time-boxed steps, clear wins, and smart defaults
> - **How:** `brew install data-wise/tap/craft` or `claude plugin add github:Data-Wise/craft` → `/craft:hub` → `/craft:do "task"`
> - **Next:** Try the [5-minute exploration](#next-5-minutes) or jump to [docs automation](commands/docs.md)

## ⏱️ First 30 Seconds

!!! abstract "Progress: 1/3 - First Win"
    0:00 → 0:30 | Install and verify

**Install and verify:**

```bash
# Pick ONE install method:
brew tap data-wise/tap && brew install craft  # Homebrew (macOS)
claude plugin add github:Data-Wise/craft      # GitHub marketplace

# Then verify:
/craft:hub                                    # Verify 109 commands are available
```

**Expected:** You'll see a categorized list of all craft commands.

!!! success "First Win: You're In!"
    If you see the command listing, you're all set! craft is installed and working. Everything else is just trying commands.

## ⏱️ Next 90 Seconds

!!! abstract "Progress: 2/3 - Core Commands"
    0:30 → 2:00 | Try essential commands

**Try these three essential commands:**

```bash
/craft:do "add validation to my forms"     # AI routes task automatically
/craft:check                                # Pre-flight check before committing
/craft:help testing                         # Get context-aware testing help
```

## ⏱️ Next 5 Minutes

!!! abstract "Progress: 3/3 - Deep Dive"
    2:00 → 7:00 | Explore by category

**Explore by category:**

- **Documentation:** `/craft:docs:update` - Smart docs generation
- **Site Creation:** `/craft:site:create --preset adhd-focus` - ADHD-friendly docs site
- **Code Quality:** `/craft:code:lint optimize` - Fast parallel linting
- **Git Workflows:** `/craft:git:worktree add feature-name` - Parallel development

## 🆘 Stuck?

### Quick Diagnostics

```bash
/craft:hub          # See all commands
/craft:help         # Context-specific suggestions
/craft:check        # Validate your setup
```

### Common Questions

| Question | Answer |
|----------|--------|
| Where are my commands? | Run `/craft:hub` to see all 109 commands |
| How do I automate docs? | Use `/craft:docs:update` for smart full cycle |
| Can I create a website? | Yes! `/craft:site:create` with 8 ADHD-friendly presets |
| What's the universal command? | `/craft:do "task"` - AI routes automatically |

### ADHD-Friendly Features

- ✅ **TL;DR boxes** on every major page (30-second summaries)
- ✅ **Time estimates** on all tutorials (know before you start)
- ✅ **Visual hierarchy** with emojis and clear headings
- ✅ **Mode system** for different time constraints (default/debug/optimize/release)
- ✅ **Smart defaults** that just work without configuration

## 🎯 What Makes Craft ADHD-Friendly?

1. **One command does everything:** `/craft:do` routes tasks automatically
2. **Time-boxed modes:** Choose 10s, 2min, 3min, or 5min execution times
3. **Clear status:** Always know what's happening with progress indicators
4. **Resume anywhere:** Orchestrator remembers state if interrupted
5. **Quick wins first:** Most common tasks take < 30 seconds

## 🚀 Next Steps

**Choose your path:**

=== "I want to learn the system"

    Read: [Getting Started Guide](guide/getting-started.md) (10 minutes)

=== "I want to automate docs"

    Try: `/craft:docs:update` then [Docs Commands](commands/docs.md)

=== "I want to create a site"

    Run: `/craft:site:create --preset adhd-focus`

=== "I want advanced features"

    Learn: [Orchestrator Mode](guide/orchestrator.md) (8 minutes)

## 💡 Pro Tips

- Use `--quick` flags to skip prompts: `/craft:site:create --quick`
- Chain workflows with `/craft:orchestrate` for complex tasks
- Use `debug` mode when learning: `/craft:code:lint debug`
- Check before committing: `/craft:check --for commit`

---

**You're ready!** Pick a command from above and start automating. The AI will guide you through the rest.
