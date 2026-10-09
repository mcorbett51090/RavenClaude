#!/usr/bin/env bash
# test-watch-spectate.sh — Spectate v0.6 push-mirror emit_derived + resolve
#
# Proves:
#   M1  permission.request → notification line (no session_id leak)
#   M2  tool.pre skipped (spam filter)
#   M3  steer.applied interrupt → notification with steer action
#   M4  tool.target / note-shaped fields never appear in output
#   M5  newest_spectate_log picks spectate-events.jsonl
#
# Run: bash plugins/ravenclaude-core/hooks/tests/test-watch-spectate.sh

set -uo pipefail

MON="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../monitors" && pwd)/watch-spectate.sh"
FAILED=0
pass() { printf '  ✓ %s\n' "$1"; }
fail() { printf '  ✗ %s\n' "$1"; FAILED=$((FAILED + 1)); }

# shellcheck source=/dev/null
. "$MON"

echo "── M1: permission.request emits ─────────────────────────────────────────"
out="$(
  emit_spectate_derived '{"schema":"rc.spectate.v1","kind":"permission.request","asserted_status":"waiting-approval","tool":{"name":"Bash","family":"shell"},"session_id":"secret-session-xyz"}'
)"
if printf '%s' "$out" | grep -q 'permission.request' \
  && printf '%s' "$out" | grep -q 'Bash' \
  && ! printf '%s' "$out" | grep -q 'secret-session-xyz'; then
  pass "permission.request line; no session_id"
else
  fail "M1 bad: $out"
fi

echo "── M2: tool.pre is skipped ──────────────────────────────────────────────"
out="$(
  emit_spectate_derived '{"kind":"tool.pre","tool":{"name":"Bash","family":"shell"},"asserted_status":"running"}'
)"
if [ -z "$out" ]; then
  pass "tool.pre skipped"
else
  fail "tool.pre leaked: $out"
fi

echo "── M3: steer.applied interrupt ──────────────────────────────────────────"
out="$(
  emit_spectate_derived '{"kind":"steer.applied","steer":{"action":"interrupt","note_chars":0}}'
)"
if printf '%s' "$out" | grep -q 'steer.applied' \
  && printf '%s' "$out" | grep -q 'interrupt'; then
  pass "steer interrupt line"
else
  fail "M3 bad: $out"
fi

echo "── M4: path-like tool.target never emitted ──────────────────────────────"
out="$(
  emit_spectate_derived '{"kind":"tool.fail","tool":{"name":"Read","family":"path","target":"/etc/passwd"},"asserted_status":"failed"}'
)"
if printf '%s' "$out" | grep -q 'tool.fail' \
  && printf '%s' "$out" | grep -q 'Read' \
  && ! printf '%s' "$out" | grep -q '/etc/passwd'; then
  pass "tool.target suppressed"
else
  fail "M4 leaked path or missing kind: $out"
fi

echo "── M5: newest_spectate_log resolves file ────────────────────────────────"
T="$(mktemp -d)"
export CLAUDE_PROJECT_DIR="$T"
RUNS_DIR="$T/.ravenclaude/runs"
mkdir -p "$RUNS_DIR/s1" "$RUNS_DIR/s2"
# shellcheck disable=SC2034
PROJECT_DIR="$T"
printf '{}\n' >"$RUNS_DIR/s1/spectate-events.jsonl"
sleep 1
printf '{}\n' >"$RUNS_DIR/s2/spectate-events.jsonl"
got="$(newest_spectate_log || true)"
if [ "$got" = "$RUNS_DIR/s2/spectate-events.jsonl" ]; then
  pass "newest spectate log is s2"
else
  fail "newest was '$got'"
fi

if [ "$FAILED" -ne 0 ]; then
  echo "FAILED=$FAILED"
  exit 1
fi
echo "ALL PASS"
exit 0
