---
name: brainstorm
description: Enhanced brainstorming with smart detection, design modes, time budgets, agent delegation, context-aware questions, and spec capture
version: 2.5.0
args:
  - name: depth
    description: "Analysis depth: q|quick|d|deep|m|max (default: balanced, shows menu if omitted)"
    required: false
  - name: focus
    description: "Focus area: f|feat|a|arch|x|ux|b|api|u|ui|o|ops (optional, auto-detect if omitted)"
    required: false
  - name: action
    description: "Action: s|save (capture as spec) - replaces --save-spec"
    required: false
  - name: topic
    description: "Topic to brainstorm (quoted string, uses conversation context if omitted)"
    required: false
  - name: format
    description: "Output format: terminal|json|markdown (default: terminal)"
    required: false
  - name: categories
    description: "Question categories: req,users,scope,tech,timeline,risks,existing,success (comma-separated, use 'all' for default)"
    required: false
  - name: orch
    description: "Enable orchestration mode (v2.5.0)"
    required: false
  - name: orch-mode
    description: "Orchestration mode: default|debug|optimize|release (v2.5.0)"
    required: false
---

# /workflow:brainstorm - Enhanced Brainstorm

ADHD-friendly brainstorming with smart mode detection, time budgets, agent delegation, context-aware smart questions, and spec capture.

## Arguments Summary

```
/brainstorm [depth:count] [focus] [action] [-C|--categories "cat1,cat2"] "topic"
```

### Depth

| Short | Full | Count | Time | Description |
|-------|------|-------|------|-------------|
| - | (default) | 2 | < 5 min | Balanced, 2 questions + "ask more?" |
| q | quick | 0 | < 1 min | Fast, 0 questions + "ask more?" |
| d | deep | 8 | < 10 min | Expert questions, no agents |
| m | max | 8 | < 30 min | Expert questions + 2 agents |

Custom counts: `d:5`, `m:12`, `q:0`. `thorough` is deprecated alias for `max`.

### Focus

| Short | Full | Synonyms | Brainstorms |
|-------|------|----------|-------------|
| f | feat | feature | User stories, MVP scope, acceptance criteria |
| a | arch | architecture | System design, scalability, component diagrams |
| x | ux | design | UI/UX wireframes, accessibility, user flows |
| b | api | backend | API endpoints, database schema, auth patterns |
| u | ui | frontend | Component tree, state management, performance |
| o | ops | devops | CI/CD pipelines, deployment, infrastructure |

### Action

| Short | Full | Synonym | Effect |
|-------|------|---------|--------|
| s | save | spec | Output SPEC.md (replaces --save-spec) |

### Categories (`-C` / `--categories`)

| Short | Full |
|-------|------|
| req | requirements |
| usr | users |
| scp | scope |
| tech | technical |
| time | timeline |
| risk | risks |
| exist | existing |
| ok | success |
| all | all categories |

---

## When Invoked

### Step 0: Parse Arguments

```python
DEPTH_MAP = {
    'q': 'quick', 'quick': 'quick',
    'd': 'deep', 'deep': 'deep',
    'm': 'max', 'max': 'max',
    't': 'max', 'thorough': 'max'
}

FOCUS_MAP = {
    'f': 'feat', 'feat': 'feat', 'feature': 'feat',
    'a': 'arch', 'arch': 'arch', 'architecture': 'arch',
    'x': 'ux', 'ux': 'ux', 'design': 'ux',
    'b': 'api', 'api': 'api', 'backend': 'api',
    'u': 'ui', 'ui': 'ui', 'frontend': 'ui',
    'o': 'ops', 'ops': 'ops', 'devops': 'ops'
}

ACTION_MAP = {'s': 'save', 'save': 'save', 'spec': 'save'}

CATEGORY_MAP = {
    'req': 'requirements', 'usr': 'users', 'scp': 'scope',
    'tech': 'technical', 'time': 'timeline', 'risk': 'risks',
    'exist': 'existing', 'ok': 'success', 'all': 'all'
}
```

**Colon notation:** `d:5` → `parse_depth_with_count()` → `('deep', 5)`

**Decision logic:**

| Input Pattern | Behavior |
|---------------|----------|
| Full args (depth + focus + topic) | Execute directly |
| Topic only | Show Q1: Depth → Q2: Focus → execute |
| No arguments | Smart context detection (Step 0.5) |
| `--orch` flag | Delegate to orchestrator (Step 0-orch) |

### Step 0-orch: Check for --orch Flag (v2.5.0)

If `--orch` present, delegate to `utils/orch_flag_handler.py`:

- `handle_orch_flag()` → determine mode
- `--dry-run` → `show_orchestration_preview()` then return
- Otherwise → `spawn_orchestrator()` then return

### Step 0.5: Smart Context Detection (No Arguments)

**New session?** → Check for resumable sessions, offer resume or start fresh.

**Detection sources** (by priority):

1. Previous sessions (new session only)
2. Conversation topics
3. Project `.STATUS` file
4. Git branch name
5. Recent commits (last 24h)

**Logic:**

- 1 topic detected → use directly, skip to Q1: Depth
- 2-4 topics → AskUserQuestion: "Which topic?"
- 0 or 5+ → Ask free-form: "What would you like to brainstorm?"

### Step 1: Interactive Menu (Topic Provided, No Mode)

**Q1: Depth** → AskUserQuestion with options: default (Recommended), quick, thorough

**Q2: Focus** → AskUserQuestion with options: auto-detect (Recommended), feature, architecture, backend

Users wanting frontend/design/devops select "Other".

### Step 1.5: "Ask More?" (All Depths)

After base questions, offer escape hatch:

| Depth | Options |
|-------|---------|
| quick (0 Qs) | Go! / Ask 2 first / Switch to deep / Switch to max |
| default (2 Qs) | Start brainstorming / 2 more / Switch to deep / Switch to max |
| deep (8 Qs) | Start brainstorming / 2 more / Switch to max |
| max (8 Qs + agents) | Generate plan / 2 more / Re-run agents |

**Milestone prompts (v2.4.0):** For counts > 8, prompt every 8 questions. Options: Done, +4 more, +8 more, Keep going (unlimited mode prompts every 4).

### Step 1.7: Context Scan (NEW v2.15.0)

Before presenting questions, scan project state and pre-fill/skip:

```python
from utils.brainstorm_context import BrainstormContext

ctx = BrainstormContext(project_path)
context = ctx.scan(topic)

# context.pre_filled_answers: {category: answer}
# context.matching_spec: Optional[str]  (path to matching spec)
# context.prior_brainstorm: Optional[str]  (path to prior brainstorm)
# context.project_type: Optional[str]  (detected project type)
# context.dynamic_questions: List[dict]  (state-triggered questions)
```

**Behavior changes:**

| Scenario | Current | New |
|----------|---------|-----|
| SPEC exists for topic | Ask all questions | "Found SPEC — load as context?" Skip if yes |
| `.STATUS` has version | Generic constraints Q | Pre-fill: "Current version: vX.Y.Z" |
| Git shows test failures | No awareness | Dynamic Q: "Recent tests failing — address first?" |
| Prior brainstorm exists | No awareness | "Found prior brainstorm — resume or start fresh?" |
| Project type detected | Generic questions | Add 2 project-type questions |

**Smart question selection:**

1. Filter by requested categories
2. Add project-type questions (from `utils/brainstorm_context.py`)
3. Pre-fill from context (mark skippable)
4. Insert dynamic questions (failing tests, matching spec, prior brainstorm)
5. Trim to requested count

### Step 1.8: Insights Integration (v2.20.0)

Before brainstorming, check session insights for relevant past patterns.

**Check:** Read `~/.claude/usage-data/facets/` for sessions matching the topic or project.

**If relevant sessions found** (same project or similar topic keywords):

```text
Previous session insights (craft, last 30 days):
  12 sessions on this project
  Top friction: wrong CWD (8x), forgot ORCHESTRATE (3x)
  Suggested guardrails applied to this brainstorm context
```

**Behavior changes:**

| Scenario | Effect on Brainstorm |
|----------|---------------------|
| Friction patterns found for project | Add "Known Friction" section to brainstorm output |
| Prior sessions on same topic | Show "Previous approaches" summary, offer to build on them |
| No insights data | Skip silently (no user prompt) |

**Integration with spec generation (Step 5.5):**

When insights exist and a spec is being captured, auto-add a "Known Risks" section to the spec based on observed friction patterns:

```markdown
## Known Risks (from session insights)

- Wrong CWD — 8 occurrences in 30 days. Add explicit CWD verification step.
- Count drift — 2 occurrences. Add validate-counts to acceptance criteria.
```

### Step 2: Gather Context

If topic not from args, detect from project type, git branch, directory context.

### Step 3: Execute Brainstorm

Based on selected focus + depth. Each focus mode has specific output sections:

| Focus | Key Output |
|-------|------------|
| feat | User stories, MVP split, quick wins, implementation order |
| arch | Component diagram (Mermaid), data flow, scalability, trade-offs |
| ux | Wireframes (ASCII), component structure, accessibility checklist |
| api | API endpoints, schema design, security checklist, integration patterns |
| ui | Component tree, state management, bundle optimization |
| ops | Deployment pipeline, platform recs, cost estimates, monitoring |

### Step 4: Format Output

- **terminal** (default): Rich box-drawing output with summary
- **json**: Structured JSON with metadata + content + recommendations
- **markdown**: Saves to `BRAINSTORM-[topic]-[date].md`

### Step 5: Save & Show Results

Always save to file. Show footer with related commands and file locations.

### Step 5.5: Spec Capture (v2.3.0)

**Trigger conditions:**

| Condition | Behavior |
|-----------|----------|
| `save` action explicit | Always capture (no prompt) |
| Focus is feat/arch/api, no action | Prompt to capture |
| Depth is quick, no action | Skip prompt |

If capturing: ask user type → ask acceptance criteria → generate SPEC.md from template → save to `docs/specs/SPEC-[topic]-[date].md`.

**IMPORTANT:** Generate comprehensive specs with ALL template sections. Mark N/A sections explicitly.

### Step 6: Create Orchestration? (v2.20.0)

After spec capture, offer to create an ORCHESTRATE file and worktree.

**Trigger conditions:**

| Condition | Behavior |
|-----------|----------|
| Spec was captured in Step 5.5 | Always prompt |
| No spec captured | Skip this step |

Prompt:

```json
{
  "questions": [{
    "question": "Create orchestration plan from this spec?",
    "header": "Orchestrate",
    "multiSelect": false,
    "options": [
      {"label": "ORCHESTRATE + worktree (Recommended)", "description": "Generate ORCHESTRATE file and create worktree for isolated development."},
      {"label": "ORCHESTRATE only", "description": "Generate ORCHESTRATE file in docs/orchestrate/ directory."},
      {"label": "Skip", "description": "Just keep the spec. Create orchestration later with /craft:orchestrate:plan."}
    ]
  }]
}
```

**When "ORCHESTRATE + worktree" selected:**

Invoke `/craft:orchestrate:plan <spec-path>` with the spec path from Step 5.5. This creates the ORCHESTRATE file and worktree in one flow.

**When "ORCHESTRATE only" selected:**

Invoke `/craft:orchestrate:plan <spec-path> --output orchestrate-only`. Saves ORCHESTRATE file to current directory.

**When "Skip" selected:**

Show reminder: "You can create orchestration later with `/craft:orchestrate:plan <spec-path>`"

### Step 7: Suggest Workflow Documentation

After spec capture (and optional orchestration), suggest creating workflow docs. Trigger when spec was saved and focus was feat/arch/ops or depth was deep/max.

---

## Time Budget Guarantees

| Depth | Budget | Questions | Agents |
|-------|--------|-----------|--------|
| quick | < 60s | 0 + "ask more?" | None |
| default | < 300s | 2 + "ask more?" | None |
| deep | < 600s | 8 + milestones | None |
| max | < 1800s | 8 + agents + milestones | 2 per focus |

Context scan (Step 1.7) adds ~1-2s overhead.

## Agent Delegation (Max Mode)

| Focus | Agents Launched |
|-------|-----------------|
| feat | product-strategist |
| arch | backend-architect, database-architect |
| ux | ux-ui-designer |
| api | backend-architect, security-specialist |
| ui | frontend-specialist, performance-engineer |
| ops | devops-engineer |

Launch in background (non-blocking), synthesize after completion.

## Question Bank Summary

8 categories, 2 questions each = 16 base questions. See [full question bank](../../docs/specs/_archive/SPEC-brainstorm-question-bank.md).

| Category | Focus | Default For |
|----------|-------|-------------|
| requirements | Key requirements, constraints | feat, api, auto |
| users | Primary users, problems solved | feat, ux, auto |
| scope | In/out of scope, MVP | feat, arch, ux |
| technical | Tech stack, integrations | arch, api, ops, auto |
| timeline | Deadlines, milestones | ops |
| risks | Potential risks, edge cases | arch, ops |
| existing | Reusable code, dependencies | arch |
| success | Success metrics, acceptance | feat, api, ux, auto |

**Project-type extensions (v2.15.0):** 6 project types, 2 questions each = 12 additional questions. Auto-detected via `utils/claude_md_detector.py`. See [question bank spec](../../docs/specs/_archive/SPEC-brainstorm-question-bank.md#project-type-question-extensions-v2150).

## Integration

**Workflow family:** brainstorm → focus → next → stuck → done

**Connected:** `/craft:docs:workflow` (create implementation docs from spec)

**Uses:** AskUserQuestion (menus), Task (agent delegation), Write (saving), Read (context), `utils/brainstorm_context.py` (smart questions)

---

## References

- [Power User Tutorial](../../docs/tutorials/TUTORIAL-brainstorm-power-user.md) — Detailed examples and advanced patterns
- [Reference Card](../../docs/reference/REFCARD-BRAINSTORM.md) — Flowcharts and quick reference
- [Question Bank](../../docs/specs/_archive/SPEC-brainstorm-question-bank.md) — Full question text and selection algorithm
- [Version History](../../docs/VERSION-HISTORY.md#v240-2026-01-18---brainstorm-question-control-phase-1) — Brainstorm spec evolution (v2.1→v2.5)
