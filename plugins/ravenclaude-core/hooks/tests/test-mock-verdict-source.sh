#!/usr/bin/env bash
# test-mock-verdict-source.sh — THING_SEAT_MOCK_VERDICT requires THING_SEAT_ALLOW_MOCK=1
set -uo pipefail
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"
SEAT="$REPO_ROOT/plugins/ravenclaude-core/scripts/thing-seat.sh"
PASS=0; FAIL=0
pass(){ printf '  \033[32m✓\033[0m %s\n' "$1"; PASS=$((PASS+1)); }
fail(){ printf '  \033[31m✗\033[0m %s\n' "$1"; FAIL=$((FAIL+1)); }
PAYLOAD='{"tool_name":"Bash","tool_input":{"command":"true"}}'

# Without ALLOW_MOCK, the canned mock string must NOT appear (mock ignored).
# Use a fake claude on PATH so we don't spend API credits on the fall-through.
tmpdir=$(mktemp -d)
printf '#!/bin/bash\necho "{\"verdict\":\"deny\",\"edited_command\":null,\"concerns_cited\":[],\"reasoning\":\"fake\",\"confidence\":0.5,\"injection_detected\":false}"\n' > "$tmpdir/claude"
chmod +x "$tmpdir/claude"
out="$(PATH="$tmpdir:$PATH" THING_PAYLOAD="$PAYLOAD" THING_SEAT_MOCK_VERDICT=allow bash "$SEAT" 2>/dev/null || true)"
if printf '%s' "$out" | grep -q 'mock: no concern applies'; then
  fail "mock honored without ALLOW_MOCK"
else
  pass "mock ignored without ALLOW_MOCK"
fi

out="$(PATH="$tmpdir:$PATH" THING_PAYLOAD="$PAYLOAD" THING_SEAT_ALLOW_MOCK=1 THING_SEAT_MOCK_VERDICT=allow bash "$SEAT" 2>/dev/null || true)"
if printf '%s' "$out" | grep -q 'mock: no concern applies'; then
  pass "mock allow with ALLOW_MOCK=1"
else
  fail "mock allow with ALLOW_MOCK=1 failed: $out"
fi
rm -rf "$tmpdir"

printf '  %d pass, %d fail\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
