#!/usr/bin/env bash
# check-qa-test-automation-anti-patterns.sh — advisory PreToolUse hook for the qa-test-automation plugin.
# Flags mechanically-detectable anti-patterns on Edit/Write/MultiEdit. Advisory by
# default (exit 0, prints a notice); set QA_STRICT=1 to make it blocking (exit 2).
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
if grep -nEi "(time\\.sleep|sleep\\(|cy\\.wait\\([0-9]|page\\.waitForTimeout\\([0-9]|Thread\\.sleep)" "$file" >/dev/null 2>&1; then
  findings+=("Fixed sleep in a test — replace with a condition-based wait; fixed sleeps are flaky or slow.")
fi
if grep -nEi "(By\\.xpath|cy\\.xpath|page\\.\\$x\\(|//div\\[|//span\\[)" "$file" >/dev/null 2>&1; then
  findings+=("XPath/brittle selector in a test — prefer roles and data-testid; XPath breaks on markup changes.")
fi
if grep -nEi "(\\.only\\(|fit\\(|fdescribe\\(|test\\.only|describe\\.only)" "$file" >/dev/null 2>&1; then
  findings+=("Focused test (.only/fit/fdescribe) — will silently skip the rest of the suite in CI; remove before commit.")
fi
if grep -nEi "(beforeAll.*global|shared.*fixture.*db|GLOBAL_TEST_DATA)" "$file" >/dev/null 2>&1; then
  findings+=("Possible shared mutable test data — isolate per test via factories to avoid order-dependence/flake.")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── qa-test-automation advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${QA_STRICT:-0}" = "1" ]; then
  echo "(blocking: QA_STRICT=1)" >&2
  exit 2
fi
exit 0
