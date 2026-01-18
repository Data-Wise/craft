# Dependency Manager Scripts

**Phase 1 Implementation - Core Dependency Checking**

This directory contains the dependency management system for Craft's demo generation commands.

## Components

### 1. tool-detector.sh (297 lines)
**Purpose:** Low-level tool detection utilities

**Functions:**
- `detect_tool(tool_name, tool_spec_json)` - Main detection routine
- `extract_version(tool_name, check_cmd)` - Extract version string
- `compare_version(current, minimum)` - Compare semantic versions
- `run_health_check(check_cmd, expected_exit)` - Validate tool health

**Returns:** JSON with detection results:
```json
{
  "installed": true,
  "version": "2.3.0",
  "version_ok": true,
  "health": "ok",
  "path": "/usr/local/bin/asciinema"
}
```

### 2. session-cache.sh (211 lines)
**Purpose:** Session-scoped caching for tool detection results

**Configuration:**
- Cache location: `/tmp/craft-deps-{SESSION_ID}/`
- Cache TTL: 60 seconds
- Atomic writes with temp files

**Functions:**
- `init_cache()` - Initialize cache directory
- `get_cached_status(tool_name)` - Retrieve cached status
- `store_cache(tool_name, status_json)` - Store detection results
- `clear_cache(tool_name)` - Invalidate single tool
- `cleanup_cache()` - Remove entire cache directory

### 3. dependency-manager.sh (476 lines)
**Purpose:** Orchestrator that integrates detection and caching

**Functions:**

#### parse_frontmatter()
Extract dependencies from `commands/docs/demo.md` frontmatter.

**Output:** JSON with tool specifications

**Example:**
```bash
bash scripts/dependency-manager.sh parse_frontmatter
```

```json
{
  "asciinema": {
    "required": true,
    "purpose": "Record real terminal sessions",
    "methods": ["asciinema"],
    "install": {
      "brew": "asciinema",
      "apt": "asciinema"
    },
    "version": {
      "min": "2.0.0",
      "check_cmd": "asciinema --version | grep -oE '[0-9.]+' | head -1"
    },
    "health": {
      "check_cmd": "asciinema --help",
      "expect_exit": 0
    }
  }
}
```

#### check_dependencies(method)
Check dependencies for specific method (asciinema, vhs, or all).

**Logic:**
1. Parse frontmatter to get tool specs
2. Filter tools by method
3. Check cache first (60s TTL)
4. If cache miss, run detection
5. Store result in cache
6. Return aggregated status

**Output:** JSON array with status for each tool

**Exit codes:**
- `0` - All required tools OK
- `1` - Missing or broken required tools

**Example:**
```bash
bash scripts/dependency-manager.sh check_dependencies asciinema
```

```json
[
  {
    "name": "asciinema",
    "installed": true,
    "version": "2.3.0",
    "version_ok": true,
    "health": "ok",
    "required": true,
    "install_cmd": "brew install asciinema"
  },
  {
    "name": "agg",
    "installed": false,
    "version": "null",
    "version_ok": false,
    "health": "n/a",
    "required": true,
    "install_cmd": "cargo install agg"
  }
]
```

#### check_all_dependencies()
Check all dependencies regardless of method.

**Example:**
```bash
bash scripts/dependency-manager.sh check_all_dependencies
```

#### display_status_table(method)
Check dependencies and display formatted ASCII table.

**Output:** Formatted table with:
- Tool name
- Status (✅ OK, ❌ MISSING, ⚠️ OPTIONAL)
- Version
- Health status
- Install command

**Example:**
```bash
bash scripts/dependency-manager.sh display_status_table asciinema
```

```
┌─────────────────────────────────────────────────────────────┐
│ 🔍 DEPENDENCY STATUS: asciinema method                      │
├─────────────────────────────────────────────────────────────┤
│ Tool         │ Status     │ Version  │ Health  │ Install         │
├──────────────┼────────────┼──────────┼─────────┼─────────────────┤
│ agg          │ ❌ MISSING  │ -        │ -       │ cargo install a... │
│ asciinema    │ ✅ OK       │ 2.3.0    │ ✅ OK    │ -               │
│ gifsicle     │ ✅ OK       │ 1.96     │ ✅ OK    │ -               │
│ fswatch      │ ⚠️  OPTIONAL   │ -        │ -       │ brew install fs... │
└──────────────┴────────────┴──────────┴─────────┴─────────────────┘

Summary: 1 missing, 0 broken
Run: /craft:docs:demo --fix
```

#### get_install_command(tool_name, install_spec)
Get platform-specific install command.

**Platform detection:**
- macOS → brew
- Debian/Ubuntu → apt
- RHEL/CentOS → yum
- Fallback → cargo/binary download

## Usage Examples

### Check specific method
```bash
# Check asciinema method dependencies
bash scripts/dependency-manager.sh display_status_table asciinema

# Check VHS method dependencies
bash scripts/dependency-manager.sh display_status_table vhs
```

### Check all dependencies
```bash
bash scripts/dependency-manager.sh display_status_table all
```

### Programmatic checking
```bash
# Check dependencies and capture JSON
status=$(bash scripts/dependency-manager.sh check_dependencies asciinema)

# Extract specific fields
echo "$status" | jq '.[] | select(.installed == false) | .name'

# Count missing tools
echo "$status" | jq '[.[] | select(.installed == false and .required == true)] | length'
```

### Integration in commands
```bash
# In /craft:docs:demo command
source scripts/dependency-manager.sh

# Check before running
if ! check_dependencies "asciinema" > /dev/null; then
    echo "Missing dependencies. Run with --check to see details."
    exit 1
fi
```

## Dependency Declarations

Dependencies are declared in `commands/docs/demo.md` frontmatter:

```yaml
dependencies:
  asciinema:
    required: true
    purpose: "Record real terminal sessions"
    methods: ["asciinema"]
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
```

**Fields:**
- `required` - Boolean, whether tool is required or optional
- `purpose` - Human-readable description
- `methods` - Array of methods that use this tool (asciinema, vhs)
- `install` - Platform-specific install commands
- `version.min` - Minimum required version
- `version.check_cmd` - Command to extract version
- `health.check_cmd` - Command to validate tool works
- `health.expect_exit` - Expected exit code (usually 0)

## Performance

**Caching Strategy:**
- First check: ~500ms (5 tools × 100ms each)
- Subsequent checks: ~50ms (cache hits)
- Cache invalidation: 60 seconds
- Cache location: `/tmp/craft-deps-{SESSION_ID}/`

**Benefits:**
- Avoid repeated version checks
- Session-scoped (no cross-session pollution)
- Automatic cleanup on session end

## Testing

Manual test suite available:
```bash
# Run comprehensive tests
bash scripts/dependency-manager.sh

# Test individual components
bash scripts/tool-detector.sh
bash scripts/session-cache.sh
```

## Error Handling

**Graceful degradation:**
- Missing tool → Returns `installed: false`
- Unparseable version → Returns `version: "unparseable"`
- Failed health check → Returns `health: "broken"`
- Invalid frontmatter → Error message to stderr, exit 1

## Future Enhancements (Phase 2)

Planned for Phase 2 (Auto-Installation):
- `install_missing_tools(dry_run=false)` - Install missing dependencies
- `suggest_install_method()` - Recommend best install method
- Dry-run mode for preview
- Confirmation prompts before install
- Integration with `/craft:docs:demo --fix`

## Architecture

```
demo.md frontmatter
       ↓
parse_frontmatter() ──→ deps_json
       ↓
check_dependencies(method) ──→ filter by method
       ↓                           ↓
   for each tool              check cache
       ↓                           ↓
   cache miss?               detect_tool()
       ↓                           ↓
   store_cache()            version + health
       ↓
   results_json
       ↓
display_status_table()
```

## Files

- `scripts/tool-detector.sh` - Low-level detection (297 lines)
- `scripts/session-cache.sh` - Caching layer (211 lines)
- `scripts/dependency-manager.sh` - Orchestrator (476 lines)
- `scripts/README-dependency-manager.md` - This file

**Total:** ~984 lines of production code

## License

Part of Craft plugin, same license as project.
