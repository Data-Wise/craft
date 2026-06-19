# Tutorial: docs:check-links — Validate Internal Links

By the end of this tutorial you will have:

- Checked all internal links in your documentation for broken references
- Scoped a check to a specific directory
- Used `--dry-run` to preview what would be checked

**Prerequisites:** craft installed, a `docs/` directory with Markdown files.

---

## Step 1: Check All Internal Links

```
/craft:docs:check-links
```

Scans all Markdown files for internal links and validates that the targets exist:

```
Link Validation — docs/
────────────────────────
Scanning 47 files...

Issues found:
  ❌  docs/guide/installation.md:23
      [Getting Started](../tutorials/getting-started.md) — file not found

  ❌  docs/reference/commands.md:187
      [See also](../commands/archive/legacy.md) — file not found

  ⚠️  docs/index.md:102
      [Changelog](CHANGELOG.md) — file exists but anchor #v2-41-0 not found

3 issues (2 broken, 1 anchor mismatch)
```

---

## Step 2: Check a Specific Path

```
/craft:docs:check-links --path docs/guide
/craft:docs:check-links --path docs/tutorials
```

---

## Step 3: Modes

```
/craft:docs:check-links --mode strict    # Anchors + files (default)
/craft:docs:check-links --mode files     # Files only (ignores anchor mismatches)
/craft:docs:check-links --mode anchors   # Anchors only (assumes files exist)
```

---

## Step 4: Preview Without Scanning

```
/craft:docs:check-links --dry-run
```

Lists which files would be scanned without actually checking links.

---

## Step 5: Fix Broken Links

Link validation is read-only — the command reports issues but does not auto-fix them (paths require human judgment). Update the broken links manually using the output as a checklist.

For high-volume fixes, use `/craft:docs:check --fix` which handles a broader set of doc issues.

---

## What's Next

- Run after every tutorial or guide addition
- Use as part of `/craft:docs:check` which includes link validation in its pipeline
- Run `mkdocs build --strict` after fixing to verify MkDocs agrees with the fix
