---
name: dist-extras
description: This skill should be used when the user asks to "publish to PyPI", "generate an install script", "curl install", "publish to Claude Code marketplace", "create marketplace.json", "PyPI trusted publishing", or needs help with non-Homebrew distribution channels (PyPI, curl-based installers, Claude Code marketplace). Covers Python package publishing, GitHub-release curl installers, and Claude Code plugin marketplace listings.
category: distribution
---

# Distribution Extras (PyPI / curl / Marketplace)

Channel-specific expertise for distribution paths that aren't covered by the
Homebrew skills (`homebrew-formula-expert`, `homebrew-multi-formula`,
`homebrew-setup-wizard`, `homebrew-workflow-expert`). Three distinct channels
are grouped here because each one alone is too small to warrant its own
top-level skill, and they share a common pattern: declarative manifest +
GitHub Actions workflow + pre-flight validation.

Use `distribution-strategist` first to pick a channel. Use this skill once a
channel is chosen and you need execution detail.

## When to use which channel

| Channel | Best for | Avoid when |
|---------|----------|------------|
| **PyPI** | Python libraries and CLIs; ecosystem-native `pip install` | Non-Python; binary-heavy distribution |
| **curl install** | Single-file CLIs with GitHub releases; quick-start docs | Security-sensitive envs (pipe-to-bash) |
| **Marketplace** | Claude Code plugins (`.claude-plugin/plugin.json` present) | Anything that isn't a Claude Code plugin |

## PyPI publishing

Channel concern: build sdist+wheel, publish to PyPI, automate via GitHub
Actions, validate package metadata before release.

### Subcommands (mirrors `/craft:dist:pypi`)

| Subcommand | Purpose |
|------------|---------|
| `validate` | Check `pyproject.toml`, classifiers, README rendering, version sanity |
| `setup` | Generate release workflow + walk user through trusted-publishing setup |
| `workflow` | Generate `.github/workflows/pypi-release.yml` (release-triggered) |
| `publish` | Build with `uv build` (or `python -m build`) and `twine upload` |
| `check` | Pre-flight: clean tree, version bumped, tag matches, CHANGELOG entry |

### Trusted publishing (preferred over API tokens)

PyPI's OIDC-based trusted publishing avoids long-lived tokens.

1. On PyPI: project → Publishing → Add a new pending publisher
2. Fields: GitHub owner/repo, workflow filename (`pypi-release.yml`),
   environment name (`pypi`)
3. In workflow: `permissions: id-token: write` + `pypa/gh-action-pypi-publish@release/v1`
4. No secret needed — OIDC handshakes the token at runtime

### Build tools

- **uv** (preferred for new projects) — `uv build` produces both sdist + wheel
- **build** (canonical) — `python -m build`
- **hatch / poetry / setuptools** — build backend declared in `pyproject.toml`

### Common failure modes

- Version on PyPI already exists (PyPI is append-only — bump and retry)
- README has reST/Markdown content-type mismatch — set `readme = "README.md"`
- Missing classifiers (license, Python versions) flagged by `twine check`
- Trusted publisher not registered before first run — workflow fails at upload

## curl install scripts

Channel concern: generate a portable `install.sh` that fetches a GitHub
release, detects platform, and installs to `~/.local/bin` (or user-chosen
prefix). Optionally append install instructions to README.

### Modes (mirrors `/craft:dist:curl-install`)

| Mode | Behavior |
|------|----------|
| `--type binary` | Download pre-built binary asset matching `OS-ARCH` |
| `--type source` | Clone repo or fetch source tarball, build locally |
| `--type auto` | Detect from repo (has release assets? → binary; else source) |
| `preview` | Print script to stdout without writing |
| `--update-readme` | Append a curl one-liner to README under "Installation" |

### Script invariants

Every generated script must:

- Start with `set -euo pipefail`
- Detect `uname -s` and `uname -m`, normalize `x86_64→amd64`, `aarch64|arm64→arm64`
- Fetch latest tag from `api.github.com/repos/<owner>/<repo>/releases/latest`
- Verify checksum (SHA256) against published checksum file when available
- Default `INSTALL_DIR="${INSTALL_DIR:-$HOME/.local/bin}"`, allow override
- Use color helpers (`info`/`success`/`error`) that degrade on non-tty

### Security notes

Curl-pipe-bash is a known anti-pattern in hardened environments. For users
who object, the generated script should also work via the canonical pattern:

```bash
curl -fsSL <url>/install.sh -o install.sh
less install.sh   # review
bash install.sh
```

Document both invocation styles in the README block.

## Claude Code marketplace

Channel concern: list a Claude Code plugin in a GitHub-hosted marketplace
that users add with `claude plugin marketplace add <owner>/<repo>`.

### Subcommands (mirrors `/craft:dist:marketplace`)

| Subcommand | Purpose |
|------------|---------|
| `init` | Generate `.claude-plugin/marketplace.json` from `plugin.json` |
| `validate` | Schema-check both `plugin.json` and `marketplace.json` |
| `test` | Local install/uninstall cycle via `claude plugin marketplace add` |
| `publish` | Push to GitHub default branch (marketplace polls the repo) |

### `marketplace.json` minimal shape

```json
{
  "name": "{org}-{plugin}",
  "owner": { "name": "...", "email": "..." },
  "metadata": { "description": "...", "version": "..." },
  "plugins": [{
    "name": "{plugin-name}",
    "source": { "source": "github", "repo": "{owner}/{repo}" },
    "description": "...",
    "version": "...",
    "homepage": "...",
    "repository": "...",
    "license": "MIT",
    "category": "development",
    "keywords": []
  }]
}
```

### Critical limitation: no build step on install

`claude plugin marketplace add` clones the repo — it does **not** run
`npm install`, `npm run build`, or any build step. Implications:

- Skills (`.md`) and commands (`.md`) work — they're inert files
- Agents (`.md`) work — same
- **MCP servers with a gitignored `dist/` won't work** — the server binary
  isn't on disk after clone. Solution: publish the MCP server to npm and
  reference via `npx -y @scope/package` in `.mcp.json`.
- Anything requiring a compile step must ship compiled or use a package
  registry as the actual delivery channel.

### Validation checklist

- [ ] `plugin.json` and `marketplace.json` versions agree
- [ ] All listed components (`commands/`, `skills/`, `agents/`, `.mcp.json`) exist
- [ ] No `dist/` / build artifacts referenced from gitignored paths
- [ ] `claude plugin marketplace add <test-path>` succeeds locally
- [ ] Plugin loads after install (`claude plugin list` shows it)

## Cowork & Desktop surfaces

The craft plugin ships to three independent surfaces. This section covers the Cowork and Desktop
surfaces — the Code surface (Claude Code CLI) is handled by the Homebrew and marketplace channels
above.

### The 3-surface model

| Surface | Runtime | Distribution channel | Gate |
|---------|---------|----------------------|------|
| **Code** | Claude Code CLI | Homebrew tap + GitHub marketplace | BLOCK |
| **Cowork** | Cowork platform | Cowork plugin registry (skills-first) | WARN |
| **Desktop** | Claude Desktop app | Desktop plugin store (DXT) | INFO |

A release is "fully shipped" when all BLOCK-gated surfaces report the expected version.
WARN surfaces (Cowork, brew-installed, Code-registered) are surfaced in the report but do not
gate the automated pipeline.

> **Registry vs. user model:** The `registry.json` tracks 8 surfaces; the user-facing "3-surface"
> view collapses them. Code aggregates git-tag, marketplace, tap, brew, code-registered, and
> aggregator; Cowork maps to the cowork surface (WARN); Desktop maps to desktop-ext (INFO).

### Code surface

Distributed via two channels (both BLOCK-gated):

- **Homebrew tap** (`data-wise/tap`) — `brew install data-wise/tap/craft`
- **GitHub marketplace** — `claude plugin marketplace add Data-Wise/craft`

The `aggregator-sync.yml` CI action keeps the Data-Wise aggregator marketplace in sync on every
`release: published` event (auto-merge PR, fail-loud on failure).

### Cowork surface

Cowork ships a skills-first subset of craft. The surface tracks craft via a separate GUI plugin
registry. Key behaviors:

- **Skills-first**: Cowork consumes `skills/` and `commands/` but may present them differently
  than Claude Code CLI.
- **Personal vs Org marketplace**: Cowork supports both personal and org-level marketplaces.
  The craft plugin is published under the Data-Wise org marketplace.
- **Install path**: `claude plugin marketplace add data-wise/craft` (Cowork variant) — the exact
  path is marketplace-specific and may differ from the Code CLI install command.
- **Manual update**: There is no automated propagation from the release pipeline to the Cowork
  store. After a release, the Cowork surface requires a manual store update. The pipeline emits
  a WARN with the Cowork report and a remind.

### Desktop surface

The Claude Desktop app ships plugins via its own DXT plugin store. Key behaviors:

- **DXT format**: Desktop plugins use the `.dxt` format (different from the Code CLI plugin format).
- **INFO only**: The Desktop surface is informational in the registry — no automated verify or
  block gate. The pipeline reports it but does not attempt automated verification.
- **Manual gate**: Before shipping, verify manually that the Desktop store version matches the
  release version.

### Surface registry

The `scripts/surfaces/registry.json` file is the source of truth for all surfaces. Use
`/craft:dist:surfaces` to view the full surface matrix and current gate states.

```bash
/craft:dist:surfaces              # verify + full human matrix
/craft:dist:surfaces --json       # machine JSON matrix (live data)
```

## Integration

Use with:

- `distribution-strategist` skill — pick the right channel first
- `homebrew-*` skills — when the project also distributes via Homebrew
- `/craft:check --for release` — pre-release validation across channels
- `/craft:code:release` — orchestrates version bump → tag → release across channels

## Cross-channel patterns

- **One canonical version**: derive from a single source (`pyproject.toml`,
  `plugin.json`, `package.json`); never hand-edit in multiple files
- **Tag triggers the workflow**: prefer GitHub Release published events
  over push-to-main for release workflows
- **Pre-flight before publish**: each channel has a `validate`/`check`
  subcommand — run it in CI before the release job
