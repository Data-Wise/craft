# Homebrew Release Gates Tutorial

Three quality gates protect every plugin formula release from common drift bugs.
Two gates are **advisory** (warn only unless `HOMEBREW_GATE_STRICT=1`) and one
gate is **blocking** (aggregator-sync always exits 1 on failure).

---

## Gate Overview

| Gate | Script | Default | Strict mode |
|------|--------|---------|-------------|
| Caveats freshness | `scripts/verify_caveats.py` | Advisory (exit 0) | `HOMEBREW_GATE_STRICT=1` → exit 1 |
| post_install structure | `scripts/post_install_check.py` | Advisory (exit 0) | `HOMEBREW_GATE_STRICT=1` → exit 1 |
| Aggregator sync | `scripts/aggregator-sync.sh` | **BLOCKING** (exit 1) | Always blocking |

---

## Step 10b: Caveats Freshness Gate

Checks that the formula's `caveats` block contains a `New in vX.Y.Z:` header for
the current release version, and that any managed bullet zone matches the CHANGELOG.

### What it checks

1. **Check 1 — Version header**: `New in v{version}:` must appear in `def caveats`.
2. **Check 2 — Managed bullets**: If the formula has a `# --- dynamic bullets ---` /
   `# --- end dynamic bullets ---` zone, its bullet items must match the CHANGELOG
   entries for the current version. A missing CHANGELOG section is always a finding.
3. **Check 3 — post_install guard**: The `post_install` block must contain
   `begin / rescue / end` to catch install errors gracefully.

### Running the gate

```bash
# Advisory (default): reports findings, exits 0
python3 scripts/verify_caveats.py "$FORMULA" CHANGELOG.md "$VERSION"

# Strict: exits 1 on any finding
HOMEBREW_GATE_STRICT=1
python3 scripts/verify_caveats.py "$FORMULA" CHANGELOG.md "$VERSION" \
  ${HOMEBREW_GATE_STRICT:+--strict} --name "$PLUGIN_NAME"
```

### Expected advisory output (stale formula)

```
⚠️  caveats missing 'New in v2.49.0:' header
⚠️  caveats bullets differ from CHANGELOG v2.49.0: {'new shiny feature'}
```

Exit code: **0** (advisory default), **1** (with `--strict`).

### Tap-absent leg

CI runners (e.g. Ubuntu) do not have the local tap checked out. When the formula
path does not exist, skip the check and continue — never block on absence.

```bash
[ -f "$FORMULA" ] || { echo "⚠️  tap formula not present, skipping caveats check"; exit 0; }
python3 scripts/verify_caveats.py "$FORMULA" CHANGELOG.md "$VERSION" \
  ${HOMEBREW_GATE_STRICT:+--strict}
```

---

## Step 10c: post_install Structure Gate

Checks that `post_install` follows the required 3-step pattern:
`begin / rescue / end`, `marketplace update` before `plugin update`, and at
least one `libexec` reference.

### Running the gate

```bash
# Advisory (default)
python3 scripts/post_install_check.py "$FORMULA"

# Strict
python3 scripts/post_install_check.py "$FORMULA" ${HOMEBREW_GATE_STRICT:+--strict}

# Sandbox (macOS-local only) — proves the block parses without touching ~/.claude
python3 scripts/post_install_check.py "$FORMULA" --sandbox
```

### Expected output (correct formula)

```
✅ post_install structurally sound
```

### Expected output (ordering bug)

```
⚠️  'marketplace update' must precede 'plugin update' (ordering bug)
```

Exit code: **0** (advisory default), **1** (with `--strict`).

---

## Step 10d: Aggregator-Sync Gate (BLOCKING)

The local-marketplace aggregator (`dist/data-wise-marketplace.json`) pins each
plugin to a specific version. A stale pin causes Cowork/Desktop users to install
the wrong version silently.

**This gate is always blocking — exit 1 on failure, no advisory mode.**

### Running the gate

```bash
bash scripts/aggregator-sync.sh || {
  echo "❌ aggregator-sync failed — release blocked"
  exit 1
}
```

### Cowork/Desktop verification after publish

After the tap formula is pushed and the GitHub release is live, verify on
Cowork and Claude Desktop:

```bash
# Refresh the local-plugins cache FIRST (else update no-ops on stale cache)
claude plugin marketplace update local-plugins

# Then update using the qualified name
claude plugin update $(jq -r .name .claude-plugin/plugin.json)@local-plugins

# Confirm the installed version
claude plugin list | grep "$(jq -r .name .claude-plugin/plugin.json)"
# Expected: <name>  v<VERSION>
```

---

## HOMEBREW_GATE_STRICT environment variable

Set this variable to `1` to promote advisory gates (Steps 10b and 10c) to
blocking in local release runs:

```bash
export HOMEBREW_GATE_STRICT=1
python3 scripts/verify_caveats.py "$FORMULA" CHANGELOG.md "$VERSION" --strict
python3 scripts/post_install_check.py "$FORMULA" --strict
```

CI runners that do not have the local tap should NOT set this variable — the
tap-absent leg will skip the check safely.

---

## Full release gate sequence

```bash
# 1. Advisory gates (promote to blocking with HOMEBREW_GATE_STRICT=1)
python3 scripts/verify_caveats.py "$FORMULA" CHANGELOG.md "$VERSION" \
  ${HOMEBREW_GATE_STRICT:+--strict} --name "$PLUGIN_NAME"

python3 scripts/post_install_check.py "$FORMULA" \
  ${HOMEBREW_GATE_STRICT:+--strict}

# 2. Blocking gate (always)
bash scripts/aggregator-sync.sh || {
  echo "❌ aggregator-sync failed — release blocked"
  exit 1
}

# 3. Push tap formula
git -C "$TAP_DIR" add Formula/"$PLUGIN_NAME".rb
git -C "$TAP_DIR" commit -m "chore: bump $PLUGIN_NAME to v$VERSION"
git -C "$TAP_DIR" push
```

---

## See Also

- `scripts/verify_caveats.py --help` — CLI reference for caveats gate
- `scripts/post_install_check.py --help` — CLI reference for post_install gate
- `commands/dist/homebrew.md` — Full `/craft:dist:homebrew` command reference
- `scripts/post-release-sweep.sh` — Post-release sweep (includes advisory caveats phase 4.6)
