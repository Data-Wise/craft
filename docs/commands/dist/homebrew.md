# /craft:dist:homebrew

> **Complete Homebrew automation - formulas, casks, workflows, auditing, and dependency management**

---

## Synopsis

```bash
/craft:dist:homebrew [mode]
```

---

## Description

Complete Homebrew automation - formulas, casks, workflows, auditing, and dependency management

---

## Release Gates (Plugin Formula)

Advisory gates run before pushing the tap formula; the aggregator-sync gate is BLOCKING.
Set `HOMEBREW_GATE_STRICT=1` to promote advisory gates to blocking for local release runs.

### Step 10b: Verify caveats freshness (advisory; strict via env)

```bash
python3 scripts/verify_caveats.py "$FORMULA" CHANGELOG.md "$VERSION" \
  ${HOMEBREW_GATE_STRICT:+--strict} --name "$PLUGIN_NAME"
# Tap-absent leg: if "$FORMULA" is not locally checked out, warn and continue.
```

### Step 10c: Verify post_install structure (advisory; strict via env)

```bash
python3 scripts/post_install_check.py "$FORMULA" \
  ${HOMEBREW_GATE_STRICT:+--strict}
# Add --sandbox only on a macOS-local release host for higher fidelity.
```

### Step 10d: Cowork/Desktop verification (BLOCKING aggregator-sync)

```bash
# BLOCKING (D4): a stale aggregator ships silent wrong-version installs.
bash scripts/aggregator-sync.sh || { echo "aggregator-sync failed - release blocked"; exit 1; }

echo "Verify on Cowork/Desktop after publish:"
echo "  claude plugin marketplace update local-plugins"
echo "  claude plugin update NAME@local-plugins"
```

See the [Homebrew Gates Tutorial](../../tutorials/TUTORIAL-homebrew-gates.md) for full usage.

## See Also

- [/craft:hub](../hub.md) — Browse all commands
