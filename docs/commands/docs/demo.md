# /craft:docs:demo

> **Terminal recording and GIF generator with dependency management**

---

## Synopsis

```bash
/craft:docs:demo "<feature>" [options]
```

**Quick examples:**

```bash
# Record a real terminal session (default: asciinema)
/craft:docs:demo "sessions"

# Generate a scripted VHS tape and convert to GIF
/craft:docs:demo "sessions" --method vhs --generate

# Check all required dependencies
/craft:docs:demo --check
```

---

## Description

Creates GIF demos of CLI features for documentation. Supports two recording methods: asciinema for real terminal sessions (default) and VHS for scripted, repeatable demos. Includes built-in dependency management to verify, install, and troubleshoot required tools.

Before generating any demo, the command expects you to test commands first, capture real output, and verify correctness. This ensures GIFs show actual, working behavior with realistic timing.

Philosophy: "Show, don't tell — but only show what actually works."

---

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--method` | Recording method: `asciinema` or `vhs` | `asciinema` |
| `--template` | VHS template: `command-showcase`, `workflow`, `before-after` | `command-showcase` |
| `--generate` | Record/generate AND convert to GIF in one step | `false` |
| `--watch` | Watch mode: auto-regenerate on tape file changes | `false` |
| `--preview` | Show recording guide without starting | `false` |
| `--check` | Validate all required dependencies | `false` |
| `--fix` | Auto-install missing dependencies | `false` |
| `--json` | Machine-readable JSON output (with `--check`) | `false` |
| `--convert` | Convert a single `.cast` file to `.gif` | — |
| `--batch` | Convert all `.cast` files in docs/ | `false` |
| `--force` | Overwrite existing GIF files | `false` |
| `--list-templates` | Show available VHS templates | `false` |

---

## How It Works

**asciinema method (default):**

1. Generates a recording guide with commands and expected output
2. You start `asciinema rec` manually and run the listed commands
3. Convert `.cast` to `.gif` with `agg`, then optimize with `gifsicle`

**VHS method (`--method vhs`):**

1. Selects a tape template based on feature type
2. Generates a `.tape` file in `docs/demos/`
3. With `--generate`, runs `vhs` and `gifsicle` automatically

**Dependency management:**

- `--check` shows a status table of all required tools with versions
- `--fix` installs missing tools via Homebrew, Cargo, or binary download
- Exit code `0` when all required tools are present, `1` when missing

---

## Required Tools

| Method | Tools |
|--------|-------|
| **asciinema** | `asciinema`, `agg`, `gifsicle`, `fswatch` (optional) |
| **vhs** | `vhs`, `gifsicle`, `fswatch` (optional) |

---

## See Also

- [/craft:docs:mermaid](mermaid.md) — Complementary visual documentation
- [/craft:docs:check](check.md) — Documentation health check
- [/craft:docs:update](update.md) — Update documentation
