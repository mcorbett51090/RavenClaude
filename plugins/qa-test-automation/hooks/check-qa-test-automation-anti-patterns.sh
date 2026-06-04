#!/usr/bin/env bash
# check-qa-test-automation-anti-patterns.sh — advisory PreToolUse hook for the qa-test-automation plugin.
# Flags mechanically-detectable anti-patterns on Edit/Write/MultiEdit. Advisory by
# default (exit 0, prints a notice); set QA_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
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
