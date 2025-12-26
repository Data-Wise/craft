# Craft - Developer Toolkit Plugin

A comprehensive full-stack developer toolkit for Claude Code. Craft provides commands for code development, documentation, git workflows, and site management.

## Installation

```bash
# Clone the repository
git clone https://github.com/Data-Wise/claude-plugins.git

# Create symlink to install
ln -s /path/to/claude-plugins/craft ~/.claude/plugins/craft
```

## Commands (25 total)

### Code Commands (6)
| Command | Description |
|---------|-------------|
| `/craft:code:debug` | Systematic debugging assistance |
| `/craft:code:demo` | Create code demonstrations |
| `/craft:code:docs-check` | Pre-flight documentation check |
| `/craft:code:refactor` | Refactoring guidance |
| `/craft:code:release` | Release workflow (R/Python/Node) |
| `/craft:code:test-gen` | Generate test files |

### Documentation Commands (5) - NEW
| Command | Description |
|---------|-------------|
| `/craft:docs:sync` | Sync docs with code changes |
| `/craft:docs:changelog` | Auto-update CHANGELOG.md |
| `/craft:docs:claude-md` | Update CLAUDE.md |
| `/craft:docs:validate` | Validate links, code, structure |
| `/craft:docs:nav-update` | Update mkdocs.yml navigation |

### Site Commands (6)
| Command | Description |
|---------|-------------|
| `/craft:site:init` | Initialize documentation site |
| `/craft:site:build` | Build documentation site |
| `/craft:site:preview` | Preview site locally |
| `/craft:site:deploy` | Deploy to GitHub Pages |
| `/craft:site:check` | Validate site before deploy |
| `/craft:site:docs:frameworks` | Compare documentation frameworks |

### Git Commands (4 + 4 guides)
| Command | Description |
|---------|-------------|
| `/craft:git:branch` | Branch management |
| `/craft:git:sync` | Smart git sync |
| `/craft:git:clean` | Clean merged branches |
| `/craft:git:recap` | Git activity summary |

**Git Guides:**
- `/craft:git:docs:refcard` - Quick reference
- `/craft:git:docs:undo` - Emergency undo guide
- `/craft:git:docs:safety` - Safety rails
- `/craft:git:docs:learn` - Learning guide

### Discovery
| Command | Description |
|---------|-------------|
| `/craft:hub` | Command discovery hub |

## Skills (3)

Auto-activated skills that enhance responses:

| Skill | Triggers |
|-------|----------|
| `backend-designer` | API design, databases, authentication |
| `frontend-designer` | UI/UX, components, accessibility |
| `devops-helper` | CI/CD, deployment, Docker |

## Agents (1)

| Agent | Purpose |
|-------|---------|
| `orchestrator` | Coordinate complex tasks with parallel agent delegation |

## Quick Start

```bash
# Discover commands for your project
/craft:hub

# Debug an issue
/craft:code:debug

# Sync documentation with code changes
/craft:docs:sync

# Preview your documentation
/craft:site:preview

# Smart git sync
/craft:git:sync
```

## Workflows

### Daily Development
```
/craft:git:sync → work → /craft:code:test-gen → commit
```

### Documentation Update
```
/craft:docs:sync → /craft:docs:validate → /craft:site:preview
```

### Release Preparation
```
/craft:docs:changelog → /craft:docs:validate → /craft:code:release
```

## Project Detection

The plugin automatically detects project type and adjusts suggestions:

| Detection | Project Type |
|-----------|--------------|
| `DESCRIPTION` | R Package |
| `pyproject.toml` | Python Package |
| `package.json` | Node.js Project |
| `_quarto.yml` | Quarto Project |
| `mkdocs.yml` | MkDocs Project |

## Version

- **Version:** 1.0.0
- **Author:** DT (Data-Wise)
- **License:** MIT

## Related Plugins

- **workflow** - ADHD-friendly workflow commands
- **rforge** - R package development
- **statistical-research** - Research and analysis

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add commands to `commands/`
4. Test installation
5. Submit PR

## Changelog

### [1.0.0] - 2025-12-26
#### Added
- Initial release with 25 commands
- 6 code commands (migrated from user commands)
- 6 site commands (migrated from user commands)
- 8 git commands (migrated from user commands)
- 5 NEW documentation automation commands
- 3 skills (backend, frontend, devops)
- 1 orchestrator agent
- Hub command for discovery
