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

# Structured hook-event substrate helper — sourced fail-safe, ONLY for its
# _ee_resolve_session() (this hook emits no events itself). guard-web-access.sh
# (the PreToolUse reader of the seen-file this hook writes) resolves the session
# the SAME way; the two MUST agree or the first-use trust gate breaks. Native
# Claude Code does NOT export CLAUDE_SESSION_ID — it is carried on the stdin
# payload's .session_id — so resolving from $CLAUDE_SESSION_ID alone collided
# every native session's seen-file into runs/unknown/ while the reader looked
# under runs/<real-session-id>/, re-prompting on every whitelisted fetch.
_emit_event_helper="$(dirname "$0")/_emit-event.sh"
if [ -f "$_emit_event_helper" ]; then
  # shellcheck source=/dev/null
  . "$_emit_event_helper" 2>/dev/null || true
fi
# Fallback if the sourced helper is unavailable: resolve the session the same way
# _ee_resolve_session() does — $CLAUDE_SESSION_ID, else the stdin payload's
# .session_id (the `payload` var read below), else "unknown".
command -v _ee_resolve_session >/dev/null 2>&1 || _ee_resolve_session() {
  if [ -n "${CLAUDE_SESSION_ID:-}" ]; then printf '%s' "$CLAUDE_SESSION_ID"; return 0; fi
  local _pl="${payload:-}" _sid=""
  if [ -n "$_pl" ]; then
    _sid="$(printf '%s' "$_pl" | grep -o '"session_id"[[:space:]]*:[[:space:]]*"[^"]*"' 2>/dev/null | head -n1 | sed 's/.*:[[:space:]]*"\([^"]*\)".*/\1/' 2>/dev/null || true)"
  fi
  [ -n "$_sid" ] && { printf '%s' "$_sid"; return 0; }
  printf '%s' "unknown"
}

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
host="${host%.}"   # strip a trailing FQDN dot — MUST mirror guard-web-access.sh:61
                   # exactly, else the writer keys the seen-file on `evil.com.`
                   # while the reader looks for `evil.com`, so first-use consent
                   # never latches and the user is re-prompted every fetch.
[ -n "$host" ] || exit 0

proj="${CLAUDE_PROJECT_DIR:-$PWD}"
[ -d "$proj" ] || exit 0
# Resolve the session id exactly as guard-web-access.sh does (payload .session_id
# on native Claude Code, where CLAUDE_SESSION_ID is not exported) so the writer
# and reader agree on runs/<sess>/web-first-seen/<domain>.
sess="$(_ee_resolve_session)"

# Same per-session, per-domain seen-file path guard-web-access.sh consults.
dom_slug="$(printf '%s' "$host" | tr -dc 'A-Za-z0-9.-' | cut -c1-80)"
[ -n "$dom_slug" ] || exit 0
seen_dir="$proj/.ravenclaude/runs/$sess/web-first-seen"
seen_file="$seen_dir/$dom_slug"

mkdir -p "$seen_dir" 2>/dev/null || exit 0
touch "$seen_file" 2>/dev/null || exit 0
exit 0
