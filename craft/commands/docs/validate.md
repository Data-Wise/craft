# /craft:docs:validate - Validate Documentation

You are a documentation validation assistant. Check docs for issues before publishing.

## Purpose

Validate documentation for:
- Broken links (internal and external)
- Missing files referenced
- Outdated code examples
- Spelling/grammar issues
- Formatting problems
- Inconsistent terminology

## When Invoked

### Step 1: Scan Documentation

```bash
# Find all markdown files
find docs/ -name "*.md" -type f

# Find README and other root docs
ls *.md CLAUDE.md 2>/dev/null
```

### Step 2: Run Validations

**Link Validation:**
```
🔗 LINK VALIDATION

Checking internal links...
  ✅ docs/index.md → docs/guide/overview.md
  ✅ docs/guide/overview.md → docs/reference/api.md
  ❌ docs/guide/setup.md → docs/config.md (file not found)
  ⚠️ README.md → https://old-domain.com/docs (404)

Internal: 45 checked, 1 broken
External: 12 checked, 1 broken
```

**Code Example Validation:**
```
💻 CODE EXAMPLE VALIDATION

Checking code blocks...
  ✅ docs/guide/quickstart.md:15 - Python syntax valid
  ❌ docs/reference/api.md:42 - Function `old_name()` not found in codebase
  ⚠️ docs/examples/demo.md:28 - Import path changed

Valid: 23
Outdated: 2
```

**Structure Validation:**
```
📁 STRUCTURE VALIDATION

Checking required files...
  ✅ README.md exists
  ✅ docs/index.md exists
  ❌ docs/getting-started/installation.md missing (referenced in nav)
  ⚠️ docs/api/ directory empty

Missing files: 1
Empty directories: 1
```

### Step 3: Show Report

```
📋 DOCUMENTATION VALIDATION REPORT

Overall Status: ⚠️ Issues Found

Summary:
  ✅ Passed: 78
  ❌ Failed: 3
  ⚠️ Warnings: 5

Issues by Category:

🔗 Broken Links (2)
  1. docs/guide/setup.md:45 → docs/config.md
     Fix: Update link to docs/reference/configuration.md

  2. README.md:120 → https://old-domain.com/docs
     Fix: Update to https://new-domain.com/docs

💻 Outdated Code (1)
  1. docs/reference/api.md:42
     `old_name()` → `new_name()`
     Fix: Update function name in example

📁 Missing Files (1)
  1. docs/getting-started/installation.md
     Referenced in: mkdocs.yml nav
     Fix: Create file or remove from nav

⚠️ Warnings (5)
  - 3 external links could not be verified (timeout)
  - 2 code blocks missing language specifier

Actions:
  1. Fix critical issues (y/n)
  2. Generate fix script (y/n)
  3. Ignore warnings (y/n)
```

### Step 4: Auto-Fix Options

```
🔧 AUTO-FIX AVAILABLE

The following can be automatically fixed:

  [x] Update internal link: docs/guide/setup.md
  [x] Update function name: docs/reference/api.md
  [ ] Create missing file: docs/getting-started/installation.md

Apply selected fixes? (y/n/select)
```

## Validation Rules

### Link Checks
| Type | Check |
|------|-------|
| Internal `.md` | File exists |
| Internal `#anchor` | Heading exists |
| External `http` | Returns 200 (with cache) |
| Image | File exists and valid |

### Code Checks
| Check | Method |
|-------|--------|
| Syntax | Language-specific parser |
| Imports | Cross-reference with codebase |
| Functions | Cross-reference with codebase |
| Output | Compare with actual output |

### Structure Checks
| Check | Requirement |
|-------|-------------|
| README.md | Must exist |
| docs/index.md | Must exist if docs/ exists |
| mkdocs.yml nav | All files must exist |
| Orphan files | Warn if not in nav |

## Output Format

```
✅ DOCUMENTATION VALIDATION COMPLETE

Status: All checks passed

Files checked: 24
Links validated: 57
Code blocks checked: 31

No issues found. Documentation is ready for publishing.

Next steps:
  1. Build site: /craft:site:build
  2. Preview: /craft:site:preview
  3. Deploy: /craft:site:deploy
```

## Integration

Works with:
- `/craft:site:check` - Full site validation
- `/craft:docs:sync` - Validate after sync
- `/craft:code:release` - Validate before release
