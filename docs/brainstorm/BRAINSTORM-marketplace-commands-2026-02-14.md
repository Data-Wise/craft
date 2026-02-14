# Marketplace Distribution Commands - Deep Brainstorm

**Generated:** 2026-02-14
**Context:** Craft plugin, dev branch
**Depth:** Deep (8 questions)
**Focus:** Architecture + Feature

## Overview

Add marketplace distribution support to craft's command/skill ecosystem: a new `/craft:dist:marketplace` command, release skill updates for auto-detecting and bumping marketplace.json, Homebrew template fixes for `brew audit --strict` compliance, and tap auto-update during releases.

## Decisions Made (from brainstorm questions)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Command structure | New `/craft:dist:marketplace` command | Marketplace is fundamentally different from Homebrew |
| Release version bump | Auto-detect marketplace.json | If it exists, bump it — no flags needed |
| Homebrew templates | Fix all for `brew audit --strict` | Templates should produce audit-clean formulas |
| Tap sync in release | Auto-update tap repo | Release skill pushes formula update to tap |
| Marketplace scope | Single-plugin first | Common case for most users |
| Tap location | Local if available, temp clone fallback | Faster + respects dev setup |
| Marketplace validation | Both standalone + in release pre-flight | `claude plugin validate .` in pre-flight checks |
| Plugin formula type | First-class auto-detection | Detect `.claude-plugin/` dir, generate plugin formula |
| Install docs tone | Marketplace recommended for new users | Simpler, cross-platform; Homebrew for power users |
| Marketplace subcommands | init, validate, publish, test | Full lifecycle management |

## Quick Wins (< 30 min each)

1. Create `.claude-plugin/marketplace.json` for craft repo (from existing spec)
2. Fix Homebrew formula templates in `commands/dist/homebrew.md` for `brew audit --strict`
3. Add marketplace.json version bump to release skill's Step 3

## Medium Effort (1-2 hours)

- [ ] Create `/craft:dist:marketplace` command with 4 subcommands
- [ ] Update release skill pre-flight to include `claude plugin validate .`
- [ ] Add tap auto-update step to release skill (Step 8.5)
- [ ] Add Claude Code plugin as first-class formula type in homebrew command
- [ ] Update installation docs (README, homebrew-installation.md)

## Long-term (Future sessions)

- [ ] Multi-plugin marketplace support
- [ ] GitHub Action for marketplace validation on PR
- [ ] Auto-update marketplace from CI on release
- [ ] Distribution strategist skill update for marketplace channel

## Recommended Path

Start with the spec (below), then implement in a single feature branch. The changes touch:

- 1 new command file (`commands/dist/marketplace.md`)
- 1 existing command update (`commands/dist/homebrew.md`)
- 1 skill update (`skills/release/SKILL.md`)
- 1 new file in repo root (`.claude-plugin/marketplace.json`)
- 2 doc updates (README, installation guide)
