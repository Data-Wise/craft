---
name: brainstorm
description: Enhanced brainstorming with smart detection, design modes, time budgets, agent delegation, and spec capture for implementation
version: 2.4.0
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
---

# /workflow:brainstorm - Enhanced Brainstorm

ADHD-friendly brainstorming with smart mode detection, time budgets, agent delegation, and **spec capture for implementation**.

## Arguments (v2.4.0 - Question Control)

```
/brainstorm [depth:count] [focus] [action] [-C|--categories "cat1,cat2"] "topic"
                  ↑              ↑       ↑              ↑
                  │              │       │              └── req,users,scope,tech,timeline,risks,existing,success
                  │              │       └────────────────── s|save (capture as spec)
                  │              └─────────────────────────── f|feat|a|arch|x|ux|b|api|u|ui|o|ops
                  └────────────────────────────────────────── q|quick|d|deep|m|max (with optional :N for count)
```

### Depth Layer (v2.4.0 - Colon Notation)

| Full | Short | Count | Time | Description |
|------|-------|-------|------|-------------|
| (default) | - | 2 | < 5 min | Balanced, 2 questions + "ask more?" |
| quick | q | 0 | < 1 min | Fast, 0 questions + "ask more?" |
| quick:N | q:N | N | < 1 min | Quick with N questions |
| deep | d | 8 | < 10 min | Expert questions (8), no agents |
| deep:N | d:N | N | < 10 min | Deep with N questions |
| max | m | 8 | < 30 min | Expert questions + 2 agents |
| max:N | m:N | N | < 30 min | Max with N questions |

**Examples:**
- `/brainstorm d:5 "auth"` → Deep mode with exactly 5 questions
- `/brainstorm m:12 "api"` → Max mode with 12 questions
- `/brainstorm q:0 "quick"` → Quick with 0 questions (go straight to brainstorming)
- `/brainstorm d:20 "complex"` → Deep with 20 questions (unlimited mode)

**Note:** `thorough` is deprecated alias for `max`

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

**Synonyms:** `design` → `ux`, `backend` → `api`, `frontend` → `ui`, `devops` → `ops`

### Action Layer

| Full | Short | Single | What it does |
|------|-------|--------|--------------|
| (none) | - | - | Output BRAINSTORM.md only |
| save | save | s | Output SPEC.md (replaces --save-spec) |

**Synonym:** `spec` → `save`

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

**Examples:**
- `/brainstorm d:5 "auth" -C req,tech` → Deep with 5 questions from requirements + technical
- `/brainstorm m:10 f "api" --categories req,usr,tech,exist` → Max with 10 questions from 4 categories
- `/brainstorm d:4 "caching" -C tech,risk` → Deep with 4 questions from technical + risks
- `/brainstorm d:8 "feature" -C all` → Deep with 8 questions from all categories

### Quick Examples (v2.4.0)

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
/brainstorm feat save "auth"    # Feature + spec
/brainstorm f s "auth"          # Same (ultra-short)

# Full control
/brainstorm deep feat save "auth"   # Deep + feature + spec
/brainstorm d f s "auth"            # Power user mode

# Maximum depth
/brainstorm max arch save "auth"    # Max + architecture + spec
/brainstorm m a s "auth"            # Same (ultra-short)

# v2.4.0 - Colon notation for custom question counts
/brainstorm d:5 "auth"              # Deep with exactly 5 questions
/brainstorm m:12 "api"              # Max with 12 questions
/brainstorm q:0 "quick"             # Quick with 0 questions (straight to brainstorming)
/brainstorm d:20 "complex"          # Deep with 20 questions

# v2.4.0 - Categories flag to filter question types
/brainstorm d:5 "auth" -C req,tech  # 5 questions from requirements + technical
/brainstorm m:10 f "api" --categories req,usr,tech,exist
/brainstorm d:4 "caching" -C tech,risk
/brainstorm d:8 "feature" -C all    # All 8 categories

# Power user - full control
/brainstorm d:15 f s -C req,tech,success "auth"   # 15 questions, feature, spec, filtered categories
```

### Backward Compatibility

| Old Syntax (v2.2.0) | New Syntax (v2.4.0) | Status |
|---------------------|---------------------|--------|
| `--save-spec` | `save` or `s` | Deprecated but works |
| `--save-spec=full` | `save` (default is full) | Deprecated but works |
| `--save-spec=quick` | `q save` | Deprecated but works |
| `feature` | `feat` or `f` | Both work |
| `architecture` | `arch` or `a` | Both work |
| `thorough` | `max` or `m` | `thorough` deprecated |
| `d` (8 questions) | `d` or `d:8` | Both work |
| `m` (8 questions) | `m` or `m:8` | Both work |

**v2.4.0 Changes:**
- Colon notation `d:5`, `m:12` adds custom question counts
- Categories flag `-C req,tech` filters question types
- Existing syntax remains fully supported

## When Invoked

### Step 0: Parse Arguments (v2.4.0)

**Parsing Rules:**
1. Keywords can appear in any order before topic
2. Last quoted string is always the topic
3. Unquoted words are parsed using lookup tables

**Argument Mapping Tables:**

```python
# Normalize shortcuts
DEPTH_MAP = {
    'q': 'quick', 'quick': 'quick',
    'd': 'deep', 'deep': 'deep',
    'm': 'max', 'max': 'max',
    't': 'max', 'thorough': 'max'  # deprecated aliases
}

FOCUS_MAP = {
    'f': 'feat', 'feat': 'feat', 'feature': 'feat',
    'a': 'arch', 'arch': 'arch', 'architecture': 'arch',
    'x': 'ux', 'ux': 'ux', 'design': 'ux',
    'b': 'api', 'api': 'api', 'backend': 'api',
    'u': 'ui', 'ui': 'ui', 'frontend': 'ui',
    'o': 'ops', 'ops': 'ops', 'devops': 'ops'
}

ACTION_MAP = {
    's': 'save', 'save': 'save', 'spec': 'save'
}

CATEGORY_MAP = {
    'req': 'requirements', 'requirements': 'requirements',
    'usr': 'users', 'users': 'users',
    'scp': 'scope', 'scope': 'scope',
    'tech': 'technical', 'technical': 'technical',
    'time': 'timeline', 'timeline': 'timeline',
    'risk': 'risks', 'risks': 'risks',
    'exist': 'existing', 'existing': 'existing',
    'ok': 'success', 'success': 'success',
    'all': 'all'
}

def parse_depth_with_count(arg):
    """Parse depth:count notation (v2.4.0).

    Examples:
        'd:5' → ('deep', 5)
        'm:12' → ('max', 12)
        'q:0' → ('quick', 0)
        'd' → ('deep', None)  # Use default

    Returns:
        tuple: (depth_mode, question_count) or (depth_mode, None)
    """
    if ':' not in arg:
        return (DEPTH_MAP.get(arg, arg), None)

    parts = arg.split(':', 1)
    depth_str = parts[0]
    count_str = parts[1]

    depth = DEPTH_MAP.get(depth_str, depth_str)

    try:
        count = int(count_str)
        if count < 0:
            raise ValueError("Negative count")
        return (depth, count)
    except ValueError:
        return (depth, 'invalid')

def get_default_question_count(depth):
    """Get default question count for depth."""
    defaults = {
        'quick': 0,
        'default': 2,
        'deep': 8,
        'max': 8
    }
    return defaults.get(depth, 2)

def parse_categories(args):
    """Parse --categories or -C flag.

    Examples:
        --categories req,tech,success
        -C req,usr,scp
        --categories all

    Returns:
        list: Category names or None (all categories)
    """
    for i, arg in enumerate(args):
        if arg in ['--categories', '-C']:
            if i + 1 < len(args):
                cat_str = args[i + 1]
                if cat_str == 'all':
                    return None

                cats = [c.strip() for c in cat_str.split(',')]
                return [CATEGORY_MAP.get(c, c) for c in cats]

    return None
```
```

**Decision Logic:**
```
Colon notation?      → d:5, m:12, q:3 for custom question counts
Categories flag?     → --categories req,tech,success or -C req,tech
Topic provided?       → Show "Ask More?" then execute
Depth + Topic?        → Skip menus, show "Ask More?" then execute
Depth + Focus + Topic? → Skip menus, show "Ask More?" then execute
Full args (+ action)? → Execute directly (action bypasses "capture?" prompt)
No arguments?         → Smart context detection (Step 0.5)
```

**Examples (v2.4.0):**
| Input | Depth | Count | Categories | Behavior |
|-------|-------|-------|------------|----------|
| `/brainstorm "auth"` | default | 2 | all | "Ask More?" → execute |
| `/brainstorm d:5 "auth"` | deep | 5 | all | 5 questions → "Ask More?" → execute |
| `/brainstorm d:5 -C req,tech "auth"` | deep | 5 | req,tech | 5 questions from selected → execute |
| `/brainstorm m:12 f s "auth"` | max | 12 | auto | 12 questions → SPEC.md |
| `/brainstorm q f s "auth"` | quick | feat | save | "Ask More?" → SPEC.md |
| `/brainstorm` | - | - | - | Smart detect → menus → execute |

### Step 0.5: Smart Context Detection (No Arguments)

When no arguments provided, automatically detect topic from context:

#### New Session Detection

If this is a **new session** (no prior conversation), first check for resumable sessions:

```
1. Check if conversation history is empty (new session)
2. If new session → Invoke /resume behavior
3. Show recent sessions from before current session started
4. Let user pick a session to continue, or start fresh
```

```
AskUserQuestion:
  question: "Continue from a previous session or start fresh?"
  header: "Session"
  multiSelect: false
  options:
    - label: "Resume: [latest session topic]"
      description: "[project] - [time ago]"
    - label: "Resume: [2nd latest session]"
      description: "[project] - [time ago]"
    - label: "Start fresh"
      description: "New brainstorm in current context"
```

If user selects a previous session → load that context, then proceed to Q1: Depth.
If user selects "Start fresh" → proceed with normal detection below.

#### Detection Sources

| Source | What to look for | Priority |
|--------|------------------|----------|
| **Previous sessions** | Recent brainstorm sessions (new session only) | Highest |
| **Conversation** | Topics discussed, problems mentioned, features planned | High |
| **Git branch** | Branch name (e.g., `feature/oauth-login`) | Medium |
| **Recent commits** | Commit messages from last 24h | Medium |
| **Project .STATUS** | Current task, next steps | High |
| **Open discussion** | Questions asked, decisions pending | High |

#### Decision Logic

```python
topics = detect_topics_from_context()

if len(topics) == 1:
    # Clear single topic - use it directly
    topic = topics[0]
    → Proceed to Q1: Depth

elif len(topics) >= 2 and len(topics) <= 4:
    # Multiple topics - ask user to pick
    → AskUserQuestion: "Which topic?"
      options: [topic1, topic2, ..., "Other"]
    → Proceed to Q1: Depth

else:  # 0 topics or too many
    # No clear context - ask free-form
    → "What would you like to brainstorm?"
    → Proceed to Q1: Depth
```

#### Context Detection AskUserQuestion

When multiple topics detected:

```
AskUserQuestion:
  question: "Which topic should we brainstorm?"
  header: "Topic"
  multiSelect: false
  options:
    - label: "[Topic from conversation]"
      description: "Mentioned earlier in chat"
    - label: "[Topic from git branch]"
      description: "Current branch: feature/xyz"
    - label: "[Topic from .STATUS]"
      description: "Current project focus"
```

#### Example: Clear Context

```
[Earlier in conversation]
User: "I need to add user notifications to the app"

[Later]
User: /brainstorm

Claude: (detects single topic: "user notifications")
  → Skips topic question
  → Shows Q1: Depth
  → Shows Q2: Focus
  → Executes brainstorm for "user notifications"
```

#### Example: Multiple Topics

```
[Earlier in conversation]
User: "Working on OAuth and also need to refactor the DB"

[Later]
User: /brainstorm

Claude: [AskUserQuestion - Topic]
  "Which topic should we brainstorm?"
  ○ OAuth integration - Mentioned in conversation
  ○ Database refactoring - Mentioned in conversation
  ○ feature/auth-system - Current git branch

User: Selects "OAuth integration"

Claude: [Q1: Depth] → [Q2: Focus] → Execute
```

#### Example: No Context

```
[New conversation, no prior discussion]
User: /brainstorm

Claude: "What would you like to brainstorm?"
User: "A new caching layer"

Claude: [Q1: Depth] → [Q2: Focus] → Execute
```

### Step 1: Interactive Menu (Topic Provided, No Mode)

When topic is provided but no mode, show **two sequential AskUserQuestion calls** (max 4 options each).

#### Question 1: Depth Selection

```
AskUserQuestion:
  question: "How deep should the analysis be?"
  header: "Depth"
  multiSelect: false
  options:
    - label: "default (Recommended)"
      description: "< 5 min, comprehensive with options"
    - label: "quick"
      description: "< 1 min, fast ideation, no agents"
    - label: "thorough"
      description: "< 30 min, 2-4 agents for deep analysis"
```

#### Question 2: Focus Area Selection

```
AskUserQuestion:
  question: "What's the focus area?"
  header: "Focus"
  multiSelect: false
  options:
    - label: "auto-detect (Recommended)"
      description: "Detect from project context"
    - label: "feature"
      description: "User stories, MVP scope"
    - label: "architecture"
      description: "System design, diagrams"
    - label: "backend"
      description: "API, database, auth"
```

**Note:** Users wanting `frontend`, `design`, or `devops` select "Other" and type the mode name.

#### Menu Constraints

| Constraint | Value |
|------------|-------|
| **Max options per question** | 4 (AskUserQuestion limit) |
| **Max questions per call** | 4 |
| **Order** | Depth first, then Focus |
| **Default** | "(Recommended)" suffix on first option |
| **Overflow** | "Other" allows typing any mode |

#### Example Flow

```
User: /brainstorm "new auth system"

Claude: [AskUserQuestion - Depth]
  "How deep should the analysis be?"
  ○ default (Recommended) - < 5 min, comprehensive
  ○ quick - < 1 min, fast ideation
  ○ thorough - < 30 min, deep analysis

User: Selects "quick"

Claude: [AskUserQuestion - Focus]
  "What's the focus area?"
  ○ auto-detect (Recommended) - Detect from context
  ○ feature - User stories, MVP scope
  ○ architecture - System design, diagrams
  ○ backend - API, database, auth

User: Selects "feature"

Claude: Executes quick + feature brainstorm for "new auth system"
```

#### Direct Invocation (Skip Menus)

```bash
/brainstorm quick feature auth     # Explicit: depth + focus + topic
/brainstorm feature auth           # Focus + topic (default depth)
/brainstorm "my topic"             # Topic only (auto-detect all)
```

---

## ⏱️ Time Budget Guarantees

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

## 📋 Question Bank (v2.4.0)

Comprehensive 8-category question bank with 2 questions per category for context gathering.

### Question Categories

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

### Questions by Category

#### requirements
- **Q1:** "What are the key requirements for this feature?"
  - Performance-critical, User-facing functionality, Internal tooling, Data processing
- **Q2:** "Are there any hard constraints we must work within?"
  - Technology stack, Performance targets, Security requirements, Budget limits

#### users
- **Q3:** "Who is the primary user for this feature?"
  - End users, Developers, Administrators, Automated systems
- **Q4:** "What problem does this solve for them?"
  - Saves time, Improves accuracy, Enables new capability, Simplifies workflow

#### scope
- **Q5:** "What's definitely in scope for the first iteration?"
  - Core functionality, Basic error handling, Essential UI/UX, Documentation
- **Q6:** "What's explicitly out of scope (nice-to-have later)?"
  - Advanced features, Polish and refinement, Integrations, Scalability

#### technical
- **Q7:** "Are there technical constraints or preferences?"
  - Use existing stack, New technology needed, Architectural patterns, No strong preferences
- **Q8:** "What existing systems does this need to integrate with?"
  - Database, Authentication, APIs or services, None (standalone)

#### timeline
- **Q9:** "Are there any deadlines or milestones?"
  - ASAP (urgent), Specific date, Flexible timeline, Unknown
- **Q10:** "Is there a target date for first working version?"
  - Within a week, 1-2 weeks, 3-4 weeks, Flexible

#### risks
- **Q11:** "What could go wrong? What are the biggest risks?"
  - Technical complexity, Integration issues, Performance concerns, Unknown unknowns
- **Q12:** "Are there edge cases we should plan for upfront?"
  - Empty/invalid input, Concurrent access, Failure scenarios, None identified

#### existing
- **Q13:** "What existing code or systems can we leverage?"
  - Similar features, Libraries or frameworks, Infrastructure, Start from scratch
- **Q14:** "What dependencies does this have?"
  - Other features, External services, Data availability, None (self-contained)

#### success
- **Q15:** "How will we know this is successful?"
  - User feedback, Metrics, Tests pass, Requirements met
- **Q16:** "What are the acceptance criteria?"
  - Feature works as described, Tests validate behavior, Documentation exists, Performance acceptable

### Default Categories by Focus

| Focus | Default Categories |
|-------|-------------------|
| `feat` | requirements, users, scope, success |
| `arch` | technical, risks, existing, scope |
| `api` | technical, requirements, success |
| `ux` | users, scope, success |
| `ops` | technical, risks, timeline |
| `auto` | requirements, users, technical, success |

### Custom Categories

Use `--categories` or `-C` flag to specify which categories to include:

```bash
/brainstorm d:5 "auth" -C req,tech,success
/brainstorm m:10 f "api" --categories req,usr,tech,exist
/brainstorm d:4 "caching" -C tech,risk
```

Category shortcuts:
- `req` → requirements
- `usr` → users
- `scp` → scope
- `tech` → technical
- `time` → timeline
- `risk` → risks
- `exist` → existing
- `ok` → success
- `all` → all categories

---

### Step 1.5: "Ask More?" Feature (All Depths)

After base questions complete for ANY depth, offer escape hatch to go deeper or proceed:

#### For quick (0 questions)

```
Claude: ⚡ Ready to quick-brainstorm: [topic] ([focus] focus)

AskUserQuestion:
  question: "Dive straight in or gather context first?"
  header: "Start"
  multiSelect: false
  options:
    - label: "Go! - Start brainstorming (Recommended)"
      description: "Generate ideas immediately"
    - label: "Ask 2 questions first"
      description: "Quick context gathering"
    - label: "Switch to deep (8 questions)"
      description: "Detailed requirements gathering"
    - label: "Switch to max (8 + agents)"
      description: "Comprehensive analysis with agents"
```

#### For default (2 questions)

```
Claude: Quick context gathered!

[Shows summary of 2 answers]

AskUserQuestion:
  question: "Need more detail before brainstorming?"
  header: "Continue"
  multiSelect: false
  options:
    - label: "No - Start brainstorming (Recommended)"
      description: "Proceed with current context"
    - label: "Yes - 2 more questions"
      description: "Gather a bit more context"
    - label: "Yes - Switch to deep (8 questions)"
      description: "Full requirements gathering"
    - label: "Yes - Switch to max (8 + agents)"
      description: "Comprehensive with agents"
```

#### For deep (8 questions)

```
Claude: Detailed requirements gathered!

[Shows summary of 8 answers]

AskUserQuestion:
  question: "Ready to brainstorm or need more?"
  header: "Continue"
  multiSelect: false
  options:
    - label: "Ready - Start brainstorming (Recommended)"
      description: "Proceed with detailed context"
    - label: "Yes - 2 more questions"
      description: "Clarify specific points"
    - label: "Yes - Switch to max (add agents)"
      description: "Add expert agent analysis"
```

#### For max (8 questions + agent analysis)

```
Claude: Comprehensive analysis complete!

[Shows summary + agent findings]

AskUserQuestion:
  question: "Proceed with brainstorm?"
  header: "Continue"
  multiSelect: false
  options:
    - label: "Yes - Generate comprehensive plan (Recommended)"
      description: "Synthesize all findings"
    - label: "Wait - 2 more questions first"
      description: "Clarify before generating"
    - label: "Re-run agents with different focus"
      description: "Try different agent perspectives"
```

**Design Rationale:**
- **ADHD-friendly**: Always offer escape hatch, never feel trapped
- **Progressive disclosure**: Easy path forward, but depth available if needed
- **Consistent UX**: Same pattern at every depth level
- **No dead ends**: Can always go deeper OR proceed

#### Unlimited Questions + Milestone Prompts (v2.4.0)

When using colon notation with counts > 8 (e.g., `d:12`, `d:20`, `m:15`), questions are asked in batches with milestone prompts:

```python
def ask_questions_with_milestones(selected_questions, total_count):
    """Ask questions with milestone prompts every 8 questions.

    Args:
        selected_questions: List of questions to ask
        total_count: Total questions requested (or None for unlimited)

    Flow:
        - Ask questions in batches of 8
        - After each batch: continuation prompt
        - User can: proceed, add more, or keep going
    """
    answers = []
    asked = 0
    milestone = 8

    while asked < len(selected_questions):
        batch_end = min(asked + milestone, len(selected_questions))
        batch = selected_questions[asked:batch_end]

        for q in batch:
            answer = AskUserQuestion([q])
            answers.append(answer)
            asked += 1

        if total_count is not None and asked >= total_count:
            break

        if asked < len(selected_questions):
            continue_choice = ask_continuation_prompt(asked, total_count)

            if continue_choice == 'done':
                break
            elif continue_choice == 'add_4':
                continue
            elif continue_choice == 'add_8':
                continue
            elif continue_choice == 'keep_going':
                total_count = None
                continue

    return answers

def ask_continuation_prompt(questions_asked, total_count):
    """Show continuation prompt at milestone."""
    remaining = None
    if total_count:
        remaining = total_count - questions_asked

    summary = f"You've answered {questions_asked} questions. Good context so far!"

    options = [
        {"label": "Done - Start brainstorming (Recommended)", "description": "Proceed with current context"},
        {"label": "4 more questions", "description": "Add a few more details"},
        {"label": "8 more questions", "description": "Thorough exploration"},
        {"label": "Keep going until I say stop", "description": "I'll tell you when I'm done"}
    ]

    if remaining and remaining <= 4:
        options[1]["label"] = f"{remaining} more questions (finish)"
        options[2] = None

    result = AskUserQuestion({
        "question": "Continue gathering context or start brainstorming?",
        "header": "Continue",
        "multiSelect": False,
        "options": [o for o in options if o]
    })

    if "Done" in result:
        return 'done'
    elif "4 more" in result:
        return 'add_4'
    elif "8 more" in result or "finish" in result:
        return 'add_8'
    else:
        return 'keep_going'
```

**Milestone Prompt Examples:**

After 8 questions (d:12 mode):
```
You've answered 8 questions. Good context so far!

Continue gathering context or start brainstorming?
○ Done - Start brainstorming (Recommended)
○ 4 more questions
○ 8 more questions
○ Keep going until I say stop
```

After 16 questions (unlimited mode):
```
You've answered 16 questions. Comprehensive context!

Continue gathering context or start brainstorming?
○ Done - Start brainstorming (Recommended)
○ 4 more questions
○ Keep going until I say stop
```

**Key Behaviors:**
- **Prompts appear every 8 questions** in batch mode
- **Prompts every 4 questions** in "keep going" (unlimited) mode
- **Customizable additions**: Users can add 4, 8, or continue unlimited
- **Seamless integration**: Works with any initial count (d:5, d:12, d:20)

**Examples:**
- `/brainstorm d:12 "auth"` → 8 questions → milestone prompt → 4 more → proceed
- `/brainstorm d:20 "api"` → 8 → milestone → 8 → milestone → 4 → proceed
- `/brainstorm d:5 "quick"` → 5 questions → no milestone (under threshold)
- `/brainstorm m:15 "complex" -C req,tech` → 8 req → milestone → 7 tech → proceed

---

### Step 2: Gather Context

If topic not provided, analyze conversation context:

```bash
# Detect project type
ls DESCRIPTION package.json pyproject.toml go.mod 2>/dev/null

# Get current directory context
pwd
git branch --show-current 2>/dev/null
```

### Step 3: Execute Brainstorm

Based on selected mode + depth:

---

#### Mode: Feature

**Focus:** User value, functionality, MVP scope
**Default Depth:** default (< 5 min)
**Agent (thorough):** product-strategist

Output includes:
- User stories with acceptance criteria
- MVP vs Nice-to-have split
- Quick wins vs Long-term features
- Recommended implementation order

---

#### Mode: Architecture

**Focus:** System design, scalability, technical trade-offs
**Default Depth:** default or thorough
**Agents (thorough):** backend-architect, database-architect

Output includes:
- Component diagram (Mermaid)
- Data flow analysis
- Scalability considerations
- Trade-offs table

---

#### Mode: Design

**Focus:** UI/UX, accessibility, user experience
**Default Depth:** default
**Agent (thorough):** ux-ui-designer

Output includes:
- Wireframes (ASCII art)
- Component structure
- Accessibility checklist
- User flow diagram

---

#### Mode: Backend

**Focus:** API design, database schema, auth patterns
**Default Depth:** default
**Agents (thorough):** backend-architect, security-specialist

Output includes:
- API endpoints
- Schema design
- Security checklist
- Integration patterns

---

#### Mode: Frontend

**Focus:** Component architecture, state management, performance
**Default Depth:** default
**Agents (thorough):** frontend-specialist, performance-engineer

Output includes:
- Component tree
- State management strategy
- Bundle optimization
- Performance budget

---

#### Mode: DevOps

**Focus:** CI/CD, deployment, infrastructure
**Default Depth:** quick or default
**Agent (thorough):** devops-engineer

Output includes:
- Deployment pipeline
- Platform recommendations
- Cost estimates
- Monitoring strategy

---

### Step 4: Format Output

**Terminal Format (Default):**
```
┌─────────────────────────────────────────────────────────────┐
│ 🧠 BRAINSTORM: [Topic]                                      │
│ Mode: [mode] │ Depth: [depth] │ Duration: [time]            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ## Quick Wins (< 30 min each)                               │
│   ⚡ [Action 1] - [Benefit]                                  │
│   ⚡ [Action 2] - [Benefit]                                  │
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
├─────────────────────────────────────────────────────────────┤
│ ✅ Completed in [time]s (within [depth] budget)             │
└─────────────────────────────────────────────────────────────┘
```

**JSON Format (`--format json`):**
```json
{
  "metadata": {
    "timestamp": "2024-12-24T10:30:00Z",
    "mode": "feature",
    "depth": "quick",
    "duration_seconds": 45,
    "agents_used": []
  },
  "content": {
    "topic": "User notifications",
    "quick_wins": [],
    "medium_effort": [],
    "long_term": []
  },
  "recommendations": {
    "recommended_path": "...",
    "next_steps": []
  }
}
```

**Markdown Format (`--format markdown`):**
Saves to `BRAINSTORM-[topic]-[date].md`

---

### Step 5: Save & Show Results

Always save output to file:
- **Location:** Project root or `~/brainstorms/`
- **Filename:** `BRAINSTORM-[topic]-[date].md` or `.json`

Show footer:
```
┌─────────────────────────────────────────────────────────────┐
│ ✅ Done: [summary of brainstorm]                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 💡 Quick tip:                                               │
│    /workflow:brainstorm quick auth  ← skip menu             │
│                                                             │
│ 🔗 Related commands:                                        │
│    /workflow:focus       ← start focused work               │
│    /workflow:next        ← get next step                    │
│    /workflow:done        ← complete session                 │
│                                                             │
│ 📄 Files:                                                   │
│    BRAINSTORM-[topic]-[date].md  ← saved output             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### Step 5.5: Spec Capture (v2.3.0)

After showing results, capture as spec if `save` action was used, or prompt if certain focus modes.

#### When to Trigger

| Condition | Trigger |
|-----------|---------|
| `save` action provided (`s`, `save`, `spec`) | Always capture (no prompt) |
| Focus is `feat`, `arch`, `api` and no action | Prompt to capture |
| Depth is `quick` and no action | Skip prompt (too brief) |
| `--save-spec` flag (deprecated) | Always capture (backward compat) |

**v2.3.0 Change:** When `save` action is explicit, skip the "capture?" prompt entirely.

#### Spec Capture Question (Only When No Action)

```
AskUserQuestion:
  question: "Capture this brainstorm as a formal spec for implementation?"
  header: "Spec"
  multiSelect: false
  options:
    - label: "Yes - Full Spec (Recommended)"
      description: "User stories, technical requirements, UI/UX specs"
    - label: "Yes - Quick Spec"
      description: "User stories + key requirements only"
    - label: "No - Keep as Brainstorm"
      description: "Save brainstorm file only"
```

#### If User Selects Yes

Ask clarifying questions to fill spec template:

```
AskUserQuestion:
  question: "Who is the primary user for this feature?"
  header: "User Type"
  multiSelect: false
  options:
    - label: "Developer"
      description: "Building/integrating the feature"
    - label: "End User"
      description: "Using the feature directly"
    - label: "Admin"
      description: "Managing/configuring the feature"
```

Then ask for acceptance criteria:

```
AskUserQuestion:
  question: "What's the primary acceptance criterion?"
  header: "Acceptance"
  multiSelect: false
  options:
    - label: "Feature works as described"
      description: "Basic functionality complete"
    - label: "Tests pass"
      description: "Automated tests validate behavior"
    - label: "Documentation complete"
      description: "Usage docs available"
    - label: "Custom criterion"
      description: "Enter your own"
```

#### Generate Spec

**IMPORTANT: Generate comprehensive specs with ALL template sections. Mark sections as "N/A - Not applicable for this feature" if they don't apply.**

1. Load spec template from `workflow/templates/SPEC-TEMPLATE.md`
2. Fill in ALL sections from brainstorm output + user answers:

**Required Sections (Always Include):**

| Section | Content Source |
|---------|----------------|
| **Metadata** | Status: draft, Created: today, From Brainstorm: link |
| **Overview** | From brainstorm summary (2-3 sentences) |
| **Primary User Story** | From user type question + brainstorm goals |
| **Acceptance Criteria** | From brainstorm quick wins + requirements |
| **Secondary User Stories** | Additional user perspectives, or "N/A" |
| **Architecture** | Mermaid diagram from brainstorm structure |
| **API Design** | Endpoint table from backend requirements, or "N/A - No API changes" |
| **Data Models** | Schema from data requirements, or "N/A - No data model changes" |
| **Dependencies** | Libraries/tools from implementation plan |
| **UI/UX Specifications** | User flow, wireframes (ASCII), accessibility checklist, or "N/A - CLI only" |
| **Open Questions** | Unresolved items from brainstorm |
| **Review Checklist** | Standard checklist (always include) |
| **Implementation Notes** | Key considerations from brainstorm |
| **History** | Initial entry with today's date |

3. For each section:
   - If applicable: Fill with brainstorm content
   - If not applicable: Include section header with "N/A - [reason]"
   - Never omit sections entirely

4. Save to `docs/specs/SPEC-[topic]-[date].md`
5. Create `docs/specs/` directory if needed
6. Show confirmation with section summary

#### Spec Capture Output

```
┌─────────────────────────────────────────────────────────────┐
│ 📋 SPEC CAPTURED (Comprehensive)                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Spec: SPEC-auth-system-2025-12-30.md                        │
│ Type: Full Spec (all sections)                              │
│ From: BRAINSTORM-auth-system-2025-12-30.md                  │
│                                                             │
│ Sections:                                                   │
│   ✓ Overview                                                │
│   ✓ User Stories (1 primary, 2 secondary)                   │
│   ✓ Technical Requirements                                  │
│       ✓ Architecture (with diagram)                         │
│       ✓ API Design (table)                                  │
│       ✓ Data Models                                         │
│       ✓ Dependencies                                        │
│   ✓ UI/UX Specifications                                    │
│       ✓ User Flow (diagram)                                 │
│       ✓ Wireframes (ASCII)                                  │
│       ✓ Accessibility Checklist                             │
│   ⚠ Open Questions (2 items)                                │
│   ✓ Review Checklist                                        │
│   ✓ Implementation Notes                                    │
│   ✓ History                                                 │
│                                                             │
│ Status: draft                                               │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ 🔗 Next steps:                                              │
│    /spec:review auth-system   ← review & approve spec       │
│    /craft:do "implement auth" ← will use this spec          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Section Status Legend:**
- `✓` = Section filled with content
- `⚠` = Section needs review/has items
- `N/A` = Section marked not applicable (but still present)

#### Skip Spec Capture

If user selects "No" or mode is `quick`:
- Save only the brainstorm file
- Show standard footer (Step 5)

---

## Agent Delegation (Max Mode)

When depth is `max` (or deprecated `thorough`), launch relevant agents in background:

```python
# When max mode is active
if depth == "max":
    # Launch agents in background (non-blocking)
    backend_analysis = Task(
        subagent_type="backend-architect",
        prompt="Analyze backend architecture for [topic]",
        run_in_background=True,
        description="Backend analysis"
    )

    ux_analysis = Task(
        subagent_type="ux-ui-designer",
        prompt="Review UX design for [topic]",
        run_in_background=True,
        description="UX analysis"
    )

    # Continue with initial brainstorm while agents work
    initial_ideas = generate_initial_ideas()

    # Wait for agents to complete, then synthesize
    backend_results = TaskOutput(backend_analysis.task_id, block=True, timeout=1200000)
    ux_results = TaskOutput(ux_analysis.task_id, block=True, timeout=1200000)

    # Synthesize comprehensive plan
    synthesize_comprehensive_plan(initial_ideas, backend_results, ux_results)
```

### Agent Selection by Mode

| Mode | Agents Launched |
|------|-----------------|
| feature | product-strategist |
| architecture | backend-architect, database-architect |
| design | ux-ui-designer |
| backend | backend-architect, security-specialist |
| frontend | frontend-specialist, performance-engineer |
| devops | devops-engineer |

---

## Examples

### Example 1: Interactive Mode Selection

```
User: /workflow:brainstorm

Claude: Shows mode menu...
User: Selects "Feature (Recommended)"

Claude: Shows depth menu...
User: Selects "Quick (Recommended)"

Claude: "What topic would you like to brainstorm?"
User: "user authentication"

→ Runs feature + quick brainstorm for auth
→ Completes in 42s
→ Saves to BRAINSTORM-user-auth-2024-12-24.md
```

### Example 2: Direct Invocation (Skip Menu)

```
User: /workflow:brainstorm quick feature auth

→ Skips menus entirely
→ Runs feature mode with quick depth
→ Completes in 38s
```

### Example 3: Thorough Architecture Analysis

```
User: /workflow:brainstorm thorough architecture "multi-tenant SaaS"

→ Launches backend-architect agent (background)
→ Launches database-architect agent (background)
→ Generates initial ideas while agents work
→ Synthesizes comprehensive plan
→ Completes in 3m 24s
→ Saves detailed analysis with agent findings
```

### Example 4: JSON Output

```
User: /workflow:brainstorm feature notifications --format json

→ Runs feature brainstorm
→ Outputs JSON structure
→ Saves to BRAINSTORM-notifications-2024-12-24.json
```

### Example 5: Colon Notation (v2.4.0)

```
User: /workflow:brainstorm d:5 "auth system"

→ Deep mode with exactly 5 questions
→ Asks 5 questions from question bank
→ Shows "Ask More?" prompt
→ Proceeds to brainstorm
```

### Example 6: Categories Flag (v2.4.0)

```
User: /workflow:brainstorm d:5 "auth" -C req,tech

→ Deep mode with 5 questions from requirements + technical
→ Skips users, scope, timeline, risks, existing, success categories
→ More focused context gathering
```

### Example 7: Unlimited Questions with Milestones (v2.4.0)

```
User: /workflow:brainstorm d:20 "microservices"

→ Asks first 8 questions
→ Milestone prompt: "You've answered 8 questions. Continue?"
→ User selects "8 more questions"
→ Asks next 8 questions
→ Milestone prompt: "You've answered 16 questions. Continue?"
→ User selects "Done - Start brainstorming"
→ Proceeds to brainstorm with 16 questions of context
```

### Example 8: Power User (v2.4.0)

```
User: /workflow:brainstorm d:15 f s -C req,tech,success "payment api"

→ Deep mode with 15 questions
→ Feature focus with spec capture
→ Categories: requirements, technical, success only
→ Milestone prompts every 8 questions
→ Generates comprehensive plan with spec
```

---

## Mode Selection Flowchart

```mermaid
flowchart TD
    Start["/brainstorm"] --> HasArgs{Arguments?}

    HasArgs -->|None| NewSession{New session?}
    HasArgs -->|Topic only| DepthQ["🔘 Q1: Depth?"]
    HasArgs -->|Topic + mode| Execute
    HasArgs -->|Full args| Execute

    NewSession -->|Yes| ResumeQ["🔘 Q-1: Resume session?"]
    NewSession -->|No| SmartDetect["🔍 Smart Context Detection"]

    ResumeQ --> ResumeChoice{User selects}
    ResumeChoice -->|Resume session| LoadSession["Load previous context"]
    ResumeChoice -->|Start fresh| SmartDetect

    LoadSession --> DepthQ

    SmartDetect --> HowMany{Topics found?}
    HowMany -->|1 topic| AutoTopic["Use detected topic"]
    HowMany -->|2-4 topics| TopicQ["🔘 Q0: Which topic?"]
    HowMany -->|0 or 5+| AskTopic["Ask: What to brainstorm?"]

    AutoTopic --> DepthQ
    TopicQ --> DepthQ
    AskTopic --> DepthQ

    DepthQ --> SelectDepth{User selects}
    SelectDepth -->|default| DefaultDepth[default < 5 min]
    SelectDepth -->|quick| QuickDepth[quick < 1 min]
    SelectDepth -->|thorough| ThoroughDepth[thorough < 30 min]
    SelectDepth -->|Other| CustomDepth[Custom input]

    DefaultDepth --> FocusQ["🔘 Q2: Focus?<br/>(auto/feature/arch/backend)"]
    QuickDepth --> FocusQ
    ThoroughDepth --> FocusQ
    CustomDepth --> FocusQ

    FocusQ --> SelectFocus{User selects}
    SelectFocus -->|auto-detect| AutoFocus[Detect from context]
    SelectFocus -->|feature| FeatureFocus[Feature mode]
    SelectFocus -->|architecture| ArchFocus[Architecture mode]
    SelectFocus -->|backend| BackendFocus[Backend mode]
    SelectFocus -->|Other| CustomFocus[frontend/design/devops]

    ParseArgs --> Execute
    AutoFocus --> Execute
    FeatureFocus --> Execute
    ArchFocus --> Execute
    BackendFocus --> Execute
    CustomFocus --> Execute

    Execute[Execute Brainstorm] --> Format{Output format?}
    Format -->|terminal| Terminal[Rich output]
    Format -->|json| JSON[JSON file]
    Format -->|markdown| Markdown[Markdown file]

    Terminal --> Save[Save to file]
    JSON --> Save
    Markdown --> Save

    Save --> SpecQ{Spec capture?}
    SpecQ -->|--save-spec| SpecCapture[Capture as spec]
    SpecQ -->|feature/arch/backend| SpecPrompt["🔘 Q3: Capture as spec?"]
    SpecQ -->|quick/no| Report["Report time + next steps"]

    SpecPrompt -->|Yes - Full| SpecCapture
    SpecPrompt -->|Yes - Quick| QuickSpec[Quick spec capture]
    SpecPrompt -->|No| Report

    SpecCapture --> UserQ["🔘 Q4: User type?"]
    QuickSpec --> UserQ
    UserQ --> AcceptQ["🔘 Q5: Acceptance criterion?"]
    AcceptQ --> GenSpec[Generate SPEC.md]
    GenSpec --> SaveSpec[Save to docs/specs/]
    SaveSpec --> SpecReport[Spec capture report]
    SpecReport --> Report

    Report --> End[Complete]
```

### v2.4.0 Flow Additions

**Colon Notation Flow:**
```
ColonArgs["d:5, m:12, q:3"] --> ParseDepthCount["parse_depth_with_count()"]
ParseDepthCount --> Depth["deep (5 questions)"]
ParseDepthCount --> Max["max (12 questions)"]
```

**Categories Flag Flow:**
```
CategoriesFlag["-C req,tech"] --> ParseCategories["parse_categories()"]
ParseCategories --> FilterBank["Filter question bank"]
FilterBank --> SelectedQuestions["Selected questions"]
```

**Milestone Prompt Flow:**
```
BatchQuestions["Ask 8 questions"] --> MilestoneQ["🔘 Continue?"]
MilestoneQ --> UserChoice{User selects}
UserChoice -->|Done| Execute
UserChoice -->|4 more| BatchQuestions
UserChoice -->|8 more| BatchQuestions
UserChoice -->|Keep going| FrequentPrompts["Prompt every 4"]
FrequentPrompts --> BatchQuestions
```

---

## Version History

### v2.4.0 (Current)

**Question Control (Phase 1) - MVP:**
- ✅ Colon notation: `d:5`, `m:12`, `q:3` for custom question counts
- ✅ Categories flag: `--categories` or `-C` to filter question types
- ✅ Unlimited questions with milestone prompts every 8 questions
- ✅ Comprehensive 8-category question bank (16 questions total)

**New Question Categories:**
- requirements: Key requirements, constraints
- users: Primary users, problems solved
- scope: In/out of scope, MVP
- technical: Tech stack, integrations
- timeline: Deadlines, milestones
- risks: Potential risks, edge cases
- existing: Reusable code, dependencies
- success: Success metrics, acceptance criteria

**Colon Notation Examples:**
```bash
/brainstorm d:5 "auth"              # Deep with exactly 5 questions
/brainstorm m:12 "api"              # Max with 12 questions
/brainstorm q:0 "quick"             # Quick with 0 questions (straight to brainstorming)
/brainstorm d:20 "complex"          # Deep with 20 questions (milestone prompts)
```

**Categories Flag Examples:**
```bash
/brainstorm d:5 "auth" -C req,tech              # 5 questions from requirements + technical
/brainstorm m:10 f "api" --categories req,usr,tech,exist
/brainstorm d:4 "caching" -C tech,risk
```

**Backward Compatible:**
- All existing syntax still works
- `d` = `d:8` (deep with default 8 questions)
- `m` = `m:8` (max with default 8 questions)

### v2.3.1

**Three-Layer Argument System:**
- ✅ New syntax: `/brainstorm [depth] [focus] [action] "topic"`
- ✅ Depth layer: `q|quick`, `d|deep`, `m|max` (thorough deprecated)
- ✅ Focus layer: `f|feat`, `a|arch`, `x|ux`, `b|api`, `u|ui`, `o|ops`
- ✅ Action layer: `s|save` (replaces `--save-spec`)
- ✅ Single-letter shortcuts: `/brainstorm d f s "auth"`

**"Ask More?" Feature (All Depths):**
- ✅ Escape hatch at every depth level
- ✅ Can upgrade from quick → default → deep → max
- ✅ Can add 2 more questions at any depth
- ✅ ADHD-friendly: never feel trapped

**Enhanced Parsing:**
- ✅ Keywords can appear in any order
- ✅ Mapping tables for all aliases and synonyms
- ✅ Backward compatible with v2.2.0 syntax

**Migration from v2.2.0:**
```bash
# Old syntax (still works)
/brainstorm --save-spec "auth"
/brainstorm feature "auth"

# New syntax (recommended)
/brainstorm save "auth"          # or: /brainstorm s "auth"
/brainstorm feat "auth"          # or: /brainstorm f "auth"
/brainstorm d f s "auth"         # deep + feat + save
```

### v2.2.0

**Spec Capture Integration:**
- ✅ Added `--save-spec` flag for automatic spec capture
- ✅ Step 5.5: Spec capture flow after brainstorm
- ✅ Prompts for Full Spec or Quick Spec
- ✅ User type and acceptance criteria questions
- ✅ Saves to `docs/specs/SPEC-[topic]-[date].md`
- ✅ Links to `/spec:review` for approval workflow
- ✅ Updated flowchart with spec capture branch

**Triggers:**
- `--save-spec` flag → always capture
- `feature`, `architecture`, `backend` modes → prompt to capture
- `quick` mode → skip (too brief)

### v2.1.3

**AskUserQuestion Compliance:**
- ✅ Two-question flow (max 4 options each)
- ✅ Q1: Depth (default/quick/thorough)
- ✅ Q2: Focus (auto-detect/feature/architecture/backend)
- ✅ "Other" option for overflow modes (frontend/design/devops)
- ✅ Updated flowchart to match implementation

### v2.1.2

**Tab-Completion Menu Spec:**
- Tab-completion dropdown design (aspirational)
- Menu navigation spec

### v2.1.0

**Interactive Menu UX:**
- ✅ Two-step mode selection (depth + focus)
- ✅ Separated "depth" from "mode" for clarity
- ✅ Quick tip showing direct invocation
- ✅ Related commands in footer

**Backward Compatible:**
- ✅ All v2.0 direct invocations work unchanged
- ✅ `quick` and `thorough` still work as modes
- ✅ Default behavior preserved

**Migration:**
```bash
# Direct invocation (skip menus)
/brainstorm quick feature auth     # Explicit: depth + focus + topic
/brainstorm feature auth           # Focus + topic (default depth)
/brainstorm "my topic"             # Topic only (auto-detect all)

# Interactive (shows menus)
/brainstorm                        # Q1: Depth → Q2: Focus → Execute
```

---

### Step 6: Suggest Workflow Documentation (After Spec Capture)

When a spec is successfully captured (either via `save` action or user selection), suggest creating workflow documentation:

#### When to Trigger

| Condition | Trigger |
|-----------|---------|
| Spec was just saved | Always suggest |
| Focus was `feat`, `arch`, or `ops` | Suggest (multi-step processes) |
| Depth was `deep` or `max` | Suggest (thorough analysis) |
| Quick brainstorm, no spec | Skip suggestion |

#### Workflow Doc Suggestion

```
AskUserQuestion:
  question: "Create workflow documentation for implementing this feature?"
  header: "Workflow"
  multiSelect: false
  options:
    - label: "Yes - Create workflow docs (Recommended)"
      description: "Step-by-step implementation guide"
    - label: "No - Skip for now"
      description: "Can run /craft:docs:workflow later"
```

#### If User Selects Yes

```
→ Show: /craft:docs:workflow "[spec-topic]" --from-spec
```

**Example Flow:**
```
User: /brainstorm d f s "authentication"
       ↓
[Deep brainstorm + spec capture]
       ↓
Claude: Spec saved to docs/specs/SPEC-authentication-2026-01-14.md

AskUserQuestion: "Create workflow documentation for implementing this feature?"
  ○ Yes - Create workflow docs (Recommended)
  ○ No - Skip for now

User: Selects "Yes"

Claude: → /craft:docs:workflow "authentication" --from-spec

[Generates docs/workflows/authentication-workflow.md]
```

#### Updated Footer (After Spec Capture)

```
┌─────────────────────────────────────────────────────────────┐
│ 📋 SPEC CAPTURED                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Spec: SPEC-auth-2026-01-14.md                               │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ 🔗 Next steps:                                              │
│    /spec:review auth           ← review & approve spec      │
│    /craft:do "implement auth"  ← will use this spec         │
│    /craft:docs:workflow "auth" ← create implementation guide│
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Integration

**Part of workflow command family:**
- `/workflow:brainstorm` - Brainstorm ideas ← this command
- `/workflow:focus` - Start focused work session
- `/workflow:next` - Get next step
- `/workflow:stuck` - Get unstuck help
- `/workflow:done` - Complete session

**Connected to documentation:**
- `/craft:docs:workflow` - Create implementation workflow docs from spec
- `/craft:docs:update` - May trigger if scoring detects workflow needs

**Uses:**
- AskUserQuestion for mode and depth selection
- Task tool for agent delegation (thorough mode)
- Write tool for saving output
- Read tool for context gathering
