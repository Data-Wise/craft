# Tutorial: ci:validate — Validate an Existing CI Workflow

By the end of this tutorial you will have:

- Validated your `.github/workflows/ci.yml` against your project configuration
- Identified mismatches between the workflow and detected project requirements
- Used `--fix` to auto-correct safe discrepancies

**Prerequisites:** craft installed, an existing `.github/workflows/` directory.

---

## Step 1: Validate the Default CI Workflow

```
/craft:ci:validate
```

Runs `ci:detect` to understand your project, then compares the detected requirements against the actual workflow file:

```
CI Validation — .github/workflows/ci.yml
──────────────────────────────────────────
Project:  Node.js / Jest / ESLint / TypeScript

Checks:
  ✅ Node version matches package.json engines (node: '20')
  ✅ npm ci before test steps
  ✅ Jest coverage step present
  ⚠️  ESLint step missing — detected .eslintrc.js but no lint step in workflow
  ⚠️  TypeScript build check missing — detected tsconfig.json but no tsc step

Issues: 2 warnings
```

---

## Step 2: Validate a Specific Workflow File

```
/craft:ci:validate --path .github/workflows/release.yml
```

---

## Step 3: Preview Fixes

```
/craft:ci:validate --dry-run
```

Shows what `--fix` would change without writing.

---

## Step 4: Auto-Fix Safe Issues

```
/craft:ci:validate --fix
```

Adds missing steps (lint, type-check) derived from project detection. Reviews each proposed change before writing.

---

## What's Next

- Use `/craft:ci:generate` if the workflow needs major restructuring rather than incremental fixes
- Run `/craft:code:ci-local` to test the validated steps locally before pushing
- Use `/craft:ci:watch` after pushing to monitor the first run with the fixed workflow
