# Changelog - RForge Plugin

All notable changes to the RForge plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] - 2025-12-26

### Added - R Package Commands

Migrated R-specific commands from user commands into the plugin:

#### New Commands (2 total)
- **`/rforge:rpkg-check`** - Run R CMD check on package with smart output parsing
- **`/rforge:ecosystem-health`** - Check health across R package ecosystem

### Changed
- **Total commands:** 13 → 15
- **Plugin installed via symlink** for easier development

---

## [1.0.0] - 2024-12-23

### Added - Initial Release

#### Commands (13 total)
- **`/rforge:analyze`** - Quick analysis with auto-delegation (< 30 seconds)
- **`/rforge:quick`** - Ultra-fast analysis using only quick tools (< 10 seconds)
- **`/rforge:thorough`** - Comprehensive analysis with background R processes (2-5 minutes)
- **`/rforge:detect`** - Auto-detect R package project structure
- **`/rforge:deps`** - Build and visualize dependency graph
- **`/rforge:impact`** - Analyze change impact across ecosystem
- **`/rforge:cascade`** - Plan coordinated updates across packages
- **`/rforge:doc-check`** - Check documentation drift and inconsistencies
- **`/rforge:release`** - Plan CRAN submission sequence
- **`/rforge:capture`** - Quick capture ideas and tasks
- **`/rforge:complete`** - Mark tasks complete with documentation cascade
- **`/rforge:next`** - Get ecosystem-aware next task recommendation
- **`/rforge:status`** - Ecosystem-wide status dashboard

#### Agents
- **orchestrator** - Auto-delegation for RForge MCP tools

#### Features
- Auto-delegation to RForge MCP tools
- Parallel execution of multiple MCP calls
- Live progress updates
- Smart result synthesis
- ADHD-friendly output

---

## Version History Summary

| Version | Date | Major Changes |
|---------|------|---------------|
| **1.1.0** | 2025-12-26 | Added rpkg-check and ecosystem-health commands |
| **1.0.0** | 2024-12-23 | Initial release: 13 commands, 1 agent |

---

**Last Updated:** 2025-12-26
**Maintained By:** Data-Wise
**License:** MIT
