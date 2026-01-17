# /workflow:brainstorm

> **ADHD-friendly brainstorming with smart detection, time budgets, and spec capture for implementation.**

---

## Synopsis

```bash
/brainstorm [depth] [focus] [action] "topic"
```

**Quick examples:**
```bash
# Minimal
/brainstorm "auth"              # Default everything

# With focus
/brainstorm feat "auth"         # Feature focus
/brainstorm f "auth"            # Same (single letter)

# With action
/brainstorm save "auth"         # Save as spec
/brainstorm s "auth"            # Same (single letter)

# Combined
/brainstorm d f s "auth"        # Deep + feature + spec (power user mode)
```

---

## Description

Enhanced brainstorming with smart mode detection, time budgets, agent delegation, and spec capture for implementation. Designed to be ADHD-friendly with escape hatches at every step.

**Features:**
- **Smart detection** - Auto-detects topic from context
- **Time budgets** - Guaranteed completion times
- **Three-layer arguments** - Depth + Focus + Action
- **Spec capture** - Save brainstorms as implementation specs

---

## Arguments

### Depth Layer

| Full | Short | Single | Time | Description |
|------|-------|--------|------|-------------|
| (default) | - | - | < 5 min | Balanced, 2 questions + "ask more?" |
| quick | quick | q | < 1 min | Fast, 0 questions + "ask more?" |
| deep | deep | d | < 10 min | Expert questions (8), no agents |
| max | max | m | < 30 min | Expert questions + 2 agents |

### Focus Layer

| Full | Short | Single | What it brainstorms |
|------|-------|--------|---------------------|
| (auto) | - | - | Auto-detect from context |
| feature | feat | f | User stories, MVP scope, acceptance criteria |
| architecture | arch | a | System design, scalability, component diagrams |
| ux | ux | x | UI/UX wireframes, accessibility, user flows |
| api | api | b | API endpoints, database schema, auth patterns |
| ui | ui | u | Component tree, state management, performance |
| ops | ops | o | CI/CD pipelines, deployment, infrastructure |

### Action Layer

| Full | Short | Single | What it does |
|------|-------|--------|--------------|
| (none) | - | - | Output BRAINSTORM.md only |
| save | save | s | Output SPEC.md (for implementation) |

---

## Time Budget Guarantees

| Depth | Time Budget | Questions | Agents | Output |
|-------|-------------|-----------|--------|--------|
| **quick (q)** | < 60s | 0 + "ask more?" | None | 5-7 ideas, quick wins |
| **default** | < 300s | 2 + "ask more?" | None | Comprehensive with options |
| **deep (d)** | < 600s | 8 + "ask more?" | None | Expert-level analysis |
| **max (m)** | < 1800s | 8 + agent Qs | 2 per focus | Deep analysis with synthesis |

---

## Examples

### Quick Brainstorm

```bash
/brainstorm q "notification system"
```

Generates 5-7 ideas in under 60 seconds.

### Feature Planning with Spec

```bash
/brainstorm f s "user authentication"
```

Runs feature-focused brainstorm and captures as spec:

```
╭─ 🧠 BRAINSTORM: User Authentication ─────────────────╮
│ Mode: feature │ Depth: default │ Duration: 3m 24s    │
├──────────────────────────────────────────────────────┤
│                                                      │
│ ## Quick Wins (< 30 min each)                        │
│   ⚡ Basic password login                            │
│   ⚡ Session management                              │
│                                                      │
│ ## Medium Effort (1-2 hours)                         │
│   □ OAuth2 integration                               │
│   □ Password reset flow                              │
│                                                      │
│ ## Long-term (Future sessions)                       │
│   □ Multi-factor authentication                      │
│   □ Social login providers                           │
│                                                      │
├──────────────────────────────────────────────────────┤
│ 📋 SPEC CAPTURED                                     │
│                                                      │
│ Spec: docs/specs/SPEC-user-auth-2026-01-14.md        │
│ Status: draft                                        │
│                                                      │
│ Next: /craft:do "implement user authentication"      │
│       (will use this spec automatically)             │
╰──────────────────────────────────────────────────────╯
```

### Deep Architecture Analysis

```bash
/brainstorm d a "multi-tenant SaaS"
```

8 expert questions, detailed architecture output with Mermaid diagrams.

### Maximum Depth with Agents

```bash
/brainstorm m a s "event-driven microservices"
```

Launches backend-architect and database-architect agents for comprehensive analysis.

---

## "Ask More?" Feature

After base questions complete, you get an escape hatch:

```
AskUserQuestion:
  "Need more detail before brainstorming?"

  ○ No - Start brainstorming (Recommended)
  ○ Yes - 2 more questions
  ○ Yes - Switch to deep (8 questions)
  ○ Yes - Switch to max (8 + agents)
```

**ADHD-friendly:** Always offer escape hatch, never feel trapped.

---

## Smart Context Detection

When no topic provided, auto-detects from:

| Source | What to look for | Priority |
|--------|------------------|----------|
| **Conversation** | Topics discussed, problems mentioned | High |
| **Git branch** | Branch name (e.g., `feature/oauth-login`) | Medium |
| **Recent commits** | Commit messages from last 24h | Medium |
| **Project .STATUS** | Current task, next steps | High |

---

## Spec Capture

When using `save` action, generates comprehensive spec:

**Sections included:**
- Overview, User Stories (primary + secondary)
- Technical Requirements (architecture, API, data models)
- UI/UX Specifications (flows, wireframes, accessibility)
- Open Questions, Review Checklist
- Implementation Notes, History

**Integration with `/craft:do`:**
```bash
# After brainstorm with spec
/craft:do "implement user authentication"
# → Automatically finds and uses SPEC-user-auth-*.md
```

---

## Agent Delegation (Max Mode)

When depth is `max`, launches relevant agents:

| Focus | Agents Launched |
|-------|-----------------|
| feature | product-strategist |
| architecture | backend-architect, database-architect |
| ux | ux-ui-designer |
| api | backend-architect, security-specialist |
| ui | frontend-specialist, performance-engineer |
| ops | devops-engineer |

---

## Output Format

**Terminal (default):**
```
┌─────────────────────────────────────────────────────────────┐
│ 🧠 BRAINSTORM: [Topic]                                      │
│ Mode: [mode] │ Depth: [depth] │ Duration: [time]            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ## Quick Wins (< 30 min each)                               │
│   ⚡ [Action 1] - [Benefit]                                  │
│                                                             │
│ ## Medium Effort (1-2 hours)                                │
│   □ [Task with clear outcome]                               │
│                                                             │
│ ## Long-term (Future sessions)                              │
│   □ [Strategic item]                                        │
│                                                             │
│ ## Recommended Path                                         │
│   → [Clear recommendation with reasoning]                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**JSON:** `--format json`
**Markdown:** `--format markdown`

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No context detected | Provide topic explicitly: `/brainstorm "topic"` |
| Agents timing out | Use `deep` instead of `max` mode |
| Spec not saved | Use `save` action: `/brainstorm s "topic"` |
| Wrong focus | Specify focus: `/brainstorm arch "topic"` |

---

## Quick Reference

| What you want | Command |
|---------------|---------|
| Quick ideas | `/brainstorm q "topic"` |
| Feature planning | `/brainstorm f "topic"` |
| Architecture design | `/brainstorm a "topic"` |
| Save as spec | `/brainstorm s "topic"` |
| Full power | `/brainstorm d f s "topic"` |

---

## See Also

- **Smart routing:** `/craft:do` - Uses specs from brainstorming
- **Spec review:** `/spec:review` - Review and approve specs
- **Focus work:** `/workflow:focus` - Start focused work session
- **Next step:** `/workflow:next` - Get next recommended action
