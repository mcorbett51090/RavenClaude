#!/usr/bin/env bash
# check-ml-engineering-anti-patterns.sh — advisory PreToolUse hook for the ml-engineering plugin.
# Flags mechanically-detectable anti-patterns on Edit/Write/MultiEdit. Advisory by
# default (exit 0, prints a notice); set ML_STRICT=1 to make it blocking (exit 2).
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
if grep -nEi "(train_test_split|sample)\\([\\s\\S]{0,80}(shuffle\\s*=\\s*True)[\\s\\S]{0,80}(time|date|timestamp)" "$file" >/dev/null 2>&1; then
  findings+=("Shuffled split on temporal data — use a time-aware split to avoid leaking future information into training.")
fi
if _rc_pcre_match "$file" "(fit_transform|scaler\\.fit|StandardScaler\\(\\)\\.fit)[\\s\\S]{0,120}(X|data)(?![\\s\\S]{0,40}train)"; then
  findings+=("Possible fitting a transform on the full dataset before splitting — fit on train only, or you leak test statistics.")
fi
if grep -nEi "\\.predict\\([\\s\\S]{0,120}(read_csv|read_sql|requests\\.get)" "$file" >/dev/null 2>&1; then
  findings+=("Computing serving features ad-hoc at predict time — risks training-serving skew; use the shared transform/feature store.")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── ml-engineering advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${ML_STRICT:-0}" = "1" ]; then
  echo "(blocking: ML_STRICT=1)" >&2
  exit 2
fi
exit 0
