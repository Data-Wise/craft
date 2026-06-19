# Tutorial: docs:check — Documentation Health Check

By the end of this tutorial you will have:

- Run a full documentation health check (links, staleness, navigation)
- Used `--fix` to auto-correct safe issues
- Understood which issues require manual attention

**Prerequisites:** craft installed, a `docs/` directory.

---

## Step 1: Run a Full Health Check

```
/craft:docs:check
```

Runs a multi-phase check across your documentation:

```
Documentation Health Check
────────────────────────────
Phase 1: Internal links ............. ✅ 0 broken
Phase 2: Staleness scan ............. ⚠️  3 files not updated since last feature
Phase 3: Navigation completeness .... ✅ all pages in mkdocs.yml
Phase 4: Count consistency .......... ✅ command/skill counts match

Issues:
  ⚠️  docs/guide/installation.md — not updated since v2.38.0 (2 versions ago)
  ⚠️  docs/reference/configuration.md — references deprecated flag --orch-mode
  ⚠️  docs/tutorials/index.md — missing 3 new tutorials from nav

Health score: 88/100
```

---

## Step 2: Auto-Fix Safe Issues

```
/craft:docs:check --fix
```

Applies fixes for mechanical issues:

- Adds missing nav entries to `mkdocs.yml`
- Updates count references (e.g., stale command counts to the current 112)
- Fixes broken internal links where the target can be inferred

Does not modify content (descriptions, prose, examples) — only structural issues.

---

## Step 3: Preview Fixes

```
/craft:docs:check --dry-run
```

Shows what `--fix` would change without writing.

---

## Step 4: Non-Interactive Mode

```
/craft:docs:check --dry-run
```

Useful in CI to detect drift without making changes:

```bash
/craft:docs:check --dry-run && echo "Docs healthy" || echo "Docs drift detected"
```

---

## What's Next

- Run after every PR merge as part of post-merge cleanup
- Use `/craft:docs:check-links` for link-only validation
- The staleness check feeds into `/craft:site:update` which drives content regeneration
