#!/usr/bin/env bash
# test-guard-destructive-shf6.sh — dangerous-target scored on the owning segment.
#
# SH-F6: `_is_dangerous_rm` / find / truncate used to match `/` `~` `$HOME` on
# the WHOLE command, so `cd /tmp/build && rm -rf dist` was a false-positive deny.
# Score flag+target on the rm/find/truncate segment only (split on ; & |).
#
# Run: bash plugins/ravenclaude-core/hooks/tests/test-guard-destructive-shf6.sh

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"

HOOK="$REPO_ROOT/plugins/ravenclaude-core/hooks/guard-destructive.sh"
PASS=0
FAIL=0
pass() { printf '  \033[32m✓\033[0m %s\n' "$1"; PASS=$((PASS + 1)); }
fail() { printf '  \033[31m✗\033[0m %s\n' "$1"; FAIL=$((FAIL + 1)); }

_gd() {
  GD_RC=0
  printf '%s' "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":$(printf '%s' "$1" | jq -Rs .)}}" \
    | bash "$HOOK" >/dev/null 2>&1 || GD_RC=$?
}

echo
echo "── SH-F6: chained abs-cd + relative rm/find/truncate is allowed ──────────"
# Strings built so a parent hook scanning this file still sees them as data.
allow=(
  "cd /tmp/build && rm -rf dist"
  "cd /tmp && rm -rf dist"
  "cd /etc && find . -name '*.tmp' -delete"
  "cd /tmp && truncate -s 0 app.log"
  "rm -rf dist && cd /tmp"
  "rm -rf ./tmp/build"
)
for c in "${allow[@]}"; do
  _gd "$c"
  if [ "$GD_RC" -eq 0 ]; then
    pass "allow: $c"
  else
    fail "allow expected 0, got $GD_RC: $c"
  fi
done

echo
echo "── SH-F6: real dangerous target on the rm/find/truncate segment still denies"
deny=(
  "cd /tmp && rm -rf /"
  "true && rm -rf /"
  "cd /tmp && rm -rf ~"
  "rm -rf /"
  "find / -delete"
  "truncate -s 0 /etc/passwd"
  'git commit -m "$(rm -rf ~)"'
)
for c in "${deny[@]}"; do
  _gd "$c"
  if [ "$GD_RC" -eq 2 ]; then
    pass "deny: $c"
  else
    fail "deny expected 2, got $GD_RC: $c"
  fi
done

echo
echo "── SH-F6 teeth: unsplit _cmd_segments re-denies the known-benign case ────"
MUT="$(mktemp)"
python3 - "$HOOK" "$MUT" <<'PY'
from pathlib import Path
import sys
src = Path(sys.argv[1]).read_text()
old = "_cmd_segments() { printf '%s' \"$1\" | tr ';&|' '\\n\\n\\n'; }"
new = "_cmd_segments() { printf '%s' \"$1\"; }"
if old not in src:
    sys.stderr.write("SH-F6 teeth: splitter not found\n")
    sys.exit(2)
Path(sys.argv[2]).write_text(src.replace(old, new, 1))
PY
if [ $? -ne 0 ]; then
  fail "SH-F6 teeth: could not build unsplit mutant"
else
  chmod +x "$MUT"
  HOOK_SAVE="$HOOK"
  HOOK="$MUT"
  _gd "cd /tmp/build && rm -rf dist"
  HOOK="$HOOK_SAVE"
  if [ "$GD_RC" -eq 2 ]; then
    pass "teeth: unsplit segments re-deny cd-abs + rm-rel"
  else
    fail "teeth: mutant did not re-deny (rc=$GD_RC)"
  fi
fi
rm -f "$MUT"

echo
printf '  %d pass, %d fail\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
exit 0
