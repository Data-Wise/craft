# Workflow Plugin - Installation Guide for DT

**Version:** 0.1.0
**Date:** 2025-12-23

> **Personalized installation and setup for DT's development workflow**

---

## 🚀 Quick Install (Homebrew - Recommended)

Once published to your Homebrew tap:

```bash
# Install from your tap
brew install data-wise/tap/workflow

# Restart Claude Code
# Plugin will be auto-installed to ~/.claude/plugins/workflow
```

---

## 📦 Manual Install (Development)

If you want to use the dev version before Homebrew publication:

### Option 1: Symlink (Recommended for Development)

```bash
# Create symlink from your clone to Claude plugins
cd ~/.claude/plugins
ln -s ~/projects/dev-tools/claude-plugins/workflow workflow

# Restart Claude Code
```

**Benefit:** Changes in `~/projects/dev-tools/claude-plugins/workflow` immediately reflect in Claude Code.

### Option 2: Copy (Stable)

```bash
# Copy plugin to Claude plugins directory
cd ~/.claude/plugins
cp -r ~/projects/dev-tools/claude-plugins/workflow .

# Restart Claude Code
```

**Benefit:** Stable, won't change when you update the source repository.

---

## ✅ Verify Installation

### 1. Check Plugin Files

```bash
ls ~/.claude/plugins/workflow

# Should show:
# .claude-plugin/
# commands/
# skills/
# agents/
# docs/
# tests/
# README.md
# package.json
# LICENSE
```

### 2. Run Tests

```bash
cd ~/.claude/plugins/workflow
bash tests/test-plugin-structure.sh

# Should show:
# ✅ All tests passed!
# • 1 command (brainstorm)
# • 3 skills (backend, frontend, devops)
# • 1 agent (orchestrator)
```

### 3. Restart Claude Code

```bash
# If running in iTerm2:
# Cmd+Q to quit Claude Code
# Relaunch from terminal or Applications
```

---

## 🧪 Test Auto-Activation

Open Claude Code and try these commands:

### Test 1: Backend Designer Skill

```
You: "I need to design a REST API for user management with CRUD operations"

Expected: backend-designer skill should activate and provide:
- RESTful API pattern recommendation
- Endpoint structure (/users, /users/:id)
- Authentication suggestion
- Database schema guidance
```

### Test 2: Frontend Designer Skill

```
You: "How should I structure my React dashboard components for the admin panel?"

Expected: frontend-designer skill should activate and provide:
- Component composition pattern
- Layout recommendations (card-based for scannability)
- Accessibility considerations
- State management approach
```

### Test 3: DevOps Helper Skill

```
You: "I need to deploy my Next.js app with a PostgreSQL database"

Expected: devops-helper skill should activate and provide:
- Platform recommendation (Vercel + Supabase)
- Cost estimate ($0 for MVP → ~$25/mo at scale)
- CI/CD setup (GitHub Actions)
- Environment variables strategy
```

---

## 💡 Test /brainstorm Command

### Quick Brainstorm (Fast)

```bash
/brainstorm quick feature user notifications
```

**Expected output (in ~2 min):**
- 5-7 notification ideas
- Quick Wins (< 30 min) highlighted with ⚡
- Medium Effort (1-2 hours)
- Long-term (Future sessions)
- Recommended path
- Next steps (numbered)
- Saved to: `BRAINSTORM-user-notifications-2025-12-23.md`

### Thorough Brainstorm (Deep Analysis)

```bash
/brainstorm thorough user authentication with OAuth
```

**Expected output (in ~3-5 min):**
- Initial ideas generated immediately
- Status updates as agents work:
  ```
  🚀 Launching analysis...
     ✓ backend-architect (background)
     ✓ security-specialist (background)
     ✓ ux-ui-designer (background)
     ✓ devops-engineer (background)

  ⏳ Progress:
     ✓ security-specialist completed (35s)
     ✓ devops-engineer completed (42s)
     ✓ ux-ui-designer completed (58s)
     ✓ backend-architect completed (1m 24s)

  ✅ Analysis complete! Synthesizing results...
  ```
- Comprehensive plan with:
  - Backend OAuth setup (passport.js, flow selection)
  - Frontend login UI components
  - DevOps secrets configuration
  - Security checklist
  - Next steps (numbered, concrete)
- Saved to: `BRAINSTORM-user-authentication-oauth-2025-12-23.md`

---

## 🔧 Integration with Your Workflow

### Works With Your Existing Commands

The workflow plugin complements your existing workflow commands:

#### `/recap` Integration
```
You: /recap

Response includes recent brainstorms:
- BRAINSTORM-user-auth-2025-12-23.md (created today)
- Design decisions captured
- Patterns applied
```

#### `/next` Integration
```
You: /next

Skills auto-activate based on next task:
- If next task involves API → backend-designer activates
- If next task involves UI → frontend-designer activates
- If next task involves deploy → devops-helper activates
```

#### `/done` Integration (Future)
```
You: /done

Future enhancement:
- Captures design decisions made during session
- References patterns used from pattern library
- Updates project CLAUDE.md with architecture notes
```

### Workflow Pattern Suggestions

**For R Package Development:**
```
1. Mention "R package structure" or "S3 methods"
   → Auto-activates general development guidance

2. /brainstorm architecture R package with C++ backend
   → Comprehensive plan for Rcpp integration
```

**For Quarto Projects:**
```
1. Mention "Quarto extension" or "Lua filter"
   → Skills provide architecture guidance

2. /brainstorm feature interactive dashboard in Quarto
   → Plan for Observable JS or Shiny integration
```

**For Teaching Materials:**
```
1. Mention "course website" or "assignment grading"
   → frontend-designer activates for UX

2. /brainstorm devops deploying course site to GitHub Pages
   → Complete deployment setup
```

---

## 📁 File Organization

Brainstorm files will be saved in your current working directory:

```bash
# Example locations:
~/projects/r-packages/active/your-package/BRAINSTORM-feature-name-2025-12-23.md
~/projects/teaching/stat-440/BRAINSTORM-interactive-demo-2025-12-23.md
~/projects/dev-tools/workflow/BRAINSTORM-plugin-enhancement-2025-12-23.md
```

**Fallback:** If current directory is not writable, files save to `~/brainstorms/`

### Recommended .gitignore

Add to your project `.gitignore`:

```
# Brainstorm files (keep in repo as design docs)
# BRAINSTORM-*.md

# Or exclude if you prefer:
BRAINSTORM-*.md
```

**Recommendation:** Keep brainstorms in repo. They document design decisions and architecture choices.

---

## 🎯 Your Use Cases

### 1. R Package Development

**Scenario:** Adding new statistical method to mediation package

```
You: "I need to add a new three-way decomposition method to rmediation"

→ backend-designer activates:
  - Suggests S3 method structure
  - Function naming conventions
  - Documentation requirements
  - Testing strategy

You: /brainstorm architecture three-way decomposition with bootstrap

→ Orchestrator launches:
  - backend-architect (method structure)
  - testing-specialist (simulation tests)
  - documentation-writer (Rd file template)

→ Output:
  - Function signatures
  - Bootstrap algorithm structure
  - Test cases (unit + integration)
  - Documentation template
  - Next steps (implement core → tests → docs → examples)
```

### 2. Teaching Course Website

**Scenario:** Redesigning STAT 440 course website

```
You: "I want to improve the UX of my course website for ADHD students"

→ frontend-designer activates:
  - ADHD-friendly design patterns (your specialty!)
  - Navigation simplification
  - Visual hierarchy improvements
  - Accessibility checklist

You: /brainstorm design course website with weekly modules

→ Orchestrator launches:
  - ux-ui-designer (layout, navigation)
  - frontend-specialist (Quarto customization)

→ Output:
  - Weekly module card layout
  - Color-coded assignment types
  - Quick-access navigation
  - Mobile-first responsive design
  - Next steps (Quarto theme → CSS customization → deploy)
```

### 3. Development Tools

**Scenario:** Enhancing aiterm CLI tool

```
You: "I want to add auto-context detection to aiterm for R projects"

→ backend-designer activates:
  - Pattern matching strategy (DESCRIPTION file, .Rbuildignore)
  - Configuration file structure
  - Plugin system design

You: /brainstorm feature context detection for R, Python, Node

→ Comprehensive plan:
  - File-based detection patterns
  - Priority ordering (R > Python > Node)
  - iTerm2 integration
  - Testing strategy (15+ test cases)
  - Next steps
```

---

## 🔮 Advanced Usage

### Custom Mode Detection

The `/brainstorm` command auto-detects mode based on your conversation. You can influence detection:

**Backend-focused:**
```
Keywords: API, database, schema, auth, authentication, backend
→ Triggers backend mode
```

**Frontend-focused:**
```
Keywords: UI, UX, component, layout, design, accessibility
→ Triggers design mode
```

**DevOps-focused:**
```
Keywords: deploy, deployment, CI/CD, Docker, hosting, infrastructure
→ Triggers devops mode
```

**Architecture-focused:**
```
Keywords: architecture, system design, scalability, microservices
→ Triggers architecture mode
```

### Force Specific Mode

```bash
# Override auto-detection
/brainstorm backend [topic]      # Force backend analysis
/brainstorm frontend [topic]     # Force frontend analysis
/brainstorm devops [topic]       # Force devops analysis
/brainstorm architecture [topic] # Force architecture analysis
```

### Speed vs Depth Trade-off

```bash
# Fast ideation (2 min, no agents)
/brainstorm quick [topic]

# Deep analysis (3-5 min, 2-4 agents in parallel)
/brainstorm thorough [topic]

# Let plugin decide based on context
/brainstorm [topic]
```

---

## 🐛 Troubleshooting

### Skills Not Auto-Activating

**Check 1:** Plugin installed?
```bash
ls ~/.claude/plugins/workflow/skills/design
# Should list: backend-designer.md, frontend-designer.md, devops-helper.md
```

**Check 2:** Restart Claude Code

**Check 3:** Use explicit keywords
```
Try: "I need to design an API" (should trigger backend-designer)
Not: "I need auth" (might be too vague)
```

### Agent Delegation Not Working

**Check 1:** experienced-engineer plugin installed?
```bash
ls ~/.claude/plugins/experienced-engineer/agents
# Should list: backend-architect, ux-ui-designer, devops-engineer, etc.
```

**Check 2:** Using quick mode?
```bash
# Quick mode skips agents (by design)
/brainstorm quick [topic]

# Use thorough for agents
/brainstorm thorough [topic]
```

**Check 3:** Agent timeout?
- Agents have 5-minute timeout
- Partial results provided if some agents timeout
- Check internet connection

### Brainstorm Files Not Saving

**Check 1:** Write permissions
```bash
# Test current directory
touch test-write && rm test-write

# If fails, files save to ~/brainstorms/
```

**Check 2:** Fallback directory exists
```bash
mkdir -p ~/brainstorms
chmod 755 ~/brainstorms
```

---

## 📊 Expected Performance

### Execution Times (Your Machine)

| Operation | Expected Time | Notes |
|-----------|---------------|-------|
| **Skill activation** | Instant | No delay, immediate guidance |
| **Quick brainstorm** | ~2 min | 5-7 ideas, no agents |
| **Thorough (1 agent)** | ~2 min | Single specialized agent |
| **Thorough (4 agents)** | ~2-3 min | Parallel execution |

**Note:** First agent invocation might be slower (Claude Code initialization). Subsequent runs faster.

### File Sizes

| Output Type | Typical Size | Lines |
|------------|--------------|-------|
| **Quick brainstorm** | ~2-5 KB | 100-150 lines |
| **Thorough brainstorm** | ~8-15 KB | 300-500 lines |
| **Architecture brainstorm** | ~15-25 KB | 500-800 lines |

---

## 🎓 Learning Path

### Week 1: Get Familiar
1. Day 1: Install + verify (20 min)
2. Day 2: Test auto-activation (30 min)
3. Day 3: Try 3 quick brainstorms (1 hour)
4. Day 4: Try 1 thorough brainstorm (30 min)
5. Day 5: Review generated files (30 min)

### Week 2: Integrate
1. Use for actual R package design decisions
2. Use for course website improvements
3. Use for development tool enhancements
4. Review which patterns were most helpful

### Week 3: Optimize
1. Note which modes you use most
2. Customize workflow based on patterns
3. Share feedback (what worked, what didn't)

---

## 🔗 Quick Reference

**Installation:**
```bash
brew install data-wise/tap/workflow  # Once published
# OR
ln -s ~/projects/dev-tools/claude-plugins/workflow ~/.claude/plugins/workflow
```

**Verify:**
```bash
bash ~/.claude/plugins/workflow/tests/test-plugin-structure.sh
```

**Test:**
```
Mention "API design" → backend-designer should activate
/brainstorm quick feature notifications
/brainstorm thorough user auth with OAuth
```

**Docs:**
- Full guide: `~/.claude/plugins/workflow/README.md`
- Quick start: `~/.claude/plugins/workflow/docs/QUICK-START.md`
- Reference: `~/.claude/plugins/workflow/docs/REFCARD.md`
- Patterns: `~/.claude/plugins/workflow/PATTERN-LIBRARY.md`

---

**Ready to ship! Install, test, and start using in your real workflow.** 🚀
