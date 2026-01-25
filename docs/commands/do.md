# /craft:do

> **Universal command that intelligently routes tasks to appropriate craft commands.**

---

## Synopsis

```bash
/craft:do <task description>
```

**Quick examples:**

```bash
# Feature development
/craft:do add user authentication

# Bug fixing
/craft:do fix the login redirect issue

# Code quality
/craft:do improve code quality

# Documentation
/craft:do update documentation
```

---

## Description

Analyzes your natural language task description and automatically routes to the right craft commands. No need to remember which commands to use - just describe what you want to do.

**Use cases:**

- Feature development workflows
- Bug fixing pipelines
- Code quality improvements
- Documentation generation
- Release preparation

**How it works:**

1. **Check Spec** - Look for existing spec matching task
2. **Analyze** - Parse task description for intent
3. **Route** - Select appropriate craft commands
4. **Execute** - Run commands in optimal order
5. **Report** - Summarize what was done

---

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

---

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

---

## Examples

### Feature Development

```bash
/craft:do add user authentication

# Routes to:
# 1. /craft:arch:plan - Design the feature
# 2. /craft:code:test-gen - Generate tests
# 3. /craft:git:branch - Create feature branch
```

**Output:**

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

### Bug Fixing

```bash
/craft:do fix the login redirect issue

# Routes to:
# 1. /craft:code:debug - Analyze the issue
# 2. /craft:test:run - Run related tests
# 3. /craft:git:sync - Commit fix
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

---

## Spec Integration

Before routing, `/craft:do` checks for existing specs that match the task.

### When Spec Found

```
AskUserQuestion:
  "Found spec for this task. How should we proceed?"

  ○ Review spec, then implement
  ○ Implement with spec context
  ○ Skip spec
  ○ Create new spec first
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
```

### No Spec Found

```
Note: No spec found for "user authentication"
      Consider: /workflow:brainstorm save "user authentication"
      Proceeding with standard routing...
```

---

## Tips

| Tip | Example |
|-----|---------|
| Be specific | "add OAuth2 login" vs "add auth" |
| Use domain keywords | auth, api, ui, db |
| Add mode hint if needed | "thoroughly test the api" |
| Create specs for complex features | `/brainstorm f s "feature"` |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Wrong commands selected | Be more specific in task description |
| Spec not found | Create one with `/brainstorm save "topic"` |
| Commands failing | Run individual commands for detailed errors |
| Missing dependencies | Run `/craft:check` first |

---

## See Also

- **Planning:** `/craft:arch:plan` - Architecture planning
- **Brainstorming:** `/workflow:brainstorm` - Idea generation with spec capture
- **Validation:** `/craft:check` - Pre-flight checks
- **Workflow:** [Feature Development](../workflows/git-feature-workflow.md)
