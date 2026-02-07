# CLI Tests for Craft Plugin

Bash-based test suites for validating the craft plugin structure and functionality.

## Test Suites

### Automated Tests (`automated-tests.sh`)

Non-interactive tests that validate plugin structure:

```bash
bash tests/cli/automated-tests.sh
```

**What it tests:**

- Plugin structure (plugin.json, directories)
- Command files exist and are valid
- Skill files exist and are valid
- Agent definitions
- Markdown syntax (code fence balance, frontmatter)

**Options:**

- `VERBOSE=1` - Show individual file checks

### Interactive Tests (`interactive-tests.sh`)

Manual testing with expected vs actual comparison:

```bash
bash tests/cli/interactive-tests.sh
```

**What it tests:**

- Plugin JSON content
- Directory structure
- Command/skill/agent counts
- Command content validation
- Markdown validation

**Keys:**

- `y` = pass
- `n` = fail
- `q` = quit

## Branch Protection Tests

### E2E Dogfooding Tests (`../test_branch_guard_e2e.sh`)

Automated end-to-end tests for the branch-guard hook that exercise full multi-step workflows:

```bash
bash tests/test_branch_guard_e2e.sh
```

**What it tests (8 groups, 31 tests):**

- Full workflow: dev -> feature worktree -> back to dev
- Bypass lifecycle: create marker -> allowed -> remove -> blocked
- Config cascade: auto-detect, custom config, malformed fallthrough
- Error messages: header, file path, branch name, options
- Cross-tool consistency: Edit vs Write on main and dev
- Dry-run -> enforcement transitions
- Performance: 50 invocations < 5s, no temp file leaks
- Real-world scenarios: CLAUDE.md, tests/, .STATUS, force push

### Interactive Branch Guard Tests (`../test_branch_guard_interactive.sh`)

Human-guided QA tests for user-facing behavior:

```bash
bash tests/test_branch_guard_interactive.sh
```

**What it tests (10 scenarios):**

- Hook registration in settings.json
- Error message readability and formatting
- Bypass marker format validation
- Command integration (status, check, worktree)
- Dry-run logging visibility
- Perceived performance responsiveness
- Config file format

**Keys:** `y` = pass, `n` = fail, `s` = skip, `q` = quit

### Related Unit Tests

- `tests/test_branch_guard.sh` — 49 unit tests (automated)
- `tests/test_integration_branch_guard.py` — 6 integration tests (automated)

## Logs

Test logs are saved to `tests/cli/logs/`:

- `interactive-test-YYYYMMDD-HHMMSS.log`
- `branch-guard-interactive-YYYYMMDD-HHMMSS.log`

## Running from Project Root

```bash
# From craft plugin directory
cd ~/projects/dev-tools/claude-plugins/craft
bash tests/cli/automated-tests.sh

# Verbose mode
VERBOSE=1 bash tests/cli/automated-tests.sh
```
