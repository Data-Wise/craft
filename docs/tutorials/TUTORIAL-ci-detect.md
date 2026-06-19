# Tutorial: ci:detect — Detect Project CI Requirements

By the end of this tutorial you will have:

- Detected your project's build tools, test frameworks, and CI requirements automatically
- Understood the detection output format
- Used detection as the first step in CI generation

**Prerequisites:** craft installed, a project directory with code.

---

## Step 1: Run Detection

```
/craft:ci:detect
```

The command scans your project root and outputs a structured summary:

```
CI Detection Report — my-project
──────────────────────────────────
Language:     Node.js (package.json detected)
Package mgr:  npm (package-lock.json)
Test runner:  Jest (jest.config.js)
Lint:         ESLint (.eslintrc.js)
Build:        TypeScript (tsconfig.json)
Coverage:     Istanbul (via Jest --coverage)

Suggested CI steps:
  1. Install: npm ci
  2. Lint:    npx eslint .
  3. Test:    npx jest --coverage
  4. Build:   npx tsc --noEmit

Confidence: HIGH (all signals consistent)
```

---

## Step 2: Detect a Non-Root Path

For monorepos or scoped detection:

```
/craft:ci:detect --path packages/api
```

---

## Step 3: Output as JSON

For scripting or piping into other tools:

```
/craft:ci:detect --output json
```

---

## Step 4: Preview Without Writing

```
/craft:ci:detect --dry-run
```

Shows what would be detected without modifying any files. Useful before feeding into `ci:generate`.

---

## What's Next

- Use `/craft:ci:generate` to turn detection output into a full GitHub Actions workflow
- Use `/craft:ci:validate` to check an existing workflow against the detected requirements
- Run `/craft:code:ci-local` to execute the detected steps locally before pushing
