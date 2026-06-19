# Tutorial: dist:homebrew — Homebrew Distribution Automation

By the end of this tutorial you will have:

- Updated a Homebrew formula to a new version
- Audited the formula for correctness
- Managed tap dependencies

**Prerequisites:** craft installed, `brew` on PATH, a Homebrew formula in a tap repository.

---

## Step 1: Update a Formula to a New Version

```
/craft:dist:homebrew update --version 2.41.0
```

Fetches the release tarball, computes the SHA256, and updates the formula:

```
Homebrew Update — craft formula
─────────────────────────────────
Tap:     data-wise/tap
Formula: Formula/craft.rb
Version: 2.40.0 → 2.41.0

Computing SHA256 for v2.41.0 tarball...
  SHA256: 314b41fc63c795b782ddcfeda78b1a2e2ae39dc85ec6f36595d46ace4db9686e

Updates applied:
  Line 7:  url "...v2.40.0.tar.gz" → url "...v2.41.0.tar.gz"
  Line 8:  sha256 "old" → sha256 "314b41f..."

Ready to commit and push to homebrew-tap.
```

---

## Step 2: Audit the Formula

```
/craft:dist:homebrew audit
```

Runs `brew audit --strict` and reports issues:

```
Homebrew Audit — craft
───────────────────────
brew audit --strict Formula/craft.rb

✅ No issues found
```

---

## Step 3: Manage Dependencies

```
/craft:dist:homebrew deps
```

Lists the formula's declared dependencies and checks for outdated pins.

---

## Step 4: Common Subcommands

```
/craft:dist:homebrew update --version X.Y.Z   # Bump version + SHA256
/craft:dist:homebrew audit                     # Validate formula
/craft:dist:homebrew install                   # Local test install
/craft:dist:homebrew test                      # Run formula test block
/craft:dist:homebrew deps                      # Dependency management
```

---

## Step 5: Specify a Different Tap

```
/craft:dist:homebrew update --tap my-org/homebrew-tools --version 1.2.0
```

---

## What's Next

- Use `/craft:dist:homebrew update` as Step 10 of the release pipeline
- After updating, run `brew install data-wise/tap/craft` to verify locally
- See [release pipeline tutorial](TUTORIAL-release-pipeline.md) for the full release flow
