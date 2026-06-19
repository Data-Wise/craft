# Tutorial: code:lint — Code Style and Quality Checks

By the end of this tutorial you will have:

- Run a lint check on your codebase
- Used mode flags to control depth
- Scoped the check to a subdirectory

**Prerequisites:** craft installed, project with a linter configured (ESLint, Ruff, RuboCop, etc.).

---

## Step 1: Run a Full Lint Check

```
/craft:code:lint
```

Detects your linter and runs it:

```
Code Lint — my-project
───────────────────────
Linter: ESLint (found .eslintrc.js)

Results:
  src/api/auth.ts:45:12  error    'token' is defined but never used  no-unused-vars
  src/utils/format.ts:8:1  warning  Unexpected console.log             no-console

2 problems (1 error, 1 warning)
```

---

## Step 2: Lint a Specific Path

```
/craft:code:lint --path src/api
/craft:code:lint --path src/utils/format.ts
```

---

## Step 3: Use Execution Modes

```
/craft:code:lint             # Default: full check
/craft:code:lint debug       # Verbose output with rule details
/craft:code:lint optimize    # Fast, errors-only (warnings suppressed)
/craft:code:lint release     # Strict: treat warnings as errors
```

**Release mode** is the right choice before cutting a version — zero tolerance for warnings.

---

## Step 4: Dry Run (Preview Only)

```
/craft:code:lint --dry-run
```

Shows which linter command would run and which files would be checked.

---

## Step 5: Auto-Fix

Lint auto-fix is handled via `/craft:code:ci-local --fix` which applies `eslint --fix` (or equivalent) across the whole project. For targeted fixes, run the linter's fix mode directly.

---

## What's Next

- Add `code:lint` to your pre-push workflow via `/craft:check`
- Use `/craft:code:ci-local --only lint` for a lint-only CI mirror
- Use `release` mode before every `/release` run to catch warning debt
