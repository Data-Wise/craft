---
description: /refine - Prompt Optimizer
category: workflow
---

# /refine - Prompt Optimizer

Optimize vague or unclear prompts into specific, well-structured requests that get better results from Claude.

## Purpose

Help users write better prompts by:

- Analyzing clarity and specificity
- Checking project context
- Rewriting with improvements
- Explaining what changed and why
- Learning prompt engineering patterns

## Usage

- `/refine "<your prompt>"` - Optimize a specific prompt
- `/refine` - Interactive mode (will ask for prompt)

## When invoked

### Step 1: Get the Prompt

**If provided as argument:**

```
/refine "Can you help me write a function that does X?"
```

Use the provided text.

**If invoked without argument:**

```
💡 PROMPT OPTIMIZER

Paste or type the prompt you want to optimize:

(Type 'cancel' to exit)
>
```

Wait for user input.

### Step 2: Analyze Context

Before optimizing, gather context:

1. **Project type** - Check for:
   - R package (DESCRIPTION file)
   - Python (pyproject.toml, setup.py)
   - Node.js (package.json)
   - Quarto (_quarto.yml)
   - General (git repo)

2. **Project instructions** - Read if exists:
   - `CLAUDE.md` in project
   - `~/.claude/CLAUDE.md` for user preferences

3. **Recent work** - Check git log (last 3 commits) for context

4. **Coding patterns** - Infer from context:
   - Language/framework in use
   - Testing framework
   - Documentation style
   - Type hints/annotations preference

### Step 3: Analyze the Prompt

Identify issues:

- ❌ **Vague requirements** - "make it better", "fix this", "help with X"
- ❌ **No language specified** - "write a function" (which language?)
- ❌ **Question phrasing** - "Can you..." instead of directive
- ❌ **Missing quality criteria** - No mention of tests, docs, types
- ❌ **Unclear scope** - What exactly should be done?
- ❌ **No edge cases** - What should handle errors, empty input, etc.
- ❌ **Context missing** - Doesn't mention relevant constraints

### Step 4: Optimize the Prompt

Rewrite to be:

- **Specific** - Clear language, framework, requirements
- **Directive** - "Write X" not "Can you write X?"
- **Structured** - Use bullets for multi-part requests
- **Complete** - Include quality criteria (tests, docs, types)
- **Contextual** - Reference project context when relevant
- **Edge-case aware** - Mention error handling, validation

### Step 5: Display Results

```
────────────────────────────────────────────────────────────
📝 ORIGINAL PROMPT
────────────────────────────────────────────────────────────
[User's original prompt, as-is]

────────────────────────────────────────────────────────────
✨ OPTIMIZED PROMPT
────────────────────────────────────────────────────────────
[Rewritten version with improvements]

────────────────────────────────────────────────────────────
🔍 IMPROVEMENTS MADE
────────────────────────────────────────────────────────────
• [Improvement 1] - [Why it matters]
• [Improvement 2] - [Why it matters]
• [Improvement 3] - [Why it matters]

Context used:
• [Context point 1 - e.g., "Detected Python project"]
• [Context point 2 - e.g., "Found pytest in dependencies"]

────────────────────────────────────────────────────────────
🎯 NEXT STEPS
────────────────────────────────────────────────────────────

Estimated execution time: ~{duration}

1. Execute now (wait for completion) ⏳
2. Execute in background (continue working) ⭐ Recommended
3. Revise - Tell me what to change
4. Copy to clipboard

💡 TIP: Choose #2 to continue working while I execute this!

>
```

### Step 6: Handle User Choice

**If user chooses "1" or "Execute" or "yes" or "wait":**

```
✅ Executing optimized prompt now...

[Proceed to execute the optimized prompt as if user had typed it]
[Wait for completion and show results]
```

---

**If user chooses "2" or "background" or "bg":** (NEW)

```
✅ Launching background agent with optimized prompt...

🚀 Running in background. Continue your work!

Task ID: {task_id}
Estimated completion: {estimated_duration}

────────────────────────────────────────────────────────────
💡 What to do while waiting:

• Continue working on other tasks
• Check status: /workflow:task-status {task_id}
• View output when ready: /workflow:task-output {task_id}

I'll notify you when execution is complete!

────────────────────────────────────────────────────────────
📋 Optimized prompt saved to PROMPTS.md for reference
```

**Implementation:**

1. Use Task tool with `run_in_background: true`
2. Set `subagent_type: "general-purpose"`
3. Pass optimized prompt as the task
4. Store task metadata:
   - Task ID
   - Command: `/workflow:refine`
   - Original prompt: {user's original prompt}
   - Optimized prompt: {the refined version}
   - Started: {timestamp}
   - Estimated duration: {estimate}
5. Save optimized prompt to PROMPTS.md (optional log file)
6. Return immediately (don't wait)

**When task completes (automatic notification):**

```
🎉 Prompt execution complete! (task: {task_id})

Original: "{original_prompt}"
Duration: {actual_duration}

────────────────────────────────────────────────────────────
View results now?

  y / yes  - Show execution results
  later    - Review later

>
```

**If user says "y" or "yes":**

- Use TaskOutput tool to retrieve results
- Display full execution output
- Offer next steps

**If user says "later":**

```
✅ Results saved

View anytime with:
  /workflow:task-output {task_id}

Ready for next task!
```

---

**If user chooses "3" or "Revise":**

```
What would you like to change about the optimization?

Examples:
• "Make it simpler"
• "Add more about error handling"
• "Remove the testing requirement"
• "Focus on performance instead"

Your feedback:
>
```

[Wait for feedback, then regenerate optimization with their input, show new version, repeat choice prompt]

**If user chooses "4" or types "copy":**

```
✅ Copied to clipboard!

The optimized prompt is now in your clipboard.
Ready to paste anywhere:
• New Claude Code session
• claude.ai web interface
• Documentation
• Email/Slack

────────────────────────────────────────────────────────────
Clipboard contains:
────────────────────────────────────────────────────────────
[First 3 lines of optimized prompt...]
[...truncated for display]

Paste it wherever you need! ✨
```

[Use pbcopy on macOS, xclip on Linux to copy to clipboard]

**If user types "cancel" or "exit":**

```
Cancelled. No changes made.
```

## Examples

### Example 1: Vague Function Request

```
User: /refine "Can you help me write a function that does X?"

Claude:
────────────────────────────────────────────────────────────
📝 ORIGINAL PROMPT
────────────────────────────────────────────────────────────
Can you help me write a function that does X?

────────────────────────────────────────────────────────────
✨ OPTIMIZED PROMPT
────────────────────────────────────────────────────────────
Write a Python function called `do_x()` that:
- Performs action X with input validation
- Handles edge cases: None, empty string, invalid types
- Returns a dict with 'result' (Any) and 'status' (str) keys
- Includes type hints for all parameters and return value
- Add a docstring with description, args, returns, and example
- Write 3 test cases covering: normal input, edge case, error case

Use pytest for tests and follow PEP 257 docstring conventions.

────────────────────────────────────────────────────────────
🔍 IMPROVEMENTS MADE
────────────────────────────────────────────────────────────
• Specified language (Python) - Detected from pyproject.toml
• Made directive instead of question - More effective prompting
• Added function name - Clear what to create
• Included edge cases - Better code quality
• Specified return type - Clear interface
• Added quality criteria - Tests, docs, type hints
• Referenced conventions - Matches project style

Context used:
• Detected Python project (has pyproject.toml)
• Found pytest in dev dependencies
• Your code style uses type hints (inferred from existing code)

────────────────────────────────────────────────────────────
🎯 NEXT STEPS
────────────────────────────────────────────────────────────

1. Execute now ⭐ (Recommended)
2. Revise - Tell me what to change

💡 Advanced: Type 'copy' to save to clipboard

>
```

### Example 2: Generic Improvement Request

```
User: /refine "make this code better"

Claude:
────────────────────────────────────────────────────────────
📝 ORIGINAL PROMPT
────────────────────────────────────────────────────────────
make this code better

────────────────────────────────────────────────────────────
✨ OPTIMIZED PROMPT
────────────────────────────────────────────────────────────
Review and improve this R code with focus on:

1. Code quality:
   - Apply tidyverse style guide conventions
   - Improve variable naming for clarity
   - Add roxygen2 documentation

2. Performance:
   - Identify bottlenecks
   - Suggest vectorization opportunities
   - Recommend data.table if processing large datasets

3. Robustness:
   - Add input validation with checkmate
   - Handle edge cases (NA, NULL, empty vectors)
   - Improve error messages

4. Testing:
   - Suggest test cases for testthat
   - Cover normal usage and edge cases

Please show the improved code with inline comments explaining changes.

[Paste the code you want to improve after this prompt]

────────────────────────────────────────────────────────────
🔍 IMPROVEMENTS MADE
────────────────────────────────────────────────────────────
• Added specific improvement areas - Guides the review
• Specified R language and tools - Detected from DESCRIPTION
• Structured as checklist - Easy to verify all aspects
• Included style guide reference - Matches R best practices
• Added testing framework - testthat is standard for R packages
• Made it actionable - Clear what to provide next

Context used:
• Detected R package (has DESCRIPTION file)
• Found testthat in Suggests field
• Package uses tidyverse (detected from DESCRIPTION Imports)

────────────────────────────────────────────────────────────
🎯 NEXT STEPS
────────────────────────────────────────────────────────────

1. Execute now ⭐ (Recommended)
2. Revise - Tell me what to change

💡 Advanced: Type 'copy' to save to clipboard

> 2

What would you like to change about the optimization?
> Focus more on performance, less on documentation

────────────────────────────────────────────────────────────
✨ REVISED OPTIMIZED PROMPT
────────────────────────────────────────────────────────────
Review and improve this R code focusing on performance:

1. Performance optimization:
   - Profile the code to identify bottlenecks
   - Suggest vectorization opportunities
   - Consider data.table for large dataset operations
   - Recommend parallel processing with future/furrr if applicable
   - Suggest memoization for repeated calculations

2. Code quality (minimal):
   - Basic tidyverse style compliance
   - Clear variable names

3. Robustness:
   - Essential input validation only
   - Handle edge cases that affect performance

Please show the optimized code with benchmark comparisons.

[Paste the code you want to improve after this prompt]

────────────────────────────────────────────────────────────
🔍 CHANGES FROM FIRST VERSION
────────────────────────────────────────────────────────────
• Emphasized performance as primary focus
• Reduced documentation requirements
• Added benchmarking request
• Suggested parallel processing
• Kept minimal quality checks

────────────────────────────────────────────────────────────
🎯 NEXT STEPS
────────────────────────────────────────────────────────────

1. Execute now ⭐ (Recommended)
2. Revise - Tell me what to change

💡 Advanced: Type 'copy' to save to clipboard

>
```

## Context-Aware Optimization Patterns

### For R Packages

- Reference roxygen2, testthat, usethis
- Mention CRAN compliance if relevant
- Suggest tidyverse patterns
- Include pkgdown for documentation

### For Python

- Type hints (PEP 484)
- Docstrings (PEP 257)
- pytest or unittest
- Black formatting, ruff linting

### For Node.js/TypeScript

- TypeScript types
- Jest or Vitest for tests
- ESLint rules
- JSDoc comments

### For Quarto/Research

- Reproducibility focus
- Citation handling
- Figure/table formatting
- Cross-referencing

### For Documentation

- Examples over explanation
- Clear structure
- Search-friendly
- Accessibility

## Learning Mode (Optional Enhancement)

When user requests it, show **why** each change improves prompting:

```
────────────────────────────────────────────────────────────
📚 LEARNING MODE: Why These Changes Matter
────────────────────────────────────────────────────────────

Change: Made directive instead of question
Why: "Write X" is clearer than "Can you write X?"
Principle: Direct instructions produce better results

Change: Added specific edge cases
Why: Makes Claude consider failure modes upfront
Principle: Explicit constraints prevent assumptions

Change: Specified return type
Why: Defines clear interface contract
Principle: Specificity reduces ambiguity

[... more explanations]

💡 Tip: These patterns apply to all prompts, not just code.
```

## Key Behaviors

1. **Never judge the original prompt** - Just improve it
2. **Explain changes clearly** - Help user learn
3. **Use project context** - Be relevant
4. **Default to execute** - Minimize friction
5. **Support iteration** - Revise until satisfied
6. **Optional clipboard** - For edge cases only

## Integration with Workflow

```
PROMPT REFINEMENT WORKFLOW:

Draft vague prompt
    ↓
/refine "..."
    ↓
See optimized version
    ↓
Choose:
  1. Execute (80% of time)
  2. Revise (15% of time)
  copy. Save for later (5% of time)
```

## When to Use

- **Learning prompt engineering** - See what works
- **Complex requirements** - Need structure
- **Multi-part requests** - Organize thoughts
- **Vague initial idea** - Clarify what you want
- **Cross-tool usage** - Optimize then copy to other AI

## When NOT to Use

- **Simple questions** - Just ask directly
- **Already clear prompts** - No benefit
- **Exploratory prompts** - Vagueness is intentional
- **Quick iterations** - Too much overhead

## Advanced Features

### Template Mode (Future)

```
/refine --template bug-report "..."
/refine --template feature-request "..."
/refine --template code-review "..."
```

### Learning Mode

```
/refine --explain "..."
[Shows prompt engineering principles for each change]
```

### Skill Integration

```
[Checks ~/.claude/ for custom skills]
[Tailors optimization to match available expertise]
```

## Implementation Notes

**Clipboard copy command:**

```bash
# macOS
echo "$optimized_prompt" | pbcopy

# Linux
echo "$optimized_prompt" | xclip -selection clipboard

# Fallback
echo "Clipboard not available. Here's the prompt to copy manually:"
echo "$optimized_prompt"
```

**Context detection:**

- Check for DESCRIPTION (R)
- Check for pyproject.toml/setup.py (Python)
- Check for package.json (Node)
- Check for _quarto.yml (Quarto)
- Read CLAUDE.md if exists
- Parse last 3 git commits

**Optimization principles:**

- Directive > Question
- Specific > Vague
- Structured > Wall of text
- Complete > Minimal
- Contextual > Generic

## Example Workflow Session

```
User: /refine

Claude:
💡 PROMPT OPTIMIZER
Paste or type the prompt you want to optimize:
>

User: help me with tests

Claude:
[Shows analysis of "help me with tests"]
[Optimizes to specific testing request based on project context]
[Shows improvements made]

🎯 NEXT STEPS:
1. Execute now ⭐ (Recommended)
2. Revise - Tell me what to change
💡 Advanced: Type 'copy' to save to clipboard
>

User: 1

Claude:
✅ Executing optimized prompt now...

[Proceeds with optimized testing help]
```
