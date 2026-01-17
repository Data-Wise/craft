# What's New in Craft: Making Your Workflow Smoother

**Estimated reading time:** 12 minutes
**Last updated:** January 17, 2026
**For:** Craft plugin users (all skill levels)

---

## Table of Contents

1. [What's Changed and Why You'll Love It](#whats-changed-and-why-youll-love-it)
2. [Enhancement #1: Smarter Task Routing](#enhancement-1-smarter-task-routing)
3. [Enhancement #2: Better Error Recovery](#enhancement-2-better-error-recovery)
4. [Enhancement #3: Add New Checks Without Restarting](#enhancement-3-add-new-checks-without-restarting)
5. [Real-World Examples](#real-world-examples)
6. [Try It Yourself](#try-it-yourself)
7. [FAQ](#faq)

---

## What's Changed and Why You'll Love It

Claude Code 2.1.0 brought some powerful new features, and we've integrated three of them into Craft to make your workflow faster and more reliable. Think of these as "quality of life" improvements—you might not notice them until you realize how much smoother everything feels.

### The Three Big Improvements

| Enhancement | What It Does | Why It Matters |
|------------|--------------|----------------|
| **Smart Task Routing** | `/craft:do` now delegates complex tasks to specialized helpers | You get better results for complicated tasks |
| **Better Error Recovery** | `/craft:orchestrate` keeps going even if something fails | One hiccup doesn't derail your whole workflow |
| **Hot-Reload Validators** | `/craft:check` finds new validation rules automatically | Add custom checks without restarting |

Let's break these down into plain English.

---

## Enhancement #1: Smarter Task Routing

### The Big Idea

Remember when you'd ask for directions and someone would just tell you "turn left," but what you really needed was step-by-step instructions with landmarks? That's the difference between the old `/craft:do` and the new one.

**Before:** `/craft:do` was like a smart switchboard—it figured out which Craft command to send you to.
**Now:** `/craft:do` can recognize when a task needs a specialist and delegate to an expert agent.

### What Are Agents?

Think of agents as specialized assistants:

- **Feature Developer** (`feature-dev`): Builds new features from scratch
- **Bug Detective** (`bug-detective`): Hunts down and fixes problems
- **Backend Architect** (`backend-architect`): Designs system architecture
- **Orchestrator** (`orchestrator-v2`): Coordinates multiple specialists for big projects

### How It Works (In Simple Terms)

When you give `/craft:do` a task, it now:

1. **Analyzes complexity** — Is this simple or complicated?
2. **Chooses the best approach:**
   - **Simple tasks** → Routes to a Craft command (like before)
   - **Complex tasks** → Delegates to a specialized agent (new!)

#### Complexity Scoring

Here's how it decides:

```
Score 0-3  → Simple    → Use existing commands
Score 4-7  → Medium    → Delegate to one specialist
Score 8-10 → Complex   → Coordinate multiple specialists
```

**What makes a task complex?**
- Multiple steps (e.g., "add user authentication with OAuth")
- Requires planning (e.g., "refactor the database layer")
- Involves many files (e.g., "prepare for release")

### Forked Context: Your Safety Net

Here's the coolest part: when an agent works on something complex, it gets its own "workspace" (we call it a **forked context**).

**Think of it like this:**
Imagine you're cooking in the kitchen and your friend offers to help by making a salad in a separate prep area. If they accidentally spill something, it doesn't mess up your main cooking area. That's what forked context does—agents work in isolation, so if something goes wrong, your main conversation stays clean.

**Benefits:**
- Agent failures don't break your whole session
- You can have multiple agents working in parallel
- Results come back to you cleanly organized

### Real Example

**Your request:**
`/craft:do "add OAuth authentication for user login"`

**What happens behind the scenes:**

```
┌─────────────────────────────────────────────┐
│ 🔍 Analyzing your task...                   │
├─────────────────────────────────────────────┤
│ Task: "add OAuth authentication"            │
│ Category: Feature Development               │
│ Complexity: 7/10 (Medium-Complex)           │
│                                             │
│ Decision: Delegate to feature-dev agent     │
│ Context: Forked (isolated workspace)        │
│ Estimated time: ~15 minutes                 │
│                                             │
│ Why? This is a multi-step feature that      │
│ requires planning, implementation, and      │
│ testing. A specialist will do it better.    │
└─────────────────────────────────────────────┘
```

The `feature-dev` agent then:
1. Plans the OAuth integration
2. Writes the code
3. Adds tests
4. Brings back a complete solution

You didn't have to break down the task yourself—the system recognized the complexity and got you the right help.

### Before vs. After Comparison

| Task | Old Behavior | New Behavior |
|------|--------------|--------------|
| "fix the login bug" | Routes to `/craft:code:debug` | Delegates to `bug-detective` agent (more thorough) |
| "add user authentication" | Routes to `/craft:arch:plan` | Delegates to `feature-dev` agent (complete implementation) |
| "refactor database layer" | Routes to `/craft:arch:analyze` | Delegates to `backend-architect` agent (architectural design) |
| "prepare release" | Routes to multiple commands | Delegates to `orchestrator-v2` agent (coordinates everything) |

**Bottom line:** You get smarter, more complete solutions for complex tasks.

---

## Enhancement #2: Better Error Recovery

### The Big Idea

Ever been on a group project where one person drops out and everything grinds to a halt? That's how orchestration used to work. Now, the show goes on.

**What is orchestration?**
When you run `/craft:orchestrate`, you're asking multiple agents to work together on a big task. They work in "waves"—some in parallel, some sequentially.

**The old problem:**
If you skipped one agent (maybe you denied permission), the whole workflow would stop.

**The new solution:**
Agents are now resilient. If one fails or you skip it, the others keep going and work with what they have.

### How Resilience Works

**Before (Brittle):**
```
Wave 1: [Agent A] [Agent B]
         ↓ denied    ↓ success
         STOP!
Wave 2: BLOCKED (can't continue)
```

**After (Resilient):**
```
Wave 1: [Agent A]       [Agent B]
         ↓ denied        ↓ success
         ↓ noted         ↓
Wave 2: [Agent C] (uses Agent B's results, notes Agent A missing)
         ↓
         "I used the available results. Agent A was skipped,
          so I'm using general best practices instead."
```

### Real Example

You run:
`/craft:orchestrate "prepare v2.0 release"`

The orchestrator plans three waves:

**Wave 1 (Parallel):**
- **Architecture Agent** → Design system changes
- **Documentation Agent** → Update docs

**Wave 2 (Sequential):**
- **Backend Agent** → Implement changes (depends on architecture)
- **Testing Agent** → Write tests (depends on backend)

**What happens if you skip the Architecture Agent?**

**Old behavior:**
❌ Everything stops. You have to start over.

**New behavior:**
✅ The workflow continues:
1. Documentation Agent completes successfully
2. Backend Agent notes: "Architecture input unavailable, using fallback approach"
3. Backend Agent implements using best practices
4. Testing Agent proceeds with backend's work
5. Final report mentions what was skipped

### Agent Hooks: Behind-the-Scenes Helpers

This resilience is powered by **agent hooks**—little checkpoints that monitor what's happening:

- **PreToolUse hook:** Checks resources before starting (like "Do we have enough memory?")
- **PostToolUse hook:** Logs results after completion (like "Agent B finished in 2m 15s")
- **Stop hook:** Cleans up when everything's done (saves your session state)

Think of hooks as quality control inspectors on an assembly line—they make sure everything runs smoothly.

### Monitoring in Action

When you run `/craft:orchestrate`, you now see real-time status:

```
╭─ /craft:orchestrate "prepare v2.0 release" ─────╮
│                                                 │
│ 📊 Resource Monitor:                            │
│   Active agents: 2/2 (at capacity)             │
│   Queued agents: 1 (wave 2)                    │
│   Context usage: 45%                           │
│                                                 │
│ 🔄 Wave 1 (In Progress):                       │
│   ✓ arch-1 (architecture) - Done (2m 15s)     │
│   ⏳ test-1 (testing) - Running (1m 30s / ~3m) │
│                                                 │
│ 📋 Wave 2 (Queued):                             │
│   ⏸ code-1 (backend) - Awaiting wave 1        │
│                                                 │
╰─────────────────────────────────────────────────╯
```

**Why this matters:**
You can see exactly what's happening, how long things take, and whether to grab coffee while you wait.

---

## Enhancement #3: Add New Checks Without Restarting

### The Big Idea

Imagine your car's dashboard could add new warning lights while you're driving—no need to take it to the shop. That's what hot-reload does for validation checks.

**What is `/craft:check`?**
It's a pre-flight checklist before you commit code or release a version. It runs tests, checks for broken links, validates coverage, etc.

**The old problem:**
If you wanted to add a new validation (like "check for API keys in code"), you'd have to edit code and restart Claude Code.

**The new solution:**
Just drop a new validation file in the right folder. `/craft:check` automatically finds and runs it. No restart needed.

### How Hot-Reload Works

**Validation skills** are small, modular checks stored as markdown files. Each one has:
- A name (e.g., `check:test-coverage`)
- A description
- Code to run the check
- A special flag: `hot_reload: true`

When you run `/craft:check`, it:
1. Scans for all validation skills (in multiple locations)
2. Loads any new ones automatically
3. Runs them in isolated "forked contexts" (remember the kitchen prep analogy?)
4. Reports all results

### Creating Your Own Validator

Let's say you want to ensure your CHANGELOG is always updated. Here's how simple it is:

**Create file:** `~/.craft/validators/changelog-updated.md`

```markdown
---
name: check:changelog-updated
description: Ensure CHANGELOG.md was updated in this release
category: validation
context: fork
hot_reload: true
---

# CHANGELOG Updated Check

Make sure CHANGELOG.md has today's date.

## Implementation

```bash
# Check if CHANGELOG.md contains today's date
TODAY=$(date +%Y-%m-%d)

if grep -q "$TODAY" CHANGELOG.md; then
  echo "✅ PASS: CHANGELOG updated today"
  exit 0
else
  echo "❌ FAIL: CHANGELOG doesn't mention $TODAY"
  exit 1
fi
```
```

**That's it!** Next time you run `/craft:check`, this validator automatically runs—no restart required.

### Where to Put Validators

The system looks in three places (in order):

1. **`.claude-plugin/skills/validation/`** — Plugin's built-in validators
2. **`~/.craft/validators/`** — Your personal custom validators
3. **`.craft/validators/`** — Project-specific validators

### What You See

When you run `/craft:check release`:

```
┌─────────────────────────────────────────────────┐
│ 🔍 /craft:check release                         │
├─────────────────────────────────────────────────┤
│                                                 │
│ Discovered validators: 11 (7 core + 4 custom)   │
│   ℹ Custom validators from: ~/.craft/validators│
│                                                 │
│ 📋 Core Validators:                             │
│   ✓ test-coverage (2.1s) - 87%                 │
│   ✓ broken-links (0.8s) - 0 broken             │
│   ✓ lint-check (1.2s) - All pass               │
│   ✓ type-check (3.4s) - No errors              │
│   ✓ security-scan (4.3s) - No vulnerabilities  │
│   ✓ dependency-check (2.0s) - Up to date       │
│   ✓ license-check (0.5s) - Compatible          │
│                                                 │
│ 🔧 Custom Validators:                           │
│   ✓ api-keys (1.8s) - No secrets [NEW]         │
│   ✓ changelog-updated (0.3s) - Current [NEW]   │
│   ✓ version-bump (0.2s) - Incremented [NEW]    │
│   ✓ pr-template (0.1s) - Exists [NEW]          │
│                                                 │
│ Results: 11/11 passed ✅                         │
│ Total time: 16.7s                               │
│                                                 │
│ 💡 Add your own: ~/.craft/validators/           │
└─────────────────────────────────────────────────┘
```

Notice the **[NEW]** tags? Those validators were added without any code changes or restarts.

---

## Real-World Examples

### Example 1: Building a New Feature

**Your task:** Add a user profile page with photo uploads

**Command:**
`/craft:do "create user profile page with photo upload"`

**What happens:**

1. `/craft:do` analyzes: "This is complex (score: 7/10)—needs UI, backend, file handling, validation"
2. Delegates to `feature-dev` agent in a forked context
3. Agent breaks it down:
   - Design database schema for user profiles
   - Create upload API endpoint
   - Add image validation
   - Build frontend form
   - Write tests
4. Returns complete implementation with all pieces

**Your experience:**
You asked for a feature. You got a complete, tested feature. One command.

---

### Example 2: Preparing a Release

**Your task:** Get v2.0 ready to ship

**Command:**
`/craft:orchestrate "prepare v2.0 release"`

**What happens:**

**Wave 1 (Parallel):**
- Architecture Agent reviews system changes
- Documentation Agent updates README, CHANGELOG, guides

**Wave 2 (Sequential):**
- Backend Agent implements final changes
- Testing Agent runs full test suite

**You skip the Architecture Agent** (you already reviewed it yourself)

**Old behavior:**
Everything stops. You're stuck.

**New behavior:**
- Documentation completes ✅
- Backend continues with note: "Using existing architecture docs"
- Testing proceeds ✅
- Final report: "3/4 agents completed. Architecture review skipped by user."

**Your experience:**
One skip didn't derail the whole release prep. You kept moving forward.

---

### Example 3: Adding a Custom Validation

**Your task:** Make sure no one commits console.log statements to production

**Steps:**

1. Create `~/.craft/validators/no-console-log.md`:

```markdown
---
name: check:no-console-log
description: Ensure no console.log in production code
category: validation
context: fork
hot_reload: true
---

# No Console.log Check

Scan for console.log statements in JavaScript files.

## Implementation

```bash
if grep -r "console\.log" src/; then
  echo "❌ FAIL: Found console.log in src/"
  exit 1
else
  echo "✅ PASS: No console.log found"
  exit 0
fi
```
```

2. That's it! No restart needed.

3. Next `/craft:check` run:

```
🔧 Custom Validators:
  ✓ no-console-log (0.4s) - No console.log [NEW]
```

**Your experience:**
You wanted a new check. You created a file. It works immediately.

---

## Try It Yourself

### Exercise 1: Smart Routing

**Try this:**
`/craft:do "fix the navigation menu bug" --dry-run`

**What to watch for:**
- Complexity score (probably 4-5, medium)
- Which agent it would delegate to (`bug-detective`)
- Why it made that choice

**Compare to:**
`/craft:do "update the README" --dry-run`

**What to watch for:**
- Lower complexity score (probably 1-2, simple)
- Routes to simple command instead of agent

---

### Exercise 2: Resilient Orchestration

**Try this:**
`/craft:orchestrate "update documentation site"`

**During execution:**
- Watch the wave progress
- If prompted for permission, try skipping one agent
- Notice that others continue
- Check the final report for how it handled the skip

---

### Exercise 3: Hot-Reload Validator

**Create this simple validator:**

**File:** `~/.craft/validators/git-status-clean.md`

```markdown
---
name: check:git-clean
description: Ensure no uncommitted changes
category: validation
context: fork
hot_reload: true
---

# Git Status Clean Check

## Implementation

```bash
if [ -z "$(git status --porcelain)" ]; then
  echo "✅ PASS: Working directory clean"
  exit 0
else
  echo "❌ FAIL: Uncommitted changes exist"
  exit 1
fi
```
```

**Then run:**
`/craft:check`

**What to watch for:**
- Your new validator appears automatically
- It runs without any restart
- Result shows in the custom validators section

---

## FAQ

### Q: How do I know when to use `/craft:do` vs a specific command?

**A:** Use `/craft:do` when you want smart routing. It'll figure out the best approach. Use specific commands when you know exactly what you want.

**Rule of thumb:**
- Unsure what command to use? → `/craft:do`
- Know exactly what you need? → Specific command

---

### Q: Will agents make mistakes?

**A:** Agents are powerful, but they're not perfect. That's why they work in **forked contexts**—if something goes wrong, it doesn't break your main session. You can always review their work and ask for changes.

---

### Q: Can I turn off agent delegation?

**A:** Yes! Use the `--no-delegate` flag:
`/craft:do "complex task" --no-delegate`

This forces simple routing, even for complex tasks.

---

### Q: How many validators can I add?

**A:** As many as you want! Each runs in its own forked context, so they don't interfere with each other. Just keep in mind that more validators = longer `/craft:check` runtime.

---

### Q: What if my custom validator has a bug?

**A:** Because validators run in forked contexts, a buggy validator just fails—it won't crash your session. You'll see a failure message, and you can fix the validator file.

---

### Q: Can I share my validators with others?

**A:** Absolutely! Validators are just markdown files. Share them with your team or post them online. Anyone can drop them into `~/.craft/validators/` and use them.

---

### Q: How much faster is the new routing?

**A:** For simple tasks, about the same. For complex tasks, much faster—you get better results in one shot instead of multiple back-and-forth commands.

---

### Q: Will this use more AI resources?

**A:** Agent delegation does use more resources than simple routing, but you get better results. Think of it as "spend a little more to get it right the first time."

Hot-reload and resilience actually save resources by avoiding restarts and failed workflows.

---

## What This Means for You

These three enhancements work together to make Craft smarter, more resilient, and more customizable:

1. **Smarter routing** → Better results for complex tasks
2. **Better error recovery** → Fewer interruptions to your workflow
3. **Hot-reload validators** → Customize checks without downtime

**The big picture:**
You spend less time managing tools and more time building great software.

---

## Learn More

- **Craft Documentation:** [https://data-wise.github.io/craft/](https://data-wise.github.io/craft/)
- **Claude Code 2.1.0 Release Notes:** Check the official changelog for all new features
- **Technical Proposal:** `docs/brainstorm/PROPOSAL-craft-enhancements-2026-01-17.md` (if you want the nitty-gritty details)

---

**Questions or feedback?** Open an issue on the [Craft GitHub repository](https://github.com/Data-Wise/craft).

**Happy crafting!** 🚀
