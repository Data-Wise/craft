# CLAUDE.md Conventions

Rules for authoring and maintaining CLAUDE.md files in Craft projects.

## Budget

- Default: **< 150 lines**
- Override via `claude_md_budget` in `.claude-plugin/plugin.json`
- Pre-commit hook enforces the budget

## Section Priority

### P0 — Always in CLAUDE.md (never cut)

| Section | Max Lines |
|---------|-----------|
| Header / TL;DR | 5 |
| Git Workflow | 15 |
| Quick Commands | 15 |
| Project Structure | 15 |
| Troubleshooting | 10 |
| Pointers (detail file links) | 10 |

### P1 — Include if under budget

Agents/routing table, execution modes, active development (branch + version only), key files.

### P2 — Never in CLAUDE.md

Release notes, feature matrices, per-test-file breakdowns, phase completion details, PR/merge details, diffstats.

## Anti-Patterns (Hard Blocks)

The `sync` command refuses to add these:

| Pattern | Detection |
|---------|-----------|
| Release notes | `^###? v\d+\.\d+` or `Released \d{4}` |
| Diffstats | `Files Changed:.*\+.*/-` |
| "What Shipped" | `What Shipped\|Merged PR` |
| Completed feature tables | `Status.*Complete\|Released` |
| Phase implementation details | `^### Phase \d` with completion markers |

## Pointer Format

```markdown
-> Full release history: [VERSION-HISTORY.md](docs/VERSION-HISTORY.md)
```

- Arrow prefix (`->`) makes pointers visually distinct
- Claude Code follows the markdown link to read the target on demand
- Use for any content moved to detail files

## Standard Detail Files

| File | Contains |
|------|----------|
| `docs/VERSION-HISTORY.md` | All release notes, changelogs, migration guides |
| `docs/ARCHITECTURE.md` | System design, component diagrams, data flows |
| `CONTRIBUTING.md` | Dev setup, testing guide, PR process |
| `docs/COMMANDS.md` | Full command/API reference with all options |

## Source

Full spec: [SPEC-claude-md-v3-optimization-2026-02-04.md](../specs/SPEC-claude-md-v3-optimization-2026-02-04.md)
