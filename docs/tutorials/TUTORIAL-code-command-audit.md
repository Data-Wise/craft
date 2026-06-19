# Tutorial: code:command-audit — Validate Command Frontmatter

By the end of this tutorial you will have:

- Audited all command files for frontmatter health
- Identified deprecated fields and structural issues
- Used `--fix` to auto-correct safe violations

**Prerequisites:** craft installed, working in the craft plugin repo.

---

## Step 1: Run the Audit

```
/craft:code:command-audit
```

Scans all `commands/**/*.md` files for frontmatter validity:

```
Command Audit — craft plugin
──────────────────────────────
Scanning 112 command files...

Health Score: 97/100

Issues found:
  ⚠️  commands/ci/watch.md — deprecated field 'aliases' (use 'alias')
  ⚠️  commands/dist/pypi.md — missing 'description' field
  ❌  commands/arch/review.md — 'arguments' is not a valid YAML list (parsing error)

Summary: 2 warnings, 1 error
```

---

## Step 2: Strict Mode

```
/craft:code:command-audit --strict
```

Treats warnings as errors. Use before releases to ensure zero-tolerance compliance.

---

## Step 3: Auto-Fix Safe Issues

```
/craft:code:command-audit --fix
```

Renames deprecated fields, adds missing defaults. Does not guess at content — only fixes structural issues it can determine safely.

---

## Step 4: Choose Output Format

```
/craft:code:command-audit --format table   # Default
/craft:code:command-audit --format json    # Machine-readable
/craft:code:command-audit --format minimal # Issues only, no summary
```

---

## What's Next

- Run before every PR that adds or modifies commands
- The audit feeds into `./scripts/docs-staleness-check.sh` Phase 8 (command coverage)
- Use `./scripts/validate-counts.sh` to verify command count consistency across all docs
