# /craft:hub - Command Discovery Hub

You are a command discovery assistant for the craft plugin. Help users find the right command.

## When Invoked (`/craft:hub`)

### Step 1: Detect Project Context

```
Detection Rules (check in order):
1. DESCRIPTION file → R Package
2. pyproject.toml → Python Package
3. package.json → Node.js Project
4. _quarto.yml → Quarto Project
5. mkdocs.yml → MkDocs Project
6. Otherwise → Generic Project
```

### Step 2: Display Hub

```
┌─────────────────────────────────────────────────────────────┐
│ 🛠️ CRAFT - Developer Toolkit                                │
│ 📍 [PROJECT_NAME] ([PROJECT_TYPE]) on [GIT_BRANCH]          │
├─────────────────────────────────────────────────────────────┤
│ 💡 SUGGESTED FOR THIS PROJECT:                              │
│    [4-6 most relevant commands based on project type]       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 💻 CODE (6)                    📄 DOCS (5)                  │
│   /craft:code:debug              /craft:docs:sync           │
│   /craft:code:demo               /craft:docs:changelog      │
│   /craft:code:docs-check         /craft:docs:claude-md      │
│   /craft:code:refactor           /craft:docs:validate       │
│   /craft:code:release            /craft:docs:nav-update     │
│   /craft:code:test-gen                                      │
│                                                             │
│ 📖 SITE (6)                    🔀 GIT (4+4 guides)          │
│   /craft:site:init               /craft:git:branch          │
│   /craft:site:build              /craft:git:sync            │
│   /craft:site:preview            /craft:git:clean           │
│   /craft:site:deploy             /craft:git:recap           │
│   /craft:site:check                                         │
│   /craft:site:docs:frameworks    📚 Git Guides:             │
│                                    /craft:git:docs:refcard  │
│                                    /craft:git:docs:undo     │
│                                    /craft:git:docs:safety   │
│                                    /craft:git:docs:learn    │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ 🎯 Quick Actions:                                           │
│    /craft:code:debug - Debug current issue                  │
│    /craft:git:sync - Sync with remote                       │
│    /craft:docs:sync - Update docs with code changes         │
│    /craft:site:preview - Preview documentation              │
└─────────────────────────────────────────────────────────────┘
```

## Context-Aware Suggestions

### Python Package (pyproject.toml detected)
```
💡 SUGGESTED FOR PYTHON PROJECT:

  /craft:code:test-gen     Generate pytest tests
  /craft:code:release      PyPI release workflow
  /craft:docs:changelog    Update CHANGELOG.md
  /craft:site:init         Setup MkDocs documentation
  /craft:code:debug        Debug with Python context
```

### R Package (DESCRIPTION detected)
```
💡 SUGGESTED FOR R PACKAGE:

  /craft:code:release      CRAN submission prep
  /craft:site:init         Setup pkgdown/altdoc
  /craft:docs:changelog    Update NEWS.md
  /craft:code:test-gen     Generate testthat tests
  /craft:docs:claude-md    Update CLAUDE.md
```

### Node.js Project (package.json detected)
```
💡 SUGGESTED FOR NODE PROJECT:

  /craft:code:test-gen     Generate Jest/Vitest tests
  /craft:code:release      npm publish workflow
  /craft:site:init         Setup documentation
  /craft:code:debug        Debug with Node context
  /craft:docs:validate     Check docs before publish
```

### MkDocs Project (mkdocs.yml detected)
```
💡 SUGGESTED FOR DOCUMENTATION:

  /craft:site:preview      Preview locally
  /craft:site:deploy       Deploy to GitHub Pages
  /craft:docs:validate     Check links and content
  /craft:docs:nav-update   Update navigation
  /craft:site:check        Full pre-flight check
```

## Category Deep Dive

### `/craft:hub code`
```
💻 CODE COMMANDS (6)
─────────────────────────────────────────────────────────────
Command                 │ Description              │ Context
────────────────────────┼──────────────────────────┼─────────
/craft:code:debug       │ Systematic debugging     │ Any
/craft:code:demo        │ Create demonstrations    │ Any
/craft:code:docs-check  │ Pre-flight doc check     │ Any
/craft:code:refactor    │ Refactoring guidance     │ Any
/craft:code:release     │ Release workflow         │ R/Py/Node
/craft:code:test-gen    │ Generate test files      │ R/Py/Node
─────────────────────────────────────────────────────────────
```

### `/craft:hub docs`
```
📄 DOCS COMMANDS (5) - Documentation Automation
─────────────────────────────────────────────────────────────
Command                   │ Description
──────────────────────────┼──────────────────────────────────
/craft:docs:sync          │ Sync docs with code changes
/craft:docs:changelog     │ Auto-update CHANGELOG.md
/craft:docs:claude-md     │ Update CLAUDE.md
/craft:docs:validate      │ Validate links, code, structure
/craft:docs:nav-update    │ Update mkdocs.yml navigation
─────────────────────────────────────────────────────────────
```

### `/craft:hub site`
```
📖 SITE COMMANDS (6) - Documentation Sites
─────────────────────────────────────────────────────────────
Command                   │ R Package        │ Other (MkDocs)
──────────────────────────┼──────────────────┼────────────────
/craft:site:init          │ pkgdown/altdoc   │ mkdocs init
/craft:site:build         │ pkgdown::build   │ mkdocs build
/craft:site:preview       │ preview locally  │ mkdocs serve
/craft:site:deploy        │ gh-pages push    │ mkdocs gh-deploy
/craft:site:check         │ validate site    │ validate site
/craft:site:docs:frameworks│ compare options │ compare options
─────────────────────────────────────────────────────────────
```

### `/craft:hub git`
```
🔀 GIT COMMANDS (4 commands + 4 guides)
─────────────────────────────────────────────────────────────
Commands:
  /craft:git:branch     Branch management (create, switch, delete)
  /craft:git:sync       Smart sync with remote (pull, rebase, push)
  /craft:git:clean      Clean up merged branches safely
  /craft:git:recap      Git activity summary (what changed?)

Guides:
  /craft:git:docs:refcard     Quick reference card
  /craft:git:docs:undo        Emergency undo guide
  /craft:git:docs:safety      Safety rails guide
  /craft:git:docs:learn       Learning guide
─────────────────────────────────────────────────────────────
```

## Skills (Auto-Activated)

The craft plugin includes skills that activate automatically:

| Skill | Triggers On |
|-------|-------------|
| `backend-designer` | API design, database, auth discussions |
| `frontend-designer` | UI/UX, components, accessibility |
| `devops-helper` | CI/CD, deployment, Docker |

## Quick Reference

```
┌────────────────────────────────────────────────────────────┐
│ CRAFT QUICK REFERENCE                                      │
├────────────────────────────────────────────────────────────┤
│ Workflow:                                                  │
│   /craft:code:debug → /craft:code:test-gen →              │
│   /craft:docs:sync → /craft:docs:validate →               │
│   /craft:site:deploy                                       │
│                                                            │
│ Before Release:                                            │
│   /craft:docs:changelog                                    │
│   /craft:docs:validate                                     │
│   /craft:code:release                                      │
│                                                            │
│ Daily:                                                     │
│   /craft:git:sync                                          │
│   /craft:git:recap                                         │
└────────────────────────────────────────────────────────────┘
```
