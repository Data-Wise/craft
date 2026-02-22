# Homebrew Quick Reference

```
┌─────────────────────────────────────────────────────────────┐
│  HOMEBREW AUTOMATION QUICK REFERENCE                         │
├─────────────────────────────────────────────────────────────┤
│  Command: /craft:dist:homebrew                               │
│  Subcommands: 6 (formula, workflow, audit, setup,            │
│                   update-resources, deps)                     │
│  Config: .craft/homebrew.json                                │
│  Workflow: .github/workflows/homebrew-release.yml            │
└─────────────────────────────────────────────────────────────┘
```

## Subcommands at a Glance

| Command | What It Does |
|---------|-------------|
| `/craft:dist:homebrew setup` | 4-step wizard: detect, formula, workflow, token |
| `/craft:dist:homebrew formula` | Generate/update Ruby formula file |
| `/craft:dist:homebrew workflow` | Create hardened GitHub Actions workflow |
| `/craft:dist:homebrew audit` | Run `brew audit` + auto-fix patterns |
| `/craft:dist:homebrew audit --build` | Audit + build from source |
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

## Release Integration (Step 10)

The `/release` skill auto-updates the tap formula:

1. Read `.craft/homebrew.json` for formula name and tap
2. Download release tarball, calculate `sha256sum`
3. Validate SHA is 64 hex chars
4. Update formula via `sed`
5. Validate syntax with `ruby -c`
6. Commit and push to tap

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
- [Homebrew Installation](../guide/homebrew-installation.md)
- [Distribution Commands](../commands/dist.md)
- [Homebrew Setup Tutorial](../tutorials/TUTORIAL-homebrew-setup.md)
