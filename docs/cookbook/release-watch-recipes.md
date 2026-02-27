# Cookbook: Release Watch Recipes

Common patterns and workflows for `scripts/release-watch.py`.

## Recipe 1: Daily Check (Cached)

Run daily to stay current. Cache makes repeat calls instant:

```bash
python3 scripts/release-watch.py
```

First call fetches from APIs (~5s). Subsequent calls within 24h use cache (~0.1s).

## Recipe 2: Pre-Release Audit

Before releasing a new craft version, check for upstream changes:

```bash
# Deep scan with fresh data
python3 scripts/release-watch.py --count 10 --refresh --format markdown > release-audit.md

# Check auto-fix suggestions
python3 scripts/release-watch.py --auto-fix
```

Review `release-audit.md` for any breaking changes or new features to adopt.

## Recipe 3: JSON Pipeline

Extract specific data for scripts:

```bash
# Get latest version
python3 scripts/release-watch.py -p code -f json | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(d['latest_version'])
"

# Count breaking changes
python3 scripts/release-watch.py -f json | python3 -c "
import json, sys
d = json.load(sys.stdin)
code_breaking = len(d['findings']['breaking'])
desktop_breaking = len(d['desktop']['findings']['breaking'])
print(f'Breaking: {code_breaking} Code, {desktop_breaking} Desktop')
"

# List hardcoded models
python3 scripts/release-watch.py -f json | python3 -c "
import json, sys
d = json.load(sys.stdin)
for m in d['craft_state']['hardcoded_models']:
    print(f'  - {m}')
"
```

## Recipe 4: Desktop-Only Monitoring

Track Claude Desktop without Code noise:

```bash
python3 scripts/release-watch.py --product desktop
```

Or via the Craft command alias:

```bash
/craft:code:desktop-watch
```

## Recipe 5: Version Delta

See what changed since a specific version:

```bash
# Everything after v2.1.50
python3 scripts/release-watch.py --since v2.1.50 --count 20

# JSON for parsing
python3 scripts/release-watch.py --since v2.1.50 --count 20 -f json
```

## Recipe 6: Full Sync Pipeline

Combine with command-audit for a complete health check:

```bash
# Step 1: Audit craft commands
bash scripts/command-audit.sh --format json > /tmp/audit.json

# Step 2: Check releases
python3 scripts/release-watch.py --format json > /tmp/releases.json

# Step 3: Review together
echo "=== Audit ==="
python3 -c "import json; d=json.load(open('/tmp/audit.json')); print(f'Health: {d.get(\"health_score\", \"N/A\")}')"
echo "=== Releases ==="
python3 -c "import json; d=json.load(open('/tmp/releases.json')); print(f'Latest: {d[\"latest_version\"]}')"
```

Or use the integrated command:

```bash
/craft:code:sync-features
```

## Recipe 7: Auto-Fix Workflow

Generate and apply safe patches:

```bash
# Generate patch
python3 scripts/release-watch.py --auto-fix

# Review what it proposes
cat .claude/release-watch-fixes.patch

# Dry-run the patch
git apply --check .claude/release-watch-fixes.patch

# Apply if satisfied
git apply .claude/release-watch-fixes.patch

# Commit
git add -A
git commit -m "fix: update MODEL_PATTERNS from release-watch auto-fix"
```

## Recipe 8: Stale Cache Debugging

If results seem outdated:

```bash
# Check cache age
python3 -c "
import json, time
from pathlib import Path
cache = json.loads(Path.home().joinpath('.claude/release-watch-cache.json').read_text())
for source, entry in cache.items():
    age_h = (time.time() - entry.get('timestamp', 0)) / 3600
    print(f'{source}: {age_h:.1f}h old')
"

# Force refresh
python3 scripts/release-watch.py --refresh

# Or nuke cache entirely
rm ~/.claude/release-watch-cache.json
python3 scripts/release-watch.py
```

## Recipe 9: CI Integration

Add to a CI pipeline (non-blocking, advisory only):

```yaml
# .github/workflows/release-check.yml
- name: Check upstream releases
  run: |
    python3 scripts/release-watch.py --no-cache -f json > release-check.json
    breaking=$(python3 -c "import json; print(len(json.load(open('release-check.json'))['findings']['breaking']))")
    if [ "$breaking" -gt 0 ]; then
      echo "::warning::$breaking breaking upstream changes detected"
    fi
  continue-on-error: true  # Advisory, never blocks
```

## Recipe 10: Backward-Compatible Usage

If you have scripts consuming the v1 JSON output:

```bash
# This produces v1-compatible output (no desktop section)
python3 scripts/release-watch.py --product code --format json
```

The `--product code` flag ensures only Code data appears, and all v1 JSON keys are preserved.
