#!/usr/bin/env bash
# regen-on-manifest-change.sh
# PostToolUse hook for Edit | Write | MultiEdit.
#
# When a manifest is modified inside the RavenClaude marketplace clone (the repo
# this hook lives in), regenerate the downstream artifacts that mirror its data
# — the Copilot package (plugins/ravenclaude-core/copilot/), dashboard.html,
# and repo-guide.html. Prevents the CI freshness gates from catching drift that
# the author "forgot to regenerate" — the regeneration is now mechanical.
#
# Triggers ONLY when:
#   1. The edited file's basename is plugin.json or marketplace.json,
#   2. The file lives INSIDE this marketplace clone (resolved via
#      $CLAUDE_PROJECT_DIR), and
#   3. The version field actually changed compared to git HEAD (cheap optimization
#      so a description/keyword edit doesn't pay the regen cost).
#
# No-ops silently outside the marketplace, on non-manifest edits, and when the
# version is unchanged. Failures are logged to stderr but never block the agent.

set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

# Resolve absolute path so the marketplace-prefix check is robust.
abs="$(cd "$(dirname "$file")" && pwd)/$(basename "$file")"
base="$(basename "$abs")"

# Trigger 1: basename match.
case "$base" in
  plugin.json|marketplace.json) ;;
  *) exit 0 ;;
esac

# Trigger 2: inside a marketplace clone (detect via the catalog at the root).
MARKET="${CLAUDE_PROJECT_DIR:-$PWD}"
[ -f "$MARKET/.claude-plugin/marketplace.json" ] || exit 0
case "$abs" in
  "$MARKET"/*) ;;
  *) exit 0 ;;
esac

# Trigger 3: did the `version` field change? Compare current to git HEAD copy.
# best-effort: jq + git failures are silently skipped to "version changed", so the
# regen runs (fail-open on the optimization, not on the safety).
rel="${abs#"$MARKET/"}"
new_version="$(jq -r '.version // ""' "$abs" 2>/dev/null || echo "")"
old_version="$(git -C "$MARKET" show "HEAD:$rel" 2>/dev/null | jq -r '.version // ""' 2>/dev/null || echo "")"
# When old and new match, nothing downstream needs regen — short-circuit.
if [ -n "$new_version" ] && [ -n "$old_version" ] && [ "$new_version" = "$old_version" ]; then
  exit 0
fi

# Run a generator quietly. Failure is reported to stderr but never blocks.
run() {
  local label="$1"; shift
  if "$@" >/dev/null 2>&1; then
    printf '[regen-on-manifest-change] regenerated %s\n' "$label" >&2
  else
    printf '[regen-on-manifest-change] failed to regenerate %s — run manually: %s\n' "$label" "$*" >&2
  fi
}

cd "$MARKET" || exit 0

# 1. Copilot package — its plugin.json mirrors plugins/ravenclaude-core/.claude-plugin/plugin.json's
#    version. A version bump here without regenerating drops the freshness gate.
if [ -f "$MARKET/scripts/generate-copilot-plugin.py" ] && [ -d "$MARKET/plugins/ravenclaude-core/copilot" ]; then
  run "Copilot package" python3 scripts/generate-copilot-plugin.py
fi

# 2. dashboard.html (plugin version is shown in the UI and embedded in generated HTML).
if [ -f "$MARKET/scripts/generate-dashboards.py" ]; then
  run "dashboard.html" python3 scripts/generate-dashboards.py
fi

# 3. repo-guide.html (plugin version is shown in nav + cards).
if [ -f "$MARKET/scripts/generate-repo-guide.py" ]; then
  run "repo-guide.html" python3 scripts/generate-repo-guide.py
fi

exit 0
