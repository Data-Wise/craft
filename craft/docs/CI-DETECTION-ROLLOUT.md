# CI Detection Rollout Plan

Scheduled testing of `/craft:ci:detect` on all active dev-tools projects.

## Priority 1: Core Projects (Have Active Development)

| Project | Type | Status | Notes |
|---------|------|--------|-------|
| aiterm | Python/uv | ⬜ Pending | Main CLI tool, has existing CI |
| scribe | Tauri | ⬜ Pending | Desktop app, Rust + Vite |
| atlas | Node/npm | ⬜ Pending | Project state engine |
| flow-cli | Node/npm | ⬜ Pending | ZSH workflow plugin |

## Priority 2: MCP Servers

| Project | Type | Status | Notes |
|---------|------|--------|-------|
| statistical-research | MCP/Bun | ⬜ Pending | 14 tools, 17 skills |
| shell | MCP/Node | ⬜ Pending | Shell command execution |
| project-refactor | MCP/Node | ⬜ Pending | Safe project renaming |

## Priority 3: Python CLIs

| Project | Type | Status | Notes |
|---------|------|--------|-------|
| obsidian-cli-ops | Python/pip | ⬜ Pending | Multi-vault Obsidian CLI |
| nexus-cli | Python/pip | ⬜ Pending | Ecosystem coordination |

## Priority 4: Infrastructure

| Project | Type | Status | Notes |
|---------|------|--------|-------|
| homebrew-tap | Homebrew | ⬜ Pending | Formula distribution |
| data-wise.github.io | Static | ⬜ Skip | No CI needed |
| zsh-claude-workflow | ZSH Plugin | ⬜ Pending | Shell functions |

## Detection Validation Checklist

For each project, verify:
- [ ] Project type detected correctly
- [ ] Build tool/package manager identified
- [ ] Test framework found (if applicable)
- [ ] Python/Node versions appropriate
- [ ] Existing CI detected (if present)
- [ ] Recommended template makes sense

## Commands to Run

```bash
# Run detection on each project
cd ~/projects/dev-tools/aiterm && claude "/craft:ci:detect"
cd ~/projects/dev-tools/scribe && claude "/craft:ci:detect"
cd ~/projects/dev-tools/atlas && claude "/craft:ci:detect"
cd ~/projects/dev-tools/flow-cli && claude "/craft:ci:detect"
cd ~/projects/dev-tools/mcp-servers/statistical-research && claude "/craft:ci:detect"
cd ~/projects/dev-tools/homebrew-tap && claude "/craft:ci:detect"
cd ~/projects/dev-tools/obsidian-cli-ops && claude "/craft:ci:detect"
cd ~/projects/dev-tools/nexus-cli && claude "/craft:ci:detect"
```

## Results Log

### aiterm
- **Date:**
- **Type Detected:**
- **Issues:**

### scribe
- **Date:**
- **Type Detected:**
- **Issues:**

### atlas
- **Date:**
- **Type Detected:**
- **Issues:**

---
*Created: 2025-12-28*
*Last Updated: 2025-12-28*
