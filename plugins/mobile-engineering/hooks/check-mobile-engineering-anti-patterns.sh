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

findings=()
if grep -nEi "(UserDefaults|SharedPreferences|AsyncStorage)[\\s\\S]{0,60}(token|password|secret|credential|apikey|api_key)" "$file" >/dev/null 2>&1; then
  findings+=("Secret stored in UserDefaults/SharedPreferences/AsyncStorage — use the Keychain/Keystore secure store; on-device storage is untrusted.")
fi
if grep -Pzi "\\{\\s*\\[?\\s*self\\b(?![\\s\\S]{0,40}weak)|capture.*self(?!.*weak)" "$file" >/dev/null 2>&1; then
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
