# Command & Spec Conventions

File formats and naming rules for commands, specs, skills, agents, and scripts.

## Command Files (`commands/*.md`)

YAML frontmatter followed by markdown body:

```yaml
---
description: Short description of what the command does
arguments:
  - name: task
    description: What this argument controls
    required: true
  - name: dry-run
    description: Preview without executing
    required: false
    default: false
    alias: -n
category: docs
---
```

Required fields: `description`. Optional: `arguments`, `category`.

## Spec Files (`docs/specs/SPEC-*.md`)

Naming: `SPEC-<feature-kebab>-<YYYY-MM-DD>.md`

Frontmatter (markdown bold fields, not YAML):

```markdown
**Status:** draft | implemented | superseded
**Created:** YYYY-MM-DD
**Implemented:** YYYY-MM-DD (PR #N -> branch)
**From Brainstorm:** BRAINSTORM-<name>.md
**Target Release:** vX.Y.Z
```

Standard sections: Overview, Architecture, Flags, Test Strategy, Migration Plan, Resolved Questions.

## Skills (`skills/*.md`)

Naming: `<skill-name>.md` (kebab-case). Frontmatter includes `name`, `description`, triggers.

## Agents (`agents/*.md`)

Naming: `<agent-name>.md` (kebab-case). Frontmatter includes `name`, `model`, `description`, `triggers` list.

## Scripts (`scripts/*.sh`)

Naming: **kebab-case, verb-first**

| Pattern | Examples |
|---------|----------|
| `<verb>-<noun>.sh` | `validate-counts.sh`, `sync-version.sh` |
| `<verb>-<noun>-<detail>.sh` | `docs-lint-emoji.sh` |
| `<noun>-<role>.sh` | `dependency-manager.sh`, `consent-prompt.sh` |

All scripts start with `#!/usr/bin/env bash` and `set -euo pipefail`.

## Naming Reference

| Artifact | Naming | Location |
|----------|--------|----------|
| Commands | `<category>/<name>.md` | `commands/` |
| Specs | `SPEC-<feature>-<date>.md` | `docs/specs/` |
| Skills | `<name>.md` (kebab) | `skills/` |
| Agents | `<name>.md` (kebab) | `agents/` |
| Scripts | `<verb>-<noun>.sh` (kebab) | `scripts/` |
| Utils | `<noun>_<detail>.py` (snake) | `utils/` |
| Tests | `test_<feature>.py` (snake) | `tests/` |
