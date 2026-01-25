# Discovery Engine Usage Guide

## Overview

The discovery engine auto-detects all commands from the `commands/` directory, parses their metadata, and caches results for performance.

## Quick Start

```python
from commands._discovery import load_cached_commands, get_command_stats

# Load all commands (uses cache if fresh)
commands = load_cached_commands()

# Get statistics
stats = get_command_stats()
print(f"Total commands: {stats['total']}")
print(f"Categories: {stats['categories']}")
```

## API Reference

### `load_cached_commands() -> list[dict]`

Load commands from cache if fresh, else regenerate.

**Returns:** List of command metadata dictionaries

**Performance:**

- Cached: ~2ms
- First run: ~12ms

**Example:**

```python
commands = load_cached_commands()
for cmd in commands:
    print(f"{cmd['name']}: {cmd['description']}")
```

### `discover_commands() -> list[dict]`

Force regeneration of command metadata (ignores cache).

**Returns:** List of command metadata dictionaries

**Example:**

```python
from commands._discovery import discover_commands

# Force fresh scan
commands = discover_commands()
```

### `get_command_stats() -> dict`

Get summary statistics about commands.

**Returns:** Dictionary with:

- `total`: Total command count
- `categories`: Dict of category → count
- `with_modes`: Count of commands with mode support
- `with_dry_run`: Count of commands with dry-run argument
- `generated`: ISO timestamp of cache generation

**Example:**

```python
stats = get_command_stats()
print(f"Found {stats['total']} commands across {len(stats['categories'])} categories")
```

### `cache_commands(commands: list[dict]) -> None`

Save commands to cache file.

**Args:**

- `commands`: List of command metadata

**Side effects:** Writes `commands/_cache.json`

## Command Metadata Schema

Each command has the following fields:

### Required Fields

- `name` (str): Command identifier (e.g., "code:lint", "hub")
- `category` (str): Primary category (e.g., "code", "test", "docs")
- `description` (str): One-line summary
- `file` (str): Relative path from commands/ directory

### Optional Fields

- `subcategory` (str): Subcategory for grouping
- `modes` (list[str]): Supported execution modes (auto-detected from arguments)
- `arguments` (list[dict]): Command-line arguments from frontmatter
- `tutorial` (bool): Whether tutorial is available
- `tutorial_level` (str): Difficulty level ("beginner", "intermediate", "advanced")
- `tutorial_file` (str): Path to tutorial markdown
- `related_commands` (list[str]): Related command names
- `tags` (list[str]): Searchable tags
- `project_types` (list[str]): Applicable project types

## Filtering Commands

```python
commands = load_cached_commands()

# Get all commands in a category
code_commands = [c for c in commands if c['category'] == 'code']

# Get commands with mode support
mode_commands = [c for c in commands if 'modes' in c]

# Get commands with dry-run
dry_run_commands = [
    c for c in commands
    if 'arguments' in c
    and any(
        isinstance(arg, dict) and 'dry-run' in arg.get('name', '').lower()
        for arg in c['arguments']
    )
]

# Search by name
lint_cmd = next((c for c in commands if c['name'] == 'code:lint'), None)
```

## Cache Invalidation

The cache auto-invalidates when:

- `_cache.json` doesn't exist
- Any `.md` file in `commands/` is newer than cache file

**Manual regeneration:**

```python
from commands._discovery import discover_commands, cache_commands

# Force regenerate
commands = discover_commands()
cache_commands(commands)
```

## CLI Usage

```bash
# Run discovery and print statistics
python3 commands/_discovery.py
```

**Output:**

```text
Discovering commands...

Found 97 commands

Categories:
  arch: 4
  check: 1
  ci: 3
  code: 12
  ...

Statistics:
  Total: 97
  With modes: 11
  With dry-run: 29
  Generated: 2026-01-17T11:24:00.383464

✓ Done!
```

## Error Handling

The discovery engine handles errors gracefully:

- **Malformed frontmatter:** Skips file, prints warning
- **Missing required fields:** Auto-generates from content
- **Cache read errors:** Regenerates cache automatically

```python
try:
    commands = load_cached_commands()
except Exception as e:
    print(f"Error loading commands: {e}")
```

## Performance Optimization

### Best Practices

1. **Use `load_cached_commands()`** instead of `discover_commands()`
2. **Cache is automatic** - no manual management needed
3. **Call once per session** - store results in memory

### Benchmarks

| Operation | Time |
|-----------|------|
| Load from cache | ~2ms |
| First discovery | ~12ms |
| Parse single file | ~0.1ms |

## Integration Example

```python
from commands._discovery import load_cached_commands

def show_hub():
    """Display command hub."""
    commands = load_cached_commands()

    # Group by category
    categories = {}
    for cmd in commands:
        cat = cmd['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(cmd)

    # Display
    for cat, cmds in sorted(categories.items()):
        print(f"\n{cat.upper()} ({len(cmds)} commands)")
        for cmd in cmds:
            print(f"  {cmd['name']:30s} {cmd['description']}")
```

## Troubleshooting

### Cache not updating

```bash
# Delete cache manually
rm commands/_cache.json

# Regenerate
python3 commands/_discovery.py
```

### Commands not detected

Check that files:

- Are in `commands/` directory
- Have `.md` extension
- Don't start with `_` (reserved for internal files)

### Incorrect categories

Categories are inferred from file paths:

- `commands/code/lint.md` → category: "code"
- `commands/hub.md` → category: "hub"
- `commands/git/docs/refcard.md` → category: "git"

### Missing metadata

If frontmatter is missing:

- `name`: Auto-generated from filepath
- `category`: Auto-inferred from directory
- `description`: Extracted from heading or first paragraph

## Files

| File | Purpose |
|------|---------|
| `commands/_discovery.py` | Discovery engine implementation |
| `commands/_schema.json` | Metadata schema documentation |
| `commands/_cache.json` | Generated cache (gitignored) |
| `commands/_discovery_usage.md` | This usage guide |

## See Also

- [SPEC-craft-hub-v2-2026-01-15.md](../docs/specs/_archive/SPEC-craft-hub-v2-2026-01-15.md) - Full Hub v2.0 specification
- [_schema.json](_schema.json) - Complete metadata schema
