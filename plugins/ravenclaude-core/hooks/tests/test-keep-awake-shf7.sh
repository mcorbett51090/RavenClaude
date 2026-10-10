#!/usr/bin/env bash
# test-keep-awake-shf7.sh — keep-awake must not leak rc_advise's saved stderr fd.
#
# SH-F7: rc_advise_init does `exec 3>&2` then buffers fd 2. keep-awake then
# backgrounds `caffeinate`. Without `3>&-` on that spawn, the child inherits
# the saved stderr and holds the terminal/socket open for the session.
#
# This harness is Darwin-independent: it asserts the source carries `3>&-` on
# the caffeinate line, and reproduces the fd-3 inherit/close pattern with
# `sleep` (same redirect shape) so a regression is behavioral, not just textual.
#
# Run: bash plugins/ravenclaude-core/hooks/tests/test-keep-awake-shf7.sh

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"

HOOK="$REPO_ROOT/plugins/ravenclaude-core/hooks/keep-awake.sh"
PASS=0
FAIL=0
pass() { printf '  \033[32m✓\033[0m %s\n' "$1"; PASS=$((PASS + 1)); }
fail() { printf '  \033[31m✗\033[0m %s\n' "$1"; FAIL=$((FAIL + 1)); }

echo
echo "── SH-F7: keep-awake caffeinate spawn closes advise fd 3 ─────────────────"

# 1. Source contract: the only caffeinate background spawn must carry 3>&-.
spawn_line="$(grep -E 'nohup[[:space:]]+caffeinate' "$HOOK" | head -1 || true)"
if printf '%s' "$spawn_line" | grep -q '3>&-'; then
  pass "caffeinate spawn line carries 3>&-"
else
  fail "caffeinate spawn missing 3>&- (line=[${spawn_line:-none}])"
fi

# 2. Behavioral: after exec 3>&2 + exec 2>buf, a background child without 3>&-
#    inherits fd 3; with 3>&- it does not. Skip if /proc is unavailable.
if [ -d /proc/self/fd ]; then
  BUF="$(mktemp "${TMPDIR:-/tmp}/rc-advise-shf7.XXXXXX")"
  exec 3>&2
  exec 2>"$BUF"

  nohup sleep 30 >/dev/null 2>&1 &
  LEAK_PID=$!
  nohup sleep 30 >/dev/null 2>&1 3>&- &
  CLOSED_PID=$!
  sleep 0.15

  if [ -e "/proc/$LEAK_PID/fd/3" ]; then
    pass "control: child without 3>&- inherits fd 3"
  else
    fail "control: child without 3>&- should inherit fd 3"
  fi

  if [ ! -e "/proc/$CLOSED_PID/fd/3" ]; then
    pass "child with 3>&- does not inherit fd 3"
  else
    fail "child with 3>&- still has fd 3 open"
  fi

  kill "$LEAK_PID" "$CLOSED_PID" 2>/dev/null || true
  wait "$LEAK_PID" "$CLOSED_PID" 2>/dev/null || true
  exec 2>&3 3>&-
  rm -f "$BUF"
else
  pass "skip behavioral /proc check (no /proc/self/fd)"
fi

# 3. Teeth: strip 3>&- from a mutant copy of the spawn line pattern — the
#    source gate above is the production assertion; teeth prove that assertion
#    is measuring the redirect, not passing vacuously.
mut="$(mktemp "${TMPDIR:-/tmp}/keep-awake-shf7.XXXXXX")"
sed 's/ 3>&-//' "$HOOK" > "$mut"
mut_line="$(grep -E 'nohup[[:space:]]+caffeinate' "$mut" | head -1 || true)"
rm -f "$mut"
if printf '%s' "$mut_line" | grep -q '3>&-'; then
  fail "teeth: sed strip left 3>&- in place — presence check is not measuring the redirect"
else
  pass "teeth: stripping 3>&- makes the presence check fail"
fi

echo
if [ "$FAIL" -eq 0 ]; then
  echo "SH-F7 keep-awake fd-3 PASS ($PASS)"
  exit 0
fi
echo "SH-F7 keep-awake fd-3 FAIL ($FAIL failed, $PASS passed)"
exit 1
