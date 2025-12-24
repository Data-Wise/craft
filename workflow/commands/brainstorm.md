---
name: brainstorm
description: Enhanced brainstorming with smart detection, design modes, and automatic agent delegation for deep analysis
args:
  - name: mode
    description: "Brainstorm mode: feature|architecture|design|quick|thorough (optional, auto-detected if omitted)"
    required: false
  - name: topic
    description: "Topic to brainstorm (optional, uses conversation context if omitted)"
    required: false
---

# Enhanced Brainstorm Command

**Usage:**
```bash
/brainstorm                          # Auto-detect mode from context
/brainstorm feature                  # Feature brainstorm mode
/brainstorm architecture             # Architecture design mode
/brainstorm design                   # UI/UX design mode
/brainstorm quick                    # Quick ideation (5 ideas, no delegation)
/brainstorm thorough "API design"    # Deep analysis with agent delegation
```

## How It Works

### 1. Smart Mode Detection

If no mode specified, I analyze the conversation context to detect:

| Keywords Detected | Mode Selected | Delegation |
|------------------|---------------|------------|
| "feature", "functionality", "user story" | `feature` | Product strategist agent (background) |
| "architecture", "system design", "scalability" | `architecture` | Backend architect agent (background) |
| "UI", "UX", "design", "layout", "accessibility" | `design` | UX/UI designer agent (background) |
| "backend", "API", "database" | `backend` | Backend architect + database architect |
| "frontend", "component", "React" | `frontend` | Frontend specialist + UX designer |
| "deployment", "CI/CD", "Docker" | `devops` | DevOps engineer agent |

### 2. Brainstorm Execution

**Quick Mode** (5-10 minutes):
1. Generate 5-7 concrete ideas
2. Organize by Quick Wins vs Long-term
3. Provide next steps
4. Save to markdown file

**Thorough Mode** (10-30 minutes):
1. Generate initial ideas (same as quick)
2. **Delegate deep analysis to agents** (background):
   - Launch 2-3 relevant agents based on topic
   - Agents run in parallel (non-blocking)
   - Monitor progress, provide updates
3. **Synthesize agent findings** into comprehensive plan
4. Save detailed brainstorm document with:
   - Multiple approaches with trade-offs
   - Agent analysis summaries
   - Recommended path forward
   - Implementation timeline

### 3. Output Structure

All brainstorms follow ADHD-friendly format:

```markdown
# [Topic] Brainstorm

**Generated:** [Date]
**Mode:** [Detected Mode]
**Agents Consulted:** [Agent list if thorough mode]

## Quick Wins (< 30 min each)
1. ⚡ [Action] - [Benefit]
2. ⚡ [Action] - [Benefit]

## Medium Effort (1-2 hours)
- [ ] [Task with clear outcome]

## Long-term (Future sessions)
- [ ] [Strategic item]

## Agent Analysis (Thorough mode only)

### Backend Architect Analysis
[Summary of agent findings]

### UX Designer Analysis
[Summary of agent findings]

## Recommended Path
→ [Clear recommendation with reasoning]

## Next Steps
1. [ ] [Immediate action]
2. [ ] [Follow-up]
```

## Mode-Specific Behaviors

### Feature Mode
**Focus:** User value, functionality, MVP scope
**Delegation:** Product strategist agent (background)
**Output:** User stories, acceptance criteria, scope definition

### Architecture Mode
**Focus:** System design, scalability, technical trade-offs
**Delegation:** Backend architect + database architect (parallel)
**Output:** Architecture diagrams (Mermaid), component breakdown, data flow

### Design Mode
**Focus:** UI/UX, accessibility, user experience
**Delegation:** UX/UI designer agent (background)
**Output:** Wireframes (ASCII art), component structure, a11y checklist

### Backend Mode
**Focus:** API design, database schema, auth patterns
**Delegation:** Backend architect + security specialist (parallel)
**Output:** API endpoints, schema design, security checklist

### Frontend Mode
**Focus:** Component architecture, state management, performance
**Delegation:** Frontend specialist + performance engineer (parallel)
**Output:** Component tree, state management strategy, bundle optimization

### DevOps Mode
**Focus:** CI/CD, deployment, infrastructure
**Delegation:** DevOps engineer agent (background)
**Output:** Deployment pipeline, platform recommendations, cost estimates

## Agent Delegation System

### Background Execution
```python
# When thorough mode is active
if mode == "thorough" or detected_complexity == "high":
    # Launch agents in background (non-blocking)
    backend_analysis = Task(
        subagent_type="backend-architect",
        prompt="Analyze backend architecture for [topic]",
        run_in_background=True
    )

    ux_analysis = Task(
        subagent_type="ux-ui-designer",
        prompt="Review UX design for [topic]",
        run_in_background=True
    )

    # Continue with initial brainstorm while agents work
    generate_initial_ideas()

    # Wait for agents to complete, then synthesize
    backend_results = TaskOutput(backend_analysis.task_id)
    ux_results = TaskOutput(ux_analysis.task_id)

    synthesize_comprehensive_plan(backend_results, ux_results)
```

### Agent Selection Logic

I automatically select agents based on topic keywords:

| Topic Contains | Agents Launched |
|---------------|----------------|
| "API", "backend", "database" | backend-architect, database-architect |
| "UI", "UX", "component" | ux-ui-designer, frontend-specialist |
| "deploy", "CI/CD", "infrastructure" | devops-engineer |
| "auth", "security", "permissions" | security-specialist |
| "performance", "optimization" | performance-engineer |
| "test", "quality", "coverage" | testing-specialist |

## Integration with Skills

This command works seamlessly with auto-activating skills:

- **backend-designer** skill provides quick backend recommendations
- **frontend-designer** skill offers UX patterns
- **devops-helper** skill suggests deployment strategies

**Workflow:**
1. User invokes `/brainstorm`
2. Skills auto-activate based on topic keywords
3. Skills provide immediate patterns/recommendations
4. If thorough mode, command delegates to agents for deep analysis
5. Final output combines skill patterns + agent analysis

## File Output

All brainstorms are automatically saved to:

**Location:** Current project root or `~/brainstorms/`
**Filename:** `BRAINSTORM-[topic]-[date].md`

**Example:** `BRAINSTORM-user-authentication-2025-12-23.md`

After saving, I ask: "Would you like me to open this file?" and use AppleScript to open in iA Writer.

## Examples

### Example 1: Quick Feature Brainstorm

```
User: "/brainstorm feature user notifications"

Response:
1. Quick pattern recognition (feature mode detected)
2. backend-designer skill auto-activates
3. Generate 5 notification approaches
4. List quick wins (email notifications) vs long-term (push, SMS)
5. Save to BRAINSTORM-user-notifications-2025-12-23.md
6. Ask to open file
```

### Example 2: Thorough Architecture Brainstorm

```
User: "/brainstorm thorough multi-tenant SaaS architecture"

Response:
1. Architecture mode detected
2. Launch backend-architect agent (background)
3. Launch database-architect agent (background)
4. Generate initial architecture options
5. Wait for agents to complete (~2-3 min)
6. Synthesize comprehensive plan with:
   - Database isolation strategies (schema vs database)
   - API design (tenant context, authorization)
   - Scalability considerations
   - Cost estimates
7. Save to BRAINSTORM-multi-tenant-architecture-2025-12-23.md
8. Ask to open file
```

### Example 3: Auto-Detected Design Brainstorm

```
User: "/brainstorm I need to improve the dashboard UX"

Response:
1. Auto-detect design mode (keywords: "dashboard", "UX")
2. frontend-designer skill auto-activates
3. Launch ux-ui-designer agent (background)
4. Provide immediate UX patterns (card layout, data visualization)
5. Wait for agent UX review
6. Synthesize with accessibility checklist, ADHD-friendly tips
7. Save comprehensive design brainstorm
```

## Tips for Best Results

**Be specific:** "User authentication with OAuth" > "auth stuff"

**Mention constraints:** "Budget: $50/month", "Team: 2 developers", "Timeline: 1 week MVP"

**Include context:** "Existing stack: Next.js, PostgreSQL, Vercel"

**Use thorough mode when:**
- Multiple valid approaches exist
- Architecture decisions with long-term impact
- Unfamiliar domain/technology
- Need detailed analysis before committing

**Use quick mode when:**
- Time-sensitive decisions
- Familiar territory
- Just need validation of approach
- Exploring initial ideas

---

**Remember:** This command enhances the existing `/brainstorm` workflow with smart detection and automatic delegation. It maintains ADHD-friendly output (scannable, actionable, quick wins) while providing deep analysis when needed.
