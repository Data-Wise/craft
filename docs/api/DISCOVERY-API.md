# Discovery Engine API Reference

**Version:** 2.0
**Module:** `commands/_discovery.py`
**Status:** Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Module Constants](#module-constants)
3. [Core Functions](#core-functions)
4. [YAML Parsing](#yaml-parsing)
5. [Category & Name Inference](#category--name-inference)
6. [Cache Management](#cache-management)
7. [Query Functions](#query-functions)
8. [Data Structures](#data-structures)
9. [Usage Examples](#usage-examples)
10. [Error Handling](#error-handling)

---

## Overview

The Discovery Engine provides auto-detection and caching for Craft commands. It scans the `commands/` directory recursively, parses YAML frontmatter from markdown files, and maintains a JSON cache for performance.

**Key Features:**
- Automatic command discovery from file system
- YAML frontmatter parsing (no external dependencies)
- JSON caching with auto-invalidation
- Category and subcategory organization
- Tutorial generation
- Related commands lookup

---

## Module Constants

### `COMMANDS_DIR`
```python
COMMANDS_DIR: str
```
**Description:** Absolute path to the `commands/` directory (same directory as the discovery module).

**Value:** Automatically set to `os.path.dirname(os.path.abspath(__file__))`

**Usage:**
```python
from commands._discovery import COMMANDS_DIR
print(f"Commands directory: {COMMANDS_DIR}")
```

### `CACHE_FILE`
```python
CACHE_FILE: str
```
**Description:** Absolute path to the cache file `commands/_cache.json`.

**Value:** `os.path.join(COMMANDS_DIR, "_cache.json")`

**Usage:**
```python
from commands._discovery import CACHE_FILE
if os.path.exists(CACHE_FILE):
    print("Cache exists")
```

---

## Core Functions

### `discover_commands()`

```python
def discover_commands() -> list[dict]:
```

**Description:** Auto-detect all commands from the file system by scanning `commands/**/*.md` recursively and parsing YAML frontmatter.

**Returns:**
- `list[dict]`: List of command metadata dictionaries

**Performance:**
- Uncached: ~12ms for 97 commands
- Linear scaling: O(n) with file count

**Example:**
```python
from commands._discovery import discover_commands

commands = discover_commands()
print(f"Found {len(commands)} commands")
# Output: Found 97 commands
```

**Scanned Metadata:**
- Required: `name`, `category`, `description`
- Optional: `subcategory`, `modes`, `arguments`, `tutorial`, `related_commands`, `tags`, `project_types`

**Error Handling:**
- Skips files starting with `_` (internal files)
- Logs warnings for parse failures but continues processing
- Infers missing metadata from file path and content

---

### `load_cached_commands()`

```python
def load_cached_commands() -> list[dict]:
```

**Description:** Load commands from cache if fresh, otherwise regenerate. Cache is considered stale if any `.md` file is newer than `_cache.json`.

**Returns:**
- `list[dict]`: List of command metadata dictionaries

**Performance:**
- Cached: <2ms (94% faster than target)
- Uncached: ~12ms (full scan + cache write)

**Cache Invalidation:**
1. Check if `_cache.json` exists
2. Compare cache mtime vs. newest `.md` file mtime
3. Regenerate if any file is newer
4. Gracefully fallback to full scan on corruption

**Example:**
```python
from commands._discovery import load_cached_commands

# Uses cache if fresh, regenerates if stale
commands = load_cached_commands()
```

**Error Handling:**
- Missing cache → Full scan
- Corrupt cache → Full scan with warning
- JSON parse error → Full scan

---

### `cache_commands()`

```python
def cache_commands(commands: list[dict]) -> None:
```

**Description:** Save commands to `_cache.json` for performance optimization.

**Parameters:**
- `commands` (list[dict]): List of command metadata dictionaries

**Returns:** None

**Cache Structure:**
```json
{
  "generated": "2026-01-17T10:30:00",
  "count": 97,
  "categories": {"code": 12, "test": 7, ...},
  "stats": {
    "total": 97,
    "with_modes": 29,
    "with_dry_run": 29
  },
  "commands": [...]
}
```

**Example:**
```python
from commands._discovery import discover_commands, cache_commands

commands = discover_commands()
cache_commands(commands)
print("Cache updated")
```

---

## YAML Parsing

### `parse_yaml_frontmatter()`

```python
def parse_yaml_frontmatter(content: str) -> dict:
```

**Description:** Extract YAML frontmatter from markdown file content. Manual parser without external dependencies.

**Parameters:**
- `content` (str): Full markdown file content

**Returns:**
- `dict`: Dictionary of frontmatter fields (empty dict if no frontmatter)

**Supported YAML Features:**
- Simple key-value pairs: `name: value`
- Arrays: `- item1\n- item2`
- Nested objects: `modes:\n  default: 10`
- Multi-line strings (indented)
- Comments (ignored)

**Limitations:**
- No complex YAML features (anchors, tags, merge keys)
- Designed specifically for command frontmatter

**Example:**
```python
from commands._discovery import parse_yaml_frontmatter

content = """---
name: code:lint
category: code
modes:
  - default
  - debug
---
# Command content
"""

metadata = parse_yaml_frontmatter(content)
print(metadata['name'])  # Output: code:lint
print(metadata['modes']) # Output: ['default', 'debug']
```

**Frontmatter Format:**
```yaml
---
name: command:name
category: category
description: One-line description
subcategory: optional
modes:
  - default
  - debug
related_commands:
  - related:cmd1
  - related:cmd2
---
```

---

### `extract_first_heading()`

```python
def extract_first_heading(content: str) -> Optional[str]:
```

**Description:** Extract the first markdown heading (# or ##) from content, skipping frontmatter.

**Parameters:**
- `content` (str): Markdown content

**Returns:**
- `Optional[str]`: First heading text (without #) or None

**Example:**
```python
from commands._discovery import extract_first_heading

content = """---
name: test
---
# Code Linting - Fast quality checks

Some content...
"""

heading = extract_first_heading(content)
print(heading)  # Output: Fast quality checks
```

**Processing:**
1. Skip YAML frontmatter
2. Find first `#` or `##` heading
3. Strip heading markers
4. Remove command prefix (e.g., `/craft:code:lint - `)

---

### `extract_first_paragraph()`

```python
def extract_first_paragraph(content: str) -> Optional[str]:
```

**Description:** Extract the first paragraph after frontmatter and headings.

**Parameters:**
- `content` (str): Markdown content

**Returns:**
- `Optional[str]`: First paragraph text (truncated to ~60 chars) or None

**Example:**
```python
from commands._discovery import extract_first_paragraph

content = """---
name: test
---
# Heading

This is the first paragraph with some description.

More content...
"""

para = extract_first_paragraph(content)
print(para)  # Output: This is the first paragraph with some description.
```

---

## Category & Name Inference

### `infer_category()`

```python
def infer_category(filepath: str) -> str:
```

**Description:** Extract category from file path structure.

**Parameters:**
- `filepath` (str): Relative path from `commands/` directory

**Returns:**
- `str`: Category name

**Examples:**
- `code/lint.md` → `"code"`
- `git/worktree.md` → `"git"`
- `hub.md` → `"hub"` (top-level)
- `git/docs/refcard.md` → `"git"`
- Files starting with `_` → `"internal"` (skipped)

**Usage:**
```python
from commands._discovery import infer_category

category = infer_category("code/lint.md")
print(category)  # Output: code
```

---

### `infer_command_name()`

```python
def infer_command_name(filepath: str, category: str) -> str:
```

**Description:** Infer command name from filepath and category.

**Parameters:**
- `filepath` (str): Relative path from `commands/` directory
- `category` (str): Inferred category

**Returns:**
- `str`: Command name (format: `category:command` or just `command` for top-level)

**Examples:**
- `code/lint.md`, `code` → `"code:lint"`
- `git/worktree.md`, `git` → `"git:worktree"`
- `hub.md`, `hub` → `"hub"`
- `git/docs/refcard.md`, `git` → `"git:refcard"` (skips "docs" in path)

**Usage:**
```python
from commands._discovery import infer_command_name, infer_category

filepath = "code/lint.md"
category = infer_category(filepath)
name = infer_command_name(filepath, category)
print(name)  # Output: code:lint
```

---

## Cache Management

### Cache Structure

```json
{
  "generated": "2026-01-17T10:30:00.123456",
  "count": 97,
  "categories": {
    "code": 12,
    "test": 7,
    "docs": 19,
    "git": 11,
    ...
  },
  "stats": {
    "total": 97,
    "with_modes": 29,
    "with_dry_run": 29
  },
  "commands": [
    {
      "name": "code:lint",
      "category": "code",
      "subcategory": "analysis",
      "description": "Code quality checks with multiple modes",
      "file": "code/lint.md",
      "modes": ["default", "debug", "optimize", "release"],
      "related_commands": ["code:coverage", "test:run"]
    },
    ...
  ]
}
```

### Cache Invalidation Logic

```python
# Pseudocode
if not cache_exists():
    regenerate()
elif any_md_file_newer_than_cache():
    regenerate()
else:
    load_cache()
```

---

## Query Functions

### `get_command_stats()`

```python
def get_command_stats() -> dict:
```

**Description:** Get summary statistics about commands from cache.

**Returns:**
- `dict`: Statistics dictionary

**Return Structure:**
```python
{
    "total": 97,
    "categories": {"code": 12, "test": 7, ...},
    "with_modes": 29,
    "with_dry_run": 29,
    "generated": "2026-01-17T10:30:00"
}
```

**Example:**
```python
from commands._discovery import get_command_stats

stats = get_command_stats()
print(f"Total commands: {stats['total']}")
print(f"Code commands: {stats['categories']['code']}")
```

---

### `get_commands_by_category()`

```python
def get_commands_by_category(category: str) -> list[dict]:
```

**Description:** Filter commands by category.

**Parameters:**
- `category` (str): Category name (e.g., 'code', 'test', 'docs')

**Returns:**
- `list[dict]`: List of command dictionaries for that category

**Example:**
```python
from commands._discovery import get_commands_by_category

code_commands = get_commands_by_category('code')
print(f"Found {len(code_commands)} code commands")

for cmd in code_commands:
    print(f"  {cmd['name']}: {cmd['description']}")
```

---

### `group_commands_by_subcategory()`

```python
def group_commands_by_subcategory(commands: list[dict]) -> dict:
```

**Description:** Group commands by subcategory field.

**Parameters:**
- `commands` (list[dict]): List of command dictionaries

**Returns:**
- `dict`: Dictionary mapping `subcategory -> list[dict]`

**Example:**
```python
from commands._discovery import get_commands_by_category, group_commands_by_subcategory

code_commands = get_commands_by_category('code')
grouped = group_commands_by_subcategory(code_commands)

print("Subcategories:")
for subcat, cmds in grouped.items():
    print(f"  {subcat}: {len(cmds)} commands")
```

**Output:**
```
Subcategories:
  analysis: 3 commands
  development: 5 commands
  general: 4 commands
```

---

### `get_category_info()`

```python
def get_category_info(category: str) -> dict:
```

**Description:** Get detailed information about a category.

**Parameters:**
- `category` (str): Category name

**Returns:**
- `dict`: Category information

**Return Structure:**
```python
{
    'name': 'code',
    'count': 12,
    'commands': [...],  # List of command dicts
    'subcategories': {  # Grouped by subcategory
        'analysis': [...],
        'development': [...]
    },
    'icon': '💻'
}
```

**Example:**
```python
from commands._discovery import get_category_info

info = get_category_info('code')
print(f"{info['icon']} {info['name'].upper()}: {info['count']} commands")

for subcat, cmds in info['subcategories'].items():
    print(f"  {subcat}: {len(cmds)} commands")
```

---

### `get_command_detail()`

```python
def get_command_detail(command_name: str) -> dict | None:
```

**Description:** Get detailed information about a specific command.

**Parameters:**
- `command_name` (str): Full command name (e.g., 'code:lint') or just command part (e.g., 'lint')

**Returns:**
- `dict | None`: Command dictionary or None if not found

**Matching Strategy:**
1. Try exact match: `code:lint`
2. Try partial match: `lint` → find unique match ending with `:lint`
3. Return None if multiple partial matches (ambiguous)

**Example:**
```python
from commands._discovery import get_command_detail

# Exact match
cmd = get_command_detail('code:lint')
if cmd:
    print(f"{cmd['name']}: {cmd['description']}")

# Partial match (if unique)
cmd = get_command_detail('lint')
if cmd:
    print(f"Found unique match: {cmd['name']}")
```

---

### `generate_command_tutorial()`

```python
def generate_command_tutorial(command: dict) -> str:
```

**Description:** Generate formatted tutorial text for a command.

**Parameters:**
- `command` (dict): Command dictionary from discovery

**Returns:**
- `str`: Formatted tutorial string with box-drawing borders

**Generated Sections:**
1. **Header**: Command name, description
2. **Description**: Full description
3. **Modes** (if applicable): Time budgets, mode explanations
4. **Basic Usage**: Example invocations
5. **Common Workflows** (if defined): Step-by-step procedures
6. **Related Commands** (if defined): Cross-references with descriptions
7. **Navigation**: Breadcrumb links

**Format:**
- Box-drawing characters: `┌─┐│└┘`
- 65-character width
- Left-aligned with padding

**Example:**
```python
from commands._discovery import get_command_detail, generate_command_tutorial

cmd = get_command_detail('code:lint')
if cmd:
    tutorial = generate_command_tutorial(cmd)
    print(tutorial)
```

**Output:**
```
┌─────────────────────────────────────────────────────────────────┐
│ 📚 COMMAND: /craft:code:lint                                    │
│ Code quality checks with multiple modes                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ DESCRIPTION                                                      │
│ ───────────                                                      │
│ Code quality checks with multiple modes                          │
│                                                                  │
│ MODES                                                            │
│ ─────                                                            │
│   default    (< 10s)      Quick checks, minimal output          │
│   debug      (< 120s)     Verbose with fix suggestions          │
│   optimize   (< 180s)     Performance focus, parallel execution │
│   release    (< 300s)     Comprehensive with security audit     │
│                                                                  │
│ BASIC USAGE                                                      │
│ ───────────                                                      │
│   /craft:code:lint                                               │
│   /craft:code:lint debug                                         │
│   /craft:code:lint release                                       │
│                                                                  │
│ 🔙 Back to CODE: /craft:hub code                                │
│ 🏠 Back to Hub: /craft:hub                                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Structures

### Command Dictionary

```python
{
    # Required fields
    "name": "code:lint",                    # Unique command identifier
    "category": "code",                     # Primary category
    "description": "Code quality checks",   # One-line description
    "file": "code/lint.md",                 # Relative path from commands/

    # Optional fields
    "subcategory": "analysis",              # Subcategory for grouping
    "modes": [                              # Execution modes
        "default", "debug", "optimize", "release"
    ],
    "arguments": [                          # Command arguments
        {"name": "mode", "description": "..."},
        {"name": "--dry-run", "description": "..."}
    ],
    "tutorial": true,                       # Has tutorial section
    "tutorial_level": "beginner",           # Tutorial difficulty
    "tutorial_file": "path/to/tutorial.md", # External tutorial
    "related_commands": [                   # Related commands
        "code:coverage", "test:run"
    ],
    "tags": ["quality", "linting"],         # Search tags
    "project_types": ["python", "node"],    # Applicable projects
    "time_budgets": {                       # Mode time budgets
        "default": 10,
        "debug": 120,
        "optimize": 180,
        "release": 300
    },
    "common_workflows": [                   # Workflows
        {
            "name": "Pre-commit",
            "steps": ["Run linter", "Fix issues", "Commit"]
        }
    ]
}
```

### Category Icons

```python
CATEGORY_ICONS = {
    'code': '💻',
    'test': '🧪',
    'docs': '📄',
    'git': '🔀',
    'site': '📖',
    'arch': '🏗️',
    'plan': '📋',
    'ci': '🚀',
    'dist': '📦',
    'workflow': '🔄',
    'hub': '🛠️',
    'check': '✅',
    'do': '🎯',
    'orchestrate': '🎯',
    'smart-help': '💡',
    'utils': '🔧'
}
```

---

## Usage Examples

### Example 1: List All Commands

```python
from commands._discovery import load_cached_commands

commands = load_cached_commands()
print(f"Total commands: {len(commands)}\n")

for cmd in commands:
    print(f"  {cmd['name']:<30s} {cmd['description']}")
```

### Example 2: Browse by Category

```python
from commands._discovery import get_commands_by_category, CATEGORY_ICONS

for category in ['code', 'test', 'docs', 'git']:
    commands = get_commands_by_category(category)
    icon = get_category_info(category)['icon']
    print(f"\n{icon} {category.upper()} ({len(commands)} commands)")

    for cmd in commands:
        modes = ' [mode]' if cmd.get('modes') else ''
        print(f"  {cmd['name']}{modes}")
```

### Example 3: Generate Tutorial

```python
from commands._discovery import get_command_detail, generate_command_tutorial

cmd = get_command_detail('code:lint')
if cmd:
    tutorial = generate_command_tutorial(cmd)
    print(tutorial)
else:
    print("Command not found")
```

### Example 4: Search Commands

```python
from commands._discovery import load_cached_commands

def search_commands(query: str) -> list[dict]:
    """Search commands by name or description."""
    commands = load_cached_commands()
    query_lower = query.lower()

    return [
        cmd for cmd in commands
        if query_lower in cmd['name'].lower() or
           query_lower in cmd['description'].lower()
    ]

# Usage
results = search_commands('lint')
for cmd in results:
    print(f"{cmd['name']}: {cmd['description']}")
```

### Example 5: Performance Benchmark

```python
import time
from commands._discovery import load_cached_commands, discover_commands

# Benchmark cached load
start = time.time()
commands = load_cached_commands()
elapsed = (time.time() - start) * 1000
print(f"Cached load: {elapsed:.2f}ms")

# Force regeneration
start = time.time()
commands = discover_commands()
elapsed = (time.time() - start) * 1000
print(f"Uncached discovery: {elapsed:.2f}ms")
```

---

## Error Handling

### Parse Failures

```python
# Files with invalid YAML are skipped with warnings
try:
    metadata = parse_yaml_frontmatter(content)
except Exception as e:
    print(f"Warning: Failed to parse {filepath}: {e}")
    continue  # Skip file
```

### Missing Required Fields

```python
# Infer missing fields from file content
if 'name' not in metadata:
    metadata['name'] = infer_command_name(filepath, category)

if 'description' not in metadata:
    metadata['description'] = extract_first_heading(content) or \
                               extract_first_paragraph(content) or \
                               "No description available"
```

### Cache Corruption

```python
try:
    with open(CACHE_FILE, 'r') as f:
        cache = json.load(f)
    return cache['commands']
except Exception as e:
    print(f"Warning: Failed to load cache: {e}")
    # Graceful fallback: regenerate
    commands = discover_commands()
    cache_commands(commands)
    return commands
```

### Ambiguous Command Names

```python
# get_command_detail() returns None for ambiguous partial matches
cmd = get_command_detail('status')  # Could be git:status or site:status
if cmd is None:
    print("Ambiguous command name. Please specify category:command")
```

---

## Performance Characteristics

| Operation | Complexity | Typical Time | Notes |
|-----------|------------|--------------|-------|
| `discover_commands()` | O(n files) | 12ms (97 files) | Linear with file count |
| `load_cached_commands()` | O(1) cached | <2ms cached | O(n) uncached |
| `get_command_stats()` | O(1) | <1ms | Read from cache |
| `get_commands_by_category()` | O(n commands) | <1ms | Linear filter |
| `group_commands_by_subcategory()` | O(n commands) | <1ms | Single pass |
| `get_command_detail()` | O(n commands) | <1ms | Linear search |
| `generate_command_tutorial()` | O(1) | <1ms | Template formatting |

---

## CLI Usage

The discovery module can be run directly from the command line:

```bash
# Regenerate cache and print statistics
python3 commands/_discovery.py
```

**Output:**
```
Discovering commands...

Found 97 commands

Categories:
  arch: 1
  check: 1
  ci: 3
  code: 12
  dist: 1
  do: 1
  docs: 19
  git: 11
  hub: 1
  orchestrate: 1
  plan: 3
  site: 16
  smart-help: 1
  test: 7
  utils: 5
  workflow: 2

Caching to /path/to/commands/_cache.json...

Statistics:
  Total: 97
  With modes: 29
  With dry-run: 29
  Generated: 2026-01-17T10:30:00.123456

✓ Done!
```

---

## See Also

- [Architecture Documentation](../architecture/HUB-V2-ARCHITECTURE.md)
- [User Guide](../../commands/hub.md)
- [Testing Guide](../../tests/HUB-V2-TESTING-GUIDE.md)
- [Command Frontmatter Schema](../../commands/_schema.json)

---

**Last Updated:** 2026-01-17
**Version:** 2.0
**Module:** `commands/_discovery.py`
