# ORCHESTRATE: Pin markdownlint-cli2 in CI

**Feature Branch:** `feature/pin-markdownlint`
**Spec:** `docs/specs/SPEC-pin-markdownlint-ci-2026-02-26.md`
**Brainstorm:** `BRAINSTORM-pin-markdownlint-ci-2026-02-26.md`
**Created:** 2026-02-26
**Estimated:** ~60 min (1 session)

---

## Goal

Eliminate CI flakiness caused by npm registry HTTP 403 errors by pinning `markdownlint-cli2` as an exact-version devDependency, committing `package-lock.json`, and updating all 10 files that invoke markdownlint to use the local install.

---

## Increments

### Increment 1: Pin version and commit lockfile (10 min)

**Files:** `package.json`, `package-lock.json`, `.gitignore`

Tasks:

- [ ] Change `package.json` devDependency from `"^0.14.0"` to `"0.14.0"` (exact pin)
- [ ] Also pin `markdown-link-check` to exact version while we're here
- [ ] Run `npm install` to regenerate `package-lock.json` with exact version
- [ ] Check if `package-lock.json` is in `.gitignore` -- remove if so
- [ ] `git add package.json package-lock.json`

**Verify:**

```bash
node -e "console.log(require('./package.json').devDependencies)"
# Should show "0.14.0" not "^0.14.0"
```

---

### Increment 2: Update CI workflows (15 min)

**Files:** `.github/workflows/ci.yml`, `.github/workflows/docs-quality.yml`

Tasks:

- [ ] **ci.yml**: Add Node.js setup step before test suite

  ```yaml
  - name: Setup Node.js
    uses: actions/setup-node@v4
    with:
      node-version: '20'
      cache: 'npm'

  - name: Install npm dependencies
    run: npm ci
  ```

- [ ] **docs-quality.yml**: Replace `npm install --save-dev markdownlint-cli2` with `npm ci`
- [ ] **docs-quality.yml**: Verify `setup-node` already has `cache: 'npm'` (line 39)

**Verify:**

```bash
grep -n "npm ci\|npm install" .github/workflows/ci.yml .github/workflows/docs-quality.yml
# Should show only "npm ci", no "npm install --save-dev"
```

---

### Increment 3: Update hook, script, and utils (10 min)

**Files:** `scripts/hooks/pre-commit-markdownlint.sh`, `scripts/docs-lint.sh`, `utils/docs_update_orchestrator.py`

Tasks:

- [ ] **pre-commit-markdownlint.sh**: Remove `-y` flag from all 3 `npx` calls (lines 53, 76, 90)
- [ ] **docs-lint.sh**: Update resolution order in `detect_markdownlint` function (lines 41-44)

  ```bash
  if [ -x "./node_modules/.bin/markdownlint-cli2" ]; then
      echo "./node_modules/.bin/markdownlint-cli2"
  elif command -v markdownlint-cli2 &>/dev/null; then
      echo "markdownlint-cli2"
  else
      echo "npx markdownlint-cli2"
  fi
  ```

- [ ] **docs_update_orchestrator.py**: Remove `-y` from subprocess call (line 531)
  - Change `["npx", "markdownlint-cli2", ...]` (already no -y? verify)

**Verify:**

```bash
grep -rn "npx -y" scripts/ utils/
# Should return zero results
```

---

### Increment 4: Update test files (15 min)

**Files:** `tests/test_markdownlint_list_spacing_unit.py`, `tests/test_markdownlint_list_spacing_e2e.py`, `tests/test_markdownlint_list_spacing_validation.py`

Tasks:

- [ ] **unit tests**: Replace all `["npx", "-y", "markdownlint-cli2", ...]` with `["npx", "markdownlint-cli2", ...]` (14 calls)
- [ ] **e2e tests**: Same replacement (10 calls)
- [ ] **validation tests**: Same replacement (4 calls)
- [ ] Use `replace_all` or sed for bulk replacement: `"-y", "markdownlint-cli2"` -> `"markdownlint-cli2"`

**Verify:**

```bash
grep -rn '"npx", "-y"' tests/
# Should return zero results
```

---

### Increment 5: Verify (10 min)

Tasks:

- [ ] Run full test suite: `python3 -m pytest tests/ -v`
- [ ] Run markdownlint locally: `npx markdownlint-cli2 "docs/**/*.md" --config .markdownlint.json`
- [ ] Run pre-commit hook: `pre-commit run markdownlint-cli2 --all-files`
- [ ] Verify no `npx -y` anywhere: `grep -rn "npx -y" --include="*.py" --include="*.sh" --include="*.yml" .`
- [ ] Create PR: `gh pr create --base dev`

---

## Done Criteria

- [ ] Zero occurrences of `npx -y markdownlint-cli2` in codebase
- [ ] `package-lock.json` committed to git
- [ ] `npm ci` in both CI workflows with npm cache
- [ ] `docs-lint.sh` resolves local install first
- [ ] All 112 tests pass
- [ ] PR created to dev
