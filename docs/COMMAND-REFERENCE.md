# Command Reference

**Last Updated:** 2025-12-26

Complete reference of all commands across all plugins.

## Table of Contents

- [Workflow](#workflow) (10 commands)
- [Rforge](#rforge) (15 commands)
- [Statistical Research](#statistical-research) (14 commands)

**Total:** 39 commands

---

## Workflow

**Plugin:** `workflow`
**Version:** 2.1.0
**Commands:** 10

| Command | Description |
|---------|-------------|
| `/workflow:brainstorm` | Enhanced brainstorming with smart detection and agent delegation |
| `/workflow:done` | Session completion with context capture |
| `/workflow:focus` | Single-task mode with distraction blocking |
| `/workflow:next` | Decision support for what to work on next |
| `/workflow:recap` | Context restoration for returning to work |
| `/workflow:refine` | Prompt optimizer for better AI interactions |
| `/workflow:stuck` | Unblock helper with guided problem solving |
| `/workflow:task-cancel` | Cancel running background tasks |
| `/workflow:task-output` | View background task results |
| `/workflow:task-status` | Check background task progress |

### Quick Reference

```bash
# Core workflow
/workflow:brainstorm              # Smart ideation with auto-delegation
/workflow:focus                   # Enter single-task mode
/workflow:next                    # What to work on next
/workflow:done                    # End session with context capture
/workflow:recap                   # Restore context from previous session

# Problem solving
/workflow:stuck                   # Get help when blocked
/workflow:refine                  # Improve prompts

# Task management
/workflow:task-status             # Check background task progress
/workflow:task-output             # View task results
/workflow:task-cancel             # Cancel running task
```

---

## Rforge

**Plugin:** `rforge`
**Version:** 1.1.0
**Commands:** 15

| Command | Description |
|---------|-------------|
| `/rforge:analyze` | Quick R package analysis with auto-delegation (< 30s) |
| `/rforge:quick` | Ultra-fast analysis (< 10 seconds) |
| `/rforge:thorough` | Comprehensive analysis (2-5 minutes) |
| `/rforge:detect` | Auto-detect R package project structure |
| `/rforge:deps` | Build and visualize dependency graph |
| `/rforge:impact` | Analyze change impact across ecosystem |
| `/rforge:cascade` | Plan coordinated updates across packages |
| `/rforge:doc-check` | Check documentation drift and inconsistencies |
| `/rforge:release` | Plan CRAN submission sequence |
| `/rforge:capture` | Quick capture ideas and tasks |
| `/rforge:complete` | Mark tasks complete with documentation cascade |
| `/rforge:next` | Get ecosystem-aware next task recommendation |
| `/rforge:status` | Ecosystem-wide status dashboard |
| `/rforge:rpkg-check` | Run R CMD check with smart output parsing |
| `/rforge:ecosystem-health` | Check health across R package ecosystem |

### Quick Reference

```bash
# Analysis commands
/rforge:quick                     # Fast check (< 10s)
/rforge:analyze "context"         # Balanced analysis (< 30s)
/rforge:thorough "context"        # Deep analysis (2-5 min)

# Ecosystem commands
/rforge:detect                    # Detect project structure
/rforge:deps                      # Show dependency graph
/rforge:impact "change"           # Analyze change impact
/rforge:cascade                   # Plan coordinated updates
/rforge:status                    # Ecosystem dashboard

# R package commands (NEW in v1.1.0)
/rforge:rpkg-check                # Run R CMD check
/rforge:ecosystem-health          # Check ecosystem health

# Task management
/rforge:next                      # Next task recommendation
/rforge:capture "idea"            # Capture task/idea
/rforge:complete "task"           # Mark task done

# Release
/rforge:release                   # Plan CRAN submission
/rforge:doc-check                 # Check documentation
```

---

## Statistical Research

**Plugin:** `statistical-research`
**Version:** 1.1.0
**Commands:** 14

| Command | Description |
|---------|-------------|
| `/research:arxiv` | Search arXiv for statistical papers |
| `/research:doi` | Look up paper metadata by DOI |
| `/research:bib:search` | Search BibTeX files for entries |
| `/research:bib:add` | Add BibTeX entry to bibliography |
| `/research:manuscript:methods` | Write methods section |
| `/research:manuscript:results` | Write results section |
| `/research:manuscript:reviewer` | Generate reviewer responses |
| `/research:manuscript:proof` | Review mathematical proofs |
| `/research:simulation:design` | Design Monte Carlo studies |
| `/research:simulation:analysis` | Analyze simulation results |
| `/research:lit-gap` | Identify literature gaps |
| `/research:hypothesis` | Generate research hypotheses |
| `/research:analysis-plan` | Create statistical analysis plan |
| `/research:method-scout` | Scout statistical methods for a problem |

### Quick Reference

```bash
# Literature
/research:arxiv "query"           # Search arXiv
/research:doi 10.1234/example     # Lookup by DOI
/research:bib:search "author"     # Search BibTeX
/research:bib:add file.bib        # Add to bibliography

# Manuscript
/research:manuscript:methods      # Write methods section
/research:manuscript:results      # Write results section
/research:manuscript:reviewer     # Respond to reviewers
/research:manuscript:proof        # Review proofs

# Simulation
/research:simulation:design       # Design Monte Carlo study
/research:simulation:analysis     # Analyze results

# Research planning
/research:lit-gap "topic"         # Find literature gaps
/research:hypothesis              # Generate hypotheses
/research:analysis-plan           # Create analysis plan
/research:method-scout "problem"  # Scout methods (NEW in v1.1.0)
```

---

## Summary

| Plugin | Version | Commands | Focus |
|--------|---------|----------|-------|
| workflow | 2.1.0 | 10 | ADHD-friendly development workflow |
| rforge | 1.1.0 | 15 | R package ecosystem management |
| statistical-research | 1.1.0 | 14 | Academic research workflows |
| **Total** | | **39** | |

---

## Installation

All plugins are installed via symlink for easy development:

```bash
~/.claude/plugins/
├── workflow → ~/projects/dev-tools/claude-plugins/workflow
├── rforge → ~/projects/dev-tools/claude-plugins/rforge
└── statistical-research → ~/projects/dev-tools/claude-plugins/statistical-research
```

---

**Last Updated:** 2025-12-26
**Maintained By:** Data-Wise
