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
# Fallback if the sourced helper is unavailable: resolve the session the same way
# _ee_resolve_session() does — $CLAUDE_SESSION_ID, else the stdin payload's
# .session_id, else "unknown". Native Claude Code does NOT export
# CLAUDE_SESSION_ID, so without the payload fallback every native session would
# collide into runs/unknown/ and the per-session web-allow / first-seen state
# (which the trust gate below depends on) would leak across sessions.
command -v _ee_resolve_session >/dev/null 2>&1 || _ee_resolve_session() {
  if [ -n "${CLAUDE_SESSION_ID:-}" ]; then printf '%s' "$CLAUDE_SESSION_ID"; return 0; fi
  local _pl="${payload:-}" _sid=""
  if [ -n "$_pl" ]; then
    _sid="$(printf '%s' "$_pl" | grep -o '"session_id"[[:space:]]*:[[:space:]]*"[^"]*"' 2>/dev/null | head -n1 | sed 's/.*:[[:space:]]*"\([^"]*\)".*/\1/' 2>/dev/null || true)"
  fi
  [ -n "$_sid" ] && { printf '%s' "$_sid"; return 0; }
  printf '%s' "unknown"
}

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
host="${host%.}"   # strip a trailing FQDN dot: `evil.com.` is DNS-equivalent to
                   # `evil.com`, but without this it matches neither a deny nor
                   # an allow rule and slips past the blacklist.
[ -n "$host" ] || exit 0

proj="${CLAUDE_PROJECT_DIR:-$PWD}"
cfg="$proj/.ravenclaude/web-access.yaml"
sess="$(_ee_resolve_session)"
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

# sess_list (this-session-only choice from the four-option prompt) is the user's
# explicit per-session consent — silent allow, no further prompts.
if match_host "$host" "${sess_list[@]:-}"; then
  printf '%s' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow"}}'
  exit 0
fi

# Persistent allow_list (from .ravenclaude/web-access.yaml `allow:`) -> first-use
# trust check (closes Codex desktop trust review Finding 5). On first WebFetch
# per domain per session, emit permissionDecision: ask so a hostile YAML edit
# can't silently auto-allow exfiltration. After the user confirms once, the
# per-session seen-file means no further prompts for that domain this session.
# Set `web_access.trusted: true` in posture YAML to skip the ask (you've reviewed
# the whitelist and accept silent allow for persistent entries).
if match_host "$host" "${allow_list[@]:-}"; then
  posture="$proj/.ravenclaude/comfort-posture.yaml"
  web_trusted="false"
  if [ -f "$posture" ]; then
    web_trusted="$(python3 - "$posture" <<'PY' 2>/dev/null || echo "false"
import sys
try:
    import yaml
    d = yaml.safe_load(open(sys.argv[1], encoding="utf-8")) or {}
except Exception:
    d = {}
wa = d.get("web_access") or {}
print("true" if (isinstance(wa, dict) and wa.get("trusted") is True) else "false")
PY
)"
  fi

  if [ "$web_trusted" = "true" ]; then
    printf '%s' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow"}}'
    exit 0
  fi

  # First-use check — seen-file path is per-session, per-domain.
  dom_slug="$(printf '%s' "$host" | tr -dc 'A-Za-z0-9.-' | cut -c1-80)"
  seen_dir="$proj/.ravenclaude/runs/$sess/web-first-seen"
  seen_file="$seen_dir/$dom_slug"

  if [ ! -f "$seen_file" ]; then
    # Do NOT mark the domain seen here — consent is recorded by the PostToolUse
    # hook (mark-web-domain-seen.sh) only after the fetch actually proceeds, so a
    # denied first fetch re-prompts instead of silently auto-allowing on retry.
    reason="First access this session to YAML-whitelisted domain '$host'. The domain is in .ravenclaude/web-access.yaml 'allow:' — allow this fetch (and any subsequent ones to $host this session)?"
    if command -v jq >/dev/null 2>&1; then
      jq -cn --arg r "$reason" '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"ask",permissionDecisionReason:$r}}'
    else
      printf '%s' "{\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"permissionDecision\":\"ask\",\"permissionDecisionReason\":\"${reason//\"/\\\"}\"}}"
    fi
    _emit_hook_event "guard-web-access.sh" "warn" "WebFetch" "$host" "web-whitelist-first-use" 0
    exit 0
  fi

  # Subsequent fetches to the same domain this session -> silent allow.
  printf '%s' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow"}}'
  exit 0
fi

# Unknown domain -> no output; the agent's normal per-domain prompt handles it.
exit 0
