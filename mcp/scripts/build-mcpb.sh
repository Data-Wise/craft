#!/usr/bin/env bash
# Build the craft-mcp .mcpb (DXT) bundle for Claude Desktop.
#
# Packs: manifest.json + dist/index.js (esbuild bundle) + bundled/ (the wrapped
# craft scripts, structure-preserving so the runtime path resolution matches
# local dev). Uses a tar copy (not cp -R) for governance/ and excludes its test
# fixtures — those contain intentionally-broken symlinks that abort cp on macOS.
set -euo pipefail
cd "$(dirname "$0")/.."   # -> mcp/

echo "==> building dist/index.js"
npm run build

echo "==> bundling craft scripts (structure-preserving)"
rm -rf bundled
mkdir -p bundled/scripts
cp ../scripts/validate-counts.sh      bundled/scripts/
cp ../scripts/docs-staleness-check.sh bundled/scripts/
mkdir -p bundled/governance
( cd ../governance && tar cf - --exclude=fixtures . ) | ( cd bundled/governance && tar xf - )

VERSION=$(node -p "require('./package.json').version")
OUT="craft-mcp-v${VERSION}.mcpb"
echo "==> packing ${OUT}"
npx --yes @anthropic-ai/mcpb pack . "${OUT}"
echo "==> built ${OUT}"
