#!/usr/bin/env bash
# Gate — Phase D alias-deprecation advisory (SessionStart).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HOOK="$ROOT/hooks/alias-deprecation-advisory.sh"
PY="$ROOT/scripts/alias-deprecation-advisory.py"
pass() { echo "  PASS $1"; }
fail() { echo "  FAIL $1"; exit 1; }

python3 "$PY" self-test >/dev/null || fail "python self-test"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/.ravenclaude"
printf '%s\n' 'schema_version: 5' 'handoff_tax:' '  pin_explore: sonnet' >"$TMP/.ravenclaude/comfort-posture.yaml"
export CLAUDE_PROJECT_DIR="$TMP" CLAUDE_PLUGIN_ROOT="$ROOT" CLAUDE_SESSION_ID="adv-test-1"
out="$(printf '%s' '{"session_id":"adv-test-1","source":"startup"}' | bash "$HOOK" 2>/dev/null || true)"
printf '%s' "$out" | grep -q 'alias deprecated' || fail "stdout advisory missing"
printf '%s' "$out" | grep -q 'SessionStart' || fail "SessionStart event missing"
[ -f "$TMP/.ravenclaude/runs/adv-test-1/alias-deprecation-advised" ] || fail "session marker missing"
out2="$(printf '%s' '{"session_id":"adv-test-1","source":"startup"}' | bash "$HOOK" 2>/dev/null || true)"
[ -z "$out2" ] || fail "second fire in same session should be quiet"

# seed quiet
cp "$ROOT/templates/comfort-posture-balanced.yaml" "$TMP/.ravenclaude/comfort-posture.yaml"
export CLAUDE_SESSION_ID="adv-seed"
out3="$(printf '%s' '{"session_id":"adv-seed","source":"startup"}' | bash "$HOOK" 2>/dev/null || true)"
[ -z "$out3" ] || fail "seed both-same should be quiet"

pass "alias-deprecation-advisory SessionStart"
echo "test-alias-deprecation-advisory: OK"
