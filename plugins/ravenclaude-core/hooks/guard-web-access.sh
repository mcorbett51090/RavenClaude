#!/usr/bin/env bash
# guard-web-access.sh
# PreToolUse(WebFetch) hook — enforces the project's website allow/deny lists.
#
# whitelist domain  -> auto-allow (no prompt)   (hookSpecificOutput permissionDecision: allow)
# blacklist domain  -> block                    (exit 2 — the only blocking code)
# unknown domain    -> fall through to the agent's normal per-domain prompt (exit 0, no output)
#
# Lists live in $CLAUDE_PROJECT_DIR/.ravenclaude/web-access.yaml:
#   allow: [domains]   deny: [domains]   (a rule matches the domain AND its subdomains)
# plus a per-session allow file written by the "this session" choice:
#   $CLAUDE_PROJECT_DIR/.ravenclaude/runs/<session>/web-allow.txt  (one domain per line)
#
# Fail-safe: absent config / missing jq / unparseable file -> exit 0 (ask as normal);
# the hook never breaks web access, it only auto-allows the whitelist and blocks the
# blacklist. Parsing uses awk only (no PyYAML dependency in a consumer env).
set -euo pipefail

# Structured hook-event substrate (P0.2). Sourced fail-safe.
_emit_event_helper="$(dirname "$0")/_emit-event.sh"
if [ -f "$_emit_event_helper" ]; then
  # shellcheck source=/dev/null
  . "$_emit_event_helper" 2>/dev/null || true
fi
command -v _emit_hook_event >/dev/null 2>&1 || _emit_hook_event() { :; }

# Read the tool call as JSON on stdin (canonical contract). Only act on WebFetch.
tool=""
url=""
if [ ! -t 0 ]; then
  payload="$(cat)"
  if [ -n "$payload" ]; then
    tool="$(printf '%s' "$payload" | jq -r '.tool_name // empty' 2>/dev/null || true)"
    url="$(printf '%s' "$payload" | jq -r '.tool_input.url // empty' 2>/dev/null || true)"
  fi
fi
[ "$tool" = "WebFetch" ] || exit 0
[ -n "$url" ] || exit 0

# Host from the URL: strip scheme, userinfo, path, port; lowercase.
host="${url#*://}"
host="${host%%/*}"
host="${host##*@}"
host="${host%%:*}"
host="$(printf '%s' "$host" | tr 'A-Z' 'a-z')"
[ -n "$host" ] || exit 0

proj="${CLAUDE_PROJECT_DIR:-$PWD}"
cfg="$proj/.ravenclaude/web-access.yaml"
sess="${CLAUDE_SESSION_ID:-unknown}"
sess_allow="$proj/.ravenclaude/runs/$sess/web-allow.txt"

# Does $1 match any of $2.. (exact host or a subdomain of the rule)?
match_host() {
  local h="$1"
  shift
  local d
  for d in "$@"; do
    [ -z "$d" ] && continue
    if [ "$h" = "$d" ] || [ "${h%.$d}" != "$h" ]; then
      return 0
    fi
  done
  return 1
}

# Extract a "section:\n  - item" list from the simple YAML (awk, no YAML lib).
parse_section() {
  [ -f "$1" ] || return 0
  awk -v sec="$2" '
    /^[A-Za-z_]+:/ { insec = ($0 ~ "^"sec":") ? 1 : 0; next }
    insec && /^[[:space:]]*-[[:space:]]*/ {
      gsub(/^[[:space:]]*-[[:space:]]*/, "")
      gsub(/[[:space:]]+$/, "")
      gsub(/["'\'']/, "")
      if ($0 != "") print tolower($0)
    }
  ' "$1"
}

deny_list=()
allow_list=()
sess_list=()
while IFS= read -r line; do deny_list+=("$line"); done < <(parse_section "$cfg" "deny")
while IFS= read -r line; do allow_list+=("$line"); done < <(parse_section "$cfg" "allow")
if [ -f "$sess_allow" ]; then
  while IFS= read -r line; do
    line="$(printf '%s' "$line" | tr 'A-Z' 'a-z' | tr -d '[:space:]')"
    [ -n "$line" ] && sess_list+=("$line")
  done < "$sess_allow"
fi

# Deny wins.
if match_host "$host" "${deny_list[@]:-}"; then
  echo "Blocked by the web blacklist: $host (listed in .ravenclaude/web-access.yaml 'deny'). Remove it there or via the dashboard Web-access editor to allow." >&2
  _emit_hook_event "guard-web-access.sh" "deny" "WebFetch" "$host" "web-blacklist" 2
  exit 2
fi

# Whitelist (persistent or this-session) -> auto-allow, no prompt.
if match_host "$host" "${allow_list[@]:-}" || match_host "$host" "${sess_list[@]:-}"; then
  printf '%s' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow"}}'
  exit 0
fi

# Unknown domain -> no output; the agent's normal per-domain prompt handles it.
exit 0
