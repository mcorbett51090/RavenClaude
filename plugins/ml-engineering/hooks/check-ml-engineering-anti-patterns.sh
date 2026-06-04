#!/usr/bin/env bash
# check-ml-engineering-anti-patterns.sh — advisory PreToolUse hook for the ml-engineering plugin.
# Flags mechanically-detectable anti-patterns on Edit/Write/MultiEdit. Advisory by
# default (exit 0, prints a notice); set ML_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()
if grep -nEi "(train_test_split|sample)\\([\\s\\S]{0,80}(shuffle\\s*=\\s*True)[\\s\\S]{0,80}(time|date|timestamp)" "$file" >/dev/null 2>&1; then
  findings+=("Shuffled split on temporal data — use a time-aware split to avoid leaking future information into training.")
fi
if grep -nEi "(fit_transform|scaler\\.fit|StandardScaler\\(\\)\\.fit)[\\s\\S]{0,120}(X|data)(?![\\s\\S]{0,40}train)" "$file" >/dev/null 2>&1; then
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
