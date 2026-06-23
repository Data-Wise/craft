---
name: changelog-automation
description: Automate changelog generation from commits, PRs, and releases following Keep a Changelog format. Use when setting up release workflows, generating release notes, or standardizing commit conventions.
---

# Changelog Automation

Patterns and tools for automating changelog generation, release notes, and version management following industry standards.

## When to Use This Skill

- Setting up automated changelog generation
- Implementing Conventional Commits
- Creating release note workflows
- Standardizing commit message formats
- Generating GitHub/GitLab release notes
- Managing semantic versioning

## Core Concepts

### 1. Keep a Changelog Format

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New feature X

## [1.2.0] - 2024-01-15

### Added
- User profile avatars
- Dark mode support

### Changed
- Improved loading performance by 40%

### Deprecated
- Old authentication API (use v2)

### Removed
- Legacy payment gateway

### Fixed
- Login timeout issue (#123)

### Security
- Updated dependencies for CVE-2024-1234

[Unreleased]: https://github.com/user/repo/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/user/repo/compare/v1.1.0...v1.2.0
```

### 2. Conventional Commits

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

| Type | Description | Changelog Section |
|------|-------------|-------------------|
| `feat` | New feature | Added |
| `fix` | Bug fix | Fixed |
| `docs` | Documentation | (usually excluded) |
| `style` | Formatting | (usually excluded) |
| `refactor` | Code restructure | Changed |
| `perf` | Performance | Changed |
| `test` | Tests | (usually excluded) |
| `chore` | Maintenance | (usually excluded) |
| `ci` | CI changes | (usually excluded) |
| `build` | Build system | (usually excluded) |
| `revert` | Revert commit | Removed |

### 3. Semantic Versioning

```
MAJOR.MINOR.PATCH

MAJOR: Breaking changes (feat! or BREAKING CHANGE)
MINOR: New features (feat)
PATCH: Bug fixes (fix)
```

## Implementation

Six methods are available depending on language and automation level. For full configuration details, see [references/tool-configs.md](references/tool-configs.md).

| Method | Stack | Best For |
|--------|-------|----------|
| **1. Conventional Changelog** | Node.js (commitlint + husky) | Teams enforcing commit standards at the hook level |
| **2. standard-version** | Node.js | Semver bumping + changelog in one command |
| **3. semantic-release** | Node.js (fully automated) | CI-driven releases with zero manual steps |
| **4. GitHub Actions** | YAML workflow | Any stack — CI-native release pipelines |
| **5. git-cliff** | Rust (fast, template-based) | Custom changelog formats with Tera templates |
| **6. commitizen** | Python | Python projects needing interactive commit tooling |

Quick start for the most common case (semantic-release in CI):

```bash
npm install -D semantic-release @semantic-release/changelog @semantic-release/git
npx semantic-release
```

See [references/tool-configs.md](references/tool-configs.md) for complete configs for all six methods.

## Release Notes Templates

For GitHub Release and Internal Release Note templates, see [references/templates-and-examples.md](references/templates-and-examples.md).

## Commit Message Examples

For annotated examples covering scopes, issue references, breaking changes, and multi-paragraph bodies, see [references/templates-and-examples.md](references/templates-and-examples.md).

## Best Practices

### Do's

- **Follow Conventional Commits** - Enables automation
- **Write clear messages** - Future you will thank you
- **Reference issues** - Link commits to tickets
- **Use scopes consistently** - Define team conventions
- **Automate releases** - Reduce manual errors

### Don'ts

- **Don't mix changes** - One logical change per commit
- **Don't skip validation** - Use commitlint
- **Don't manual edit** - Generated changelogs only
- **Don't forget breaking changes** - Mark with `!` or footer
- **Don't ignore CI** - Validate commits in pipeline

## Resources

- [Keep a Changelog](https://keepachangelog.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [semantic-release](https://semantic-release.gitbook.io/)
- [git-cliff](https://git-cliff.org/)
