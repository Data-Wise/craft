# /craft:site:deploy

> **Deploy documentation sites (Quarto, pkgdown, MkDocs) to GitHub Pages**

---

## Synopsis

```bash
/craft:site:deploy [--dry-run | -n]
```

**Quick examples:**

```bash
# Preview deployment without pushing
/craft:site:deploy --dry-run
/craft:site:deploy -n

# Execute deployment
/craft:site:deploy
```

---

## Description

Detects the documentation system in use (MkDocs, Quarto, or pkgdown) from
config files present in the repo, runs pre-deployment checks (site built,
git status clean, remote configured, GitHub Pages enabled), and deploys to
the `gh-pages` branch.

---

## Options

| Option           | Description                                     | Default |
|------------------|---------------------------------------------------|---------|
| `--dry-run`, `-n` | Preview the deployment plan without pushing       | `false` |

---

## Context Detection

| File            | Type    | Deploy Command             |
|-----------------|---------|------------------------------|
| `mkdocs.yml`    | MkDocs  | `mkdocs gh-deploy`           |
| `_quarto.yml`   | Quarto  | `quarto publish gh-pages`    |
| `_pkgdown.yml`  | pkgdown | Push `docs/` folder          |

---

## Pre-deployment Checks

1. **Site built** — verifies the output directory exists
2. **Git status** — checks for uncommitted changes
3. **Remote repository** — ensures a remote is configured
4. **GitHub Pages** — checks whether Pages is enabled

---

## Troubleshooting

| Symptom              | Likely cause / fix                                        |
|-----------------------|-------------------------------------------------------------|
| 404 after deployment | Wait 1-2 min for Pages to update; check base URL; verify Pages is enabled |
| Build failed         | Check GitHub Actions logs; verify dependencies; check for broken links |
| Permission denied    | Check repo permissions, GitHub token write access, branch protection on `gh-pages` |

---

## See Also

- [/folio:docs:site](https://github.com/Data-Wise/folio) — build, audit, and manage documentation sites (moved to `folio`)
- [/craft:ci:local](../ci/local.md) — check deployment/CI status locally
