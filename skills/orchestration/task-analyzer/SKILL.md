---
name: task-analyzer
description: This skill should be used when the user asks to "analyze a task", "route a command", "what craft command should I use", or describes a development task that needs routing to the appropriate craft workflow. Analyzes natural language task descriptions and maps them to optimal craft command sequences.
---

# Task Analyzer Skill

Expert in analyzing natural language task descriptions and routing to appropriate craft commands.

## When to Use

This skill is automatically activated when:

- User invokes `/craft:do <task>`
- User describes a development task
- Context suggests multi-step workflow needed

## Capabilities

### Intent Recognition

Identifies task intent from natural language:

| Intent | Keywords | Example |
|--------|----------|---------|
| **Create** | add, create, implement, build, new | "add user authentication" |
| **Fix** | fix, debug, resolve, repair, issue | "fix the login bug" |
| **Test** | test, verify, check, validate | "test the api endpoints" |
| **Document** | document, docs, readme, explain | "document the api" |
| **Release** | release, deploy, publish, ship | "prepare for release" |
| **Refactor** | refactor, clean, improve, optimize | "refactor the utils module" |
| **Review** | review, audit, analyze | "review the architecture" |

### Domain Detection

Identifies affected domain from context:

| Domain | Indicators | Commands |
|--------|------------|----------|
| **API** | api, endpoint, rest, graphql | arch:plan, code:test-gen |
| **UI** | ui, component, page, view | frontend-designer skill |
| **Database** | db, database, model, schema | backend-designer skill |
| **Auth** | auth, login, permission | arch:plan, code:test-gen |
| **Testing** | test, coverage, spec | test, test --coverage |
| **Docs** | docs, readme, changelog | docs:sync, docs:validate |

### Workflow Selection

Maps intent + domain to optimal command sequence:

```
Feature Workflow:
  1. /craft:arch:plan     - Design the feature
  2. /craft:code:test-gen - Generate tests (TDD)
  3. /craft:git:branch    - Create feature branch
  4. → Implementation     - User implements
  5. /craft:test          - Verify tests pass
  6. /craft:git:sync      - Commit changes

Bug Fix Workflow:
  1. /craft:code:debug    - Analyze the issue
  2. /craft:test debug    - Isolate in tests
  3. → Fix               - User implements fix
  4. /craft:test          - Verify fix
  5. /craft:git:sync      - Commit fix

Release Workflow:
  1. /craft:code:deps-audit  - Security scan
  2. /craft:test release     - Full test suite
  3. /craft:code:lint release - Comprehensive lint
  4. /craft:docs:changelog   - Update changelog
  5. /craft:code:release     - Release workflow
```

### Coded-Workflow Shape Detection (D7)

When a task description reads like a **fixed coded shape** —
decompose → cover N → verify M → synthesize — **suggest**
`/craft:orchestrate:workflow`, do **not** silently switch to it.

Detect the shape conservatively (the helper
`workflow_parse.detects_workflow_shape(text)` fires only when ≥3 of the four
stage categories appear, or the explicit `decompose…synthesize` chain is
present):

| Stage category | Trigger words |
|----------------|---------------|
| decompose | decompose, break down, split into, dimensions, for each |
| fan-out | fan out, in parallel, one per, cover each, per finding, reviewers |
| verify | verify, verifier, double-check, confirm each |
| synthesize | synthesize, aggregate, summarize, combine, merge findings |

**Suggest, never switch (routing-false-positive guard).** A lone "verify" or
"in parallel" must NOT route anywhere — auto-hijacking a task better served by
improvised `orchestrate` is the accepted residual risk. On a match, present a
*suggestion* the user confirms:

```
This looks like a fixed decompose → cover → verify → synthesize shape.
Consider: /craft:orchestrate:workflow (coded, schema-gated, resumable)
Or keep going with improvised orchestration. Which do you want?
```

| Input | Detected? | Action |
|-------|-----------|--------|
| "decompose into dimensions, review each in parallel, verify, synthesize" | yes | suggest `:workflow` |
| "fan out reviewers, verify findings, then summarize" | yes | suggest `:workflow` |
| "verify the login flow works" | no | route normally |
| "review the architecture" | no | route normally |

### Complexity Assessment

Determines task complexity for mode selection:

| Complexity | Indicators | Default Mode |
|------------|------------|--------------|
| **Simple** | Single file, quick fix | default |
| **Medium** | Few files, feature | default |
| **Complex** | Many files, architecture | debug |
| **Critical** | Release, security | release |

## Output Format

### Analysis Report

```
╭─ Task Analysis ─────────────────────────────────────╮
│ Input: "add user authentication"                   │
├─────────────────────────────────────────────────────┤
│ Intent: Create (feature)                           │
│ Domain: Authentication                             │
│ Complexity: Medium                                 │
│ Workflow: Feature Development                      │
├─────────────────────────────────────────────────────┤
│ Recommended Commands:                              │
│   1. /craft:arch:plan       Design auth system    │
│   2. /craft:code:test-gen   Generate auth tests   │
│   3. /craft:git:branch      Create feature/auth   │
╰─────────────────────────────────────────────────────╯
```

## Integration

Works with:

- `/craft:do` - Primary entry point
- `/craft:check` - Validation after workflows
- All category commands (code, test, arch, etc.)
- All design skills (backend, frontend, devops)

## Example Analyses

### Simple Task

```
Input: "fix typo in readme"
Analysis:
  - Intent: Fix
  - Domain: Documentation
  - Complexity: Simple
  - Command: Direct edit (no routing needed)
```

### Complex Task

```
Input: "implement oauth2 login with google"
Analysis:
  - Intent: Create (feature)
  - Domain: Authentication + API
  - Complexity: Complex
  - Workflow: Feature Development
  - Skills: backend-designer, devops-helper
  - Commands: arch:plan → code:test-gen → git:branch
```
