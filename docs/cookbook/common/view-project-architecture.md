---
title: "Recipe: View Project Architecture"
description: "Get a quick architecture overview of your project with a single command"
category: "cookbook"
level: "beginner"
time_estimate: "2 minutes"
related:
  - ../../commands/arch.md
  - ../../architecture.md
---

# Recipe: View Project Architecture

**Time:** 2 minutes
**Level:** Beginner
**Prerequisites:** Craft installed, existing project

## Problem

I want a quick overview of my project's structure, dependencies, and key components without reading every file.

## Solution

1. **Run the architecture analyzer**

   ```bash
   /craft:arch:analyze
   ```

   Why: Scans your project and produces a structured summary of directories, modules, dependencies, and entry points

2. **Review the output**

   The analyzer reports several sections:

   ```
   Project: craft (Claude Code Plugin)
   Type: Plugin (detected from .claude-plugin/)

   Directory Structure:
     commands/    106 command files across 8 categories
     agents/      8 agent definitions
     skills/      21 skill modules
     utils/       7 Python utilities
     tests/       16 test files (1174 tests)

   Key Entry Points:
     commands/do.md         Smart routing hub
     commands/hub.md        Command discovery
     commands/check.md      Pre-flight validation

   Dependencies:
     Python 3.x, mkdocs, pytest, ruff
   ```

   Why: Gives you a mental map of the project in seconds instead of manually exploring directories

3. **Explore a specific area**

   ```bash
   /craft:arch:analyze commands
   ```

   Why: Narrows the analysis to one directory for a deeper look at that subsystem

## Explanation

`/craft:arch:analyze` detects your project type and walks the file tree to identify structure, key files, dependency relationships, and test coverage. It recognizes patterns for many project types: Node.js (`package.json`), Python (`pyproject.toml`), R packages (`DESCRIPTION`), Quarto sites (`_quarto.yml`), and Claude Code plugins (`.claude-plugin/`). The output adapts to what it finds, highlighting the most important architectural elements for that project type.

## What's Next

- [Architecture Commands Reference](../../commands/arch.md) -- All 12 architecture commands
- [Craft Architecture Guide](../../architecture.md) -- How the Craft plugin itself is built
- [Find the Right Command](find-the-right-command.md) -- Discover more commands with the Hub
