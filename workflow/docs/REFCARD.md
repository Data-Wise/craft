# Workflow Plugin - Reference Card

> **Version:** 0.1.0 | **Last Updated:** 2025-12-23

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  WORKFLOW PLUGIN REFERENCE                                         v0.1.0  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  COMMANDS (1)                      │  AUTO-ACTIVATING SKILLS (3)           │
│  ─────────                         │  ─────────────────────────            │
│  /brainstorm [mode] [topic]        │  • backend-designer                   │
│    Enhanced brainstorm with        │    Auto-activates: API design,        │
│    smart detection & delegation    │    database, auth, caching            │
│                                    │                                       │
│  Modes:                            │  • frontend-designer                  │
│    • feature      (MVP scope)      │    Auto-activates: UI/UX,             │
│    • architecture (system design)  │    components, a11y, responsive       │
│    • design       (UI/UX)          │                                       │
│    • backend      (API/DB)         │  • devops-helper                      │
│    • frontend     (components)     │    Auto-activates: CI/CD,             │
│    • devops       (deployment)     │    Docker, deployment, hosting        │
│    • quick        (fast, no agents)│                                       │
│    • thorough     (deep + agents)  │                                       │
│                                    │                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  AGENTS (Background Delegation)                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  workflow-orchestrator - Manages parallel agent execution & synthesis      │
│                                                                             │
│  Delegates to (from experienced-engineer plugin):                          │
│    • backend-architect       • ux-ui-designer        • devops-engineer     │
│    • database-architect      • frontend-specialist   • performance-eng     │
│    • security-specialist     • testing-specialist    • code-quality-rev    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  SKILL AUTO-ACTIVATION TRIGGERS                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  backend-designer                  │  frontend-designer                    │
│  ────────────────                  │  ─────────────────                    │
│  • API design, REST, GraphQL       │  • UI design, UX design               │
│  • database schema, migration      │  • component architecture             │
│  • authentication, OAuth, JWT      │  • accessibility, a11y, WCAG          │
│  • session management              │  • responsive design, layout          │
│  • rate limiting, caching          │  • React/Vue component                │
│                                    │  • state management, form design      │
│  devops-helper                     │                                       │
│  ─────────────                     │  All skills provide:                  │
│  • CI/CD, deployment               │    ✓ Immediate pattern guidance       │
│  • Docker, container, Kubernetes   │    ✓ Trade-off analysis               │
│  • GitHub Actions, pipeline        │    ✓ "Solid indie" advice             │
│  • infrastructure, hosting         │    ✓ Agent delegation (when needed)   │
│  • environment variables           │    ✓ ADHD-friendly format             │
│                                    │                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  BRAINSTORM COMMAND USAGE                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  Command                           │  What Happens                         │
│  ───────                           │  ────────────                         │
│  /brainstorm                       │  Auto-detects mode from context       │
│                                    │  Launches relevant agents (thorough)  │
│                                    │                                       │
│  /brainstorm quick                 │  Fast ideation (5-7 ideas)            │
│                                    │  No agent delegation                  │
│                                    │  Saves to markdown                    │
│                                    │  ~2 minutes                           │
│                                    │                                       │
│  /brainstorm thorough "topic"      │  Deep analysis                        │
│                                    │  Launches 2-4 agents (parallel)       │
│                                    │  Synthesizes comprehensive plan       │
│                                    │  ~3-5 minutes                         │
│                                    │                                       │
│  /brainstorm feature               │  User value, MVP scope                │
│                                    │  Delegates: product-strategist        │
│                                    │                                       │
│  /brainstorm architecture          │  System design, scalability           │
│                                    │  Delegates: backend + database        │
│                                    │                                       │
│  /brainstorm design                │  UI/UX, accessibility                 │
│                                    │  Delegates: ux-ui-designer            │
│                                    │                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  OUTPUT FORMAT (ADHD-Friendly)                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  All brainstorms follow this structure:                                    │
│                                                                             │
│    ## Quick Wins (< 30 min each)                                           │
│    1. ⚡ [Action] - [Benefit]                                               │
│    2. ⚡ [Action] - [Benefit]                                               │
│                                                                             │
│    ## Medium Effort (1-2 hours)                                            │
│    - [ ] [Task with clear outcome]                                         │
│                                                                             │
│    ## Long-term (Future sessions)                                          │
│    - [ ] [Strategic item]                                                  │
│                                                                             │
│    ## Recommended Path                                                     │
│    → [Clear recommendation with reasoning]                                 │
│                                                                             │
│    ## Next Steps                                                           │
│    1. [ ] [Immediate action]                                               │
│    2. [ ] [Follow-up]                                                      │
│                                                                             │
│  Files saved to: [project-root]/BRAINSTORM-[topic]-[date].md               │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  COMMON WORKFLOWS                                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  Feature Planning                  │  Architecture Review                  │
│  ────────────────                  │  ───────────────────                  │
│  1. Describe feature naturally     │  1. /brainstorm architecture          │
│  2. Skills auto-activate           │  2. Agents analyze in parallel:       │
│  3. /brainstorm thorough [topic]   │     - backend-architect               │
│  4. Review generated plan          │     - database-architect              │
│  5. Start with Quick Wins!         │     - performance-engineer            │
│                                    │  3. Review synthesis (~3 min)         │
│  Quick Design Decision             │  4. Implement quick wins first        │
│  ─────────────────────             │                                       │
│  1. Ask about pattern:             │  Deployment Strategy                  │
│     "JWT or session cookies?"      │  ───────────────────                  │
│  2. backend-designer activates     │  1. Mention deployment need           │
│  3. Get immediate answer           │  2. devops-helper activates           │
│  4. No delegation needed           │  3. Get platform + cost estimate      │
│                                    │  4. /brainstorm devops (optional)     │
│                                    │                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  DESIGN PHILOSOPHY: "SOLID INDIE"                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  ✅ DO                              │  ❌ AVOID                              │
│  ──                                │  ─────                                │
│  • Ship fast, iterate              │  • Microservices (small teams)        │
│  • Proven patterns                 │  • Over-abstraction                   │
│  • Boring technology               │  • Premature optimization             │
│  • Right-sized complexity          │  • Corporate patterns                 │
│  • Cost-conscious (~$50/mo)        │  • Generic repositories               │
│  • Monolith → extract later        │  • Kubernetes (< 10 people)           │
│                                    │                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  AGENT DELEGATION PERFORMANCE                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  Parallel Execution Example:                                               │
│                                                                             │
│    Task: "Design user auth with OAuth"                                     │
│    Agents launched (parallel):                                             │
│      • backend-architect      (OAuth flow)        ~1m 30s                  │
│      • security-specialist    (security review)   ~45s                     │
│      • ux-ui-designer          (login UI)          ~1m 10s                 │
│      • devops-engineer         (secrets mgmt)      ~50s                    │
│                                                                             │
│    Total time: ~1m 30s (slowest agent, NOT 4m 15s sequential!)             │
│                                                                             │
│    Output: Comprehensive plan with backend, frontend, DevOps, security     │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  TIPS FOR BEST RESULTS                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  Be Specific                       │  Use Right Mode                       │
│  ───────────                       │  ──────────────                       │
│  ✅ "User auth with Google OAuth"  │  Quick validation  → quick mode       │
│  ❌ "auth stuff"                    │  Familiar domain   → skills only      │
│                                    │  Unfamiliar tech   → thorough mode    │
│  Mention Constraints               │  Big decision      → architecture     │
│  ───────────────────               │                                       │
│  • Budget: "$50/month max"         │  Provide Context                      │
│  • Team: "2 developers"            │  ────────────────                     │
│  • Timeline: "1 week MVP"          │  • Existing stack                     │
│                                    │  • Current users                      │
│                                    │  • Growth expectations                │
│                                    │                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  TROUBLESHOOTING                                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  Skills not activating?            │  Agent delegation not working?        │
│  ──────────────────────            │  ─────────────────────────────        │
│  • Check plugin installed          │  • Using quick mode?                  │
│  • Restart Claude Code             │  • experienced-engineer installed?    │
│  • Use trigger keywords            │  • Check agent timeout (5 min)        │
│                                    │                                       │
│  Brainstorm not saving?            │  Getting too much detail?             │
│  ──────────────────────            │  ────────────────────────             │
│  • Check write permissions         │  • Use quick mode                     │
│  • Create ~/brainstorms/           │  • Ask for summary only               │
│                                    │  • Skip thorough mode                 │
│                                    │                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Command Reference

| What You Want | What To Do |
|---------------|------------|
| **Quick feature ideas** | `/brainstorm quick feature [topic]` |
| **Deep architecture analysis** | `/brainstorm thorough architecture [topic]` |
| **UI/UX design guidance** | Mention "UI design" → frontend-designer activates |
| **API design help** | Mention "API" → backend-designer activates |
| **Deployment advice** | Mention "deploy" → devops-helper activates |
| **Auto-detect mode** | `/brainstorm` (analyzes conversation context) |

---

## Pattern Library Quick Reference

### Backend Patterns
- **REST API:** Resources + HTTP methods + versioning
- **Auth:** JWT (stateless) vs Sessions (server state)
- **Database:** Normalized (consistency) vs Denormalized (performance)
- **Caching:** Redis (shared) vs In-memory (single server)

### Frontend Patterns
- **Components:** Container/Presentational split
- **State:** Context (simple) → Zustand (medium) → Redux (complex)
- **A11y:** WCAG 2.1 AA minimum, keyboard nav, ARIA labels
- **Performance:** Code split routes, lazy load images, virtual scroll lists

### DevOps Patterns
- **Platforms:** Vercel (Next.js), Render (full-stack), Fly.io (containers)
- **CI/CD:** GitHub Actions → Test → Auto-deploy
- **Databases:** Supabase (Postgres), PlanetScale (MySQL), MongoDB Atlas
- **Costs:** $0 MVP → ~$25/mo at 1K users → ~$100/mo at 10K

---

## Installation

```bash
cd ~/.claude/plugins
git clone https://github.com/Data-Wise/claude-plugins.git temp
mv temp/workflow .
rm -rf temp
# Restart Claude Code
```

---

## Links

- **Full docs:** [README.md](../README.md)
- **Quick start:** [QUICK-START.md](QUICK-START.md)
- **Doc hub:** [docs/README.md](README.md)
- **Repository:** https://github.com/Data-Wise/claude-plugins

---

**Print this page for quick reference while coding!** 🖨️
