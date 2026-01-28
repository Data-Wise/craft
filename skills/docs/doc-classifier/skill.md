# doc-classifier Skill

Classify documentation needs based on code changes.

## Description

Analyzes git commits, file changes, and feature scope to determine what documentation types are needed. Returns structured classification data.

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `feature_name` | string | Optional feature name to analyze |
| `commit_range` | string | Git commit range (default: HEAD~10) |
| `format` | string | Output format: `json`, `summary`, `actions` |

## Outputs

```json
{
  "feature": "session tracking",
  "scope": {
    "commands": ["sessions live", "sessions current", "sessions task"],
    "modules": ["src/aiterm/sessions/"],
    "hooks": ["session-register", "session-cleanup"],
    "files_changed": 23,
    "commits": 15
  },
  "classification": {
    "guide": { "score": 8, "needed": true, "reason": "New module with 5 CLI commands" },
    "refcard": { "score": 5, "needed": true, "reason": "5 new commands" },
    "gif_demo": { "score": 6, "needed": true, "reason": "User-facing CLI workflow" },
    "mermaid": { "score": 7, "needed": true, "reason": "Hook-based event system" }
  }
}
```

## Scoring Algorithm

### Base Scores

| Factor | Guide | Refcard | GIF | Mermaid |
|--------|-------|---------|-----|---------|
| New command (each) | +1 | +1 | +0.5 | +0 |
| New module | +3 | +1 | +1 | +2 |
| New hook | +2 | +1 | +1 | +3 |
| Multi-step workflow | +2 | +0 | +3 | +2 |
| Config changes | +0 | +2 | +0 | +0 |
| Architecture change | +1 | +0 | +0 | +3 |
| User-facing CLI | +1 | +1 | +2 | +0 |

### Threshold

- Score >= 3: **needed**
- Score >= 5: **high priority**
- Score >= 7: **essential**

## Detection Logic

### Command Detection

```bash
# Find new @app.command decorators
git diff HEAD~10 --name-only | xargs grep -l "@app.command"

# Parse command names
grep -E "@app\.command\(|def \w+\(" src/*/cli/*.py
```

### Module Detection

```bash
# New directories with __init__.py
git diff --diff-filter=A HEAD~10 --name-only | grep "__init__.py"
```

### Hook Detection

```bash
# Hook-related files
git diff HEAD~10 --name-only | grep -E "hook|event"

# Hook configuration
grep -E "SessionStart|Stop|PreToolUse" ~/.claude/settings.json
```

### Workflow Detection

```bash
# Subcommand groups (Typer)
grep "typer.Typer()" src/*/cli/*.py

# Multi-step docs
grep -E "Step [0-9]" docs/**/*.md
```

## Usage Examples

### From /craft:docs:analyze

```python
# Internal call
classification = doc_classifier(
    feature_name="session tracking",
    commit_range="HEAD~15"
)

if classification["guide"]["needed"]:
    # Generate guide
    pass
```

### Standalone

```bash
/skill doc-classifier "session tracking" --format json
```

## Integration

**Used by:**

- `/craft:docs:analyze` - Main classification command
- `/craft:docs:guide` - Determine what to generate
- `/craft:docs:feature` - Smart detection enhancement
- `/craft:docs:update` - Selective updates

**Complements:**

- `mermaid-linter` skill - Validate generated diagrams
- `changelog-automation` skill - Detect feature boundaries
