# GRILL: Token Efficiency + Context Tooling Consolidation

**Target:** SPEC-token-efficiency-and-context-tooling-2026-07-01.md (consolidation of _archive/SPEC-token-efficiency-research-2026-06-30.md +_archive/SPEC-superpowers-claude-context-workflows-2026-07-01.md)
**Date:** 2026-07-01
**Outcome:** Approved for Tasks 1/2/4; Task 3 blocked on claude-context MCP install.

## Decision Ledger

| # | Branch | Decision |
|---|---|---|
| 1 | Task 3 MCP dependency | Block Task 3 explicitly on MCP install/connection verification — do not imply shovel-ready. |
| 2 | Overall spec status | Approved for Tasks 1/2/4 only; Task 3 stays blocked; this grill session satisfies the grill-before-implementing gate. |
| 3 | Task 1's external-file scope | Keep, but gated on the file resolving inside repo/outputs first — else it is a note, not a task. |
| 4 | Priority ordering of open items | Usage checkpoint listed first — the only item that validates the headline 48% claim. |
| 5 | Scope boundary vs. deprecated-commands audit | Cross-reference issue #233 / the audit spec; do not absorb its 18-item list here. |

## Open Questions

- [ ] Real /usage checkpoint (~2026-07-14) — validates or refutes the 48% line-reduction -> token-savings hypothesis. Record result in _archive/SPEC-token-efficiency-research-2026-06-30.md §9.
- [ ] Task 3 (claude-context pilot) — blocked until claude-context MCP is installed and connected.
- [ ] Task 1 (external docx correction) — confirm the file resolves inside this repo/session before treating as actionable.
