# Homebrew Quick Reference

```
┌─────────────────────────────────────────────────────────────┐
│  HOMEBREW AUTOMATION QUICK REFERENCE                         │
├─────────────────────────────────────────────────────────────┤
│  Command: /craft:dist:homebrew                               │
│  Subcommands: 7 (formula, cask, workflow, audit, setup,      │
│                   update-resources, deps)                     │
│  Config: .craft/homebrew.json                                │
│  Workflow: .github/workflows/homebrew-release.yml            │
└─────────────────────────────────────────────────────────────┘
```

## Subcommands at a Glance

| Command | What It Does |
|---------|-------------|
| `/craft:dist:homebrew setup` | 4-step wizard: detect, formula/cask, workflow, token |
| `/craft:dist:homebrew formula` | Generate/update Ruby formula file |
| `/craft:dist:homebrew cask` | Generate/update Homebrew Cask for desktop apps (Tauri) |
| `/craft:dist:homebrew workflow` | Create hardened GitHub Actions workflow |
| `/craft:dist:homebrew audit` | Run `brew audit` + auto-fix (formula or cask) |
| `/craft:dist:homebrew audit --build` | Audit + build from source |
| `/craft:dist:homebrew audit --cask` | Force cask audit mode |
| `/craft:dist:homebrew audit --check-only` | Report issues without fixing |
| `/craft:dist:homebrew deps` | Inter-formula dependency graph |
| `/craft:dist:homebrew deps --system` | System dependencies matrix |
| `/craft:dist:homebrew deps --dot` | Graphviz DOT output |
| `/craft:dist:homebrew update-resources <name>` | Fix stale PyPI URLs |

## Config File

```json
// .craft/homebrew.json
{
  "formula_name": "craft",
  "tap": "data-wise/tap",
  "source_type": "github"
}
```

**Lookup chain:** `.craft/homebrew.json` > git remote > basename (fallback)

## Audit Auto-Fix Patterns

| Pattern | Auto-Fix |
|---------|----------|
| `Array#include?` | `.include?` |
| `assert_equal path` | `assert_path_exists` |
| `rescue StandardError` | bare `rescue` |
| caveats after test | move before test |
| long description | truncate to 80 chars |

## Workflow Security Features

| Feature | What It Prevents |
|---------|-----------------|
| `env:` indirection | Script injection |
| `sha256sum` | Wrong hash tool on Ubuntu |
| `--retry 3` | Transient download failures |
| 64-char SHA guard | Empty/truncated hashes |
| `ruby -c` check | Corrupted formula |

## Common Recipes

```bash
# First-time setup
/craft:dist:homebrew setup

# Pre-release validation
/craft:dist:homebrew audit --build

# Check what depends on what
/craft:dist:homebrew deps

# Fix PyPI URL drift
/craft:dist:homebrew update-resources aiterm

# Full release (auto-updates tap)
/release
```

## Desktop App Distribution (Cask)

| Command | What It Does |
|---------|-------------|
| `/craft:dist:homebrew cask` | Auto-detect Tauri, generate/update cask |
| `/craft:dist:homebrew cask --skip-build` | Update cask from existing release assets |
| `/craft:dist:homebrew cask --update-content` | Update postflight/caveats from CHANGELOG |
| `/craft:dist:homebrew cask --content-only` | Content-only (skip version/SHA256) |
| `/craft:dist:homebrew cask --dry-run` | Preview changes without writing |

**Detection:** `.craft/homebrew.json` `"type": "cask"` > `src-tauri/tauri.conf.json` > tap structure

**Build:** Serial multi-arch (aarch64 native first, then x64 cross-compile)

**SHA256:** From local build artifacts (not GitHub CDN)

## Release Integration (Step 10)

The `/release` skill auto-detects formula vs cask and routes accordingly:

**Formula (Step 10a):**

1. Read `.craft/homebrew.json` for formula name and tap
2. Download release tarball, calculate `sha256sum`
3. Validate SHA is 64 hex chars
4. Update formula via `sed`
5. Validate syntax with `ruby -c`
6. Commit and push to tap

**Cask (Step 10b — Tauri desktop apps):**

1. Read `tauri.conf.json` for product name, version, identifier
2. Validate build environment (Rust targets, Tauri CLI, Xcode)
3. Build aarch64 (native) then x86_64 (cross-compile)
4. Verify architectures via `file` command
5. Compute SHA256 from local DMGs
6. Upload DMGs + CHECKSUMS.txt to GitHub release
7. Update cask file (version, SHA256, postflight, caveats)
8. Push tap with conflict resolution

## Quick Troubleshooting

| Issue | Fix |
|-------|-----|
| Wrong formula name | Add `.craft/homebrew.json` |
| SHA mismatch | `curl -sL <url> \| shasum -a 256 \| cut -d' ' -f1` |
| `rescue StandardError` | Use bare `rescue` |
| Description too long | Under 80 chars, no "A/An" |
| Script injection in workflow | Use `env:` block, not `${{ }}` in `run:` |

## See Also

- [Homebrew Automation Guide](../guide/homebrew-automation.md)
- [Desktop Release Guide](../guide/desktop-release.md)
- [Homebrew Installation](../guide/homebrew-installation.md)
- [Distribution Commands](../commands/dist.md)
- [Homebrew Setup Tutorial](../tutorials/TUTORIAL-homebrew-setup.md)
