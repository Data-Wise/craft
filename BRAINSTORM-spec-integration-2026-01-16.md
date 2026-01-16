# Brainstorm: Spec Standards Integration into Craft Commands

**Date:** 2026-01-16
**Mode:** Deep Feature Brainstorm
**Context:** 12 expert questions answered
**From Plan:** `/Users/dt/.claude/plans/purring-prancing-mango.md`
**Related Spec:** `docs/specs/SPEC-help-template-menu-2026-01-16.md`

---

## Problem Statement

We've created a comprehensive spec template for the help file system, but currently:
- No standardized way to create specs from brainstorms
- Specs can be inconsistent (missing sections, incomplete content)
- No integration between spec creation and implementation commands
- Website doesn't publish or link to specifications
- No validation to ensure spec quality

**Result:** Specs are ad-hoc, inconsistent, and disconnected from the development workflow.

---

## Solution Overview

Integrate spec standards deeply into craft commands with:
1. **Consistency:** All specs follow the same template structure
2. **Command integration:** Brainstorm creates, /craft:do implements, site/docs publish
3. **Validation:** Content validation on commit via pre-commit hook
4. **Website integration:** Generate help from specs, publish specs to site, validate completeness
5. **Smart routing:** /craft:do searches specs by keyword and uses them for implementation

---

## User Answers Summary (12 Total)

### Foundation (Q1-4)
1. **Goal**: Consistency across all specs
2. **Command integration**: Review to add website commands too
3. **Template storage**: Embedded in brainstorm command
4. **Validation level**: Content validation

### Website Integration (Q5-8)
5. **Website commands**: All of the above (generate help, validate, publish)
6. **Spec publication**: Website specs section
7. **Validation trigger**: On commit (pre-commit hook)
8. **Error handling**: Block and prompt to fix

### Implementation Details (Q9-12)
9. **Smart routing**: Search docs/specs/ by keyword
10. **Help ↔ Spec link**: Help pages link to specs
11. **Validator design**: Integrated into commands
12. **Template evolution**: Versioned templates

---

## Detailed Solution Design

### Part 1: Spec Template Embedding

**Where:** `commands/workflow/brainstorm.md`

**What to add:**

````markdown
## Spec Template (v1.0.0)

When `save` action is used, populate this template:

```markdown
---
version: 1.0.0
status: draft
created: {date}
from_brainstorm: {brainstorm_file}
---

# SPEC: {Topic}

**Status:** Draft
**Date:** {date}
**Priority:** {priority}
**Target:** {version}
**Effort:** {estimate}

---

## Problem Statement

{From brainstorm - problem being solved}

---

## Solution Overview

{From brainstorm - high-level approach}

**Key Principles:**
{From brainstorm - design principles}

---

## Scope

### In Scope
{From brainstorm - what's included}

### Out of Scope
{From brainstorm - what's excluded}

---

## Design

{From brainstorm - technical design details}

---

## Implementation Phases

{From brainstorm - phased rollout plan}

---

## Files Created/Modified

### New Files
{From brainstorm - files to create}

### Modified Files
{From brainstorm - files to change}

---

## Success Metrics

{From brainstorm - how to measure success}

---

## Risk Assessment

{From brainstorm - risks and mitigations}

---

## Dependencies

{From brainstorm - prerequisites}

---

## Open Questions

{From brainstorm - unresolved items}

---

## Next Steps

### Immediate
{From brainstorm - first actions}

### Week 2+
{From brainstorm - follow-up work}

---

**Specification Author:** Claude Sonnet 4.5
**Brainstorm Mode:** {mode}
**Plan File:** {plan_path}
```
````

**Validation Rules (Content Validation Level):**

| Section | Validation |
|---------|------------|
| Problem Statement | Must have 2+ sentences (not just "N/A") |
| Solution Overview | Must have 2+ sentences |
| Scope (In/Out) | At least one item in each |
| Success Metrics | At least one metric |
| All other sections | Can be "N/A - [reason]" |

---

### Part 2: Command Modifications

#### 2.1 /craft:workflow:brainstorm

**File:** `commands/workflow/brainstorm.md`

**Changes:**

1. **Add spec template embedding** (see Part 1)

2. **Enhance spec capture logic:**
```python
def capture_spec(brainstorm_output, user_answers):
    """
    Capture brainstorm as formal specification.

    Args:
        brainstorm_output: The generated brainstorm content
        user_answers: Dictionary of user responses from questions

    Returns:
        spec_path: Path to generated SPEC-{topic}-{date}.md
    """
    # Load embedded template (v1.0.0)
    template = load_embedded_template()

    # Populate template from brainstorm
    spec_content = populate_template(
        template=template,
        brainstorm=brainstorm_output,
        answers=user_answers
    )

    # Validate content before saving
    validation_result = validate_spec_content(spec_content)

    if not validation_result.is_valid:
        # Block and prompt to fix
        show_validation_errors(validation_result.errors)
        return prompt_to_fix_or_skip()

    # Save to docs/specs/
    spec_path = f"docs/specs/SPEC-{topic}-{date}.md"
    write_file(spec_path, spec_content)

    # Show spec capture report
    show_spec_capture_report(spec_path, validation_result)

    return spec_path
```

3. **Update v2.3.1 spec capture output:**
```markdown
┌─────────────────────────────────────────────────────────────┐
│ 📋 SPEC CAPTURED (v1.0.0)                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Spec: SPEC-spec-integration-2026-01-16.md                   │
│ Template Version: 1.0.0                                     │
│ From: BRAINSTORM-spec-integration-2026-01-16.md             │
│                                                             │
│ Content Validation:                                         │
│   ✓ Problem Statement (42 words)                            │
│   ✓ Solution Overview (38 words)                            │
│   ✓ Scope (5 in, 3 out)                                     │
│   ✓ Success Metrics (4 metrics)                             │
│   ⚠ Open Questions (0 items - consider adding)              │
│                                                             │
│ Status: draft                                               │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ 🔗 Next steps:                                              │
│    /craft:do "implement spec integration"  ← will find spec │
│    /craft:site:check                       ← validate site  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

#### 2.2 /craft:do (Smart Routing)

**File:** `commands/do.md`

**Changes:**

1. **Add spec search logic:**
```python
def find_relevant_spec(user_request):
    """
    Search docs/specs/ for relevant specification.

    Args:
        user_request: User's task description

    Returns:
        spec_path: Path to best matching spec, or None
    """
    # Parse user request for keywords
    keywords = extract_keywords(user_request)

    # Search all SPEC-*.md files
    specs = glob("docs/specs/SPEC-*.md")

    # Score each spec by keyword match
    scores = []
    for spec_path in specs:
        spec_content = read_file(spec_path)
        score = calculate_similarity(keywords, spec_content)
        scores.append((score, spec_path))

    # Return best match if score > 0.6
    best_score, best_spec = max(scores, default=(0, None))

    if best_score > 0.6:
        return best_spec
    else:
        return None
```

2. **Integrate spec into routing decision:**
```python
# In do.md routing logic
def route_task(user_request):
    # Check for relevant spec
    spec_path = find_relevant_spec(user_request)

    if spec_path:
        spec_content = read_file(spec_path)
        context = f"Spec found: {spec_path}\n\n{spec_content}"

        # Pass spec to appropriate agent/command
        return route_with_spec_context(user_request, context)
    else:
        # Normal routing without spec
        return route_normal(user_request)
```

3. **Update do.md output:**
```markdown
┌─────────────────────────────────────────────────────────────┐
│ 🎯 CRAFT:DO - Smart Routing                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Task: "implement spec integration"                          │
│                                                             │
│ 📋 Found specification:                                     │
│    docs/specs/SPEC-spec-integration-2026-01-16.md           │
│    Match score: 0.87 (high confidence)                      │
│                                                             │
│ 🤖 Routing to: backend-development:backend-architect        │
│    Using spec as implementation guide                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

#### 2.3 /craft:check

**File:** `commands/check.md`

**Changes:**

1. **Add spec validation check:**
```python
def check_specs():
    """
    Validate all specs in docs/specs/ directory.

    Returns:
        validation_report: Summary of spec validation
    """
    specs = glob("docs/specs/SPEC-*.md")
    results = []

    for spec_path in specs:
        spec_content = read_file(spec_path)
        validation = validate_spec_content(spec_content)
        results.append({
            'path': spec_path,
            'valid': validation.is_valid,
            'errors': validation.errors
        })

    return generate_validation_report(results)
```

2. **Integrate into check command:**
```python
# In check.md
def run_checks():
    checks = [
        check_git_status(),
        check_tests(),
        check_linting(),
        check_specs(),  # NEW: Spec validation
    ]

    return aggregate_results(checks)
```

3. **Update check output:**
```markdown
┌─────────────────────────────────────────────────────────────┐
│ ✅ /craft:check - Pre-flight Validation                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Git Status:          ✓ Clean                                │
│ Tests:               ✓ 30/30 passing                        │
│ Code Lint:           ✓ No issues                            │
│ Specifications:      ⚠ 1 issue                              │
│                                                             │
│ Spec Issues:                                                │
│   SPEC-auth-2026-01-15.md:                                  │
│   ⚠ Problem Statement too brief (12 words, need 20+)        │
│                                                             │
│ Fix: Edit spec or run /craft:workflow:brainstorm to recreate│
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

#### 2.4 /craft:site:check

**File:** `commands/site/check.md`

**Changes:**

1. **Add spec completeness validation:**
```python
def validate_specs_for_site():
    """
    Validate specs before site deployment.

    Checks:
    - All specs have required sections
    - Spec content meets minimum quality
    - Spec version is current
    - No broken links in specs

    Returns:
        validation_report: Deployment readiness
    """
    specs = glob("docs/specs/SPEC-*.md")
    issues = []

    for spec_path in specs:
        # Load spec
        spec = parse_spec(spec_path)

        # Check template version
        if spec.version != CURRENT_TEMPLATE_VERSION:
            issues.append(f"{spec_path}: Outdated template (v{spec.version}, current v{CURRENT_TEMPLATE_VERSION})")

        # Validate content
        validation = validate_spec_content(spec.content)
        if not validation.is_valid:
            issues.extend(validation.errors)

        # Check for broken links
        broken_links = find_broken_links(spec.content)
        if broken_links:
            issues.extend(broken_links)

    return issues
```

2. **Integrate into site:check:**
```python
# In site/check.md
def run_site_checks():
    checks = [
        validate_broken_links(),
        validate_structure(),
        validate_build(),
        validate_specs_for_site(),  # NEW: Spec validation
    ]

    return aggregate_results(checks)
```

---

#### 2.5 /craft:docs:update

**File:** `commands/docs/update.md`

**Changes:**

1. **Add spec-to-help generation:**
```python
def generate_help_from_spec(spec_path):
    """
    Generate help page from specification.

    Args:
        spec_path: Path to SPEC-*.md file

    Returns:
        help_path: Path to generated help page
    """
    # Parse spec
    spec = parse_spec(spec_path)

    # Extract help-relevant content
    help_content = f"""
# {spec.title}

> **TL;DR** (30 seconds)
> - **What:** {spec.solution_overview.first_sentence}
> - **Why:** {spec.problem_statement.first_sentence}
> - **Status:** {spec.status}
> - **Target:** {spec.target}

## Overview

{spec.solution_overview}

## Scope

{spec.scope}

## Implementation

See the full specification for detailed implementation guidance:

**[View Full Specification](../../specs/{spec.filename})**

## Next Steps

{spec.next_steps}

## See Also

- [Related Command](../command.md)
- [Related Workflow](../../workflows/workflow.md)
"""

    # Determine help file path
    help_path = f"docs/help/{spec.category}/{spec.topic}.md"

    # Write help file
    write_file(help_path, help_content)

    return help_path
```

2. **Add docs:update task:**
```bash
# New task: generate-help-from-specs
/craft:docs:update generate-help-from-specs
```

---

#### 2.6 /craft:site:update

**File:** `commands/site/update.md`

**Changes:**

1. **Add specs to navigation:**
```python
def update_navigation_with_specs():
    """
    Add Specifications section to mkdocs.yml.
    """
    mkdocs_yml = read_file("mkdocs.yml")

    # Find insertion point (after Workflows)
    nav_section = """
  - Specifications:
    - Overview: specs/index.md
    - By Category:
      - Feature Specs: specs/features.md
      - Architecture Specs: specs/architecture.md
      - API Specs: specs/api.md
"""

    # Insert into nav
    updated_mkdocs = insert_after(
        mkdocs_yml,
        search="- Workflows:",
        insert=nav_section
    )

    write_file("mkdocs.yml", updated_mkdocs)
```

2. **Create spec index pages:**
```python
def generate_spec_index():
    """
    Generate docs/specs/index.md listing all specs.
    """
    specs = glob("docs/specs/SPEC-*.md")

    # Group by category
    by_category = group_specs_by_category(specs)

    # Generate index
    index_content = """
# Specifications

> **Formal specifications** for craft features, architecture, and implementation plans.

## By Category

"""

    for category, specs_list in by_category.items():
        index_content += f"\n### {category}\n\n"
        for spec in specs_list:
            index_content += f"- [{spec.title}]({spec.filename}) - {spec.status}\n"

    write_file("docs/specs/index.md", index_content)
```

---

### Part 3: Pre-commit Hook Integration

**File:** `commands/git/init.md` (modify existing hook)

**Add spec validation to pre-commit hook:**

```bash
#!/bin/bash
# .git/hooks/pre-commit (append to existing)

# Spec validation (only if specs changed)
STAGED_SPECS=$(git diff --cached --name-only --diff-filter=ACM | grep '^docs/specs/SPEC.*\.md$')

if [ -n "$STAGED_SPECS" ]; then
  echo "📋 Validating specifications..."

  for spec_file in $STAGED_SPECS; do
    # Validate spec content
    # (This would call Python validator or inline bash check)

    # Check for required sections
    REQUIRED_SECTIONS=(
      "## Problem Statement"
      "## Solution Overview"
      "## Scope"
      "## Success Metrics"
    )

    for section in "${REQUIRED_SECTIONS[@]}"; do
      if ! grep -q "^$section" "$spec_file"; then
        echo "❌ Missing section in $spec_file: $section"
        echo ""
        echo "Fix: Add missing section or run /craft:workflow:brainstorm to regenerate"
        exit 1
      fi
    done

    # Validate Problem Statement length
    problem_lines=$(sed -n '/^## Problem Statement/,/^##/p' "$spec_file" | wc -l)
    if [ "$problem_lines" -lt 3 ]; then
      echo "❌ Problem Statement too brief in $spec_file"
      echo "   Expected: 2+ sentences (20+ words)"
      echo ""
      echo "Fix: Expand Problem Statement section"
      exit 1
    fi
  done

  echo "✅ All specs valid"
fi
```

---

### Part 4: Website Changes

#### 4.1 Add Specifications Section to mkdocs.yml

**File:** `mkdocs.yml`

**Before:**
```yaml
nav:
  - Workflows:
    - Pre-commit Workflow: workflows/pre-commit-workflow.md
  - Architecture & Reference:
    - Architecture Overview: architecture.md
```

**After:**
```yaml
nav:
  - Workflows:
    - Pre-commit Workflow: workflows/pre-commit-workflow.md

  - Specifications:
    - Overview: specs/index.md
    - Feature Specs: specs/features.md
    - Architecture Specs: specs/architecture.md
    - API Specs: specs/api.md

  - Architecture & Reference:
    - Architecture Overview: architecture.md
```

---

#### 4.2 Create Spec Index Pages

**File:** `docs/specs/index.md` (NEW)

```markdown
# Specifications

> **Formal specifications** for craft features, architecture, and implementation plans.

Specifications are created from brainstorm sessions and serve as the single source of truth for feature implementation.

## What's in a Spec?

Each specification includes:
- **Problem Statement** - What are we solving?
- **Solution Overview** - High-level approach
- **Scope** - What's in/out
- **Implementation Phases** - Rollout plan
- **Success Metrics** - How to measure success
- **Risk Assessment** - Known challenges

## Browse by Category

### Feature Specifications

Features in development or completed:

- [Help File Template & Menu Design](SPEC-help-template-menu-2026-01-16.md) - Draft
- [Dry-run Support](SPEC-dry-run-2026-01-15.md) - Implemented

[See all feature specs →](features.md)

### Architecture Specifications

System design and architecture decisions:

- [Agent Orchestration v2](SPEC-orchestrator-v2-2025-12-10.md) - Implemented

[See all architecture specs →](architecture.md)

### API Specifications

API design and integration specs:

(No API specs yet - will appear here when created)

[See all API specs →](api.md)

## Creating Specifications

Specs are generated from brainstorm sessions:

```bash
# Create spec during brainstorm
/craft:workflow:brainstorm deep feat save "new feature"

# Spec automatically saved to docs/specs/
```

## See Also

- [Brainstorm Command](../help/workflow/workflow-brainstorm.md) - Create specs
- [Implementation Workflow](../workflows/feature-workflow.md) - Use specs
```

---

#### 4.3 Category Index Pages

**File:** `docs/specs/features.md` (NEW)

```markdown
# Feature Specifications

All feature specifications, organized by status.

## Draft (In Planning)

Features currently being planned:

| Spec | Created | Priority | Description |
|------|---------|----------|-------------|
| [Help Template & Menu](SPEC-help-template-menu-2026-01-16.md) | 2026-01-16 | High | Standardized help file template |
| [Spec Integration](SPEC-spec-integration-2026-01-16.md) | 2026-01-16 | High | Integrate specs into commands |

## Approved (Ready for Implementation)

Features approved and ready to build:

(No approved specs yet)

## Implemented

Features completed and deployed:

| Spec | Implemented | Version | Description |
|------|-------------|---------|-------------|
| [Dry-run Support](SPEC-dry-run-2026-01-15.md) | 2026-01-15 | v1.20.0 | Dry-run for 27 commands |

## Deprecated

Specs that are no longer relevant:

(None yet)
```

---

### Part 5: Validation Module

**File:** `tests/validate_specs.py` (NEW)

```python
"""
Spec Validation Module

Validates specification files against template v1.0.0.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple

# Template version
CURRENT_TEMPLATE_VERSION = "1.0.0"

# Required sections (must exist)
REQUIRED_SECTIONS = [
    "# SPEC:",
    "## Problem Statement",
    "## Solution Overview",
    "## Scope",
    "## Implementation Phases",
    "## Success Metrics",
    "## Risk Assessment",
    "## Dependencies",
    "## Open Questions",
    "## Next Steps",
]

# Content validation rules
CONTENT_RULES = {
    "Problem Statement": {
        "min_words": 20,
        "description": "Must have 2+ sentences (20+ words)",
    },
    "Solution Overview": {
        "min_words": 20,
        "description": "Must have 2+ sentences",
    },
    "Scope": {
        "must_contain": ["### In Scope", "### Out of Scope"],
        "description": "Must define what's in and out of scope",
    },
    "Success Metrics": {
        "min_items": 1,
        "description": "Must have at least one metric",
    },
}


def validate_spec_file(spec_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate a single spec file.

    Args:
        spec_path: Path to SPEC-*.md file

    Returns:
        (is_valid, errors): Validation result
    """
    errors = []

    # Read spec content
    content = spec_path.read_text()

    # Check template version
    version_match = re.search(r"version:\s*(\d+\.\d+\.\d+)", content)
    if not version_match:
        errors.append("Missing template version in frontmatter")
    elif version_match.group(1) != CURRENT_TEMPLATE_VERSION:
        errors.append(f"Outdated template (v{version_match.group(1)}, current v{CURRENT_TEMPLATE_VERSION})")

    # Check required sections
    for section in REQUIRED_SECTIONS:
        if section not in content:
            errors.append(f"Missing required section: {section}")

    # Content validation
    for section_name, rules in CONTENT_RULES.items():
        section_content = extract_section(content, section_name)

        # Word count check
        if "min_words" in rules:
            word_count = len(section_content.split())
            if word_count < rules["min_words"]:
                errors.append(
                    f"{section_name}: Too brief ({word_count} words, need {rules['min_words']}+)"
                )

        # Must contain check
        if "must_contain" in rules:
            for required_text in rules["must_contain"]:
                if required_text not in section_content:
                    errors.append(f"{section_name}: Missing '{required_text}'")

        # Min items check
        if "min_items" in rules:
            items = count_list_items(section_content)
            if items < rules["min_items"]:
                errors.append(
                    f"{section_name}: Not enough items ({items}, need {rules['min_items']}+)"
                )

    is_valid = len(errors) == 0
    return (is_valid, errors)


def extract_section(content: str, section_name: str) -> str:
    """Extract content of a section from spec."""
    pattern = rf"## {re.escape(section_name)}\n\n(.*?)(?=\n##|\Z)"
    match = re.search(pattern, content, re.DOTALL)
    return match.group(1).strip() if match else ""


def count_list_items(content: str) -> int:
    """Count markdown list items in content."""
    return len(re.findall(r"^\s*[-*]", content, re.MULTILINE))


def validate_all_specs() -> Dict:
    """
    Validate all specs in docs/specs/ directory.

    Returns:
        results: Dictionary with validation results
    """
    specs_dir = Path("docs/specs")
    specs = list(specs_dir.glob("SPEC-*.md"))

    results = {
        "total": len(specs),
        "valid": 0,
        "invalid": 0,
        "errors": [],
    }

    for spec_path in specs:
        is_valid, errors = validate_spec_file(spec_path)

        if is_valid:
            results["valid"] += 1
        else:
            results["invalid"] += 1
            results["errors"].append({
                "file": spec_path.name,
                "errors": errors,
            })

    return results


def main():
    """CLI entry point."""
    import sys

    results = validate_all_specs()

    print(f"📋 Spec Validation Results")
    print(f"")
    print(f"Total specs: {results['total']}")
    print(f"Valid: {results['valid']}")
    print(f"Invalid: {results['invalid']}")
    print(f"")

    if results["invalid"] > 0:
        print("❌ Validation Errors:")
        print("")
        for error in results["errors"]:
            print(f"{error['file']}:")
            for err_msg in error["errors"]:
                print(f"  - {err_msg}")
            print("")
        sys.exit(1)
    else:
        print("✅ All specs valid!")
        sys.exit(0)


if __name__ == "__main__":
    main()
```

**Usage:**
```bash
# Standalone validation
python3 tests/validate_specs.py

# In pre-commit hook
python3 tests/validate_specs.py || exit 1

# Import in commands
from tests.validate_specs import validate_spec_file
```

---

### Part 6: Template Versioning

**File:** `docs/specs/TEMPLATE-VERSIONS.md` (NEW)

```markdown
# Spec Template Versions

Track changes to the specification template over time.

## v1.0.0 (Current - 2026-01-16)

**Initial stable template for craft specifications.**

### Required Sections
1. Problem Statement
2. Solution Overview
3. Scope (In/Out)
4. Design
5. Implementation Phases
6. Files Created/Modified
7. Success Metrics
8. Risk Assessment
9. Dependencies
10. Open Questions
11. Next Steps

### Content Validation Rules
- Problem Statement: 20+ words
- Solution Overview: 20+ words
- Scope: Must define In/Out
- Success Metrics: 1+ metric

### Frontmatter
```yaml
---
version: 1.0.0
status: draft|approved|implemented|deprecated
created: YYYY-MM-DD
from_brainstorm: BRAINSTORM-*.md
---
```

### Migration from Pre-v1.0.0 Specs

If you have specs created before versioning:

1. Add frontmatter with `version: 1.0.0`
2. Ensure all required sections exist
3. Add "N/A - [reason]" for non-applicable sections
4. Validate with `python3 tests/validate_specs.py`

---

## Future Versions

### Proposed v1.1.0

**Potential changes:**
- Add "User Stories" section
- Add "Acceptance Criteria" section
- Split "Design" into "Architecture" and "UI/UX"

**Status:** Under discussion

### Migration Strategy

When template version changes:

```bash
# Option 1: Manual migration
# Edit spec files to match new template

# Option 2: Auto-migration script (TBD)
./scripts/migrate-specs.sh --from v1.0.0 --to v1.1.0
```

---

## Backward Compatibility

**Policy:** Old template versions remain supported.

- Specs can use any template version
- Validation checks against spec's declared version
- No forced upgrades (opt-in migration)
```

---

## Quick Wins (< 30 min each)

1. ⚡ **Embed template in brainstorm command**
   - Add SPEC template to commands/workflow/brainstorm.md
   - Update capture_spec() function to use embedded template
   - Test: Run `/craft:workflow:brainstorm d f s "test"` and verify spec generated

2. ⚡ **Create validation module**
   - Copy template above to `tests/validate_specs.py`
   - Test: `python3 tests/validate_specs.py`
   - Should pass on existing specs

3. ⚡ **Add spec section to mkdocs.yml**
   - Insert Specifications nav section
   - Create `docs/specs/index.md` placeholder
   - Test: `mkdocs serve` and verify section appears

4. ⚡ **Update pre-commit hook**
   - Add spec validation to `.git/hooks/pre-commit`
   - Test: Stage a spec file and commit
   - Hook should validate before allowing commit

---

## Medium Effort (1-2 hours each)

1. 🔧 **Implement /craft:do spec search**
   - Add `find_relevant_spec()` function
   - Integrate into do.md routing logic
   - Test: `/craft:do "implement X"` finds spec for X

2. 🔧 **Add spec validation to /craft:check**
   - Create `check_specs()` function
   - Integrate into check.md output
   - Test: `/craft:check` shows spec validation results

3. 🔧 **Create spec index pages**
   - Generate `docs/specs/index.md`
   - Generate `docs/specs/features.md`
   - Generate `docs/specs/architecture.md`
   - Group specs by category

4. 🔧 **Implement help-from-spec generation**
   - Add `generate_help_from_spec()` to docs:update
   - Test: Run on one spec, verify help page created
   - Validate links between help and spec

---

## Long-term (Future sessions)

1. 🏗️ **Template version migration tool**
   - Create `scripts/migrate-specs.sh`
   - Support v1.0.0 → v1.1.0 migration
   - Bulk update all specs to new template

2. 🏗️ **Spec-driven development workflow**
   - Auto-create GitHub issues from specs
   - Link PRs to specs
   - Update spec status on implementation

3. 🏗️ **Spec analytics**
   - Track spec creation → implementation time
   - Identify incomplete specs
   - Measure spec quality over time

4. 🏗️ **Interactive spec editor**
   - TUI for creating/editing specs
   - Guided wizard for filling sections
   - Real-time validation feedback

---

## Recommended Path

**Phase 1: Foundation (Week 1)**
1. Embed template in brainstorm ← Start here
2. Create validation module
3. Update pre-commit hook

**Phase 2: Command Integration (Week 2)**
4. Implement /craft:do spec search
5. Add spec validation to /craft:check
6. Update /craft:site:check

**Phase 3: Website Integration (Week 3)**
7. Add Specifications section to mkdocs.yml
8. Create spec index pages
9. Implement help-from-spec generation

**Phase 4: Polish (Week 4)**
10. Test end-to-end workflow
11. Update documentation
12. Create template versioning guide

---

## Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Spec consistency** | 100% use template v1.0.0 | Count specs with version: 1.0.0 |
| **Validation coverage** | All new specs validated | Pre-commit hook blocks invalid specs |
| **Spec usage** | 80% of features have specs | Count specs vs features in .STATUS |
| **Help generation** | 50% of help pages link to specs | Grep for "View Full Specification" |
| **Site integration** | Specs section live on site | Check mkdocs.yml nav |

---

## Files to Create/Modify

### New Files

| File | Purpose | Lines (est) |
|------|---------|-------------|
| `tests/validate_specs.py` | Spec validation module | 150 |
| `docs/specs/index.md` | Spec index page | 80 |
| `docs/specs/features.md` | Feature specs category | 60 |
| `docs/specs/architecture.md` | Architecture specs category | 60 |
| `docs/specs/api.md` | API specs category | 60 |
| `docs/specs/TEMPLATE-VERSIONS.md` | Template version history | 100 |

**Total new:** ~510 lines across 6 files

### Modified Files

| File | Changes | Lines (est) |
|------|---------|-------------|
| `commands/workflow/brainstorm.md` | Embed template, enhance capture | +200 |
| `commands/do.md` | Add spec search logic | +50 |
| `commands/check.md` | Add spec validation | +30 |
| `commands/site/check.md` | Add spec validation | +40 |
| `commands/docs/update.md` | Add help-from-spec generation | +60 |
| `commands/site/update.md` | Add specs to navigation | +30 |
| `commands/git/init.md` | Add spec validation to hook | +40 |
| `mkdocs.yml` | Add Specifications section | +10 |

**Total modified:** ~460 lines across 8 files

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Template changes break old specs** | Medium | Medium | Version tracking + backward compat policy |
| **Validation too strict** | Low | High | Start with content validation only, not format |
| **Spec search mismatches** | Medium | Medium | Manual override: `--spec=SPEC-*.md` flag |
| **Help generation loses context** | Low | Medium | Keep specs comprehensive, help links to spec |
| **Pre-commit hook friction** | Low | Low | Allow skip with `--no-verify` flag |

---

## Open Questions

1. **Should specs be required for all features?**
   - Recommendation: Start optional, require for High/Critical priority

2. **How to handle spec updates after implementation?**
   - Recommendation: Keep specs immutable, create v2 spec if design changes

3. **Should specs be versioned (v1, v2) or timestamped?**
   - Recommendation: Timestamp in filename, version in frontmatter

4. **What about specs for bug fixes vs features?**
   - Recommendation: Specs for features only, bugs use GitHub issues

---

## Next Steps (Immediate Actions)

### This Session (Complete Brainstorm)

1. ✅ Complete deep feature brainstorming
2. ⏭️ Auto-capture as spec (because `save` was used)
3. ⏭️ Generate SPEC-spec-integration-2026-01-16.md

### Next Session (Start Implementation)

1. **Embed template** in `commands/workflow/brainstorm.md`
2. **Create validator** `tests/validate_specs.py`
3. **Test validation** on this spec and help-template spec
4. **Update pre-commit hook** to validate specs

**Start with:** Quick wins (4 items, < 2 hours total)

---

**Generated:** 2026-01-16
**Mode:** Deep Feature Brainstorm (12 expert questions)
**Plan File:** `/Users/dt/.claude/plans/purring-prancing-mango.md`
**Related Spec:** `docs/specs/SPEC-help-template-menu-2026-01-16.md`
**From Command:** `/craft:workflow:brainstorm deep feat save`
