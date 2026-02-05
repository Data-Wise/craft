---
title: "Troubleshooting: MkDocs Build Fails"
description: "Fix common mkdocs build and mkdocs serve errors"
category: "cookbook"
level: "beginner"
time_estimate: "5 minutes"
related:
  - ../../commands/site.md
  - ../../guide/documentation-quality.md
---

# Troubleshooting: MkDocs Build Fails

**Level:** Beginner

## Problem

Running `mkdocs build` or `mkdocs serve` fails with an error:

```
ERROR - Config value 'theme': Uninstalled theme 'material'.
Aborted with 1 Configuration Errors!
```

or `Unable to find 'guide/nonexistent-page.md' in the docs directory.`

## Common Causes & Solutions

### 1. Missing Python Dependencies

**Issue:** The Material theme or required extensions are not installed.

**Solution:**

```bash
pip install mkdocs-material          # includes most extensions
pip install pymdown-extensions       # if pymdownx errors appear
mkdocs build                         # retry
```

**Why:** A fresh machine or new virtual environment will be missing these packages.

### 2. YAML Syntax Error in `mkdocs.yml`

**Issue:** Invalid YAML prevents MkDocs from parsing the config.

**Solution:**

```bash
python3 -c "import yaml; yaml.safe_load(open('mkdocs.yml'))"
```

Common mistakes: tabs instead of spaces, missing colon after a key, wrong indentation in nav.

### 3. Nav Path Points to Missing File

**Issue:** A `nav` entry references a file that does not exist on disk.

**Solution:** Search `mkdocs.yml` for the filename from the error, then either create the missing file or correct the nav entry to match the actual path under `docs/`.

### 4. Duplicate Nav Entries

**Issue:** The same page appears twice in `nav`, producing a warning.

**Solution:**

```bash
grep -n "my-page.md" mkdocs.yml    # find duplicates
# Remove the extra entry
```

### 5. Extension Load Failure

**Issue:** A Markdown extension is misconfigured or its package is missing.

**Solution:**

```bash
pip install --upgrade pymdown-extensions
```

**Why:** Extension names must match their Python package exactly, and version mismatches cause load failures.

## Verification Steps

```bash
rm -rf site/                   # clean stale output
mkdocs build --strict          # strict mode treats warnings as errors
mkdocs serve                   # preview at http://127.0.0.1:8000
```

A successful `--strict` build with zero errors confirms the site is healthy.

## Related

- [Site Commands](../../commands/site.md) -- Commands for building and deploying the docs site
- [Documentation Quality Guide](../../guide/documentation-quality.md) -- Best practices for maintaining docs
