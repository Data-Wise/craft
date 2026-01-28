# Debug Assistance

Help diagnose and fix bugs in code.

## Purpose

Systematic debugging support for:

- Error message interpretation
- Root cause analysis
- Reproducing issues
- Fixing bugs
- Preventing regressions

## Required Input

- **Error/symptom**: What's happening
- **Expected behavior**: What should happen
- **Code context**: Relevant code or function
- **Steps to reproduce**: How to trigger the issue

## Process

1. **Understand the problem**
   - Parse error messages
   - Identify symptom vs. root cause
   - Clarify expected behavior

2. **Reproduce the issue**
   - Create minimal reproducible example
   - Identify triggers and conditions
   - Document environment

3. **Diagnose**
   - Trace execution flow
   - Check inputs and outputs
   - Identify where behavior diverges

4. **Fix**
   - Propose solution
   - Explain the fix
   - Consider side effects

5. **Verify**
   - Test the fix
   - Check edge cases
   - Add regression test

## Output Format

```markdown
## Bug Analysis

### Problem Summary
[Clear description of the issue]

### Error Details
```

[Error message or unexpected output]

```

### Root Cause
[Explanation of why this is happening]

### Minimal Reproducible Example
```r
# Code that demonstrates the issue
```

### Suggested Fix

```r
# Fixed code with explanation
```

### Explanation

[Why this fix works]

### Prevention

- [ ] Add test case for this scenario
- [ ] Update documentation if behavior was unclear
- [ ] Consider related edge cases

```

## Debugging Strategies

### For R
```r
# Tracing
traceback()
debug(function_name)
browser()

# Inspection
str(object)
class(object)
attributes(object)

# Options
options(error = recover)
options(warn = 2)  # Treat warnings as errors
```

### For JavaScript/TypeScript

```javascript
// Console debugging
console.log(variable)
console.trace()
debugger;

// Error inspection
try { } catch (e) { console.error(e.stack) }
```

## MCP Integration

Uses these tools when available:

- `r_execute` - Run code snippets
- `r_inspect` - Examine objects
- `r_session` - Interactive debugging

## Common Bug Patterns

### Type Errors

- Wrong data type passed
- NULL/undefined where object expected
- Vector vs. scalar confusion

### Logic Errors

- Off-by-one errors
- Wrong comparison operator
- Missing edge case handling

### Environment Issues

- Missing dependencies
- Version conflicts
- Path problems

### Data Issues

- Unexpected NA/NULL values
- Encoding problems
- Format mismatches

## Examples

**Request**: "Help me debug this error: 'object of type closure is not subsettable'"

**Request**: "My function returns NULL instead of the expected data frame"

**Request**: "This code works in RStudio but fails in a script"

**Request**: "Help me understand why my test is failing"

## Tips

- Start with the simplest possible reproduction
- Check assumptions explicitly
- Use version control to bisect
- Read the full error message
- Check recent changes first
