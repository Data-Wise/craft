---
description: Universal command that intelligently routes to appropriate craft commands
arguments:
  - name: task
    description: Natural language description of what you want to do
    required: true
  - name: dry-run
    description: Preview routing plan without executing commands
    required: false
    default: false
    alias: -n
  - name: orch
    description: Enable orchestration mode
    required: false
    default: false
  - name: orch-mode
    description: Orchestration mode (default|debug|optimize|release)
    required: false
    default: null
---

# /craft:do - Universal Command

Intelligently analyze your task and execute the right craft commands.

## Usage

```bash
/craft:do <task description>
/craft:do <task description> --dry-run    # Preview routing plan
/craft:do <task description> -n           # Preview routing plan
```

## Dry-Run Mode

Preview which commands will be executed without actually running them:

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Smart Routing Analysis                            │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Task Analysis:                                              │
│   - Input: "add user authentication"                          │
│   - Category: Feature Development                             │
│   - Complexity: 4/10 (Medium)                                 │
│   - Spec check: No matching spec found                        │
│                                                               │
│ ✓ Complexity Breakdown:                                       │
│   - Multi-step task: +2 (design → implement → test)          │
│   - Requires planning: +2 (auth architecture needed)          │
│   Total score: 4 → Agent delegation                           │
│                                                               │
│ ✓ Routing Decision: feature-dev Agent                         │
│   - Reason: Medium complexity (4/10), feature development     │
│   - Context: Forked (isolated execution)                      │
│   - Agent triggers: add, create, implement                    │
│   - Max complexity: 7 (within agent's capability)             │
│   - Estimated: ~15 minutes                                    │
│                                                               │
│ ✓ Alternative Routes:                                         │
│   1. Command routing (if complexity < 4)                      │
│      → /craft:arch:plan → /craft:code:test-gen               │
│   2. Orchestration (if complexity > 7)                        │
│      → /craft:orchestrate "add user authentication"          │
│                                                               │
│ ⚠ Notes:                                                      │
│   • Consider creating spec first: /craft:workflow:brainstorm  │
│   • Agent will execute in forked context (results synthesized)│
│   • Permission may be requested for agent delegation          │
│                                                               │
│ 📊 Summary: Agent delegation to feature-dev (~15 min)         │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

### Simple Task Dry-Run (Complexity < 4)

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Smart Routing Analysis                            │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Task Analysis:                                              │
│   - Input: "lint the code"                                    │
│   - Category: Code Quality                                    │
│   - Complexity: 0/10 (Simple)                                 │
│                                                               │
│ ✓ Complexity Breakdown:                                       │
│   - Single-step task: 0 (no multi-step)                      │
│   - No planning needed: 0                                     │
│   Total score: 0 → Command routing                            │
│                                                               │
│ ✓ Routing Plan (1 command):                                   │
│   1. /craft:code:lint default                                 │
│      Purpose: Check code style and quality                    │
│      Estimated: ~3 seconds                                    │
│                                                               │
│ 📊 Summary: 1 command, ~3 seconds                             │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

**Note**: Dry-run shows routing decision based on complexity score. Agent delegation triggers for medium (4-7) and complex (8-10) tasks.

## How It Works

1. **Check Spec** - Look for existing spec matching task (NEW in v1.1.0)
2. **Analyze** - Parse task description for intent and category
3. **Score Complexity** - Calculate 0-10 score based on 5 factors (NEW in v1.23.0)
4. **Route Decision** - Choose execution strategy:
   - **Score 0-3**: Route to craft commands (traditional)
   - **Score 4-7**: Delegate to specialized agent (NEW)
   - **Score 8-10**: Delegate to orchestrator-v2 (NEW)
5. **Execute** - Run commands or invoke agent with forked context
6. **Synthesize** - Gather results and report to user
7. **Report** - Summarize what was done

## Agent Delegation Workflow (NEW in v1.23.0)

When complexity score ≥ 4, `/craft:do` delegates to specialized agents:

### Step 1: Complexity Analysis

```
User: /craft:do "add OAuth login to the app"

Claude analyzes:
- Multi-step task: +2 (design → implement → test)
- Requires planning: +2 (auth architecture)
- Total score: 4/10 (Medium)
→ Decision: Delegate to feature-dev agent
```

### Step 2: Agent Selection

Based on task keywords and complexity:

```
Keywords: "add", "OAuth", "login"
Category: Feature Development
Score: 4/10
→ Selected agent: feature-dev (max complexity: 7)
```

### Step 3: Forked Context Execution

```
Main Context (your conversation)
    ↓
    Spawn feature-dev agent in forked context
    ↓
    Agent works independently:
    - Designs OAuth flow
    - Creates implementation plan
    - Generates test stubs
    - Identifies dependencies
    ↓
    Results synthesized back to main context
```

### Step 4: Result Synthesis

```
Claude receives agent results and presents:
✓ Architecture designed (OAuth 2.0 + PKCE)
✓ Implementation plan created (4 phases)
✓ Test stubs generated (12 test cases)
✓ Dependencies identified (oauth2 SDK, JWT library)

Ready to implement? (y/n)
```

## Agent Delegation Rules

### When to Delegate

| Condition | Action | Reason |
|-----------|--------|--------|
| Score < 4 | Route to commands | Simple, fast execution |
| Score 4-7 | Delegate to agent | Medium complexity, needs expertise |
| Score 8-10 | Delegate to orchestrator | Complex, multi-agent coordination |
| User says "no agents" | Force command routing | Explicit user preference |

### Forked Context Benefits

- **Isolation**: Agent failures don't corrupt main conversation
- **Parallelization**: Multiple agents can run simultaneously
- **Resource Control**: Each agent has own context budget
- **Clean Results**: Only final synthesis appears in main conversation

### Fallback Strategy

If agent delegation fails or is denied:

```
1. Attempt agent delegation
   ↓ (if permission denied or agent fails)
2. Fall back to command routing
   ↓
3. Execute traditional command sequence
   ↓
4. Report with note: "Completed without agent delegation"
```

## Examples

### Feature Development
```bash
/craft:do add user authentication

# Routes to:
# 1. /craft:arch:plan - Design the feature
# 2. /craft:code:test-gen - Generate tests
# 3. /craft:git:branch - Create feature branch
```

### Bug Fixing
```bash
/craft:do fix the login redirect issue

# Routes to:
# 1. /craft:code:debug - Analyze the issue
# 2. /craft:test:run - Run related tests
# 3. /craft:git:sync - Commit fix
```

### Code Quality
```bash
/craft:do improve code quality

# Routes to:
# 1. /craft:code:lint - Check style
# 2. /craft:test:coverage - Check coverage
# 3. /craft:code:refactor - Suggest improvements
```

### Documentation
```bash
/craft:do update documentation

# Routes to:
# 1. /craft:docs:sync - Sync docs with code
# 2. /craft:docs:validate - Check links
# 3. /craft:docs:changelog - Update changelog
```

### Release Preparation
```bash
/craft:do prepare for release

# Routes to:
# 1. /craft:code:deps-audit - Security scan
# 2. /craft:test:run release - Full tests
# 3. /craft:code:lint release - Full lint
# 4. /craft:docs:changelog - Update changelog
# 5. /craft:code:release - Release workflow
```

## Examples with --orch Flag (NEW in v2.5.0)

### Quick Orchestration
```bash
/craft:do "add user authentication" --orch=optimize

# ORCHESTRATOR v2.1 — OPTIMIZE MODE
Spawning orchestrator...
   Task: add user authentication
   Mode: optimize

Executing: /craft:orchestrate 'add user authentication' optimize
```

### Mode Selection Prompt
```bash
/craft:do "add payment" --orch

 Orchestration Mode Selection
==================================================

Available modes:
  default   - Quick tasks (2 agents max, 70% compression)
  debug     - Sequential troubleshooting (1 agent, 90% compression)
  optimize  - Fast parallel work (4 agents, 60% compression)
  release   - Pre-release audit (4 agents, 85% compression)

[AskUserQuestion prompt appears]
```

### Preview Orchestration
```bash
/craft:do "refactor auth" --orch=release --dry-run

+---------------------------------------------------------------------+
| DRY RUN: Orchestration Preview                                      |
+---------------------------------------------------------------------+
| Task: refactor auth                                                 |
| Mode: release                                                       |
| Max Agents: 4                                                       |
| Compression: 85%                                                    |
+---------------------------------------------------------------------+
| This would spawn the orchestrator with the above settings.          |
| Remove --dry-run to execute.                                        |
+---------------------------------------------------------------------+
```

### Orchestrate Complex Task
```bash
/craft:do "redesign database layer with migrations and tests" --orch=release

# Complex task automatically suggests orchestration
# Score: 6 → orchestrator-v2 with release mode for thorough validation
```

## Task Categories

| Category | Keywords | Commands Used |
|----------|----------|---------------|
| **Feature** | add, create, implement, build | arch:plan, code:test-gen, git:branch |
| **Bug** | fix, debug, issue, error | code:debug, test:run, test:debug |
| **Quality** | lint, quality, clean, improve | code:lint, test:coverage, code:refactor |
| **Docs** | document, update docs, readme | docs:sync, docs:validate, docs:changelog |
| **Test** | test, coverage, verify | test:run, test:coverage, test:debug |
| **Release** | release, deploy, publish | deps-audit, lint, test:run, code:release |
| **Architecture** | design, refactor, restructure | arch:analyze, arch:plan, arch:diagram |

## Routing Logic

```
Task Analysis:
  ├── Contains "add/create/implement"
  │   └── Feature workflow
  ├── Contains "fix/debug/error/issue"
  │   └── Bug fix workflow
  ├── Contains "test/coverage/verify"
  │   └── Testing workflow
  ├── Contains "doc/readme/changelog"
  │   └── Documentation workflow
  ├── Contains "release/deploy/publish"
  │   └── Release workflow
  └── Contains "refactor/restructure/design"
      └── Architecture workflow
```

## Complexity Analysis (NEW in v1.23.0)

Before routing, `/craft:do` analyzes task complexity to determine execution strategy:

### Complexity Scoring

| Score | Task Type | Routing Decision | Example |
|-------|-----------|------------------|---------|
| 0-3 | **Simple** | Route to commands | "lint the code" |
| 4-7 | **Medium** | Single agent delegation | "add OAuth login" |
| 8-10 | **Complex** | orchestrator-v2 delegation | "prepare v2.0 release" |

### Scoring Factors

Each factor adds +2 to complexity score:

- **Multi-step task** - Requires 3+ distinct operations
  - Example: "add auth" → design + implement + test
- **Cross-category task** - Spans multiple categories
  - Example: "refactor and document API" → architecture + docs
- **Requires planning** - Needs design/architecture phase
  - Example: "redesign authentication system"
- **Requires research** - Needs investigation/exploration
  - Example: "investigate performance bottleneck"
- **Multi-file changes** - Affects 5+ files
  - Example: "refactor database layer"

### Routing Decision Flow

```
Task Input
    ↓
Complexity Score (0-10)
    ↓
├─ Score 0-3: Simple → Route to commands (current behavior)
├─ Score 4-7: Medium → Delegate to specialized agent
│                      ├─ feature-dev (add/create/implement)
│                      ├─ backend-architect (design/refactor)
│                      ├─ bug-detective (fix/debug/error)
│                      └─ code-quality-reviewer (quality/lint)
└─ Score 8-10: Complex → Delegate to orchestrator-v2
```

### Agent Delegation (Enabled for Score ≥ 4)

When complexity score ≥ 4, `/craft:do` delegates to specialized agents:

| Agent | Triggers | Max Complexity | Use Case |
|-------|----------|----------------|----------|
| `feature-dev` | add, create, implement, build | 7 | New features |
| `backend-architect` | design, architect, refactor | 8 | Architecture |
| `bug-detective` | fix, debug, error, issue | 6 | Debugging |
| `code-quality-reviewer` | quality, lint, improve | 5 | Code quality |
| `orchestrator-v2` | (any) | 10 | Multi-step orchestration |

### Example Complexity Scores

| Task | Factors | Score | Decision |
|------|---------|-------|----------|
| "lint the code" | None | 0 | → /craft:code:lint |
| "fix login bug" | Multi-step | 2 | → /craft:code:debug |
| "add OAuth login" | Multi-step, Planning | 4 | → feature-dev agent |
| "refactor DB layer" | Multi-step, Planning, Multi-file | 6 | → backend-architect agent |
| "prepare v2.0 release" | Multi-step, Cross-category, Multi-file | 8 | → orchestrator-v2 agent |

## Output Format

```
╭─ /craft:do "add user authentication" ───────────────╮
│ Task Type: Feature Development                      │
│ Commands: 4                                         │
├─────────────────────────────────────────────────────┤
│ Step 1: /craft:arch:plan                           │
│   ✓ Architecture designed                          │
│                                                     │
│ Step 2: /craft:code:test-gen                       │
│   ✓ 12 test cases generated                        │
│                                                     │
│ Step 3: /craft:git:branch                          │
│   ✓ Branch 'feature/user-auth' created             │
│                                                     │
│ Step 4: Ready to implement                         │
│   Next: Start coding in feature/user-auth          │
├─────────────────────────────────────────────────────┤
│ ✓ Task setup complete                              │
╰─────────────────────────────────────────────────────╯
```

## Integration

Works with all craft commands and skills:
- Routes to appropriate category commands
- Uses skills for specialized analysis
- Chains commands for complex workflows

## Spec Integration (NEW in v1.1.0)

Before routing, `/craft:do` checks for existing specs that match the task.

### Spec Check Flow

```bash
# Check for specs in project
find docs/specs -name "SPEC-*.md" 2>/dev/null | while read spec; do
    # Extract topic from filename
    topic=$(basename "$spec" | sed 's/SPEC-//;s/-[0-9].*\.md//')

    # Check if task matches topic
    if [[ "$task" == *"$topic"* ]]; then
        # Found matching spec
        show_spec_prompt "$spec"
    fi
done
```

### Spec Found Prompt

```
AskUserQuestion:
  question: "Found spec for this task. How should we proceed?"
  header: "Spec"
  multiSelect: false
  options:
    - label: "Review spec, then implement"
      description: "Show spec summary first"
    - label: "Implement with spec context"
      description: "Use spec as implementation guide"
    - label: "Skip spec"
      description: "Proceed without spec reference"
    - label: "Create new spec first"
      description: "Current spec may be outdated"
```

### Example: Spec-Aware Execution

```
User: /craft:do implement user authentication

Claude: Found spec: SPEC-auth-system-2025-12-30.md (status: approved)

        [AskUserQuestion: Review/Implement/Skip/New?]

User: Selects "Implement with spec context"

Claude: Loading spec context...
        - User Stories: 1 primary, 2 secondary
        - Acceptance Criteria: 3 items
        - Technical Requirements: OAuth2, JWT tokens
        - Dependencies: auth0 SDK

        Proceeding with implementation...
        Step 1: /craft:arch:plan (using spec requirements)
        Step 2: /craft:code:test-gen (from acceptance criteria)
        ...
```

### No Spec Found

If no matching spec exists and task is a feature:

```
Note: No spec found for "user authentication"
      Consider: /workflow:brainstorm save "user authentication"
      Proceeding with standard routing...
```

---

## Implementation (NEW in v1.23.0, UPDATED in v2.5.0)

When `/craft:do` is invoked, follow these steps:

### Step 0: Check for --orch Flag (NEW in v2.5.0)

```python
from utils.orch_flag_handler import handle_orch_flag, show_orchestration_preview, spawn_orchestrator

task = args.task
orch_flag = args.orch
mode_flag = args.orch_mode
dry_run = args.dry_run

if orch_flag:
    should_orchestrate, mode = handle_orch_flag(task, orch_flag, mode_flag)

    if dry_run:
        show_orchestration_preview(task, mode)
        return

    spawn_orchestrator(task, mode)
    return

# Otherwise, continue with complexity-based routing...
```

### Step 1: Analyze Task and Calculate Complexity

```
1. Parse task description for keywords and intent
2. Calculate complexity score (0-10):

   score = 0
   if multi-step task (3+ operations):           score += 2
   if cross-category (spans multiple domains):   score += 2
   if requires planning (design/architecture):   score += 2
   if requires research (investigation):          score += 2
   if multi-file changes (5+ files):             score += 2

3. Determine category:
   - Feature (add/create/implement/build)
   - Bug (fix/debug/error/issue)
   - Quality (lint/quality/improve)
   - Documentation (document/update docs/readme)
   - Architecture (design/refactor/restructure)
   - Release (release/deploy/publish)
```

### Step 2: Select Execution Strategy

```
if score < 4:
    # Simple task - use traditional command routing
    route_to_commands(task)

elif score >= 4 and score <= 7:
    # Medium complexity - delegate to specialized agent
    agent = select_agent(task, score)
    delegate_to_agent(agent, task)

else:  # score >= 8
    # Complex task - delegate to orchestrator
    delegate_to_agent("orchestrator-v2", task)
```

### Step 3: Agent Selection Logic

```python
def select_agent(task, score):
    # Check keywords for agent triggers
    keywords = task.lower()

    if score > 7:
        return "orchestrator-v2"  # Complex, multi-step

    if any(word in keywords for word in ["add", "create", "implement", "build"]):
        if score <= 7:
            return "feature-dev"  # Feature development

    if any(word in keywords for word in ["design", "architect", "refactor"]):
        if score <= 8:
            return "backend-architect"  # Architecture

    if any(word in keywords for word in ["fix", "debug", "error", "issue"]):
        if score <= 6:
            return "bug-detective"  # Debugging

    if any(word in keywords for word in ["quality", "lint", "improve", "clean"]):
        if score <= 5:
            return "code-quality-reviewer"  # Code quality

    # Default fallback for medium complexity
    if score >= 4:
        return "feature-dev"  # General purpose

    return None  # Route to commands
```

### Step 4: Agent Delegation (Score ≥ 4)

Use the `Task` tool to delegate to the selected agent:

```
# Example: Delegate to feature-dev agent
Task(
    subagent_type="feature-dev",
    description="Implement OAuth login feature",
    prompt=f"""
    Task: {user_task}
    Complexity: {score}/10 ({complexity_level})

    Please:
    1. Design the architecture
    2. Create implementation plan
    3. Generate test stubs
    4. Identify dependencies

    Provide a structured response with:
    - Architecture overview
    - Implementation phases
    - Test coverage plan
    - Dependencies and tools needed
    """,
    model="sonnet"  # Use appropriate model for complexity
)
```

### Step 5: Result Synthesis

```
1. Receive agent results (automatically synthesized from forked context)
2. Present results to user in structured format:

   ✓ Architecture designed
   ✓ Implementation plan created
   ✓ Test stubs generated
   ✓ Dependencies identified

3. Ask user if they want to proceed with implementation
4. If yes, execute next steps
5. If no, save plan for later
```

### Step 6: Fallback to Command Routing

If agent delegation is not available or fails:

```
1. Log: "Agent delegation unavailable, using command routing"
2. Route to traditional craft commands based on category:

   if category == "feature":
       execute(["/craft:arch:plan", "/craft:code:test-gen", "/craft:git:branch"])
   elif category == "bug":
       execute(["/craft:code:debug", "/craft:test:run"])
   elif category == "quality":
       execute(["/craft:code:lint", "/craft:test:coverage"])
   # ... etc

3. Execute commands sequentially
4. Report results
```

### Implementation Notes

- **Forked Context**: All agent delegations use `context: fork` for isolation
- **Error Handling**: If agent fails, fall back to command routing
- **User Preference**: If user says "no agents", skip delegation
- **Dry-Run Mode**: Show delegation plan without executing

---

## Tips

- Be specific for better routing
- Use domain keywords (auth, api, ui, db)
- Add mode hint if needed: "thoroughly test the api"
- Create specs for complex features: `/workflow:brainstorm save "feature"` (or `s` for short)
- For detailed specs: `/brainstorm d f s "feature"` (deep + feat + save)
- Review specs before implementation: `/spec:review [topic]`
