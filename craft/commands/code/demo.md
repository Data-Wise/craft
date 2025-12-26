# Code Demonstration

Create working code demonstrations and examples.

## Purpose

Generate demonstrations for:
- Package vignettes
- Tutorial materials
- Conference presentations
- Documentation examples
- Teaching code

## Required Input

- **Topic**: What to demonstrate
- **Audience**: Beginners, intermediate, experts
- **Format**: Vignette, slides, standalone script
- **Length**: Brief example or comprehensive tutorial

## Process

1. **Define scope**
   - What concepts to cover
   - Prerequisite knowledge assumed
   - Learning objectives

2. **Design flow**
   - Build from simple to complex
   - Include intermediate outputs
   - Show common variations

3. **Write code**
   - Clear, readable style
   - Helpful comments
   - Runnable examples

4. **Add context**
   - Explain the "why"
   - Note common pitfalls
   - Suggest next steps

## Output Format

```markdown
# Demo: [Topic]

## Overview
[What this demo covers and why it matters]

## Prerequisites
- [Required packages]
- [Assumed knowledge]

## Setup
```r
# Load packages
library(package1)
library(package2)

# Sample data
data <- create_example_data()
```

## Part 1: [First Concept]

[Explanation of what we're doing]

```r
# Step 1: Description
result <- function_call(data)
result
#> [Expected output shown]
```

[Interpretation and notes]

## Part 2: [Second Concept]

[Continue building...]

## Common Variations

### Variation A: [Description]
```r
# How to modify for this case
```

### Variation B: [Description]
```r
# Alternative approach
```

## Troubleshooting

**Issue**: [Common problem]
**Solution**: [How to fix]

## Next Steps
- [Where to learn more]
- [Related functions/topics]

## References
- [Documentation links]
- [Papers if applicable]
```

## Demo Types

### Quick Example
- Single concept
- ~10 lines of code
- Immediate output

### Tutorial
- Multiple concepts
- Step-by-step progression
- Full workflow

### Vignette
- Comprehensive coverage
- Real-world use case
- Publication quality

### Live Coding
- Presentation format
- Clear stopping points
- Audience interaction notes

## MCP Integration

Uses these tools when available:
- `r_execute` - Run and verify code
- `r_plot` - Generate visualizations
- `r_preview` - Preview output

## Examples

**Request**: "Create a demo of linear regression in R for beginners"

**Request**: "Generate a vignette showing mediation analysis workflow"

**Request**: "Demo ggplot2 customization for publication-quality figures"

**Request**: "Create live-coding examples for a dplyr workshop"

## Best Practices

### Code Style
- Use consistent formatting
- Include all library() calls
- Show expected output in comments

### Explanation
- Explain before code blocks
- Interpret after outputs
- Connect to real-world use

### Reproducibility
- Set seeds for random operations
- Include data creation code
- Note package versions

## Tips

- Start with the simplest working example
- Build complexity gradually
- Include "what if" variations
- Show both success and error cases
- Link to further resources
