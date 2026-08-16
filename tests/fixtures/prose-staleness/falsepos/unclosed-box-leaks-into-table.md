<!-- Planted regression check (F8): an unclosed version-box must not leak
     `inbox` mode into the rest of the file. Before the fix, an opening box
     character with no matching closing one kept every later line tagged as
     part of the box until EOF, so the structure-table row below lost its own
     -type restriction and its incidental secondary-type mention got compared
     against the wrong expected count. Uses the singular noun form (not the
     plural the broad, unscoped scan also matches) so this fixture isolates
     the shape-classification bug rather than tripping an unrelated scan. -->

# Notes

```text
┌ untouched legacy snapshot, never finished
```

| Directory | Purpose |
|-----------|---------|
| `commands/` | 48 commands, once listed 3 agent placeholders here too |
