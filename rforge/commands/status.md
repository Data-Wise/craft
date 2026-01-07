---
name: rforge:status
description: Ecosystem-wide status dashboard with mode-specific detail levels
arguments:
  - name: package
    description: Package name (optional, defaults to current or ecosystem)
    required: false
    type: string
  - name: mode
    description: Status detail level (debug, optimize, release)
    required: false
    type: string
    default: "default"
  - name: format
    description: Output format (json, markdown, terminal)
    required: false
    type: string
    default: "terminal"
tags: ["rforge", "status", "ecosystem"]
version: 2.0.0
---

# /rforge:status - Mode-Aware Status Dashboard

Get comprehensive status information for your R package ecosystem with explicit control over detail level.

## Mode System

**Current Mode:** {{mode | default: "default"}}

### Mode Selection

Parse the user's request to detect mode:
- If user explicitly provides "debug", "optimize", or "release" → use that mode
- Otherwise → use "default" mode (quick dashboard)

### Default Mode (2-5 seconds)

**Purpose:** Daily check-ins, morning stand-up, quick validation

**Behavior:**
- Overall health score (0-100)
- Active warnings (critical severity only)
- Git status (clean/dirty, branch)
- Last update timestamp
- Quick summary of ecosystem state

**Data Retrieved:**
- Package count and names
- Critical issues only
- Basic test status (pass/fail)
- CRAN check status (if recent)

**Time Budget:** MUST complete in < 5 seconds

**Output Format:**
```
📊 STATUS: mediationverse ecosystem

Overall Health: 87/100 (B+)

✅ medfit          92/100
⚠️  probmed        78/100  (2 warnings)
✅ medsim          85/100
✅ mediationverse  91/100

Critical Issues: 1
  • probmed: Missing NEWS.md entry

Last Updated: 2 hours ago
Git: Clean, branch: main
```

### Debug Mode (15-30 seconds)

**Purpose:** Investigating issues, understanding problems, detailed diagnostics

**Behavior:**
- Per-package health breakdown
- All warnings (all severity levels)
- Dependency tree visualization
- Test coverage metrics per package
- Documentation coverage per package
- Known issues list with details

**Data Retrieved:**
- Complete dependency graph
- All test results with details
- Documentation completeness per function
- Recent changes analysis
- Build logs (if available)
- Environment diagnostics

**Time Budget:** SHOULD complete in < 30 seconds

**Output Format:**
```
📊 DETAILED STATUS: mediationverse ecosystem

Overall Health: 87/100 (B+)

═══════════════════════════════════════════
Package: medfit v2.1.0
═══════════════════════════════════════════
Health: 92/100 (A-)
Tests: 187/187 passing (94% coverage)
  • R/mediation.R: 98% coverage
  • R/bootstrap.R: 91% coverage
  • R/utils.R: 87% coverage
CRAN: ✅ All checks OK
Docs: 24/25 functions documented (96%)
  • Missing: .internal_helper
Dependencies: 12 direct, 34 total
  ✅ All current versions
Issues: 1 warning
  ⚠️ NEWS.md needs entry for v2.1.1
Last Updated: 2 hours ago

═══════════════════════════════════════════
Package: probmed v1.3.0
═══════════════════════════════════════════
Health: 78/100 (C+)
Tests: 95/98 passing (84% coverage)
  ❌ 3 failures in test-edge-cases.R
  • Low coverage: R/sensitivity.R (67%)
CRAN: ⚠️ 2 NOTEs
  • NOTE: Package size (3.2 MB)
  • NOTE: GNU make required
Docs: 18/20 functions documented (90%)
  • Missing: calc_internal, validate_args
Dependencies: 8 direct, 28 total
  ⚠️ 1 outdated: boot (1.3-28 → 1.3-30)
Issues: 4 warnings
  ⚠️ NEWS.md missing entry
  ⚠️ 3 test failures
  ⚠️ Low coverage on sensitivity.R
  ⚠️ Outdated dependency: boot
Last Updated: 5 hours ago

Dependency Tree:
medfit ← probmed ← medsim ← mediationverse
  └─> boot, MASS, stats
```

### Optimize Mode (30s - 1 minute)

**Purpose:** Performance tuning, identifying slow components, resource optimization

**Behavior:**
- Package load times per package
- Test execution times per suite
- Build times (R CMD build)
- Slow functions identified (top 5)
- Resource usage statistics
- Dependency bloat analysis

**Data Retrieved:**
- Load time profiling
- Test timing breakdown
- Build performance metrics
- Function execution profiles
- Memory usage patterns
- Dependency size analysis

**Time Budget:** SHOULD complete in < 1 minute

**Output Format:**
```
📊 PERFORMANCE STATUS: mediationverse ecosystem

Overall Health: 87/100 (B+)

⚡ Performance Metrics
═══════════════════════════════════════════

Load Times:
  medfit:          0.8s  ✅ Fast
  probmed:         1.2s  ✅ Fast
  medsim:          2.4s  ⚠️ Slow
  mediationverse:  0.3s  ✅ Fast

Test Execution:
  medfit:          12.3s (187 tests)  ✅ 66ms/test
  probmed:         18.7s (98 tests)   ⚠️ 191ms/test
  medsim:          45.2s (156 tests)  ❌ 290ms/test (SLOW!)
  mediationverse:  3.1s (24 tests)    ✅ 129ms/test

Build Times:
  medfit:          8.2s   ✅
  probmed:         11.4s  ✅
  medsim:          23.8s  ⚠️ Slow
  mediationverse:  4.1s   ✅

🐌 Slow Functions (Top 5):
  1. medsim::run_simulation     3.2s  (heavy computation)
  2. probmed::bootstrap_ci       1.8s  (1000 iterations)
  3. medsim::parallel_setup      0.9s  (cluster init)
  4. medfit::fit_complex_model   0.7s  (optimization)
  5. probmed::validate_inputs    0.4s  (excessive checks)

💡 Optimization Opportunities:
  • medsim: Cache simulation results (save ~2s)
  • probmed: Vectorize bootstrap (save ~0.8s)
  • medsim: Lazy parallel setup (save ~0.9s)
  • Total potential savings: ~3.7s (15% improvement)

Dependency Analysis:
  Total Size: 15.4 MB
  Largest: medsim (8.2 MB - simulation data)
  Suggestion: Consider moving large datasets to separate package
```

### Release Mode (1-2 minutes)

**Purpose:** Pre-release validation, CRAN preparation, release readiness

**Behavior:**
- CRAN compliance check
- Version number validation (semantic versioning)
- NEWS.md completeness check
- Documentation currency validation
- Test coverage requirements (>80% target)
- Breaking change summary
- Reverse dependency impact

**Data Retrieved:**
- R CMD check results (all platforms)
- CRAN policy compliance
- Version consistency across ecosystem
- NEWS.md completeness
- Documentation completeness
- Reverse dependency list
- Breaking change analysis

**Time Budget:** SHOULD complete in < 2 minutes

**Output Format:**
```
📊 RELEASE READINESS: mediationverse ecosystem

Overall Health: 87/100 (B+)

🎯 Release Status
═══════════════════════════════════════════

medfit v2.1.0 → v2.1.1
  ✅ CRAN Checks: All platforms OK
  ✅ Version: Valid semantic version
  ⚠️ NEWS.md: Missing entry for v2.1.1
  ✅ Documentation: 96% complete (24/25)
  ✅ Test Coverage: 94% (meets 80% requirement)
  ✅ Breaking Changes: None detected
  ✅ Reverse Dependencies: 3 packages
     • All will remain compatible

  READINESS: 95% (READY after NEWS.md update)

probmed v1.3.0 → v1.3.1
  ⚠️ CRAN Checks: 2 NOTEs (acceptable)
  ✅ Version: Valid semantic version
  ❌ NEWS.md: Missing entry for v1.3.1
  ⚠️ Documentation: 90% complete (18/20)
  ❌ Test Coverage: 84% but 3 failures!
  ⚠️ Breaking Changes: 1 function signature changed
     • calc_sensitivity(data, method) → calc_sensitivity(data, method, alpha)
     • Impact: LOW (argument has default)
  ✅ Reverse Dependencies: 2 packages
     • May need notification about API change

  READINESS: 65% (NOT READY - fix tests first)

medsim v0.9.5 → v1.0.0
  ✅ CRAN Checks: All OK
  ✅ Version: Major version bump (API stable)
  ✅ NEWS.md: Complete
  ✅ Documentation: 100% complete
  ✅ Test Coverage: 89% (meets requirement)
  ⚠️ Breaking Changes: 2 functions removed
     • old_simulate() → use run_simulation()
     • legacy_plot() → use plot_results()
     • Impact: MEDIUM (deprecated in v0.9.0)
  ⚠️ Reverse Dependencies: 1 package needs update
     • mediationverse still uses old_simulate()

  READINESS: 80% (READY after mediationverse update)

📋 Release Sequence Recommendation:
  1. Fix probmed tests (2 hours)
  2. Update NEWS.md files (30 min)
  3. Update mediationverse for medsim v1.0.0 (1 hour)
  4. Release sequence: medfit → probmed → medsim → mediationverse
  5. Total effort: 4 hours over 2 days

⚠️ CRAN Submission Checklist:
  ✅ R CMD check clean (all packages)
  ⚠️ NEWS.md complete (2 need updates)
  ✅ Version numbers valid
  ⚠️ No test failures (probmed needs fix)
  ✅ Documentation complete (>90% all packages)
  ✅ No major breaking changes without migration path

OVERALL READINESS: 75% (Address 3 issues before release)
```

## Implementation Instructions

You are using the `rforge_status` MCP tool to gather status information. Follow this workflow:

### Step 1: Detect Mode

```
If user provides --mode argument:
    mode = argument value
Else if user mentions "detailed", "debug", "all" in context:
    mode = "debug"
Else if user mentions "performance", "speed", "slow" in context:
    mode = "optimize"
Else if user mentions "release", "CRAN", "ready" in context:
    mode = "release"
Else:
    mode = "default"
```

### Step 2: Set Time Budget

```
time_budgets = {
    "default": 5 seconds,
    "debug": 30 seconds,
    "optimize": 60 seconds,
    "release": 120 seconds
}

Start timer
```

### Step 3: Call MCP Tool with Mode

```
Use Task tool to call rforge_status:
  - package: {{package | default: "ecosystem"}}
  - mode: {{mode}}
  - format: {{format}}
```

### Step 4: Format Output

Based on mode and format parameter:
- **Default + terminal**: Quick dashboard with emojis
- **Debug + terminal**: Detailed breakdown with tree views
- **Optimize + terminal**: Performance metrics with charts
- **Release + terminal**: Release readiness with checklist
- **Any + json**: Structured JSON for scripting
- **Any + markdown**: Documentation-friendly markdown

**Implementation:**

```python
# Import formatters from rforge/lib/formatters.py
import sys
from pathlib import Path
rforge_lib = Path(__file__).parent.parent / "rforge" / "lib"
sys.path.insert(0, str(rforge_lib))

from formatters import format_output

# Structure your status results
data = {
    "title": "Ecosystem Status Dashboard",
    "status": "success",  # or "warning" if issues found
    "data": {
        "mode": mode,
        "overall_health": 87,
        "packages": {
            "medfit": {"health": 92, "status": "healthy"},
            "probmed": {"health": 78, "status": "warning", "issues": 2}
        },
        "critical_issues": 1,
        "last_updated": "2 hours ago"
    }
}

# Format based on user preference
output = format_output(
    data=data,
    format_name=format,  # "terminal", "json", or "markdown"
    mode=mode,
    package_name=package if package else "ecosystem"  # optional metadata
)

# Display formatted output
print(output)
```

**Data Structure Guidelines:**

- **title**: Dashboard title (e.g., "Ecosystem Status", "Package Status: medfit")
- **status**: "success" (healthy), "warning" (has issues), "error" (critical problems)
- **data**: Dictionary with status information (flexible structure based on mode)

**Format-Specific Behavior:**

- **Terminal**: Adds emojis (✅ ❌ ⚠️ ℹ️), colors via Rich, tables and bullet lists
- **JSON**: Wraps in metadata envelope with timestamp, mode, and package name
- **Markdown**: Creates H1 title, bold status, structured sections with JSON code blocks

### Step 5: Verify Time Budget

If approaching time budget:
- Return partial results
- Show warning
- Explain what was checked and what was skipped

## Package Selection

{{package | default: "Current package or ecosystem"}}

If no package specified:
1. Try to detect from current directory
2. Fall back to ecosystem-wide status
3. Show all packages found in workspace

## Usage Examples

### Basic Usage (Default Mode)

```bash
/rforge:status
# Quick dashboard in < 5s

/rforge:status medfit
# Quick status for specific package
```

### Explicit Mode

```bash
/rforge:status --mode debug
# Detailed breakdown in < 30s

/rforge:status --mode optimize
# Performance metrics in < 1m

/rforge:status --mode release
# Release readiness in < 2m
```

### Mode + Format

```bash
/rforge:status --mode debug --format json
# Detailed status as JSON for scripting

/rforge:status --mode release --format markdown
# Release readiness as markdown report
```

### Package-Specific

```bash
/rforge:status medfit --mode debug
# Detailed status for medfit only

/rforge:status medfit --mode release
# Release readiness for medfit
```

## Backward Compatibility

All existing usage patterns continue to work:

```bash
/rforge:status              # Uses default mode
/rforge:status medfit       # Uses default mode for package
/rforge:status --detailed   # Maps to debug mode
```

**No breaking changes** - default mode provides fast, actionable status.

## Performance Guarantees

- **Default mode**: MUST complete in < 5 seconds (hard requirement)
- **Debug mode**: SHOULD complete in < 30 seconds (target)
- **Optimize mode**: SHOULD complete in < 1 minute (target)
- **Release mode**: SHOULD complete in < 2 minutes (target)

## Quality Guarantees

- **Default**: Shows critical issues, always actionable
- **Debug**: Shows all issues with root causes
- **Optimize**: Identifies performance bottlenecks with quantified impact
- **Release**: Provides CRAN submission confidence with checklist

## Output Format

{{format | default: "terminal"}}

## Use When

- **Default mode**: Daily stand-up, quick check before commits
- **Debug mode**: Investigating issues, need full picture
- **Optimize mode**: Performance tuning, finding slow spots
- **Release mode**: Pre-CRAN submission, release planning

## ADHD-Friendly Features

✅ **Fast by default** - Results in < 5 seconds (default mode)
✅ **Scannable** - Clear visual hierarchy with emojis
✅ **Actionable** - Always shows what to do next
✅ **Progressive detail** - Choose depth vs speed
✅ **Predictable** - Know what to expect from each mode

## Related Commands

- `/rforge:analyze` - Full analysis with mode support
- `/rforge:quick` - Ultra-fast status (always < 5s, ignores modes)
- `/rforge:doc-check` - Documentation-focused status
- `/rforge:detect` - Find packages in workspace

## Troubleshooting

**"Status too slow"**
- Default mode should be < 5s - if not, report as bug
- Use default mode for daily checks
- Reserve debug/optimize/release for specific needs

**"Not enough detail"**
- Use --mode debug for complete breakdown
- Default mode shows critical issues only

**"Mode not recognized"**
- Valid modes: default, debug, optimize, release
- Mode names are case-insensitive

---

## Implementation Notes for Claude

When executing this command:

1. **Parse mode** from user request (explicit flag or context hints)
2. **Respect time budget** - default mode MUST be < 5s
3. **Use Task tool** to delegate to `rforge_status` MCP tool with mode parameter
4. **Format appropriately** based on format parameter
5. **Make output scannable** - use visual hierarchy
6. **Track timing** and warn if approaching budget
7. **Maintain backward compatibility** - no mode = default mode

**Remember:**
- Default mode is optimized for frequent use (daily check-ins)
- Mode names are VERBS describing intent (debug, optimize, release)
- NO automatic mode detection (explicit only, except context hints)
- Always provide actionable next steps

**Example Task Delegation:**

```
Use Task tool to call rforge_status MCP tool:
  - package: {{package | default: "ecosystem"}}
  - mode: {{mode}}
  - detail_level: [mode-specific detail level]
  - include_metrics: [mode-specific metrics]
  - time_budget: {{time_budget}}
  - format: {{format}}
```

---

**Version 2.0.0** - Mode System Implementation
**Updated:** 2024-12-24
**Status:** ✅ Ready for use
