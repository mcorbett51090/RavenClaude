#!/usr/bin/env bash
# test-runaway-shf4-shf5.sh — SH-F4 (posture root walk-up) + SH-F5 (stderr survives flock).
#
# SH-F4: payload cwd in a subdirectory must still find the project posture file
#        (walk-up / CLAUDE_PROJECT_DIR), so the brake stays armed.
# SH-F5: after taking the flock, a tripped brake must still emit its reason on stderr.
#
# Run: bash plugins/ravenclaude-core/hooks/tests/test-runaway-shf4-shf5.sh

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"

HOOK="$REPO_ROOT/plugins/ravenclaude-core/hooks/runaway-brake.sh"
PASS=0
FAIL=0
pass() { printf '  \033[32m✓\033[0m %s\n' "$1"; PASS=$((PASS + 1)); }
fail() { printf '  \033[31m✗\033[0m %s\n' "$1"; FAIL=$((FAIL + 1)); }

mk_payload() {
  python3 - "$1" "$2" "$3" "$4" <<'PY'
import json, sys
cwd, sid, tn, ti = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
print(json.dumps({"cwd": cwd, "session_id": sid, "tool_name": tn,
                  "tool_input": json.loads(ti)}))
PY
}

echo
echo "── SH-F4: subdirectory cwd still finds project posture (brake arms) ───────"
root="$(mktemp -d)"
mkdir -p "$root/.ravenclaude/subdir"
# posture only at project root — NOT in subdir
printf '%s\n' 'runaway:' '  max_consecutive: 3' '  max_total: 1000' \
  > "$root/.ravenclaude/comfort-posture.yaml"
sid="sess-shf4-$RANDOM"
# Mutating call, payload cwd = subdirectory (no posture file there)
payload="$(mk_payload "$root/subdir" "$sid" "Bash" '{"command":"touch x"}')"
unset CLAUDE_PROJECT_DIR
rc_last=0
for _ in 1 2 3; do
  printf '%s' "$payload" | env -u CLAUDE_PROJECT_DIR bash "$HOOK" >/dev/null 2>&1
  rc_last=$?
done
if [ "$rc_last" -eq 2 ]; then
  pass "SH-F4: brake trips when payload cwd is a subdirectory of the project"
else
  fail "SH-F4: brake stayed inert under subdirectory cwd (rc=$rc_last)"
fi

echo
echo "── SH-F4 control: without walk-up posture, subdir cwd would no-op ─────────"
# Teeth: if we point CLAUDE_PROJECT_DIR at an empty tree and posture is only
# under a different root, and payload cwd has no walk-up hit… already covered
# by the positive case above. Negative: empty temp with no .ravenclaude → exit 0.
empty="$(mktemp -d)"
payload2="$(mk_payload "$empty" "sess-empty-$RANDOM" "Bash" '{"command":"touch x"}')"
printf '%s' "$payload2" | env -u CLAUDE_PROJECT_DIR bash "$HOOK" >/dev/null 2>&1
rc=$?
if [ "$rc" -eq 0 ]; then
  pass "SH-F4 control: no posture anywhere → exit 0 (opt-in untouched)"
else
  fail "SH-F4 control: unexpected rc=$rc with no posture"
fi

echo
echo "── SH-F5: tripped brake reason reaches stderr after flock ────────────────"
# Stock macOS has no flock — the hook skips the lock block entirely, so SH-F5's
# brace-scoped open is never exercised. Inject a no-op flock stub when absent so
# the flock path (and the teeth mutant) still run on the macOS CI shard.
stub_bin=""
run_with_flock() {
  # Usage: run_with_flock <hook> <payload> <stderr-file> → sets rc_last
  local hook="$1" payload="$2" err="$3"
  if command -v flock >/dev/null 2>&1; then
    printf '%s' "$payload" | bash "$hook" >/dev/null 2>"$err"
  else
    if [ -z "$stub_bin" ]; then
      stub_bin="$(mktemp -d)"
      printf '%s\n' '#!/bin/sh' 'exit 0' >"$stub_bin/flock"
      chmod +x "$stub_bin/flock"
    fi
    printf '%s' "$payload" | PATH="$stub_bin:$PATH" bash "$hook" >/dev/null 2>"$err"
  fi
  rc_last=$?
}

root3="$(mktemp -d)"
mkdir -p "$root3/.ravenclaude"
printf '%s\n' 'runaway:' '  max_consecutive: 3' '  max_total: 1000' \
  > "$root3/.ravenclaude/comfort-posture.yaml"
sid3="sess-shf5-$RANDOM"
payload3="$(mk_payload "$root3" "$sid3" "Bash" '{"command":"touch y"}')"
errf="$(mktemp)"
rc_last=0
for _ in 1 2 3; do
  run_with_flock "$HOOK" "$payload3" "$errf"
done
if [ "$rc_last" -eq 2 ] && grep -q 'Runaway brake:' "$errf"; then
  pass "SH-F5: trip reason present on stderr (flock did not silence fd 2)"
else
  fail "SH-F5: reason missing or no trip (rc=$rc_last bytes=$(wc -c <"$errf"))"
fi

# Teeth: restore the unbraced exec form and the reason must vanish.
# Python replace — BSD sed on macOS does not reliably apply the GNU-style escape.
MUT="$(mktemp)"
python3 - "$HOOK" "$MUT" <<'PY'
import sys
from pathlib import Path
src = Path(sys.argv[1]).read_text()
old = '{ exec 9>"${f}.lock"; } 2>/dev/null'
new = 'exec 9>"${f}.lock" 2>/dev/null'
if old not in src:
    sys.stderr.write("SH-F5 teeth: braced exec open not found in hook\n")
    sys.exit(2)
Path(sys.argv[2]).write_text(src.replace(old, new, 1))
PY
mut_rc=$?
chmod +x "$MUT" 2>/dev/null || true
if [ "$mut_rc" -eq 0 ] && grep -q 'exec 9>"${f}.lock" 2>/dev/null && flock' "$MUT"; then
  root4="$(mktemp -d)"
  mkdir -p "$root4/.ravenclaude"
  printf '%s\n' 'runaway:' '  max_consecutive: 3' '  max_total: 1000' \
    > "$root4/.ravenclaude/comfort-posture.yaml"
  sid4="sess-teeth-$RANDOM"
  payload4="$(mk_payload "$root4" "$sid4" "Bash" '{"command":"touch z"}')"
  err4="$(mktemp)"
  rc_last=0
  for _ in 1 2 3; do
    run_with_flock "$MUT" "$payload4" "$err4"
  done
  if [ "$rc_last" -eq 2 ] && ! grep -q 'Runaway brake:' "$err4"; then
    pass "SH-F5 teeth: unbraced exec 9>… 2>/dev/null loses the reason"
  else
    fail "SH-F5 teeth: mutant still carried reason or did not trip (rc=$rc_last)"
  fi
  rm -rf "$root4" "$err4"
else
  fail "SH-F5 teeth: could not build the unbraced-exec mutant (adapter shape changed?)"
fi

rm -rf "$root" "$empty" "$root3" "$errf" "$MUT" ${stub_bin:+"$stub_bin"}

echo
printf '  %d pass, %d fail\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
exit 0
