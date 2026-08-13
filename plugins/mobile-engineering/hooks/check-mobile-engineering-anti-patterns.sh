#!/usr/bin/env bash
# check-mobile-engineering-anti-patterns.sh — advisory PreToolUse hook for the mobile-engineering plugin.
# Flags mechanically-detectable anti-patterns on Edit/Write/MultiEdit. Advisory by
# default (exit 0, prints a notice); set MOBILE_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
# $CLAUDE_TOOL_FILE_PATH (passed as $1 by hooks.json) is NOT a real Claude Code
# hook variable, so under Claude Code the arg is empty and the path arrives only
# via the canonical stdin JSON contract. Fall back to it — same dual-source
# pattern regen-on-manifest-change.sh / guard-destructive.sh already use.
if [[ -z "$file" ]] && [[ ! -t 0 ]] && command -v jq >/dev/null 2>&1; then
  payload="$(cat 2>/dev/null || true)"
  if [[ -n "$payload" ]]; then
    file="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_input.path // empty' 2>/dev/null || true)"
  fi
fi
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

# Stock-toolchain portability: `grep -P` (PCRE) is a GNU extension — BSD/macOS grep exits
# 2, which inside `if grep -Pzi ...; then` reads as NO MATCH, so these checks silently
# never fired on macOS. `_rc_pcre_match` uses perl (the PCRE engine, stock on macOS) for
# REAL coverage. Fail-safe: an absent helper degrades to an inline perl equivalent.
_rc_portable="${CLAUDE_PLUGIN_ROOT:-}/hooks/_portable.sh"
[ -f "$_rc_portable" ] || _rc_portable="$(dirname "${BASH_SOURCE[0]}")/../../ravenclaude-core/hooks/_portable.sh"
# shellcheck source=/dev/null
[ -f "$_rc_portable" ] && . "$_rc_portable" 2>/dev/null || true
command -v _rc_pcre_match >/dev/null 2>&1 || _rc_pcre_match() {
  [ -r "$1" ] || return 1
  RC_PCRE_PAT="$2" perl -0777 -ne 'BEGIN{$m=1} $m=0 if /$ENV{RC_PCRE_PAT}/i; END{exit $m}' -- "$1" 2>/dev/null
}

findings=()
if grep -nEi "(UserDefaults|SharedPreferences|AsyncStorage)[\\s\\S]{0,60}(token|password|secret|credential|apikey|api_key)" "$file" >/dev/null 2>&1; then
  findings+=("Secret stored in UserDefaults/SharedPreferences/AsyncStorage — use the Keychain/Keystore secure store; on-device storage is untrusted.")
fi
if _rc_pcre_match "$file" "\\{\\s*\\[?\\s*self\\b(?![\\s\\S]{0,40}weak)|capture.*self(?!.*weak)"; then
  findings+=("Closure capturing self strongly (iOS) — use [weak self] where it can cause a retain cycle.")
fi
if grep -nEi "(NSAllowsArbitraryLoads|usesCleartextTraffic\\s*=\\s*\\\"?true|cleartextTrafficPermitted\\s*=\\s*\\\"?true)" "$file" >/dev/null 2>&1; then
  findings+=("Cleartext/arbitrary HTTP allowed — require TLS; mobile traffic must not be cleartext.")
fi
if grep -nEi "(while\\s*\\(true\\)[\\s\\S]{0,80}(fetch|http|request)|setInterval\\([\\s\\S]{0,40},\\s*[0-9]{1,4}\\))" "$file" >/dev/null 2>&1; then
  findings+=("Possible polling loop — prefer push (APNs/FCM) or batched/deferred work; polling drains battery + data.")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── mobile-engineering advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${MOBILE_STRICT:-0}" = "1" ]; then
  echo "(blocking: MOBILE_STRICT=1)" >&2
  exit 2
fi
exit 0
