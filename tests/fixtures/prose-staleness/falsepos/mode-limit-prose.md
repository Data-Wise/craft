<!-- Must NOT flag: orchestration mode-limit prose counts concurrent agents, not agent definitions. -->
<!-- This is review finding 3's original false-positive source. The runner writes it to its real -->
<!-- path, docs/guide/orch-flag-usage.md, because the "4 agents" pattern exclusion in -->
<!-- scripts/config/exclusions.txt is path-keyed — this fixture proves the NEW shape scan honors -->
<!-- that exclusion too, not just the pre-existing broad scan. -->

# Orchestration flag usage

Default mode dispatches 2 agents max. Raising the cap to 4 agents is supported but rarely
useful; beyond that the coordination overhead dominates.
