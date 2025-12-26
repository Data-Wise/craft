# Refactoring Guidance

Improve code structure without changing behavior.

## Purpose

Support refactoring efforts:
- Improve code readability
- Reduce duplication (DRY)
- Enhance maintainability
- Optimize performance
- Prepare for new features

## Required Input

- **Code to refactor**: The current implementation
- **Goals**: What you want to improve
- **Constraints**: What must stay the same
- **Context**: How code is used

## Process

1. **Understand current code**
   - Document current behavior
   - Identify dependencies
   - Note existing tests

2. **Identify improvements**
   - Code smells
   - Duplication
   - Complex logic
   - Naming issues

3. **Plan refactoring**
   - Small, incremental changes
   - Maintain test coverage
   - Preserve API if needed

4. **Execute safely**
   - One change at a time
   - Test after each step
   - Use version control

5. **Verify**
   - All tests pass
   - Behavior unchanged
   - Performance acceptable

## Output Format

```markdown
## Refactoring Plan

### Current State
[Description of existing code]

### Issues Identified
1. [Issue 1]: [Description]
2. [Issue 2]: [Description]

### Proposed Changes

#### Change 1: [Name]
**Before:**
```r
[Original code]
```

**After:**
```r
[Refactored code]
```

**Rationale:** [Why this improves the code]

#### Change 2: [Name]
[Same structure]

### Implementation Order
1. [First change - safest]
2. [Second change]
3. [Continue...]

### Risk Assessment
- **Breaking changes**: [None/List]
- **Performance impact**: [None/Describe]
- **Test updates needed**: [Yes/No]
```

## Common Refactorings

### Extract Function
```r
# Before: Long function with repeated logic
process_data <- function(data) {
  # 50 lines of code
}

# After: Smaller, focused functions
validate_input <- function(data) { }
transform_data <- function(data) { }
process_data <- function(data) {
  data <- validate_input(data)
  transform_data(data)
}
```

### Rename for Clarity
```r
# Before
x <- calc(d, n)

# After
mean_score <- calculate_mean(data, sample_size)
```

### Simplify Conditionals
```r
# Before
if (x == TRUE) { } else if (x == FALSE) { }

# After
if (x) { } else { }
```

### Remove Duplication
```r
# Before: Same code in multiple places
# After: Single function called from multiple places
```

## Code Smells to Watch

- **Long functions**: > 30 lines
- **Deep nesting**: > 3 levels
- **Long parameter lists**: > 4 parameters
- **Duplicated code**: Copy-paste patterns
- **Magic numbers**: Unexplained constants
- **Dead code**: Unused functions/variables

## Examples

**Request**: "Refactor this 100-line function into smaller pieces"

**Request**: "Help me reduce duplication in these three similar functions"

**Request**: "Improve the readability of this complex conditional"

**Request**: "Rename variables in this code to be more descriptive"

## Tips

- Refactor when tests are green
- Make one change at a time
- Run tests frequently
- Don't refactor and add features simultaneously
- Document breaking changes
