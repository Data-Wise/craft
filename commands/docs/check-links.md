---
description: Internal link validation for documentation
category: docs
arguments:
  - name: mode
    description: Execution mode (default|debug|optimize|release)
    required: false
    default: default
  - name: path
    description: Specific file or directory to check
    required: false
  - name: dry-run
    description: Preview checks without executing them
    required: false
    default: false
    alias: -n
---

# /craft:docs:check-links - Documentation Link Validation

Validate internal links in documentation files to prevent broken references.

## Purpose

**Fast, focused link validation:**
- Internal markdown links (relative & absolute)
- Detects broken file references before deployment
- Catches issues like v1.20.0 workflows/ directory not deployed
- CI-ready with exit codes

## Philosophy

> **"Find broken links before they break production."**

## Usage

```bash
# DEFAULT: Quick check of all docs
/craft:docs:check-links

# MODES: Different thoroughness levels
/craft:docs:check-links default      # Quick check (< 10s)
/craft:docs:check-links debug        # Verbose with context (< 120s)
/craft:docs:check-links optimize     # Parallel checking (< 180s)
/craft:docs:check-links release      # Comprehensive validation (< 300s)

# SPECIFIC PATH
/craft:docs:check-links docs/guide/  # Check specific directory
/craft:docs:check-links README.md    # Check specific file

# DRY-RUN: Preview what will be checked
/craft:docs:check-links --dry-run
/craft:docs:check-links release -n
```

## Modes

| Mode | Time | Focus | Use Case |
|------|------|-------|----------|
| **default** | < 10s | Internal links only | Quick pre-commit check |
| **debug** | < 120s | + Context + verbose | Troubleshooting broken links |
| **optimize** | < 180s | + Parallel processing | Large doc sets |
| **release** | < 300s | + Anchors + comprehensive | Pre-release validation |

## When Invoked

### Step 1: Detect Scope

```bash
# Determine what to check
if [ -n "$path" ]; then
  # Specific path provided
  if [ -f "$path" ]; then
    FILES="$path"
  elif [ -d "$path" ]; then
    FILES=$(find "$path" -name "*.md" -type f)
  fi
else
  # Default: all docs
  FILES=$(find docs/ -name "*.md" -type f 2>/dev/null)
  FILES+=" "$(ls *.md CLAUDE.md 2>/dev/null)
fi

echo "Checking ${#FILES[@]} markdown files..."
```

### Step 2: Parse Links

For each markdown file, extract links:

```bash
# Extract markdown links: [text](url)
grep -oP '\[([^\]]+)\]\(([^)]+)\)' file.md

# Extract reference-style links: [text][ref]
grep -oP '\[([^\]]+)\]\[([^\]]+)\]' file.md

# Extract link definitions: [ref]: url
grep -oP '^\[([^\]]+)\]:\s*(.+)$' file.md
```

### Step 3: Validate Links (Mode-Specific)

#### Default Mode: Internal Links Only

```
🔗 CHECKING INTERNAL LINKS...

docs/index.md:
  ✓ Line 12: [Quick Start](guide/quickstart.md)
  ✓ Line 25: [API Reference](reference/api.md)
  ✗ Line 34: [Configuration](/docs/config.md) → File not found

docs/guide/setup.md:
  ✓ Line 8: [../reference/commands.md](../reference/commands.md)
  ✗ Line 15: [missing.md](missing.md) → File not found

README.md:
  ✓ Line 45: [Documentation](docs/index.md)
  ✗ Line 67: [Guide](docs/guide/nonexistent.md) → File not found

Summary:
  Total: 45 internal links
  Valid: 42 ✓
  Broken: 3 ✗
```

#### Debug Mode: + Verbose Context

```
🔍 DEBUG: Link Validation with Context

docs/index.md:34 (BROKEN):
  Link: [Configuration](/docs/config.md)
  Target: /docs/config.md
  Resolved: /Users/dt/projects/craft/docs/config.md
  Error: File does not exist

  Context (lines 32-36):
    32: ## Getting Started
    33:
    34: Check the [Configuration](/docs/config.md) guide to set up your
    35: environment. This will walk you through all the necessary steps
    36: to get started with Craft.

  Suggestions:
    • Did you mean: docs/reference/configuration.md?
    • Or: docs/guide/setup.md?

docs/guide/setup.md:15 (BROKEN):
  Link: [missing.md](missing.md)
  Target: missing.md
  Resolved: /Users/dt/projects/craft/docs/guide/missing.md
  Error: File does not exist

  Context (lines 13-17):
    13: ### Installation
    14:
    15: See [missing.md](missing.md) for detailed installation
    16: instructions. Follow these steps carefully to avoid
    17: common pitfalls.

  Suggestions:
    • Check filename case (case-sensitive filesystems)
    • Verify file exists in repository
```

#### Optimize Mode: + Parallel Processing

```
⚡ OPTIMIZE: Parallel Link Checking

Processing batches of 10 files concurrently...

[Batch 1/5] Checking 10 files... ✓ (1.2s)
[Batch 2/5] Checking 10 files... ✓ (1.1s)
[Batch 3/5] Checking 10 files... ✗ 1 broken (1.3s)
[Batch 4/5] Checking 10 files... ✓ (0.9s)
[Batch 5/5] Checking 5 files... ✓ (0.6s)

Total time: 5.1 seconds (vs ~15s sequential)

Broken links found:
  docs/index.md:34 → /docs/config.md
  docs/guide/setup.md:15 → missing.md
  README.md:67 → docs/guide/nonexistent.md
```

#### Release Mode: + Anchor Validation

```
🎯 RELEASE: Comprehensive Link Validation

Phase 1: Internal file links... ✓ 42/45 (3 broken)
Phase 2: Anchor validation...

Checking anchor targets in 12 files with cross-references...

docs/guide/quickstart.md:
  ✓ Line 23: [Setup](setup.md#installation) → setup.md has #installation
  ✗ Line 45: [Config](../reference/config.md#options) → #options not found

docs/reference/api.md:
  ✓ Line 12: [Example](#examples) → #examples exists in same file
  ✗ Line 78: [Auth Flow](#authentication-flow) → heading case mismatch
    Found: ## Authentication flow (lowercase 'flow')

Phase 3: Link consistency...

Checking for inconsistent link patterns...
  ⚠ Mixed link styles detected:
    - docs/index.md: Uses absolute paths (/docs/...)
    - docs/guide/: Uses relative paths (../...)
    Recommendation: Use relative paths for portability

Summary:
  File links: 42/45 valid (3 broken)
  Anchor links: 15/17 valid (2 broken)
  Consistency: 1 warning
```

### Step 4: Output Format

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:docs:check-links (default mode)                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ✓ Checked: 45 internal links in 54 files                    │
│                                                             │
│ ✗ Broken Links (3):                                         │
│   1. docs/index.md:34                                       │
│      [Configuration](/docs/config.md)                       │
│      → File not found                                       │
│                                                             │
│   2. docs/guide/setup.md:15                                 │
│      [missing.md](missing.md)                               │
│      → File not found                                       │
│                                                             │
│   3. README.md:67                                           │
│      [Guide](docs/guide/nonexistent.md)                     │
│      → File not found                                       │
│                                                             │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ Exit code: 1 (broken links found)                           │
│                                                             │
│ Fix these before deployment to prevent 404 errors.          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**VS Code Integration (file:line:col format):**
```
docs/index.md:34:10: [Configuration](/docs/config.md) → File not found
docs/guide/setup.md:15:5: [missing.md](missing.md) → File not found
README.md:67:23: [Guide](docs/guide/nonexistent.md) → File not found
```

## Link Types Supported

### Internal Links (MVP)

| Format | Example | Validated |
|--------|---------|-----------|
| Relative | `[text](../other.md)` | ✓ File exists |
| Relative same dir | `[text](file.md)` | ✓ File exists |
| Absolute repo | `[text](/docs/file.md)` | ✓ File exists |
| Anchor (release) | `[text](file.md#heading)` | ✓ Heading exists |

### External Links (Not in MVP)

| Format | Example | Status |
|--------|---------|--------|
| HTTP/HTTPS | `[text](https://example.com)` | ⚠ Skipped (use /craft:site:check) |
| Mailto | `[text](mailto:user@example.com)` | ⚠ Skipped |

## Implementation Details

### Link Resolution Algorithm

```bash
# For each link in markdown file
for link in $(extract_links "$file"); do
  # Skip external links
  if [[ $link =~ ^https?:// ]]; then
    continue
  fi

  # Skip anchors in default mode
  if [[ $mode != "release" ]] && [[ $link =~ \# ]]; then
    link=${link%%#*}  # Strip anchor
  fi

  # Resolve path
  if [[ $link =~ ^/ ]]; then
    # Absolute repo path
    target="${repo_root}${link}"
  else
    # Relative path
    target=$(realpath -m "$(dirname "$file")/$link")
  fi

  # Check if target exists
  if [ ! -f "$target" ]; then
    echo "BROKEN: $file:$line:$col: $link → File not found"
    broken_count=$((broken_count + 1))
  fi
done
```

### Anchor Validation (Release Mode Only)

```bash
# Extract heading from markdown file
extract_headings() {
  grep -E '^#{1,6} ' "$1" | sed 's/^#* //' | \
    tr '[:upper:]' '[:lower:]' | \
    tr ' ' '-' | \
    sed 's/[^a-z0-9-]//g'
}

# Check if anchor exists
validate_anchor() {
  local file=$1
  local anchor=$2

  headings=$(extract_headings "$file")

  if ! echo "$headings" | grep -qx "$anchor"; then
    return 1  # Anchor not found
  fi
  return 0  # Anchor exists
}
```

## Dry-Run Mode

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Documentation Link Validation                     │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Mode: default (Quick check)                                 │
│   Time budget: < 10 seconds                                   │
│   Focus: Internal file links only                             │
│                                                               │
│ ✓ Scope Detection:                                            │
│   - docs/ directory: 45 markdown files                        │
│   - Root level: 3 files (README.md, CLAUDE.md, CHANGELOG.md) │
│   - Total: 48 files to check                                  │
│                                                               │
│ ✓ Link Types to Validate:                                     │
│   • Relative links: ../other.md, file.md                      │
│   • Absolute repo links: /docs/file.md                        │
│   • Skipping: External links (https://)                       │
│   • Skipping: Anchors (file.md#heading) - use release mode   │
│                                                               │
│ ✓ Validation Process:                                         │
│   1. Parse markdown files for [text](url) patterns           │
│   2. Extract internal links (skip external URLs)              │
│   3. Resolve relative/absolute paths                          │
│   4. Check if target files exist                              │
│   5. Report broken links with file:line:col format           │
│                                                               │
│ ✓ Output Format:                                              │
│   - Success: "✓ All 45 internal links valid"                 │
│   - Failures: file:line:col format (VS Code clickable)       │
│   - Exit code: 0 (no broken links) or 1 (broken links found) │
│                                                               │
│ ⚠ Estimated Time: ~3 seconds (48 files)                       │
│                                                               │
│ 📊 Summary: 48 files, internal links only, ~3s                │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

### Release Mode Dry-Run

```bash
/craft:docs:check-links release --dry-run
```

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Documentation Link Validation (Release Mode)      │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Mode: release (Comprehensive validation)                    │
│   Time budget: < 300 seconds                                  │
│   Focus: Internal links + anchors + consistency              │
│                                                               │
│ ✓ Validation Phases (3):                                      │
│                                                               │
│   Phase 1: Internal file links                                │
│     • Relative links: ../other.md, file.md                    │
│     • Absolute repo links: /docs/file.md                      │
│     • Estimated: ~3 seconds                                   │
│                                                               │
│   Phase 2: Anchor validation                                  │
│     • Cross-file anchors: [text](file.md#heading)            │
│     • Same-file anchors: [text](#heading)                     │
│     • Heading extraction and normalization                    │
│     • Estimated: ~8 seconds                                   │
│                                                               │
│   Phase 3: Link consistency                                   │
│     • Check for mixed link styles (absolute vs relative)      │
│     • Detect case sensitivity issues                          │
│     • Validate link patterns                                  │
│     • Estimated: ~2 seconds                                   │
│                                                               │
│ ✓ Total Estimated Time: ~13 seconds                           │
│                                                               │
│ ⚠ Strict Mode:                                                │
│   • Any broken link causes failure                            │
│   • Anchor mismatches reported as errors                      │
│   • Consistency warnings don't block                          │
│                                                               │
│ 📊 Summary: 3 phases, comprehensive checks, ~13s              │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

## Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | All links valid | ✓ Safe to deploy |
| 1 | Broken links found | ✗ Fix before deployment |
| 2 | Validation error | ✗ Check command syntax |

## Integration

**Called by:**
- `/craft:check` - Pre-flight validation
- `/craft:site:check` - Site validation
- Pre-commit hooks - Prevent broken links

**Works with:**
- `/craft:docs:lint` - Markdown quality checks
- `/craft:ci:validate` - CI pipeline validation

## CI Pipeline Usage

```yaml
# .github/workflows/docs-quality.yml
- name: Check Documentation Links
  run: |
    claude "/craft:docs:check-links"
    # Exit code 1 if broken links found
```

## Examples

```bash
# Quick check before commit
/craft:docs:check-links
# → Fast, internal links only

# Debug broken link
/craft:docs:check-links debug
# → Verbose with context and suggestions

# Release validation
/craft:docs:check-links release
# → Comprehensive with anchors

# Specific file
/craft:docs:check-links README.md
# → Check just one file

# Preview without executing
/craft:docs:check-links --dry-run
# → Shows what will be checked
```

## Performance

| Files | Mode | Time |
|-------|------|------|
| 50 | default | ~3s |
| 50 | debug | ~15s |
| 50 | optimize | ~5s (parallel) |
| 50 | release | ~13s (+ anchors) |

**Optimization Tips:**
- Use `optimize` mode for large doc sets (100+ files)
- Use specific paths for quick checks: `/craft:docs:check-links docs/guide/`
- Default mode skips anchors for speed

## Troubleshooting

### False Positives

**Issue:** Link reported as broken but file exists

```bash
# Check case sensitivity
ls -la docs/guide/  # Verify exact filename

# Check current directory
pwd  # Ensure you're in repo root

# Try absolute path
/craft:docs:check-links /full/path/to/docs/
```

### Performance Issues

**Issue:** Checking takes too long

```bash
# Use optimize mode (parallel)
/craft:docs:check-links optimize

# Or check specific directory
/craft:docs:check-links docs/guide/
```

### Anchor Validation Errors

**Issue:** Anchors reported as broken but heading exists

```bash
# Headings are normalized: lowercase, spaces → dashes
# "Setup Guide" → #setup-guide
# "API Reference" → #api-reference

# Debug mode shows normalized anchor
/craft:docs:check-links debug release
```

## See Also

- `/craft:docs:lint` - Markdown style and quality checks
- `/craft:docs:check` - Full documentation health check
- `/craft:site:check` - Site validation (includes external links)
- Template: `templates/dry-run-pattern.md`
