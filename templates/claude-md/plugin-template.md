# CLAUDE.md - {plugin_name}

> **TL;DR**: {tagline}

**{command_count} commands** · **{skill_count} skills** · **{agent_count} agents** · [Documentation]({docs_url}) · [GitHub]({repo_url})

**Current Version:** v{version} (released {release_date})
**Documentation Status:** {docs_percent}% complete | **Tests:** {test_count} passing

## Quick Commands

| Task | Command |
|------|---------|
| command_table_placeholder | command_table_placeholder |

## Project Structure

```text
{plugin_name}/
├── .claude-plugin/     # Plugin manifest, hooks, validators
├── commands/           # {command_count} commands
{command_dirs}
├── skills/             # {skill_count} specialized skills
{skill_dirs}
├── agents/             # {agent_count} agents
{agent_dirs}
├── tests/              # {test_count} tests
{test_dirs}
└── docs/               # Documentation
{docs_dirs}
```

## Key Files

| File | Purpose |
|------|---------|
| key_files_placeholder | key_files_placeholder |

## Development Workflow

1. Make changes in relevant directory (commands/skills/agents)
2. Add tests in tests/
3. Run validation: `/craft:check`
4. Update docs: `/craft:docs:claude-md:sync`
5. Commit and push

## Testing

```bash
# Run all tests
python3 tests/test_{plugin_name}.py

# Run specific test
python3 tests/test_{plugin_name}.py -k test_name

# Run integration tests
python3 tests/test_integration_*.py
```

**Test Coverage:** {coverage}%

## Git Workflow

```text
main (protected) ← PR only
  ↑
dev (integration) ← Plan here, branch from here
  ↑
feature/* (worktrees) ← All implementation work
```

### Workflow Steps

| Step | Action | Command |
|------|--------|---------|
| 1. Plan | Analyze on `dev`, wait for approval | `git checkout dev` |
| 2. Branch | Create worktree for isolation | `/craft:git:worktree feature/<name>` |
| 3. Develop | Conventional commits | Small, atomic commits |
| 4. Integrate | Test → rebase → PR to dev | `gh pr create --base dev` |
| 5. Release | PR from dev to main | `gh pr create --base main --head dev` |

## Related Commands

{related_commands}

## Common Issues

| Issue | Fix |
|-------|-----|
| Tests failing | `python3 tests/test_{plugin_name}.py` |
| Stale CLAUDE.md | `/craft:docs:claude-md:sync` |
| Broken links | `/craft:docs:check-links` |

## References

-> Release history: [VERSION-HISTORY.md](docs/VERSION-HISTORY.md)
-> Architecture: [ARCHITECTURE.md](docs/ARCHITECTURE.md)
-> Command reference: [Commands]({docs_url}/commands/)
-> GitHub: [{plugin_name}]({repo_url})
