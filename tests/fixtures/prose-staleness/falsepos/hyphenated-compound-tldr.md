<!-- Planted regression check (F1/F2): a hyphenated compound must never read as
     a count. Before the trailer fix, "([^a-z]|$)" accepted "-" as a boundary,
     so "30 command-line" matched as "30 command" (expected 48) and "3
     agent-facing" matched as "3 agent" (expected 2) -- and [f]ix would have
     rewritten this line's hyphenated compounds around the false match. -->

# Architecture

**TL;DR** — craft exposes 30 command-line entry points across 3 agent-facing surfaces.
