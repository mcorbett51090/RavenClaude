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

findings=()
if grep -nEi "(train_test_split|sample)\\([\\s\\S]{0,80}(shuffle\\s*=\\s*True)[\\s\\S]{0,80}(time|date|timestamp)" "$file" >/dev/null 2>&1; then
  findings+=("Shuffled split on temporal data — use a time-aware split to avoid leaking future information into training.")
fi
if grep -Pzi "(fit_transform|scaler\\.fit|StandardScaler\\(\\)\\.fit)[\\s\\S]{0,120}(X|data)(?![\\s\\S]{0,40}train)" "$file" >/dev/null 2>&1; then
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
