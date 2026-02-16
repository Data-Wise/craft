# Tutorial: Homebrew Distribution Setup

> **Time:** 15 minutes | **Level:** Beginner | **Goal:** Set up automated Homebrew releases for your project

---

## What You'll Learn

1. Create a `.craft/homebrew.json` config file
2. Generate a Homebrew formula for your project
3. Set up a security-hardened release workflow
4. Configure token access for your tap
5. Validate everything with `brew audit`
6. Understand how `/release` auto-updates the formula

---

## Prerequisites

- A project with at least one GitHub release (or ready to create one)
- Homebrew installed (`brew --version`)
- GitHub CLI installed (`gh --version`)
- A Homebrew tap repository (e.g., `your-org/homebrew-tap`)

---

## Step 1: Create the Config File

Every project that distributes via Homebrew needs a `.craft/homebrew.json` in the project root.

```bash
mkdir -p .craft
```

Create `.craft/homebrew.json`:

```json
{
  "formula_name": "myapp",
  "tap": "my-org/tap",
  "source_type": "github"
}
```

**What each field means:**

- **`formula_name`**: The name users will type in `brew install my-org/tap/myapp`
- **`tap`**: Your tap in `org/name` format (the repo is `my-org/homebrew-tap`)
- **`source_type`**: Where releases come from — `github` for tarball releases, `pypi` for Python packages

**Why this matters:** Without this file, the release automation guesses the formula name from the directory name. This fails in git worktrees where the directory might be `feature-auth` instead of `myapp`.

---

## Step 2: Run the Setup Wizard

The fastest path is the 4-step wizard:

```bash
/craft:dist:homebrew setup
```

The wizard will:

1. **Detect** your project type (Python, Node, Go, etc.)
2. **Generate** a Ruby formula file
3. **Create** a GitHub Actions workflow
4. **Guide** token configuration

If you prefer to do each step manually, continue with Steps 3-5 below.

---

## Step 3: Generate the Formula

```bash
/craft:dist:homebrew formula
```

This creates a Ruby formula matching your project type. For a Python project, it generates something like:

```ruby
class Myapp < Formula
  include Language::Python::Virtualenv

  desc "Short description of myapp"
  homepage "https://github.com/my-org/myapp"
  url "https://github.com/my-org/myapp/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "abc123..."

  depends_on "python@3.12"

  # ... resources and install method ...

  test do
    system bin/"myapp", "--version"
  end
end
```

---

## Step 4: Generate the Workflow

```bash
/craft:dist:homebrew workflow
```

This creates `.github/workflows/homebrew-release.yml` with security hardening built in:

- **Env indirection** — prevents script injection attacks
- **`sha256sum`** — correct hash tool for Ubuntu runners
- **`--retry 3`** — resilient downloads
- **64-char SHA guard** — catches empty or truncated hashes
- **`ruby -c` check** — validates formula syntax after updates

The workflow triggers on:

- GitHub release published
- Manual dispatch (for testing)

---

## Step 5: Configure the Token

Your workflow needs a token to push formula updates to your tap repo.

### Create a Fine-Grained Token

1. Go to [github.com/settings/tokens](https://github.com/settings/tokens?type=beta)
2. Click "Generate new token"
3. Set scope to your tap repository only
4. Permission: **Contents** (Read and Write)
5. Copy the token

### Add as Repository Secret

```bash
gh secret set HOMEBREW_TAP_GITHUB_TOKEN
# Paste your token when prompted
```

---

## Step 6: Validate with Audit

Before your first release, make sure the formula passes validation:

```bash
# Standard audit
/craft:dist:homebrew audit

# Build from source (catches runtime issues)
/craft:dist:homebrew audit --build
```

Common issues the audit catches:

| Issue | Auto-Fixed? |
|-------|------------|
| Description starts with "A/An" | Yes |
| `Array#include?` deprecation | Yes |
| `rescue StandardError` style | Yes |
| Missing test block | No — add manually |
| SHA256 mismatch | No — regenerate formula |

---

## Step 7: Release

With everything configured, the `/release` skill handles formula updates automatically at Step 8.5:

```bash
/release
```

What happens behind the scenes:

1. Release is created on GitHub
2. Step 8.5 reads `.craft/homebrew.json`
3. Downloads the release tarball
4. Calculates SHA256 with validation
5. Updates the formula via `sed`
6. Validates with `ruby -c`
7. Commits and pushes to the tap

If no local tap checkout exists, the GitHub Actions workflow handles it automatically.

---

## Verify It Works

After your first release:

```bash
# Update tap
brew update

# Install your formula
brew install my-org/tap/myapp

# Check it works
myapp --version
```

---

## Next Steps

- **[Homebrew Automation Guide](../guide/homebrew-automation.md)** — Deep dive into all subcommands
- **[Homebrew Quick Reference](../reference/REFCARD-HOMEBREW.md)** — Cheat sheet
- **[Distribution Commands](../commands/dist.md)** — All distribution options
- **[Release Pipeline Tutorial](TUTORIAL-release-pipeline.md)** — Full release workflow

---

## Troubleshooting

### Formula Not Found After Release

The workflow may take 1-2 minutes to push. Check:

```bash
# Verify workflow ran
gh run list --workflow homebrew-release

# Check tap status
brew update && brew info my-org/tap/myapp
```

### Token Permission Denied

Ensure the token has **Contents: Read and Write** on the tap repository, not just the source repository.

### Build From Source Fails

```bash
# Debug locally
brew install --build-from-source --verbose ./Formula/myapp.rb
```

Look for missing system dependencies or path issues in the verbose output.
