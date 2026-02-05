# /craft:code:deps-audit

> **Security audit of dependencies for known vulnerabilities**

---

## Synopsis

```bash
/craft:code:deps-audit [--fix] [--json] [--ignore CVE] [--fail-on severity] [--dry-run|-n]
```

**Quick examples:**

```bash
# Run security audit
/craft:code:deps-audit

# Auto-fix vulnerabilities
/craft:code:deps-audit --fix

# CI mode - fail on high severity
/craft:code:deps-audit --fail-on high

# Ignore known false positive
/craft:code:deps-audit --ignore CVE-2023-1234

# Preview audit plan
/craft:code:deps-audit --dry-run
```

---

## Description

Audits project dependencies for known security vulnerabilities by checking against CVE databases, GitHub Advisory, and language-specific vulnerability databases. Scans both direct and transitive dependencies, reports severity levels, and suggests remediation paths.

---

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--fix` | Auto-fix vulnerabilities where possible | false |
| `--json` | Output results as JSON | false |
| `--ignore CVE` | Ignore specific CVE identifier | - |
| `--fail-on level` | Fail on severity level (critical\|high\|medium\|low) | - |
| `--dry-run` / `-n` | Preview audit commands without executing | false |

---

## Project Type Detection

| Project | Tool | Database |
|---------|------|----------|
| Python | pip-audit, safety | PyPI Advisory Database |
| JavaScript | npm audit | npm Advisory Database |
| R | oysteR | R Advisory Database |
| Go | govulncheck | Go Vulnerability Database |
| Rust | cargo audit | RustSec Advisory Database |

---

## Output Format

```text
Security audit...

CRITICAL (1):
  requests 2.28.0
    CVE-2023-32681 - Unintended leak of Proxy-Auth header
    Fix: upgrade to >= 2.31.0

HIGH (0):
  None

MEDIUM (2):
  numpy 1.24.0
    CVE-2023-XXXX - Buffer overflow in...
    Fix: upgrade to >= 1.25.0

Summary: 1 critical, 0 high, 2 medium, 0 low
Run with --fix to auto-fix
```

---

## See Also

- [/craft:code:ci-local](ci-local.md) — Run full CI suite locally
- [/craft:check](../check.md) — Pre-flight validation
