#!/usr/bin/env bash
# mark-web-domain-seen.sh
# PostToolUse(WebFetch) hook — records that a whitelisted domain's first-use
# confirmation has been satisfied, but ONLY after the fetch actually ran.
#
# Why this is a PostToolUse hook (the consent-ordering fix):
#   guard-web-access.sh (PreToolUse) emits `permissionDecision: ask` on the first
#   WebFetch to a YAML-whitelisted domain, then silent-allows subsequent fetches
#   to that domain this session — gated by a per-session "seen" marker file. A
#   PreToolUse hook CANNOT see the user's answer to its own `ask`, so if it wrote
#   the marker before prompting, a user who DENIED the first fetch would have the
#   domain silently auto-allowed on the immediate retry (the control inverts).
#   The marker must therefore be written only when the fetch genuinely proceeded
#   — and a PostToolUse hook fires exactly then (it does not run when the tool was
#   blocked/denied). So consent is recorded post-allow, here, not pre-answer.
#
# Mirrors guard-web-access.sh's host-extraction + seen-file path byte-for-byte so
# the two hooks agree on which marker file represents which domain.
#
# Fail-safe: not a WebFetch / no url / missing jq / unwritable path -> silent
# no-op. This hook NEVER blocks (it is PostToolUse; the tool already ran) and
# never affects the run. Always exits 0.
set -euo pipefail

# Read the tool call as JSON on stdin. Only act on WebFetch.
tool=""
url=""
if [ ! -t 0 ]; then
  payload="$(cat 2>/dev/null || true)"
  if [ -n "$payload" ]; then
    tool="$(printf '%s' "$payload" | jq -r '.tool_name // empty' 2>/dev/null || true)"
    url="$(printf '%s' "$payload" | jq -r '.tool_input.url // empty' 2>/dev/null || true)"
  fi
fi
[ "$tool" = "WebFetch" ] || exit 0
[ -n "$url" ] || exit 0

# Host from the URL: strip scheme, userinfo, path, port; lowercase.
# (Identical normalization to guard-web-access.sh.)
host="${url#*://}"
host="${host%%/*}"
host="${host##*@}"
host="${host%%:*}"
host="$(printf '%s' "$host" | tr 'A-Z' 'a-z')"
[ -n "$host" ] || exit 0

proj="${CLAUDE_PROJECT_DIR:-$PWD}"
[ -d "$proj" ] || exit 0
sess="${CLAUDE_SESSION_ID:-unknown}"

# Same per-session, per-domain seen-file path guard-web-access.sh consults.
dom_slug="$(printf '%s' "$host" | tr -dc 'A-Za-z0-9.-' | cut -c1-80)"
[ -n "$dom_slug" ] || exit 0
seen_dir="$proj/.ravenclaude/runs/$sess/web-first-seen"
seen_file="$seen_dir/$dom_slug"

mkdir -p "$seen_dir" 2>/dev/null || exit 0
touch "$seen_file" 2>/dev/null || exit 0
exit 0
