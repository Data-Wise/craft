# Doc Coverage Enforcement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ensure every newly added craft command gets its doc surfaces (REFCARD row, mkdocs nav entry, CHANGELOG line, tutorial if it takes arguments) enforced automatically — at pre-commit, post-merge, and release time.

**Architecture:** A new standalone `scripts/doc-coverage-check.sh` provides the core detection logic. It is called by three existing enforcement points: `docs-staleness-check.sh` Phase 8 (detection/reporting), `pre-release-check.sh` (blocking gate), and `/craft:check` (pre-commit warning). The REFCARD is auto-generated from command frontmatter by a new `scripts/refcard-gen.sh` script. The release skill gains Step 13.4. Post-merge docs update is added as a mandatory workflow step.

**Tech Stack:** Bash (POSIX-compatible, BSD + GNU safe), Python 3 stdlib (frontmatter parsing), pytest + `tests/test_doc_coverage.sh` (bash integration), existing `_discovery.py` patterns.

## Global Constraints

- All bash must be BSD + GNU portable (no `sed -i ''` without compat wrapper — use the existing `sedi()` pattern from `scripts/post-release-sweep.sh`)
- No new Python dependencies — stdlib only
- `internal: true` frontmatter field must be added to `VALID_FIELDS` in `scripts/command-audit.sh` before any coverage checks run (or `command-audit.sh` will flag it as an unknown field)
- Deprecated commands (`deprecated: true`) and internal commands (`internal: true`) are EXEMPT from all coverage checks
- Tests live in `tests/` and must be discoverable by `pytest tests/` (Python wrapper) or called directly as bash scripts
- All new scripts must be executable (`chmod +x`)
- Pre-release gate BLOCKS (exit 1) on missing REFCARD row or nav entry; WARNS (exit 0) on missing tutorial

---

## File Map

| File | Action | Purpose |
|------|--------|---------|
| `scripts/doc-coverage-check.sh` | **CREATE** | Core coverage checker — used by all enforcement points |
| `scripts/refcard-gen.sh` | **CREATE** | Auto-generate REFCARD rows from command frontmatter |
| `tests/test_doc_coverage.sh` | **CREATE** | Bash integration tests for doc-coverage-check.sh |
| `tests/test_refcard_gen.sh` | **CREATE** | Bash integration tests for refcard-gen.sh |
| `scripts/command-audit.sh` | **MODIFY** line 24 | Add `internal` to `VALID_FIELDS` |
| `scripts/docs-staleness-check.sh` | **MODIFY** lines 337-385 | Extend Phase 8: add REFCARD + nav sub-checks |
| `scripts/pre-release-check.sh` | **MODIFY** (new section) | Add doc coverage gate (blocking) |
| `commands/check.md` | **MODIFY** frontmatter | Document new `--for commit` doc-surface warning behavior |
| `skills/release/SKILL.md` | **MODIFY** ~line 1091 | Insert Step 13.4 between Step 13 and Step 13.5 |
| `docs/workflows/release-workflow.md` | **MODIFY** | Add mandatory post-merge docs update step |
| `docs/REFCARD.md` | **MODIFY** | Add generation header comment; update generation instructions |

---

## Task 1: `internal: true` frontmatter support + command-audit.sh

**Context for implementer:** `scripts/command-audit.sh` maintains a `VALID_FIELDS` array (line 20–27). Any frontmatter key not in that list causes the audit to flag the file as having an unknown field. We need to add `internal` before any coverage check reads frontmatter, or the audit will error on the new field.

**Files:**

- Modify: `scripts/command-audit.sh:24`
- Test: `tests/test_doc_coverage.sh` (new file, first test block)

**Interfaces:**

- Produces: `internal: true` is a recognized frontmatter field in all scripts that parse command files

- [ ] **Step 1: Create test file with first test — audit accepts `internal: true`**

```bash
# tests/test_doc_coverage.sh
#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TMPDIR_TEST="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_TEST"' EXIT

pass() { echo "PASS: $1"; }
fail() { echo "FAIL: $1"; exit 1; }

# --- Test: command-audit.sh accepts internal: true ---
test_audit_accepts_internal_field() {
    local cmd_file="$TMPDIR_TEST/commands/test/internal-cmd.md"
    mkdir -p "$(dirname "$cmd_file")"
    cat > "$cmd_file" <<'EOF'
---
name: test-internal
description: An internal command
category: test
internal: true
---
# /craft:test:internal-cmd
EOF
    # Run audit scoped to the temp dir (override SCAN_DIRS)
    output=$(SCAN_DIRS_OVERRIDE="$TMPDIR_TEST/commands" bash "$ROOT/scripts/command-audit.sh" "$cmd_file" 2>&1 || true)
    if echo "$output" | grep -q "Unknown field: internal"; then
        fail "command-audit.sh flagged 'internal' as unknown field"
    fi
    pass "command-audit.sh accepts internal: true"
}

test_audit_accepts_internal_field
echo "All Task 1 tests passed."
```

- [ ] **Step 2: Run test — expect FAIL (internal not yet in VALID_FIELDS)**

```bash
bash tests/test_doc_coverage.sh
# Expected: FAIL: command-audit.sh flagged 'internal' as unknown field
```

- [ ] **Step 3: Add `internal` to VALID_FIELDS in command-audit.sh**

Open `scripts/command-audit.sh` line 20. Change:

```bash
VALID_FIELDS=(
    name category subcategory description file modes arguments flags
    tutorial tutorial_level tutorial_file related_commands tags
    project_types common_workflows time_budgets examples
    deprecated replaced-by
)
```

To:

```bash
VALID_FIELDS=(
    name category subcategory description file modes arguments flags
    tutorial tutorial_level tutorial_file related_commands tags
    project_types common_workflows time_budgets examples
    deprecated replaced-by internal
)
```

- [ ] **Step 4: Run test — expect PASS**

```bash
bash tests/test_doc_coverage.sh
# Expected: PASS: command-audit.sh accepts internal: true
# All Task 1 tests passed.
```

- [ ] **Step 5: Commit**

```bash
git add scripts/command-audit.sh tests/test_doc_coverage.sh
git commit -m "feat(doc-coverage): add internal: true frontmatter field to command-audit VALID_FIELDS"
```

---

## Task 2: `scripts/doc-coverage-check.sh` — core checker

**Context for implementer:** This is the heart of the feature. A standalone script that reads every non-deprecated, non-internal `commands/**/*.md` file and checks three surfaces: (1) REFCARD row in `docs/REFCARD.md`, (2) nav entry in `mkdocs.yml`, (3) tutorial presence if the command has `arguments:` in frontmatter. Outputs a machine-readable summary and exits 1 if any blocking surface is missing.

**Files:**

- Create: `scripts/doc-coverage-check.sh`
- Modify: `tests/test_doc_coverage.sh` (add Task 2 tests)

**Interfaces:**

- Consumes: `commands/**/*.md` frontmatter fields `deprecated`, `internal`, `arguments`, `name`
- Produces:
  - stdout: human-readable per-command report
  - exit 0: all blocking surfaces present (REFCARD + nav)
  - exit 1: one or more blocking surfaces missing
  - `--json` flag: JSON array of findings `[{cmd, surface, severity}]`
  - `--since <git-ref>`: scope to commands added/modified since `<git-ref>`

- [ ] **Step 1: Add tests for doc-coverage-check.sh to tests/test_doc_coverage.sh**

Append to `tests/test_doc_coverage.sh`:

```bash
# --- Test: detects missing REFCARD row ---
test_detects_missing_refcard() {
    local tmp="$TMPDIR_TEST/refcard_test"
    mkdir -p "$tmp/commands/ci"
    mkdir -p "$tmp/docs"

    # Command with no REFCARD entry
    cat > "$tmp/commands/ci/newcmd.md" <<'EOF'
---
name: newcmd
description: A new command
category: ci
---
# /craft:ci:newcmd
EOF
    # Empty REFCARD
    echo "# REFCARD" > "$tmp/docs/REFCARD.md"
    # Empty mkdocs nav (has the nav entry so only REFCARD fails)
    cat > "$tmp/mkdocs.yml" <<'EOF'
nav:
  - /craft:ci:newcmd: commands/ci/newcmd.md
EOF

    output=$(bash "$ROOT/scripts/doc-coverage-check.sh" --root "$tmp" 2>&1 || true)
    exit_code=$(bash "$ROOT/scripts/doc-coverage-check.sh" --root "$tmp" > /dev/null 2>&1; echo $?) || true

    if ! echo "$output" | grep -q "REFCARD"; then
        fail "did not detect missing REFCARD row"
    fi
    pass "detects missing REFCARD row"
}

# --- Test: detects missing nav entry ---
test_detects_missing_nav() {
    local tmp="$TMPDIR_TEST/nav_test"
    mkdir -p "$tmp/commands/ci"
    mkdir -p "$tmp/docs"

    cat > "$tmp/commands/ci/newcmd.md" <<'EOF'
---
name: newcmd
description: A new command
category: ci
---
EOF
    # REFCARD has entry, nav does not
    printf "| \`/craft:ci:newcmd\` | ci | A new command |\n" > "$tmp/docs/REFCARD.md"
    echo "nav:" > "$tmp/mkdocs.yml"

    output=$(bash "$ROOT/scripts/doc-coverage-check.sh" --root "$tmp" 2>&1 || true)
    if ! echo "$output" | grep -q "nav"; then
        fail "did not detect missing nav entry"
    fi
    pass "detects missing mkdocs nav entry"
}

# --- Test: skips deprecated commands ---
test_skips_deprecated() {
    local tmp="$TMPDIR_TEST/deprecated_test"
    mkdir -p "$tmp/commands/ci"
    mkdir -p "$tmp/docs"
    echo "nav:" > "$tmp/mkdocs.yml"
    echo "# REFCARD" > "$tmp/docs/REFCARD.md"

    cat > "$tmp/commands/ci/oldcmd.md" <<'EOF'
---
name: oldcmd
description: Old command
deprecated: true
replaced-by: newcmd
---
EOF
    exit_code=0
    bash "$ROOT/scripts/doc-coverage-check.sh" --root "$tmp" > /dev/null 2>&1 || exit_code=$?
    if [[ "$exit_code" -ne 0 ]]; then
        fail "deprecated command should not cause non-zero exit"
    fi
    pass "skips deprecated commands"
}

# --- Test: skips internal commands ---
test_skips_internal() {
    local tmp="$TMPDIR_TEST/internal_test"
    mkdir -p "$tmp/commands/ci"
    mkdir -p "$tmp/docs"
    echo "nav:" > "$tmp/mkdocs.yml"
    echo "# REFCARD" > "$tmp/docs/REFCARD.md"

    cat > "$tmp/commands/ci/internalcmd.md" <<'EOF'
---
name: internalcmd
description: Internal only
internal: true
---
EOF
    exit_code=0
    bash "$ROOT/scripts/doc-coverage-check.sh" --root "$tmp" > /dev/null 2>&1 || exit_code=$?
    if [[ "$exit_code" -ne 0 ]]; then
        fail "internal command should not cause non-zero exit"
    fi
    pass "skips internal commands"
}

test_detects_missing_refcard
test_detects_missing_nav
test_skips_deprecated
test_skips_internal
```

- [ ] **Step 2: Run tests — expect FAIL (script doesn't exist yet)**

```bash
bash tests/test_doc_coverage.sh
# Expected: multiple failures — script not found
```

- [ ] **Step 3: Create scripts/doc-coverage-check.sh**

```bash
#!/usr/bin/env bash
# doc-coverage-check.sh — verify doc surfaces exist for every active command
# Exit 0: all blocking surfaces present. Exit 1: blocking gaps found.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${SCRIPT_DIR}/.."
JSON_MODE=false
SINCE_REF=""

usage() {
    echo "Usage: $0 [--root DIR] [--since GIT_REF] [--json]"
    echo "  --root DIR      Project root (default: script's parent)"
    echo "  --since REF     Only check commands changed since git ref"
    echo "  --json          Output JSON array of findings"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --root) ROOT="$2"; shift 2 ;;
        --since) SINCE_REF="$2"; shift 2 ;;
        --json) JSON_MODE=true; shift ;;
        -h|--help) usage ;;
        *) echo "Unknown arg: $1"; usage ;;
    esac
done

COMMANDS_DIR="$ROOT/commands"
REFCARD="$ROOT/docs/REFCARD.md"
MKDOCS="$ROOT/mkdocs.yml"

blocking_gaps=0
warn_gaps=0
json_findings=()

# Parse a frontmatter field from a markdown file
# Usage: get_field FILE FIELD
get_field() {
    local file="$1" field="$2"
    sed -n '/^---$/,/^---$/{ /^'"$field"':/s/^'"$field"':[[:space:]]*//p; }' "$file" 2>/dev/null | head -1 | tr -d '"'"'"
}

# Emit a finding
finding() {
    local cmd="$1" surface="$2" severity="$3" message="$4"
    if [[ "$JSON_MODE" == "true" ]]; then
        json_findings+=("{\"cmd\":\"$cmd\",\"surface\":\"$surface\",\"severity\":\"$severity\",\"message\":\"$message\"}")
    else
        local icon="🔴"
        [[ "$severity" == "warn" ]] && icon="🟡"
        echo "  $icon $cmd — $message"
    fi
    [[ "$severity" == "block" ]] && blocking_gaps=$((blocking_gaps + 1))
    [[ "$severity" == "warn" ]]  && warn_gaps=$((warn_gaps + 1))
}

# Build list of command files to check
if [[ -n "$SINCE_REF" ]]; then
    mapfile -t cmd_files < <(
        git -C "$ROOT" diff --name-only "$SINCE_REF"..HEAD -- 'commands/**/*.md' 2>/dev/null \
        | grep -v -E '(index|README)\.md$' || true
    )
    # Also include untracked new files
    mapfile -t untracked < <(
        git -C "$ROOT" ls-files --others --exclude-standard 'commands/**/*.md' 2>/dev/null || true
    )
    cmd_files+=("${untracked[@]}")
else
    mapfile -t cmd_files < <(
        find "$COMMANDS_DIR" -name "*.md" \
            ! -name "index.md" ! -name "README.md" \
            2>/dev/null | sort
    )
fi

[[ "${#cmd_files[@]}" -eq 0 ]] && { echo "No command files to check."; exit 0; }

[[ "$JSON_MODE" != "true" ]] && echo "Doc Coverage Check (${#cmd_files[@]} commands)"

for cmd_file in "${cmd_files[@]}"; do
    [[ -z "$cmd_file" ]] && continue
    # Use absolute path for field parsing
    local_file="$cmd_file"
    [[ "$cmd_file" != /* ]] && local_file="$ROOT/$cmd_file"
    [[ -f "$local_file" ]] || continue

    # Skip deprecated and internal
    deprecated=$(get_field "$local_file" "deprecated")
    internal=$(get_field "$local_file" "internal")
    [[ "$deprecated" == "true" ]] && continue
    [[ "$internal"   == "true" ]] && continue

    # Derive command name: commands/ci/watch.md → ci:watch → /craft:ci:watch
    rel="${local_file#"$COMMANDS_DIR/"}"
    rel="${rel%.md}"
    cmd_name=$(echo "$rel" | tr '/' ':')

    # Check 1: REFCARD row (blocking)
    if [[ -f "$REFCARD" ]]; then
        if ! grep -qF "$cmd_name" "$REFCARD" 2>/dev/null; then
            finding "$cmd_name" "refcard" "block" "Missing REFCARD row in docs/REFCARD.md"
        fi
    fi

    # Check 2: mkdocs.yml nav entry (blocking)
    if [[ -f "$MKDOCS" ]]; then
        # Look for the command file path in nav section
        rel_path="${local_file#"$ROOT/"}"
        if ! grep -qF "$rel_path" "$MKDOCS" 2>/dev/null; then
            finding "$cmd_name" "nav" "block" "Missing mkdocs.yml nav entry for $rel_path"
        fi
    fi

    # Check 3: Tutorial (warn only — required if arguments: present)
    has_args=$(get_field "$local_file" "arguments")
    if [[ -n "$has_args" ]]; then
        # Look for tutorial file or reference in docs/tutorials/
        tut_glob="$ROOT/docs/tutorials/*${cmd_name//:/-}*"
        # shellcheck disable=SC2086
        if ! ls $tut_glob 2>/dev/null | grep -q .; then
            finding "$cmd_name" "tutorial" "warn" "Has arguments: but no tutorial in docs/tutorials/"
        fi
    fi
done

# Output JSON
if [[ "$JSON_MODE" == "true" ]]; then
    echo "["
    for i in "${!json_findings[@]}"; do
        [[ $i -lt $((${#json_findings[@]} - 1)) ]] \
            && echo "  ${json_findings[$i]}," \
            || echo "  ${json_findings[$i]}"
    done
    echo "]"
    exit $(( blocking_gaps > 0 ? 1 : 0 ))
fi

# Human summary
echo ""
echo "Blocking gaps:  $blocking_gaps"
echo "Warnings:       $warn_gaps"
[[ "$blocking_gaps" -gt 0 ]] && echo "Status: ❌ FAIL" || echo "Status: ✅ PASS"
exit $(( blocking_gaps > 0 ? 1 : 0 ))
```

- [ ] **Step 4: Make executable and run tests**

```bash
chmod +x scripts/doc-coverage-check.sh
bash tests/test_doc_coverage.sh
# Expected: all PASS
```

- [ ] **Step 5: Smoke test against the real repo (should pass — all commands documented)**

```bash
bash scripts/doc-coverage-check.sh
# Expected: Status: ✅ PASS  (or any warnings about tutorials are non-blocking)
```

- [ ] **Step 6: Commit**

```bash
git add scripts/doc-coverage-check.sh tests/test_doc_coverage.sh
git commit -m "feat(doc-coverage): add doc-coverage-check.sh — REFCARD + nav + tutorial surface checker"
```

---

## Task 3: `scripts/refcard-gen.sh` — auto-generate REFCARD rows

**Context for implementer:** `docs/REFCARD.md` is currently hand-maintained. This script generates the command table rows from frontmatter `name`, `description`, and `category` fields. It prints rows to stdout; the caller appends or replaces. The REFCARD structure has per-category tables with rows like `| \`/craft:ci:watch\` | ci | description |`. The script must NOT overwrite human-written sections (overview, usage examples) — only the generated command table rows marked between sentinel comments.

**Files:**

- Create: `scripts/refcard-gen.sh`
- Create: `tests/test_refcard_gen.sh`

**Interfaces:**

- Consumes: `commands/**/*.md` frontmatter (`name`, `description`, `category`, `deprecated`, `internal`)
- Produces: stdout with markdown table rows per category, wrapped in sentinel comments:

  ```
  <!-- REFCARD:GENERATED:START:ci -->
  | `/craft:ci:triage` | ci | Classify a failing CI check |
  | `/craft:ci:watch` | ci | Poll a run, route next action |
  <!-- REFCARD:GENERATED:END:ci -->
  ```

- `--category CAT`: only emit rows for that category
- `--check`: exit 1 if generated output differs from what's in docs/REFCARD.md (used by pre-release-check)

- [ ] **Step 1: Create tests/test_refcard_gen.sh**

```bash
#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TMPDIR_TEST="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_TEST"' EXIT

pass() { echo "PASS: $1"; }
fail() { echo "FAIL: $1"; exit 1; }

setup_fixture() {
    local tmp="$1"
    mkdir -p "$tmp/commands/ci"
    cat > "$tmp/commands/ci/triage.md" <<'EOF'
---
name: triage
description: Classify a failing CI check
category: ci
---
EOF
    cat > "$tmp/commands/ci/watch.md" <<'EOF'
---
name: watch
description: Poll a run, route next action
category: ci
---
EOF
    cat > "$tmp/commands/ci/deprecated-old.md" <<'EOF'
---
name: deprecated-old
description: Old command
deprecated: true
category: ci
---
EOF
}

test_generates_rows() {
    local tmp="$TMPDIR_TEST/gen_test"
    setup_fixture "$tmp"
    output=$(bash "$ROOT/scripts/refcard-gen.sh" --root "$tmp" --category ci)
    if ! echo "$output" | grep -q "craft:ci:triage"; then
        fail "missing triage row"
    fi
    if ! echo "$output" | grep -q "craft:ci:watch"; then
        fail "missing watch row"
    fi
    if echo "$output" | grep -q "deprecated-old"; then
        fail "deprecated command should not appear in output"
    fi
    pass "generates correct rows, skips deprecated"
}

test_check_mode_fails_on_drift() {
    local tmp="$TMPDIR_TEST/check_test"
    setup_fixture "$tmp"
    mkdir -p "$tmp/docs"
    # REFCARD missing triage row
    cat > "$tmp/docs/REFCARD.md" <<'EOF'
<!-- REFCARD:GENERATED:START:ci -->
| `/craft:ci:watch` | ci | Poll a run, route next action |
<!-- REFCARD:GENERATED:END:ci -->
EOF
    exit_code=0
    bash "$ROOT/scripts/refcard-gen.sh" --root "$tmp" --check > /dev/null 2>&1 || exit_code=$?
    if [[ "$exit_code" -eq 0 ]]; then
        fail "--check should exit 1 when REFCARD is stale"
    fi
    pass "--check mode exits 1 on drift"
}

test_generates_rows
test_check_mode_fails_on_drift
echo "All refcard-gen tests passed."
```

- [ ] **Step 2: Run tests — expect FAIL**

```bash
bash tests/test_refcard_gen.sh
# Expected: FAIL — script doesn't exist yet
```

- [ ] **Step 3: Create scripts/refcard-gen.sh**

```bash
#!/usr/bin/env bash
# refcard-gen.sh — generate REFCARD table rows from command frontmatter
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${SCRIPT_DIR}/.."
CATEGORY_FILTER=""
CHECK_MODE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --root) ROOT="$2"; shift 2 ;;
        --category) CATEGORY_FILTER="$2"; shift 2 ;;
        --check) CHECK_MODE=true; shift ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

COMMANDS_DIR="$ROOT/commands"
REFCARD="$ROOT/docs/REFCARD.md"

get_field() {
    local file="$1" field="$2"
    sed -n '/^---$/,/^---$/{ /^'"$field"':/s/^'"$field"':[[:space:]]*//p; }' "$file" 2>/dev/null | head -1 | tr -d '"'"'"
}

# Collect all categories (or just the filtered one)
declare -A cat_rows
mapfile -t cmd_files < <(find "$COMMANDS_DIR" -name "*.md" \
    ! -name "index.md" ! -name "README.md" | sort)

for cmd_file in "${cmd_files[@]}"; do
    [[ -f "$cmd_file" ]] || continue
    deprecated=$(get_field "$cmd_file" "deprecated")
    internal=$(get_field "$cmd_file" "internal")
    [[ "$deprecated" == "true" ]] && continue
    [[ "$internal"   == "true" ]] && continue

    category=$(get_field "$cmd_file" "category")
    [[ -z "$category" ]] && continue
    [[ -n "$CATEGORY_FILTER" && "$category" != "$CATEGORY_FILTER" ]] && continue

    description=$(get_field "$cmd_file" "description")
    rel="${cmd_file#"$COMMANDS_DIR/"}"
    rel="${rel%.md}"
    cmd_name=$(echo "$rel" | tr '/' ':')

    row="| \`/craft:${cmd_name}\` | ${category} | ${description} |"
    cat_rows["$category"]+="${row}"$'\n'
done

# Emit sentinel-wrapped blocks
generated=""
for cat in $(echo "${!cat_rows[@]}" | tr ' ' '\n' | sort); do
    block="<!-- REFCARD:GENERATED:START:${cat} -->"$'\n'
    block+="${cat_rows[$cat]}"
    block+="<!-- REFCARD:GENERATED:END:${cat} -->"
    generated+="${block}"$'\n'
done

if [[ "$CHECK_MODE" == "true" ]]; then
    if [[ ! -f "$REFCARD" ]]; then
        echo "REFCARD not found: $REFCARD" >&2; exit 1
    fi
    current=$(grep -A9999 'REFCARD:GENERATED' "$REFCARD" 2>/dev/null || true)
    if [[ "$current" != *"${cat_rows[*]:-}"* ]]; then
        # Diff for visibility
        diff <(echo "$generated") <(grep 'REFCARD:GENERATED\|^|' "$REFCARD" 2>/dev/null || true) || true
        echo "❌ REFCARD is stale — run scripts/refcard-gen.sh and commit" >&2
        exit 1
    fi
    echo "✅ REFCARD is current"
    exit 0
fi

echo "$generated"
```

- [ ] **Step 4: Make executable and run tests**

```bash
chmod +x scripts/refcard-gen.sh
bash tests/test_refcard_gen.sh
# Expected: All refcard-gen tests passed.
```

- [ ] **Step 5: Commit**

```bash
git add scripts/refcard-gen.sh tests/test_refcard_gen.sh
git commit -m "feat(doc-coverage): add refcard-gen.sh — auto-generate REFCARD rows from frontmatter"
```

---

## Task 4: Extend `docs-staleness-check.sh` Phase 8

**Context for implementer:** `scripts/docs-staleness-check.sh` has a `phase8_skill_agent_coverage()` function starting at line 337. It already checks commands against `docs/commands.md`. We extend it with two new sub-checks: (1) REFCARD coverage via `doc-coverage-check.sh --json`, (2) mkdocs nav coverage. Both add `add_finding` calls using the existing helper.

**Files:**

- Modify: `scripts/docs-staleness-check.sh` — inside `phase8_skill_agent_coverage()` after line 385

**Interfaces:**

- Consumes: `scripts/doc-coverage-check.sh` (Task 2) — must be present
- Produces: Phase 8 findings now include REFCARD + nav gaps alongside existing command-doc findings

- [ ] **Step 1: Add a Phase 8 extension test to tests/test_doc_coverage.sh**

Append to `tests/test_doc_coverage.sh`:

```bash
# --- Test: staleness check Phase 8 catches missing REFCARD row ---
test_phase8_catches_refcard_gap() {
    # Use the real staleness check — it calls doc-coverage-check.sh internally
    # Create a minimal fixture via tmp command file that we can add temporarily
    local tmp_cmd="$ROOT/commands/ci/_test_coverage_gap_$$.md"
    cat > "$tmp_cmd" <<'EOF'
---
name: _test_coverage_gap
description: Temp test command
category: ci
---
EOF
    # Run staleness check JSON mode and check Phase 8 findings
    output=$(bash "$ROOT/scripts/docs-staleness-check.sh" --json 2>/dev/null || true)
    rm -f "$tmp_cmd"
    if ! echo "$output" | grep -q "refcard\|REFCARD\|nav"; then
        fail "Phase 8 did not report REFCARD/nav gap for new command"
    fi
    pass "Phase 8 detects REFCARD/nav gap for undocumented command"
}

test_phase8_catches_refcard_gap
```

- [ ] **Step 2: Run test — expect FAIL (Phase 8 not extended yet)**

```bash
bash tests/test_doc_coverage.sh 2>/dev/null | grep -E "PASS|FAIL|Task"
# Expected: FAIL on the phase8 test
```

- [ ] **Step 3: Extend phase8_skill_agent_coverage() in docs-staleness-check.sh**

After the closing `done` of the commands coverage `while` loop (around line 385, before the `# --- Skills coverage ---` comment), add:

```bash
    # --- Doc surface coverage (REFCARD + nav) ---
    # Delegate to doc-coverage-check.sh for structured findings
    local cov_script="${SCRIPT_DIR}/doc-coverage-check.sh"
    if [[ -x "$cov_script" ]]; then
        local cov_json
        cov_json=$(bash "$cov_script" --json 2>/dev/null || true)
        # Parse each finding from JSON and add_finding
        while IFS= read -r line; do
            [[ -z "$line" ]] && continue
            local cmd surface severity message
            cmd=$(echo "$line" | sed 's/.*"cmd":"\([^"]*\)".*/\1/')
            surface=$(echo "$line" | sed 's/.*"surface":"\([^"]*\)".*/\1/')
            severity_raw=$(echo "$line" | sed 's/.*"severity":"\([^"]*\)".*/\1/')
            message=$(echo "$line" | sed 's/.*"message":"\([^"]*\)".*/\1/')
            # Map block→error, warn→warning for staleness check convention
            local sev="warning"
            [[ "$severity_raw" == "block" ]] && sev="error"
            add_finding 8 "$sev" "commands/${cmd//:///}.md" \
                "$message" "uncertain" "doc-coverage:${surface}:${cmd}"
            issues=$((issues + 1))
        done < <(echo "$cov_json" | grep '"cmd"' || true)
    fi
```

- [ ] **Step 4: Run tests — expect PASS**

```bash
bash tests/test_doc_coverage.sh 2>/dev/null
# Expected: all PASS
```

- [ ] **Step 5: Verify real repo still passes staleness check**

```bash
./scripts/docs-staleness-check.sh --non-interactive
# Expected: all GREEN (no new gaps in real repo)
```

- [ ] **Step 6: Commit**

```bash
git add scripts/docs-staleness-check.sh tests/test_doc_coverage.sh
git commit -m "feat(doc-coverage): extend staleness check Phase 8 with REFCARD + nav coverage sub-checks"
```

---

## Task 5: `pre-release-check.sh` doc coverage gate (blocking)

**Context for implementer:** `scripts/pre-release-check.sh` validates metadata before a release. We add a doc coverage gate after the existing checks. It calls `doc-coverage-check.sh` and exits 1 (blocking) if any blocking gap exists. Warnings (missing tutorials) are printed but don't block. This corresponds to **Step 13.4** in the release pipeline.

**Files:**

- Modify: `scripts/pre-release-check.sh` — add new section before final summary

**Interfaces:**

- Consumes: `scripts/doc-coverage-check.sh` (Task 2)
- Produces: pre-release-check.sh exits 1 if blocking doc gaps exist; exit 0 if only warnings

- [ ] **Step 1: Add test to tests/test_doc_coverage.sh**

Append:

```bash
# --- Test: pre-release-check.sh blocks on missing doc surfaces ---
test_prerelease_blocks_on_doc_gap() {
    # Temporarily add an undocumented command
    local tmp_cmd="$ROOT/commands/ci/_prerelease_gap_$$.md"
    cat > "$tmp_cmd" <<'EOF'
---
name: _prerelease_gap
description: Temp undocumented command
category: ci
---
EOF
    local version
    version=$(grep '"version"' "$ROOT/plugin.json" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    exit_code=0
    bash "$ROOT/scripts/pre-release-check.sh" "$version" > /dev/null 2>&1 || exit_code=$?
    rm -f "$tmp_cmd"
    if [[ "$exit_code" -eq 0 ]]; then
        fail "pre-release-check.sh should exit 1 when commands have missing doc surfaces"
    fi
    pass "pre-release-check.sh blocks on missing doc surfaces"
}

test_prerelease_blocks_on_doc_gap
```

- [ ] **Step 2: Run test — expect FAIL**

```bash
bash tests/test_doc_coverage.sh 2>/dev/null | tail -5
# Expected: FAIL on prerelease test
```

- [ ] **Step 3: Add doc coverage check to pre-release-check.sh**

Find the final summary block in `scripts/pre-release-check.sh` (search for `echo "Pre-release check" or "SUMMARY"`). Before it, add:

```bash
# --- Doc Coverage Gate (Step 13.4) ---
echo ""
echo "=== Doc Coverage Gate ==="
DOC_COVERAGE_SCRIPT="$(dirname "$0")/doc-coverage-check.sh"
if [[ -x "$DOC_COVERAGE_SCRIPT" ]]; then
    doc_exit=0
    bash "$DOC_COVERAGE_SCRIPT" || doc_exit=$?
    if [[ "$doc_exit" -ne 0 ]]; then
        echo "❌ BLOCKING: Commands with missing REFCARD rows or nav entries." >&2
        echo "   Run: bash scripts/doc-coverage-check.sh" >&2
        echo "   Fix gaps, then re-run pre-release-check.sh" >&2
        ERRORS=$((ERRORS + 1))
    else
        echo "✅ Doc coverage: all commands documented"
    fi
else
    echo "⚠️  doc-coverage-check.sh not found — skipping doc coverage gate"
fi
```

(The exact insertion point depends on the existing summary variable — grep for `ERRORS` in `pre-release-check.sh` to find the pattern used; add to the same `ERRORS` counter.)

- [ ] **Step 4: Run tests — expect PASS**

```bash
bash tests/test_doc_coverage.sh 2>/dev/null
```

- [ ] **Step 5: Verify pre-release-check passes on current clean repo**

```bash
version=$(grep '"version"' plugin.json | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
bash scripts/pre-release-check.sh "$version"
# Expected: passes all checks including new doc coverage gate
```

- [ ] **Step 6: Commit**

```bash
git add scripts/pre-release-check.sh tests/test_doc_coverage.sh
git commit -m "feat(doc-coverage): add blocking doc coverage gate to pre-release-check.sh (Step 13.4)"
```

---

## Task 6: `/craft:check` pre-commit warning

**Context for implementer:** `commands/check.md` defines the pre-flight check command. When `--for commit` is passed (or default mode), and staged files include a new `commands/**/*.md`, craft should call `doc-coverage-check.sh --since HEAD` and print a non-blocking checklist. The command file itself defines the behavior description — the actual check logic goes in a new helper section of the check command's implementation prose that Claude Code reads when executing `/craft:check`.

**Files:**

- Modify: `commands/check.md` — add `doc-surfaces` check to the `--for commit` section

**Interfaces:**

- Consumes: `scripts/doc-coverage-check.sh --since HEAD` (Task 2)
- Produces: When staged files include new command `.md` files, `/craft:check` prints the doc-surfaces checklist (non-blocking — never fails the check)

- [ ] **Step 1: Find the --for commit section in commands/check.md**

```bash
grep -n "for commit\|pre.commit\|staged" commands/check.md | head -10
```

- [ ] **Step 2: Add doc-surfaces check to the commit mode section in commands/check.md**

Find the section describing what `--for commit` checks. Add:

```markdown
### Doc Surfaces Warning (non-blocking)

When `--for commit` is active (or mode is default and staged files include `commands/**/*.md`):

```bash
# Detect new/modified command files in staging area
new_cmds=$(git diff --cached --name-only --diff-filter=A -- 'commands/**/*.md' 2>/dev/null || true)
if [[ -n "$new_cmds" ]]; then
    echo ""
    echo "⚠️  New commands detected. Doc surfaces needed:"
    bash scripts/doc-coverage-check.sh --since HEAD 2>/dev/null || true
    echo ""
    echo "Run /craft:docs:update --post-merge to fill gaps."
fi
```

This check is **non-blocking** — it prints the checklist but never causes `/craft:check` to fail.

```

- [ ] **Step 3: Verify command-audit.sh is happy with the updated check.md**

```bash
bash scripts/command-audit.sh commands/check.md
# Expected: no errors
```

- [ ] **Step 4: Commit**

```bash
git add commands/check.md
git commit -m "feat(doc-coverage): add non-blocking doc-surfaces warning to /craft:check --for commit"
```

---

## Task 7: Wire Step 13.4 into release skill + make post-merge mandatory

**Context for implementer:** Two doc changes: (1) `skills/release/SKILL.md` needs a new Step 13.4 block inserted between Step 13 and Step 13.5. (2) `docs/workflows/release-workflow.md` (if it exists) or the post-merge section of the release skill needs a "mandatory post-merge docs update" step. These are documentation changes, no new code.

**Files:**

- Modify: `skills/release/SKILL.md` around line 1091
- Modify: `docs/workflows/release-workflow.md` (post-merge section)

- [ ] **Step 1: Insert Step 13.4 in skills/release/SKILL.md**

Find the line `### Step 13.5: Post-Release Sweep` (around line 1091). Insert BEFORE it:

```markdown
### Step 13.4: Doc Coverage Gate (MANDATORY)

Before sweeping for drift, verify all commands shipped in this release have their doc surfaces. This check is performed by `pre-release-check.sh` (Task 5 above already wired it in). If you skipped `pre-release-check.sh`, run manually:

```bash
bash scripts/doc-coverage-check.sh
```

**Blocking:** Missing REFCARD rows or mkdocs nav entries → fix before continuing.
**Warning:** Missing tutorials (commands with `arguments:`) → add tutorial before next release but does not block.

If gaps found, fix them:

1. Add missing REFCARD rows: `bash scripts/refcard-gen.sh --category <cat>`  (copy rows to docs/REFCARD.md)
2. Add missing nav entries to `mkdocs.yml`
3. Re-run `bash scripts/doc-coverage-check.sh` until exit 0

```bash
git add docs/REFCARD.md mkdocs.yml
git commit -m "docs: add doc surfaces for newly shipped commands"
```

```

- [ ] **Step 2: Add mandatory post-merge docs update to release workflow**

In `docs/workflows/release-workflow.md` (or wherever the PR merge workflow is documented), add after the "merge PR to dev" step:

```markdown
### After Every PR Merge to `dev` (MANDATORY)

Run the post-merge docs update scoped to changes since the last release tag:

```bash
/craft:docs:update --post-merge --since-release
```

This auto-fixes: nav entries, REFCARD rows (via refcard-gen.sh), version refs.
It prompts for: tutorials (when new command has `arguments:`), changelog draft.

**Do not skip this step.** Doc debt caught here takes 5 minutes. Doc debt caught at release takes longer and blocks the pipeline.

```

- [ ] **Step 3: Verify staleness check still passes**

```bash
./scripts/docs-staleness-check.sh --non-interactive
# Expected: GREEN
```

- [ ] **Step 4: Commit**

```bash
git add skills/release/SKILL.md docs/workflows/release-workflow.md
git commit -m "docs(release): add Step 13.4 doc coverage gate + mandatory post-merge docs update step"
```

---

## Task 8: Run full test suite + validate-counts

**Context for implementer:** Verify everything hangs together. The new scripts should be counted nowhere in the plugin counts (they're scripts, not commands/skills/agents), but validate-counts.sh should still pass.

- [ ] **Step 1: Run all new tests**

```bash
bash tests/test_doc_coverage.sh
bash tests/test_refcard_gen.sh
# Expected: all PASS
```

- [ ] **Step 2: Run the full pytest suite**

```bash
python3 -m pytest tests/ -v --tb=short 2>&1 | tail -20
# Expected: no new failures
```

- [ ] **Step 3: Run validate-counts and staleness check**

```bash
./scripts/validate-counts.sh
./scripts/docs-staleness-check.sh --non-interactive
# Expected: both GREEN
```

- [ ] **Step 4: Smoke test the full doc-coverage-check against real repo**

```bash
bash scripts/doc-coverage-check.sh
# Expected: Status: ✅ PASS
bash scripts/refcard-gen.sh | head -20
# Expected: generated REFCARD rows for all active commands
```

- [ ] **Step 5: Final commit**

```bash
git add -u
git commit -m "test(doc-coverage): all integration tests passing — doc coverage enforcement complete"
```

---

## Self-Review

**Spec coverage check:**

- ✅ REFCARD coverage check in Phase 8 — Task 4
- ✅ Command nav entries in Phase 8 — Task 4
- ✅ Pre-commit doc checklist hook — Task 6 (`/craft:check`)
- ✅ `--since-release` scoping — Task 2 (`--since` flag)
- ✅ `deprecated: true` skip — Task 2 + Task 3
- ✅ `internal: true` new field — Task 1
- ✅ REFCARD auto-generate — Task 3
- ✅ Tutorial required if `arguments:` — Task 2
- ✅ Release Step 13.4 — Task 5 (pre-release-check) + Task 7 (skill doc)
- ✅ Post-merge mandatory — Task 7

**No placeholders found.**

**Type/name consistency:**

- `doc-coverage-check.sh --root`, `--since`, `--json` — consistent across Tasks 2, 4, 5
- `refcard-gen.sh --root`, `--category`, `--check` — consistent across Tasks 3, 7
- `get_field()` helper defined in both scripts independently (no shared lib needed — YAGNI)
- `ERRORS` counter in pre-release-check.sh — Task 5 uses it; implementer must grep to find the exact variable name used in that file before inserting

---

## Execution Handoff

Plan saved to `docs/superpowers/plans/2026-06-18-doc-coverage-enforcement.md`.

**Two execution options:**

**1. Subagent-Driven (recommended)** — fresh subagent per task, review between tasks, fast iteration. Use `superpowers:subagent-driven-development`.

**2. Inline Execution** — execute in this session using `superpowers:executing-plans`, batch with checkpoints.

**Before either:** Create the feature worktree:

```bash
git worktree add ~/.git-worktrees/craft/feature-doc-coverage -b feature/doc-coverage-enforcement dev
```

Then open a new Claude Code session in that worktree directory.
