# Tutorial: code:deps-audit — Security Audit Dependencies

By the end of this tutorial you will have:

- Audited your project's dependencies for known vulnerabilities
- Filtered results by severity
- Used `--fix` to auto-apply safe updates

**Prerequisites:** craft installed, `npm`/`pip`/`bundle` on PATH depending on your project type.

---

## Step 1: Run the Audit

```
/craft:code:deps-audit
```

Detects your package manager and runs the appropriate audit tool:

```
Dependency Security Audit — my-project
────────────────────────────────────────
Package manager: npm
Packages audited: 847

Vulnerabilities found:
  HIGH   lodash@4.17.15 — prototype pollution (CVE-2020-8203)
           Fix: upgrade to lodash@4.17.21
  MEDIUM express@4.18.1 — open redirect (CVE-2022-24999)
           Fix: upgrade to express@4.18.2
  LOW    minimist@1.2.5 — prototype pollution
           Fix: upgrade to minimist@1.2.6 (dev dependency)

Summary: 1 HIGH, 1 MEDIUM, 1 LOW
```

---

## Step 2: Filter by Severity

```
/craft:code:deps-audit --fail-on high
/craft:code:deps-audit --fail-on moderate
```

Exit code 1 only if vulnerabilities at or above the threshold are found. Useful in CI.

---

## Step 3: Ignore Specific Advisories

```
/craft:code:deps-audit --ignore CVE-2022-24999
```

For accepted risks with a documented exception.

---

## Step 4: Auto-Fix Safe Updates

```
/craft:code:deps-audit --fix
```

Applies `npm audit fix` (or equivalent) for vulnerabilities with non-breaking fixes available.

---

## Step 5: JSON Output

```
/craft:code:deps-audit --json
```

Returns structured vulnerability data for integration with security dashboards.

---

## Step 6: Dry Run

```
/craft:code:deps-audit --dry-run
```

Shows what `--fix` would change without applying it.

---

## What's Next

- Add `--fail-on high` to your CI workflow via `/craft:ci:generate`
- Run after every `npm install` or dependency update
- Use `/craft:code:ci-local` for the full pre-push check including deps audit
