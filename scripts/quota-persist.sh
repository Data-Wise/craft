#!/usr/bin/env bash
# Persist native rate_limits from statusline stdin for non-statusline consumers.
in=$(cat); cache="$HOME/.claude/quota-cache.json"
has=$(printf '%s' "$in" | jq -r 'has("rate_limits") and (.rate_limits|has("five_hour"))' 2>/dev/null)
[ "$has" = "true" ] || exit 0
printf '%s' "$in" | jq '{
  five_hour_pct: .rate_limits.five_hour.used_percentage,
  seven_day_pct: .rate_limits.seven_day.used_percentage,
  five_hour_resets_at: .rate_limits.five_hour.resets_at,
  seven_day_resets_at: .rate_limits.seven_day.resets_at,
  captured_at: now
}' > "$cache"
