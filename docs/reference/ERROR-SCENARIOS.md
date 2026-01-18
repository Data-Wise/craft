# Craft Command Error Scenarios & Recovery Guide

Complete error handling and recovery guide for Craft commands.

**Version**: v1.24.0 | **Last Updated**: 2026-01-17 | **Coverage**: 97 commands

---

## Quick Error Reference

### Error Code Categories

| Category | Range | Severity | Examples |
|----------|-------|----------|----------|
| **Validation** | 1000-1099 | Warning | Invalid arguments, missing params |
| **File System** | 1100-1199 | Error | File not found, permission denied |
| **Process** | 1200-1299 | Error | Command failed, timeout |
| **Git** | 1300-1399 | Error | Merge conflict, branch not found |
| **Build** | 1400-1499 | Error | Build failed, test failure |
| **Network** | 1500-1599 | Error | Connection timeout, DNS failure |
| **Configuration** | 1600-1699 | Error | Invalid config, missing tool |
| **Permission** | 1700-1799 | Error | Access denied, unauthorized |

---

## Root Commands Error Scenarios

### /craft:do

#### Error: Empty Task Description
**Code**: `1000` | **Severity**: Warning | **Frequency**: Common

```
Error: Task description cannot be empty
Usage: /craft:do "task description"
```

**Recovery**:
```bash
# Provide a non-empty task description
/craft:do "add user authentication system"
```

**Prevention**: Always include a meaningful task description

---

#### Error: Invalid Execution Mode
**Code**: `1001` | **Severity**: Warning | **Frequency**: Common

```
Error: Invalid mode: "fast"
Valid modes: default, debug, optimize, release
```

**Recovery**:
```bash
# Use valid mode
/craft:do "refactor code" optimize

# Or omit mode for default
/craft:do "refactor code"
```

---

#### Error: Invalid Complexity Override
**Code**: `1002` | **Severity**: Warning | **Frequency**: Rare

```
Error: Invalid complexity: "tiny"
Valid values: simple, moderate, complex
```

**Recovery**:
```bash
# Use valid complexity
/craft:do "small task" simple
```

---

#### Error: Complexity Scoring Timeout
**Code**: `1200` | **Severity**: Error | **Frequency**: Rare

```
Error: Complexity scoring timed out after 5s
Task may be too complex to analyze
```

**Recovery**:
```bash
# Option 1: Override complexity manually
/craft:do "complex task" complex

# Option 2: Break into smaller tasks
/craft:do "step 1: design"
/craft:do "step 2: implement"

# Option 3: Wait and retry
sleep 10
/craft:do "complex task"
```

---

### /craft:check

#### Error: No Checks Configured
**Code**: `1601` | **Severity**: Warning | **Frequency**: Rare

```
Error: No check configurations found
Ensure .craft/config.yml exists
```

**Recovery**:
```bash
# Initialize Craft config
/craft:git:init

# Or manually create config
mkdir -p .craft
echo "version: 1" > .craft/config.yml
```

---

#### Error: Check Validation Failed
**Code**: `1400` | **Severity**: Error | **Frequency**: Common

```
Error: Check validation failed

FAILING CHECKS:
  code: 2 linting errors
  tests: 1 test failure
  git: Uncommitted changes

Run /craft:check --fix to auto-fix issues
```

**Recovery**:
```bash
# Option 1: Auto-fix all issues
/craft:check --fix

# Option 2: Fix specific scope
/craft:check code --fix
/craft:check tests

# Option 3: Preview before fixing
/craft:check --dry-run --fix
```

---

#### Error: Insufficient Permissions
**Code**: `1700` | **Severity**: Error | **Frequency**: Rare

```
Error: Permission denied writing to .git/hooks
```

**Recovery**:
```bash
# Option 1: Run with sudo (not recommended)
sudo /craft:check

# Option 2: Fix permissions
chmod u+w .git/hooks

# Option 3: Skip problematic check
/craft:check code tests
```

---

### /craft:hub

#### Error: Hub Index Corrupt
**Code**: `1100` | **Severity**: Error | **Frequency**: Rare

```
Error: Hub index is corrupt or missing
Rebuilding index...
```

**Recovery** (automatic):
- Hub automatically rebuilds the index
- If still fails:

```bash
# Force rebuild
rm -rf .craft/cache
/craft:hub
```

---

#### Error: Invalid Search Query
**Code**: `1001` | **Severity**: Warning | **Frequency**: Rare

```
Error: Search query contains invalid characters
Use alphanumeric, hyphens, and underscores
```

**Recovery**:
```bash
# Quote the query or remove special chars
/craft:hub "user authentication"
```

---

### /craft:orchestrate

#### Error: Orchestrator Not Available
**Code**: `1701` | **Severity**: Error | **Frequency**: Rare

```
Error: Orchestrator agent not available
No agents running or all busy
```

**Recovery**:
```bash
# Option 1: Wait for agents to free
sleep 30
/craft:orchestrate "task" optimize

# Option 2: Reduce agent count
/craft:orchestrate "task" default

# Option 3: Check agent status
/craft:orchestrate status
```

---

#### Error: Task Decomposition Failed
**Code**: `1002` | **Severity**: Error | **Frequency**: Rare

```
Error: Failed to decompose task into subtasks
Task description may be too vague
```

**Recovery**:
```bash
# Option 1: Provide more specific task
/craft:orchestrate "Add OAuth 2.0 authentication with PKCE"

# Option 2: Break into smaller tasks
/craft:orchestrate "Design OAuth flow"
/craft:orchestrate "Implement OAuth provider"
/craft:orchestrate "Add tests"

# Option 3: Use manual planning
/craft:plan:feature "authentication system"
```

---

#### Error: Agent Task Failure
**Code**: `1200` | **Severity**: Error | **Frequency**: Common

```
Error: Agent (code-1) failed on subtask

Subtask: Implement authentication module
Error: Dependency "bcrypt" not installed

Suggested recovery:
1. Install missing dependencies
2. Re-run orchestrator

Run: /craft:code:deps-check --fix
```

**Recovery**:
```bash
# Option 1: Install missing dependencies
/craft:code:deps-check --fix

# Option 2: Resume orchestration
/craft:orchestrate resume task-123

# Option 3: Manually fix and retry
npm install bcrypt
/craft:orchestrate "task" optimize
```

---

## Code Commands Error Scenarios

### /craft:code:lint

#### Error: No Linter Configured
**Code**: `1601` | **Severity**: Error | **Frequency**: Common

```
Error: No linter configured for this project
Supported: eslint, pylint, clippy, stylelint

Create .eslintrc or equivalent
```

**Recovery**:
```bash
# Option 1: Initialize with default linter
npm init -y
npm install --save-dev eslint
npx eslint --init

# Option 2: Specify linter manually
/craft:code:lint --linter eslint

# Option 3: Use dry-run to see available linters
/craft:code:lint --dry-run
```

---

#### Error: Linter Parse Error
**Code**: `1100` | **Severity**: Error | **Frequency**: Rare

```
Error: Linter failed to parse file: src/main.ts
  SyntaxError: Unexpected token

File: src/main.ts (line 42, col 15)
```

**Recovery**:
```bash
# Fix the syntax error manually
# Then retry
/craft:code:lint src/main.ts

# Or skip problematic files
/craft:code:lint --exclude "src/main.ts"
```

---

#### Error: Fix Failed
**Code**: `1200` | **Severity**: Error | **Frequency**: Rare

```
Error: Auto-fix failed for 2 issues
Manual intervention required

Unfixable issues in: src/auth.ts (line 56)
```

**Recovery**:
```bash
# View the specific issues
/craft:code:lint src/auth.ts

# Fix manually
# Then verify
/craft:code:lint src/auth.ts
```

---

### /craft:code:refactor

#### Error: Invalid Refactoring Pattern
**Code**: `1001` | **Severity**: Warning | **Frequency**: Common

```
Error: Unknown refactoring pattern: "delete everything"
Supported patterns:
  - rename <old> to <new>
  - extract method <name>
  - inline variable <name>
```

**Recovery**:
```bash
# Use valid pattern
/craft:code:refactor "rename getCwd to getCurrentWorkingDirectory"
```

---

#### Error: Refactoring Would Break Code
**Code**: `1200` | **Severity**: Error | **Frequency**: Common

```
Error: Refactoring would break code
Test failures detected

Run: /craft:test:run to see failures
```

**Recovery**:
```bash
# Option 1: Fix tests first, then refactor
/craft:test:debug
# Fix the failing tests manually
/craft:code:refactor "your pattern"

# Option 2: Use dry-run to preview
/craft:code:refactor "your pattern" --dry-run

# Option 3: Abort and try different approach
git checkout -- .
```

---

### /craft:code:test-gen

#### Error: No Testable Functions Found
**Code**: `1100` | **Severity**: Warning | **Frequency**: Rare

```
Error: No exported functions found in src/index.ts
```

**Recovery**:
```bash
# Option 1: Specify different source file
/craft:code:test-gen --source src/auth.ts

# Option 2: Export functions and retry
# Edit src/index.ts to export functions
/craft:code:test-gen --source src/index.ts

# Option 3: Use manual template
cp tests/templates/unit-test.template tests/unit-auth.test.ts
```

---

### /craft:code:demo

#### Error: Demo Script Not Found
**Code**: `1100` | **Severity**: Error | **Frequency**: Common

```
Error: Demo script not found: scripts/demo-auth.sh
```

**Recovery**:
```bash
# Option 1: Create the script
mkdir -p scripts
cat > scripts/demo-auth.sh << 'EOF'
#!/bin/bash
npm start
EOF

# Option 2: Use existing script
/craft:code:demo scripts/existing-demo.sh

# Option 3: List available scripts
find scripts -name "*.sh" -type f
```

---

#### Error: Recording Failed
**Code**: `1200` | **Severity**: Error | **Frequency**: Common

```
Error: Recording failed - asciinema not installed

Install with:
  brew install asciinema (macOS)
  apt-get install asciinema (Linux)
  pip install asciinema (Python)
```

**Recovery**:
```bash
# Install missing tool
brew install asciinema

# Retry recording
/craft:code:demo scripts/demo.sh
```

---

### /craft:code:coverage

#### Error: Coverage Threshold Not Met
**Code**: `1400` | **Severity**: Error | **Frequency**: Common

```
Error: Code coverage below threshold

Current:  78%
Required: 80%

Uncovered:
  - src/utils/helpers.ts (14 lines)
  - src/auth/oauth.ts (8 lines)
```

**Recovery**:
```bash
# Option 1: Add missing tests
/craft:code:test-gen unit src/utils/helpers.ts

# Option 2: Lower threshold temporarily
/craft:code:coverage --threshold 75

# Option 3: Skip coverage check
/craft:check --scope code tests
```

---

## Git Commands Error Scenarios

### /craft:git:sync

#### Error: Merge Conflict
**Code**: `1300` | **Severity**: Error | **Frequency**: Common

```
Error: Merge conflict detected

Conflicted files:
  - src/auth.ts (2 conflicts)
  - package.json (1 conflict)

Resolve manually or use: git mergetool
```

**Recovery**:
```bash
# Option 1: Use visual merge tool
git mergetool

# Option 2: Abort and retry with rebase
git merge --abort
/craft:git:sync --rebase

# Option 3: Keep current version
git checkout --ours .
git add .
git commit -m "merge: keep our version"
```

---

#### Error: Diverged Branch
**Code**: `1300` | **Severity**: Error | **Frequency**: Common

```
Error: Branch has diverged from origin
Local: 5 commits ahead
Remote: 3 commits ahead

Sync would lose history
```

**Recovery**:
```bash
# Option 1: Rebase onto remote
/craft:git:sync --rebase

# Option 2: Merge remote branch
/craft:git:sync --no-rebase

# Option 3: Force local (DANGEROUS)
/craft:git:sync --force
# Only use if you're sure!
```

---

### /craft:git:worktree

#### Error: Worktree Already Exists
**Code**: `1300` | **Severity**: Error | **Frequency**: Common

```
Error: Worktree already exists for branch 'feature/auth'
Location: /path/to/.git-worktrees/feature-auth

Use /craft:git:worktree list to see all
```

**Recovery**:
```bash
# Option 1: Move to existing worktree
cd /path/to/.git-worktrees/feature-auth

# Option 2: Remove old worktree
/craft:git:worktree clean

# Option 3: Create with different name
/craft:git:worktree create feature/auth-v2
```

---

#### Error: Branch Not Found
**Code**: `1300` | **Severity**: Error | **Frequency**: Common

```
Error: Branch 'feature/nonexistent' not found
```

**Recovery**:
```bash
# Option 1: Create new branch
/craft:git:worktree create feature/auth

# Option 2: List existing branches
/craft:git:branch list

# Option 3: Checkout existing branch
/craft:git:branch checkout feature/auth
```

---

## Documentation Commands Error Scenarios

### /craft:docs:check-links

#### Error: Broken Link Found
**Code**: `1500` | **Severity**: Warning | **Frequency**: Common

```
Warning: Broken link detected

File: docs/guides/auth.md
Link: https://example.com/api (404)
Line: 42

Fix with: /craft:docs:check-links --fix
```

**Recovery**:
```bash
# Option 1: Auto-fix broken links
/craft:docs:check-links --fix

# Option 2: Review and fix manually
/craft:docs:check-links --detailed

# Option 3: Exclude problematic links
echo "https://deprecated.example.com" >> .linkcheck-ignore
/craft:docs:check-links
```

---

#### Error: External Links Timeout
**Code**: `1500` | **Severity**: Warning | **Frequency**: Common

```
Warning: External link check timed out

URL: https://slow-api.example.com
Timeout: 5000ms
```

**Recovery**:
```bash
# Option 1: Increase timeout
/craft:docs:check-links --timeout 10000

# Option 2: Skip external links
/craft:docs:check-links --no-external

# Option 3: Check manually
curl -I https://slow-api.example.com
```

---

### /craft:docs:api

#### Error: No Exports Found
**Code**: `1100` | **Severity**: Warning | **Frequency**: Rare

```
Warning: No exported functions/classes found
```

**Recovery**:
```bash
# Option 1: Add exports to source code
# Edit src/index.ts to export functions
export function myFunction() {}

# Option 2: Use manual API documentation
/craft:docs:tutorial "Write API documentation manually"
```

---

## Test Commands Error Scenarios

### /craft:test:run

#### Error: Tests Failed
**Code**: `1400` | **Severity**: Error | **Frequency**: Very Common

```
Error: Test suite failed

Failing tests:
  ✗ Auth tests (5 failures)
    - Should authenticate user (timeout)
    - Should validate token (assertion error)
  ✗ DB tests (1 failure)
    - Should connect to database (connection refused)

Run: /craft:test:debug to debug
```

**Recovery**:
```bash
# Option 1: Debug specific test
/craft:test:debug "Should authenticate user"

# Option 2: Run in debug mode for more info
/craft:test:run debug

# Option 3: Run with detailed output
/craft:test:run debug --verbose
```

---

#### Error: Test File Not Found
**Code**: `1100` | **Severity**: Error | **Frequency**: Common

```
Error: Test file not found: tests/auth.test.ts
```

**Recovery**:
```bash
# Option 1: Generate test file
/craft:code:test-gen unit src/auth.ts

# Option 2: Check correct path
/craft:test:run tests/

# Option 3: List test files
find tests -name "*.test.*" -o -name "*.spec.*"
```

---

#### Error: Test Dependency Missing
**Code**: `1601` | **Severity**: Error | **Frequency**: Common

```
Error: Test dependency missing: jest

Install with:
  npm install --save-dev jest
```

**Recovery**:
```bash
# Option 1: Auto-install
/craft:code:deps-check --fix

# Option 2: Manual install
npm install --save-dev jest

# Option 3: Skip tests temporarily
/craft:code:ci-local --skip-tests
```

---

### /craft:test:watch

#### Error: Watch Mode Crashed
**Code**: `1200` | **Severity**: Error | **Frequency**: Rare

```
Error: Watch mode crashed

Last error: ENOSPC: no space left on device
```

**Recovery**:
```bash
# Option 1: Free up disk space
df -h
# Delete unnecessary files

# Option 2: Increase file watch limit (Linux)
echo 65536 | sudo tee /proc/sys/fs/inotify/max_user_watches

# Option 3: Run tests without watch
/craft:test:run
```

---

## Build & Site Commands Error Scenarios

### /craft:site:build

#### Error: Build Failed
**Code**: `1400` | **Severity**: Error | **Frequency**: Common

```
Error: Site build failed

Error in: docs/guides/index.md
Line 42: Invalid markdown syntax

Fix the markdown and retry
```

**Recovery**:
```bash
# Option 1: Fix markdown syntax
# Edit docs/guides/index.md

# Option 2: Preview to see issues
/craft:site:preview

# Option 3: Use dry-run to get details
/craft:site:build --dry-run
```

---

#### Error: Theme Not Found
**Code**: `1100` | **Severity**: Error | **Frequency**: Rare

```
Error: Theme 'custom-theme' not found

Available themes:
  - material
  - readthedocs
  - mkdocs
```

**Recovery**:
```bash
# Option 1: Use available theme
/craft:site:init mkdocs

# Option 2: Install theme
pip install mkdocs-material

# Option 3: Use default theme
/craft:site:init
```

---

### /craft:site:deploy

#### Error: Authentication Failed
**Code**: `1700` | **Severity**: Error | **Frequency**: Common

```
Error: Authentication failed for deployment platform

Platform: Netlify
Error: Invalid or expired token

Set NETLIFY_TOKEN environment variable
```

**Recovery**:
```bash
# Option 1: Set authentication token
export NETLIFY_TOKEN="your-token-here"
/craft:site:deploy netlify

# Option 2: Use dry-run to test
/craft:site:deploy --dry-run

# Option 3: Create new token
# Go to platform's settings and generate new token
```

---

#### Error: Build Artifact Too Large
**Code**: `1400` | **Severity**: Error | **Frequency**: Rare

```
Error: Build artifact (250MB) exceeds limit (100MB)

Reduce size with:
  - /craft:site:build --minify
  - Remove large assets
  - Use CDN for images
```

**Recovery**:
```bash
# Option 1: Minify production build
/craft:site:build --production --minify

# Option 2: Exclude large assets
# Remove or externalize large files

# Option 3: Split into subdomains
# Create separate sites for different sections
```

---

## Network & External Service Errors

### Common Network Errors

#### Error: Connection Timeout
**Code**: `1500` | **Severity**: Error | **Frequency**: Common

```
Error: Connection timeout connecting to registry.npmjs.org

Check:
  1. Internet connection
  2. Network firewall
  3. DNS resolution
```

**Recovery**:
```bash
# Option 1: Check network
ping 8.8.8.8
nslookup registry.npmjs.org

# Option 2: Use different registry
npm config set registry https://registry.yarnpkg.com

# Option 3: Retry later
sleep 30
/craft:code:deps-check
```

---

#### Error: DNS Resolution Failed
**Code**: `1500` | **Severity**: Error | **Frequency**: Rare

```
Error: DNS resolution failed: api.github.com

Check your DNS settings or ISP connection
```

**Recovery**:
```bash
# Option 1: Use alternate DNS
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# Option 2: Check DNS
nslookup api.github.com

# Option 3: Use VPN if blocked
```

---

## Configuration & Setup Errors

### Common Configuration Errors

#### Error: Configuration File Invalid
**Code**: `1601` | **Severity**: Error | **Frequency**: Rare

```
Error: Configuration file .craft/config.yml is invalid

Line 12: Invalid YAML syntax
  Expected mapping, got scalar
```

**Recovery**:
```bash
# Option 1: Fix YAML syntax
# Edit .craft/config.yml
# Use YAML validator: https://www.yamllint.com/

# Option 2: Restore defaults
rm .craft/config.yml
/craft:git:init

# Option 3: Show correct syntax
/craft:smart-help
```

---

## Common Patterns for Error Recovery

### Pattern 1: Insufficient Permissions
```bash
# Check permissions
ls -la file.txt

# Fix permissions
chmod 644 file.txt

# Or use sudo (last resort)
sudo command
```

---

### Pattern 2: Missing Dependency
```bash
# Check what's missing
/craft:code:deps-check

# Auto-install
/craft:code:deps-check --fix

# Or manual install
npm install missing-package
```

---

### Pattern 3: Configuration Issue
```bash
# Check config
/craft:check

# Reset to defaults
rm -rf .craft
/craft:git:init

# Reconfigure
/craft:docs:claude-md --sync
```

---

### Pattern 4: Retry with Backoff
```bash
# Try again
/craft:command

# Wait and retry
sleep 10
/craft:command

# Use different mode
/craft:command optimize
```

---

## Debugging Tips

### Enable Debug Output
```bash
# Verbose output
/craft:command debug

# Or with environment variable
CRAFT_DEBUG=1 /craft:command
```

---

### Check Logs
```bash
# Show recent logs
tail -f ~/.craft/logs/craft.log

# Filter by command
grep "code:lint" ~/.craft/logs/craft.log
```

---

### Validate Configuration
```bash
# Check configuration
/craft:check --scope docs

# Validate syntax
/craft:docs:lint --strict
```

---

### Test Isolated
```bash
# Use dry-run
/craft:command --dry-run

# Use test mode
/craft:test:run debug
```

---

## When to Escalate

### Escalate if:

1. Error persists after following recovery steps
2. Error is not in this guide
3. Multiple unrelated commands failing
4. System appears corrupted

### How to Report:
```bash
# Gather diagnostics
/craft:check --verbose
/craft:code:coverage --report json

# Save environment info
env > environment.txt
uname -a >> environment.txt

# File issue with details
gh issue create --title "Error: ..." --body "$(cat environment.txt)"
```

---

**Last Updated**: January 17, 2026 | **Version**: v1.24.0
