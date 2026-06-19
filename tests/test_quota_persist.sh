#!/usr/bin/env bash
set -e
TMP=$(mktemp -d); export HOME="$TMP"; mkdir -p "$HOME/.claude"
echo '{"rate_limits":{"five_hour":{"used_percentage":31,"resets_at":1781000000},"seven_day":{"used_percentage":9,"resets_at":1781500000}}}' \
  | bash scripts/quota-persist.sh
test -f "$HOME/.claude/quota-cache.json" || { echo FAIL no cache; exit 1; }
grep -q '"five_hour_pct": *31' "$HOME/.claude/quota-cache.json" || { echo FAIL pct; exit 1; }
# absent rate_limits keeps last-good (does not overwrite to empty)
echo '{"model":{"display_name":"Opus"}}' | bash scripts/quota-persist.sh
grep -q '"five_hour_pct": *31' "$HOME/.claude/quota-cache.json" || { echo FAIL last-good; exit 1; }
echo PASS
