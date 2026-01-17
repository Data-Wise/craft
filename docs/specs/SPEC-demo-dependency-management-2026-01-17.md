# SPEC: Demo Dependency Management

**Version:** 1.0
**Date:** 2026-01-17
**Status:** In Progress (Research Complete)
**Branch:** `feature/demo-dependency-management`
**Authors:** arch-1 (architecture), doc-1 (codebase research)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Design](#architecture-design)
3. [Codebase Research Findings](#codebase-research-findings)
4. [Implementation Roadmap](#implementation-roadmap)
5. [Reference Files](#reference-files)

---

## Executive Summary

This specification defines the architecture for embedding dependency checking, auto-installation, and batch conversion into the `/craft:docs:demo` command. The design follows Claude Code plugin patterns (YAML frontmatter, progressive enhancement) and prioritizes **informed consent**, **graceful degradation**, and **session-level caching**.

**Key Principles:**
1. **Non-intrusive** - Dependencies checked only when needed
2. **Multi-strategy** - Fallback installation methods (brew → cargo → binary)
3. **Informed consent** - User approves installations explicitly
4. **Cache-optimized** - Session-level caching avoids redundant checks
5. **Graceful degradation** - Suggest alternatives when tools missing

**Total Effort:** 24h implementation + 8h testing + 4h docs = 36 hours (4 phases)

---

## Architecture Design

### 1. Dependency Declaration Format

#### 1.1 Frontmatter Schema (YAML)

Add to `commands/docs/demo.md` frontmatter:

```yaml
---
description: Terminal Recording & GIF Generator
dependencies:
  asciinema:
    required: true
    purpose: "Record real terminal sessions"
    methods: ["asciinema"]  # When this tool is needed
    install:
      brew: "asciinema"
      apt: "asciinema"
      yum: "asciinema"
    version:
      min: "2.0.0"
      check_cmd: "asciinema --version | grep -oE '[0-9.]+' | head -1"
    health:
      check_cmd: "asciinema --help"
      expect_exit: 0

  agg:
    required: true
    purpose: "Convert .cast to .gif"
    methods: ["asciinema"]
    install:
      cargo: "agg"
      cargo_git: "https://github.com/asciinema/agg"
      binary:
        url: "https://github.com/asciinema/agg/releases/latest/download/agg-{{arch}}-apple-darwin"
        arch_map:
          x86_64: "x86_64"
          arm64: "aarch64"
        target: "/usr/local/bin/agg"
    version:
      min: "1.4.0"
      check_cmd: "agg --version 2>&1 | grep -oE '[0-9.]+' | head -1"
    health:
      check_cmd: "agg --help"
      expect_exit: 0

  gifsicle:
    required: true
    purpose: "Optimize GIF file size"
    methods: ["asciinema", "vhs"]
    install:
      brew: "gifsicle"
      apt: "gifsicle"
      yum: "gifsicle"
    version:
      min: "1.90"
      check_cmd: "gifsicle --version | grep -oE '[0-9.]+' | head -1"
    health:
      check_cmd: "gifsicle --help"
      expect_exit: 0

  vhs:
    required: false
    purpose: "Generate scripted demos (alternative to asciinema)"
    methods: ["vhs"]
    install:
      brew: "charmbracelet/tap/vhs"
    version:
      min: "0.7.0"
      check_cmd: "vhs --version | grep -oE '[0-9.]+' | head -1"
    health:
      check_cmd: "vhs --help"
      expect_exit: 0

  fswatch:
    required: false
    purpose: "Watch mode for iterative development"
    methods: ["asciinema", "vhs"]
    install:
      brew: "fswatch"
      apt: "fswatch"
    version:
      min: "1.14.0"
      check_cmd: "fswatch --version | grep -oE '[0-9.]+' | head -1"
    health:
      check_cmd: "fswatch --help"
      expect_exit: 0
---
```

#### 1.2 Schema Fields Reference

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `required` | boolean | Fail if missing (vs warn) | `true` |
| `purpose` | string | User-facing explanation | "Record terminal sessions" |
| `methods` | array | Which recording methods need this | `["asciinema", "vhs"]` |
| `install` | object | Installation strategies | `{brew: "asciinema"}` |
| `version.min` | string | Minimum version required | `"2.0.0"` |
| `version.check_cmd` | string | Command to extract version | `"tool --version \| grep..."` |
| `health.check_cmd` | string | Command to validate tool works | `"tool --help"` |
| `health.expect_exit` | int | Expected exit code | `0` |

---

### 2. Tool Detection Strategy

#### 2.1 Detection Algorithm (Pseudocode)

```bash
function detect_tool(tool_name, method) {
  # 1. Check session cache first
  cached_status = get_cached_status(tool_name)
  if cached_status.exists and cached_status.age < 60s:
    return cached_status

  # 2. Check if command exists in PATH
  if ! command -v $tool_name &> /dev/null:
    result = { installed: false, version: null, health: "n/a" }
    store_cache(tool_name, result)
    return result

  # 3. Extract version (optional, may fail)
  version = extract_version(tool_name, dependencies[tool_name].version.check_cmd)
  version_ok = compare_version(version, dependencies[tool_name].version.min)

  # 4. Run health check (can tool actually run?)
  health_cmd = dependencies[tool_name].health.check_cmd
  health_ok = run_health_check(health_cmd, expected_exit=0)

  # 5. Store result in cache
  result = {
    installed: true,
    version: version,
    version_ok: version_ok,
    health: health_ok ? "ok" : "broken",
    path: $(which $tool_name)
  }

  store_cache(tool_name, result)
  return result
}
```

#### 2.2 Caching Strategy

**Session-level cache** (not persistent across sessions):

```bash
# Cache location: /tmp/craft-deps-$SESSION_ID/
# File structure:
/tmp/craft-deps-abc123/
  asciinema.json    # { "installed": true, "version": "2.3.0", "health": "ok", "timestamp": 1705510800 }
  agg.json
  gifsicle.json
  vhs.json
  fswatch.json

# Cache hit conditions:
# - File exists
# - Age < 60 seconds (configurable)
# - Same session ID

# Cache invalidation:
# - Session ends (temp dir cleanup)
# - Manual: --check --no-cache
# - After installation: delete specific tool cache
```

**Why session-level?**
- Performance: Avoid redundant `command -v` calls within same session
- Freshness: Tools installed mid-session are detected
- Simplicity: No persistent state to manage

---

### 3. Installation Orchestration

#### 3.1 Multi-Strategy Installer Design

```bash
function install_tool(tool_name, method) {
  tool_spec = dependencies[tool_name]

  # 1. Get installation methods in priority order
  strategies = get_install_strategies(tool_spec)
  # strategies = ["brew", "cargo_git", "binary"]

  # 2. Filter strategies available on this platform
  available = filter_available_strategies(strategies)
  # On macOS with cargo: ["brew", "cargo_git", "binary"]
  # On macOS without cargo: ["brew", "binary"]

  # 3. Prompt user for consent
  consent = prompt_user_consent(tool_name, tool_spec.purpose, available)
  if ! consent:
    echo "Skipped $tool_name installation"
    return 1

  # 4. Try each strategy with fallback
  for strategy in available:
    echo "Attempting: $strategy installation for $tool_name..."
    result = try_install(tool_name, strategy, tool_spec)

    if result.success:
      # 5. Verify installation
      verify = detect_tool(tool_name, method)
      if verify.installed and verify.health == "ok":
        echo "✅ $tool_name installed successfully via $strategy"
        return 0
      else:
        echo "⚠️  $tool_name installed but health check failed"
        continue  # Try next strategy
    else:
      echo "❌ $strategy failed: ${result.error}"
      continue  # Try next strategy

  # 6. All strategies failed
  echo "❌ Failed to install $tool_name via all methods"
  return 1
}
```

#### 3.2 User Consent Flow

```bash
function prompt_user_consent(tool_name, purpose, strategies) {
  cat <<EOF
┌─────────────────────────────────────────────────────────────┐
│ 🔧 INSTALLATION REQUIRED                                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Tool: $tool_name                                             │
│ Purpose: $purpose                                            │
│                                                              │
│ Installation will try (in order):                            │
EOF

  for i, strategy in enumerate(strategies):
    time_estimate = get_time_estimate(strategy)
    echo "│   ${i+1}. $strategy ($time_estimate)                               │"
  done

  cat <<EOF
│                                                              │
│ Install $tool_name now?                                      │
│   [Y] Yes, install                                           │
│   [N] No, skip this tool                                     │
│   [S] Skip all missing tools                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
EOF

  read -p "Your choice [Y/n/s]: " choice
  case $choice in
    Y|y|"") return 0 ;;  # Yes, install
    S|s) SKIP_ALL=true; return 1 ;;  # Skip all
    *) return 1 ;;  # No, skip
  esac
}
```

---

### 4. Integration Points in demo.md Workflow

#### 4.1 Workflow Trigger Points

| Flag/Mode | When to Check Dependencies | Action |
|-----------|---------------------------|--------|
| `--check` | Immediately on invocation | Detect all tools, display status table, exit |
| `--fix` | After `--check` shows missing | Install missing tools, re-check, display status |
| `--method asciinema` | Before recording guide | Detect asciinema/agg/gifsicle, warn if missing |
| `--method vhs` | Before tape generation | Detect vhs/gifsicle, warn if missing |
| `--generate` | Before conversion step | Detect method-specific tools, fail if missing |
| `--batch` | Before batch processing | Detect agg/gifsicle, fail if missing |
| `--watch` | Before watch loop | Detect fswatch, fallback to manual reload if missing |

#### 4.2 Status Display Format

```
┌─────────────────────────────────────────────────────────────┐
│ 🔍 DEPENDENCY STATUS: asciinema method                      │
├─────────────────────────────────────────────────────────────┤
│ Tool       │ Status    │ Version │ Health │ Install         │
├────────────┼───────────┼─────────┼────────┼─────────────────┤
│ asciinema  │ ✅ OK     │ 2.3.0   │ ✅ OK  │ -               │
│ agg        │ ❌ MISSING│ -       │ -      │ brew install... │
│ gifsicle   │ ✅ OK     │ 1.93    │ ✅ OK  │ -               │
│ fswatch    │ ⚠️  OPTIONAL│ -     │ -      │ brew install... │
└─────────────────────────────────────────────────────────────┘

Summary: 1 missing required tool
Run: /craft:docs:demo --fix
```

---

### 5. Key Design Decisions & Trade-offs

#### 5.1 YAML Frontmatter vs Separate Config

**Decision:** Embed dependencies in command frontmatter

**Rationale:**
- ✅ Single source of truth (command + deps in one file)
- ✅ Follows existing Craft plugin patterns
- ✅ Version controlled with command
- ❌ Larger frontmatter (mitigated by clear structure)

---

#### 5.2 Session-Level vs Persistent Caching

**Decision:** Session-level caching in `/tmp/`

**Rationale:**
- ✅ Simple implementation (no DB needed)
- ✅ Auto-cleanup on session end
- ✅ Sufficient performance (checks take <100ms)
- ❌ Re-checks across sessions (acceptable overhead)

---

#### 5.3 Informed Consent vs Auto-Install

**Decision:** Require explicit user consent before installations

**Rationale:**
- ✅ Respects user control
- ✅ Shows what will be installed and how
- ✅ Allows skipping individual tools
- ❌ Requires interaction (acceptable for one-time setup)

---

#### 5.4 Multi-Strategy Fallback vs Single Method

**Decision:** Try multiple installation methods with fallback

**Rationale:**
- ✅ Works on systems without Homebrew
- ✅ Handles cargo-only installs (agg)
- ✅ Provides binary fallback for air-gapped systems
- ❌ More complex installer logic (mitigated by clear prioritization)

---

## Codebase Research Findings

### Existing Dependency Patterns

**Current State:**
- No centralized dependency management system exists yet
- Individual commands have dependencies but no standardized declaration method
- Example: `commands/docs/demo.md` requires asciinema, agg, gifsicle, and VHS but dependencies aren't formally declared
- Basic tool detection exists: `utils/detect_teaching_mode.py` provides a reusable pattern for checking file/config existence

**Existing Patterns to Leverage:**
- `detect_teaching_mode.py` shows priority-based detection pattern (config → metadata → structure)
- Graceful fallback handling (PyYAML available? → fallback to text search)
- Return tuple pattern: `(bool, Optional[str])` for result + method

### Command Frontmatter Conventions

**Standard YAML Frontmatter Structure** (from `commands/check.md`, `commands/do.md`, `commands/code/lint.md`):

```yaml
---
description: One-line command summary
arguments:
  - name: flag_name
    description: What it does
    required: false|true
    default: value
    alias: -x
category: category_name  [optional]
---
```

### Reusable Script Patterns

**From `validate-counts.sh`:**
```bash
# Standard header
#!/bin/bash
set -e

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# Path resolution
PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Error handling
if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}Error message${NC}"
    exit 1
fi

# Success message
echo -e "${GREEN}✓ Success message${NC}"
```

### Testing Patterns

**Test Structure** (from `tests/test_craft_plugin.py`):

```python
#!/usr/bin/env python3
"""Docstring with module purpose"""

import unittest
from pathlib import Path
from dataclasses import dataclass

@dataclass
class TestResult:
    name: str
    passed: bool
    duration_ms: float
    details: str
    category: str = "general"

class TestClassName(unittest.TestCase):
    def setUp(self):
        """Create fixtures"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)

    def test_specific_behavior(self):
        """Test one thing"""
        result = function_under_test()
        self.assertEqual(result, expected)
```

### Dry-Run Output Pattern

**Utility: `utils/dry_run_output.py`** provides standardized formatting:

```python
from enum import Enum
from dataclasses import dataclass
from typing import List

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Operation:
    type: OperationType
    description: str
    details: List[str]
    target: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.MEDIUM
```

---

## Implementation Roadmap

### Phase 1: Core Dependency Checking (v1.23.0)

**Duration:** 6 hours

**Files to Create/Modify:**

| File | Action | Purpose |
|------|--------|---------|
| `commands/docs/demo.md` | Modify | Add dependencies YAML frontmatter |
| `scripts/dependency-manager.sh` | Create | Core dependency management logic |
| `scripts/tool-detector.sh` | Create | Tool detection utilities |
| `scripts/session-cache.sh` | Create | Session-level caching |
| `tests/test_dependency_checking.py` | Create | Test suite for Phase 1 |

**Deliverables:**
- ✅ Add dependencies section to frontmatter
- ✅ Implement tool detection and validation
- ✅ Add session-level caching
- ✅ Create `--check` flag with status table
- ✅ Implement graceful degradation

---

### Phase 2: Auto-Installation (v1.24.0)

**Duration:** 8 hours

**Files to Create/Modify:**

| File | Action | Purpose |
|------|--------|---------|
| `scripts/dependency-installer.sh` | Create | Installation orchestration |
| `scripts/installers/brew-installer.sh` | Create | Homebrew installation |
| `scripts/installers/cargo-installer.sh` | Create | Cargo installation |
| `scripts/installers/binary-installer.sh` | Create | Binary download |
| `scripts/consent-prompt.sh` | Create | User consent UI |
| `tests/test_dependency_installation.py` | Create | Installation tests |

**Deliverables:**
- ✅ Implement multi-strategy installer (brew, cargo, binary)
- ✅ Add informed consent prompts
- ✅ Create `--fix` flag
- ✅ Implement retry with fallbacks
- ✅ Add installation logging

---

### Phase 3: Batch Conversion (v1.25.0)

**Duration:** 4 hours

**Files to Create/Modify:**

| File | Action | Purpose |
|------|--------|---------|
| `scripts/batch-convert.sh` | Create | Batch conversion logic |
| `scripts/convert-cast.sh` | Create | Single .cast → .gif conversion |
| `commands/docs/demo.md` | Modify | Add --convert and --batch flags |

**Deliverables:**
- ✅ Implement `--convert` flag for single files
- ✅ Implement `--batch` flag for bulk processing
- ✅ Add progress indicators
- ✅ Add size reporting
- ✅ Add `--force` flag

---

### Phase 4: Advanced Features (v1.26.0)

**Duration:** 6 hours

**Files to Create/Modify:**

| File | Action | Purpose |
|------|--------|---------|
| `scripts/health-check.sh` | Create | Health validation |
| `scripts/version-check.sh` | Create | Version validation |
| `scripts/repair-tools.sh` | Create | Repair broken installs |
| `commands/docs/demo.md` | Modify | Add JSON output |
| `.github/workflows/validate-dependencies.yml` | Create | CI integration |
| `docs/reference/dependency-management.md` | Create | Complete guide |

**Deliverables:**
- ✅ Implement health check validation
- ✅ Add version checking with warnings
- ✅ Implement repair functionality
- ✅ Add JSON output (`--check --json`)
- ✅ Create CI/CD integration
- ✅ Write comprehensive guide

---

## Reference Files

### Core Reference Files

| File | Purpose | Key Pattern |
|------|---------|-------------|
| `utils/detect_teaching_mode.py` | Detection pattern | Priority-based detection with fallback |
| `utils/dry_run_output.py` | Output formatting | Structured output with risk levels |
| `commands/code/lint.md` | Frontmatter example | Comprehensive argument docs |
| `commands/check.md` | Dry-run example | Complete preview before execution |
| `tests/test_linkcheck_ignore_parser.py` | Test pattern | setUp/tearDown, assertions |
| `tests/test_project_detector.py` | Detection tests | Testing multiple detection methods |
| `scripts/validate-counts.sh` | Bash validation | Error handling, colored output |
| `IMPLEMENTATION-PLAN.md` | Complete roadmap | 4-phase detailed plan |

---

## Open Questions & Future Considerations

1. **Version constraint syntax**: Currently `min: "2.0.0"`, should we support ranges like `>=2.0.0,<3.0.0`?
   - **Recommendation:** Start with min-only, add ranges in v1.1 if needed

2. **CI/CD auto-install**: Should we add `--auto-yes` for non-interactive environments?
   - **Recommendation:** Add in Phase 4 with env var `CRAFT_AUTO_INSTALL=1`

3. **Cross-platform testing**: Need Linux CI testing?
   - **Recommendation:** Yes, add GitHub Actions matrix for macOS + Ubuntu

4. **Tool update notifications**: Warn when installed version is outdated?
   - **Recommendation:** Phase 4 feature, show in --check output

5. **Dependency graph visualization**: Show tool dependencies (agg requires asciinema recordings)?
   - **Recommendation:** Future enhancement, not v1.0

---

## Conclusion

This specification provides a **robust, user-friendly dependency management system** that:
- ✅ Minimizes installation friction with multi-strategy installers
- ✅ Respects user control via informed consent
- ✅ Optimizes performance with session-level caching
- ✅ Degrades gracefully when tools are unavailable
- ✅ Integrates cleanly into existing command workflows

**Estimated implementation effort:** 24 hours (matches plan)

**Next step:** Begin Phase 1 implementation (dependency-manager.sh, tool-detector.sh)
