# Orchestration Plan: Brainstorm Question Control - Phase 1

**Created:** 2026-01-18
**Target:** v2.4.0
**Worktree:** `~/.git-worktrees/craft/feature-brainstorm-question-control`
**Estimated Effort:** 12 hours
**Status:** Ready to Execute

---

## Executive Summary

Implement Phase 1 (MVP) of the brainstorm question control feature, enabling users to:

- Specify custom question counts via colon notation (`d:5`, `m:12`)
- Filter questions by categories (`--categories req,tech,success`)
- Ask unlimited questions with milestone prompts
- Use a comprehensive 8-category question bank

**Success Criteria:** Users can control brainstorming depth and focus without Phase 2/3 features.

---

## Phase 1 Deliverables

| Task | Hours | Complexity | Priority |
|------|-------|------------|----------|
| 1. Colon notation parsing | 3h | Medium | Critical |
| 2. Question bank implementation | 2h | Low | Critical |
| 3. Categories flag (`--categories`) | 1h | Low | Critical |
| 4. Unlimited questions + prompts | 3h | Medium | Critical |
| 5. Documentation updates | 1h | Low | High |
| 6. Tests (unit + integration) | 2h | Medium | High |

**Total:** 12 hours

---

## Task Breakdown

### Task 1: Colon Notation Parsing [3 hours]

**Goal:** Parse `depth:N` syntax (e.g., `d:5`, `m:12`, `q:3`)

**Location:** `commands/workflow/brainstorm.md` - Step 0: Parse Arguments

**Implementation:**

```python
# Extend existing DEPTH_MAP with colon notation support
DEPTH_MAP = {
    'q': 'quick', 'quick': 'quick',
    'd': 'deep', 'deep': 'deep',
    'm': 'max', 'max': 'max',
    't': 'max', 'thorough': 'max'
}

def parse_depth_with_count(arg):
    """Parse depth:count notation.

    Examples:
        'd:5' → ('deep', 5)
        'm:12' → ('max', 12)
        'q:0' → ('quick', 0)
        'd' → ('deep', None)  # Use default

    Returns:
        tuple: (depth_mode, question_count) or (depth_mode, None)
    """
    if ':' not in arg:
        # Standard depth without count
        return (DEPTH_MAP.get(arg, arg), None)

    # Parse depth:count
    parts = arg.split(':', 1)
    depth_str = parts[0]
    count_str = parts[1]

    # Normalize depth
    depth = DEPTH_MAP.get(depth_str, depth_str)

    # Parse count
    try:
        count = int(count_str)
        if count < 0:
            raise ValueError("Negative count")
        return (depth, count)
    except ValueError:
        # Invalid count - will trigger validation prompt
        return (depth, 'invalid')

def get_default_question_count(depth):
    """Get default question count for depth."""
    defaults = {
        'quick': 0,
        'default': 2,
        'deep': 8,
        'max': 8
    }
    return defaults.get(depth, 2)
```

**Validation Handling:**

When invalid syntax detected (e.g., `d:abc`), prompt user:

```yaml
AskUserQuestion:
  question: "Invalid question count 'abc'. What did you mean?"
  header: "Count"
  multiSelect: false
  options:
    - label: "Use deep default (8 questions)"
      description: "Standard deep mode"
    - label: "0 questions"
      description: "Skip questions, just analyze"
    - label: "Enter number"
      description: "Specify exact count"
```

**Test Cases:**

- `d:5` → deep with 5 questions
- `m:12` → max with 12 questions
- `q:0` → quick with 0 questions
- `d:abc` → validation prompt
- `d:-5` → validation prompt
- `:5` alone → error (depth required)

**Acceptance Criteria:**

- ✅ All colon notation formats parse correctly
- ✅ Invalid syntax triggers interactive prompt
- ✅ Standalone `:N` shows error
- ✅ Counts override depth defaults

---

### Task 2: Question Bank Implementation [2 hours]

**Goal:** Create 8-category question bank with 2 questions each

**Location:** `commands/workflow/brainstorm.md` - New section after "Time Budget Guarantees"

**Question Bank Structure:**

```yaml
question_bank:
  requirements:
    - question: "What are the key requirements for this feature?"
      multiSelect: false
      options:
        - label: "Performance-critical"
          description: "Speed and efficiency are top priorities"
        - label: "User-facing functionality"
          description: "Direct user interaction and UX"
        - label: "Internal tooling"
          description: "Developer productivity and automation"
        - label: "Data processing"
          description: "Transform, validate, or store data"

    - question: "Are there any hard constraints we must work within?"
      multiSelect: true
      options:
        - label: "Technology stack limitations"
          description: "Must use specific languages/frameworks"
        - label: "Performance targets"
          description: "Response time, throughput requirements"
        - label: "Security requirements"
          description: "Compliance, authentication, authorization"
        - label: "Budget/resource limits"
          description: "Time, cost, or infrastructure constraints"

  users:
    - question: "Who is the primary user for this feature?"
      multiSelect: false
      options:
        - label: "End users"
          description: "People using the application"
        - label: "Developers"
          description: "Building or integrating with the feature"
        - label: "Administrators"
          description: "Managing or configuring the feature"
        - label: "Automated systems"
          description: "APIs, services, or scripts"

    - question: "What problem does this solve for them?"
      multiSelect: false
      options:
        - label: "Saves time"
          description: "Automates or speeds up a task"
        - label: "Improves accuracy"
          description: "Reduces errors or inconsistencies"
        - label: "Enables new capability"
          description: "Something not possible before"
        - label: "Simplifies workflow"
          description: "Makes existing tasks easier"

  scope:
    - question: "What's definitely in scope for the first iteration?"
      multiSelect: true
      options:
        - label: "Core functionality only"
          description: "Minimum viable feature"
        - label: "Basic error handling"
          description: "Handle common failure cases"
        - label: "Essential UI/UX"
          description: "Usable but not polished"
        - label: "Documentation"
          description: "How to use the feature"

    - question: "What's explicitly out of scope (nice-to-have later)?"
      multiSelect: true
      options:
        - label: "Advanced features"
          description: "Complex edge cases or optimizations"
        - label: "Polish and refinement"
          description: "UX improvements, visual design"
        - label: "Integrations"
          description: "Third-party services or APIs"
        - label: "Scalability"
          description: "Handle massive scale or high load"

  technical:
    - question: "Are there technical constraints or preferences?"
      multiSelect: true
      options:
        - label: "Use existing stack"
          description: "Leverage current languages/frameworks"
        - label: "New technology needed"
          description: "Requires new tools or libraries"
        - label: "Architectural patterns"
          description: "Must follow specific design patterns"
        - label: "No strong preferences"
          description: "Choose best tool for the job"

    - question: "What existing systems does this need to integrate with?"
      multiSelect: true
      options:
        - label: "Database"
          description: "Read/write data persistence"
        - label: "Authentication"
          description: "User identity and permissions"
        - label: "APIs or services"
          description: "External integrations"
        - label: "None (standalone)"
          description: "Self-contained feature"

  timeline:
    - question: "Are there any deadlines or milestones?"
      multiSelect: false
      options:
        - label: "ASAP (urgent)"
          description: "Needed immediately"
        - label: "Specific date"
          description: "Hard deadline exists"
        - label: "Flexible timeline"
          description: "No strict deadline"
        - label: "Unknown"
          description: "Need to determine"

    - question: "Is there a target date for first working version?"
      multiSelect: false
      options:
        - label: "Within a week"
          description: "Quick prototype or MVP"
        - label: "1-2 weeks"
          description: "Basic implementation"
        - label: "3-4 weeks"
          description: "More thorough development"
        - label: "Flexible"
          description: "Ready when it's ready"

  risks:
    - question: "What could go wrong? What are the biggest risks?"
      multiSelect: true
      options:
        - label: "Technical complexity"
          description: "Harder to implement than expected"
        - label: "Integration issues"
          description: "Challenges connecting to other systems"
        - label: "Performance concerns"
          description: "May not scale or be fast enough"
        - label: "Unknown unknowns"
          description: "Uncertainties in requirements or approach"

    - question: "Are there edge cases we should plan for upfront?"
      multiSelect: true
      options:
        - label: "Empty or invalid input"
          description: "Handle bad data gracefully"
        - label: "Concurrent access"
          description: "Multiple users or processes"
        - label: "Failure scenarios"
          description: "Network errors, timeouts, crashes"
        - label: "None identified yet"
          description: "Handle as discovered"

  existing:
    - question: "What existing code or systems can we leverage?"
      multiSelect: true
      options:
        - label: "Similar features"
          description: "Patterns or code to reuse"
        - label: "Libraries or frameworks"
          description: "Tools that solve part of the problem"
        - label: "Infrastructure"
          description: "Deployment, monitoring, logging"
        - label: "Start from scratch"
          description: "Build new"

    - question: "What dependencies does this have?"
      multiSelect: true
      options:
        - label: "Other features"
          description: "Requires other work to be done first"
        - label: "External services"
          description: "Third-party APIs or tools"
        - label: "Data availability"
          description: "Needs specific data sources"
        - label: "None (self-contained)"
          description: "Independent feature"

  success:
    - question: "How will we know this is successful?"
      multiSelect: true
      options:
        - label: "User feedback"
          description: "Positive reception and adoption"
        - label: "Metrics"
          description: "Usage stats, performance numbers"
        - label: "Tests pass"
          description: "Automated validation"
        - label: "Requirements met"
          description: "Delivers what was asked for"

    - question: "What are the acceptance criteria?"
      multiSelect: true
      options:
        - label: "Feature works as described"
          description: "Basic functionality complete"
        - label: "Tests validate behavior"
          description: "Automated tests pass"
        - label: "Documentation exists"
          description: "How-to guides and API docs"
        - label: "Performance acceptable"
          description: "Meets speed/resource targets"
```

**Default Category Selection by Focus:**

| Focus | Default Categories |
|-------|-------------------|
| `feat` | requirements, users, scope, success |
| `arch` | technical, risks, existing, scope |
| `api` | technical, requirements, success |
| `ux` | users, scope, success |
| `ops` | technical, risks, timeline |
| `auto` | requirements, users, technical, success |

**Acceptance Criteria:**

- ✅ All 8 categories implemented
- ✅ 2 questions per category (16 total)
- ✅ Questions use AskUserQuestion format
- ✅ Sensible defaults per focus mode

---

### Task 3: Categories Flag Implementation [1 hour]

**Goal:** Add `--categories` flag to filter question types

**Location:** `commands/workflow/brainstorm.md` - Extend argument parsing

**Implementation:**

```python
CATEGORY_MAP = {
    'req': 'requirements', 'requirements': 'requirements',
    'usr': 'users', 'users': 'users',
    'scp': 'scope', 'scope': 'scope',
    'tech': 'technical', 'technical': 'technical',
    'time': 'timeline', 'timeline': 'timeline',
    'risk': 'risks', 'risks': 'risks',
    'exist': 'existing', 'existing': 'existing',
    'ok': 'success', 'success': 'success',
    'all': 'all'
}

def parse_categories(args):
    """Parse --categories or -C flag.

    Examples:
        --categories req,tech,success
        -C req,usr,scp
        --categories all

    Returns:
        list: Category names or None (all categories)
    """
    # Find --categories or -C in args
    for i, arg in enumerate(args):
        if arg in ['--categories', '-C']:
            if i + 1 < len(args):
                cat_str = args[i + 1]
                if cat_str == 'all':
                    return None  # All categories

                # Parse comma-separated list
                cats = [c.strip() for c in cat_str.split(',')]
                # Normalize shortcuts
                return [CATEGORY_MAP.get(c, c) for c in cats]

    return None  # Default: all categories

def select_questions(depth, question_count, categories, focus):
    """Select questions based on user preferences.

    Args:
        depth: Depth mode (quick, default, deep, max)
        question_count: Number of questions (or None for default)
        categories: List of category names (or None for all)
        focus: Focus area (feat, arch, api, etc.)

    Returns:
        list: Selected questions in order
    """
    # Get question count
    if question_count is None:
        count = get_default_question_count(depth)
    else:
        count = question_count

    # Get categories
    if categories is None:
        # Use focus-based defaults
        cats = get_default_categories_for_focus(focus)
    else:
        cats = categories

    # Gather questions from selected categories
    available = []
    for cat in cats:
        if cat in question_bank:
            available.extend(question_bank[cat])

    # Prioritize and select
    if count >= len(available):
        return available
    else:
        return prioritize_questions(available, count)

def prioritize_questions(questions, count):
    """Select most important questions when count < available.

    Priority order: requirements > users > scope > technical > success
    """
    priority_order = [
        'requirements', 'users', 'scope', 'technical',
        'success', 'risks', 'timeline', 'existing'
    ]

    selected = []
    for cat in priority_order:
        if len(selected) >= count:
            break
        cat_questions = [q for q in questions if q['category'] == cat]
        # Take 1-2 from each category based on count
        take = max(1, count // len(priority_order))
        selected.extend(cat_questions[:take])

    return selected[:count]
```

**Usage Examples:**

```bash
/brainstorm d:6 "auth" -C req,tech,success
/brainstorm m:10 f "api" --categories req,usr,tech,exist
/brainstorm d:4 "caching" -C tech,risk
```

**Acceptance Criteria:**

- ✅ `--categories` and `-C` both work
- ✅ Comma-separated list parsing
- ✅ Shorthand expansion (req → requirements)
- ✅ `all` selects all categories
- ✅ Prioritization when count < available

---

### Task 4: Unlimited Questions + Milestone Prompts [3 hours]

**Goal:** Support unlimited question counts with continuation prompts every 8 questions

**Location:** `commands/workflow/brainstorm.md` - Step 1.5: "Ask More?" Feature

**Implementation:**

```python
def ask_questions_with_milestones(selected_questions, total_count):
    """Ask questions with milestone prompts.

    Args:
        selected_questions: List of questions to ask
        total_count: Total questions requested (or None for unlimited)

    Flow:
        - Ask questions in batches of 8
        - After each batch: continuation prompt
        - User can: proceed, add more, or keep going
    """
    answers = []
    asked = 0
    milestone = 8  # Prompt every 8 questions

    while asked < len(selected_questions):
        # Ask next batch (up to milestone)
        batch_end = min(asked + milestone, len(selected_questions))
        batch = selected_questions[asked:batch_end]

        # Ask questions in batch
        for q in batch:
            answer = AskUserQuestion([q])
            answers.append(answer)
            asked += 1

        # Check if we've reached the requested count
        if total_count is not None and asked >= total_count:
            break

        # Check if more questions available
        if asked < len(selected_questions):
            # Continuation prompt
            continue_choice = ask_continuation_prompt(asked, total_count)

            if continue_choice == 'done':
                break
            elif continue_choice == 'add_4':
                # Add 4 more questions
                continue
            elif continue_choice == 'add_8':
                # Add 8 more questions
                continue
            elif continue_choice == 'keep_going':
                # Continue until user says stop
                total_count = None  # Unlimited
                continue

    return answers

def ask_continuation_prompt(questions_asked, total_count):
    """Show continuation prompt at milestone.

    Args:
        questions_asked: Number of questions asked so far
        total_count: Total requested (or None)

    Returns:
        str: User choice (done, add_4, add_8, keep_going)
    """
    remaining = None
    if total_count:
        remaining = total_count - questions_asked

    summary = f"You've answered {questions_asked} questions. Good context so far!"

    options = [
        {
            "label": "Done - Start brainstorming (Recommended)",
            "description": "Proceed with current context"
        },
        {
            "label": "4 more questions",
            "description": "Add a few more details"
        },
        {
            "label": "8 more questions",
            "description": "Thorough exploration"
        },
        {
            "label": "Keep going until I say stop",
            "description": "I'll tell you when I'm done"
        }
    ]

    if remaining and remaining <= 4:
        # Close to end, adjust options
        options[1]["label"] = f"{remaining} more questions (finish)"
        options[2] = None  # Remove "8 more"

    result = AskUserQuestion({
        "question": "Continue gathering context or start brainstorming?",
        "header": "Continue",
        "multiSelect": false,
        "options": [o for o in options if o]
    })

    if "Done" in result:
        return 'done'
    elif "4 more" in result:
        return 'add_4'
    elif "8 more" in result or "finish" in result:
        return 'add_8'
    else:
        return 'keep_going'
```

**Milestone Prompt Examples:**

After 8 questions:

```
You've answered 8 questions. Good context so far!

Continue gathering context or start brainstorming?
○ Done - Start brainstorming (Recommended)
○ 4 more questions
○ 8 more questions
○ Keep going until I say stop
```

After 16 questions (unlimited mode):

```
You've answered 16 questions. Comprehensive context!

Continue gathering context or start brainstorming?
○ Done - Start brainstorming (Recommended)
○ 4 more questions
○ Keep going until I say stop
```

**Acceptance Criteria:**

- ✅ Prompts appear every 8 questions
- ✅ User can add 4, 8, or unlimited
- ✅ "Keep going" mode asks after every 4
- ✅ Works with any initial count (d:5, d:12, d:20)

---

### Task 5: Documentation Updates [1 hour]

**Goal:** Update brainstorm.md and CLAUDE.md with Phase 1 features

**Files to Update:**

1. **`commands/workflow/brainstorm.md`**
   - Add colon notation syntax to arguments section
   - Document question bank (8 categories)
   - Document `--categories` flag
   - Add examples showing new syntax
   - Update version history (v2.4.0)

2. **`CLAUDE.md`**
   - Add Phase 1 features to brainstorm command section
   - Include example usage
   - Note Phase 2/3 as future enhancements

**Documentation Template:**

```markdown
### v2.4.0 - Question Control (Phase 1)

**New Features:**
- ✅ Colon notation: `d:5`, `m:12`, `q:3` for custom question counts
- ✅ Unlimited questions with milestone prompts
- ✅ Categories flag: `--categories req,tech,success`
- ✅ Question bank: 8 categories × 2 questions each

**Examples:**
```bash
# Custom question count
/brainstorm d:5 "auth system"

# Unlimited with categories
/brainstorm d:12 -C req,tech,success "api design"

# Max mode with focused questions
/brainstorm m:20 f s "payment system" -C req,tech,risk
```

**Backward Compatible:**

- All existing syntax still works
- `d` = `d:8` (deep with default 8 questions)
- `m` = `m:8` (max with default 8 questions)

```

**Acceptance Criteria:**
- ✅ brainstorm.md updated with syntax
- ✅ Examples show Phase 1 features
- ✅ CLAUDE.md includes quick reference
- ✅ Version history updated

---

### Task 6: Tests (Unit + Integration) [2 hours]

**Goal:** Comprehensive test coverage for Phase 1

**Test Files:**

1. **`tests/test_brainstorm_phase1.py`** - Unit tests
2. **`tests/test_integration_brainstorm_phase1.py`** - Integration tests

**Unit Test Coverage:**

```python
class TestColonNotationParsing:
    """Test depth:count syntax parsing."""

    def test_parse_standard_depth_with_count(self):
        """d:5 should parse as (deep, 5)."""
        result = parse_depth_with_count('d:5')
        assert result == ('deep', 5)

    def test_parse_max_with_count(self):
        """m:12 should parse as (max, 12)."""
        result = parse_depth_with_count('m:12')
        assert result == ('max', 12)

    def test_parse_quick_with_zero(self):
        """q:0 should parse as (quick, 0)."""
        result = parse_depth_with_count('q:0')
        assert result == ('quick', 0)

    def test_parse_depth_without_count(self):
        """d should parse as (deep, None)."""
        result = parse_depth_with_count('d')
        assert result == ('deep', None)

    def test_parse_invalid_count(self):
        """d:abc should return (deep, 'invalid')."""
        result = parse_depth_with_count('d:abc')
        assert result == ('deep', 'invalid')

    def test_parse_negative_count(self):
        """d:-5 should return (deep, 'invalid')."""
        result = parse_depth_with_count('d:-5')
        assert result == ('deep', 'invalid')

class TestQuestionBank:
    """Test question bank structure."""

    def test_all_categories_exist(self):
        """All 8 categories should be present."""
        expected = ['requirements', 'users', 'scope', 'technical',
                   'timeline', 'risks', 'existing', 'success']
        assert set(question_bank.keys()) == set(expected)

    def test_each_category_has_two_questions(self):
        """Each category should have exactly 2 questions."""
        for cat, questions in question_bank.items():
            assert len(questions) == 2, f"{cat} should have 2 questions"

    def test_questions_have_required_fields(self):
        """Each question should have question, options, multiSelect."""
        for cat, questions in question_bank.items():
            for q in questions:
                assert 'question' in q
                assert 'options' in q
                assert 'multiSelect' in q
                assert len(q['options']) >= 2

class TestCategoriesFlag:
    """Test --categories flag parsing."""

    def test_parse_single_category(self):
        """--categories req should parse correctly."""
        result = parse_categories(['--categories', 'req'])
        assert result == ['requirements']

    def test_parse_multiple_categories(self):
        """--categories req,tech,success should parse correctly."""
        result = parse_categories(['--categories', 'req,tech,success'])
        assert result == ['requirements', 'technical', 'success']

    def test_parse_shorthand_flag(self):
        """-C req,usr should parse correctly."""
        result = parse_categories(['-C', 'req,usr'])
        assert result == ['requirements', 'users']

    def test_parse_all_categories(self):
        """--categories all should return None."""
        result = parse_categories(['--categories', 'all'])
        assert result is None

    def test_no_categories_flag(self):
        """Missing flag should return None."""
        result = parse_categories(['d:5', 'auth'])
        assert result is None

class TestQuestionSelection:
    """Test question selection logic."""

    def test_select_fewer_questions_than_available(self):
        """Requesting 4 from 16 should prioritize correctly."""
        categories = ['requirements', 'users', 'scope', 'technical']
        questions = select_questions('deep', 4, categories, 'feat')
        assert len(questions) == 4
        # Should include requirements first
        assert questions[0]['category'] == 'requirements'

    def test_select_more_questions_than_available(self):
        """Requesting 10 from 4 should return all 4."""
        categories = ['requirements', 'users']
        questions = select_questions('deep', 10, categories, 'feat')
        assert len(questions) == 4  # Only 2 cats × 2 questions

    def test_select_default_count_for_depth(self):
        """None count should use depth default."""
        questions = select_questions('deep', None, None, 'feat')
        assert len(questions) == 8

class TestMilestonePrompts:
    """Test unlimited question milestone prompts."""

    def test_milestone_at_8_questions(self):
        """Should prompt after 8 questions."""
        # Mock AskUserQuestion calls
        with mock_ask_user_question():
            ask_questions_with_milestones(range(16), 16)
            # Should have prompted at question 8
            assert prompt_called_at == [8]

    def test_unlimited_mode_prompts_every_8(self):
        """Unlimited should prompt every 8."""
        with mock_ask_user_question():
            ask_questions_with_milestones(range(24), None)
            # Should prompt at 8, 16, 24
            assert prompt_called_at == [8, 16, 24]

    def test_stop_at_requested_count(self):
        """Should stop exactly at requested count."""
        questions = ask_questions_with_milestones(range(20), 12)
        assert len(questions) == 12
```

**Integration Test Coverage:**

```python
class TestBrainstormPhase1Integration:
    """End-to-end tests for Phase 1 features."""

    def test_custom_count_with_categories(self):
        """d:6 -C req,tech should work end-to-end."""
        result = run_brainstorm('d:6 -C req,tech "auth system"')
        assert result['questions_asked'] == 6
        assert set(result['categories_used']) == {'requirements', 'technical'}

    def test_unlimited_with_continuation(self):
        """d:20 should prompt at milestones."""
        result = run_brainstorm('d:20 "microservices"')
        assert result['milestones_hit'] == [8, 16]
        assert result['questions_asked'] == 20

    def test_backward_compatibility(self):
        """d should still mean d:8."""
        result = run_brainstorm('d "api design"')
        assert result['questions_asked'] == 8

    def test_invalid_syntax_recovery(self):
        """d:abc should trigger validation prompt."""
        result = run_brainstorm('d:abc "notifications"')
        assert result['validation_prompted'] == True
        assert result['recovered'] == True
```

**Acceptance Criteria:**

- ✅ All unit tests pass (100% coverage)
- ✅ Integration tests validate end-to-end
- ✅ Edge cases handled (invalid syntax, etc.)
- ✅ Tests run in < 5 seconds

---

## Execution Order

**Recommended sequence:**

1. **Task 2 first** (Question Bank) - Foundation for everything
2. **Task 3 second** (Categories Flag) - Simple, builds on bank
3. **Task 1 third** (Colon Notation) - Core parsing logic
4. **Task 4 fourth** (Unlimited Questions) - Most complex
5. **Task 5 fifth** (Documentation) - After implementation
6. **Task 6 last** (Tests) - Validate everything

**Why this order?**

- Question bank is the foundation
- Categories flag is simple and useful for testing
- Colon notation can use real question bank for testing
- Unlimited questions builds on everything else
- Documentation after implementation is complete
- Tests validate the entire system

---

## Testing Strategy

### Manual Testing Checklist

Before considering Phase 1 complete, test these scenarios:

- [ ] `/brainstorm d:5 "auth system"`
- [ ] `/brainstorm m:12 f s "payment api" -C req,tech,risk,success`
- [ ] `/brainstorm q:2 "caching"`
- [ ] `/brainstorm d:20 "microservices"` (test milestones)
- [ ] `/brainstorm d:abc "test"` (invalid syntax)
- [ ] `/brainstorm d "backward compat"`
- [ ] `/brainstorm m:0 "agent only"`

### Automated Testing

```bash
# Run all Phase 1 tests
python3 tests/test_brainstorm_phase1.py
python3 tests/test_integration_brainstorm_phase1.py

# Check coverage
pytest --cov=commands/workflow tests/test_brainstorm_phase1.py
```

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Test coverage | > 95% |
| Test execution time | < 5 seconds |
| All examples work | 100% |
| Documentation complete | 100% |
| Backward compatible | 100% |

---

## Rollback Plan

If Phase 1 causes issues:

1. **Revert PR** - `git revert <commit>`
2. **Feature flag** - Add `ENABLE_PHASE1=false` env var
3. **Hotfix** - Create `hotfix/revert-phase1` branch

**Critical bugs that require rollback:**

- Breaks existing brainstorm functionality
- Causes data loss or corruption
- Performance regression > 2x slower

---

## Post-Implementation

### Merge Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] Manual testing complete
- [ ] Examples verified
- [ ] CHANGELOG.md updated
- [ ] PR created to `dev`
- [ ] Code review requested
- [ ] CI/CD passes

### Release Process

1. Merge PR to `dev`
2. Tag release: `git tag -a v2.4.0 -m "Phase 1: Question Control"`
3. Push tag: `git push origin v2.4.0`
4. Update `CLAUDE.md` with v2.4.0 features
5. Announce in project notes

---

## Notes

**IMPORTANT:**

- This is MVP - Phase 2/3 are deferred
- Focus on core functionality, not polish
- Ship and gather feedback before Phase 2/3
- Keep implementation simple and testable

**Known Limitations (Phase 1):**

- No question style choice (always one-at-a-time)
- No saved preferences
- No custom questions
- No project templates
- No session memory

**These are intentional** - Phase 2/3 features only if users request them.
