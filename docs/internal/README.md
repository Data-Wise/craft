# Internal Conventions

Documented conventions for Craft contributors and Claude sessions.

These capture patterns that are implicit in the codebase — the "how we do things here" that new contributors (human or AI) need to know but won't find in external docs.

## Documents

| File | Covers |
|------|--------|
| [CLAUDE-MD-CONVENTIONS.md](CLAUDE-MD-CONVENTIONS.md) | CLAUDE.md authoring rules, anti-patterns, pointer format, section priorities |
| [TEST-CONVENTIONS.md](TEST-CONVENTIONS.md) | `_check_*` + `test_*` wrapper pattern, CheckResult contract, pytest rules |
| [PYTHON-CONVENTIONS.md](PYTHON-CONVENTIONS.md) | Dataclass style, walrus operator chains, import patterns, naming |
| [COMMAND-SPEC-CONVENTIONS.md](COMMAND-SPEC-CONVENTIONS.md) | Command frontmatter, spec file format, script/skill/agent naming |

## What's NOT here

These topics are already documented elsewhere:

- **Branch workflow** — [CLAUDE.md](../../CLAUDE.md) + [CONTRIBUTING.md](../../CONTRIBUTING.md)
- **Commit format** — [CONTRIBUTING.md](../../CONTRIBUTING.md)
- **PR process** — [CONTRIBUTING.md](../../CONTRIBUTING.md)
- **Test wrapper pattern (full guide)** — [docs/guide/test-wrapper-pattern.md](../guide/test-wrapper-pattern.md)
