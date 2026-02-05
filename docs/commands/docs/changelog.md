# /craft:docs:changelog

> **Auto-update CHANGELOG.md from git commits**

---

## Synopsis

```bash
/craft:docs:changelog [options]
```

**Quick examples:**

```bash
# Update changelog from last release
/craft:docs:changelog

# Generate entries since specific version
/craft:docs:changelog --since v2.11.0

# Preview without writing
/craft:docs:changelog --dry-run
```

---

## Description

Automatically generates and updates `CHANGELOG.md` by parsing git commits since the last release. Uses conventional commit message format (`feat:`, `fix:`, `docs:`, etc.) to categorize changes.

---

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--since` | Version tag or commit to start from | Last release tag |
| `--dry-run`, `-n` | Preview changelog without writing | `false` |

---

## Commit Message Format

Uses conventional commits for categorization:

| Prefix | Category | Example |
|--------|----------|---------|
| `feat:` | Features | `feat: add CLAUDE.md sync command` |
| `fix:` | Bug Fixes | `fix: repair broken link detection` |
| `docs:` | Documentation | `docs: update installation guide` |
| `refactor:` | Refactoring | `refactor: simplify complexity scorer` |
| `test:` | Tests | `test: add integration tests for sync` |
| `chore:` | Maintenance | `chore: update dependencies` |

---

## Output Format

Generates sections in this order:

1. **Breaking Changes** (commits with `BREAKING CHANGE:` footer)
2. **Features** (`feat:` commits)
3. **Bug Fixes** (`fix:` commits)
4. **Documentation** (`docs:` commits)
5. **Refactoring** (`refactor:` commits)
6. **Tests** (`test:` commits)
7. **Maintenance** (`chore:` commits)

---

## See Also

- [/craft:docs:sync](sync.md) — Smart documentation detection
- [/craft:docs:check](check.md) — Documentation health check
- [Site Management](../site.md) — Documentation site commands
