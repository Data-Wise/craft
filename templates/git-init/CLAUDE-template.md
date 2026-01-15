# CLAUDE.md - {{PROJECT_NAME}}

> **TL;DR**: **Always start work from `dev` branch.** Use feature branches for all development. Never commit directly to `main`.

**Repository:** [{{USER}}/{{REPO}}](https://github.com/{{USER}}/{{REPO}})

## Git Workflow

```
main (protected) ← PR only, never direct commits
  ↑
dev (integration) ← Plan here, branch from here
  ↑
feature/* ← All implementation work
```

### Workflow Steps

| Step | Action | Command |
|------|--------|---------|
| 1. Plan | Analyze on `dev`, wait for approval | `git checkout dev` |
| 2. Branch | Create feature branch | `git checkout -b feature/<name>` |
| 3. Develop | Conventional commits (`feat:`, `fix:`, etc.) | Small, atomic commits |
| 4. Integrate | Test → rebase → PR to dev | `gh pr create --base dev` |
| 5. Release | PR from dev to main | `gh pr create --base main --head dev` |

### Constraints

- **CRITICAL**: Always start work from `dev` branch (`git checkout dev`)
- **Never** commit directly to `main`
- **Never** write feature code on `dev`
- **Always** verify branch: `git branch --show-current`

## Quick Commands

| Task | Command |
|------|---------|
| Switch to dev | `git checkout dev` |
| Create feature | `git checkout -b feature/<name>` |
| Run tests | `# Add your test command` |
| Lint code | `# Add your lint command` |
| Build | `# Add your build command` |
| Create PR | `gh pr create --base dev` |

## Project Structure

```
{{REPO}}/
├── # Add your project structure here
└── .github/
    ├── workflows/
    │   └── ci.yml
    └── pull_request_template.md
```

## Key Files

| File | Purpose |
|------|---------|
| `.STATUS` | Project status and tracking |
| `CLAUDE.md` | Development guidelines (this file) |
| `.github/workflows/ci.yml` | CI/CD pipeline |

## Conventional Commits

This project uses [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `chore:` Maintenance tasks
- `test:` Test additions or fixes
- `refactor:` Code refactoring
- `perf:` Performance improvements

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Wrong branch | `git checkout dev` |
| Accidentally committed to main | `git reset HEAD~1` (before push) |
| Merge conflicts | Resolve manually, then `git rebase --continue` |
| Need to sync with remote | `git pull --rebase origin dev` |

## Links

- [GitHub Repository](https://github.com/{{USER}}/{{REPO}})
- [CI Status](https://github.com/{{USER}}/{{REPO}}/actions)
- [Issues](https://github.com/{{USER}}/{{REPO}}/issues)
