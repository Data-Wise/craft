# AGENTS.md - Development Guidelines for Craft Plugin

## Working contract

Commands/skills/agents use YAML frontmatter; keep counts, public interfaces, README, examples, breaking-change notices, and documentation synchronized. Python: explicit types, specific exceptions, pathlib, public API docstrings; validate paths and inputs, mock external dependencies, clean test artifacts. Coverage target: 90%+, including critical paths and edge/error cases.
Required gates: `python3 -m pytest tests/ -v`, `bash tests/test_dependency_management.sh`, `./scripts/validate-counts.sh`, configured Markdown lint, documentation build and link checks. Read the reference's Build/Lint/Test Commands and CI/CD Integration before committing or releasing.

## On-demand requirements

The exact pre-condensation instructions are preserved in `/Users/davood/.codex/reference/repos/dev-tools-craft/AGENTS-detail-2026-10-12.md`. Before a task, read only its applicable sections: scientific/model changes, builds/tests, source conventions, dependency/API changes, packaging/releases, configuration/imports, deployment, or workflow cleanup. Every applicable requirement and verification gate there remains binding; this shorter file does not waive any. Do not load the whole reference for unrelated tasks. Historical versions, counts, results and completed-work snapshots are not live status: check the owning source and .STATUS. Current user instructions and project holds take precedence.

Preserve unrelated changes and concurrent sessions. Required checks must pass before claiming completion; inspect actual rendered artifacts where applicable. Author review/submission holds remain active until explicitly lifted. Passing checks never authorizes submission, merge, release, deployment, email sending or privacy changes.
