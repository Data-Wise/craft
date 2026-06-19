# Tutorial: ci:generate — Generate a GitHub Actions Workflow

By the end of this tutorial you will have:

- Generated a complete GitHub Actions CI workflow for your project
- Customized the output with a template flag
- Used orchestration mode for multi-job workflows

**Prerequisites:** craft installed, `ci:detect` has been run (or will be run automatically).

---

## Step 1: Generate a Workflow

```
/craft:ci:generate
```

This runs `ci:detect` internally, then generates a `.github/workflows/ci.yml` file:

```yaml
name: CI
on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npx eslint .
      - run: npx jest --coverage
      - run: npx tsc --noEmit
```

---

## Step 2: Preview Before Writing

```
/craft:ci:generate --dry-run
```

Shows the generated YAML without writing the file. Review it before committing.

---

## Step 3: Use a Template

```
/craft:ci:generate --template minimal
/craft:ci:generate --template full
/craft:ci:generate --template release
```

- `minimal` — install + test only
- `full` — lint, test, build, coverage upload (default)
- `release` — full + publish step

---

## Step 4: Specify Output Path

```
/craft:ci:generate --output .github/workflows/test.yml
```

Useful for generating a separate workflow for PRs vs. main branch.

---

## Step 5: Generate with Orchestration

For complex multi-job setups:

```
/craft:ci:generate --orch
```

Uses the orchestrator to generate parallel job definitions, matrix strategies, and job dependency graphs.

---

## What's Next

- Run `/craft:ci:validate` to verify the generated workflow matches your project config
- Use `/craft:ci:watch` after pushing to monitor the first run
- See `/craft:ci:triage` if the first run fails
