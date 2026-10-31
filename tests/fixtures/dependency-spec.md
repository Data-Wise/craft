---
dependencies:
  bash:
    required: true
    purpose: Exercise a tool available in the test runner
    methods: [asciinema]
  craft-dependency-missing-test-tool:
    required: true
    purpose: Exercise a missing required tool without installing software
    methods: [vhs]
---

# Dependency checker test specification

Test-only input for the retained dependency scripts after the demo command moved
to Folio. These entries exercise method filtering and missing-tool reporting;
they are not the production tool requirements for demo recording. No health or
installation commands are executed by this fixture.
