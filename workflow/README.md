# Workflow Plugin for Claude Code

**Version:** 0.1.0
**Author:** Data-Wise
**License:** MIT

> **ADHD-friendly workflow automation with auto-delegation, brainstorming, and design pattern assistance**

---

## Overview

The Workflow Plugin enhances your development workflow with:

✨ **Auto-activating skills** - Backend, frontend, and DevOps guidance triggers automatically based on conversation keywords

⚡ **Smart brainstorming** - Enhanced `/brainstorm` command with mode detection and agent delegation

🤖 **Background delegation** - Automatically delegates complex analysis to specialized agents running in parallel

📊 **Result synthesis** - Combines multiple agent outputs into unified, actionable recommendations

🧠 **ADHD-friendly** - Scannable output, quick wins, clear next steps, reduced decision paralysis

---

## Features

### 1. Auto-Activating Skills (3 skills)

Skills that automatically provide guidance when relevant topics are discussed:

#### **backend-designer**
- **Triggers:** API design, database schema, authentication, caching
- **Provides:** Pragmatic backend patterns, "solid indie" architecture advice
- **Delegates to:** backend-architect, database-architect, security-specialist agents

#### **frontend-designer**
- **Triggers:** UI/UX design, component architecture, accessibility, responsive design
- **Provides:** ADHD-friendly design patterns, component structure, a11y guidance
- **Delegates to:** ux-ui-designer, frontend-specialist agents

#### **devops-helper**
- **Triggers:** CI/CD, deployment, Docker, infrastructure
- **Provides:** Platform recommendations, cost optimization, indie-friendly DevOps
- **Delegates to:** devops-engineer, performance-engineer agents

### 2. Enhanced Brainstorm Command

**Usage:**
```bash
/brainstorm                          # Auto-detect mode from context
/brainstorm feature                  # Feature brainstorm
/brainstorm architecture             # Architecture design
/brainstorm design                   # UI/UX design
/brainstorm quick                    # Fast ideation (no delegation)
/brainstorm thorough "topic"         # Deep analysis with agents
```

**Modes:**
- **feature** - User value, MVP scope, user stories
- **architecture** - System design, scalability, trade-offs
- **design** - UI/UX, accessibility, user experience
- **backend** - API design, database, auth patterns
- **frontend** - Components, state management, performance
- **devops** - CI/CD, deployment, infrastructure

**Smart Features:**
- Auto-detects mode from conversation context
- Launches 2-4 specialized agents in background (thorough mode)
- Provides immediate ideas while agents work
- Synthesizes agent findings into comprehensive plan
- Saves all brainstorms to markdown files

### 3. Workflow Orchestrator Agent

Manages complex workflows by:
- Analyzing task requirements
- Selecting appropriate specialized agents
- Running multiple agents in parallel (non-blocking)
- Monitoring progress with status updates
- Synthesizing results into unified recommendations

**Example orchestration:**
```
User: "Design user authentication with OAuth"

Orchestrator:
1. Launches 4 agents in parallel:
   - backend-architect (OAuth flow design)
   - security-specialist (security review)
   - ux-ui-designer (login UI design)
   - devops-engineer (secrets management)

2. Provides status updates:
   "✓ Security specialist completed (35s)"
   "✓ DevOps engineer completed (42s)"
   "✓ UX designer completed (58s)"
   "✓ Backend architect completed (1m 24s)"

3. Synthesizes into implementation plan with:
   - Backend setup steps
   - Frontend UI components
   - DevOps secrets configuration
   - Security checklist
   - Next steps (numbered, concrete)

Total time: ~1.5 min (4 agents in parallel, not 4+ min sequential!)
```

---

## Installation

### Option 1: Manual Installation (Recommended for Development)

```bash
cd ~/.claude/plugins
git clone https://github.com/Data-Wise/claude-plugins.git temp
mv temp/workflow .
rm -rf temp
```

### Option 2: Symlink for Development

```bash
cd ~/.claude/plugins
ln -s /path/to/claude-plugins/workflow workflow
```

### Verify Installation

```bash
# Restart Claude Code, then check:
ls ~/.claude/plugins/workflow

# You should see:
# .claude-plugin/
# commands/
# skills/
# agents/
# README.md
```

---

## Quick Start

### 1. Auto-Activating Skills (Zero Setup)

Skills activate automatically when you discuss relevant topics:

```
You: "I need to design a REST API for user management"

→ backend-designer skill auto-activates
→ Provides API design patterns (RESTful resources, auth strategies)
→ May delegate to backend-architect agent for deep analysis
```

No explicit invocation needed!

### 2. Brainstorming

**Quick brainstorm** (5 ideas, no delegation):
```
/brainstorm quick feature user notifications
```

**Thorough brainstorm** (comprehensive analysis with agents):
```
/brainstorm thorough multi-tenant SaaS architecture
```

**Auto-detected mode** (analyzes conversation context):
```
You: "I'm thinking about how to handle user authentication"
/brainstorm

→ Detects backend topic
→ Launches backend-architect + security-specialist agents
→ Generates comprehensive auth implementation plan
```

### 3. Design Philosophy

All guidance follows **"Solid Indie" principles:**

✅ **Ship fast** - Pragmatic solutions over perfect architecture
✅ **Proven patterns** - Boring technology that works
✅ **Right-sized** - Complexity matches team size
✅ **Cost-conscious** - Indie developer budget (~$50/month)

❌ **Avoid over-engineering** - No microservices for small teams
❌ **No premature optimization** - Ship functionality first
❌ **No corporate patterns** - Generic repositories, complex abstractions

---

## Usage Examples

### Example 1: API Design with Auto-Activation

```
You: "I need to add pagination to my API endpoints"

→ backend-designer skill activates
→ Suggests cursor-based vs offset pagination
→ Provides implementation examples
→ Notes trade-offs (cursor = better perf, offset = simpler)
→ Recommends offset for MVP, cursor for scale
```

### Example 2: UI Component Design

```
You: "How should I structure my dashboard components?"

→ frontend-designer skill activates
→ Suggests component composition pattern
→ Recommends card-based layout for scannability
→ Provides accessibility checklist
→ May delegate to ux-ui-designer agent for comprehensive review
```

### Example 3: Deployment Strategy

```
You: "I need to deploy my Next.js app with PostgreSQL"

→ devops-helper skill activates
→ Recommends Vercel (Next.js) + Supabase (PostgreSQL)
→ Estimates cost ($0 for MVP, ~$25/month at scale)
→ Provides CI/CD setup (GitHub Actions + Vercel auto-deploy)
→ Outlines environment variables strategy
```

### Example 4: Comprehensive Feature Brainstorm

```
/brainstorm thorough real-time collaboration feature

Response:
1. Auto-detects architecture + frontend topics
2. Launches 3 agents in parallel:
   - backend-architect (WebSocket vs SSE vs polling)
   - frontend-specialist (state synchronization)
   - performance-engineer (scaling considerations)
3. Provides immediate ideas while agents work
4. After ~2 min, synthesizes comprehensive plan:
   - Technology recommendation (WebSocket via Socket.io)
   - State sync strategy (operational transforms)
   - Scaling approach (Redis pub/sub)
   - Implementation steps (numbered, concrete)
   - Cost estimate (~$15/month for 1K users)
5. Saves to BRAINSTORM-real-time-collaboration-2025-12-23.md
```

---

## Plugin Structure

```
workflow/
├── .claude-plugin/
│   └── plugin.json              # Plugin metadata
├── commands/
│   └── brainstorm.md            # Enhanced /brainstorm command
├── skills/
│   └── design/
│       ├── backend-designer.md  # Auto-activating backend skill
│       ├── frontend-designer.md # Auto-activating frontend skill
│       └── devops-helper.md     # Auto-activating DevOps skill
├── agents/
│   └── orchestrator.md          # Workflow orchestrator agent
├── tests/
│   └── test-plugin-structure.sh # Unit tests
├── docs/
│   ├── QUICK-START.md           # 5-minute getting started
│   ├── REFCARD.md               # One-page reference
│   └── README.md                # Documentation hub
├── README.md                    # This file
├── package.json                 # npm metadata
└── LICENSE                      # MIT license
```

---

## Configuration

### No Configuration Required!

The plugin works out of the box with sensible defaults.

### Optional: Customize Agent Behavior

Skills automatically delegate to agents when thorough analysis is needed. You can control delegation by:

**In conversation:**
- Use `/brainstorm quick` to skip agent delegation
- Use `/brainstorm thorough` to force deep analysis

**Agents used:**
- backend-architect (from experienced-engineer plugin)
- ux-ui-designer (from experienced-engineer plugin)
- devops-engineer (from experienced-engineer plugin)
- security-specialist (from experienced-engineer plugin)
- performance-engineer (from experienced-engineer plugin)

*Note: These agents must be installed separately (typically included in Claude Code).*

---

## Design Patterns Library

Skills reference proven patterns for common scenarios:

### Backend Patterns
- **RESTful API design** - Resources, HTTP methods, versioning
- **Authentication flows** - JWT vs sessions, OAuth 2.0, API keys
- **Database design** - Normalization, indexing, migrations
- **Caching strategies** - Redis, in-memory, CDN

### Frontend Patterns
- **Component composition** - Container/presentational, compound components
- **State management** - Context, Redux, Zustand (when to use which)
- **Accessibility** - WCAG checklist, keyboard nav, screen readers
- **Performance** - Code splitting, lazy loading, virtualization

### DevOps Patterns
- **CI/CD pipelines** - GitHub Actions, testing automation
- **Deployment platforms** - Vercel, Render, Fly.io (comparison)
- **Infrastructure** - Docker multi-stage builds, container orchestration
- **Cost optimization** - Free tier strategies, scaling thresholds

### ADHD-Friendly Patterns
- **Progressive disclosure** - Hide complexity behind toggles
- **Immediate feedback** - Loading states, success confirmations
- **Visual hierarchy** - Clear focus states, limited colors
- **Cognitive load reduction** - One action per screen, templates

---

## Troubleshooting

### Skills Not Auto-Activating

**Check:**
1. Plugin installed in `~/.claude/plugins/workflow/`
2. Skills directory present: `~/.claude/plugins/workflow/skills/design/`
3. Restart Claude Code

**Test activation:**
```
You: "I need to design a REST API"

Expected: backend-designer skill should activate and provide guidance
```

### Agent Delegation Not Working

**Possible causes:**
1. Missing experienced-engineer plugin (provides specialized agents)
2. Agent timed out (5 min max per agent)
3. Using quick mode (`/brainstorm quick` skips delegation)

**Check agent availability:**
```
# Should list agents: backend-architect, ux-ui-designer, devops-engineer, etc.
ls ~/.claude/plugins/experienced-engineer/agents/
```

### Brainstorm Files Not Saving

**Check:**
1. Write permissions in current directory
2. Fallback location: `~/brainstorms/` should be writable

**Manual save location:**
```bash
mkdir -p ~/brainstorms
chmod 755 ~/brainstorms
```

---

## Development

### Running Tests

```bash
cd ~/.claude/plugins/workflow
bash tests/test-plugin-structure.sh
```

**Tests verify:**
- Required files exist (.claude-plugin/plugin.json, package.json)
- JSON files are valid
- 1 command present (brainstorm.md)
- 3 skills present (backend-designer, frontend-designer, devops-helper)
- 1 agent present (orchestrator.md)
- No hardcoded paths

### Adding New Skills

1. Create skill file in `skills/[category]/[name].md`
2. Add frontmatter with triggers
3. Document auto-activation behavior
4. Update tests to expect new skill count

### Adding New Commands

1. Create command file in `commands/[name].md`
2. Add frontmatter with arguments
3. Document usage examples
4. Update tests

---

## Roadmap

### v0.1.0 (Current)
- [x] 3 auto-activating skills (backend, frontend, devops)
- [x] Enhanced /brainstorm command with delegation
- [x] Workflow orchestrator agent
- [x] Comprehensive documentation

### v0.2.0 (Planned)
- [ ] /analyze command (architecture analysis)
- [ ] /review command (code review with quality + security)
- [ ] /optimize command (performance review)
- [ ] Pattern library expansion (30+ patterns)
- [ ] Result caching for faster repeated queries

### v1.0.0 (Future)
- [ ] Custom skill creation wizard
- [ ] Integration with /done command (capture design decisions)
- [ ] Workflow templates (auth, payment, notifications)
- [ ] MCP server integration for external tools

---

## Contributing

This plugin follows "solid indie" principles:

1. **Ship fast** - PR merged quickly for working features
2. **Pragmatic** - Real-world usage over theoretical perfection
3. **ADHD-friendly** - Scannable docs, clear examples, quick wins

**How to contribute:**
1. Test with real projects
2. Share use cases that worked well
3. Suggest patterns that saved time
4. Report what felt over-engineered

---

## License

MIT License - see LICENSE file

---

## Links

- **Repository:** https://github.com/Data-Wise/claude-plugins
- **Documentation:** [docs/README.md](docs/README.md)
- **Quick Start:** [docs/QUICK-START.md](docs/QUICK-START.md)
- **Reference Card:** [docs/REFCARD.md](docs/REFCARD.md)

---

**Built with ❤️ for indie developers who ship fast and iterate based on real usage.**
