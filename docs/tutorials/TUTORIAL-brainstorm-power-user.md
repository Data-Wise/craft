# Brainstorm Power User Tutorial

> Advanced patterns, detailed examples, and expert workflows for `/workflow:brainstorm`

**Prerequisites:** Basic familiarity with `/brainstorm` (see `/craft:hub workflow:brainstorm`)

---

## Quick Reference

```bash
# Minimal
/brainstorm "auth"                           # Default everything

# With focus
/brainstorm feat "auth"                      # Feature focus
/brainstorm f "auth"                         # Same (single letter)

# With action
/brainstorm save "auth"                      # Save as spec
/brainstorm s "auth"                         # Same (single letter)

# Combined
/brainstorm feat save "auth"                 # Feature + spec
/brainstorm f s "auth"                       # Same (ultra-short)

# Full control
/brainstorm deep feat save "auth"            # Deep + feature + spec
/brainstorm d f s "auth"                     # Power user mode

# Maximum depth
/brainstorm max arch save "auth"             # Max + architecture + spec
/brainstorm m a s "auth"                     # Same (ultra-short)

# Custom question counts (v2.4.0)
/brainstorm d:5 "auth"                       # Deep with exactly 5 questions
/brainstorm m:12 "api"                       # Max with 12 questions
/brainstorm q:0 "quick"                      # Quick with 0 questions

# Category filtering (v2.4.0)
/brainstorm d:5 "auth" -C req,tech           # 5 questions from req + tech
/brainstorm m:10 f "api" --categories req,usr,tech,exist

# Power user - full control
/brainstorm d:15 f s -C req,tech,success "auth"
```

---

## Example Scenarios

### Scenario 1: Interactive Mode Selection

```
User: /workflow:brainstorm

Claude: Shows mode menu...
User: Selects "Feature (Recommended)"

Claude: Shows depth menu...
User: Selects "Quick (Recommended)"

Claude: "What topic would you like to brainstorm?"
User: "user authentication"

-> Runs feature + quick brainstorm for auth
-> Completes in 42s
-> Saves to BRAINSTORM-user-auth-2024-12-24.md
```

### Scenario 2: Direct Invocation (Skip Menu)

```
User: /workflow:brainstorm quick feature auth

-> Skips menus entirely
-> Runs feature mode with quick depth
-> Completes in 38s
```

### Scenario 3: Thorough Architecture Analysis

```
User: /workflow:brainstorm thorough architecture "multi-tenant SaaS"

-> Launches backend-architect agent (background)
-> Launches database-architect agent (background)
-> Generates initial ideas while agents work
-> Synthesizes comprehensive plan
-> Completes in 3m 24s
-> Saves detailed analysis with agent findings
```

### Scenario 4: JSON Output

```
User: /workflow:brainstorm feature notifications --format json

-> Runs feature brainstorm
-> Outputs JSON structure
-> Saves to BRAINSTORM-notifications-2024-12-24.json
```

### Scenario 5: Colon Notation (v2.4.0)

```
User: /workflow:brainstorm d:5 "auth system"

-> Deep mode with exactly 5 questions
-> Asks 5 questions from question bank
-> Shows "Ask More?" prompt
-> Proceeds to brainstorm
```

### Scenario 6: Categories Flag (v2.4.0)

```
User: /workflow:brainstorm d:5 "auth" -C req,tech

-> Deep mode with 5 questions from requirements + technical
-> Skips users, scope, timeline, risks, existing, success
-> More focused context gathering
```

### Scenario 7: Unlimited Questions with Milestones

```
User: /workflow:brainstorm d:20 "microservices"

-> Asks first 8 questions
-> Milestone prompt: "You've answered 8 questions. Continue?"
-> User selects "8 more questions"
-> Asks next 8 questions
-> Milestone prompt: "You've answered 16 questions. Continue?"
-> User selects "Done - Start brainstorming"
-> Proceeds to brainstorm with 16 questions of context
```

### Scenario 8: Power User (v2.4.0)

```
User: /workflow:brainstorm d:15 f s -C req,tech,success "payment api"

-> Deep mode with 15 questions
-> Feature focus with spec capture
-> Categories: requirements, technical, success only
-> Milestone prompts every 8 questions
-> Generates comprehensive plan with spec
```

### Scenario 9: Orchestration Mode (v2.5.0)

```
User: /workflow:brainstorm "authentication system" --orch=optimize

-> Orchestrator spawns with optimize mode
-> Parallel agent analysis for comprehensive coverage
```

### Scenario 10: Orchestration Dry-Run (v2.5.0)

```
User: /workflow:brainstorm "payment api" --orch=release --dry-run

+---------------------------------------------------------------------+
| DRY RUN: Orchestration Preview                                      |
+---------------------------------------------------------------------+
| Task: brainstorm 'payment api' focusing on categories: all         |
| Mode: release                                                       |
| Max Agents: 4                                                       |
| Compression: 85%                                                    |
+---------------------------------------------------------------------+
```

### Scenario 11: Context-Aware Smart Questions (v2.15.0)

```
User: /workflow:brainstorm d:5 "dependency management"

-> Context scan finds SPEC-dependency-management.md
-> "Found SPEC-dependency-management.md -- load as context?" -> Yes
-> Pre-fills requirements + technical from spec
-> Asks 3 remaining questions (scope, risks, success)
-> Generates brainstorm with full spec context
```

---

## Output Formats

### Terminal (Default)

```
+-------------------------------------------------------------+
| BRAINSTORM: [Topic]                                          |
| Mode: [mode] | Depth: [depth] | Duration: [time]            |
+-------------------------------------------------------------+
|                                                              |
| ## Quick Wins (< 30 min each)                                |
|   [Action 1] - [Benefit]                                     |
|   [Action 2] - [Benefit]                                     |
|                                                              |
| ## Medium Effort (1-2 hours)                                 |
|   [ ] [Task with clear outcome]                              |
|                                                              |
| ## Long-term (Future sessions)                               |
|   [ ] [Strategic item]                                       |
|                                                              |
| ## Recommended Path                                          |
|   -> [Clear recommendation with reasoning]                   |
+-------------------------------------------------------------+
```

### JSON (`--format json`)

```json
{
  "metadata": {
    "timestamp": "2024-12-24T10:30:00Z",
    "mode": "feature",
    "depth": "quick",
    "duration_seconds": 45,
    "agents_used": []
  },
  "content": {
    "topic": "User notifications",
    "quick_wins": [],
    "medium_effort": [],
    "long_term": []
  },
  "recommendations": {
    "recommended_path": "...",
    "next_steps": []
  }
}
```

### Markdown (`--format markdown`)

Saves to `BRAINSTORM-[topic]-[date].md`

---

## Backward Compatibility

| Old Syntax (v2.2.0) | New Syntax (v2.4.0) | Status |
|---------------------|---------------------|--------|
| `--save-spec` | `save` or `s` | Deprecated but works |
| `--save-spec=full` | `save` (default is full) | Deprecated but works |
| `--save-spec=quick` | `q save` | Deprecated but works |
| `feature` | `feat` or `f` | Both work |
| `architecture` | `arch` or `a` | Both work |
| `thorough` | `max` or `m` | `thorough` deprecated |

---

## Tips

1. **Start quick, go deep if needed** — `q` mode with "Ask More?" is the fastest path
2. **Use categories to focus** — `-C req,tech` skips irrelevant questions
3. **Colon notation saves time** — `d:5` is more precise than generic `d` (8 questions)
4. **Spec capture for implementation** — `s` flag auto-generates implementation spec
5. **Orchestration for complex topics** — `--orch=optimize` parallelizes analysis
6. **Context-aware saves repetition** — Smart questions skip what's already known (v2.15.0)

---

*See also: [Question Bank Reference](../specs/SPEC-brainstorm-question-bank.md) | [Brainstorm Reference Card](../reference/REFCARD-BRAINSTORM.md)*
