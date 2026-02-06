# SPEC: Teaching Ecosystem Coordination (Craft + Scholar + Flow-CLI)

**Created:** 2026-02-06
**Status:** Draft
**Scope:** Cross-tool (Craft, Scholar, Flow-CLI)
**Effort:** ~8 hours total across 5 quick wins
**Priority:** High (Quick Win 3 is critical — Craft teaching commands broken on real projects)

---

## Problem Statement

The teaching workflow is split across three tools with no transparency about who does what:

- **Craft** (Claude Code plugin): Site management, publish workflow, semester progress, content validation
- **Scholar** (Claude Code plugin): AI content generation (exams, lectures, slides, quizzes, assignments, rubrics, feedback, syllabi), YAML schema validation
- **Flow-CLI** (ZSH): Shell-speed dispatcher (`teach` command), deploy with rollback, config editing, templates, macros

**Pain points:**

1. Duplicate config parsing (3x) with incompatible schemas
2. No unified discovery — users don't know which tool handles what
3. Documented shell aliases (`tst`, `tweek`, `tlec`, `tpublish`) don't exist anywhere
4. Isolated semester tracking (Craft and flow-cli each have their own)
5. Config schema divergence means Craft teaching commands silently fail on real projects

**Critical bug:** Craft's `teach_config.py` requires `dates.start`/`dates.end` and `course.number`, but the real teaching project (stat-545) uses flow-cli's schema: `semester_info.start_date`/`semester_info.end_date` and `course.name`. Craft's `/craft:site:progress` and `/craft:site:publish` would fail with `ValueError` on real configs.

---

## Overlap Analysis

| Capability | Craft | Scholar | Flow-CLI | Status |
|---|---|---|---|---|
| **Config parsing** | `teach_config.py` (expects `dates.*`) | `config/loader.js` (reads `scholar.*`) | `teach-dispatcher.zsh` (reads `semester_info.*`) | 3x duplicated, incompatible |
| **Content validation** | `teaching_validation.py` (syllabus, schedule, assignments) | `/teaching:validate` (4-level YAML schema) | `teach validate` (render + syntax) | Complementary but invisible |
| **Semester progress** | `semester_progress.py` + `/craft:site:progress` | None | `teaching-utils.zsh` + `teach status` | 2x duplicated |
| **Publishing/deploy** | `/craft:site:publish` (5-step safety) | None | `teach deploy` (history, rollback, partial) | 2x duplicated |
| **AI content gen** | None | 9 commands (exam, lecture, slides, quiz, etc.) | Wraps scholar via `_teach_build_command()` | Scholar canonical, flow-cli wraps |
| **Teaching detection** | `detect_teaching_mode.py` (3-priority) | Pre-command hook (sync check) | `_teach_require_config()` | 3x duplicated |
| **Shell aliases** | Documented (`tst`, `tweek`, `tlec`, `tpublish`) | None | Not implemented | Documented but broken |

### Unique to each tool

| Tool | Unique Capabilities |
|---|---|
| **Craft** | CI integration, pre-commit hooks, MkDocs site commands, teaching mode 3-priority detection |
| **Scholar** | AI content generation (9 commands), 4-layer teaching style system, JSON Schema v2, YAML-JSON sync/diff/migrate |
| **Flow-CLI** | Shell-speed execution (<10ms), deploy with rollback/history, template/macro/prompt management, lesson plan CRUD, archive/backup, doctor/health-check, interactive wizards |

---

## Config Schema Divergence (Evidence)

### Real stat-545 config (`/Users/dt/projects/teaching/stat-545/.flow/teach-config.yml`)

```yaml
course:
  name: "STAT 545"                    # flow-cli uses 'name'
  full_name: "STAT 545 - Analysis of Variance and Experimental Design"
  semester: "spring"                  # lowercase
  year: 2026

semester_info:
  start_date: "2026-01-19"           # flow-cli uses semester_info.start_date
  end_date: "2026-05-16"             # flow-cli uses semester_info.end_date
  breaks:
    - name: "MLK Day"
      start: "2026-01-19"            # single-day break (start == end)
      end: "2026-01-19"
    - name: "Spring Break"
      start: "2026-03-15"
      end: "2026-03-22"
  finals_week:
    start: "2026-05-11"
    end: "2026-05-16"
```

### What Craft expects (`commands/utils/teach_config.py`)

```yaml
course:
  number: "STAT 545"        # craft requires 'number'
  title: "..."               # craft requires 'title'
  semester: "Spring"         # capitalized
  year: 2026

dates:
  start: "2026-01-19"       # craft requires dates.start
  end: "2026-05-16"         # craft requires dates.end
  breaks:
    - name: "Spring Break"
      start: "2026-03-15"   # craft rejects start == end (line 257)
      end: "2026-03-22"
```

### Specific failures on real config

1. **`validate_config()` line 278-280:** Requires `"course"` and `"dates"` top-level sections. The stat-545 config has `"course"` but `"semester_info"` instead of `"dates"` → `ValueError: Missing required section: 'dates'`
2. **`validate_config()` line 288-291:** Requires `course.number` — stat-545 has `course.name` → `ValueError: Missing required field: 'course.number'`
3. **`validate_config()` line 294-299:** Validates `semester` against `["Spring", "Fall", "Winter", "Summer"]` — stat-545 has `"spring"` (lowercase) → `ValueError: Invalid semester: 'spring'`
4. **`validate_breaks()` line 257-258:** Rejects `break_start >= break_end` — MLK Day is a single-day break where `start == end` → `ValueError: Break 'MLK Day': start date must be before end date`
5. **`semester_progress.py` line 72-74:** Reads `config["dates"]["start"]` / `config["dates"]["end"]` — would `KeyError` after normalization failure

---

## Quick Wins

### Quick Win 1: Implement Missing Shell Aliases

**Effort:** 30 minutes | **Tool:** flow-cli | **Impact:** High (fixes documentation lie)

The aliases `tst`, `tweek`, `tlec`, `tpublish` are documented in Craft's CLAUDE.md but never defined anywhere. Confirmed by grep across all flow-cli files — only references are in archived docs and test files listing expected aliases.

**Where:** Flow-cli already has alias infrastructure in `commands/alias.zsh` (`flow_alias()` with add/rm/show/doctor/test subcommands). Teaching aliases should integrate with this system.

**Option A — Static alias file:**
Create `/Users/dt/projects/dev-tools/flow-cli/commands/teach-aliases.zsh`:

```zsh
# Teaching workflow shell aliases
# Sourced by flow-cli init

alias tst='teach status'        # Teaching dashboard
alias tweek='teach week'         # Current week info
alias tlec='teach lecture'       # Generate lecture
alias tpublish='teach deploy'    # Deploy course site
```

**Option B — Use flow_alias system:**

```zsh
flow_alias add tst "teach status" --category teaching
flow_alias add tweek "teach week" --category teaching
flow_alias add tlec "teach lecture" --category teaching
flow_alias add tpublish "teach deploy" --category teaching
```

**Decision:** Option A is simpler and more transparent. Option B integrates with existing infrastructure but aliases become user-local state.

**Verify:** Source flow-cli, run each alias, confirm it routes correctly through the teach dispatcher.

---

### Quick Win 2: Add `teach map` — Unified Ecosystem Discovery

**Effort:** 2-3 hours | **Tool:** flow-cli | **Impact:** High (single source of truth)

A `teach map` subcommand that shows the full ecosystem with clear tool attribution.

**Where:** Add `map` case to `teach()` function in `teach-dispatcher.zsh` (line 4518, before the `*` catch-all). Create `_teach_map()` function.

**Changes to teach-dispatcher.zsh:**

1. Add routing in `teach()` (after `style|st)` block, before `*)`):

```zsh
map)
    _teach_map "$@"
    ;;
```

2. Add `_teach_map()` function (before `_teach_dispatcher_help()`):

```zsh
_teach_map() {
    # Detect which tools are available
    local has_scholar=false has_craft=false
    command -v claude &>/dev/null && {
        # Check for scholar plugin
        [[ -d "${HOME}/.claude/plugins/scholar" ]] && has_scholar=true
        # Check for craft plugin
        [[ -d "${HOME}/.claude/plugins/craft" ]] && has_craft=true
    }

    # ... box-drawing output showing all commands with tool attribution
}
```

**Output design:**

```
╭─────────────────────────────────────────────────────╮
│  TEACHING ECOSYSTEM MAP                              │
╰─────────────────────────────────────────────────────╯

SETUP & CONFIG                         [flow-cli]
  teach init           Create .flow/teach-config.yml
  teach config         Edit configuration
  teach doctor         Health check & dependency fix
  teach dates          Date management
  teach plan           Lesson plan CRUD
  teach templates      Template management
  teach macros         LaTeX macro management
  teach prompt         AI prompt management
  teach style          Teaching style management

CONTENT GENERATION                     [scholar AI]
  teach lecture         Generate lecture notes (Quarto)
  teach exam            Generate exams with answer keys
  teach quiz            Create quizzes (Canvas/Moodle/PDF)
  teach slides          Generate RevealJS/Beamer slides
  teach assignment      Homework with solutions + rubrics
  teach rubric          Grading rubrics
  teach feedback        Student feedback
  teach syllabus        Course syllabus

VALIDATION                             [all three]
  teach validate        Render + syntax check         [flow-cli]
  /scholar:validate     YAML schema (4-level)         [scholar]
  /craft:site:check     Content completeness          [craft]

DEPLOYMENT                             [flow-cli]
  teach deploy          Deploy (preview/rollback)
  teach deploy --preview  Draft preview

SEMESTER TRACKING                      [flow-cli]
  teach status          Semester dashboard
  teach week            Current week details
  teach dates           Date management

SITE MANAGEMENT                        [craft]
  /craft:site:publish   5-step safe publish
  /craft:site:progress  Semester progress bar
  /craft:site:build     Teaching-aware build

MAINTENANCE                            [flow-cli]
  teach backup          Backup management
  teach archive         Archive semester
  teach clean           Delete _freeze/ + _site/
  teach cache           Cache operations
  teach profiles        Profile management

 Legend: [flow-cli] = shell command  [scholar] = Claude plugin
         [craft] = Claude plugin    [all three] = tools collaborate
```

**Pattern:** Follow existing `_teach_dispatcher_help()` box-drawing style (lines 4170-4250).

---

### Quick Win 3: Fix Config Schema Divergence in Craft

**Effort:** 1-2 hours | **Tool:** craft | **Impact:** Critical (Craft teaching commands broken on real projects)

**Where:** `/Users/dt/projects/dev-tools/craft/commands/utils/teach_config.py`

**What:** Add `_normalize_config()` adapter function called before `apply_defaults()` in `load_teach_config()`.

#### Changes to `teach_config.py`

**1. Add `_normalize_config()` function (after `VALID_SEMESTERS`, before `get_config_path()`):**

```python
def _normalize_config(raw_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize flow-cli schema (semester_info.*) to craft-native format (dates.*).

    Flow-cli's teach-config.yml uses:
        semester_info.start_date / end_date / breaks
        course.name (instead of course.number)
        course.semester: "spring" (lowercase)

    Craft expects:
        dates.start / end / breaks
        course.number
        course.semester: "Spring" (capitalized)

    Args:
        raw_config: Parsed YAML dictionary (modified in-place)

    Returns:
        The same dictionary with normalized schema
    """
    # Translate semester_info -> dates (if flow-cli schema detected)
    if "semester_info" in raw_config and "dates" not in raw_config:
        si = raw_config["semester_info"]
        raw_config["dates"] = {
            "start": si.get("start_date"),
            "end": si.get("end_date"),
            "breaks": si.get("breaks", []),
        }

    # Normalize course.name -> course.number (flow-cli uses 'name')
    if "course" in raw_config:
        c = raw_config["course"]
        if "number" not in c and "name" in c:
            c["number"] = c["name"]
        # Populate title from full_name if missing
        if "title" not in c and "full_name" in c:
            c["title"] = c["full_name"]

    # Normalize semester to capitalized form (flow-cli uses lowercase)
    if "course" in raw_config and "semester" in raw_config["course"]:
        sem = raw_config["course"]["semester"]
        if isinstance(sem, str):
            # Handle "spring" -> "Spring", "Spring 2026" -> "Spring"
            sem_word = sem.split()[0] if " " in sem else sem
            capitalized = sem_word.capitalize()
            if capitalized in VALID_SEMESTERS:
                raw_config["course"]["semester"] = capitalized

    # Normalize deployment from flow-cli's branches structure
    if "branches" in raw_config and "deployment" not in raw_config:
        branches = raw_config["branches"]
        raw_config["deployment"] = {
            "production_branch": branches.get("production", "production"),
            "draft_branch": branches.get("draft", "draft"),
        }

    return raw_config
```

**2. Call normalization in `load_teach_config()` (line ~456, before `apply_defaults()`):**

```python
    # Normalize flow-cli schema to craft-native format
    config = _normalize_config(config)

    # Apply defaults
    config = apply_defaults(config)
```

**3. Fix single-day break validation in `validate_breaks()` (line 257):**

Change `>=` to `>`:

```python
    # Before (rejects single-day breaks like holidays):
    if break_start >= break_end:
        errors.append(f"Break '{name}': start date must be before end date")

    # After (allows start == end for single-day holidays):
    if break_start > break_end:
        errors.append(f"Break '{name}': start date must be before or equal to end date")
```

#### Changes to `semester_progress.py`

No changes needed. `semester_progress.py` reads from `config["dates"]` which will be populated by `_normalize_config()` before it's called.

#### Changes to `test_integration_teaching_workflow.py`

**1. Fix broken import (line 40):**

```python
# Before (functions don't exist):
from commands.utils.teach_config import parse_teach_config, calculate_current_week

# After (actual exports):
from commands.utils.teach_config import load_teach_config, _normalize_config, validate_config
```

**2. Add new test class `TestFlowCliSchemaNormalization`:**

```python
class TestFlowCliSchemaNormalization(unittest.TestCase):
    """Tests for flow-cli → craft schema normalization."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_dir = Path(self.temp_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @unittest.skipIf(not CONFIG_AVAILABLE, "Config module not available")
    def test_normalize_semester_info_to_dates(self):
        """Flow-cli's semester_info.start_date -> dates.start."""
        config = {
            "course": {"name": "STAT 545", "full_name": "STAT 545 - ANOVA",
                       "semester": "spring", "year": 2026},
            "semester_info": {
                "start_date": "2026-01-19",
                "end_date": "2026-05-16",
                "breaks": [{"name": "Spring Break",
                            "start": "2026-03-15", "end": "2026-03-22"}]
            }
        }
        result = _normalize_config(config)
        self.assertEqual(result["dates"]["start"], "2026-01-19")
        self.assertEqual(result["dates"]["end"], "2026-05-16")
        self.assertEqual(len(result["dates"]["breaks"]), 1)

    @unittest.skipIf(not CONFIG_AVAILABLE, "Config module not available")
    def test_normalize_course_name_to_number(self):
        """Flow-cli's course.name -> course.number."""
        config = {
            "course": {"name": "STAT 545", "full_name": "ANOVA",
                       "semester": "spring", "year": 2026},
            "semester_info": {"start_date": "2026-01-19",
                              "end_date": "2026-05-16"}
        }
        result = _normalize_config(config)
        self.assertEqual(result["course"]["number"], "STAT 545")
        self.assertEqual(result["course"]["title"], "ANOVA")

    @unittest.skipIf(not CONFIG_AVAILABLE, "Config module not available")
    def test_normalize_semester_capitalization(self):
        """Flow-cli's 'spring' -> 'Spring'."""
        config = {
            "course": {"name": "TEST 101", "semester": "spring", "year": 2026},
            "semester_info": {"start_date": "2026-01-19",
                              "end_date": "2026-05-16"}
        }
        result = _normalize_config(config)
        self.assertEqual(result["course"]["semester"], "Spring")

    @unittest.skipIf(not CONFIG_AVAILABLE, "Config module not available")
    def test_single_day_break_accepted(self):
        """Single-day holidays (start == end) should not fail validation."""
        config_dir = self.project_dir / ".flow"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "teach-config.yml"

        config_content = {
            "course": {"name": "STAT 545", "full_name": "ANOVA",
                       "semester": "spring", "year": 2026},
            "semester_info": {
                "start_date": "2026-01-19",
                "end_date": "2026-05-16",
                "breaks": [{"name": "MLK Day",
                            "start": "2026-01-20", "end": "2026-01-20"}]
            }
        }
        config_file.write_text(yaml.dump(config_content))
        config = load_teach_config(str(self.project_dir))
        self.assertIsNotNone(config, "Should parse flow-cli schema successfully")

    @unittest.skipIf(not CONFIG_AVAILABLE, "Config module not available")
    def test_full_stat545_fixture(self):
        """Full stat-545-style config loads successfully through craft pipeline."""
        config_dir = self.project_dir / ".flow"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "teach-config.yml"

        # Minimal stat-545-style config
        config_content = {
            "course": {
                "name": "STAT 545",
                "full_name": "STAT 545 - Analysis of Variance",
                "semester": "spring",
                "year": 2026
            },
            "semester_info": {
                "start_date": "2026-01-19",
                "end_date": "2026-05-16",
                "breaks": [
                    {"name": "MLK Day",
                     "start": "2026-01-20", "end": "2026-01-20"},
                    {"name": "Spring Break",
                     "start": "2026-03-15", "end": "2026-03-22"}
                ]
            }
        }
        config_file.write_text(yaml.dump(config_content))
        config = load_teach_config(str(self.project_dir))
        self.assertIsNotNone(config)
        self.assertEqual(config["course"]["number"], "STAT 545")
        self.assertEqual(config["dates"]["start"], "2026-01-19")
        self.assertEqual(config["course"]["semester"], "Spring")

    @unittest.skipIf(not CONFIG_AVAILABLE, "Config module not available")
    def test_craft_native_schema_unchanged(self):
        """Craft-native schema (dates.start) still works as before."""
        config_dir = self.project_dir / ".flow"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "teach-config.yml"

        config_content = {
            "course": {"number": "TEST 101", "title": "Test Course",
                       "semester": "Spring", "year": 2026},
            "dates": {"start": "2026-01-20", "end": "2026-05-15"}
        }
        config_file.write_text(yaml.dump(config_content))
        config = load_teach_config(str(self.project_dir))
        self.assertIsNotNone(config)
        self.assertEqual(config["course"]["number"], "TEST 101")
        self.assertEqual(config["dates"]["start"], "2026-01-20")
```

---

### Quick Win 4: Cross-Tool Validation Summary via `teach check`

**Effort:** 2-3 hours | **Tool:** flow-cli | **Impact:** Medium (unified health view)

**Where:** Add `check|chk` case to `teach()` function. Create `_teach_check()` function.

**What:** Runs all three validation layers and presents unified report:

1. Flow-cli's `teach validate --yaml` (config syntax + render check)
2. Scholar's schema validation via `_teach_build_command validate` (if available)
3. Craft's content validation via `python3 commands/utils/teaching_validation.py` (if available)

**Routing addition in `teach()` (before `*)`catch-all):**

```zsh
check|chk)
    case "$1" in
        --help|-h|help) _teach_check_help; return 0 ;;
        *) _teach_check "$@" ;;
    esac
    ;;
```

**`_teach_check()` function design:**

```zsh
_teach_check() {
    local config_file=$(_teach_require_config) || return 1
    local pass=0 warn=0 fail=0 total=0

    # 1. Config syntax (flow-cli)
    total=$((total + 1))
    if yq '.' "$config_file" &>/dev/null; then
        _check_pass "Config syntax" "flow-cli"
        pass=$((pass + 1))
    else
        _check_fail "Config syntax" "flow-cli" "YAML parse error"
        fail=$((fail + 1))
    fi

    # 2. Schema validation (scholar — if available)
    if [[ -d "${HOME}/.claude/plugins/scholar" ]]; then
        total=$((total + 1))
        # Invoke scholar validate and capture exit code
        # ...
    fi

    # 3. Content validation (craft — if available)
    local craft_validator="${HOME}/.claude/plugins/craft/commands/utils/teaching_validation.py"
    if [[ -f "$craft_validator" ]]; then
        total=$((total + 1))
        # Run python3 "$craft_validator" and parse output
        # ...
    fi

    # 4. Quarto render check (flow-cli)
    total=$((total + 1))
    # Run quarto check or validate --render
    # ...

    # Summary
    echo ""
    echo "$pass/$total passed, $warn warnings, $fail failures"
}
```

**Output:**

```
╭─────────────────────────────────────────────╮
│  TEACHING PROJECT HEALTH                     │
╰─────────────────────────────────────────────╯
  Config syntax      PASS   [flow-cli]
  YAML schema        PASS   [scholar]
  Syllabus sections  PASS   [craft]    4/4 required
  Schedule           WARN   [craft]    week 14 missing content
  Assignments        PASS   [craft]    all referenced files exist
  Quarto render      PASS   [flow-cli]

  5/6 passed, 1 warning
```

**Dependencies:** Quick Win 3 must be done first so Craft's validation doesn't reject real configs.

---

### Quick Win 5: Update Craft + Scholar CLAUDE.md Teaching Docs

**Effort:** 1 hour | **Tool:** craft + scholar | **Impact:** Medium (transparency)

**Where (3 files):**

1. `/Users/dt/projects/dev-tools/craft/CLAUDE.md` — Add "Teaching Ecosystem" section after "Key Files"
2. `/Users/dt/projects/dev-tools/scholar/CLAUDE.md` — Add equivalent section after "Configuration"
3. `/Users/dt/projects/dev-tools/craft/docs/guide/teaching-workflow.md` — Add ecosystem overview near top

**Content for all three locations (adapted per context):**

```markdown
## Teaching Ecosystem

The teaching workflow spans three tools. Each has clear ownership:

| Capability | Tool | Command/Skill |
|---|---|---|
| Config & setup | flow-cli | `teach init`, `teach config`, `teach doctor` |
| Content generation | Scholar | `teach lecture`, `teach exam`, etc. (9 commands) |
| Content validation | All three | `teach validate` / `/scholar:validate` / `/craft:site:check` |
| Deployment | flow-cli | `teach deploy` (history, rollback) |
| Semester tracking | flow-cli | `teach status`, `teach week` |
| Site management | Craft | `/craft:site:publish`, `/craft:site:progress` |
| Shell speed | flow-cli | All `teach *` commands (<10ms dispatch) |

### Which tool do I use?

- **"Generate a lecture/exam/quiz"** → `teach lecture` (routes to Scholar)
- **"Deploy the course site"** → `teach deploy` (flow-cli handles rollback)
- **"Check if my content is ready"** → `teach check` (runs all validators)
- **"What week is it?"** → `teach status` or `tst` alias
- **"Publish with CI safety"** → `/craft:site:publish` (5-step workflow)
- **"See all available commands"** → `teach map` (ecosystem overview)

### Config schema

Flow-cli is the canonical config owner. Its schema uses `semester_info.start_date`/`end_date` and `course.name`. Craft normalizes this to its internal format (`dates.start`/`end`, `course.number`) via `_normalize_config()` in `teach_config.py`.
```

---

## Implementation Order

| # | Quick Win | Effort | Tool | Blocked By |
|---|---|---|---|---|
| 1 | **QW3: Fix config schema** | 1-2h | craft | None |
| 2 | **QW1: Shell aliases** | 30min | flow-cli | None |
| 3 | **QW2: teach map** | 2-3h | flow-cli | None |
| 4 | **QW5: CLAUDE.md docs** | 1h | craft + scholar | QW3 (reference normalization) |
| 5 | **QW4: teach check** | 2-3h | flow-cli | QW3 (craft validation must work first) |

---

## Verification Checklist

- [ ] `python3 -c "from commands.utils.teach_config import load_teach_config; print(load_teach_config('/Users/dt/projects/teaching/stat-545'))"` succeeds
- [ ] Existing tests still pass: `python3 tests/test_integration_teaching_workflow.py`
- [ ] New normalization tests pass (6 tests)
- [ ] `tst` in stat-545 project shows semester dashboard
- [ ] `teach map` displays full ecosystem with tool attribution
- [ ] `/craft:site:progress` in stat-545 works with `semester_info` schema
- [ ] `teach check` in stat-545 shows unified validation from all three tools
- [ ] Craft CLAUDE.md contains Teaching Ecosystem section
- [ ] Scholar CLAUDE.md contains Teaching Ecosystem section

---

## Files Changed (Summary)

### Craft (this repo)

| File | Change |
|---|---|
| `commands/utils/teach_config.py` | Add `_normalize_config()`, fix single-day break validation |
| `tests/test_integration_teaching_workflow.py` | Fix broken import, add 6 normalization tests |
| `CLAUDE.md` | Add Teaching Ecosystem section |
| `docs/guide/teaching-workflow.md` | Add ecosystem overview |

### Flow-CLI (separate repo)

| File | Change |
|---|---|
| `commands/teach-aliases.zsh` | New file: `tst`, `tweek`, `tlec`, `tpublish` |
| `lib/dispatchers/teach-dispatcher.zsh` | Add `map` and `check` subcommands, `_teach_map()`, `_teach_check()` |

### Scholar (separate repo)

| File | Change |
|---|---|
| `CLAUDE.md` | Add Teaching Ecosystem section |

---

## Longer-Term Vision (Not in scope)

1. **Shared config adapter** — Standalone module that normalizes both schemas, all tools import from it
2. **Teaching context bus** — `.flow/.teach-context.json` file-based IPC for semester state sharing
3. **Unified pipeline** — `teach pipeline "Week 5"` chains: validate -> generate -> render -> deploy
4. **Scholar semester awareness** — Scholar's pre-command hook reads semester progress to auto-populate `--week`
