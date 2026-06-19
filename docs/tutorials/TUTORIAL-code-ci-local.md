# Tutorial: code:ci-local — Run CI Checks Locally

By the end of this tutorial you will have:

- Run the same checks CI runs, locally before pushing
- Used `--quick` mode for a fast pre-commit check
- Targeted specific check types with `--only`

**Prerequisites:** craft installed, local project with test/lint tooling.

---

## Step 1: Run a Full CI Mirror Locally

```
/craft:code:ci-local
```

Runs lint, tests, coverage, and security in sequence — the same pipeline CI uses:

```
CI Local — my-project
──────────────────────
[1/4] Lint (ESLint)...       ✅ 0 issues
[2/4] Tests (Jest)...        ✅ 142 passed (0 failed)
[3/4] Coverage...            ✅ 87% (threshold: 80%)
[4/4] Security (npm audit).. ✅ 0 vulnerabilities

All checks passed. Safe to push.
```

---

## Step 2: Quick Mode (Lint + Tests Only)

For a fast pre-push check without coverage:

```
/craft:code:ci-local --quick
```

---

## Step 3: Run Only Specific Checks

```
/craft:code:ci-local --only lint
/craft:code:ci-local --only tests
/craft:code:ci-local --only security
```

---

## Step 4: Auto-Fix Lint Issues

```
/craft:code:ci-local --fix
```

Runs linters with `--fix` mode enabled. Restages auto-fixed files.

---

## Step 5: Verbose Output

```
/craft:code:ci-local --verbose
```

Shows full output from each tool, not just summaries. Useful when a check fails and you need the detailed error.

---

## Step 6: Dry Run (Preview Only)

```
/craft:code:ci-local --dry-run
```

Shows which commands would run without executing them.

---

## What's Next

- Run before every `git push` to catch failures before CI does
- Use `/craft:check --for release` for the full pre-release validation suite
- See `/craft:ci:validate` to ensure your local checks match the CI workflow definition
