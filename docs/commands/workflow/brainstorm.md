# /workflow:brainstorm

> **ADHD-friendly brainstorming with smart detection, time budgets, and spec capture for implementation. v2.4.0 adds question control with colon notation and categories!**

---

## Synopsis

```bash
/brainstorm [depth:count] [focus] [action] [-C|--categories "cat1,cat2"] "topic"
```

**Quick examples (v2.4.0):**
```bash
# Minimal
/brainstorm "auth"              # Default everything

# Colon notation for custom question counts
/brainstorm d:5 "auth"          # Deep with exactly 5 questions
/brainstorm m:12 "api"          # Max with 12 questions
/brainstorm q:0 "quick"         # Quick with 0 questions (straight to brainstorming)

# Categories flag to filter question types
/brainstorm d:5 "auth" -C req,tech          # 5 questions from requirements + technical
/brainstorm m:10 f "api" --categories req,usr,tech,exist

# Power user - full control
/brainstorm d:15 f s -C req,tech,success "auth"   # 15 questions, feature, spec, filtered categories
```

---

## Description

Enhanced brainstorming with smart mode detection, time budgets, agent delegation, and spec capture for implementation. Designed to be ADHD-friendly with escape hatches at every step.

**v2.4.0 Features:**
- **Colon notation** - `d:5`, `m:12`, `q:3` for custom question counts
- **Categories flag** - Filter questions by type (`-C req,tech,success`)
- **Unlimited questions** - Milestone prompts every 8 questions
- **8-category question bank** - 16 questions total

**Features:**
- **Smart detection** - Auto-detects topic from context
- **Time budgets** - Guaranteed completion times
- **Three-layer arguments** - Depth + Focus + Action
- **Spec capture** - Save brainstorms as implementation specs
- **Question control** - Custom counts and categories (v2.4.0)

---

## Arguments

### Depth Layer (v2.4.0 - Colon Notation)

| Full | Short | Count | Time | Description |
|------|-------|-------|------|-------------|
| (default) | - | 2 | < 5 min | Balanced, 2 questions + "ask more?" |
| quick:N | q:N | N | < 1 min | Quick with N questions |
| deep:N | d:N | N | < 10 min | Deep with N questions |
| max:N | m:N | N | < 30 min | Max with N questions + agents |
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

### Categories Layer (v2.4.0)

Filter which question categories to ask. Defaults to focus-appropriate categories if omitted.

| Flag | Short | Description |
|------|-------|-------------|
| --categories | -C | Comma-separated category list |

**Category Shortcuts:**

| Short | Full | Description |
|-------|------|-------------|
| req | requirements | Key requirements, constraints |
| usr | users | Primary users, problems solved |
| scp | scope | In/out of scope, MVP |
| tech | technical | Tech stack, integrations |
| time | timeline | Deadlines, milestones |
| risk | risks | Potential risks, edge cases |
| exist | existing | Reusable code, dependencies |
| ok | success | Success metrics, acceptance criteria |
| all | all | All 8 categories |

---

## Time Budget Guarantees (v2.4.0)

| Depth | Time Budget | Questions | Agents | Output |
|-------|-------------|-----------|--------|--------|
| **quick (q)** | < 60s | 0 + "ask more?" | None | 5-7 ideas, quick wins |
| **quick:N (q:N)** | < 60s | N + milestones | None | N questions with continuation prompts |
| **default** | < 300s | 2 + "ask more?" | None | Comprehensive with options |
| **deep (d)** | < 600s | 8 + "ask more?" | None | Expert-level analysis |
| **deep:N (d:N)** | < 600s | N + milestones | None | N questions with continuation prompts |
| **max (m)** | < 1800s | 8 + agent Qs | 2 per focus | Deep analysis with synthesis |
| **max:N (m:N)** | < 1800s | N + agent Qs + milestones | 2 per focus | N questions with agents and prompts |

**Milestone Behavior:**
- Questions asked in batches of 8
- Continuation prompt after each batch
- User can: proceed, add 4, add 8, or go unlimited
- "Keep going" mode prompts every 4 questions

---

## Examples (v2.4.0)

### Quick Brainstorm

```bash
/brainstorm q "notification system"
```

Generates 5-7 ideas in under 60 seconds.

### Colon Notation (v2.4.0)

```bash
/brainstorm d:5 "auth"              # Deep with exactly 5 questions
/brainstorm m:12 "api"              # Max with 12 questions
/brainstorm q:0 "quick"             # Quick with 0 questions (straight to brainstorming)
```

### Categories Flag (v2.4.0)

```bash
/brainstorm d:5 "auth" -C req,tech              # 5 questions from requirements + technical
/brainstorm m:10 f "api" --categories req,usr,tech,exist
/brainstorm d:4 "caching" -C tech,risk
```

### Unlimited Questions with Milestones (v2.4.0)

```bash
/brainstorm d:20 "microservices"
```

Flow: 8 questions → milestone → 8 more → milestone → 4 more → proceed

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

### Power User (v2.4.0)

```bash
/brainstorm d:15 f s -C req,tech,success "payment api"
```

Deep mode with 15 questions, feature focus, spec capture, filtered categories.

---

## Question Bank (v2.4.0)

Comprehensive 8-category question bank with 2 questions per category.

### Categories

| Category | Focus | Questions |
|----------|-------|-----------|
| **requirements** | Key requirements, constraints | 2 |
| **users** | Primary users, problems solved | 2 |
| **scope** | In/out of scope, MVP | 2 |
| **technical** | Tech stack, integrations | 2 |
| **timeline** | Deadlines, milestones | 2 |
| **risks** | Potential risks, edge cases | 2 |
| **existing** | Reusable code, dependencies | 2 |
| **success** | Success metrics, acceptance criteria | 2 |

### Default Categories by Focus

| Focus | Default Categories |
|-------|-------------------|
| `feat` | requirements, users, scope, success |
| `arch` | technical, risks, existing, scope |
| `api` | technical, requirements, success |
| `ux` | users, scope, success |
| `ops` | technical, risks, timeline |
| `auto` | requirements, users, technical, success |

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
