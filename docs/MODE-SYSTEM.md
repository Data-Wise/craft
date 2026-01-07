# Mode System Documentation

**Consolidated:** 2026-01-07
**Status:** Implemented and Tested
**Plugin:** rforge

This document consolidates the mode system development history into a comprehensive reference.

---

## Overview

The mode system provides time-budgeted analysis modes for RForge plugin commands, enabling users to control the depth and duration of analysis operations.

### Core Principles

1. **Modes are VERBS** - `debug`, `optimize`, `release` (not adjectives)
2. **Default = Fast** - All commands default to < 10s
3. **Explicit Only** - NO automatic mode detection
4. **Backward Compatible** - All existing commands work unchanged
5. **Performance Guarantees** - Strict time budgets enforced

---

## Mode Definitions

| Mode | Time Budget | Purpose | When to Use |
|------|-------------|---------|-------------|
| **default** | < 10s | Fast, lightweight | Daily check-ins, quick status |
| **debug** | 30s - 2m | Deep inspection | Finding bugs, investigating issues |
| **optimize** | 1-3m | Performance analysis | Speed improvements, profiling |
| **release** | 2-5m | Comprehensive validation | Before CRAN submission, releases |

### Usage Examples

```bash
# Default mode (fast)
/rforge:analyze
/rforge:status

# Explicit modes
/rforge:analyze --mode debug
/rforge:status --mode optimize
/rforge:analyze --mode release
```

---

## Design Decisions

### Why Time Budgets?

**Problem:** Analysis tools can take arbitrarily long, creating unpredictable user experience.

**Solution:** Strict time budgets with guaranteed completion times.

**Benefits:**
- Predictable performance
- Clear user expectations
- Prevents analysis paralysis
- Forces prioritization of checks

### Why Not Auto-Detection?

**Decision:** Explicit mode selection only (no automatic mode detection based on context).

**Rationale:**
- Predictable behavior
- No surprises
- User maintains control
- Simpler implementation
- Easier to debug

**User can always:**
- Start with default (fast)
- Upgrade to debug if needed
- Escalate to release for comprehensive checks

---

## Implementation

### Command Structure

Commands supporting modes follow this pattern:

```python
def analyze(mode: str = "default", format: str = "terminal"):
    """
    Analyze R package with specified mode.

    Args:
        mode: Analysis depth (default, debug, optimize, release)
        format: Output format (terminal, json, markdown)
    """
    # Get time budget for mode
    budget = get_time_budget(mode)

    # Execute analysis within budget
    with TimeLimit(budget):
        results = perform_analysis(mode)

    # Format and return results
    return format_output(results, format)
```

### MCP Server Integration

Mode parameter added to RForge MCP tools:

```typescript
// MCP tool definition
{
  name: "analyze_package",
  description: "Analyze R package structure",
  inputSchema: {
    type: "object",
    properties: {
      path: { type: "string" },
      mode: {
        type: "string",
        enum: ["default", "debug", "optimize", "release"],
        default: "default"
      }
    }
  }
}
```

---

## Testing Strategy

### Unit Tests

- Mode parameter parsing
- Time budget enforcement
- Format output validation
- Backward compatibility

### Integration Tests

- End-to-end command execution
- MCP server tool calls
- Mode switching behavior
- Performance within budgets

### Performance Tests

- Actual execution times vs. budgets
- Quality metrics per mode
- Regression testing

**Results:** 96 tests, 100% pass rate, 0.44s execution time

---

## Deployment

### CI/CD Pipeline

**GitHub Actions Workflows:**
1. **validate.yml** - Multi-Python testing (3.9-3.12)
2. **docs.yml** - Documentation deployment
3. **benchmark.yml** - Performance validation

**All workflows passing** ✅

### Pre-commit Hooks

- JSON validation (plugin.json, package.json)
- Plugin structure validation
- Performance benchmark checks

---

## Performance Monitoring

### Time Budget Tracking

Each command execution logs:
- Mode selected
- Actual execution time
- Budget compliance (within/exceeded)
- Quality metrics achieved

### Quality Metrics

**Tracked per mode:**
- Issues found
- False positive rate
- Coverage percentage
- User satisfaction

**Results:**
- default: Fast baseline, catches common issues
- debug: Deep inspection, comprehensive diagnostics
- optimize: Performance focused, identifies bottlenecks
- release: Full validation, production-ready checks

---

## Before & After Comparison

### Before Mode System

```bash
/rforge:analyze    # Time: Unknown (5s - 5min)
                   # Behavior: Unpredictable
                   # User: Frustrated by inconsistency
```

**Problems:**
- Unpredictable execution time
- No control over depth
- Can't plan workflow
- Analysis paralysis

### After Mode System

```bash
/rforge:analyze               # < 10s guaranteed
/rforge:analyze --mode debug  # 30s-2m, deep inspection
/rforge:analyze --mode release # 2-5m, comprehensive
```

**Benefits:**
- Predictable performance
- User controls depth
- Clear expectations
- Workflow planning possible

---

## Future Enhancements

### Planned Features

1. **Custom Time Budgets**
   - User-configurable budgets in settings
   - Override defaults per-project

2. **Result Caching**
   - Cache analysis results
   - Skip unchanged files
   - Faster repeated runs

3. **Progressive Analysis**
   - Start fast, offer to go deeper
   - Upgrade mode on-the-fly
   - Adaptive based on findings

4. **Mode Presets**
   - Save favorite configurations
   - Quick mode switching
   - Team shared presets

---

## Lessons Learned

### What Worked Well

✅ **Time budgets** - Enforced predictability
✅ **Explicit modes** - No surprising behavior
✅ **Backward compatibility** - Smooth transition
✅ **Comprehensive testing** - High confidence
✅ **Clear documentation** - Easy onboarding

### Challenges Overcome

⚠️ **Performance tuning** - Balancing speed vs. thoroughness
⚠️ **Mode naming** - Finding clear, intuitive names
⚠️ **Testing strategy** - Covering all mode combinations

### Would Do Differently

💡 **Earlier user testing** - Get feedback sooner
💡 **Progressive disclosure** - Start simpler, add modes gradually
💡 **Better metrics** - Track quality per mode from day 1

---

## References

### Original Development Documents

All source documents archived in `sessions/mode-system-development/`:

- MODE-SYSTEM-DESIGN.md - Technical specification
- MODE-SYSTEM-SUMMARY.md - Overview and quick reference
- MODE-SYSTEM-IMPLEMENTATION.md - Implementation details
- MODE-SYSTEM-TESTING-GUIDE.md - Testing strategy
- MODE-SYSTEM-TESTING-STRATEGY.md - Comprehensive testing
- MODE-SYSTEM-DEPLOYMENT-PLAN.md - Deployment approach
- MODE-SYSTEM-CICD-PIPELINE.md - CI/CD automation
- MODE-SYSTEM-MONITORING.md - Performance tracking
- MODE-SYSTEM-BEFORE-AFTER.md - Comparison analysis

### Related Documentation

- [CLAUDE.md](CLAUDE.md) - Developer guide
- RForge plugin documentation: `rforge/README.md` in repository root
- Test suite documentation: `rforge/docs/TESTING.md` in repository root

---

**Last Updated:** 2026-01-07
**Maintained By:** Data-Wise Team
