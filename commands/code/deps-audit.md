---
description: Security audit of dependencies for known vulnerabilities
category: code
arguments:
  - name: fix
    description: Auto-fix vulnerabilities where possible
    required: false
    default: false
  - name: json
    description: Output results as JSON
    required: false
    default: false
  - name: ignore
    description: Ignore specific CVE
    required: false
  - name: fail-on
    description: Fail on severity level (critical|high|medium|low)
    required: false
  - name: dry-run
    description: Preview audit commands without executing them
    required: false
    default: false
    alias: -n
---

# /craft:code:deps-audit - Security Audit

Audit dependencies for known security vulnerabilities.

## Usage

```bash
/craft:code:deps-audit                  # Run security audit
/craft:code:deps-audit --fix            # Auto-fix vulnerabilities
/craft:code:deps-audit --fail-on high   # CI mode
/craft:code:deps-audit --ignore CVE-... # Ignore specific CVE
/craft:code:deps-audit --dry-run        # Preview audit
/craft:code:deps-audit -n               # Preview audit
```

## Dry-Run Mode

Preview security audit commands:

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Security Audit                                    │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Project Detection:                                          │
│   - Type: Python                                              │
│   - Package manager: uv                                       │
│   - Dependencies: 45 packages (12 direct, 33 transitive)      │
│   - Lock file: uv.lock                                        │
│                                                               │
│ ✓ Audit Tools:                                                │
│   1. pip-audit (primary)                                      │
│      Command: uv run pip-audit                                │
│      Database: PyPI Advisory Database                         │
│      Scope: All installed packages                            │
│      Estimated: ~8 seconds                                    │
│                                                               │
│   2. safety (fallback)                                        │
│      Command: safety check                                    │
│      Database: Safety DB                                      │
│      Status: Available if pip-audit fails                     │
│                                                               │
│ ✓ Check Process:                                              │
│   - Scan 45 packages for known CVEs                           │
│   - Query vulnerability databases                             │
│   - Match versions against advisory records                   │
│   - Calculate severity scores (CVSS)                          │
│   - Identify upgrade paths                                    │
│                                                               │
│ ✓ Output Format:                                              │
│   - Group by severity: CRITICAL, HIGH, MEDIUM, LOW            │
│   - For each vulnerability:                                   │
│     • Package name and version                                │
│     • CVE identifier                                          │
│     • Description                                             │
│     • Fix recommendation (upgrade version)                    │
│                                                               │
│ ⚠ Notes:                                                      │
│   • Read-only scan (no auto-fix unless --fix flag)           │
│   • Checks transitive dependencies                            │
│   • May report false positives (use --ignore)                 │
│   • Results depend on database freshness                      │
│                                                               │
│ 📊 Summary: 45 packages, ~8 seconds                           │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

**Note**: Dry-run shows the audit plan without actually scanning packages. Use this to understand what will be checked before running the potentially time-consuming audit.

## What This Does

1. **Scans dependencies** including transitive dependencies
2. **Checks vulnerability databases** (CVE, GitHub Advisory, etc.)
3. **Reports severity levels** (critical, high, medium, low)
4. **Suggests remediations** with upgrade paths

## Project Type Detection

| Project | Tool | Database |
|---------|------|----------|
| Python | pip-audit, safety | PyPI Advisory |
| JavaScript | npm audit | npm Advisory |
| R | oysteR | R Advisory |
| Go | govulncheck | Go Vuln DB |
| Rust | cargo audit | RustSec |

## Options

- `--fix` - Auto-fix where possible
- `--json` - Output as JSON
- `--ignore <CVE>` - Ignore specific CVE
- `--fail-on <level>` - Fail on severity level

## Examples

```bash
# Run security audit
/craft:code:deps-audit

# Auto-fix vulnerabilities
/craft:code:deps-audit --fix

# CI mode - fail on high severity
/craft:code:deps-audit --fail-on high

# Ignore known false positive
/craft:code:deps-audit --ignore CVE-2023-1234
```

## Output

```
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

  pillow 9.4.0
    CVE-2023-YYYY - DoS via crafted image
    Fix: upgrade to >= 9.5.0

Summary: 1 critical, 0 high, 2 medium, 0 low
Run with --fix to auto-fix
```

## Integration

Works with:

- `/craft:code:deps-check` - Dependency health
- `/craft:ci:local` - Pre-commit checks
- `/craft:code:release` - Release validation
