# Generate Tests

Create comprehensive test cases for code.

## Purpose

Generate tests that:

- Verify correct behavior
- Cover edge cases
- Catch regressions
- Document expected behavior
- Support refactoring

## Required Input

- **Code to test**: Function(s) or module
- **Framework**: testthat, Jest, pytest, etc.
- **Coverage goals**: What scenarios to cover
- **Existing tests**: If any (to avoid duplication)

## Process

1. **Analyze the code**
   - Identify inputs and outputs
   - Find decision points
   - Note dependencies

2. **Design test cases**
   - Happy path (normal usage)
   - Edge cases
   - Error conditions
   - Boundary values

3. **Generate tests**
   - One test per behavior
   - Clear, descriptive names
   - Arrange-Act-Assert pattern

4. **Review coverage**
   - Check all paths covered
   - Identify gaps
   - Add additional tests

## Output Format

```markdown
## Test Plan for [Function/Module]

### Function Signature
```r
function_name(param1, param2, ...)
```

### Test Categories

#### 1. Basic Functionality

- [ ] Returns expected output for typical input
- [ ] Handles default parameters correctly

#### 2. Edge Cases

- [ ] Empty input
- [ ] Single element
- [ ] Maximum size input

#### 3. Error Handling

- [ ] Invalid input type
- [ ] Missing required parameters
- [ ] Out of range values

#### 4. Special Values

- [ ] NA/NULL handling
- [ ] Infinite values
- [ ] Zero values

### Generated Tests

```r
# test-function_name.R

test_that("function_name returns expected output for typical input", {
  result <- function_name(input)
  expect_equal(result, expected)
})

test_that("function_name handles empty input", {
  expect_error(function_name(c()))
  # or
  expect_equal(function_name(c()), expected_empty)
})

test_that("function_name validates input types", {
  expect_error(function_name("not_a_number"), "must be numeric")
})
```

```

## Test Frameworks

### R (testthat)
```r
library(testthat)

test_that("description of behavior", {
  # Arrange
  input <- create_test_data()

  # Act
  result <- function_under_test(input)

  # Assert
  expect_equal(result, expected)
  expect_true(condition)
  expect_error(code, "message")
})
```

### JavaScript (Jest)

```javascript
describe('functionName', () => {
  it('should return expected output', () => {
    expect(functionName(input)).toBe(expected);
  });
});
```

## MCP Integration

Uses these tools when available:

- `r_test` - Run testthat tests
- `r_coverage` - Check test coverage
- `r_execute` - Verify test behavior

## Test Types

### Unit Tests

- Test single functions in isolation
- Mock dependencies
- Fast execution

### Integration Tests

- Test multiple components together
- Real dependencies
- Slower but more realistic

### Snapshot Tests

- Capture output and compare
- Good for complex outputs
- Detect unexpected changes

## Examples

**Request**: "Generate tests for my calculate_effect_size function"

**Request**: "Create edge case tests for data validation"

**Request**: "Write tests to achieve 90% coverage on this module"

**Request**: "Add regression test for the bug I just fixed"

## Tips

- Test behavior, not implementation
- Use descriptive test names
- One assertion per test (when practical)
- Keep tests independent
- Don't test external libraries
